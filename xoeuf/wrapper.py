#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Wraps write operations.

Usage::

  @write_wrapper()
  def wrapper(sender, **kwargs):
      yield

The wrapper must yield exactly once.  All the code above the 'yield' will be
executed before the actual write.  All the code below the 'yield' will be
executed after the write.  You can have as many wrappers as you want.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

try:
    from xoeuf.odoo.wrapper import write_wrapper  # TODO: migrate
except ImportError:
    from ._wrapper_impl import write_wrapper  # noqa
