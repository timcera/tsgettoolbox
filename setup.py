#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    os.system('python setup.py upload_docs')
    sys.exit()

readme = open('README.rst').read()

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
    'ulmo >= 0.2.4',
    'baker >= 1.3',
    'pandas >= 0.12',
    'voluptuous',
    'six',
]


setup(name='tsgettoolbox',
      version=open("VERSION").readline().strip(),
      description="Will get time series from different sources on the internet.",
      long_description=readme,
      classifiers=['Environment :: Console',
                   'Intended Audience :: Developers',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.3',
                   ],
      keywords='time_series uri url',
      author='Tim Cera, P.E.',
      author_email='tim@cerazone.net',
      url='',
      license='GPL2',
      packages=['tsgettoolbox'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      entry_points={
          'console_scripts':
              ['tsgettoolbox=tsgettoolbox.tsgettoolbox:main']
      }
      )
