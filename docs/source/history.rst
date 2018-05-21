=========
 History
=========

Beta releases (series 0.X)
==========================

2018-05-21.  Release 0.38.0
---------------------------

- Refactor `xoeuf.fields.Enumeration`:class: to reduce overhead in models not
  using it.  No visible changes in the API.


2018-05-17.  Release 0.37.0
---------------------------

- Add `xoeuf.fields.One2one`:class:

- Add `xoeuf.signals.pre_search`:object: and
  `xoeuf.signals.post_search`:object:.

- Allow to search over fields defined with an `enumeration
  <xoeuf.fields.Enumeration>`:class:


2018-05-14. Release 0.36.0
--------------------------

- `xoeuf.fields.Enumeration`:class: was generalized to support any kind of
  enumeration.

  The integer DB representation will still works: if all the members of the
  enumeration class are integers the DB representation will the integer.


2018-05-07. Release 0.35.0
--------------------------

- Change the default of `leak_context` in `xoeuf.api.from_active_ids`:func:.
  Also `~xoeuf.api.from_active_ids`:func: does not change the value
  'active_model' in the context.


2018-05-03. Release 0.34.0
--------------------------

- Improve the decorator `~xoeuf.api.from_active_ids`:func: to have
  `leak_context` argument and, also, allow the decorated method to take
  arguments.


2018-05-02. Release 0.33.0
--------------------------

- Add `xoeuf.api.from_active_ids`:func:.


2018-04-25. Release 0.32.0
--------------------------

- Make model proxy modules more resilient to introspection.  Some tools might
  try to get the ``__file__`` attribute to generate tracebacks.

  When getting ``__file__`` or ``__module__`` they are not proxied to the
  underlying model object.


2018-04-21. Release 0.31.0
--------------------------

Revert the requirement of xoutil 2 when installed in Python 3.  Just allow any
'xoutil>=1.9.0' and require it to be less than xoutil 2 when not in Python 3.

Roughly::

  'xoutil>=1.9.0,<2.0; python_version < "3.4"'
  'xoutil>=1.9.0; python_version >= "3.4"'


Packages that need to support Python 2 but also want to use xoeuf's latest
version wouldn't be able to do so otherwise.


2018-04-17. Release 0.30.0
--------------------------

No user visible changes.  Requires xoutil 2.0 when installed in Python 3 and
xoutil 1.9 for Python 2.


2018-04-13. Release 0.29.1
--------------------------

No user visible changes.  Just packages and CI related.  That made CI fail to
build and publish 0.29.0.


2018-04-13.  Release 0.29.0
---------------------------

- Remove the command 'shell'.  Since Odoo has its own shell now, and we
  already updated our shell to be the same as its, there's no point in keeping
  our copy of 'shell'.

- Remove the ``xoeuf.pool`` module.  Its main purpose was to be used in our
  shell.

- Remove the ``xoeuf.osv.registry`` module.  It was there mainly to support
  ``xoeuf.pool``.  Other modules now use Odoo's registry
  (``odoo.modules.registry``) directly.

- Remove the command 'mailgate'.  We no longer use it.  It's best to use a
  proven Inbox server (e.g dovecot) to safely store the emails.  Calling
  'mailgate' directly from the MTA may lead to lost of emails, if any error
  happens in the Python code.

- Add attribute `concrete` to `xoeuf.fields.Monetary`:class:.  MR `!22`_.

- Drop support for Odoo 8 and 9.

  Odoo 8 is not supported by Odoo SA any more.  We don't have the resources to
  support Odoo 9.  We support only Odoo 10 and Odoo 11.

.. _!22: https://gitlab.lahavane.com/mercurio/xoeuf/merge_requests/22


2018-03-02. Release 0.28.0
--------------------------

- Adds no functions.  Just allows xoutil 1.9.


2018-02-09. Release 0.27.0
--------------------------

- Drop official support for Odoo 8 and 9.  Tests are only run in Odoo 10
  and 11.

- Add `_instances_ <xoeuf.models.proxy.ModelProxy._instances_>`:attr: property
  to allows easy recordset ``isinstance`` like checks.


2018-01-23. Release 0.26.0
--------------------------

- Fix access denied error in `xoeuf.modules.is_object_installed`:func:.


2018-01-22. Release 0.25.0
--------------------------

- Unify sentry configuration under the 'sentry' namespace.  Also read the
  configuration from Odoo config object.


2018-01-04. Release 0.24.0
--------------------------

- Fix bug in `xoeuf secure` command for Odoo 10.


2017-12-29.  Release 0.23.0
---------------------------

- Fix critical issue in `xoeuf.signals`:mod:.  Different receivers for the
  same model would not be registered (and thus not called).  Introduced in
  0.22.0.


2017-12-23. Release 0.22.0
--------------------------

- Add `~xoeuf.signals.Wrapping`:class: and `~xoeuf.signals.wrapper`:func:.


2017-12-20.  Release 0.21.1
---------------------------

- 0.21.0 was published as 0.21.0.dev20171220.  This is just a version
  correction.


2017-12-20.  Release 0.21.0
---------------------------

- Require ``xoutil`` 1.8.4.

- Improve the documentation of `xoeuf.osv.expression.DomainTree`:class:.  Add
  method `~xoeuf.osv.expression.DomainTree.walk`:meth:.


2017-11-06.  Release 0.20.0
---------------------------

- Fix `xoeuf.modules.get_object_module`:func: for Odoo 10.


2017-11-01. Release 0.19.0
--------------------------

- Add `fields.TimeDelta`:class:


2017-10-31. Release 0.18.0
--------------------------

- Fix issue `#2`_: `xoeuf.osv.datetime_user_to_server_tz`:func: and
  `xoeuf.osv.datetime_server_to_user_tz`:func: didn't work on Odoo 10.


.. _#2: https://gitlab.lahavane.com/mercurio/xoeuf/issues/2

- Add explicit 'not equal' operator for `domain related
  <xoeuf.osv.expression>`:mod: functions.

- Covert to properties: `xoeuf.osv.expression.DomainTree.is_leaf`:attr: and
  `xoeuf.osv.expression.DomainTree.is_operator`:attr:.


2017-10-16. Release 0.17.2
--------------------------

- Fix AttributeError in DomainTree.


2017-10-14. Release 0.17.1
--------------------------

- Fix cyclic import in `fields.timezone`.  We have to retire 0.17.0.


2017-10-14. Release 0.17.0 (unusable)
-------------------------------------

- Added `fields.TimezoneSelection`:func: as simple way to avoid creating the
  same `fields.Selection` for timezones all over the place.


2017-10-14. Release 0.16.2
--------------------------

- Fix interface of `xoeuf.osv.expression.AND`:func: and
  `xoeuf.osv.expression.OR`:func:.

  They take a single argument (a list of lists), so they can be drop-in
  replacements for the ones in `odoo.osv.expression`:mod:.


2017-10-12. Release 0.16.1
--------------------------

- Avoid errors in `xoeuf.fields.Enumeration` if the writing/creating with
  values for unknown fields.

  Fixes MERCURIO-1ES.


2017-10-11. Release 0.16.0
--------------------------

- Allow to define `framework-level receivers <xoeuf.signals.receiver>`:func:.

- Make `xoeuf.fields.Enumeration`:func: check values on creation/write.  So no
  more invalid values can slip to the DB.

  .. note:: Requires the newest `signals` module if using a Merchise
            distributed Odoo.

- Start (yet unclaimed) support for Odoo 11.  `xoeuf.fields`:mod: and
  `xoeuf.models.proxy`:mod: pass all tests.

- Fix bug introduced in 0.15.0 when updating `xoeuf.models.proxy`:mod: to
  support HTTP requests.

- Add `xoeuf.osv.expression`:mod:.


2017-10-07.  Release 0.15.0
---------------------------

- Allow `xoeuf.fields.Property`:class: to setup.  When the ORM setups the
  models in the registry, the setup will be called.

- Extend models proxies to support HTTP requests.  This allows model proxies
  to be used in HTTP controllers.


2017-09-14.  Release 0.14.0
---------------------------

- Added `xoeuf.fields.Enumeration`:func:.



2017-09-05.  Release 0.13.0
---------------------------

- Added `xoeuf.fields.TimeSpan`:func:.  Requires xoutil 1.7.6.


.. note:: I created the release 0.13.0 out of 0.12.0.



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
