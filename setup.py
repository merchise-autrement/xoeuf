#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# setup
# ---------------------------------------------------------------------
# Copyright (c) 2013-2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2013-05-05


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)
                        # XXX: Don't put absolute imports in setup.py

import sys, os
from setuptools import setup, find_packages

# Import the version from the release module
project_name = 'xoeuf'
_current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(_current_dir, project_name))
from release import VERSION as version


def safe_read(*paths):
    fname = os.path.join(_current_dir, *paths)
    try:
        with open(fname, 'r') as fh:
            return fh.read()
    except (IOError, OSError):
        return ''


setup(name=project_name,
      version=version,
      description="Basic utilities for OpenERP Open Object Services",
      long_description=safe_read('docs', 'readme.txt'),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          "Programming Language :: Python",
          "Intended Audience :: Developers",
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Development Status :: 4 - Beta',
      ],
      keywords='openerp open-object server library',
      author='Merchise Autrement',
      author_email='',
      url='http://www.merchise.org/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'xoutil>=1.6.6,<1.7',
          'six',
          'ipython',
          'raven>=5.2.0',
          'raven-sanitize-openerp',
      ],
      entry_points="""
      [console_scripts]
      xoeuf = xoeuf.cli.server:server
      xoeuf_mailgate = xoeuf.cli.mailgate:main
      """)
