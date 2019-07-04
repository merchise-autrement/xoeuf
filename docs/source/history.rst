=========
 History
=========

Beta releases (series 0.X)
==========================

We're approaching a final 1.0 release.  We're stopping adding new features
to xoeuf, but the next releases will remove most of the deprecated features
that remain in the code.

Each major version of xoeuf (1.x, 2.x, etc) will be 100% compatible with
latest version of Odoo supported by xoeuf (at that moment).  We'll try to make
each major version backwards-compatible with the two previous versions of
Odoo.  So, xoeuf 1.0 will be compatible with Odoo 12, and many of its features
will work on Odoo 10 and 11.


2019-07-04.  Release 0.66.0
---------------------------

- Fix bug in `xoeuf.fields.Enumeration.get_selection_field`:func:.  Basically
  it would not work when used directly in models.

- The argument to `compute_member_string` in
  `~xoeuf.fields.Enumeration.get_selection_field`:func: must now accept three
  arguments: the model, the name, and the value.


2019-06-13.  Release 0.65.0
---------------------------

- Fix bug in `xoeuf.fields.One2one`:class: when used as a related field.


2019-05-31.  Release 0.64.0
---------------------------

- Make `~xoeuf.fields.Enumeration`:class: class and allow deferring the
  creation of the enumeration class to each model.


2019-05-30.  Release 0.63.0
---------------------------

- Update `~xoeuf.signals.pre_create`:data: and
  `~xoeuf.signals.post_create`:data: to reflect the standard
  ``@api.model_create_multi`` when running in Odoo 12.  In Odoo 10 and 11, the
  are decorated with ``@api.model``.

  Similarly, update the internal mixin used by
  `xoeuf.fields.Enumeration`:func:.

- Bootstrap all fields in the 'ir.model.fields' selection of 'ttype'.  You
  SHOULD run Odoo by running the 'xoeuf' command so this bootstrapping work.
  Otherwise new field types (`xoeuf.fields.Property`:class: and others) fail
  in the 'report.base.report_irmodeloverview'.


2019-05-14.  Release 0.62.0
---------------------------


- Fix NameError when running in Python 3+.

- Allow to use xoutil_ 2.1+.

.. _xoutil: https://pypi.org/project/xoutil


2019-05-11.  Release 0.61.0
---------------------------

- Remove the INT-based DB representation of `xoeuf.fields.Enumeration`:class:.

  This a breaking change.  User SHOULD NOT upgrade without doing a DB
  migration.

- Fix several bugs of `xoeuf.fields.Eumeration`:class:\ :

  - Enumeration fields would not properly work in abstract models.

  - Enumeration fields would not properly work when used via delegation (or
    related).

    .. warning:: This was fixed for Odoo 12, but still fails in Odoo 10
       and 11.

- Add an automatic selection field in `xoeuf.fields.Enumeration`:class:.

- Remove support to use `~xoeuf.models.base.get_modelname`:func: with model
  proxies.

- Deprecate model proxies `xoeuf.models.proxy`:mod:.

- Remove deprecated module ``xoeuf.models.importer``.


2019-05-03.  Release 0.60.0
---------------------------

- We're starting to remove support for Odoo 10.  All features still work in
  the three previously supported versions (10, 11 and 12); but newer features
  may not work in Odoo 10.

- Add `xoeuf.fields.TypedReference`:class:.


2019-04-29.  Release 0.59.0
---------------------------

- Restate `xoeuf.fields.Property`:class: as class.  Release 0.58.0 converted
  Property to a function (fields in Odoo can't be callable because that
  confuses ``api.guess``).  That broke some code in other projects that uses
  ``isinstance(field, fields.Property)``.

  This release makes the function a class with a special metaclass to actually
  return a ``PropertyField`` instance, and to perform the instance check.


2019-04-26.  Release 0.58.0
---------------------------

- Add parameter `memoize` to `xoeuf.fields.Property`:class:


2019-03-27.  Release 0.57.0
---------------------------

- Fix bug in `xoeuf.tools.add_symbols_to_xmls`:func: when passing positional
  arguments.


2019-03-03.  Release 0.56.0
---------------------------

- `xoeuf.signals.receiver`:func: can take an iterable of signals.

- Add `xoeuf.signals.no_signals`:func:.


2019-03-01.  Release 0.55.0
---------------------------

- Improve `xoeuf.osv.expression.Domain.asfilter()`:meth: to avoid *required
  singleton* errors if the domain uses Many2many or One2many fields.


2019-02-27.  Release 0.54.0
---------------------------

- Add `xoeuf.osv.expression.Domain.asfilter()`:meth:.


2019-02-08.  Release 0.53.0
---------------------------

- Add support for Odoo 12.


2019-01-07.  Release 0.52.0
---------------------------

- Add function `xoeuf.models.extensions.get_ref`:func:.


2018-12-24.  Release 0.51.0
---------------------------

- Add argument `max_depth` to `~xoeuf.modules.get_caller_addon`:func:

- Add function `xoeuf.models.base.ViewModel`:class:.


2018-10-18.  Release 0.50.0
---------------------------

- Reimplement `~xoeuf.tools.localtime_as_remotetime`:func: so that it takes
  into account DST properly.  Reimplement
  `~xoeuf.tools.localize_datetime`:func: in terms of
  `~xoeuf.tools.localtime_as_remotetime`:func:.


2018-10-08.  Release 0.49.1
---------------------------

- No code changes.

  A known bug in `xoeuf.fields.LocalizedDatetime`:class: was preventing the CI
  pipeline to run and generated the docs.

  The bug remains marked as a known bug so the CI pipeline continues.

  Also corrected the documentation of some functions that were not in the
  documents but exist in the code.


2018-10-07.  Release 0.49.0
---------------------------

- Deprecate using `~xoeuf.models.get_modelname`:func: with a model proxy as an
  argument.

- Add parameter `ignore_dst` to `~xoeuf.tools.localtime_as_remotetime`:func:.

- Fix bug with `xoeuf.fields.Enumeration`:class:\ : it was not possible to set
  an enumeration to False or None.

2018-09-19.  Release 0.48.0
---------------------------

- Fix bug in the BaseModel that raises KeyError with unknown fields.

  Introduced in 0.46.0, with the `~xoeuf.api.onupdate`:func: hack of
  ``_validate_fields``.


2018-08-28. Release 0.47.0
--------------------------

- Fix issues with Char based :class:`xoeuf.fields.Enumeration`:

  - Putting a default value would break the whole model (creating the DB table
    failed).

  - When assigning an enumeration inside the inverse method of computed field,
    it double-converted the value to str which raised a KeyError.

  - The ``create`` method of the models using Enumeration field didn't have
    the downgrade which means that any model using it would be hard to use in
    the web client.

    The web client would get the id as string: 'model(id, )'.


2018-08-24.  Release 0.46.0
---------------------------

- Add `xoeuf.modules.get_caller_addon`:func:.

- Add `xoeuf.api.onupdate`:func:.

- Remove deprecated decorator ``xoeuf.api.take_one``.


2018-07-18.  Release 0.45.0
---------------------------

- Make ``xoeuf.osv.expression.Domain.simplified`` return a domain that is
  compatible with Odoo.

  See `MR 9`_.

.. _MR 9: https://gitlab.merchise.org/merchise/xoeuf/merge_requests/9


2018-06-27.  Release 0.44.0
---------------------------

- Don't re-export ``xoeuf.fields.Serialized``.  We cannot properly import it
  from xoeuf, since it's now in an addon.  This corrects a critical import
  error introduced in 0.43.0, which makes it impossible to import.


2018-06-22.  Release 0.43.0
---------------------------

- Ensure we always have the ``xoeuf.fields.Serialized``.  Odoo 11 moved it to
  an addon.

- Add variable positional arguments to
  `xoeuf.tools.add_symbols_to_xmls`:func:.


2018-06-15.  Release 0.42.0
---------------------------

- Create the utility `xoeuf.tools.add_symbols_to_xmls`:func:.

- Allow to use the all ORM human symbols
  (`~xoeuf.osv.orm.CREATE_RELATED`:func:, etc) in XML files.

- Add experimental field `xoeuf.fields.TimeRange`:class:.

2018-06-04. Release 0.41.0
--------------------------

- Don't force value to `int`:class: in `xoeuf.fields.Enumeration`:class:.
  This allows customized `create` to get the *real* value from the
  enumeration (and it will be an integer anyways).

2018-05-25. Release 0.40.0
--------------------------

- Fix issue with XMLRPC clients when calling 'search'.  The signals were
  masking the 'search' signature.


2018-05-24.  Release 0.39.0
---------------------------

- Fix bug in `xoeuf.signals.pre_fields_view_get`:obj: and
  `xoeuf.signals.post_fields_view_get`:obj:, which by-passed
  ``fields_view_get`` in abstract models.


2018-05-21.  Release 0.38.0
---------------------------

- Refactor `xoeuf.fields.Enumeration`:class: to reduce overhead in models not
  using it.  No visible changes in the API.


2018-05-17.  Release 0.37.0
---------------------------

- Add `xoeuf.fields.One2one`:class:

- Add `xoeuf.signals.pre_search`:obj: and `xoeuf.signals.post_search`:obj:.

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

- Deprecate ``xoeuf.api.take_one`` and provide an idiomatic
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

- Added ``xoeuf.api.take_one``.


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
