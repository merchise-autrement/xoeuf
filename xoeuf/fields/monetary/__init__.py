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

from xoeuf.odoo.release import version_info as ODOO_VERSION_INFO

if ODOO_VERSION_INFO[0] == 8:
    from ._v8 import Monetary as Base
else:
    from xoeuf.odoo.fields import Monetary as Base


class Monetary(Base):
    _slots = {
        'concrete': False,
    }

    def convert_to_cache(self, value, record, validate=True):
        from xoutil.dim.currencies import currency as Currency
        value = super(Monetary, self).convert_to_cache(value, record, validate=validate)
        # FIXME:  Ensure to resolve currency for compute and or related.
        if self.concrete and record[self.currency_field].name:
            currency = Currency(record[self.currency_field].name)
            return value * currency
        else:
            return value
