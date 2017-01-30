#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xouef.osv.fields
# ---------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-07-14

'''(Old fashioned) extensions to fields in the ORM.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


import pytz
from xoeuf.tools import localtime_as_remotetime
from openerp.release import version_info as ODOO_VERSION_INFO

if ODOO_VERSION_INFO < (10, 0):
    from openerp import fields


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
        }

        def compute(self, records):
            tzone_field = self.__tzone_field
            dt_field = self.__dt_field
            tz = self._context.get('tz', None)
            if not tz:
                user = self.env.user
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
                if dt:
                    dt = localtime_as_remotetime(dt, tz, tzone)
                setattr(item, self.name, dt)

        def inverse(self, records):
            tzone_field = self.__tzone_field
            dt_field = self.__dt_field
            tz = self._context.get('tz', None)
            if not tz:
                user = self.env.user
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
                if dt:
                    dt = localtime_as_remotetime(dt, tzone, tz)
                setattr(item, dt_field, dt)

        def search(self, records, operator, value):
            # TODO: localize value.
            return [(self.__dt_field, operator, value)]

        def setup(self, env):
            if not self.setup_done:
                self.depends = (self.qty_field, self.uom_field)
            super(LocalizedDatetime, self).setup(env)

        def __init__(self, dt_field, tzone_field, **kwargs):
            self.__dt_field = dt_field
            self.__tzone_field = tzone_field
            # Include store=False if is not include in kwargs
            kwargs = dict(dict(store=False), **kwargs)
            super(LocalizedDatetime, self).__init__(**kwargs)


else:
    from odoo import fields


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
        }

        def __init__(self, dt_field=None, tzone_field=None, **kwargs):
            # Include store=False if is not include in kwargs
            self.dt_field = dt_field
            self.tzone_field = tzone_field
            kwargs = dict(dict(store=False), **kwargs)
            super(LocalizedDatetime, self).__init__(**kwargs)
            pass

        def setup_full(self, env):
            super(LocalizedDatetime, self).setup_full(env)
            self.depends = tuple(
                [f for f in (self.dt_field, self.tzone_field) if f]
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
                user = self.env.user
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
                if dt:
                    dt = localtime_as_remotetime(dt, tz, tzone)
                setattr(item, self.name, dt)

        def _inverse(self, records):
            tzone_field = self.tzone_field
            dt_field = self.dt_field
            tz = records._context.get('tz', None)
            if not tz:
                user = self.env.user
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
                if dt:
                    dt = localtime_as_remotetime(dt, tzone, tz)
                setattr(item, dt_field, dt)

        def _search(self, records, operator, value):
            # TODO: localize value.
            return [(self.dt_field, operator, value)]
