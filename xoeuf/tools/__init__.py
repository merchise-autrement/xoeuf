#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Xœuf tools for Open Object (OpenERP) models.

'''
from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from datetime import datetime as _dt, date as _d, time as _t

try:
    from xoeuf.odoo.tools import safe_eval, float_round  # noqa: reexport
except ImportError:
    # This allows to generate the documentation without actually installing
    # Odoo
    pass


try:
    from xoeuf.odoo.tools import (
        DEFAULT_SERVER_DATE_FORMAT as _SVR_DATE_FMT,
        DEFAULT_SERVER_DATETIME_FORMAT as _SVR_DATETIME_FMT,
    )
except ImportError:
    # This allows to generate the documentation without actually installing
    # Odoo
    _SVR_DATE_FMT = '%Y-%m-%d'
    _SVR_DATETIME_FMT = '%Y-%m-%d %H:%M:%S'

import pytz

utc = pytz.UTC

_SVR_DATETIME_FMT2 = _SVR_DATETIME_FMT + '.%f'

try:
    from xoutil.future.datetime import without_tzinfo as strip_tzinfo  # noqa: migrate
except ImportError:
    def strip_tzinfo(dt):
        '''Return the given datetime value with tzinfo removed.

        '''
        from datetime import datetime  # noqa
        return datetime(*(dt.timetuple()[:6] + (dt.microsecond, )))


def localize_datetime(self, datetime_value=None, from_tz='UTC', to_tz='UTC'):
    """Convert datetime value from a timezone to another.

    We assume `datetime_value` is expressed in the timezone given in
    `from_tz`, i.e is a naive datetime.

    If `datetime_value` is None then context today is used.

    If `from_tz` or `to_tz` is None then user timezone is used.

    If `from_tz` is the same as `to_tz`, return `datetime_value`.

    """
    from xoeuf.odoo import fields
    if not from_tz:
        from_tz = self.env.user.tz or 'UTC'
    if not to_tz:
        to_tz = self.env.user.tz or 'UTC'
    if datetime_value:
        datetime_value = normalize_datetime(datetime_value)
    elif from_tz != 'UTC':
        datetime_value = normalize_datetime(fields.Date.context_today(self))
    else:
        datetime_value = normalize_datetime(fields.Datetime.now())
    if from_tz == to_tz:
        return datetime_value
    from_tz = pytz.timezone(from_tz)
    to_tz = pytz.timezone(to_tz)
    local_timestamp = from_tz.localize(datetime_value, is_dst=False)
    return strip_tzinfo(local_timestamp.astimezone(to_tz))


def date2str(d):
    '''Convert a date to a string using `OpenERP` default date format.

    If the argument is not a `datetime.date`:class:, normalize it first with
    `normalize_datetime`:func:.

    '''
    if not isinstance(d, _d):
        d = normalize_datetime(d)
    return d.strftime(_SVR_DATE_FMT)


normalize_datestr = date2str


def dt2str(dt):
    '''Convert a date-time to a string using `OpenERP` default datetime
    format.

    If the argument is not a `datetime.datetime`:class:, normalize it first
    with `normalize_datetime`:func:.

    '''
    if not isinstance(dt, _dt):
        dt = normalize_datetime(dt)
    return dt.strftime(_SVR_DATETIME_FMT)


normalize_datetimestr = dt2str


def str2dt(s):
    'Convert a string to a date-time using `OpenERP` default datetime format.'
    try:
        return _dt.strptime(s, _SVR_DATETIME_FMT)
    except ValueError:
        # Try a second time but allowing microseconds, this avoid some errors
        # when you save a .now() directly via the ORM.  It seems to not
        # sanitize properly the datetimes.
        return _dt.strptime(s, _SVR_DATETIME_FMT2)


parse_datetime = str2dt


def str2date(s):
    'Convert a string to a date-time using `OpenERP` default date format.'
    return _dt.strptime(s, _SVR_DATE_FMT)


parse_date = str2date


def normalize_datetime(which):
    '''Normalizes `which` to a datetime.

    If `which` is a `datetime`, we ensure it will yield a valid string
    (matches the OpenERP datetime format).

    If `which` is a `date` is returned as a `datetime` with time components
    set to 0.  Otherwise, it must be a string with either of OpenERP's date or
    date-time format.  The date-time format is used first.

    For instance, having ``now`` and ``today`` values like::

       >>> import datetime
       >>> from xoutil.objects import validate_attrs
       >>> now = datetime.datetime(2014, 12, 20, 16, 0, 17, 678233)
       >>> today = now.date()

    Then, ``now`` is returned as-is::

       >>> normalize_datetime(now)
       datetime.datetime(2014, 12, 20, 16, 0, 17)

    But ``today`` is converted to a `datetime` with the same date components::

       >>> dtoday = normalize_datetime(today)
       >>> validate_attrs(today, dtoday,
       ...                force_equals=('year', 'month', 'day'))
       True

    If a string is given, a `datetime` is returned::

       >>> normalize_datetime('2014-02-12')
       datetime.datetime(2014, 2, 12, 0, 0)

    If the string does not match any of the server's date or datetime format,
    raise a ValueError::

       >>> normalize_datetime('not a datetime')  # doctest: +ELLIPSIS
       Traceback (most recent call last):
          ...
       ValueError: ...

    '''
    from xoutil.eight import string_types
    if isinstance(which, _dt):
        return str2dt(dt2str(which))
    elif isinstance(which, _d):
        return _dt(which.year, which.month, which.day)
    elif isinstance(which, string_types):
        try:
            return parse_datetime(which)
        except ValueError:
            return parse_date(which)
    else:
        raise TypeError("Expected a string, date or date but a '%s' was given"
                        % type(which))


def normalize_date(which):
    '''Normalizes `which` to a date.

    If `which` is a `date` is returned unchanged.  If is a `datetime`, then
    its `~datetime.date`:func: method is used.  Otherwise, it must be a string
    with either of OpenERP's date or date-time format.  The date format is
    tried first.

    For instance, having ``now`` and ``today`` values like::

       >>> import datetime
       >>> now = datetime.datetime.now()
       >>> today = now.date()

    Then, ``today`` is returned as-if::

       >>> normalize_date(today) is today
       True

    But ``now`` is converted to a `date`

       >>> normalize_date(now) == today
       True

    If a string is given, a `date` is returned::

       >>> normalize_date('2014-02-12 10:00:00')
       datetime.date(2014, 2, 12)

    If the string does not match any of the server's date or datetime format,
    raise a ValueError::

       >>> normalize_date('not a date')  # doctest: +ELLIPSIS
       Traceback (most recent call last):
          ...
       ValueError: ...

    '''
    from xoutil.eight import string_types
    if isinstance(which, _dt):
        return which.date()
    elif isinstance(which, _d):
        return which
    elif isinstance(which, string_types):
        try:
            return parse_date(which).date()
        except ValueError:
            return parse_datetime(which).date()
    else:
        raise TypeError("Expected a string, date or date but a '%s' was given"
                        % type(which))


def dt_as_timezone(dt, tz_name=None):
    """ Localize datetime in desired timezone.

    :param datetime dt: datetime
    :param string tz_name: name of the timezone to localize the datetime
    :return: datetime with tzinfo, UTC in case tz_name is none.
    """
    dt = normalize_datetime(dt)
    if tz_name:
        tz = pytz.timezone(tz_name)
    else:
        tz = pytz.UTC
    return tz.localize(strip_tzinfo(dt))


def localtime_as_remotetime(dt_UTC, from_tz=utc, as_tz=utc):
    """ Compute the datetime as the timezone source,
    then force to it the desired TZ and back to UTC.

   :param datetime dt_UTC: datetime in UTC
   :param string from_tz: timezone to compute the datetime
   :param string as_tz: timezone to localize the datetime
   :return: datetime in desired timezone
   """

    dt_UTC = normalize_datetime(dt_UTC)
    if not isinstance(from_tz, pytz.tzinfo.tzinfo):
        from_tz = pytz.timezone(from_tz)
    if not isinstance(as_tz, pytz.tzinfo.tzinfo):
        as_tz = pytz.timezone(as_tz)
    if not dt_UTC.tzinfo:
        dt_UTC = dt_as_timezone(dt_UTC)
    local = from_tz.normalize(dt_UTC)
    faked = as_tz.localize(strip_tzinfo(local))
    return strip_tzinfo(pytz.UTC.normalize(faked))


def get_time_from_float(value):
    """Get time tuple from a float value.

    :param value: float value to convert to time tuple
    :return: time value)

    """
    hours, minutes = divmod(value * 60, 60)
    minutes, seconds = divmod(minutes * 60, 60)
    return _t(hour=int(hours), minute=int(minutes), second=int(seconds))


def get_time_string(time_value, up_24=True, include_seconds=False):
    """ Get a human friendly representation of time

    :param time_value: time value
    :param up_24: True for military time format
    :param include_seconds: True to include seconds value in result
    :return string time formatted like `13:01 PM`

    For instance, having ``now`` value like::

       >>> import datetime
       >>> now = datetime.time(hour=13, minute=24, second=14)

    Then

       >>> get_time_string(now)
       '13:24'

       >>> get_time_string(now, include_seconds=True)
       '13:24:14'

       >>> get_time_string(now, up_24=False)
       '01:24 PM'

       >>> get_time_string(now, up_24=False, include_seconds=True)
       '01:24:14 PM'

    """
    if up_24:
        result = time_value.strftime('%T' if include_seconds else '%R')
    else:
        result = time_value.strftime('%r' if include_seconds else '%I:%M %p')
    return result


def get_time_string_from_float(value, up_24=True, include_seconds=False):
    """ Get a human friendly representation of time from a float value.

    :param value: float value that represent a time value.
    :param up_24: True for military time format
    :param include_seconds: True to include seconds value in result
    :return string time formatted like `13:01 PM`

    For instance, having ``now`` value like::

       >>> value = 13.404

    Then

       >>> get_time_string_from_float(value)
       '13:24'

       >>> get_time_string_from_float(value, include_seconds=True)
       '13:24:14'

       >>> get_time_string_from_float(value, up_24=False)
       '01:24 PM'

       >>> get_time_string_from_float(value, False, True)
       '01:24:14 PM'
    """
    return get_time_string(
        get_time_from_float(value),
        up_24=up_24,
        include_seconds=include_seconds
    )
