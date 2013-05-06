#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoeuf.cli
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement
# All rights reserved.
#
# Created on 26 avr. 2013

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)


from openerp.cli import Command, commands


def get_command_class(command, full=False):
    '''
    '''
    cmd_class = commands.get(command, None)
    if not cmd_class or full:
        import sys
        from openerp.modules.module import get_modules
        modules = get_modules()
        i = 0
        while (not cmd_class or full) and i < len(modules):
            module_name = str('openerp.addons.' + modules[i])
            i += 1
            if module_name not in sys.modules:
                try:
                    from importlib import import_module
                    import_module(module_name)
                except Exception as _error:
                    pass
                    # TODO: Use deprecated OpenERP feature including all paths
                    # print('ERROR:', type(_error), _error, file=sys.stderr)
                cmd_class = commands.get(command, None)
    return cmd_class


class Help(Command):
    '''Show all commands

    Redefine OpenERP "help" command.

    '''
    def run(self, args):
        print('Available commands:', end='\n\n')
        for cmd in commands:
            cmd_class = commands[cmd]
            doc = self._strip_doc(cmd_class.__doc__)
            if not doc:
                doc = self._strip_doc(cmd_class.run.__doc__)
            if not doc:
                import sys
                mod_name = cmd_class.__module__
                module = sys.modules.get(mod_name, None)
                if module:
                    doc = self._strip_doc(module.__doc__)
                    doc = '"%s"' % (doc if doc else mod_name)
                else:
                    doc = '"%s"' % mod_name
            print("\t%s:\t%s" % (cmd, doc))

    @staticmethod
    def _strip_doc(doc):
        if doc:
            doc = str('%s' % doc).strip()
            return str(doc.strip().split('\n')[0].strip('''.'" \t\n\r'''))
        else:
            return ''


def main(**kwargs):
    '''
    Execute a server command, it can be given as :param:`command` or as the
    first program argument.

    Only one of both alternatives is possible: is the command is given as the
    parameter of this function, then the program arguments can't contain it and
    vice-versa.

    Additional options can be given in :param:`kwargs`, they overwrite the
    default options obtained, first from a configuration file, then from the
    remainder program arguments.

    '''
    from xoeuf.tools.config import options, DEFAULT_COMMAND
    options.update(**kwargs)
    command = options.command or DEFAULT_COMMAND
    import_all = command == Help.__name__.lower()
    cmd_class = get_command_class(command, full=import_all)
    if cmd_class:
        cmd = cmd_class()
        return cmd.run(options.command_args)
    else:
        raise KeyError(command)


if __name__ == "__main__":
    main()
