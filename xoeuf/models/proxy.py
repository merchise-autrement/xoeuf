#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Transparently import models.

Example usage (in xoeuf' shell)::

    $ xoeuf shell
    >>> from xoeuf.models.proxy import AccountAccount

    # We need a 'self' (and possible cr, uid) in the context of any method
    # call to model.
    >>> AccountAccount.search([])   # doctest: +ELLIPSIS
    Traceback (...)
    ...
    AttributeError: search


    $ xoeuf shell -d somedb
    >>> from xoeuf.models.proxy import ResUsers as User

    >>> User.search([], limit=1)  # doctest: +ELLIPSIS
    res.users(...)


'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


import re
from os.path import splitext
from types import ModuleType
from . import _proxy


class ModelImporter(object):
    @classmethod
    def hook(cls, path):
        if path == __path__[0]:
            return cls
        else:
            raise ImportError

    @classmethod
    def find_module(cls, name, path=None):
        base, _sep, name = name.rpartition(str('.'))
        if base == __name__:
            return cls(name, base)
        else:
            msg = 'We can not load "%s" outside "%s".'
            raise ImportError(msg % (name, __name__))

    def load_module(self, fullname):
        '''Returns the loaded module or raises an exception.'''
        import sys
        self._check(fullname)
        res = sys.modules.get(fullname, None)
        if res is None:
            res = ModelProxy(fullname.rsplit(str('.'), 1)[-1])
            res.__path__ = __path__
            sys.modules[fullname] = res
        return res

    def __init__(self, name, base):
        self.__name = name
        self.__base = base

    @property
    def fullname(self):
        sep = str('.')
        return sep.join((self.__base, self.__name))

    def _check(self, fullname, asserting=False):
        'Check `fullname` and raise an error if not correct.'
        local = self.fullname
        if local == fullname:
            return fullname
        elif asserting:
            return False
        else:
            msg = 'Using loader for "%s" to manage "%s"!'
            raise ImportError(msg % (self.name, fullname))


class ModelProxy(ModuleType, _proxy.ModelProxy):
    def __init__(self, name):
        ModuleType.__init__(self, name)
        _proxy.ModelProxy.__init__(self, name)


__path__ = [splitext(__file__)[0]]


import sys
sys.path_hooks.append(ModelImporter.hook)
del sys, ModelImporter, splitext, re
