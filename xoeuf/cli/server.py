#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoeuf.cli.app
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 7 mai 2013

'''An example of an application that use "xoeuf.cli"

It behaves similar to "openerp-server"script.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)

from xoeuf.cli import DEFAULT_COMMAND
from xoutil.cli.app import main

__docstring_format__ = 'rst'
__author__ = 'med'


if __name__ == "__main__":
    main(default=DEFAULT_COMMAND)
