#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoeuf.fields.datetime
# ---------------------------------------------------------------------
# Copyright (c) 2016-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2016-11-15

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
