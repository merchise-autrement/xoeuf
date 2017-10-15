#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


from xoeuf.odoo import api, fields


@api.model
def _tz_get(self):
    import pytz

    def key(tz):
        return tz if not tz.startswith('Etc/') else '_'

    return [(tz, "(" + tz + ")") for tz in sorted(pytz.all_timezones, key=key)]


def TimezoneSelection(*args, **kwargs):
    '''A selection field for installed timezones.

    '''
    return fields.Selection(
        _tz_get,
        *args,
        **kwargs
    )
