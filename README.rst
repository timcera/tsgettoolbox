.. image:: https://github.com/timcera/tsgettoolbox/actions/workflows/python-package.yml/badge.svg
    :alt: Tests
    :target: https://github.com/timcera/tsgettoolbox/actions/workflows/python-package.yml
    :height: 20

.. image:: https://img.shields.io/coveralls/github/timcera/tsgettoolbox
    :alt: Test Coverage
    :target: https://coveralls.io/r/timcera/tsgettoolbox?branch=master
    :height: 20

.. image:: https://img.shields.io/pypi/v/tsgettoolbox.svg
    :alt: Latest release
    :target: https://pypi.python.org/pypi/tsgettoolbox/
    :height: 20

.. image:: https://img.shields.io/pypi/l/tsgettoolbox.svg
    :alt: BSD-3 clause license
    :target: https://pypi.python.org/pypi/tsgettoolbox/
    :height: 20

.. image:: https://img.shields.io/pypi/dd/tsgettoolbox.svg
    :alt: tsgettoolbox downloads
    :target: https://pypi.python.org/pypi/tsgettoolbox/
    :height: 20

.. image:: https://img.shields.io/pypi/pyversions/tsgettoolbox
    :alt: PyPI - Python Version
    :target: https://pypi.org/project/tsgettoolbox/
    :height: 20

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

    about
        Display version number and system information.

    cdec
        US/CA station E,H,D,M: California Department of Water Resources

    coops
        global station 1T,6T,H,D,M: Center for Operational Oceanographic
        Products and Services

    cpc
        US/region W: Climate Prediction Center, Weekly Drought Index

    daymet
        NAmerica 1km 1980- D,M:Daymet, daily meteorology by the Oak Ridge
        National Laboratory

    fawn
        US/FL 15T,H,D,M:Florida Automated Weather Network (FAWN)

    hydstra_ts
        Kisters Hydstra Webservice - time series values

    hydstra_catalog
        Kisters Hydstra Webservice - variable catalog for a station

    hydstra_stations
        Kisters Hydstra Webservice - station list for a server

    ldas
        grid: Land Data Assimilation System, includes all ldas_* (NLDAS,
        GLDAS2, TRMM, SMERGE, GRACE, MERRA)

    ldas_gldas_noah
        global 0.25deg 2000- 3H:GLDAS NOAH hydrology model results

    ldas_grace
        NAmerica 0.125deg 2002- 7D:Groundwater and soil moisture from GRACE

    ldas_merra
        global 0.5x0.625deg 1980- H:MERRA-2 Land surface forcings

    ldas_merra_update
        global 0.5x0.667deg 1980-2016 H:MERRA-2 Analysis update

    ldas_nldas_fora
        NAmerica 0.125deg 1979- H:NLDAS Weather Forcing A (surface)

    ldas_nldas_noah
        NAmerica 0.125deg 1979- H:NLDAS NOAH hydrology model results

    ldas_smerge
        global 0.125deg 1997- D:SMERGE-Noah-CCI root zone soil moisture

    ldas_trmm_tmpa
        global 0.25deg 1997- 3H:TRMM (TMPA) rainfall estimate

    metdata
        NAmerica 4km 1980- D: Download daily data from METDATA based on PRISM.

    modis
        global 250m,500m,1000m 2000- 4D,8D,16D,A:Download MODIS derived data.

    ncei_ghcnd_ftp
        global station D:NCEI Global Historical Climatology Network - Daily
        (GHCND)

    ncei_ghcnd
        global station D:Global Historical Climatology Network - Daily (GHCND)

    ncei_gsod
        global station D:NCEI Global Summary of the Day (GSOD)

    ncei_gsom
        global station M:NCEI Global Summary of Month (GSOM)

    ncei_gsoy
        global station A:NCEI Global Summary of Year (GSOY)

    ncei_normal_ann
        global station A: NCEI annual normals

    ncei_normal_dly
        global station D:NCEI Daily Normals

    ncei_normal_hly
        global station H:NCEI Normal hourly

    ncei_normal_mly
        global station M:NCEI Monthly Summaries.

    ncei_precip_15
        global station 15T:NCEI 15 minute precipitation

    ncei_precip_hly
        global station H:NCEI hourly precipitation

    ncei_annual
        global station A:NCEI annual data summaries

    ncei_ghcndms
        global station M:NCEI GHCND Monthly Summaries (GHCNDMS)

    ncei_ish
        global station H:Integrated Surface Database

    ndbc
        US station T,6T,10T,15T,H,D:Download historical from the National Data
        Buoy Center.

    nwis
        US station:Use the ``nwis_*`` functions instead.

    nwis_iv
        US station E:USGS NWIS Instantaneous Values

    nwis_dv
        US station D:USGS NWIS Daily Values

    nwis_site
        US station:USGS NWIS Site Database

    nwis_gwlevels
        US station:USGS NWIS Groundwater Levels

    nwis_measurements
        US station:USGS NWIS Measurements

    nwis_peak
        US station:USGS NWIS Peak

    nwis_stat
        US station:USGS NWIS Statistic

    epa_wqp
        US station E:EPA Water Quality Portal.

    rivergages
        US station:USACE river gages

    swtwc
        US/region station:USACE Southwest Division, Tulsa Water Control

    terraclimate
        global 1/24deg 1958- M:Download monthly data from Terraclimate.

    terraclimate2C
        global 1/24deg M:Monthly normals from Terraclimate with 2deg C hotter
        climate.

    terraclimate4C
        global 1/24deg M:Monthly normals from Terraclimate with 4deg C hotter
        climate.

    terraclimate19611990
        global 1/24deg M:Monthly normals using TerraClimate monthly data from
        1961 to 1990.

    terraclimate19812010
        global 1/24deg M:Monthly normals using TerraClimate monthly data from
        1981 to 2010.

    topowx
        US 30arcsecond 1948- M:Topoclimatic Monthly Air Temperature Dataset.

    topowx_daily
        US 30arcsecond 1948- D:Topoclimatic Daily Air Temperature Dataset.

    twc
        US/TX station D:Download Texas Weather Connection (TWC) data.

    unavco
        US station: Download data from the Unavco web services.

    usgs_flet_narr
        US/FL 2km D:USGS FL ET data from NARR meteorologic data.

    usgs_flet_stns
        US/FL 2km D:USGS FL ET data from station interpolated meteorologic
        data.

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
