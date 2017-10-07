#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# _proxy
# ---------------------------------------------------------------------
# Copyright (c) 2016-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2016-11-10

'''Implementation for 'xoeuf.models.proxy'.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


import re

try:
    from xoeuf.odoo import models
except ImportError:
    # So that we can generate the docs easily
    pass


class ModelProxy(object):
    def __init__(self, name):
        self.__model = _get_model(name)
        self.__env = None

    @property
    def _this(self):
        import sys
        f = sys._getframe(1)
        try:
            this, tries = None, 5
            while this is None and tries and f:
                this = f.f_locals.get('self', None)
                if not isinstance(this, models.BaseModel):
                    this = cr = uid = None
                elif not hasattr(this, 'env'):
                    # We still need to support possible old-API methods
                    cr = f.f_locals.get('cr', None)
                    uid = f.f_locals.get('uid', None)
                    context = f.f_locals.get('context', None)
                    this = this.browse(cr, uid, context=context)
                f = f.f_back
                tries -= 1
            return this
        finally:
            f = None

    def __dir__(self):
        this = self._this
        if this is not None:
            return dir(this)
        else:
            return dir(models.BaseModel)

    def __getattr__(self, attr):
        this = self._this
        if this is not None:
            return getattr(this.env[self.__model], attr)
        else:
            raise RuntimeError(
                'Cannot find attribute %r in proxy model. This is most '
                'likely due to an invalid call site.' % attr
            )


def _get_model(name):
    if '.' in name:
        return name
    words, last = [], 0
    for i, match in enumerate(UPPERS.finditer(name)):
        pos = match.start()
        if i == 0:
            assert pos == 0, 'The first char must an upper case'
        else:
            words.append(name[last:pos].lower())
        last = pos
    words.append(name[last:].lower())
    return '.'.join(words)


UPPERS = re.compile('[A-Z]')
