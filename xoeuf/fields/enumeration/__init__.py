#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from __future__ import (
    division as _py3_division,
    print_function as _py3_print,
    absolute_import as _py3_abs_import,
)

from collections import namedtuple, Mapping
from xoutil.string import cut_prefix
from xoutil.objects import import_object

from odoo import fields, api, models
from odoo.fields import Char
from odoo.release import version_info as ODOO_VERSION_INFO

from ...eight import string_types


if ODOO_VERSION_INFO < (12,):
    api_create_signature = api.model
else:
    api_create_signature = api.model_create_multi

__all__ = ["Enumeration"]

Member = namedtuple("Member", ("name", "value"))


class _EnumeratedField(object):
    # I'm keeping this class just in case someone has been testing for it.
    pass


class Enumeration(Char, _EnumeratedField):
    """Create an enumeration field.

    The `enumclass` argument must be either an `enumeration class` or a fully
    qualified name of an enumeration class.  If either way return a callable,
    it must accept a single argument (the model) and return the enumeration
    class.

    The actual enumeration used per model is stored in the ``Enumclass``
    attribute.

    The column in the DB will be of type CHAR and the values are the name of
    attribute in the enumeration class.

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

    .. rubric:: Automatic selection field

    Enumeration fields cannot be put in views because their values can be
    arbitrary Python objects which are not easily transferred to/from the web
    client.

    You can use the parameter 'selection_field_name' to automatically inject a
    computed Selection field that allows to represent this Enumeration in the
    web client.  This automatic is by default not stored in the DB.  Its
    values are the names of the members of the enumeration class.

    You may pass a function 'compute_member_string' which will be called to
    get the user facing text of each member.  The function will be passed both
    the name and value of the member.  By default we return the member's name.

    Additional keyword arguments starting with the prefix ``selection_field_``
    are used to construct the Selection field.  For instance,
    'selection_field_string' sets the argument 'string'.  If not provided, we
    set 'string', and 'help' to the same values of the Enumeration field.

    .. versionchanged:: 0.36.0 A new generalized enumeration field.  Maintains
       DB compatibility (does not need migrations), but do require changes in
       the code.

    .. versionchanged:: 0.47.0 Add keyword parameter 'force_char_column'.

    .. versionchanged:: 0.61.0 The DB column type is always a CHAR.  Ignore
       the parameter 'force_char_column'.

    .. versionchanged:: 0.61.0 Add an automatic way to create a selection
       field via the parameter 'selection_field_name'.

    .. versionchanged:: 0.64.0 The `enumclass` can be a callable.  Enumeration
       is now class instead of a function.  Gain the ``Enumclass`` attribute.

    """

    _slots = {
        "enumclass": None,
        "selection_field_kwargs": None,
        "compute_member_string": None,
    }

    def __init__(self, enumclass, *args, **kwargs):
        selection_field_kwargs = kwargs.pop("selection_field_kwargs", {})
        if not selection_field_kwargs:
            SELECTION_FIELD_PREFIX = "selection_field_"
            selection_field_kwargs = {
                cut_prefix(kw, SELECTION_FIELD_PREFIX): value
                for kw, value in kwargs.items()
                if kw.startswith(SELECTION_FIELD_PREFIX)
            }
            compute_member_string = kwargs.pop("compute_member_string", None)
            if compute_member_string:
                selection_field_kwargs["compute_member_string"] = compute_member_string

        super(Enumeration, self).__init__(
            enumclass=enumclass,
            selection_field_kwargs=selection_field_kwargs,
            *args,
            **kwargs
        )
        self.enumclass = enumclass
        self.selection_field_kwargs = selection_field_kwargs

    def new(self, **kwargs):
        enumclass = kwargs.pop("enumclass", self.enumclass)
        selection_field_kwargs = kwargs.pop(
            "selection_field_kwargs", self.selection_field_kwargs
        )
        return type(self)(
            enumclass=enumclass, selection_field_kwargs=selection_field_kwargs, **kwargs
        )

    def resolve_enumclass(self, model):
        enumclass = import_object(self.enumclass)

        if callable(enumclass) and not hasattr(enumclass, "__members__"):
            enumclass_factory = enumclass
        else:
            enumclass_factory = constant(enumclass)
        return enumclass_factory(model)

    def get_selection_field(
        self, field_name, name, compute_member_string=None, **kwargs
    ):
        """Return a computed Selection field to set/get the Enumeration.

        """
        selection_field_name = name

        @api.multi
        @api.depends(field_name)
        def _compute_selection_field(rs):
            for record in rs:
                value = getattr(record, field_name, None)
                if value is not None:
                    member = self.get_member_by_value(value)
                    setattr(record, selection_field_name, member.name)
                else:
                    setattr(record, selection_field_name, False)

        @api.multi
        def _set_selection(rs):
            for record in rs:
                key = getattr(record, selection_field_name, None)
                if key:
                    member = self.get_member_by_name(key)
                    setattr(record, field_name, member.value)
                else:
                    setattr(record, field_name, False)

        if not compute_member_string:
            compute_member_string = self._compute_member_string
        kwargs.setdefault("store", False)
        kwargs.setdefault("compute", _compute_selection_field)
        kwargs.setdefault("inverse", _set_selection)
        return fields.Selection(
            selection=lambda s: [
                (name, compute_member_string(name, value))
                for name, value in self.Enumclass.__members__.items()
            ],
            **kwargs
        )

    @staticmethod
    def _compute_member_string(name, value):
        return name

    def get_member_by_value(self, value):
        """Find the enumclass's member that is equal to `value`."""
        try:
            return next(
                Member(k, v)
                for k, v in self.Enumclass.__members__.items()
                if v == value
            )
        except StopIteration:
            raise ValueError(
                "Invalid member %r of enumeration %r"
                % (value, self.Enumclass.__members__)
            )

    def get_member_by_name(self, name):
        """Find the enumclass's member by name"""
        try:
            return Member(name, self.Enumclass.__members__[name])
        except (AttributeError, KeyError):
            raise ValueError(
                "Invalid key %r of enumeration %r" % (name, self.Enumclass.__members__)
            )

    def setup_full(self, model):
        # Injects a new class in the model MRO, so that we can guarantee
        # the expectation about the methods create, write and search.
        #
        # The alternative would be to implement pre_save and pre_search
        # receivers.  But that would run for ALL models regardless of the
        # presence of Enumeration fields.  Also, we need to rewrite the
        # argument in the 'search' method, and signals aren't designed for
        # such use case (although they work at the moment).
        #
        # We must find EnumerationAdapter in the MRO to avoid injecting it
        # twice when using Enumeration fields in abstract models.
        #
        # We don't need to inject the EnumerationAdapter in related
        # (delegated) copies for this Enumeration fields, because the
        # actual field does the right thing with DB (it does have the
        # EnumerationAdapter injected.)
        cls = type(model)
        if EnumerationAdapter not in cls.mro() and not self.related:
            cls.__bases__ = (EnumerationAdapter,) + cls.__bases__
            # I tried to use model._add_field because it changes the
            # cls._fields that Odoo is iterating and that raises an error
            # (RuntimeError: dictionary changed size during iteration).
            #
            # So let's resort to injection.
            if self.selection_field_kwargs:
                selection_field_name = self.selection_field_kwargs.pop("name")
                selection_field = self.get_selection_field(
                    self.name, selection_field_name, **self.selection_field_kwargs
                )
                cls.__bases__ = (
                    SelectionMixin(self.name, selection_field_name, selection_field),
                ) + cls.__bases__
        result = super(Enumeration, self).setup_full(model)
        self.Enumclass = self.resolve_enumclass(model)
        return result

    def convert_to_read(self, value, record, use_name_get=True):
        if value is not None and value is not False:
            return self.get_member_by_value(value).value
        else:
            return value

    def convert_to_write(self, value, record):
        if value is not None and value is not False:
            if value in self.Enumclass.__members__.values():
                member = self.get_member_by_value(value)
                # Our EnumerationAdapter takes care of doing the right
                # thing when writing to the DB, also convert_to_column
                # does.
                return member.value
        return value

    def convert_to_cache(self, value, record, validate=True):
        if value not in self.Enumclass.__members__.values():
            if value is not None and value is not False:
                return self.get_member_by_name(value).value
        return value

    # NOTE: The parameter `values` was introduced in Odoo 11; the
    # parameter validate was introduced in Odoo 12.  We don't use
    # either; but declare them both to work across the three Odoo
    # versions.
    def convert_to_column(self, value, record, values=None, validate=True):
        if value in self.Enumclass.__members__.values():
            return Char.convert_to_column(
                self, self.get_member_by_value(value).name, record
            )
        else:
            return Char.convert_to_column(self, value, record)


class Adapter(object):
    # See the note in setup_full above.

    # Odoo 11 requires all bases to have these attributes.  See
    # odoo/models.py, method _build_model_attributes in lines 515-555 (at the
    # time of writing).
    _table = None
    _sequence = None
    _inherits = _depends = {}
    _sql_constraints = []
    _constraints = []
    _description = None

    # Odoo 12 requires this attribute.  See odoo/models.py, line 528
    _inherit = None


class EnumerationAdapter(Adapter):
    "Adapt the create/write/search method to Enumeration fields."

    @api.model
    @api.returns(*models.BaseModel.search._returns)
    def search(self, args, *pos_args, **kwargs):
        for index, query_part in enumerate(args):
            if not isinstance(query_part, string_types):
                fieldname, operator, operands = query_part
                field = self._fields.get(fieldname, None)
                if isinstance(field, _EnumeratedField):
                    if operator in ("=", "!="):
                        values = _get_db_value(field, operands)
                    elif operator in ("in", "not in"):
                        values = [_get_db_value(field, o) for o in operands]
                    else:
                        raise TypeError(
                            "Unsupported operator %r for an enumeration field"
                            % operator
                        )
                    args[index] = (fieldname, operator, values)
        return super(EnumerationAdapter, self).search(args, *pos_args, **kwargs)

    @api_create_signature
    @api.returns("self", lambda value: value.id)
    def create(self, values):
        if isinstance(values, Mapping):
            values = {
                fieldname: _get_db_value(self._fields.get(fieldname, None), value)
                for fieldname, value in values.items()
            }
        else:
            values = [
                {
                    fieldname: _get_db_value(self._fields.get(fieldname, None), value)
                    for fieldname, value in vals.items()
                }
                for vals in values
            ]
        return super(EnumerationAdapter, self).create(values)

    @api.multi
    def write(self, values):
        for fieldname, value in dict(values).items():
            field = self._fields.get(fieldname, None)
            values[fieldname] = _get_db_value(field, value)
        return super(EnumerationAdapter, self).write(values)


def SelectionMixin(field_name, selection_field_name, selection_field):
    return type(
        "selection_mixin_" + field_name,
        (Adapter,),
        {selection_field_name: selection_field},
    )


def _get_db_value(field, value):
    if value is None or value is False:  # and not field.required
        return value
    if isinstance(field, Enumeration):
        member = field.get_member_by_value(value)
        return member.name
    else:
        return value


def constant(value):
    "Create a function (of many args) that always returns a constant `value`."

    def result(*args, **kwargs):
        return value

    return result
