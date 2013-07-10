#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from setuptools import setup
from __version__ import version

setup(name='smartcp',
  version=version,
  description='Smart Copy Utility',
  author='Benoît Legat',
  author_email='benoit.legat@gmail.com',
  url='http://www.github.com/blegat/smartcp',
  long_description = """Smart copy utility useful for automating
  copy to custom source and destination depending on parameters.""",
  license = 'GPLv3+',
  install_requires = [
    'PyYAML',
    ],
  py_modules=['smartcp'],
  #scripts=['smartcp.py'],
  entry_points=dict(console_scripts=['smartcp=smartcp:main', 
    'smartcp-%s=smartcp:main' % sys.version[:3]]),
  #entry_points=dict(console_scripts=['smartcp=smartcp:main', 
  #  'smartcp-%s=smartcp:main' % sys.version[:3]]),
  classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Topic :: Utilities',
    ],
)
