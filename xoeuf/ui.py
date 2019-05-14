#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

"""User interface stuff.

"""

from __future__ import (
    division as _py3_division,
    print_function as _py3_print,
    absolute_import as _py3_abs_import,
)


class _const(dict):
    def __call__(self):
        return self


# Return this to close a window
CLOSE_WINDOW = _const({"type": "ir.actions.act_window_close"})


# Return this to reload the interface
RELOAD_UI = _const({"type": "ir.actions.client", "tag": "reload"})


# The do nothing action.
DO_NOTHING = _const({})
