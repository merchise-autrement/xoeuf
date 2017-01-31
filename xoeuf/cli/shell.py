# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoeuf.cli.shell
# ---------------------------------------------------------------------
# Copyright (c) 2014-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2014-05-02


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


from . import Command
from xoeuf.api import contextual
from xoutil.eight.types import new_class


class Base(object):
    # This Base is just here to have many 'shell' commands.  See aliases
    # below.  Odoo 9 includes its own 'shell' command, we the aliases to be
    # able to work with our shell.
    #
    # Needed the '@contextual' cause we don't inherit from Command.
    @contextual
    def run(self, argv=None):
        self.invalidate_logging()
        from IPython import start_ipython
        start_ipython(argv=argv)


for alias in ('shell', 'ishell', 'python', 'ipython'):
    class aliased(object):
        command_cli_name = alias
    new_class(alias, (aliased, Base, Command))
