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
from xoutil.eight import string_types

from odoo.fields import Selection, Datetime, Float, Default as DEFAULT

from xoeuf.tools import normalize_datetime, get_time_from_float

from .utils import TimeRange as _TimeRangeObject


class TimeField(_TimeRangeObject):
    def __init__(self, start, end, name):
        super(TimeField, self).__init__(start, end)
        self.name = name


class TimeRangeSelector(object):
    def __init__(self, choices=[]):
        self.ranges = [TimeField(c[2], c[3], c[0]) for c in choices]

    def get_range(self, _time=time.min):
        if isinstance(_time, datetime):
            _time = _time.time()
        return next(
            (_range for _range in self.ranges if _time in _range),
            None
        )


# TODO: This is not actually a Selection.  In a selection the user is allowed
# to select a value from a collection.  This is kind of computation of a set
# from a given classifier.
class TimeRange(Selection):
    """A timerange field.

    .. warning:: This field is still experimental and may heavily changed or
       removed.

    A field calculated from two elements, the field that contains the time of day
    represented either by a 'datetime' or a 'float' and the list of possible
    values of time ranges in a day.

    :param t_field: The name of the column that contains the day time.

    :param selection: The possible ranges for this field.  It is given as
        either a list of tuples ``(value, string, start, end)``, a model
        method, or a method name.  `value` is the range identifier; `string`
        is the translatable text to show; `start` and `end` are values of
        times expressed in the 'hour:minutes' format.

    :param selection_add: Adds more options to the `selection`.  Only needed
                          if your extending an existing model's field.

    """
    type = 'timerange'

    _slots = {
        'time_field': None,
        'readonly': True,
    }

    def __init__(self, time_field, selection=DEFAULT, *args, **kwargs):
        from xoutil.symbols import Unset
        kwargs = dict(
            dict(copy=False, readonly=True),
            **kwargs
        )
        super(TimeRange, self).__init__(
            time_field=time_field or Unset,
            selection=selection,
            *args,
            **kwargs
        )
        self.time_field = time_field or Unset

    def new(self, **kwargs):
        # Pass original args to the new one.  This ensures that the
        # t_field and selection are present.  In odoo/models.py, Odoo calls
        # this `new()` without arguments to duplicate the fields from parent
        # classes.
        return type(self)(self.time_field, **kwargs)

    def setup_full(self, model):
        super(TimeRange, self).setup_full(model)
        time_field = self.time_field
        field = model._fields[time_field]
        if not isinstance(field, (Datetime, Float)):
            raise TypeError(
                'Type of time_field must be Datetime or Float, '
                'instead of %s.' % type(field)
            )

    def _setup_regular_full(self, env):
        # This is to support the case where ModelB `_inherits` from a ModelA
        # with a timerange. In such a case, we don't override the
        # compute method.
        super(TimeRange, self)._setup_regular_full(env)
        self.depends = (self.time_field,)
        self.compute = self._compute

    def _description_selection(self, env):
        """ return the selection list (tuple (value, label, start, end)); labels
            are translated according to context language
        """
        selection = self.selection
        if isinstance(selection, string_types):
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

    def _dict_selection(self, env):
        """ return a dictionary value:translatable String """
        selection = self.selection
        if env.lang and isinstance(selection, list):
            name = "%s,%s" % (self.model_name, self.name)
            translate = partial(
                env['ir.translation']._get_source,
                name,
                'selection',
                env.lang
            )
            return {
                value: translate(label) if label else label
                for value, label, start, end in selection
            }
        if isinstance(selection, string_types):
            selection = getattr(env[self.model_name], selection)()
        if callable(selection):
            selection = selection(env[self.model_name])
        return {
            value: label
            for value, label, start, end in selection
        }

    def get_values(self, env):
        """ return a list of the possible values """
        selection = self.selection
        if isinstance(selection, string_types):
            selection = getattr(env[self.model_name], selection)()
        elif callable(selection):
            selection = selection(env[self.model_name])
        return [value for value, _, _, _ in selection]

    def _compute(self, records):
        time_field = self.time_field
        env = records.env
        field = records._fields[time_field]
        for item in records:
            t_value = getattr(item, time_field)
            if isinstance(field, Datetime):
                dt = normalize_datetime(t_value)
                _time = dt.time()
            if isinstance(field, Float):
                _time = get_time_from_float(t_value)
            setattr(item, self.name, self._compute_selection(_time, env))

    def _compute_selection(self, time_value, env):
        selections = self._description_selection(env)
        _range = TimeRangeSelector(selections).get_range(time_value)
        if _range:
            return _range.name
        return False
