#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoeuf.models
# ---------------------------------------------------------------------
# Copyright (c) 2016 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2016-08-24

'''Transparently import models.

Example usage (in xoeuf' shell)::

    >>> from xoeuf.pool import mercurio as db
    >>> from xoeuf.models import AccountAccount

    # We need a 'self' (and possible cr, uid) in the context of any method
    # call to model.
    >>> AccountAccount.search([])   # doctest: +ELLIPSIS
    Traceback (...)
    ...
    AttributeError: search

    >>> db.salt_shell(_='mail.mail')  # inject a 'self'

    >>> AccountAccount.search([], limit=1)  # doctest: +ELLIPSIS
    account.account(...)


'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


import re
from os.path import splitext
from types import ModuleType

import openerp.models


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


class ModelProxy(ModuleType):
    def __init__(self, name):
        self.__model = _get_model(name)
        self.__env = None

    def __getattr__(self, attr):
        if self.__env is None:
            import sys
            f = sys._getframe(1)
            try:
                this, tries = None, 5
                while this is None and tries and f:
                    this = f.f_locals.get('self', None)
                    if not isinstance(this, openerp.models.Model):
                        this = cr = uid = None
                    elif not hasattr(this, 'env'):
                        # We still need to support possible old-API methods
                        cr = f.f_locals.get('cr', None)
                        uid = f.f_locals.get('uid', None)
                        context = f.f_locals.get('context', None)
                        this = this.browse(cr, uid, context=context)
                    f = f.f_back
                    tries -= 1
                if this is not None:
                    self.__env = this.env
                else:
                    raise AttributeError(attr)
            finally:
                f = None
        return getattr(self.__env[self.__model], attr)


def _get_model(name):
    if '.' in name:
        return name
    words, last = [], 0
    for i, match in enumerate(UPPERS.finditer(name)):
        pos = match.start()
        if i == 0:
            assert pos == 0, 'The first char must an upper case'
        else:
            words.append(name[last:pos].lower())
        last = pos
    words.append(name[last:].lower())
    return '.'.join(words)


UPPERS = re.compile('[A-Z]')

__path__ = [splitext(__file__)[0]]


import sys
sys.path_hooks.append(ModelImporter.hook)
del sys, ModelImporter, splitext, re
