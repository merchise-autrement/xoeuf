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

import contextlib

from hypothesis import strategies as s, given
from xoeuf.odoo.tests.common import TransactionCase

from ..models import COLORS, Pax, CARS

colors = s.sampled_from(COLORS.__members__.values())
cars = s.sampled_from(CARS.__members__.values())
paxs = s.sampled_from(Pax.__members__.values())


class TestEnum(TransactionCase):
    at_install = False
    post_install = not at_install

    def setUp(self):
        super(TestEnum, self).setUp()
        self.EnumModel = self.env['test.enum.model']

    def test_can_set_valid_integers(self):
        with force_ready(self.env.registry):
            obj = self.EnumModel.create({'color': 1, 'car': CARS.FORD, 'pax': 1})
        id = obj.id
        self.EnumModel.invalidate_cache()
        obj = self.EnumModel.browse(id)
        assert obj.color == COLORS.Red, '%r == %r' % (obj.color, COLORS.Red)
        assert obj.car is CARS.FORD
        assert obj.pax == 1

    @given(colors)
    def test_can_set_valid_values(self, color):
        with force_ready(self.env.registry):
            obj = self.EnumModel.create({'color': color})
        id = obj.id
        self.EnumModel.invalidate_cache()
        obj = self.EnumModel.browse(id)
        assert obj.color == color, '%r == %r' % (obj.color, color)

    @given(colors)
    def test_can_set_valid_values_as_integers_and_get_values(self, color):
        with force_ready(self.env.registry):
            obj = self.EnumModel.create({'color': int(color)})
        id = obj.id
        self.EnumModel.invalidate_cache()
        obj = self.EnumModel.browse(id)
        assert obj.color == color, '%r == %r' % (obj.color, color)
        assert isinstance(obj.color, COLORS)

    def test_cannot_set_invalid_integers(self):
        # Sinces tests are run while the registry is being populated, i.e not
        # ready, we need to trick it to allow receivers be executed.
        with force_ready(self.env.registry), self.assertRaises(ValueError):
            self.EnumModel.create({'color': 10})

    def test_cannot_write_invalid_integers(self):
        with force_ready(self.env.registry):
            obj = self.EnumModel.create({'color': 1})
            with self.assertRaises(ValueError):
                obj.write({'color': 10})

    def test_cannot_write_invalid_values(self):
        obj = self.EnumModel.create({'car': CARS.FORD})
        with force_ready(self.env.registry), self.assertRaises(ValueError):
            obj.write({'car': 'any other brand'})

    def test_search_non_integer(self):
        with force_ready(self.env.registry):
            obj = self.EnumModel.create({'car': CARS.FORD})
            self.EnumModel.invalidate_cache()
            self.assertEqual(
                self.EnumModel.search([('car', '=', CARS.FORD)]),
                obj
            )
            self.assertEqual(
                self.EnumModel.search([('car', '=', CARS.CHEV)], count=True),
                0
            )
            self.assertEqual(
                self.EnumModel.search([('car', 'in', (CARS.FORD, CARS.CHEV))]),
                obj
            )
            with self.assertRaises(ValueError):
                self.EnumModel.search([('car', '=', 1)])

    def test_search_integer(self):
        with force_ready(self.env.registry):
            obj = self.EnumModel.create({'color': COLORS.Red})
            self.EnumModel.invalidate_cache()
            self.assertEqual(
                self.EnumModel.search([('color', '=', 1)]),
                obj
            )
            with self.assertRaises(ValueError):
                self.EnumModel.search([('color', '=', 10)])


@contextlib.contextmanager
def force_ready(registry):
    ready = registry.ready
    registry.ready = True
    try:
        yield
    finally:
        registry.ready = ready
