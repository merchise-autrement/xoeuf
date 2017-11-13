#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

import xoeuf.odoo.osv.fields as fields7

if not hasattr(fields7, 'timedelta'):

    def ensure_float(x):
        from datetime import timedelta
        if isinstance(x, timedelta):
            x = x.total_seconds()
        return x

    _base = fields7.float

    class timedelta(_base):
        _type = 'timedelta'

        def __init__(self, **args):
            _base.__init__(self, **args)
            _lambda = self._symbol_f
            self._symbol_f = lambda x: _lambda(ensure_float(x))
            self._symbol_set = (self._symbol_c, self._symbol_f)

        def to_field_args(self):
            raise NotImplementedError(
                "fields.timdelta is only supported in the new API."
            )

    fields7.timedelta = timedelta
    del timedelta

del fields7
