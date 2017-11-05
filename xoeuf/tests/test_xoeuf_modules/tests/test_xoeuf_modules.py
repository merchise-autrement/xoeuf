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

import unittest


class TestModules(unittest.TestCase):
    def test_get_object_module(self):
        from .. import Foo
        from xoeuf.modules import get_object_module
        self.assertEqual(get_object_module(Foo), Foo.module)
