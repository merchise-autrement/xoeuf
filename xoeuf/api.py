#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoeuf.api
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-01-01

'''Odoo API bridge.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


try:
    from openerp.api import Environment
except ImportError:
    Environment = None


def contextual(func):
    '''Decorate a function to run in a proper Odoo environment.

    You should decorate every function that represents an "entry point" for
    working with the ORM.  If Odoo is not installed, the original function is
    returned unchanged.  However, if Odoo is present a proper `Environment` is
    entered upon calling the function.

    Every command in the `xouef.cli`:mod: is automatically decorated.

    '''
    if Environment is None:
        return func

    def inner(*args, **kwargs):
        with Environment.manage():
            return func(*args, **kwargs)
    return inner
