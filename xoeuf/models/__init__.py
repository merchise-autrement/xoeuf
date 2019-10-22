#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

"""A new object model.


"""
from . import proxy  # noqa: ensure the hook is registered.
from .base import *  # noqa: reexport

from xoeuf.odoo.models import *  # noqa: reexport
