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

from xoeuf import models, api

__all__ = ['Enumeration']

Member = namedtuple('Member', ('name', 'value'))


def Enumeration(enumclass, *args, **kwargs):
    '''Create an enumeration field.

    The `enumclass` argument must be either an `enumeration class` or a
    fully qualified name of an enumeration class.

    The column in the DB will be either of type INTEGER or a CHAR: If **all**
    values of the enumeration are integers (instances of `int`, possibly by
    subclassing), the DB column will be a integer unless you pass a keyword
    argument 'force_char_column' set to True.  Otherwise, it will be a char
    with the *name* of the enumeration's key.

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

    .. versionchanged:: 0.47.0 Add keyword parameter 'force_char_column'.

    '''
    from xoeuf import fields
    from xoutil.objects import import_object, classproperty

    force_char_column = kwargs.get('force_char_column', False)
    enumclass = import_object(enumclass)
    if force_char_column:
        members_integers = False
    else:
        members_integers = all(
            isinstance(value, int)
            for value in enumclass.__members__.values()
        )
    Base = fields.Integer if members_integers else fields.Char

    class EnumeratedField(Base, _EnumeratedField):
        @classproperty
        def members(cls):
            return enumclass.__members__

        def setup_full(self, model):
            # Injects a new class in the model MRO, so that we can guarantee
            # the expectation about the methods create, write and search.
            #
            # The alternative would be to implement pre_save and pre_search
            # receivers.  But that would run for ALL models regardless of the
            # presence of Enumeration fields.  Also, we need to rewrite the
            # argument in the 'search' method, and signals are designed for
            # such use case (although they work at the moment).
            #
            cls = type(model)
            if EnumerationAdapter not in cls.__bases__:
                cls.__bases__ = (EnumerationAdapter, ) + cls.__bases__
            return super(EnumeratedField, self).setup_full(model)

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

            def convert_to_cache(self, value, record, validate=True):
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
                    if value in enumclass.__members__.values():
                        member = self.get_member_by_value(value)
                        # Our EnumerationAdapter takes care of doing the right
                        # thing when writing to the DB, also convert_to_column
                        # does.
                        return member.value
                return value

            def convert_to_cache(self, value, record, validate=True):
                if value not in enumclass.__members__.values():
                    if value is not None and value is not False:
                        return self.get_member_by_name(value).value
                return value

            def convert_to_column(self, value, record, values=None):
                if value in enumclass.__members__.values():
                    return Base.convert_to_column(
                        self,
                        self.get_member_by_value(value).name,
                        record
                    )
                else:
                    return Base.convert_to_column(self, value, record)

    return EnumeratedField(*args, **kwargs)


class EnumerationAdapter(object):
    'Adapt the create/write/search method to Enumeration fields.'
    # See the note in setup_full above.

    # Odoo 11 requires all bases to have these attributes.  See
    # odoo/models.py, method _build_model_attributes in lines 515-555 (at the
    # time of writing).
    _table = None
    _description = None
    _sequence = None
    _inherits = _depends = {}
    _sql_constraints = []
    _constraints = []

    @api.model
    @api.returns(*models.BaseModel.search._returns)
    def search(self, args, *pos_args, **kwargs):
        for index, query_part in enumerate(args):
            if not isinstance(query_part, string_types):
                fieldname, operator, operands = query_part
                field = self._fields.get(fieldname, None)
                if isinstance(field, _EnumeratedField):
                    if operator in ('=', '!='):
                        values = _get_db_value(field, operands)
                    elif operator in ('in', 'not in'):
                        values = [_get_db_value(field, o) for o in operands]
                    else:
                        raise TypeError(
                            'Unsupported operator %r for an enumeration field' % operator
                        )
                    args[index] = (fieldname, operator, values)
        return super(EnumerationAdapter, self).search(args, *pos_args, **kwargs)

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, values):
        for fieldname, value in dict(values).items():
            field = self._fields.get(fieldname, None)
            values[fieldname] = _get_db_value(field, value)
        return super(EnumerationAdapter, self).create(values)

    @api.multi
    def write(self, values):
        for fieldname, value in dict(values).items():
            field = self._fields.get(fieldname, None)
            values[fieldname] = _get_db_value(field, value)
        return super(EnumerationAdapter, self).write(values)


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


def _get_db_value(field, value):
    from xoeuf.odoo import fields
    if value is None or value is False:  # and not field.required
        return value
    if isinstance(field, _EnumeratedField):
        member = field.get_member_by_value(value)
        if isinstance(field, fields.Integer):
            return member.value
        else:
            return member.name
    else:
        return value
