#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''An alternative OpenERP mailgate that does it's stuff in the DB instead via
XMLRPC.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

import time
import random

from logging import Handler
from psycopg2 import OperationalError, errorcodes

from xoutil.future.codecs import safe_encode, safe_decode

try:
    from xoeuf.odoo.jobs import Deferred
except ImportError:
    Deferred = None

# A size limit for messages sent through the message broker.
MAX_SIZE_FOR_DEFERRED = 200 * 1024

from . import Command


PG_CONCURRENCY_ERRORS_TO_RETRY = (
    errorcodes.LOCK_NOT_AVAILABLE,
    errorcodes.SERIALIZATION_FAILURE,
    errorcodes.DEADLOCK_DETECTED
)
MAX_TRIES_ON_CONCURRENCY_FAILURE = 5

try:
    # A Py3k more compatible Exception value
    # TODO: Use `xoutil.eight.exceptions.StandardError`
    #       Rename all use of `Exception`
    Exception = StandardError
except NameError:
    pass


# TODO: This has grown into a monstrous pile of code that needs
# refactorization.


CR = str('\r')
LF = str('\n')
CRLF = CR + LF


# TODO: Should this be moved elsewhere?
class SysLogHandler(Handler):
    def emit(self, report):
        # This avoids the /dev/log system issue and goes directly to Unix
        # syslog.  But then Windows is f.cked.
        import syslog
        syslog.syslog(safe_encode(self.format(report)))


del Handler


class Mailgate(Command):
    '''The xoeuf mailgate for OpenERP.

    It does not need the XMLRPC server to be running.  The only requirement is
    that you have configured properly the OpenERP:

    a) Set up DB host, user and password.

    '''

    MESSAGE_TEMPLATE = safe_encode(
        "Error while processing message."
        "from {sender}.\n\n"
        "{traceback}\n\n"
        "{details_title}:\n\n"
        "{message_details}\n"
    )

    @classmethod
    def get_arg_parser(cls):
        def path(extensions=None):
            '''A type-builder for file arguments.'''
            from xoutil.future.types import is_collection
            from os.path import abspath, isfile, splitext
            if extensions and not is_collection(extensions):
                extensions = (extensions, )
            acceptable = lambda ext: not extensions or ext in extensions

            def inner(value):
                res = abspath(value)
                name, extension = splitext(value)
                if not isfile(res) or not acceptable(extension):
                    raise TypeError('Invalid filename %r' % res)
                return res
            return inner

        res = getattr(cls, '_arg_parser', None)
        if not res:
            from argparse import ArgumentParser
            res = ArgumentParser()
            cls._arg_parser = res
            res.add_argument('--quick', dest='quick',
                             action='store_true',
                             default=False,
                             help=('Accept the message as quickly as '
                                   'possible, deferring actions if needed. '
                                   'NOTICE: This means your Odoo application '
                                   'needs to be prepared to send bounces '
                                   'if needed.'))
            res.add_argument('-c', '--config', dest='conf',
                             required=False,
                             type=path(),
                             help='A configuration file.  This could be '
                             'either a Python file, like that required by '
                             'Gunicorn deployments, or a INI-like '
                             'like the standard ".openerp-serverrc".')
            res.add_argument('-d', '--database', dest='database',
                             required=True)
            res.add_argument('-m', '--model', dest='default_model',
                             default=str('crm.lead'),
                             type=str,
                             help='The fallback model to use if the message '
                             'it not a reply or is not addressed to an '
                             'email alias.  Defaults to "crm.lead", i.e. '
                             'creating a CRM lead.')
            res.add_argument('--strip-attachment', dest='strip_attachments',
                             default=False,
                             action='store_true',
                             help='Set to strip the attachments from the '
                             'messages.')
            res.add_argument('--save-original', dest='save_original',
                             default=False,
                             action='store_true',
                             help='Set to also save the message in '
                             'its original format.')
            res.add_argument('--slowness', dest='slowness',
                             default=0,
                             type=float,
                             help='How much time in seconds to wait '
                             'before standard input needs to be ready. '
                             'Defaults to 0 (i.e not to wait).')
            res.add_argument('--allow-empty', dest='allow_empty',
                             default=False,
                             action='store_true',
                             help='Whether to accept an empty message '
                             'without error.')
            res.add_argument('--input-file', '-f', dest='input',
                             type=path(),
                             help='Read the message from the file INPUT '
                             'instead of the stdin.')
            res.add_argument('--defer', default=False, action='store_true',
                             help='Treat errors as transient.')
            res.add_argument('--queue-id', dest='queue_id', default='',
                             help=('The queue ID the MTA queue.  If provided '
                                   'the header X-Queue-ID will be injected '
                                   'to the message'))
            # Deprecated, but simply ignored
            loggroup = res.add_argument_group('Logging')
            loggroup.add_argument('--log-level',
                                  choices=('debug', 'warning',
                                           'info', 'error'),
                                  default='warning',
                                  help='How much to log')
            loggroup.add_argument('--log-host', default=None,
                                  help='The SMTP host for reporting errors.')
            loggroup.add_argument('--log-to', default=None,
                                  nargs='+',
                                  help='The address to receive error logs.')
            loggroup.add_argument('--log-from', default=None,
                                  help='The issuer of error reports.')
        return res

    @classmethod
    def database_factory(cls, database):
        # TODO: Homogenize 'get' in a compatibility module.
        try:
            from odoo.modules.registry import Registry
            get = Registry
        except ImportError:
            from openerp.modules.registry import RegistryManager
            get = RegistryManager.get
        return get(database)

    @staticmethod
    def get_raw_message(timeout=0, raises=True):
        '''Return the data provide via stdin.

        This will wait until the stdin is ready until the timeout expires.  If
        the `raises` is True and the stdin returns an empty byte-stream a
        RuntimeError is raised.

        The result is always bytes.

        '''
        from xoutil.eight import binary_type as bytes
        import select
        import sys
        import logging
        logger = logging.getLogger(__name__)
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        if ready:
            stdin = ready[0]
            # XXX: To read bytes in both Py3k and Py 2.
            buffer = getattr(stdin, 'buffer', stdin)
            result = buffer.read()
            return result
        elif raises:
            raise RuntimeError('No message via stdin')
        else:
            logger.warn('No message provided, but allowing.')
            return bytes('')

    @classmethod
    def send_error_notification(cls, message):
        '''Report an error dealing with `message`.'''
        import logging
        import email
        from email.message import Message
        try:
            logger = logging.getLogger(__name__)
            if not isinstance(message, Message):
                msg = email.message_from_string(safe_encode(message))
            else:
                msg = message
                message = safe_encode(msg.as_string())
            # The follow locals vars are mean to be retrieved from tracebacks.
            msgid = safe_encode(msg.get('Message-Id', '<NO ID>'))  # noqa
            mail_from = safe_encode(msg.get('From', '<nobody>'))  # noqa
            sender = safe_encode(msg.get('Sender', '<nobody>'))  # noqa
            logger.critical("Error while processing incoming message.",
                            exc_info=1)
        except Exception:
            # Avoid errors... This should be logged to the syslog instead and
            # raven prints the connection error.
            pass

    def send_immediate(self, options, message):
        from xoeuf.odoo import SUPERUSER_ID, api
        default_model = options.default_model
        db = self.database_factory(options.database)
        with db.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            obj = env['mail.thread']
            obj.message_process(default_model,
                                message,
                                save_original=options.save_original,
                                strip_attachments=options.strip_attachments)

    def send_deferred(self, options, message):
        from xoeuf.odoo import SUPERUSER_ID
        default_model = options.default_model
        Deferred(
            str('mail.thread'),
            options.database, SUPERUSER_ID, 'message_process',
            default_model, message, save_original=options.save_original,
            strip_attachments=options.strip_attachments
        )

    def run(self, args=None):
        from xoeuf.sentrylog import patch_logging
        patch_logging(override=True, force=True)
        parser = self.get_arg_parser()
        options = parser.parse_args(args)
        conffile = options.conf
        if conffile:
            self.read_conffile(conffile)
        message = None
        try:
            if not options.input:
                message = self.get_raw_message(timeout=options.slowness,
                                               raises=not options.allow_empty)
            else:
                with open(options.input, 'rb') as f:
                    message = f.read()
            # TODO: assert message is bytes
            if options.queue_id:
                message = (
                    'X-Queue-ID: %s%s' % (options.queue_id, CRLF) + message
                )
            retries = 0
            done = False
            while not done:
                try:
                    if Deferred and options.quick and random.random() < 0.1 and len(message) < MAX_SIZE_FOR_DEFERRED:  # noqa
                        # In order to test this feature we're only deferring a
                        # 10% of messages.  Increase this number with care
                        # until you reach 100%.  Also don't send large emails
                        # through the broker, that may breaker the broker ;)
                        self.send_deferred(options, message)
                    else:
                        self.send_immediate(options, message)
                except OperationalError as error:
                    if error.pgcode not in PG_CONCURRENCY_ERRORS_TO_RETRY:
                        raise
                    if retries < MAX_TRIES_ON_CONCURRENCY_FAILURE:
                        retries += 1
                        wait_time = random.uniform(0.0, 2**retries)
                        time.sleep(wait_time)
                    else:
                        raise
                else:
                    done = True
        except Exception:
            import sys
            if options.defer:
                print(str('4.3.5 System incorrectly configured'),
                      file=sys.stderr)
            else:
                print(str('5.0.0 Permanent error. System error.'),
                      file=sys.stderr)
            # First decode the message since the raw message may contain
            # invalid UTF-8 sequences or come with a mixture of encodings
            # (each MIME part can be encoded differently) and thus the logger
            # fail to construct the log message.
            self.send_error_notification(
                safe_decode(message) if message else 'No message provided'
            )
            if sys.stdout.isatty():
                import traceback
                traceback.print_exc()
            sys.exit(1)

    def read_conffile(self, filename):
        import os
        ext = os.path.splitext(filename)[-1]
        if ext == '.py':
            self.load_config_from_script(filename)
        else:
            self.load_config_from_inifile(filename)

    @staticmethod
    def load_config_from_script(filename):
        from xoutil.eight import exec_
        cfg = {
            "__builtins__": __builtins__,
            "__name__": "__config__",
            "__file__": filename,
            "__doc__": None,
            "__package__": None
        }
        try:
            with open(filename, 'rb') as fh:
                return exec_(compile(fh.read(), filename, 'exec'), cfg, cfg)
        except Exception:
            import traceback
            import sys
            print("Failed to read config file: %s" % filename)
            traceback.print_exc()
            sys.exit(1)

    @staticmethod
    def load_config_from_inifile(filename):
        from xoeuf.odoo.tools import config
        config.rcfile = filename
        config.load()


def main():
    '''The OpenERP mailgate.'''
    from xoutil.cli.app import main
    from xoutil.cli import command_name
    main(default=command_name(Mailgate))


if __name__ == '__main__':
    main()
