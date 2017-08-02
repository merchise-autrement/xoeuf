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

from xoeuf import models, fields


class Value(models.Model):
    _name = 'test.property.value'

    value = fields.Char()

    @fields.Property
    def inverted(self):
        return ''.join(reversed(self.value)) if self.value else self.value

    @inverted.setter
    def inverted(self, value):
        self.value = ''.join(reversed(value)) if value else value

    @inverted.deleter
    def inverted(self):
        self.value = None
