=====================================================================
:mod:`xoeuf.pool` -- A pool of OpenERP *managed* database connections
=====================================================================

.. module:: xoeuf.pool

This module provides the entry point for an Import Hook (:pep:`302`) that
allows to "import" OpenERP's managed database connections.

This allows to use OpenERP's connections in a shell and test your code there::


  >>> from xoeuf.pool import dbname  # This should be a real database name
  ...                                # with OpenERP installed.

Afterwards, you may just use the ``dbame.models`` to get access to installed
models::

  >>> dbname.models.res_partner
  <openerp.osv.orm.res.partner at 0x6c3a790>


Implementation details
======================

.. class:: ModuleHook

   Import Hooks for OpenERP databases.

   .. classmethod:: find_module(cls, name, path=None)

      Implements the first protocol described in :pep:`302` -- Import Hooks.


See also:

- :mod:`xoeuf.osv.registry`
