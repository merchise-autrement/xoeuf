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
# Created on 2017-09-05

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


def TimeSpan(start_date_field, end_date_field):
    '''Create a time span property.

    A time span property is stored in the DB as two separate Date fields [*].
    It's never actually stored in the DB a single value.  You cannot search
    for this property.

    '''
    from xoeuf.fields import Property
    try:
        from xoutil.future.datetime import TimeSpan
    except ImportError:
        from xoutil.datetime import TimeSpan

    @Property
    def result(self):
        return TimeSpan(
            getattr(self, start_date_field),
            getattr(self, end_date_field)
        )

    @result.setter
    def result(self, value):
        setattr(self, start_date_field, value.start_date)
        setattr(self, end_date_field, value.end_date)

    @result.deleter
    def result(self):
        # This may fail if any of these fields is required.
        setattr(self, start_date_field, None)
        setattr(self, end_date_field, None)

    return result
