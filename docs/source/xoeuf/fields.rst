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

.. autoclass:: Property(getter, setter=None, deleter=None, onsetup=None, memoize=False, **kwargs)

.. autoclass:: Monetary(string=None, currency_field='currency_id', **kwargs)

.. autofunction:: TimeSpan

.. autoclass:: Enumeration
   :members: get_selection_field

.. autofunction:: TimezoneSelection

.. autoclass:: TimeDelta(string=None, digits=None, **kwargs)

.. autoclass:: One2one

.. autoclass:: TimeRange(time_field, selection, *args, **kwargs)

.. autoclass:: TypedReference(mixin, [delegate=False], **kwargs)
