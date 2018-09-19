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

from xoeuf import api, fields, models


class APIModel(models.Model):
    _name = 'xoeuf.tests.test_api.model'

    @api.from_active_ids(leak_context=True)
    def return_self_ids(self):
        return list(self.ids)

    @api.from_active_ids
    def return_ids_and_call_method(self, ids, methodname):
        return list(self.ids), getattr(self.browse(ids), methodname)()

    @api.from_active_ids(leak_context=True)
    def leaked_return_ids_and_call_method(self, ids, methodname):
        return list(self.ids), getattr(self.browse(ids), methodname)()


class Users(models.Model):
    _inherit = 'res.users'

    text_field = fields.Char()

    # 'name' and 'partner_id.name' are the same thing.
    @api.onupdate('partner_id', 'name', 'partner_id.name', )
    def update_text_field(self):
        for record in self:
            record.text_field = record.get_text_field()

    @api.requires_singleton
    def get_text_field(self):
        return 's2 %s' % self.name
