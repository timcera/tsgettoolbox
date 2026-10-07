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

+----------------------------------+----------+--------+----------+----------+----------------------------+
| Sub-command                      | Spatial  | Time   | Type     | Time     | Description                |
|                                  | Extent   | Extent |          | Interval |                            |
+==================================+==========+========+==========+==========+============================+
| cdec                             | US/CA    | varies | station  | E,H,D,M  | California Department of   |
|                                  |          |        |          |          | Water Resources            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| coops                            | global   | varies | station  | 1T,6T,H, | Center for Operational     |
|                                  |          |        |          | D,M      | Oceanographic Products and |
|                                  |          |        |          |          | Services                   |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| cpc DISCONTINUED                 | US       | varies | region   | W        | Climate Prediction Center  |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| daymet                           | NAmerica | 1980-  | grid 1km | D,M      | daily meteorology by the   |
|                                  |          |        |          |          | Oak Ridge National         |
|                                  |          |        |          |          | Laboratory                 |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| fawn                             | US/FL    | varies | station  | 15T,H,D, | Florida Automated Weather  |
|                                  |          |        |          | M        |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| hydstra_ts                       | varies   | varies | station  | E,H,D,M  | Kisters Hydstra Webservice |
|                                  |          |        |          |          | - time series values       |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| hydstrsa_catalog                 | varies   | varies | station  | -NA-     | Kisters Hydstra Webservice |
|                                  |          |        |          |          | - variable catalog         |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| hydrstra_stations                | varies   | varies | station  | -NA-     | Kisters Hydstra Webservice |
|                                  |          |        |          |          | - station list             |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| ldas DEPRECATED use ldas_*       | global   | varies | grid     | varies   | Land Data Assimilation     |
| functions below instead          |          |        |          |          | System                     |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| ldas_gldas_noah                  | global   | 2000-  | grid     | 3H       | GLDAS NOAH hydrology model |
|                                  |          |        | 0.25deg  |          | results                    |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| ldas_gldas_noah_v2_0             | global   | 1948-  | grid     | 3H       | GLDAS NOAH hydrology model |
|                                  |          | 2014   | 0.25deg  |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| ldas_gldas_noah_v2_1             | global   | 2000-  | grid     | 3H       | GLDAS NOAH hydrology model |
|                                  |          |        | 0.25deg  |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| ldas_grace                       | NAmerica | 2002-  | grid     | 7D       | Groundwater and soil       |
|                                  |          |        | 0.125deg |          | moisture from GRACE        |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| ldas_merra                       | global   | 1980-  | grid     | H        | MERRA-2 Land surface       |
|                                  |          |        | 0.5x     |          |                            |
|                                  |          |        | 0.625deg |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| ldas_nldas3_forcing              | NAmerica | 2001-  | grid     | HDM      | NLDAS3 Weather Forcing A   |
|                                  |          |        | 0.01deg  |          | (surface)                  |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| ldas_nldas_fora                  | NAmerica | 1979-  | grid     | H        | NLDAS Weather Forcing A    |
|                                  |          |        | 0.125deg |          | (surface)                  |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| ldas_nldas_noah                  | NAmerica | 1979-  | grid     | H        | NLDAS NOAH hydrology model |
|                                  |          |        | 0.125deg |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| ldas_nldas_vic                   | NAmerica | 1979-  | grid     | H        | NLDAS VIC hydrology model  |
|                                  |          |        | 0.125deg |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| ldas_smerge                      | global   | 1997-  | grid     | D        | SMERGE-Noah-CCI root zone  |
|                                  |          |        | 0.125deg |          | soil                       |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| metdata                          | NAmerica | 1980-  | grid 4km | D        | Daily data from METDATA    |
|                                  |          |        |          |          | based on PRISM.            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| modis                            | global   | 2000-  | grid     | 4D,8D,16 | MODIS derived data         |
|                                  |          |        | 250m,    | D,A      |                            |
|                                  |          |        | 500m,    |          |                            |
|                                  |          |        | 1000m    |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| ncei_ghcnd_ftp                   | global   | varies | station  | D        | NCEI Global Historical     |
|                                  |          |        |          |          | Climatology Network -      |
|                                  |          |        |          |          | Daily (GHCND) from FTP     |
|                                  |          |        |          |          | server.                    |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| ncei_ghcnd                       | global   | varies | station  | D        | NCEI Global Historical     |
|                                  |          |        |          |          | Climatology Network -      |
|                                  |          |        |          |          | Daily (GHCND) from web     |
|                                  |          |        |          |          | services.                  |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| ncei_gsod                        | global   | varies | station  | D        | NCEI Global Summary of the |
|                                  |          |        |          |          | Day (GSOD)                 |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| ncei_gsom                        | global   | varies | station  | M        | NCEI Global Summary of the |
|                                  |          |        |          |          | Month (GSOM)               |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| ncei_gsoy                        | global   | varies | station  | A        | NCEI Global Summary of     |
|                                  |          |        |          |          | Year                       |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| ncei_normal_ann                  | global   | varies | station  | A        | NCEI annual normals        |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| ncei_normal_dly                  | global   | varies | station  | D        | NCEI daily normals         |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| ncei_normal_hly                  | global   | varies | station  | H        | NCEI hourly normals        |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| ncei_normal_mly                  | global   | varies | station  | M        | NCEI monthly normals       |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| ncei_precip_15                   | global   | varies | station  | 15T      | NCEI 15 minute             |
|                                  |          |        |          |          | precipitation              |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| ncei_precip_hly                  | global   | varies | station  | H        | NCEI hourly precipitation  |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| ncei_annual                      | global   | varies | station  | A        | NCEI annual data summaries |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| ncei_ghcndms                     | global   | varies | station  | M        | NCEI GHCND Monthly         |
|                                  |          |        |          |          | Summaries (GHCNDMS)        |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| ncei_ish                         | global   | varies | station  | H        | NCEI Integrated Surface    |
|                                  |          |        |          |          | hourly                     |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| ndbc                             | US       | varies | station  | 6T,10T,  | National Data Buoy Center  |
|                                  |          |        |          | 15T,H,D  |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| nwis DEPRECATED use nwis_*       | US       | varies | station  | varies   | USGS National Water        |
| functions below instead.         |          |        |          |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| nwis_iv DEPRECATED: use          | US       | varies | station  | E        | USGS NWIS Instantaneous    |
| wdfn_continuous                  |          |        |          |          | Values                     |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| nwis_dv DEPRECATED: use          | US       | varies | station  | D        | USGS NWIS Daily Values     |
| wdfn_daily                       |          |        |          |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| nwis_site DEPRECATED: use        | US       | varies | station  | -NA-     | USGS NWIS Site Database    |
| wdfn_monitoring_locations        |          |        |          |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| nwis_gwlevels DEPRECATED: use    | US       | varies | station  | varies   | USGS NWIS Groundwater      |
| wdfn_field_measurements          |          |        |          |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| nwis_measurements DEPRECATED:    | US       | varies | station  | varies   | USGS NWIS Measurements     |
| use wdfn_field_measurements      |          |        |          |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| nwis_peak DEPRECATED: use        | US       | varies | station  | varies   | USGS NWIS Peak             |
| wdfn_peaks                       |          |        |          |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| nwis_stat DEPRECATED: use        | US       | varies | station  | varies   | USGS NWIS Statistic        |
| wdfn_read_normal_observations or |          |        |          |          |                            |
| wdfn_read_interval_observations  |          |        |          |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| epa_wqp                          | US       | varies | station  | varies   | US EPA Water Quality       |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| rivergages                       | US       | varies | station  | varies   | USACE river gages          |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| terraclimate                     | global   | varies | grid     | M        | Monthly data from          |
|                                  |          |        | 1/24deg  |          | TerraClimate               |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| terraclimate19812010             | global   | varies | grid     | M        | Monthly normals using      |
|                                  |          |        | 1/24deg  |          | TerraClimate monthly data  |
|                                  |          |        |          |          | from 1981 to 2010          |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| terraclimate19912020             | global   | varies | grid     | M        | Monthly normals using      |
|                                  |          |        | 1/24deg  |          | TerraClimate monthly data  |
|                                  |          |        |          |          | from 1991 to 2020          |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| twc                              | US/OK    | varies | station  | D        | Texas Weather Connection   |
|                                  |          |        |          |          | (TWC) data                 |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| unavco                           | US       | varies | station  | varies   | UNAVCO well data           |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_agency_codes                | US       | varies | station  |          | USGS WDFN Agency codes as  |
|                                  |          |        |          |          | table                      |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_altitude_datums             | US       | varies | station  |          | USGS WDFN Altitude datums  |
|                                  |          |        |          |          | as table                   |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_aquifer_codes               | US       | varies | station  |          | USGS WDFN Aquifer codes as |
|                                  |          |        |          |          | table                      |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_aquifer_types               | US       | varies | station  |          | USGS WDFN Aquifer types as |
|                                  |          |        |          |          | table                      |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_channel_measurements        | US       | varies | station  | E        | USGS WDFN Channel          |
|                                  |          |        |          |          | measurements as time-      |
|                                  |          |        |          |          | series                     |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_citations                   | US       | varies | station  |          | USGS WDFN Citations as     |
|                                  |          |        |          |          | table                      |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_combined_metadata           | US       | varies | station  |          | USGS WDFN Combined         |
|                                  |          |        |          |          | metadata as table          |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_continuous                  | US       | varies | station  | E        | USGS WDFN Continuous data  |
|                                  |          |        |          |          | as time-series             |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_coordinate_accuracy_codes   | US       | varies | station  |          | USGS WDFN Coordinate       |
|                                  |          |        |          |          | accuracy codes as table    |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_coordinate_datum_codes      | US       | varies | station  |          | USGS WDFN Coordinate datum |
|                                  |          |        |          |          | codes as table             |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_coordinate_method_codes     | US       | varies | station  |          | USGS WDFN Coordinate       |
|                                  |          |        |          |          | method codes as table      |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_counties                    | US       | varies | station  |          | USGS WDFN Counties as      |
|                                  |          |        |          |          | table                      |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_countries                   | US       | varies | station  |          | USGS WDFN Countries as     |
|                                  |          |        |          |          | table                      |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_daily                       | US       | varies | station  | D        | USGS WDFN Daily data as    |
|                                  |          |        |          |          | time-series                |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_field_measurements          | US       | varies | station  | E        | USGS WDFN Field            |
|                                  |          |        |          |          | measurements as time-      |
|                                  |          |        |          |          | series                     |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_field_measurements_metadata | US       | varies | station  |          | USGS WDFN Field            |
|                                  |          |        |          |          | measurements metadata as   |
|                                  |          |        |          |          | table                      |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_hydrologic_unit_codes       | US       | varies | station  |          | USGS WDFN Hydrologic unit  |
|                                  |          |        |          |          | codes as table             |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_latest_continuous           | US       | varies | station  | E        | USGS WDFN Latest           |
|                                  |          |        |          |          | continuous data as time-   |
|                                  |          |        |          |          | series                     |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_latest_daily                | US       | varies | station  | D        | USGS WDFN Latest daily     |
|                                  |          |        |          |          | data as time-series        |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_latest_field_measurements   | US       | varies | station  | E        | USGS WDFN Latest field     |
|                                  |          |        |          |          | measurements as time-      |
|                                  |          |        |          |          | series                     |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_medium_codes                | US       | varies | station  |          | USGS WDFN Medium codes as  |
|                                  |          |        |          |          | table                      |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_method_categories           | US       | varies | station  |          | USGS WDFN Method           |
|                                  |          |        |          |          | categories as table        |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_method_citations            | US       | varies | station  |          | USGS WDFN Method citations |
|                                  |          |        |          |          | as table                   |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_methods                     | US       | varies | station  |          | USGS WDFN Methods as table |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_monitoring_locations        | US       | varies | station  |          | USGS WDFN Monitoring       |
|                                  |          |        |          |          | locations as table         |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_national_aquifer_codes      | US       | varies | station  |          | USGS WDFN National aquifer |
|                                  |          |        |          |          | codes as table             |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_parameter_codes             | US       | varies | station  |          | USGS WDFN Parameter codes  |
|                                  |          |        |          |          | as table                   |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_peaks                       | US       | varies | station  | E        | USGS WDFN Peaks as time-   |
|                                  |          |        |          |          | series                     |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_reliability_codes           | US       | varies | station  |          | USGS WDFN Reliability      |
|                                  |          |        |          |          | codes as table             |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_site_types                  | US       | varies | station  |          | USGS WDFN Site types as    |
|                                  |          |        |          |          | table                      |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_states                      | US       | varies | station  |          | USGS WDFN States as table  |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_statistic_codes             | US       | varies | station  |          | USGS WDFN Statistic codes  |
|                                  |          |        |          |          | as table                   |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_time_series_metadata        | US       | varies | station  |          | USGS WDFN Time series      |
|                                  |          |        |          |          | metadata as table          |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_time_series_methods         | US       | varies | station  |          | USGS WDFN Time series      |
|                                  |          |        |          |          | methods as table           |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_time_series_revisions       | US       | varies | station  | E        | USGS WDFN Time series      |
|                                  |          |        |          |          | revisions as time-series   |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_time_zone_codes             | US       | varies | station  |          | USGS WDFN Time zone codes  |
|                                  |          |        |          |          | as table                   |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_read_normal_observations    | US       | varies | station  | DM       | USGS WDFN Statistical      |
|                                  |          |        |          |          | normal observations        |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| wdfn_read_interval_observations  | US       | varies | station  | MA       | USGS WDFN Statistical      |
|                                  |          |        |          |          | interval obs as time-      |
|                                  |          |        |          |          | series                     |
+----------------------------------+----------+--------+----------+----------+----------------------------+

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
    df = tsgettoolbox.wdfn_daily(monitoring_location_number="02329500", time="2000-01-01/..")

Refer to the API Documentation at `tsgettoolbox_api`_.

Usage Summary - Command Line
----------------------------

    tsgettoolbox wdfn_daily --monitoring_location_number 02329500 --time 2000-01-01/..

Refer to the command line documentation at `tsgettoolbox_cli`_.

Development
~~~~~~~~~~~
Development is managed on bitbucket or github.
https://bitbucket.org/timcera/tsgettoolbox/overview.
https://github.com/timcera/tsgettoolbox

.. _tsgettoolbox_documentation: https://timcera.bitbucket.io/tsgettoolbox/docs/index.html#tsgettoolbox-documentation
.. _tsgettoolbox_api: https://timcera.bitbucket.io/tsgettoolbox/docs/function_summary.html
.. _tsgettoolbox_cli: https://timcera.bitbucket.io/tsgettoolbox/docs/command_line.html
