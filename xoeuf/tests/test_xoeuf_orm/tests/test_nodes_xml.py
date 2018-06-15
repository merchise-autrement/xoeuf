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


class TestORMSymbolsInXML(TransactionCase):
    def test_nodes_were_created(self):
        parent = self.env.ref('test_xoeuf_orm.parent_node')
        self.assertEqual(len(parent.children), 2)
