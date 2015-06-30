#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# sentrylog
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-04-09

'''Extends/Overrides the OpenERP's logging system to Sentry-based approach.

Sentry_ aggregates logs and lets you inspect the server's health by a web
application.

To configure, simply set the global `conf`:obj: dictionary and call
`patch_logging`:func:.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoutil.functools import lru_cache
from xoutil.modules import moduleproperty, modulemethod
from xoutil.objects import setdefaultattr

# A dictionary holding the Raven's client keyword arguments.  You should
# modify this dictionary before patching the logging.
conf = {}

# The name of the context to the logger to avoid logging sentry-related
# errors.
SENTRYLOGGER = object()


@moduleproperty
@lru_cache(1)
def client(self):
    import raven
    if 'dsn' in conf:
        client = raven.Client(**conf)
        client.processors += (
            'raven_sanitize_openerp.OpenerpPasswordsProcessor',
        )
        return client
    else:
        return None


@modulemethod
def patch_logging(self, override=True):
    '''Patch openerp's logging.

    :param override: If True suppress all normal logging.  All logs will be
           sent to the Sentry instead of being logged to the console.  If
           False, extends the loogers to sent the errors to the Sentry but
           keep the console log as well.

    The Sentry will only receive the error-level messages.

    '''
    import logging
    from raven.handlers.logging import SentryHandler as Base
    from openerp.netsvc import init_logger
    init_logger()

    class SentryHandler(Base):
        def _handle_cli_tags(self, record):
            import sys
            from openerp.release import version
            tags = setdefaultattr(record, 'tags', {})
            tags['odoo-version'] = version
            cmd = sys.argv[0] if sys.argv else None
            if cmd:
                import os
                cmd = os.path.basename(cmd)
            if cmd:
                tags['cmd'] = cmd

        def _handle_http_tags(self, record, request):
            tags = setdefaultattr(record, 'tags', {})
            ua = request.user_agent
            if ua:
                tags['os'] = ua.platform.capitalize()
                tags['browser'] = ua.browser.capitalize() + ' ' + ua.version
            username = getattr(request, 'session', {}).get('login', None)
            if username:
                tags['username'] = username

        def _handle_db_tags(self, record, request):
            db = getattr(request, 'session', {}).get('db', None)
            if db:
                tags = setdefaultattr(record, 'tags', {})
                tags['db'] = db

        def _handle_http_request(self, record):
            try:
                from openerp.http import request
                httprequest = getattr(request, 'httprequest', None)
                if httprequest:
                    data = setdefaultattr(record, 'data', {})
                    # Make a copy of the WSGI environment as extra data, but
                    # remove cookies and wsgi. special keys.
                    data['wsgi'] = {
                        key: value
                        for key, value in httprequest.environ.items()
                        if key != 'HTTP_COOKIE'
                        if not key.startswith('wsgi.')
                        if not key.startswith('werkzeug.')
                    }
                    self._handle_http_tags(record, httprequest)
                    self._handle_db_tags(record, httprequest)
            except ImportError:
                pass
            except RuntimeError:
                # When upgrading a DB the request may exists but the bound to
                # it does not.
                pass

        def can_record(self, record):
            res = super(SentryHandler, self).can_record(record)
            if not res:
                return False
            exc_info = record.exc_info
            if not exc_info:
                return res
            from openerp.exceptions import Warning
            ignored = (Warning, )
            try:
                from openerp.exceptions import RedirectWarning
                ignored += (RedirectWarning, )
            except ImportError:
                pass
            try:
                from openerp.exceptions import except_orm
            except ImportError:
                from openerp.osv.orm import except_orm
            ignored += (except_orm, )
            try:
                from openerp.osv.osv import except_osv
                ignored += (except_osv, )
            except ImportError:
                pass
            _type, value, _tb = exc_info
            return not isinstance(value, ignored)

        def emit(self, record):
            self._handle_cli_tags(record)
            self._handle_http_request(record)
            return super(SentryHandler, self).emit(record)

    client = self.client
    if not client:
        return

    level = conf.get('report_level', 'ERROR')

    def sethandler(logger, override=override, level=level):
        handler = SentryHandler(client=client)
        handler.setLevel(getattr(logging, level.upper(), logging.ERROR))
        if override or not logger.handlers:
            logger.handlers = [handler]
        else:
            logger.handlers.append(handler)

    for name in (None, 'openerp'):
        logger = logging.getLogger(name)
        sethandler(logger)


del moduleproperty, modulemethod, lru_cache
