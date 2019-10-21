#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
"""Xœuf are basic services for OpenERP and Open Object.

The name is composed by:
  * x: The starting letter for almost all Merchise projects.
  * oe: Open and ERP initials.
  * œuf: Is "egg" in french.

"""
from . import modules  # noqa; bootstrap 'xoeuf.odoo'
from . import signals  # noqa; bootstrap signals
from .osv import orm  # bootstrap 'orm' (injects _RELATED in XMLs 'eval')

from xoeuf.odoo import SUPERUSER_ID  # noqa
from xoeuf.odoo.release import version_info as ODOO_VERSION_INFO  # noqa

MAJOR_ODOO_VERSION = ODOO_VERSION_INFO[0]  # noqa

# Bootstrap fields; otherwise they won't appear in the FIELD_TYPES in
# ir_model.py
from . import fields  # noqa

from ._version import get_versions

del orm

__version__ = get_versions()["version"]
del get_versions
