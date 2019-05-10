====================================================================
 `xoeuf.models.proxy`:mod: -- High-level importer for Odoo's models
====================================================================

.. module:: xoeuf.models.proxy

.. deprecated:: 0.61.0 This module is completely deprecated and will be
                removed before the final release of 1.0

.. warning:: In the previous release this was named `xoeuf.models`, however
   that's now a package that contains a lot more, and the `ModelProxy`:class:
   is just a part.

   This is backwards breaking change.

This module allows to *import* the models for the DB like::

  >>> from xoeuf.models.proxy import AccountAccount

This returns a `ModelProxy`:class: to a model name.  The model name is
obtained by converting the 'CamelCase' to Odoo's "standard" on models name:
"camel.case", ie. each word is lowercase and words are separated by a dot.

In order to actually *use* the model proxy you must invoke in a frame were a
'self' local refers to an Odoo's model instance.  Otherwise you'll get an
AttributeError.  This 'self' is used to get access to the Odoo environment.

If the 'self' is not a new API model instance, but it's an Odoo model, we also
look for the 'cr', 'uid', and 'context' locals to create the environment.

The model proxy will always use the new API.


Example::

  >>> from xoeuf.models import ResPartner as Partner

  # At this point you can't use any method of Partner, since there's no
  # self.

  >>> Partner.search([])  # doctest: +ELLIPSIS
  Traceback (...)
  ...
  RuntimeError: ...


  >>> from xoeuf.pool import mercurio as db
  >>> db.salt_shell(_='account.account')

  # Now we have an oldish API self, cr, uid and context

  >>> Partner.search([])
  res.partner(...)

  >>> self = env['account.account']  # new API self

  >>> Partner.search([])
  res.partner(...)


Internals
=========

.. autoclass:: ModelProxy

   This is Python module that proxies an Odoo model.

   .. method:: __getattr__(self, attr)

      Looks for `attr` in the proxied model.  We inspect the Python frame
      stack looking a local 'self', which must be a instance of an Odoo
      model.  We use the 'self' to get access to the model registry and the
      execution environment to fetch the model this proxy stands for.

   .. attribute:: _instances_

      All the *possible* instances of this model.

      The result is an object that allows for containment tests.  The
      containment test would be equivalent to an `isinstance` check.

      Example::

        from xoeuf.models.proxy import SomeModel
        record in SomeModel._instances_

      .. warning:: This may shadow an attribute '_instances_' in the proxied
                   model.
