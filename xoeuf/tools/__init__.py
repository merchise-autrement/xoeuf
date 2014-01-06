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

from datetime import datetime as _dt

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as _SVR_DATE_FMT
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as _SVR_DATETIME_FMT


def date2str(d):
    'Convert a date to a string using `OpenERP` default server format'
    return d.strftime(_SVR_DATE_FMT)


def dt2str(dt):
    'Convert a date-time to a string using `OpenERP` default server format'
    return dt.strftime(_SVR_DATETIME_FMT)


def str2dt(s):
    'Convert a string to a date-time using `OpenERP` default server format'
    from datetime import datetime
    return _dt.strptime(s, _SVR_DATETIME_FMT)


def str2date(s):
    'Convert a string to a date using `OpenERP` default server format'
    return _dt.strptime(s, _SVR_DATETIME_FMT)
