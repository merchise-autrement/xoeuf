#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Xœuf Models registry for OpenERP databases.

Through this registry you can obtain a database from a customized
configuration.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


from types import ModuleType
from collections import MutableMapping
from xoutil.symbols import Unset
from xoutil.context import Context
from xoutil.decorator import aliases, memoized_property

from .transaction import TransactionManager

from xoeuf.odoo import SUPERUSER_ID
# TODO: Homogenize 'manager_get' and 'manager_lock' in a compatibility module
try:
    from odoo.modules.registry import Registry as manager
    manager_get = manager
    manager_lock = lambda: manager._lock  # noqa
except ImportError:
    from openerp.modules.registry import RegistryManager as manager
    manager_get = manager.get
    manager_lock = manager.lock


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
            except Exception:
                del self.wrapped
                del cls.instances[self.db_name]
                # TODO: Manage the module in "sys.modules"
                raise

    def salt_shell(self, **kwargs):
        '''Assign common shell global variables.

        Also fix documentations and execute special tools
        ``fix_documentations`` and ``integrate_extensions``.

        '''
        from sys import _getframe
        from xoeuf.osv.improve import fix_documentations, integrate_extensions
        ENV_NAME = str('env')
        clear_names = (ENV_NAME, )
        names = ()
        f = _getframe(1)
        vars = f.f_locals
        for name in clear_names:
            if name in vars:
                var = vars[name]
                try:
                    var.clear()
                except Exception:
                    pass
        for name in names:
            var = getattr(self, name, Unset)
            if var is not Unset:
                vars[name] = var
        vars[ENV_NAME] = env = self.env
        if not kwargs:
            kwargs['_'] = 'res.users'
        if kwargs:
            models = self.models
            for kwname in kwargs:
                model_name = kwargs[kwname]
                model = models.get(model_name, Unset)
                if not model:
                    model = getattr(models, model_name, Unset)
                if model:
                    var_name = 'self' if kwname == '_' else kwname
                    # Instead of getting the model from 'models' do it from
                    # the environment.
                    vars[var_name] = env[model_name]
        fix_documentations(self)
        integrate_extensions()

    @staticmethod
    def get_all_db_names():
        '''Return all database names presents in the connected host.'''
        from xoeuf.odoo.service.db import exp_list
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

        '''
        return TransactionManager(self, **kwargs)

    @property
    def cursor(self):
        '''Return a not managed cursor, callers are responsible of
        transactions and of closing it.

        '''
        return self.wrapped.cursor()

    cr = cursor    # An alias

    @memoized_property
    def models(self):
        from .models import ModelsManager
        return ModelsManager(self)

    @property
    def env(self):
        from xoeuf.odoo.api import Environment
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
        from xoutil.future.collections import opendict
        res = opendict(**self._default_context)
        mngr = self.current_manager
        if mngr:
            res.update(**mngr)
        return self._check_context(res)

    def _check_context(self, ctx):
        from xoeuf.odoo import api
        # TODO: catch these values
        if 'lang' not in ctx:
            import os
            DEFAULT = 'en_US'
            lang = os.environ.get('LANG', DEFAULT).split('.')[0]
            # Environment language could not be installed.
            # So, check and obtain 'lang' from DB
            with self.cr as cr:
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
