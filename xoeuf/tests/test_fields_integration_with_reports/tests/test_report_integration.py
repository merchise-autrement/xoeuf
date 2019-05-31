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

from xoeuf.odoo.tests.common import BaseCase

try:
    from xoeuf.odoo.addons.base.models.ir_model import FIELD_TYPES
except ImportError:
    try:
        from xoeuf.odoo.addons.base.ir.ir_model import FIELD_TYPES
    except ImportError:
        # Odoo 10 is cool
        FIELD_TYPES = None


class TestNewFieldsAreRegistered(BaseCase):
    def test_getting_the_field_property(self):
        if FIELD_TYPES is not None:
            self.assertIn(("python-property", "python-property"), FIELD_TYPES)

    def test_getting_the_field_timedelta(self):
        if FIELD_TYPES is not None:
            self.assertIn(("timedelta", "timedelta"), FIELD_TYPES)

    def test_getting_the_field_timerange(self):
        if FIELD_TYPES is not None:
            self.assertIn(("timerange", "timerange"), FIELD_TYPES)
