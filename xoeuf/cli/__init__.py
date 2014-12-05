#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoeuf.cli
#----------------------------------------------------------------------
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


import logging
_logger = logging.getLogger(__name__)

DEFAULT_COMMAND = str('server')

# Makes sure modules are patched before any command-related code is
# invoked.
from openerp.netsvc import init_logger
init_logger()

from xoeuf.modules import patch_modules
patch_modules()


import openerp
if openerp.release.version_info < (8, 0, 0):
    from openerp.modules.loading import open_openerp_namespace
    import openerp.addons.base  # Needed to bootstrap base, otherwise addons
                                # that import openerp.addons.base fail to
                                # load.

    # XXX: OpenERP's own commands discovery inside addons is totally flawed.
    # Trying `openerp-server some-command` fails to load any addon that
    # imports stuff without the "openerp.".  So let's do the open namespace
    # now
    open_openerp_namespace()


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
            import sys
            from importlib import import_module
            from openerp.cli import commands
            from openerp.modules.module import get_modules
            from openerp.modules.module import initialize_sys_path
            cls._discover_addons_path()
            initialize_sys_path()
            modules = get_modules()
            for addon in modules:
                module_name = str('openerp.addons.' + addon)
                if not sys.modules.get(module_name):
                    try:
                        import_module(module_name)
                    except Exception:
                        import traceback
                        _logger.critical('Could not load module %s', addon)
                        traceback.print_exc()
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


from xoutil.cli import Command as BaseCommand

BaseCommand.register(CommandsProxy)
BaseCommand.set_default_command(DEFAULT_COMMAND)


class Command(BaseCommand):
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
from . import shell as _shell
from . import secure as _secure
del _, _shell, _secure
