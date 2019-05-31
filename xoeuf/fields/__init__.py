#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from __future__ import (
    division as _py3_division,
    print_function as _py3_print,
    absolute_import as _py3_abs_import,
)

from odoo.fields import *  # noqa: reexport

from .datetime import LocalizedDatetime  # noqa: reexport
from .properties import Property  # noqa: reexport
from .monetary import Monetary  # noqa: reexport
from .timespan import TimeSpan  # noqa: reexport
from .enumeration import Enumeration  # noqa: reexport
from .timezone import TimezoneSelection  # noqa: reexport
from .timedelta import TimeDelta  # noqa: reexport
from .one2one import One2one  # noqa: reexport
from .timerange import TimeRange  # noqa: reexport
from .reference import TypedReference  # noqa: reexport


try:
    del Serialized  # noqa
except NameError:
    pass
