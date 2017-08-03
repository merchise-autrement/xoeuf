#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# _dt10
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


try:
    from openerp.release import version_info as ODOO_VERSION_INFO
    from openerp import fields
except ImportError:
    from odoo.release import version_info as ODOO_VERSION_INFO
    from odoo import fields
assert ODOO_VERSION_INFO >= (9, 0)
del ODOO_VERSION_INFO

import pytz

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
        'dt_field': '',
        'tzone_field': '',
        'store': False,
    }

    def __init__(self, dt_field=None, tzone_field=None, **kwargs):
        # Include store=False if is not include in kwargs
        self.dt_field = dt_field
        self.tzone_field = tzone_field
        kwargs = dict(
            dict(store=False, copy=False, dt_field=dt_field,
                 tzone_field=tzone_field),
            **kwargs
        )
        super(LocalizedDatetime, self).__init__(**kwargs)

    def new(self, **kwargs):
        # pass origin field args to the new one.
        kwargs = dict(self.args, **kwargs)
        return super(LocalizedDatetime, self).new(**kwargs)

    def _setup_regular_full(self, env):
        # This is to support the case where ModelB `_inherits` from a ModelA
        # with a localized datetime.  In such a case, we don't override the
        # compute method.
        super(LocalizedDatetime, self)._setup_regular_full(env)
        self.depends = tuple(
            f for f in (self.dt_field, self.tzone_field) if f
        )
        self.compute = self._compute
        if not self.readonly:
            self.inverse = self._inverse
        self.search = self._search

    def _compute(self, records):
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
            # Compute the datetime in users timezone,
            # then force to it the desired TZ and back to UTC.
            if dt and tz != tzone:
                dt = localtime_as_remotetime(dt, tzone, tz)
            setattr(item, self.name, dt)

    def _inverse(self, records):
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
            # Compute the datetime in the desired timezone, then
            # extract all datetime components but the TZ and localize
            # it to the users TZ and convert it back to UTC...
            # This makes the UI to reverse the process and show the
            # datetime in the desired timezone.
            if dt and tz != tzone:
                dt = localtime_as_remotetime(dt, tz, tzone)
            setattr(item, dt_field, dt)

    def _search(self, records, operator, value):
        # TODO: localize value.
        return [(self.dt_field, operator, value)]
