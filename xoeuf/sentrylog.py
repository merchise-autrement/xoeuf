#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO: @manu, At least in Odoo 10, there is 'openerp.sentrylog'
try:
    from odoo.sentrylog import *  # noqa: reexport
except ImportError:
    from ._sentrylog import *  # noqa: reexport
