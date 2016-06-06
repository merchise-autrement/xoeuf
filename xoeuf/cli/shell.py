# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoeuf.cli.shell
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise and Contributors
# Copyright (c) 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2014-05-02


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)


from . import Command
from xoeuf.api import contextual


class Base(object):
    @contextual
    def run(self, argv=None):
        self.invalidate_logging()
        from IPython import start_ipython
        start_ipython(argv=argv)


# The following commands is shadowed by the Odoo 9's shell.  So we create an
# alias ishell.
class Shell(Base, Command):
    pass


class IShell(Base, Command):
    command_cli_name = 'ishell'
