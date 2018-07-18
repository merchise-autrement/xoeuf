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

from itertools import product
import unittest
from hypothesis import strategies as s, given

from xoeuf.osv import expression as expr
from xoeuf.odoo.osv import expression as odoo_expr
from xoeuf.osv.expression import Domain, DomainTree

names = s.text(alphabet='abdefgh', min_size=1, average_size=3)
operators = s.sampled_from(['=', '!=', '<', '>', '<>'])

# Logical connectors with the amount of terms it connects.  Notice that ''
# takes two arguments because it's the same as '&'.
connectors = s.sampled_from([('', 2), ('&', 2), ('!', 1), ('|', 2)])


@s.composite
def terms(draw, values=s.integers(min_value=-10, max_value=10)):
    name = str(draw(names))
    operator = draw(operators)
    value = draw(values)
    return (name, operator, value)


@s.composite
def domains(draw, min_size=1, average_size=4):
    leaves = draw(s.lists(
        terms(),
        min_size=min_size,
        average_size=average_size
    ))
    result = []
    while leaves:
        connector, many = draw(connectors)
        if many <= len(leaves):
            if connector:
                result.append(connector)
            result.extend(leaves[:many])
            leaves = leaves[many:]
        elif len(leaves) == 1:
            result.append(leaves.pop(0))
    return Domain(result)


class TestDomain(unittest.TestCase):
    @given(domains())
    def test_first_normal_form_idempotency(self, domain):
        self.assertEqual(
            domain.first_normal_form,
            domain.first_normal_form.first_normal_form
        )

    @given(domains())
    def test_second_normal_form_idempotency(self, domain):
        self.assertEqual(
            domain.second_normal_form,
            domain.second_normal_form.second_normal_form
        )

    @given(domains())
    def test_versions_equivalency(self, domain):
        # Any domain must be equivalent in all its versions.
        all_versions = [
            domain,
            domain.simplified,
            domain.first_normal_form,
            domain.second_normal_form
        ]
        for version1, version2 in product(all_versions, all_versions):
            self.assertEqual(
                version1,
                version2,
                msg="%r != %r" % (version1, version2)
            )

    @given(domains())
    def test_simplified(self, domain):
        # A simplified domain never start with '&' operator.
        self.assertNotEqual(
            domain.simplified[0],
            expr.AND_OPERATOR,
            msg="%r start with &" % domain.simplified
        )
        # The simplified domain must be the shortest.
        all_versions = [
            domain,
            domain.first_normal_form,
            domain.second_normal_form
        ]
        for version in all_versions:
            self.assertLessEqual(
                len(domain.simplified),
                len(version),
                msg="len(%r) > len(%r)" % (domain.simplified, version)
            )
        self.assertTrue(
            all(odoo_expr.is_leaf(term) or odoo_expr.is_operator(term)
                for term in domain.simplified)
        )

    @given(domains())
    def test_simplified_idempotency(self, domain):
        self.assertEqual(
            domain.simplified,
            domain.simplified.simplified
        )

    @given(s.lists(domains(), max_size=10, average_size=5))
    def test_expr_replacement(self, domains):
        expr.AND(domains)
        odoo_expr.AND(domains)

    def test_eq(self):
        A = Domain([
            ('field_x', '=', 1)
        ])
        # A == A
        self.assertTrue(A == A)

        # ~A == ~A
        self.assertTrue(~A == ~A)

        # (x = 1)  == ! (x <> 1)
        A1 = Domain([
            '!',
            ('field_x', '<>', 1)
        ])
        self.assertTrue(A == A1)

    def test_implies(self):
        # Basic implications.
        # -------------------

        A = Domain([
            ('field_x', '=', 1)
        ])
        B = Domain([
            ('field_y', '!=', False)
        ])

        # A => A
        self.assertTrue(A.implies(A))

        # A => A | B
        self.assertTrue(A.implies(A | B))

        # A & B => A
        self.assertTrue((A & B).implies(A))

        # A & B => A | B
        self.assertTrue((A & B).implies(A | B))

        self.assertEqual(Domain.AND(list(A), B), (A & B))
        self.assertEqual(expr.AND([list(A), B]), (A & B))

        # Inter terms implications.
        # -------------------------

        # (x = 1)  => (x = 1)
        A = Domain([
            ('field_x', '=', 1)
        ])
        A1 = Domain([
            ('field_x', '=', 1)
        ])
        self.assertTrue(A.implies(A1))

        # (x != 1)  => (x <> 1)
        A = Domain([
            ('field_x', '!=', 1)
        ])
        A1 = Domain([
            ('field_x', '<>', 1)
        ])
        self.assertTrue(A.implies(A1))

        # (x > 1) => (x > 0)
        A = Domain([
            ('field_x', '>', 10)
        ])
        A1 = Domain([
            ('field_x', '>', 1)
        ])
        self.assertTrue(A.implies(A1))

        # (x in (1,2,3)) => (x in (1,2,3,4))
        A = Domain([
            ('field_x', 'in', (1, 2, 3))
        ])
        A1 = Domain([
            ('field_x', 'in', (1, 2, 3, 4))
        ])
        self.assertTrue(A.implies(A1))
        #

        # Compound implications.
        # ----------------------
        # A => B & C iff (A => B) & (A => C)
        A = Domain([
            ('field_x', 'in', (1, 4))
        ])
        B = Domain([
            ('field_x', 'in', (1, 2, 4))
        ])
        C = Domain([
            ('field_x', 'in', (1, 3, 4))
        ])
        self.assertTrue(A.implies(B))
        self.assertTrue(A.implies(C))
        self.assertTrue(A.implies(B & C))

        # More complex implications
        # -------------------------

        x = Domain([
            '|',
            ('field_y', '!=', False),
            ('field_x', '=', 'value'),
            ('field_z', 'in', (1,))
        ])
        y = Domain([
            '|',
            ('field_y', '!=', False),
            ('field_x', '=', 'value'),
            ('field_z', 'in', (1, 2, 3)),
            '|',
            ('field_x', '=', 'value'),
            ('field_y', '!=', False)
        ])
        assert x.implies(y)

        x = Domain([
            ('field_y', '!=', False),
            ('field_z', 'in', (1,)),
            ('field_z', 'in', (1, 2)),
            '|',
            ('field_y', '!=', False),
            '|',
            ('field_z', 'in', (1,)),
            ('field_z', 'in', (2,))
        ])
        y = Domain([
            ('field_y', '!=', False),
            ('field_z', 'in', (1, 2, 3))
        ])
        assert x.implies(y)

    def test_walk(self):
        y = Domain([
            '|',
            ('a', '!=', False),
            ('b', '=', 'value'),
            ('c', 'in', (1, 2, 3)),
            '|', '|', '!',
            ('d', '=', 'value'),
            ('f', '!=', False),
            ('g', '=', 'h')
        ])
        DomainTree(y.second_normal_form)
        # expected = [
        #     ('TERM', ('c', 'in', (1, 2, 3))),
        #     ('TERM', ('g', '=', 'h')),
        #     ('TERM', ('d', '!=', 'value')),
        #     ('TERM', ('f', '!=', False)),
        #     ('OPERATOR', '|'),
        #     ('OPERATOR', '|'),
        #     ('TERM', ('a', '!=', False)),
        #     ('TERM', ('b', '=', 'value')),
        #     ('OPERATOR', '|'),
        #     ('OPERATOR', '&'),
        #     ('OPERATOR', '&')
        # ]
        # self.assertEqual(expected, list(tree.walk()))
