#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
try:
    from ._version import get_version

    VERSION = get_version()
except:  # noqa
    from ._version import get_versions

    VERSION = get_versions()["version"]

RELEASE_TAG = ""
