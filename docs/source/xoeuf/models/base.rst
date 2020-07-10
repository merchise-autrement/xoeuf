============================================
 :mod:`xoeuf.models` - Utilities for models
============================================

The package
===========

.. module:: xoeuf.models

This module imports all of ``odoo.models`` into its namespace.  It also
re-exports the functions in `xoeuf.models.base`:mod:

.. class:: BaseModel

   This is the same as ``odoo.models.BaseModel`` with some extensions
   injected:

   .. property:: reference_repr

      The string representation compatible for Reference fields

   .. method:: iter_descendant_models(find_inherited=True, find_delegated=True, allow_abstract=False, allow_transient=False, exclude_self=True)

      Return a iterable of `(model_name, model)` of models inheriting from `self`.

      If `find_inherited` is True find models which use ``_inherit`` from
      `self`.  If `find_delegated` is True find models which use ``_inherits``
      (or ``delegate=True``) from `self`.

      If `allow_abstract` is True, yield models which are AbstractModels.  If
      `allow_transient` is True, yield transient models.

      If `exclude_self` is True, don't yield `self`.

      .. seealso:: xoeuf.models.base.iter_descendant_models

      .. versionadded:: 1.2.0


Basic extensions
================

.. automodule:: xoeuf.models.base
   :members: get_modelname, ViewModel, iter_descendant_models
