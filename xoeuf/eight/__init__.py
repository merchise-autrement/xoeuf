#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
"""Part of xouti.eight we need to keep Python 2.7 compatibility.

"""
import sys

_py2 = sys.version_info[0] == 2
_py3 = sys.version_info[0] == 3

try:
    input = raw_input
except NameError:
    input = input

try:
    from xoutil.eight import string_types
except ImportError:
    string_types = (str,)

try:
    from xoutil.eight import integer_types
except ImportError:
    integer_types = (int,)


try:
    import __builtin__  # noqa

    builtins = __builtin__
except ImportError:
    import builtins  # noqa

    __builtin__ = builtins


try:
    exec_ = getattr(builtins, "exec")  # noqa
except AttributeError:

    def exec_(_code_, _globs_=None, _locs_=None):
        """Execute code in a namespace."""
        import sys

        if _globs_ is None:
            frame = sys._getframe(1)
            _globs_ = frame.f_globals
            if _locs_ is None:
                _locs_ = frame.f_locals
            del frame
        elif _locs_ is None:
            _locs_ = _globs_
        exec("""exec _code_ in _globs_, _locs_""")


def typeof(obj):
    """Obtain the object's type (compatible with Python 2**3)."""
    if _py3:
        return type(obj)
    else:
        from types import InstanceType

        return obj.__class__ if isinstance(obj, InstanceType) else type(obj)
