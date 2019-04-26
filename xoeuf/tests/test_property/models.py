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

import logging

from xoeuf import models, fields, api
from xoeuf.odoo.tools.safe_eval import safe_eval

logger = logging.getLogger(__name__)
del logging


class ValueMixin(models.AbstractModel):
    _name = 'test.property.valuemixin'

    value = fields.Char()

    @fields.Property
    def inverted(self):
        return ''.join(reversed(self.value)) if self.value else self.value

    @inverted.setter
    def inverted(self, value):
        self.value = ''.join(reversed(value)) if value else value

    @inverted.deleter
    def inverted(self):
        self.value = None

    @inverted.onsetup
    def inverted(field, model):
        type(model).inverted_setup = True

    @fields.Property(memoize=True)
    def memoized_object(self):
        return object()

    @memoized_object.setter
    def memoized_object(self, value):
        pass

    @memoized_object.deleter
    def memoized_object(self):
        pass

    @fields.Property
    def new_object(self):
        return object()


class ObjectMixin(models.AbstractModel):
    _name = 'test.property.object'

    thing = fields.Char(
        # This stores the representation (result of repr) of the value.  You
        # may use `result` to read/update this field.  If you use Odoo's
        # write/create, or set this field directly you MUST ensure to pass the
        # result of `repr()`.  The `write/create` methods below ensure the
        # writing to 'result' works.
    )

    @api.multi
    def write(self, values):
        # Makes writing to 'result' work.  If you pass both 'value' and
        # 'result', 'result' wins.
        if 'result' in values:
            values['thing'] = repr(values.pop('result'))
        return super(ObjectMixin, self).write(values)

    @api.model
    def create(self, values):
        # Makes writing to 'result' work.  If you pass both 'value' and
        # 'result', 'result' wins.
        if 'result' in values:
            values['thing'] = repr(values.pop('result'))
        return super(ObjectMixin, self).create(values)

    def _get_result(self):
        return safe_eval(self.thing) if self.thing else self.thing

    def _set_result(self, value):
        self.thing = repr(value)

    def _del_result(self):
        self.thing = None

    result = fields.Property(
        getter=_get_result,
        setter=_set_result,
        deleter=_del_result,
    )
    del _get_result, _set_result, _del_result


class Value(models.Model):
    _name = 'test.property.value'
    _inherit = ['test.property.valuemixin', 'test.property.object']


class IdentifiedValue(models.Model):
    _name = 'test.property.inherits'
    _inherits = {'test.property.value': 'value_id'}

    name = fields.Char(required=True)
    value_id = fields.Many2one(
        'test.property.value',
        required=True,
        ondelete='cascade'
    )

    _sql_constrains = [
        ('unique_name', 'UNIQUE(name)', 'Names cannot be repeated'),
        ('single_value', 'UNIQUE(value_id)', 'A value can only appear once'),
    ]


class DelegatedValue(models.Model):
    _name = 'test.property.delegated'
    name = fields.Char(required=True)
    value_id = fields.Many2one(
        'test.property.value',
        required=True,
        ondelete='cascade',
        delegate=True,
    )

    _sql_constrains = [
        ('unique_name', 'UNIQUE(name)', 'Names cannot be repeated'),
        ('single_value', 'UNIQUE(value_id)', 'A value can only appear once'),
    ]
