#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
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

from odoo.tests.common import TransactionCase

Hours = {"15:30": 15.5, "12:00": 12, "9:45": 9.75}


class TestTimeRange(TransactionCase):
    def setUp(self):
        super(TestTimeRange, self).setUp()
        self.Model = self.env["test.time.range"]

    def test_compute_range(self):
        obj = self.Model.create(dict(time_value=Hours["15:30"]))

        self.assertEqual(obj.range_value, "afternoon")

        obj.time_value = Hours["9:45"]

        self.assertEqual(obj.range_value, "morning")

        obj.time_value = Hours["12:00"]

        self.assertEqual(obj.range_value, "noon")
