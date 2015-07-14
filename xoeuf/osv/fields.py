#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xouef.osv.fields
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise Autrement and Contributors
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
from datetime import datetime
from xoeuf.tools import normalize_datetime

from openerp.osv import fields as _v7_fields
# from openerp import fields as _v8_fields

try:
    from xoutil.datetime import strip_tzinfo  # migrate
except ImportError:
    def strip_tzinfo(dt):
        '''Return the given datetime value with tzinfo removed.

        '''
        from datetime import datetime  # noqa
        return datetime(*(dt.timetuple()[:6] + (dt.microsecond, )))


class localized_datetime(_v7_fields.function):
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

    def _ldt_write(self, obj, cr, uid, ids, field, val, args, context=None):
        tzone_field = self.__tzone_field
        dt_field = self.__dt_field
        tz = context.get('tz', None)
        if not tz:
            user = obj.pool['res.users'].browse(cr, uid, uid, context=context)
            tz = pytz.timezone(user.tz) if user.tz else pytz.UTC
        else:
            tz = pytz.timezone(tz)
        if isinstance(ids, (int, long)):
            ids = [ids]
        for row in obj.browse(cr, uid, ids, context=context):
            tzone = getattr(row, tzone_field, None)
            if not tzone:
                tzone = pytz.UTC
            else:
                tzone = pytz.timezone(tzone)
            dt = normalize_datetime(val)
            dt = pytz.UTC.localize(dt)
            # Compute the datetime as seen by the user, then force to it the
            # desired TZ and back to UTC.
            userdt = tz.normalize(dt) if tz is not pytz.UTC else dt
            faked = tzone.localize(strip_tzinfo(userdt))
            obj.write(
                cr, uid, [row.id],
                {dt_field: strip_tzinfo(pytz.UTC.normalize(faked))},
                context=context
            )

    def _ldt_read(self, obj, cr, uid, ids, field, arg, context=None):
        tzone_field = self.__tzone_field
        dt_field = self.__dt_field
        tz = context.get('tz', None)
        if not tz:
            user = obj.pool['res.users'].browse(cr, uid, uid, context=context)
            tz = pytz.timezone(user.tz) if user.tz else pytz.UTC
        else:
            tz = pytz.timezone(tz)
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = {}
        for row in obj.browse(cr, uid, ids, context=context):
            tzone = getattr(row, tzone_field, None)
            if not tzone:
                tzone = pytz.UTC
            else:
                tzone = pytz.timezone(tzone)
            dt = normalize_datetime(getattr(row, dt_field))
            dt = pytz.UTC.localize(dt)  # datetimes are UTC in the DB
            # Compute the datetime in the desired timezone, then extract
            # all datetime components but the TZ and localize it to the
            # users TZ and convert it back to UTC... This makes the UI to
            # reverse the process and show the datetime in the desired
            # timezone.
            local = tzone.normalize(dt) if tzone is not pytz.UTC else dt
            faked = tz.localize(strip_tzinfo(local))
            res[row.id] = strip_tzinfo(pytz.UTC.normalize(faked))
        return res

    def __init__(self, dt_field, tzone_field, **kwargs):
        self.__dt_field = dt_field
        self.__tzone_field = tzone_field
        super(localized_datetime, self).__init__(
            self._ldt_read, None, fnct_inv=self._ldt_write, store=False,
            **kwargs
        )
