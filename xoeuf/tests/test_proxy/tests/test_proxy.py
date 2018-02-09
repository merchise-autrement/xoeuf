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

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from xoeuf import MAJOR_ODOO_VERSION
from xoeuf.models.proxy import ResUsers as Users
from xoeuf.odoo import SUPERUSER_ID
from xoeuf.odoo.tests.common import TransactionCase, HttpCase


class TestModelProxy(TransactionCase):
    def test_must_the_right_self(self):
        with self.assertRaises(RuntimeError):
            Users.search([])

    def test_finds_self(this):
        self = this.env['ir.model']  # noqa: make self a valid recordset
        Users.create({'name': 'John Doe', 'login': 'john.doe'})
        this.assertEqual(Users.search([]), self.env['res.users'].search([]))

    def test_instances_check(this):
        self = this.env['ir.model']  # noqa: make self a valid recordset
        root = Users.browse(SUPERUSER_ID)
        this.assertIn(root, Users._instances_)
        this.assertNotIn(self, Users._instances_)
        this.assertNotIn(object(), Users._instances_)


class TestHTTPModelProxy(HttpCase):
    at_install = False
    post_install = not at_install

    @staticmethod
    def getcode(response):
        if MAJOR_ODOO_VERSION < 11:
            return response.getcode()
        else:
            # Odoo 11+ uses requests to load the URL.
            return response.status_code

    @unittest.skipIf(MAJOR_ODOO_VERSION >= 9,
                     'Does not raises the error in Odoo 9+')
    def test_request_no_auth(self):
        # The controller won't be able to find a proper environment and fail
        # with an AttributeError, we'll see as an error 500
        self.authenticate('admin', 'admin')
        response = self.url_open('/test_proxy_none')
        code = self.getcode(response)
        self.assertEqual(code, HTTP_SERVER_ERROR)

    def test_request_with_auth(self):
        response = self.url_open('/test_proxy_pub')
        code = self.getcode(response)
        self.assertEqual(code, HTTP_OK)


HTTP_OK = 200
HTTP_SERVER_ERROR = 500
