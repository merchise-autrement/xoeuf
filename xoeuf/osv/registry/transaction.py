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

from xoutil.context import Context
from xoutil.names import strlist as slist

# TODO: Homogenize 'manager_lock' in a compatibility module
try:
    from odoo.modules.registry import Registry as manager
    manager_lock = lambda: manager._lock  # noqa
except ImportError:
    from openerp.modules.registry import RegistryManager as manager
    manager_lock = manager.lock


# TODO: Allow to change "openerp.tools.config" per context level
#       Implement for this "push" and "pop" methods in "xoeuf.tools.config"
class TransactionManager(Context):
    '''Manages an Odoo environment.

    There's some overlap between `odoo.api.Environment`:class: and this class.

    Usage::

       >>> with TransactionManager(registry) as tm:
       ...    tm['res.users'].search([])

    Notes:

    - You may pass the keyword 'managed' to False to avoid entering a
      transaction.

      First level contexts are always managed (regardless of the value of
      `managed`).

    - The transaction manager yields itself (``tm`` in the example above).
      The underlying Odoo environment is automatically proxied.

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

    def __getitem__(self, key):
        return self._wrapped[key]

    def __getattr__(self, attr):
        return getattr(self._wrapped, attr)

    def __enter__(self):
        ctx = super(TransactionManager, self).__enter__()
        assert ctx is self
        if not self._wrapped:
            assert self.count == 1
            self._wrapped = self._registry.env
            self._wrapped._wrapper = self
            self._wrapped.cr.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._wrapped:
            managed = self.get('managed', True)
            if managed and self.count == 1:
                self._wrapped.cr.__exit__(exc_type, exc_val, exc_tb)
                self._wrapped = None
        return super(TransactionManager, self).__exit__(exc_type, exc_val,
                                                        exc_tb)
