#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoeuf.release
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise and Contributors
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-05-05


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)


def dev_tag_installed():
    import re
    import pkg_resources
    tag_start_regex = re.compile(r'[^\d\.]')
    try:
        dist = pkg_resources.get_distribution('xoeuf')
        version = dist.version
        match = tag_start_regex.search(version)
        if match:
            return version[match.start():]
        else:
            return None
    except:
        return None


VERSION = '0.6.5'
RELEASE_TAG = dev_tag_installed() or ''
