#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Wraps write operations.

Usage::

  @write_wrapper()
  def wrapper(sender, **kwargs):
      yield

The wrapper must yield exactly once.  All the code above the 'yield' will be
executed before the actual write.  All the code below the 'yield' will be
executed after the write.  You can have as many wrappers as you want.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


import logging
try:
    from openerp import api, models
except ImportError:
    from odoo import api, models


logger = logging.getLogger(__name__)
del logging


class WriteWrapperRegistry(object):
    def __init__(self):
        self.wrappers = []

    def __call__(self, sender=None, require_registry=True):
        def decorator(func):
            return self.connect(func, sender=sender,
                                require_registry=require_registry)
        return decorator

    def connect(self, wrapper, sender=None, require_registry=True):
        '''Install a wrapper around a write operation.

        :param receiver: A function or an instance method that complies with
                the wrapper protocol explained below.

        :param sender: The sender(s) to which the wrapper should respond. Must
                either a model name, list of model names or None to wrap
                writes from any sender.

        :param require_registry: If True the receiver will only be called if a
               the actual `sender` of the signal has a ready DB registry.

        :return: wrapper

        '''
        if not isinstance(sender, (list, tuple)):
            sender = [sender]
        for s in sender:
            lookup_key = (_make_id(wrapper), _make_model_id(s))
            if not any(lookup_key == r_key for r_key, _ in self.wrappers):
                self.wrappers.append(
                    (lookup_key,
                     WriteWrapper(wrapper, sender=s,
                                  require_registry=require_registry))
                )
        return wrapper

    def perform_write(self, write, sender, *args, **kwargs):
        livewrappers = self.live_wrappers(sender)
        wrappers = []
        if args:
            values = args[0]
        else:
            values = kwargs['vals']
        for wrapper in livewrappers:
            try:
                w = wrapper(sender, values=values)
                try:
                    next(w)
                except StopIteration:
                    logger.error(
                        'Wrapper %s failed to yield once',
                        wrapper
                    )
                else:
                    wrappers.append(w)
            except Exception:
                logger.exception('Unexpected error in wrapper')
        result = write(sender, *args, **kwargs)
        for wrapper in wrappers:
            try:
                wrapper.send((sender, dict(values=values)))
                logger.error('Wrapper %s failed to yield only once')
            except StopIteration:
                pass
            except Exception:
                logger.exception('Unexpected error in wrapper')
        return result

    def live_wrappers(self, sender):
        if isinstance(sender, models.Model):
            registry_ready = sender.pool.ready
        else:
            registry_ready = False
        wrappers = []
        for (key, r_senderkey), wrapper in self.wrappers:
            if wrapper.is_installed(sender) and wrapper.matches(sender):
                if registry_ready or not wrapper.require_registry:
                    logger.debug(
                        'Accepting wrapper %s as live',
                        wrapper,
                        extra=dict(
                            registry_ready=registry_ready,
                            registry_required=wrapper.require_registry,
                            r_senderkey=r_senderkey,
                            senderkey=key,
                        )
                    )
                    wrappers.append(wrapper)
        return wrappers


class WriteWrapper(object):
    def __init__(self, func, sender=None, require_registry=True):
        self.func = func
        self.sender = sender
        self.require_registry = require_registry

    def __call__(self, sender, **kwargs):
        return self.func(sender, **kwargs)

    def matches(self, sender):
        key = _make_model_id(sender)
        return not self.sender or key == _make_model_id(self.sender)

    def is_installed(self, sender):
        '''True if this wrapper is installed in the same DB as `sender`.

        '''
        from xoeuf.modules import get_object_module
        module = get_object_module(self.func, typed=True)
        env = getattr(sender, 'env', None)
        if module and env:
            mm = env['ir.module.module']
            query = [('state', '=', 'installed'), ('name', '=', module)]
            return bool(mm.search(query))
        else:
            return True


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


def _issubcls(which, Class):
    return isinstance(which, type) and issubclass(which, Class)


def _make_id(target):
    if hasattr(target, '__func__'):
        return (id(target.__self__), id(target.__func__))
    return id(target)


write_wrapper = WriteWrapperRegistry()
_model_write = models.BaseModel.write


@api.multi
def write(self, vals):
    return write_wrapper.perform_write(_model_write, self, vals)


models.BaseModel.write = write
