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
from xoeuf import models, fields, api


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


class WorkType(int):
    pass


class WORK_TYPE(object):
    easy = WorkType(0)
    hard = WorkType(1)
    __members__ = {'easy': easy, 'hard': hard}


class Model(models.Model):
    _name = 'test.enum.model'
    color = fields.Enumeration(COLORS)
    color_name = fields.Selection(
        selection=[(name, name) for name in COLORS.__members__],
        compute='_compute_color_name',
        inverse='_set_color_name',
        store=False,
    )

    car = fields.Enumeration(CARS)
    pax = fields.Enumeration(Pax)
    wtype = fields.Enumeration(WORK_TYPE, default=WORK_TYPE.hard)

    color2 = fields.Enumeration(COLORS, force_char_column=True)
    color2_name = fields.Selection(
        selection=[(name, name) for name in COLORS.__members__],
        compute='_compute_color2_name',
        inverse='_set_color2_name',
        store=False,
    )

    color3 = fields.Enumeration(COLORS, force_char_column=True,
                                default=COLORS.Red)

    @api.multi
    @api.depends('color')
    def _compute_color_name(self):
        for record in self:
            record.color_name = next(
                name
                for name, value in COLORS.__members__.items()
                if value == record.color
            )

    @api.multi
    def _set_color_name(self):
        for record in self:
            record.color = COLORS.__members__[record.color_name]

    @api.multi
    @api.depends('color2')
    def _compute_color2_name(self):
        for record in self:
            record.color2_name = next(
                name
                for name, value in COLORS.__members__.items()
                if value == record.color2
            )

    @api.multi
    def _set_color2_name(self):
        for record in self:
            record.color2 = COLORS.__members__[record.color2_name]
