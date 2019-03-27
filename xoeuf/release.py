#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
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
    except Exception:
        return None


VERSION = '0.58.0'
RELEASE_TAG = dev_tag_installed() or ''
