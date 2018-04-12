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


import json

from xoeuf.odoo import http
from xoeuf.models.proxy import ResUsers as User


class Controller(http.Controller):
    @http.route('/test_proxy_none', type='http', auth='none')
    def count_users_none(self):
        return json.dumps(User.search([], count=True))

    @http.route('/test_proxy_pub', type='http', auth='public')
    def count_users_public(self):
        return json.dumps(User.search([], count=True))
