#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoeuf.pool
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 30 avr. 2013

'''A smart pool of OpenERP database connections managed by Xœuf.

This is mainly used in a shell, although can be used in any service.

All database names are exported as attributes from this modules.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)


from os.path import splitext


__docstring_format__ = 'rst'
__author__ = 'med'


def db_names():
    '''Each database can be imported as "from xoeuf.pool import <db-name>".
    '''
    # TODO: Register mechanisms for remote hosts
    from xoeuf.osv.registry import Registry
    return Registry.get_all_db_names()


class ModuleHook(object):
    '''Import Hooks for OpenERP databases.
    '''
    def __new__(cls, path):
        '''This class is not instantiable.'''
        if path == __path__[0]:
            return cls
        else:
            raise ImportError

    @classmethod
    def find_module(cls, name, path=None):
        base, _sep, db_name = name.rpartition(str('.'))
        if base == __name__:
            from xoeuf.osv.registry import ModuleLoader
            return ModuleLoader(db_name, base)
        else:
            msg = 'We can not load DB "%s" outside "%s".' % (db_name, __name__)
            raise ImportError(msg)


__path__ = [splitext(__file__)[0]]

import sys
sys.path_hooks.append(ModuleHook)
del sys, ModuleHook, splitext
