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

from collections import defaultdict
from inspect import getmembers
from xoeuf.odoo import api, models, tools
from xoeuf.osv.expression import Domain
from xoeuf.modules import get_caller_addon


def get_modelname(model):
    """Gets the ORM object's name for a model class/object.

    Main usage::

        self.pool[get_modelname(some_model_class)]

    :param model: Either an object (i.e an instance bound to some database) or
                  the any of the it's class definitions.

    .. deprecated:: 0.49.0 Calling with a `model proxy
                    <xoeuf.models.proxy>`:mod:.

    .. versionchanged:: 0.61.0 Calling with a `model proxy
       <xoeuf.models.proxy>`:mod: is an error.

    """
    from xoeuf.eight import string_types
    from xoeuf.odoo.models import BaseModel

    if not isinstance(model, BaseModel) and not issubclass(model, BaseModel):
        msg = "Invalid argument '%s' for param 'model'" % model
        raise TypeError(msg)
    result = model._name
    if not result:
        # This is the case of a model class having no _name defined, but then
        # it must have the _inherit and _name is regarded the same by OpenERP.
        result = model._inherit
    assert isinstance(result, string_types), "Got an invalid name for %r" % model
    return result


@property
def _onupdate_methods(self):
    """ Return a list of updater methods. """

    def is_onupdate(func):
        return callable(func) and hasattr(func, "_onupdates")

    cls = type(self)
    methods = []
    for _, func in getmembers(cls, is_onupdate):
        methods.append(func)

    # optimization: memoize result on cls, it will not be recomputed
    cls._onupdate_methods = methods
    return methods


models.BaseModel._onupdate_methods = _onupdate_methods


# extend :meth:`odoo.models.BaseModel._setup_base`
super_setup_base = models.BaseModel._setup_base


@api.model
def _setup_base(self, *args, **kwargs):
    cls = type(self)
    do_setup = not cls._setup_done
    res = super_setup_base(self, *args, **kwargs)
    if do_setup:
        cls._method_triggers = tools.Collector()
    return res


models.BaseModel._setup_base = _setup_base


# extend :meth:`odoo.models.BaseModel._setup_complete`
super_setup_complete = models.BaseModel._setup_complete


@api.model
def _setup_complete(self, *args, **kwargs):
    res = super_setup_complete(self, *args, **kwargs)
    cls = type(self)
    cls._onupdate_methods = models.BaseModel._onupdate_methods
    self.setup_triggers()
    return res


models.BaseModel._setup_complete = _setup_complete


# add :meth:`odoo.models.BaseModel.resolve_deps`
@api.model
def resolve_deps(self, method):
    """ Get the `method` dependencies list.

    Return the list of dependencies of ``method`` as tuples
    ``(model, field, path)``, where ``path`` is an optional list of field
    names.
    """
    result = []
    # add self's own dependencies
    for dotnames in method._onupdates:
        model, path = self, dotnames.split(".")
        for i, fname in enumerate(path):
            field = model._fields[fname]
            result.append((model, field, path[:i]))
            model = self.env.get(field.comodel_name)
    # add self's model dependencies
    for mname, fnames in self._depends.items():
        model = self.env[mname]
        for fname in fnames:
            field = model._fields[fname]
            result.append((model, field, None))
    # add indirect dependencies from the dependencies found above
    for model, field, path in list(result):
        for inv_field in model._field_inverses[field]:
            inv_model = self.env[inv_field.model_name]
            inv_path = None if path is None else path + [field.name]
            result.append((inv_model, inv_field, inv_path))
    return result


models.BaseModel.resolve_deps = resolve_deps


# add :meth:`odoo.models.BaseModel.setup_triggers`
@api.model
def setup_triggers(self):
    """ Add the necessary triggers to execute updater methods. """
    for update_method in self._onupdate_methods:
        for model, field, path in self.resolve_deps(update_method):
            path_str = None if path is None else (".".join(path) or "id")
            model._method_triggers.add(field, (update_method, self._name, path_str))


models.BaseModel.setup_triggers = setup_triggers


# add :meth:`odoo.models.BaseModel.update_onupdate`
@api.multi
def execute_onupdate(self, fnames):
    """Notify that fields have been modified on ``self``.

    This invalidates the cache, and prepares the recomputation of stored
    function fields (new-style fields only).

    .. versionchanged:: 0.48.0 Ignore unknown fields.

    """
    # group triggers by (model, path) to minimize the calls to search()
    triggers = defaultdict(set)
    # Take only the fields that are in the model. This is necessary because in
    # some rare cases this method is called with fields that may not be in the
    # model. (e.g. xopgi_object_merger).
    for fname in set(fnames) & set(self._fields):
        mfield = self._fields[fname]
        # group triggers by model and path to reduce the number of search()
        for method, model_name, path in self._method_triggers[mfield]:
            triggers[(model_name, method)].add(path)
    # process triggers, mark fields to be invalidated/recomputed
    for model_method, paths in triggers.items():
        model_name, method = model_method
        # process stored fields
        if paths:
            # determine records of model_name linked by any of paths to self
            if any(path == "id" for path in paths):
                target = self
            else:
                env = self.sudo().with_context({"active_test": False}).env
                target = env[model_name].search(
                    Domain.OR(*([(path, "in", self.ids)] for path in paths))
                )
                target = target.with_env(self.env)
            # prepare recomputation for each field on linked records
            method(target)


models.BaseModel.execute_onupdate = execute_onupdate


# extend :meth:`odoo.models.BaseModel._validate_fields`
super_validate_fields = models.BaseModel._validate_fields


@api.multi
def _validate_fields(self, field_names):
    res = super_validate_fields(self, field_names)
    self.execute_onupdate(field_names)
    return res


models.BaseModel._validate_fields = _validate_fields


def ViewModel(name, model_name, table=None, mixins=None):
    """Create a ViewModel in a simple way.

    A ViewModel is one that inherit other by prototype mode and is persisted
    in the same table as original model.  This allows to consider it a
    separate view of the same underlying data.  Beware you must implement all
    views consistently.

    :param name: name for view model to define.

    :param model_name: Name of the model to which the ModelView will be
                       created.

    :param table: attribute _table of model to which the ModelView will be
                  created or None to get the default using odoo convention.

    :param mixins: List of model names "mixins" that will inherit the
                   ModelView or None to include no mixin.

    """
    if not table:
        table = model_name.replace(".", "_")
    if not mixins:
        mixins = []

    class Res(models.Model):
        _name = name
        _inherit = [model_name] + mixins
        _table = table
        _module = get_caller_addon(2)  # class Res + function ViewModel.

    return Res
