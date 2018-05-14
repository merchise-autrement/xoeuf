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

from datetime import timedelta
from xoeuf.odoo.fields import Float


class TimeDelta(Float):
    '''A timedelta field.

    At the DB the field is represented as an Integer (total_seconds).  In
    Python code we get a timedelta object.

    '''
    type = 'timedelta'

    @staticmethod
    def ensure_timedelta(value):
        """ If `value` is not an timedelta value is assume as float that
        represent the quantity of seconds.

        :param value:
            * timedelta or float are expected.

        :raises TypeError:
            * If value is no an expected type.
        """
        if not isinstance(value, timedelta):
            return timedelta(seconds=value or 0)
        return value

    def convert_to_cache(self, value, *args, **kwargs):
        value = self._convert_to('cache', value, *args, **kwargs)
        return self.ensure_timedelta(value)

    def convert_to_read(self, value, *args, **kwargs):
        return self._convert_to('read', value, *args, **kwargs)

    def convert_to_write(self, value, *args, **kwargs):
        return self._convert_to('write', value, *args, **kwargs)

    def convert_to_column(self, value, *args, **kwargs):
        return self._convert_to('column', value, *args, **kwargs)

    def _convert_to(self, method, value, *args, **kwargs):
        if isinstance(value, timedelta):
            # Ensure pass value as float val.
            value = value.total_seconds()
        return getattr(super(TimeDelta, self), 'convert_to_%s' % method)(
            value,
            *args,
            **kwargs
        )
