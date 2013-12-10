# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoeuf.osv.improve
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# @created: 2013-11-27

'''Xœuf extensions for Open Object (OpenERP) models.

This module improve `OpenERP` object services (OSV) with some extensions
related to model programming or shell (Command Line Interface) use:

- Integrate methods `search_read` and ``search_browse`` to `ModelBase`.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)

from xoutil.names import strlist as strs


__all__ = strs('integrate_search')

del strs


def integrate_search():
    '''Integrate methods `search_read` and ``search_browse`` to `ModelBase`.

    '''
    from openerp.osv.orm import BaseModel
    from xoeuf.osv.orm import search_read, search_browse
    BaseModel.search_read = search_read
    BaseModel.search_browse = search_browse
