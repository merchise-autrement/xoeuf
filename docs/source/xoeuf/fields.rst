=====================================================
 :mod:`xoeuf.fields` -- Other fields for Odoo models
=====================================================

.. module:: xoeuf.fields

This module re-export all attributes from `odoo.fields`:mod: (or
`openerp.fields`:mod: if using Odoo 8 o 9).  This means you can use it as
replacement.  We recommend doing::

  from xoeuf import fields

We don't backport all fields from later Odoo versions to earlier ones, though.


.. autoclass:: LocalizedDatetime

.. class:: Property(getter, setter=None, deleter=None, onsetup=None, **kwargs)

   A property-like field.

   This is always non-store field.  This is a kind of hack:

   Normal Python `properties <property>`:class: are not copied through Odoo
   inheritance mechanisms.  This `Property` is a Field and Odoo accounts for
   it.  But, it is NOT an actual ORM field in the sense that it never
   interacts with the DB.  Therefore:

   - You MUST NEVER use `write()` or `create()` on these type of fields.
     You may update the value via the `setter` (i.e assign it).

   - You cannot `search()` for this type of fields.

   - You cannot use Property fields in views.

     The main difference to any other computed field is that Property is
     **untyped**.  We don't enforce any type check on the value returned by
     getters.  But, then, we cannot communicate which widget can manage the
     value of a Property.

   The getter, setter and deleter functions receive (and thus we required it)
   a singleton recordset instance.  The onsetup functions receive the field
   instance, and the model on which the field is being setup.

   Usage::

      @Property
      def result(self):
          return 1

      @result.setter
      def result(self, value):
         pass

   You may also do::

      def _set_result(self, value):
          pass

      result = Property(lambda s: 1, setter=_set_result)
      del _set_result


.. autoclass:: Monetary(string=None, currency_field='currency_id', **kwargs)

.. autofunction:: TimeSpan

.. autofunction:: Enumeration

.. autofunction:: TimezoneSelection

.. autoclass:: TimeDelta(string=None, digits=None, **kwargs)

.. autoclass:: One2one
