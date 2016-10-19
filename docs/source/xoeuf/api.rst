=====================================================
 :mod:`xoeuf.api` -- Bridge between Odoo and OpenERP
=====================================================

.. versionadded:: 0.5.0

.. automodule:: xoeuf.api

.. autofunction:: contextual

.. class:: Environment

   When Odoo is available (i.e is importable [#odoo-v-openerp]_) this is the
   same `openerp.api.Enviroment`:class: class.

.. autofunction:: take_one



Version 8 and Version 7
=======================

Odoo introduces a change in its API for models.  This document won't explain
all the details.  For that you should see the `Official API documentation
<openerp.api>`:mod:.

.. Use auto-class so that the "alias of" is printed.

.. function:: v8(func)

   Either an alias to `_version_X`:func: or an alias to
   `openerp.api.v8`:func:.

.. function:: v7(func)

   Either an alias to `_version_X`:func: or an alias to
   `openerp.api.v7`:func:.


.. autofunction:: _version_X


.. function:: guess(func)

   A bridge for `openerp.api.guess`:func:.  It allows to guess the API version
   from the function signature.

   This allows you old mixins to work properly on both Odoo and OpenERP::

      class OldMixin(object):
         @api.guess
         def name_get(self, cr, uid, ids, context=None):
	     pass

      class MyModel(OldMixin, Model):
         _name = _inherit = 'some.model'

   Not doing this, causes a TypeError when running in Odoo.

   .. note:: You should use if possible the inheritance schemes provided by
      OpenERP.

      This was provided because one of our addons actually use the Python
      inheritance for mixin injection in our models.


Notes
=====

.. [#odoo-v-openerp]  You MUST NOT install both Odoo and OpenERP on the same
   Python environment, for one will shadow the other.
