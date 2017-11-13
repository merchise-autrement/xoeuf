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

from operator import attrgetter
from xoeuf.odoo.fields import Field

import xoeuf.odoo.osv.fields as fields7

if not hasattr(fields7, 'monetary'):
    import __builtin__

    class monetary(fields7.float):
        _type = 'monetary'
        _symbol_set = ('%s', lambda x: __builtin__.float(x or 0.0))
        _symbol_get = lambda self, x: x or 0.0  # noqa: E731

        def to_field_args(self):
            raise NotImplementedError(
                "fields.monetary is only supported in the new API, "
                "but you can use widget='monetary' in client-side views"
            )

    fields7.monetary = monetary
    del monetary

del fields7


class Monetary(Field):
    """The decimal precision and currency symbol are taken from the attribute

    :param currency_field: name of the field holding the currency this monetary
                           field is expressed in (default: `currency_id`)
    """
    type = 'monetary'
    _slots = {
        'currency_field': None,
        'group_operator': None,         # operator for aggregating values
    }

    def __init__(self, string=None, currency_field=None, **kwargs):
        super(Monetary, self).__init__(
            string=string,
            currency_field=currency_field,
            **kwargs
        )

    _related_currency_field = property(attrgetter('currency_field'))
    _related_group_operator = property(attrgetter('group_operator'))

    _description_currency_field = property(attrgetter('currency_field'))
    _description_group_operator = property(attrgetter('group_operator'))

    _column_currency_field = property(attrgetter('currency_field'))
    _column_group_operator = property(attrgetter('group_operator'))

    def _setup_regular(self, env):
        super(Monetary, self)._setup_regular(env)
        model = env[self.model_name]
        if not self.currency_field:
            # pick a default, trying in order: 'currency_id', 'x_currency_id'
            if 'currency_id' in model._fields:
                self.currency_field = 'currency_id'
            elif 'x_currency_id' in model._fields:
                self.currency_field = 'x_currency_id'
        assert self.currency_field in model._fields, \
            "Field %s with unknown currency_field %r" % (self, self.currency_field)   # noqa

    def convert_to_cache(self, value, record, validate=True):
        currency = record[self.currency_field]
        if currency:
            return currency.round(float(value or 0.0))
        return float(value or 0.0)
