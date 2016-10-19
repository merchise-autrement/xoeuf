=========
 History
=========

Beta releases (series 0.X)
==========================

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
