#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# transaction
# ---------------------------------------------------------------------
# Copyright (c) 2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2017-01-25

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoutil.context import Context
from xoutil.names import strlist as slist

try:
    from odoo.modules.registry import Registry as manager
    manager_lock = lambda: manager._lock  # noqa
except ImportError:
    from openerp.modules.registry import RegistryManager as manager
    manager_lock = manager.lock


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
