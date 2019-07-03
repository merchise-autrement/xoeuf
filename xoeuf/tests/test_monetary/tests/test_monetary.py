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

import hypothesis
from hypothesis import strategies as s
from xoutil.dim.currencies import currency as Currency

from xoeuf.odoo.tests.common import TransactionCase

finite_floats = s.floats(
    min_value=-(2 ** 32), max_value=2 ** 32, allow_nan=False, allow_infinity=False
)


class TestMonetary(TransactionCase):
    def assertValueInCurrency(self, value, currency):
        """Assert value is expressed in units of `currency`."""
        unit = Currency(currency.name)
        try:
            # If can sum the currency's unit to the value, it's expressed in
            # the same currency unit.
            value + unit
        except TypeError:
            raise AssertionError(
                "'%s' is not in terms of currency '%s'" % (value, currency.name)
            )

    @hypothesis.given(finite_floats)
    @hypothesis.settings(max_examples=5)
    def test_monetary_concrete(self, value):
        Line = self.env["test.monetary.concrete"]
        EUR = self.env.ref("base.EUR")
        obj = Line.create({"value": value, "currency_id": EUR.id})
        self.assertValueInCurrency(obj.value, EUR)

    @hypothesis.given(finite_floats)
    @hypothesis.settings(max_examples=5)
    def test_monetary_related(self, value):
        Line = self.env["test.monetary.related"]
        company = self.env.ref("base.main_company")
        EUR = company.currency_id = self.env.ref("base.EUR")
        obj = Line.create({"value": value, "company_id": company.id})
        self.assertValueInCurrency(obj.value, EUR)
