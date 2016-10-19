===================================================
 `xoeuf.sentrylog`:mod: -- Integration with Sentry
===================================================

.. module:: xoeuf.sentrylog

Extends/Overrides the OpenERP's logging system to Sentry-based approach.

Sentry_ aggregates logs and lets you inspect the server's health by a web
application.

To configure, simply set the global `conf`:obj: dictionary and call
`patch_logging`:func:.


.. function:: patch_logging(override=True)

   Patch openerp's logging.

   :param override: If True suppress all normal logging.  All logs will be
                    sent to the Sentry instead of being logged to the console.
                    If False, extends the loogers to sent the errors to the
                    Sentry but keep the console log as well.

   The Sentry will only receive the error-level messages.

.. object:: conf

   Configuration object.

   Keys:

   ``"dsn"``

      The DSN (an URL) to configure the Raven_ client.

   ``"release"``

      The release number to include error reports.

   ``"transport"``

      Should be one of "gevent", "sync" or "threaded".  The default is
      "threaded".

      Determines the transport to use when connecting to Sentry to report
      events.

   Other keys are passed directly to the ``raven.Client`` object.


.. _Sentry: https://sentry.io/
.. _Raven: https://pypi.python.org/pypi/raven
