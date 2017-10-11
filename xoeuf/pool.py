#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''A smart pool of OpenERP database connections managed by Xœuf.

This is mainly used in a shell, although can be used in any service.

All database names are exported as attributes from this modules.

Each database can be imported as "from xoeuf.pool import <db-name>".

If "from xoeuf.pool import test" (or any other name starting with prefix
``test``) is executed and a data-base with the given name doesn't exists, then
one in registry is returned.

When all existing data-bases are exhausted for testing purposes, standard
error will be re-raised.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


from os.path import splitext
from xoutil.names import strlist as slist
from xoutil.modules import modulemethod


__docstring_format__ = 'rst'
__author__ = 'med'


def db_names():
    '''Return all `OpenERP` data-base names.

    See module documentation for more info.

    '''
    # TODO: Register mechanisms for remote hosts
    from xoeuf.osv.registry import Registry
    return Registry.get_all_db_names()


@modulemethod
def __dir__(self):
    res = [self.db_names.__name__]
    res.extend(self.db_names())
    return res


class ModuleManager(object):
    '''Import Hooks for OpenERP databases.

    A database finder and loader as a module using PEP-302 (New Import
    Hooks) protocol.

    Import Hook for OpenERP databases.

    '''
    default_context = {}
    test_db_index = 0    # Index for test databases

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
        '''Return a loader object if the module was found, or None if not.

        If it raises an exception, it will be propagated to the caller,
        aborting the import.

        '''
        base, _sep, db_name = name.rpartition(str('.'))
        if base == __name__:
            return cls(db_name, base)
        else:
            msg = 'We can not load DB "%s" outside "%s".'
            raise ImportError(msg % (db_name, __name__))

    def load_module(self, fullname):
        '''Returns the loaded module or raises an exception.'''
        import sys
        self._check(fullname)
        res = sys.modules.get(fullname, None)
        if res is None:
            from psycopg2 import OperationalError
            try:
                res = self._load_module()
            except OperationalError:
                res = self._load_module(test_db=self.db_name)
                if not res:
                    raise
            sys.modules[fullname] = res
        else:
            assert res is self.registry
        return res

    def get_filename(self, fullname):
        'Return the value used in attribute `__file__` for a DB module.'
        assert self._check(fullname, asserting=True)
        return str('<%s>' % fullname)

    def _load_module(self, test_db=None):
        'Internal method for loading a DB module,'
        from xoeuf.osv.registry import Registry
        if test_db is None:
            db_name = self.db_name
        else:
            dbs = db_names()
            if test_db.startswith('test') and self.test_db_index < len(dbs):
                db_name = dbs[self.test_db_index]
                self.test_db_index += 1
            else:
                db_name = None
        if db_name:
            res = Registry(db_name, **self.default_context)
            self.registry = res
            self._inner = self.registry.wrapped      # Force check database
            res.__loader__ = self
            res.__name__ = self.db_name
            res.__file__ = self.get_filename(self.fullname)
            res.__all__ = slist('db_name', 'uid', 'context', 'connection',
                                'cursor', 'models')
            return res
        else:
            return None

    @property
    def fullname(self):
        'Return full qualified name.'
        sep = str('.')
        return sep.join((self.base, self.db_name))

    def _check(self, fullname, asserting=False):
        'Check `fullname` and raise an error if not correct.'
        local = self.fullname
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
del sys, ModuleManager, splitext, modulemethod
