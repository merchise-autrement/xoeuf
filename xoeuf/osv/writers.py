# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoeuf.osv.writers
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise and Contributors
# Copyright (c) 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2014-03-18

'''Helpers to generate ``BaseModel.write`` commands.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


class _BaseWriter(object):
    '''Core of the function for `ORMWriter`:class: and `ORMCreator`:class:.

    .. warning:: Currently we don't support nested context managers.

    '''
    def __init__(self, obj, cr, uid, **kwargs):
        from xoutil.collections import StackedDict
        self.obj = obj
        self.cr = cr
        self.uid = uid
        self.kwargs = kwargs
        self._commands = StackedDict()
        self.result = None

    def _get_field(self, attrname):
        return self.obj._all_columns[attrname].column

    __getitem__ = _get_field

    def _is_many2many(self, attrname):
        from openerp.osv.fields import many2many
        return isinstance(self[attrname], many2many)

    def _is_one2many(self, attrname):
        from openerp.osv.fields import one2many
        return isinstance(self[attrname], one2many)

    @property
    def commands(self):
        '''The current stack of commands at the current level.

        Since commands could be nested, this will only return the
        top-of-the-stack commands.

        :rtype: dict

        '''
        # TODO: Deal with nested writers properly.
        return self._commands.peek()

    def __enter__(self):
        # Try to use xoutil 1.7 (i.e push_level) but fallback to push if
        # xoutil is older.
        push = getattr(self._commands, 'push_level', self._commands.push)
        push()
        return self

    def __exit__(self, ex_type, exc_value, exc_tb):
        raise NotImplemented

    def create(self, attrname, **values):
        '''Issues a command to create a newly related object with given `values` for
        the many2many/one2many column `attrname`.

        '''
        assert self._is_many2many(attrname) or self._is_one2many(attrname)
        from .orm import CREATE_RELATED
        cmds = self._commands.setdefault(attrname, [])
        cmds.append(CREATE_RELATED(**values))

    def update(self, *replacement, **values):
        '''Issues update commands.

        There are two possible signatures for this method:

        - Keywords only `attrname=value`.  This case is used mostly for
          "plain" columns.  If any `attrname` is a relation it must be a
          many2many, and value must be either None or a list of all related
          objects' ids.

        - Two positional arguments and several keyword arguments, like
          ``update(attrname, id, **values)``.  This is for updating the
          attributes of a single related object.  In this case `attrname` must
          be either a many2many or one2many column.

        '''
        from xoutil.types import is_collection
        from .orm import UPDATE_RELATED
        commands = self._commands
        if replacement:
            attrname, id = replacement
            assert self._is_many2many(attrname) or self._is_one2many(attrname)
            cmds = commands.setdefault(attrname, [])
            cmds.append(UPDATE_RELATED(id, **values))
        else:
            for attrname, val in values.items():
                if self._is_many2many(attrname):
                    if val is None:
                        self.forgetall(attrname)
                    elif is_collection(val):
                        self.replace(attrname, *tuple(val))
                    else:
                        raise TypeError("Malformed value '%s' for "
                                        "attribute %s" % (val, attrname))
                elif self._is_one2many(attrname):
                    raise TypeError("'update' does not allow one2many keyword"
                                    "arguments.")
                else:
                    commands[attrname] = val

    def remove(self, attrname, *ids):
        '''Issues several "remove related object" commands for the attribute
        named `attrname`.

        '''
        assert self._is_many2many(attrname) or self._is_one2many(attrname)
        from .orm import REMOVE_RELATED
        cmds = self._commands.setdefault(attrname, [])
        cmds.extend(REMOVE_RELATED(id) for id in ids)

    def forget(self, attrname, *ids):
        '''Issues several "forget related object" commands for the attribute
        named `attrname`.

        '''
        assert self._is_many2many(attrname)
        from .orm import FORGET_RELATED
        cmds = self._commands.setdefault(attrname, [])
        cmds.extend(FORGET_RELATED(id) for id in ids)

    def forgetall(self, attrname):
        '''Issues a "forget all related objects" command for the attribute
        named `attrname`.

        '''
        assert self._is_many2many(attrname)
        from .orm import UNLINKALL_RELATED
        cmds = self._commands.setdefault(attrname, [])
        cmds.append(UNLINKALL_RELATED())

    def replace(self, attrname, *ids):
        '''Issues a "replace related objects" command for the attribute named
        `attrname`.

        '''
        assert self._is_many2many(attrname)
        from .orm import REPLACEWITH_RELATED
        cmds = self._commands.setdefault(attrname, [])
        cmds.append(REPLACEWITH_RELATED(*ids))

    def add(self, attrname, *ids):
        '''Issues several "link to" commands to the attribute named
        `attrname`.

        '''
        from .orm import LINK_RELATED
        assert self._is_many2many(attrname)
        cmds = self._commands.setdefault(attrname, [])
        cmds.extend(LINK_RELATED(id) for id in ids)


class ORMWriter(_BaseWriter):
    '''A writer that issues a ``obj.write`` when exiting the context manager.

    Most likely you'll be using `xoeuf.osv.model_extensions.get_writer`:func:,
    but there are times when you need to build the commands without entering
    the context manager; in such cases you may get the command by retrieving
    the property `_BaseWriter.commands`:attr:.

    '''
    def __init__(self, obj, cr, uid, ids, **kwargs):
        super(ORMWriter, self).__init__(obj, cr, uid, **kwargs)
        self.ids = ids

    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type or exc_value:
            return False
        self.result = self.obj.write(self.cr, self.uid, self.ids,
                                     self.commands, **self.kwargs)


class ORMCreator(_BaseWriter):
    '''A writer that emits `create` at manager's exit.'''
    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type or exc_value:
            return False
        self.result = self.obj.create(self.cr, self.uid, self.commands,
                                      **self.kwargs)

    set = _BaseWriter.update
