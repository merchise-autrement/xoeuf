# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoeuf.cli.mailgate
# ---------------------------------------------------------------------
# Copyright (c) 2014, 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2014-03-12

'''An alternative OpenERP mailgate that does it's stuff in the DB instead via
XMLRPC.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


from . import Command
from logging import Handler
from psycopg2 import OperationalError

try:
    # A Py3k more compatible Exception value
    Exception = StandardError
except NameError:
    pass


from xoutil.string import safe_encode, safe_decode

# TODO: This has grown into a monstrous pile of code that needs
# refactorization.


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
            from xoutil.types import is_collection
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
        import importlib
        module = 'xoeuf.pool.%s' % database
        return importlib.import_module(module)

    @staticmethod
    def get_raw_message(timeout=0, raises=True):
        '''Return the data provide via stdin.

        This will wait until the stdin is ready until the timeout expires.  If
        the `raises` is True and the stdin returns an empty byte-stream a
        RuntimeError is raised.

        The result is always bytes.

        '''
        from six import binary_type as bytes
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
        logger = logging.getLogger(__name__)
        if not isinstance(message, Message):
            msg = email.message_from_string(safe_encode(message))
        else:
            msg = message
            message = msg.as_string()
        msgid = safe_encode(msg.get('Message-Id', '<NO ID>'))  # noqa
        sender = safe_encode(  # noqa
            msg.get('Sender', msg.get('From', '<nobody>'))
        )
        logger.exception("Error while processing incoming message.")

    def run(self, args=None):
        from openerp import SUPERUSER_ID
        parser = self.get_arg_parser()
        options = parser.parse_args(args)
        conffile = options.conf
        if conffile:
            self.read_conffile(conffile)
        default_model = options.default_model
        message = None
        try:
            if not options.input:
                message = self.get_raw_message(timeout=options.slowness,
                                               raises=not options.allow_empty)
            else:
                with open(options.input, 'rb') as f:
                    message = f.read()
            # TODO: assert message is bytes
            db = self.database_factory(options.database)
            retries, MAX_RETRIES = 0, 3
            done = False
            while not done:
                try:
                    with db(transactional=True) as cr:
                        obj = db.models.mail_thread
                        obj.message_process(
                            cr, SUPERUSER_ID, default_model,
                            message, save_original=options.save_original,
                            strip_attachments=options.strip_attachments)
                except OperationalError:
                    if retries < MAX_RETRIES:
                        retries += 1
                    else:
                        raise
                except Exception:
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
        from six import exec_
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
            import traceback, sys
            print("Failed to read config file: %s" % filename)
            traceback.print_exc()
            sys.exit(1)

    @staticmethod
    def load_config_from_inifile(filename):
        from openerp.tools import config
        config.rcfile = filename
        config.load()


def main():
    '''The OpenERP mailgate.'''
    from xoutil.cli.app import main
    from xoutil.cli import command_name
    main(default=command_name(Mailgate))

if __name__ == '__main__':
    main()
