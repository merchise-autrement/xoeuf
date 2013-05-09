#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoeuf.tools.logger
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 21 avr. 2013

'''Initialize the OpenERP logger, and provides a function to smartly get a
logger.

'''

from openerp.netsvc import init_logger


__docstring_format__ = 'rst'
__author__ = 'med'


DEFAULT_LOGGER_NAME = str('xoeuf')


def get_logger(name=None):
    '''If a `name` is given, is normally getter, otherwise look for the upper
    module name.

    '''
    from logging import getLogger
    if not name:
        import sys
        frame = sys._getframe(1)
        name = frame.f_globals.get('__name__', DEFAULT_LOGGER_NAME)
    return getLogger(str(name))


init_logger()
