=======================================================
 :mod:`xoeuf.signals` -- Basic signaling of ORM events
=======================================================

.. module:: xoeuf.signals

.. function:: receiver(signal, **kwargs)

   A decorator for connecting receivers to signals.

   :param signal: Either a single signal or a list of signals.

   :keyword require_registry: If set to True the receiver will only be called
                              if the Odoo DB registry is ready.

   Used by passing in the signal (or list of signals) and keyword arguments to
   connect::

     @receiver(post_save, sender='my.model')
     def signal_receiver(sender, **kwargs):
        pass

     @receiver([post_save, post_delete], sender='my.model')
     def signals_receiver(sender, **kwargs):
        pass


.. function:: filtered(*predicates)

   Allow to decorate receivers with simple predicates.

   This is useful if the simple filter by model name is not enough, and also
   if the filter needs to connect to use the DB.

   Usage::

     >>> @receiver(signal)
     ... @filtered(lambda self, **kwargs: True)
     ... def handler(self, **kwargs):
     ...     pass


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
