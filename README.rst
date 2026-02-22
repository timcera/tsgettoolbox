.. image:: https://github.com/timcera/tsgettoolbox/actions/workflows/pypi-package.yml/badge.svg
    :alt: Tests
    :target: https://github.com/timcera/tsgettoolbox/actions/workflows/pypi-package.yml
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

.. image:: https://img.shields.io/pypi/pyversions/tsgettoolbox
    :alt: PyPI - Python Version
    :target: https://pypi.org/project/tsgettoolbox/
    :height: 20

tsgettoolbox - Quick Guide
==========================
The 'tsgettoolbox' is a Python script and library to get time-series data from
different web services.  The tsgettoolbox will work with Python and 3.10+.

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

+----------------------+----------+--------+----------+----------+----------------------------+
| Sub-command          | Spatial  | Time   | Type     | Time     | Description                |
|                      | Extent   | Extent |          | Interval |                            |
+======================+==========+========+==========+==========+============================+
| cdec                 | US/CA    | varies | station  | E,H,D,M  | California Department of   |
|                      |          |        |          |          | Water Resources            |
+----------------------+----------+--------+----------+----------+----------------------------+
| coops                | global   | varies | station  | 1T,6T,H, | Center for Operational     |
|                      |          |        |          | D,M      | Oceanographic Products and |
|                      |          |        |          |          | Services                   |
+----------------------+----------+--------+----------+----------+----------------------------+
| cpc DISCONTINUED     | US       | varies | region   | W        | Climate Prediction Center  |
+----------------------+----------+--------+----------+----------+----------------------------+
| daymet               | NAmerica | 1980-  | grid 1km | D,M      | daily meteorology by the   |
|                      |          |        |          |          | Oak Ridge National         |
|                      |          |        |          |          | Laboratory                 |
+----------------------+----------+--------+----------+----------+----------------------------+
| fawn                 | US/FL    | varies | station  | 15T,H,D, | Florida Automated Weather  |
|                      |          |        |          | M        |                            |
+----------------------+----------+--------+----------+----------+----------------------------+
| hydstra_ts           | varies   | varies | station  | E,H,D,M  | Kisters Hydstra Webservice |
|                      |          |        |          |          | - time series values       |
+----------------------+----------+--------+----------+----------+----------------------------+
| hydstrsa_catalog     | varies   | varies | station  | -NA-     | Kisters Hydstra Webservice |
|                      |          |        |          |          | - variable catalog         |
+----------------------+----------+--------+----------+----------+----------------------------+
| hydrstra_stations    | varies   | varies | station  | -NA-     | Kisters Hydstra Webservice |
|                      |          |        |          |          | - station list             |
+----------------------+----------+--------+----------+----------+----------------------------+
| ldas DEPRECATED use  | global   | varies | grid     | varies   | Land Data Assimilation     |
| ldas_* functions     |          |        |          |          | System                     |
| below instead        |          |        |          |          |                            |
+----------------------+----------+--------+----------+----------+----------------------------+
| ldas_gldas_noah      | global   | 2000-  | grid     | 3H       | GLDAS NOAH hydrology model |
|                      |          |        | 0.25deg  |          | results                    |
+----------------------+----------+--------+----------+----------+----------------------------+
| ldas_gldas_noah_v2_0 | global   | 1948-  | grid     | 3H       | GLDAS NOAH hydrology model |
|                      |          | 2014   | 0.25deg  |          |                            |
+----------------------+----------+--------+----------+----------+----------------------------+
| ldas_gldas_noah_v2_1 | global   | 2000-  | grid     | 3H       | GLDAS NOAH hydrology model |
|                      |          |        | 0.25deg  |          |                            |
+----------------------+----------+--------+----------+----------+----------------------------+
| ldas_grace           | NAmerica | 2002-  | grid     | 7D       | Groundwater and soil       |
|                      |          |        | 0.125deg |          | moisture from GRACE        |
+----------------------+----------+--------+----------+----------+----------------------------+
| ldas_merra           | global   | 1980-  | grid     | H        | MERRA-2 Land surface       |
|                      |          |        | 0.5x     |          |                            |
|                      |          |        | 0.625deg |          |                            |
+----------------------+----------+--------+----------+----------+----------------------------+
| ldas_nldas_fora      | NAmerica | 1979-  | grid     | H        | NLDAS Weather Forcing A    |
|                      |          |        | 0.125deg |          | (surface)                  |
+----------------------+----------+--------+----------+----------+----------------------------+
| ldas_nldas_noah      | NAmerica | 1979-  | grid     | H        | NLDAS NOAH hydrology model |
|                      |          |        | 0.125deg |          |                            |
+----------------------+----------+--------+----------+----------+----------------------------+
| ldas_nldas_vic       | NAmerica | 1979-  | grid     | H        | NLDAS VIC hydrology model  |
|                      |          |        | 0.125deg |          |                            |
+----------------------+----------+--------+----------+----------+----------------------------+
| ldas_smerge          | global   | 1997-  | grid     | D        | SMERGE-Noah-CCI root zone  |
|                      |          |        | 0.125deg |          | soil                       |
+----------------------+----------+--------+----------+----------+----------------------------+
| metdata              | NAmerica | 1980-  | grid 4km | D        | Daily data from METDATA    |
|                      |          |        |          |          | based on PRISM.            |
+----------------------+----------+--------+----------+----------+----------------------------+
| modis                | global   | 2000-  | grid     | 4D,8D,16 | MODIS derived data         |
|                      |          |        | 250m,    | D,A      |                            |
|                      |          |        | 500m,    |          |                            |
|                      |          |        | 1000m    |          |                            |
+----------------------+----------+--------+----------+----------+----------------------------+
| ncei_ghcnd_ftp       | global   | varies | station  | D        | NCEI Global Historical     |
|                      |          |        |          |          | Climatology Network -      |
|                      |          |        |          |          | Daily (GHCND) from FTP     |
|                      |          |        |          |          | server.                    |
+----------------------+----------+--------+----------+----------+----------------------------+
| ncei_ghcnd           | global   | varies | station  | D        | NCEI Global Historical     |
|                      |          |        |          |          | Climatology Network -      |
|                      |          |        |          |          | Daily (GHCND) from web     |
|                      |          |        |          |          | services.                  |
+----------------------+----------+--------+----------+----------+----------------------------+
| ncei_gsod            | global   | varies | station  | D        | NCEI Global Summary of the |
|                      |          |        |          |          | Day (GSOD)                 |
+----------------------+----------+--------+----------+----------+----------------------------+
| ncei_gsom            | global   | varies | station  | M        | NCEI Global Summary of the |
|                      |          |        |          |          | Month (GSOM)               |
+----------------------+----------+--------+----------+----------+----------------------------+
| ncei_gsoy            | global   | varies | station  | A        | NCEI Global Summary of     |
|                      |          |        |          |          | Year                       |
+----------------------+----------+--------+----------+----------+----------------------------+
| ncei_normal_ann      | global   | varies | station  | A        | NCEI annual normals        |
+----------------------+----------+--------+----------+----------+----------------------------+
| ncei_normal_dly      | global   | varies | station  | D        | NCEI daily normals         |
+----------------------+----------+--------+----------+----------+----------------------------+
| ncei_normal_hly      | global   | varies | station  | H        | NCEI hourly normals        |
+----------------------+----------+--------+----------+----------+----------------------------+
| ncei_normal_mly      | global   | varies | station  | M        | NCEI monthly normals       |
+----------------------+----------+--------+----------+----------+----------------------------+
| ncei_precip_15       | global   | varies | station  | 15T      | NCEI 15 minute             |
|                      |          |        |          |          | precipitation              |
+----------------------+----------+--------+----------+----------+----------------------------+
| ncei_precip_hly      | global   | varies | station  | H        | NCEI hourly precipitation  |
+----------------------+----------+--------+----------+----------+----------------------------+
| ncei_annual          | global   | varies | station  | A        | NCEI annual data summaries |
+----------------------+----------+--------+----------+----------+----------------------------+
| ncei_ghcndms         | global   | varies | station  | M        | NCEI GHCND Monthly         |
|                      |          |        |          |          | Summaries (GHCNDMS)        |
+----------------------+----------+--------+----------+----------+----------------------------+
| ncei_ish             | global   | varies | station  | H        | NCEI Integrated Surface    |
|                      |          |        |          |          | hourly                     |
+----------------------+----------+--------+----------+----------+----------------------------+
| ndbc                 | US       | varies | station  | 6T,10T,  | National Data Buoy Center  |
|                      |          |        |          | 15T,H,D  |                            |
+----------------------+----------+--------+----------+----------+----------------------------+
| nwis DEPRECATED use  | US       | varies | station  | varies   | USGS National Water        |
| nwis_* functions     |          |        |          |          |                            |
| below instead.       |          |        |          |          |                            |
+----------------------+----------+--------+----------+----------+----------------------------+
| nwis_iv              | US       | varies | station  | E        | USGS NWIS Instantaneous    |
|                      |          |        |          |          | Values                     |
+----------------------+----------+--------+----------+----------+----------------------------+
| nwis_dv              | US       | varies | station  | D        | USGS NWIS Daily Values     |
+----------------------+----------+--------+----------+----------+----------------------------+
| nwis_site            | US       | varies | station  | -NA-     | USGS NWIS Site Database    |
+----------------------+----------+--------+----------+----------+----------------------------+
| nwis_gwlevels        | US       | varies | station  | varies   | USGS NWIS Groundwater      |
+----------------------+----------+--------+----------+----------+----------------------------+
| nwis_measurements    | US       | varies | station  | varies   | USGS NWIS Measurements     |
+----------------------+----------+--------+----------+----------+----------------------------+
| nwis_peak            | US       | varies | station  | varies   | USGS NWIS Peak             |
+----------------------+----------+--------+----------+----------+----------------------------+
| nwis_stat            | US       | varies | station  | varies   | USGS NWIS Statistic        |
+----------------------+----------+--------+----------+----------+----------------------------+
| epa_wqp              | US       | varies | station  | varies   | US EPA Water Quality       |
+----------------------+----------+--------+----------+----------+----------------------------+
| rivergages           | US       | varies | station  | varies   | USACE river gages          |
+----------------------+----------+--------+----------+----------+----------------------------+
| swtwc DISCONTINUED   | US/OK    | varies | station  | varies   | USACE Southwest Division,  |
|                      |          |        |          |          | Tulsa Water Control        |
+----------------------+----------+--------+----------+----------+----------------------------+
| terraclimate         | global   | varies | grid     | M        | Monthly data from          |
|                      |          |        | 1/24deg  |          | TerraClimate               |
+----------------------+----------+--------+----------+----------+----------------------------+
| terraclimate19611990 | global   | varies | grid     | M        | Monthly normals using      |
| DISCONTINUED         |          |        | 1/24deg  |          | TerraClimate monthly data  |
|                      |          |        |          |          | from 1961 to 1990          |
+----------------------+----------+--------+----------+----------+----------------------------+
| terraclimate19812010 | global   | varies | grid     | M        | Monthly normals using      |
|                      |          |        | 1/24deg  |          | TerraClimate monthly data  |
|                      |          |        |          |          | from 1981 to 2010          |
+----------------------+----------+--------+----------+----------+----------------------------+
| terraclimate19912020 | global   | varies | grid     | M        | Monthly normals using      |
|                      |          |        | 1/24deg  |          | TerraClimate monthly data  |
|                      |          |        |          |          | from 1991 to 2020          |
+----------------------+----------+--------+----------+----------+----------------------------+
| terraclimate2C       | global   | varies | grid     | M        | Monthly normals using      |
| DISCONTINUED         |          |        | 1/24deg  |          | TerraClimate with 2deg C   |
|                      |          |        |          |          | hotter climate             |
+----------------------+----------+--------+----------+----------+----------------------------+
| terraclimate4C       | global   | varies | grid     | M        | Monthly normals using      |
| DISCONTINUED         |          |        | 1/24deg  |          | TerraClimate with 4deg C   |
|                      |          |        |          |          | hotter climate             |
+----------------------+----------+--------+----------+----------+----------------------------+
| twc                  | US/OK    | varies | station  | D        | Texas Weather Connection   |
|                      |          |        |          |          | (TWC) data                 |
+----------------------+----------+--------+----------+----------+----------------------------+
| unavco               | US       | varies | station  | varies   | UNAVCO well data           |
+----------------------+----------+--------+----------+----------+----------------------------+

+-------------------+-------------+
| Time Interval     | Description |
| Code              |             |
+===================+=============+
| E                 | Event       |
+-------------------+-------------+
| T                 | Minute      |
+-------------------+-------------+
| H                 | Hourly      |
+-------------------+-------------+
| D                 | Daily       |
+-------------------+-------------+
| M                 | Monthly     |
+-------------------+-------------+
| A                 | Annual      |
+-------------------+-------------+


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
