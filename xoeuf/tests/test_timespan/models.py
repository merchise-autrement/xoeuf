#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# models
# ---------------------------------------------------------------------
# Copyright (c) 2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2017-08-01


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoeuf import models, fields, api
from xoeuf.odoo.tools.safe_eval import safe_eval


class TimeSpanValue(models.Model):
    _name = 'test.timespan.value'

    start_date = fields.Date()
    end_date = fields.Date()
    period = fields.TimeSpan('start_date', 'end_date')
