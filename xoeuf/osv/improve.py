# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoeuf.osv.improve
#----------------------------------------------------------------------
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# @created: 2013-11-27

'''Xœuf extensions for Open Object (OpenERP) models.

This module define functions to improve `OpenERP` object services (OSV) with
some extensions related to model programming or shell (Command Line Interface)
use:

- :func:`integrate_extensions` -  integrate all methods defined as
  functions in module ``xoeuf.osv.model_extensions`` to `ModelBase`.

- :func:`fix_documentations` - Fixes all models documentation from a given
  Xœuf registry (`OpenERP` data-base).

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)

from xoutil.names import strlist as strs


__all__ = strs('integrate_extensions', 'fix_documentations')

del strs


def integrate_extensions():
    '''Integrate all functions defined in ``xoeuf.osv.model_extensions`` as
    new `ModelBase` methods.

    It can be used in Python modules like::

       from xoeuf.osv.improve import integrate_extensions as _; _(); del _

    :return: extended `BaseModel`

    '''
    from types import FunctionType
    from openerp.osv.orm import BaseModel
    from xoeuf.osv import model_extensions
    if not model_extensions.INTEGRATED:
        model_extensions.INTEGRATED = True
        for name in dir(model_extensions):
            value = getattr(model_extensions, name)
            if type(value) is FunctionType:
                setattr(BaseModel, name, value)
    return BaseModel


def fix_documentations(db):
    '''Fixes all models documentation from a given data-base.

    This function may be useful for shells or Python Command Line Interfaces
    (CLI).

    '''
    from xoutil.objects import (fix_class_documentation,
                                fix_method_documentation)
    if not getattr(db, '__documentation_fixed', False):
        setattr(db, '__documentation_fixed', True)
        ignore = ('object', 'AbstractModel', 'BaseModel', 'Model',
                  'TransientModel')
        models = db.models
        for model in models.values():
            cls = model.__class__
            fix_class_documentation(cls, ignore=ignore, deep=10)
            for attr_name in dir(cls):
                fix_method_documentation(cls, attr_name, deep=3)
