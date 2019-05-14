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
from xoeuf.odoo.addons.test_view_model import TEST_MODEL_NAME


class Model(models.Model):
    _inherit = TEST_MODEL_NAME

    new_value = fields.Float()
