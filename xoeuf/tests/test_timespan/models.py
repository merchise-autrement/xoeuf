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

from xoeuf import models, fields


class TimeSpanValue(models.Model):
    _name = 'test.timespan.value'

    start_date = fields.Date()
    end_date = fields.Date()
    period = fields.TimeSpan('start_date', 'end_date')
