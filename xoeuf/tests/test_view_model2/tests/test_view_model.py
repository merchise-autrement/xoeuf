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


class TestViewModel(TransactionCase):

    def test_shared_extensions(self):
        self.assertTrue(all(
            'new_value' in self.env[model]._fields
            for model in ['test_view_model.model', 'view_model1', 'view_model2']
        ))
