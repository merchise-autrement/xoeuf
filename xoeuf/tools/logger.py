#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Initialize the OpenERP logger, and provides a function to smartly get a
logger.

'''
from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoeuf.odoo.netsvc import init_logger


DEFAULT_LOGGER_NAME = str('xoeuf')


def get_logger(name=None):
    '''If a `name` is given, is normally getter, otherwise look for the upper
    module name.

    '''
    from logging import getLogger
    if not name:
        import sys
        frame = sys._getframe(1)
        name = frame.f_globals.get('__name__', DEFAULT_LOGGER_NAME)
    return getLogger(str(name))


init_logger()
