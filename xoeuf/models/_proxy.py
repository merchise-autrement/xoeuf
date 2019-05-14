#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

"""Implementation for 'xoeuf.models.proxy'.

"""

from __future__ import (
    division as _py3_division,
    print_function as _py3_print,
    absolute_import as _py3_abs_import,
)


import re
from xoutil.objects import memoized_property

try:
    from xoeuf.odoo import models
except ImportError:
    # So that we can generate the docs easily
    pass


class ModelProxy(object):
    @memoized_property
    def _instances_(self):
        """All the *possible* instances of this model.

        The result is an object that allows for containment tests.  The
        containment test would be equivalent to an `isinstance` check.

        Example::

           from xoeuf.models.proxy import SomeModel
           record in SomeModel._instances_

        .. warning:: This may shadow an attribute '_instances_' in the proxied
           model.

        """
        model = self.__model

        class Instances(object):
            def __contains__(_, who):
                from xoeuf import models

                return isinstance(who, models.BaseModel) and who._name == model

        return Instances()

    def __init__(self, name):
        self.__model = _get_model(name)
        self.__env = None

    @property
    def _proxy_request(self):
        try:
            from xoeuf.odoo.http import request

            if request.env:  # An HTTP request may not be bound to a single DB.
                return request
        except RuntimeError:
            pass
        return None

    @property
    def _this(self):
        if self._proxy_request:
            return self._proxy_request.env
        import sys

        f = sys._getframe(1)
        try:
            this, tries = None, 5
            while this is None and tries and f:
                this = f.f_locals.get("self", None)
                if not isinstance(this, models.BaseModel):
                    this = cr = uid = None
                elif not hasattr(this, "env"):
                    # We still need to support possible old-API methods
                    cr = f.f_locals.get("cr", None)
                    uid = f.f_locals.get("uid", None)
                    context = f.f_locals.get("context", None)
                    this = this.browse(cr, uid, context=context)
                f = f.f_back
                tries -= 1
            return this.env if this is not None else None
        finally:
            f = None

    def __dir__(self):
        return dir(models.BaseModel)

    def __getattr__(self, attr):
        if attr in MODULE_ATTRS:
            return globals()[attr]
        this = self._this
        if this is not None:
            return getattr(this[self.__model], attr)
        else:
            raise RuntimeError(
                "Cannot find attribute %r in proxy model. This is most "
                "likely due to an invalid call site." % attr
            )

    def __repr__(self):
        return "<ModelProxy: %r>" % self.__model


def _get_model(name):
    if "." in name:
        return name
    words, last = [], 0
    for i, match in enumerate(UPPERS.finditer(name)):
        pos = match.start()
        if i == 0:
            assert pos == 0, "The first char must an upper case"
        else:
            words.append(name[last:pos].lower())
        last = pos
    words.append(name[last:].lower())
    return ".".join(words)


UPPERS = re.compile("[A-Z]")


# Attributes which others might think all modules should have and that
# shouldn't be delegated to the underlying model.
MODULE_ATTRS = ("__file__", "__module__")


del memoized_property
