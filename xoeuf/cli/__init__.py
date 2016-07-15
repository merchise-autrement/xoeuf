#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoeuf.cli
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise and Contributors
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 26 avr. 2013

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)


DEFAULT_COMMAND = str('server')

# Makes sure modules are patched before any command-related code is
# invoked.
from xoeuf.modules import patch_modules
patch_modules()


class CommandsProxy(object):
    '''Define a proxy to register all OpenERP CLI commands to "xoutil.cli".

    '''
    __new__ = None  # Can't be instantiated

    @classmethod
    def __commands__(cls):
        '''Get all OpenERP registered commands.

        Discard add-ons that raise errors when importing them.

        '''
        name = '__commands_cache__'
        res = getattr(cls, name, None)
        if not res:
            try:
                from openerp.cli import commands
            except ImportError:
                # future-proof
                from openerp.cli.command import commands
            from openerp.netsvc import init_logger
            init_logger()
            from openerp.modules.module import initialize_sys_path
            cls._discover_addons_path()
            initialize_sys_path()
            res = commands
            setattr(cls, name, res)
        return res.values()

    @staticmethod
    def _discover_addons_path():
        import sys
        args = sys.argv[1:]
        prefix = '--addons-path='
        addons_path = next((a for a in args if a.startswith(prefix)), None)
        if addons_path:
            from openerp.tools import config
            config.parse_config([addons_path])


try:
    from xoutil.eight.meta import metaclass
except ImportError:
    from xoutil.objects import metaclass

from xoutil.cli import Command as BaseCommand

BaseCommand.register(CommandsProxy)
BaseCommand.set_default_command(DEFAULT_COMMAND)


class CommandType(type(BaseCommand)):
    def __new__(cls, name, bases, attrs):
        from xoeuf.api import contextual
        run = attrs.get('run', None)
        if run:
            attrs['run'] = contextual(run)
        return super(CommandType, cls).__new__(cls, name, bases, attrs)


class Command(metaclass(CommandType), BaseCommand):
    @staticmethod
    def invalidate_logging(base=None):
        '''Force the logger `base` to report only CRITICAL messages.

        :param base: The name of logger to invalidate.  None is the root
                     logger *and* the "openerp" logger.

        '''
        import logging
        logger = logging.getLogger(base)
        logger.setLevel(logging.CRITICAL)
        if not base:
            Command.invalidate_logging('openerp')


del BaseCommand


# TODO: Loader?
from . import mailgate as _
from . import migration
from . import shell as _shell
from . import secure as _secure
from . import addons as _addons
del _, _shell, _secure, _addons
