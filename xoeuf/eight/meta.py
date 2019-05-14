#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
"""Implements the metaclass() function using the Py3k syntax.

"""
from __future__ import (
    division as _py3_division,
    print_function as _py3_print,
    absolute_import as _py3_abs_import,
)

from . import _py3

if _py3:
    from ._meta3 import metaclass
else:
    from ._meta2 import metaclass


metaclass.__module__ = __name__
