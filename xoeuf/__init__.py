#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Xœuf are basic services for OpenERP and Open Object.

The name is composed by:
  * x: The starting letter for almost all Merchise projects.
  * oe: Open and ERP initials.
  * œuf: Is "egg" in french.

'''
from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


from . import modules  # noqa; bootstrap 'xoeuf.odoo'
from . import signals  # noqa; bootstrap signals
from .osv import orm   # bootstrap 'orm' (injects _RELATED in XMLs 'eval')

from xoeuf.odoo import SUPERUSER_ID  # noqa
from xoeuf.odoo.release import version_info as ODOO_VERSION_INFO  # noqa

MAJOR_ODOO_VERSION = ODOO_VERSION_INFO[0]  # noqa

del orm
