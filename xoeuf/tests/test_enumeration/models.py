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

from enum import IntEnum, Enum
from xoeuf import models, fields


class COLORS(IntEnum):
    Blue = 0
    Red = 1
    Green = 2


class CARS(Enum):
    FORD = object()
    CHEV = object()


class Pax(object):
    single = 1
    double = 2
    __members__ = {'single': single, 'double': double}


class Model(models.Model):
    _name = 'test.enum.model'
    color = fields.Enumeration(COLORS)
    car = fields.Enumeration(CARS)
    pax = fields.Enumeration(Pax)
