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
from xoeuf.odoo.tests.common import TransactionCase
from xoeuf.odoo.addons.test_signals.models import (
    signals,  # this is the same implementation the models use.
    do_nothing,
    do_nothing_again,
    wrap_nothing,
)

from .tools import temp_attributes


class TestXoeufSignals(TransactionCase):
    at_install = False
    post_install = not at_install

    def setUp(self):
        super(TestXoeufSignals, self).setUp()
        self.Model = self.env['test_signals.signaling_model']

    @contextlib.contextmanager
    def mocks(self, method):
        def wrapper(sender, wrapping, **kwargs):
            yield

        mock = signals.mock_replace
        with mock(signals.post_create, method) as post, \
             mock(signals.pre_create, method) as pre, \
             mock(signals.write_wrapper, method,
                  side_effect=wrapper) as wrap, \
             temp_attributes(self.env.registry, dict(ready=True)):
            yield post, pre, wrap

    def test_post_create(self):
        with self.mocks(do_nothing) as (post, pre, _):
            self.Model.create(dict(name='My name'))
            self.assertTrue(post.called)
            self.assertFalse(pre.called)

    def test_pre_create(self):
        ready = self.env.registry.ready
        with self.mocks(do_nothing_again) as (post, pre, _):
            self.Model.create(dict(name='My name'))
            self.assertFalse(post.called)
            self.assertTrue(pre.called)
        self.assertEqual(ready, self.env.registry.ready)

    def test_writer_wrap(self):
        who = self.Model.create(dict(name='My name'))
        with self.mocks(wrap_nothing) as (_, _p, wrap):
            self.assertFalse(wrap.called)
            who.write(dict(name='My new name'))
            self.assertTrue(wrap.called)
