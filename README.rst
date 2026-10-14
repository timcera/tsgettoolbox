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

Starting with version 27.0.0+, this package supplies the core functionality for
the tsgettoolbox command line tool and Python library.  The real work is done
by a group of plugins that have this package as a dependency.  The plugins are
available using pip or conda.

The current plugins are:

* tsgettoolbox_cdec
  + California Department of Water Resources (CDEC) time series data
* tsgettoolbox_coops
  + Center for Operational Oceanographic Products and Services (CO-OPS) time
  series data
* tsgettoolbox_daymet
  + Daily meteorology by the Oak Ridge National Laboratory (Daymet) gridded
  data
* tsgettoolbox_fawn
  + Florida Automated Weather Network (FAWN) time series data
* tsgettoolbox_hydstra
  + Kisters Hydstra Webservice time series data
* tsgettoolbox_ldas
  + Land Data Assimilation System (LDAS) gridded data
* tsgettoolbox_metdata
  + Daily data from METDATA based on PRISM gridded data
* tsgettoolbox_modis
  + MODIS derived gridded data
* tsgettoolbox_ncei
  + National Centers for Environmental Information (NCEI) time series data
* tsgettoolbox_ndbc
  + National Data Buoy Center (NDBC) time series data
* tsgettoolbox_nldas3
  + North American Land Data Assimilation System (NLDAS) version 3 gridded data
* tsgettoolbox_nwis
  + USGS National Water Information System (NWIS) time series data (USGS will
  turn off NWIS in 2027, use functions in tsgettoolbox_wdfn instead)
* tsgettoolbox_rivergages
  + USACE river gages time series data
* tsgettoolbox_terraclimate
  + TerraClimate gridded data
* tsgettoolbox_twc
  + Texas Weather Connection (TWC) time series data
* tsgettoolbox_unavco
  + UNAVCO well time series data
* tsgettoolbox_wdfn
  + USGS Water Data for the Nation (WDFN) time series data

Documentation
-------------
Reference documentation is at `tsgettoolbox_documentation`_.

Installation
------------
At the command line::

    $ pip install <tsgettoolbox plugin name>

    OR

    $ conda install -c conda-forge <tsgettoolbox plugin name>

Usage Summary - Command Line
----------------------------
Just run 'tsgettoolbox --help' to get a list of subcommands from currently
install plugins.  To get detailed help for a particular sub-command, for
instance 'coops', type 'tsgettoolbox coops --help'.

+----------------------------------+----------+--------+----------+----------+----------------------------+
| plugin.function                  | Spatial  | Time   | Type     | Time     | Description                |
|                                  | Extent   | Extent |          | Interval |                            |
+==================================+==========+========+==========+==========+============================+
| tsgettoolbox_cdec.cdec           | US/CA    | varies | station  | E,H,D,M  | California Department of   |
|                                  |          |        |          |          | Water Resources            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_coops.coops         | global   | varies | station  | 1T,6T,H, | Center for Operational     |
|                                  |          |        |          | D,M      | Oceanographic Products and |
|                                  |          |        |          |          | Services                   |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| cpc DISCONTINUED                 | US       | varies | region   | W        | Climate Prediction Center  |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_daymet.daymet       | NAmerica | 1980-  | grid 1km | D,M      | daily meteorology by the   |
|                                  |          |        |          |          | Oak Ridge National         |
|                                  |          |        |          |          | Laboratory                 |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_fawn.fawn           | US/FL    | varies | station  | 15T,H,D, | Florida Automated Weather  |
|                                  |          |        |          | M        |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_hydstra.hydstra_ts  | varies   | varies | station  | E,H,D,M  | Kisters Hydstra Webservice |
|                                  |          |        |          |          | - time series values       |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_hydstra.            | varies   | varies | station  | -NA-     | Kisters Hydstra Webservice |
| hydstra_catalog                  |          |        |          |          | - variable catalog         |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_hydstra.            | varies   | varies | station  | -NA-     | Kisters Hydstra Webservice |
| hydstra_stations                 |          |        |          |          | - station list             |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| ldas DEPRECATED use ldas_*       | global   | varies | grid     | varies   | Land Data Assimilation     |
| functions below instead          |          |        |          |          | System                     |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_ldas.               | global   | 2000-  | grid     | 3H       | GLDAS NOAH hydrology model |
| ldas_gldas_noah                  |          |        | 0.25deg  |          | results                    |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_ldas.               | global   | 1948-  | grid     | 3H       | GLDAS NOAH hydrology model |
| ldas_gldas_noah_v2_0             |          | 2014   | 0.25deg  |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_ldas.               | global   | 2000-  | grid     | 3H       | GLDAS NOAH hydrology model |
| ldas_gldas_noah_v2_1             |          |        | 0.25deg  |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_ldas.ldas_grace     | NAmerica | 2002-  | grid     | 7D       | Groundwater and soil       |
|                                  |          |        | 0.125deg |          | moisture from GRACE        |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_ldas.ldas_merra     | global   | 1980-  | grid     | H        | MERRA-2 Land surface       |
|                                  |          |        | 0.5x     |          |                            |
|                                  |          |        | 0.625deg |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_ldas.               | NAmerica | 2001-  | grid     | HDM      | NLDAS3 Weather Forcing A   |
| ldas_nldas3_forcing              |          |        | 0.01deg  |          | (surface)                  |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_ldas.               | NAmerica | 1979-  | grid     | H        | NLDAS Weather Forcing A    |
| ldas_nldas_fora                  |          |        | 0.125deg |          | (surface)                  |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_ldas.               | NAmerica | 1979-  | grid     | H        | NLDAS NOAH hydrology model |
| ldas_nldas_noah                  |          |        | 0.125deg |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_ldas.ldas_nldas_vic | NAmerica | 1979-  | grid     | H        | NLDAS VIC hydrology model  |
|                                  |          |        | 0.125deg |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_ldas.ldas_smerge    | global   | 1997-  | grid     | D        | SMERGE-Noah-CCI root zone  |
|                                  |          |        | 0.125deg |          | soil                       |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_metdata.metdata     | NAmerica | 1980-  | grid 4km | D        | Daily data from METDATA    |
|                                  |          |        |          |          | based on PRISM.            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_modis.modis         | global   | 2000-  | grid     | 4D,8D,16 | MODIS derived data         |
|                                  |          |        | 250m,    | D,A      |                            |
|                                  |          |        | 500m,    |          |                            |
|                                  |          |        | 1000m    |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_ncei.ncei_ghcnd_ftp | global   | varies | station  | D        | NCEI Global Historical     |
|                                  |          |        |          |          | Climatology Network -      |
|                                  |          |        |          |          | Daily (GHCND) from FTP     |
|                                  |          |        |          |          | server.                    |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_ncei.ncei_ghcnd     | global   | varies | station  | D        | NCEI Global Historical     |
|                                  |          |        |          |          | Climatology Network -      |
|                                  |          |        |          |          | Daily (GHCND) from web     |
|                                  |          |        |          |          | services.                  |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_ncei.ncei_gsod      | global   | varies | station  | D        | NCEI Global Summary of the |
|                                  |          |        |          |          | Day (GSOD)                 |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_ncei.ncei_gsom      | global   | varies | station  | M        | NCEI Global Summary of the |
|                                  |          |        |          |          | Month (GSOM)               |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_ncei.ncei_gsoy      | global   | varies | station  | A        | NCEI Global Summary of     |
|                                  |          |        |          |          | Year                       |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_ncei.               | global   | varies | station  | A        | NCEI annual normals        |
| ncei_normal_ann                  |          |        |          |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_ncei.               | global   | varies | station  | D        | NCEI daily normals         |
| ncei_normal_dly                  |          |        |          |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_ncei.               | global   | varies | station  | H        | NCEI hourly normals        |
| ncei_normal_hly                  |          |        |          |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_ncei.               | global   | varies | station  | M        | NCEI monthly normals       |
| ncei_normal_mly                  |          |        |          |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_ncei.ncei_precip_15 | global   | varies | station  | 15T      | NCEI 15 minute             |
|                                  |          |        |          |          | precipitation              |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_ncei.               | global   | varies | station  | H        | NCEI hourly precipitation  |
| ncei_precip_hly                  |          |        |          |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_ncei.ncei_annual    | global   | varies | station  | A        | NCEI annual data summaries |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_ncei.ncei_ghcndms   | global   | varies | station  | M        | NCEI GHCND Monthly         |
|                                  |          |        |          |          | Summaries (GHCNDMS)        |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_ncei.ncei_ish       | global   | varies | station  | H        | NCEI Integrated Surface    |
|                                  |          |        |          |          | hourly                     |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_ndbc.ndbc           | US       | varies | station  | 6T,10T,  | National Data Buoy Center  |
|                                  |          |        |          | 15T,H,D  |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| nwis DEPRECATED use wdfn_*       | US       | varies | station  | varies   | USGS National Water        |
| functions from tsgetoolbox_wdfn  |          |        |          |          |                            |
| instead.                         |          |        |          |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_nwis.nwis_iv        | US       | varies | station  | E        | USGS NWIS Instantaneous    |
| DEPRECATED: use                  |          |        |          |          | Values                     |
| tsgettoolbox_wdfn.               |          |        |          |          |                            |
| wdfn_continuous                  |          |        |          |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_nwis.nwis_dv        | US       | varies | station  | D        | USGS NWIS Daily Values     |
| DEPRECATED: use                  |          |        |          |          |                            |
| tsgettoolbox_wdfn.wdfn_daily     |          |        |          |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_nwis.nwis_site      | US       | varies | station  | -NA-     | USGS NWIS Site Database    |
| DEPRECATED: use                  |          |        |          |          |                            |
| tsgettoolbox_wdfn.               |          |        |          |          |                            |
| wdfn_monitoring_locations        |          |        |          |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_nwis.nwis_gwlevels  | US       | varies | station  | varies   | USGS NWIS Groundwater      |
| DEPRECATED: use                  |          |        |          |          |                            |
| tsgettoolbox_wdfn.               |          |        |          |          |                            |
| wdfn_field_measurements          |          |        |          |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_nwis.               | US       | varies | station  | varies   | USGS NWIS Measurements     |
| nwis_measurements DEPRECATED:    |          |        |          |          |                            |
| use tsgettoolbox_wdfn.           |          |        |          |          |                            |
| wdfn_field_measurements          |          |        |          |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_nwis.nwis_peak      | US       | varies | station  | varies   | USGS NWIS Peak             |
| DEPRECATED: use                  |          |        |          |          |                            |
| tsgettoolbox_wdfn.wdfn_peaks     |          |        |          |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_nwis.nwis_stat      | US       | varies | station  | varies   | USGS NWIS Statistic        |
| DEPRECATED: use                  |          |        |          |          |                            |
| tsgettoolbox_wdfn.               |          |        |          |          |                            |
| wdfn_read_normal_observations or |          |        |          |          |                            |
| tsgettoolbox_wdfn.               |          |        |          |          |                            |
| wdfn_read_interval_observations  |          |        |          |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wqp.project         | US       | varies | station  | varies   | US EPA Water Quality       |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wqp.station         | US       | varies | station  | varies   | US EPA Water Quality       |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wqp.result          | US       | varies | station  | varies   | US EPA Water Quality       |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wqp.                | US       | varies | station  | varies   | US EPA Water Quality       |
| result_detection_quantitation_li |          |        |          |          |                            |
| mit                              |          |        |          |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wqp.activity        | US       | varies | station  | varies   | US EPA Water Quality       |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wqp.activity_metric | US       | varies | station  | varies   | US EPA Water Quality       |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wqp.                | US       | varies | station  | varies   | US EPA Water Quality       |
| biological_metric                |          |        |          |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wqp.                | US       | varies | station  | varies   | US EPA Water Quality       |
| projec_monitoring_location_weigh |          |        |          |          |                            |
| ting                             |          |        |          |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_rivergages.         | US       | varies | station  | varies   | USACE river gages          |
| rivergages                       |          |        |          |          |                            |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_terraclimate.       | global   | varies | grid     | M        | Monthly data from          |
| terraclimate                     |          |        | 1/24deg  |          | TerraClimate               |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_terraclimate.       | global   | varies | grid     | M        | Monthly normals using      |
| terraclimate19812010             |          |        | 1/24deg  |          | TerraClimate monthly data  |
|                                  |          |        |          |          | from 1981 to 2010          |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_terraclimate.       | global   | varies | grid     | M        | Monthly normals using      |
| terraclimate19912020             |          |        | 1/24deg  |          | TerraClimate monthly data  |
|                                  |          |        |          |          | from 1991 to 2020          |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_twc.twc             | US/OK    | varies | station  | D        | Texas Weather Connection   |
|                                  |          |        |          |          | (TWC) data                 |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_unavco.unavco       | US       | varies | station  | varies   | UNAVCO well data           |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.               | US       | varies | station  |          | USGS WDFN Agency codes as  |
| wdfn_agency_codes                |          |        |          |          | table                      |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.               | US       | varies | station  |          | USGS WDFN Altitude datums  |
| wdfn_altitude_datums             |          |        |          |          | as table                   |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.               | US       | varies | station  |          | USGS WDFN Aquifer codes as |
| wdfn_aquifer_codes               |          |        |          |          | table                      |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.               | US       | varies | station  |          | USGS WDFN Aquifer types as |
| wdfn_aquifer_types               |          |        |          |          | table                      |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.               | US       | varies | station  | E        | USGS WDFN Channel          |
| wdfn_channel_measurements        |          |        |          |          | measurements as time-      |
|                                  |          |        |          |          | series                     |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.wdfn_citations | US       | varies | station  |          | USGS WDFN Citations as     |
|                                  |          |        |          |          | table                      |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.               | US       | varies | station  |          | USGS WDFN Combined         |
| wdfn_combined_metadata           |          |        |          |          | metadata as table          |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.               | US       | varies | station  | E        | USGS WDFN Continuous data  |
| wdfn_continuous                  |          |        |          |          | as time-series             |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.               | US       | varies | station  |          | USGS WDFN Coordinate       |
| wdfn_coordinate_accuracy_codes   |          |        |          |          | accuracy codes as table    |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.               | US       | varies | station  |          | USGS WDFN Coordinate datum |
| wdfn_coordinate_datum_codes      |          |        |          |          | codes as table             |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.               | US       | varies | station  |          | USGS WDFN Coordinate       |
| wdfn_coordinate_method_codes     |          |        |          |          | method codes as table      |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.wdfn_counties  | US       | varies | station  |          | USGS WDFN Counties as      |
|                                  |          |        |          |          | table                      |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.wdfn_countries | US       | varies | station  |          | USGS WDFN Countries as     |
|                                  |          |        |          |          | table                      |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.wdfn_daily     | US       | varies | station  | D        | USGS WDFN Daily data as    |
|                                  |          |        |          |          | time-series                |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.               | US       | varies | station  | E        | USGS WDFN Field            |
| wdfn_field_measurements          |          |        |          |          | measurements as time-      |
|                                  |          |        |          |          | series                     |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.               | US       | varies | station  |          | USGS WDFN Field            |
| wdfn_field_measurements_metadata |          |        |          |          | measurements metadata as   |
|                                  |          |        |          |          | table                      |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.               | US       | varies | station  |          | USGS WDFN Hydrologic unit  |
| wdfn_hydrologic_unit_codes       |          |        |          |          | codes as table             |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.               | US       | varies | station  | E        | USGS WDFN Latest           |
| wdfn_latest_continuous           |          |        |          |          | continuous data as time-   |
|                                  |          |        |          |          | series                     |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.               | US       | varies | station  | D        | USGS WDFN Latest daily     |
| wdfn_latest_daily                |          |        |          |          | data as time-series        |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.               | US       | varies | station  | E        | USGS WDFN Latest field     |
| wdfn_latest_field_measurements   |          |        |          |          | measurements as time-      |
|                                  |          |        |          |          | series                     |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.               | US       | varies | station  |          | USGS WDFN Medium codes as  |
| wdfn_medium_codes                |          |        |          |          | table                      |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.               | US       | varies | station  |          | USGS WDFN Method           |
| wdfn_method_categories           |          |        |          |          | categories as table        |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.               | US       | varies | station  |          | USGS WDFN Method citations |
| wdfn_method_citations            |          |        |          |          | as table                   |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.wdfn_methods   | US       | varies | station  |          | USGS WDFN Methods as table |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.               | US       | varies | station  |          | USGS WDFN Monitoring       |
| wdfn_monitoring_locations        |          |        |          |          | locations as table         |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.               | US       | varies | station  |          | USGS WDFN National aquifer |
| wdfn_national_aquifer_codes      |          |        |          |          | codes as table             |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.               | US       | varies | station  |          | USGS WDFN Parameter codes  |
| wdfn_parameter_codes             |          |        |          |          | as table                   |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.wdfn_peaks     | US       | varies | station  | E        | USGS WDFN Peaks as time-   |
|                                  |          |        |          |          | series                     |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.               | US       | varies | station  |          | USGS WDFN Reliability      |
| wdfn_reliability_codes           |          |        |          |          | codes as table             |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.               | US       | varies | station  |          | USGS WDFN Site types as    |
| wdfn_site_types                  |          |        |          |          | table                      |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.wdfn_states    | US       | varies | station  |          | USGS WDFN States as table  |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.               | US       | varies | station  |          | USGS WDFN Statistic codes  |
| wdfn_statistic_codes             |          |        |          |          | as table                   |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.               | US       | varies | station  |          | USGS WDFN Time series      |
| wdfn_time_series_metadata        |          |        |          |          | metadata as table          |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.               | US       | varies | station  |          | USGS WDFN Time series      |
| wdfn_time_series_methods         |          |        |          |          | methods as table           |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.               | US       | varies | station  | E        | USGS WDFN Time series      |
| wdfn_time_series_revisions       |          |        |          |          | revisions as time-series   |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.               | US       | varies | station  |          | USGS WDFN Time zone codes  |
| wdfn_time_zone_codes             |          |        |          |          | as table                   |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.               | US       | varies | station  | DM       | USGS WDFN Statistical      |
| wdfn_read_normal_observations    |          |        |          |          | normal observations        |
+----------------------------------+----------+--------+----------+----------+----------------------------+
| tsgettoolbox_wdfn.               | US       | varies | station  | MA       | USGS WDFN Statistical      |
| wdfn_read_interval_observations  |          |        |          |          | interval obs as time-      |
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
