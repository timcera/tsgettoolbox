.. image:: https://travis-ci.org/timcera/tsgettoolbox.svg?branch=master
    :target: https://travis-ci.org/timcera/tsgettoolbox
    :height: 20

.. image:: https://coveralls.io/repos/timcera/tsgettoolbox/badge.png?branch=master
    :target: https://coveralls.io/r/timcera/tsgettoolbox?branch=master
    :height: 20

.. image:: https://img.shields.io/pypi/v/tsgettoolbox.svg
    :alt: Latest release
    :target: https://pypi.python.org/pypi/tsgettoolbox

.. image:: http://img.shields.io/badge/license-BSD-lightgrey.svg
    :alt: tsgettoolbox license
    :target: https://pypi.python.org/pypi/tsgettoolbox/

tsgettoolbox - Quick Guide
==========================
The 'tsgettoolbox' is a Python script and library to get time-series data from
different web services.  The tsgettoolbox will work with Python 2.6+ and 3.0+.

Documentation
-------------
Reference documentation is at `tsgettoolbox_documentation`_.

Installation
------------
At the command line::

    $ pip install tsgettoolbox

Usage Summary - Command Line
----------------------------
Just run 'tsgettoolbox --help' to get a list of subcommands.  To get detailed
help for a particular sub-command, for instance 'coops', type 'tsgettoolbox
coops --help'.

    cdec
        station: California Department of Water Resources

    coops
        station: Center for Operational Oceanographic Products and Services

    cpc
        station: Climate Prediction Center, Weekly Drought Index

    daymet
        gridded: Daymet, daily meteorology by the Oak Ridge National Laboratory

    fawn
        station: Florida Automated Weather Network (FAWN)

    ldas
        gridded: Land Data Assimilation System (NLDAS, GLDAS2, TRMM, SMERGE, GRACE, MERRA)

    metdata
        gridded: Download daily data from METDATA.

    modis
        gridded: Download MODIS derived data.

    ncei_ghcnd_ftp
        station: NCEI Global Historical Climatology Network - Daily (GHCND)

    ncei_ghcnd
        station: Global Historical Climatology Network - Daily (GHCND)

    ncei_gsod
        station: NCEI Global Summary of the Day (GSOD)

    ncei_gsom
        station: NCEI Global Summary of Month (GSOM)

    ncei_gsoy
        station: NCEI Global Summary of Year (GSOY)

    ncei_normal_ann
        station: NCEI annual normals

    ncei_normal_dly
        station: NCEI Daily Normals

    ncei_normal_hly
        station: NCEI Normal hourly

    ncei_normal_mly
        station: NCEI Monthly Summaries.

    ncei_precip_15
        station: NCEI 15 minute precipitation

    ncei_precip_hly
        station: NCEI hourly precipitation

    ncei_annual
        station: NCEI annual data summaries

    ncei_ghcndms
        station: NCEI GHCND Monthly Summaries (GHCNDMS)

    ncei_ish
        station: Integrated Surface Database

    ndbc
        station: Download historical from the National Data Buoy Center.

    nwis
        station: Use the ``nwis_*`` functions instead.

    nwis_iv
        station: USGS NWIS Instantaneous Values

    nwis_dv
        station: USGS NWIS Daily Values

    nwis_site
        station: USGS NWIS Site Database

    nwis_gwlevels
        station: USGS NWIS Groundwater Levels

    nwis_measurements
        station: USGS NWIS Measurements

    nwis_peak
        station: USGS NWIS Peak

    nwis_stat
        station: USGS NWIS Statistic

    epa_wqp
        station: EPA Water Quality Portal.

    rivergages
        station: USACE river gages

    swtwc
        station: USACE Southwest Division, Tulsa Water Control

    terraclimate
        gridded: Download monthly data from Terraclimate.

    terraclimate2C
        gridded: Download monthly data from Terraclimate.

    terraclimate4C
        gridded: Download monthly data from Terraclimate.

    terraclimate19611990
        gridded: Download monthly data from Terraclimate.

    terraclimate19812010
        gridded: Download monthly data from Terraclimate.

    topowx
        gridded: Topoclimatic Daily Air Temperature Dataset for the Conterminous United States

    twc
        station: Download Texas Weather Connection (TWC) data.

    unavco
        station: Download data from the Unavco web services.

    usgs_flet_narr
        gridded: USGS FL ET data from NARR meteorologic data.

    usgs_flet_stns
        gridded: USGS FL ET data from station interpolated meteorologic data.

Usage Summary - Python Library
------------------------------
To use the tsgettoolbox in a project::

    from tsgettoolbox import tsgettoolbox
    df = tsgettoolbox.nwis_dv(sites="02329500", startDT="2000-01-01")

Refer to the API Documentation at `tsgettoolbox_api`_.

Usage Summary - Command Line
----------------------------

    tsgettoolbox nwis_dv --sites 02329500 --startDT 2000-01-01

Refer to the command line documentation at `tsgettoolbox_cli`_.

Development
~~~~~~~~~~~
Development is managed on bitbucket or github.
https://bitbucket.org/timcera/tsgettoolbox/overview.
https://github.com/timcera/tsgettoolbox

.. _tsgettoolbox_documentation: https://timcera.bitbucket.io/tsgettoolbox/docs/index.html#tsgettoolbox-documentation
.. _tsgettoolbox_api: https://timcera.bitbucket.io/tsgettoolbox/docs/function_summary.html
.. _tsgettoolbox_cli: https://timcera.bitbucket.io/tsgettoolbox/docs/command_line.html
