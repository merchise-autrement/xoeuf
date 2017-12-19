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


from collections import MutableMapping
from xoutil.symbols import Unset
from xoutil.collections import SmartDictMixin


# TODO: Use `OpenDictMixin`
class ModelsManager(MutableMapping, SmartDictMixin):
    '''Xœuf models manager for a particular `registry` database.

    The mapping is essentially a mapping between model names and model
    instances.

    There is only one manager instance per database.

    Instances are:

     * A dictionary like object containing all database modules.

     * An open dictionary allowing access to keys as attributes.

    '''
    from xoutil.future.collections \
        import opendict as __search_result_type__  # noqa
    # see the the SmartDictMixin.search method

    def __new__(cls, registry):
        '''Create, or return if already exists, a instance of a models manager.
        '''
        self = super(ModelsManager, cls).__new__(cls)
        self._registry = registry
        self._mapping = None    # for "__invert__" operator cache
        return self

    def __str__(self):
        args = (type(self).__name__, self._registry.db_name, len(self))
        return str('<Database %s for "%s" with %s models>' % args)

    def __repr__(self):
        name = type(self).__name__
        db = self._registry.db_name
        return str('<Database %s for "%s">' % (name, db))

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        return (isinstance(other, ModelsManager) and
                self._registry == other._registry)

    @property
    def wrapped(self):
        return self._registry.wrapped.models

    def __dir__(self):
        attrs = set(getattr(self, '__dict__', {}))
        all_slots = (getattr(cls, '__slots__', ()) for cls in type(self).mro())
        slot_attrs = {name for slots in all_slots for name in slots}
        return list(set(~self) | attrs | slot_attrs)

    def __invert__(self):
        '''Return a inverted mapping between model names (keys are identifiers
        for attributes, values are normal dotted model names).

        To obtain this mapping you can use as the unary operator "~".

        '''
        if not self._mapping or len(self) != len(self._mapping):
            self._mapping = {str(key.replace('.', '_')): key for key in self}
        return self._mapping

    def __getattr__(self, name):
        model_name = self._is_model_name(name)
        if model_name:
            return self[model_name]
        else:
            try:
                return super(ModelsManager, self).__getattr__(name)
            except Exception:  # FIXME: Should we deal with this?
                msg = "'%s' object has no attribute '%s'"
                raise AttributeError(msg % (type(self).__name__, name))

    def __setattr__(self, name, value):
        model_name = self._is_model_name(name)
        if model_name:
            self[model_name] = value
        else:
            super(ModelsManager, self).__setattr__(name, value)

    def __delattr__(self, name):
        model_name = self._is_model_name(name)
        if model_name:
            del self[name]
        else:
            super(ModelsManager, self).__delattr__(name)

    def __len__(self):
        return len(self.wrapped)

    def __iter__(self):
        return iter(self.wrapped)

    def __contains__(self, model_name):
        return model_name in self.wrapped

    def __getitem__(self, model_name):
        res = self.get(model_name, Unset)
        if res is not Unset:
            return res
        else:
            raise KeyError(model_name)

    def __setitem__(self, model_name, model):
        from xoutil.validators.identifiers import is_valid_full_identifier
        if is_valid_full_identifier(model_name):
            _valid_model_base(model)
            self.wrapped[model_name] = model
        else:
            msg = 'Inappropriate model name "%s"!'
            raise ValueError(msg % model_name)

    def __delitem__(self, model_name):
        del self.wrapped[model_name]

    def get(self, model_name, *args):
        '''Return a model for a given name or None if it doesn't exist.

        :params args: allows 0 or one value for default definition.'''
        return self._get_pop(self.wrapped.get, model_name, *args)

    def pop(self, model_name, *args):
        '''Remove specified model and return the corresponding value.

        :params args: allows 0 or one value for default definition.

        If model is not found, default value is returned if given,
        otherwise KeyError is raised.

        '''
        return self._get_pop(self.wrapped.pop, model_name, *args)

    def popitem(self):
        '''Remove and return some (model_name, model) pair as a 2-tuple;
        but raise KeyError if empty.

        '''
        return self.wrapped.popitem()

    def clear(self):
        '''Remove all models.'''
        self.wrapped.clear()

    def update(self, *args, **kwargs):
        '''A really smart update implementation.

          * Convert model name from identifiers to normal names.

          * Check that all values are valid OpenERP models.

        '''
        from collections import Mapping
        from itertools import chain
        from xoutil.validators.identifiers import is_valid_identifier
        args = [
            ((key, m[key]) for key in m)
            if isinstance(m, Mapping) else m
            for m in args
        ]
        args.append(((key, kwargs[key]) for key in kwargs))
        mapping = ~self
        for name, model in chain(args):
            if is_valid_identifier(name):
                name = mapping[name]
            self[name] = model

    def setdefault(self, model_name, default=None):
        '''return registry.get(model_name, default),
        also set registry[model_name]=default if model_name not in registry
        and default is not None

        '''
        from xoutil.validators.identifiers import is_valid_identifier
        if is_valid_identifier(model_name):
            mapping = ~self
            model_name = mapping[model_name]
        res = self.get(model_name, Unset)
        if res is Unset:
            res = default
            if default is not None:
                self[model_name] = default
        return res

    def _is_model_name(self, name):
        '''Avoid unnecessary mapping calling.

        Return a correct model name or None.

        '''
        if name not in {'db_name', 'uid'} and not name.startswith('_'):
            mapping = ~self
            return mapping.get(name)
        else:
            return None

    @staticmethod
    def _is_model_value(value):
        if value in (None, False, Unset):
            return value
        else:
            _valid_model_base(value)
            return value

    @staticmethod
    def _get_pop(method, model_name, *args):
        '''Local method used in `get` and `pop`.

        :params args: allows 0 or one value for default definition.

        '''
        count = len(args)
        if count == 0:
            res = method(model_name)
        elif count == 1:
            res = method(model_name, args[0])
        else:
            msg = '%s method expected at most 2 arguments, got "%s"!'
            raise TypeError(msg % (method.__name__, count + 1))
        return ModelsManager._is_model_value(res)


def _valid_model_base(model):
    '''Check if a model has a right base class.'''
    from xoeuf.odoo.models import BaseModel
    model_types = (BaseModel, )
    try:
        from xoeuf.odoo.models import MetaModel
        model_types += (MetaModel, )
    except ImportError:
        pass
    if not isinstance(model, model_types):
        from inspect import getmro
        from xoutil.eight import typeof
        msg = 'Inappropriate type "%s" for model value!\tMRO=%s'
        t = typeof(model)
        raise TypeError(msg % (t.__name__, getmro(t)))
