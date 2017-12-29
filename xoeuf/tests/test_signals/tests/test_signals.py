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
    do_nothing2,
    do_nothing3,
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
        def post_create(sender, signal, **kwargs):
            return method(sender, signal, **kwargs)

        def pre_create(sender, signal, **kwargs):
            return method(sender, signal, **kwargs)

        def wrapper(sender, wrapping, *args, **kwargs):
            return method(sender, wrapping, *args, **kwargs)

        mock = signals.mock_replace
        with mock(signals.post_create, method, side_effect=post_create) as post, \
             mock(signals.pre_create, method, side_effect=pre_create) as pre, \
             mock(signals.write_wrapper, method,
                  side_effect=wrapper) as wrap, \
             temp_attributes(self.env.registry, dict(ready=True)):
            yield post, pre, wrap

    def test_post_create(self):
        with self.mocks(do_nothing) as (post, pre, _), \
             self.mocks(do_nothing2) as (post2, pre2, _), \
             self.mocks(do_nothing3) as (post3, pre3, _):
            self.Model.create(dict(name='My name'))
            self.assertTrue(post.called)
            self.assertTrue(post2.called)
            self.assertTrue(post3.called)
            self.assertFalse(pre.called)
            self.assertFalse(pre2.called)
            self.assertFalse(pre3.called)

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
        with self.mocks(wrap_nothing) as (_, _p, wrap):
            who.name = 'My new other name'
            self.assertTrue(wrap.called)

    def test_not_called_for_partners(self):
        with self.mocks(do_nothing) as (post, pre, wrap):
            partner = self.env['res.partner'].create(dict(name='Contact Info'))
            partner.email = 'a@b.c'
            self.assertFalse(post.called and pre.called and wrap.called)
