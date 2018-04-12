#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Integrate both Model Definition classes with Models.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoeuf.odoo import models
from xoutil.eight.meta import metaclass
from xoutil.future.types import SimpleNamespace

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
