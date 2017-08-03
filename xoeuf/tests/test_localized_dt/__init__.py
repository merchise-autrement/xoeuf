#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# test_localized_datetime
# ---------------------------------------------------------------------
# Copyright (c) 2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2017-03-07


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


from xoeuf import fields, models


class ModelA(models.TransientModel):
    _name = __name__ + '.' + 'a'

    tzone = fields.Char(default='America/Havana')
    dt = fields.Datetime()
    dt_at_tzone = fields.LocalizedDatetime


class ModelB(models.TransientModel):
    _name = __name__ + '.' + 'b'
    _inherits = {models.get_modelname(ModelA): 'a_id'}
