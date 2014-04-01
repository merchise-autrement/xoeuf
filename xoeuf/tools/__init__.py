# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoeuf.tools
#----------------------------------------------------------------------
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# @created: 2013-04-20

'''Xœuf tools for Open Object (OpenERP) models.

'''

from datetime import datetime as _dt, date as _d

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as _SVR_DATE_FMT
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as _SVR_DATETIME_FMT


def date2str(d):
    'Convert a date to a string using `OpenERP` default date format'
    return d.strftime(_SVR_DATE_FMT)


def dt2str(dt):
    'Convert a date-time to a string using `OpenERP` default datetime format'
    return dt.strftime(_SVR_DATETIME_FMT)


def str2dt(s):
    'Convert a string to a date-time using `OpenERP` default datetime format'
    return _dt.strptime(s, _SVR_DATETIME_FMT)
parse_datetime = str2dt


def str2date(s):
    'Convert a string to a date-time using `OpenERP` default date format.'
    return _dt.strptime(s, _SVR_DATE_FMT)
parse_date = str2date


def normalize_datetime(which):
    '''Normalizes `which` to a datetime.

    If `which` is a `datetime` is returned unchanged.  If is a `date` is
    returned as a `datetime` with time components set to 0.  Otherwise, it
    must be a string with either of OpenERP's date or date-time format.  The
    date-time format is used first.

    For instance, having ``now`` and ``today`` values like::

       >>> import datetime
       >>> from xoutil.objects import validate_attrs
       >>> now = datetime.datetime.now()
       >>> today = datetime.date.today()

    Then, ``now`` is returned as-is::

       >>> normalize_datetime(now) is now
       True

    But ``today`` is converted to a `datetime` with the same date components::

       >>> dtoday = normalize_date(today)
       >>> validate_attrs(today, dtoday,
       ...                force_equals=('year', 'month', 'day'))
       True

    If a string is given, a `datetime` is returned::

       >>> normalize_date('2014-02-12')
       datetime.datetime(2014, 2, 12, 0, 0)


    If the string does not match any of the server's date or datetime format,
    raise a ValueError::

       >>> normalize_date('not a date')  # doctest: +ELLIPSIS
       Traceback (most recent call last)
          ...
       ValueError: ...

    '''
    from xoutil.compat import str_base as string_types
    if isinstance(which, _dt):
        return which
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
