#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from xoeuf import fields
from xoeuf.odoo.tests.common import TransactionCase


class TestReferences(TransactionCase):
    def test_simple_typed_reference(self):
        obj = self.env["test.model"].create({})
        typed_ref = obj._fields["typed_ref"]
        self.assertTrue(isinstance(typed_ref, fields.TypedReference))
        self.assertEqual(typed_ref.mixin, "example.mixin")

        def typed_ref_assign(value):
            obj.typed_ref = value
            return True

        self.assertTrue(typed_ref_assign(False))
        obj2 = self.env["test.model1"].create({})
        self.assertTrue(typed_ref_assign(obj2))
        self.assertTrue(typed_ref_assign("%s,%d" % (obj2._name, obj2.id)))
        self.assertRaises(ValueError, typed_ref_assign, obj)

    def test_filtered_typed_reference(self):
        obj = self.env["test.model"].create({})

        def typed_ref_assign(value):
            obj.filtered_typed_ref = value
            return True

        obj2 = self.env["test.model1"].create({})
        # This should work, but the odoo validation is missing,
        # I am making a PR to propose it.
        # self.assertRaises(ValueError, typed_ref_assign, '%s,%d' % (obj2._name, obj2.id))
        self.assertRaises(ValueError, typed_ref_assign, obj2)

    def test_delegate_typed_reference(self):
        obj = self.env["test.model"].create({})
        obj2 = self.env["test.model1"].create({"test": "ok"})
        dummy_value = "any value"
        obj.test = dummy_value
        self.assertEqual(obj.test, dummy_value)
        obj.invalidate_cache()
        self.assertFalse(obj.test)
        obj.typed_ref = obj2
        obj.invalidate_cache()
        obj2.invalidate_cache()
        self.assertTrue(obj._fields["typed_ref"].delegate)
        self.assertTrue(obj._fields["test"].compute)
        self.assertEqual(obj.test, obj2.test)
        obj.test = "other value"
        self.assertEqual(obj.test, obj2.test)
        obj.invalidate_cache()
        obj2.invalidate_cache()
        self.assertEqual(obj.test, obj2.test)
        obj2.test = "other more value"
        # todo: indirect depends are not working fine.
        # self.assertEqual(obj.test, obj2.test)
        obj.invalidate_cache()
        obj2.invalidate_cache()
        self.assertEqual(obj.test, obj2.test)

    def test_related_field_search(self):
        self.env["test.model"].search([("test", "=", "any value")])
