#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoeuf.release
# ---------------------------------------------------------------------
# Copyright (c) 2013-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#


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


VERSION = '0.7.1'
RELEASE_TAG = dev_tag_installed() or ''
