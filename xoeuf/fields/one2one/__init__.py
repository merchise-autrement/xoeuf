#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from __future__ import (
    division as _py3_division,
    print_function as _py3_print,
    absolute_import as _py3_abs_import,
)

from odoo.fields import Many2one


class One2one(Many2one):
    """A classical one-2-one field.

    This is basically syntax sugar over a `~odoo.fields.Many2one`:class: with:

    - `ondelete` set to ``'cascade'`` by default;

    - a SQL uniqueness constraint in the model.

    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("ondelete", "cascade")
        super(One2one, self).__init__(*args, **kwargs)

    def setup_full(self, model):
        res = super(One2one, self).setup_full(model)
        if self.related is None:
            constraint_name = "unique_{model}_{target}".format(
                model=model._name.replace(".", "_"),
                target=self.comodel_name.replace(".", "_"),
            )
            constraints = type(model)._sql_constraints
            exists = any(True for name, _, _ in constraints if name == constraint_name)
            if not exists:
                constraints.append(
                    (
                        constraint_name,
                        "unique ({field})".format(field=self.name),
                        "One2one field {field!r} must be unique".format(
                            field=self.name
                        ),
                    )
                )
        return res
