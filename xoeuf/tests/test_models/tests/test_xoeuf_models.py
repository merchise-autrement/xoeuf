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

from xoeuf.odoo.tests.common import TransactionCase
from xoeuf.models.extensions import get_ref


class TestModels(TransactionCase):
    def test_get_ref(self):
        Foo = self.env["test_xoeuf_models.foobar"]
        record = self.env.ref("test_models.record1")
        self.assertEqual(record, get_ref(Foo, "record1"))
        self.assertEqual(record, Foo.get_ref("record1"))
