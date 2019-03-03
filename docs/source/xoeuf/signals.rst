=======================================================
 :mod:`xoeuf.signals` -- Basic signaling of ORM events
=======================================================

.. module:: xoeuf.signals

Implements basic signals system for Odoo.  Allows you to define a
`Signal`:class: or `Wrapping`:class: and dispatch them when certain events
happen in the system.


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

Caveats
-------

Signals may be bypassed if any model extension redefines the Model method and
does not issue the signal.

To the best of our knowledge all model extension call the `super` and, thus,
the signal is called but probably after some code of the extension method, and
the 'post' signals will be called before the code following the call to
`super`.


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


API
===

.. autoclass:: Signal
   :members: send, safe_send

.. autoclass:: Wrapping
   :members: perform

.. function:: receiver(signal, , sender=None, require_registry=True, framework=False)

   A decorator for connecting receivers to signals.

   :param signal: Either a single signal or a list of signals_.

   :keyword require_registry: If set to True the receiver will only be called
                              if the Odoo DB registry is ready.

   :keyword framework: Set to True to make this a `framework-level hook
                       <FrameworkHook>`:class:.

                       Framework-level hooks are always considered installed
                       in any DB.  So you should be careful no requiring
                       addon-level stuff

  Basic usage::

     @receiver(post_save, sender='my.model')
     def signal_receiver(sender, signal, **kwargs):
        pass


.. function:: wrapper(wrapping, sender=None, require_registry=True, framework=False)

   A decorator for connecting wrappers to wrappings_.

   :param wrapping: Either a single wrapping or a list of wrappings.

   :keyword require_registry: If set to True the receiver will only be called
                              if the Odoo DB registry is ready.

   :keyword framework: Set to True to make this a `framework-level hook
                       <FrameworkHook>`:class:.

                       Framework-level hooks are always considered installed
                       in any DB.  So you should be careful no requiring
                       addon-level stuff

   Basic usage::

     @wrapper(write_wrapper, sender='my.model')
     def signal_receiver(sender, wrapping, *args, *kwargs):
        yield



Signals
=======

.. object:: pre_fields_view_get

   A `Signal`:class: signaled when the method `fields_view_get` is about to
   execute in a model.


.. object:: post_fields_view_get

   A `Signal`:class: signaled when the method `fields_view_get` was executed
   in a model.


.. object:: pre_create

   Signal sent when the 'create' method is to be invoked.

   If a receiver raises an error the create is aborted, and post_create won't
   be issued.  The error is propagated.

   Arguments:

   :param sender: The recordset where the 'create' was called.

   :keyword values: The values passed to 'create'.


.. object:: post_create

   Signal sent when the 'create' method has finished but before data is
   committed to the DB.

   If the 'create' raises an error no receiver is invoked.

   If a receiver raises an error, is trapped and other receivers are allowed
   to run.  However if the error renders the cursor unusable, other receivers
   and the commit to DB may fail.

   If a receiver raises an error the create is halted and the error is
   propagated.

   Arguments:

   :param sender: The recordset where the 'create' was called.

   :keyword result: The result of the call to 'create'.
   :keyword values: The values passed to 'create'.


.. object:: pre_write

   Signal sent when the 'write' method of model is to be invoked.

   If a receiver raises an error the write is aborted and 'post_write' is not
   sent.  The error is propagated.

   Arguments:

   :param sender: The recordset sending the signal.

   :keyword values: The values passed to the write method.


.. object:: post_write

   Signal sent after the 'write' method of model was executed.

   If 'write' raises an error no receiver is invoked.  If a receiver raises an
   error is trapped (see `safe_send`) and other receivers are allowed to run.
   However, if the error renders the cursor unusable other receivers may fail
   and the write may fail to commit.

   Arguments:

   :param sender: The recordset sending the signal.

   :keyword result: The result from the write method.

   :keyword values: The values passed to the write method.


.. object:: pre_unlink

   Signal sent when the 'unlink' method of model is to be invoked.

   If a receiver raises an error unlink is aborted and 'post_unlink' is not
   called.  The error is propagated.

   Arguments:

   :param sender: The recordset sending the signal.


.. object:: post_unlink

   Signal sent when the 'unlink' method of a model was executed.

   If the 'unlink' raises an error no receiver is invoked.  If a receiver
   raises an error is trapped (see `safe_send`) other receivers are allowed to
   run.  However, if the error renders the cursor unusable other receivers may
   fail and the unlink may fail to commit.

   Arguments:

   :param sender: The recordset sending the signal.

   :keyword result:  The result from the unlink method.


.. object:: pre_search

   Signal sent when the 'search' method is to be invoked.

   Arguments:

   :param sender: The recordset where the 'search' was called.

   :keyword query: The domain (argument `args` in Odoo's search method).
                   This will be `list`:class: that can be modified in place, to
                   customize the search.  But notice that the order in which the
                   receivers are called is not defined.

   :keyword pos_args:  The rest of the positional arguments (if any).

   :keyword kw_args: The rest of the keyword arguments (if any).


.. object:: post_search

   Signal sent after the 'search' method was invoked.

   Arguments:

   :param sender: The recordset where the 'search' was called.

   :keyword query: The domain (argument `args` in Odoo's search method).
                   This will be `list`:class: that can be modified in place, to
                   customize the search.

   :keyword pos_args:  The rest of the positional arguments (if any).

   :keyword kw_args: The rest of the keyword arguments (if any).

   :keyword result: The result of the actual 'search'.



Wrappings
=========

.. object:: write_wrapper

   A wrapping around the 'write' method of models.


Other
=====

.. autofunction:: no_signals

.. autofunction:: mock_replace
