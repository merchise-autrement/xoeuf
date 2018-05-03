#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from xoeuf import api, models


class APIModel(models.Model):
    _name = 'xoeuf.tests.test_api.model'

    @api.from_active_ids
    def return_self_ids(self):
        return list(self.ids)

    @api.from_active_ids(leak_context=False)
    def return_ids_and_call_method(self, ids, methodname):
        return list(self.ids), getattr(self.browse(ids), methodname)()

    @api.from_active_ids(leak_context=True)
    def leaked_return_ids_and_call_method(self, ids, methodname):
        return list(self.ids), getattr(self.browse(ids), methodname)()
