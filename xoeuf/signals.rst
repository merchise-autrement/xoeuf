=======================
 Signals and Wrappings
=======================

A basic signals system for Odoo.  Allows you to define Signal and Wrapping and
dispatch them when certain events happen in the system.

Includes four basic pairs of signals:

- `pre_create`:obj: and `post_create`:obj:
- `pre_write`:obj: and `post_write`:obj:
- `pre_unlink`:obj: and `post_unlink`:obj:
- `pre_fields_view_get`:obj: and `post_fields_view_get`:obj:

and a wrapping:

- `write_wrapper`:obj:.


Terms and concepts
==================

.. glossary::

   signal

     It's the notification of an event in the system.  The provided signals
     belongs to very simple types of events.

   receiver

     Any callable (although normally a function) that should be ran when a
     signal is dispatched.

   wrapping

     Allows to defined (more) complex types of events that occur when the
     conditions of the systems are different before and after an operation.

   wrapper

     A function that ``yields`` exactly once, that is processed when a
     wrapping is executing.


Usage
=====

Example::

   >>> @receiver([pre_write, pre_create], sender='account.move.line')
   ... def watch_for_something(sender, signal, values=None, **kwargs):
   ...     pass


The `watch_for_something` function will be called each time a ``.create()`` or
``.write()`` performed for the model 'account.move.line'.

A single call is made per per call of ``.create()`` or ``.write()``.  No
serialization of singleton recordset happens.

The receiver is called only if the addon where it is defined is installed in
the DB where the signal was dispatched.

This signal scheme can be applied to non Odoo models, in this case all
receivers matching the sender will be applied despite the addon where they are
defined.

.. warning:: The first positional is always the sender.

   It's best to make your receivers functions outside Odoo models to gain
   readability: Readers may believe they are reading a normal method code.

Caveats:

- Signals may be bypassed if any model extension redefines the Model method
  and does not issue the signal.

  To the best of our knowledge all model extension call the `super` and,
  thus, the signal is called but probably after some code of the extension
  method, and the 'post' signals will be called before the code following
  the call to `super`.


Writing receivers and wrappers
==============================

The signature of the receiver is::

  _do_receive(sender, signal, **kwargs)


The keyword arguments vary from signal to signal.  It's recommended that all
receivers include the ``**kwargs`` after the known keywords.


The signature of the wrapper is::

  _do_wrap(sender, wrapping, *args, **kwargs)


The variable positional arguments and keywords are just the same as the
operation that we're wrapping.

..
   Local Variables:
   ispell-dictionary: "en"
   End:
