# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoeuf.modules
#----------------------------------------------------------------------
# Copyright (c) 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2014-04-28

'''External OpenERP's addons

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)


from xoutil.functools import lru_cache

XOEUF_EXTERNAL_ADDON_GROUP = 'xoeuf.addons'


@lru_cache(1)
def find_external_addons():
    '''Finds all externally installed addons.

    Externally installed addons are modules that are distributed with
    setuptools' distributions.

    An externally addon is defined in a package that defines an `entry
    point`__ in the group "xoeuf.addons" which points to a standard package
    (i.e loadable without any specific loader).

    Example::

       [xoeuf.addons]
       xopgi_account = xopgi.addons.xopgi_account

    '''
    import os
    from xoutil.iterators import delete_duplicates
    from pkg_resources import iter_entry_points
    res = []
    for entry in iter_entry_points(XOEUF_EXTERNAL_ADDON_GROUP):
        # We can't load the module here, cause the whole point is to grab
        # the paths before openerp is configured, but if you load an
        # OpenERP you will be importing openerp somehow and enacting
        # configuration
        loc = entry.dist.location
        relpath = entry.module_name.replace('.', os.path.sep)
        # The parent directory is the one!
        abspath = os.path.abspath(os.path.join(loc, relpath, '..'))
        if os.path.isdir(abspath):
            res.append(abspath)
    return delete_duplicates(res)
