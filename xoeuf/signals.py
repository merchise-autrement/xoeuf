#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoeuf.signals
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-12-19

'''Signals.

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

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


from xoutil import logger

from openerp import api, models


def _make_id(target):
    if hasattr(target, '__func__'):
        return (id(target.__self__), id(target.__func__))
    return id(target)


def _issubcls(which, Class):
    return isinstance(which, type) and issubclass(which, Class)


def _make_model_id(sender):
    '''Creates a unique key for 'senders'.

    Since Odoo models can be spread across several classes we can't simply
    compare by class object.  So if 'sender' is a BaseModel (subclass or
    instance), the key will be the same for all classes targeting the same
    model.

    '''
    BaseModel = models.BaseModel
    if isinstance(sender, BaseModel) or _issubcls(sender, BaseModel):
        return sender._name
    else:
        return sender


class Signal(object):
    """Base class for all signals

    Internal attributes:

        receivers
            [(receriverkey (id), receiver)]
    """
    def __init__(self, action=None, doc=None):
        self.receivers = []
        self.action = action
        self.__doc__ = doc

    def connect(self, receiver, sender=None, require_registry=True):
        """Connect receiver to sender for signal.

        :param receiver: A function or an instance method which is to receive
                signals.  Receivers must be hashable objects and must be able
                to accept keyword arguments.

        :param sender: The sender(s) to which the receiver should
                respond. Must either a model name, list of model names or None
                to receive events from any sender.

        :param require_registry: If True the receiver will only be called if a
               the actual `sender` of the signal has a ready DB registry.

        :return: None

        """
        if not isinstance(sender, (list, tuple)):
            sender = [sender]
        for s in sender:
            lookup_key = (_make_id(receiver), _make_model_id(s))
            if not any(lookup_key == r_key for r_key, _ in self.receivers):
                self.receivers.append(
                    (lookup_key,
                     Receiver(receiver, sender=sender,
                              require_registry=require_registry))
                )

    def disconnect(self, receiver=None, sender=None):
        """Disconnect receiver from sender for signal.

        :param receiver: The registered receiver to disconnect.

        :param sender: The registered sender to disconnect

        """
        receiver_item = (_make_id(receiver), sender), receiver
        if receiver_item in self.receivers:
            sender.receivers.remove(receiver_item)

    def has_listeners(self, sender=None):
        return bool(self._live_receivers(sender))

    def send(self, sender, **kwargs):
        """Send signal from sender to all connected receivers.

        If any receiver raises an error, the error propagates back through
        send, terminating the dispatch loop, so it is quite possible to not
        have all receivers called if a raises an error.

        If the `sender` is not an Odoo model any `receiver`:func: that
        requires a ready registry will no be called.

        :param sender: The sender of the signal either a model or None.
        :param kwargs: Named arguments which will be passed to receivers.
        :return: Returns a list of tuple pairs [(receiver, response), ... ].

        """
        responses = []
        if not self.receivers:
            return responses
        for receiver in self._live_receivers(sender):
            response = receiver(sender, signal=self, **kwargs)
            responses.append((receiver, response))
        return responses

    def safe_send(self, sender, catched=(Exception, ), thrown=None, **kwargs):
        """Send signal from sender to all connected receivers catching errors.

        :param sender: The sender of the signal either a model or None.

        :keyword catched: A (tuple of ) exception to safely catch. The default
                          is ``(Exception, )``.

        :keyword thrown: A (tuple of) exceptions to re-raise even though in
                 `catched`.  The default is not to re-raise any error.

        :return: Returns a list of tuple pairs [(receiver, response), ... ].

        All remaining keyword arguments are passed to receivers.

        If any receiver raises an error (specifically any subclass of
        Exception), the error instance is returned as the result for that
        receiver.

        """
        responses = []
        if thrown and not isinstance(thrown, (list, tuple)):
            thrown = (thrown, )
        if not self.receivers:
            return responses
        for receiver in self._live_receivers(sender):
            try:
                response = receiver(sender, signal=self, **kwargs)
            except catched as err:
                if thrown and isinstance(err, thrown):
                    # Don't log: I expect you'll log where you actually catch
                    # it.
                    raise
                else:
                    logger.exception(err)
                    responses.append((receiver, err))
            except:
                # Don't log: I expect you'll log where you actually catch it.
                raise
            else:
                responses.append((receiver, response))
        return responses

    def _live_receivers(self, sender):
        """Filter sequence of receivers to get resolved, live receivers.

        """
        if isinstance(sender, models.Model):
            registry_ready = sender.pool.ready
        else:
            registry_ready = False
        senderkey = _make_model_id(sender)
        receivers = []
        for (receiverkey, r_senderkey), receiver in self.receivers:
            if self._installed(sender, receiver) and not r_senderkey or r_senderkey == senderkey:
                if registry_ready or not receiver.require_registry:
                    receivers.append(receiver)
        return receivers

    def _installed(self, sender, receiver):
        '''Return True if the receiver is defined in a module installed in
        sender's database.

        If the receiver is not inside an addon it is considered system-wide,
        and thus, return True.

        If the sender does not have an 'env' attribute it will considered
        installed as well (this is for dispatching outside the Odoo model
        framework.)

        '''
        from xoeuf.modules import get_object_module
        module = get_object_module(receiver, typed=True)
        env = getattr(sender, 'env', None)
        if module and env:
            mm = env['ir.module.module']
            query = [('state', '=', 'installed'), ('name', '=', module)]
            return bool(mm.search(query))
        else:
            return True


class Receiver(object):
    '''Wraps a receiver, so that we can store some metadata.'''
    def __init__(self, receiver, **kwargs):
        from xoutil.objects import smart_copy
        self.receiver = receiver
        smart_copy(
            kwargs,
            self.__dict__,
            defaults={'require_registry': True, }
        )

    def __call__(self, *args, **kwargs):
        return self.receiver(*args, **kwargs)

    # So that the original receiver compares equal to this wrapper.
    def __hash__(self):
        return hash(self.receiver)

    def __eq__(self, other):
        return self.receiver == other


def receiver(signal, **kwargs):
    """A decorator for connecting receivers to signals.

    :param signal: Either a single signal or a list of signals.

    :keyword require_registry: If set to True the receiver will only be called
             if the Odoo DB registry is ready.

    Used by passing in the signal (or list of signals) and keyword arguments
    to connect::

        @receiver(post_save, sender='my.model')
        def signal_receiver(sender, **kwargs):
            ...

        @receiver([post_save, post_delete], sender='my.model')
        def signals_receiver(sender, **kwargs):
            ...

    """
    def _decorator(func):
        if isinstance(signal, (list, tuple)):
            for s in signal:
                s.connect(func, **kwargs)
        else:
            signal.connect(func, **kwargs)
        return func
    return _decorator


def filtered(*predicates):
    '''Allow to decorate receivers with simple predicates.

    This is useful if the simple filter by model name is not enough, and also
    if the filter needs to connect to use the DB.

    Usage::

        >>> @receiver(signal)
        ... @filtered(lambda self, **kwargs: True)
        ... def handler(self, **kwargs):
        ...     pass

    '''
    def decorator(func):
        from functools import wraps

        @wraps(func)
        def inner(self, **kwargs):
            if all(pred(self, **kwargs) for pred in predicates):
                return func(self, **kwargs)
        return inner
    return decorator


# **************SIGNALS DECLARATION****************
pre_fields_view_get = Signal('fields_view_get')
post_fields_view_get = Signal('fields_view_get')

pre_create = Signal('create', '''
Signal sent when the 'create' method is to be invoked.

If a receiver raises an error the create is aborted, and post_create won't be
issued.  The error is propagated.

Arguments:

:param sender: The recordset where the 'create' was called.

:keyword values: The values passed to 'create'.

''')

post_create = Signal('create', '''
Signal sent when the 'create' method has finished but before data is committed
to the DB.

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
''')

pre_write = Signal('write', '''
Signal sent when the 'write' method of model is to be invoked.

If a receiver raises an error the write is aborted and 'post_write' is not
sent.  The error is propagated.

Arguments:

:param sender: The recordset sending the signal.

:keyword values: The values passed to the write method.

''')
post_write = Signal('write', '''
Signal sent after the 'write' method of model was executed.

If 'write' raises an error no receiver is invoked.  If a receiver raises an
error is trapped (see `safe_send`) and other receivers are allowed to run.
However, if the error renders the cursor unusable other receivers may fail
and the write may fail to commit.

Arguments:

:param sender: The recordset sending the signal.

:keyword result: The result from the write method.

:keyword values: The values passed to the write method.

''')

pre_unlink = Signal('unlink', '''
Signal sent when the 'unlink' method of model is to be invoked.

If a receiver raises an error unlink is aborted and 'post_unlink' is not
called.  The error is propagated.

Arguments:

:param sender: The recordset sending the signal.

''')

post_unlink = Signal('unlink', '''
Signal sent when the 'unlink' method of a model was executed.

If the 'unlink' raises an error no receiver is invoked.  If a receiver
raises an error is trapped (see `safe_send`) other receivers are allowed to
run.  However, if the error renders the cursor unusable other receivers may
fail and the unlink may fail to commit.

Arguments:

:param sender: The recordset sending the signal.

:keyword result:  The result from the unlink method.

''')

pre_save = [pre_create, pre_write, pre_unlink]
post_save = [post_create, post_write, post_unlink]


# **************SIGNALS SEND****************
super_fields_view_get = models.Model.fields_view_get
super_create = models.BaseModel.create
super_write = models.BaseModel.write
super_unlink = models.BaseModel.unlink


# TODO: change to new api.
@api.guess
def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                    context=None, toolbar=False, submenu=False):
    kwargs = dict(
        view_id=view_id,
        view_type=view_type,
        toolbar=toolbar,
        submenu=submenu
    )
    self = self.browse(cr, uid, None, context=context)
    pre_fields_view_get.send(sender=self, **kwargs)
    result = super(models.Model, self).fields_view_get(**kwargs)
    post_fields_view_get.safe_send(sender=self, result=result, **kwargs)
    return result


@api.model
@api.returns('self', lambda value: value.id)
def create(self, vals):
    pre_create.send(sender=self, values=vals)
    res = super_create(self, vals)
    post_create.safe_send(sender=self, result=res, values=vals)
    return res


@api.multi
def write(self, vals):
    pre_write.send(self, values=vals)
    res = super_write(self, vals)
    post_write.safe_send(self, result=res, values=vals)
    return res


@api.multi
def unlink(self):
    pre_unlink.send(self)
    res = super_unlink(self)
    post_unlink.safe_send(self, result=res)
    return res


models.Model.fields_view_get = fields_view_get
models.BaseModel.create = create
models.BaseModel.write = write
models.BaseModel.unlink = unlink
