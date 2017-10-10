#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# __init__
# ---------------------------------------------------------------------
# Copyright (c) 2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoeuf import signals

__all__ = ['Enumeration']


def Enumeration(enumclass, *args, **kwargs):
    '''Create an enumeration field.

    The `enumclass` argument must be either an `enumeration class` or a
    fully qualified name of an enumeration class.

    At the DB level the enumeration will be an integer.  This requires that
    the members of provided enumeration class are instances of `int` (probably
    via a subclass).

    Enumeration classes are required to:

    - have an attribute ``__members__`` with a `collections.Mapping`:class:
      from names to values.

    - have an attribute for each name in ``__member__`` with the same value as
      in the mapping.

    Those rules imply::

       >>> all(getattr(Enumclass, name) is value and isinstance(value, int)
       ...     for name, value in Enumclass.__members__.items())

    .. note:: These requirements are compatible with Python 3.4's
       `enum.IntEnum`:class:

       Notice, however, that we don't require that members are instances of
       the enumeration class.  But it won't hurt.

    .. warning:: The returned field is a subclass of
                 `xoeuf.fields.Integer`:class: and it's a new API field.

    '''
    from xoeuf import fields, MAJOR_ODOO_VERSION
    from xoutil.objects import classproperty

    class EnumeratedField(fields.Integer, EnumerationField):
        @classproperty
        def klass(cls):
            return import_object(enumclass)

        @classproperty
        def members_by_value(cls):
            klass = cls.klass
            return {v: k for k, v in klass.__members__.items()}

        @classmethod
        def get_member(cls, value):
            # `value` is most likely an integer, but since we require
            # members to be subclasses of `int` they should compare equal.
            try:
                return next(v for v in cls.members_by_value if v == value)
            except StopIteration:
                raise ValueError('Invalid member of enumeration: %r' % value)

        def convert_to_cache(self, value, record, validate=True):
            value = super(EnumeratedField, self).convert_to_cache(
                value, record, validate=validate
            )
            return self.get_member(value)

        if MAJOR_ODOO_VERSION < 10:
            def convert_to_read(self, value, use_name_get=True):
                # None should be False in read.
                return self.get_member(value) if value is not None else False
        else:
            def convert_to_read(self, value, record, use_name_get=True):
                # None should be False in read.
                return self.get_member(value) if value is not None else False

    return EnumeratedField(*args, **kwargs)


class EnumerationField(object):
    '''A base clase for enumerated fields.

    '''
    pass


try:
    from xoutil.objects import import_object   # TODO: migrate
except ImportError:
    def import_object(name, package=None,
                      sep='.', default=None, **kwargs):
        """Get symbol by qualified name.

        The name should be the full dot-separated path to the class::

            modulename.ClassName

        Example::

            celery.concurrency.processes.TaskPool
                                        ^- class name

        or using ':' to separate module and symbol::

            celery.concurrency.processes:TaskPool

        Examples:

            >>> import_object('celery.concurrency.processes.TaskPool')
            <class 'celery.concurrency.processes.TaskPool'>

            # Does not try to look up non-string names.
            >>> from celery.concurrency.processes import TaskPool
            >>> import_object(TaskPool) is TaskPool
            True

        """
        import importlib
        from xoutil.eight import string_types
        imp = importlib.import_module
        if not isinstance(name, string_types):
            return name                                 # already a class
        sep = ':' if ':' in name else sep
        module_name, _, cls_name = name.rpartition(sep)
        if not module_name:
            cls_name, module_name = None, package if package else cls_name
        try:
            module = imp(module_name, package=package, **kwargs)
            return getattr(module, cls_name) if cls_name else module
        except (ImportError, AttributeError):
            if default is None:
                raise
        return default


@signals.receiver([signals.pre_create, signals.pre_write], framework=True)
def _check_enumeration_value(sender, signal, values=None, **kwargs):
    for fieldname, value in values.items():
        field = sender._fields[fieldname]
        if isinstance(field, EnumerationField):
            # The following raises a ValueError if the value is not a member
            # of the enumeration class
            field.get_member(value)