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
from xoutil.names import strlist as slist


__docstring_format__ = 'rst'
__author__ = 'med'


def db_names():
    '''Each database can be imported as "from xoeuf.pool import <db-name>".
    '''
    # TODO: Register mechanisms for remote hosts
    from xoeuf.osv.registry import Registry
    return Registry.get_all_db_names()


class ModuleManager(object):
    '''Import Hooks for OpenERP databases.
    '''

    '''A database finder and loader as a module using PEP-302 (New Import
    Hooks) protocol.

    Import Hook for OpenERP databases.

    '''
    default_context = {}

    def __init__(self, db_name, base):
        '''Create the Module Loader.'''
        self.db_name = db_name
        self.base = base

    @classmethod
    def hook(cls, path):
        '''Return class a the module finder.'''
        if path == __path__[0]:
            return cls
        else:
            raise ImportError

    @classmethod
    def find_module(cls, name, path=None):
        base, _sep, db_name = name.rpartition(str('.'))
        if base == __name__:
            return cls(db_name, base)
        else:
            msg = 'We can not load DB "%s" outside "%s".' % (db_name, __name__)
            raise ImportError(msg)

    def load_module(self, fullname):
        import sys
        self._check(fullname)
        res = sys.modules.get(fullname, None)
        if res is None:
            from xoeuf.osv.registry import Registry
            res = Registry(self.db_name, **self.default_context)
            self.registry = res
            self._inner = self.registry.wrapped      # Force check database
            res.__loader__ = self
            res.__name__ = self.db_name
            res.__file__ = self.get_filename(fullname)
            res.__all__ = slist('db_name', 'uid', 'context', 'connection',
                                'cursor', 'models')
            sys.modules[str('.'.join((__name__, self.db_name)))] = res
        else:
            assert res is self.registry
        return res

    def get_filename(self, fullname):
        assert self._check(fullname, asserting=True)
        return str('<%s>' % fullname)

    def _check(self, fullname, asserting=False):
        sep = str('.')
        local = sep.join((self.base, self.db_name))
        if local == fullname:
            return fullname
        elif asserting:
            return False
        else:
            msg = 'Using loader for DB "%s" for manage "%s"!'
            raise ImportError(msg % (self.db_name, fullname))


__path__ = [splitext(__file__)[0]]


import sys
sys.path_hooks.append(ModuleManager.hook)
del sys, ModuleManager, splitext
