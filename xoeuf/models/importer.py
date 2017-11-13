#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Integrate both Model Definition classes with Models.

Usage::

   >>> class M(xoeuf.models.importer.ImportNamespace):
   ...     from openerp.addons.base.res.res_partner import res_partner as Partner

   # M.defs.Partner will be the model definition class

   # M(r).Partner will be the model as seen by registry r.  If r is None, i.e
   # M().Partner or M.Partner, we search the frame stack to find a 'self' with
   # the registry to get the model.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoeuf.odoo import models
from xoutil.eight.meta import metaclass
try:
    from xoutil.future.types import SimpleNamespace
except ImportError:
    from xoutil.eight.types import SimpleNamespace

from . import get_modelname
from . import _proxy

__all__ = ['ImportNamespace']


class _ImportNamespaceType(type):
    def __new__(cls, name, bases, attrs):
        import warnings
        warnings.warn(
            'The entire xoeuf.models.importer is now deprecated. '
            'Please use xoeuf.models.proxy directly.',
            DeprecationWarning
        )
        definitions = SimpleNamespace()
        proxies = {}
        for attr, val in attrs.items():
            if isinstance(val, type) and issubclass(val, models.BaseModel):
                setattr(definitions, attr, val)
                proxies[attr] = _proxy.ModelProxy(get_modelname(val))
        attrs = dict(proxies, defs=definitions)
        return super(_ImportNamespaceType, cls).__new__(
            cls,
            name,
            bases,
            attrs
        )


class ImportNamespace(metaclass(_ImportNamespaceType)):
    pass
