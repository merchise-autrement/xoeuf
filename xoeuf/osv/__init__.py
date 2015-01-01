# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoeuf.osv
# ---------------------------------------------------------------------
# Copyright (c) 2013-2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# @author: Medardo Rodriguez
#
# @created: 20/04/2013

'''Xœuf services for access Open Object (OpenERP) models.

Implement the network protocols that the Xœuf applications that access OpenERP
databases uses to communicate with its clients.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


def savepoint(cr, name=None):
    '''A context manager that enters a new savepoint.

    If `name` is not provided a random one is generated.

    .. note:: In Odoo v8, the cursor `cr` has already a ``savepoint`` method.
              This function will fallback to it in this case.  However, the
              argument `name` will be ignored in this case.

    '''
    from xoutil import Unset
    _savepoint = getattr(cr, 'savepoint', Unset)
    if _savepoint is Unset:
        from contextlib import contextmanager
        if not name:
            from xoutil.uuid import uuid
            name = uuid(True)

        @contextmanager
        def _savepoint():
            cr.execute('SAVEPOINT "%s"' % name)
            try:
                yield
            except:
                cr.execute('ROLLBACK TO SAVEPOINT "%s"' % name)
                raise
            else:
                cr.execute('RELEASE SAVEPOINT "%s"' % name)
    return _savepoint()
