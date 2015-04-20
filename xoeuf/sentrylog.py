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

This module will gracefully do nothing if raven is not installed.

To configure, simply call the

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoutil.functools import lru_cache
from xoutil.modules import moduleproperty, modulemethod

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
    '''Patch the both logging and openerp's logging.

    :param override: If True suppress all normal logging.  All logs will be
           sent to the Sentry instead of being logged to the console.  If
           False, extends the to sent the errors to the Sentry but keep the
           console log as well.

    The Sentry will only receive the error-level messages.

    '''
    import logging
    from openerp.netsvc import init_logger
    init_logger()
    client = self.client
    if not client:
        return

    class SentryHandler(logging.Handler):
        def emit(self, record):
            from xoutil.context import context
            if SENTRYLOGGER not in context:
                with context(SENTRYLOGGER):
                    if record.exc_info:
                        client.captureException(exc_info=record.exc_info)
                    else:
                        client.captureMessage(record.getMessage(),
                                              stack=True)

    def sethandler(logger, override=override):
        handler = SentryHandler()
        handler.setLevel(logging.ERROR)
        if override or not logger.handlers:
            logger.handlers = [handler]
        else:
            logger.handlers.append(handler)

    for name in (None, 'openerp'):
        logger = logging.getLogger(name)
        sethandler(logger)


del moduleproperty, modulemethod, lru_cache
