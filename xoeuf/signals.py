#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoeuf.signals
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-12-19

'''Signals.

Caveats:

- Receivers must ensure to be registered on every thread/process.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from openerp import api, models
from xoutil import logger


def _make_id(target):
    if hasattr(target, '__func__'):
        return (id(target.__self__), id(target.__func__))
    return id(target)


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

    def connect(self, receiver, sender=None):
        """Connect receiver to sender for signal.

        :param receiver: A function or an instance method which is to receive
                signals.  Receivers must be hashable objects and must be able
                to accept keyword arguments.

        :param sender: The sender(s) to which the receiver should
                respond. Must either a model name, list of model names or None
                to receive events from any sender.

        :return: None

        """
        if not isinstance(sender, (list, tuple)):
            sender = [sender]
        for s in sender:
            lookup_key = (_make_id(receiver), s)
            if not any(lookup_key == r_key for r_key, _ in self.receivers):
                self.receivers.append((lookup_key, receiver))

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

    def safe_send(self, sender, **kwargs):
        """Send signal from sender to all connected receivers catching errors.

        :param sender: The sender of the signal either a model or None.
        :param kwargs: Named arguments which will be passed to receivers.
        :return: Returns a list of tuple pairs [(receiver, response), ... ].

        If any receiver raises an error (specifically any subclass of
        Exception), the error instance is returned as the result for that
        receiver.
        """
        responses = []
        if not self.receivers:
            return responses
        for receiver in self._live_receivers(sender):
            try:
                response = receiver(sender, signal=self, **kwargs)
            except Exception as err:
                logger.exception(err)
                responses.append((receiver, err))
            else:
                responses.append((receiver, response))
        return responses

    def _live_receivers(self, sender):
        """Filter sequence of receivers to get resolved, live receivers.

        This checks for weak references and resolves them, then returning only
        live receivers.

        """
        senderkey = getattr(sender, '_name', None)
        receivers = []
        for (receiverkey, r_senderkey), receiver in self.receivers:
            if not r_senderkey or r_senderkey == senderkey:
                receivers.append(receiver)
        return receivers


def receiver(signal, **kwargs):
    """A decorator for connecting receivers to signals.

    Used by passing in the signal (or list of signals) and keyword arguments
    to connect::

        @receiver(post_save, sender=MyModel)
        def signal_receiver(sender, **kwargs):
            ...

        @receiver([post_save, post_delete], sender=MyModel)
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


# **************SIGNALS DECLARATION****************
pre_fields_view_get = Signal('fields_view_get')
post_fields_view_get = Signal('fields_view_get')

pre_create = Signal('create', '''
Signal sent when the 'create' method is to be invoked.

Signature for handlers:

:param sender: The recordset where the 'create' was called.

:keyword values: The values passed to 'create'.

''')

post_create = Signal('create', '''
Signal sent when the 'create' method has finished but before data is committed
to the DB.

Signature for handlers:

:param sender: The recordset where the 'create' was called.

:keyword result: The result of the call to 'create'.
:keyword values: The values passed to 'create'.
''')

pre_write = Signal('write')
post_write = Signal('write')

pre_unlink = Signal('unlink')
post_unlink = Signal('unlink')

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
    pre_fields_view_get.safe_send(sender=self, **kwargs)
    result = super(models.Model, self).fields_view_get(**kwargs)
    post_fields_view_get.safe_send(sender=self, result=result, **kwargs)
    return result


@api.model
@api.returns('self', lambda value: value.id)
def create(self, vals):
    pre_create.safe_send(sender=self, values=vals)
    res = super_create(self, vals)
    post_create.safe_send(sender=self, result=res, values=vals)
    return res


@api.multi
def write(self, vals):
    pre_write.send(self, values=vals)
    res = super_write(self, vals)
    post_write.send(self, result=res, values=vals)
    return res


@api.multi
def unlink(self):
    pre_unlink.send(self)
    res = super_unlink(self)
    post_unlink.send(self, result=res)
    return res


models.Model.fields_view_get = fields_view_get
models.BaseModel.create = create
models.BaseModel.write = write
models.BaseModel.unlink = unlink
