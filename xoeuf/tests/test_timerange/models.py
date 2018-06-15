#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoeuf import fields, models


class TestTimeRange(models.Model):
    _name = 'test.time.range'

    time_value = fields.Float()
    range_value = fields.TimeRange(
        time_field='time_value',
        selection=[
            ('morning', 'Morning', '6:00', '11:59'),
            ('noon', 'Noon', '12:00', '13:59'),
            ('afternoon', 'Afternoon', '14:00', '18:59')
        ]
    )
