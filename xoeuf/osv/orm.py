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
