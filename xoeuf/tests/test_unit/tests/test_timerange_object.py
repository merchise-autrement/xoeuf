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

import unittest
from hypothesis import strategies, given
from datetime import datetime

formats = strategies.sampled_from(
    ('%H:%M', '%H:%M:%S', '%H:%M:%S.%f')
)


class TestTimeRange(unittest.TestCase):
    @given(strategies.times(), strategies.times())
    def test_timerange(self, t1, t2):
        from xoeuf.fields.timerange.utils import TimeRange
        start = min(t1, t2)
        end = max(t1, t2)
        timerange = TimeRange(start, end)
        self.assertEqual(eval(repr(timerange)), timerange)
        if start != end:
            with self.assertRaises(ValueError):
                TimeRange(end, start)

    @given(strategies.times(), strategies.times(), formats)
    def test_timerange_fmt(self, t1, t2, fmt):
        from xoeuf.fields.timerange.utils import TimeRange
        # Since any of t1 or t2 will be formatted, for the 'end', I have to make
        # sure that start < end.
        t1 = datetime.strptime(t1.strftime(fmt), fmt).time()
        t2 = datetime.strptime(t2.strftime(fmt), fmt).time()
        start = min(t1, t2)
        end = max(t1, t2)
        TimeRange(start, end.strftime(fmt))
