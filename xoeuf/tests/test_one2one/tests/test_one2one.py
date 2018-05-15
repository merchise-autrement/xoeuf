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

from psycopg2 import IntegrityError
from xoeuf.odoo.tests.common import TransactionCase


class TestO2O(TransactionCase):
    def test_one2one_injects_restriction(self):
        C = self.env['test.one2one.c']
        c = C.create({'name': 'I am a C'})
        a = c.a_id
        with self.assertRaises(IntegrityError):
            C.create({'name': 'I am trying to steal the A', 'a_id': a.id})

    def test_one2one_baseline(self):
        B = self.env['test.one2one.b']
        b = B.create({'name': 'I am a B'})
        a = b.a_id
        B.create({'name': 'I can steal the A', 'a_id': a.id})

    def test_one2one_cascade(self):
        C = self.env['test.one2one.c']
        c = C.create({'name': 'I am a C'})
        a = c.a_id
        a.unlink()
        self.assertFalse(c.exists())
