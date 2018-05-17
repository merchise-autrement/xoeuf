#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

# This is the implementation of the signals.  The 'signals' module remains the
# API but we're porting this to 'openerp.signals'.

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

import logging
logger = logging.getLogger(__name__)
del logging

from xoeuf.odoo import api, models
from xoutil.objects import temp_attributes


class HookDefinition(object):
    def __init__(self, action=None, doc=None):
        self.hooks = []
        self.action = action
        self.__doc__ = doc

    def __repr__(self):
        return '<Signal(%r)>' % self.action

    def connect(self, hook, sender=None, require_registry=True,
                framework=False):
        """Connect hook.

        :param hook: A function or an instance method which is to receive
                handle the hook.  Hooks must be hashable objects and must be
                able to accept keyword arguments.

        :param sender: The sender(s) to which the receiver should
                respond. Must either a model name, list of model names or None
                to receive events from any sender.

        :param require_registry: If True the receiver will only be called if a
               the actual `sender` of the signal has a ready DB registry.

        :keyword framework: Set to True to make this a `framework-level hook
                            <FrameworkHook>`:class:.

        :return: receiver

        """
        if not isinstance(sender, (list, tuple)):
            sender = [sender]
        HookClass = Hook if not framework else FrameworkHook
        for s in sender:
            lookup_key = (_make_id(hook), _make_model_id(s))
            if not any(lookup_key == r_key for r_key, _ in self.hooks):
                self.hooks.append(
                    (lookup_key,
                     HookClass(hook, sender=s,
                               require_registry=require_registry))
                )
        return hook

    def disconnect(self, hook=None, sender=None):
        """Disconnect hook from sender.

        :param hook: The registered hook to disconnect.

        :param sender: The registered sender to disconnect

        """
        key = (_make_id(hook), _make_model_id(sender)), hook
        if key in self.hooks:
            self.hooks.remove(key)

    def has_listeners(self, sender=None):
        return bool(self.live_hooks(sender))

    def live_hooks(self, sender):
        """Filter sequence of hooks to get resolved (live hooks).

        Live hook are defined as those that are installed in the DB and apply
        to the given sender.  Framework-level hooks are always live.

        """
        if isinstance(sender, models.Model):
            registry_ready = sender.pool.ready
        else:
            registry_ready = False
        result = []
        for _, hook in self.hooks:
            if hook.is_installed(sender) and hook.matches(sender):
                if registry_ready or not hook.require_registry:
                    logger.debug(
                        'Accepting hook %s as live',
                        hook,
                        extra=dict(
                            registry_ready=registry_ready,
                            registry_required=hook.require_registry,
                        )
                    )
                    result.append(hook)
        return result


class Signal(HookDefinition):
    """Base class for all signals

    """
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
        if not self.hooks:
            return responses
        for hook in self.live_hooks(sender):
            response = hook(sender, self, **kwargs)
            responses.append((hook, response))
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
        from celery.exceptions import SoftTimeLimitExceeded
        responses = []
        if thrown and not isinstance(thrown, (list, tuple)):
            thrown = (thrown, )
        if not self.hooks:
            return responses
        for hook in self.live_hooks(sender):
            try:
                response = hook(sender, self, **kwargs)
            except SoftTimeLimitExceeded:
                raise
            except catched as err:
                if thrown and isinstance(err, thrown):
                    # Don't log: I expect you'll log where you actually catch
                    # it.
                    raise
                else:
                    logger.exception(err)
                    responses.append((hook, err))
            else:
                responses.append((hook, response))
        return responses


class Wrapping(HookDefinition):
    def perform(self, method, sender, *args, **kwargs):
        livewrappers = self.live_hooks(sender)
        wrappers = []
        for wrapper in livewrappers:
            try:
                w = wrapper(sender, self, *args, **kwargs)
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
        result = method(sender, *args, **kwargs)
        for wrapper in wrappers:
            try:
                wrapper.send(dict(result=result))
                logger.error('Wrapper %s failed to yield only once')
            except StopIteration:
                pass
            except Exception:
                logger.exception('Unexpected error in wrapper')
        return result


class Hook(object):
    '''Wraps a hook function, so that we can store some metadata.'''
    def __init__(self, func, **kwargs):
        from xoutil.objects import smart_copy
        hash(func)  # Fail if func is not hashable
        self.func = func
        smart_copy(
            kwargs,
            self.__dict__,
            defaults={'require_registry': True, 'sender': None}
        )

    def __repr__(self):
        return '<Hook for %r>' % self.func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    # So that the original receiver compares equal to this wrapper.  This
    # avoids having the same function being registered twice.
    def __hash__(self):
        return hash(self.func)

    def __eq__(self, other):
        return self.func == other

    def matches(self, sender):
        key = _make_model_id(sender)
        return not self.sender or key == _make_model_id(self.sender)

    def is_installed(self, sender):
        '''Check whether this receiver is installed in the DB of `sender`.

        If the sender does not have an 'env' attribute it will considered
        installed as well (this is for dispatching outside the Odoo model
        framework.)

        '''
        from xoeuf.modules import get_object_module
        module = get_object_module(self.func, typed=True)
        env = getattr(sender, 'env', None)
        if module and env:
            mm = env['ir.module.module'].sudo()
            query = [('state', '=', 'installed'), ('name', '=', module)]
            with _no_signalling(pre_search), _no_signalling(post_search):
                return bool(mm.search(query))
        else:
            return True


class FrameworkHook(Hook):
    '''A hook that is defined in a framework-level module.

    Framework-level hooks are always considered installed in any DB.  So you
    should be careful no requiring addon-level stuff.

    '''
    def is_installed(self, sender):
        '''Check whether this receiver is installed in the DB of `sender`.'''
        return True


def receiver(signal, **kwargs):
    """A decorator for connecting receivers to signals.

    :param signal: Either a single signal or a list of signals.

    :keyword require_registry: If set to True the receiver will only be called
             if the Odoo DB registry is ready.

    :keyword framework: Set to True to make this a `framework-level receiver
                        <FrameworkHook>`:class:.

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


def wrapper(wrapping, **kwargs):
    """A decorator for connecting wrappers.

    :param wrapping: Either a single wrapping or a list of them.

    :keyword require_registry: If set to True the wrapper will only be called
             if the Odoo DB registry is ready.

    :keyword framework: Set to True to make this a `framework-level wrapper
                        <FrameworkHookData>`:class:.

    Example::

        @wrapper(write_wrapper, sender='my.model')
        def _do_what_i_mean(sender, **kwargs):
            yield

    Wrappers must yield exactly once.  The code before the ``yield`` runs
    before the original method.  Any errors in the code of the wrapper are
    logged and ignored: the original method always runs.

    Standard wrappers wrap the pre/post signals.  So wrappers may be affected
    by the effects in post signals.

    """
    return receiver(wrapping, **kwargs)


def _no_signalling(signal):
    '''Context manager that temporarily stop the signal from being called.

    Basically, we disconnect all receivers from `signal` within the scope of
    the context manager.

    '''
    return temp_attributes(signal, {'hooks': []})


def mock_replace(hook, func, **replacement_attrs):
    '''Mock a hook.

    Example::

       with mock_replace(post_create, receiver) as mock:
          # do things that should trigger post_create
          assert mock.called

    '''
    import contextlib
    from xoutil.symbols import Undefined
    try:
        from unittest.mock import MagicMock
    except ImportError:
        from mock import MagicMock

    @contextlib.contextmanager
    def _hidden_patcher():
        mock = MagicMock(func, **replacement_attrs)
        registry = hook.hooks
        pos = find(func, registry, extract=snd)
        if pos is not Undefined:
            _, receiver_holder = registry[pos]
            previous_receiver = receiver_holder.func
            receiver_holder.func = mock
            previous_is_installed = receiver_holder.is_installed
            receiver_holder.is_installed = is_installed
        else:
            receiver_holder = None
        try:
            yield mock
        finally:
            if receiver_holder is not None:
                receiver_holder.func = previous_receiver
                receiver_holder.is_installed = previous_is_installed

    def snd(pair):
        _, res = pair
        return res

    def find(what, l, extract=None):
        if not extract:
            extract = lambda x: x  # noqa: E731
        ll = [extract(x) for x in l]
        try:
            return ll.index(what)
        except ValueError:
            return Undefined

    def is_installed(sender):
        '''Mocked is installed'''
        from xoeuf.modules import get_object_module
        module = get_object_module(func, typed=True)
        env = getattr(sender, 'env', None)
        if module and env:
            mm = env['ir.module.module'].sudo()
            query = [('state', '=', 'installed'), ('name', '=', module)]
            with _no_signalling(pre_search), _no_signalling(post_search):
                return bool(mm.search(query))
        else:
            return True

    return _hidden_patcher()


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


# **************SIGNALS DECLARATION****************
pre_fields_view_get = Signal('pre_fields_view_get')
post_fields_view_get = Signal('post_fields_view_get')

pre_search = Signal('pre_search', '''
Signal sent when the 'search' method is to be invoked.

Arguments:

:param sender: The recordset where the 'search' was called.

:keyword query: The domain (argument `args` in Odoo's search method).
                This will be `list`:class: that can be modified in place, to
                customize the search.  But notice that the order in which the
                receivers are called is not defined.

:keyword pos_args:  The rest of the positional arguments (if any).

:keyword kw_args: The rest of the keyword arguments (if any).

''')


post_search = Signal('post_search', '''
Signal sent after the 'search' method was invoked.

Arguments:

:param sender: The recordset where the 'search' was called.

:keyword query: The domain (argument `args` in Odoo's search method).
                This will be `list`:class: that can be modified in place, to
                customize the search.

:keyword pos_args:  The rest of the positional arguments (if any).

:keyword kw_args: The rest of the keyword arguments (if any).

:keyword result: The result of the actual 'search'.

''')


pre_create = Signal('pre_create', '''
Signal sent when the 'create' method is to be invoked.

If a receiver raises an error the create is aborted, and post_create won't be
issued.  The error is propagated.

Arguments:

:param sender: The recordset where the 'create' was called.

:keyword values: The values passed to 'create'.

''')

post_create = Signal('post_create', '''
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

pre_write = Signal('pre_write', '''
Signal sent when the 'write' method of model is to be invoked.

If a receiver raises an error the write is aborted and 'post_write' is not
sent.  The error is propagated.

Arguments:

:param sender: The recordset sending the signal.

:keyword values: The values passed to the write method.

''')
post_write = Signal('post_write', '''
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

pre_unlink = Signal('pre_unlink', '''
Signal sent when the 'unlink' method of model is to be invoked.

If a receiver raises an error unlink is aborted and 'post_unlink' is not
called.  The error is propagated.

Arguments:

:param sender: The recordset sending the signal.

''')

post_unlink = Signal('post_unlink', '''
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
super_search = models.BaseModel.search


@api.model
def _api_model_fields_view_get(self, view_id=None, view_type='form',
                               toolbar=False, submenu=False):
    kwargs = dict(
        view_id=view_id,
        view_type=view_type,
        toolbar=toolbar,
        submenu=submenu
    )
    pre_fields_view_get.send(sender=self, **kwargs)
    result = super_fields_view_get(self, **kwargs)
    post_fields_view_get.safe_send(sender=self, result=result, **kwargs)
    return result


if getattr(super_fields_view_get, '_api', None) is api.cr_uid_context:
    @api.cr_uid_context
    def _fvg_for_signals(self, cr, uid, view_id=None, view_type='form',
                         context=None, toolbar=False, submenu=False):
        from xoeuf import api
        env = api.Environment(cr, uid, context or {})
        self = env[self._name]
        return _api_model_fields_view_get(
            self,
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu
        )
else:
    _fvg_for_signals = _api_model_fields_view_get


@api.model
@api.returns('self', lambda value: value.id if value else value)
def _create_for_signals(self, vals):
    pre_create.send(sender=self, values=vals)
    res = super_create(self, vals)
    post_create.safe_send(sender=self, result=res, values=vals)
    return res


@api.multi
def _write_for_signals(self, vals):
    pre_write.send(self, values=vals)
    res = super_write(self, vals)
    post_write.safe_send(self, result=res, values=vals)
    return res


@api.multi
def _unlink_for_signals(self):
    pre_unlink.send(self)
    res = super_unlink(self)
    post_unlink.safe_send(self, result=res)
    return res


write_wrapper = Wrapping('write_wrapper', '''\
Wraps the `write` method.

''')


@api.multi
def _write_for_wrappers(self, vals):
    return write_wrapper.perform(_write_for_signals, self, vals)


@api.model
@api.returns(*super_search._returns)
def _search_for_signals(self, args, *pos_args, **kw_args):
    query = list(args)
    pre_search.send(self, query=query, pos_args=pos_args, kw_args=kw_args)
    result = super_search(self, query, *pos_args, **kw_args)
    post_search.safe_send(self, query=query, pos_args=pos_args, kw_args=kw_args, result=result)
    return result


models.Model.fields_view_get = _fvg_for_signals
models.BaseModel.create = _create_for_signals
models.BaseModel.unlink = _unlink_for_signals
models.BaseModel.write = _write_for_wrappers
models.BaseModel.search = _search_for_signals
