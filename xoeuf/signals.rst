=========
 Signals
=========

A basic signals system for Odoo.  Allows you to define Signal and dispatch
them when certain events happen in the system.

Includes four basic pairs of signals:

- `pre_create`:obj: and `post_create`:obj:
- `pre_write`:obj: and `post_write`:obj:
- `pre_unlink`:obj: and `post_unlink`:obj:
- `pre_fields_view_get`:obj: and `post_fields_view_get`:obj:


Usage::

   >>> @receiver([pre_write, pre_create], sender='account.move.line')
   ... def watch_for_something(sender, signal, values=None, **kwargs):
   ...     pass

The `watch_for_something` function will be called each time a ``.create()`` or
``.write()`` performed for an 'account.move.line'.

Notice that a single call is made per recordset.  The receiver is called only
if the addon where it is defined is installed in the DB where the signal was
dispatched.

This signal scheme can be applied to non Odoo models, in which case all
receivers matching receives will be applied despite the addon where they are
defined.

.. warning:: The first positional is always the sender.

   It's best to make your receivers functions outside Odoo models to gain
   readability.

Caveats:

- Signals may be bypassed if any model extension redefines the Model method
  and does not issue the signal.

  To the best of our knowledge all model extension call the `super` and,
  thus, the signal is called but probably after some code of the extension
  method, and the 'post' signals will be called before the code following
  the call to `super`.

- Receivers must ensure to be registered on every thread/process.  Most of
  the time this requires little effort, though.


..
   Local Variables:
   ispell-dictionary: "en"
   End:
