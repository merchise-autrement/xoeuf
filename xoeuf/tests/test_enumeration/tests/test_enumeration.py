#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# test_property
# ---------------------------------------------------------------------
# Copyright (c) 2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2017-08-01

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from hypothesis import strategies as s, given
from xoeuf.odoo.tests.common import TransactionCase

from ..models import COLORS

colors = s.sampled_from(COLORS.__members__.values())


class TestEnum(TransactionCase):
    def setUp(self):
        super(TestEnum, self).setUp()
        self.EnumModel = self.env['test.enum.model']

    def test_can_set_valid_integers(self):
        obj = self.EnumModel.create({'color': 1})
        id = obj.id
        self.EnumModel.invalidate_cache()
        obj = self.EnumModel.browse(id)
        assert obj.color == COLORS.Red, '%r == %r' % (obj.color, COLORS.Red)

    @given(colors)
    def test_can_set_valid_values(self, color):
        obj = self.EnumModel.create({'color': color})
        id = obj.id
        self.EnumModel.invalidate_cache()
        obj = self.EnumModel.browse(id)
        assert obj.color == color, '%r == %r' % (obj.color, color)

    @given(colors)
    def test_can_set_valid_values_as_integers_and_get_values(self, color):
        obj = self.EnumModel.create({'color': int(color)})
        id = obj.id
        self.EnumModel.invalidate_cache()
        obj = self.EnumModel.browse(id)
        assert obj.color == color, '%r == %r' % (obj.color, color)
        assert isinstance(obj.color, COLORS)

    def test_cannot_set_invalid_integers(self):
        # Unfortunately we can insert invalid values in the DB, but we get a
        # ValueError upon 'reading'.
        obj = self.EnumModel.create({'color': 10})
        id = obj.id
        self.EnumModel.invalidate_cache()
        obj = self.EnumModel.browse(id)
        with self.assertRaises(ValueError):
            obj.color

    def test_cannot_set_invalid_integers2(self):
        # Unfortunately we can insert invalid values in the DB, but we get a
        # ValueError upon 'reading'.
        obj = self.EnumModel.create({'color': 10})
        id = obj.id
        self.EnumModel.invalidate_cache()
        with self.assertRaises(ValueError):
            self.EnumModel.browse(id).read(['color'])
