#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoeuf.api
# ---------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise and Contributors
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

from xoutil.decorator.meta import decorator

try:
    from openerp import api as _odoo_api
except ImportError:
    from odoo import api as _odoo_api

from xoutil.modules import copy_members as _copy_python_module_members
this = _copy_python_module_members(_odoo_api)
del _copy_python_module_members


def contextual(func):
    '''Decorate a function to run within a proper Odoo environment.

    You should decorate every function that represents an "entry point" for
    working with the ORM.  A proper `Environment`:class: is entered upon
    calling the function.

    '''
    def inner(*args, **kwargs):
        with _odoo_api.Environment.manage():
            return func(*args, **kwargs)
    return inner


@decorator
def take_one(func, index=0, warn=True, strict=False):
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

    If `strict` is True and there's more than one record (or none), raise a
    ValueError.

    .. note:: Odoo's ``ensure_one()`` raises another kind of error.

    If the given recordset has no `index`, raise an IndexError.

    '''
    from functools import wraps
    import logging
    logger = logging.getLogger(__name__)
    del logging

    @_odoo_api.multi
    @wraps(func)
    def inner(self):
        if self[index] != self:
            # More than one item was in the recordset.
            if strict:
                raise ValueError(
                    'More than one record for function %s' % func.__name__
                )
            elif warn:
                logger.warn('More than one record for function %s',
                            func, extra=self)
            self = self[index]
        return func(self)
    return inner


def mimic(original):
    '''Apply the API guess of `original` to the decorated function.

    Usage::

       def f1(self, cr, uid, ids, context=None):
           # Actually any valid signature

       @api.mimic(f1)
       def f2(*args, **kwargs):
           pass

    '''
    import types
    method = _odoo_api.guess(original)
    # Odoo stores the decorator in the _api attribute.  But Odoo 10 only
    # stores the name of the API method.
    decorator = method._api
    if isinstance(decorator, types.FunctionType):
        return decorator
    else:
        return getattr(_odoo_api, decorator)
