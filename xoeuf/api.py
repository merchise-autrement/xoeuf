#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoeuf.api
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-01-01

'''Odoo API bridge.

Eases the task of writing modules which are compatible with both Odoo and
OpenERP.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

try:
    from openerp.api import guess
except ImportError:
    guess = lambda f: f

try:
    from openerp.api import Environment
except ImportError:
    Environment = None


def contextual(func):
    '''Decorate a function to run in a proper Odoo environment.

    You should decorate every function that represents an "entry point" for
    working with the ORM.  If Odoo is not installed, the original function is
    returned unchanged.  However, if Odoo is present a proper
    `Environment`:class: is entered upon calling the function.

    Every command in the `xoeuf.cli`:mod: is automatically decorated.

    '''
    if Environment is None:
        return func

    def inner(*args, **kwargs):
        with Environment.manage():
            return func(*args, **kwargs)
    return inner


try:
    from openerp.api import v8, v7  # noqa
except ImportError:
    from xoutil.decorator import aliases

    @aliases('v8', 'v7')
    def _version_X(f):
        '''Mimic the `openerp.api.v8`:func: and `openerp.api.v7`:func: behaviour in
        Odoo.

        Odoo has introduced a new API for model methods.  Basically it has
        removed the ``(cr, uid, ..., context=None)`` boilerplate.  See the
        ``api.py`` file in the branch 8.0 of Odoo for details.

        To ease the upgrade path for modules, they allow to keep using both
        signatures.  Furthermore a model may provide two different
        implementations for both versions by using the `api.v8
        <openerp.api.v8>`:func: and `api.v7 <openerp.api.v7>`:func: decorators
        like in::

           @api.v8
           def browse(self, ids=None):
               pass

           @api.v7
           def browse(self, cr, uid, ids, context=None):
               pass

        When running Odoo, these are actually aliases to ``openerp.api.v8()``
        and ``openerp.api.v7()``.

        When running OpenERP, return the decorated function unchanged.

        .. warning:: The order is very important.

           Since we simply return the function unchanged when running OpenERP
           you must place the ``v7`` after the ``v8``, for the module to work
           properly.

        '''
        return f


try:
    from xoutil.decorator.meta import decorator
    from openerp import api as _odoo_api
    multi = _odoo_api.multi

    @decorator
    def take_one(func, index=0, warn=True):
        '''A weaker version of `api.one`.

        The decorated method will receive a recordset with a single record
        just like `api.one` does.

        The single record will be the one in the `index` provided in the
        decorator.

        This means the decorated method *can* make the same assumptions about
        its `self` it can make when decorated with `api.one`.  Nevertheless
        its return value *will not* be enclosed in a list.

        If `warn` is True and more than one record is in the record set, a
        warning will be issued.

        If the given recordset has no `index`, raise an IndexError.

        '''
        from functools import wraps
        from xoutil import logger

        @multi
        @wraps(func)
        def inner(self):
            if self[index] != self:
                # More than one item was in the recordset.
                if warn:
                    logger.warn('More than one record for function %s',
                                func, extra=self)
                self = self[index]
            return func(self)
        return inner

except ImportError:
    multi = lambda f: f
    take_first = lambda *args, **kwargs: (lambda f: f)
