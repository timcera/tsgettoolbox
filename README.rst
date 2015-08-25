.. image:: https://travis-ci.org/timcera/tsgettoolbox.svg?branch=master
    :target: https://travis-ci.org/timcera/tsgettoolbox
    :height: 20

.. image:: https://coveralls.io/repos/timcera/tsgettoolbox/badge.png?branch=master
    :target: https://coveralls.io/r/timcera/tsgettoolbox?branch=master
    :height: 20

.. image:: https://img.shields.io/pypi/v/tsgettoolbox.svg
    :alt: Latest release
    :target: https://pypi.python.org/pypi/tsgettoolbox

.. image:: https://img.shields.io/pypi/dm/tsgettoolbox.svg
    :alt: PyPI downloads count
    :target: https://pypi.python.org/pypi/tsgettoolbox

.. image:: http://img.shields.io/badge/license-BSD-lightgrey.svg
    :alt: tsgettoolbox license
    :target: https://pypi.python.org/pypi/tsgettoolbox/

TSgettoolbox - Quick Guide
==========================
The 'tsgettoolbox' is a Python script and library to get time-series data from
different web services.  The tsgettoolbox will work with Python 2.6+ and 3.0+.

Documentation
-------------
Reference documentation is at http://pythonhosted.org/tsgettoolbox/

Installation
------------
At the command line::

    $ pip install tsgettoolbox
    # OR
    $ easy_install tsgettoolbox

Or, if you have virtualenvwrapper installed::

    $ mkvirtualenv tsgettoolbox
    $ pip install tsgettoolbox

Or, if you use conda::

    $ conda install -c timcera tsgettoolbox

Usage - Command Line
--------------------
Just run 'tsgettoolbox --help' to get a list of subcommands.  To get detailed
help for a particular sub-command, for instance 'coops', type 'tsgettoolbox
coops --help'.

    coops
                Download data from Center for Operational Oceanographic
                Products and Services (CO-OPS). Detailed documentation about
                the National Ocean Service CO-OPS web services is at
                http://tidesandcurrents.noaa.gov/api/

    nwis
                Download time-series from the USGS National Water Information
                Service (NWIS). There are three main NWIS databases. The
                'tsgettoolbox' can currently pull from the Instantaneous Value
                database (--database-iv) for sub-daily interval data starting
                in 2007, and the Daily Values database (--database=dv).
                Detailed documnetation is available at
                http://waterdata.usgs.gov/nwis

    daymet
                Download data from the Daymet dataset created by the Oak Ridge
                National Laboratory. Detailed documentation is at
                http://daymet.ornl.gov/

    ldas
                Download data from the Land Data Assimillation Service (LDAS).
                Two projects are available, the National LDAS (0.125x0.125
                degree hourly) and the Global LDAS (0.25x0.25 degree 3 hourly).

    forecast_io Download data from http://forecast.io Detailed documentation
                about the Forecast.io service is at
                https://developer.forecast.io/docs/v2 You have to get an API
                key from https://developer.forecast.io/

Usage - Python Library
----------------------
To use the tsgettoolbox in a project::

	from tsgettoolbox import tsgettoolbox

Refer to the API Documentation at http://pythonhosted.org/tsgettoolbox/

Development
~~~~~~~~~~~
Development is managed on bitbucket at
https://bitbucket.org/timcera/tsgettoolbox/overview.
