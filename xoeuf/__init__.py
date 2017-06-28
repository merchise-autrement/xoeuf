#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoeuf
# ---------------------------------------------------------------------
# Copyright (c) 2013-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-05-01

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
from . import signals  # noqa

from xoeuf.odoo import SUPERUSER_ID
from xoeuf.odoo.release import version_info as ODOO_VERSION_INFO  # noqa
