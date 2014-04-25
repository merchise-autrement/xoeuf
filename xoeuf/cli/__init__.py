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


DEFAULT_COMMAND = str('server')


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
            cls._discover_addons_path()
            modules = get_modules()
            for addon in modules:
                module_name = str('openerp.addons.' + addon)
                if module_name not in sys.modules:
                    try:
                        import_module(module_name)
                    except Exception as _error:
                        pass
                        #print('ERROR:', type(_error), _error, file=sys.stderr)
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


from xoutil.cli import Command

Command.register(CommandsProxy)
Command.set_default_command(DEFAULT_COMMAND)

del Command


# TODO: Loader?
from . import mailgate as _
del _
