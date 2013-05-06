#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoeuf.tools.config
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License (GPL) as published by the
# Free Software Foundation;  either version 2  of  the  License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
# Created on 20/04/2013

'''Xœuf Configuration Service.

Define the class :class:`OptionsManager` which is a singleton that wraps
"openerp.tools.config", it's instanced automatically at the end of this
module.

If Xœuf Services are called from an application with arguments, they are
parsed and loaded the first time this module is used.

If a command is invoked, it's looked in all OpenERP configured modules (addons)
and its arguments are parsed and it's executed.

You can update or load all options by calling in any time either the method
:method:`load` or the method :method:`update`.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)

from collections import MutableMapping
from xoutil.names import strlist as _strs


__docstring_format__ = 'rst'
__author__ = 'med'


DEFAULT_COMMAND = str('server')


# TODO: OpenERP must migrate to use "argparse" instead "optparse".
class OptionsManager(MutableMapping):
    '''A singleton that wraps "openerp.tools.config".

    Initialize the server options by load configuration file
    (:param:`config_file`) and extra variables given in :param:`options`.

    Xœuf server options wraps base "openerp.tools.config".

    First time, command line arguments are parsed; the method :method:`load`
    can be used to apply additional options.

    '''
    __slots__ = _strs('_wrapped')

    def __new__(cls):
        self = getattr(cls, '__singleton__', False)
        if not self:
            self = super(OptionsManager, cls).__new__(cls)
            cls.__singleton__ = self
            from openerp.tools import config
            self._wrapped = config
            self._parse_config()
        return self

    @property
    def misc(self):
        return self._wrapped.misc

    def __dir__(self):
        return (list(self._wrapped.options) + list(self.__dict__) +
                list(type(self).__dict__))

    def __len__(self):
        return len(self._wrapped.options)

    def __iter__(self):
        return iter(self._wrapped.options)

    def __getitem__(self, key):
        if '.' in key:
            section, option = key.split('.')
            return self._wrapped.misc[section][option]
        else:
            return self._wrapped[key]
    __getattr__ = __getitem__

    def __setitem__(self, key, value):
        if value in ('True', 'true'):
            value = True
        elif value in ('False', 'false'):
            value = False
        elif value == 'None':
            value = None
        if '.' in key:
            section, option = key.split('.')
            self._wrapped.misc[section][str(option)] = value
        else:
            self._wrapped[str(key)] = value

    def __setattr__(self, name, value):
        if name in type(self).__slots__:
            super(OptionsManager, self).__setattr__(name, value)
        else:
            self[name] = value

    def __delitem__(self, key):
        raise NotImplementedError("Can't delete options members.")

    def load(self, config_file):
        '''Update options with the ones in a configuration file.'''
        if config_file:
            from xoutil.fs import normalize_path
            config_file = normalize_path(config_file)
        self._wrapped.config_file = config_file
        self._wrapped.load()

    def _parse_config(self):
        '''Intended to be called in constructor.'''
        PROGRAM_NAME = str('program_name')
        if PROGRAM_NAME not in self:      # command args parsed?
            import sys
            self[PROGRAM_NAME] = sys.argv[0]
            args = sys.argv[1:]
            # Isolate "addons-path" if exists
            i = 0
            while i < len(args) and not args[i].startswith('--addons-path='):
                i += 1
            addons_path = [args.pop(i)] if i < len(args) else []
            # Check for a command
            COMMAND = str('command')
            COMMAND_ARGS = str('command_args')
            if args and not args[0].startswith("-"):
                self._wrapped.parse_config(addons_path)
                command = args[0]
                args = args[1:]
            else:
                print('='*50, addons_path)
                self._wrapped.parse_config(args)
                command = None
            if command in (None, DEFAULT_COMMAND):
                args += addons_path
            self[COMMAND] = command
            self[COMMAND_ARGS] = args


options = OptionsManager()
