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

import logging

from xoutil.functools import lru_cache
from xoutil.modules import customize
from xoutil.modules import moduleproperty, modulemethod

_logger = logging.getLogger(__name__)

XOEUF_EXTERNAL_ADDON_GROUP = 'xoeuf.addons'


@modulemethod
@lru_cache(1)
def find_external_addons(self):
    '''Finds all externally installed addons.

    Externally installed addons are modules that are distributed with
    setuptools' distributions.

    An externally addon is defined in a package that defines an `entry
    point`__ in the group "xoeuf.addons" which points to a standard package
    (i.e loadable without any specific loader).

    :returns:  A dictionary from addons to it's a tuple of `(container's path,
               entry_point)`.

    Example::

       [xoeuf.addons]
       xopgi_account = xopgi.addons.xopgi_account

    '''
    import os
    from pkg_resources import iter_entry_points
    from xoutil.iterators import delete_duplicates
    res = []
    for entry in iter_entry_points(XOEUF_EXTERNAL_ADDON_GROUP):
        if not entry.attrs:  # The EP is a whole module
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
                name = entry.module_name
                pos = name.rfind('.')
                if pos >= 0:
                    name = name[pos+1:]
        else:
            _logger.error('Invalid external addon %r', entry)
    return delete_duplicates(res)


@modulemethod
def initialize_sys_path(self):
    from xoutil.objects import setdefaultattr
    from openerp.modules import module
    assert self.__oe_initiliaze_sys_path
    external_addons = setdefaultattr(self, '__addons', [])
    if not external_addons:
        self.__oe_initiliaze_sys_path()
        result = module.ad_paths
        external_addons.extend(self.find_external_addons())
        result.extend(external_addons)
        module.ad_paths = result
        return result
    else:
        return module.ad_paths


@modulemethod
def patch_modules(self):
    '''Patches OpenERP `modules.module` to work with external addons.

    '''
    bootstraped = getattr(self, 'bootstraped', False)
    if not bootstraped:
        _logger.info('Using xoeuf\'s module loader')
        from openerp.modules import module
        self.__oe_initiliaze_sys_path = module.initialize_sys_path
        module = customize(module)[0]
        module.initialize_sys_path = self.initialize_sys_path
        self.bootstraped = True
