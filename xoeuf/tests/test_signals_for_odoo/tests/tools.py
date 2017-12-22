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

try:
    from xoutil.objects import temp_attributes  # TODO: migrate
except ImportError:
    from contextlib import contextmanager
    from xoutil.objects import save_attributes, smart_setter

    @contextmanager
    def temp_attributes(obj, attrs, **kwargs):
        '''A context manager that temporarily sets attributes.

        `attrs` is a dictionary containing the attributes to set.

        Keyword arguments `getter` and `setter` have the same meaning as in
        `save_attributes`:func:.  We also use the `setter` to set the values
        provided in `attrs`.

        '''
        setter = kwargs.get('setter', smart_setter)
        set_ = setter(obj)
        with save_attributes(obj, *tuple(attrs.keys()), **kwargs):
            for attr, value in attrs.items():
                set_(attr, value)
            yield

    del contextmanager
