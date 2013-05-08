# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoeuf.tween
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# @created: 1 mai 2013

'''Different mediators, each one acting as a link between Open Object Services
(osv) and client applications or libraries that needs to access OpenERP
databases.


Maybe only two "tweens" are needed:

 * A local one that uses directly the database through Open Object API.

 * A XML-RPC connector that expose the same interface and capabilities.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)
