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
from math import isinf

from xoeuf import MAJOR_ODOO_VERSION
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

    if MAJOR_ODOO_VERSION < 9:
        @hypothesis.given(finite_floats)
        def test_monetary_value(self, value):
            Line = self.env['test.monetary.line']
            obj = Line.create({'value': value})

            # Big-big values causes obj.value to be inf, skip those
            hypothesis.assume(not isinf(obj.value))

            # For big numbers like ``value=3.6893488147419103e+19``, we get
            # approximate ``obj.value=3.68934881474191e+19`` which, when
            # substracted is quite large (4096); this represents a loss of
            # precision representing these values and it may be introduced either
            # by orm, psycopg2 or postgresql (check who).  According to docs both
            # Python and PG use 64 bits for floats (53 bits of precision), I don't
            # know why I can represent that value in Python but we something
            # different
            #
            # Since assertAlmostEqual does ``round(a - b, e) == 0`` this
            # difference is large enough to fail.  To overcome that I do
            # ``round(a/b - 1, 7) == 0``.
            if value:
                self.assertAlmostEqual(
                    obj.value / value, 1,
                    places=7,
                    msg='%s !~ %s from %s' % (obj.value, value, obj.value / value)
                )
            else:
                self.assertAlmostEqual(obj.value, value, places=7)

            cr = self.env.cr
            cr.execute(
                'SELECT value FROM test_monetary_line WHERE id=%s',
                (obj.id, )
            )
            fetched = cr.fetchone()[0]
            if value:
                self.assertAlmostEqual(
                    fetched / value, 1,
                    places=7,
                    msg='%s !~ %s from %s' % (fetched, value, fetched / value)
                )
            else:
                self.assertAlmostEqual(fetched, value, places=7)
