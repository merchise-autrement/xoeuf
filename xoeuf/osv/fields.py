#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''(Old fashioned) extensions to fields in the ORM.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


from xoutil.deprecation import deprecated

# FIX: Next doesn't work any more in version 10
from openerp.osv import fields as _v7_fields

import pytz
from xoeuf.tools import localtime_as_remotetime
import xoeuf.fields as _future


try:
    integer_types = (int, long)
except NameError:
    integer_types = (int, )


@deprecated(_future.LocalizedDatetime)
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
        if isinstance(ids, integer_types):
            ids = [ids]
        for row in obj.browse(cr, uid, ids, context=context):
            tzone = getattr(row, tzone_field)
            if not tzone:
                tzone = pytz.UTC
            else:
                tzone = pytz.timezone(tzone)
            # Compute the datetime in users timezone, then force to it the
            # desired TZ and back to UTC.
            if val:
                val = localtime_as_remotetime(val, tz, tzone)
            obj.write(
                cr, uid, [row.id],
                {dt_field: val},
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
        if isinstance(ids, integer_types):
            ids = [ids]
        res = {}
        for row in obj.browse(cr, uid, ids, context=context):
            tzone = getattr(row, tzone_field)
            if not tzone:
                tzone = pytz.UTC
            else:
                tzone = pytz.timezone(tzone)
            dt = getattr(row, dt_field)
            # Compute the datetime in the desired timezone, then extract
            # all datetime components but the TZ and localize it to the
            # users TZ and convert it back to UTC... This makes the UI to
            # reverse the process and show the datetime in the desired
            # timezone.
            if dt:
                dt = localtime_as_remotetime(dt, tzone, tz)
            res[row.id] = dt
        return res

    def __init__(self, dt_field, tzone_field, **kwargs):
        self.__dt_field = dt_field
        self.__tzone_field = tzone_field
        super(localized_datetime, self).__init__(
            self._ldt_read, None, fnct_inv=self._ldt_write, store=False,
            **kwargs
        )


del _future, deprecated
