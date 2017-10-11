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

from xoeuf.odoo.release import version_info as ODOO_VERSION_INFO

# XXX: Next pattern is not consistent with v9
if ODOO_VERSION_INFO[0] == 8:
    from ._dt8 import LocalizedDatetime  # noqa: reexport
elif ODOO_VERSION_INFO[0] >= 9:
    from ._dt10 import LocalizedDatetime  # noqa: reexport
else:
    assert False

LocalizedDatetime.__module__ = __name__
