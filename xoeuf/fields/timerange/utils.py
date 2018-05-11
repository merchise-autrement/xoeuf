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
    from xoutil.future.datetime import TimeRange  # TODO: migrate
except ImportError:
    from xoutil.eight import string_types
    from datetime import datetime, time

    class TimeField(object):
        '''A descriptor for a `datetime.time`:class:.

        You may set either `datetime.time`:class: values or strings with the
        HH:MM format.

        `name` is the attribute name.  This is the key in the instance's
        __dict__.

        If `nullable` is True (the default).  You may also set, None or False
        (Odoo).

        '''
        def __init__(self, name, nullable=True):
            self.name = name
            self.nullable = nullable

        def __get__(self, instance, owner):
            try:
                return instance.__dict__[self.name]
            except KeyError:
                raise AttributeError(self.name)

        def __set__(self, instance, value):
            if value in (None, False):
                if not self.nullable:
                    raise ValueError('Setting None to a non nullable attribute')
            elif isinstance(value, string_types):
                value = datetime.strptime(value, '%H:%M').time()
            elif not isinstance(value, time):
                raise TypeError(
                    'Either time or str expected. Got %r' % type(value).__name__
                )
            instance.__dict__[self.name] = value

        def __delete__(self, instance):
            del instance.__dict__[self.name]

    class TimeRange(object):
        '''A continuous `datetime.time`:class: range.

        Both `start` and `end` are inclusive.

        .. note:: So far we don't support unbounded ranges.

        '''
        start = TimeField('start', False)
        end = TimeField('end', False)

        def __init__(self, start, end):
            self.start = start
            self.end = end
            if self.start > self.end:
                raise ValueError('start must be earlier than end.')

        def __bool__(self):
            return True
        __nonzero__ = __bool__

        def __contains__(self, value):
            return self.start <= value <= self.end

        def __repr__(self):
            start, end = self.start, self.end
            return 'TimeRange(%r, %r)' % (
                start.strftime('%H:%M') if start else None,
                end.strftime('%H:%M') if end else None
            )

        # TODO: All others operators like __and__, __lshift__, and the empty
        # timerange, which is only needed to make __and__ closed.
