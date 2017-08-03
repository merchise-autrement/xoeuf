#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# _dt8
# ---------------------------------------------------------------------
# Copyright (c) 2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2017-02-02

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from openerp.release import version_info as ODOO_VERSION_INFO
assert (8, 0) <= ODOO_VERSION_INFO < (9, 0)
del ODOO_VERSION_INFO

import pytz
from openerp import fields

from xoeuf.tools import localtime_as_remotetime


class LocalizedDatetime(fields.Datetime):
    '''A field for localized datetimes.

    Localized datetimes are actually a functional field that takes two
    underlying columns a datetime and timezone name.

    :param dt: The name of the column where the datetime (in UTC) is actually
               saved.

    :param tzone:  The name of the column where the timezone where the event
                   should be presented to the user.

    Upon reading, we assume the user's timezone is properly set.

    The datetime column will be actually saved in UTC as all datetimes in
    Odoo.   But upon reading we convert to a properly shifted datetime so that
    is presented to the user in the saved time zone.

    .. note:: At the time this field is read-only, not searchable, and
              non-storable.

    '''

    _slots = {
        'dt_field': None,
        'tzone_field': None,
    }

    def compute(self, records):
        tzone_field = self.tzone_field
        dt_field = self.dt_field
        tz = records._context.get('tz', None)
        if not tz:
            user = records.env.user
            tz = pytz.timezone(user.tz) if user.tz else pytz.UTC
        else:
            tz = pytz.timezone(tz)
        for item in records:
            tzone = getattr(item, tzone_field)
            if not tzone:
                tzone = pytz.UTC
            else:
                tzone = pytz.timezone(tzone)
            dt = getattr(item, dt_field)
            # Compute the datetime in users timezone, then force to it the
            # desired TZ and back to UTC.
            if dt and tz != tzone:
                dt = localtime_as_remotetime(dt, tzone, tz)
            setattr(item, self.name, dt)

    def inverse(self, records):
        tzone_field = self.tzone_field
        dt_field = self.dt_field
        tz = records._context.get('tz', None)
        if not tz:
            user = records.env.user
            tz = pytz.timezone(user.tz) if user.tz else pytz.UTC
        else:
            tz = pytz.timezone(tz)
        for item in records:
            tzone = getattr(item, tzone_field)
            if not tzone:
                tzone = pytz.UTC
            else:
                tzone = pytz.timezone(tzone)
            dt = getattr(item, self.name)
            # Compute the datetime in the desired timezone, then extract
            # all datetime components but the TZ and localize it to the
            # users TZ and convert it back to UTC... This makes the UI to
            # reverse the process and show the datetime in the desired
            # timezone.
            if dt and tz != tzone:
                dt = localtime_as_remotetime(dt, tz, tzone)
            setattr(item, dt_field, dt)

    def search(self, records, operator, value):
        # TODO: localize value.
        return [(self.dt_field, operator, value)]

    def _setup_regular(self, env):
        super(LocalizedDatetime, self)._setup_regular(env)
        self.depends = (self.dt_field, self.tzone_field)

    def __init__(self, dt_field=None, tzone_field=None, **kwargs):
        self.dt_field = dt_field
        self.tzone_field = tzone_field
        # Include store=False and copy=False if not already included.
        kwargs = dict(dict(store=False, copy=False), **kwargs)
        super(LocalizedDatetime, self).__init__(
            dt_field=dt_field, tzone_field=tzone_field, **kwargs
        )
