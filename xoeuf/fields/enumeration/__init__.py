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

from collections import namedtuple
from xoutil.eight import string_types

from xoeuf import signals

__all__ = ['Enumeration']

Member = namedtuple('Member', ('name', 'value'))


def Enumeration(enumclass, *args, **kwargs):
    '''Create an enumeration field.

    The `enumclass` argument must be either an `enumeration class` or a
    fully qualified name of an enumeration class.

    The column in the DB will be either of type INTEGER or a CHAR: If **all**
    values of the enumeration are integers (instances of `int`, possibly by
    subclassing), the DB column will be a integer.  Otherwise, it will be a
    char with the *name* of the enumeration's key.

    .. warning:: In a future release we might drop the INTEGER/CHAR
       variation.

       This is to avoid possible mistakes: you create an enumeration with
       integers and afterwards you change to other types; that would require a
       migration step in the DB to convert old integer values to names.

    .. note:: Even in Python 2, we test for instances of `int`.  So values of
       type `long` won't be considered integers.

    Enumeration classes are required to:

    - have an attribute ``__members__`` with a `collections.Mapping`:class:
      from names to values.

    - have an attribute for each name in ``__member__`` with the same value as
      in the mapping.

    Those rules imply::

       >>> all(getattr(enumclass, name) is value
       ...     for name, value in enumclass.__members__.items())

    These requirements are compatible with Python 3.4's `enum.Enum`:class:
    However, we don't require that values are instances of the enumeration
    class.

    .. versionchanged:: 0.36.0 A new generalized enumeration field.  Maintains
       DB compatibility (does not need migrations), but do require changes in
       the code.

    .. warning:: To avoid mistakes in the final 1.0 release (or some releases
       before that) the column DB will always be a CHAR representing the
       member's name.

    '''
    from xoeuf import fields
    from xoutil.objects import import_object, classproperty

    enumclass = import_object(enumclass)
    members_integers = all(
        isinstance(value, int)
        for value in enumclass.__members__.values()
    )
    Base = fields.Integer if members_integers else fields.Char

    class EnumeratedField(Base, _EnumeratedField):
        @classproperty
        def members(cls):
            return enumclass.__members__

        def convert_to_read(self, value, record, use_name_get=True):
            if value is not None and value is not False:
                return self.get_member_by_value(value).value
            else:
                return value

        if Base is fields.Integer:
            def convert_to_write(self, value, record):
                if value:
                    return self.get_member_by_value(value).value
                else:
                    return value

            def convert_to_record(self, value, record, validate=True):
                if value:
                    return self.get_member_by_value(value).value
                elif value == 0:
                    # Odoo converts NULL to 0 for Integers, we try to find a
                    # 0-member, and return False if not found.
                    try:
                        return self.get_member_by_value(value).value
                    except ValueError:
                        return False
                return value
        else:
            def convert_to_write(self, value, record):
                if value is not None and value is not False:
                    member = self.get_member_by_value(value)
                    return member.name
                else:
                    return value

            def convert_to_record(self, value, record, validate=True):
                if value is not None and value is not False:
                    return self.get_member_by_name(value).value
                return value

    return EnumeratedField(*args, **kwargs)


class _EnumeratedField(object):
    @classmethod
    def get_member_by_value(cls, value):
        '''Find the enumclass's member that is equal to `value`.'''
        try:
            return next(
                Member(k, v)
                for k, v in cls.members.items()
                if v == value
            )
        except StopIteration:
            raise ValueError(
                'Invalid member %r of enumeration %r' % (value, cls.members)
            )

    @classmethod
    def get_member_by_name(cls, name):
        '''Find the enumclass's member by name'''
        try:
            return Member(name, cls.members[name])
        except (AttributeError, KeyError):
            raise ValueError(
                'Invalid key %r of enumeration %r' % (name, cls.members)
            )


@signals.receiver([signals.pre_create, signals.pre_write], framework=True)
def _select_db_value(sender, signal, values=None, **kwargs):
    # I expect the clients of Enumeration fields to use `create` and `write`,
    # without regard of how those values will be actually stored in the DB.
    # Yet Odoo sends those values right through psycopg2 throat.  So this
    # pre-writer signals serves the dual purpose of validating the value and
    # changing that value to it's DB counterpart.
    #
    # If the `value` is not a member of the field, raise a ValueError
    #
    # Notice we iterate over a copy of the dict because we're possibly
    # changing `values` in the loop.
    for fieldname, value in dict(values).items():
        field = sender._fields.get(fieldname, None)
        values[fieldname] = _get_db_value(field, value)


@signals.receiver(signals.pre_search, framework=True)
def _rewrite_db_values(sender, signal, query=None, **kwargs):
    for index, query_part in enumerate(query):
        if not isinstance(query_part, string_types):
            fieldname, operator, operands = query_part
            field = sender._fields.get(fieldname, None)
            if isinstance(field, _EnumeratedField):
                if operator in ('=', '!='):
                    values = _get_db_value(field, operands)
                elif operator in ('in', 'not in'):
                    values = [_get_db_value(field, o) for o in operands]
                else:
                    raise TypeError(
                        'Unsupported operator %r for an enumeration field' % operator
                    )
                query[index] = (fieldname, operator, values)


def _get_db_value(field, value):
    from xoeuf.odoo import fields
    if isinstance(field, _EnumeratedField):
        member = field.get_member_by_value(value)
        if isinstance(field, fields.Integer):
            return int(member.value)
        else:
            return member.name
    else:
        return value
