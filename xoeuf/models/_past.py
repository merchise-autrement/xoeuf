#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''This is not a future extension module.

Add a function to assure that future module is being used correctly.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


def dissuade(name=None):
    '''Check future module for being used correctly.

    If not, -meaning in the past- issue a deprecation warning.

    :param name: name of module to check (could be ``None`` to inspect it in
           the stack-frame).

    '''
    if name is None:
        import inspect
        frame = inspect.currentframe().f_back
        try:
            name = frame.f_globals.get('__name__')
        finally:
            # As recommended in Python's documentation to avoid memory leaks
            del frame
    prefix = '.'.join(__name__.split('.')[:-1])
    if name and prefix not in name:
        from warnings import warn
        new_name = '{}.{}'.format(prefix, name.split('.')[-1])
        warn(('"{}" is now deprecated and it will be removed; use "{}" '
              'instead.').format(name, new_name),
             # TODO: Why ``category=DeprecationWarning,`` doesn't work?
             stacklevel=3)
