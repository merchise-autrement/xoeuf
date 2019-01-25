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

from xoeuf.odoo import fields, models, _


def get_mixin_descendants(pool, mixin):
    ''' Get the models that inherit from `mixin`.

    :param mixin: mixin name to get it descendants.

    '''
    for model_name in pool.descendants([mixin], '_inherit'):
        if not pool[model_name]._abstract:
            yield model_name


class TypedReference(fields.Reference):
    '''A reference field filtered by type (mixin).

    Many2one equivalent recordset.

    '''
    type = 'reference'
    _slots = {
        'mixin': None,
    }

    def __init__(self, mixin=fields.Default, **kwargs):
        super(TypedReference, self).__init__(
            mixin=mixin,
            **kwargs
        )

    def new(self, **kwargs):
        # Pass original args to the new one.  This ensures that the
        # mixin arg is present.  In odoo/models.py, Odoo calls
        # this `new()` without arguments to duplicate the fields from parent
        # classes.
        kwargs = dict(self.args, **kwargs)
        return super(TypedReference, self).new(**kwargs)

    def _setup_regular_base(self, model):
        def selection(model):
            return [
                (model_name, _(model.env[model_name]._description or model_name))
                for model_name in get_mixin_descendants(model.pool, self.mixin)
            ]
        if self.selection:
            descendants = [val for val, string in selection(model)]
            for val in self.get_values(model.env):
                if val not in descendants:
                    raise ValueError(
                        _("Wrong value for %s: %r") % (self, val)
                    )
        else:
            self.selection = selection
        return super(TypedReference, self)._setup_regular_base(model)
