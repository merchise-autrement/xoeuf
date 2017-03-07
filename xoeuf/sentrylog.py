#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

try:
    from openerp.sentrylog import *   # noqa: reexport
except ImportError:
    from ._sentrylog import *  # noqa: reexport
