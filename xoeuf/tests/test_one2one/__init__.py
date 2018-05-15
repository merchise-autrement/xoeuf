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


class A(models.Model):
    _name = 'test.one2one.a'
    name = fields.Char()


class B(models.Model):
    _name = 'test.one2one.b'
    _inherits = {'test.one2one.a': 'a_id'}


class C(models.Model):
    _name = 'test.one2one.c'
    _inherits = {'test.one2one.a': 'a_id'}

    a_id = fields.One2one('test.one2one.a')
