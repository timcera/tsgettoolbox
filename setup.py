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
    sys.exit()

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

version = open("VERSION").readline().strip()

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
    'odo',
    'owslib',
    'tstoolbox >= 13.37.19.18',
    'requests',
    'zeep',
    'ulmo',
    'networkx < 2.0',
]


setup(name='tsgettoolbox',
      version=version,
      description="Will get time series from different sources on the internet.",
      long_description=README,
      classifiers=['Environment :: Console',
                   'Intended Audience :: Developers',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   ],
      keywords='time_series uri url web_services rest',
      author='Tim Cera, P.E.',
      author_email='tim@cerazone.net',
      url='http://timcera.bitbucket.io/tsgettoolbox/docsrc/index.html',
      packages=['tsgettoolbox',
                'tsgettoolbox/services',
                'tsgettoolbox/services/lcra',
                'tsgettoolbox/services/ncdc',
                'tsgettoolbox/services/usace',
                'tsgettoolbox/services/usgs',
                ],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      entry_points={
          'console_scripts':
              ['tsgettoolbox=tsgettoolbox.tsgettoolbox:main']
      },
      test_suite='tests',
      )
