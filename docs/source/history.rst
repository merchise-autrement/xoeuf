=========
 History
=========

Beta releases (series 0.X)
==========================

2017-08-25. Release 0.11.0
--------------------------

- `xoeuf.models.extensions.get_treeview_action`:func: is ported to the new
  API.


2017-08-17.  Summary of changes up to release 0.10.0
----------------------------------------------------

- Drop support for OpenERP 7.0, and support Odoo 8, 9 and 10.

- Remove the browse extensions (``xoeuf.osv.browser_extensions``) since new
  record-sets cover those uses.

- Module `xoeuf.osv.model_extensions`:mod: was moved to
  `xoeuf.models.extensions`:mod:.  You should import from there.

- Function `xoeuf.osv.orm.get_modelname`:func: was moved to
  `xoeuf.models.get_modelname`:func:.

- New module `xoeuf.models.proxy`:mod:.  `xoeuf.models.get_modelname`:func:
  supports model proxies.

- `xoeuf.models.extensions.get_writer`:func: and
  `xoeuf.models.extensions.get_creator`:func: now support and encourage the
  new API.  The old API is left to support Odoo 8 and 9, but Odoo 10 lacks
  it.  You can't use the old API when running Odoo 10.

- Both `xoeuf.sentrylog`:mod: and `xoeuf.signals` check if Odoo has those
  modules (we have a distribution of Odoo that does).

  This poses the challenge to keep changes in our Odoo distribution with
  xoeuf.

- Deprecate `xoeuf.osv.fields`:mod:, will promote the usage of new API fields.

- Add fields `xoeuf.fields.LocalizedDatetime`:class:,
  `xoeuf.fields.Property`:class:, and `xoeuf.fields.Monetary`:class:.  All of
  those fields work in Odoo 8, 9 and 10.

  .. note:: `xoeuf.fields.Monetary`:class: is actually a float in Odoo 8, in
     Odoo 9 and Odoo 10 it's an alias to Odoo's own field.

- Remove `xoeuf.api.take_one`:func: and provide an idiomatic
  `xoeuf.api.requires_singleton`:func:.

- Add imports hooks to import from either `odoo` or `openerp` according to the
  Odoo version.

  Odoo 10 changes it's namespace from `openerp` to `odoo`.  They provide a
  fallback so that imports don't fail.  We provide it via:
  ``from xoeuf.odoo ...``.

  Examples::

    from xoeuf.odoo.tools import config


2016-10-19. Summary of changes up to release 0.6.6
--------------------------------------------------

- Added the `xoeuf.sentrylog`:mod: to make Odoo report errors to Sentry.

- Added the `xoeuf.signals`:mod: module (ported to our Odoo version).

- Provide an 'ishell' alias to our own shell for Odoo >= 9.0

- Make `xoeuf.osv.fields.localized_datetime`:class: fail if the time-zone
  field does not exist.

- Allow the new API in `xoeuf.osv.model_extensions.get_writer`:func: and
  `xoeuf.osv.model_extensions.get_creator`:func:.

- Added `xoeuf.api.take_one`:func:.


2015-01-21. Release 0.5.0
-------------------------

.. note:: We start to record the history changes in this release.

   All items below are introduced in this release only.  Other features are
   simply introduced in earlier version.

   The pre-1.0 series will be always latest-is-best.  No fixes will be done to
   previous versions.

- Now `xoeuf` is capable to run Odoo (version 8.0).  `xoeuf` no longer
  requires the "``openerp``" distribution, to allow be installed along with
  Odoo.

  The new `xoeuf.api`:mod: module eases the task to write modules with are
  compatible with OpenERP 7.0 and Odoo 8.0.

- Add the documentation of `xoeuf.tools`:mod:.  Several functions were fixes
  and others were added.
