#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

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
                        absolute_import)

from xoutil.names import strlist as strs


__all__ = strs('integrate_extensions', 'fix_documentations')

del strs


def integrate_extensions():
    '''Integrate all functions defined in ``xoeuf.osv.model_extensions`` as new
    `BaseModel` methods and operators.

    It can be used in Python modules like::

      from xoeuf.osv.improve import integrate_extensions as _ie
      _ie(); del _ie

    '''
    from types import FunctionType
    from xoeuf.odoo.models import BaseModel
    from xoeuf.models import extensions as model_extensions
    from xoeuf.api import guess as adapt

    def fixname(name):
        'Convert operator names, just in case'
        op_prefix = 'operator__'
        c = len(op_prefix)
        return '__%s__' % name[c:] if name.startswith(op_prefix) else name

    if not model_extensions.INTEGRATED:
        model_extensions.INTEGRATED = True
        for name in dir(model_extensions):
            value = getattr(model_extensions, name)
            if type(value) is FunctionType:
                setattr(BaseModel, fixname(name), adapt(value))


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
