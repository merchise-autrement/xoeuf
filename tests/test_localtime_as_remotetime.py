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

from hypothesis import strategies, given
from hypothesis.extra.pytz import timezones
from xoeuf.tools import localtime_as_remotetime, normalize_datetime


@given(
    strategies.datetimes(
        min_value=normalize_datetime('1900-01-01'),
        max_value=normalize_datetime('2100-12-31')
    ),
    timezones(),
    timezones()
)
def test_(_dt, from_tz, to_tz):
    _dt = normalize_datetime(_dt)
    assert _dt == localtime_as_remotetime(
        localtime_as_remotetime(_dt, from_tz, to_tz),
        to_tz,
        from_tz
    )
    assert _dt == localtime_as_remotetime(
        localtime_as_remotetime(_dt, from_tz, to_tz, ignore_dst=True),
        to_tz,
        from_tz,
        ignore_dst=True
    )
