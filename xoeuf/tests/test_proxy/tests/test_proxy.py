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

from xoeuf.models.proxy import ResUsers as Users
from xoeuf.odoo.tests.common import TransactionCase


class TestModelProxy(TransactionCase):
    def test_must_the_right_self(self):
        with self.assertRaises(AttributeError):
            Users.search([])

    def test_finds_self(this):
        self = this.env['ir.model']  # noqa: make self a valid recordset
        Users.create({'name': 'John Doe', 'login': 'john.doe'})
        Users.search([])
