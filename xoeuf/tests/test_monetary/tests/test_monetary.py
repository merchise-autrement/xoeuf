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

import hypothesis
from hypothesis import strategies as s

from xoeuf.odoo.tests.common import TransactionCase

finite_floats = s.floats(allow_nan=False, allow_infinity=False)


class TestMonetary(TransactionCase):
    @hypothesis.given(finite_floats)
    @hypothesis.settings(max_examples=5)
    def test_monetary_concrete(self, value):
        from xoutil.dim.currencies import currency as Currency
        Line = self.env['test.monetary.concrete']
        EUR = Currency(self.env.ref('base.EUR').name)
        obj = Line.create({'value': value,
                           'currency_id': self.env.ref('base.EUR').id})
        self.assertIsInstance(obj.value, EUR)

    @hypothesis.given(finite_floats)
    @hypothesis.settings(max_examples=5)
    def test_monetary_related(self, value):
        from xoutil.dim.currencies import currency as Currency
        Line = self.env['test.monetary.related']
        company = self.env.ref('base.main_company')
        company.currency_id = self.env.ref('base.EUR')
        EUR = Currency(company.currency_id.name)
        obj = Line.create({'value': value,
                           'company_id': company.id})
        self.assertIsInstance(obj.value, EUR)

