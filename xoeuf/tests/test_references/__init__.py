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

from xoeuf import fields, models

MIXIN_NAME = "example.mixin"


class ExampleMixin(models.AbstractModel):
    _name = MIXIN_NAME

    test = fields.Char(default="Hello")


class Model1(models.Model):
    _name = "test.model1"
    _inherit = MIXIN_NAME
    _description = "Model 1"


class Model2(models.Model):
    _name = "test.model2"
    _inherit = MIXIN_NAME


class SubModel2(models.Model):
    _name = "test.sub.model2"
    _inherit = "test.model2"


class TestModel(models.Model):
    _name = "test.model"

    typed_ref = fields.TypedReference(mixin=MIXIN_NAME, delegate=True)
    filtered_typed_ref = fields.TypedReference(
        mixin=MIXIN_NAME, selection=[("test.model2", "model2")]
    )
