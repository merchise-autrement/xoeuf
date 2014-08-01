# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoeuf.osv.orm
#----------------------------------------------------------------------
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# @created: 2013-11-27

'''Xœuf basic ORM extensions for Open Object (OpenERP) models.'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)


def store_identity(self, cr, uid, ids, context=None):
    '''To be used in ``store`` parameter for functional fields when monitor
    is needed for fields in a local model.

    For example::

        'active':
            fields.function(_get_active, type='boolean', string='Active?',
                store={_name: (store_identity, ['contract_ids'], 10), }),

    '''
    return ids


def get_modelname(model):
    '''Gets the ORM object's name for a model class/object.

    Main usage::

        self.pool[get_modelname(some_model_class)]

    :param model: Either an object (i.e an instance bound to some database) or
                  the any of the it's class definitions.

    Examples::

        >>> from xoeuf.pool import database  # doctest: +SKIP

        # Lets assume that you have installed the accounting module in this
        # database.

        >>> get_modelname(database.models.account_account)  # doctest: +SKIP
        'account.account'

        # But in your add-on you'd probably want to access some other module

        >>> from openerp.addons.account.account import account_fiscalyear
        >>> get_modelname(account_fiscalyear)  # doctest: +SKIP
        'account.fiscalyear'

    '''
    from xoutil.six import string_types
    from openerp.osv.orm import BaseModel
    if not isinstance(model, BaseModel) and not issubclass(model, BaseModel):
        msg = "Invalid argument '%s' for param 'model'" % model
        raise TypeError(msg)
    result = model._name
    if not result:
        # This is the case of a model class having no _name defined, but then
        # it must have the _inherit and _name is regarded the same by OpenERP.
        result = model._inherit
    assert isinstance(result, string_types), ('Got an invalid name for %r' %
                                              model)
    return result


# XXX [manu]  Discovered similar things in openerp/addons/base/ir/ir_fields.

#: Returns a single "command" to create a new related record
CREATE_RELATED = lambda **values: (0, 0, values)
ONE2MANY_CREATE = MANY2MANY_CREATE = CREATE_RELATED

#: Returns a single "command" to update a linked record
UPDATE_RELATED = lambda id, **values: (1, id, values)
ONE2MANY_UPDATE = MANY2MANY_UPDATE = UPDATE_RELATED

#: Returns a single "command" to remove (and unlink) the related record
REMOVE_RELATED = lambda id: (2, id)
ONE2MANY_REMOVE = MANY2MANY_REMOVE = REMOVE_RELATED

#: Returns a single command to forget about a relation
FORGET_RELATED = lambda id: (3, id)

#: Returns a single command to link a record
LINK_RELATED = lambda id: (4, id)

#: Returns a single command to unlink all
UNLINKALL_RELATED = (5, )

#: Returns a single command to replace all related with existing ids
REPLACEWITH_RELATED = lambda *ids: (6, 0, list(ids))
