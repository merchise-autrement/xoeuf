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

# notice that receivers are normally called only when they are defined in
# INSTALLED addons, during at_install tests the addon is not installed, but
# 'to be installed', so write your tests to run post_install.

from xoeuf.odoo.tests.common import TransactionCase
from xoeuf.odoo.addons.test_signals.models import (
    signals,
    do_nothing,
    do_nothing_again,
    wrap_nothing
)

from .tools import temp_attributes


mock_replace = signals.mock_replace


class TestSignals(TransactionCase):
    at_install = False
    post_install = not at_install

    def setUp(self):
        super(TestSignals, self).setUp()
        self.Model = self.env['test_signals.signaling_model']

    def test_post_create(self):
        with mock_replace(signals.post_create, do_nothing) as post, \
             mock_replace(signals.pre_create, do_nothing) as pre, \
             temp_attributes(self.env.registry, dict(ready=True)):
            self.Model.create(dict(name='My name'))
            self.assertTrue(post.called)
            self.assertFalse(pre.called)

    def test_pre_create(self):
        ready = self.env.registry.ready
        with mock_replace(signals.post_create, do_nothing_again) as post, \
             mock_replace(signals.pre_create, do_nothing_again) as pre, \
             temp_attributes(self.env.registry, dict(ready=True)):
            self.Model.create(dict(name='My name'))
            self.assertFalse(post.called)
            self.assertTrue(pre.called)
        self.assertEqual(ready, self.env.registry.ready)


class TestWrappers(TransactionCase):
    at_install = False
    post_install = not at_install

    def setUp(self):
        super(TestWrappers, self).setUp()
        self.Model = self.env['test_signals.signaling_model']

    def test_writer_wrap(self):
        def wrapper(sender, wrapping, **kwargs):
            yield

        who = self.Model.create(dict(name='My name'))
        with mock_replace(signals.write_wrapper, wrap_nothing,
                          side_effect=wrapper) as wrap, \
             temp_attributes(self.env.registry, dict(ready=True)):
            who.write(dict(name='My new name'))
            self.assertTrue(wrap.called)
