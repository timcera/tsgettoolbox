"""
ncei_ghcnd_ftp      global station D:NCEI Global Historical Climatology
                    Network - Daily (GHCND)
ncei_ghcnd          global station D:Global Historical Climatology Network
                    - Daily (GHCND)
ncei_gsod           global station D:NCEI Global Summary of the Day (GSOD)
ncei_gsom           global station M:NCEI Global Summary of Month (GSOM)
ncei_gsoy           global station A:NCEI Global Summary of Year (GSOY)
ncei_normal_ann     global station A: NCEI annual normals
ncei_normal_dly     global station D:NCEI Daily Normals
ncei_normal_hly     global station H:NCEI Normal hourly
ncei_normal_mly     global station M:NCEI Monthly Summaries.
ncei_precip_15      global station 15T:NCEI 15 minute precipitation
ncei_precip_hly     global station H:NCEI hourly precipitation
ncei_annual         global station A:NCEI annual data summaries
ncei_ghcndms        global station M:NCEI GHCND Monthly Summaries
                    (GHCNDMS)
ncei_ish            global station H:Integrated Surface Database
"""

from collections import OrderedDict

import cltoolbox
import numpy as np
import pandas as pd
from cltoolbox.rst_text_formatter import RSTHelpFormatter as HelpFormatter
from toolbox_utils import tsutils

from tsgettoolbox import utils
from tsgettoolbox.cdo_api_py import Client
from tsgettoolbox.ulmo.ncdc.cirs.core import get_data

__all__ = [
    "ncei_ghcnd_ftp",
    "ncei_ghcnd",
    "ncei_gsod",
    "ncei_gsom",
    "ncei_gsoy",
    "ncei_nexrad2",
    "ncei_nexrad3",
    "ncei_normal_ann",
    "ncei_normal_dly",
    "ncei_normal_hly",
    "ncei_normal_mly",
    "ncei_precip_15",
    "ncei_precip_hly",
    "ncei_annual",
    "ncei_ghcndms",
    "ncei_ish",
    "ncei_cirs",
]

ncei_ghcnd_docstrings = {
    "info": r"""If you use this data, please read
    ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt about "How to
    cite".

    GHCN (Global Historical Climatology Network)-Daily is an integrated
    database of daily climate summaries from land surface stations
    across the globe. Like its monthly counterpart (GHCN-Monthly),
    GHCN-Daily is comprised of daily climate records from numerous
    sources that have been integrated and subjected to a common suite of
    quality assurance reviews.

    GHCN-Daily now contains records from over 75000 stations in 180
    countries and territories. Numerous daily variables are provided,
    including maximum and minimum temperature, total daily
    precipitation, snowfall, and snow depth; however, about two thirds
    of the stations report precipitation only.  Both the record length
    and period of record vary by station and cover intervals ranging
    from less than year to more than 175 years.

    The dataset is regularly reconstructed (usually every weekend) from
    its 20-plus data source components to ensure that GHCN-Daily is
    generally in sync with its growing list of constituent sources.
    During this process, quality assurance checks are applied to the
    full dataset. On most weekdays, GHCN-Daily station data are updated
    when possible from a variety of data streams, which also undergo
    a suite of quality checks.

    Some of the data provided here are based on data exchanged under the
    World Meteorological Organization (WMO) World Weather Watch Program
    according to WMO Resolution 40 (Cg-XII). This allows WMO member
    countries to place restrictions on the use or re-export of their
    data for commercial purposes outside of the receiving country. Those
    countries' data summaries and products which are available here are
    intended for free and unrestricted use in research, education, and
    other non-commercial activities. For non-U.S. locations' data, the
    data or any derived product shall not be provided to other users or
    be used for the re-export of commercial services.

    The five core values are:

    +------+----------------------------+
    | Code | Description                |
    +======+============================+
    | TMAX | Temperature MAX (degree C) |
    +------+----------------------------+
    | TMIN | Temperature MIN (degree C) |
    +------+----------------------------+
    | PRCP | PReCiPitation (mm)         |
    +------+----------------------------+
    | SNOW | SNOWfall (mm)              |
    +------+----------------------------+
    | SNWD | SNoW Depth (mm)            |
    +------+----------------------------+

    Other possible data collected:

    +------+-------------------------------------------------------------------+
    | Code | Description                                                       |
    +======+===================================================================+
    | ACMC | Average cloudiness midnight to midnight from 30-second ceilometer |
    |      | data (percent)                                                    |
    +------+-------------------------------------------------------------------+
    | ACMH | Average cloudiness midnight to midnight from manual observations  |
    |      | (percent)                                                         |
    +------+-------------------------------------------------------------------+
    | ACSC | Average cloudiness sunrise to sunset from 30-second ceilometer    |
    |      | data (percent)                                                    |
    +------+-------------------------------------------------------------------+
    | ACSH | Average cloudiness sunrise to sunset from manual observations     |
    |      | (percent)                                                         |
    +------+-------------------------------------------------------------------+
    | AWDR | Average daily wind direction (degrees)                            |
    +------+-------------------------------------------------------------------+
    | AWND | Average daily wind speed (meters per second)                      |
    +------+-------------------------------------------------------------------+
    | DAEV | Number of days included in the multiday evaporation total (MDEV)  |
    +------+-------------------------------------------------------------------+
    | DAPR | Number of days included in the multiday precipitation total       |
    |      | (MDPR)                                                            |
    +------+-------------------------------------------------------------------+
    | DASF | Number of days included in the multiday snowfall total (MDSF)     |
    +------+-------------------------------------------------------------------+
    | DATN | Number of days included in the multiday minimum temperature       |
    |      | (MDTN)                                                            |
    +------+-------------------------------------------------------------------+
    | DATX | Number of days included in the multiday maximum temperature       |
    |      | (MDTX)                                                            |
    +------+-------------------------------------------------------------------+
    | DAWM | Number of days included in the multiday wind movement (MDWM)      |
    +------+-------------------------------------------------------------------+
    | DWPR | Number of days with non-zero precipitation included in multiday   |
    |      | precipitation total (MDPR)                                        |
    +------+-------------------------------------------------------------------+
    | EVAP | Evaporation of water from evaporation pan (mm)                    |
    +------+-------------------------------------------------------------------+
    | FMTM | Time of fastest mile or fastest 1-minute wind (hours and minutes, |
    |      | i.e., HHMM)                                                       |
    +------+-------------------------------------------------------------------+
    | FRGB | Base of frozen ground layer (cm)                                  |
    +------+-------------------------------------------------------------------+
    | FRGT | Top of frozen ground layer (cm)                                   |
    +------+-------------------------------------------------------------------+
    | FRTH | Thickness of frozen ground layer (cm)                             |
    +------+-------------------------------------------------------------------+
    | GAHT | Difference between river and gauge height (cm)                    |
    +------+-------------------------------------------------------------------+
    | MDEV | Multiday evaporation total (use with DAEV)                        |
    +------+-------------------------------------------------------------------+
    | MDPR | Multiday precipitation total (mm; use with DAPR and DWPR, if      |
    |      | available)                                                        |
    +------+-------------------------------------------------------------------+
    | MDSF | Multiday snowfall total                                           |
    +------+-------------------------------------------------------------------+
    | MDTN | Multiday minimum temperature (degrees C; use with DATN)           |
    +------+-------------------------------------------------------------------+
    | MDTX | Multiday maximum temperature (degrees C; use with DATX)           |
    +------+-------------------------------------------------------------------+
    | MDWM | Multiday wind movement (km)                                       |
    +------+-------------------------------------------------------------------+
    | MNPN | Daily minimum temperature of water in an evaporation pan (degrees |
    |      | C)                                                                |
    +------+-------------------------------------------------------------------+
    | MXPN | Daily maximum temperature of water in an evaporation pan (degrees |
    |      | C)                                                                |
    +------+-------------------------------------------------------------------+
    | PGTM | Peak gust time (hours and minutes, i.e., HHMM)                    |
    +------+-------------------------------------------------------------------+
    | PSUN | Daily percent of possible sunshine (percent)                      |
    +------+-------------------------------------------------------------------+
    | TAVG | Average temperature (degrees C) [Note that TAVG from source 'S'   |
    |      | corresponds to an average for the period ending at 2400 UTC       |
    |      | rather than local midnight]                                       |
    +------+-------------------------------------------------------------------+
    | THIC | Thickness of ice on water (mm)                                    |
    +------+-------------------------------------------------------------------+
    | TOBS | Temperature at the time of observation (degrees C)                |
    +------+-------------------------------------------------------------------+
    | TSUN | Daily total sunshine (minutes)                                    |
    +------+-------------------------------------------------------------------+
    | WDF1 | Direction of fastest 1-minute wind (degrees)                      |
    +------+-------------------------------------------------------------------+
    | WDF2 | Direction of fastest 2-minute wind (degrees)                      |
    +------+-------------------------------------------------------------------+
    | WDF5 | Direction of fastest 5-second wind (degrees)                      |
    +------+-------------------------------------------------------------------+
    | WDFG | Direction of peak wind gust (degrees)                             |
    +------+-------------------------------------------------------------------+
    | WDFI | Direction of highest instantaneous wind (degrees)                 |
    +------+-------------------------------------------------------------------+
    | WDFM | Fastest mile wind direction (degrees)                             |
    +------+-------------------------------------------------------------------+
    | WDMV | 24-hour wind movement (km)                                        |
    +------+-------------------------------------------------------------------+
    | WESD | Water equivalent of snow on the ground (mm)                       |
    +------+-------------------------------------------------------------------+
    | WESF | Water equivalent of snowfall (mm)                                 |
    +------+-------------------------------------------------------------------+
    | WSF1 | Fastest 1-minute wind speed (meters per second)                   |
    +------+-------------------------------------------------------------------+
    | WSF2 | Fastest 2-minute wind speed (meters per second)                   |
    +------+-------------------------------------------------------------------+
    | WSF5 | Fastest 5-second wind speed (meters per second)                   |
    +------+-------------------------------------------------------------------+
    | WSFG | Peak gust wind speed (meters per second)                          |
    +------+-------------------------------------------------------------------+
    | WSFI | Highest instantaneous wind speed (meters per second)              |
    +------+-------------------------------------------------------------------+
    | WSFM | Fastest mile wind speed (meters per second)                       |
    +------+-------------------------------------------------------------------+

    SNXY and SXXY Table

    +-------+------------------------------------------------------------------+
    | SNXY  | Minimum soil temperature (degrees C) where 'X' corresponds to a  |
    |       | code for ground cover and 'Y' corresponds to a code for soil     |
    |       | depth.                                                           |
    +=======+==================================================================+
    |       | Ground cover codes include the following:                        |
    +-------+------------------------------------------------------------------+
    | X = 0 | unknown                                                          |
    +-------+------------------------------------------------------------------+
    | X = 1 | grass                                                            |
    +-------+------------------------------------------------------------------+
    | X = 2 | fallow                                                           |
    +-------+------------------------------------------------------------------+
    | X = 3 | bare ground                                                      |
    +-------+------------------------------------------------------------------+
    | X = 4 | brome grass                                                      |
    +-------+------------------------------------------------------------------+
    | X = 5 | sod                                                              |
    +-------+------------------------------------------------------------------+
    | X = 6 | straw mulch                                                      |
    +-------+------------------------------------------------------------------+
    | X = 7 | grass muck                                                       |
    +-------+------------------------------------------------------------------+
    | X = 8 | bare muck                                                        |
    +-------+------------------------------------------------------------------+
    |       | Depth codes include the following:                               |
    +-------+------------------------------------------------------------------+
    | Y = 1 | 5 cm                                                             |
    +-------+------------------------------------------------------------------+
    | Y = 2 | 10 cm                                                            |
    +-------+------------------------------------------------------------------+
    | Y = 3 | 20 cm                                                            |
    +-------+------------------------------------------------------------------+
    | Y = 4 | 50 cm                                                            |
    +-------+------------------------------------------------------------------+
    | Y = 5 | 100 cm                                                           |
    +-------+------------------------------------------------------------------+
    | Y = 6 | 150 cm                                                           |
    +-------+------------------------------------------------------------------+
    | Y = 7 | 180 cm                                                           |
    +-------+------------------------------------------------------------------+
    | SXXY  | Maximum soil temperature (degrees C) where the second 'X'        |
    |       | corresponds to a code for ground cover and 'Y' corresponds to a  |
    |       | code for soil depth. See SNXY for ground cover and depth codes.  |
    +-------+------------------------------------------------------------------+

    WTXX and WVXX Table

    +------+-------------------------------------------------------------------+
    | XX   | Description                                                       |
    +======+===================================================================+
    | 01   | Fog, ice fog, or freezing fog (may include heavy fog)             |
    +------+-------------------------------------------------------------------+
    | 02   | Heavy fog or heaving freezing fog (not always distinguished from  |
    |      | fog)                                                              |
    +------+-------------------------------------------------------------------+
    | 03   | Thunder                                                           |
    +------+-------------------------------------------------------------------+
    | 04   | Ice pellets, sleet, snow pellets, or small hail                   |
    +------+-------------------------------------------------------------------+
    | 05   | Hail (may include small hail)                                     |
    +------+-------------------------------------------------------------------+
    | 06   | Glaze or rime                                                     |
    +------+-------------------------------------------------------------------+
    | 07   | Dust, volcanic ash, blowing dust, blowing sand, or blowing        |
    |      | obstruction                                                       |
    +------+-------------------------------------------------------------------+
    | 08   | Smoke or haze                                                     |
    +------+-------------------------------------------------------------------+
    | 09   | Blowing or drifting snow                                          |
    +------+-------------------------------------------------------------------+
    | 11   | High or damaging winds                                            |
    +------+-------------------------------------------------------------------+
    | 12   | Blowing spray                                                     |
    +------+-------------------------------------------------------------------+
    | 13   | Mist                                                              |
    +------+-------------------------------------------------------------------+
    | 14   | Drizzle                                                           |
    +------+-------------------------------------------------------------------+
    | 15   | Freezing drizzle                                                  |
    +------+-------------------------------------------------------------------+
    | 16   | Rain (may include freezing rain, drizzle, and freezing drizzle)   |
    +------+-------------------------------------------------------------------+
    | 17   | Freezing rain                                                     |
    +------+-------------------------------------------------------------------+
    | 18   | Snow, snow pellets, snow grains, or ice crystals                  |
    +------+-------------------------------------------------------------------+
    | 19   | Unknown source of precipitation                                   |
    +------+-------------------------------------------------------------------+
    | 21   | Ground fog                                                        |
    +------+-------------------------------------------------------------------+
    | 22   | Ice fog or freezing fog                                           |
    +------+-------------------------------------------------------------------+
    | WVXX | Weather in the Vicinity where XX has one of the following values  |
    |      | described above: 01, 03, 07, 18, and 20                           |
    +------+-------------------------------------------------------------------+

    """,
    "stationid": r"""stationid
        The station id. from the first column of
        ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt""",
    "datatypeid": r"""datatypeid : str
        The following table lists the datatypes available for the 'ghcnd'
        dataset.  If the datatypeid is not given defaults to getting all data
        available at that station for the requested time period.

        +------+---------------------------------------------------------------+
        | Code | Description                                                   |
        +======+===============================================================+
        | TMAX | Monthly/Annual Maximum Temperature. Average of daily maximum  |
        |      | temperature given in C or F depending on user specification.  |
        |      | Missing if more than 5 days within the month are missing or   |
        |      | flagged or if more than 3 consecutive values within the month |
        |      | are missing or flagged.  DaysMissing: Flag indicating number  |
        |      | of days missing or flagged (from 1 to 5).                     |
        +------+---------------------------------------------------------------+
        | TMIN | Monthly/Annual Minimum Temperature. Average of daily minimum  |
        |      | temperature given in C or F depending on user specification.  |
        |      | Missing if more than 5 days within the month are missing or   |
        |      | flagged or if more than 3 consecutive values within the month |
        |      | are missing or flagged.  DaysMissing: Flag indicating number  |
        |      | of days missing or flagged (from 1 to 5).                     |
        +------+---------------------------------------------------------------+
        | TAVG | Average Monthly/Annual Temperature. Computed by adding the    |
        |      | unrounded monthly/annual maximum and minimum temperatures and |
        |      | dividing by 2. Given in C or F depending on user              |
        |      | specification. Missing if more than 5 days within the month   |
        |      | are missing or flagged or if more than 3 consecutive values   |
        |      | within the month are missing or flagged. DaysMissing: Flag    |
        |      | indicating number of days missing or flagged (from 1 to 5).   |
        +------+---------------------------------------------------------------+
        | EMXT | Extreme maximum temperature for month/year. Highest daily     |
        |      | maximum temperature for the month/year. Given in C or F       |
        |      | depending on user specification.                              |
        +------+---------------------------------------------------------------+
        | DYXT | Day of the EMXT for the month/year.                           |
        +------+---------------------------------------------------------------+
        | EMNT | Extreme minimum temperature for month/year. Lowest daily      |
        |      | minimum temperature for the month/year. Given in C or F       |
        |      | depending on user specification.                              |
        +------+---------------------------------------------------------------+
        | DYXT | Day of the EMNT for the month/year.                           |
        +------+---------------------------------------------------------------+
        | DX90 | Number of days with maximum temperature >= 90 degrees F/32.2  |
        |      | degrees C.                                                    |
        +------+---------------------------------------------------------------+
        | DX70 | Number of days with maximum temperature >= 70 degrees F/21.1  |
        |      | degrees C.                                                    |
        +------+---------------------------------------------------------------+
        | DX32 | Number of days with maximum temperature <= 32 degrees F/0     |
        |      | degrees C.                                                    |
        +------+---------------------------------------------------------------+
        | DT32 | Number of days with minimum temperature <= 32 degrees F/0     |
        |      | degrees C.                                                    |
        +------+---------------------------------------------------------------+
        | DT00 | Number of days with maximum temperature <= 0 degrees F/-17.8  |
        |      | degrees C.                                                    |
        +------+---------------------------------------------------------------+
        | HTDD | Heating Degree Days. Computed when daily average temperature  |
        |      | is less than 65 degrees F/18.3 degrees C. HDD = 65(F)/18.3(C) |
        |      | - mean daily temperature. Each day is summed to produce a     |
        |      | monthly/annual total. Annual totals are computed based on a   |
        |      | July - June year in Northern Hemisphere and January -         |
        |      | December year in Southern Hemisphere. Given in C or F degrees |
        |      | depending on user specification.                              |
        +------+---------------------------------------------------------------+
        | CLDD | Cooling Degree Days. Computed when daily average temperature  |
        |      | is more than 65 degrees F/18.3 degrees C. CDD = mean daily    |
        |      | temperature - 65 degrees F/18.3 degrees C. Each day is summed |
        |      | to produce a monthly/annual total. Annual totals are computed |
        |      | based on a January - December year in Northern Hemisphere and |
        |      | July - June year in Southern Hemisphere. Given in C or F      |
        |      | degrees depending on user specification.                      |
        +------+---------------------------------------------------------------+
        | PRCP | Total Monthly/Annual Precipitation. Given in in or mm         |
        |      | depending on user specification. Measurement Flags: T is used |
        |      | for trace amount, a is used for any accumulation within a     |
        |      | month/year that includes missing days. If no days are         |
        |      | missing, no flag is used. Source Flag: Source flag from GHCN- |
        |      | Daily (see separate documentation for GHCN- Daily). Days Miss |
        |      | Flag: Number of days missing or flagged.                      |
        +------+---------------------------------------------------------------+
        | EMXP | Highest daily total of precipitation in the month/year. Given |
        |      | in in or mm depending on user specification.                  |
        +------+---------------------------------------------------------------+
        | DYXP | Day that EMXP for the month/year occurred.                    |
        +------+---------------------------------------------------------------+
        | DP01 | Number of days with >= 0.01 inch/0.254 millimeter in the      |
        |      | month/year.                                                   |
        +------+---------------------------------------------------------------+
        | DP05 | Number of days with >= 0.5 inch/12.7 mm in the month/year.    |
        +------+---------------------------------------------------------------+
        | DP10 | Number of days with >= 1.00 inch/25.4 mm in the month/year.   |
        +------+---------------------------------------------------------------+
        | SNOW | Total Monthly/Annual Snowfall. Given in in or mm depending on |
        |      | user specification. Measurement Flags: T is used for trace    |
        |      | amount, a is used for any accumulation within a month/year    |
        |      | that includes missing days. If no days are missing, no flag   |
        |      | is used. Source Flag: Source flag from GHCN- Daily (see       |
        |      | separate documentation for GHCN-Daily). Days Miss Flag:       |
        |      | Number of days missing or flagged.                            |
        +------+---------------------------------------------------------------+
        | EMSN | Highest daily snowfall in the month/year. Given in in or mm   |
        |      | depending on user specification.                              |
        +------+---------------------------------------------------------------+
        | DYSN | Day EMSN for the month/year occurred.                         |
        +------+---------------------------------------------------------------+
        | DSNW | Number of days with snowfall >= 1 inch/25 mm.                 |
        +------+---------------------------------------------------------------+
        | DSND | Number of days with snow depth >= 1 inch/25 mm.               |
        +------+---------------------------------------------------------------+
        | EMSD | Highest daily snow depth in the month/year. Given in in or mm |
        |      | depending on user specification.                              |
        +------+---------------------------------------------------------------+
        | DYSD | Day EMSD for the month/year occurred.                         |
        +------+---------------------------------------------------------------+
        | EVAP | Total Monthly/Annual Evaporation. Given in in or mm depending |
        |      | on user specification. Measurement Flags: T is used for trace |
        |      | amount, a is used for any accumulation within a month/year    |
        |      | that includes missing days. If no days are missing, no flag   |
        |      | is used. Source Flag: Source flag from GHCN- Daily (see       |
        |      | separate documentation for GHCN- Daily). Days Miss Flag:      |
        |      | Number of days missing or flagged.                            |
        +------+---------------------------------------------------------------+
        | MNPN | Monthly/Annual Mean Minimum Temperature of evaporation pan    |
        |      | water. Given in C or F depending on user specification.       |
        |      | Missing if more than 5 days within the month are missing or   |
        |      | flagged or if more than 3 consecutive values within the month |
        |      | are missing or flagged. DaysMissing: Flag indicating number   |
        |      | of days missing or flagged (from 1 to 5).                     |
        +------+---------------------------------------------------------------+
        | MXPN | Monthly/Annual Mean Maximum Temperature of evaporation pan    |
        |      | water. Given in C or F depending on user specification.       |
        |      | Missing if more than 5 days within the month are missing or   |
        |      | flagged or if more than 3 consecutive values within the month |
        |      | are missing or flagged. DaysMissing: Flag indicating number   |
        |      | of days missing or flagged (from 1 to 5).                     |
        +------+---------------------------------------------------------------+
        | WDMV | Total Monthly/Annual Wind Movement over evaporation pan.      |
        |      | Given in miles or kilometers depending on user specification. |
        |      | Days Miss Flag: Number of days missing or flagged.            |
        +------+---------------------------------------------------------------+
        | TSUN | Daily total sunshine in minutes. Days Miss Flag: Number of    |
        |      | days missing or flagged.                                      |
        +------+---------------------------------------------------------------+
        | PSUN | Monthly/Annual Average of the daily percents of possible      |
        |      | sunshine. Days Miss Flag: Number of days missing or flagged.  |
        +------+---------------------------------------------------------------+
        | AWND | Monthly/Annual Average Wind Speed. Given in miles per hour or |
        |      | meters per second depending on user specification. Missing if |
        |      | more than 5 days within the month are missing or flagged or   |
        |      | if more than 3 consecutive values within the month are        |
        |      | missing or flagged. DaysMissing: Flag indicating number of    |
        |      | days missing or flagged (from 1 to 5).                        |
        +------+---------------------------------------------------------------+
        | WSFM | Maximum Wind Speed/Fastest Mile. Maximum wind speed for the   |
        |      | month/year reported as the fastest mile. Given in miles per   |
        |      | hour or meters per second depending on user specification.    |
        |      | Missing if more than 5 days within the month are missing or   |
        |      | flagged or if more than 3 consecutive values within the month |
        |      | are missing or flagged. DaysMissing: Flag indicating number   |
        |      | of days missing or flagged (from 1 to 5).                     |
        +------+---------------------------------------------------------------+
        | WDFM | Wind Direction for Maximum Wind Speed/Fastest Mile (WSFM).    |
        |      | Given in 360-degree compass point directions (e.g. 360 =      |
        |      | north, 180 = south, etc.).                                    |
        +------+---------------------------------------------------------------+
        | WSF2 | Maximum Wind Speed/Fastest 2-minute. Maximum wind speed for   |
        |      | the month/year reported as the fastest 2-minute. Given in     |
        |      | miles per hour or meters per second depending on user         |
        |      | specification.  Missing if more than 5 days within the month  |
        |      | are missing or flagged or if more than 3 consecutive values   |
        |      | within the month are missing or flagged. DaysMissing: Flag    |
        |      | indicating number of days missing or flagged (from 1 to 5).   |
        +------+---------------------------------------------------------------+
        | WDF2 | Wind Direction for Maximum Wind Speed/Fastest 2-Minute        |
        |      | (WSF2). Given in 360-degree compass point directions (e.g.    |
        |      | 360 = north, 180 = south, etc.).                              |
        +------+---------------------------------------------------------------+
        | WSF1 | Maximum Wind Speed/Fastest 1-minute. Maximum wind speed for   |
        |      | the month/year reported as the fastest 1-minute. Given in     |
        |      | miles per hour or meters per second depending on user         |
        |      | specification.  Missing if more than 5 days within the month  |
        |      | are missing or flagged or if more than 3 consecutive values   |
        |      | within the month are missing or flagged. DaysMissing: Flag    |
        |      | indicating number of days missing or flagged (from 1 to 5).   |
        +------+---------------------------------------------------------------+
        | WDF1 | Wind Direction for Maximum Wind Speed/Fastest 1-Minute        |
        |      | (WSF1). Given in 360-degree compass point directions (e.g.    |
        |      | 360 = north, 180 = south, etc.). Missing if more than 5 days  |
        |      | within the month are missing or flagged or if more than 3     |
        |      | consecutive values within the month are missing or flagged.   |
        |      | DaysMissing: Flag indicating number of days missing or        |
        |      | flagged (from 1 to 5).                                        |
        +------+---------------------------------------------------------------+
        | WSFG | Peak Wind Gust Speed. Maximum wind gust for the month/year.   |
        |      | Given in miles per hour or second depending on user           |
        |      | specification. Missing if more than 5 days within the month   |
        |      | are missing or flagged or if more than 3 consecutive values   |
        |      | within the month are missing or flagged. DaysMissing: Flag    |
        |      | indicating number of days missing or flagged (from 1 to 5).   |
        +------+---------------------------------------------------------------+
        | WDFG | Wind Direction for Peak Wind Gust Speed (WSFG). Given in      |
        |      | 360-degree compass point directions (e.g. 360 = north, 180 =  |
        |      | south, etc.). Missing if more than 5 days within the month    |
        |      | are missing or flagged or if more than 3 consecutive values   |
        |      | within the month are missing or flagged. DaysMissing: Flag    |
        |      | indicating number of days missing or flagged (from 1 to 5).   |
        +------+---------------------------------------------------------------+
        | WSF5 | Peak Wind Gust Speed - Fastest 5-second wind. Maximum wind    |
        |      | gust for the month/year. Given in miles per hour or second    |
        |      | depending on user specification. Missing if more than 5 days  |
        |      | within the month are missing or flagged or if more than 3     |
        |      | consecutive values within the month are missing or flagged.   |
        |      | DaysMissing: Flag indicating number of days missing or        |
        |      | flagged (from 1 to 5).                                        |
        +------+---------------------------------------------------------------+
        | WDF5 | Wind Direction for Peak Wind Gust Speed - Fastest 5-second    |
        |      | (WSF5). Given in 360-degree compass point directions (e.g.    |
        |      | 360 = north, 180 = south, etc.). Missing if more than 5 days  |
        |      | within the month are missing or flagged or if more than 3     |
        |      | consecutive values within the month are missing or flagged.   |
        |      | DaysMissing: Flag indicating number of days missing or        |
        |      | flagged (from 1 to 5).                                        |
        +------+---------------------------------------------------------------+
        | WSF3 | Peak Wind Gust Speed - Fastest 3-second wind. Maximum wind    |
        |      | gust for the month/year. Given in miles per hour or second    |
        |      | depending on user specification. Missing if more than 5 days  |
        |      | within the month are missing or flagged or if more than 3     |
        |      | consecutive values within the month are missing or flagged.   |
        |      | DaysMissing: Flag indicating number of days missing or        |
        |      | flagged (from 1 to 5).                                        |
        +------+---------------------------------------------------------------+
        | WDF3 | Wind Direction for Peak Wind Gust Speed - Fastest 5-second    |
        |      | (WSF3). Given in 360-degree compass point directions (e.g.    |
        |      | 360 = north, 180 = south, etc.). Missing if more than 5 days  |
        |      | within the month are missing or flagged or if more than 3     |
        |      | consecutive values within the month are missing or flagged.   |
        |      | DaysMissing: Flag indicating number of days missing or        |
        |      | flagged (from 1 to 5).                                        |
        +------+---------------------------------------------------------------+
        | MXyz | Monthly/Annual Mean of daily maximum soil temperature given   |
        |      | in C or F depending on user specification. Missing if more    |
        |      | than 5 days within the month are missing or flagged or if     |
        |      | more than 3 consecutive values within the month are missing   |
        |      | or flagged. DaysMissing: Flag indicating number of days       |
        |      | missing or flagged (from 1 to 5).                             |
        |      | ------------------------------------------------------------- |
        |      | "y" values for MXyz, MNyz, HXyz, HNyz, LXyz, and LNyz         |
        |      | ------------------------------------------------------------- |
        |      | 1=grass                                                       |
        |      | ------------------------------------------------------------- |
        |      | 2=fallow                                                      |
        |      | ------------------------------------------------------------- |
        |      | 3=bare ground                                                 |
        |      | ------------------------------------------------------------- |
        |      | 4=brome grass                                                 |
        |      | ------------------------------------------------------------- |
        |      | 5=sod                                                         |
        |      | ------------------------------------------------------------- |
        |      | 6=straw mulch                                                 |
        |      | ------------------------------------------------------------- |
        |      | 7=grass muck                                                  |
        |      | ------------------------------------------------------------- |
        |      | 8=bare muck                                                   |
        |      | ------------------------------------------------------------- |
        |      | 0=unknown                                                     |
        |      | ------------------------------------------------------------- |
        |      | "z" values for HXyz, HNyz, LXyz, and LNyz:                    |
        |      | ------------------------------------------------------------- |
        |      | 1= 2 in or 5 cm depth                                         |
        |      | ------------------------------------------------------------- |
        |      | 2= 4 in or 10 cm depth                                        |
        |      | ------------------------------------------------------------- |
        |      | 3= 8 in or 20 cm depth                                        |
        |      | ------------------------------------------------------------- |
        |      | 4= 20 in or 50 cm depth                                       |
        |      | ------------------------------------------------------------- |
        |      | 5= 40 in or 100 cm depth                                      |
        |      | ------------------------------------------------------------- |
        |      | 6= 60 in or                                                   |
        |      | ------------------------------------------------------------- |
        |      | 150 cm depth                                                  |
        |      | ------------------------------------------------------------- |
        |      | 7= 72 in or 180 cm depth                                      |
        |      | ------------------------------------------------------------- |
        |      | other=unknown                                                 |
        +------+---------------------------------------------------------------+
        | MNyz | Monthly/Annual Mean of daily minimum soil temperature given   |
        |      | in C or F depending on user specification. Missing if more    |
        |      | than 5 days within the month are missing or flagged or if     |
        |      | more than 3 consecutive values within the month are missing   |
        |      | or flagged. DaysMissing: Flag indicating number of days       |
        |      | missing or flagged (from 1 to 5). See description of flags in |
        |      | MXyz.                                                         |
        +------+---------------------------------------------------------------+
        | HXyz | Highest maximum soil temperature for the month/year given in  |
        |      | C or F depending on user specification. Missing if more than  |
        |      | 5 days within the month are missing or flagged or if more     |
        |      | than 3 consecutive values within the month are missing or     |
        |      | flagged. DaysMissing: Flag indicating number of days missing  |
        |      | or flagged (from 1 to 5). See description of flags in MXyz.   |
        +------+---------------------------------------------------------------+
        | HNyz | Highest minimum soil temperature for the month/year given in  |
        |      | C or F depending on user specification. Missing if more than  |
        |      | 5 days within the month are missing or flagged or if more     |
        |      | than 3 consecutive values within the month are missing or     |
        |      | flagged. DaysMissing: Flag indicating number of days missing  |
        |      | or flagged (from 1 to 5). See description of flags in MXyz.   |
        +------+---------------------------------------------------------------+
        | LXyz | Lowest maximum soil temperature for the month/year given in C |
        |      | or F depending on user specification. Missing if more than 5  |
        |      | days within the month are missing or flagged or if more than  |
        |      | 3 consecutive values within the month are missing or flagged. |
        |      | DaysMissing: Flag indicating number of days missing or        |
        |      | flagged (from 1 to 5). See description of flags in MXyz.      |
        +------+---------------------------------------------------------------+
        | LNyz | Lowest minimum soil temperature for the month/year given in C |
        |      | or F depending on user specification. Missing if more than 5  |
        |      | days within the month are missing or flagged or if more than  |
        |      | 3 consecutive values within the month are missing or flagged. |
        |      | DaysMissing: Flag indicating number of days missing or        |
        |      | flagged (from 1 to 5). See description of flags in MXyz.      |
        +------+---------------------------------------------------------------+
        | HDSD | Heating Degree Days (season-to-date). Running total of        |
        |      | monthly heating degree days through the end of the most       |
        |      | recent month. Each month is summed to produce a season-to-    |
        |      | date total. Season starts in July in Northern Hemisphere and  |
        |      | January in Southern Hemisphere. Given in C or F degrees       |
        |      | depending on user specification.                              |
        +------+---------------------------------------------------------------+
        | CDSD | Cooling Degree Days (season-to-date). Running total of        |
        |      | monthly cooling degree days through the end of the most       |
        |      | recent month. Each month is summed to produce a season-to-    |
        |      | date total. Season starts in January in Northern Hemisphere   |
        |      | and July in Southern Hemisphere. Given in C or F degrees      |
        |      | depending on user specification.                              |
        +------+---------------------------------------------------------------+
        | FZFx | (x= 0-9) First/Last Freeze Days. Annual element only. Years   |
        |      | begins on August 1. Missing if more than 5 days within the    |
        |      | month are missing or flagged or if more than 3 consecutive    |
        |      | values within the month are missing or flagged. DaysMissing:  |
        |      | Flag indicating number of days missing or flagged (from 1 to  |
        |      | 5). Given in format tttt.tyyyymmdds where tttt.t is           |
        |      | temperature in degrees F or C depending on user               |
        |      | specification, yyyy is the year, mm is the month, dd is the   |
        |      | day of the month and s is a source flag.                      |
        |      | ------------------------------------------------------------- |
        |      | "x" values for FZFx                                           |
        |      | ------------------------------------------------------------- |
        |      | 0 = first minimum temperature <= 32 degrees F/0 degrees C     |
        |      | ------------------------------------------------------------- |
        |      | 1 = first minimum temperature <= 28 degrees F/-2.2 degrees C  |
        |      | ------------------------------------------------------------- |
        |      | 2 = first minimum temperature <= 24 degrees F/-4.4 degrees C  |
        |      | ------------------------------------------------------------- |
        |      | 3 = first minimum temperature <= 20 degrees F/-6.7 degrees C  |
        |      | ------------------------------------------------------------- |
        |      | 4 = first minimum temperature <= 16 degrees F/-8.9 degrees C  |
        |      | ------------------------------------------------------------- |
        |      | 5 = last minimum temperature <= 32 degrees F/0 degrees C      |
        |      | ------------------------------------------------------------- |
        |      | 6 = last minimum temperature <= 28 degrees F/-2.2 degrees C   |
        |      | ------------------------------------------------------------- |
        |      | 7 = last minimum temperature <= 24 degrees F/-4.4 degrees C   |
        |      | ------------------------------------------------------------- |
        |      | 8 = last minimum temperature <= 20 degrees F/-6.7 degrees C   |
        |      | ------------------------------------------------------------- |
        |      | 9 = last minimum temperature <= 16 degrees F/-8.9 degrees C   |
        +------+---------------------------------------------------------------+
        """,
    "datatype_temp": """datatypeid : str
        The following table lists the datatypes available for the annual
        dataset.  If the datatypeid is not given defaults to getting all data
        available at that station.

        +--------+-------------------------------------------------------------+
        | Code   | Description                                                 |
        +========+=============================================================+
        | HN7290 | Highest minimum soil temperature for the month (cover:      |
        |        | grass muck                                                  |
        +--------+-------------------------------------------------------------+
        | HN8190 | Highest minimum soil temperature for the month (cover: bare |
        |        | muck                                                        |
        +--------+-------------------------------------------------------------+
        | HN8290 | Highest minimum soil temperature for the month (cover: bare |
        |        | muck                                                        |
        +--------+-------------------------------------------------------------+
        | HN8390 | Highest minimum soil temperature for the month (cover: bare |
        |        | muck                                                        |
        +--------+-------------------------------------------------------------+
        | HO84A0 | Highest soil temperature at observation time (cover: bare   |
        |        | muck                                                        |
        +--------+-------------------------------------------------------------+
        | HO85A0 | Highest soil temperature at observation time (cover: bare   |
        |        | muck                                                        |
        +--------+-------------------------------------------------------------+
        | HX7290 | Highest maximum soil temperature for the month (cover:      |
        |        | grass muck                                                  |
        +--------+-------------------------------------------------------------+
        | HX8190 | Highest maximum soil temperature for the month (cover: bare |
        |        | muck                                                        |
        +--------+-------------------------------------------------------------+
        | HX8290 | Highest maximum soil temperature for the month (cover: bare |
        |        | muck                                                        |
        +--------+-------------------------------------------------------------+
        | HX8390 | Highest maximum soil temperature for the month (cover: bare |
        |        | muck                                                        |
        +--------+-------------------------------------------------------------+
        | LN7290 | Lowest minimum soil temperature for the month (cover: grass |
        |        | muck                                                        |
        +--------+-------------------------------------------------------------+
        | LN8190 | Lowest minimum soil temperature for the month (cover: bare  |
        |        | muck                                                        |
        +--------+-------------------------------------------------------------+
        | LN8290 | Lowest minimum soil temperature for the month (cover: bare  |
        |        | muck                                                        |
        +--------+-------------------------------------------------------------+
        | LN8390 | Lowest minimum soil temperature for the month (cover: bare  |
        |        | muck                                                        |
        +--------+-------------------------------------------------------------+
        | LO84A0 | Lowest soil temperature at observation time (cover: bare    |
        |        | muck                                                        |
        +--------+-------------------------------------------------------------+
        | LO85A0 | Lowest soil temperature at observation time (cover: bare    |
        |        | muck                                                        |
        +--------+-------------------------------------------------------------+
        | LX7290 | Lowest maximum soil temperature for the month (cover: grass |
        |        | muck                                                        |
        +--------+-------------------------------------------------------------+
        | LX8190 | Lowest maximum soil temperature for the month (cover: bare  |
        |        | muck                                                        |
        +--------+-------------------------------------------------------------+
        | LX8290 | Lowest maximum soil temperature for the month (cover: bare  |
        |        | muck                                                        |
        +--------+-------------------------------------------------------------+
        | LX8390 | Lowest maximum soil temperature for the month (cover: bare  |
        |        | muck                                                        |
        +--------+-------------------------------------------------------------+
        | MN7290 | Monthly mean minimum soil temperature (cover: grass muck    |
        +--------+-------------------------------------------------------------+
        | MN8190 | Monthly mean minimum soil temperature (cover: bare muck     |
        +--------+-------------------------------------------------------------+
        | MN8290 | Monthly mean minimum soil temperature (cover: bare muck     |
        +--------+-------------------------------------------------------------+
        | MN8390 | Monthly mean minimum soil temperature (cover: bare muck     |
        +--------+-------------------------------------------------------------+
        | MO84A0 | Monthly mean soil temperature at observation time (cover:   |
        |        | bare muck                                                   |
        +--------+-------------------------------------------------------------+
        | MO85A0 | Monthly mean soil temperature at observation time (cover:   |
        |        | bare muck                                                   |
        +--------+-------------------------------------------------------------+
        | MX7290 | Monthly mean maximum soil temperature (cover: grass muck    |
        +--------+-------------------------------------------------------------+
        | MX8190 | Monthly mean maximum soil temperature (cover: bare muck     |
        +--------+-------------------------------------------------------------+
        | MX8290 | Monthly mean maximum soil temperature (cover: bare muck     |
        +--------+-------------------------------------------------------------+
        | MX8390 | Monthly mean maximum soil temperature (cover: bare muck     |
        +--------+-------------------------------------------------------------+
        | HN6190 | Highest minimum soil temperature for the month (cover:      |
        |        | straw mulch                                                 |
        +--------+-------------------------------------------------------------+
        | LN6190 | Lowest minimum soil temperature for the month (cover: straw |
        |        | mulch                                                       |
        +--------+-------------------------------------------------------------+
        | MN6190 | Monthly mean minimum soil temperature (cover: straw mulch   |
        +--------+-------------------------------------------------------------+
        | HX6190 | Highest maximum soil temperature for the month (cover:      |
        |        | straw mulch                                                 |
        +--------+-------------------------------------------------------------+
        | LX6190 | Lowest maximum soil temperature for the month (cover: straw |
        |        | mulch                                                       |
        +--------+-------------------------------------------------------------+
        | MX6190 | Monthly mean maximum soil temperature (cover: straw mulch   |
        +--------+-------------------------------------------------------------+
        | CLDD   | Cooling Degree Days                                         |
        +--------+-------------------------------------------------------------+
        | DP01   | Number of days with greater than or equal to 0.1 inch of    |
        |        | precipitation                                               |
        +--------+-------------------------------------------------------------+
        | DP05   | Number of days with greater than or equal to 0.5 inch of    |
        |        | precipitation                                               |
        +--------+-------------------------------------------------------------+
        | DP10   | Number of days with greater than or equal to 1.0 inch of    |
        |        | precipitation                                               |
        +--------+-------------------------------------------------------------+
        | DPNP   | Departure from normal monthly precipitation.                |
        +--------+-------------------------------------------------------------+
        | DPNT   | Departure from normal monthly temperature.                  |
        +--------+-------------------------------------------------------------+
        | DSNW   | Number days with snow depth > 1 inch.                       |
        +--------+-------------------------------------------------------------+
        | DT00   | Number days with minimum temperature less than or equal to  |
        |        | 0.0 F                                                       |
        +--------+-------------------------------------------------------------+
        | DT32   | Number days with minimum temperature less than or equal to  |
        |        | 32.0 F                                                      |
        +--------+-------------------------------------------------------------+
        | DT70   | Number days with maximum temperature > 70 F. (Alaska only.) |
        +--------+-------------------------------------------------------------+
        | DT90   | Number days with maximum temperature greater than or equal  |
        |        | 90.0 F                                                      |
        +--------+-------------------------------------------------------------+
        | DX32   | Number days with maximum temperature < 32 F.                |
        +--------+-------------------------------------------------------------+
        | EMNT   | Extreme minimum temperature for the period.                 |
        +--------+-------------------------------------------------------------+
        | EMXP   | Extreme maximum precipitation for the period.               |
        +--------+-------------------------------------------------------------+
        | EMXT   | Extreme maximum temperature for the period.                 |
        +--------+-------------------------------------------------------------+
        | HN0190 | Highest minimum soil temperature for the month (cover:      |
        |        | unknown                                                     |
        +--------+-------------------------------------------------------------+
        | HN0290 | Highest minimum soil temperature for the month (cover:      |
        |        | unknown                                                     |
        +--------+-------------------------------------------------------------+
        | HN0390 | Highest minimum soil temperature for the month (cover:      |
        |        | unknown                                                     |
        +--------+-------------------------------------------------------------+
        | HN1190 | Highest minimum soil temperature for the month (cover:      |
        |        | grass                                                       |
        +--------+-------------------------------------------------------------+
        | HN1290 | Highest minimum soil temperature for the month (cover:      |
        |        | grass                                                       |
        +--------+-------------------------------------------------------------+
        | HN1390 | Highest minimum soil temperature for the month (cover:      |
        |        | grass                                                       |
        +--------+-------------------------------------------------------------+
        | HN2190 | Highest minimum soil temperature for the month (cover:      |
        |        | fallow                                                      |
        +--------+-------------------------------------------------------------+
        | HN2290 | Highest minimum soil temperature for the month (cover:      |
        |        | fallow                                                      |
        +--------+-------------------------------------------------------------+
        | HN2390 | Highest minimum soil temperature for the month (cover:      |
        |        | fallow                                                      |
        +--------+-------------------------------------------------------------+
        | HN3190 | Highest minimum soil temperature for the month (cover: bare |
        |        | ground                                                      |
        +--------+-------------------------------------------------------------+
        | HN3290 | Highest minimum soil temperature for the month (cover: bare |
        |        | ground                                                      |
        +--------+-------------------------------------------------------------+
        | HN3390 | Highest minimum soil temperature for the month (cover: bare |
        |        | ground                                                      |
        +--------+-------------------------------------------------------------+
        | HN5190 | Highest minimum soil temperature for the month (cover: sod  |
        +--------+-------------------------------------------------------------+
        | HN5290 | Highest minimum soil temperature for the month (cover: sod  |
        +--------+-------------------------------------------------------------+
        | HN5390 | Highest minimum soil temperature for the month (cover: sod  |
        +--------+-------------------------------------------------------------+
        | HO01A0 | Highest soil temperature at observation time (cover:        |
        |        | unknown                                                     |
        +--------+-------------------------------------------------------------+
        | HO01P0 | Highest soil temperature at observation time (cover:        |
        |        | unknown                                                     |
        +--------+-------------------------------------------------------------+
        | HO02A0 | Highest soil temperature at observation time (cover:        |
        |        | unknown                                                     |
        +--------+-------------------------------------------------------------+
        | HO02P0 | Highest soil temperature at observation time (cover:        |
        |        | unknown                                                     |
        +--------+-------------------------------------------------------------+
        | HO03A0 | Highest soil temperature at observation time (cover:        |
        |        | unknown                                                     |
        +--------+-------------------------------------------------------------+
        | HO03P0 | Highest soil temperature at observation time (cover:        |
        |        | unknown                                                     |
        +--------+-------------------------------------------------------------+
        | HO04A0 | Highest soil temperature at observation time (cover:        |
        |        | unknown                                                     |
        +--------+-------------------------------------------------------------+
        | HO04P0 | Highest soil temperature at observation time (cover:        |
        |        | unknown                                                     |
        +--------+-------------------------------------------------------------+
        | HO05A0 | Highest soil temperature at observation time (cover:        |
        |        | unknown                                                     |
        +--------+-------------------------------------------------------------+
        | HO05P0 | Highest soil temperature at observation time (cover:        |
        |        | unknown                                                     |
        +--------+-------------------------------------------------------------+
        | HO11A0 | Highest soil temperature at observation time (cover: grass  |
        +--------+-------------------------------------------------------------+
        | HO11P0 | Highest soil temperature at observation time (cover: grass  |
        +--------+-------------------------------------------------------------+
        | HO12A0 | Highest soil temperature at observation time (cover: grass  |
        +--------+-------------------------------------------------------------+
        | HO12P0 | Highest soil temperature at observation time (cover: grass  |
        +--------+-------------------------------------------------------------+
        | HO13A0 | Highest soil temperature at observation time (cover: grass  |
        +--------+-------------------------------------------------------------+
        | HO14A0 | Highest soil temperature at observation time (cover: grass  |
        +--------+-------------------------------------------------------------+
        | HO15A0 | Highest soil temperature at observation time (cover: grass  |
        +--------+-------------------------------------------------------------+
        | HO31A0 | Highest soil temperature at observation time (cover: bare   |
        |        | ground                                                      |
        +--------+-------------------------------------------------------------+
        | HO31P0 | Highest soil temperature at observation time (cover: bare   |
        |        | ground                                                      |
        +--------+-------------------------------------------------------------+
        | HO32A0 | Highest soil temperature at observation time (cover: bare   |
        |        | ground                                                      |
        +--------+-------------------------------------------------------------+
        | HO32P0 | Highest soil temperature at observation time (cover: bare   |
        |        | ground                                                      |
        +--------+-------------------------------------------------------------+
        | HO33A0 | Highest soil temperature at observation time (cover: bare   |
        |        | ground                                                      |
        +--------+-------------------------------------------------------------+
        | HO33P0 | Highest soil temperature at observation time (cover: bare   |
        |        | ground                                                      |
        +--------+-------------------------------------------------------------+
        | HO34A0 | Highest soil temperature at observation time (cover: bare   |
        |        | ground                                                      |
        +--------+-------------------------------------------------------------+
        | HO34P0 | Highest soil temperature at observation time (cover: bare   |
        |        | ground                                                      |
        +--------+-------------------------------------------------------------+
        | HO35A0 | Highest soil temperature at observation time (cover: bare   |
        |        | ground                                                      |
        +--------+-------------------------------------------------------------+
        | HO35P0 | Highest soil temperature at observation time (cover: bare   |
        |        | ground                                                      |
        +--------+-------------------------------------------------------------+
        | HO51A0 | Highest soil temperature at observation time (cover: sod    |
        +--------+-------------------------------------------------------------+
        | HO51P0 | Highest soil temperature at observation time (cover: sod    |
        +--------+-------------------------------------------------------------+
        | HO52A0 | Highest soil temperature at observation time (cover: sod    |
        +--------+-------------------------------------------------------------+
        | HO52P0 | Highest soil temperature at observation time (cover: sod    |
        +--------+-------------------------------------------------------------+
        | HO53A0 | Highest soil temperature at observation time (cover: sod    |
        +--------+-------------------------------------------------------------+
        | HO53P0 | Highest soil temperature at observation time (cover: sod    |
        +--------+-------------------------------------------------------------+
        | HO54A0 | Highest soil temperature at observation time (cover: sod    |
        +--------+-------------------------------------------------------------+
        | HO54P0 | Highest soil temperature at observation time (cover: sod    |
        +--------+-------------------------------------------------------------+
        | HO55A0 | Highest soil temperature at observation time (cover: sod    |
        +--------+-------------------------------------------------------------+
        | HO55P0 | Highest soil temperature at observation time (cover: sod    |
        +--------+-------------------------------------------------------------+
        | HTDD   | Heating degree days                                         |
        +--------+-------------------------------------------------------------+
        | HX0190 | Highest maximum soil temperature for the month (cover:      |
        |        | unknown                                                     |
        +--------+-------------------------------------------------------------+
        | HX0290 | Highest maximum soil temperature for the month (cover:      |
        |        | unknown                                                     |
        +--------+-------------------------------------------------------------+
        | HX0390 | Highest maximum soil temperature for the month (cover:      |
        |        | unknown                                                     |
        +--------+-------------------------------------------------------------+
        | HX1190 | Highest maximum soil temperature for the month (cover:      |
        |        | grass                                                       |
        +--------+-------------------------------------------------------------+
        | HX1290 | Highest maximum soil temperature for the month (cover:      |
        |        | grass                                                       |
        +--------+-------------------------------------------------------------+
        | HX1390 | Highest maximum soil temperature for the month (cover:      |
        |        | grass                                                       |
        +--------+-------------------------------------------------------------+
        | HX2190 | Highest maximum soil temperature for the month (cover:      |
        |        | fallow                                                      |
        +--------+-------------------------------------------------------------+
        | HX2290 | Highest maximum soil temperature for the month (cover:      |
        |        | fallow                                                      |
        +--------+-------------------------------------------------------------+
        | HX2390 | Highest maximum soil temperature for the month (cover:      |
        |        | fallow                                                      |
        +--------+-------------------------------------------------------------+
        | HX3190 | Highest maximum soil temperature for the month (cover: bare |
        |        | ground                                                      |
        +--------+-------------------------------------------------------------+
        | HX3290 | Highest maximum soil temperature for the month (cover: bare |
        |        | ground                                                      |
        +--------+-------------------------------------------------------------+
        | HX3390 | Highest maximum soil temperature for the month (cover: bare |
        |        | ground                                                      |
        +--------+-------------------------------------------------------------+
        | HX5190 | Highest maximum soil temperature for the month (cover: sod  |
        +--------+-------------------------------------------------------------+
        | HX5290 | Highest maximum soil temperature for the month (cover: sod  |
        +--------+-------------------------------------------------------------+
        | HX5390 | Highest maximum soil temperature for the month (cover: sod  |
        +--------+-------------------------------------------------------------+
        | LN0190 | Lowest minimum soil temperature for the month (cover:       |
        |        | unknown                                                     |
        +--------+-------------------------------------------------------------+
        | LN0290 | Lowest minimum soil temperature for the month (cover:       |
        |        | unknown                                                     |
        +--------+-------------------------------------------------------------+
        | LN0390 | Lowest minimum soil temperature for the month (cover:       |
        |        | unknown                                                     |
        +--------+-------------------------------------------------------------+
        | LN1190 | Lowest minimum soil temperature for the month (cover: grass |
        +--------+-------------------------------------------------------------+
        | LN1290 | Lowest minimum soil temperature for the month (cover: grass |
        +--------+-------------------------------------------------------------+
        | LN1390 | Lowest minimum soil temperature for the month (cover: grass |
        +--------+-------------------------------------------------------------+
        | LN2190 | Lowest minimum soil temperature for the month (cover:       |
        |        | fallow                                                      |
        +--------+-------------------------------------------------------------+
        | LN2290 | Lowest minimum soil temperature for the month (cover:       |
        |        | fallow                                                      |
        +--------+-------------------------------------------------------------+
        | LN2390 | Lowest minimum soil temperature for the month (cover:       |
        |        | fallow                                                      |
        +--------+-------------------------------------------------------------+
        | LN3190 | Lowest minimum soil temperature for the month (cover: bare  |
        |        | ground                                                      |
        +--------+-------------------------------------------------------------+
        | LN3290 | Lowest minimum soil temperature for the month (cover: bare  |
        |        | ground                                                      |
        +--------+-------------------------------------------------------------+
        | LN3390 | Lowest minimum soil temperature for the month (cover: bare  |
        |        | ground                                                      |
        +--------+-------------------------------------------------------------+
        | LN5190 | Lowest minimum soil temperature for the month (cover: sod   |
        +--------+-------------------------------------------------------------+
        | LN5290 | Lowest minimum soil temperature for the month (cover: sod   |
        +--------+-------------------------------------------------------------+
        | LN5390 | Lowest minimum soil temperature for the month (cover: sod   |
        +--------+-------------------------------------------------------------+
        | LO01A0 | Lowest soil temperature at observation time (cover: unknown |
        +--------+-------------------------------------------------------------+
        | LO01P0 | Lowest soil temperature at observation time (cover: unknown |
        +--------+-------------------------------------------------------------+
        | LO02A0 | Lowest soil temperature at observation time (cover: unknown |
        +--------+-------------------------------------------------------------+
        | LO02P0 | Lowest soil temperature at observation time (cover: unknown |
        +--------+-------------------------------------------------------------+
        | LO03A0 | Lowest soil temperature at observation time (cover: unknown |
        +--------+-------------------------------------------------------------+
        | LO03P0 | Lowest soil temperature at observation time (cover: unknown |
        +--------+-------------------------------------------------------------+
        | LO04A0 | Lowest soil temperature at observation time (cover: unknown |
        +--------+-------------------------------------------------------------+
        | LO04P0 | Lowest soil temperature at observation time (cover: unknown |
        +--------+-------------------------------------------------------------+
        | LO05A0 | Lowest soil temperature at observation time (cover: unknown |
        +--------+-------------------------------------------------------------+
        | LO05P0 | Lowest soil temperature at observation time (cover: unknown |
        +--------+-------------------------------------------------------------+
        | LO11A0 | Lowest soil temperature at observation time (cover: grass   |
        +--------+-------------------------------------------------------------+
        | LO12A0 | Lowest soil temperature at observation time (cover: grass   |
        +--------+-------------------------------------------------------------+
        | LO12P0 | Lowest soil temperature at observation time (cover: grass   |
        +--------+-------------------------------------------------------------+
        | LO13A0 | Lowest soil temperature at observation time (cover: grass   |
        +--------+-------------------------------------------------------------+
        | LO14A0 | Lowest soil temperature at observation time (cover: grass   |
        +--------+-------------------------------------------------------------+
        | LO15A0 | Lowest soil temperature at observation time (cover: grass   |
        +--------+-------------------------------------------------------------+
        | LO31A0 | Lowest soil temperature at observation time (cover: bare    |
        |        | ground                                                      |
        +--------+-------------------------------------------------------------+
        | LO31P0 | Lowest soil temperature at observation time (cover: bare    |
        |        | ground                                                      |
        +--------+-------------------------------------------------------------+
        | LO32A0 | Lowest soil temperature at observation time (cover: bare    |
        |        | ground                                                      |
        +--------+-------------------------------------------------------------+
        | LO32P0 | Lowest soil temperature at observation time (cover: bare    |
        |        | ground                                                      |
        +--------+-------------------------------------------------------------+
        | LO33A0 | Lowest soil temperature at observation time (cover: bare    |
        |        | ground                                                      |
        +--------+-------------------------------------------------------------+
        | LO33P0 | Lowest soil temperature at observation time (cover: bare    |
        |        | ground                                                      |
        +--------+-------------------------------------------------------------+
        | LO34A0 | Lowest soil temperature at observation time (cover: bare    |
        |        | ground                                                      |
        +--------+-------------------------------------------------------------+
        | LO34P0 | Lowest soil temperature at observation time (cover: bare    |
        |        | ground                                                      |
        +--------+-------------------------------------------------------------+
        | LO35A0 | Lowest soil temperature at observation time (cover: bare    |
        |        | ground                                                      |
        +--------+-------------------------------------------------------------+
        | LO35P0 | Lowest soil temperature at observation time (cover: bare    |
        |        | ground                                                      |
        +--------+-------------------------------------------------------------+
        | LO51A0 | Lowest soil temperature at observation time (cover: sod     |
        +--------+-------------------------------------------------------------+
        | LO51P0 | Lowest soil temperature at observation time (cover: sod     |
        +--------+-------------------------------------------------------------+
        | LO52A0 | Lowest soil temperature at observation time (cover: sod     |
        +--------+-------------------------------------------------------------+
        | LO52P0 | Lowest soil temperature at observation time (cover: sod     |
        +--------+-------------------------------------------------------------+
        | LO53A0 | Lowest soil temperature at observation time (cover: sod     |
        +--------+-------------------------------------------------------------+
        | LO53P0 | Lowest soil temperature at observation time (cover: sod     |
        +--------+-------------------------------------------------------------+
        | LO54A0 | Lowest soil temperature at observation time (cover: sod     |
        +--------+-------------------------------------------------------------+
        | LO54P0 | Lowest soil temperature at observation time (cover: sod     |
        +--------+-------------------------------------------------------------+
        | LO55A0 | Lowest soil temperature at observation time (cover: sod     |
        +--------+-------------------------------------------------------------+
        | LO55P0 | Lowest soil temperature at observation time (cover: sod     |
        +--------+-------------------------------------------------------------+
        | LX0190 | Lowest maximum soil temperature for the month (cover:       |
        |        | unknown                                                     |
        +--------+-------------------------------------------------------------+
        | LX0290 | Lowest maximum soil temperature for the month (cover:       |
        |        | unknown                                                     |
        +--------+-------------------------------------------------------------+
        | LX0390 | Lowest maximum soil temperature for the month (cover:       |
        |        | unknown                                                     |
        +--------+-------------------------------------------------------------+
        | LX1190 | Lowest maximum soil temperature for the month (cover: grass |
        +--------+-------------------------------------------------------------+
        | LX1290 | Lowest maximum soil temperature for the month (cover: grass |
        +--------+-------------------------------------------------------------+
        | LX1390 | Lowest maximum soil temperature for the month (cover: grass |
        +--------+-------------------------------------------------------------+
        | LX2190 | Lowest maximum soil temperature for the month (cover:       |
        |        | fallow                                                      |
        +--------+-------------------------------------------------------------+
        | LX2290 | Lowest maximum soil temperature for the month (cover:       |
        |        | fallow                                                      |
        +--------+-------------------------------------------------------------+
        | LX2390 | Lowest maximum soil temperature for the month (cover:       |
        |        | fallow                                                      |
        +--------+-------------------------------------------------------------+
        | LX3190 | Lowest maximum soil temperature for the month (cover: bare  |
        |        | ground                                                      |
        +--------+-------------------------------------------------------------+
        | LX3290 | Lowest maximum soil temperature for the month (cover: bare  |
        |        | ground                                                      |
        +--------+-------------------------------------------------------------+
        | LX3390 | Lowest maximum soil temperature for the month (cover: bare  |
        |        | ground                                                      |
        +--------+-------------------------------------------------------------+
        | LX5190 | Lowest maximum soil temperature for the month (cover: sod   |
        +--------+-------------------------------------------------------------+
        | LX5290 | Lowest maximum soil temperature for the month (cover: sod   |
        +--------+-------------------------------------------------------------+
        | LX5390 | Lowest maximum soil temperature for the month (cover: sod   |
        +--------+-------------------------------------------------------------+
        | MMNP   | Mean minimum temperature of evaporation pan water for the   |
        |        | period.                                                     |
        +--------+-------------------------------------------------------------+
        | MMNT   | Monthly Mean minimum temperature                            |
        +--------+-------------------------------------------------------------+
        | MMXP   | Mean maximum temperature of evaporation pan water for the   |
        |        | period.                                                     |
        +--------+-------------------------------------------------------------+
        | MMXT   | Monthly Mean maximum temperature                            |
        +--------+-------------------------------------------------------------+
        | MN0190 | Monthly mean minimum soil temperature (cover: unknown       |
        +--------+-------------------------------------------------------------+
        | MN0290 | Monthly mean minimum soil temperature (cover: unknown       |
        +--------+-------------------------------------------------------------+
        | MN0390 | Monthly mean minimum soil temperature (cover: unknown       |
        +--------+-------------------------------------------------------------+
        | MN1190 | Monthly mean minimum soil temperature (cover: grass         |
        +--------+-------------------------------------------------------------+
        | MN1290 | Monthly mean minimum soil temperature (cover: grass         |
        +--------+-------------------------------------------------------------+
        | MN1390 | Monthly mean minimum soil temperature (cover: grass         |
        +--------+-------------------------------------------------------------+
        | MN2190 | Monthly mean minimum soil temperature (cover: fallow        |
        +--------+-------------------------------------------------------------+
        | MN2290 | Monthly mean minimum soil temperature (cover: fallow        |
        +--------+-------------------------------------------------------------+
        | MN2390 | Monthly mean minimum soil temperature (cover: fallow        |
        +--------+-------------------------------------------------------------+
        | MN3190 | Monthly mean minimum soil temperature (cover: bare ground   |
        +--------+-------------------------------------------------------------+
        | MN3290 | Monthly mean minimum soil temperature (cover: bare ground   |
        +--------+-------------------------------------------------------------+
        | MN3390 | Monthly mean minimum soil temperature (cover: bare ground   |
        +--------+-------------------------------------------------------------+
        | MN5190 | Monthly mean minimum soil temperature (cover: sod           |
        +--------+-------------------------------------------------------------+
        | MN5290 | Monthly mean minimum soil temperature (cover: sod           |
        +--------+-------------------------------------------------------------+
        | MN5390 | Monthly mean minimum soil temperature (cover: sod           |
        +--------+-------------------------------------------------------------+
        | MNTM   | Monthly mean temperature                                    |
        +--------+-------------------------------------------------------------+
        | MO01A0 | Monthly mean soil temperature at observation time (cover:   |
        |        | unknown                                                     |
        +--------+-------------------------------------------------------------+
        | MO01P0 | Monthly mean soil temperature at observation time (cover:   |
        |        | unknown                                                     |
        +--------+-------------------------------------------------------------+
        | MO02A0 | Monthly mean soil temperature at observation time (cover:   |
        |        | unknown                                                     |
        +--------+-------------------------------------------------------------+
        | MO02P0 | Monthly mean soil temperature at observation time (cover:   |
        |        | unknown                                                     |
        +--------+-------------------------------------------------------------+
        | MO03A0 | Monthly mean soil temperature at observation time (cover:   |
        |        | unknown                                                     |
        +--------+-------------------------------------------------------------+
        | MO03P0 | Monthly mean soil temperature at observation time (cover:   |
        |        | unknown                                                     |
        +--------+-------------------------------------------------------------+
        | MO04A0 | Monthly mean soil temperature at observation time (cover:   |
        |        | unknown                                                     |
        +--------+-------------------------------------------------------------+
        | MO04P0 | Monthly mean soil temperature at observation time (cover:   |
        |        | unknown                                                     |
        +--------+-------------------------------------------------------------+
        | MO05A0 | Monthly mean soil temperature at observation time (cover:   |
        |        | unknown                                                     |
        +--------+-------------------------------------------------------------+
        | MO05P0 | Monthly mean soil temperature at observation time (cover:   |
        |        | unknown                                                     |
        +--------+-------------------------------------------------------------+
        | MO11A0 | Monthly mean soil temperature at observation time (cover:   |
        |        | grass                                                       |
        +--------+-------------------------------------------------------------+
        | MO11P0 | Monthly mean soil temperature at observation time (cover:   |
        |        | grass                                                       |
        +--------+-------------------------------------------------------------+
        | MO12A0 | Monthly mean soil temperature at observation time (cover:   |
        |        | grass                                                       |
        +--------+-------------------------------------------------------------+
        | MO12P0 | Monthly mean soil temperature at observation time (cover:   |
        |        | grass                                                       |
        +--------+-------------------------------------------------------------+
        | MO13A0 | Monthly mean soil temperature at observation time (cover:   |
        |        | grass                                                       |
        +--------+-------------------------------------------------------------+
        | MO13P0 | Monthly mean soil temperature at observation time (cover:   |
        |        | grass                                                       |
        +--------+-------------------------------------------------------------+
        | MO14A0 | Monthly mean soil temperature at observation time (cover:   |
        |        | grass                                                       |
        +--------+-------------------------------------------------------------+
        | MO15A0 | Monthly mean soil temperature at observation time (cover:   |
        |        | grass                                                       |
        +--------+-------------------------------------------------------------+
        | MO31A0 | Monthly mean soil temperature at observation time (cover:   |
        |        | bare ground                                                 |
        +--------+-------------------------------------------------------------+
        | MO31P0 | Monthly mean soil temperature at observation time (cover:   |
        |        | bare ground                                                 |
        +--------+-------------------------------------------------------------+
        | MO32A0 | Monthly mean soil temperature at observation time (cover:   |
        |        | bare ground                                                 |
        +--------+-------------------------------------------------------------+
        | MO32P0 | Monthly mean soil temperature at observation time (cover:   |
        |        | bare ground                                                 |
        +--------+-------------------------------------------------------------+
        | MO33A0 | Monthly mean soil temperature at observation time (cover:   |
        |        | bare ground                                                 |
        +--------+-------------------------------------------------------------+
        | MO33P0 | Monthly mean soil temperature at observation time (cover:   |
        |        | bare ground                                                 |
        +--------+-------------------------------------------------------------+
        | MO34A0 | Monthly mean soil temperature at observation time (cover:   |
        |        | bare ground                                                 |
        +--------+-------------------------------------------------------------+
        | MO34P0 | Monthly mean soil temperature at observation time (cover:   |
        |        | bare ground                                                 |
        +--------+-------------------------------------------------------------+
        | MO35A0 | Monthly mean soil temperature at observation time (cover:   |
        |        | bare ground                                                 |
        +--------+-------------------------------------------------------------+
        | MO35P0 | Monthly mean soil temperature at observation time (cover:   |
        |        | bare ground                                                 |
        +--------+-------------------------------------------------------------+
        | MO51A0 | Monthly mean soil temperature at observation time (cover:   |
        |        | sod                                                         |
        +--------+-------------------------------------------------------------+
        | MO51P0 | Monthly mean soil temperature at observation time (cover:   |
        |        | sod                                                         |
        +--------+-------------------------------------------------------------+
        | MO52A0 | Monthly mean soil temperature at observation time (cover:   |
        |        | sod                                                         |
        +--------+-------------------------------------------------------------+
        | MO52P0 | Monthly mean soil temperature at observation time (cover:   |
        |        | sod                                                         |
        +--------+-------------------------------------------------------------+
        | MO53A0 | Monthly mean soil temperature at observation time (cover:   |
        |        | sod                                                         |
        +--------+-------------------------------------------------------------+
        | MO53P0 | Monthly mean soil temperature at observation time (cover:   |
        |        | sod                                                         |
        +--------+-------------------------------------------------------------+
        | MO54A0 | Monthly mean soil temperature at observation time (cover:   |
        |        | sod                                                         |
        +--------+-------------------------------------------------------------+
        | MO54P0 | Monthly mean soil temperature at observation time (cover:   |
        |        | sod                                                         |
        +--------+-------------------------------------------------------------+
        | MO55A0 | Monthly mean soil temperature at observation time (cover:   |
        |        | sod                                                         |
        +--------+-------------------------------------------------------------+
        | MO55P0 | Monthly mean soil temperature at observation time (cover:   |
        |        | sod                                                         |
        +--------+-------------------------------------------------------------+
        | MX0190 | Monthly mean maximum soil temperature (cover: unknown       |
        +--------+-------------------------------------------------------------+
        | MX0290 | Monthly mean maximum soil temperature (cover: unknown       |
        +--------+-------------------------------------------------------------+
        | MX0390 | Monthly mean maximum soil temperature (cover: unknown       |
        +--------+-------------------------------------------------------------+
        | MX1190 | Monthly mean maximum soil temperature (cover: grass         |
        +--------+-------------------------------------------------------------+
        | MX1290 | Monthly mean maximum soil temperature (cover: grass         |
        +--------+-------------------------------------------------------------+
        | MX1390 | Monthly mean maximum soil temperature (cover: grass         |
        +--------+-------------------------------------------------------------+
        | MX2190 | Monthly mean maximum soil temperature (cover: fallow        |
        +--------+-------------------------------------------------------------+
        | MX2290 | Monthly mean maximum soil temperature (cover: fallow        |
        +--------+-------------------------------------------------------------+
        | MX2390 | Monthly mean maximum soil temperature (cover: fallow        |
        +--------+-------------------------------------------------------------+
        | MX3190 | Monthly mean maximum soil temperature (cover: bare ground   |
        +--------+-------------------------------------------------------------+
        | MX3290 | Monthly mean maximum soil temperature (cover: bare ground   |
        +--------+-------------------------------------------------------------+
        | MX3390 | Monthly mean maximum soil temperature (cover: bare ground   |
        +--------+-------------------------------------------------------------+
        | MX5190 | Monthly mean maximum soil temperature (cover: sod           |
        +--------+-------------------------------------------------------------+
        | MX5290 | Monthly mean maximum soil temperature (cover: sod           |
        +--------+-------------------------------------------------------------+
        | MX5390 | Monthly mean maximum soil temperature (cover: sod           |
        +--------+-------------------------------------------------------------+
        | MXSD   | Maximum snow depth                                          |
        +--------+-------------------------------------------------------------+
        | TEVP   | Total monthly evaporation.                                  |
        +--------+-------------------------------------------------------------+
        | TPCP   | Total precipitation                                         |
        +--------+-------------------------------------------------------------+
        | TSNW   | Total snow fall                                             |
        +--------+-------------------------------------------------------------+
        | TWND   | Total monthly wind movement over evaporation pan.           |
        +--------+-------------------------------------------------------------+
        """,
}


@cltoolbox.command("ncei_ghcnd_ftp", formatter_class=HelpFormatter)
@tsutils.doc({**tsutils.docstrings, **ncei_ghcnd_docstrings})
def ncei_ghcnd_ftp_cli(stationid, start_date=None, end_date=None):
    r"""global station D:NCEI Global Historical Climatology Network - Daily (GHCND)

    ${info}

    Parameters
    ----------
    ${stationid}
    ${start_date}
    ${end_date}
    """
    tsutils.printiso(
        ncei_ghcnd_ftp(stationid, start_date=start_date, end_date=end_date),
    )


@tsutils.copy_doc(ncei_ghcnd_ftp_cli)
def ncei_ghcnd_ftp(stationid, start_date=None, end_date=None):
    r"""global station D:Download from the Global Historical Climatology Network - Daily."""
    stationid = stationid.split(":")[-1]
    params = {"station": stationid, "start_date": start_date, "end_date": end_date}

    url = r"ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/all"
    df = pd.read_fwf(
        f"{url}/{params['station']}.dly",
        widths=[11, 4, 2, 4] + [5, 1, 1, 1] * 31,
    )
    newcols = ["station", "year", "month", "code"]
    for day in list(range(1, 32)):
        newcols.extend(f"{col}{day:02}" for col in ("", "m", "q", "s"))
    df.columns = newcols
    codes = [
        "TMAX",  # Temperature MAX (1/10 degree C)
        "TMIN",  # Temperature MIN (1/10 degree C)
        "PRCP",  # PReCiPitation (tenths of mm)
        "SNOW",  # SNOWfall (mm)
        "SNWD",  # SNoW Depth (mm)
        # Average cloudiness midnight to midnight from 30-second
        # ceilometer data (percent)
        "ACMC",
        # Average cloudiness midnight to midnight from manual observations
        # (percent)
        "ACMH",
        # Average cloudiness sunrise to sunset from 30-second ceilometer
        # data (percent)
        "ACSC",
        # Average cloudiness sunrise to sunset from manual observations
        # (percent)
        "ACSH",
        "AWDR",  # Average daily wind direction (degrees)
        "AWND",  # Average daily wind speed (tenths of meters per second)
        # Number of days included in the multiday evaporation total (MDEV)
        "DAEV",
        # Number of days included in the multiday precipiation total
        # (MDPR)
        "DAPR",
        # Number of days included in the multiday snowfall total (MDSF)
        "DASF",
        # Number of days included in the multiday minimum temperature
        # (MDTN)
        "DATN",
        # Number of days included in the multiday maximum temperature
        # (MDTX)
        "DATX",
        # Number of days included in the multiday wind movement (MDWM)
        "DAWM",
        # Number of days with non-zero precipitation included in multiday
        # precipitation total (MDPR)
        "DWPR",
        # Evaporation of water from evaporation pan (tenths of mm)
        "EVAP",
        # Time of fastest mile or fastest 1-minute wind (hours and
        # minutes, i.e., HHMM)
        "FMTM",
        "FRGB",  # Base of frozen ground layer (cm)
        "FRGT",  # Top of frozen ground layer (cm)
        "FRTH",  # Thickness of frozen ground layer (cm)
        "GAHT",  # Difference between river and gauge height (cm)
        # Multiday evaporation total (tenths of mm; use with DAEV)
        "MDEV",
        # Multiday precipitation total (tenths of mm; use with DAPR and
        # DWPR, if available)
        "MDPR",
        "MDSF",  # Multiday snowfall total
        # Multiday minimum temperature (tenths of degrees C; use with
        # DATN)
        "MDTN",
        # Multiday maximum temperature (tenths of degress C; use with
        # DATX)
        "MDTX",
        "MDWM",  # Multiday wind movement (km)
        # Daily minimum temperature of water in an evaporation pan (tenths
        # of degrees C)
        "MNPN",
        # Daily maximum temperature of water in an evaporation pan (tenths
        # of degrees C)
        "MXPN",
        "PGTM",  # Peak gust time (hours and minutes, i.e., HHMM)
        "PSUN",  # Daily percent of possible sunshine (percent)
        # Average temperature (tenths of degrees C) [Note that TAVG from
        # source 'S' corresponds to an average for the period ending at
        # 2400 UTC rather than local midnight]
        "TAVG",
        "THIC",  # Thickness of ice on water (tenths of mm)
        # Temperature at the time of observation (tenths of degrees C)
        "TOBS",
        "TSUN",  # Daily total sunshine (minutes)
        "WDF1",  # Direction of fastest 1-minute wind (degrees)
        "WDF2",  # Direction of fastest 2-minute wind (degrees)
        "WDF5",  # Direction of fastest 5-second wind (degrees)
        "WDFG",  # Direction of peak wind gust (degrees)
        "WDFI",  # Direction of highest instantaneous wind (degrees)
        "WDFM",  # Fastest mile wind direction (degrees)
        "WDMV",  # 24-hour wind movement (km)
        "WESD",  # Water equivalent of snow on the ground (tenths of mm)
        "WESF",  # Water equivalent of snowfall (tenths of mm)
        # Fastest 1-minute wind speed (tenths of meters per second)
        "WSF1",
        # Fastest 2-minute wind speed (tenths of meters per second)
        "WSF2",
        # Fastest 5-second wind speed (tenths of meters per second)
        "WSF5",
        "WSFG",  # Peak gust wind speed (tenths of meters per second)
        # Highest instantaneous wind speed (tenths of meters per second)
        "WSFI",
        "WSFM",  # Fastest mile wind speed (tenths of meters per second)
    ]

    # SN*# = Minimum soil temperature (tenths of degrees C)
    #        where * corresponds to a code
    #        for ground cover and # corresponds to a code for soil
    #        depth.
    #
    #        Ground cover codes include the following:
    #        0 = unknown
    #        1 = grass
    #        2 = fallow
    #        3 = bare ground
    #        4 = brome grass
    #        5 = sod
    #        6 = straw multch
    #        7 = grass muck
    #        8 = bare muck
    #
    #        Depth codes include the following:
    #        1 = 5 cm
    #        2 = 10 cm
    #        3 = 20 cm
    #        4 = 50 cm
    #        5 = 100 cm
    #        6 = 150 cm
    #        7 = 180 cm
    for i in range(9):
        codes.extend(f"SN{i}{j}" for j in range(1, 8))
    # SX*# = Maximum soil temperature (tenths of degrees C)
    #        where * corresponds to a code for ground cover
    #        and # corresponds to a code for soil depth.
    #        See SN*# for ground cover and depth codes.
    for i in range(9):
        codes.extend(f"SX{i}{j}" for j in range(1, 8))
    # WT** = Weather Type where ** has one of the following values:
    #
    #        01 = Fog, ice fog, or freezing fog (may include heavy fog)
    #        02 = Heavy fog or heaving freezing fog (not always distinquished
    #        from fog)
    #        03 = Thunder
    #        04 = Ice pellets, sleet, snow pellets, or small hail
    #        05 = Hail (may include small hail)
    #        06 = Glaze or rime
    #        07 = Dust, volcanic ash, blowing dust, blowing sand, or blowing
    #        obstruction
    #        08 = Smoke or haze
    #        09 = Blowing or drifting snow
    #        10 = Tornado, waterspout, or funnel cloud
    #        11 = High or damaging winds
    #        12 = Blowing spray
    #        13 = Mist
    #        14 = Drizzle
    #        15 = Freezing drizzle
    #        16 = Rain (may include freezing rain, drizzle, and freezing
    #        drizzle)
    #        17 = Freezing rain
    #        18 = Snow, snow pellets, snow grains, or ice crystals
    #        19 = Unknown source of precipitation
    #        21 = Ground fog
    #        22 = Ice fog or freezing fog
    codes.extend([f"WT{i:02}" for i in range(1, 23)])

    # WV** = Weather in the Vicinity where ** has one of the following values:
    #        01 = Fog, ice fog, or freezing fog (may include heavy fog)
    #        03 = Thunder
    #        07 = Ash, dust, sand, or other blowing obstruction
    #        18 = Snow or ice crystals
    #        20 = Rain or snow shower
    codes.extend([f"WV{i:02}" for i in (1, 3, 7, 18, 20)])

    for code in codes:
        tmpdf = df.loc[df["code"] == code, :]
        if len(tmpdf) == 0:
            continue
        tmpdf.set_index(["year", "month"], inplace=True)
        tmpdf = tmpdf.iloc[:, list(range(2, 126, 4))].stack()
        tmpdf.index = (
            f"{tmpdf.index.get_level_values(0).astype(str).values}-"
            f"{tmpdf.index.get_level_values(1).astype(str).values}-"
            f"{tmpdf.index.get_level_values(2).astype(str).values}"
        )

        # Get rid of bad dates, for example April 31.
        tmpdf.index = pd.to_datetime(tmpdf.index, errors="coerce")
        tmpdf = tmpdf[pd.notnull(tmpdf.index)]

        tmpdf = pd.DataFrame(tmpdf)
        tmpdf.columns = [code]
        tmpdf = tmpdf.loc[
            tsutils.parsedate(
                params["start_date"], strftime="%Y-%m-%d"
            ) : tsutils.parsedate(params["end_date"], strftime="%Y-%m-%d"),
            :,
        ]
        try:
            ndf = ndf.join(tmpdf)
        except NameError:
            ndf = tmpdf

    # Set missing values to None
    ndf.replace(to_replace=[-9999], value=[None], inplace=True)

    mcols = [
        i
        for i in ndf.columns
        if i
        in (
            "TMAX",
            "TMIN",
            "MDTN",
            "MDTX",
            "MNPN",
            "MXPN",
            "TAVG",
            "TOBS",
            "PRCP",
            "AWND",
            "EVAP",
            "MDEV",
            "MDPR",
            "THIC",
            "WESD",
            "WESF",
            "WSF1",
            "WSF2",
            "WSF5",
            "WSFG",
            "WSFI",
            "WSFM",
            "SNXY",
            "SXXY",
        )
    ]
    if mcols:
        ndf.loc[:, mcols] = ndf.loc[:, mcols] / 10.0

    ndf.index.name = "Datetime"
    ndf.rename(columns=add_units(ndf.columns), inplace=True)
    return ndf


_units = OrderedDict(
    {
        "CLDD": "day",
        "DUTR": "day",
        "GRDD": "day",
        "HTDD": "day",
        "TMAX": "degC",
        "TMIN": "degC",
        "TAVG": "degC",
        "EMXT": "degC",
        "EMNT": "degC",
        "DX": "day",
        "DT": "day",
        "DP": "day",
        "DSNW": "day",
        "DSND": "day",
        "PRCP": "mm",
        "SNOW": "mm",
        "EMSN": "mm",
        "EMSD": "mm",
        "SNWD": "mm",
        "EVAP": "mm",
        "FRGB": "cm",
        "FRGT": "cm",
        "FRTH": "cm",
        "GAHT": "cm",
        "MDEV": "cm",
        "MDPR": "cm",
        "MDSF": "cm",
        "MDTN": "degC",
        "MDTX": "degC",
        "MDWM": "km",
        "MNPN": "degC",
        "MXPN": "degC",
        "PSUN": "percent",
        "ACMC": "percent",
        "ACMH": "percent",
        "ACSC": "percent",
        "ACSH": "percent",
        "AWDR": "degree",
        "WDFM": "degree",
        "WDF": "degree",
        "AWND": "m/s",
        "WSFM": "m/s",
        "WSF": "m/s",
        "DAEV": "day",
        "DAPR": "day",
        "DASF": "day",
        "DATN": "day",
        "DATX": "day",
        "DAWM": "day",
        "DWPR": "day",
        "HDSD": "day",
        "CDSD": "day",
        "MX": "degC",
        "MN": "degC",
        "HX": "degC",
        "HN": "degC",
        "LX": "degC",
        "LN": "degC",
        "THIC": "mm",
        "TOBS": "degC",
        "TSUN": "minute",
        "WDMV": "km",
        "WESD": "mm",
        "WESF": "mm",
        "SN": "degC",
        "SX": "degC",
        "DUTR-NORMAL": "degC",
        "DUTR-STDDEV": "degC",
        "AVGNDS": "day",
        "TPCP": "mm",
        "QGAG": "mm",
        "QPCP": "mm",
        "HPCP": "mm",
        "-CLDH-": "hour",
        "-CLOD-": "percent",
        "-DEWP-": "degC",
        "-HTDH-": "hour",
        "-TEMP-": "degC",
        "-WCHL-": "degC",
        "-AVGSPD": "m/s",
        "-1STDIR": "degree",
        "-2NDDIR": "degree",
        "-1STPCT": "percent",
        "-2NDPCT": "percent",
        "-PCTCLM": "percent",
        "-VCTDIR": "percent",
        "-VCTSPD": "m/s",
    }
)


def add_units(dfcols):
    """Add units to the column names."""
    ncols = {}
    for col in dfcols:
        for key, value in _units.items():
            if (key in col and "value_" in col) or key == col:
                ncols[col] = f"{col}:{value}"
    return ncols


def ncei_cdo_json_to_df(datasetid, stationid, start_date=None, end_date=None):
    """Convert a NCEI CDO JSON to a pandas dataframe."""
    # Read in API key
    token = utils.read_api_key("ncei_cdo")

    my_client = Client(token, default_units="metric", default_limit=1000)
    my_client.verbose = False

    df = my_client.get_data_by_station(
        datasetid=datasetid,
        stationid=stationid,
        startdate=pd.to_datetime(start_date),
        enddate=pd.to_datetime(end_date),
        return_dateframe=True,
    )

    df.columns = list(df.columns)

    if "station" in df.columns:
        df = df.drop("station", axis="columns")
    if "date" in df.columns:
        df = df.set_index("date")
        df.index.name = "Datetime"
        df.index = pd.to_datetime(df.index)

    return df.rename(columns=add_units(df.columns))


# 1763-01-01, 2016-11-05, Daily Summaries             , 1    , GHCND
@cltoolbox.command("ncei_ghcnd", formatter_class=HelpFormatter)
@tsutils.doc({**tsutils.docstrings, **ncei_ghcnd_docstrings})
def ncei_ghcnd_cli(stationid, start_date=None, end_date=None):
    r"""global station D:Global Historical Climatology Network - Daily (GHCND)

    Requires registration and free API key.

    ${info}

    For every datatype and record there is a set of meta-data flags.
    For the GHCNDMS dataset, the flags are::

        'Total Missing','Consecutive Missing'

    Total Missing:

    Defined as total number of days observation/element is missing in that
    month.  This can be taken as a measure of quality or completeness as the
    higher the number of days sampled in the month, the more representative the
    value is for the entire month.

    Consecutive Missing:

    Defined as the maximum number of consecutive days in the month that an
    observation/element is missing.

    Parameters
    ----------
    ${stationid}
    ${start_date}
    ${end_date}"""
    tsutils.printiso(
        ncei_ghcnd(stationid, start_date=start_date, end_date=end_date),
    )


@tsutils.copy_doc(ncei_ghcnd_cli)
def ncei_ghcnd(stationid, start_date=None, end_date=None):
    r"""Download from the Global Historical Climatology Network - Daily."""
    stationid = stationid.replace("-", "")
    return ncei_cdo_json_to_df(
        "GHCND",
        stationid,
        start_date=start_date,
        end_date=end_date,
    )


@cltoolbox.command("ncei_gsod", formatter_class=HelpFormatter)
@tsutils.doc({**tsutils.docstrings, **ncei_ghcnd_docstrings})
def ncei_gsod_cli(stationid, start_date=None, end_date=None):
    r"""global station D:NCEI Global Summary of the Day (GSOD)

    National Centers for Environmental Information (NCEI) Global Summary of the
    MONTH (GSOM)
    https://gis.ncdc.noaa.gov/all-records/catalog/search/resource/details.page
    Cite this dataset when used as a source: Lawrimore, Jay (2016). Global
    Summary of the Month, Version 1.0. [indicate subset used]. NOAA National
    Centers for Environmental Information. DOI:10.7289/V5QV3JJ5

    National Centers for Environmental Information (NCEI) Global Summary of the
    YEAR (GSOY)
    https://gis.ncdc.noaa.gov/all-records/catalog/search/resource/details.page?id=gov.noaa.ncei:C00947
    Cite this dataset when used as a source: Lawrimore, Jay (2016). Global
    Summary of the Year, Version 1.0. [indicate subset used]. NOAA National
    Centers for Environmental Information

    Requires registration and free API key.

    NCEI cannot assume liability for any damages caused by any errors or
    omissions in the data, nor as a result of the failure of the data to
    function on a particular system. NCEI makes no warranty, expressed or
    implied, nor does the fact of distribution constitute such a warranty. NCEI
    can only certify that the data it distributes are an authentic copy of the
    records that were accepted for inclusion in the NCEI archives.

    The global summaries data set contains a monthly (GSOM) resolution of
    meteorological elements (max temp, snow, etc) from 1763 to present with
    updates weekly. The major parameters are: monthly mean maximum, mean
    minimum and mean temperatures; monthly total precipitation and snowfall;
    departure from normal of the mean temperature and total precipitation;
    monthly heating and cooling degree days; number of days that temperatures
    and precipitation are above or below certain thresholds; and extreme daily
    temperature and precipitation amounts. The primary source data set source
    is the Global Historical Climatology Network (GHCN)-Daily Data set. The
    global summaries data set also contains a yearly (GSOY) resolution of
    meteorological elements. See associated resources for more information.
    This data is not to be confused with "GHCN-Monthly", "Annual Summaries" or
    "ncei Summary of the Month". There are unique elements that are produced
    globally within the GSOM and GSOY data files.  There are also bias
    corrected temperature data in GHCN-Monthly, which will not be available in
    GSOM and GSOY. The GSOM and GSOY data set is going to replace the legacy
    DSI-3220 and expand to include non-U.S. (a.k.a. global) stations.  DSI-3220
    only included National Weather Service (NWS) COOP Published, or "Published
    in CD", sites.  For every datatype and record there is a set of meta-data
    flags.

    For the GHCNDMS dataset the flags are::

        'Total Missing','Consecutive Missing'

    Total Missing:

    Defined as total number of days observation/element is missing in that
    month.  This can be taken as a measure of quality or completeness as the
    higher the number of days sampled in the month, the more representative the
    value is for the entire month.

    Consecutive Missing:

    Defined as the maximum number of consecutive days in the month that an
    observation/element is missing.

    Parameters
    ----------
    ${stationid}
    ${start_date}
    ${end_date}
    """
    tsutils.printiso(
        ncei_gsod(stationid, start_date=start_date, end_date=end_date),
    )


# https://www.ncei.noaa.gov/data/global-summary-of-the-day/access/
# GSOD
@tsutils.copy_doc(ncei_gsod_cli)
def ncei_gsod(stationid, start_date=None, end_date=None):
    r"""Access NCEI Global Summary of the Day."""
    stationid = stationid.replace("-", "")
    df = ncei_cdo_json_to_df(
        "GSOD",
        stationid,
        start_date=start_date,
        end_date=end_date,
    )

    return df.rename(columns=add_units(df.columns))


# 1763-01-01, 2016-09-01, Global Summary of the Month , 1    , GSOM
@cltoolbox.command("ncei_gsom", formatter_class=HelpFormatter)
@tsutils.doc({**tsutils.docstrings, **ncei_ghcnd_docstrings})
def ncei_gsom_cli(stationid, start_date=None, end_date=None):
    r"""global station M:NCEI Global Summary of Month (GSOM)

    National Centers for Environmental Information (NCEI) Global Summary of the
    MONTH (GSOM)
    https://gis.ncdc.noaa.gov/all-records/catalog/search/resource/details.page
    Cite this dataset when used as a source: Lawrimore, Jay (2016). Global
    Summary of the Month, Version 1.0. [indicate subset used]. NOAA National
    Centers for Environmental Information. DOI:10.7289/V5QV3JJ5

    National Centers for Environmental Information (NCEI) Global Summary of the
    YEAR (GSOY)
    https://gis.ncdc.noaa.gov/all-records/catalog/search/resource/details.page?id=gov.noaa.ncei:C00947
    Cite this dataset when used as a source: Lawrimore, Jay (2016). Global
    Summary of the Year, Version 1.0. [indicate subset used]. NOAA National
    Centers for Environmental Information

    Requires registration and free API key.

    NCEI cannot assume liability for any damages caused by any errors or
    omissions in the data, nor as a result of the failure of the data to
    function on a particular system. NCEI makes no warranty, expressed or
    implied, nor does the fact of distribution constitute such a warranty. NCEI
    can only certify that the data it distributes are an authentic copy of the
    records that were accepted for inclusion in the NCEI archives.

    The global summaries data set contains a monthly (GSOM) resolution of
    meteorological elements (max temp, snow, etc) from 1763 to present with
    updates weekly. The major parameters are: monthly mean maximum, mean
    minimum and mean temperatures; monthly total precipitation and snowfall;
    departure from normal of the mean temperature and total precipitation;
    monthly heating and cooling degree days; number of days that temperatures
    and precipitation are above or below certain thresholds; and extreme daily
    temperature and precipitation amounts. The primary source data set source
    is the Global Historical Climatology Network (GHCN)-Daily Data set. The
    global summaries data set also contains a yearly (GSOY) resolution of
    meteorological elements. See associated resources for more information.
    This data is not to be confused with "GHCN-Monthly", "Annual Summaries" or
    "ncei Summary of the Month". There are unique elements that are produced
    globally within the GSOM and GSOY data files.  There are also bias
    corrected temperature data in GHCN-Monthly, which will not be available in
    GSOM and GSOY. The GSOM and GSOY data set is going to replace the legacy
    DSI-3220 and expand to include non-U.S. (a.k.a. global) stations.  DSI-3220
    only included National Weather Service (NWS) COOP Published, or "Published
    in CD", sites.  For every datatype and record there is a set of meta-data
    flags.

    For the GHCNDMS dataset the flags are::

        'Total Missing','Consecutive Missing'

    Total Missing:

    Defined as total number of days observation/element is missing in that
    month.  This can be taken as a measure of quality or completeness as the
    higher the number of days sampled in the month, the more representative the
    value is for the entire month.

    Consecutive Missing:

    Defined as the maximum number of consecutive days in the month that an
    observation/element is missing.

    Parameters
    ----------
    ${stationid}
    ${start_date}
    ${end_date}
    """
    tsutils.printiso(
        ncei_gsom(
            stationid,
            start_date=start_date,
            end_date=end_date,
        ),
    )


@tsutils.copy_doc(ncei_gsom_cli)
def ncei_gsom(stationid, start_date=None, end_date=None):
    r"""Access ncei Global Summary of Month (GSOM)."""
    stationid = stationid.replace("-", "")
    return ncei_cdo_json_to_df(
        "GSOM",
        stationid,
        start_date=start_date,
        end_date=end_date,
    )


# 1763-01-01, 2016-01-01, Global Summary of the Year  , 1    , GSOY
@cltoolbox.command("ncei_gsoy", formatter_class=HelpFormatter)
@tsutils.doc({**tsutils.docstrings, **ncei_ghcnd_docstrings})
def ncei_gsoy_cli(stationid, start_date=None, end_date=None):
    r"""global station A:NCEI Global Summary of Year (GSOY)

    National Centers for Environmental Information (NCEI) Global Summary of the YEAR
    (GSOY)
    https://gis.ncdc.noaa.gov/all-records/catalog/search/resource/details.page?id=gov.noaa.ncei:C00947
    Cite this dataset when used as a source: Lawrimore, Jay (2016). Global Summary of
    the Year, Version 1.0. [indicate subset used]. NOAA National Centers for
    Environmental Information.  DOI:10.7289/V5QV3JJ5

    Requires registration and free API key.

    NCEI cannot assume liability for any damages caused by any errors or
    omissions in the data, nor as a result of the failure of the data to
    function on a particular system. NCEI makes no warranty, expressed or
    implied, nor does the fact of distribution constitute such a warranty. NCEI
    can only certify that the data it distributes are an authentic copy of the
    records that were accepted for inclusion in the NCEI archives.

    The global summaries data set contains a monthly (GSOM) resolution of
    meteorological elements (max temp, snow, etc) from 1763 to present with
    updates weekly. The major parameters are: monthly mean maximum, mean
    minimum and mean temperatures; monthly total precipitation and snowfall;
    departure from normal of the mean temperature and total precipitation;
    monthly heating and cooling degree days; number of days that temperatures
    and precipitation are above or below certain thresholds; and extreme daily
    temperature and precipitation amounts. The primary source data set source
    is the Global Historical Climatology Network (GHCN)-Daily Data set. The
    global summaries data set also contains a yearly (GSOY) resolution of
    meteorological elements. See associated resources for more information.
    This data is not to be confused with "GHCN-Monthly", "Annual Summaries" or
    "ncei Summary of the Month". There are unique elements that are produced
    globally within the GSOM and GSOY data files.  There are also bias
    corrected temperature data in GHCN-Monthly, which will not be available in
    GSOM and GSOY. The GSOM and GSOY data set is going to replace the legacy
    DSI-3220 and expand to include non-U.S. (a.k.a. global) stations.  DSI-3220
    only included National Weather Service (NWS) COOP Published, or "Published
    in CD", sites.  For every datatype and record there is a set of meta-data
    flags.

    For the GHCNDMS dataset the flags are::

        'Total Missing','Consecutive Missing'

    Total Missing:

    Defined as total number of days observation/element is missing in that
    month.  This can be taken as a measure of quality or completeness as the
    higher the number of days sampled in the month, the more representative the
    value is for the entire month.

    Consecutive Missing:

    Defined as the maximum number of consecutive days in the month that an
    observation/element is missing.

    Parameters
    ----------
    ${stationid}
    ${start_date}
    ${end_date}
    """
    tsutils.printiso(
        ncei_gsoy(
            stationid,
            start_date=start_date,
            end_date=end_date,
        ),
    )


@tsutils.copy_doc(ncei_gsoy_cli)
def ncei_gsoy(stationid, start_date=None, end_date=None):
    r"""Access NCEI Global Summary of Year (GSOY)."""
    return ncei_cdo_json_to_df(
        "GSOY",
        stationid,
        start_date=start_date,
        end_date=end_date,
    )


# 1991-06-05, 2016-11-06, Weather Radar (Level II)    , 0.95 , NEXRAD2
# @cltoolbox.command('ncei_nexrad2', formatter_class=HelpFormatter)
def ncei_nexrad2_cli(stationid, start_date=None, end_date=None):
    r"""station: NCEI NEXRAD Level II.

    Requires registration and free API key.

    stationid:  Station ID.
    starttime:  Start date in ISO8601 format.
    endtime:  End date in ISO8601 format.

    For every datatype and record there is a set of meta-data flags.
    For the GHCNDMS dataset, the flags are::

        'Total Missing','Consecutive Missing'

    Total Missing:

    Defined as total number of days observation/element is missing in that
    month.  This can be taken as a measure of quality or completeness as the
    higher the number of days sampled in the month, the more representative the
    value is for the entire month.

    Consecutive Missing:

    Defined as the maximum number of consecutive days in the month that an
    observation/element is missing."""
    tsutils.printiso(
        ncei_nexrad2(stationid, start_date=start_date, end_date=end_date),
    )


@tsutils.copy_doc(ncei_nexrad2_cli)
def ncei_nexrad2(stationid, start_date=None, end_date=None):
    r"""National Centers for Environmental Information (NCEI) NEXRAD Level II."""
    return ncei_cdo_json_to_df(
        "NEXRAD2",
        stationid,
        start_date=start_date,
        end_date=end_date,
    )


# 1991-06-05, 2016-11-06, Weather Radar (Level III)   , 0.95 , NEXRAD3
# @cltoolbox.command('ncei_nexrad3',formatter_class=HelpFormatter)
def ncei_nexrad3_cli(stationid, start_date=None, end_date=None):
    r"""station: NCEI NEXRAD Level III.

    Requires registration and free API key.

    stationid:  Station ID.
    starttime:  Start date in ISO8601 format.
    endtime:  End date in ISO8601 format.

    For every datatype and record there is a set of meta-data flags.
    For the GHCNDMS dataset, the flags are::

        'Total Missing','Consecutive Missing'

    Total Missing:

    Defined as total number of days observation/element is missing in that
    month.  This can be taken as a measure of quality or completeness as the
    higher the number of days sampled in the month, the more representative the
    value is for the entire month.

    Consecutive Missing:

    Defined as the maximum number of consecutive days in the month that an
    observation/element is missing."""
    return tsutils.printiso(
        ncei_nexrad3(stationid, start_date=start_date, end_date=end_date),
    )


@tsutils.copy_doc(ncei_nexrad3_cli)
def ncei_nexrad3(stationid, start_date=None, end_date=None):
    r"""National Centers for Environmental Information (NCEI) NEXRAD Level III."""
    return ncei_cdo_json_to_df(
        "NEXRAD3",
        stationid,
        start_date=start_date,
        end_date=end_date,
    )


# 2010-01-01, 2010-01-01, Normals Annual/Seasonal     , 1    , NORMAL_ANN
@cltoolbox.command("ncei_normal_ann", formatter_class=HelpFormatter)
def ncei_normal_ann_cli(stationid):
    r"""global station A: NCEI annual normals

    Requires registration and free API key.

    The 1981-2010 Normals comprise all climate normals using the thirty year
    period of temperature, degree days, precipitation, snowfall, snow depth,
    wind, etc. Data is organized into hourly, daily, monthly, seasonal and
    annual.  This document describes the elements and layout of the Seasonal
    and Annual Normals which are derived from a composite of climate records
    from numerous sources that were merged and then subjected to a suite of
    quality assurance reviews.

    flags accompany every normals value and indicate the completeness of the
    data record used to compute each value, accounting for methodological
    differences for different product classes. There are six flag options
    described generally below. Due to methodological differences, the flags are
    applied somewhat differently between the temperature-based normals and the
    precipitation-based normals. For the precipitation-based and hourly
    normals, the following flags were assigned independently for each normals
    value reported based on number of years available for that individual
    calculation. For temperature-based normals, strong precedence is given to
    the monthly normals of maximum and minimum temperature or derived from the
    flags for these two variables.

    +-------+------------------------------------------------------------------+
    | Code  | Description                                                      |
    +=======+==================================================================+
    | C     | complete (all 30 years used)                                     |
    +-------+------------------------------------------------------------------+
    | S     | standard (no more than 5 years missing and no more than 3        |
    |       | consecutive years missing among the sufficiently complete years) |
    +-------+------------------------------------------------------------------+
    | R     | representative (observed record utilized incomplete, but value   |
    |       | was scaled or based on filled values to be representative of the |
    |       | full period of record)                                           |
    +-------+------------------------------------------------------------------+
    | P     | provisional (at least 10 years used, but not sufficiently        |
    |       | complete to be labeled as standard or representative). Also used |
    |       | for parameter values on February 29 as well as for interpolated  |
    |       | daily precipitation, snowfall, and snow depth percentiles.       |
    +-------+------------------------------------------------------------------+
    | Q     | quasi-normal (at least 2 years per month, but not sufficiently   |
    |       | complete to be labeled as provisional or any other higher flag   |
    |       | code. The associated value was computed using a pseudo-normals   |
    |       | approach or derived from monthly pseudo-normals.                 |
    +-------+------------------------------------------------------------------+
    | Blank | the data value is reported as a special value (see section B     |
    |       | under III. Additional Information below).                        |
    +-------+------------------------------------------------------------------+

    Note: flags Q and R aren't applicable to average number of days with
    different precipitation, snowfall, and snow depth threshold exceedance;
    precipitation/snowfall/snow probabilities of occurrence. Further, Q flags
    are not applicable for standard deviations.

    The following table lists the datatypes available for the annual dataset.
    Not all of these are available at all stations.

    +-------------------------+------------------------------------------------+
    | Code                    | Description                                    |
    +=========================+================================================+
    | ANN-CLDD-BASExx         | Average annual cooling degree days where xx is |
    |                         | the base in degree F. 'xx' can be one of 45,   |
    |                         | 50, 57, 60, 65, 70, 72                         |
    +-------------------------+------------------------------------------------+
    | ANN-CLDD-NORMAL         | Average annual cooling degree days with base   |
    |                         | 65F                                            |
    +-------------------------+------------------------------------------------+
    | ANN-DUTR-NORMAL         | Average annual diurnal temperature range       |
    +-------------------------+------------------------------------------------+
    | ANN-GRDD-BASExx         | Average annual growing degree days where xx is |
    |                         | the base in degree F. 'xx' can be one of 40,   |
    |                         | 45, 50, 55, 57, 60, 65, 70, 72.                |
    +-------------------------+------------------------------------------------+
    | ANN-GRDD-TB4886         | Average annual growing degree days with        |
    |                         | truncated bases 48F and 86F                    |
    +-------------------------+------------------------------------------------+
    | ANN-GRDD-TB5086         | Average annual growing degree days with        |
    |                         | truncated bases 50F and 86F                    |
    +-------------------------+------------------------------------------------+
    | ANN-HTDD-BASE40         | Average annual heating degree days with base   |
    |                         | 40F                                            |
    +-------------------------+------------------------------------------------+
    | ANN-HTDD-BASE45         | Average annual heating degree days with base   |
    |                         | 45F                                            |
    +-------------------------+------------------------------------------------+
    | ANN-HTDD-BASE50         | Average annual heating degree days with base   |
    |                         | 50F                                            |
    +-------------------------+------------------------------------------------+
    | ANN-HTDD-BASE55         | Average annual heating degree days with base   |
    |                         | 55F                                            |
    +-------------------------+------------------------------------------------+
    | ANN-HTDD-BASE57         | Average annual heating degree days with base   |
    |                         | 57F                                            |
    +-------------------------+------------------------------------------------+
    | ANN-HTDD-BASE60         | Average annual heating degree days with base   |
    |                         | 60F                                            |
    +-------------------------+------------------------------------------------+
    | ANN-HTDD-NORMAL         | Average annual heating degree days with base   |
    |                         | 65F                                            |
    +-------------------------+------------------------------------------------+
    | ANN-PRCP-AVGNDS-GE001HI | Average number of days during the year with    |
    |                         | precipitation >= 0.01 in                       |
    +-------------------------+------------------------------------------------+
    | ANN-PRCP-AVGNDS-GE010HI | Average number of days during the year with    |
    |                         | precipitation >= 0.10 in                       |
    +-------------------------+------------------------------------------------+
    | ANN-PRCP-AVGNDS-GE050HI | Average number of days during the year with    |
    |                         | precipitation >= 0.50 in                       |
    +-------------------------+------------------------------------------------+
    | ANN-PRCP-AVGNDS-GE100HI | Average number of days during the year with    |
    |                         | precipitation >= 1.00 in                       |
    +-------------------------+------------------------------------------------+
    | ANN-PRCP-NORMAL         | Average annual precipitation totals            |
    +-------------------------+------------------------------------------------+
    | ANN-SNOW-AVGNDS-GE001TI | Average number of days during the year with    |
    |                         | snowfall >= 0.1 in                             |
    +-------------------------+------------------------------------------------+
    | ANN-SNOW-AVGNDS-GE010TI | Average number of days during the year with    |
    |                         | snowfall >= 1.0 in                             |
    +-------------------------+------------------------------------------------+
    | ANN-SNOW-AVGNDS-GE030TI | Average number of days during the year with    |
    |                         | snowfall >= 3.0 in                             |
    +-------------------------+------------------------------------------------+
    | ANN-SNOW-AVGNDS-GE050TI | Average number of days during the year with    |
    |                         | snowfall >= 5.0 in                             |
    +-------------------------+------------------------------------------------+
    | ANN-SNOW-AVGNDS-GE100TI | Average number of days during the year with    |
    |                         | snowfall >= 10.0 in                            |
    +-------------------------+------------------------------------------------+
    | ANN-SNOW-NORMAL         | Average annual snowfall totals                 |
    +-------------------------+------------------------------------------------+
    | ANN-SNWD-AVGNDS-GE001WI | Average number of days during the year with    |
    |                         | snow depth >= 1 inch                           |
    +-------------------------+------------------------------------------------+
    | ANN-SNWD-AVGNDS-GE003WI | Average number of days during the year with    |
    |                         | snow depth >= 3 in                             |
    +-------------------------+------------------------------------------------+
    | ANN-SNWD-AVGNDS-GE005WI | Average number of days during the year with    |
    |                         | snow depth >=5 in                              |
    +-------------------------+------------------------------------------------+
    | ANN-SNWD-AVGNDS-GE010WI | Average number of days during the year with    |
    |                         | snow depth >=10 in                             |
    +-------------------------+------------------------------------------------+
    | ANN-TAVG-NORMAL         | Average annual average temperature             |
    +-------------------------+------------------------------------------------+
    | ANN-TMAX-AVGNDS-GRTH040 | Average number of days per year where tmax is  |
    |                         | greater than or equal to 40F                   |
    +-------------------------+------------------------------------------------+
    | ANN-TMAX-AVGNDS-GRTH050 | Average number of days per year where tmax is  |
    |                         | greater than or equal to 50F                   |
    +-------------------------+------------------------------------------------+
    | ANN-TMAX-AVGNDS-GRTH060 | Average number of days per year where tmax is  |
    |                         | greater than or equal to 60F                   |
    +-------------------------+------------------------------------------------+
    | ANN-TMAX-AVGNDS-GRTH070 | Average number of days per year where tmax is  |
    |                         | greater than or equal to 70F                   |
    +-------------------------+------------------------------------------------+
    | ANN-TMAX-AVGNDS-GRTH080 | Average number of days per year where tmax is  |
    |                         | greater than or equal to 80F                   |
    +-------------------------+------------------------------------------------+
    | ANN-TMAX-AVGNDS-GRTH090 | Average number of days per year where tmax is  |
    |                         | greater than or equal to 90F                   |
    +-------------------------+------------------------------------------------+
    | ANN-TMAX-AVGNDS-GRTH100 | Average number of days per year where tmax is  |
    |                         | greater than or equal to 100F                  |
    +-------------------------+------------------------------------------------+
    | ANN-TMAX-AVGNDS-LSTH032 | Average number of days per year where tmax is  |
    |                         | less than or equal to 32F                      |
    +-------------------------+------------------------------------------------+
    | ANN-TMAX-NORMAL         | Average annual maximum temperature             |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-AVGNDS-LSTH000 | Average number of days per year where tmin is  |
    |                         | less than or equal to 0F                       |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-AVGNDS-LSTH010 | Average number of days per year where tmin is  |
    |                         | less than or equal to 10F                      |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-AVGNDS-LSTH020 | Average number of days per year where tmin is  |
    |                         | less than or equal to 20F                      |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-AVGNDS-LSTH032 | Average number of days per year where tmin is  |
    |                         | less than or equal to 32F                      |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-AVGNDS-LSTH040 | Average number of days per year where tmin is  |
    |                         | less than or equal to 40F                      |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-AVGNDS-LSTH050 | Average number of days per year where tmin is  |
    |                         | less than or equal to 50F                      |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-AVGNDS-LSTH060 | Average number of days per year where tmin is  |
    |                         | less than or equal to 60F                      |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-AVGNDS-LSTH070 | Average number of days per year where tmin is  |
    |                         | less than or equal to 70F                      |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-NORMAL         | Average annual minimum temperature             |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T16FP10 | 10 percent probability date of first 16F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T16FP20 | 20 percent probability date of first 16F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T16FP30 | 30 percent probability date of first 16F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T16FP40 | 40 percent probability date of first 16F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T16FP50 | 50 percent probability date of first 16F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T16FP60 | 60 percent probability date of first 16F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T16FP70 | 70 percent probability date of first 16F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T16FP80 | 80 percent probability date of first 16F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T16FP90 | 90 percent probability date of first 16F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T20FP10 | 10 percent probability date of first 20F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T20FP20 | 20 percent probability date of first 20F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T20FP30 | 30 percent probability date of first 20F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T20FP40 | 40 percent probability date of first 20F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T20FP50 | 50 percent probability date of first 20F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T20FP60 | 60 percent probability date of first 20F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T20FP70 | 70 percent probability date of first 20F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T20FP80 | 80 percent probability date of first 20F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T20FP90 | 90 percent probability date of first 20F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T24FP10 | 10 percent probability date of first 24F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T24FP20 | 20 percent probability date of first 24F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T24FP30 | 30 percent probability date of first 24F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T24FP40 | 40 percent probability date of first 24F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T24FP50 | 50 percent probability date of first 24F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T24FP60 | 60 percent probability date of first 24F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T24FP70 | 70 percent probability date of first 24F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T24FP80 | 80 percent probability date of first 24F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T24FP90 | 90 percent probability date of first 24F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T28FP10 | 10 percent probability date of first 28F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T28FP20 | 20 percent probability date of first 28F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T28FP30 | 30 percent probability date of first 28F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T28FP40 | 40 percent probability date of first 28F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T28FP50 | 50 percent probability date of first 28F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T28FP60 | 60 percent probability date of first 28F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T28FP70 | 70 percent probability date of first 28F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T28FP80 | 80 percent probability date of first 28F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T28FP90 | 90 percent probability date of first 28F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T32FP10 | 10 percent probability date of first 32F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T32FP20 | 20 percent probability date of first 32F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T32FP30 | 30 percent probability date of first 32F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T32FP40 | 40 percent probability date of first 32F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T32FP50 | 50 percent probability date of first 32F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T32FP60 | 60 percent probability date of first 32F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T32FP70 | 70 percent probability date of first 32F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T32FP80 | 80 percent probability date of first 32F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T32FP90 | 90 percent probability date of first 32F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T36FP10 | 10 percent probability date of first 36F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T36FP20 | 20 percent probability date of first 36F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T36FP30 | 30 percent probability date of first 36F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T36FP40 | 40 percent probability date of first 36F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T36FP50 | 50 percent probability date of first 36F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T36FP60 | 60 percent probability date of first 36F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T36FP70 | 70 percent probability date of first 36F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T36FP80 | 80 percent probability date of first 36F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBFST-T36FP90 | 90 percent probability date of first 36F       |
    |                         | occurrence or earlier                          |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T16FP10 | 10 percent probability of 16F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T16FP20 | 20 percent probability of 16F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T16FP30 | 30 percent probability of 16F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T16FP40 | 40 percent probability of 16F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T16FP50 | 50 percent probability of 16F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T16FP60 | 60 percent probability of 16F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T16FP70 | 70 percent probability of 16F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T16FP80 | 80 percent probability of 16F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T16FP90 | 90 percent probability of 16F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T20FP10 | 10 percent probability of 20F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T20FP20 | 20 percent probability of 20F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T20FP30 | 30 percent probability of 20F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T20FP40 | 40 percent probability of 20F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T20FP50 | 50 percent probability of 20F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T20FP60 | 60 percent probability of 20F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T20FP70 | 70 percent probability of 20F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T20FP80 | 80 percent probability of 20F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T20FP90 | 90 percent probability of 20F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T24FP10 | 10 percent probability of 24F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T24FP20 | 20 percent probability of 24F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T24FP30 | 30 percent probability of 24F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T24FP40 | 40 percent probability of 24F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T24FP50 | 50 percent probability of 24F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T24FP60 | 60 percent probability of 24F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T24FP70 | 70 percent probability of 24F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T24FP80 | 80 percent probability of 24F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T24FP90 | 90 percent probability of 24F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T28FP10 | 10 percent probability of 28F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T28FP20 | 20 percent probability of 28F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T28FP30 | 30 percent probability of 28F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T28FP40 | 40 percent probability of 28F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T28FP50 | 50 percent probability of 28F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T28FP60 | 60 percent probability of 28F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T28FP70 | 70 percent probability of 28F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T28FP80 | 80 percent probability of 28F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T28FP90 | 90 percent probability of 28F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T32FP10 | 10 percent probability of 32F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T32FP20 | 20 percent probability of 32F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T32FP30 | 30 percent probability of 32F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T32FP40 | 40 percent probability of 32F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T32FP50 | 50 percent probability of 32F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T32FP60 | 60 percent probability of 32F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T32FP70 | 70 percent probability of 32F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T32FP80 | 80 percent probability of 32F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T32FP90 | 90 percent probability of 32F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T36FP10 | 10 percent probability of 36F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T36FP20 | 20 percent probability of 36F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T36FP30 | 30 percent probability of 36F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T36FP40 | 40 percent probability of 36F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T36FP50 | 50 percent probability of 36F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T36FP60 | 60 percent probability of 36F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T36FP70 | 70 percent probability of 36F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T36FP80 | 80 percent probability of 36F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBGSL-T36FP90 | 90 percent probability of 36F growing season   |
    |                         | length or longer                               |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T16FP10 | 10 percent probability date of last 16F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T16FP20 | 20 percent probability date of last 16F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T16FP30 | 30 percent probability date of last 16F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T16FP40 | 40 percent probability date of last 16F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T16FP50 | 50 percent probability date of last 16F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T16FP60 | 60 percent probability date of last 16F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T16FP70 | 70 percent probability date of last 16F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T16FP80 | 80 percent probability date of last 16F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T16FP90 | 90 percent probability date of last 16F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T20FP10 | 10 percent probability date of last 20F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T20FP20 | 20 percent probability date of last 20F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T20FP30 | 30 percent probability date of last 20F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T20FP40 | 40 percent probability date of last 20F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T20FP50 | 50 percent probability date of last 20F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T20FP60 | 60 percent probability date of last 20F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T20FP70 | 70 percent probability date of last 20F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T20FP80 | 80 percent probability date of last 20F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T20FP90 | 90 percent probability date of last 20F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T24FP10 | 10 percent probability date of last 24F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T24FP20 | 20 percent probability date of last 24F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T24FP30 | 30 percent probability date of last 24F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T24FP40 | 40 percent probability date of last 24F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T24FP50 | 50 percent probability date of last 24F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T24FP60 | 60 percent probability date of last 24F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T24FP70 | 70 percent probability date of last 24F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T24FP80 | 80 percent probability date of last 24F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T24FP90 | 90 percent probability date of last 24F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T28FP10 | 10 percent probability date of last 28F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T28FP20 | 20 percent probability date of last 28F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T28FP30 | 30 percent probability date of last 28F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T28FP40 | 40 percent probability date of last 28F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T28FP50 | 50 percent probability date of last 28F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T28FP60 | 60 percent probability date of last 28F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T28FP70 | 70 percent probability date of last 28F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T28FP80 | 80 percent probability date of last 28F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T28FP90 | 90 percent probability date of last 28F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T32FP10 | 10 percent probability date of last 32F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T32FP20 | 20 percent probability date of last 32F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T32FP30 | 30 percent probability date of last 32F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T32FP40 | 40 percent probability date of last 32F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T32FP50 | 50 percent probability date of last 32F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T32FP60 | 60 percent probability date of last 32F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T32FP70 | 70 percent probability date of last 32F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T32FP80 | 80 percent probability date of last 32F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T32FP90 | 90 percent probability date of last 32F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T36FP10 | 10 percent probability date of last 36F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T36FP20 | 20 percent probability date of last 36F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T36FP30 | 30 percent probability date of last 36F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T36FP40 | 40 percent probability date of last 36F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T36FP50 | 50 percent probability date of last 36F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T36FP60 | 60 percent probability date of last 36F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T36FP70 | 70 percent probability date of last 36F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T36FP80 | 80 percent probability date of last 36F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBLST-T36FP90 | 90 percent probability date of last 36F        |
    |                         | occurrence or later                            |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBOCC-LSTH016 | probability of 16F or below at least once in   |
    |                         | the year                                       |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBOCC-LSTH020 | probability of 20F or below at least once in   |
    |                         | the year                                       |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBOCC-LSTH024 | probability of 24F or below at least once in   |
    |                         | the year                                       |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBOCC-LSTH028 | probability of 28F or below at least once in   |
    |                         | the year                                       |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBOCC-LSTH032 | probability of 32F or below at least once in   |
    |                         | the year                                       |
    +-------------------------+------------------------------------------------+
    | ANN-TMIN-PRBOCC-LSTH036 | probability of 36F or below at least once in   |
    |                         | the year                                       |
    +-------------------------+------------------------------------------------+
    | DJF-CLDD-BASE45         | Average winter cooling degree days with base   |
    |                         | 45F                                            |
    +-------------------------+------------------------------------------------+
    | DJF-CLDD-BASE50         | Average winter cooling degree days with base   |
    |                         | 50F                                            |
    +-------------------------+------------------------------------------------+
    | DJF-CLDD-BASE55         | Average winter cooling degree days with base   |
    |                         | 55F                                            |
    +-------------------------+------------------------------------------------+
    | DJF-CLDD-BASE57         | Average winter cooling degree days with base   |
    |                         | 57F                                            |
    +-------------------------+------------------------------------------------+
    | DJF-CLDD-BASE60         | Average winter cooling degree days with base   |
    |                         | 60F                                            |
    +-------------------------+------------------------------------------------+
    | DJF-CLDD-BASE70         | Average winter cooling degree days with base   |
    |                         | 70F                                            |
    +-------------------------+------------------------------------------------+
    | DJF-CLDD-BASE72         | Average winter cooling degree days with base   |
    |                         | 72F                                            |
    +-------------------------+------------------------------------------------+
    | DJF-CLDD-NORMAL         | Average winter cooling degree days with base   |
    |                         | 65F                                            |
    +-------------------------+------------------------------------------------+
    | DJF-DUTR-NORMAL         | Average winter diurnal temperature range       |
    +-------------------------+------------------------------------------------+
    | DJF-GRDD-BASE40         | Average winter growing degree days with base   |
    |                         | 40F                                            |
    +-------------------------+------------------------------------------------+
    | DJF-GRDD-BASE45         | Average winter growing degree days with base   |
    |                         | 45F                                            |
    +-------------------------+------------------------------------------------+
    | DJF-GRDD-BASE50         | Average winter growing degree days with base   |
    |                         | 50F                                            |
    +-------------------------+------------------------------------------------+
    | DJF-GRDD-BASE55         | Average winter growing degree days with base   |
    |                         | 55F                                            |
    +-------------------------+------------------------------------------------+
    | DJF-GRDD-BASE57         | Average winter growing degree days with base   |
    |                         | 57F                                            |
    +-------------------------+------------------------------------------------+
    | DJF-GRDD-BASE60         | Average winter growing degree days with base   |
    |                         | 60F                                            |
    +-------------------------+------------------------------------------------+
    | DJF-GRDD-BASE65         | Average winter growing degree days with base   |
    |                         | 65F                                            |
    +-------------------------+------------------------------------------------+
    | DJF-GRDD-BASE70         | Average winter growing degree days with base   |
    |                         | 70F                                            |
    +-------------------------+------------------------------------------------+
    | DJF-GRDD-BASE72         | Average winter growing degree days with base   |
    |                         | 72F                                            |
    +-------------------------+------------------------------------------------+
    | DJF-GRDD-TB4886         | Average winter growing degree days with        |
    |                         | truncated bases 48F and 86F                    |
    +-------------------------+------------------------------------------------+
    | DJF-GRDD-TB5086         | Average winter growing degree days with        |
    |                         | truncated bases 50F and 86F                    |
    +-------------------------+------------------------------------------------+
    | DJF-HTDD-BASE40         | Average winter heating degree days with base   |
    |                         | 40F                                            |
    +-------------------------+------------------------------------------------+
    | DJF-HTDD-BASE45         | Average winter heating degree days with base   |
    |                         | 45F                                            |
    +-------------------------+------------------------------------------------+
    | DJF-HTDD-BASE50         | Average winter heating degree days with base   |
    |                         | 50F                                            |
    +-------------------------+------------------------------------------------+
    | DJF-HTDD-BASE55         | Average winter heating degree days with base   |
    |                         | 55F                                            |
    +-------------------------+------------------------------------------------+
    | DJF-HTDD-BASE57         | Average winter heating degree days with base   |
    |                         | 57F                                            |
    +-------------------------+------------------------------------------------+
    | DJF-HTDD-BASE60         | Average winter heating degree days with base   |
    |                         | 60F                                            |
    +-------------------------+------------------------------------------------+
    | DJF-HTDD-NORMAL         | Average winter heating degree days with base   |
    |                         | 65F                                            |
    +-------------------------+------------------------------------------------+
    | DJF-PRCP-AVGNDS-GE001HI | Average number of days during December-        |
    |                         | February with precipitation >= 0.01 in         |
    +-------------------------+------------------------------------------------+
    | DJF-PRCP-AVGNDS-GE010HI | Average number of days during December-        |
    |                         | February with precipitation >= 0.10 in         |
    +-------------------------+------------------------------------------------+
    | DJF-PRCP-AVGNDS-GE050HI | Average number of days during December-        |
    |                         | February with precipitation >= 0.50 in         |
    +-------------------------+------------------------------------------------+
    | DJF-PRCP-AVGNDS-GE100HI | Average number of days during December-        |
    |                         | February with precipitation >= 1.00 in         |
    +-------------------------+------------------------------------------------+
    | DJF-PRCP-NORMAL         | Average seasonal precipitation totals for      |
    |                         | December- February                             |
    +-------------------------+------------------------------------------------+
    | DJF-SNOW-AVGNDS-GE001TI | Average number of days during December-        |
    |                         | February with snowfall >= 0.1 in               |
    +-------------------------+------------------------------------------------+
    | DJF-SNOW-AVGNDS-GE010TI | Average number of days during December-        |
    |                         | February with snowfall >= 1.0 in               |
    +-------------------------+------------------------------------------------+
    | DJF-SNOW-AVGNDS-GE030TI | Average number of days during December-        |
    |                         | February with snowfall >= 3.0 in               |
    +-------------------------+------------------------------------------------+
    | DJF-SNOW-AVGNDS-GE050TI | Average number of days during December-        |
    |                         | February with snowfall >= 5.0 in               |
    +-------------------------+------------------------------------------------+
    | DJF-SNOW-AVGNDS-GE100TI | Average number of days during December-        |
    |                         | February with snowfall >= 10.0 in              |
    +-------------------------+------------------------------------------------+
    | DJF-SNOW-NORMAL         | Average seasonal snowfall totals for December- |
    |                         | February                                       |
    +-------------------------+------------------------------------------------+
    | DJF-SNWD-AVGNDS-GE001WI | Average number of days during December-        |
    |                         | February with snow depth >= 1 inch             |
    +-------------------------+------------------------------------------------+
    | DJF-SNWD-AVGNDS-GE003WI | Average number of days during December-        |
    |                         | February with snow depth >= 3 in               |
    +-------------------------+------------------------------------------------+
    | DJF-SNWD-AVGNDS-GE005WI | Average number of days during December-        |
    |                         | February with snow depth >= 5 in               |
    +-------------------------+------------------------------------------------+
    | DJF-SNWD-AVGNDS-GE010WI | Average number of days during December-        |
    |                         | February with snow depth >= 10 in              |
    +-------------------------+------------------------------------------------+
    | DJF-TAVG-NORMAL         | Average winter average temperature             |
    +-------------------------+------------------------------------------------+
    | DJF-TMAX-AVGNDS-GRTH040 | Average number of days per winter where tmax   |
    |                         | is greater than or equal to 40F                |
    +-------------------------+------------------------------------------------+
    | DJF-TMAX-AVGNDS-GRTH050 | Average number of days per winter where tmax   |
    |                         | is greater than or equal to 50F                |
    +-------------------------+------------------------------------------------+
    | DJF-TMAX-AVGNDS-GRTH060 | Average number of days per winter where tmax   |
    |                         | is greater than or equal to 60F                |
    +-------------------------+------------------------------------------------+
    | DJF-TMAX-AVGNDS-GRTH070 | Average number of days per winter where tmax   |
    |                         | is greater than or equal to 70F                |
    +-------------------------+------------------------------------------------+
    | DJF-TMAX-AVGNDS-GRTH080 | Average number of days per winter where tmax   |
    |                         | is greater than or equal to 80F                |
    +-------------------------+------------------------------------------------+
    | DJF-TMAX-AVGNDS-GRTH090 | Average number of days per winter where tmax   |
    |                         | is greater than or equal to 90F                |
    +-------------------------+------------------------------------------------+
    | DJF-TMAX-AVGNDS-GRTH100 | Average number of days per winter where tmax   |
    |                         | is greater than or equal to 100F               |
    +-------------------------+------------------------------------------------+
    | DJF-TMAX-AVGNDS-LSTH032 | Average number of days per winter where tmax   |
    |                         | is less than or equal to 32F                   |
    +-------------------------+------------------------------------------------+
    | DJF-TMAX-NORMAL         | Average winter maximum temperature             |
    +-------------------------+------------------------------------------------+
    | DJF-TMIN-AVGNDS-LSTH000 | Average number of days per winter where tmin   |
    |                         | is less than or equal to 0F                    |
    +-------------------------+------------------------------------------------+
    | DJF-TMIN-AVGNDS-LSTH010 | Average number of days per winter where tmin   |
    |                         | is less than or equal to 10F                   |
    +-------------------------+------------------------------------------------+
    | DJF-TMIN-AVGNDS-LSTH020 | Average number of days per winter where tmin   |
    |                         | is less than or equal to 20F                   |
    +-------------------------+------------------------------------------------+
    | DJF-TMIN-AVGNDS-LSTH032 | Average number of days per winter where tmin   |
    |                         | is less than or equal to 32F                   |
    +-------------------------+------------------------------------------------+
    | DJF-TMIN-AVGNDS-LSTH040 | Average number of days per winter where tmin   |
    |                         | is less than or equal to 40F                   |
    +-------------------------+------------------------------------------------+
    | DJF-TMIN-AVGNDS-LSTH050 | Average number of days per winter where tmin   |
    |                         | is less than or equal to 50F                   |
    +-------------------------+------------------------------------------------+
    | DJF-TMIN-AVGNDS-LSTH060 | Average number of days per winter where tmin   |
    |                         | is less than or equal to 60F                   |
    +-------------------------+------------------------------------------------+
    | DJF-TMIN-AVGNDS-LSTH070 | Average number of days per winter where tmin   |
    |                         | is less than or equal to 70F                   |
    +-------------------------+------------------------------------------------+
    | DJF-TMIN-NORMAL         | Average winter minimum temperature             |
    +-------------------------+------------------------------------------------+
    | JJA-CLDD-BASE45         | Average summer cooling degree days with base   |
    |                         | 45F                                            |
    +-------------------------+------------------------------------------------+
    | JJA-CLDD-BASE50         | Average summer cooling degree days with base   |
    |                         | 50F                                            |
    +-------------------------+------------------------------------------------+
    | JJA-CLDD-BASE55         | Average summer cooling degree days with base   |
    |                         | 55F                                            |
    +-------------------------+------------------------------------------------+
    | JJA-CLDD-BASE57         | Average summer cooling degree days with base   |
    |                         | 57F                                            |
    +-------------------------+------------------------------------------------+
    | JJA-CLDD-BASE60         | Average summer cooling degree days with base   |
    |                         | 60F                                            |
    +-------------------------+------------------------------------------------+
    | JJA-CLDD-BASE70         | Average summer cooling degree days with base   |
    |                         | 70F                                            |
    +-------------------------+------------------------------------------------+
    | JJA-CLDD-BASE72         | Average summer cooling degree days with base   |
    |                         | 72F                                            |
    +-------------------------+------------------------------------------------+
    | JJA-CLDD-NORMAL         | Average summer cooling degree days with base   |
    |                         | 65F                                            |
    +-------------------------+------------------------------------------------+
    | JJA-DUTR-NORMAL         | Average summer diurnal temperature range       |
    +-------------------------+------------------------------------------------+
    | JJA-GRDD-BASE40         | Average summer growing degree days with base   |
    |                         | 40F                                            |
    +-------------------------+------------------------------------------------+
    | JJA-GRDD-BASE45         | Average summer growing degree days with base   |
    |                         | 45F                                            |
    +-------------------------+------------------------------------------------+
    | JJA-GRDD-BASE50         | Average summer growing degree days with base   |
    |                         | 50F                                            |
    +-------------------------+------------------------------------------------+
    | JJA-GRDD-BASE55         | Average summer growing degree days with base   |
    |                         | 55F                                            |
    +-------------------------+------------------------------------------------+
    | JJA-GRDD-BASE57         | Average summer growing degree days with base   |
    |                         | 57F                                            |
    +-------------------------+------------------------------------------------+
    | JJA-GRDD-BASE60         | Average summer growing degree days with base   |
    |                         | 60F                                            |
    +-------------------------+------------------------------------------------+
    | JJA-GRDD-BASE65         | Average summer growing degree days with base   |
    |                         | 65F                                            |
    +-------------------------+------------------------------------------------+
    | JJA-GRDD-BASE70         | Average summer growing degree days with base   |
    |                         | 70F                                            |
    +-------------------------+------------------------------------------------+
    | JJA-GRDD-BASE72         | Average summer growing degree days with base   |
    |                         | 72F                                            |
    +-------------------------+------------------------------------------------+
    | JJA-GRDD-TB4886         | Average summer growing degree days with        |
    |                         | truncated bases 48F and 86F                    |
    +-------------------------+------------------------------------------------+
    | JJA-GRDD-TB5086         | Average summer growing degree days with        |
    |                         | truncated bases 50F and 86F                    |
    +-------------------------+------------------------------------------------+
    | JJA-HTDD-BASE40         | Average summer heating degree days with base   |
    |                         | 40F                                            |
    +-------------------------+------------------------------------------------+
    | JJA-HTDD-BASE45         | Average summer heating degree days with base   |
    |                         | 45F                                            |
    +-------------------------+------------------------------------------------+
    | JJA-HTDD-BASE50         | Average summer heating degree days with base   |
    |                         | 50F                                            |
    +-------------------------+------------------------------------------------+
    | JJA-HTDD-BASE55         | Average summer heating degree days with base   |
    |                         | 55F                                            |
    +-------------------------+------------------------------------------------+
    | JJA-HTDD-BASE57         | Average summer heating degree days with base   |
    |                         | 57F                                            |
    +-------------------------+------------------------------------------------+
    | JJA-HTDD-BASE60         | Average summer heating degree days with base   |
    |                         | 60F                                            |
    +-------------------------+------------------------------------------------+
    | JJA-HTDD-NORMAL         | Average summer heating degree days with base   |
    |                         | 65F                                            |
    +-------------------------+------------------------------------------------+
    | JJA-PRCP-AVGNDS-GE001HI | Average number of days during June-August with |
    |                         | precipitation >= 0.01 in                       |
    +-------------------------+------------------------------------------------+
    | JJA-PRCP-AVGNDS-GE010HI | Average number of days during June-August with |
    |                         | precipitation >= 0.10 in                       |
    +-------------------------+------------------------------------------------+
    | JJA-PRCP-AVGNDS-GE050HI | Average number of days during June-August with |
    |                         | precipitation >= 0.50 in                       |
    +-------------------------+------------------------------------------------+
    | JJA-PRCP-AVGNDS-GE100HI | Average number of days during June-August with |
    |                         | precipitation >= 1.00 in                       |
    +-------------------------+------------------------------------------------+
    | JJA-PRCP-NORMAL         | Average seasonal precipitation totals for      |
    |                         | June- August                                   |
    +-------------------------+------------------------------------------------+
    | JJA-SNOW-AVGNDS-GE001TI | Average number of days during June-August with |
    |                         | snowfall >= 0.1 in                             |
    +-------------------------+------------------------------------------------+
    | JJA-SNOW-AVGNDS-GE010TI | Average number of days during June-August with |
    |                         | snowfall >= 1.0 in                             |
    +-------------------------+------------------------------------------------+
    | JJA-SNOW-AVGNDS-GE030TI | Average number of days during June-August with |
    |                         | snowfall >= 3.0 in                             |
    +-------------------------+------------------------------------------------+
    | JJA-SNOW-AVGNDS-GE050TI | Average number of days during June-August with |
    |                         | snowfall >= 5.0 in                             |
    +-------------------------+------------------------------------------------+
    | JJA-SNOW-AVGNDS-GE100TI | Average number of days during June-August with |
    |                         | snowfall >= 10.0 in                            |
    +-------------------------+------------------------------------------------+
    | JJA-SNOW-NORMAL         | Average seasonal snowfall totals for June-     |
    |                         | August                                         |
    +-------------------------+------------------------------------------------+
    | JJA-SNWD-AVGNDS-GE001WI | Average number of days during June-August with |
    |                         | snow depth >= 1 inch                           |
    +-------------------------+------------------------------------------------+
    | JJA-SNWD-AVGNDS-GE003WI | Average number of days during June-August with |
    |                         | snow depth >= 3 in                             |
    +-------------------------+------------------------------------------------+
    | JJA-SNWD-AVGNDS-GE005WI | Average number of days during June-August with |
    |                         | snow depth >= 5 in                             |
    +-------------------------+------------------------------------------------+
    | JJA-SNWD-AVGNDS-GE010WI | Average number of days during June-August with |
    |                         | snow depth >= 10 in                            |
    +-------------------------+------------------------------------------------+
    | JJA-TAVG-NORMAL         | Average summer average temperature             |
    +-------------------------+------------------------------------------------+
    | JJA-TMAX-AVGNDS-GRTH040 | Average number of days per summer where tmax   |
    |                         | is greater than or equal to 40F                |
    +-------------------------+------------------------------------------------+
    | JJA-TMAX-AVGNDS-GRTH050 | Average number of days per summer where tmax   |
    |                         | is greater than or equal to 50F                |
    +-------------------------+------------------------------------------------+
    | JJA-TMAX-AVGNDS-GRTH060 | Average number of days per summer where tmax   |
    |                         | is greater than or equal to 60F                |
    +-------------------------+------------------------------------------------+
    | JJA-TMAX-AVGNDS-GRTH070 | Average number of days per summer where tmax   |
    |                         | is greater than or equal to 70F                |
    +-------------------------+------------------------------------------------+
    | JJA-TMAX-AVGNDS-GRTH080 | Average number of days per summer where tmax   |
    |                         | is greater than or equal to 80F                |
    +-------------------------+------------------------------------------------+
    | JJA-TMAX-AVGNDS-GRTH090 | Average number of days per summer where tmax   |
    |                         | is greater than or equal to 90F                |
    +-------------------------+------------------------------------------------+
    | JJA-TMAX-AVGNDS-GRTH100 | Average number of days per summer where tmax   |
    |                         | is greater than or equal to 100F               |
    +-------------------------+------------------------------------------------+
    | JJA-TMAX-AVGNDS-LSTH032 | Average number of days per summer where tmax   |
    |                         | is less than or equal to 32F                   |
    +-------------------------+------------------------------------------------+
    | JJA-TMAX-NORMAL         | Average summer maximum temperature             |
    +-------------------------+------------------------------------------------+
    | JJA-TMIN-AVGNDS-LSTH000 | Average number of days per summer where tmin   |
    |                         | is less than or equal to 0F                    |
    +-------------------------+------------------------------------------------+
    | JJA-TMIN-AVGNDS-LSTH010 | Average number of days per summer where tmin   |
    |                         | is less than or equal to 10F                   |
    +-------------------------+------------------------------------------------+
    | JJA-TMIN-AVGNDS-LSTH020 | Average number of days per summer where tmin   |
    |                         | is less than or equal to 20F                   |
    +-------------------------+------------------------------------------------+
    | JJA-TMIN-AVGNDS-LSTH032 | Average number of days per summer where tmin   |
    |                         | is less than or equal to 32F                   |
    +-------------------------+------------------------------------------------+
    | JJA-TMIN-AVGNDS-LSTH040 | Average number of days per summer where tmin   |
    |                         | is less than or equal to 40F                   |
    +-------------------------+------------------------------------------------+
    | JJA-TMIN-AVGNDS-LSTH050 | Average number of days per summer where tmin   |
    |                         | is less than or equal to 50F                   |
    +-------------------------+------------------------------------------------+
    | JJA-TMIN-AVGNDS-LSTH060 | Average number of days per summer where tmin   |
    |                         | is less than or equal to 60F                   |
    +-------------------------+------------------------------------------------+
    | JJA-TMIN-AVGNDS-LSTH070 | Average number of days per summer where tmin   |
    |                         | is less than or equal to 70F                   |
    +-------------------------+------------------------------------------------+
    | JJA-TMIN-NORMAL         | Average summer minimum temperature             |
    +-------------------------+------------------------------------------------+
    | MAM-CLDD-BASE45         | Average spring cooling degree days with base   |
    |                         | 45F                                            |
    +-------------------------+------------------------------------------------+
    | MAM-CLDD-BASE50         | Average spring cooling degree days with base   |
    |                         | 50F                                            |
    +-------------------------+------------------------------------------------+
    | MAM-CLDD-BASE55         | Average spring cooling degree days with base   |
    |                         | 55F                                            |
    +-------------------------+------------------------------------------------+
    | MAM-CLDD-BASE57         | Average spring cooling degree days with base   |
    |                         | 57F                                            |
    +-------------------------+------------------------------------------------+
    | MAM-CLDD-BASE60         | Average spring cooling degree days with base   |
    |                         | 60F                                            |
    +-------------------------+------------------------------------------------+
    | MAM-CLDD-BASE70         | Average spring cooling degree days with base   |
    |                         | 70F                                            |
    +-------------------------+------------------------------------------------+
    | MAM-CLDD-BASE72         | Average spring cooling degree days with base   |
    |                         | 72F                                            |
    +-------------------------+------------------------------------------------+
    | MAM-CLDD-NORMAL         | Average spring cooling degree days with base   |
    |                         | 65F                                            |
    +-------------------------+------------------------------------------------+
    | MAM-DUTR-NORMAL         | Average spring diurnal temperature range       |
    +-------------------------+------------------------------------------------+
    | MAM-GRDD-BASE40         | Average spring growing degree days with base   |
    |                         | 40F                                            |
    +-------------------------+------------------------------------------------+
    | MAM-GRDD-BASE45         | Average spring growing degree days with base   |
    |                         | 45F                                            |
    +-------------------------+------------------------------------------------+
    | MAM-GRDD-BASE50         | Average spring growing degree days with base   |
    |                         | 50F                                            |
    +-------------------------+------------------------------------------------+
    | MAM-GRDD-BASE55         | Average spring growing degree days with base   |
    |                         | 55F                                            |
    +-------------------------+------------------------------------------------+
    | MAM-GRDD-BASE57         | Average spring growing degree days with base   |
    |                         | 57F                                            |
    +-------------------------+------------------------------------------------+
    | MAM-GRDD-BASE60         | Average spring growing degree days with base   |
    |                         | 60F                                            |
    +-------------------------+------------------------------------------------+
    | MAM-GRDD-BASE65         | Average spring growing degree days with base   |
    |                         | 65F                                            |
    +-------------------------+------------------------------------------------+
    | MAM-GRDD-BASE70         | Average spring growing degree days with base   |
    |                         | 70F                                            |
    +-------------------------+------------------------------------------------+
    | MAM-GRDD-BASE72         | Average spring growing degree days with base   |
    |                         | 72F                                            |
    +-------------------------+------------------------------------------------+
    | MAM-GRDD-TB4886         | Average summer growing degree days with        |
    |                         | truncated bases 48F and 86F                    |
    +-------------------------+------------------------------------------------+
    | MAM-GRDD-TB5086         | Average summer growing degree days with        |
    |                         | truncated bases 50F and 86F                    |
    +-------------------------+------------------------------------------------+
    | MAM-HTDD-BASE40         | Average spring heating degree days with base   |
    |                         | 40F                                            |
    +-------------------------+------------------------------------------------+
    | MAM-HTDD-BASE45         | Average spring heating degree days with base   |
    |                         | 45F                                            |
    +-------------------------+------------------------------------------------+
    | MAM-HTDD-BASE50         | Average spring heating degree days with base   |
    |                         | 50F                                            |
    +-------------------------+------------------------------------------------+
    | MAM-HTDD-BASE55         | Average spring heating degree days with base   |
    |                         | 55F                                            |
    +-------------------------+------------------------------------------------+
    | MAM-HTDD-BASE57         | Average spring heating degree days with base   |
    |                         | 57F                                            |
    +-------------------------+------------------------------------------------+
    | MAM-HTDD-BASE60         | Average spring heating degree days with base   |
    |                         | 60F                                            |
    +-------------------------+------------------------------------------------+
    | MAM-HTDD-NORMAL         | Average spring heating degree days with base   |
    |                         | 65F                                            |
    +-------------------------+------------------------------------------------+
    | MAM-PRCP-AVGNDS-GE001HI | Average number of days during March-May with   |
    |                         | precipitation >= 0.01 in                       |
    +-------------------------+------------------------------------------------+
    | MAM-PRCP-AVGNDS-GE010HI | Average number of days during March-May with   |
    |                         | precipitation >= a 0.10 in                     |
    +-------------------------+------------------------------------------------+
    | MAM-PRCP-AVGNDS-GE050HI | Average number of days during March-May with   |
    |                         | precipitation >= 0.50 in                       |
    +-------------------------+------------------------------------------------+
    | MAM-PRCP-AVGNDS-GE100HI | Average number of days during March-May with   |
    |                         | precipitation >= 1.00 in                       |
    +-------------------------+------------------------------------------------+
    | MAM-PRCP-NORMAL         | Average seasonal precipitation totals for      |
    |                         | March- May                                     |
    +-------------------------+------------------------------------------------+
    | MAM-SNOW-AVGNDS-GE001TI | Average number of days during March-May with   |
    |                         | snowfall >= 0.1 in                             |
    +-------------------------+------------------------------------------------+
    | MAM-SNOW-AVGNDS-GE010TI | Average number of days during March-May with   |
    |                         | snowfall >= 1.0 in                             |
    +-------------------------+------------------------------------------------+
    | MAM-SNOW-AVGNDS-GE030TI | Average number of days during March-May with   |
    |                         | snowfall >= 3.0 in                             |
    +-------------------------+------------------------------------------------+
    | MAM-SNOW-AVGNDS-GE050TI | Average number of days during March-May with   |
    |                         | snowfall >= 5.0 in                             |
    +-------------------------+------------------------------------------------+
    | MAM-SNOW-AVGNDS-GE100TI | Average number of days during March-May with   |
    |                         | snowfall >= 10.0 in                            |
    +-------------------------+------------------------------------------------+
    | MAM-SNOW-NORMAL         | Average seasonal snowfall totals for March-    |
    |                         | May                                            |
    +-------------------------+------------------------------------------------+
    | MAM-SNWD-AVGNDS-GE001WI | Average number of days during March-May with   |
    |                         | snow depth >= 1 inch                           |
    +-------------------------+------------------------------------------------+
    | MAM-SNWD-AVGNDS-GE003WI | Average number of days during March-May with   |
    |                         | snow depth >= 3 in                             |
    +-------------------------+------------------------------------------------+
    | MAM-SNWD-AVGNDS-GE005WI | Average number of days during March-May with   |
    |                         | snow depth >= 5 in                             |
    +-------------------------+------------------------------------------------+
    | MAM-SNWD-AVGNDS-GE010WI | Average number of days during March-May with   |
    |                         | snow depth >= 10 in                            |
    +-------------------------+------------------------------------------------+
    | MAM-TAVG-NORMAL         | Average spring average temperature             |
    +-------------------------+------------------------------------------------+
    | MAM-TMAX-AVGNDS-GRTH040 | Average number of days per spring where tmax   |
    |                         | is greater than or equal to 40F                |
    +-------------------------+------------------------------------------------+
    | MAM-TMAX-AVGNDS-GRTH050 | Average number of days per spring where tmax   |
    |                         | is greater than or equal to 50F                |
    +-------------------------+------------------------------------------------+
    | MAM-TMAX-AVGNDS-GRTH060 | Average number of days per spring where tmax   |
    |                         | is greater than or equal to 60F                |
    +-------------------------+------------------------------------------------+
    | MAM-TMAX-AVGNDS-GRTH070 | Average number of days per spring where tmax   |
    |                         | is greater than or equal to 70F                |
    +-------------------------+------------------------------------------------+
    | MAM-TMAX-AVGNDS-GRTH080 | Average number of days per spring where tmax   |
    |                         | is greater than or equal to 80F                |
    +-------------------------+------------------------------------------------+
    | MAM-TMAX-AVGNDS-GRTH090 | Average number of days per spring where tmax   |
    |                         | is greater than or equal to 90F                |
    +-------------------------+------------------------------------------------+
    | MAM-TMAX-AVGNDS-GRTH100 | Average number of days per spring where tmax   |
    |                         | is greater than or equal to 100F               |
    +-------------------------+------------------------------------------------+
    | MAM-TMAX-AVGNDS-LSTH032 | Average number of days per spring where tmax   |
    |                         | is less than or equal to 32F                   |
    +-------------------------+------------------------------------------------+
    | MAM-TMAX-NORMAL         | Average spring maximum temperature             |
    +-------------------------+------------------------------------------------+
    | MAM-TMIN-AVGNDS-LSTH000 | Average number of days per spring where tmin   |
    |                         | is less than or equal to 0F                    |
    +-------------------------+------------------------------------------------+
    | MAM-TMIN-AVGNDS-LSTH010 | Average number of days per spring where tmin   |
    |                         | is less than or equal to 10F                   |
    +-------------------------+------------------------------------------------+
    | MAM-TMIN-AVGNDS-LSTH020 | Average number of days per spring where tmin   |
    |                         | is less than or equal to 20F                   |
    +-------------------------+------------------------------------------------+
    | MAM-TMIN-AVGNDS-LSTH032 | Average number of days per spring where tmin   |
    |                         | is less than or equal to 32F                   |
    +-------------------------+------------------------------------------------+
    | MAM-TMIN-AVGNDS-LSTH040 | Average number of days per spring where tmin   |
    |                         | is less than or equal to 40F                   |
    +-------------------------+------------------------------------------------+
    | MAM-TMIN-AVGNDS-LSTH050 | Average number of days per spring where tmin   |
    |                         | is less than or equal to 50F                   |
    +-------------------------+------------------------------------------------+
    | MAM-TMIN-AVGNDS-LSTH060 | Average number of days per spring where tmin   |
    |                         | is less than or equal to 60F                   |
    +-------------------------+------------------------------------------------+
    | MAM-TMIN-AVGNDS-LSTH070 | Average number of days per spring where tmin   |
    |                         | is less than or equal to 70F                   |
    +-------------------------+------------------------------------------------+
    | MAM-TMIN-NORMAL         | Average spring minimum temperature             |
    +-------------------------+------------------------------------------------+
    | SON-CLDD-BASE45         | Average autumn cooling degree days with base   |
    |                         | 45F                                            |
    +-------------------------+------------------------------------------------+
    | SON-CLDD-BASE50         | Average autumn cooling degree days with base   |
    |                         | 50F                                            |
    +-------------------------+------------------------------------------------+
    | SON-CLDD-BASE55         | Average autumn cooling degree days with base   |
    |                         | 55F                                            |
    +-------------------------+------------------------------------------------+
    | SON-CLDD-BASE57         | Average autumn cooling degree days with base   |
    |                         | 57F                                            |
    +-------------------------+------------------------------------------------+
    | SON-CLDD-BASE60         | Average autumn cooling degree days with base   |
    |                         | 60F                                            |
    +-------------------------+------------------------------------------------+
    | SON-CLDD-BASE70         | Average autumn cooling degree days with base   |
    |                         | 70F                                            |
    +-------------------------+------------------------------------------------+
    | SON-CLDD-BASE72         | Average autumn cooling degree days with base   |
    |                         | 72F                                            |
    +-------------------------+------------------------------------------------+
    | SON-CLDD-NORMAL         | Average autumn cooling degree days with base   |
    |                         | 65F                                            |
    +-------------------------+------------------------------------------------+
    | SON-DUTR-NORMAL         | Average autumn diurnal temperature range       |
    +-------------------------+------------------------------------------------+
    | SON-GRDD-BASE40         | Average fall growing degree days with base 40F |
    +-------------------------+------------------------------------------------+
    | SON-GRDD-BASE45         | Average fall growing degree days with base 45F |
    +-------------------------+------------------------------------------------+
    | SON-GRDD-BASE50         | Average fall growing degree days with base 50F |
    +-------------------------+------------------------------------------------+
    | SON-GRDD-BASE55         | Average fall growing degree days with base 55F |
    +-------------------------+------------------------------------------------+
    | SON-GRDD-BASE57         | Average fall growing degree days with base 57F |
    +-------------------------+------------------------------------------------+
    | SON-GRDD-BASE60         | Average fall growing degree days with base 60F |
    +-------------------------+------------------------------------------------+
    | SON-GRDD-BASE65         | Average fall growing degree days with base 65F |
    +-------------------------+------------------------------------------------+
    | SON-GRDD-BASE70         | Average fall growing degree days with base 70F |
    +-------------------------+------------------------------------------------+
    | SON-GRDD-BASE72         | Average fall growing degree days with base 72F |
    +-------------------------+------------------------------------------------+
    | SON-GRDD-TB4886         | Average summer growing degree days with        |
    |                         | truncated bases 48F and 86F                    |
    +-------------------------+------------------------------------------------+
    | SON-GRDD-TB5086         | Average summer growing degree days with        |
    |                         | truncated bases 50F and 86F                    |
    +-------------------------+------------------------------------------------+
    | SON-HTDD-BASE40         | Average autumn heating degree days with base   |
    |                         | 40F                                            |
    +-------------------------+------------------------------------------------+
    | SON-HTDD-BASE45         | Average autumn heating degree days with base   |
    |                         | 45F                                            |
    +-------------------------+------------------------------------------------+
    | SON-HTDD-BASE50         | Average autumn heating degree days with base   |
    |                         | 50F                                            |
    +-------------------------+------------------------------------------------+
    | SON-HTDD-BASE55         | Average autumn heating degree days with base   |
    |                         | 55F                                            |
    +-------------------------+------------------------------------------------+
    | SON-HTDD-BASE57         | Average autumn heating degree days with base   |
    |                         | 57F                                            |
    +-------------------------+------------------------------------------------+
    | SON-HTDD-BASE60         | Average autumn heating degree days with base   |
    |                         | 60F                                            |
    +-------------------------+------------------------------------------------+
    | SON-HTDD-NORMAL         | Average autumn heating degree days with base   |
    |                         | 65F                                            |
    +-------------------------+------------------------------------------------+
    | SON-PRCP-AVGNDS-GE001HI | Average number of days during September-       |
    |                         | November with precipitation >= 0.01 in         |
    +-------------------------+------------------------------------------------+
    | SON-PRCP-AVGNDS-GE010HI | Average number of days during September-       |
    |                         | November with precipitation >= 0.10 in         |
    +-------------------------+------------------------------------------------+
    | SON-PRCP-AVGNDS-GE050HI | Average number of days during September-       |
    |                         | November with precipitation >= 0.50 in         |
    +-------------------------+------------------------------------------------+
    | SON-PRCP-AVGNDS-GE100HI | Average number of days during September-       |
    |                         | November with precipitation >= 1.00 in         |
    +-------------------------+------------------------------------------------+
    | SON-PRCP-NORMAL         | Average seasonal precipitation totals for      |
    |                         | September- November                            |
    +-------------------------+------------------------------------------------+
    | SON-SNOW-AVGNDS-GE001TI | Average number of days during September-       |
    |                         | November with snowfall >= 0.1 in               |
    +-------------------------+------------------------------------------------+
    | SON-SNOW-AVGNDS-GE010TI | Average number of days during September-       |
    |                         | November with snowfall >= 1.0 in               |
    +-------------------------+------------------------------------------------+
    | SON-SNOW-AVGNDS-GE030TI | Average number of days during September-       |
    |                         | November with snowfall >= 3.0 in               |
    +-------------------------+------------------------------------------------+
    | SON-SNOW-AVGNDS-GE050TI | Average number of days during September-       |
    |                         | November with snowfall >= 5.0 in               |
    +-------------------------+------------------------------------------------+
    | SON-SNOW-AVGNDS-GE100TI | Average number of days during September-       |
    |                         | November with snowfall >= 10.0 in              |
    +-------------------------+------------------------------------------------+
    | SON-SNOW-NORMAL         | Average seasonal snowfall totals for           |
    |                         | September- November                            |
    +-------------------------+------------------------------------------------+
    | SON-SNWD-AVGNDS-GE001WI | Average number of days during September-       |
    |                         | November with snow depth >= 1 inch             |
    +-------------------------+------------------------------------------------+
    | SON-SNWD-AVGNDS-GE003WI | Average number of days during September-       |
    |                         | November with snow depth >= 3 in               |
    +-------------------------+------------------------------------------------+
    | SON-SNWD-AVGNDS-GE005WI | Average number of days during September-       |
    |                         | November with snow depth >= 5 in               |
    +-------------------------+------------------------------------------------+
    | SON-SNWD-AVGNDS-GE010WI | Average number of days during September-       |
    |                         | November with snow depth >= 10 in              |
    +-------------------------+------------------------------------------------+
    | SON-TAVG-NORMAL         | Average autumn average temperature             |
    +-------------------------+------------------------------------------------+
    | SON-TMAX-AVGNDS-GRTH040 | Average number of days per autumn where tmax   |
    |                         | is greater than or equal to 40F                |
    +-------------------------+------------------------------------------------+
    | SON-TMAX-AVGNDS-GRTH050 | Average number of days per autumn where tmax   |
    |                         | is greater than or equal to 50F                |
    +-------------------------+------------------------------------------------+
    | SON-TMAX-AVGNDS-GRTH060 | Average number of days per autumn where tmax   |
    |                         | is greater than or equal to 60F                |
    +-------------------------+------------------------------------------------+
    | SON-TMAX-AVGNDS-GRTH070 | Average number of days per autumn where tmax   |
    |                         | is greater than or equal to 70F                |
    +-------------------------+------------------------------------------------+
    | SON-TMAX-AVGNDS-GRTH080 | Average number of days per autumn where tmax   |
    |                         | is greater than or equal to 80F                |
    +-------------------------+------------------------------------------------+
    | SON-TMAX-AVGNDS-GRTH090 | Average number of days per autumn where tmax   |
    |                         | is greater than or equal to 90F                |
    +-------------------------+------------------------------------------------+
    | SON-TMAX-AVGNDS-GRTH100 | Average number of days per autumn where tmax   |
    |                         | is greater than or equal to 100F               |
    +-------------------------+------------------------------------------------+
    | SON-TMAX-AVGNDS-LSTH032 | Average number of days per autumn where tmax   |
    |                         | is less than or equal to 32F                   |
    +-------------------------+------------------------------------------------+
    | SON-TMAX-NORMAL         | Average autumn maximum temperature             |
    +-------------------------+------------------------------------------------+
    | SON-TMIN-AVGNDS-LSTHxxx | Average number of days per autumn where tmin   |
    |                         | is less than or equal to 'xxx' degree F. Where |
    |                         | 'xxx' is one of 000, 010, 020, 032, 040, 050,  |
    |                         | 060, 070                                       |
    +-------------------------+------------------------------------------------+
    | SON-TMIN-NORMAL         | Average autumn minimum temperature             |
    +-------------------------+------------------------------------------------+

    Parameters
    ----------
    ${stationid}
    ${start_date}
    ${end_date}
    """
    tsutils.printiso(ncei_normal_ann(stationid))


@tsutils.copy_doc(ncei_normal_ann_cli)
def ncei_normal_ann(stationid):
    r"""National Centers for Environmental Information (NCEI) annual normals."""
    return ncei_cdo_json_to_df(
        "NORMAL_ANN",
        stationid,
        start_date="2010-01-01",
        end_date="2010-01-01",
    )


# 2010-01-01, 2010-12-31, Normals Daily               , 1    , NORMAL_DLY
@cltoolbox.command("ncei_normal_dly", formatter_class=HelpFormatter)
def ncei_normal_dly_cli(stationid):
    r"""global station D:NCEI Daily Normals

    Requires registration and free API key.

    For every datatype and record there is a set of meta-data flags.
    For the GHCNDMS dataset, the flags are::

        'Total Missing','Consecutive Missing'

    Total Missing:

    Defined as total number of days observation/element is missing in that
    month.  This can be taken as a measure of quality or completeness as the
    higher the number of days sampled in the month, the more representative the
    value is for the entire month.

    Consecutive Missing:

    Defined as the maximum number of consecutive days in the month that an
    observation/element is missing.

    The following table lists the datatypes available for the annual dataset.
    Not all datatypes are available for all stations.

    +-------------------------+------------------------------------------------+
    | Code                    | Description                                    |
    +=========================+================================================+
    | DLY-CLDD-BASE45         | Average daily cooling degree days with base    |
    |                         | 45F                                            |
    +-------------------------+------------------------------------------------+
    | DLY-CLDD-BASE50         | Average daily cooling degree days with base    |
    |                         | 50F                                            |
    +-------------------------+------------------------------------------------+
    | DLY-CLDD-BASE55         | Average daily cooling degree days with base    |
    |                         | 55F                                            |
    +-------------------------+------------------------------------------------+
    | DLY-CLDD-BASE57         | Average daily cooling degree days with base    |
    |                         | 57F                                            |
    +-------------------------+------------------------------------------------+
    | DLY-CLDD-BASE60         | Average daily cooling degree days with base    |
    |                         | 60F                                            |
    +-------------------------+------------------------------------------------+
    | DLY-CLDD-BASE70         | Average daily cooling degree days with base    |
    |                         | 70F                                            |
    +-------------------------+------------------------------------------------+
    | DLY-CLDD-BASE72         | Average daily cooling degree days with base    |
    |                         | 72F                                            |
    +-------------------------+------------------------------------------------+
    | DLY-CLDD-NORMAL         | Average daily cooling degree days with base    |
    |                         | 65F                                            |
    +-------------------------+------------------------------------------------+
    | DLY-DUTR-NORMAL         | Average daily diurnal temperature range        |
    +-------------------------+------------------------------------------------+
    | DLY-DUTR-STDDEV         | Long-term standard deviations of daily diurnal |
    |                         | temperature range                              |
    +-------------------------+------------------------------------------------+
    | DLY-GRDD-BASE40         | Average daily growing degree days with base    |
    |                         | 40F                                            |
    +-------------------------+------------------------------------------------+
    | DLY-GRDD-BASE45         | Average daily growing degree days with base    |
    |                         | 45F                                            |
    +-------------------------+------------------------------------------------+
    | DLY-GRDD-BASE50         | Average daily growing degree days with base    |
    |                         | 50F                                            |
    +-------------------------+------------------------------------------------+
    | DLY-GRDD-BASE55         | Average daily growing degree days with base    |
    |                         | 55F                                            |
    +-------------------------+------------------------------------------------+
    | DLY-GRDD-BASE57         | Average daily growing degree days with base    |
    |                         | 57F                                            |
    +-------------------------+------------------------------------------------+
    | DLY-GRDD-BASE60         | Average daily growing degree days with base    |
    |                         | 60F                                            |
    +-------------------------+------------------------------------------------+
    | DLY-GRDD-BASE65         | Average daily growing degree days with base    |
    |                         | 65F                                            |
    +-------------------------+------------------------------------------------+
    | DLY-GRDD-BASE70         | Average daily growing degree days with base    |
    |                         | 70F                                            |
    +-------------------------+------------------------------------------------+
    | DLY-GRDD-BASE72         | Average daily growing degree days with base    |
    |                         | 72F                                            |
    +-------------------------+------------------------------------------------+
    | DLY-GRDD-TB4886         | Average daily growing degree days with         |
    |                         | truncated bases 48F and 86F                    |
    +-------------------------+------------------------------------------------+
    | DLY-GRDD-TB5086         | Average daily growing degree days with         |
    |                         | truncated bases 50F and 86F                    |
    +-------------------------+------------------------------------------------+
    | DLY-HTDD-BASE40         | Average daily heating degree days with base    |
    |                         | 40F                                            |
    +-------------------------+------------------------------------------------+
    | DLY-HTDD-BASE45         | Average daily heating degree days with base    |
    |                         | 45F                                            |
    +-------------------------+------------------------------------------------+
    | DLY-HTDD-BASE50         | Average daily heating degree days with base    |
    |                         | 50F                                            |
    +-------------------------+------------------------------------------------+
    | DLY-HTDD-BASE55         | Average daily heating degree days with base    |
    |                         | 55F                                            |
    +-------------------------+------------------------------------------------+
    | DLY-HTDD-BASE57         | Average daily heating degree days with base    |
    |                         | 57F                                            |
    +-------------------------+------------------------------------------------+
    | DLY-HTDD-BASE60         | Average daily heating degree days with base    |
    |                         | 60F                                            |
    +-------------------------+------------------------------------------------+
    | DLY-HTDD-NORMAL         | Average daily heating degree days with base    |
    |                         | 65F                                            |
    +-------------------------+------------------------------------------------+
    | DLY-PRCP-25PCTL         | 25th percentiles of daily nonzero              |
    |                         | precipitation totals for 29-day windows        |
    |                         | centered on each day of the year               |
    +-------------------------+------------------------------------------------+
    | DLY-PRCP-50PCTL         | 50th percentiles of daily nonzero              |
    |                         | precipitation totals for 29-day windows        |
    |                         | centered on each day of the year               |
    +-------------------------+------------------------------------------------+
    | DLY-PRCP-75PCTL         | 75th percentiles of daily nonzero              |
    |                         | precipitation totals for 29-day windows        |
    |                         | centered on each day of the year               |
    +-------------------------+------------------------------------------------+
    | DLY-PRCP-PCTALL-GE001HI | Probability of precipitation >= 0.01 in for    |
    |                         | 29-day windows centered on each day of the     |
    |                         | year                                           |
    +-------------------------+------------------------------------------------+
    | DLY-PRCP-PCTALL-GE010HI | Probability of precipitation >= 0.10 in for    |
    |                         | 29-day windows centered on each day of the     |
    |                         | year                                           |
    +-------------------------+------------------------------------------------+
    | DLY-PRCP-PCTALL-GE050HI | Probability of precipitation >= 0.50 in for    |
    |                         | 29-day windows centered on each day of the     |
    |                         | year                                           |
    +-------------------------+------------------------------------------------+
    | DLY-PRCP-PCTALL-GE100HI | Probability of precipitation >= 1.00 in for    |
    |                         | 29-day windows centered on each day of the     |
    |                         | year                                           |
    +-------------------------+------------------------------------------------+
    | DLY-SNOW-25PCTL         | 25th percentiles of daily nonzero snowfall     |
    |                         | totals for 29-day windows centered on each day |
    |                         | of the year                                    |
    +-------------------------+------------------------------------------------+
    | DLY-SNOW-50PCTL         | 50th percentiles of daily nonzero snowfall     |
    |                         | totals for 29-day windows centered on each day |
    |                         | of the year                                    |
    +-------------------------+------------------------------------------------+
    | DLY-SNOW-75PCTL         | 75th percentiles of daily nonzero snowfall     |
    |                         | totals for 29-day windows centered on each day |
    |                         | of the year                                    |
    +-------------------------+------------------------------------------------+
    | DLY-SNOW-PCTALL-GE001TI | Probability of snowfall >= 0.1 in for 29-day   |
    |                         | windows centered on each day of the year       |
    +-------------------------+------------------------------------------------+
    | DLY-SNOW-PCTALL-GE010TI | Probability of snowfall >= 1.0 in for 29-day   |
    |                         | windows centered on each day of the year       |
    +-------------------------+------------------------------------------------+
    | DLY-SNOW-PCTALL-GE030TI | Probability of snowfall >= 3.0 in for 29-day   |
    |                         | windows centered on each day of the year       |
    +-------------------------+------------------------------------------------+
    | DLY-SNOW-PCTALL-GE050TI | Probability of snowfall >= 5.0 in for 29-day   |
    |                         | windows centered on each day of the year       |
    +-------------------------+------------------------------------------------+
    | DLY-SNOW-PCTALL-GE100TI | Probability of snowfall >= 10 in for 29-day    |
    |                         | windows centered on each day of the year       |
    +-------------------------+------------------------------------------------+
    | DLY-SNWD-25PCTL         | 25th percentiles of daily nonzero snow depth   |
    |                         | for 29-day windows centered on each day of the |
    |                         | year                                           |
    +-------------------------+------------------------------------------------+
    | DLY-SNWD-50PCTL         | 50th percentiles of daily nonzero snow depth   |
    |                         | for 29-day windows centered on each day of the |
    |                         | year                                           |
    +-------------------------+------------------------------------------------+
    | DLY-SNWD-75PCTL         | 75th percentiles of daily nonzero snow depth   |
    |                         | for 29-day windows centered on each day of the |
    |                         | year                                           |
    +-------------------------+------------------------------------------------+
    | DLY-SNWD-PCTALL-GE001WI | Probability of snow depth >= 1 inch for 29-day |
    |                         | windows centered on each day of the year       |
    +-------------------------+------------------------------------------------+
    | DLY-SNWD-PCTALL-GE003WI | Probability of snow depth >= 3 in for 29-day   |
    |                         | windows centered on each day of the year       |
    +-------------------------+------------------------------------------------+
    | DLY-SNWD-PCTALL-GE005WI | Probability of snow depth >= 5 in for 29-day   |
    |                         | windows centered on each day of the year       |
    +-------------------------+------------------------------------------------+
    | DLY-SNWD-PCTALL-GE010WI | Probability of snow depth >= 10 in for 29-day  |
    |                         | windows centered on each day of the year       |
    +-------------------------+------------------------------------------------+
    | DLY-TAVG-NORMAL         | Average daily average temperature              |
    +-------------------------+------------------------------------------------+
    | DLY-TAVG-STDDEV         | Long-term standard deviations of daily average |
    |                         | temperature                                    |
    +-------------------------+------------------------------------------------+
    | DLY-TMAX-NORMAL         | Average daily maximum temperature              |
    +-------------------------+------------------------------------------------+
    | DLY-TMAX-STDDEV         | Long-term standard deviations of daily maximum |
    |                         | temperature                                    |
    +-------------------------+------------------------------------------------+
    | DLY-TMIN-NORMAL         | Average daily minimum temperature              |
    +-------------------------+------------------------------------------------+
    | DLY-TMIN-STDDEV         | Long-term standard deviations of daily minimum |
    |                         | temperature                                    |
    +-------------------------+------------------------------------------------+
    | MTD-PRCP-NORMAL         | Average month-to-date precipitation totals     |
    +-------------------------+------------------------------------------------+
    | MTD-SNOW-NORMAL         | Average month-to-date snowfall totals          |
    +-------------------------+------------------------------------------------+
    | YTD-PRCP-NORMAL         | Average year-to-date precipitation totals      |
    +-------------------------+------------------------------------------------+
    | YTD-SNOW-NORMAL         | Average year-to-date snowfall totals           |
    +-------------------------+------------------------------------------------+

    Parameters
    ----------
    ${stationid}
    ${start_date}
    ${end_date}
    """
    tsutils.printiso(ncei_normal_dly(stationid))


@tsutils.copy_doc(ncei_normal_dly_cli)
def ncei_normal_dly(stationid):
    r"""National Centers for Environmental Information (NCEI) Daily Normals."""
    return ncei_cdo_json_to_df(
        "NORMAL_DLY",
        stationid,
    )


# 2010-01-01, 2010-12-31, Normals Hourly              , 1    , NORMAL_HLY
@cltoolbox.command("ncei_normal_hly", formatter_class=HelpFormatter)
def ncei_normal_hly_cli(stationid):
    r"""global station H:NCEI Normal hourly

    Requires registration and free API key.

    For every datatype and record there is a set of meta-data flags.
    For the GHCNDMS dataset, the flags are::

        'Total Missing','Consecutive Missing'

    Total Missing:

    Defined as total number of days observation/element is missing in that
    month.  This can be taken as a measure of quality or completeness as the
    higher the number of days sampled in the month, the more representative the
    value is for the entire month.

    Consecutive Missing:

    Defined as the maximum number of consecutive days in the month that an
    observation/element is missing.

    The following table lists the datatypes available for the annual dataset.
    Not all datatypes are available for all stations.

    +-----------------+-------------------------------------------------+
    | Code            | Description                                     |
    +=================+=================================================+
    | HLY-CLDH-NORMAL | Cooling degree hours                            |
    +-----------------+-------------------------------------------------+
    | HLY-CLOD-PCTBKN | Clouds broken percentage                        |
    +-----------------+-------------------------------------------------+
    | HLY-CLOD-PCTCLR | Clouds clear percentage                         |
    +-----------------+-------------------------------------------------+
    | HLY-CLOD-PCTFEW | Clouds few percentage                           |
    +-----------------+-------------------------------------------------+
    | HLY-CLOD-PCTOVC | Clouds overcast percentage                      |
    +-----------------+-------------------------------------------------+
    | HLY-CLOD-PCTSCT | Clouds scattered percentage                     |
    +-----------------+-------------------------------------------------+
    | HLY-DEWP-10PCTL | Dew point 10th percentile                       |
    +-----------------+-------------------------------------------------+
    | HLY-DEWP-90PCTL | Dew point 90th percentile                       |
    +-----------------+-------------------------------------------------+
    | HLY-DEWP-NORMAL | Dew point mean                                  |
    +-----------------+-------------------------------------------------+
    | HLY-HIDX-NORMAL | Heat index mean                                 |
    +-----------------+-------------------------------------------------+
    | HLY-HTDH-NORMAL | Heating degree hours                            |
    +-----------------+-------------------------------------------------+
    | HLY-PRES-10PCTL | Sea level pressure 10th percentile              |
    +-----------------+-------------------------------------------------+
    | HLY-PRES-90PCTL | Sea level pressure 90th percentile              |
    +-----------------+-------------------------------------------------+
    | HLY-PRES-NORMAL | Sea level pressure mean                         |
    +-----------------+-------------------------------------------------+
    | HLY-TEMP-10PCTL | Temperature 10th percentile                     |
    +-----------------+-------------------------------------------------+
    | HLY-TEMP-90PCTL | Temperature 90th percentile                     |
    +-----------------+-------------------------------------------------+
    | HLY-TEMP-NORMAL | Temperature mean                                |
    +-----------------+-------------------------------------------------+
    | HLY-WCHL-NORMAL | Wind chill mean                                 |
    +-----------------+-------------------------------------------------+
    | HLY-WIND-1STDIR | Prevailing wind direction (1-8)                 |
    +-----------------+-------------------------------------------------+
    | HLY-WIND-1STPCT | Prevailing wind percentage                      |
    +-----------------+-------------------------------------------------+
    | HLY-WIND-2NDDIR | Secondary wind direction (1-8)                  |
    +-----------------+-------------------------------------------------+
    | HLY-WIND-2NDPCT | Secondary wind percentage                       |
    +-----------------+-------------------------------------------------+
    | HLY-WIND-AVGSPD | Average wind speed                              |
    +-----------------+-------------------------------------------------+
    | HLY-WIND-PCTCLM | Percentage calm                                 |
    +-----------------+-------------------------------------------------+
    | HLY-WIND-VCTDIR | Mean wind vector direction                      |
    +-----------------+-------------------------------------------------+
    | HLY-WIND-VCTSPD | Mean wind vector magnitude                      |
    +-----------------+-------------------------------------------------+

    Parameters
    ----------
    ${stationid}
    ${start_date}
    ${end_date}
    """
    tsutils.printiso(ncei_normal_hly(stationid))


@tsutils.copy_doc(ncei_normal_hly_cli)
def ncei_normal_hly(stationid):
    r"""National Centers for Environmental Information (NCEI) Normal hourly."""
    return ncei_cdo_json_to_df(
        "NORMAL_HLY",
        stationid,
    )


# 2010-01-01, 2010-12-01, Normals Monthly             , 1    , NORMAL_MLY
@cltoolbox.command("ncei_normal_mly", formatter_class=HelpFormatter)
def ncei_normal_mly_cli(stationid):
    r"""global station M:NCEI Monthly Summaries.

    Requires registration and free API key.

    For every datatype and record there is a set of meta-data flags.
    For the GHCNDMS dataset, the flags are::

        'Total Missing','Consecutive Missing'

    Total Missing:

    Defined as total number of days observation/element is missing in that
    month.  This can be taken as a measure of quality or completeness as the
    higher the number of days sampled in the month, the more representative the
    value is for the entire month.

    Consecutive Missing:

    Defined as the maximum number of consecutive days in the month that an
    observation/element is missing.

    The following table lists the datatypes available for the annual dataset.
    Not all of the datatypes are available for all stations.

    +-------------------------+------------------------------------------------+
    | Code                    | Description                                    |
    +=========================+================================================+
    | MLY-CLDD-BASE45         | Average monthly cooling degree days with base  |
    |                         | 45F                                            |
    +-------------------------+------------------------------------------------+
    | MLY-CLDD-BASE50         | Average monthly cooling degree days with base  |
    |                         | 50F                                            |
    +-------------------------+------------------------------------------------+
    | MLY-CLDD-BASE55         | Average monthly cooling degree days with base  |
    |                         | 55F                                            |
    +-------------------------+------------------------------------------------+
    | MLY-CLDD-BASE57         | Average monthly cooling degree days with base  |
    |                         | 57F                                            |
    +-------------------------+------------------------------------------------+
    | MLY-CLDD-BASE60         | Average monthly cooling degree days with base  |
    |                         | 60F                                            |
    +-------------------------+------------------------------------------------+
    | MLY-CLDD-BASE70         | Average monthly cooling degree days with base  |
    |                         | 70F                                            |
    +-------------------------+------------------------------------------------+
    | MLY-CLDD-BASE72         | Average monthly cooling degree days with base  |
    |                         | 72F                                            |
    +-------------------------+------------------------------------------------+
    | MLY-CLDD-NORMAL         | Average monthly cooling degree days with base  |
    |                         | 65F                                            |
    +-------------------------+------------------------------------------------+
    | MLY-DUTR-NORMAL         | Average monthly diurnal temperature range      |
    +-------------------------+------------------------------------------------+
    | MLY-DUTR-STDDEV         | Long-term standard deviations of monthly       |
    |                         | diurnal temperature range                      |
    +-------------------------+------------------------------------------------+
    | MLY-GRDD-BASE40         | Average monthly growing degree days with base  |
    |                         | 40F                                            |
    +-------------------------+------------------------------------------------+
    | MLY-GRDD-BASE45         | Average monthly growing degree days with base  |
    |                         | 45F                                            |
    +-------------------------+------------------------------------------------+
    | MLY-GRDD-BASE50         | Average monthly growing degree days with base  |
    |                         | 50F                                            |
    +-------------------------+------------------------------------------------+
    | MLY-GRDD-BASE55         | Average monthly growing degree days with base  |
    |                         | 55F                                            |
    +-------------------------+------------------------------------------------+
    | MLY-GRDD-BASE57         | Average monthly growing degree days with base  |
    |                         | 57F                                            |
    +-------------------------+------------------------------------------------+
    | MLY-GRDD-BASE60         | Average monthly growing degree days with base  |
    |                         | 60F                                            |
    +-------------------------+------------------------------------------------+
    | MLY-GRDD-BASE65         | Average monthly growing degree days with base  |
    |                         | 65F                                            |
    +-------------------------+------------------------------------------------+
    | MLY-GRDD-BASE70         | Average monthly growing degree days with base  |
    |                         | 70F                                            |
    +-------------------------+------------------------------------------------+
    | MLY-GRDD-BASE72         | Average monthly growing degree days with base  |
    |                         | 72F                                            |
    +-------------------------+------------------------------------------------+
    | MLY-GRDD-TB4886         | Average monthly growing degree days with       |
    |                         | truncated bases 48F and 86F                    |
    +-------------------------+------------------------------------------------+
    | MLY-GRDD-TB5086         | Average monthly growing degree days with       |
    |                         | truncated bases 50F and 86F                    |
    +-------------------------+------------------------------------------------+
    | MLY-HTDD-BASE40         | Average monthly heating degree days with base  |
    |                         | 40F                                            |
    +-------------------------+------------------------------------------------+
    | MLY-HTDD-BASE45         | Average monthly heating degree days with base  |
    |                         | 45F                                            |
    +-------------------------+------------------------------------------------+
    | MLY-HTDD-BASE50         | Average monthly heating degree days with base  |
    |                         | 50F                                            |
    +-------------------------+------------------------------------------------+
    | MLY-HTDD-BASE55         | Average monthly heating degree days with base  |
    |                         | 55F                                            |
    +-------------------------+------------------------------------------------+
    | MLY-HTDD-BASE57         | Average monthly heating degree days with base  |
    |                         | 57F                                            |
    +-------------------------+------------------------------------------------+
    | MLY-HTDD-BASE60         | Average monthly heating degree days with base  |
    |                         | 60F                                            |
    +-------------------------+------------------------------------------------+
    | MLY-HTDD-NORMAL         | Average monthly heating degree days with base  |
    |                         | 65F                                            |
    +-------------------------+------------------------------------------------+
    | MLY-PRCP-25PCTL         | 25th percentiles of monthly precipitation      |
    |                         | totals                                         |
    +-------------------------+------------------------------------------------+
    | MLY-PRCP-50PCTL         | 50th percentiles of monthly precipitation      |
    |                         | totals                                         |
    +-------------------------+------------------------------------------------+
    | MLY-PRCP-75PCTL         | 75th percentiles of monthly precipitation      |
    |                         | totals                                         |
    +-------------------------+------------------------------------------------+
    | MLY-PRCP-AVGNDS-GE001HI | Average number of days per month with          |
    |                         | precipitation >= 0.01 in                       |
    +-------------------------+------------------------------------------------+
    | MLY-PRCP-AVGNDS-GE010HI | Average number of days per month with          |
    |                         | precipitation >= 0.10 in                       |
    +-------------------------+------------------------------------------------+
    | MLY-PRCP-AVGNDS-GE050HI | Average number of days per month with          |
    |                         | precipitation >= 0.50 in                       |
    +-------------------------+------------------------------------------------+
    | MLY-PRCP-AVGNDS-GE100HI | Average number of days per month with          |
    |                         | precipitation >= 1.00 in                       |
    +-------------------------+------------------------------------------------+
    | MLY-PRCP-NORMAL         | Average monthly precipitation totals           |
    +-------------------------+------------------------------------------------+
    | MLY-SNOW-25PCTL         | 25th percentiles of monthly snowfall totals    |
    +-------------------------+------------------------------------------------+
    | MLY-SNOW-50PCTL         | 50th percentiles of monthly snowfall totals    |
    +-------------------------+------------------------------------------------+
    | MLY-SNOW-75PCTL         | 75th percentiles of monthly snowfall totals    |
    +-------------------------+------------------------------------------------+
    | MLY-SNOW-AVGNDS-GE001TI | Average number of days per month with Snowfall |
    |                         | >= 0.1 in                                      |
    +-------------------------+------------------------------------------------+
    | MLY-SNOW-AVGNDS-GE010TI | Average number of days per month with Snowfall |
    |                         | >= 1.0 in                                      |
    +-------------------------+------------------------------------------------+
    | MLY-SNOW-AVGNDS-GE030TI | Average number of days per month with Snowfall |
    |                         | >= 3.0 in                                      |
    +-------------------------+------------------------------------------------+
    | MLY-SNOW-AVGNDS-GE050TI | Average number of days per month with Snowfall |
    |                         | >= 5.0 in                                      |
    +-------------------------+------------------------------------------------+
    | MLY-SNOW-AVGNDS-GE100TI | Average number of days per month with Snowfall |
    |                         | >= 10.0 in                                     |
    +-------------------------+------------------------------------------------+
    | MLY-SNOW-NORMAL         | Average monthly snowfall totals                |
    +-------------------------+------------------------------------------------+
    | MLY-SNWD-AVGNDS-GE001WI | Average number of days per month with snow     |
    |                         | depth >= 1 inch                                |
    +-------------------------+------------------------------------------------+
    | MLY-SNWD-AVGNDS-GE003WI | Average number of days per month with snow     |
    |                         | depth >= 3 in                                  |
    +-------------------------+------------------------------------------------+
    | MLY-SNWD-AVGNDS-GE005WI | Average number of days per month with snow     |
    |                         | depth >= 5 in                                  |
    +-------------------------+------------------------------------------------+
    | MLY-SNWD-AVGNDS-GE010WI | Average number of days per month with snow     |
    |                         | depth >= 10 in                                 |
    +-------------------------+------------------------------------------------+
    | MLY-TAVG-NORMAL         | Average monthly average temperature            |
    +-------------------------+------------------------------------------------+
    | MLY-TAVG-STDDEV         | Long-term standard deviations of monthly       |
    |                         | average temperature                            |
    +-------------------------+------------------------------------------------+
    | MLY-TMAX-AVGNDS-GRTH040 | Average number of days per month where tmax is |
    |                         | greater than or equal to 40F                   |
    +-------------------------+------------------------------------------------+
    | MLY-TMAX-AVGNDS-GRTH050 | Average number of days per month where tmax is |
    |                         | greater than or equal to 50F                   |
    +-------------------------+------------------------------------------------+
    | MLY-TMAX-AVGNDS-GRTH060 | Average number of days per month where tmax is |
    |                         | greater than or equal to 60F                   |
    +-------------------------+------------------------------------------------+
    | MLY-TMAX-AVGNDS-GRTH070 | Average number of days per month where tmax is |
    |                         | greater than or equal to 70F                   |
    +-------------------------+------------------------------------------------+
    | MLY-TMAX-AVGNDS-GRTH080 | Average number of days per month where tmax is |
    |                         | greater than or equal to 80F                   |
    +-------------------------+------------------------------------------------+
    | MLY-TMAX-AVGNDS-GRTH090 | Average number of days per month where tmax is |
    |                         | greater than or equal to 90F                   |
    +-------------------------+------------------------------------------------+
    | MLY-TMAX-AVGNDS-GRTH100 | Average number of days per month where tmax is |
    |                         | greater than or equal to 100F                  |
    +-------------------------+------------------------------------------------+
    | MLY-TMAX-AVGNDS-LSTH032 | Average number of days per month where tmax is |
    |                         | less than or equal to 32F                      |
    +-------------------------+------------------------------------------------+
    | MLY-TMAX-NORMAL         | Average monthly maximum temperature            |
    +-------------------------+------------------------------------------------+
    | MLY-TMAX-STDDEV         | Long-term standard deviations of monthly       |
    |                         | maximum temperature                            |
    +-------------------------+------------------------------------------------+
    | MLY-TMIN-AVGNDS-LSTH000 | Average number of days per month where tmin is |
    |                         | less than or equal to 0F                       |
    +-------------------------+------------------------------------------------+
    | MLY-TMIN-AVGNDS-LSTH010 | Average number of days per month where tmin is |
    |                         | less than or equal to 10F                      |
    +-------------------------+------------------------------------------------+
    | MLY-TMIN-AVGNDS-LSTH020 | Average number of days per month where tmin is |
    |                         | less than or equal to 20F                      |
    +-------------------------+------------------------------------------------+
    | MLY-TMIN-AVGNDS-LSTH032 | Average number of days per month where tmin is |
    |                         | less than or equal to 32F                      |
    +-------------------------+------------------------------------------------+
    | MLY-TMIN-AVGNDS-LSTH040 | Average number of days per month where tmin is |
    |                         | less than or equal to 40F                      |
    +-------------------------+------------------------------------------------+
    | MLY-TMIN-AVGNDS-LSTH050 | Average number of days per month where tmin is |
    |                         | less than or equal to 50F                      |
    +-------------------------+------------------------------------------------+
    | MLY-TMIN-AVGNDS-LSTH060 | Average number of days per month where tmin is |
    |                         | less than or equal to 60F                      |
    +-------------------------+------------------------------------------------+
    | MLY-TMIN-AVGNDS-LSTH070 | Average number of days per month where tmin is |
    |                         | less than or equal to 70F                      |
    +-------------------------+------------------------------------------------+
    | MLY-TMIN-NORMAL         | Average monthly minimum temperature            |
    +-------------------------+------------------------------------------------+
    | MLY-TMIN-PRBOCC-LSTH016 | probability of 16F or below at least once in   |
    |                         | the month                                      |
    +-------------------------+------------------------------------------------+
    | MLY-TMIN-PRBOCC-LSTH020 | probability of 20F or below at least once in   |
    |                         | the month                                      |
    +-------------------------+------------------------------------------------+
    | MLY-TMIN-PRBOCC-LSTH024 | probability of 24F or below at least once in   |
    |                         | the month                                      |
    +-------------------------+------------------------------------------------+
    | MLY-TMIN-PRBOCC-LSTH028 | probability of 28F or below at least once in   |
    |                         | the month                                      |
    +-------------------------+------------------------------------------------+
    | MLY-TMIN-PRBOCC-LSTH032 | probability of 32F or below at least once in   |
    |                         | the month                                      |
    +-------------------------+------------------------------------------------+
    | MLY-TMIN-PRBOCC-LSTH036 | probability of 36F or below at least once in   |
    |                         | the month                                      |
    +-------------------------+------------------------------------------------+
    | MLY-TMIN-STDDEV         | Long-term standard deviations of monthly       |
    |                         | minimum temperature                            |
    +-------------------------+------------------------------------------------+

    Parameters
    ----------
    ${stationid}
    ${start_date}
    ${end_date}
    """
    tsutils.printiso(ncei_normal_mly(stationid))


@tsutils.copy_doc(ncei_normal_mly_cli)
def ncei_normal_mly(stationid):
    r"""National Centers for Environmental Information (NCEI) GHCND Normal monthly."""
    return ncei_cdo_json_to_df(
        "NORMAL_MLY",
        stationid,
    )


# 1970-05-12, 2014-01-01, Precipitation 15 Minute     , 0.25 , PRECIP_15
@cltoolbox.command("ncei_precip_15", formatter_class=HelpFormatter)
def ncei_precip_15_cli(stationid, start_date=None, end_date=None):
    r"""global station 15T:NCEI 15 minute precipitation

    Requires registration and free API key.

    For every datatype and record there is a set of meta-data flags.
    For the GHCNDMS dataset, the flags are::

        'Total Missing','Consecutive Missing'

    Total Missing:

    Defined as total number of days observation/element is missing in that
    month.  This can be taken as a measure of quality or completeness as the
    higher the number of days sampled in the month, the more representative the
    value is for the entire month.

    Consecutive Missing:

    Defined as the maximum number of consecutive days in the month that an
    observation/element is missing.

    The following table lists the datatypes available for the annual dataset.
    Not all datatypes are available for all stations.

    +------+---------------+
    | Code | Description   |
    +======+===============+
    | QGAG | Precipitation |
    +------+---------------+
    | QPCP | Precipitation |
    +------+---------------+

    Parameters
    ----------
    ${stationid}
    ${start_date}
    ${end_date}
    """
    tsutils.printiso(
        ncei_precip_15(stationid, start_date=start_date, end_date=end_date),
    )


@tsutils.copy_doc(ncei_precip_15_cli)
def ncei_precip_15(stationid, start_date=None, end_date=None):
    r"""National Centers for Environmental Information (NCEI) 15 minute precipitation."""
    return ncei_cdo_json_to_df(
        "PRECIP_15",
        stationid,
        start_date=start_date,
        end_date=end_date,
    )


# 1900-01-01, 2014-01-01, Precipitation Hourly        , 1    , PRECIP_HLY
@cltoolbox.command("ncei_precip_hly", formatter_class=HelpFormatter)
def ncei_precip_hly_cli(stationid, start_date=None, end_date=None):
    r"""global station H:NCEI hourly precipitation

    Requires registration and free API key.

    For every datatype and record there is a set of meta-data flags.
    For the GHCNDMS dataset, the flags are::

        'Total Missing','Consecutive Missing'

    Total Missing:

    Defined as total number of days observation/element is missing in that
    month.  This can be taken as a measure of quality or completeness as the
    higher the number of days sampled in the month, the more representative the
    value is for the entire month.

    Consecutive Missing:

    Defined as the maximum number of consecutive days in the month that an
    observation/element is missing.

    Parameters
    ----------
    ${stationid}
    ${start_date}
    ${end_date}
    """
    tsutils.printiso(
        ncei_precip_hly(stationid, start_date=start_date, end_date=end_date),
    )


@tsutils.copy_doc(ncei_precip_hly_cli)
def ncei_precip_hly(stationid, start_date=None, end_date=None):
    r"""National Centers for Environmental Information (NCEI) hourly precipitation."""
    return ncei_cdo_json_to_df(
        "PRECIP_HLY",
        stationid,
        start_date=start_date,
        end_date=end_date,
    )


# ANNUAL
@cltoolbox.command("ncei_annual", formatter_class=HelpFormatter)
def ncei_annual_cli(stationid, start_date=None, end_date=None):
    r"""global station A:NCEI annual data summaries

    Requires registration and free API key.

    For every datatype and record there is a set of meta-data flags.
    For the ANNUAL dataset, the flags are::

        'Measurement','Quality','Days','Units'

    The flags are described in the following tables.

    More info:
    http://www1.ncdc.noaa.gov/pub/data/cdo/documentation/ANNUAL_documentation.pdf

    Measurement flag

    +-------+------------------------------------------------------------------+
    | Code  | Description                                                      |
    +=======+==================================================================+
    | A     | Accumulated amount. This value is a total that may include data  |
    |       | from a previous month or months (TPCP)                           |
    +-------+------------------------------------------------------------------+
    | B     | Adjusted Total. Monthly value totals based on proportional       |
    |       | available data across the entire month. (CLDD, HTDD.             |
    +-------+------------------------------------------------------------------+
    | E     | An estimated monthly or annual total                             |
    +-------+------------------------------------------------------------------+
    | I     | Monthly means or totals based on incomplete time series. 1 to 9  |
    |       | days are missing. (MMNT,MMXP, MMXT, MNTM, TPCP, TSNW).           |
    +-------+------------------------------------------------------------------+
    | M     | Used to indicate data element missing.                           |
    +-------+------------------------------------------------------------------+
    | S     | Precipitation for the amount is continuing to be accumulated.    |
    |       | Total will be included in a subsequent value (TPCP). Example:    |
    |       | Days 1-20 had 1.35 in of precipitation, then a period of         |
    |       | accumulation began. The element TPCP would then be 00135S and    |
    |       | the total accumulated amount value appears in a subsequent       |
    |       | monthly value. If TPCP = 0 there was no precipitation measured   |
    |       | during the month. flag 1 is set to "S" and the total accumulated |
    |       | amount appears in a subsequent monthly value.                    |
    +-------+------------------------------------------------------------------+
    | T     | Trace of precipitation, snowfall, or snow depth. The             |
    |       | precipitation data value will = "00000". (EMXP, MXSD, TPCP,      |
    |       | TSNW).                                                           |
    +-------+------------------------------------------------------------------+
    | \+    | The phenomena in question occurred on several days. The date in  |
    |       | the DAY field is the last day of occurrence.                     |
    +-------+------------------------------------------------------------------+
    | Blank | No report.                                                       |
    +-------+------------------------------------------------------------------+

    Quality flag

    +------+--------------------------------------+
    | Code | Description                          |
    +======+======================================+
    | A    | Accumulated amount                   |
    +------+--------------------------------------+
    | E    | Estimated value                      |
    +------+--------------------------------------+
    | \+   | Value occurred on more than one day, |
    |      | last date of occurrence is used      |
    +------+--------------------------------------+

    Number of days flag

    Number of days is given as 00 when all days in the month are
    considered in computing data value or otherwise the maximum number
    of consecutive days in the month considered in computing the data
    value.

    Units flag

    +------+-------------------------------------------------------------------+
    | Code | Description                                                       |
    +======+===================================================================+
    | C    | Whole degree C                                                    |
    +------+-------------------------------------------------------------------+
    | D    | Whole F Degree Day                                                |
    +------+-------------------------------------------------------------------+
    | F    | Whole degree F                                                    |
    +------+-------------------------------------------------------------------+
    | HI   | Hundredths of in                                                  |
    +------+-------------------------------------------------------------------+
    | I    | Whole in                                                          |
    +------+-------------------------------------------------------------------+
    | M    | Whole miles                                                       |
    +------+-------------------------------------------------------------------+
    | MH   | Miles per hour                                                    |
    +------+-------------------------------------------------------------------+
    | MM   | mm                                                                |
    +------+-------------------------------------------------------------------+
    | NA   | No units applicable (dimensionless)                               |
    +------+-------------------------------------------------------------------+
    | TC   | Tenths of degrees C                                               |
    +------+-------------------------------------------------------------------+
    | TF   | Tenths of degrees F                                               |
    +------+-------------------------------------------------------------------+
    | TI   | Tenths of in                                                      |
    +------+-------------------------------------------------------------------+
    | TM   | Tenths of mm                                                      |
    +------+-------------------------------------------------------------------+
    | 1    | Soils, degrees F, soil depths in in and hundredths                |
    +------+-------------------------------------------------------------------+
    | 2    | Soils, degrees C, soil depth in whole cm                          |
    +------+-------------------------------------------------------------------+
    | 3    | Soils, degrees C, soil, soil depth in in and hundredths           |
    +------+-------------------------------------------------------------------+
    | 4    | Soils, degrees F, soil depth in whole cm                          |
    +------+-------------------------------------------------------------------+
    | 5    | Soils, If the soil station closed during the current month, '5'   |
    |      | indicates the station has closed.                                 |
    +------+-------------------------------------------------------------------+

    Parameters
    ----------
    ${stationid}
    ${start_date}
    ${end_date}
    """
    tsutils.printiso(
        ncei_annual(stationid, start_date=start_date, end_date=end_date),
    )


@tsutils.copy_doc(ncei_annual_cli)
def ncei_annual(stationid, start_date=None, end_date=None):
    r"""National Centers for Environmental Information (NCEI) annual data summaries."""
    return ncei_cdo_json_to_df(
        "ANNUAL",
        stationid,
        start_date=start_date,
        end_date=end_date,
    )


# GHCNDMS
@cltoolbox.command("ncei_ghcndms", formatter_class=HelpFormatter)
def ncei_ghcndms_cli(stationid, start_date=None, end_date=None):
    r"""global station M:NCEI GHCND Monthly Summaries (GHCNDMS)

    Requires registration and free API key.

    For every datatype and record there is a set of meta-data flags.

    GHCNDMS Meta-Data Flags

    +---------------------+-----------------------------------------------+
    | Total Missing       | Defined as total number of days               |
    |                     | observation/element is missing in that month. |
    |                     | This can be taken as a measure of quality or  |
    |                     | completeness as the higher the number of days |
    |                     | sampled in the month, the more representative |
    |                     | the value is for the entire month.            |
    +---------------------+-----------------------------------------------+
    | Consecutive Missing | Defined as the maximum number of consecutive  |
    |                     | days in the month that an observation/element |
    |                     | is missing.                                   |
    +---------------------+-----------------------------------------------+

    The following table lists the datatypes available for the 'ghcndms'
    dataset.  Not all datatypes are available for all stations.

    +------+-------------------------------------------------------------------+
    | Code | Description                                                       |
    +======+===================================================================+
    | ACMC | Average cloudiness midnight to midnight from 30-second ceilometer |
    |      | data                                                              |
    +------+-------------------------------------------------------------------+
    | ACMH | Average cloudiness midnight to midnight from manual observations  |
    +------+-------------------------------------------------------------------+
    | ACSC | Average cloudiness sunrise to sunset from 30-second ceilometer    |
    |      | data                                                              |
    +------+-------------------------------------------------------------------+
    | ACSH | Average cloudiness sunrise to sunset from manual observations     |
    +------+-------------------------------------------------------------------+
    | AWND | Average wind speed                                                |
    +------+-------------------------------------------------------------------+
    | DAEV | Number of days included in the multiday evaporation total (MDEV)  |
    +------+-------------------------------------------------------------------+
    | DAPR | Number of days included in the multiday precipitation total       |
    |      | (MDPR)                                                            |
    +------+-------------------------------------------------------------------+
    | DASF | Number of days included in the multiday snow fall total (MDSF)    |
    +------+-------------------------------------------------------------------+
    | DATN | Number of days included in the multiday minimum temperature       |
    |      | (MDTN)                                                            |
    +------+-------------------------------------------------------------------+
    | DATX | Number of days included in the multiday maximum temperature       |
    |      | (MDTX)                                                            |
    +------+-------------------------------------------------------------------+
    | DAWM | Number of days included in the multiday wind movement (MDWM)      |
    +------+-------------------------------------------------------------------+
    | DWPR | Number of days with non-zero precipitation included in multiday   |
    |      | precipitation total (MDPR)                                        |
    +------+-------------------------------------------------------------------+
    | EVAP | Evaporation of water from evaporation pan                         |
    +------+-------------------------------------------------------------------+
    | FMTM | Time of fastest mile or fastest 1-minute wind                     |
    +------+-------------------------------------------------------------------+
    | FRGB | Base of frozen ground layer                                       |
    +------+-------------------------------------------------------------------+
    | FRGT | Top of frozen ground layer                                        |
    +------+-------------------------------------------------------------------+
    | FRTH | Thickness of frozen ground layer                                  |
    +------+-------------------------------------------------------------------+
    | GAHT | Difference between river and gauge height                         |
    +------+-------------------------------------------------------------------+
    | MDEV | Multiday evaporation total (use with DAEV)                        |
    +------+-------------------------------------------------------------------+
    | MDPR | Multiday precipitation total (use with DAPR and DWPR, if          |
    |      | available)                                                        |
    +------+-------------------------------------------------------------------+
    | MDSF | Multiday snowfall total                                           |
    +------+-------------------------------------------------------------------+
    | MDTN | Multiday minimum temperature (use with DATN)                      |
    +------+-------------------------------------------------------------------+
    | MDTX | Multiday maximum temperature (use with DATX)                      |
    +------+-------------------------------------------------------------------+
    | MDWM | Multiday wind movement                                            |
    +------+-------------------------------------------------------------------+
    | MNPN | Daily minimum temperature of water in an evaporation pan          |
    +------+-------------------------------------------------------------------+
    | MXPN | Daily maximum temperature of water in an evaporation pan          |
    +------+-------------------------------------------------------------------+
    | PGTM | Peak gust time                                                    |
    +------+-------------------------------------------------------------------+
    | PRCP | Precipitation                                                     |
    +------+-------------------------------------------------------------------+
    | PSUN | Daily percent of possible sunshine for the period                 |
    +------+-------------------------------------------------------------------+
    | SN01 | Minimum soil temperature with unknown cover at 5 cm depth         |
    +------+-------------------------------------------------------------------+
    | SN02 | Minimum soil temperature with unknown cover at 10 cm depth        |
    +------+-------------------------------------------------------------------+
    | SN03 | Minimum soil temperature with unknown cover at 20 cm depth        |
    +------+-------------------------------------------------------------------+
    | SN11 | Minimum soil temperature with grass cover at 5 cm depth           |
    +------+-------------------------------------------------------------------+
    | SN12 | Minimum soil temperature with grass cover at 10 cm depth          |
    +------+-------------------------------------------------------------------+
    | SN13 | Minimum soil temperature with grass cover at 20 cm depth          |
    +------+-------------------------------------------------------------------+
    | SN14 | Minimum soil temperature with grass cover at 50 cm depth          |
    +------+-------------------------------------------------------------------+
    | SN21 | Minimum soil temperature with fallow cover at 5 cm depth          |
    +------+-------------------------------------------------------------------+
    | SN22 | Minimum soil temperature with fallow cover at 10 cm depth         |
    +------+-------------------------------------------------------------------+
    | SN23 | Minimum soil temperature with fallow cover at 20 cm depth         |
    +------+-------------------------------------------------------------------+
    | SN31 | Minimum soil temperature with bare ground cover at 5 cm depth     |
    +------+-------------------------------------------------------------------+
    | SN32 | Minimum soil temperature with bare ground cover at 10 cm depth    |
    +------+-------------------------------------------------------------------+
    | SN33 | Minimum soil temperature with bare ground cover at 20 cm depth    |
    +------+-------------------------------------------------------------------+
    | SN34 | Minimum soil temperature with bare ground cover at 50 cm depth    |
    +------+-------------------------------------------------------------------+
    | SN35 | Minimum soil temperature with bare ground cover at 100 cm depth   |
    +------+-------------------------------------------------------------------+
    | SN36 | Minimum soil temperature with bare ground cover at 150 cm depth   |
    +------+-------------------------------------------------------------------+
    | SN51 | Minimum soil temperature with sod cover at 5 cm depth             |
    +------+-------------------------------------------------------------------+
    | SN52 | Minimum soil temperature with sod cover at 10 cm depth            |
    +------+-------------------------------------------------------------------+
    | SN53 | Minimum soil temperature with sod cover at 20 cm depth            |
    +------+-------------------------------------------------------------------+
    | SN54 | Minimum soil temperature with sod cover at 50 cm depth            |
    +------+-------------------------------------------------------------------+
    | SN55 | Minimum soil temperature with sod cover at 100 cm depth           |
    +------+-------------------------------------------------------------------+
    | SN56 | Minimum soil temperature with sod cover at 150 cm depth           |
    +------+-------------------------------------------------------------------+
    | SN57 | Minimum soil temperature with sod cover at 180 cm depth           |
    +------+-------------------------------------------------------------------+
    | SN61 | Minimum soil temperature with straw multch cover at 5 cm depth    |
    +------+-------------------------------------------------------------------+
    | SN72 | Minimum soil temperature with grass muck cover at 10 cm depth     |
    +------+-------------------------------------------------------------------+
    | SN81 | Minimum soil temperature with bare muck cover at 5 cm depth       |
    +------+-------------------------------------------------------------------+
    | SN82 | Minimum soil temperature with bare muck cover at 10 cm depth      |
    +------+-------------------------------------------------------------------+
    | SN83 | Minimum soil temperature with bare muck cover at 20 cm depth      |
    +------+-------------------------------------------------------------------+
    | SNOW | Snowfall                                                          |
    +------+-------------------------------------------------------------------+
    | SNWD | Snow depth                                                        |
    +------+-------------------------------------------------------------------+
    | SX01 | Maximum soil temperature with unknown cover at 5 cm depth         |
    +------+-------------------------------------------------------------------+
    | SX02 | Maximum soil temperature with unknown cover at 10 cm depth        |
    +------+-------------------------------------------------------------------+
    | SX03 | Maximum soil temperature with unknown cover at 20 cm depth        |
    +------+-------------------------------------------------------------------+
    | SX11 | Maximum soil temperature with grass cover at 5 cm depth           |
    +------+-------------------------------------------------------------------+
    | SX12 | Maximum soil temperature with grass cover at 10 cm depth          |
    +------+-------------------------------------------------------------------+
    | SX13 | Maximum soil temperature with grass cover at 20 cm depth          |
    +------+-------------------------------------------------------------------+
    | SX14 | Maximum soil temperature with grass cover at 50 cm depth          |
    +------+-------------------------------------------------------------------+
    | SX15 | Maximum soil temperature with grass cover at 100 cm depth         |
    +------+-------------------------------------------------------------------+
    | SX17 | Maximum soil temperature with grass cover at 180 cm depth         |
    +------+-------------------------------------------------------------------+
    | SX21 | Maximum soil temperature with fallow cover at 5 cm depth          |
    +------+-------------------------------------------------------------------+
    | SX22 | Maximum soil temperature with fallow cover at 10 cm depth         |
    +------+-------------------------------------------------------------------+
    | SX23 | Maximum soil temperature with fallow cover at 20 cm depth         |
    +------+-------------------------------------------------------------------+
    | SX31 | Maximum soil temperature with bare ground cover at 5 cm depth     |
    +------+-------------------------------------------------------------------+
    | SX32 | Maximum soil temperature with bare ground cover at 10 cm depth    |
    +------+-------------------------------------------------------------------+
    | SX33 | Maximum soil temperature with bare ground cover at 20 cm depth    |
    +------+-------------------------------------------------------------------+
    | SX34 | Maximum soil temperature with bare ground cover at 50 cm depth    |
    +------+-------------------------------------------------------------------+
    | SX35 | Maximum soil temperature with bare ground cover at 100 cm depth   |
    +------+-------------------------------------------------------------------+
    | SX36 | Maximum soil temperature with bare ground cover at 150 cm depth   |
    +------+-------------------------------------------------------------------+
    | SX51 | Maximum soil temperature with sod cover at 5 cm depth             |
    +------+-------------------------------------------------------------------+
    | SX52 | Maximum soil temperature with sod cover at 10 cm depth            |
    +------+-------------------------------------------------------------------+
    | SX53 | Maximum soil temperature with sod cover at 20 cm depth            |
    +------+-------------------------------------------------------------------+
    | SX54 | Maximum soil temperature with sod cover at 50 cm depth            |
    +------+-------------------------------------------------------------------+
    | SX55 | Maximum soil temperature with sod cover at 100 cm depth           |
    +------+-------------------------------------------------------------------+
    | SX56 | Maximum soil temperature with sod cover at 150 cm depth           |
    +------+-------------------------------------------------------------------+
    | SX57 | Maximum soil temperature with sod cover at 180 cm depth           |
    +------+-------------------------------------------------------------------+
    | SX61 | Maximum soil temperature with straw mulch cover at 5 cm depth     |
    +------+-------------------------------------------------------------------+
    | SX72 | Maximum soil temperature with grass muck cover at 10 cm depth     |
    +------+-------------------------------------------------------------------+
    | SX81 | Maximum soil temperature with bare muck cover at 5 cm depth       |
    +------+-------------------------------------------------------------------+
    | SX82 | Maximum soil temperature with bare muck cover at 10 cm depth      |
    +------+-------------------------------------------------------------------+
    | SX83 | Maximum soil temperature with bare muck cover at 20 cm depth      |
    +------+-------------------------------------------------------------------+
    | TAVG | Average Temperature.                                              |
    +------+-------------------------------------------------------------------+
    | THIC | Thickness of ice on water                                         |
    +------+-------------------------------------------------------------------+
    | TMAX | Maximum temperature                                               |
    +------+-------------------------------------------------------------------+
    | TMIN | Minimum temperature                                               |
    +------+-------------------------------------------------------------------+
    | TOBS | Temperature at the time of observation                            |
    +------+-------------------------------------------------------------------+
    | TSUN | Total sunshine for the period                                     |
    +------+-------------------------------------------------------------------+
    | WDF1 | Direction of fastest 1-minute wind                                |
    +------+-------------------------------------------------------------------+
    | WDF2 | Direction of fastest 2-minute wind                                |
    +------+-------------------------------------------------------------------+
    | WDF5 | Direction of fastest 5-second wind                                |
    +------+-------------------------------------------------------------------+
    | WDFG | Direction of peak wind gust                                       |
    +------+-------------------------------------------------------------------+
    | WDFI | Direction of highest instantaneous wind                           |
    +------+-------------------------------------------------------------------+
    | WDFM | Fastest mile wind direction                                       |
    +------+-------------------------------------------------------------------+
    | WDMV | Total wind movement                                               |
    +------+-------------------------------------------------------------------+
    | WESD | Water equivalent of snow on the ground                            |
    +------+-------------------------------------------------------------------+
    | WESF | Water equivalent of snowfall                                      |
    +------+-------------------------------------------------------------------+
    | WSF1 | Fastest 1-minute wind speed                                       |
    +------+-------------------------------------------------------------------+
    | WSF2 | Fastest 2-minute wind speed                                       |
    +------+-------------------------------------------------------------------+
    | WSF5 | Fastest 5-second wind speed                                       |
    +------+-------------------------------------------------------------------+
    | WSFG | Peak gust wind speed                                              |
    +------+-------------------------------------------------------------------+
    | WSFI | Highest instantaneous wind speed                                  |
    +------+-------------------------------------------------------------------+
    | WSFM | Fastest mile wind speed                                           |
    +------+-------------------------------------------------------------------+
    | WT01 | Fog, ice fog, or freezing fog (may include heavy fog)             |
    +------+-------------------------------------------------------------------+
    | WT02 | Heavy fog or heaving freezing fog (not always distinguished from  |
    |      | fog)                                                              |
    +------+-------------------------------------------------------------------+
    | WT03 | Thunder                                                           |
    +------+-------------------------------------------------------------------+
    | WT04 | Ice pellets, sleet, snow pellets, or small hail                   |
    +------+-------------------------------------------------------------------+
    | WT05 | Hail (may include small hail)                                     |
    +------+-------------------------------------------------------------------+
    | WT06 | Glaze or rime                                                     |
    +------+-------------------------------------------------------------------+
    | WT07 | Dust, volcanic ash, blowing dust, blowing sand, or blowing        |
    |      | obstruction                                                       |
    +------+-------------------------------------------------------------------+
    | WT08 | Smoke or haze                                                     |
    +------+-------------------------------------------------------------------+
    | WT09 | Blowing or drifting snow                                          |
    +------+-------------------------------------------------------------------+
    | WT10 | Tornado, waterspout, or funnel cloud                              |
    +------+-------------------------------------------------------------------+
    | WT11 | High or damaging winds                                            |
    +------+-------------------------------------------------------------------+
    | WT12 | Blowing spray                                                     |
    +------+-------------------------------------------------------------------+
    | WT13 | Mist                                                              |
    +------+-------------------------------------------------------------------+
    | WT14 | Drizzle                                                           |
    +------+-------------------------------------------------------------------+
    | WT15 | Freezing drizzle                                                  |
    +------+-------------------------------------------------------------------+
    | WT16 | Rain (may include freezing rain, drizzle, and freezing drizzle)   |
    +------+-------------------------------------------------------------------+
    | WT17 | Freezing rain                                                     |
    +------+-------------------------------------------------------------------+
    | WT18 | Snow, snow pellets, snow grains, or ice crystals                  |
    +------+-------------------------------------------------------------------+
    | WT19 | Unknown source of precipitation                                   |
    +------+-------------------------------------------------------------------+
    | WT21 | Ground fog                                                        |
    +------+-------------------------------------------------------------------+
    | WT22 | Ice fog or freezing fog                                           |
    +------+-------------------------------------------------------------------+
    | WV01 | Fog, ice fog, or freezing fog (may include heavy fog)             |
    +------+-------------------------------------------------------------------+
    | WV03 | Thunder                                                           |
    +------+-------------------------------------------------------------------+
    | WV07 | Ash, dust, sand, or other blowing obstruction                     |
    +------+-------------------------------------------------------------------+
    | WV18 | Snow or ice crystals                                              |
    +------+-------------------------------------------------------------------+
    | WV20 | Rain or snow shower                                               |
    +------+-------------------------------------------------------------------+

    Parameters
    ----------
    ${stationid}
    ${start_date}
    ${end_date}
    """
    tsutils.printiso(
        ncei_ghcndms(stationid, start_date=start_date, end_date=end_date),
    )


@tsutils.copy_doc(ncei_ghcndms_cli)
def ncei_ghcndms(stationid, start_date=None, end_date=None):
    r"""National Centers for Environmental Information (NCEI) GHCND Monthly Summaries."""
    return ncei_cdo_json_to_df(
        "GHCNDMS",
        stationid,
        start_date=start_date,
        end_date=end_date,
    )


@cltoolbox.command("ncei_ish", formatter_class=HelpFormatter)
@tsutils.doc({**tsutils.docstrings, **ncei_ghcnd_docstrings})
def ncei_ish_cli(stationid, start_date=None, end_date=None):
    r"""global station H:Integrated Surface Database

    ${info}

    Parameters
    ----------
    ${stationid}
    ${start_date}
    ${end_date}
    """
    tsutils.printiso(
        ncei_ish(stationid, start_date=start_date, end_date=end_date),
    )


@tsutils.copy_doc(ncei_ish_cli)
def ncei_ish(stationid, start_date=None, end_date=None):
    r"""Download from the Global Historical Climatology Network - Daily."""
    stationid = stationid.replace("-", "")

    # "https://www1.ncdc.noaa.gov/pub/data/noaa/{year}/{station}-{year}.gz",
    final = utils.file_downloader(
        "https://www.ncei.noaa.gov/data/global-hourly/access/{year}/{station}.csv",
        stationid,
        startdate=pd.to_datetime(start_date),
        enddate=pd.to_datetime(end_date),
    )

    # Get rid of unused columns
    final = final.drop(
        columns=[
            "STATION",
            "SOURCE",
            "LATITUDE",
            "LONGITUDE",
            "ELEVATION",
            "NAME",
            "CALL_SIGN",
        ]
    )

    # Get rid of not useful REPORT_TYPEs.
    final = final[
        ~final["REPORT_TYPE"].isin(["BOGUS", "COOPD", "SOD", "SOM", "PCP15", "PCP60"])
    ]

    process = {
        "WND": OrderedDict(
            {
                "WND_DIR:deg": {"astype": "float64", "replace": "999"},
                "WND_DIR_QC": {},
                "WND_OBS_TYPE": {"replace": "9"},
                "WND_SPD:m/s": {"astype": "float64", "replace": "9999", "factor": 0.1},
                "WND_SPD_QC": {},
            }
        ),
        "CIG": OrderedDict(
            {
                "CEIL:m": {"astype": "float64", "replace": "99999"},
                "CEIL_QC": {},
                "CEIL:DC": {"replace": "9"},
                "CAVOK": {"replace": "9"},
            }
        ),
        "VIS": OrderedDict(
            {
                "VIS:m": {"astype": "float64", "replace": "999999"},
                "VIS_QC": {},
                "VIS_VAR": {"replace": "9"},
                "VIS_VAR_QC": {},
            }
        ),
        "TMP": OrderedDict(
            {
                "AIRT:degC": {"astype": "float64", "replace": "+9999", "factor": 0.1},
                "AIRT_QC": {},
            }
        ),
        "DEW": OrderedDict(
            {
                "DEW:degC": {"astype": "float64", "replace": "+9999", "factor": 0.1},
                "DEW_QC": {},
            }
        ),
        "SLP": OrderedDict(
            {
                "AIR_PRESS:hectopascals": {
                    "astype": "float64",
                    "replace": "99999",
                    "factor": 0.1,
                },
                "AIR_PRESS_QC": {},
            }
        ),
        "AA1": OrderedDict(
            {
                "PREC1_PER:hour": {"astype": "float64", "replace": "99"},
                "PREC1_DPTH:mm": {
                    "astype": "float64",
                    "replace": "9999",
                    "factor": 0.1,
                },
                "PREC1_COND": {},
                "PREC1_QC": {},
            }
        ),
        "AA2": OrderedDict(
            {
                "PREC2_PER:hour": {"astype": "float64", "replace": "99"},
                "PREC2_DPTH:mm": {
                    "astype": "float64",
                    "replace": "9999",
                    "factor": 0.1,
                },
                "PREC2_COND": {},
                "PREC2_QC": {},
            }
        ),
        "AA3": OrderedDict(
            {
                "PREC3_PER:hour": {"astype": "float64", "replace": "99"},
                "PREC3_DPTH:mm": {
                    "astype": "float64",
                    "replace": "9999",
                    "factor": 0.1,
                },
                "PREC3_COND": {},
                "PREC3_QC": {},
            }
        ),
        "AA4": OrderedDict(
            {
                "PREC4_PER:hour": {"astype": "float64", "replace": "99"},
                "PREC4_DPTH:mm": {
                    "astype": "float64",
                    "replace": "9999",
                    "factor": 0.1,
                },
                "PREC4_COND": {},
                "PREC4_QC": {},
            }
        ),
        "AB1": OrderedDict(
            {
                "PREC_MON_DPTH:mm": {
                    "astype": "float64",
                    "replace": "9999",
                    "factor": 0.1,
                },
                "PREC_MON_COND": {},
                "PREC_MON_QC": {},
            }
        ),
        "AC1": OrderedDict(
            {
                "PREC_HIST_DUR": {"astype": "float64", "replace": "9"},
                "PREC_HIST_COND": {"replace": "9"},
                "PREC_HIST_QC": {},
            }
        ),
        "AD1": OrderedDict(
            {
                "PREC_HIST_DUR": {"astype": "float64", "replace": "9"},
                "PREC_HIST_COND": {"replace": "9"},
                "PREC_HIST_QC": {},
            }
        ),
        "GA1": OrderedDict(
            {
                "SKY_COV1": {"replace": "99"},
                "SKY_COV1_QC": {},
                "SKY_COV1_BASE:m": {"replace": "99999"},
                "SKY_COV1_BASE_QC": {},
                "SKY_COV1_CLD": {},
                "SKY_COV1_CLD_QC": {},
            }
        ),
        "GA2": OrderedDict(
            {
                "SKY_COV2": {"replace": "99"},
                "SKY_COV2_QC": {},
                "SKY_COV2_BASE:m": {"replace": "99999"},
                "SKY_COV2_BASE_QC": {},
                "SKY_COV2_CLD": {},
                "SKY_COV2_CLD_QC": {},
            }
        ),
        "GA3": OrderedDict(
            {
                "SKY_COV3": {"replace": "99"},
                "SKY_COV3_QC": {},
                "SKY_COV3_BASE:m": {"replace": "99999"},
                "SKY_COV3_BASE_QC": {},
                "SKY_COV3_CLD": {},
                "SKY_COV3_CLD_QC": {},
            }
        ),
        "GA4": OrderedDict(
            {
                "SKY_COV4": {"replace": "99"},
                "SKY_COV4_QC": {},
                "SKY_COV4_BASE:m": {"replace": "99999"},
                "SKY_COV4_BASE_QC": {},
                "SKY_COV4_CLD": {},
                "SKY_COV4_CLD_QC": {},
            }
        ),
        "GA5": OrderedDict(
            {
                "SKY_COV5": {"replace": "99"},
                "SKY_COV5_QC": {},
                "SKY_COV5_BASE:m": {"replace": "99999"},
                "SKY_COV5_BASE_QC": {},
                "SKY_COV5_CLD": {},
                "SKY_COV5_CLD_QC": {},
            }
        ),
        "GA6": OrderedDict(
            {
                "SKY_COV6": {"replace": "99"},
                "SKY_COV6_QC": {},
                "SKY_COV6_BASE:m": {"replace": "99999"},
                "SKY_COV6_BASE_QC": {},
                "SKY_COV6_CLD": {},
                "SKY_COV6_CLD_QC": {},
            }
        ),
        "GF1": OrderedDict(
            {
                "SKY_COV_TOT": {"replace": "99"},
                "SKY_COV_OPAQUE": {"replace": "99"},
                "SKY_COV_TOT_QC": {},
                "SKY_COV_LOW": {"replace": "99"},
                "SKY_COV_LOW_QC": {},
                "SKY_COV_CLD": {},
                "SKY_COV_CLD_QC": {},
                "SKY_COV_LOW_BASE:m": {"replace": "99999"},
                "SKY_COV_LOW_BASE_QC": {},
                "SKY_COV_MID": {},
                "SKY_COV_MIN_QC": {},
                "SKY_COV_HIGH": {},
                "SKY_COV_HIGH_QC": {},
            }
        ),
        "MW1": OrderedDict(
            {
                "WTHR_OBS1": {"astype": "Int64"},
                "WTHR_OBS1_QC": {},
            }
        ),
        "MW2": OrderedDict(
            {
                "WTHR_OBS2": {"astype": "Int64"},
                "WTHR_OBS2_QC": {},
            }
        ),
        "MW3": OrderedDict(
            {
                "WTHR_OBS3": {"astype": "Int64"},
                "WTHR_OBS3_QC": {},
            }
        ),
        "MW4": OrderedDict(
            {
                "WTHR_OBS4": {"astype": "Int64"},
                "WTHR_OBS4_QC": {},
            }
        ),
        "MD1": OrderedDict(
            {
                "ATM_PRESS_CHG:hectopascals": {"astype": "Int64", "replace": "9"},
                "ATM_PRESS_CHG_QC": {},
                "ATM_PRESS_CHG_3HR:hectopascals": {
                    "astype": "float64",
                    "replace": "999",
                    "factor": 0.1,
                },
                "ATM_PRESS_CHG_3HR_QC": {},
                "ATM_PRESS_CHG_24HR:hectopascals": {
                    "astype": "float64",
                    "replace": "+999",
                    "factor": 0.1,
                },
                "ATM_PRESS_CHG_24HR_QC": {},
            }
        ),
        "EQD": OrderedDict({"ELEMENT_QUALITY_DATA": {}}),
        "AY1": OrderedDict(
            {
                "PAST_WEATHER_MANUAL_1_ATM_CONDITION": {},
                "PAST_WEATHER_MANUAL_1_ATM_QC": {},
                "PAST_WEATHER_MANUAL_1_ATM_PERIOD_QUANTITY:hour": {
                    "astype": "float64",
                    "replace": "99",
                },
                "PAST_WEATHER_MANUAL_1_ATM_PERIOD_QUANTITY_QC": {},
            }
        ),
        "AY2": OrderedDict(
            {
                "PAST_WEATHER_MANUAL_2_ATM_CONDITION": {},
                "PAST_WEATHER_MANUAL_2_ATM_QC": {},
                "PAST_WEATHER_MANUAL_2_ATM_PERIOD_QUANTITY:hour": {
                    "astype": "float64",
                    "replace": "99",
                },
                "PAST_WEATHER_MANUAL_2_ATM_PERIOD_QUANTITY_QC": {},
            }
        ),
        "OC1": OrderedDict(
            {
                "WND_GUST:m/s": {"astype": "float64", "replace": "9999", "factor": 0.1},
                "WND_GUST_QC": {},
            }
        ),
        "UA1": OrderedDict(
            {
                "WAVE_METHOD": {"replace": "9"},
                "WAVE_PER:s": {"astype": "float64", "replace": "99"},
                "WAVE_HGT:m": {"astype": "float64", "replace": "999", "factor": 0.1},
                "WAVE_HGT_QC": {},
                "WAVE_STATE": {"replace": "99"},
                "WAVE_STATE_QC": {},
            }
        ),
        "KA1": OrderedDict(
            {
                "EXTREME_AIR_TEMPERATURE_1_period_quantity:hour": {
                    "astype": "float64",
                    "replace": "999",
                    "factor": 0.1,
                },
                "EXTREME_AIR_TEMPERATURE_1_code": {"replace": "9"},
                "EXTREME_AIR_TEMPERATURE_1_air_temperature:degC": {
                    "astype": "float64",
                    "replace": "9999",
                    "factor": 0.1,
                },
                "EXTREME_AIR_TEMPERATURE_1_temperature_quality_code": {},
            }
        ),
        "KA2": OrderedDict(
            {
                "EXTREME_AIR_TEMPERATURE_2_period_quantity:hour": {
                    "astype": "float64",
                    "replace": "999",
                    "factor": 0.1,
                },
                "EXTREME_AIR_TEMPERATURE_2_code": {"replace": "9"},
                "EXTREME_AIR_TEMPERATURE_2_air_temperature:degC": {
                    "astype": "float64",
                    "replace": "9999",
                    "factor": 0.1,
                },
                "EXTREME_AIR_TEMPERATURE_2_temperature_quality_code": {},
            }
        ),
        "KA3": OrderedDict(
            {
                "EXTREME_AIR_TEMPERATURE_3_period_quantity:hour": {
                    "astype": "float64",
                    "replace": "999",
                    "factor": 0.1,
                },
                "EXTREME_AIR_TEMPERATURE_3_code": {"replace": "9"},
                "EXTREME_AIR_TEMPERATURE_3_air_temperature:degC": {
                    "astype": "float64",
                    "replace": "9999",
                    "factor": 0.1,
                },
                "EXTREME_AIR_TEMPERATURE_3_temperature_quality_code": {},
            }
        ),
        "KA4": OrderedDict(
            {
                "EXTREME_AIR_TEMPERATURE_4_period_quantity:hour": {
                    "astype": "float64",
                    "replace": "999",
                    "factor": 0.1,
                },
                "EXTREME_AIR_TEMPERATURE_4_code": {"replace": "9"},
                "EXTREME_AIR_TEMPERATURE_4_air_temperature:degC": {
                    "astype": "float64",
                    "replace": "9999",
                    "factor": 0.1,
                },
                "EXTREME_AIR_TEMPERATURE_4_temperature_quality_code": {},
            }
        ),
        "AJ1": OrderedDict(
            {
                "SNOW_DEPTH:cm": {"replace": "9999"},
                "SNOW_DEPTH_COND": {"replace": "9"},
                "SNOW_DEPTH_QC": {},
                "SNOW_DEPTH_EW:mm": {
                    "astype": "float64",
                    "replace": "999999",
                    "factor": 0.1,
                },
                "SNOW_DEPTH_EW_COND": {"replace": "9"},
                "SNOW_DEPTH_EW_QC": {},
            }
        ),
        "MA1": OrderedDict(
            {
                "ATM_PRESS_altimeter_setting_rate:hectopascals": {
                    "astype": "float64",
                    "replace": "99999",
                    "factor": 0.1,
                },
                "ATM_PRESS_altimeter_quality_code": {},
                "ATM_PRESS_station_pressure_rate:hectopascals": {
                    "astype": "float64",
                    "replace": "99999",
                    "factor": 0.1,
                },
                "ATM_PRESS_station_pressure_quality_code": {},
            }
        ),
        # "REM" documentation indicates 3 columns, but the script parses out 5.
        # "REM": OrderedDict(
        #     {
        #         "GEOPHYSICAL_PNT_OBS_rem_id": {},
        #         "GEOPHYSICAL_PNT_OBS_rem_length": {},
        #         "GEOPHYSICAL_PNT_OBS_rem": {},
        #     }
        # ),
        # WG1,OA1,AL1,IA1,IA2,AG1,HL1,OA2,OA3,AW1,AZ1,AZ2,SA1,UG1,ME1,OD1,OD2,GE1,AW2
    }

    loopvar = list(final.columns)
    for cname, variables in process.items():
        if cname in loopvar:
            addto = final[cname].str.split(" *, *", expand=True)
            addto.columns = variables.keys()
            for vname in variables.keys():
                modifiers = process[cname][vname]
                if "astype" in modifiers:
                    addto[vname] = addto[vname].astype(modifiers["astype"])
                if "replace" in modifiers:
                    addto[vname] = addto[vname].replace(modifiers["replace"], np.nan)
                if "factor" in modifiers:
                    addto[vname] = addto[vname] * modifiers["factor"]
            final = final.drop(cname, axis="columns")
            final = pd.concat([final, addto], axis="columns")
    return final


# @cltoolbox.command("ncei_cirs", formatter_class=HelpFormatter)
def ncei_cirs_cli(elements=None, by_state=False, location_names="abbr"):
    """global station: Retrieves climate indices

    Parameters
    ----------
    elements
        The element(s) for which to get data for. If None (default), then all
        elements are used. An individual element is a string, but a list or
        tuple of them can be used to specify a set of elements. Elements are:

        +------+-------------------------------------------+
        | Code | Description                               |
        +======+===========================================+
        | cddc | Cooling Degree Days                       |
        +------+-------------------------------------------+
        | hddc | Heating Degree Days                       |
        +------+-------------------------------------------+
        | pcpn | Precipitation                             |
        +------+-------------------------------------------+
        | pdsi | Palmer Drought Severity Index             |
        +------+-------------------------------------------+
        | phdi | Palmer Hydrological Drought Index         |
        +------+-------------------------------------------+
        | pmdi | Modified Palmer Drought Severity Index    |
        +------+-------------------------------------------+
        | sp01 | 1-month Standardized Precipitation Index  |
        +------+-------------------------------------------+
        | sp02 | 2-month Standardized Precipitation Index  |
        +------+-------------------------------------------+
        | sp03 | 3-month Standardized Precipitation Index  |
        +------+-------------------------------------------+
        | sp06 | 6-month Standardized Precipitation Index  |
        +------+-------------------------------------------+
        | sp09 | 9-month Standardized Precipitation Index  |
        +------+-------------------------------------------+
        | sp12 | 12-month Standardized Precipitation Index |
        +------+-------------------------------------------+
        | sp24 | 24-month Standardized Precipitation Index |
        +------+-------------------------------------------+
        | tmpc | Temperature                               |
        +------+-------------------------------------------+
        | zndx | ZNDX                                      |
        +------+-------------------------------------------+

    by_state
        If False (default), divisional data will be retrieved. If True, then
        regional data will be retrieved.

    location_names
        This parameter defines what (if any) type of names will be added to the
        values. If set to ‘abbr’ (default), then abbreviated location names
        will be used. If ‘full’, then full location names will be used. If set
        to None, then no location name will be added and the only identifier
        will be the location_codes (this is the most memory-conservative
        option)."""
    tsutils.printiso(
        ncei_cirs(elements=elements, by_state=by_state, location_names=location_names)
    )


@tsutils.copy_doc(ncei_cirs_cli)
def ncei_cirs(elements=None, by_state=False, location_names="abbr"):
    """global station: Retrieves climate indices"""
    # df = df.set_index("period")
    # df.index = pd.PeriodIndex(df.index)
    # df.index.name = "Datetime"
    # df.columns = [unit_conv.get(i, i) for i in df.columns]
    return get_data(
        elements=elements,
        by_state=by_state,
        location_names=location_names,
        as_dataframe=True,
    )


if __name__ == "__main__":
    # r = ncei_cirs()
    # print(r)
    for station in ("028360-99999", "03391099999"):
        print(f"ISH:{station}")
        r = ncei_ish(station)
        print(r)

    r = ncei_ghcnd_ftp(
        stationid="ASN00075020",
        start_date="2000-01-01",
        end_date="2001-01-01",
    )

    print("3 ghcnd")
    print(r)

    r = ncei_ghcnd_ftp(
        stationid="ASN00075020",
        start_date="2001-01-01",
        end_date="2002-01-01",
    )

    print("4 ghcnd")
    print(r)

    # http://www.ncdc.noaa.gov/cdo-web/api/v2/data?
    #  datasetid=PRECIP_15&
    #  stationid=COOP:010008&
    #  units=metric&start_date=2010-05-01&end_date=2010-05-31
    r = ncei_precip_15(
        "COOP:010008",
        start_date="2010-05-01",
        end_date="2010-05-31",
    )
    print("5 precip_15")
    print(r)
    mardi = [
        ["GHCND", "GHCND:AE000041196"],
        ["GHCND", "GHCND:USR0000GCOO"],
        ["GSOM", "GHCND:US1FLAL0004"],
        ["GSOY", "GHCND:USW00012816"],
        ["NEXRAD2", "NEXRAD:KJAX"],
        ["NEXRAD3", "NEXRAD:KJAX"],
        ["NORMAL_ANN", "GHCND:USC00083322"],
        ["NORMAL_DLY", "GHCND:USC00084731"],
        ["NORMAL_HLY", "GHCND:USW00013889"],
        ["NORMAL_MLY", "GHCND:USC00086618"],
        ["PRECIP_15", "COOP:087440"],
        ["PRECIP_HLY", "COOP:087440"],
        # ['ANNUAL', 'GHCND:US1MOLN0006'],
        # ["GHCNDMS", "GHCND:US1FLAL0004"],
    ]
    start_date = "2010-01-01"
    end_date = "2013-01-01"

    print("GHCND")
    r = ncei_ghcnd(
        "GHCND:AE000041196",
        start_date=start_date,
        end_date=end_date,
    )
    print(r)

    print("GHCND")
    r = ncei_ghcnd(
        "GHCND:USR0000GCOO",
        start_date=start_date,
        end_date=end_date,
    )
    print(r)

    print("GSOM")
    r = ncei_gsom(
        "GHCND:US1FLAL0004",
        start_date=start_date,
        end_date=end_date,
    )
    print(r)

    print("GSOY")
    r = ncei_gsoy(
        "GHCND:USW00012816",
        start_date=start_date,
        end_date="2013-12-31",
    )
    print(r)

    print("NEXRAD2")
    r = ncei_nexrad2(
        "NEXRAD:KJAX",
        start_date=start_date,
        end_date=end_date,
    )
    print(r)

    print("NEXRAD3")
    r = ncei_nexrad3(
        "NEXRAD:KJAX",
        start_date=start_date,
        end_date=end_date,
    )
    print(r)

    print("NORMAL_ANN")
    r = ncei_normal_ann(
        "GHCND:USC00084731",
    )
    print(r)

    print("NORMAL_DLY")
    r = ncei_normal_dly(
        "GHCND:USC00084731",
    )
    print(r)

    print("NORMAL_HLY")
    r = ncei_normal_hly(
        "GHCND:USW00013889",
    )
    print(r)

    print("NORMAL_MLY")
    r = ncei_normal_mly(
        "GHCND:USC00086618",
    )
    print(r)

    print("PRECIP_15")
    r = ncei_precip_15(
        "COOP:087440",
        start_date=start_date,
        end_date=end_date,
    )
    print(r)

    print("PRECIP_HLY")
    r = ncei_precip_hly(
        "COOP:087440",
        start_date=start_date,
        end_date=end_date,
    )
    print(r)
