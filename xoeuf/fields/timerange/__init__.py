#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from datetime import datetime, time
from functools import partial

from odoo.fields import Selection, Datetime, Float

from xoeuf.tools import normalize_datetime, get_time_from_float
from xoeuf.odoo.tools import pycompat

from .utils import TimeRange as TimeRangeObject


Default = object()  # default value for __init__() methods


class TimeRangeSelector(object):
    ranges = list()

    def __init__(self, choices=[]):
        self.ranges = [TimeRangeObject(c[2], c[3]) for c in choices]

    def get_range(self, _time=time.min):
        if isinstance(_time, datetime):
            _time = time.time()
        for _range in self.ranges:
            if _time in _range:
                return _range
        else:
            return None


class TimeRange(Selection):
    """A timerange field

    A field calculated from two elements, the field that contains the time of day
    represented either by a 'datetime' or a 'float' and the list of possible
    values of time ranges in a day.

    :param t_field: The name of the column that contains the day time.

    :param selection: specifies the possible values for this field.
        It is given as either a list of tuples
        (``value``, ``string``,``start``,``end``), or a model method, or a
        method name.
        ``value`` is the range identifier
        ``string`` is the translatable text to show
        ``start``, ``end`` are values of times expressed in the
            'hour:minutes' format.
    :param selection_add: provides an extension of the selection in the case
        of an overridden field. It is a list of tuples same as ``selection``.

    Attributes ``selection`` and ``t_field`` are mandatory.

    """
    type = 'timerange'

    _slots = {
        't_field': None,
        'readonly': True,
    }

    def __init__(self, t_field=Default, selection=Default, string=Default, **kwargs):
        # Include readonly=True if is not include in kwargs
        kwargs = dict(
            dict(copy=False, readonly=True),
            **kwargs
        )
        super(TimeRange, self).__init__(
            t_field=t_field,
            selection=selection,
            string=string,
            **kwargs
        )

    def new(self, **kwargs):
        # Pass original args to the new one.  This ensures that the
        # tzone_field and dt_field are present.  In odoo/models.py, Odoo calls
        # this `new()` without arguments to duplicate the fields from parent
        # classes.
        kwargs = dict(self.args, **kwargs)
        return super(TimeRange, self).new(**kwargs)

    def _setup_regular_base(self, model):
        super(TimeRange, self)._setup_regular_base(model)
        t_field = self.t_field
        if not t_field:
            raise TypeError('TimeRange requires the surrogates fields')
        field = model._fields[t_field]
        if not isinstance(field, (Datetime, Float)):
            raise TypeError(
                'Type of t_field must be Datetime or Float, '
                'instead of %s.' % type(field)
            )

    def _setup_regular_full(self, env):
        # This is to support the case where ModelB `_inherits` from a ModelA
        # with a timerange. In such a case, we don't override the
        # compute method.
        super(TimeRange, self)._setup_regular_full(env)
        self.depends = (self.t_field,)
        self.compute = self._compute

    def _description_selection(self, env):
        """ return the selection list (tuple (value, label, start, end)); labels
            are translated according to context language
        """
        selection = self.selection
        if isinstance(selection, pycompat.string_types):
            return getattr(env[self.model_name], selection)()
        if callable(selection):
            return selection(env[self.model_name])

        # translate selection labels
        if env.lang:
            name = "%s,%s" % (self.model_name, self.name)
            translate = partial(
                env['ir.translation']._get_source, name, 'selection', env.lang)
            return [(value, translate(label), start, end if label else label)
                    for value, label, start, end in selection]
        else:
            return selection

    def get_values(self, env):
        """ return a list of the possible values """
        selection = self.selection
        if isinstance(selection, pycompat.string_types):
            selection = getattr(env[self.model_name], selection)()
        elif callable(selection):
            selection = selection(env[self.model_name])
        return [value for value, _, _, _ in selection]

    def _compute(self, records):
        t_field = self.t_field
        env = records.env
        field = records._fields[t_field]
        for item in records:
            t_value = getattr(item, t_field)
            if isinstance(field, Datetime):
                dt = normalize_datetime(t_value)
                _time = dt.time()
            if isinstance(field, Float):
                _time = get_time_from_float(t_value)
            setattr(item, self.name, self._compute_selection(_time, env))

    def _compute_selection(self, time_value, env):
        selections = self._description_selection(env)
        return TimeRangeSelector(selections).get_range(time_value)
