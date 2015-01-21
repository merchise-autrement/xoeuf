# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoeuf.osv.browser_extensions
# ---------------------------------------------------------------------
# Copyright (c) 2014, 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# @created: 2014-01-12

'''Xœuf ORM extensions for Open Object (OpenERP) borwser.

All the attributes of this module must be functions that can be integrated as
`browse_record` methods or operators.

Operators name has the format ``operator__<name>`` and are converted to
``__<name>__``.

Use :func:`xoeuf.osv.improve.integrate_extensions` for integrate these
extensions.

'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)


INTEGRATED = False    # True after integrated to `browse_record`


def operator__dir(self):
    '''Establishes the ``__dir__`` protocol for browse records.

      :return: list of names for all valid fields.

    '''
    cr, uid, context = self._cr, self._uid, self._context
    flds = list(self._model.fields_get_keys(cr, uid, context))
    return flds + list(self.__dict__)
