#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Xœuf ORM extensions for Open Object (OpenERP) models.

All the attributes of this module must be functions that can be integrated as
`BaseModel` methods or operators.

Operators name has the format ``operator__<name>`` and are converted to
``__<name>__``.

'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import)

from xoeuf.osv.writers import ORMWriter as get_writer  # noqa
orm_writer = get_writer


from xoeuf.osv.writers import ORMCreator as get_creator  # noqa
orm_creator = get_creator


def get_treeview_action(self, **options):
    '''Return the tree view action for `self`.

    There are two possible signatures:

    - ``get_treeview_action(recordset, **options)``

    If the recordset is a singleton, return the view type 'form' so that it's
    easier to see the full object.

    :rtype: An action `dict` you can return to the web client.

    `options` is used to override **almost any** key in the returned dict.  An
    interesting option is `target`.

    '''
    _, _, context = self.env.args
    ids = self.ids
    if not ids or len(ids) > 1:
        vtype = 'list'
        active_id = None
    else:
        vtype = 'form'
        active_id = ids[0]
    result = {
        'type': 'ir.actions.act_window',
        'res_model': self._name,
        'src_model': False,
        'view_id': False,
        'view_type': vtype,
        'view_mode': 'list,form',
        'views': [(False, 'list'), (False, 'form')],
        'target': 'current',
        'context': context,
    }
    if ids:
        result['domain'] = [('id', 'in', tuple(ids))]
    if active_id:
        result['active_id'] = active_id
    result.update(options)
    return result
