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

from xoeuf.odoo.tests.common import TransactionCase


class TestLocalizedDt(TransactionCase):
    def test_getting_the_field(self):
        obj = self.env['test_localizated_dt.model'].create(
            {'dt_at_tzone': '2018-01-01 12:00:00'}
        )
        # 12PM on January (no DTS) in Cuba is -4 hours from UTC
        self.assertEqual(obj.dt, '2018-01-01 18:00:00')
