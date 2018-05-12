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

import pytest
from hypothesis import strategies, given

formats = strategies.sampled_from(
    ('%H:%M', '%H:%M:%S', '%H:%M:%S.%f')
)


@given(strategies.times(), strategies.times(), formats)
def test_timerange(t1, t2, fmt):
    from xoeuf.fields.timerange.utils import TimeRange
    start = min(t1, t2)
    end = max(t1, t2)

    timerange = TimeRange(start, end.strftime(fmt))
    assert eval(repr(timerange)) == timerange

    if start != end:
        with pytest.raises(ValueError):
            TimeRange(end, start)
