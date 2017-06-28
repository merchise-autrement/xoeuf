# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoeuf.osv.orm
# ---------------------------------------------------------------------
# Copyright (c) 2013-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#

'''Xœuf basic ORM extensions for Open Object (OpenERP) models.'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import)


def guess_id(which, attr='id'):
    '''Guess the id of an object.

    If `which` is an integer, it is returned unchanged.  If it is a dict
    or a browse_record the attribute/key given by `attr` is look up and
    return.  If not found an AttibuteError is raised.  Any other type is a
    TypeError.

    '''
    from xoeuf.odoo.osv.orm import browse_record
    try:
        from xoutil.future.collections import Mapping
    except ImportError:
        from xoutil.collections import Mapping
    from xoutil.eight import integer_types
    if isinstance(which, integer_types):
        return which
    elif isinstance(which, (Mapping, browse_record)):
        from xoutil.objects import smart_getter
        get = smart_getter(which, strict=True)
        return get(attr)
    else:
        raise TypeError('Object %r of invalid type' % which)


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


    '''
    from xoutil.eight import string_types
    from xoeuf.odoo.models import BaseModel
    from xoeuf.models._proxy import ModelProxy
    if isinstance(model, ModelProxy):
        # Minor hack to support models imported using 'xoeuf.models' stuff
        return model._ModelProxy__model
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


# Making this a subclass of int allows to be reliably tested for equality in
# both Python 2.7 and Python 3.4
class _Command(int):
    def __new__(cls, value, *args):
        return super(_Command, cls).__new__(cls, value)

    def __init__(self, value, _lambda):
        self.value = value
        self._lambda = _lambda

    def __call__(self, *args, **kwargs):
        if callable(self._lambda):
            return self._lambda(*args, **kwargs)
        else:
            return self._lambda


# The index where the command magic number is in tuples
COMMAND_INDEX = 0

# For applicable commands this is the index where id/ids are located.
ID_INDEX = 1

# For applicable commands this is the index where values are located
VALUE_INDEX = VALUES_INDEX = -1


#: Returns a single "command" to create a new related record
CREATE_RELATED = _Command(0, lambda **values: (0, 0, values))
ONE2MANY_CREATE = MANY2MANY_CREATE = CREATE_RELATED

#: Returns a single "command" to update a linked record
UPDATE_RELATED = _Command(1, lambda id, **values: (1, id, values))
ONE2MANY_UPDATE = MANY2MANY_UPDATE = UPDATE_RELATED

#: Returns a single "command" to remove (and unlink) the related record
REMOVE_RELATED = _Command(2, lambda id: (2, id))
ONE2MANY_REMOVE = MANY2MANY_REMOVE = REMOVE_RELATED

#: Returns a single command to forget about a relation
FORGET_RELATED = _Command(3, lambda id: (3, id))

#: Returns a single command to link a record
LINK_RELATED = _Command(4, lambda id: (4, id))

#: Returns a single command to unlink all
UNLINKALL_RELATED = _Command(5, lambda: (5, ))

#: Returns a single command to replace all related with existing ids
REPLACEWITH_RELATED = _Command(6, lambda *ids: (6, 0, list(ids)))
