#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# __init__
# ---------------------------------------------------------------------
# Copyright (c) 2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2017-08-01


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


from xoeuf.odoo.release import version_info as ODOO_VERSION_INFO

if 8 <= ODOO_VERSION_INFO[0] < 9:
    from ._v8 import Property  # noqa: reexport
elif ODOO_VERSION_INFO[0] < 12:
    from ._v10 import Property  # noqa: reexport
else:
    raise NotImplementedError

Property.__module__ = __name__
