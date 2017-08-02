#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# property_v8
# ---------------------------------------------------------------------
# Copyright (c) 2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2017-08-01


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoeuf.odoo.fields import Field as Base


class Property(Base):
    '''A property-like field.

    This is always non-store field.  In fact, you may only pass the getter,
    setter and deleter functions.

    .. warning:: This is a kind of hack.

       Normal Python `properties <property>` are not copied through Odoo
       inheritance mechanisms.  This `Property` is a Field and Odoo accounts
       for it.  But, it is NOT an actual ORM field in the sense that it's
       never interacts with the DB.  Therefore:

       - You MUST NEVER use `write()` or `create()` on these type of fields.
         You may update the value via the `setter`.

       - You cannot `search()` for this type of fields.

    The getter, setter and deleter functions receive (and thus we required it)
    a singleton recordset instance.

    Usage::

       @Property
       def result(self):
           return 1

       @result.setter
       def result(self, value):
          pass

    You may also do::

       def _set_result(self, value):
           pass

       result = Property(lambda s: 1, setter=_set_result)
       del _set_result

    '''
    # This is the best of the three major versions of Odoo we support.  This
    # create a __slot__ and avoids that these values go to the
    # __getattr__/__setattr__ mechanism in fields.Field.  But it also, means
    # that we need to do some tricks in the `__init__`:meth: to make all
    # versions happy.
    _slots = {
        'property_getter': None,
        'property_setter': None,
        'property_deleter': None,
    }
    type = 'python-property'  # needed to satisfy ir.models.field

    def __init__(self, getter, setter=None, deleter=None):
        # Notice we don't abide to the expected fields signature.  Instead, we
        # require one that is compatible with `property`; but we ensure that
        # Odoo sees this Property as normal field with custom attributes.
        from xoutil import Unset
        super(Property, self).__init__(
            # Odoo ignores arguments which are None, therefore, let's force
            # them with Unset.  Odoo 9 and 10, uses this args to call
            # field.new(**args), and also to restore the values of the _slots
            # to provided values instead of default ones.  This last thing is
            # done when building the specific field for each Model Class (see
            # our `registry.rst`); cf. Field._setup_attrs.
            #
            # WARNING: If you remove this thinking that put those values just
            # a few lines below, you're fooling yourself.
            property_getter=getter or Unset,
            property_setter=setter or Unset,
            property_deleter=deleter or Unset,

            compute=getter,
            store=False,
        )
        # In any case, we need those values now to make `new()` below work.
        self.property_getter = getter or Unset
        self.property_setter = setter or Unset
        self.property_deleter = deleter or Unset

    def new(self, **kwargs):
        # This method is called upon when setting up the models (in the
        # registry)... We ignore most of the arguments, since we may just
        # return a copy of `self`.  The arguments 'setter' and 'deleter' are
        # only used in `setter`:meth: and `deleter`:meth: to support the
        # feeling of property. Odoo won't pass them when calling `new`.
        setter = kwargs.get('setter', self.property_setter)
        deleter = kwargs.get('deleter', self.property_deleter)
        return Property(
            self.property_getter,
            setter=setter,
            deleter=deleter,
        )

    def setter(self, f):
        return self.new(setter=f)

    def deleter(self, f):
        return self.new(deleter=f)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            if not instance:
                return self.null(instance.env)
            instance.ensure_one()
            return self.property_getter(instance)

    def __set__(self, instance, value):
        if self.property_setter:
            instance.ensure_one()
            self.property_setter(instance, value)
        else:
            raise TypeError('Setting to read-only Property')

    def __delete__(self, instance):
        if self.property_deleter:
            instance.ensure_one()
            self.property_deleter(instance)
        else:
            raise TypeError('Deleting undeletable Property')