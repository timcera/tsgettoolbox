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
    # OR
    $ easy_install tsgettoolbox

Or, if you have virtualenvwrapper installed::

    $ mkvirtualenv tsgettoolbox
    $ pip install tsgettoolbox

Usage Summary - Command Line
----------------------------
Just run 'tsgettoolbox --help' to get a list of subcommands.  To get detailed
help for a particular sub-command, for instance 'coops', type 'tsgettoolbox
coops --help'.

    about               
                Print out information about tsgettoolbox and the system.

    cdec        
                This module provides access to data provided by the California
                Department of Water Resources: California Data Exchange
                Center web site.

    coops
                Download data from Center for Operational Oceanographic
                Products and Services (CO-OPS). Detailed documentation about
                the National Ocean Service CO-OPS web services is at
                http://tidesandcurrents.noaa.gov/api/

    cpc         
                This module provides direct access to Climate Prediction
                Center, Weekly Drought Index dataset.

    darksky
                Download data from http://api.darksky.net. Detailed
                documentation about the Forecast.io service is at
                https://darksky.net/dev/docs. You have to get an API
                key from https://darksky.net/dev/register

    daymet
                Download data from the Daymet dataset created by the Oak Ridge
                National Laboratory. Detailed documentation is at
                http://daymet.ornl.gov/

    lcra_hydromet
                Fetches site parameter data

    lcra_wq     
                Fetches historical or near real-time (for some sites) data

    ldas
                Download data from the Land Data Assimilation Service (LDAS).
                Two projects are available, the National LDAS (0.125x0.125
                degree hourly) and the Global LDAS (0.25x0.25 degree 3 hourly).

    modis
                Download datasets developed using the MODIS satellite imagery.

                Documentation: https://modis.ornl.gov/documentation.html

                Policies: https://lpdaac.usgs.gov/products/modis_policies

                Citation: https://lpdaac.usgs.gov/citing_our_data

                +---------+---------------------------------------------------+
                | Product | Name                                              |
                +=========+===================================================+
                | MCD12Q1 | MODIS/Terra+Aqua Land Cover (LC) Type Yearly L3   |
                |         | Global 500m SIN Grid                              |
                +---------+---------------------------------------------------+
                | MCD12Q2 | MODIS/Terra+Aqua Land Cover Dynamics (LCD) Yearly |
                |         | L3 Global 500m SIN Grid                           |
                +---------+---------------------------------------------------+
                | MCD43A1 | MODIS/Terra+Aqua BRDF/Albedo (BRDF/MCD43A1)       |
                |         | 16-Day L3 Global 500m SIN Grid                    |
                +---------+---------------------------------------------------+
                | MCD43A2 | MODIS/Terra+Aqua BRDF/Model Quality               |
                |         | (BRDF/MCD43A2) 16-Day L3 Global 500m SIN Grid     |
                |         | V005                                              |
                +---------+---------------------------------------------------+
                | MCD43A4 | MODIS/Terra+Aqua Nadir BRDF-Adjusted Reflectance  |
                |         | (NBAR) 16-Day L3 Global 500m SIN Grid             |
                +---------+---------------------------------------------------+
                | MOD09A1 | MODIS/Terra Surface Reflectance (SREF) 8-Day L3   |
                |         | Global 500m SIN Grid                              |
                +---------+---------------------------------------------------+
                | MOD11A2 | MODIS/Terra Land Surface Temperature/Emissivity   |
                |         | (LST) 8-Day L3 Global 1km SIN Grid                |
                +---------+---------------------------------------------------+
                | MOD13Q1 | MODIS/Terra Vegetation Indices (NDVI/EVI) 16-Day  |
                |         | L3 Global 250m SIN Grid [Collection 5]            |
                +---------+---------------------------------------------------+
                | MOD15A2 | Leaf Area Index (LAI) and Fraction of             |
                |         | Photosynthetically Active Radiation (FPAR) 8-Day  |
                |         | Composite [Collection 5]                          |
                +---------+---------------------------------------------------+
                | MOD16A2 | MODIS/Terra Evapotranspiration (ET) 8-Day L4      |
                |         | Global Collection 5                               |
                +---------+---------------------------------------------------+
                | MOD17A2 | MODIS/Terra Gross Primary Production (GPP) 8-Day  |
                |         | L4 Global [Collection 5.1]                        |
                +---------+---------------------------------------------------+
                | MOD17A3 | MODIS/Terra Net Primary Production (NPP) Yearly   |
                |         | L4 Global 1km SIN Grid                            |
                +---------+---------------------------------------------------+
                | MYD09A1 | MODIS/Aqua Surface Reflectance (SREF) 8-Day L3    |
                |         | Global 500m SIN Grid                              |
                +---------+---------------------------------------------------+
                | MYD11A2 | MODIS/Aqua Land Surface Temperature/Emissivity    |
                |         | (LST)8-Day L3 Global 1km SIN Grid                 |
                +---------+---------------------------------------------------+
                | MYD13Q1 | MODIS/Aqua Vegetation Indices (NDVI/EVI) 16-Day   |
                |         | L3 Global 1km SIN Grid                            |
                +---------+---------------------------------------------------+
                | MYD15A2 | MODIS/Aqua Leaf Area Index (LAI) and Fraction of  |
                |         | Photosynthetically Active Radiation (FPAR) 8 Day  |
                |         | Composite                                         |
                +---------+---------------------------------------------------+
                | MYD17A2 | MODIS/Aqua Gross Primary Production (GPP) 8 Day   |
                |         | L4 Global                                         |
                +---------+---------------------------------------------------+

    ncdc_ghcnd  
                Download from the Global Historical Climatology Network
                - Daily. Requires registration and free API key.

                If you use this data, please read
                ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt
                about "How to cite".

                GHCN (Global Historical Climatology Network)-Daily is an
                integrated database of daily climate summaries from land
                surface stations across the globe. Like its monthly counterpart
                (GHCN-Monthly) , GHCN-Daily is comprised of daily climate
                records from numerous sources that have been integrated and
                subjected to a common suite of quality assurance reviews.

    ncdc_ghcnd_ftp
                Download from the Global Historical Climatology Network -
                Daily.

    ncdc_gs
                National Climatic Data Center Global Summary of the Month
                (GSOM) or Global Summary of the Year (GSOY). 
                Requires registration and free API key.

    ncdc_normal_ann
                National Climatic Data Center annual normals. Requires
                registration and free API key.

    ncdc_normal_dly
                National Climatic Data Center Daily Normals. Requires
                registration and free API key.

    ncdc_normal_hly
                National Climatic Data Center GHCND Monthly Summaries. Requires
                registration and free API key.

    ncdc_normal_mly
                National Climatic Data Center GHCND Monthly Summaries. Requires
                registration and free API key.

    ncdc_precip_15
                National Climatic Data Center 15 minute precipitation.
                Requires registration and free API key.

    ncdc_precip_hly
                National Climatic Data Center hourly precipitation.  Requires
                registration and free API key.

    ncdc_annual
                National Climatic Data Center annual data summaries.  Requires
                registration and free API key.

    ncdc_ghcndms
                National Climatic Data Center GHCND Monthly Summaries.
                Requires registration and free API key.

    ndbc
                Download data from the National Data Buoy Center.

    nwis
                Download time-series from the USGS National Water Information
                Service (NWIS). There are three main NWIS databases. The
                'tsgettoolbox' can currently pull from the Instantaneous Value
                database (--database=iv) for sub-daily interval data starting
                in 2007, and the Daily Values database (--database=dv).
                Detailed documentation is available at
                http://waterdata.usgs.gov/nwis

    twc                 
                Fetches Texas weather data

    unavco
                Detailed information at:
                http://www.unavco.com/data/web-services/web-services.html

                Returns 'met', 'pore_temperature', 'pore_pressure', 'tilt',
                'strain', or 'positional' data for UNAVCO stations.

    usgs_eddn   
                Download from the USGS Emergency Data Distribution Network

Usage Summary - Python Library
------------------------------
To use the tsgettoolbox in a project::

    from tsgettoolbox import tsgettoolbox

Refer to the API Documentation at `tsgettoolbox_documentation`_.

Development
~~~~~~~~~~~
Development is managed on bitbucket at
https://bitbucket.org/timcera/tsgettoolbox/overview.

.. _tsgettoolbox_documentation: https://timcera.bitbucket.io/tsgettoolbox/docsrc/index.html#tsgettoolbox-documentation
