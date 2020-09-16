#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
"""External Odoo's addons

"""
import sys
import logging
import re

from xotl.tools.future.functools import lru_cache
from xotl.tools.modules import customize
from xotl.tools.modules import modulemethod
from xotl.tools.string import cut_prefix

_ADDONS_NAMESPACE = re.compile(r"^(?:odoo|openerp)\.addons\.(?P<module>[^\.]+)\.")
XOEUF_EXTERNAL_ADDON_GROUP = "xoeuf.addons"


class _PatchesRegistry(object):
    _registry = {}
    _wrapped = {}

    def __call__(self, func):
        from xotl.tools.names import nameof

        name = nameof(func, inner=True, full=False)
        self._registry[name] = func
        return func

    def get_super(self, name):
        return self._wrapped[name]

    def apply(self):
        from odoo.modules import module

        patched = getattr(module, "__xoeuf_patched__", False)
        if patched:
            # This is an Odoo that's being patched by us.
            return
        bootstraped = getattr(self, "bootstraped", False)
        if not bootstraped:
            for name, _func in self._registry.items():
                self._wrapped[name] = getattr(module, name)
            module = customize(module)[0]
            for name, func in self._registry.items():
                setattr(module, name, func)
            self.bootstraped = True


patch = _PatchesRegistry()


@modulemethod
@lru_cache(1)
def find_external_addons(self):
    """Finds all externally installed addons.

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

    """
    import os
    from pkg_resources import iter_entry_points
    from xotl.tools.future.itertools import delete_duplicates

    res = []
    for entry in iter_entry_points(XOEUF_EXTERNAL_ADDON_GROUP):
        if not entry.attrs:
            # The entry-point is a whole module.  We can't load the module
            # here, cause the whole point is to grab the paths before openerp
            # is configured, but if you load an OpenERP addon you will be
            # importing openerp somehow and enacting configuration
            loc = entry.dist.location
            relpath = entry.module_name.replace(".", os.path.sep)
            # The parent directory is the one!
            abspath = os.path.abspath(os.path.join(loc, relpath, ".."))
            if os.path.isdir(abspath):
                res.append(abspath)
                name = entry.module_name
                pos = name.rfind(".")
                if pos >= 0:
                    name = name[pos + 1 :]  # noqa
    return delete_duplicates(res)


@patch
@modulemethod
def initialize_sys_path(self):
    from xotl.tools.objects import setdefaultattr
    from odoo.modules import module

    _super = patch.get_super("initialize_sys_path")
    external_addons = setdefaultattr(self, "__addons", [])
    if not external_addons:
        _super()
        result = module.ad_paths
        external_addons.extend(self.find_external_addons())
        result.extend(external_addons)
        module.ad_paths = result
        return result
    else:
        return module.ad_paths


def patch_modules():
    """Patches OpenERP `modules.module` to work with external addons."""
    patch.apply()


def _get_registry(db_name):
    """Helper method to get the registry for a `db_name`."""
    from odoo.modules.registry import Registry

    if isinstance(db_name, str):
        db = Registry(db_name)
    elif isinstance(db_name, Registry):
        db = db_name
    else:
        import sys

        caller = sys.getframe(1).f_code.co_name
        raise TypeError('"%s" requires a string or a Registry' % caller)
    return db


def get_dangling_modules(db):
    """Get registered modules that are no longer available.

    Returns the recordset of dangling modules.  This is a recordset of the
    model `ir.module.module`.

    A dangling module is one that is listed in the DB, but is not reachable in
    any of the addons paths (not even externally installed).

    :param db: Either the name of the database to load or a `registry
               <xoeuf.odoo.modules.registry.Registry>`:class:.

    :return: A record-set with dangling modules.

    .. warning:: We create a new cursor to the DB and the returned recordset
                 uses it.

    """
    from xoeuf import api
    from odoo import SUPERUSER_ID
    from odoo.modules.module import get_modules

    registry = _get_registry(db)
    cr = registry.cursor()
    env = api.Environment(cr, SUPERUSER_ID, {})
    Module = env["ir.module.module"]
    available = get_modules()
    return Module.search([("name", "not in", available)])


def mark_dangling_modules(db):
    """Mark `dangling <get_dangling_modules>`:func: as uninstallable.

    Parameters and return value are the same as in function
    :func:`get_dangling_modules`.

    """
    dangling = get_dangling_modules(db)
    dangling.write(dict(state="uninstallable"))
    dangling.env.cr.commit()
    return dangling


def get_object_module(obj, typed=False):
    """Return the name of the OpenERP addon the `obj` has been defined.

    If the `obj` is not defined (imported) from the "openerp.addons."
    namespace, return None.

    """
    from xotl.tools.names import nameof

    name = nameof(obj, inner=True, full=True, typed=typed)
    match = _ADDONS_NAMESPACE.match(name)
    if match:
        module = match.groupdict()["module"]
        return module
    else:
        return None


def is_object_installed(self, object):
    """Detects if `object` is installed in the DB.

    `self` must be an Odoo model (recordset, but it may be empty).

    """
    module = get_object_module(object)
    if module:
        mm = self.env["ir.module.module"].sudo()
        query = [("state", "=", "installed"), ("name", "=", module)]
        return bool(mm.search(query))
    else:
        return False


def get_caller_addon(depth=0, max_depth=5):
    """Guess the caller addon.

    :param depth: Skip that many levels in the call stack.

    :param max_depth: Max level to look in the call stack.

    Technically, we look in the globals of the *calling* stack frame for the
    ``__name__`` and, its matches the format with 'oddo.addons.<addon>.*',
    return the addon name; otherwise, look up in the frame stack until
    `max_depth` is reached.  No addon name is found, return None.

    .. versionchanged:: 0.51.0 Added `max_depth` argument.

    """
    res = None
    frame = sys._getframe(1 + depth)
    while depth < max_depth and frame is not None and not res:
        module = frame.f_globals["__name__"]
        if module.startswith("odoo.addons."):
            module = cut_prefix(module, "odoo.addons.")
            res = module.split(".", 1)[0]
        elif module.startswith("openerp.addons."):
            module = cut_prefix(module, "openerp.addons.")
            res = module.split(".", 1)[0]
        depth += 1
        frame = frame.f_back
    return res


del re, logging
