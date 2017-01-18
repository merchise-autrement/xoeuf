#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoeuf.osv.registry
# ---------------------------------------------------------------------
# Copyright (c) 2013-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#

'''Xœuf Models registry for OpenERP databases.

If OpenERP is properly installed and configured, then all databases can be
found as submodules of :mod:`xoeuf.pool`.

Through this registry you can obtain a database from a customized
configuration.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


from types import ModuleType
from collections import MutableMapping
from xoutil import Unset
from xoutil.names import strlist as slist
from xoutil.context import Context
from xoutil.collections import SmartDictMixin
from xoutil.decorator import aliases, memoized_property


try:
    from odoo import SUPERUSER_ID
    from odoo.modules.registry import Registry as manager
    manager_get = manager
    manager_lock = lambda: manager._lock  # noqa
except ImportError:
    from openerp import SUPERUSER_ID
    from openerp.modules.registry import RegistryManager as manager
    manager_get = manager.get
    manager_lock = manager.lock

def _valid_model_base(model):
    '''Check if a model has a right base class.'''
    try:
        from openerp.models import BaseModel
    except ImportError:
        from odoo.models import BaseModel
    if not isinstance(model, BaseModel):
        from inspect import getmro
        from xoutil.eight import typeof
        msg = 'Inappropriate type "%s" for model value!\tMRO=%s'
        t = typeof(model)
        raise TypeError(msg % (t.__name__, getmro(t)))


# TODO: Allow to change "openerp.tools.config" per context level
#       Implement for this "push" and "pop" methods in "xoeuf.tools.config"
class TransactionManager(Context):
    '''Xœuf Execution Context that manage an OpenERP connection: when enter the
    context a database cursor is obtained, when exit the context the
    transaction is managed.

    Use always as part of a database Registry::

        reg = Registry(db_name='test')
        users = reg.models.res_users
        uid = 1
        with reg(foo='bar') as cr:   # Define context variables
            ids = users.search(cr, uid, [('partner_id', 'like', 'Med%')])
            for rec in users.read(cr, uid, ids):
                name = rec['partner_id'][1]
                mail = rec['user_email']
                print('"%s" <%s>' % (name, mail))

    If `transactional` is True, then "commit" or "rollback" is called on
    exiting the level::

        with reg(transactional=True) as cr:  # commit after this is exited
            ids = users.search(cr, uid, [('partner_id', 'like', 'Med%')])
            with reg() as cr2:   # Reuse the same cursor of parent context
                assert cr is cr2
                for rec in users.read(cr, uid, ids):
                    name = rec['partner_id'][1]
                    mail = rec['user_email']
                    print('"%s" <%s>' % (name, mail))

    First level contexts are always transactional.

    '''

    __slots__ = slist('_registry', '_wrapped')

    default_context = {}    # TODO: check its value

    def __new__(cls, registry, **kwargs):
        with manager_lock():
            _super = super(TransactionManager, cls)
            self = _super.__new__(cls, registry.context_name, **kwargs)
            if self.count == 0:
                self._registry = registry
                self._wrapped = None
            else:
                assert self._registry == registry and self._wrapped
            return self

    def __init__(self, registry, **kwargs):
        super(TransactionManager, self).__init__(registry.context_name,
                                                 **kwargs)

    def __enter__(self):
        ctx = super(TransactionManager, self).__enter__()
        assert ctx is self
        if not self._wrapped:
            assert self.count == 1
            self._wrapped = self._registry.cursor
            self._wrapped._wrapper = self
        return self._wrapped

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._wrapped:
            # FIXME:  [med]{?} Documentation says reg(transactional=True), but
            #                  this checks for `managed`...
            managed = self.get('managed', True)
            if managed and self.count == 1:
                if exc_type or exc_val:
                    self._wrapped.rollback()
                else:
                    self._wrapped.commit()
                self._wrapped.close()
        return super(TransactionManager, self).__exit__(exc_type, exc_val,
                                                        exc_tb)


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
    from xoutil.collections import opendict as __search_result_type__  # noqa:
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
            except:
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
        args = [((key, m[key]) for key in m) if isinstance(m, Mapping) else m
                    for m in args]
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


class Registry(ModuleType):
    '''Xœuf Model registry for a particular database.

    The registry is essentially a mapping between model names and model
    instances. There is one registry instance per database.

    Instances are Python modules in order to be easily used in a shell.

    '''
    instances = {}

    def __new__(cls, db_name, **kwargs):
        '''Create, or return if already exists, a instance of a database
        registry.
        '''
        import threading
        with manager_lock():
            db_name = str(db_name)
            self = cls.instances.get(db_name)    # Only one per database
            if not self:
                wrapped = manager_get(db_name)
                self = super(Registry, cls).__new__(cls, db_name)
                self.db_name = db_name
                self.wrapped = wrapped
                self._default_context = kwargs
                self.uid = SUPERUSER_ID
                self._cardinality = 1
                cls.instances[db_name] = self
            else:
                self._default_context.update(kwargs)
                self._cardinality += 1
            current_thread = threading.current_thread()
            current_thread.dbname = self.db_name
            current_thread.uid = self.uid
            return self

    def __init__(self, db_name, **kwargs):
        '''A trick to finish object creation.
        '''
        if self._cardinality == 1:
            doc = str('Model registry for database "%s".\n\n'
                      'See "%s" module documentation for more info.'
                      '' % (db_name, __name__))
            super(Registry, self).__init__(str(db_name), doc)

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        return isinstance(other, Registry) and self.db_name == other.db_name

    def __repr__(self):
        return '<%s for "%s" DB>' % (type(self).__name__, self.db_name)

    def __getitem__(self, model_name):
        '''Return a model for a given name or raise KeyError if it doesn't
        exist.

        "obj[model_name]" is only a shortcut for "obj.models[model_name]".

        '''
        return self.models[model_name]

    def restart(self):
        '''Restart the database connection.

        Delete an existing registry and return a newly initialized registry
        with a database connection.

        '''
        cls = type(self)
        with manager_lock():
            try:
                self.wrapped = manager.new(self.db_name)
            except:
                del self.wrapped
                del cls.instances[self.db_name]
                # TODO: Manage the module in "sys.modules"
                raise

    def salt_shell(self, **kwargs):
        '''Assign common shell global variables.

        It only function properly if the client of this function is a shell
        running in a terminal (like `IPython`) and working with a `Pythn`
        version with support for ``sys._getframe``.

        Keyword parameters are models to be assigned, for example
        ``db.salt_shell(_='hr.contract', users_obj='res.users')``. Especial
        name ``_`` is replaced by ``self``.

        Also fix documentations and execute special tools
        ``fix_documentations`` and ``integrate_extensions``.

        '''
        from sys import _getframe
        try:
            from openerp.api import Environment
        except ImportError:
            from odoo.api import Environment
        from xoeuf.osv.improve import fix_documentations, integrate_extensions
        CURSOR_NAME = str('cr')
        ROOT_USER_NAME = str('uid')
        MODELS_NAME = str('models')
        CONTEXT_NAME = str('context')
        ENV_NAME = str('env')
        close_names = (CURSOR_NAME, )
        clear_names = (ENV_NAME, )
        names = (CURSOR_NAME, ROOT_USER_NAME, MODELS_NAME, CONTEXT_NAME)
        f = _getframe(1)
        vars = f.f_locals
        for name in clear_names:
            if name in vars:
                var = vars[name]
                try:
                    var.clear()
                except:
                    pass
        for name in close_names:
            if name in vars:
                var = vars[name]
                try:
                    var.close()
                except:
                    pass
        for name in names:
            var = getattr(self, name, Unset)
            if var is not Unset:
                vars[name] = var
        # The env cannot be simply gotten from the Registry cause it will
        # create another cursor for it. The property Registry.cursor is not
        # memoized, and it probably shouldn't since that would render the
        # registry a single-use thing.
        vars[ENV_NAME] = Environment(vars[CURSOR_NAME],
                                     vars[ROOT_USER_NAME],
                                     vars[CONTEXT_NAME])
        if kwargs:
            models = getattr(self, MODELS_NAME)
            for kwname in kwargs:
                model_name = kwargs[kwname]
                model = models.get(model_name, Unset)
                if not model:
                    model = getattr(models, model_name, Unset)
                if model:
                    var_name = 'self' if kwname == '_' else kwname
                    vars[var_name] = model
        fix_documentations(self)
        integrate_extensions()

    @staticmethod
    def get_all_db_names():
        '''Return all database names presents in the connected host.'''
        try:
            from openerp.service.db import exp_list
        except ImportError:
            from odoo.service.db import exp_list
        return exp_list()

    @aliases('db')
    @property
    def connection(self):
        res = getattr(self.wrapped, 'db', None)
        if not res:
            res = getattr(self.wrapped, '_db')
        return res

    def __call__(self, **kwargs):
        '''Create a execution context.

        To use it as a managed cursor::

        reg = Registry('my_db')
        users = reg.models.res_users
        with reg(foo='bar') as cr:   # Define context variables
            ids = users.search(cr, 1, [('partner_id', 'like', 'Med%')])
            for rec in users.read(cr, uid, ids):
                name = rec['partner_id'][1]
                mail = rec['user_email']
                print('"%s" <%s>' % (name, mail))

        '''
        return TransactionManager(self, **kwargs)

    @property
    def cursor(self):
        '''Return a not managed cursor, callers are responsible of
        transactions and of closing it.

        '''
        return self.connection.cursor()

    cr = cursor    # An alias

    @memoized_property
    def models(self):
        return ModelsManager(self)

    @property
    def env(self):
        try:
            from openerp.api import Environment
        except ImportError:
            from odoo.api import Environment
        return Environment(self.cr, self.uid, self.context)

    @property
    def context_name(self):
        return str('%s-%s' % (__name__.partition('.')[0], self.db_name))

    @property
    def current_manager(self):
        '''Obtain the current cursor execution context if one exits, else
        return None.
        '''
        ctx = TransactionManager[self.context_name]
        return ctx or None

    @property
    def context(self):
        '''Build a context to be used as argument in Open Object methods using
        database registry defaults and current cursor context arguments; also
        checks the resulting context for common values (lang, tz).

        '''
        from xoutil.collections import opendict
        res = opendict(**self._default_context)
        mngr = self.current_manager
        if mngr:
            res.update(**mngr)
        return self._check_context(res)

    def _check_context(self, ctx):
        try:
            from odoo import api
        except ImportError:
            from openerp import api
        # TODO: catch these values
        if 'lang' not in ctx:
            import os
            DEFAULT = 'en_US'
            lang = os.environ.get('LANG', DEFAULT).split('.')[0]
            # Environment language could not be installed.
            # So, check and obtain 'lang' from DB
            with self() as cr:
                Lang = api.Environment(cr, self.uid, {})['res.lang']
                ok = Lang.search([('code', '=', lang)])
                if not ok:
                    predicate = [('code', 'like', '%s%%' % lang[:2])]
                    langs = Lang.search(predicate, limit=1)
                    if langs:
                        lang = langs.code
                    else:
                        lang = DEFAULT
                ctx['lang'] = lang
        if 'tz' not in ctx:
            from xoutil.fs import read_file as read
            ctx['tz'] = read('/etc/timezone').strip() or 'America/Havana'
        return ctx

    def __dir__(self):
        return list({name for name in self.__dict__.keys() + dir(type(self))
                     if not name.startswith('_')})


# Discarding not neeeded globals
del Context
del MutableMapping
del ModuleType
del aliases
