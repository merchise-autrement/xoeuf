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

from .base import Property as Base


class Property(Base):
    def setup_full(self, model):
        res = super(Property, self).setup_full(model)
        if self.property_onsetup:
            self.property_onsetup(self, model)
        return res
