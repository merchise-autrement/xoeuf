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
                        absolute_import as _py3_abs_import)

import sys
import os
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
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',  # noqa
          'Development Status :: 4 - Beta',
      ],
      keywords='openerp open-object server library'.split(),
      author='Merchise Autrement [~º/~]',
      author_email='',
      url='http://www.merchise.org/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'pytz',
          'decorator>=4.0,<4.2',
          'xoutil>=1.9.0,<2.0; python_version < "3.4"',
          'xoutil>=1.9.0,<2.1; python_version >= "3.4"',
          'ipython<6',
          'raven>=5.8.0',
          'raven-sanitize-openerp',
          'enum34; python_version < "3.4"',
          'celery>=4.1.0,<5',
          'typing;python_version<"3.5"',
      ],
      extra_requires={
          'odoo': [
              'odoo==10.0; python_version < "3.0"',
              'odoo>=11.0,<13.0; python_version >= "3.5"',
          ],
          'test': ['hypothesis>=3.7.0,<4', ],
      },
      entry_points="""
      [console_scripts]
      xoeuf = xoeuf.cli.server:server
      xoeuf_mailgate = xoeuf.cli.mailgate:main

      [xoeuf.addons]
      test_localized_dt = xoeuf.tests.test_localized_dt
      """)
