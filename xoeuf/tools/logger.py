#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoeuf.tools.logger
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
