#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoeuf.cli.app
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise and Contributors
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 7 mai 2013

'''An example of an application that use :mod:`xoeuf.cli`.

It behaves similar to "openerp-server" script. This module does not provide any
external facilities, but uses :func:`xoutil:xoutil.cli.app.main` to run the
OpenERP server. Usage::

  $ python server.py [options...]

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)


def server():
    from xoeuf.cli import DEFAULT_COMMAND
    from xoutil.cli.app import main
    main(default=DEFAULT_COMMAND)


if __name__ == "__main__":
    server()
