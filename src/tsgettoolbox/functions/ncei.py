# -*- coding: utf-8 -*-
import datetime
import logging
import os
import time
from collections import OrderedDict

import mando
import pandas as pd

try:
    from mando.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter

from requests import Request
from requests.utils import unquote
from tstoolbox import tsutils

from tsgettoolbox import utils

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

    +------+----------------------------------------------------------+
    | Code | Description                                              |
    +======+==========================================================+
    | TMAX | Temperature MAX (degree C)                               |
    +------+----------------------------------------------------------+
    | TMIN | Temperature MIN (degree C)                               |
    +------+----------------------------------------------------------+
    | PRCP | PReCiPitation (mm)                                       |
    +------+----------------------------------------------------------+
    | SNOW | SNOWfall (mm)                                            |
    +------+----------------------------------------------------------+
    | SNWD | SNoW Depth (mm)                                          |
    +------+----------------------------------------------------------+

    Other possible data collected:

    +------+----------------------------------------------------------+
    | Code | Description                                              |
    +======+==========================================================+
    | ACMC | Average cloudiness midnight to midnight from 30-second   |
    |      | ceilometer data (percent)                                |
    +------+----------------------------------------------------------+
    | ACMH | Average cloudiness midnight to midnight from manual      |
    |      | observations (percent)                                   |
    +------+----------------------------------------------------------+
    | ACSC | Average cloudiness sunrise to sunset from 30-second      |
    |      | ceilometer data (percent)                                |
    +------+----------------------------------------------------------+
    | ACSH | Average cloudiness sunrise to sunset from manual         |
    |      | observations (percent)                                   |
    +------+----------------------------------------------------------+
    | AWDR | Average daily wind direction (degrees)                   |
    +------+----------------------------------------------------------+
    | AWND | Average daily wind speed (meters per second)             |
    +------+----------------------------------------------------------+
    | DAEV | Number of days included in the multiday evaporation      |
    |      | total (MDEV)                                             |
    +------+----------------------------------------------------------+
    | DAPR | Number of days included in the multiday precipitation    |
    |      | total (MDPR)                                             |
    +------+----------------------------------------------------------+
    | DASF | Number of days included in the multiday snowfall total   |
    |      | (MDSF)                                                   |
    +------+----------------------------------------------------------+
    | DATN | Number of days included in the multiday minimum          |
    |      | temperature (MDTN)                                       |
    +------+----------------------------------------------------------+
    | DATX | Number of days included in the multiday maximum          |
    |      | temperature (MDTX)                                       |
    +------+----------------------------------------------------------+
    | DAWM | Number of days included in the multiday wind movement    |
    |      | (MDWM)                                                   |
    +------+----------------------------------------------------------+
    | DWPR | Number of days with non-zero precipitation included in   |
    |      | multiday precipitation total (MDPR)                      |
    +------+----------------------------------------------------------+
    | EVAP | Evaporation of water from evaporation pan (mm)           |
    +------+----------------------------------------------------------+
    | FMTM | Time of fastest mile or fastest 1-minute wind (hours and |
    |      | minutes, i.e., HHMM)                                     |
    +------+----------------------------------------------------------+
    | FRGB | Base of frozen ground layer (cm)                         |
    +------+----------------------------------------------------------+
    | FRGT | Top of frozen ground layer (cm)                          |
    +------+----------------------------------------------------------+
    | FRTH | Thickness of frozen ground layer (cm)                    |
    +------+----------------------------------------------------------+
    | GAHT | Difference between river and gauge height (cm)           |
    +------+----------------------------------------------------------+
    | MDEV | Multiday evaporation total (use with DAEV)               |
    +------+----------------------------------------------------------+
    | MDPR | Multiday precipitation total (mm; use with               |
    |      | DAPR and DWPR, if available)                             |
    +------+----------------------------------------------------------+
    | MDSF | Multiday snowfall total                                  |
    +------+----------------------------------------------------------+
    | MDTN | Multiday minimum temperature (degrees C; use             |
    |      | with DATN)                                               |
    +------+----------------------------------------------------------+
    | MDTX | Multiday maximum temperature (degrees C; use             |
    |      | with DATX)                                               |
    +------+----------------------------------------------------------+
    | MDWM | Multiday wind movement (km)                              |
    +------+----------------------------------------------------------+
    | MNPN | Daily minimum temperature of water in an evaporation pan |
    |      | (degrees C)                                              |
    +------+----------------------------------------------------------+
    | MXPN | Daily maximum temperature of water in an evaporation pan |
    |      | (degrees C)                                              |
    +------+----------------------------------------------------------+
    | PGTM | Peak gust time (hours and minutes, i.e., HHMM)           |
    +------+----------------------------------------------------------+
    | PSUN | Daily percent of possible sunshine (percent)             |
    +------+----------------------------------------------------------+
    | TAVG | Average temperature (degrees C) [Note that               |
    |      | TAVG from source 'S' corresponds to an average for the   |
    |      | period ending at 2400 UTC rather than local midnight]    |
    +------+----------------------------------------------------------+
    | THIC | Thickness of ice on water (mm)                           |
    +------+----------------------------------------------------------+
    | TOBS | Temperature at the time of observation                   |
    |      | (degrees C)                                              |
    +------+----------------------------------------------------------+
    | TSUN | Daily total sunshine (minutes)                           |
    +------+----------------------------------------------------------+
    | WDF1 | Direction of fastest 1-minute wind (degrees)             |
    +------+----------------------------------------------------------+
    | WDF2 | Direction of fastest 2-minute wind (degrees)             |
    +------+----------------------------------------------------------+
    | WDF5 | Direction of fastest 5-second wind (degrees)             |
    +------+----------------------------------------------------------+
    | WDFG | Direction of peak wind gust (degrees)                    |
    +------+----------------------------------------------------------+
    | WDFI | Direction of highest instantaneous wind (degrees)        |
    +------+----------------------------------------------------------+
    | WDFM | Fastest mile wind direction (degrees)                    |
    +------+----------------------------------------------------------+
    | WDMV | 24-hour wind movement (km)                               |
    +------+----------------------------------------------------------+
    | WESD | Water equivalent of snow on the ground (mm)              |
    +------+----------------------------------------------------------+
    | WESF | Water equivalent of snowfall (mm)                        |
    +------+----------------------------------------------------------+
    | WSF1 | Fastest 1-minute wind speed (meters per                  |
    |      | second)                                                  |
    +------+----------------------------------------------------------+
    | WSF2 | Fastest 2-minute wind speed (meters per                  |
    |      | second)                                                  |
    +------+----------------------------------------------------------+
    | WSF5 | Fastest 5-second wind speed (meters per                  |
    |      | second)                                                  |
    +------+----------------------------------------------------------+
    | WSFG | Peak gust wind speed (meters per second)                 |
    +------+----------------------------------------------------------+
    | WSFI | Highest instantaneous wind speed (meters per             |
    |      | second)                                                  |
    +------+----------------------------------------------------------+
    | WSFM | Fastest mile wind speed (meters per second)              |
    +------+----------------------------------------------------------+

    SNXY and SXXY Table

    +-------+------------------------------------------------------------+
    | SNXY  | Minimum soil temperature (degrees C) where 'X'             |
    |       | corresponds to a code for ground cover and 'Y' corresponds |
    |       | to a code for soil depth.                                  |
    +=======+============================================================+
    |       | Ground cover codes include the following:                  |
    +-------+------------------------------------------------------------+
    | X = 0 | unknown                                                    |
    +-------+------------------------------------------------------------+
    | X = 1 | grass                                                      |
    +-------+------------------------------------------------------------+
    | X = 2 | fallow                                                     |
    +-------+------------------------------------------------------------+
    | X = 3 | bare ground                                                |
    +-------+------------------------------------------------------------+
    | X = 4 | brome grass                                                |
    +-------+------------------------------------------------------------+
    | X = 5 | sod                                                        |
    +-------+------------------------------------------------------------+
    | X = 6 | straw mulch                                                |
    +-------+------------------------------------------------------------+
    | X = 7 | grass muck                                                 |
    +-------+------------------------------------------------------------+
    | X = 8 | bare muck                                                  |
    +-------+------------------------------------------------------------+
    |       | Depth codes include the following:                         |
    +-------+------------------------------------------------------------+
    | Y = 1 | 5 cm                                                       |
    +-------+------------------------------------------------------------+
    | Y = 2 | 10 cm                                                      |
    +-------+------------------------------------------------------------+
    | Y = 3 | 20 cm                                                      |
    +-------+------------------------------------------------------------+
    | Y = 4 | 50 cm                                                      |
    +-------+------------------------------------------------------------+
    | Y = 5 | 100 cm                                                     |
    +-------+------------------------------------------------------------+
    | Y = 6 | 150 cm                                                     |
    +-------+------------------------------------------------------------+
    | Y = 7 | 180 cm                                                     |
    +-------+------------------------------------------------------------+
    | SXXY  | Maximum soil temperature (degrees C) where the             |
    |       | second 'X' corresponds to a code for ground cover and 'Y'  |
    |       | corresponds to a code for soil depth. See SNXY for ground  |
    |       | cover and depth codes.                                     |
    +-------+------------------------------------------------------------+

    WTXX and WVXX Table

    +------+-------------------------------------------------------+
    | XX   | Description                                           |
    +======+=======================================================+
    | 01   | Fog, ice fog, or freezing fog (may include heavy      |
    |      | fog)                                                  |
    +------+-------------------------------------------------------+
    | 02   | Heavy fog or heaving freezing fog (not always         |
    |      | distinguished from fog)                               |
    +------+-------------------------------------------------------+
    | 03   | Thunder                                               |
    +------+-------------------------------------------------------+
    | 04   | Ice pellets, sleet, snow pellets, or small hail       |
    +------+-------------------------------------------------------+
    | 05   | Hail (may include small hail)                         |
    +------+-------------------------------------------------------+
    | 06   | Glaze or rime                                         |
    +------+-------------------------------------------------------+
    | 07   | Dust, volcanic ash, blowing dust, blowing sand, or    |
    |      | blowing obstruction                                   |
    +------+-------------------------------------------------------+
    | 08   | Smoke or haze                                         |
    +------+-------------------------------------------------------+
    | 09   | Blowing or drifting snow                              |
    +------+-------------------------------------------------------+
    | 11   | High or damaging winds                                |
    +------+-------------------------------------------------------+
    | 12   | Blowing spray                                         |
    +------+-------------------------------------------------------+
    | 13   | Mist                                                  |
    +------+-------------------------------------------------------+
    | 14   | Drizzle                                               |
    +------+-------------------------------------------------------+
    | 15   | Freezing drizzle                                      |
    +------+-------------------------------------------------------+
    | 16   | Rain (may include freezing rain, drizzle, and         |
    |      | freezing drizzle)                                     |
    +------+-------------------------------------------------------+
    | 17   | Freezing rain                                         |
    +------+-------------------------------------------------------+
    | 18   | Snow, snow pellets, snow grains, or ice crystals      |
    +------+-------------------------------------------------------+
    | 19   | Unknown source of precipitation                       |
    +------+-------------------------------------------------------+
    | 21   | Ground fog                                            |
    +------+-------------------------------------------------------+
    | 22   | Ice fog or freezing fog                               |
    +------+-------------------------------------------------------+
    | WVXX | Weather in the Vicinity where XX has one of the       |
    |      | following values described above: 01, 03, 07, 18, and |
    |      | 20                                                    |
    +------+-------------------------------------------------------+""",
    "station": r"""station
        The station id. from the first column of
        ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt""",
}


@mando.command("ncei_ghcnd_ftp", formatter_class=HelpFormatter, doctype="numpy")
@tsutils.doc(tsutils.merge_dicts(tsutils.docstrings, ncei_ghcnd_docstrings))
def ncei_ghcnd_ftp_cli(station, start_date=None, end_date=None):
    r"""Download from the Global Historical Climatology Network - Daily.

    {info}

    Parameters
    ----------
    {station}
    {start_date}
    {end_date}
    """
    tsutils._printiso(ncei_ghcnd_ftp(station, start_date=start_date, end_date=end_date))


def ncei_ghcnd_ftp(station, start_date=None, end_date=None):
    r"""Download from the Global Historical Climatology Network - Daily."""
    station = station.split(":")[-1]
    params = {"station": station, "start_date": start_date, "end_date": end_date}

    url = r"ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/all"
    df = pd.read_fwf(
        url + "/" + params["station"] + ".dly",
        widths=[11, 4, 2, 4] + [5, 1, 1, 1] * 31,
    )
    newcols = ["station", "year", "month", "code"]
    for day in list(range(1, 32)):
        for col in ["", "m", "q", "s"]:
            newcols.append("{}{:02}".format(col, day))
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
        for j in range(1, 8):
            codes.append("SN{}{}".format(i, j))

    # SX*# = Maximum soil temperature (tenths of degrees C)
    #        where * corresponds to a code for ground cover
    #        and # corresponds to a code for soil depth.
    #        See SN*# for ground cover and depth codes.
    for i in range(9):
        for j in range(1, 8):
            codes.append("SX{}{}".format(i, j))

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
    codes.extend(["WT{:02}".format(i) for i in range(1, 23)])

    # WV** = Weather in the Vicinity where ** has one of the following values:
    #        01 = Fog, ice fog, or freezing fog (may include heavy fog)
    #        03 = Thunder
    #        07 = Ash, dust, sand, or other blowing obstruction
    #        18 = Snow or ice crystals
    #        20 = Rain or snow shower
    codes.extend(["WV{:02}".format(i) for i in [1, 3, 7, 18, 20]])

    for code in codes:
        tmpdf = df.loc[df["code"] == code, :]
        if len(tmpdf) == 0:
            continue
        tmpdf.set_index(["year", "month"], inplace=True)
        tmpdf = tmpdf.iloc[:, list(range(2, 126, 4))].stack()
        tmpdf.index = (
            tmpdf.index.get_level_values(0).astype(str).values
            + "-"
            + tmpdf.index.get_level_values(1).astype(str).values
            + "-"
            + tmpdf.index.get_level_values(2).astype(str).values
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

    # Some columns are 1/10 degree C.  The next section of code multiplies
    # those columns by 10.
    mcols = []
    for i in ndf.columns:
        if i in [
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
        ]:
            mcols.append(i)
    if mcols:
        ndf.loc[:, mcols] = ndf.loc[:, mcols] * 10.0

    ndf.index.name = "Datetime"
    ndf.replace(to_replace=[-9999], value=[None], inplace=True)
    ndf.rename(columns=add_units(ndf.columns), inplace=True)
    return ndf


def get_por(query_params, headers):
    # Get startdate and/or enddate information
    s = utils.requests_retry_session()
    ireq = Request(
        "GET",
        r"http://www.ncdc.noaa.gov/cdo-web/api/v2/stations/{}".format(
            query_params["stationid"]
        ),
        headers=headers,
    )
    prepped = ireq.prepare()
    dreq = s.send(prepped)
    dreq.raise_for_status()

    sdate = pd.to_datetime(dreq.json()["mindate"])
    edate = pd.to_datetime(dreq.json()["maxdate"])

    if "startdate" in query_params:
        tdate = tsutils.parsedate(query_params["startdate"])
        if tdate > sdate:
            sdate = tdate

    if "enddate" in query_params:
        tdate = tsutils.parsedate(query_params["enddate"])
        if tdate < edate:
            edate = tdate

    if sdate >= edate:
        raise ValueError(
            tsutils.error_wrapper(
                """
The startdate of {} is greater than, or equal to, the enddate of {}.
""".format(
                    sdate, edate
                )
            )
        )
    return sdate, edate


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
        "MNPN": "degC",
        "MXPN": "degC",
        "TSUN": "minute",
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
    ncols = {}
    for col in dfcols:
        for key, value in _units.items():
            if (key in col and "value_" in col) or key == col:
                ncols[col] = f"{col}:{value}"
    return ncols


def ncei_cdo_json_to_df(url, **query_params):
    delta = pd.Timedelta(days=360)
    if query_params["datasetid"] in ["ANNUAL", "GSOM", "GSOY", "GHCNDMS"]:
        delta = pd.Timedelta(days=3650)

    query_params["units"] = "metric"

    # Read in API key
    api_key = utils.read_api_key("ncei_cdo")
    headers = {"token": api_key}

    sdate = datetime.datetime(1900, 1, 1)
    td = datetime.datetime.today()
    edate = datetime.datetime(td.year, td.month, td.day) + pd.Timedelta(days=1)
    if "NORMAL_" in query_params["datasetid"]:
        # All the NORMAL_* datasets must have a startdate/endate of
        # 2010-01-01/2010-12-31
        sdate = datetime.datetime(2010, 1, 1)
        edate = datetime.datetime(2010, 12, 31)
        delta = pd.Timedelta(days=370)
    elif "stationid" in query_params:
        sdate, edate = get_por(query_params, headers)

    df = pd.DataFrame()

    query_params["limit"] = 1000

    testdate = sdate
    oldtestdate = sdate
    while testdate < edate:
        time.sleep(1)

        query_params["startdate"] = testdate.strftime("%Y-%m-%d")

        if testdate + delta > edate:
            query_params["enddate"] = edate.strftime("%Y-%m-%d")
        else:
            query_params["enddate"] = (testdate + delta).strftime("%Y-%m-%d")

        s = utils.requests_retry_session()
        ireq = Request("GET", url, params=query_params, headers=headers)
        prepped = ireq.prepare()
        prepped.url = unquote(prepped.url)
        if os.path.exists("debug_tsgettoolbox"):
            logging.warning(prepped.url)
        req = s.send(prepped)
        req.raise_for_status()

        try:
            tdf = pd.io.json.json_normalize(req.json()["results"])
        except KeyError:
            continue

        tdf.set_index("date", inplace=True)
        tdf.index = pd.to_datetime(tdf.index)

        testdate = tdf.index[-1]

        if testdate == oldtestdate:
            testdate = testdate + delta
        oldtestdate = testdate

        df = df.combine_first(tdf)

    if len(df) == 0:
        if "NORMAL_" in query_params["datasetid"]:
            raise ValueError(
                tsutils.error_wrapper(
                    """
No normalized statistics available for station {}
""".format(
                        query_params["stationid"]
                    )
                )
            )
        else:
            raise ValueError(
                tsutils.error_wrapper(
                    """
There should be data between {2} and {3}, however there is no data between {0} and {1}.
""".format(
                        query_params["startdate"],
                        query_params["enddate"],
                        pd.to_datetime(dreq.json()["mindate"]),
                        pd.to_datetime(dreq.json()["maxdate"]),
                    )
                )
            )

    df = df.drop("station", axis="columns")
    df = df.pivot_table(
        index=df.index,
        values=df.columns.drop("datatype"),
        columns="datatype",
        aggfunc="first",
    )

    df.index.name = "Datetime"

    df.columns = [
        "_".join(tuple(map(str, col))).rstrip("_") for col in df.columns.values
    ]

    return df.rename(columns=add_units(df.columns))


# 1763-01-01, 2016-11-05, Daily Summaries             , 1    , GHCND
@mando.command("ncei_ghcnd", formatter_class=HelpFormatter, doctype="numpy")
@tsutils.doc(tsutils.merge_dicts(tsutils.docstrings, ncei_ghcnd_docstrings))
def ncei_ghcnd_cli(stationid, datatypeid="", start_date="", end_date=""):
    r"""Download from the Global Historical Climatology Network - Daily.

    Requires registration and free API key.

    {info}

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
    {station}

    datatypeid
        [optional, defaults to returning all available data at that station]

        See the tables above for available datatypeid for the 'ghcnd'
        dataset.  If the datatypeid is not given defaults to getting all data
        available at that station for the time period requested.

    {start_date}

    {end_date}"""
    tsutils._printiso(
        ncei_ghcnd(
            stationid, datatypeid=datatypeid, start_date=start_date, end_date=end_date
        )
    )


def ncei_ghcnd(stationid, datatypeid="", start_date="", end_date=""):
    r"""Download from the Global Historical Climatology Network - Daily."""

    df = ncei_cdo_json_to_df(
        r"http://www.ncdc.noaa.gov/cdo-web/api/v2/data",
        startdate=start_date,
        enddate=end_date,
        datasetid="GHCND",
        stationid=stationid,
    )

    return df


@mando.command("ncei_gsod", formatter_class=HelpFormatter, doctype="numpy")
def ncei_gsod_cli(stationid, datatypeid="", startdate="", enddate=""):
    r"""Access ncei Global Summary of the Day.

    National Centers for Environmental Information (NCEI) Global Summary of the MONTH (GSOM)
    https://gis.ncdc.noaa.gov/all-records/catalog/search/resource/details.page
    Cite this dataset when used as a source: Lawrimore, Jay (2016). Global
    Summary of the Month, Version 1.0. [indicate subset used]. NOAA National
    Centers for Environmental Information. DOI:10.7289/V5QV3JJ5

    National Centers for Environmental Information (NCEI) Global Summary of the YEAR (GSOY)
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
    stationid
        This is the ncei
        station ID.

    database : str
        Either 'GSOM' for Global Summary of the Month, or 'GSOY' for Global
        Summary of the Year.

    datatypeid : str
        The following table lists the datatypes available for the 'ghcnd'
        dataset.  If the datatypeid is not given defaults to getting all data
        available at that station for the requested time period.

        +------+-------------------------------------------------------+
        | Code | Description                                           |
        +======+=======================================================+
        | TMAX | Monthly/Annual Maximum Temperature. Average of daily  |
        |      | maximum temperature given in Celsius or Fahrenheit    |
        |      | depending on user specification. Missing if more than |
        |      | 5 days within the month are missing or flagged or if  |
        |      | more than 3 consecutive values within the month are   |
        |      | missing or flagged.  DaysMissing: Flag indicating     |
        |      | number of days missing or flagged (from 1 to 5).      |
        +------+-------------------------------------------------------+
        | TMIN | Monthly/Annual Minimum Temperature. Average of daily  |
        |      | minimum temperature given in Celsius or Fahrenheit    |
        |      | depending on user specification. Missing if more than |
        |      | 5 days within the month are missing or flagged or if  |
        |      | more than 3 consecutive values within the month are   |
        |      | missing or flagged.  DaysMissing: Flag indicating     |
        |      | number of days missing or flagged (from 1 to 5).      |
        +------+-------------------------------------------------------+
        | TAVG | Average Monthly/Annual Temperature. Computed by       |
        |      | adding the unrounded monthly/annual maximum and       |
        |      | minimum temperatures and dividing by 2. Given in      |
        |      | Celsius or Fahrenheit depending on user               |
        |      | specification. Missing if more than 5 days within the |
        |      | month are missing or flagged or if more than 3        |
        |      | consecutive values within the month are missing or    |
        |      | flagged. DaysMissing: Flag indicating number of days  |
        |      | missing or flagged (from 1 to 5).                     |
        +------+-------------------------------------------------------+
        | EMXT | Extreme maximum temperature for month/year. Highest   |
        |      | daily maximum temperature for the month/year. Given   |
        |      | in Celsius or Fahrenheit depending on user            |
        |      | specification.                                        |
        +------+-------------------------------------------------------+
        | DYXT | Day of the EMXT for the month/year.                   |
        +------+-------------------------------------------------------+
        | EMNT | Extreme minimum temperature for month/year. Lowest    |
        |      | daily minimum temperature for the month/year. Given   |
        |      | in Celsius or Fahrenheit depending on user            |
        |      | specification.                                        |
        +------+-------------------------------------------------------+
        | DYXT | Day of the EMNT for the month/year.                   |
        +------+-------------------------------------------------------+
        | DX90 | Number of days with maximum temperature >= 90 degrees |
        |      | Fahrenheit/32.2 degrees Celsius.                      |
        +------+-------------------------------------------------------+
        | DX70 | Number of days with maximum temperature >= 70 degrees |
        |      | Fahrenheit/21.1 degrees Celsius.                      |
        +------+-------------------------------------------------------+
        | DX32 | Number of days with maximum temperature <= 32 degrees |
        |      | Fahrenheit/0 degrees Celsius.                         |
        +------+-------------------------------------------------------+
        | DT32 | Number of days with minimum temperature <= 32 degrees |
        |      | Fahrenheit/0 degrees Celsius.                         |
        +------+-------------------------------------------------------+
        | DT00 | Number of days with maximum temperature <= 0 degrees  |
        |      | Fahrenheit/-17.8 degrees Celsius.                     |
        +------+-------------------------------------------------------+
        | HTDD | Heating Degree Days. Computed when daily average      |
        |      | temperature is less than 65 degrees Fahrenheit/18.3   |
        |      | degrees Celsius. HDD = 65(F)/18.3(C) - mean daily     |
        |      | temperature. Each day is summed to produce a          |
        |      | monthly/annual total. Annual totals are computed      |
        |      | based on a July - June year in Northern Hemisphere    |
        |      | and January - December year in Southern Hemisphere.   |
        |      | Given in Celsius or Fahrenheit degrees depending on   |
        |      | user specification.                                   |
        +------+-------------------------------------------------------+
        | CLDD | Cooling Degree Days. Computed when daily average      |
        |      | temperature is more than 65 degrees Fahrenheit/18.3   |
        |      | degrees Celsius. CDD = mean daily temperature - 65    |
        |      | degrees Fahrenheit/18.3 degrees Celsius. Each day is  |
        |      | summed to produce a monthly/annual total. Annual      |
        |      | totals are computed based on a January - December     |
        |      | year in Northern Hemisphere and July - June year in   |
        |      | Southern Hemisphere. Given in Celsius or Fahrenheit   |
        |      | degrees depending on user specification.              |
        +------+-------------------------------------------------------+
        | PRCP | Total Monthly/Annual Precipitation. Given in inches   |
        |      | or millimeters depending on user specification.       |
        |      | Measurement Flags: T is used for trace amount, a is   |
        |      | used for any accumulation within a month/year that    |
        |      | includes missing days. If no days are missing, no     |
        |      | flag is used. Source Flag: Source flag from GHCN-     |
        |      | Daily (see separate documentation for GHCN-Daily).    |
        |      | Days Miss Flag: Number of days missing or flagged.    |
        +------+-------------------------------------------------------+
        | EMXP | Highest daily total of precipitation in the           |
        |      | month/year. Given in inches or millimeters depending  |
        |      | on user specification.                                |
        +------+-------------------------------------------------------+
        | DYXP | Day that EMXP for the month/year occurred.            |
        +------+-------------------------------------------------------+
        | DP01 | Number of days with >= 0.01 inch/0.254 millimeter in  |
        |      | the month/year.                                       |
        +------+-------------------------------------------------------+
        | DP05 | Number of days with >= 0.5 inch/12.7 millimeters in   |
        |      | the month/year.                                       |
        +------+-------------------------------------------------------+
        | DP10 | Number of days with >= 1.00 inch/25.4 millimeters in  |
        |      | the month/year.                                       |
        +------+-------------------------------------------------------+
        | SNOW | Total Monthly/Annual Snowfall. Given in inches or     |
        |      | millimeters depending on user specification.          |
        |      | Measurement Flags: T is used for trace amount, a is   |
        |      | used for any accumulation within a month/year that    |
        |      | includes missing days. If no days are missing, no     |
        |      | flag is used. Source Flag: Source flag from GHCN-     |
        |      | Daily (see separate documentation for GHCN-Daily).    |
        |      | Days Miss Flag: Number of days missing or flagged.    |
        +------+-------------------------------------------------------+
        | EMSN | Highest daily snowfall in the month/year. Given in    |
        |      | inches or millimeters depending on user               |
        |      | specification.                                        |
        +------+-------------------------------------------------------+
        | DYSN | Day EMSN for the month/year occurred.                 |
        +------+-------------------------------------------------------+
        | DSNW | Number of days with snowfall >= 1 inch/25             |
        |      | millimeters.                                          |
        +------+-------------------------------------------------------+
        | DSND | Number of days with snow depth >= 1 inch/25           |
        |      | millimeters.                                          |
        +------+-------------------------------------------------------+
        | EMSD | Highest daily snow depth in the month/year. Given in  |
        |      | inches or millimeters depending on user               |
        |      | specification.                                        |
        +------+-------------------------------------------------------+
        | DYSD | Day EMSD for the month/year occurred.                 |
        +------+-------------------------------------------------------+
        | EVAP | Total Monthly/Annual Evaporation. Given in inches or  |
        |      | millimeters depending on user specification.          |
        |      | Measurement Flags: T is used for trace amount, a is   |
        |      | used for any accumulation within a month/year that    |
        |      | includes missing days. If no days are missing, no     |
        |      | flag is used. Source Flag: Source flag from GHCN-     |
        |      | Daily (see separate documentation for GHCN-Daily).    |
        |      | Days Miss Flag: Number of days missing or flagged.    |
        +------+-------------------------------------------------------+
        | MNPN | Monthly/Annual Mean Minimum Temperature of            |
        |      | evaporation pan water. Given in Celsius or Fahrenheit |
        |      | depending on user specification. Missing if more than |
        |      | 5 days within the month are missing or flagged or if  |
        |      | more than 3 consecutive values within the month are   |
        |      | missing or flagged. DaysMissing: Flag indicating      |
        |      | number of days missing or flagged (from 1 to 5).      |
        +------+-------------------------------------------------------+
        | MXPN | Monthly/Annual Mean Maximum Temperature of            |
        |      | evaporation pan water. Given in Celsius or Fahrenheit |
        |      | depending on user specification. Missing if more than |
        |      | 5 days within the month are missing or flagged or if  |
        |      | more than 3 consecutive values within the month are   |
        |      | missing or flagged. DaysMissing: Flag indicating      |
        |      | number of days missing or flagged (from 1 to 5).      |
        +------+-------------------------------------------------------+
        | WDMV | Total Monthly/Annual Wind Movement over evaporation   |
        |      | pan. Given in miles or kilometers depending on user   |
        |      | specification. Days Miss Flag: Number of days missing |
        |      | or flagged.                                           |
        +------+-------------------------------------------------------+
        | TSUN | Daily total sunshine in minutes. Days Miss Flag:      |
        |      | Number of days missing or flagged.                    |
        +------+-------------------------------------------------------+
        | PSUN | Monthly/Annual Average of the daily percents of       |
        |      | possible sunshine. Days Miss Flag: Number of days     |
        |      | missing or flagged.                                   |
        +------+-------------------------------------------------------+
        | AWND | Monthly/Annual Average Wind Speed. Given in miles per |
        |      | hour or meters per second depending on user           |
        |      | specification. Missing if more than 5 days within the |
        |      | month are missing or flagged or if more than 3        |
        |      | consecutive values within the month are missing or    |
        |      | flagged. DaysMissing: Flag indicating number of days  |
        |      | missing or flagged (from 1 to 5).                     |
        +------+-------------------------------------------------------+
        | WSFM | Maximum Wind Speed/Fastest Mile. Maximum wind speed   |
        |      | for the month/year reported as the fastest mile.      |
        |      | Given in miles per hour or meters per second          |
        |      | depending on user specification. Missing if more than |
        |      | 5 days within the month are missing or flagged or if  |
        |      | more than 3 consecutive values within the month are   |
        |      | missing or flagged. DaysMissing: Flag indicating      |
        |      | number of days missing or flagged (from 1 to 5).      |
        +------+-------------------------------------------------------+
        | WDFM | Wind Direction for Maximum Wind Speed/Fastest Mile    |
        |      | (WSFM). Given in 360-degree compass point directions  |
        |      | (e.g. 360 = north, 180 = south, etc.).                |
        +------+-------------------------------------------------------+
        | WSF2 | Maximum Wind Speed/Fastest 2-minute. Maximum wind     |
        |      | speed for the month/year reported as the fastest      |
        |      | 2-minute. Given in miles per hour or meters per       |
        |      | second depending on user specification.  Missing if   |
        |      | more than 5 days within the month are missing or      |
        |      | flagged or if more than 3 consecutive values within   |
        |      | the month are missing or flagged. DaysMissing: Flag   |
        |      | indicating number of days missing or flagged (from 1  |
        |      | to 5).                                                |
        +------+-------------------------------------------------------+
        | WDF2 | Wind Direction for Maximum Wind Speed/Fastest         |
        |      | 2-Minute (WSF2). Given in 360-degree compass point    |
        |      | directions (e.g. 360 = north, 180 = south, etc.).     |
        +------+-------------------------------------------------------+
        | WSF1 | Maximum Wind Speed/Fastest 1-minute. Maximum wind     |
        |      | speed for the month/year reported as the fastest      |
        |      | 1-minute. Given in miles per hour or meters per       |
        |      | second depending on user specification.  Missing if   |
        |      | more than 5 days within the month are missing or      |
        |      | flagged or if more than 3 consecutive values within   |
        |      | the month are missing or flagged. DaysMissing: Flag   |
        |      | indicating number of days missing or flagged (from 1  |
        |      | to 5).                                                |
        +------+-------------------------------------------------------+
        | WDF1 | Wind Direction for Maximum Wind Speed/Fastest         |
        |      | 1-Minute (WSF1). Given in 360-degree compass point    |
        |      | directions (e.g. 360 = north, 180 = south, etc.).     |
        |      | Missing if more than 5 days within the month are      |
        |      | missing or flagged or if more than 3 consecutive      |
        |      | values within the month are missing or flagged.       |
        |      | DaysMissing: Flag indicating number of days missing   |
        |      | or flagged (from 1 to 5).                             |
        +------+-------------------------------------------------------+
        | WSFG | Peak Wind Gust Speed. Maximum wind gust for the       |
        |      | month/year. Given in miles per hour or second         |
        |      | depending on user specification. Missing if more than |
        |      | 5 days within the month are missing or flagged or if  |
        |      | more than 3 consecutive values within the month are   |
        |      | missing or flagged. DaysMissing: Flag indicating      |
        |      | number of days missing or flagged (from 1 to 5).      |
        +------+-------------------------------------------------------+
        | WDFG | Wind Direction for Peak Wind Gust Speed (WSFG). Given |
        |      | in 360-degree compass point directions (e.g. 360 =    |
        |      | north, 180 = south, etc.). Missing if more than 5     |
        |      | days within the month are missing or flagged or if    |
        |      | more than 3 consecutive values within the month are   |
        |      | missing or flagged. DaysMissing: Flag indicating      |
        |      | number of days missing or flagged (from 1 to 5).      |
        +------+-------------------------------------------------------+
        | WSF5 | Peak Wind Gust Speed - Fastest 5-second wind. Maximum |
        |      | wind gust for the month/year. Given in miles per hour |
        |      | or second depending on user specification. Missing if |
        |      | more than 5 days within the month are missing or      |
        |      | flagged or if more than 3 consecutive values within   |
        |      | the month are missing or flagged. DaysMissing: Flag   |
        |      | indicating number of days missing or flagged (from 1  |
        |      | to 5).                                                |
        +------+-------------------------------------------------------+
        | WDF5 | Wind Direction for Peak Wind Gust Speed - Fastest     |
        |      | 5-second (WSF5). Given in 360-degree compass point    |
        |      | directions (e.g. 360 = north, 180 = south, etc.).     |
        |      | Missing if more than 5 days within the month are      |
        |      | missing or flagged or if more than 3 consecutive      |
        |      | values within the month are missing or flagged.       |
        |      | DaysMissing: Flag indicating number of days missing   |
        |      | or flagged (from 1 to 5).                             |
        +------+-------------------------------------------------------+
        | WSF3 | Peak Wind Gust Speed - Fastest 3-second wind. Maximum |
        |      | wind gust for the month/year. Given in miles per hour |
        |      | or second depending on user specification. Missing if |
        |      | more than 5 days within the month are missing or      |
        |      | flagged or if more than 3 consecutive values within   |
        |      | the month are missing or flagged. DaysMissing: Flag   |
        |      | indicating number of days missing or flagged (from 1  |
        |      | to 5).                                                |
        +------+-------------------------------------------------------+
        | WDF3 | Wind Direction for Peak Wind Gust Speed - Fastest     |
        |      | 5-second (WSF3). Given in 360-degree compass point    |
        |      | directions (e.g. 360 = north, 180 = south, etc.).     |
        |      | Missing if more than 5 days within the month are      |
        |      | missing or flagged or if more than 3 consecutive      |
        |      | values within the month are missing or flagged.       |
        |      | DaysMissing: Flag indicating number of days missing   |
        |      | or flagged (from 1 to 5).                             |
        +------+-------------------------------------------------------+
        | MXyz | Monthly/Annual Mean of daily maximum soil temperature |
        |      | given in Celsius or Fahrenheit depending on user      |
        |      | specification. Missing if more than 5 days within the |
        |      | month are missing or flagged or if more than 3        |
        |      | consecutive values within the month are missing or    |
        |      | flagged. DaysMissing: Flag indicating number of days  |
        |      | missing or flagged (from 1 to 5).                     |
        |      |                                                       |
        |      | "y" values for MXyz, MNyz, HXyz, HNyz, LXyz, and LNyz |
        |      | 1=grass                                               |
        |      | 2=fallow                                              |
        |      | 3=bare ground                                         |
        |      | 4=brome grass                                         |
        |      | 5=sod                                                 |
        |      | 6=straw mulch                                         |
        |      | 7=grass muck                                          |
        |      | 8=bare muck                                           |
        |      | 0=unknown                                             |
        |      |                                                       |
        |      | "z" values for HXyz, HNyz, LXyz, and LNyz:            |
        |      | 1= 2 inches or 5 centimeters depth                    |
        |      | 2= 4 inches or 10 centimeters depth                   |
        |      | 3= 8 inches or 20 centimeters depth                   |
        |      | 4= 20 inches or 50 centimeters depth                  |
        |      | 5= 40 inches or 100 centimeters depth                 |
        |      | 6= 60 inches or 150 centimeters depth                 |
        |      | 7= 72 inches or 180 centimeters depth                 |
        |      | other=unknown                                         |
        +------+-------------------------------------------------------+
        | MNyz | Monthly/Annual Mean of daily minimum soil temperature |
        |      | given in Celsius or Fahrenheit depending on user      |
        |      | specification. Missing if more than 5 days within the |
        |      | month are missing or flagged or if more than 3        |
        |      | consecutive values within the month are missing or    |
        |      | flagged. DaysMissing: Flag indicating number of days  |
        |      | missing or flagged (from 1 to 5).                     |
        |      |                                                       |
        |      | See description of flags in MXyz.                     |
        +------+-------------------------------------------------------+
        | HXyz | Highest maximum soil temperature for the month/year   |
        |      | given in Celsius or Fahrenheit depending on user      |
        |      | specification. Missing if more than 5 days within the |
        |      | month are missing or flagged or if more than 3        |
        |      | consecutive values within the month are missing or    |
        |      | flagged. DaysMissing: Flag indicating number of days  |
        |      | missing or flagged (from 1 to 5).                     |
        |      |                                                       |
        |      | See description of flags in MXyz.                     |
        +------+-------------------------------------------------------+
        | HNyz | Highest minimum soil temperature for the month/year   |
        |      | given in Celsius or Fahrenheit depending on user      |
        |      | specification. Missing if more than 5 days within the |
        |      | month are missing or flagged or if more than 3        |
        |      | consecutive values within the month are missing or    |
        |      | flagged. DaysMissing: Flag indicating number of days  |
        |      | missing or flagged (from 1 to 5).                     |
        |      |                                                       |
        |      | See description of flags in MXyz.                     |
        +------+-------------------------------------------------------+
        | LXyz | Lowest maximum soil temperature for the month/year    |
        |      | given in Celsius or Fahrenheit depending on user      |
        |      | specification. Missing if more than 5 days within the |
        |      | month are missing or flagged or if more than 3        |
        |      | consecutive values within the month are missing or    |
        |      | flagged. DaysMissing: Flag indicating number of days  |
        |      | missing or flagged (from 1 to 5).                     |
        |      |                                                       |
        |      | See description of flags in MXyz.                     |
        +------+-------------------------------------------------------+
        | LNyz | Lowest minimum soil temperature for the month/year    |
        |      | given in Celsius or Fahrenheit depending on user      |
        |      | specification. Missing if more than 5 days within the |
        |      | month are missing or flagged or if more than 3        |
        |      | consecutive values within the month are missing or    |
        |      | flagged. DaysMissing: Flag indicating number of days  |
        |      | missing or flagged (from 1 to 5).                     |
        |      |                                                       |
        |      | See description of flags in MXyz.                     |
        +------+-------------------------------------------------------+
        | HDSD | Heating Degree Days (season-to-date). Running total   |
        |      | of monthly heating degree days through the end of the |
        |      | most recent month. Each month is summed to produce a  |
        |      | season-to-date total. Season starts in July in        |
        |      | Northern Hemisphere and January in Southern           |
        |      | Hemisphere. Given in Celsius or Fahrenheit degrees    |
        |      | depending on user specification.                      |
        +------+-------------------------------------------------------+
        | CDSD | Cooling Degree Days (season-to-date). Running total   |
        |      | of monthly cooling degree days through the end of the |
        |      | most recent month. Each month is summed to produce a  |
        |      | season-to-date total. Season starts in January in     |
        |      | Northern Hemisphere and July in Southern Hemisphere.  |
        |      | Given in Celsius or Fahrenheit degrees depending on   |
        |      | user specification.                                   |
        +------+-------------------------------------------------------+
        | FZFx | (x= 0-9) First/Last Freeze Days. Annual element only. |
        |      | Years begins on August 1. Missing if more than 5 days |
        |      | within the month are missing or flagged or if more    |
        |      | than 3 consecutive values within the month are        |
        |      | missing or flagged. DaysMissing: Flag indicating      |
        |      | number of days missing or flagged (from 1 to 5).      |
        |      | Given in format tttt.tyyyymmdds where tttt.t is       |
        |      | temperature in degrees Fahrenheit or Celsius          |
        |      | depending on user specification, yyyy is the year, mm |
        |      | is the month, dd is the day of the month and s is a   |
        |      | source flag.                                          |
        |      |                                                       |
        |      | "x" values for FZFx                                   |
        |      | 0 = first minimum temperature <= 32 degrees           |
        |      | Fahrenheit/0 degrees Celsius                          |
        |      | 1 = first minimum temperature <= 28 degrees           |
        |      | Fahrenheit/-2.2 degrees Celsius                       |
        |      | 2 = first minimum temperature <= 24 degrees           |
        |      | Fahrenheit/-4.4 degrees Celsius                       |
        |      | 3 = first minimum temperature <= 20 degrees           |
        |      | Fahrenheit/-6.7 degrees Celsius                       |
        |      | 4 = first minimum temperature <= 16 degrees           |
        |      | Fahrenheit/-8.9 degrees Celsius                       |
        |      | 5 = last minimum temperature <= 32 degrees            |
        |      | Fahrenheit/0 degrees Celsius                          |
        |      | 6 = last minimum temperature <= 28 degrees            |
        |      | Fahrenheit/-2.2 degrees Celsius                       |
        |      | 7 = last minimum temperature <= 24 degrees            |
        |      | Fahrenheit/-4.4 degrees Celsius                       |
        |      | 8 = last minimum temperature <= 20 degrees            |
        |      | Fahrenheit/-6.7 degrees Celsius                       |
        |      | 9 = last minimum temperature <= 16 degrees            |
        |      | Fahrenheit/-8.9 degrees Celsius                       |
        +------+-------------------------------------------------------+

    startdate
        Start date in ISO8601 format.

    enddate
        End date in ISO8601 format."""
    tsutils._printiso(
        ncei_gsod(
            stationid,
            datatypeid=datatypeid,
            startdate=startdate,
            enddate=enddate,
        )
    )


# https://www.ncei.noaa.gov/data/global-summary-of-the-day/access/
# GSOD
def ncei_gsod(stationid, datatypeid="", startdate="", enddate=""):
    r"""Access NCEI Global Summary of the Day."""
    # Read in API key
    api_key = utils.read_api_key("ncei_cdo")
    headers = {"token": api_key}

    sdate, edate = get_por(
        {"stationid": stationid, "startdate": startdate, "enddate": enddate}, headers
    )
    df = pd.DataFrame()
    for year in range(sdate.year, edate.year + 1):
        ndf = pd.read_csv(
            f"https://www.ncei.noaa.gov/data/global-summary-of-the-day/access/{year}/{stationid}.csv"
        )
        df = df.join(ndf)
    return df.rename(columns=add_units(df.columns))


# 1763-01-01, 2016-09-01, Global Summary of the Month , 1    , GSOM
@mando.command("ncei_gsom", formatter_class=HelpFormatter, doctype="numpy")
def ncei_gsom_cli(stationid, datatypeid="", startdate="", enddate=""):
    r"""Access NCEI Global Summary of Month.

    National Centers for Environmental Information (NCEI) Global Summary of the MONTH (GSOM)
    https://gis.ncdc.noaa.gov/all-records/catalog/search/resource/details.page
    Cite this dataset when used as a source: Lawrimore, Jay (2016). Global
    Summary of the Month, Version 1.0. [indicate subset used]. NOAA National
    Centers for Environmental Information. DOI:10.7289/V5QV3JJ5

    National Centers for Environmental Information (NCEI) Global Summary of the YEAR (GSOY)
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
    stationid
        This is the ncei
        station ID.

    datatypeid : str
        The following table lists the datatypes available for the 'ghcnd'
        dataset.  If the datatypeid is not given defaults to getting all data
        available at that station for the requested time period.

        +------+-------------------------------------------------------+
        | Code | Description                                           |
        +======+=======================================================+
        | TMAX | Monthly/Annual Maximum Temperature. Average of daily  |
        |      | maximum temperature given in Celsius or Fahrenheit    |
        |      | depending on user specification. Missing if more than |
        |      | 5 days within the month are missing or flagged or if  |
        |      | more than 3 consecutive values within the month are   |
        |      | missing or flagged.  DaysMissing: Flag indicating     |
        |      | number of days missing or flagged (from 1 to 5).      |
        +------+-------------------------------------------------------+
        | TMIN | Monthly/Annual Minimum Temperature. Average of daily  |
        |      | minimum temperature given in Celsius or Fahrenheit    |
        |      | depending on user specification. Missing if more than |
        |      | 5 days within the month are missing or flagged or if  |
        |      | more than 3 consecutive values within the month are   |
        |      | missing or flagged.  DaysMissing: Flag indicating     |
        |      | number of days missing or flagged (from 1 to 5).      |
        +------+-------------------------------------------------------+
        | TAVG | Average Monthly/Annual Temperature. Computed by       |
        |      | adding the unrounded monthly/annual maximum and       |
        |      | minimum temperatures and dividing by 2. Given in      |
        |      | Celsius or Fahrenheit depending on user               |
        |      | specification. Missing if more than 5 days within the |
        |      | month are missing or flagged or if more than 3        |
        |      | consecutive values within the month are missing or    |
        |      | flagged. DaysMissing: Flag indicating number of days  |
        |      | missing or flagged (from 1 to 5).                     |
        +------+-------------------------------------------------------+
        | EMXT | Extreme maximum temperature for month/year. Highest   |
        |      | daily maximum temperature for the month/year. Given   |
        |      | in Celsius or Fahrenheit depending on user            |
        |      | specification.                                        |
        +------+-------------------------------------------------------+
        | DYXT | Day of the EMXT for the month/year.                   |
        +------+-------------------------------------------------------+
        | EMNT | Extreme minimum temperature for month/year. Lowest    |
        |      | daily minimum temperature for the month/year. Given   |
        |      | in Celsius or Fahrenheit depending on user            |
        |      | specification.                                        |
        +------+-------------------------------------------------------+
        | DYXT | Day of the EMNT for the month/year.                   |
        +------+-------------------------------------------------------+
        | DX90 | Number of days with maximum temperature >= 90 degrees |
        |      | Fahrenheit/32.2 degrees Celsius.                      |
        +------+-------------------------------------------------------+
        | DX70 | Number of days with maximum temperature >= 70 degrees |
        |      | Fahrenheit/21.1 degrees Celsius.                      |
        +------+-------------------------------------------------------+
        | DX32 | Number of days with maximum temperature <= 32 degrees |
        |      | Fahrenheit/0 degrees Celsius.                         |
        +------+-------------------------------------------------------+
        | DT32 | Number of days with minimum temperature <= 32 degrees |
        |      | Fahrenheit/0 degrees Celsius.                         |
        +------+-------------------------------------------------------+
        | DT00 | Number of days with maximum temperature <= 0 degrees  |
        |      | Fahrenheit/-17.8 degrees Celsius.                     |
        +------+-------------------------------------------------------+
        | HTDD | Heating Degree Days. Computed when daily average      |
        |      | temperature is less than 65 degrees Fahrenheit/18.3   |
        |      | degrees Celsius. HDD = 65(F)/18.3(C) - mean daily     |
        |      | temperature. Each day is summed to produce a          |
        |      | monthly/annual total. Annual totals are computed      |
        |      | based on a July - June year in Northern Hemisphere    |
        |      | and January - December year in Southern Hemisphere.   |
        |      | Given in Celsius or Fahrenheit degrees depending on   |
        |      | user specification.                                   |
        +------+-------------------------------------------------------+
        | CLDD | Cooling Degree Days. Computed when daily average      |
        |      | temperature is more than 65 degrees Fahrenheit/18.3   |
        |      | degrees Celsius. CDD = mean daily temperature - 65    |
        |      | degrees Fahrenheit/18.3 degrees Celsius. Each day is  |
        |      | summed to produce a monthly/annual total. Annual      |
        |      | totals are computed based on a January - December     |
        |      | year in Northern Hemisphere and July - June year in   |
        |      | Southern Hemisphere. Given in Celsius or Fahrenheit   |
        |      | degrees depending on user specification.              |
        +------+-------------------------------------------------------+
        | PRCP | Total Monthly/Annual Precipitation. Given in inches   |
        |      | or millimeters depending on user specification.       |
        |      | Measurement Flags: T is used for trace amount, a is   |
        |      | used for any accumulation within a month/year that    |
        |      | includes missing days. If no days are missing, no     |
        |      | flag is used. Source Flag: Source flag from GHCN-     |
        |      | Daily (see separate documentation for GHCN-Daily).    |
        |      | Days Miss Flag: Number of days missing or flagged.    |
        +------+-------------------------------------------------------+
        | EMXP | Highest daily total of precipitation in the           |
        |      | month/year. Given in inches or millimeters depending  |
        |      | on user specification.                                |
        +------+-------------------------------------------------------+
        | DYXP | Day that EMXP for the month/year occurred.            |
        +------+-------------------------------------------------------+
        | DP01 | Number of days with >= 0.01 inch/0.254 millimeter in  |
        |      | the month/year.                                       |
        +------+-------------------------------------------------------+
        | DP05 | Number of days with >= 0.5 inch/12.7 millimeters in   |
        |      | the month/year.                                       |
        +------+-------------------------------------------------------+
        | DP10 | Number of days with >= 1.00 inch/25.4 millimeters in  |
        |      | the month/year.                                       |
        +------+-------------------------------------------------------+
        | SNOW | Total Monthly/Annual Snowfall. Given in inches or     |
        |      | millimeters depending on user specification.          |
        |      | Measurement Flags: T is used for trace amount, a is   |
        |      | used for any accumulation within a month/year that    |
        |      | includes missing days. If no days are missing, no     |
        |      | flag is used. Source Flag: Source flag from GHCN-     |
        |      | Daily (see separate documentation for GHCN-Daily).    |
        |      | Days Miss Flag: Number of days missing or flagged.    |
        +------+-------------------------------------------------------+
        | EMSN | Highest daily snowfall in the month/year. Given in    |
        |      | inches or millimeters depending on user               |
        |      | specification.                                        |
        +------+-------------------------------------------------------+
        | DYSN | Day EMSN for the month/year occurred.                 |
        +------+-------------------------------------------------------+
        | DSNW | Number of days with snowfall >= 1 inch/25             |
        |      | millimeters.                                          |
        +------+-------------------------------------------------------+
        | DSND | Number of days with snow depth >= 1 inch/25           |
        |      | millimeters.                                          |
        +------+-------------------------------------------------------+
        | EMSD | Highest daily snow depth in the month/year. Given in  |
        |      | inches or millimeters depending on user               |
        |      | specification.                                        |
        +------+-------------------------------------------------------+
        | DYSD | Day EMSD for the month/year occurred.                 |
        +------+-------------------------------------------------------+
        | EVAP | Total Monthly/Annual Evaporation. Given in inches or  |
        |      | millimeters depending on user specification.          |
        |      | Measurement Flags: T is used for trace amount, a is   |
        |      | used for any accumulation within a month/year that    |
        |      | includes missing days. If no days are missing, no     |
        |      | flag is used. Source Flag: Source flag from GHCN-     |
        |      | Daily (see separate documentation for GHCN-Daily).    |
        |      | Days Miss Flag: Number of days missing or flagged.    |
        +------+-------------------------------------------------------+
        | MNPN | Monthly/Annual Mean Minimum Temperature of            |
        |      | evaporation pan water. Given in Celsius or Fahrenheit |
        |      | depending on user specification. Missing if more than |
        |      | 5 days within the month are missing or flagged or if  |
        |      | more than 3 consecutive values within the month are   |
        |      | missing or flagged. DaysMissing: Flag indicating      |
        |      | number of days missing or flagged (from 1 to 5).      |
        +------+-------------------------------------------------------+
        | MXPN | Monthly/Annual Mean Maximum Temperature of            |
        |      | evaporation pan water. Given in Celsius or Fahrenheit |
        |      | depending on user specification. Missing if more than |
        |      | 5 days within the month are missing or flagged or if  |
        |      | more than 3 consecutive values within the month are   |
        |      | missing or flagged. DaysMissing: Flag indicating      |
        |      | number of days missing or flagged (from 1 to 5).      |
        +------+-------------------------------------------------------+
        | WDMV | Total Monthly/Annual Wind Movement over evaporation   |
        |      | pan. Given in miles or kilometers depending on user   |
        |      | specification. Days Miss Flag: Number of days missing |
        |      | or flagged.                                           |
        +------+-------------------------------------------------------+
        | TSUN | Daily total sunshine in minutes. Days Miss Flag:      |
        |      | Number of days missing or flagged.                    |
        +------+-------------------------------------------------------+
        | PSUN | Monthly/Annual Average of the daily percents of       |
        |      | possible sunshine. Days Miss Flag: Number of days     |
        |      | missing or flagged.                                   |
        +------+-------------------------------------------------------+
        | AWND | Monthly/Annual Average Wind Speed. Given in miles per |
        |      | hour or meters per second depending on user           |
        |      | specification. Missing if more than 5 days within the |
        |      | month are missing or flagged or if more than 3        |
        |      | consecutive values within the month are missing or    |
        |      | flagged. DaysMissing: Flag indicating number of days  |
        |      | missing or flagged (from 1 to 5).                     |
        +------+-------------------------------------------------------+
        | WSFM | Maximum Wind Speed/Fastest Mile. Maximum wind speed   |
        |      | for the month/year reported as the fastest mile.      |
        |      | Given in miles per hour or meters per second          |
        |      | depending on user specification. Missing if more than |
        |      | 5 days within the month are missing or flagged or if  |
        |      | more than 3 consecutive values within the month are   |
        |      | missing or flagged. DaysMissing: Flag indicating      |
        |      | number of days missing or flagged (from 1 to 5).      |
        +------+-------------------------------------------------------+
        | WDFM | Wind Direction for Maximum Wind Speed/Fastest Mile    |
        |      | (WSFM). Given in 360-degree compass point directions  |
        |      | (e.g. 360 = north, 180 = south, etc.).                |
        +------+-------------------------------------------------------+
        | WSF2 | Maximum Wind Speed/Fastest 2-minute. Maximum wind     |
        |      | speed for the month/year reported as the fastest      |
        |      | 2-minute. Given in miles per hour or meters per       |
        |      | second depending on user specification.  Missing if   |
        |      | more than 5 days within the month are missing or      |
        |      | flagged or if more than 3 consecutive values within   |
        |      | the month are missing or flagged. DaysMissing: Flag   |
        |      | indicating number of days missing or flagged (from 1  |
        |      | to 5).                                                |
        +------+-------------------------------------------------------+
        | WDF2 | Wind Direction for Maximum Wind Speed/Fastest         |
        |      | 2-Minute (WSF2). Given in 360-degree compass point    |
        |      | directions (e.g. 360 = north, 180 = south, etc.).     |
        +------+-------------------------------------------------------+
        | WSF1 | Maximum Wind Speed/Fastest 1-minute. Maximum wind     |
        |      | speed for the month/year reported as the fastest      |
        |      | 1-minute. Given in miles per hour or meters per       |
        |      | second depending on user specification.  Missing if   |
        |      | more than 5 days within the month are missing or      |
        |      | flagged or if more than 3 consecutive values within   |
        |      | the month are missing or flagged. DaysMissing: Flag   |
        |      | indicating number of days missing or flagged (from 1  |
        |      | to 5).                                                |
        +------+-------------------------------------------------------+
        | WDF1 | Wind Direction for Maximum Wind Speed/Fastest         |
        |      | 1-Minute (WSF1). Given in 360-degree compass point    |
        |      | directions (e.g. 360 = north, 180 = south, etc.).     |
        |      | Missing if more than 5 days within the month are      |
        |      | missing or flagged or if more than 3 consecutive      |
        |      | values within the month are missing or flagged.       |
        |      | DaysMissing: Flag indicating number of days missing   |
        |      | or flagged (from 1 to 5).                             |
        +------+-------------------------------------------------------+
        | WSFG | Peak Wind Gust Speed. Maximum wind gust for the       |
        |      | month/year. Given in miles per hour or second         |
        |      | depending on user specification. Missing if more than |
        |      | 5 days within the month are missing or flagged or if  |
        |      | more than 3 consecutive values within the month are   |
        |      | missing or flagged. DaysMissing: Flag indicating      |
        |      | number of days missing or flagged (from 1 to 5).      |
        +------+-------------------------------------------------------+
        | WDFG | Wind Direction for Peak Wind Gust Speed (WSFG). Given |
        |      | in 360-degree compass point directions (e.g. 360 =    |
        |      | north, 180 = south, etc.). Missing if more than 5     |
        |      | days within the month are missing or flagged or if    |
        |      | more than 3 consecutive values within the month are   |
        |      | missing or flagged. DaysMissing: Flag indicating      |
        |      | number of days missing or flagged (from 1 to 5).      |
        +------+-------------------------------------------------------+
        | WSF5 | Peak Wind Gust Speed - Fastest 5-second wind. Maximum |
        |      | wind gust for the month/year. Given in miles per hour |
        |      | or second depending on user specification. Missing if |
        |      | more than 5 days within the month are missing or      |
        |      | flagged or if more than 3 consecutive values within   |
        |      | the month are missing or flagged. DaysMissing: Flag   |
        |      | indicating number of days missing or flagged (from 1  |
        |      | to 5).                                                |
        +------+-------------------------------------------------------+
        | WDF5 | Wind Direction for Peak Wind Gust Speed - Fastest     |
        |      | 5-second (WSF5). Given in 360-degree compass point    |
        |      | directions (e.g. 360 = north, 180 = south, etc.).     |
        |      | Missing if more than 5 days within the month are      |
        |      | missing or flagged or if more than 3 consecutive      |
        |      | values within the month are missing or flagged.       |
        |      | DaysMissing: Flag indicating number of days missing   |
        |      | or flagged (from 1 to 5).                             |
        +------+-------------------------------------------------------+
        | WSF3 | Peak Wind Gust Speed - Fastest 3-second wind. Maximum |
        |      | wind gust for the month/year. Given in miles per hour |
        |      | or second depending on user specification. Missing if |
        |      | more than 5 days within the month are missing or      |
        |      | flagged or if more than 3 consecutive values within   |
        |      | the month are missing or flagged. DaysMissing: Flag   |
        |      | indicating number of days missing or flagged (from 1  |
        |      | to 5).                                                |
        +------+-------------------------------------------------------+
        | WDF3 | Wind Direction for Peak Wind Gust Speed - Fastest     |
        |      | 5-second (WSF3). Given in 360-degree compass point    |
        |      | directions (e.g. 360 = north, 180 = south, etc.).     |
        |      | Missing if more than 5 days within the month are      |
        |      | missing or flagged or if more than 3 consecutive      |
        |      | values within the month are missing or flagged.       |
        |      | DaysMissing: Flag indicating number of days missing   |
        |      | or flagged (from 1 to 5).                             |
        +------+-------------------------------------------------------+
        | MXyz | Monthly/Annual Mean of daily maximum soil temperature |
        |      | given in Celsius or Fahrenheit depending on user      |
        |      | specification. Missing if more than 5 days within the |
        |      | month are missing or flagged or if more than 3        |
        |      | consecutive values within the month are missing or    |
        |      | flagged. DaysMissing: Flag indicating number of days  |
        |      | missing or flagged (from 1 to 5).                     |
        |      |                                                       |
        |      | "y" values for MXyz, MNyz, HXyz, HNyz, LXyz, and LNyz |
        |      | 1=grass                                               |
        |      | 2=fallow                                              |
        |      | 3=bare ground                                         |
        |      | 4=brome grass                                         |
        |      | 5=sod                                                 |
        |      | 6=straw mulch                                         |
        |      | 7=grass muck                                          |
        |      | 8=bare muck                                           |
        |      | 0=unknown                                             |
        |      |                                                       |
        |      | "z" values for HXyz, HNyz, LXyz, and LNyz:            |
        |      | 1= 2 inches or 5 centimeters depth                    |
        |      | 2= 4 inches or 10 centimeters depth                   |
        |      | 3= 8 inches or 20 centimeters depth                   |
        |      | 4= 20 inches or 50 centimeters depth                  |
        |      | 5= 40 inches or 100 centimeters depth                 |
        |      | 6= 60 inches or 150 centimeters depth                 |
        |      | 7= 72 inches or 180 centimeters depth                 |
        |      | other=unknown                                         |
        +------+-------------------------------------------------------+
        | MNyz | Monthly/Annual Mean of daily minimum soil temperature |
        |      | given in Celsius or Fahrenheit depending on user      |
        |      | specification. Missing if more than 5 days within the |
        |      | month are missing or flagged or if more than 3        |
        |      | consecutive values within the month are missing or    |
        |      | flagged. DaysMissing: Flag indicating number of days  |
        |      | missing or flagged (from 1 to 5).                     |
        |      |                                                       |
        |      | See description of flags in MXyz.                     |
        +------+-------------------------------------------------------+
        | HXyz | Highest maximum soil temperature for the month/year   |
        |      | given in Celsius or Fahrenheit depending on user      |
        |      | specification. Missing if more than 5 days within the |
        |      | month are missing or flagged or if more than 3        |
        |      | consecutive values within the month are missing or    |
        |      | flagged. DaysMissing: Flag indicating number of days  |
        |      | missing or flagged (from 1 to 5).                     |
        |      |                                                       |
        |      | See description of flags in MXyz.                     |
        +------+-------------------------------------------------------+
        | HNyz | Highest minimum soil temperature for the month/year   |
        |      | given in Celsius or Fahrenheit depending on user      |
        |      | specification. Missing if more than 5 days within the |
        |      | month are missing or flagged or if more than 3        |
        |      | consecutive values within the month are missing or    |
        |      | flagged. DaysMissing: Flag indicating number of days  |
        |      | missing or flagged (from 1 to 5).                     |
        |      |                                                       |
        |      | See description of flags in MXyz.                     |
        +------+-------------------------------------------------------+
        | LXyz | Lowest maximum soil temperature for the month/year    |
        |      | given in Celsius or Fahrenheit depending on user      |
        |      | specification. Missing if more than 5 days within the |
        |      | month are missing or flagged or if more than 3        |
        |      | consecutive values within the month are missing or    |
        |      | flagged. DaysMissing: Flag indicating number of days  |
        |      | missing or flagged (from 1 to 5).                     |
        |      |                                                       |
        |      | See description of flags in MXyz.                     |
        +------+-------------------------------------------------------+
        | LNyz | Lowest minimum soil temperature for the month/year    |
        |      | given in Celsius or Fahrenheit depending on user      |
        |      | specification. Missing if more than 5 days within the |
        |      | month are missing or flagged or if more than 3        |
        |      | consecutive values within the month are missing or    |
        |      | flagged. DaysMissing: Flag indicating number of days  |
        |      | missing or flagged (from 1 to 5).                     |
        |      |                                                       |
        |      | See description of flags in MXyz.                     |
        +------+-------------------------------------------------------+
        | HDSD | Heating Degree Days (season-to-date). Running total   |
        |      | of monthly heating degree days through the end of the |
        |      | most recent month. Each month is summed to produce a  |
        |      | season-to-date total. Season starts in July in        |
        |      | Northern Hemisphere and January in Southern           |
        |      | Hemisphere. Given in Celsius or Fahrenheit degrees    |
        |      | depending on user specification.                      |
        +------+-------------------------------------------------------+
        | CDSD | Cooling Degree Days (season-to-date). Running total   |
        |      | of monthly cooling degree days through the end of the |
        |      | most recent month. Each month is summed to produce a  |
        |      | season-to-date total. Season starts in January in     |
        |      | Northern Hemisphere and July in Southern Hemisphere.  |
        |      | Given in Celsius or Fahrenheit degrees depending on   |
        |      | user specification.                                   |
        +------+-------------------------------------------------------+
        | FZFx | (x= 0-9) First/Last Freeze Days. Annual element only. |
        |      | Years begins on August 1. Missing if more than 5 days |
        |      | within the month are missing or flagged or if more    |
        |      | than 3 consecutive values within the month are        |
        |      | missing or flagged. DaysMissing: Flag indicating      |
        |      | number of days missing or flagged (from 1 to 5).      |
        |      | Given in format tttt.tyyyymmdds where tttt.t is       |
        |      | temperature in degrees Fahrenheit or Celsius          |
        |      | depending on user specification, yyyy is the year, mm |
        |      | is the month, dd is the day of the month and s is a   |
        |      | source flag.                                          |
        |      |                                                       |
        |      | "x" values for FZFx                                   |
        |      | 0 = first minimum temperature <= 32 degrees           |
        |      | Fahrenheit/0 degrees Celsius                          |
        |      | 1 = first minimum temperature <= 28 degrees           |
        |      | Fahrenheit/-2.2 degrees Celsius                       |
        |      | 2 = first minimum temperature <= 24 degrees           |
        |      | Fahrenheit/-4.4 degrees Celsius                       |
        |      | 3 = first minimum temperature <= 20 degrees           |
        |      | Fahrenheit/-6.7 degrees Celsius                       |
        |      | 4 = first minimum temperature <= 16 degrees           |
        |      | Fahrenheit/-8.9 degrees Celsius                       |
        |      | 5 = last minimum temperature <= 32 degrees            |
        |      | Fahrenheit/0 degrees Celsius                          |
        |      | 6 = last minimum temperature <= 28 degrees            |
        |      | Fahrenheit/-2.2 degrees Celsius                       |
        |      | 7 = last minimum temperature <= 24 degrees            |
        |      | Fahrenheit/-4.4 degrees Celsius                       |
        |      | 8 = last minimum temperature <= 20 degrees            |
        |      | Fahrenheit/-6.7 degrees Celsius                       |
        |      | 9 = last minimum temperature <= 16 degrees            |
        |      | Fahrenheit/-8.9 degrees Celsius                       |
        +------+-------------------------------------------------------+

    startdate
        Start date in ISO8601 format.

    enddate
        End date in ISO8601 format."""
    tsutils._printiso(
        ncei_gs(
            stationid,
            datatypeid=datatypeid,
            startdate=startdate,
            enddate=enddate,
        )
    )


def ncei_gsom(stationid, datatypeid="", startdate="", enddate=""):
    r"""Access ncei Global Summary of Month (GSOM) and Year (GSOY)."""
    df = ncei_cdo_json_to_df(
        r"http://www.ncdc.noaa.gov/cdo-web/api/v2/data",
        startdate=startdate,
        enddate=enddate,
        datasetid="GSOM",
        stationid=stationid,
    )

    return df


# 1763-01-01, 2016-01-01, Global Summary of the Year  , 1    , GSOY
@mando.command("ncei_gsoy", formatter_class=HelpFormatter, doctype="numpy")
def ncei_gsoy_cli(stationid, datatypeid="", startdate="", enddate=""):
    r"""Access ncei Global Summary of Year (GSOY).

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
    stationid
        This is the ncei
        station ID.

    datatypeid : str
        The following table lists the datatypes available for the 'ghcnd'
        dataset.  If the datatypeid is not given defaults to getting all data
        available at that station for the requested time period.

        +------+-------------------------------------------------------+
        | Code | Description                                           |
        +======+=======================================================+
        | TMAX | Monthly/Annual Maximum Temperature. Average of daily  |
        |      | maximum temperature given in Celsius or Fahrenheit    |
        |      | depending on user specification. Missing if more than |
        |      | 5 days within the month are missing or flagged or if  |
        |      | more than 3 consecutive values within the month are   |
        |      | missing or flagged.  DaysMissing: Flag indicating     |
        |      | number of days missing or flagged (from 1 to 5).      |
        +------+-------------------------------------------------------+
        | TMIN | Monthly/Annual Minimum Temperature. Average of daily  |
        |      | minimum temperature given in Celsius or Fahrenheit    |
        |      | depending on user specification. Missing if more than |
        |      | 5 days within the month are missing or flagged or if  |
        |      | more than 3 consecutive values within the month are   |
        |      | missing or flagged.  DaysMissing: Flag indicating     |
        |      | number of days missing or flagged (from 1 to 5).      |
        +------+-------------------------------------------------------+
        | TAVG | Average Monthly/Annual Temperature. Computed by       |
        |      | adding the unrounded monthly/annual maximum and       |
        |      | minimum temperatures and dividing by 2. Given in      |
        |      | Celsius or Fahrenheit depending on user               |
        |      | specification. Missing if more than 5 days within the |
        |      | month are missing or flagged or if more than 3        |
        |      | consecutive values within the month are missing or    |
        |      | flagged. DaysMissing: Flag indicating number of days  |
        |      | missing or flagged (from 1 to 5).                     |
        +------+-------------------------------------------------------+
        | EMXT | Extreme maximum temperature for month/year. Highest   |
        |      | daily maximum temperature for the month/year. Given   |
        |      | in Celsius or Fahrenheit depending on user            |
        |      | specification.                                        |
        +------+-------------------------------------------------------+
        | DYXT | Day of the EMXT for the month/year.                   |
        +------+-------------------------------------------------------+
        | EMNT | Extreme minimum temperature for month/year. Lowest    |
        |      | daily minimum temperature for the month/year. Given   |
        |      | in Celsius or Fahrenheit depending on user            |
        |      | specification.                                        |
        +------+-------------------------------------------------------+
        | DYXT | Day of the EMNT for the month/year.                   |
        +------+-------------------------------------------------------+
        | DX90 | Number of days with maximum temperature >= 90 degrees |
        |      | Fahrenheit/32.2 degrees Celsius.                      |
        +------+-------------------------------------------------------+
        | DX70 | Number of days with maximum temperature >= 70 degrees |
        |      | Fahrenheit/21.1 degrees Celsius.                      |
        +------+-------------------------------------------------------+
        | DX32 | Number of days with maximum temperature <= 32 degrees |
        |      | Fahrenheit/0 degrees Celsius.                         |
        +------+-------------------------------------------------------+
        | DT32 | Number of days with minimum temperature <= 32 degrees |
        |      | Fahrenheit/0 degrees Celsius.                         |
        +------+-------------------------------------------------------+
        | DT00 | Number of days with maximum temperature <= 0 degrees  |
        |      | Fahrenheit/-17.8 degrees Celsius.                     |
        +------+-------------------------------------------------------+
        | HTDD | Heating Degree Days. Computed when daily average      |
        |      | temperature is less than 65 degrees Fahrenheit/18.3   |
        |      | degrees Celsius. HDD = 65(F)/18.3(C) - mean daily     |
        |      | temperature. Each day is summed to produce a          |
        |      | monthly/annual total. Annual totals are computed      |
        |      | based on a July - June year in Northern Hemisphere    |
        |      | and January - December year in Southern Hemisphere.   |
        |      | Given in Celsius or Fahrenheit degrees depending on   |
        |      | user specification.                                   |
        +------+-------------------------------------------------------+
        | CLDD | Cooling Degree Days. Computed when daily average      |
        |      | temperature is more than 65 degrees Fahrenheit/18.3   |
        |      | degrees Celsius. CDD = mean daily temperature - 65    |
        |      | degrees Fahrenheit/18.3 degrees Celsius. Each day is  |
        |      | summed to produce a monthly/annual total. Annual      |
        |      | totals are computed based on a January - December     |
        |      | year in Northern Hemisphere and July - June year in   |
        |      | Southern Hemisphere. Given in Celsius or Fahrenheit   |
        |      | degrees depending on user specification.              |
        +------+-------------------------------------------------------+
        | PRCP | Total Monthly/Annual Precipitation. Given in inches   |
        |      | or millimeters depending on user specification.       |
        |      | Measurement Flags: T is used for trace amount, a is   |
        |      | used for any accumulation within a month/year that    |
        |      | includes missing days. If no days are missing, no     |
        |      | flag is used. Source Flag: Source flag from GHCN-     |
        |      | Daily (see separate documentation for GHCN-Daily).    |
        |      | Days Miss Flag: Number of days missing or flagged.    |
        +------+-------------------------------------------------------+
        | EMXP | Highest daily total of precipitation in the           |
        |      | month/year. Given in inches or millimeters depending  |
        |      | on user specification.                                |
        +------+-------------------------------------------------------+
        | DYXP | Day that EMXP for the month/year occurred.            |
        +------+-------------------------------------------------------+
        | DP01 | Number of days with >= 0.01 inch/0.254 millimeter in  |
        |      | the month/year.                                       |
        +------+-------------------------------------------------------+
        | DP05 | Number of days with >= 0.5 inch/12.7 millimeters in   |
        |      | the month/year.                                       |
        +------+-------------------------------------------------------+
        | DP10 | Number of days with >= 1.00 inch/25.4 millimeters in  |
        |      | the month/year.                                       |
        +------+-------------------------------------------------------+
        | SNOW | Total Monthly/Annual Snowfall. Given in inches or     |
        |      | millimeters depending on user specification.          |
        |      | Measurement Flags: T is used for trace amount, a is   |
        |      | used for any accumulation within a month/year that    |
        |      | includes missing days. If no days are missing, no     |
        |      | flag is used. Source Flag: Source flag from GHCN-     |
        |      | Daily (see separate documentation for GHCN-Daily).    |
        |      | Days Miss Flag: Number of days missing or flagged.    |
        +------+-------------------------------------------------------+
        | EMSN | Highest daily snowfall in the month/year. Given in    |
        |      | inches or millimeters depending on user               |
        |      | specification.                                        |
        +------+-------------------------------------------------------+
        | DYSN | Day EMSN for the month/year occurred.                 |
        +------+-------------------------------------------------------+
        | DSNW | Number of days with snowfall >= 1 inch/25             |
        |      | millimeters.                                          |
        +------+-------------------------------------------------------+
        | DSND | Number of days with snow depth >= 1 inch/25           |
        |      | millimeters.                                          |
        +------+-------------------------------------------------------+
        | EMSD | Highest daily snow depth in the month/year. Given in  |
        |      | inches or millimeters depending on user               |
        |      | specification.                                        |
        +------+-------------------------------------------------------+
        | DYSD | Day EMSD for the month/year occurred.                 |
        +------+-------------------------------------------------------+
        | EVAP | Total Monthly/Annual Evaporation. Given in inches or  |
        |      | millimeters depending on user specification.          |
        |      | Measurement Flags: T is used for trace amount, a is   |
        |      | used for any accumulation within a month/year that    |
        |      | includes missing days. If no days are missing, no     |
        |      | flag is used. Source Flag: Source flag from GHCN-     |
        |      | Daily (see separate documentation for GHCN-Daily).    |
        |      | Days Miss Flag: Number of days missing or flagged.    |
        +------+-------------------------------------------------------+
        | MNPN | Monthly/Annual Mean Minimum Temperature of            |
        |      | evaporation pan water. Given in Celsius or Fahrenheit |
        |      | depending on user specification. Missing if more than |
        |      | 5 days within the month are missing or flagged or if  |
        |      | more than 3 consecutive values within the month are   |
        |      | missing or flagged. DaysMissing: Flag indicating      |
        |      | number of days missing or flagged (from 1 to 5).      |
        +------+-------------------------------------------------------+
        | MXPN | Monthly/Annual Mean Maximum Temperature of            |
        |      | evaporation pan water. Given in Celsius or Fahrenheit |
        |      | depending on user specification. Missing if more than |
        |      | 5 days within the month are missing or flagged or if  |
        |      | more than 3 consecutive values within the month are   |
        |      | missing or flagged. DaysMissing: Flag indicating      |
        |      | number of days missing or flagged (from 1 to 5).      |
        +------+-------------------------------------------------------+
        | WDMV | Total Monthly/Annual Wind Movement over evaporation   |
        |      | pan. Given in miles or kilometers depending on user   |
        |      | specification. Days Miss Flag: Number of days missing |
        |      | or flagged.                                           |
        +------+-------------------------------------------------------+
        | TSUN | Daily total sunshine in minutes. Days Miss Flag:      |
        |      | Number of days missing or flagged.                    |
        +------+-------------------------------------------------------+
        | PSUN | Monthly/Annual Average of the daily percents of       |
        |      | possible sunshine. Days Miss Flag: Number of days     |
        |      | missing or flagged.                                   |
        +------+-------------------------------------------------------+
        | AWND | Monthly/Annual Average Wind Speed. Given in miles per |
        |      | hour or meters per second depending on user           |
        |      | specification. Missing if more than 5 days within the |
        |      | month are missing or flagged or if more than 3        |
        |      | consecutive values within the month are missing or    |
        |      | flagged. DaysMissing: Flag indicating number of days  |
        |      | missing or flagged (from 1 to 5).                     |
        +------+-------------------------------------------------------+
        | WSFM | Maximum Wind Speed/Fastest Mile. Maximum wind speed   |
        |      | for the month/year reported as the fastest mile.      |
        |      | Given in miles per hour or meters per second          |
        |      | depending on user specification. Missing if more than |
        |      | 5 days within the month are missing or flagged or if  |
        |      | more than 3 consecutive values within the month are   |
        |      | missing or flagged. DaysMissing: Flag indicating      |
        |      | number of days missing or flagged (from 1 to 5).      |
        +------+-------------------------------------------------------+
        | WDFM | Wind Direction for Maximum Wind Speed/Fastest Mile    |
        |      | (WSFM). Given in 360-degree compass point directions  |
        |      | (e.g. 360 = north, 180 = south, etc.).                |
        +------+-------------------------------------------------------+
        | WSF2 | Maximum Wind Speed/Fastest 2-minute. Maximum wind     |
        |      | speed for the month/year reported as the fastest      |
        |      | 2-minute. Given in miles per hour or meters per       |
        |      | second depending on user specification.  Missing if   |
        |      | more than 5 days within the month are missing or      |
        |      | flagged or if more than 3 consecutive values within   |
        |      | the month are missing or flagged. DaysMissing: Flag   |
        |      | indicating number of days missing or flagged (from 1  |
        |      | to 5).                                                |
        +------+-------------------------------------------------------+
        | WDF2 | Wind Direction for Maximum Wind Speed/Fastest         |
        |      | 2-Minute (WSF2). Given in 360-degree compass point    |
        |      | directions (e.g. 360 = north, 180 = south, etc.).     |
        +------+-------------------------------------------------------+
        | WSF1 | Maximum Wind Speed/Fastest 1-minute. Maximum wind     |
        |      | speed for the month/year reported as the fastest      |
        |      | 1-minute. Given in miles per hour or meters per       |
        |      | second depending on user specification.  Missing if   |
        |      | more than 5 days within the month are missing or      |
        |      | flagged or if more than 3 consecutive values within   |
        |      | the month are missing or flagged. DaysMissing: Flag   |
        |      | indicating number of days missing or flagged (from 1  |
        |      | to 5).                                                |
        +------+-------------------------------------------------------+
        | WDF1 | Wind Direction for Maximum Wind Speed/Fastest         |
        |      | 1-Minute (WSF1). Given in 360-degree compass point    |
        |      | directions (e.g. 360 = north, 180 = south, etc.).     |
        |      | Missing if more than 5 days within the month are      |
        |      | missing or flagged or if more than 3 consecutive      |
        |      | values within the month are missing or flagged.       |
        |      | DaysMissing: Flag indicating number of days missing   |
        |      | or flagged (from 1 to 5).                             |
        +------+-------------------------------------------------------+
        | WSFG | Peak Wind Gust Speed. Maximum wind gust for the       |
        |      | month/year. Given in miles per hour or second         |
        |      | depending on user specification. Missing if more than |
        |      | 5 days within the month are missing or flagged or if  |
        |      | more than 3 consecutive values within the month are   |
        |      | missing or flagged. DaysMissing: Flag indicating      |
        |      | number of days missing or flagged (from 1 to 5).      |
        +------+-------------------------------------------------------+
        | WDFG | Wind Direction for Peak Wind Gust Speed (WSFG). Given |
        |      | in 360-degree compass point directions (e.g. 360 =    |
        |      | north, 180 = south, etc.). Missing if more than 5     |
        |      | days within the month are missing or flagged or if    |
        |      | more than 3 consecutive values within the month are   |
        |      | missing or flagged. DaysMissing: Flag indicating      |
        |      | number of days missing or flagged (from 1 to 5).      |
        +------+-------------------------------------------------------+
        | WSF5 | Peak Wind Gust Speed - Fastest 5-second wind. Maximum |
        |      | wind gust for the month/year. Given in miles per hour |
        |      | or second depending on user specification. Missing if |
        |      | more than 5 days within the month are missing or      |
        |      | flagged or if more than 3 consecutive values within   |
        |      | the month are missing or flagged. DaysMissing: Flag   |
        |      | indicating number of days missing or flagged (from 1  |
        |      | to 5).                                                |
        +------+-------------------------------------------------------+
        | WDF5 | Wind Direction for Peak Wind Gust Speed - Fastest     |
        |      | 5-second (WSF5). Given in 360-degree compass point    |
        |      | directions (e.g. 360 = north, 180 = south, etc.).     |
        |      | Missing if more than 5 days within the month are      |
        |      | missing or flagged or if more than 3 consecutive      |
        |      | values within the month are missing or flagged.       |
        |      | DaysMissing: Flag indicating number of days missing   |
        |      | or flagged (from 1 to 5).                             |
        +------+-------------------------------------------------------+
        | WSF3 | Peak Wind Gust Speed - Fastest 3-second wind. Maximum |
        |      | wind gust for the month/year. Given in miles per hour |
        |      | or second depending on user specification. Missing if |
        |      | more than 5 days within the month are missing or      |
        |      | flagged or if more than 3 consecutive values within   |
        |      | the month are missing or flagged. DaysMissing: Flag   |
        |      | indicating number of days missing or flagged (from 1  |
        |      | to 5).                                                |
        +------+-------------------------------------------------------+
        | WDF3 | Wind Direction for Peak Wind Gust Speed - Fastest     |
        |      | 5-second (WSF3). Given in 360-degree compass point    |
        |      | directions (e.g. 360 = north, 180 = south, etc.).     |
        |      | Missing if more than 5 days within the month are      |
        |      | missing or flagged or if more than 3 consecutive      |
        |      | values within the month are missing or flagged.       |
        |      | DaysMissing: Flag indicating number of days missing   |
        |      | or flagged (from 1 to 5).                             |
        +------+-------------------------------------------------------+
        | MXyz | Monthly/Annual Mean of daily maximum soil temperature |
        |      | given in Celsius or Fahrenheit depending on user      |
        |      | specification. Missing if more than 5 days within the |
        |      | month are missing or flagged or if more than 3        |
        |      | consecutive values within the month are missing or    |
        |      | flagged. DaysMissing: Flag indicating number of days  |
        |      | missing or flagged (from 1 to 5).                     |
        |      |                                                       |
        |      | "y" values for MXyz, MNyz, HXyz, HNyz, LXyz, and LNyz |
        |      | 1=grass                                               |
        |      | 2=fallow                                              |
        |      | 3=bare ground                                         |
        |      | 4=brome grass                                         |
        |      | 5=sod                                                 |
        |      | 6=straw mulch                                         |
        |      | 7=grass muck                                          |
        |      | 8=bare muck                                           |
        |      | 0=unknown                                             |
        |      |                                                       |
        |      | "z" values for HXyz, HNyz, LXyz, and LNyz:            |
        |      | 1= 2 inches or 5 centimeters depth                    |
        |      | 2= 4 inches or 10 centimeters depth                   |
        |      | 3= 8 inches or 20 centimeters depth                   |
        |      | 4= 20 inches or 50 centimeters depth                  |
        |      | 5= 40 inches or 100 centimeters depth                 |
        |      | 6= 60 inches or 150 centimeters depth                 |
        |      | 7= 72 inches or 180 centimeters depth                 |
        |      | other=unknown                                         |
        +------+-------------------------------------------------------+
        | MNyz | Monthly/Annual Mean of daily minimum soil temperature |
        |      | given in Celsius or Fahrenheit depending on user      |
        |      | specification. Missing if more than 5 days within the |
        |      | month are missing or flagged or if more than 3        |
        |      | consecutive values within the month are missing or    |
        |      | flagged. DaysMissing: Flag indicating number of days  |
        |      | missing or flagged (from 1 to 5).                     |
        |      |                                                       |
        |      | See description of flags in MXyz.                     |
        +------+-------------------------------------------------------+
        | HXyz | Highest maximum soil temperature for the month/year   |
        |      | given in Celsius or Fahrenheit depending on user      |
        |      | specification. Missing if more than 5 days within the |
        |      | month are missing or flagged or if more than 3        |
        |      | consecutive values within the month are missing or    |
        |      | flagged. DaysMissing: Flag indicating number of days  |
        |      | missing or flagged (from 1 to 5).                     |
        |      |                                                       |
        |      | See description of flags in MXyz.                     |
        +------+-------------------------------------------------------+
        | HNyz | Highest minimum soil temperature for the month/year   |
        |      | given in Celsius or Fahrenheit depending on user      |
        |      | specification. Missing if more than 5 days within the |
        |      | month are missing or flagged or if more than 3        |
        |      | consecutive values within the month are missing or    |
        |      | flagged. DaysMissing: Flag indicating number of days  |
        |      | missing or flagged (from 1 to 5).                     |
        |      |                                                       |
        |      | See description of flags in MXyz.                     |
        +------+-------------------------------------------------------+
        | LXyz | Lowest maximum soil temperature for the month/year    |
        |      | given in Celsius or Fahrenheit depending on user      |
        |      | specification. Missing if more than 5 days within the |
        |      | month are missing or flagged or if more than 3        |
        |      | consecutive values within the month are missing or    |
        |      | flagged. DaysMissing: Flag indicating number of days  |
        |      | missing or flagged (from 1 to 5).                     |
        |      |                                                       |
        |      | See description of flags in MXyz.                     |
        +------+-------------------------------------------------------+
        | LNyz | Lowest minimum soil temperature for the month/year    |
        |      | given in Celsius or Fahrenheit depending on user      |
        |      | specification. Missing if more than 5 days within the |
        |      | month are missing or flagged or if more than 3        |
        |      | consecutive values within the month are missing or    |
        |      | flagged. DaysMissing: Flag indicating number of days  |
        |      | missing or flagged (from 1 to 5).                     |
        |      |                                                       |
        |      | See description of flags in MXyz.                     |
        +------+-------------------------------------------------------+
        | HDSD | Heating Degree Days (season-to-date). Running total   |
        |      | of monthly heating degree days through the end of the |
        |      | most recent month. Each month is summed to produce a  |
        |      | season-to-date total. Season starts in July in        |
        |      | Northern Hemisphere and January in Southern           |
        |      | Hemisphere. Given in Celsius or Fahrenheit degrees    |
        |      | depending on user specification.                      |
        +------+-------------------------------------------------------+
        | CDSD | Cooling Degree Days (season-to-date). Running total   |
        |      | of monthly cooling degree days through the end of the |
        |      | most recent month. Each month is summed to produce a  |
        |      | season-to-date total. Season starts in January in     |
        |      | Northern Hemisphere and July in Southern Hemisphere.  |
        |      | Given in Celsius or Fahrenheit degrees depending on   |
        |      | user specification.                                   |
        +------+-------------------------------------------------------+
        | FZFx | (x= 0-9) First/Last Freeze Days. Annual element only. |
        |      | Years begins on August 1. Missing if more than 5 days |
        |      | within the month are missing or flagged or if more    |
        |      | than 3 consecutive values within the month are        |
        |      | missing or flagged. DaysMissing: Flag indicating      |
        |      | number of days missing or flagged (from 1 to 5).      |
        |      | Given in format tttt.tyyyymmdds where tttt.t is       |
        |      | temperature in degrees Fahrenheit or Celsius          |
        |      | depending on user specification, yyyy is the year, mm |
        |      | is the month, dd is the day of the month and s is a   |
        |      | source flag.                                          |
        |      |                                                       |
        |      | "x" values for FZFx                                   |
        |      | 0 = first minimum temperature <= 32 degrees           |
        |      | Fahrenheit/0 degrees Celsius                          |
        |      | 1 = first minimum temperature <= 28 degrees           |
        |      | Fahrenheit/-2.2 degrees Celsius                       |
        |      | 2 = first minimum temperature <= 24 degrees           |
        |      | Fahrenheit/-4.4 degrees Celsius                       |
        |      | 3 = first minimum temperature <= 20 degrees           |
        |      | Fahrenheit/-6.7 degrees Celsius                       |
        |      | 4 = first minimum temperature <= 16 degrees           |
        |      | Fahrenheit/-8.9 degrees Celsius                       |
        |      | 5 = last minimum temperature <= 32 degrees            |
        |      | Fahrenheit/0 degrees Celsius                          |
        |      | 6 = last minimum temperature <= 28 degrees            |
        |      | Fahrenheit/-2.2 degrees Celsius                       |
        |      | 7 = last minimum temperature <= 24 degrees            |
        |      | Fahrenheit/-4.4 degrees Celsius                       |
        |      | 8 = last minimum temperature <= 20 degrees            |
        |      | Fahrenheit/-6.7 degrees Celsius                       |
        |      | 9 = last minimum temperature <= 16 degrees            |
        |      | Fahrenheit/-8.9 degrees Celsius                       |
        +------+-------------------------------------------------------+

    startdate
        Start date in ISO8601 format.

    enddate
        End date in ISO8601 format."""
    tsutils._printiso(
        ncei_gsoy(
            stationid,
            datatypeid=datatypeid,
            startdate=startdate,
            enddate=enddate,
        )
    )


def ncei_gsoy(stationid, datatypeid="", startdate="", enddate=""):
    r"""Access ncei Global Summary of Month (GSOM) and Year (GSOY)."""
    df = ncei_cdo_json_to_df(
        r"http://www.ncdc.noaa.gov/cdo-web/api/v2/data",
        startdate=startdate,
        enddate=enddate,
        datasetid="GSOY",
        stationid=stationid,
    )

    return df


# 1991-06-05, 2016-11-06, Weather Radar (Level II)    , 0.95 , NEXRAD2
# @mando.command('ncei_nexrad2', formatter_class=HelpFormatter, doctype='numpy')
def ncei_nexrad2_cli(stationid, datatypeid="", startdate="", enddate=""):
    r"""National Centers for Environmental Information (NCEI) NEXRAD Level II.

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
    tsutils._printiso(
        ncei_nexrad2(
            stationid, datatypeid=datatypeid, startdate=startdate, enddate=enddate
        )
    )


def ncei_nexrad2(stationid, datatypeid="", startdate="", enddate=""):
    r"""National Centers for Environmental Information (NCEI) NEXRAD Level II."""
    df = ncei_cdo_json_to_df(
        r"http://www.ncdc.noaa.gov/cdo-web/api/v2/data",
        startdate=startdate,
        enddate=enddate,
        datasetid="NEXRAD2",
        stationid=stationid,
    )

    return df


# 1991-06-05, 2016-11-06, Weather Radar (Level III)   , 0.95 , NEXRAD3
# @mando.command('ncei_nexrad3',formatter_class=HelpFormatter, doctype='numpy')
def ncei_nexrad3_cli(stationid, datatypeid="", startdate="", enddate=""):
    r"""National Centers for Environmental Information (NCEI) NEXRAD Level III.

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
    return tsutils._printiso(
        ncei_nexrad3(
            stationid, datatypeid=datatypeid, startdate=startdate, enddate=enddate
        )
    )


def ncei_nexrad3(stationid, datatypeid="", startdate="", enddate=""):
    r"""National Centers for Environmental Information (NCEI) NEXRAD Level III."""
    df = ncei_cdo_json_to_df(
        r"http://www.ncdc.noaa.gov/cdo-web/api/v2/data",
        startdate=startdate,
        enddate=enddate,
        datasetid="NEXRAD3",
        stationid=stationid,
    )

    return df


# 2010-01-01, 2010-01-01, Normals Annual/Seasonal     , 1    , NORMAL_ANN
@mando.command("ncei_normal_ann", formatter_class=HelpFormatter, doctype="numpy")
def ncei_normal_ann_cli(stationid, datatypeid="", startdate="", enddate=""):
    r"""National Centers for Environmental Information (NCEI) annual normals.

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

    +-------+----------------------------------------------------------+
    | Code  | Description                                              |
    +=======+==========================================================+
    | C     | complete (all 30 years used)                             |
    +-------+----------------------------------------------------------+
    | S     | standard (no more than 5 years missing and no more than  |
    |       | 3 consecutive years missing among the sufficiently       |
    |       | complete years)                                          |
    +-------+----------------------------------------------------------+
    | R     | representative (observed record utilized incomplete, but |
    |       | value was scaled or based on filled values to be         |
    |       | representative of the full period of record)             |
    +-------+----------------------------------------------------------+
    | P     | provisional (at least 10 years used, but not             |
    |       | sufficiently complete to be labeled as standard or       |
    |       | representative). Also used for parameter values on       |
    |       | February 29 as well as for interpolated daily            |
    |       | precipitation, snowfall, and snow depth percentiles.     |
    +-------+----------------------------------------------------------+
    | Q     | quasi-normal (at least 2 years per month, but not        |
    |       | sufficiently complete to be labeled as provisional or    |
    |       | any other higher flag code. The associated value was     |
    |       | computed using a pseudo-normals approach or derived      |
    |       | from monthly pseudo-normals.                             |
    +-------+----------------------------------------------------------+
    | Blank | the data value is reported as a special value (see       |
    |       | section B under III. Additional Information below).      |
    +-------+----------------------------------------------------------+

    Note: flags Q and R aren't applicable to average number of days with
    different precipitation, snowfall, and snow depth threshold exceedance;
    precipitation/snowfall/snow probabilities of occurrence. Further, Q flags
    are not applicable for standard deviations.

    Parameters
    ----------
    stationid
        The is the ncei
        station ID.

    datatypeid : str
        The following table lists the datatypes available for the annual
        dataset.  If the datatypeid is not given defaults to getting all data
        available at that station.

        +-------------------------+------------------------------------+
        | Code                    | Description                        |
        +=========================+====================================+
        | ANN-CLDD-BASExx         | Average annual                     |
        |                         | cooling degree days where xx is    |
        |                         | the base in degree F.              |
        |                         | 'xx' can be one of 45, 50, 57, 60, |
        |                         | 65, 70, 72                         |
        +-------------------------+------------------------------------+
        | ANN-CLDD-NORMAL         | Average annual                     |
        |                         | cooling degree days with base 65F  |
        +-------------------------+------------------------------------+
        | ANN-DUTR-NORMAL         | Average annual                     |
        |                         | diurnal temperature range          |
        +-------------------------+------------------------------------+
        | ANN-GRDD-BASExx         | Average annual                     |
        |                         | growing degree days where xx is    |
        |                         | the base in degree F.              |
        |                         | 'xx' can be one of 40, 45, 50, 55, |
        |                         | 57, 60, 65, 70, 72.                |
        +-------------------------+------------------------------------+
        | ANN-GRDD-TB4886         | Average annual                     |
        |                         | growing degree days with truncated |
        |                         | bases 48F and 86F                  |
        +-------------------------+------------------------------------+
        | ANN-GRDD-TB5086         | Average annual                     |
        |                         | growing degree days with truncated |
        |                         | bases 50F and 86F                  |
        +-------------------------+------------------------------------+
        | ANN-HTDD-BASE40         | Average annual                     |
        |                         | heating degree days with base 40F  |
        +-------------------------+------------------------------------+
        | ANN-HTDD-BASE45         | Average annual                     |
        |                         | heating degree days with base 45F  |
        +-------------------------+------------------------------------+
        | ANN-HTDD-BASE50         | Average annual                     |
        |                         | heating degree days with base 50F  |
        +-------------------------+------------------------------------+
        | ANN-HTDD-BASE55         | Average annual                     |
        |                         | heating degree days with base 55F  |
        +-------------------------+------------------------------------+
        | ANN-HTDD-BASE57         | Average annual                     |
        |                         | heating degree days with base 57F  |
        +-------------------------+------------------------------------+
        | ANN-HTDD-BASE60         | Average annual                     |
        |                         | heating degree days with base 60F  |
        +-------------------------+------------------------------------+
        | ANN-HTDD-NORMAL         | Average annual                     |
        |                         | heating degree days with base 65F  |
        +-------------------------+------------------------------------+
        | ANN-PRCP-AVGNDS-GE001HI | Average number of                  |
        |                         | days during the year with          |
        |                         | precipitation >= 0.01 inches       |
        +-------------------------+------------------------------------+
        | ANN-PRCP-AVGNDS-GE010HI | Average number of                  |
        |                         | days during the year with          |
        |                         | precipitation >= 0.10 inches       |
        +-------------------------+------------------------------------+
        | ANN-PRCP-AVGNDS-GE050HI | Average number of                  |
        |                         | days during the year with          |
        |                         | precipitation >= 0.50 inches       |
        +-------------------------+------------------------------------+
        | ANN-PRCP-AVGNDS-GE100HI | Average number of                  |
        |                         | days during the year with          |
        |                         | precipitation >= 1.00 inches       |
        +-------------------------+------------------------------------+
        | ANN-PRCP-NORMAL         | Average annual                     |
        |                         | precipitation totals               |
        +-------------------------+------------------------------------+
        | ANN-SNOW-AVGNDS-GE001TI | Average number of                  |
        |                         | days during the year with snowfall |
        |                         | >= 0.1 inches                      |
        +-------------------------+------------------------------------+
        | ANN-SNOW-AVGNDS-GE010TI | Average number of                  |
        |                         | days during the year with snowfall |
        |                         | >= 1.0 inches                      |
        +-------------------------+------------------------------------+
        | ANN-SNOW-AVGNDS-GE030TI | Average number of                  |
        |                         | days during the year with snowfall |
        |                         | >= 3.0 inches                      |
        +-------------------------+------------------------------------+
        | ANN-SNOW-AVGNDS-GE050TI | Average number of                  |
        |                         | days during the year with snowfall |
        |                         | >= 5.0 inches                      |
        +-------------------------+------------------------------------+
        | ANN-SNOW-AVGNDS-GE100TI | Average number of                  |
        |                         | days during the year with snowfall |
        |                         | >= 10.0 inches                     |
        +-------------------------+------------------------------------+
        | ANN-SNOW-NORMAL         | Average annual                     |
        |                         | snowfall totals                    |
        +-------------------------+------------------------------------+
        | ANN-SNWD-AVGNDS-GE001WI | Average number of                  |
        |                         | days during the year with snow     |
        |                         | depth >= 1 inch                    |
        +-------------------------+------------------------------------+
        | ANN-SNWD-AVGNDS-GE003WI | Average number of                  |
        |                         | days during the year with snow     |
        |                         | depth >= 3 inches                  |
        +-------------------------+------------------------------------+
        | ANN-SNWD-AVGNDS-GE005WI | Average number of                  |
        |                         | days during the year with snow     |
        |                         | depth >=5 inches                   |
        +-------------------------+------------------------------------+
        | ANN-SNWD-AVGNDS-GE010WI | Average number of                  |
        |                         | days during the year with snow     |
        |                         | depth >=10 inches                  |
        +-------------------------+------------------------------------+
        | ANN-TAVG-NORMAL         | Average annual                     |
        |                         | average temperature                |
        +-------------------------+------------------------------------+
        | ANN-TMAX-AVGNDS-GRTH040 | Average number of days             |
        |                         | per year where tmax is greater     |
        |                         | than or equal to 40F               |
        +-------------------------+------------------------------------+
        | ANN-TMAX-AVGNDS-GRTH050 | Average number of days             |
        |                         | per year where tmax is greater     |
        |                         | than or equal to 50F               |
        +-------------------------+------------------------------------+
        | ANN-TMAX-AVGNDS-GRTH060 | Average number of days             |
        |                         | per year where tmax is greater     |
        |                         | than or equal to 60F               |
        +-------------------------+------------------------------------+
        | ANN-TMAX-AVGNDS-GRTH070 | Average number of days             |
        |                         | per year where tmax is greater     |
        |                         | than or equal to 70F               |
        +-------------------------+------------------------------------+
        | ANN-TMAX-AVGNDS-GRTH080 | Average number of days             |
        |                         | per year where tmax is greater     |
        |                         | than or equal to 80F               |
        +-------------------------+------------------------------------+
        | ANN-TMAX-AVGNDS-GRTH090 | Average number of days             |
        |                         | per year where tmax is greater     |
        |                         | than or equal to 90F               |
        +-------------------------+------------------------------------+
        | ANN-TMAX-AVGNDS-GRTH100 | Average number of days             |
        |                         | per year where tmax is greater     |
        |                         | than or equal to 100F              |
        +-------------------------+------------------------------------+
        | ANN-TMAX-AVGNDS-LSTH032 | Average number of days             |
        |                         | per year where tmax is less than   |
        |                         | or equal to 32F                    |
        +-------------------------+------------------------------------+
        | ANN-TMAX-NORMAL         | Average annual                     |
        |                         | maximum temperature                |
        +-------------------------+------------------------------------+
        | ANN-TMIN-AVGNDS-LSTH000 | Average number of days             |
        |                         | per year where tmin is less than   |
        |                         | or equal to 0F                     |
        +-------------------------+------------------------------------+
        | ANN-TMIN-AVGNDS-LSTH010 | Average number of days             |
        |                         | per year where tmin is less than   |
        |                         | or equal to 10F                    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-AVGNDS-LSTH020 | Average number of days             |
        |                         | per year where tmin is less than   |
        |                         | or equal to 20F                    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-AVGNDS-LSTH032 | Average number of days             |
        |                         | per year where tmin is less than   |
        |                         | or equal to 32F                    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-AVGNDS-LSTH040 | Average number of days             |
        |                         | per year where tmin is less than   |
        |                         | or equal to 40F                    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-AVGNDS-LSTH050 | Average number of days             |
        |                         | per year where tmin is less than   |
        |                         | or equal to 50F                    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-AVGNDS-LSTH060 | Average number of days             |
        |                         | per year where tmin is less than   |
        |                         | or equal to 60F                    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-AVGNDS-LSTH070 | Average number of days             |
        |                         | per year where tmin is less than   |
        |                         | or equal to 70F                    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-NORMAL         | Average annual                     |
        |                         | minimum temperature                |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T16FP10 | 10 per cent probability date of    |
        |                         | first 16F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T16FP20 | 20 per cent probability date of    |
        |                         | first 16F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T16FP30 | 30 per cent probability date of    |
        |                         | first 16F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T16FP40 | 40 per cent probability date of    |
        |                         | first 16F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T16FP50 | 50 per cent probability date of    |
        |                         | first 16F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T16FP60 | 60 per cent probability date of    |
        |                         | first 16F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T16FP70 | 70 per cent probability date of    |
        |                         | first 16F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T16FP80 | 80 per cent probability date of    |
        |                         | first 16F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T16FP90 | 90 per cent probability date of    |
        |                         | first 16F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T20FP10 | 10 per cent probability date of    |
        |                         | first 20F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T20FP20 | 20 per cent probability date of    |
        |                         | first 20F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T20FP30 | 30 per cent probability date of    |
        |                         | first 20F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T20FP40 | 40 per cent probability date of    |
        |                         | first 20F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T20FP50 | 50 per cent probability date of    |
        |                         | first 20F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T20FP60 | 60 per cent probability date of    |
        |                         | first 20F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T20FP70 | 70 per cent probability date of    |
        |                         | first 20F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T20FP80 | 80 per cent probability date of    |
        |                         | first 20F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T20FP90 | 90 per cent probability date of    |
        |                         | first 20F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T24FP10 | 10 per cent probability date of    |
        |                         | first 24F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T24FP20 | 20 per cent probability date of    |
        |                         | first 24F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T24FP30 | 30 per cent probability date of    |
        |                         | first 24F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T24FP40 | 40 per cent probability date of    |
        |                         | first 24F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T24FP50 | 50 per cent probability date of    |
        |                         | first 24F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T24FP60 | 60 per cent probability date of    |
        |                         | first 24F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T24FP70 | 70 per cent probability date of    |
        |                         | first 24F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T24FP80 | 80 per cent probability date of    |
        |                         | first 24F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T24FP90 | 90 per cent probability date of    |
        |                         | first 24F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T28FP10 | 10 per cent probability date of    |
        |                         | first 28F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T28FP20 | 20 per cent probability date of    |
        |                         | first 28F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T28FP30 | 30 per cent probability date of    |
        |                         | first 28F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T28FP40 | 40 per cent probability date of    |
        |                         | first 28F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T28FP50 | 50 per cent probability date of    |
        |                         | first 28F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T28FP60 | 60 per cent probability date of    |
        |                         | first 28F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T28FP70 | 70 per cent probability date of    |
        |                         | first 28F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T28FP80 | 80 per cent probability date of    |
        |                         | first 28F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T28FP90 | 90 per cent probability date of    |
        |                         | first 28F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T32FP10 | 10 per cent probability date of    |
        |                         | first 32F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T32FP20 | 20 per cent probability date of    |
        |                         | first 32F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T32FP30 | 30 per cent probability date of    |
        |                         | first 32F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T32FP40 | 40 per cent probability date of    |
        |                         | first 32F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T32FP50 | 50 per cent probability date of    |
        |                         | first 32F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T32FP60 | 60 per cent probability date of    |
        |                         | first 32F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T32FP70 | 70 per cent probability date of    |
        |                         | first 32F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T32FP80 | 80 per cent probability date of    |
        |                         | first 32F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T32FP90 | 90 per cent probability date of    |
        |                         | first 32F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T36FP10 | 10 per cent probability date of    |
        |                         | first 36F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T36FP20 | 20 per cent probability date of    |
        |                         | first 36F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T36FP30 | 30 per cent probability date of    |
        |                         | first 36F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T36FP40 | 40 per cent probability date of    |
        |                         | first 36F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T36FP50 | 50 per cent probability date of    |
        |                         | first 36F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T36FP60 | 60 per cent probability date of    |
        |                         | first 36F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T36FP70 | 70 per cent probability date of    |
        |                         | first 36F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T36FP80 | 80 per cent probability date of    |
        |                         | first 36F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBFST-T36FP90 | 90 per cent probability date of    |
        |                         | first 36F occurrence or earlier    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T16FP10 | 10 per cent probability of 16F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T16FP20 | 20 per cent probability of 16F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T16FP30 | 30 per cent probability of 16F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T16FP40 | 40 per cent probability of 16F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T16FP50 | 50 per cent probability of 16F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T16FP60 | 60 per cent probability of 16F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T16FP70 | 70 per cent probability of 16F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T16FP80 | 80 per cent probability of 16F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T16FP90 | 90 per cent probability of 16F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T20FP10 | 10 per cent probability of 20F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T20FP20 | 20 per cent probability of 20F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T20FP30 | 30 per cent probability of 20F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T20FP40 | 40 per cent probability of 20F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T20FP50 | 50 per cent probability of 20F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T20FP60 | 60 per cent probability of 20F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T20FP70 | 70 per cent probability of 20F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T20FP80 | 80 per cent probability of 20F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T20FP90 | 90 per cent probability of 20F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T24FP10 | 10 per cent probability of 24F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T24FP20 | 20 per cent probability of 24F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T24FP30 | 30 per cent probability of 24F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T24FP40 | 40 per cent probability of 24F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T24FP50 | 50 per cent probability of 24F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T24FP60 | 60 per cent probability of 24F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T24FP70 | 70 per cent probability of 24F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T24FP80 | 80 per cent probability of 24F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T24FP90 | 90 per cent probability of 24F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T28FP10 | 10 per cent probability of 28F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T28FP20 | 20 per cent probability of 28F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T28FP30 | 30 per cent probability of 28F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T28FP40 | 40 per cent probability of 28F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T28FP50 | 50 per cent probability of 28F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T28FP60 | 60 per cent probability of 28F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T28FP70 | 70 per cent probability of 28F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T28FP80 | 80 per cent probability of 28F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T28FP90 | 90 per cent probability of 28F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T32FP10 | 10 per cent probability of 32F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T32FP20 | 20 per cent probability of 32F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T32FP30 | 30 per cent probability of 32F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T32FP40 | 40 per cent probability of 32F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T32FP50 | 50 per cent probability of 32F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T32FP60 | 60 per cent probability of 32F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T32FP70 | 70 per cent probability of 32F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T32FP80 | 80 per cent probability of 32F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T32FP90 | 90 per cent probability of 32F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T36FP10 | 10 per cent probability of 36F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T36FP20 | 20 per cent probability of 36F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T36FP30 | 30 per cent probability of 36F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T36FP40 | 40 per cent probability of 36F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T36FP50 | 50 per cent probability of 36F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T36FP60 | 60 per cent probability of 36F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T36FP70 | 70 per cent probability of 36F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T36FP80 | 80 per cent probability of 36F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBGSL-T36FP90 | 90 per cent probability of 36F     |
        |                         | growing season length or longer    |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T16FP10 | 10 per cent probability date of    |
        |                         | last 16F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T16FP20 | 20 per cent probability date of    |
        |                         | last 16F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T16FP30 | 30 per cent probability date of    |
        |                         | last 16F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T16FP40 | 40 per cent probability date of    |
        |                         | last 16F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T16FP50 | 50 per cent probability date of    |
        |                         | last 16F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T16FP60 | 60 per cent probability date of    |
        |                         | last 16F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T16FP70 | 70 per cent probability date of    |
        |                         | last 16F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T16FP80 | 80 per cent probability date of    |
        |                         | last 16F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T16FP90 | 90 per cent probability date of    |
        |                         | last 16F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T20FP10 | 10 per cent probability date of    |
        |                         | last 20F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T20FP20 | 20 per cent probability date of    |
        |                         | last 20F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T20FP30 | 30 per cent probability date of    |
        |                         | last 20F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T20FP40 | 40 per cent probability date of    |
        |                         | last 20F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T20FP50 | 50 per cent probability date of    |
        |                         | last 20F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T20FP60 | 60 per cent probability date of    |
        |                         | last 20F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T20FP70 | 70 per cent probability date of    |
        |                         | last 20F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T20FP80 | 80 per cent probability date of    |
        |                         | last 20F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T20FP90 | 90 per cent probability date of    |
        |                         | last 20F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T24FP10 | 10 per cent probability date of    |
        |                         | last 24F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T24FP20 | 20 per cent probability date of    |
        |                         | last 24F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T24FP30 | 30 per cent probability date of    |
        |                         | last 24F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T24FP40 | 40 per cent probability date of    |
        |                         | last 24F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T24FP50 | 50 per cent probability date of    |
        |                         | last 24F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T24FP60 | 60 per cent probability date of    |
        |                         | last 24F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T24FP70 | 70 per cent probability date of    |
        |                         | last 24F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T24FP80 | 80 per cent probability date of    |
        |                         | last 24F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T24FP90 | 90 per cent probability date of    |
        |                         | last 24F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T28FP10 | 10 per cent probability date of    |
        |                         | last 28F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T28FP20 | 20 per cent probability date of    |
        |                         | last 28F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T28FP30 | 30 per cent probability date of    |
        |                         | last 28F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T28FP40 | 40 per cent probability date of    |
        |                         | last 28F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T28FP50 | 50 per cent probability date of    |
        |                         | last 28F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T28FP60 | 60 per cent probability date of    |
        |                         | last 28F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T28FP70 | 70 per cent probability date of    |
        |                         | last 28F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T28FP80 | 80 per cent probability date of    |
        |                         | last 28F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T28FP90 | 90 per cent probability date of    |
        |                         | last 28F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T32FP10 | 10 per cent probability date of    |
        |                         | last 32F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T32FP20 | 20 per cent probability date of    |
        |                         | last 32F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T32FP30 | 30 per cent probability date of    |
        |                         | last 32F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T32FP40 | 40 per cent probability date of    |
        |                         | last 32F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T32FP50 | 50 per cent probability date of    |
        |                         | last 32F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T32FP60 | 60 per cent probability date of    |
        |                         | last 32F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T32FP70 | 70 per cent probability date of    |
        |                         | last 32F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T32FP80 | 80 per cent probability date of    |
        |                         | last 32F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T32FP90 | 90 per cent probability date of    |
        |                         | last 32F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T36FP10 | 10 per cent probability date of    |
        |                         | last 36F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T36FP20 | 20 per cent probability date of    |
        |                         | last 36F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T36FP30 | 30 per cent probability date of    |
        |                         | last 36F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T36FP40 | 40 per cent probability date of    |
        |                         | last 36F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T36FP50 | 50 per cent probability date of    |
        |                         | last 36F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T36FP60 | 60 per cent probability date of    |
        |                         | last 36F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T36FP70 | 70 per cent probability date of    |
        |                         | last 36F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T36FP80 | 80 per cent probability date of    |
        |                         | last 36F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBLST-T36FP90 | 90 per cent probability date of    |
        |                         | last 36F occurrence or later       |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBOCC-LSTH016 | probability of 16F or below at     |
        |                         | least once in the year             |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBOCC-LSTH020 | probability of 20F or below at     |
        |                         | least once in the year             |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBOCC-LSTH024 | probability of 24F or below at     |
        |                         | least once in the year             |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBOCC-LSTH028 | probability of 28F or below at     |
        |                         | least once in the year             |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBOCC-LSTH032 | probability of 32F or below at     |
        |                         | least once in the year             |
        +-------------------------+------------------------------------+
        | ANN-TMIN-PRBOCC-LSTH036 | probability of 36F or below at     |
        |                         | least once in the year             |
        +-------------------------+------------------------------------+
        | DJF-CLDD-BASE45         | Average winter                     |
        |                         | cooling degree days with base 45F  |
        +-------------------------+------------------------------------+
        | DJF-CLDD-BASE50         | Average winter                     |
        |                         | cooling degree days with base 50F  |
        +-------------------------+------------------------------------+
        | DJF-CLDD-BASE55         | Average winter                     |
        |                         | cooling degree days with base 55F  |
        +-------------------------+------------------------------------+
        | DJF-CLDD-BASE57         | Average winter                     |
        |                         | cooling degree days with base 57F  |
        +-------------------------+------------------------------------+
        | DJF-CLDD-BASE60         | Average winter                     |
        |                         | cooling degree days with base 60F  |
        +-------------------------+------------------------------------+
        | DJF-CLDD-BASE70         | Average winter                     |
        |                         | cooling degree days with base 70F  |
        +-------------------------+------------------------------------+
        | DJF-CLDD-BASE72         | Average winter                     |
        |                         | cooling degree days with base 72F  |
        +-------------------------+------------------------------------+
        | DJF-CLDD-NORMAL         | Average winter                     |
        |                         | cooling degree days with base 65F  |
        +-------------------------+------------------------------------+
        | DJF-DUTR-NORMAL         | Average winter                     |
        |                         | diurnal temperature range          |
        +-------------------------+------------------------------------+
        | DJF-GRDD-BASE40         | Average winter                     |
        |                         | growing degree days with base 40F  |
        +-------------------------+------------------------------------+
        | DJF-GRDD-BASE45         | Average winter                     |
        |                         | growing degree days with base 45F  |
        +-------------------------+------------------------------------+
        | DJF-GRDD-BASE50         | Average winter                     |
        |                         | growing degree days with base 50F  |
        +-------------------------+------------------------------------+
        | DJF-GRDD-BASE55         | Average winter                     |
        |                         | growing degree days with base 55F  |
        +-------------------------+------------------------------------+
        | DJF-GRDD-BASE57         | Average winter                     |
        |                         | growing degree days with base 57F  |
        +-------------------------+------------------------------------+
        | DJF-GRDD-BASE60         | Average winter                     |
        |                         | growing degree days with base 60F  |
        +-------------------------+------------------------------------+
        | DJF-GRDD-BASE65         | Average winter                     |
        |                         | growing degree days with base 65F  |
        +-------------------------+------------------------------------+
        | DJF-GRDD-BASE70         | Average winter                     |
        |                         | growing degree days with base 70F  |
        +-------------------------+------------------------------------+
        | DJF-GRDD-BASE72         | Average winter                     |
        |                         | growing degree days with base 72F  |
        +-------------------------+------------------------------------+
        | DJF-GRDD-TB4886         | Average winter                     |
        |                         | growing degree days with truncated |
        |                         | bases 48F and 86F                  |
        +-------------------------+------------------------------------+
        | DJF-GRDD-TB5086         | Average winter                     |
        |                         | growing degree days with truncated |
        |                         | bases 50F and 86F                  |
        +-------------------------+------------------------------------+
        | DJF-HTDD-BASE40         | Average winter                     |
        |                         | heating degree days with base 40F  |
        +-------------------------+------------------------------------+
        | DJF-HTDD-BASE45         | Average winter                     |
        |                         | heating degree days with base 45F  |
        +-------------------------+------------------------------------+
        | DJF-HTDD-BASE50         | Average winter                     |
        |                         | heating degree days with base 50F  |
        +-------------------------+------------------------------------+
        | DJF-HTDD-BASE55         | Average winter                     |
        |                         | heating degree days with base 55F  |
        +-------------------------+------------------------------------+
        | DJF-HTDD-BASE57         | Average winter                     |
        |                         | heating degree days with base 57F  |
        +-------------------------+------------------------------------+
        | DJF-HTDD-BASE60         | Average winter                     |
        |                         | heating degree days with base 60F  |
        +-------------------------+------------------------------------+
        | DJF-HTDD-NORMAL         | Average winter                     |
        |                         | heating degree days with base 65F  |
        +-------------------------+------------------------------------+
        | DJF-PRCP-AVGNDS-GE001HI | Average number of                  |
        |                         | days during December- February     |
        |                         | with precipitation >= 0.01 inches  |
        +-------------------------+------------------------------------+
        | DJF-PRCP-AVGNDS-GE010HI | Average number of                  |
        |                         | days during December- February     |
        |                         | with precipitation >= 0.10 inches  |
        +-------------------------+------------------------------------+
        | DJF-PRCP-AVGNDS-GE050HI | Average number of                  |
        |                         | days during December- February     |
        |                         | with precipitation >= 0.50 inches  |
        +-------------------------+------------------------------------+
        | DJF-PRCP-AVGNDS-GE100HI | Average number of                  |
        |                         | days during December- February     |
        |                         | with precipitation >= 1.00 inches  |
        +-------------------------+------------------------------------+
        | DJF-PRCP-NORMAL         | Average seasonal                   |
        |                         | precipitation totals for December- |
        |                         | February                           |
        +-------------------------+------------------------------------+
        | DJF-SNOW-AVGNDS-GE001TI | Average number of                  |
        |                         | days during December- February     |
        |                         | with snowfall >= 0.1 inches        |
        +-------------------------+------------------------------------+
        | DJF-SNOW-AVGNDS-GE010TI | Average number of                  |
        |                         | days during December- February     |
        |                         | with snowfall >= 1.0 inches        |
        +-------------------------+------------------------------------+
        | DJF-SNOW-AVGNDS-GE030TI | Average number of                  |
        |                         | days during December- February     |
        |                         | with snowfall >= 3.0 inches        |
        +-------------------------+------------------------------------+
        | DJF-SNOW-AVGNDS-GE050TI | Average number of                  |
        |                         | days during December- February     |
        |                         | with snowfall >= 5.0 inches        |
        +-------------------------+------------------------------------+
        | DJF-SNOW-AVGNDS-GE100TI | Average number of                  |
        |                         | days during December- February     |
        |                         | with snowfall >= 10.0 inches       |
        +-------------------------+------------------------------------+
        | DJF-SNOW-NORMAL         | Average seasonal                   |
        |                         | snowfall totals for December-      |
        |                         | February                           |
        +-------------------------+------------------------------------+
        | DJF-SNWD-AVGNDS-GE001WI | Average number of                  |
        |                         | days during December- February     |
        |                         | with snow depth >= 1 inch          |
        +-------------------------+------------------------------------+
        | DJF-SNWD-AVGNDS-GE003WI | Average number of                  |
        |                         | days during December- February     |
        |                         | with snow depth >= 3 inches        |
        +-------------------------+------------------------------------+
        | DJF-SNWD-AVGNDS-GE005WI | Average number of                  |
        |                         | days during December- February     |
        |                         | with snow depth >= 5 inches        |
        +-------------------------+------------------------------------+
        | DJF-SNWD-AVGNDS-GE010WI | Average number of                  |
        |                         | days during December- February     |
        |                         | with snow depth >= 10 inches       |
        +-------------------------+------------------------------------+
        | DJF-TAVG-NORMAL         | Average winter                     |
        |                         | average temperature                |
        +-------------------------+------------------------------------+
        | DJF-TMAX-AVGNDS-GRTH040 | Average number of days             |
        |                         | per winter where tmax is greater   |
        |                         | than or equal to 40F               |
        +-------------------------+------------------------------------+
        | DJF-TMAX-AVGNDS-GRTH050 | Average number of days             |
        |                         | per winter where tmax is greater   |
        |                         | than or equal to 50F               |
        +-------------------------+------------------------------------+
        | DJF-TMAX-AVGNDS-GRTH060 | Average number of days             |
        |                         | per winter where tmax is greater   |
        |                         | than or equal to 60F               |
        +-------------------------+------------------------------------+
        | DJF-TMAX-AVGNDS-GRTH070 | Average number of days             |
        |                         | per winter where tmax is greater   |
        |                         | than or equal to 70F               |
        +-------------------------+------------------------------------+
        | DJF-TMAX-AVGNDS-GRTH080 | Average number of days             |
        |                         | per winter where tmax is greater   |
        |                         | than or equal to 80F               |
        +-------------------------+------------------------------------+
        | DJF-TMAX-AVGNDS-GRTH090 | Average number of days             |
        |                         | per winter where tmax is greater   |
        |                         | than or equal to 90F               |
        +-------------------------+------------------------------------+
        | DJF-TMAX-AVGNDS-GRTH100 | Average number of days             |
        |                         | per winter where tmax is greater   |
        |                         | than or equal to 100F              |
        +-------------------------+------------------------------------+
        | DJF-TMAX-AVGNDS-LSTH032 | Average number of days             |
        |                         | per winter where tmax is less than |
        |                         | or equal to 32F                    |
        +-------------------------+------------------------------------+
        | DJF-TMAX-NORMAL         | Average winter                     |
        |                         | maximum temperature                |
        +-------------------------+------------------------------------+
        | DJF-TMIN-AVGNDS-LSTH000 | Average number of days             |
        |                         | per winter where tmin is less than |
        |                         | or equal to 0F                     |
        +-------------------------+------------------------------------+
        | DJF-TMIN-AVGNDS-LSTH010 | Average number of days             |
        |                         | per winter where tmin is less than |
        |                         | or equal to 10F                    |
        +-------------------------+------------------------------------+
        | DJF-TMIN-AVGNDS-LSTH020 | Average number of days             |
        |                         | per winter where tmin is less than |
        |                         | or equal to 20F                    |
        +-------------------------+------------------------------------+
        | DJF-TMIN-AVGNDS-LSTH032 | Average number of days             |
        |                         | per winter where tmin is less than |
        |                         | or equal to 32F                    |
        +-------------------------+------------------------------------+
        | DJF-TMIN-AVGNDS-LSTH040 | Average number of days             |
        |                         | per winter where tmin is less than |
        |                         | or equal to 40F                    |
        +-------------------------+------------------------------------+
        | DJF-TMIN-AVGNDS-LSTH050 | Average number of days             |
        |                         | per winter where tmin is less than |
        |                         | or equal to 50F                    |
        +-------------------------+------------------------------------+
        | DJF-TMIN-AVGNDS-LSTH060 | Average number of days             |
        |                         | per winter where tmin is less than |
        |                         | or equal to 60F                    |
        +-------------------------+------------------------------------+
        | DJF-TMIN-AVGNDS-LSTH070 | Average number of days             |
        |                         | per winter where tmin is less than |
        |                         | or equal to 70F                    |
        +-------------------------+------------------------------------+
        | DJF-TMIN-NORMAL         | Average winter                     |
        |                         | minimum temperature                |
        +-------------------------+------------------------------------+
        | JJA-CLDD-BASE45         | Average summer                     |
        |                         | cooling degree days with base 45F  |
        +-------------------------+------------------------------------+
        | JJA-CLDD-BASE50         | Average summer                     |
        |                         | cooling degree days with base 50F  |
        +-------------------------+------------------------------------+
        | JJA-CLDD-BASE55         | Average summer                     |
        |                         | cooling degree days with base 55F  |
        +-------------------------+------------------------------------+
        | JJA-CLDD-BASE57         | Average summer                     |
        |                         | cooling degree days with base 57F  |
        +-------------------------+------------------------------------+
        | JJA-CLDD-BASE60         | Average summer                     |
        |                         | cooling degree days with base 60F  |
        +-------------------------+------------------------------------+
        | JJA-CLDD-BASE70         | Average summer                     |
        |                         | cooling degree days with base 70F  |
        +-------------------------+------------------------------------+
        | JJA-CLDD-BASE72         | Average summer                     |
        |                         | cooling degree days with base 72F  |
        +-------------------------+------------------------------------+
        | JJA-CLDD-NORMAL         | Average summer                     |
        |                         | cooling degree days with base 65F  |
        +-------------------------+------------------------------------+
        | JJA-DUTR-NORMAL         | Average summer                     |
        |                         | diurnal temperature range          |
        +-------------------------+------------------------------------+
        | JJA-GRDD-BASE40         | Average summer                     |
        |                         | growing degree days with base 40F  |
        +-------------------------+------------------------------------+
        | JJA-GRDD-BASE45         | Average summer                     |
        |                         | growing degree days with base 45F  |
        +-------------------------+------------------------------------+
        | JJA-GRDD-BASE50         | Average summer                     |
        |                         | growing degree days with base 50F  |
        +-------------------------+------------------------------------+
        | JJA-GRDD-BASE55         | Average summer                     |
        |                         | growing degree days with base 55F  |
        +-------------------------+------------------------------------+
        | JJA-GRDD-BASE57         | Average summer                     |
        |                         | growing degree days with base 57F  |
        +-------------------------+------------------------------------+
        | JJA-GRDD-BASE60         | Average summer                     |
        |                         | growing degree days with base 60F  |
        +-------------------------+------------------------------------+
        | JJA-GRDD-BASE65         | Average summer                     |
        |                         | growing degree days with base 65F  |
        +-------------------------+------------------------------------+
        | JJA-GRDD-BASE70         | Average summer                     |
        |                         | growing degree days with base 70F  |
        +-------------------------+------------------------------------+
        | JJA-GRDD-BASE72         | Average summer                     |
        |                         | growing degree days with base 72F  |
        +-------------------------+------------------------------------+
        | JJA-GRDD-TB4886         | Average summer                     |
        |                         | growing degree days with truncated |
        |                         | bases 48F and 86F                  |
        +-------------------------+------------------------------------+
        | JJA-GRDD-TB5086         | Average summer                     |
        |                         | growing degree days with truncated |
        |                         | bases 50F and 86F                  |
        +-------------------------+------------------------------------+
        | JJA-HTDD-BASE40         | Average summer                     |
        |                         | heating degree days with base 40F  |
        +-------------------------+------------------------------------+
        | JJA-HTDD-BASE45         | Average summer                     |
        |                         | heating degree days with base 45F  |
        +-------------------------+------------------------------------+
        | JJA-HTDD-BASE50         | Average summer                     |
        |                         | heating degree days with base 50F  |
        +-------------------------+------------------------------------+
        | JJA-HTDD-BASE55         | Average summer                     |
        |                         | heating degree days with base 55F  |
        +-------------------------+------------------------------------+
        | JJA-HTDD-BASE57         | Average summer                     |
        |                         | heating degree days with base 57F  |
        +-------------------------+------------------------------------+
        | JJA-HTDD-BASE60         | Average summer                     |
        |                         | heating degree days with base 60F  |
        +-------------------------+------------------------------------+
        | JJA-HTDD-NORMAL         | Average summer                     |
        |                         | heating degree days with base 65F  |
        +-------------------------+------------------------------------+
        | JJA-PRCP-AVGNDS-GE001HI | Average number of                  |
        |                         | days during June-August with       |
        |                         | precipitation >= 0.01 inches       |
        +-------------------------+------------------------------------+
        | JJA-PRCP-AVGNDS-GE010HI | Average number of                  |
        |                         | days during June-August with       |
        |                         | precipitation >= 0.10 inches       |
        +-------------------------+------------------------------------+
        | JJA-PRCP-AVGNDS-GE050HI | Average number of                  |
        |                         | days during June-August with       |
        |                         | precipitation >= 0.50 inches       |
        +-------------------------+------------------------------------+
        | JJA-PRCP-AVGNDS-GE100HI | Average number of                  |
        |                         | days during June-August with       |
        |                         | precipitation >= 1.00 inches       |
        +-------------------------+------------------------------------+
        | JJA-PRCP-NORMAL         | Average seasonal                   |
        |                         | precipitation totals for June-     |
        |                         | August                             |
        +-------------------------+------------------------------------+
        | JJA-SNOW-AVGNDS-GE001TI | Average number of                  |
        |                         | days during June-August with       |
        |                         | snowfall >= 0.1 inches             |
        +-------------------------+------------------------------------+
        | JJA-SNOW-AVGNDS-GE010TI | Average number of                  |
        |                         | days during June-August with       |
        |                         | snowfall >= 1.0 inches             |
        +-------------------------+------------------------------------+
        | JJA-SNOW-AVGNDS-GE030TI | Average number of                  |
        |                         | days during June-August with       |
        |                         | snowfall >= 3.0 inches             |
        +-------------------------+------------------------------------+
        | JJA-SNOW-AVGNDS-GE050TI | Average number of                  |
        |                         | days during June-August with       |
        |                         | snowfall >= 5.0 inches             |
        +-------------------------+------------------------------------+
        | JJA-SNOW-AVGNDS-GE100TI | Average number of                  |
        |                         | days during June-August with       |
        |                         | snowfall >= 10.0 inches            |
        +-------------------------+------------------------------------+
        | JJA-SNOW-NORMAL         | Average seasonal                   |
        |                         | snowfall totals for June- August   |
        +-------------------------+------------------------------------+
        | JJA-SNWD-AVGNDS-GE001WI | Average number of                  |
        |                         | days during June-August with snow  |
        |                         | depth >= 1 inch                    |
        +-------------------------+------------------------------------+
        | JJA-SNWD-AVGNDS-GE003WI | Average number of                  |
        |                         | days during June-August with snow  |
        |                         | depth >= 3 inches                  |
        +-------------------------+------------------------------------+
        | JJA-SNWD-AVGNDS-GE005WI | Average number of                  |
        |                         | days during June-August with snow  |
        |                         | depth >= 5 inches                  |
        +-------------------------+------------------------------------+
        | JJA-SNWD-AVGNDS-GE010WI | Average number of                  |
        |                         | days during June-August with snow  |
        |                         | depth >= 10 inches                 |
        +-------------------------+------------------------------------+
        | JJA-TAVG-NORMAL         | Average summer                     |
        |                         | average temperature                |
        +-------------------------+------------------------------------+
        | JJA-TMAX-AVGNDS-GRTH040 | Average number of days             |
        |                         | per summer where tmax is greater   |
        |                         | than or equal to 40F               |
        +-------------------------+------------------------------------+
        | JJA-TMAX-AVGNDS-GRTH050 | Average number of days             |
        |                         | per summer where tmax is greater   |
        |                         | than or equal to 50F               |
        +-------------------------+------------------------------------+
        | JJA-TMAX-AVGNDS-GRTH060 | Average number of days             |
        |                         | per summer where tmax is greater   |
        |                         | than or equal to 60F               |
        +-------------------------+------------------------------------+
        | JJA-TMAX-AVGNDS-GRTH070 | Average number of days             |
        |                         | per summer where tmax is greater   |
        |                         | than or equal to 70F               |
        +-------------------------+------------------------------------+
        | JJA-TMAX-AVGNDS-GRTH080 | Average number of days             |
        |                         | per summer where tmax is greater   |
        |                         | than or equal to 80F               |
        +-------------------------+------------------------------------+
        | JJA-TMAX-AVGNDS-GRTH090 | Average number of days             |
        |                         | per summer where tmax is greater   |
        |                         | than or equal to 90F               |
        +-------------------------+------------------------------------+
        | JJA-TMAX-AVGNDS-GRTH100 | Average number of days             |
        |                         | per summer where tmax is greater   |
        |                         | than or equal to 100F              |
        +-------------------------+------------------------------------+
        | JJA-TMAX-AVGNDS-LSTH032 | Average number of days             |
        |                         | per summer where tmax is less than |
        |                         | or equal to 32F                    |
        +-------------------------+------------------------------------+
        | JJA-TMAX-NORMAL         | Average summer                     |
        |                         | maximum temperature                |
        +-------------------------+------------------------------------+
        | JJA-TMIN-AVGNDS-LSTH000 | Average number of days             |
        |                         | per summer where tmin is less than |
        |                         | or equal to 0F                     |
        +-------------------------+------------------------------------+
        | JJA-TMIN-AVGNDS-LSTH010 | Average number of days             |
        |                         | per summer where tmin is less than |
        |                         | or equal to 10F                    |
        +-------------------------+------------------------------------+
        | JJA-TMIN-AVGNDS-LSTH020 | Average number of days             |
        |                         | per summer where tmin is less than |
        |                         | or equal to 20F                    |
        +-------------------------+------------------------------------+
        | JJA-TMIN-AVGNDS-LSTH032 | Average number of days             |
        |                         | per summer where tmin is less than |
        |                         | or equal to 32F                    |
        +-------------------------+------------------------------------+
        | JJA-TMIN-AVGNDS-LSTH040 | Average number of days             |
        |                         | per summer where tmin is less than |
        |                         | or equal to 40F                    |
        +-------------------------+------------------------------------+
        | JJA-TMIN-AVGNDS-LSTH050 | Average number of days             |
        |                         | per summer where tmin is less than |
        |                         | or equal to 50F                    |
        +-------------------------+------------------------------------+
        | JJA-TMIN-AVGNDS-LSTH060 | Average number of days             |
        |                         | per summer where tmin is less than |
        |                         | or equal to 60F                    |
        +-------------------------+------------------------------------+
        | JJA-TMIN-AVGNDS-LSTH070 | Average number of days             |
        |                         | per summer where tmin is less than |
        |                         | or equal to 70F                    |
        +-------------------------+------------------------------------+
        | JJA-TMIN-NORMAL         | Average summer                     |
        |                         | minimum temperature                |
        +-------------------------+------------------------------------+
        | MAM-CLDD-BASE45         | Average spring                     |
        |                         | cooling degree days with base 45F  |
        +-------------------------+------------------------------------+
        | MAM-CLDD-BASE50         | Average spring                     |
        |                         | cooling degree days with base 50F  |
        +-------------------------+------------------------------------+
        | MAM-CLDD-BASE55         | Average spring                     |
        |                         | cooling degree days with base 55F  |
        +-------------------------+------------------------------------+
        | MAM-CLDD-BASE57         | Average spring                     |
        |                         | cooling degree days with base 57F  |
        +-------------------------+------------------------------------+
        | MAM-CLDD-BASE60         | Average spring                     |
        |                         | cooling degree days with base 60F  |
        +-------------------------+------------------------------------+
        | MAM-CLDD-BASE70         | Average spring                     |
        |                         | cooling degree days with base 70F  |
        +-------------------------+------------------------------------+
        | MAM-CLDD-BASE72         | Average spring                     |
        |                         | cooling degree days with base 72F  |
        +-------------------------+------------------------------------+
        | MAM-CLDD-NORMAL         | Average spring                     |
        |                         | cooling degree days with base 65F  |
        +-------------------------+------------------------------------+
        | MAM-DUTR-NORMAL         | Average spring                     |
        |                         | diurnal temperature range          |
        +-------------------------+------------------------------------+
        | MAM-GRDD-BASE40         | Average spring                     |
        |                         | growing degree days with base 40F  |
        +-------------------------+------------------------------------+
        | MAM-GRDD-BASE45         | Average spring                     |
        |                         | growing degree days with base 45F  |
        +-------------------------+------------------------------------+
        | MAM-GRDD-BASE50         | Average spring                     |
        |                         | growing degree days with base 50F  |
        +-------------------------+------------------------------------+
        | MAM-GRDD-BASE55         | Average spring                     |
        |                         | growing degree days with base 55F  |
        +-------------------------+------------------------------------+
        | MAM-GRDD-BASE57         | Average spring                     |
        |                         | growing degree days with base 57F  |
        +-------------------------+------------------------------------+
        | MAM-GRDD-BASE60         | Average spring                     |
        |                         | growing degree days with base 60F  |
        +-------------------------+------------------------------------+
        | MAM-GRDD-BASE65         | Average spring                     |
        |                         | growing degree days with base 65F  |
        +-------------------------+------------------------------------+
        | MAM-GRDD-BASE70         | Average spring                     |
        |                         | growing degree days with base 70F  |
        +-------------------------+------------------------------------+
        | MAM-GRDD-BASE72         | Average spring                     |
        |                         | growing degree days with base 72F  |
        +-------------------------+------------------------------------+
        | MAM-GRDD-TB4886         | Average summer                     |
        |                         | growing degree days with truncated |
        |                         | bases 48F and 86F                  |
        +-------------------------+------------------------------------+
        | MAM-GRDD-TB5086         | Average summer                     |
        |                         | growing degree days with truncated |
        |                         | bases 50F and 86F                  |
        +-------------------------+------------------------------------+
        | MAM-HTDD-BASE40         | Average spring                     |
        |                         | heating degree days with base 40F  |
        +-------------------------+------------------------------------+
        | MAM-HTDD-BASE45         | Average spring                     |
        |                         | heating degree days with base 45F  |
        +-------------------------+------------------------------------+
        | MAM-HTDD-BASE50         | Average spring                     |
        |                         | heating degree days with base 50F  |
        +-------------------------+------------------------------------+
        | MAM-HTDD-BASE55         | Average spring                     |
        |                         | heating degree days with base 55F  |
        +-------------------------+------------------------------------+
        | MAM-HTDD-BASE57         | Average spring                     |
        |                         | heating degree days with base 57F  |
        +-------------------------+------------------------------------+
        | MAM-HTDD-BASE60         | Average spring                     |
        |                         | heating degree days with base 60F  |
        +-------------------------+------------------------------------+
        | MAM-HTDD-NORMAL         | Average spring                     |
        |                         | heating degree days with base 65F  |
        +-------------------------+------------------------------------+
        | MAM-PRCP-AVGNDS-GE001HI | Average number of                  |
        |                         | days during March-May with         |
        |                         | precipitation >= 0.01 inches       |
        +-------------------------+------------------------------------+
        | MAM-PRCP-AVGNDS-GE010HI | Average number of                  |
        |                         | days during March-May with         |
        |                         | precipitation >= a 0.10 inches     |
        +-------------------------+------------------------------------+
        | MAM-PRCP-AVGNDS-GE050HI | Average number of                  |
        |                         | days during March-May with         |
        |                         | precipitation >= 0.50 inches       |
        +-------------------------+------------------------------------+
        | MAM-PRCP-AVGNDS-GE100HI | Average number of                  |
        |                         | days during March-May with         |
        |                         | precipitation >= 1.00 inches       |
        +-------------------------+------------------------------------+
        | MAM-PRCP-NORMAL         | Average seasonal                   |
        |                         | precipitation totals for March-    |
        |                         | May                                |
        +-------------------------+------------------------------------+
        | MAM-SNOW-AVGNDS-GE001TI | Average number of                  |
        |                         | days during March-May with         |
        |                         | snowfall >= 0.1 inches             |
        +-------------------------+------------------------------------+
        | MAM-SNOW-AVGNDS-GE010TI | Average number of                  |
        |                         | days during March-May with         |
        |                         | snowfall >= 1.0 inches             |
        +-------------------------+------------------------------------+
        | MAM-SNOW-AVGNDS-GE030TI | Average number of                  |
        |                         | days during March-May with         |
        |                         | snowfall >= 3.0 inches             |
        +-------------------------+------------------------------------+
        | MAM-SNOW-AVGNDS-GE050TI | Average number of                  |
        |                         | days during March-May with         |
        |                         | snowfall >= 5.0 inches             |
        +-------------------------+------------------------------------+
        | MAM-SNOW-AVGNDS-GE100TI | Average number of                  |
        |                         | days during March-May with         |
        |                         | snowfall >= 10.0 inches            |
        +-------------------------+------------------------------------+
        | MAM-SNOW-NORMAL         | Average seasonal                   |
        |                         | snowfall totals for March- May     |
        +-------------------------+------------------------------------+
        | MAM-SNWD-AVGNDS-GE001WI | Average number of                  |
        |                         | days during March-May with snow    |
        |                         | depth >= 1 inch                    |
        +-------------------------+------------------------------------+
        | MAM-SNWD-AVGNDS-GE003WI | Average number of                  |
        |                         | days during March-May with snow    |
        |                         | depth >= 3 inches                  |
        +-------------------------+------------------------------------+
        | MAM-SNWD-AVGNDS-GE005WI | Average number of                  |
        |                         | days during March-May with snow    |
        |                         | depth >= 5 inches                  |
        +-------------------------+------------------------------------+
        | MAM-SNWD-AVGNDS-GE010WI | Average number of                  |
        |                         | days during March-May with snow    |
        |                         | depth >= 10 inches                 |
        +-------------------------+------------------------------------+
        | MAM-TAVG-NORMAL         | Average spring                     |
        |                         | average temperature                |
        +-------------------------+------------------------------------+
        | MAM-TMAX-AVGNDS-GRTH040 | Average number of days             |
        |                         | per spring where tmax is greater   |
        |                         | than or equal to 40F               |
        +-------------------------+------------------------------------+
        | MAM-TMAX-AVGNDS-GRTH050 | Average number of days             |
        |                         | per spring where tmax is greater   |
        |                         | than or equal to 50F               |
        +-------------------------+------------------------------------+
        | MAM-TMAX-AVGNDS-GRTH060 | Average number of days             |
        |                         | per spring where tmax is greater   |
        |                         | than or equal to 60F               |
        +-------------------------+------------------------------------+
        | MAM-TMAX-AVGNDS-GRTH070 | Average number of days             |
        |                         | per spring where tmax is greater   |
        |                         | than or equal to 70F               |
        +-------------------------+------------------------------------+
        | MAM-TMAX-AVGNDS-GRTH080 | Average number of days             |
        |                         | per spring where tmax is greater   |
        |                         | than or equal to 80F               |
        +-------------------------+------------------------------------+
        | MAM-TMAX-AVGNDS-GRTH090 | Average number of days             |
        |                         | per spring where tmax is greater   |
        |                         | than or equal to 90F               |
        +-------------------------+------------------------------------+
        | MAM-TMAX-AVGNDS-GRTH100 | Average number of days             |
        |                         | per spring where tmax is greater   |
        |                         | than or equal to 100F              |
        +-------------------------+------------------------------------+
        | MAM-TMAX-AVGNDS-LSTH032 | Average number of days             |
        |                         | per spring where tmax is less than |
        |                         | or equal to 32F                    |
        +-------------------------+------------------------------------+
        | MAM-TMAX-NORMAL         | Average spring                     |
        |                         | maximum temperature                |
        +-------------------------+------------------------------------+
        | MAM-TMIN-AVGNDS-LSTH000 | Average number of days             |
        |                         | per spring where tmin is less than |
        |                         | or equal to 0F                     |
        +-------------------------+------------------------------------+
        | MAM-TMIN-AVGNDS-LSTH010 | Average number of days             |
        |                         | per spring where tmin is less than |
        |                         | or equal to 10F                    |
        +-------------------------+------------------------------------+
        | MAM-TMIN-AVGNDS-LSTH020 | Average number of days             |
        |                         | per spring where tmin is less than |
        |                         | or equal to 20F                    |
        +-------------------------+------------------------------------+
        | MAM-TMIN-AVGNDS-LSTH032 | Average number of days             |
        |                         | per spring where tmin is less than |
        |                         | or equal to 32F                    |
        +-------------------------+------------------------------------+
        | MAM-TMIN-AVGNDS-LSTH040 | Average number of days             |
        |                         | per spring where tmin is less than |
        |                         | or equal to 40F                    |
        +-------------------------+------------------------------------+
        | MAM-TMIN-AVGNDS-LSTH050 | Average number of days             |
        |                         | per spring where tmin is less than |
        |                         | or equal to 50F                    |
        +-------------------------+------------------------------------+
        | MAM-TMIN-AVGNDS-LSTH060 | Average number of days             |
        |                         | per spring where tmin is less than |
        |                         | or equal to 60F                    |
        +-------------------------+------------------------------------+
        | MAM-TMIN-AVGNDS-LSTH070 | Average number of days             |
        |                         | per spring where tmin is less than |
        |                         | or equal to 70F                    |
        +-------------------------+------------------------------------+
        | MAM-TMIN-NORMAL         | Average spring                     |
        |                         | minimum temperature                |
        +-------------------------+------------------------------------+
        | SON-CLDD-BASE45         | Average autumn                     |
        |                         | cooling degree days with base 45F  |
        +-------------------------+------------------------------------+
        | SON-CLDD-BASE50         | Average autumn                     |
        |                         | cooling degree days with base 50F  |
        +-------------------------+------------------------------------+
        | SON-CLDD-BASE55         | Average autumn                     |
        |                         | cooling degree days with base 55F  |
        +-------------------------+------------------------------------+
        | SON-CLDD-BASE57         | Average autumn                     |
        |                         | cooling degree days with base 57F  |
        +-------------------------+------------------------------------+
        | SON-CLDD-BASE60         | Average autumn                     |
        |                         | cooling degree days with base 60F  |
        +-------------------------+------------------------------------+
        | SON-CLDD-BASE70         | Average autumn                     |
        |                         | cooling degree days with base 70F  |
        +-------------------------+------------------------------------+
        | SON-CLDD-BASE72         | Average autumn                     |
        |                         | cooling degree days with base 72F  |
        +-------------------------+------------------------------------+
        | SON-CLDD-NORMAL         | Average autumn                     |
        |                         | cooling degree days with base 65F  |
        +-------------------------+------------------------------------+
        | SON-DUTR-NORMAL         | Average autumn                     |
        |                         | diurnal temperature range          |
        +-------------------------+------------------------------------+
        | SON-GRDD-BASE40         | Average fall growing               |
        |                         | degree days with base 40F          |
        +-------------------------+------------------------------------+
        | SON-GRDD-BASE45         | Average fall growing               |
        |                         | degree days with base 45F          |
        +-------------------------+------------------------------------+
        | SON-GRDD-BASE50         | Average fall growing               |
        |                         | degree days with base 50F          |
        +-------------------------+------------------------------------+
        | SON-GRDD-BASE55         | Average fall growing               |
        |                         | degree days with base 55F          |
        +-------------------------+------------------------------------+
        | SON-GRDD-BASE57         | Average fall growing               |
        |                         | degree days with base 57F          |
        +-------------------------+------------------------------------+
        | SON-GRDD-BASE60         | Average fall growing               |
        |                         | degree days with base 60F          |
        +-------------------------+------------------------------------+
        | SON-GRDD-BASE65         | Average fall growing               |
        |                         | degree days with base 65F          |
        +-------------------------+------------------------------------+
        | SON-GRDD-BASE70         | Average fall growing               |
        |                         | degree days with base 70F          |
        +-------------------------+------------------------------------+
        | SON-GRDD-BASE72         | Average fall growing               |
        |                         | degree days with base 72F          |
        +-------------------------+------------------------------------+
        | SON-GRDD-TB4886         | Average summer                     |
        |                         | growing degree days with truncated |
        |                         | bases 48F and 86F                  |
        +-------------------------+------------------------------------+
        | SON-GRDD-TB5086         | Average summer                     |
        |                         | growing degree days with truncated |
        |                         | bases 50F and 86F                  |
        +-------------------------+------------------------------------+
        | SON-HTDD-BASE40         | Average autumn                     |
        |                         | heating degree days with base 40F  |
        +-------------------------+------------------------------------+
        | SON-HTDD-BASE45         | Average autumn                     |
        |                         | heating degree days with base 45F  |
        +-------------------------+------------------------------------+
        | SON-HTDD-BASE50         | Average autumn                     |
        |                         | heating degree days with base 50F  |
        +-------------------------+------------------------------------+
        | SON-HTDD-BASE55         | Average autumn                     |
        |                         | heating degree days with base 55F  |
        +-------------------------+------------------------------------+
        | SON-HTDD-BASE57         | Average autumn                     |
        |                         | heating degree days with base 57F  |
        +-------------------------+------------------------------------+
        | SON-HTDD-BASE60         | Average autumn                     |
        |                         | heating degree days with base 60F  |
        +-------------------------+------------------------------------+
        | SON-HTDD-NORMAL         | Average autumn                     |
        |                         | heating degree days with base 65F  |
        +-------------------------+------------------------------------+
        | SON-PRCP-AVGNDS-GE001HI | Average number of                  |
        |                         | days during September- November    |
        |                         | with precipitation >= 0.01 inches  |
        +-------------------------+------------------------------------+
        | SON-PRCP-AVGNDS-GE010HI | Average number of                  |
        |                         | days during September- November    |
        |                         | with precipitation >= 0.10 inches  |
        +-------------------------+------------------------------------+
        | SON-PRCP-AVGNDS-GE050HI | Average number of                  |
        |                         | days during September- November    |
        |                         | with precipitation >= 0.50 inches  |
        +-------------------------+------------------------------------+
        | SON-PRCP-AVGNDS-GE100HI | Average number of                  |
        |                         | days during September- November    |
        |                         | with precipitation >= 1.00 inches  |
        +-------------------------+------------------------------------+
        | SON-PRCP-NORMAL         | Average seasonal                   |
        |                         | precipitation totals for           |
        |                         | September- November                |
        +-------------------------+------------------------------------+
        | SON-SNOW-AVGNDS-GE001TI | Average number of                  |
        |                         | days during September- November    |
        |                         | with snowfall >= 0.1 inches        |
        +-------------------------+------------------------------------+
        | SON-SNOW-AVGNDS-GE010TI | Average number of                  |
        |                         | days during September- November    |
        |                         | with snowfall >= 1.0 inches        |
        +-------------------------+------------------------------------+
        | SON-SNOW-AVGNDS-GE030TI | Average number of                  |
        |                         | days during September- November    |
        |                         | with snowfall >= 3.0 inches        |
        +-------------------------+------------------------------------+
        | SON-SNOW-AVGNDS-GE050TI | Average number of                  |
        |                         | days during September- November    |
        |                         | with snowfall >= 5.0 inches        |
        +-------------------------+------------------------------------+
        | SON-SNOW-AVGNDS-GE100TI | Average number of                  |
        |                         | days during September- November    |
        |                         | with snowfall >= 10.0 inches       |
        +-------------------------+------------------------------------+
        | SON-SNOW-NORMAL         | Average seasonal                   |
        |                         | snowfall totals for September-     |
        |                         | November                           |
        +-------------------------+------------------------------------+
        | SON-SNWD-AVGNDS-GE001WI | Average number of                  |
        |                         | days during September- November    |
        |                         | with snow depth >= 1 inch          |
        +-------------------------+------------------------------------+
        | SON-SNWD-AVGNDS-GE003WI | Average number of                  |
        |                         | days during September- November    |
        |                         | with snow depth >= 3 inches        |
        +-------------------------+------------------------------------+
        | SON-SNWD-AVGNDS-GE005WI | Average number of                  |
        |                         | days during September- November    |
        |                         | with snow depth >= 5 inches        |
        +-------------------------+------------------------------------+
        | SON-SNWD-AVGNDS-GE010WI | Average number of                  |
        |                         | days during September- November    |
        |                         | with snow depth >= 10 inches       |
        +-------------------------+------------------------------------+
        | SON-TAVG-NORMAL         | Average autumn                     |
        |                         | average temperature                |
        +-------------------------+------------------------------------+
        | SON-TMAX-AVGNDS-GRTH040 | Average number of days             |
        |                         | per autumn where tmax is greater   |
        |                         | than or equal to 40F               |
        +-------------------------+------------------------------------+
        | SON-TMAX-AVGNDS-GRTH050 | Average number of days             |
        |                         | per autumn where tmax is greater   |
        |                         | than or equal to 50F               |
        +-------------------------+------------------------------------+
        | SON-TMAX-AVGNDS-GRTH060 | Average number of days             |
        |                         | per autumn where tmax is greater   |
        |                         | than or equal to 60F               |
        +-------------------------+------------------------------------+
        | SON-TMAX-AVGNDS-GRTH070 | Average number of days             |
        |                         | per autumn where tmax is greater   |
        |                         | than or equal to 70F               |
        +-------------------------+------------------------------------+
        | SON-TMAX-AVGNDS-GRTH080 | Average number of days             |
        |                         | per autumn where tmax is greater   |
        |                         | than or equal to 80F               |
        +-------------------------+------------------------------------+
        | SON-TMAX-AVGNDS-GRTH090 | Average number of days             |
        |                         | per autumn where tmax is greater   |
        |                         | than or equal to 90F               |
        +-------------------------+------------------------------------+
        | SON-TMAX-AVGNDS-GRTH100 | Average number of days             |
        |                         | per autumn where tmax is greater   |
        |                         | than or equal to 100F              |
        +-------------------------+------------------------------------+
        | SON-TMAX-AVGNDS-LSTH032 | Average number of days             |
        |                         | per autumn where tmax is less than |
        |                         | or equal to 32F                    |
        +-------------------------+------------------------------------+
        | SON-TMAX-NORMAL         | Average autumn                     |
        |                         | maximum temperature                |
        +-------------------------+------------------------------------+
        | SON-TMIN-AVGNDS-LSTHxxx | Average number of days             |
        |                         | per autumn where tmin is less than |
        |                         | or equal to 'xxx' degree F.        |
        |                         | Where 'xxx' is one of 000, 010,    |
        |                         | 020, 032, 040, 050, 060, 070       |
        +-------------------------+------------------------------------+
        | SON-TMIN-NORMAL         | Average autumn                     |
        |                         | minimum temperature                |
        +-------------------------+------------------------------------+

    startdate
        Many different formats can be used here for the date
        string, however the closest to ISO8601, the better.

    enddate
        Many different formats can be used here for the date
        string, however the closest to ISO8601, the better."""
    tsutils._printiso(
        ncei_normal_ann(
            stationid, datatypeid=datetypeid, startdate=startdate, enddate=enddate
        )
    )


def ncei_normal_ann(stationid, datatypeid="", startdate="", enddate=""):
    r"""National Centers for Environmental Information (NCEI) annual normals."""
    df = ncei_cdo_json_to_df(
        r"http://www.ncdc.noaa.gov/cdo-web/api/v2/data",
        startdate=startdate,
        enddate=enddate,
        datasetid="NORMAL_ANN",
        stationid=stationid,
    )

    return df


# 2010-01-01, 2010-12-31, Normals Daily               , 1    , NORMAL_DLY
@mando.command("ncei_normal_dly", formatter_class=HelpFormatter, doctype="numpy")
def ncei_normal_dly_cli(stationid, datatypeid="", startdate="", enddate=""):
    r"""National Centers for Environmental Information (NCEI) Daily Normals.

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
    stationid
        Station ID.

    datatypeid
        The following table lists the datatypes available for the annual
        dataset.  If the datatypeid is not given defaults to getting all data
        available at that station.

        +-------------------------+------------------------------------+
        | Code                    | Description                        |
        +=========================+====================================+
        | DLY-CLDD-BASE45         | Average daily                      |
        |                         | cooling degree days with base 45F  |
        +-------------------------+------------------------------------+
        | DLY-CLDD-BASE50         | Average daily                      |
        |                         | cooling degree days with base 50F  |
        +-------------------------+------------------------------------+
        | DLY-CLDD-BASE55         | Average daily                      |
        |                         | cooling degree days with base 55F  |
        +-------------------------+------------------------------------+
        | DLY-CLDD-BASE57         | Average daily                      |
        |                         | cooling degree days with base 57F  |
        +-------------------------+------------------------------------+
        | DLY-CLDD-BASE60         | Average daily                      |
        |                         | cooling degree days with base 60F  |
        +-------------------------+------------------------------------+
        | DLY-CLDD-BASE70         | Average daily                      |
        |                         | cooling degree days with base 70F  |
        +-------------------------+------------------------------------+
        | DLY-CLDD-BASE72         | Average daily                      |
        |                         | cooling degree days with base 72F  |
        +-------------------------+------------------------------------+
        | DLY-CLDD-NORMAL         | Average daily                      |
        |                         | cooling degree days with base 65F  |
        +-------------------------+------------------------------------+
        | DLY-DUTR-NORMAL         | Average daily                      |
        |                         | diurnal temperature range          |
        +-------------------------+------------------------------------+
        | DLY-DUTR-STDDEV         | Long-term standard deviations of   |
        |                         | daily diurnal temperature range    |
        +-------------------------+------------------------------------+
        | DLY-GRDD-BASE40         | Average daily                      |
        |                         | growing degree days with base 40F  |
        +-------------------------+------------------------------------+
        | DLY-GRDD-BASE45         | Average daily                      |
        |                         | growing degree days with base 45F  |
        +-------------------------+------------------------------------+
        | DLY-GRDD-BASE50         | Average daily                      |
        |                         | growing degree days with base 50F  |
        +-------------------------+------------------------------------+
        | DLY-GRDD-BASE55         | Average daily                      |
        |                         | growing degree days with base 55F  |
        +-------------------------+------------------------------------+
        | DLY-GRDD-BASE57         | Average daily                      |
        |                         | growing degree days with base 57F  |
        +-------------------------+------------------------------------+
        | DLY-GRDD-BASE60         | Average daily                      |
        |                         | growing degree days with base 60F  |
        +-------------------------+------------------------------------+
        | DLY-GRDD-BASE65         | Average daily                      |
        |                         | growing degree days with base 65F  |
        +-------------------------+------------------------------------+
        | DLY-GRDD-BASE70         | Average daily                      |
        |                         | growing degree days with base 70F  |
        +-------------------------+------------------------------------+
        | DLY-GRDD-BASE72         | Average daily                      |
        |                         | growing degree days with base 72F  |
        +-------------------------+------------------------------------+
        | DLY-GRDD-TB4886         | Average daily                      |
        |                         | growing degree days with truncated |
        |                         | bases 48F and 86F                  |
        +-------------------------+------------------------------------+
        | DLY-GRDD-TB5086         | Average daily                      |
        |                         | growing degree days with truncated |
        |                         | bases 50F and 86F                  |
        +-------------------------+------------------------------------+
        | DLY-HTDD-BASE40         | Average daily                      |
        |                         | heating degree days with base 40F  |
        +-------------------------+------------------------------------+
        | DLY-HTDD-BASE45         | Average daily                      |
        |                         | heating degree days with base 45F  |
        +-------------------------+------------------------------------+
        | DLY-HTDD-BASE50         | Average daily                      |
        |                         | heating degree days with base 50F  |
        +-------------------------+------------------------------------+
        | DLY-HTDD-BASE55         | Average daily                      |
        |                         | heating degree days with base 55F  |
        +-------------------------+------------------------------------+
        | DLY-HTDD-BASE57         | Average daily                      |
        |                         | heating degree days with base 57F  |
        +-------------------------+------------------------------------+
        | DLY-HTDD-BASE60         | Average daily                      |
        |                         | heating degree days with base 60F  |
        +-------------------------+------------------------------------+
        | DLY-HTDD-NORMAL         | Average daily                      |
        |                         | heating degree days with base 65F  |
        +-------------------------+------------------------------------+
        | DLY-PRCP-25PCTL         | 25th percentiles of daily nonzero  |
        |                         | precipitation totals for 29-day    |
        |                         | windows centered on each day of    |
        |                         | the year                           |
        +-------------------------+------------------------------------+
        | DLY-PRCP-50PCTL         | 50th percentiles of daily nonzero  |
        |                         | precipitation totals for 29-day    |
        |                         | windows centered on each day of    |
        |                         | the year                           |
        +-------------------------+------------------------------------+
        | DLY-PRCP-75PCTL         | 75th percentiles of daily nonzero  |
        |                         | precipitation totals for 29-day    |
        |                         | windows centered on each day of    |
        |                         | the year                           |
        +-------------------------+------------------------------------+
        | DLY-PRCP-PCTALL-GE001HI | Probability of precipitation >=    |
        |                         | 0.01 inches for 29-day windows     |
        |                         | centered on each day of the year   |
        +-------------------------+------------------------------------+
        | DLY-PRCP-PCTALL-GE010HI | Probability of precipitation >=    |
        |                         | 0.10 inches for 29-day windows     |
        |                         | centered on each day of the year   |
        +-------------------------+------------------------------------+
        | DLY-PRCP-PCTALL-GE050HI | Probability of precipitation >=    |
        |                         | 0.50 inches for 29-day windows     |
        |                         | centered on each day of the year   |
        +-------------------------+------------------------------------+
        | DLY-PRCP-PCTALL-GE100HI | Probability of precipitation >=    |
        |                         | 1.00 inches for 29-day windows     |
        |                         | centered on each day of the year   |
        +-------------------------+------------------------------------+
        | DLY-SNOW-25PCTL         | 25th percentiles of daily nonzero  |
        |                         | snowfall totals for 29-day windows |
        |                         | centered on each day of the year   |
        +-------------------------+------------------------------------+
        | DLY-SNOW-50PCTL         | 50th percentiles of daily nonzero  |
        |                         | snowfall totals for 29-day windows |
        |                         | centered on each day of the year   |
        +-------------------------+------------------------------------+
        | DLY-SNOW-75PCTL         | 75th percentiles of daily nonzero  |
        |                         | snowfall totals for 29-day windows |
        |                         | centered on each day of the year   |
        +-------------------------+------------------------------------+
        | DLY-SNOW-PCTALL-GE001TI | Probability of snowfall >= 0.1     |
        |                         | inches for 29-day windows centered |
        |                         | on each day of the year            |
        +-------------------------+------------------------------------+
        | DLY-SNOW-PCTALL-GE010TI | Probability of snowfall >= 1.0     |
        |                         | inches for 29-day windows centered |
        |                         | on each day of the year            |
        +-------------------------+------------------------------------+
        | DLY-SNOW-PCTALL-GE030TI | Probability of snowfall >= 3.0     |
        |                         | inches for 29-day windows centered |
        |                         | on each day of the year            |
        +-------------------------+------------------------------------+
        | DLY-SNOW-PCTALL-GE050TI | Probability of snowfall >= 5.0     |
        |                         | inches for 29-day windows centered |
        |                         | on each day of the year            |
        +-------------------------+------------------------------------+
        | DLY-SNOW-PCTALL-GE100TI | Probability of snowfall >= 10      |
        |                         | inches for 29-day windows centered |
        |                         | on each day of the year            |
        +-------------------------+------------------------------------+
        | DLY-SNWD-25PCTL         | 25th percentiles of daily nonzero  |
        |                         | snow depth for 29-day windows      |
        |                         | centered on each day of the year   |
        +-------------------------+------------------------------------+
        | DLY-SNWD-50PCTL         | 50th percentiles of daily nonzero  |
        |                         | snow depth for 29-day windows      |
        |                         | centered on each day of the year   |
        +-------------------------+------------------------------------+
        | DLY-SNWD-75PCTL         | 75th percentiles of daily nonzero  |
        |                         | snow depth for 29-day windows      |
        |                         | centered on each day of the year   |
        +-------------------------+------------------------------------+
        | DLY-SNWD-PCTALL-GE001WI | Probability of snow depth >= 1     |
        |                         | inch for 29-day windows centered   |
        |                         | on each day of the year            |
        +-------------------------+------------------------------------+
        | DLY-SNWD-PCTALL-GE003WI | Probability of snow depth >= 3     |
        |                         | inches for 29-day windows centered |
        |                         | on each day of the year            |
        +-------------------------+------------------------------------+
        | DLY-SNWD-PCTALL-GE005WI | Probability of snow depth >= 5     |
        |                         | inches for 29-day windows centered |
        |                         | on each day of the year            |
        +-------------------------+------------------------------------+
        | DLY-SNWD-PCTALL-GE010WI | Probability of snow depth >= 10    |
        |                         | inches for 29-day windows centered |
        |                         | on each day of the year            |
        +-------------------------+------------------------------------+
        | DLY-TAVG-NORMAL         | Average daily                      |
        |                         | average temperature                |
        +-------------------------+------------------------------------+
        | DLY-TAVG-STDDEV         | Long-term standard deviations of   |
        |                         | daily average temperature          |
        +-------------------------+------------------------------------+
        | DLY-TMAX-NORMAL         | Average daily                      |
        |                         | maximum temperature                |
        +-------------------------+------------------------------------+
        | DLY-TMAX-STDDEV         | Long-term standard deviations of   |
        |                         | daily maximum temperature          |
        +-------------------------+------------------------------------+
        | DLY-TMIN-NORMAL         | Average daily                      |
        |                         | minimum temperature                |
        +-------------------------+------------------------------------+
        | DLY-TMIN-STDDEV         | Long-term standard deviations of   |
        |                         | daily minimum temperature          |
        +-------------------------+------------------------------------+
        | MTD-PRCP-NORMAL         | Average month-to-date              |
        |                         | precipitation totals               |
        +-------------------------+------------------------------------+
        | MTD-SNOW-NORMAL         | Average month-to-date              |
        |                         | snowfall totals                    |
        +-------------------------+------------------------------------+
        | YTD-PRCP-NORMAL         | Average year-to-date               |
        |                         | precipitation totals               |
        +-------------------------+------------------------------------+
        | YTD-SNOW-NORMAL         | Average year-to-date               |
        |                         | snowfall totals                    |
        +-------------------------+------------------------------------+

    startdate
        Start date in ISO8601 format.

    enddate
        End date in ISO8601 format."""
    tsutils._printiso(
        ncei_normal_dly(
            stationid, datatypeid=datatypeid, startdate=startdate, enddate=enddate
        )
    )


def ncei_normal_dly(stationid, datatypeid="", startdate="", enddate=""):
    r"""National Centers for Environmental Information (NCEI) Daily Normals."""
    df = ncei_cdo_json_to_df(
        r"http://www.ncdc.noaa.gov/cdo-web/api/v2/data",
        startdate=startdate,
        enddate=enddate,
        datasetid="NORMAL_DLY",
        stationid=stationid,
    )

    return df


# 2010-01-01, 2010-12-31, Normals Hourly              , 1    , NORMAL_HLY
@mando.command("ncei_normal_hly", formatter_class=HelpFormatter, doctype="numpy")
def ncei_normal_hly_cli(stationid, datatypeid="", startdate="", enddate=""):
    r"""National Centers for Environmental Information (NCEI) GHCND Normal hourly.

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
    stationid
        Station ID.

    datatypeid
        The following table lists the datatypes available for the annual
        dataset.  If the datatypeid is not given defaults to getting all data
        available at that station.

        +-----------------+------------------------------------+
        | Code            | Description                        |
        +=================+====================================+
        | HLY-CLDH-NORMAL | Cooling degree hours               |
        +-----------------+------------------------------------+
        | HLY-CLOD-PCTBKN | Clouds broken percentage           |
        +-----------------+------------------------------------+
        | HLY-CLOD-PCTCLR | Clouds clear percentage            |
        +-----------------+------------------------------------+
        | HLY-CLOD-PCTFEW | Clouds few percentage              |
        +-----------------+------------------------------------+
        | HLY-CLOD-PCTOVC | Clouds overcast percentage         |
        +-----------------+------------------------------------+
        | HLY-CLOD-PCTSCT | Clouds scattered percentage        |
        +-----------------+------------------------------------+
        | HLY-DEWP-10PCTL | Dew point 10th percentile          |
        +-----------------+------------------------------------+
        | HLY-DEWP-90PCTL | Dew point 90th percentile          |
        +-----------------+------------------------------------+
        | HLY-DEWP-NORMAL | Dew point mean                     |
        +-----------------+------------------------------------+
        | HLY-HIDX-NORMAL | Heat index mean                    |
        +-----------------+------------------------------------+
        | HLY-HTDH-NORMAL | Heating degree hours               |
        +-----------------+------------------------------------+
        | HLY-PRES-10PCTL | Sea level pressure 10th percentile |
        +-----------------+------------------------------------+
        | HLY-PRES-90PCTL | Sea level pressure 90th percentile |
        +-----------------+------------------------------------+
        | HLY-PRES-NORMAL | Sea level pressure mean            |
        +-----------------+------------------------------------+
        | HLY-TEMP-10PCTL | Temperature 10th percentile        |
        +-----------------+------------------------------------+
        | HLY-TEMP-90PCTL | Temperature 90th percentile        |
        +-----------------+------------------------------------+
        | HLY-TEMP-NORMAL | Temperature mean                   |
        +-----------------+------------------------------------+
        | HLY-WCHL-NORMAL | Wind chill mean                    |
        +-----------------+------------------------------------+
        | HLY-WIND-1STDIR | Prevailing wind direction (1-8)    |
        +-----------------+------------------------------------+
        | HLY-WIND-1STPCT | Prevailing wind percentage         |
        +-----------------+------------------------------------+
        | HLY-WIND-2NDDIR | Secondary wind direction (1-8)     |
        +-----------------+------------------------------------+
        | HLY-WIND-2NDPCT | Secondary wind percentage          |
        +-----------------+------------------------------------+
        | HLY-WIND-AVGSPD | Average wind speed                 |
        +-----------------+------------------------------------+
        | HLY-WIND-PCTCLM | Percentage calm                    |
        +-----------------+------------------------------------+
        | HLY-WIND-VCTDIR | Mean wind vector direction         |
        +-----------------+------------------------------------+
        | HLY-WIND-VCTSPD | Mean wind vector magnitude         |
        +-----------------+------------------------------------+

    startdate
        Start date in ISO8601 format.

    enddate
        End date in ISO8601 format."""
    tsutils._printiso(
        ncei_normal_hly(
            stationid, datatypeid=datatypeid, startdate=startdate, enddate=enddate
        )
    )


def ncei_normal_hly(stationid, datatypeid="", startdate="", enddate=""):
    r"""National Centers for Environmental Information (NCEI) GHCND Normal hourly."""
    df = ncei_cdo_json_to_df(
        r"http://www.ncdc.noaa.gov/cdo-web/api/v2/data",
        startdate=startdate,
        enddate=enddate,
        datasetid="NORMAL_HLY",
        stationid=stationid,
    )

    return df


# 2010-01-01, 2010-12-01, Normals Monthly             , 1    , NORMAL_MLY
@mando.command("ncei_normal_mly", formatter_class=HelpFormatter, doctype="numpy")
def ncei_normal_mly_cli(stationid, datatypeid="", startdate="", enddate=""):
    r"""National Centers for Environmental Information (NCEI) GHCND Monthly Summaries.

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
    stationid : str
        Station ID.

    datatypeid : str
        The following table lists the datatypes available for the annual
        dataset.  If the datatypeid is not given defaults to getting all data
        available at that station.

        +-------------------------+------------------------------------+
        | Code                    | Description                        |
        +=========================+====================================+
        | MLY-CLDD-BASE45         | Average monthly                    |
        |                         | cooling degree days with base 45F  |
        +-------------------------+------------------------------------+
        | MLY-CLDD-BASE50         | Average monthly                    |
        |                         | cooling degree days with base 50F  |
        +-------------------------+------------------------------------+
        | MLY-CLDD-BASE55         | Average monthly                    |
        |                         | cooling degree days with base 55F  |
        +-------------------------+------------------------------------+
        | MLY-CLDD-BASE57         | Average monthly                    |
        |                         | cooling degree days with base 57F  |
        +-------------------------+------------------------------------+
        | MLY-CLDD-BASE60         | Average monthly                    |
        |                         | cooling degree days with base 60F  |
        +-------------------------+------------------------------------+
        | MLY-CLDD-BASE70         | Average monthly                    |
        |                         | cooling degree days with base 70F  |
        +-------------------------+------------------------------------+
        | MLY-CLDD-BASE72         | Average monthly                    |
        |                         | cooling degree days with base 72F  |
        +-------------------------+------------------------------------+
        | MLY-CLDD-NORMAL         | Average monthly                    |
        |                         | cooling degree days with base 65F  |
        +-------------------------+------------------------------------+
        | MLY-DUTR-NORMAL         | Average monthly                    |
        |                         | diurnal temperature range          |
        +-------------------------+------------------------------------+
        | MLY-DUTR-STDDEV         | Long-term standard deviations of   |
        |                         | monthly diurnal temperature range  |
        +-------------------------+------------------------------------+
        | MLY-GRDD-BASE40         | Average monthly                    |
        |                         | growing degree days with base 40F  |
        +-------------------------+------------------------------------+
        | MLY-GRDD-BASE45         | Average monthly                    |
        |                         | growing degree days with base 45F  |
        +-------------------------+------------------------------------+
        | MLY-GRDD-BASE50         | Average monthly                    |
        |                         | growing degree days with base 50F  |
        +-------------------------+------------------------------------+
        | MLY-GRDD-BASE55         | Average monthly                    |
        |                         | growing degree days with base 55F  |
        +-------------------------+------------------------------------+
        | MLY-GRDD-BASE57         | Average monthly                    |
        |                         | growing degree days with base 57F  |
        +-------------------------+------------------------------------+
        | MLY-GRDD-BASE60         | Average monthly                    |
        |                         | growing degree days with base 60F  |
        +-------------------------+------------------------------------+
        | MLY-GRDD-BASE65         | Average monthly                    |
        |                         | growing degree days with base 65F  |
        +-------------------------+------------------------------------+
        | MLY-GRDD-BASE70         | Average monthly                    |
        |                         | growing degree days with base 70F  |
        +-------------------------+------------------------------------+
        | MLY-GRDD-BASE72         | Average monthly                    |
        |                         | growing degree days with base 72F  |
        +-------------------------+------------------------------------+
        | MLY-GRDD-TB4886         | Average monthly                    |
        |                         | growing degree days with truncated |
        |                         | bases 48F and 86F                  |
        +-------------------------+------------------------------------+
        | MLY-GRDD-TB5086         | Average monthly                    |
        |                         | growing degree days with truncated |
        |                         | bases 50F and 86F                  |
        +-------------------------+------------------------------------+
        | MLY-HTDD-BASE40         | Average monthly                    |
        |                         | heating degree days with base 40F  |
        +-------------------------+------------------------------------+
        | MLY-HTDD-BASE45         | Average monthly                    |
        |                         | heating degree days with base 45F  |
        +-------------------------+------------------------------------+
        | MLY-HTDD-BASE50         | Average monthly                    |
        |                         | heating degree days with base 50F  |
        +-------------------------+------------------------------------+
        | MLY-HTDD-BASE55         | Average monthly                    |
        |                         | heating degree days with base 55F  |
        +-------------------------+------------------------------------+
        | MLY-HTDD-BASE57         | Average monthly                    |
        |                         | heating degree days with base 57F  |
        +-------------------------+------------------------------------+
        | MLY-HTDD-BASE60         | Average monthly                    |
        |                         | heating degree days with base 60F  |
        +-------------------------+------------------------------------+
        | MLY-HTDD-NORMAL         | Average monthly                    |
        |                         | heating degree days with base 65F  |
        +-------------------------+------------------------------------+
        | MLY-PRCP-25PCTL         | 25th percentiles of monthly        |
        |                         | precipitation totals               |
        +-------------------------+------------------------------------+
        | MLY-PRCP-50PCTL         | 50th percentiles of monthly        |
        |                         | precipitation totals               |
        +-------------------------+------------------------------------+
        | MLY-PRCP-75PCTL         | 75th percentiles of monthly        |
        |                         | precipitation totals               |
        +-------------------------+------------------------------------+
        | MLY-PRCP-AVGNDS-GE001HI | Average number of                  |
        |                         | days per month with precipitation  |
        |                         | >= 0.01 inches                     |
        +-------------------------+------------------------------------+
        | MLY-PRCP-AVGNDS-GE010HI | Average number of                  |
        |                         | days per month with precipitation  |
        |                         | >= 0.10 inches                     |
        +-------------------------+------------------------------------+
        | MLY-PRCP-AVGNDS-GE050HI | Average number of                  |
        |                         | days per month with precipitation  |
        |                         | >= 0.50 inches                     |
        +-------------------------+------------------------------------+
        | MLY-PRCP-AVGNDS-GE100HI | Average number of                  |
        |                         | days per month with precipitation  |
        |                         | >= 1.00 inches                     |
        +-------------------------+------------------------------------+
        | MLY-PRCP-NORMAL         | Average monthly                    |
        |                         | precipitation totals               |
        +-------------------------+------------------------------------+
        | MLY-SNOW-25PCTL         | 25th percentiles of monthly        |
        |                         | snowfall totals                    |
        +-------------------------+------------------------------------+
        | MLY-SNOW-50PCTL         | 50th percentiles of monthly        |
        |                         | snowfall totals                    |
        +-------------------------+------------------------------------+
        | MLY-SNOW-75PCTL         | 75th percentiles of monthly        |
        |                         | snowfall totals                    |
        +-------------------------+------------------------------------+
        | MLY-SNOW-AVGNDS-GE001TI | Average number of                  |
        |                         | days per month with Snowfall >=    |
        |                         | 0.1 inches                         |
        +-------------------------+------------------------------------+
        | MLY-SNOW-AVGNDS-GE010TI | Average number of                  |
        |                         | days per month with Snowfall >=    |
        |                         | 1.0 inches                         |
        +-------------------------+------------------------------------+
        | MLY-SNOW-AVGNDS-GE030TI | Average number of                  |
        |                         | days per month with Snowfall >=    |
        |                         | 3.0 inches                         |
        +-------------------------+------------------------------------+
        | MLY-SNOW-AVGNDS-GE050TI | Average number of                  |
        |                         | days per month with Snowfall >=    |
        |                         | 5.0 inches                         |
        +-------------------------+------------------------------------+
        | MLY-SNOW-AVGNDS-GE100TI | Average number of                  |
        |                         | days per month with Snowfall >=    |
        |                         | 10.0 inches                        |
        +-------------------------+------------------------------------+
        | MLY-SNOW-NORMAL         | Average monthly                    |
        |                         | snowfall totals                    |
        +-------------------------+------------------------------------+
        | MLY-SNWD-AVGNDS-GE001WI | Average number of                  |
        |                         | days per month with snow depth >=  |
        |                         | 1 inch                             |
        +-------------------------+------------------------------------+
        | MLY-SNWD-AVGNDS-GE003WI | Average number of                  |
        |                         | days per month with snow depth >=  |
        |                         | 3 inches                           |
        +-------------------------+------------------------------------+
        | MLY-SNWD-AVGNDS-GE005WI | Average number of                  |
        |                         | days per month with snow depth >=  |
        |                         | 5 inches                           |
        +-------------------------+------------------------------------+
        | MLY-SNWD-AVGNDS-GE010WI | Average number of                  |
        |                         | days per month with snow depth >=  |
        |                         | 10 inches                          |
        +-------------------------+------------------------------------+
        | MLY-TAVG-NORMAL         | Average monthly                    |
        |                         | average temperature                |
        +-------------------------+------------------------------------+
        | MLY-TAVG-STDDEV         | Long-term standard deviations of   |
        |                         | monthly average temperature        |
        +-------------------------+------------------------------------+
        | MLY-TMAX-AVGNDS-GRTH040 | Average number of days             |
        |                         | per month where tmax is greater    |
        |                         | than or equal to 40F               |
        +-------------------------+------------------------------------+
        | MLY-TMAX-AVGNDS-GRTH050 | Average number of days             |
        |                         | per month where tmax is greater    |
        |                         | than or equal to 50F               |
        +-------------------------+------------------------------------+
        | MLY-TMAX-AVGNDS-GRTH060 | Average number of days             |
        |                         | per month where tmax is greater    |
        |                         | than or equal to 60F               |
        +-------------------------+------------------------------------+
        | MLY-TMAX-AVGNDS-GRTH070 | Average number of days             |
        |                         | per month where tmax is greater    |
        |                         | than or equal to 70F               |
        +-------------------------+------------------------------------+
        | MLY-TMAX-AVGNDS-GRTH080 | Average number of days             |
        |                         | per month where tmax is greater    |
        |                         | than or equal to 80F               |
        +-------------------------+------------------------------------+
        | MLY-TMAX-AVGNDS-GRTH090 | Average number of days             |
        |                         | per month where tmax is greater    |
        |                         | than or equal to 90F               |
        +-------------------------+------------------------------------+
        | MLY-TMAX-AVGNDS-GRTH100 | Average number of days             |
        |                         | per month where tmax is greater    |
        |                         | than or equal to 100F              |
        +-------------------------+------------------------------------+
        | MLY-TMAX-AVGNDS-LSTH032 | Average number of days             |
        |                         | per month where tmax is less than  |
        |                         | or equal to 32F                    |
        +-------------------------+------------------------------------+
        | MLY-TMAX-NORMAL         | Average monthly                    |
        |                         | maximum temperature                |
        +-------------------------+------------------------------------+
        | MLY-TMAX-STDDEV         | Long-term standard deviations of   |
        |                         | monthly maximum temperature        |
        +-------------------------+------------------------------------+
        | MLY-TMIN-AVGNDS-LSTH000 | Average number of days             |
        |                         | per month where tmin is less than  |
        |                         | or equal to 0F                     |
        +-------------------------+------------------------------------+
        | MLY-TMIN-AVGNDS-LSTH010 | Average number of days             |
        |                         | per month where tmin is less than  |
        |                         | or equal to 10F                    |
        +-------------------------+------------------------------------+
        | MLY-TMIN-AVGNDS-LSTH020 | Average number of days             |
        |                         | per month where tmin is less than  |
        |                         | or equal to 20F                    |
        +-------------------------+------------------------------------+
        | MLY-TMIN-AVGNDS-LSTH032 | Average number of days             |
        |                         | per month where tmin is less than  |
        |                         | or equal to 32F                    |
        +-------------------------+------------------------------------+
        | MLY-TMIN-AVGNDS-LSTH040 | Average number of days             |
        |                         | per month where tmin is less than  |
        |                         | or equal to 40F                    |
        +-------------------------+------------------------------------+
        | MLY-TMIN-AVGNDS-LSTH050 | Average number of days             |
        |                         | per month where tmin is less than  |
        |                         | or equal to 50F                    |
        +-------------------------+------------------------------------+
        | MLY-TMIN-AVGNDS-LSTH060 | Average number of days             |
        |                         | per month where tmin is less than  |
        |                         | or equal to 60F                    |
        +-------------------------+------------------------------------+
        | MLY-TMIN-AVGNDS-LSTH070 | Average number of days             |
        |                         | per month where tmin is less than  |
        |                         | or equal to 70F                    |
        +-------------------------+------------------------------------+
        | MLY-TMIN-NORMAL         | Average monthly                    |
        |                         | minimum temperature                |
        +-------------------------+------------------------------------+
        | MLY-TMIN-PRBOCC-LSTH016 | probability of 16F or below at     |
        |                         | least once in the month            |
        +-------------------------+------------------------------------+
        | MLY-TMIN-PRBOCC-LSTH020 | probability of 20F or below at     |
        |                         | least once in the month            |
        +-------------------------+------------------------------------+
        | MLY-TMIN-PRBOCC-LSTH024 | probability of 24F or below at     |
        |                         | least once in the month            |
        +-------------------------+------------------------------------+
        | MLY-TMIN-PRBOCC-LSTH028 | probability of 28F or below at     |
        |                         | least once in the month            |
        +-------------------------+------------------------------------+
        | MLY-TMIN-PRBOCC-LSTH032 | probability of 32F or below at     |
        |                         | least once in the month            |
        +-------------------------+------------------------------------+
        | MLY-TMIN-PRBOCC-LSTH036 | probability of 36F or below at     |
        |                         | least once in the month            |
        +-------------------------+------------------------------------+
        | MLY-TMIN-STDDEV         | Long-term standard deviations of   |
        |                         | monthly minimum temperature        |
        +-------------------------+------------------------------------+

    startdate
        Start date in ISO8601
        format.

    enddate
        End date in ISO8601
        format."""
    tsutils._printiso(
        ncei_normal_mly(
            stationid, datatypeid=datatypeid, startdate=startdate, enddate=enddate
        )
    )


def ncei_normal_mly(stationid, datatypeid="", startdate="", enddate=""):
    r"""National Centers for Environmental Information (NCEI) GHCND Normal monthly."""
    df = ncei_cdo_json_to_df(
        r"http://www.ncdc.noaa.gov/cdo-web/api/v2/data",
        startdate=startdate,
        enddate=enddate,
        datasetid="NORMAL_MLY",
        stationid=stationid,
    )

    return df


# 1970-05-12, 2014-01-01, Precipitation 15 Minute     , 0.25 , PRECIP_15
@mando.command("ncei_precip_15", formatter_class=HelpFormatter, doctype="numpy")
def ncei_precip_15_cli(stationid, datatypeid="", startdate="", enddate=""):
    r"""National Centers for Environmental Information (NCEI) 15 minute precipitation.

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
    stationid : str
        Station
        ID.

    datatypeid : str
        The following table lists the datatypes available for the annual
        dataset.  If the datatypeid is not given defaults to getting all data
        available at that station.

        +------+---------------+
        | Code | Description   |
        +======+===============+
        | QGAG | Precipitation |
        +------+---------------+
        | QPCP | Precipitation |
        +------+---------------+

    startdate
        Start date in ISO8601
        format.

    enddate
        End date in ISO8601
        format."""
    tsutils._printiso(
        ncei_precip_15(
            stationid, datatypeid=datatypeid, startdate=startdate, enddate=enddate
        )
    )


def ncei_precip_15(stationid, datatypeid="", startdate="", enddate=""):
    r"""National Centers for Environmental Information (NCEI) 15 minute precipitation."""
    df = ncei_cdo_json_to_df(
        r"http://www.ncdc.noaa.gov/cdo-web/api/v2/data",
        startdate=startdate,
        enddate=enddate,
        datasetid="PRECIP_15",
        stationid=stationid,
    )

    return df


# 1900-01-01, 2014-01-01, Precipitation Hourly        , 1    , PRECIP_HLY
@mando.command("ncei_precip_hly", formatter_class=HelpFormatter, doctype="numpy")
def ncei_precip_hly_cli(stationid, datatypeid="", startdate="", enddate=""):
    r"""National Centers for Environmental Information (NCEI) hourly precipitation.

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
    stationid : str
        Station ID.

    datatypeid : str
        The following table lists the datatypes available for the annual
        dataset.  If the datatypeid is not given defaults to getting all data
        available at that station.

        +------+---------------+
        | Code | Description   |
        +======+===============+
        | HPCP | Precipitation |
        +------+---------------+

    startdate
        Start date in ISO8601 format.

    enddate
        End date in ISO8601 format."""
    tsutils._printiso(
        ncei_precip_hly(
            stationid, datatypeid=datatypeid, startdate=startdate, enddate=enddate
        )
    )


def ncei_precip_hly(stationid, datatypeid="", startdate="", enddate=""):
    r"""National Centers for Environmental Information (NCEI) hourly precipitation."""
    df = ncei_cdo_json_to_df(
        r"http://www.ncdc.noaa.gov/cdo-web/api/v2/data",
        startdate=startdate,
        enddate=enddate,
        datasetid="PRECIP_HLY",
        stationid=stationid,
    )

    return df


# ANNUAL
@mando.command("ncei_annual", formatter_class=HelpFormatter, doctype="numpy")
def ncei_annual_cli(stationid, datatypeid="", startdate="", enddate=""):
    r"""National Centers for Environmental Information (NCEI) annual data summaries.

    Requires registration and free API key.

    For every datatype and record there is a set of meta-data flags.
    For the ANNUAL dataset, the flags are::

        'Measurement','Quality','Days','Units'

    The flags are described in the following tables.

    More info:
    http://www1.ncdc.noaa.gov/pub/data/cdo/documentation/ANNUAL_documentation.pdf

    Measurement flag

    +-------+----------------------------------------------------------+
    | Code  | Description                                              |
    +=======+==========================================================+
    | A     | Accumulated amount. This value is a total that may       |
    |       | include data from a previous month or months (TPCP)      |
    +-------+----------------------------------------------------------+
    | B     | Adjusted Total. Monthly value totals based on            |
    |       | proportional available data across the entire month.     |
    |       | (CLDD, HTDD.                                             |
    +-------+----------------------------------------------------------+
    | E     | An estimated monthly or annual total                     |
    +-------+----------------------------------------------------------+
    | I     | Monthly means or totals based on incomplete time series. |
    |       | 1 to 9 days are missing. (MMNT,MMXP, MMXT, MNTM, TPCP,   |
    |       | TSNW).                                                   |
    +-------+----------------------------------------------------------+
    | M     | Used to indicate data element missing.                   |
    +-------+----------------------------------------------------------+
    | S     | Precipitation for the amount is continuing to be         |
    |       | accumulated. Total will be included in a subsequent      |
    |       | value (TPCP). Example: Days 1-20 had 1.35 inches of      |
    |       | precipitation, then a period of accumulation began. The  |
    |       | element TPCP would then be 00135S and the total          |
    |       | accumulated amount value appears in a subsequent monthly |
    |       | value. If TPCP = 0 there was no precipitation measured   |
    |       | during the month. flag 1 is set to "S" and the total     |
    |       | accumulated amount appears in a subsequent monthly       |
    |       | value.                                                   |
    +-------+----------------------------------------------------------+
    | T     | Trace of precipitation, snowfall, or snow depth. The     |
    |       | precipitation data value will = "00000". (EMXP, MXSD,    |
    |       | TPCP, TSNW).                                             |
    +-------+----------------------------------------------------------+
    | +     | The phenomena in question occurred on several days. The  |
    |       | date in the DAY field is the last day of occurrence.     |
    +-------+----------------------------------------------------------+
    | Blank | No report.                                               |
    +-------+----------------------------------------------------------+

    Quality flag

    +------+--------------------------------------+
    | Code | Description                          |
    +======+======================================+
    | A    | Accumulated amount                   |
    +------+--------------------------------------+
    | E    | Estimated value                      |
    +------+--------------------------------------+
    | +    | Value occurred on more than one day, |
    |      | last date of occurrence is used      |
    +------+--------------------------------------+

    Number of days flag

    Number of days is given as 00 when all days in the month are
    considered in computing data value or otherwise the maximum number
    of consecutive days in the month considered in computing the data
    value.

    Units flag

    +------+---------------------------------------------------------+
    | Code | Description                                             |
    +======+=========================================================+
    | C    | Whole degree Celsius                                    |
    +------+---------------------------------------------------------+
    | D    | Whole Fahrenheit Degree Day                             |
    +------+---------------------------------------------------------+
    | F    | Whole degree Fahrenheit                                 |
    +------+---------------------------------------------------------+
    | HI   | Hundredths of inches                                    |
    +------+---------------------------------------------------------+
    | I    | Whole inches                                            |
    +------+---------------------------------------------------------+
    | M    | Whole miles                                             |
    +------+---------------------------------------------------------+
    | MH   | Miles per hour                                          |
    +------+---------------------------------------------------------+
    | MM   | Millimeters                                             |
    +------+---------------------------------------------------------+
    | NA   | No units applicable (dimensionless)                     |
    +------+---------------------------------------------------------+
    | TC   | Tenths of degrees Celsius                               |
    +------+---------------------------------------------------------+
    | TF   | Tenths of degrees Fahrenheit                            |
    +------+---------------------------------------------------------+
    | TI   | Tenths of inches                                        |
    +------+---------------------------------------------------------+
    | TM   | Tenths of millimeters                                   |
    +------+---------------------------------------------------------+
    | 1    | Soils, degrees Fahrenheit, soil depths in inches and    |
    |      | hundredths                                              |
    +------+---------------------------------------------------------+
    | 2    | Soils, degrees Celsius, soil depth in whole centimeters |
    +------+---------------------------------------------------------+
    | 3    | Soils, degrees Celsius, soil, soil depth in inches and  |
    |      | hundredths                                              |
    +------+---------------------------------------------------------+
    | 4    | Soils, degrees Fahrenheit, soil depth in whole          |
    |      | centimeters                                             |
    +------+---------------------------------------------------------+
    | 5    | Soils, If the soil station closed during the current    |
    |      | month, '5' indicates the station has closed.            |
    +------+---------------------------------------------------------+

    Parameters
    ----------
    stationid : str
        Station ID.

    datatypeid : str
        The following table lists the datatypes available for the annual
        dataset.  If the datatypeid is not given defaults to getting all data
        available at that station.

        +--------+-----------------------------------------------------+
        | Code   | Description                                         |
        +========+=====================================================+
        | HN7290 | Highest minimum soil temperature for the month      |
        |        | (cover: grass muck                                  |
        +--------+-----------------------------------------------------+
        | HN8190 | Highest minimum soil temperature for the month      |
        |        | (cover: bare muck                                   |
        +--------+-----------------------------------------------------+
        | HN8290 | Highest minimum soil temperature for the month      |
        |        | (cover: bare muck                                   |
        +--------+-----------------------------------------------------+
        | HN8390 | Highest minimum soil temperature for the month      |
        |        | (cover: bare muck                                   |
        +--------+-----------------------------------------------------+
        | HO84A0 | Highest soil temperature at observation time        |
        |        | (cover: bare muck                                   |
        +--------+-----------------------------------------------------+
        | HO85A0 | Highest soil temperature at observation time        |
        |        | (cover: bare muck                                   |
        +--------+-----------------------------------------------------+
        | HX7290 | Highest maximum soil temperature for the month      |
        |        | (cover: grass muck                                  |
        +--------+-----------------------------------------------------+
        | HX8190 | Highest maximum soil temperature for the month      |
        |        | (cover: bare muck                                   |
        +--------+-----------------------------------------------------+
        | HX8290 | Highest maximum soil temperature for the month      |
        |        | (cover: bare muck                                   |
        +--------+-----------------------------------------------------+
        | HX8390 | Highest maximum soil temperature for the month      |
        |        | (cover: bare muck                                   |
        +--------+-----------------------------------------------------+
        | LN7290 | Lowest minimum soil temperature for the month       |
        |        | (cover: grass muck                                  |
        +--------+-----------------------------------------------------+
        | LN8190 | Lowest minimum soil temperature for the month       |
        |        | (cover: bare muck                                   |
        +--------+-----------------------------------------------------+
        | LN8290 | Lowest minimum soil temperature for the month       |
        |        | (cover: bare muck                                   |
        +--------+-----------------------------------------------------+
        | LN8390 | Lowest minimum soil temperature for the month       |
        |        | (cover: bare muck                                   |
        +--------+-----------------------------------------------------+
        | LO84A0 | Lowest soil temperature at observation time (cover: |
        |        | bare muck                                           |
        +--------+-----------------------------------------------------+
        | LO85A0 | Lowest soil temperature at observation time (cover: |
        |        | bare muck                                           |
        +--------+-----------------------------------------------------+
        | LX7290 | Lowest maximum soil temperature for the month       |
        |        | (cover: grass muck                                  |
        +--------+-----------------------------------------------------+
        | LX8190 | Lowest maximum soil temperature for the month       |
        |        | (cover: bare muck                                   |
        +--------+-----------------------------------------------------+
        | LX8290 | Lowest maximum soil temperature for the month       |
        |        | (cover: bare muck                                   |
        +--------+-----------------------------------------------------+
        | LX8390 | Lowest maximum soil temperature for the month       |
        |        | (cover: bare muck                                   |
        +--------+-----------------------------------------------------+
        | MN7290 | Monthly mean minimum soil temperature (cover: grass |
        |        | muck                                                |
        +--------+-----------------------------------------------------+
        | MN8190 | Monthly mean minimum soil temperature (cover: bare  |
        |        | muck                                                |
        +--------+-----------------------------------------------------+
        | MN8290 | Monthly mean minimum soil temperature (cover: bare  |
        |        | muck                                                |
        +--------+-----------------------------------------------------+
        | MN8390 | Monthly mean minimum soil temperature (cover: bare  |
        |        | muck                                                |
        +--------+-----------------------------------------------------+
        | MO84A0 | Monthly mean soil temperature at observation time   |
        |        | (cover: bare muck                                   |
        +--------+-----------------------------------------------------+
        | MO85A0 | Monthly mean soil temperature at observation time   |
        |        | (cover: bare muck                                   |
        +--------+-----------------------------------------------------+
        | MX7290 | Monthly mean maximum soil temperature (cover: grass |
        |        | muck                                                |
        +--------+-----------------------------------------------------+
        | MX8190 | Monthly mean maximum soil temperature (cover: bare  |
        |        | muck                                                |
        +--------+-----------------------------------------------------+
        | MX8290 | Monthly mean maximum soil temperature (cover: bare  |
        |        | muck                                                |
        +--------+-----------------------------------------------------+
        | MX8390 | Monthly mean maximum soil temperature (cover: bare  |
        |        | muck                                                |
        +--------+-----------------------------------------------------+
        | HN6190 | Highest minimum soil temperature for the month      |
        |        | (cover: straw mulch                                 |
        +--------+-----------------------------------------------------+
        | LN6190 | Lowest minimum soil temperature for the month       |
        |        | (cover: straw mulch                                 |
        +--------+-----------------------------------------------------+
        | MN6190 | Monthly mean minimum soil temperature (cover: straw |
        |        | mulch                                               |
        +--------+-----------------------------------------------------+
        | HX6190 | Highest maximum soil temperature for the month      |
        |        | (cover: straw mulch                                 |
        +--------+-----------------------------------------------------+
        | LX6190 | Lowest maximum soil temperature for the month       |
        |        | (cover: straw mulch                                 |
        +--------+-----------------------------------------------------+
        | MX6190 | Monthly mean maximum soil temperature (cover: straw |
        |        | mulch                                               |
        +--------+-----------------------------------------------------+
        | CLDD   | Cooling Degree Days                                 |
        +--------+-----------------------------------------------------+
        | DP01   | Number of days with greater than or equal to 0.1    |
        |        | inch of precipitation                               |
        +--------+-----------------------------------------------------+
        | DP05   | Number of days with greater than or equal to 0.5    |
        |        | inch of precipitation                               |
        +--------+-----------------------------------------------------+
        | DP10   | Number of days with greater than or equal to 1.0    |
        |        | inch of precipitation                               |
        +--------+-----------------------------------------------------+
        | DPNP   | Departure from normal monthly precipitation.        |
        +--------+-----------------------------------------------------+
        | DPNT   | Departure from normal monthly temperature.          |
        +--------+-----------------------------------------------------+
        | DSNW   | Number days with snow depth > 1 inch.               |
        +--------+-----------------------------------------------------+
        | DT00   | Number days with minimum temperature less than or   |
        |        | equal to 0.0 F                                      |
        +--------+-----------------------------------------------------+
        | DT32   | Number days with minimum temperature less than or   |
        |        | equal to 32.0 F                                     |
        +--------+-----------------------------------------------------+
        | DT70   | Number days with maximum temperature > 70 F.        |
        |        | (Alaska only.)                                      |
        +--------+-----------------------------------------------------+
        | DT90   | Number days with maximum temperature greater than   |
        |        | or equal 90.0 F                                     |
        +--------+-----------------------------------------------------+
        | DX32   | Number days with maximum temperature < 32 F.        |
        +--------+-----------------------------------------------------+
        | EMNT   | Extreme minimum temperature for the period.         |
        +--------+-----------------------------------------------------+
        | EMXP   | Extreme maximum precipitation for the period.       |
        +--------+-----------------------------------------------------+
        | EMXT   | Extreme maximum temperature for the period.         |
        +--------+-----------------------------------------------------+
        | HN0190 | Highest minimum soil temperature for the month      |
        |        | (cover: unknown                                     |
        +--------+-----------------------------------------------------+
        | HN0290 | Highest minimum soil temperature for the month      |
        |        | (cover: unknown                                     |
        +--------+-----------------------------------------------------+
        | HN0390 | Highest minimum soil temperature for the month      |
        |        | (cover: unknown                                     |
        +--------+-----------------------------------------------------+
        | HN1190 | Highest minimum soil temperature for the month      |
        |        | (cover: grass                                       |
        +--------+-----------------------------------------------------+
        | HN1290 | Highest minimum soil temperature for the month      |
        |        | (cover: grass                                       |
        +--------+-----------------------------------------------------+
        | HN1390 | Highest minimum soil temperature for the month      |
        |        | (cover: grass                                       |
        +--------+-----------------------------------------------------+
        | HN2190 | Highest minimum soil temperature for the month      |
        |        | (cover: fallow                                      |
        +--------+-----------------------------------------------------+
        | HN2290 | Highest minimum soil temperature for the month      |
        |        | (cover: fallow                                      |
        +--------+-----------------------------------------------------+
        | HN2390 | Highest minimum soil temperature for the month      |
        |        | (cover: fallow                                      |
        +--------+-----------------------------------------------------+
        | HN3190 | Highest minimum soil temperature for the month      |
        |        | (cover: bare ground                                 |
        +--------+-----------------------------------------------------+
        | HN3290 | Highest minimum soil temperature for the month      |
        |        | (cover: bare ground                                 |
        +--------+-----------------------------------------------------+
        | HN3390 | Highest minimum soil temperature for the month      |
        |        | (cover: bare ground                                 |
        +--------+-----------------------------------------------------+
        | HN5190 | Highest minimum soil temperature for the month      |
        |        | (cover: sod                                         |
        +--------+-----------------------------------------------------+
        | HN5290 | Highest minimum soil temperature for the month      |
        |        | (cover: sod                                         |
        +--------+-----------------------------------------------------+
        | HN5390 | Highest minimum soil temperature for the month      |
        |        | (cover: sod                                         |
        +--------+-----------------------------------------------------+
        | HO01A0 | Highest soil temperature at observation time        |
        |        | (cover: unknown                                     |
        +--------+-----------------------------------------------------+
        | HO01P0 | Highest soil temperature at observation time        |
        |        | (cover: unknown                                     |
        +--------+-----------------------------------------------------+
        | HO02A0 | Highest soil temperature at observation time        |
        |        | (cover: unknown                                     |
        +--------+-----------------------------------------------------+
        | HO02P0 | Highest soil temperature at observation time        |
        |        | (cover: unknown                                     |
        +--------+-----------------------------------------------------+
        | HO03A0 | Highest soil temperature at observation time        |
        |        | (cover: unknown                                     |
        +--------+-----------------------------------------------------+
        | HO03P0 | Highest soil temperature at observation time        |
        |        | (cover: unknown                                     |
        +--------+-----------------------------------------------------+
        | HO04A0 | Highest soil temperature at observation time        |
        |        | (cover: unknown                                     |
        +--------+-----------------------------------------------------+
        | HO04P0 | Highest soil temperature at observation time        |
        |        | (cover: unknown                                     |
        +--------+-----------------------------------------------------+
        | HO05A0 | Highest soil temperature at observation time        |
        |        | (cover: unknown                                     |
        +--------+-----------------------------------------------------+
        | HO05P0 | Highest soil temperature at observation time        |
        |        | (cover: unknown                                     |
        +--------+-----------------------------------------------------+
        | HO11A0 | Highest soil temperature at observation time        |
        |        | (cover: grass                                       |
        +--------+-----------------------------------------------------+
        | HO11P0 | Highest soil temperature at observation time        |
        |        | (cover: grass                                       |
        +--------+-----------------------------------------------------+
        | HO12A0 | Highest soil temperature at observation time        |
        |        | (cover: grass                                       |
        +--------+-----------------------------------------------------+
        | HO12P0 | Highest soil temperature at observation time        |
        |        | (cover: grass                                       |
        +--------+-----------------------------------------------------+
        | HO13A0 | Highest soil temperature at observation time        |
        |        | (cover: grass                                       |
        +--------+-----------------------------------------------------+
        | HO14A0 | Highest soil temperature at observation time        |
        |        | (cover: grass                                       |
        +--------+-----------------------------------------------------+
        | HO15A0 | Highest soil temperature at observation time        |
        |        | (cover: grass                                       |
        +--------+-----------------------------------------------------+
        | HO31A0 | Highest soil temperature at observation time        |
        |        | (cover: bare ground                                 |
        +--------+-----------------------------------------------------+
        | HO31P0 | Highest soil temperature at observation time        |
        |        | (cover: bare ground                                 |
        +--------+-----------------------------------------------------+
        | HO32A0 | Highest soil temperature at observation time        |
        |        | (cover: bare ground                                 |
        +--------+-----------------------------------------------------+
        | HO32P0 | Highest soil temperature at observation time        |
        |        | (cover: bare ground                                 |
        +--------+-----------------------------------------------------+
        | HO33A0 | Highest soil temperature at observation time        |
        |        | (cover: bare ground                                 |
        +--------+-----------------------------------------------------+
        | HO33P0 | Highest soil temperature at observation time        |
        |        | (cover: bare ground                                 |
        +--------+-----------------------------------------------------+
        | HO34A0 | Highest soil temperature at observation time        |
        |        | (cover: bare ground                                 |
        +--------+-----------------------------------------------------+
        | HO34P0 | Highest soil temperature at observation time        |
        |        | (cover: bare ground                                 |
        +--------+-----------------------------------------------------+
        | HO35A0 | Highest soil temperature at observation time        |
        |        | (cover: bare ground                                 |
        +--------+-----------------------------------------------------+
        | HO35P0 | Highest soil temperature at observation time        |
        |        | (cover: bare ground                                 |
        +--------+-----------------------------------------------------+
        | HO51A0 | Highest soil temperature at observation time        |
        |        | (cover: sod                                         |
        +--------+-----------------------------------------------------+
        | HO51P0 | Highest soil temperature at observation time        |
        |        | (cover: sod                                         |
        +--------+-----------------------------------------------------+
        | HO52A0 | Highest soil temperature at observation time        |
        |        | (cover: sod                                         |
        +--------+-----------------------------------------------------+
        | HO52P0 | Highest soil temperature at observation time        |
        |        | (cover: sod                                         |
        +--------+-----------------------------------------------------+
        | HO53A0 | Highest soil temperature at observation time        |
        |        | (cover: sod                                         |
        +--------+-----------------------------------------------------+
        | HO53P0 | Highest soil temperature at observation time        |
        |        | (cover: sod                                         |
        +--------+-----------------------------------------------------+
        | HO54A0 | Highest soil temperature at observation time        |
        |        | (cover: sod                                         |
        +--------+-----------------------------------------------------+
        | HO54P0 | Highest soil temperature at observation time        |
        |        | (cover: sod                                         |
        +--------+-----------------------------------------------------+
        | HO55A0 | Highest soil temperature at observation time        |
        |        | (cover: sod                                         |
        +--------+-----------------------------------------------------+
        | HO55P0 | Highest soil temperature at observation time        |
        |        | (cover: sod                                         |
        +--------+-----------------------------------------------------+
        | HTDD   | Heating degree days                                 |
        +--------+-----------------------------------------------------+
        | HX0190 | Highest maximum soil temperature for the month      |
        |        | (cover: unknown                                     |
        +--------+-----------------------------------------------------+
        | HX0290 | Highest maximum soil temperature for the month      |
        |        | (cover: unknown                                     |
        +--------+-----------------------------------------------------+
        | HX0390 | Highest maximum soil temperature for the month      |
        |        | (cover: unknown                                     |
        +--------+-----------------------------------------------------+
        | HX1190 | Highest maximum soil temperature for the month      |
        |        | (cover: grass                                       |
        +--------+-----------------------------------------------------+
        | HX1290 | Highest maximum soil temperature for the month      |
        |        | (cover: grass                                       |
        +--------+-----------------------------------------------------+
        | HX1390 | Highest maximum soil temperature for the month      |
        |        | (cover: grass                                       |
        +--------+-----------------------------------------------------+
        | HX2190 | Highest maximum soil temperature for the month      |
        |        | (cover: fallow                                      |
        +--------+-----------------------------------------------------+
        | HX2290 | Highest maximum soil temperature for the month      |
        |        | (cover: fallow                                      |
        +--------+-----------------------------------------------------+
        | HX2390 | Highest maximum soil temperature for the month      |
        |        | (cover: fallow                                      |
        +--------+-----------------------------------------------------+
        | HX3190 | Highest maximum soil temperature for the month      |
        |        | (cover: bare ground                                 |
        +--------+-----------------------------------------------------+
        | HX3290 | Highest maximum soil temperature for the month      |
        |        | (cover: bare ground                                 |
        +--------+-----------------------------------------------------+
        | HX3390 | Highest maximum soil temperature for the month      |
        |        | (cover: bare ground                                 |
        +--------+-----------------------------------------------------+
        | HX5190 | Highest maximum soil temperature for the month      |
        |        | (cover: sod                                         |
        +--------+-----------------------------------------------------+
        | HX5290 | Highest maximum soil temperature for the month      |
        |        | (cover: sod                                         |
        +--------+-----------------------------------------------------+
        | HX5390 | Highest maximum soil temperature for the month      |
        |        | (cover: sod                                         |
        +--------+-----------------------------------------------------+
        | LN0190 | Lowest minimum soil temperature for the month       |
        |        | (cover: unknown                                     |
        +--------+-----------------------------------------------------+
        | LN0290 | Lowest minimum soil temperature for the month       |
        |        | (cover: unknown                                     |
        +--------+-----------------------------------------------------+
        | LN0390 | Lowest minimum soil temperature for the month       |
        |        | (cover: unknown                                     |
        +--------+-----------------------------------------------------+
        | LN1190 | Lowest minimum soil temperature for the month       |
        |        | (cover: grass                                       |
        +--------+-----------------------------------------------------+
        | LN1290 | Lowest minimum soil temperature for the month       |
        |        | (cover: grass                                       |
        +--------+-----------------------------------------------------+
        | LN1390 | Lowest minimum soil temperature for the month       |
        |        | (cover: grass                                       |
        +--------+-----------------------------------------------------+
        | LN2190 | Lowest minimum soil temperature for the month       |
        |        | (cover: fallow                                      |
        +--------+-----------------------------------------------------+
        | LN2290 | Lowest minimum soil temperature for the month       |
        |        | (cover: fallow                                      |
        +--------+-----------------------------------------------------+
        | LN2390 | Lowest minimum soil temperature for the month       |
        |        | (cover: fallow                                      |
        +--------+-----------------------------------------------------+
        | LN3190 | Lowest minimum soil temperature for the month       |
        |        | (cover: bare ground                                 |
        +--------+-----------------------------------------------------+
        | LN3290 | Lowest minimum soil temperature for the month       |
        |        | (cover: bare ground                                 |
        +--------+-----------------------------------------------------+
        | LN3390 | Lowest minimum soil temperature for the month       |
        |        | (cover: bare ground                                 |
        +--------+-----------------------------------------------------+
        | LN5190 | Lowest minimum soil temperature for the month       |
        |        | (cover: sod                                         |
        +--------+-----------------------------------------------------+
        | LN5290 | Lowest minimum soil temperature for the month       |
        |        | (cover: sod                                         |
        +--------+-----------------------------------------------------+
        | LN5390 | Lowest minimum soil temperature for the month       |
        |        | (cover: sod                                         |
        +--------+-----------------------------------------------------+
        | LO01A0 | Lowest soil temperature at observation time (cover: |
        |        | unknown                                             |
        +--------+-----------------------------------------------------+
        | LO01P0 | Lowest soil temperature at observation time (cover: |
        |        | unknown                                             |
        +--------+-----------------------------------------------------+
        | LO02A0 | Lowest soil temperature at observation time (cover: |
        |        | unknown                                             |
        +--------+-----------------------------------------------------+
        | LO02P0 | Lowest soil temperature at observation time (cover: |
        |        | unknown                                             |
        +--------+-----------------------------------------------------+
        | LO03A0 | Lowest soil temperature at observation time (cover: |
        |        | unknown                                             |
        +--------+-----------------------------------------------------+
        | LO03P0 | Lowest soil temperature at observation time (cover: |
        |        | unknown                                             |
        +--------+-----------------------------------------------------+
        | LO04A0 | Lowest soil temperature at observation time (cover: |
        |        | unknown                                             |
        +--------+-----------------------------------------------------+
        | LO04P0 | Lowest soil temperature at observation time (cover: |
        |        | unknown                                             |
        +--------+-----------------------------------------------------+
        | LO05A0 | Lowest soil temperature at observation time (cover: |
        |        | unknown                                             |
        +--------+-----------------------------------------------------+
        | LO05P0 | Lowest soil temperature at observation time (cover: |
        |        | unknown                                             |
        +--------+-----------------------------------------------------+
        | LO11A0 | Lowest soil temperature at observation time (cover: |
        |        | grass                                               |
        +--------+-----------------------------------------------------+
        | LO12A0 | Lowest soil temperature at observation time (cover: |
        |        | grass                                               |
        +--------+-----------------------------------------------------+
        | LO12P0 | Lowest soil temperature at observation time (cover: |
        |        | grass                                               |
        +--------+-----------------------------------------------------+
        | LO13A0 | Lowest soil temperature at observation time (cover: |
        |        | grass                                               |
        +--------+-----------------------------------------------------+
        | LO14A0 | Lowest soil temperature at observation time (cover: |
        |        | grass                                               |
        +--------+-----------------------------------------------------+
        | LO15A0 | Lowest soil temperature at observation time (cover: |
        |        | grass                                               |
        +--------+-----------------------------------------------------+
        | LO31A0 | Lowest soil temperature at observation time (cover: |
        |        | bare ground                                         |
        +--------+-----------------------------------------------------+
        | LO31P0 | Lowest soil temperature at observation time (cover: |
        |        | bare ground                                         |
        +--------+-----------------------------------------------------+
        | LO32A0 | Lowest soil temperature at observation time (cover: |
        |        | bare ground                                         |
        +--------+-----------------------------------------------------+
        | LO32P0 | Lowest soil temperature at observation time (cover: |
        |        | bare ground                                         |
        +--------+-----------------------------------------------------+
        | LO33A0 | Lowest soil temperature at observation time (cover: |
        |        | bare ground                                         |
        +--------+-----------------------------------------------------+
        | LO33P0 | Lowest soil temperature at observation time (cover: |
        |        | bare ground                                         |
        +--------+-----------------------------------------------------+
        | LO34A0 | Lowest soil temperature at observation time (cover: |
        |        | bare ground                                         |
        +--------+-----------------------------------------------------+
        | LO34P0 | Lowest soil temperature at observation time (cover: |
        |        | bare ground                                         |
        +--------+-----------------------------------------------------+
        | LO35A0 | Lowest soil temperature at observation time (cover: |
        |        | bare ground                                         |
        +--------+-----------------------------------------------------+
        | LO35P0 | Lowest soil temperature at observation time (cover: |
        |        | bare ground                                         |
        +--------+-----------------------------------------------------+
        | LO51A0 | Lowest soil temperature at observation time (cover: |
        |        | sod                                                 |
        +--------+-----------------------------------------------------+
        | LO51P0 | Lowest soil temperature at observation time (cover: |
        |        | sod                                                 |
        +--------+-----------------------------------------------------+
        | LO52A0 | Lowest soil temperature at observation time (cover: |
        |        | sod                                                 |
        +--------+-----------------------------------------------------+
        | LO52P0 | Lowest soil temperature at observation time (cover: |
        |        | sod                                                 |
        +--------+-----------------------------------------------------+
        | LO53A0 | Lowest soil temperature at observation time (cover: |
        |        | sod                                                 |
        +--------+-----------------------------------------------------+
        | LO53P0 | Lowest soil temperature at observation time (cover: |
        |        | sod                                                 |
        +--------+-----------------------------------------------------+
        | LO54A0 | Lowest soil temperature at observation time (cover: |
        |        | sod                                                 |
        +--------+-----------------------------------------------------+
        | LO54P0 | Lowest soil temperature at observation time (cover: |
        |        | sod                                                 |
        +--------+-----------------------------------------------------+
        | LO55A0 | Lowest soil temperature at observation time (cover: |
        |        | sod                                                 |
        +--------+-----------------------------------------------------+
        | LO55P0 | Lowest soil temperature at observation time (cover: |
        |        | sod                                                 |
        +--------+-----------------------------------------------------+
        | LX0190 | Lowest maximum soil temperature for the month       |
        |        | (cover: unknown                                     |
        +--------+-----------------------------------------------------+
        | LX0290 | Lowest maximum soil temperature for the month       |
        |        | (cover: unknown                                     |
        +--------+-----------------------------------------------------+
        | LX0390 | Lowest maximum soil temperature for the month       |
        |        | (cover: unknown                                     |
        +--------+-----------------------------------------------------+
        | LX1190 | Lowest maximum soil temperature for the month       |
        |        | (cover: grass                                       |
        +--------+-----------------------------------------------------+
        | LX1290 | Lowest maximum soil temperature for the month       |
        |        | (cover: grass                                       |
        +--------+-----------------------------------------------------+
        | LX1390 | Lowest maximum soil temperature for the month       |
        |        | (cover: grass                                       |
        +--------+-----------------------------------------------------+
        | LX2190 | Lowest maximum soil temperature for the month       |
        |        | (cover: fallow                                      |
        +--------+-----------------------------------------------------+
        | LX2290 | Lowest maximum soil temperature for the month       |
        |        | (cover: fallow                                      |
        +--------+-----------------------------------------------------+
        | LX2390 | Lowest maximum soil temperature for the month       |
        |        | (cover: fallow                                      |
        +--------+-----------------------------------------------------+
        | LX3190 | Lowest maximum soil temperature for the month       |
        |        | (cover: bare ground                                 |
        +--------+-----------------------------------------------------+
        | LX3290 | Lowest maximum soil temperature for the month       |
        |        | (cover: bare ground                                 |
        +--------+-----------------------------------------------------+
        | LX3390 | Lowest maximum soil temperature for the month       |
        |        | (cover: bare ground                                 |
        +--------+-----------------------------------------------------+
        | LX5190 | Lowest maximum soil temperature for the month       |
        |        | (cover: sod                                         |
        +--------+-----------------------------------------------------+
        | LX5290 | Lowest maximum soil temperature for the month       |
        |        | (cover: sod                                         |
        +--------+-----------------------------------------------------+
        | LX5390 | Lowest maximum soil temperature for the month       |
        |        | (cover: sod                                         |
        +--------+-----------------------------------------------------+
        | MMNP   | Mean minimum temperature of evaporation pan water   |
        |        | for the period.                                     |
        +--------+-----------------------------------------------------+
        | MMNT   | Monthly Mean minimum temperature                    |
        +--------+-----------------------------------------------------+
        | MMXP   | Mean maximum temperature of evaporation pan water   |
        |        | for the period.                                     |
        +--------+-----------------------------------------------------+
        | MMXT   | Monthly Mean maximum temperature                    |
        +--------+-----------------------------------------------------+
        | MN0190 | Monthly mean minimum soil temperature (cover:       |
        |        | unknown                                             |
        +--------+-----------------------------------------------------+
        | MN0290 | Monthly mean minimum soil temperature (cover:       |
        |        | unknown                                             |
        +--------+-----------------------------------------------------+
        | MN0390 | Monthly mean minimum soil temperature (cover:       |
        |        | unknown                                             |
        +--------+-----------------------------------------------------+
        | MN1190 | Monthly mean minimum soil temperature (cover: grass |
        +--------+-----------------------------------------------------+
        | MN1290 | Monthly mean minimum soil temperature (cover: grass |
        +--------+-----------------------------------------------------+
        | MN1390 | Monthly mean minimum soil temperature (cover: grass |
        +--------+-----------------------------------------------------+
        | MN2190 | Monthly mean minimum soil temperature (cover:       |
        |        | fallow                                              |
        +--------+-----------------------------------------------------+
        | MN2290 | Monthly mean minimum soil temperature (cover:       |
        |        | fallow                                              |
        +--------+-----------------------------------------------------+
        | MN2390 | Monthly mean minimum soil temperature (cover:       |
        |        | fallow                                              |
        +--------+-----------------------------------------------------+
        | MN3190 | Monthly mean minimum soil temperature (cover: bare  |
        |        | ground                                              |
        +--------+-----------------------------------------------------+
        | MN3290 | Monthly mean minimum soil temperature (cover: bare  |
        |        | ground                                              |
        +--------+-----------------------------------------------------+
        | MN3390 | Monthly mean minimum soil temperature (cover: bare  |
        |        | ground                                              |
        +--------+-----------------------------------------------------+
        | MN5190 | Monthly mean minimum soil temperature (cover: sod   |
        +--------+-----------------------------------------------------+
        | MN5290 | Monthly mean minimum soil temperature (cover: sod   |
        +--------+-----------------------------------------------------+
        | MN5390 | Monthly mean minimum soil temperature (cover: sod   |
        +--------+-----------------------------------------------------+
        | MNTM   | Monthly mean temperature                            |
        +--------+-----------------------------------------------------+
        | MO01A0 | Monthly mean soil temperature at observation time   |
        |        | (cover: unknown                                     |
        +--------+-----------------------------------------------------+
        | MO01P0 | Monthly mean soil temperature at observation time   |
        |        | (cover: unknown                                     |
        +--------+-----------------------------------------------------+
        | MO02A0 | Monthly mean soil temperature at observation time   |
        |        | (cover: unknown                                     |
        +--------+-----------------------------------------------------+
        | MO02P0 | Monthly mean soil temperature at observation time   |
        |        | (cover: unknown                                     |
        +--------+-----------------------------------------------------+
        | MO03A0 | Monthly mean soil temperature at observation time   |
        |        | (cover: unknown                                     |
        +--------+-----------------------------------------------------+
        | MO03P0 | Monthly mean soil temperature at observation time   |
        |        | (cover: unknown                                     |
        +--------+-----------------------------------------------------+
        | MO04A0 | Monthly mean soil temperature at observation time   |
        |        | (cover: unknown                                     |
        +--------+-----------------------------------------------------+
        | MO04P0 | Monthly mean soil temperature at observation time   |
        |        | (cover: unknown                                     |
        +--------+-----------------------------------------------------+
        | MO05A0 | Monthly mean soil temperature at observation time   |
        |        | (cover: unknown                                     |
        +--------+-----------------------------------------------------+
        | MO05P0 | Monthly mean soil temperature at observation time   |
        |        | (cover: unknown                                     |
        +--------+-----------------------------------------------------+
        | MO11A0 | Monthly mean soil temperature at observation time   |
        |        | (cover: grass                                       |
        +--------+-----------------------------------------------------+
        | MO11P0 | Monthly mean soil temperature at observation time   |
        |        | (cover: grass                                       |
        +--------+-----------------------------------------------------+
        | MO12A0 | Monthly mean soil temperature at observation time   |
        |        | (cover: grass                                       |
        +--------+-----------------------------------------------------+
        | MO12P0 | Monthly mean soil temperature at observation time   |
        |        | (cover: grass                                       |
        +--------+-----------------------------------------------------+
        | MO13A0 | Monthly mean soil temperature at observation time   |
        |        | (cover: grass                                       |
        +--------+-----------------------------------------------------+
        | MO13P0 | Monthly mean soil temperature at observation time   |
        |        | (cover: grass                                       |
        +--------+-----------------------------------------------------+
        | MO14A0 | Monthly mean soil temperature at observation time   |
        |        | (cover: grass                                       |
        +--------+-----------------------------------------------------+
        | MO15A0 | Monthly mean soil temperature at observation time   |
        |        | (cover: grass                                       |
        +--------+-----------------------------------------------------+
        | MO31A0 | Monthly mean soil temperature at observation time   |
        |        | (cover: bare ground                                 |
        +--------+-----------------------------------------------------+
        | MO31P0 | Monthly mean soil temperature at observation time   |
        |        | (cover: bare ground                                 |
        +--------+-----------------------------------------------------+
        | MO32A0 | Monthly mean soil temperature at observation time   |
        |        | (cover: bare ground                                 |
        +--------+-----------------------------------------------------+
        | MO32P0 | Monthly mean soil temperature at observation time   |
        |        | (cover: bare ground                                 |
        +--------+-----------------------------------------------------+
        | MO33A0 | Monthly mean soil temperature at observation time   |
        |        | (cover: bare ground                                 |
        +--------+-----------------------------------------------------+
        | MO33P0 | Monthly mean soil temperature at observation time   |
        |        | (cover: bare ground                                 |
        +--------+-----------------------------------------------------+
        | MO34A0 | Monthly mean soil temperature at observation time   |
        |        | (cover: bare ground                                 |
        +--------+-----------------------------------------------------+
        | MO34P0 | Monthly mean soil temperature at observation time   |
        |        | (cover: bare ground                                 |
        +--------+-----------------------------------------------------+
        | MO35A0 | Monthly mean soil temperature at observation time   |
        |        | (cover: bare ground                                 |
        +--------+-----------------------------------------------------+
        | MO35P0 | Monthly mean soil temperature at observation time   |
        |        | (cover: bare ground                                 |
        +--------+-----------------------------------------------------+
        | MO51A0 | Monthly mean soil temperature at observation time   |
        |        | (cover: sod                                         |
        +--------+-----------------------------------------------------+
        | MO51P0 | Monthly mean soil temperature at observation time   |
        |        | (cover: sod                                         |
        +--------+-----------------------------------------------------+
        | MO52A0 | Monthly mean soil temperature at observation time   |
        |        | (cover: sod                                         |
        +--------+-----------------------------------------------------+
        | MO52P0 | Monthly mean soil temperature at observation time   |
        |        | (cover: sod                                         |
        +--------+-----------------------------------------------------+
        | MO53A0 | Monthly mean soil temperature at observation time   |
        |        | (cover: sod                                         |
        +--------+-----------------------------------------------------+
        | MO53P0 | Monthly mean soil temperature at observation time   |
        |        | (cover: sod                                         |
        +--------+-----------------------------------------------------+
        | MO54A0 | Monthly mean soil temperature at observation time   |
        |        | (cover: sod                                         |
        +--------+-----------------------------------------------------+
        | MO54P0 | Monthly mean soil temperature at observation time   |
        |        | (cover: sod                                         |
        +--------+-----------------------------------------------------+
        | MO55A0 | Monthly mean soil temperature at observation time   |
        |        | (cover: sod                                         |
        +--------+-----------------------------------------------------+
        | MO55P0 | Monthly mean soil temperature at observation time   |
        |        | (cover: sod                                         |
        +--------+-----------------------------------------------------+
        | MX0190 | Monthly mean maximum soil temperature (cover:       |
        |        | unknown                                             |
        +--------+-----------------------------------------------------+
        | MX0290 | Monthly mean maximum soil temperature (cover:       |
        |        | unknown                                             |
        +--------+-----------------------------------------------------+
        | MX0390 | Monthly mean maximum soil temperature (cover:       |
        |        | unknown                                             |
        +--------+-----------------------------------------------------+
        | MX1190 | Monthly mean maximum soil temperature (cover: grass |
        +--------+-----------------------------------------------------+
        | MX1290 | Monthly mean maximum soil temperature (cover: grass |
        +--------+-----------------------------------------------------+
        | MX1390 | Monthly mean maximum soil temperature (cover: grass |
        +--------+-----------------------------------------------------+
        | MX2190 | Monthly mean maximum soil temperature (cover:       |
        |        | fallow                                              |
        +--------+-----------------------------------------------------+
        | MX2290 | Monthly mean maximum soil temperature (cover:       |
        |        | fallow                                              |
        +--------+-----------------------------------------------------+
        | MX2390 | Monthly mean maximum soil temperature (cover:       |
        |        | fallow                                              |
        +--------+-----------------------------------------------------+
        | MX3190 | Monthly mean maximum soil temperature (cover: bare  |
        |        | ground                                              |
        +--------+-----------------------------------------------------+
        | MX3290 | Monthly mean maximum soil temperature (cover: bare  |
        |        | ground                                              |
        +--------+-----------------------------------------------------+
        | MX3390 | Monthly mean maximum soil temperature (cover: bare  |
        |        | ground                                              |
        +--------+-----------------------------------------------------+
        | MX5190 | Monthly mean maximum soil temperature (cover: sod   |
        +--------+-----------------------------------------------------+
        | MX5290 | Monthly mean maximum soil temperature (cover: sod   |
        +--------+-----------------------------------------------------+
        | MX5390 | Monthly mean maximum soil temperature (cover: sod   |
        +--------+-----------------------------------------------------+
        | MXSD   | Maximum snow depth                                  |
        +--------+-----------------------------------------------------+
        | TEVP   | Total monthly evaporation.                          |
        +--------+-----------------------------------------------------+
        | TPCP   | Total precipitation                                 |
        +--------+-----------------------------------------------------+
        | TSNW   | Total snow fall                                     |
        +--------+-----------------------------------------------------+
        | TWND   | Total monthly wind movement over evaporation pan.   |
        +--------+-----------------------------------------------------+

    startdate
        Start date in ISO8601 format.

    enddate
        End date in ISO8601 format."""
    tsutils._printiso(ncei_annual(stationid, datatypeid="", startdate="", enddate=""))


def ncei_annual(stationid, datatypeid="", startdate="", enddate=""):
    r"""National Centers for Environmental Information (NCEI) annual data summaries."""
    df = ncei_cdo_json_to_df(
        r"http://www.ncdc.noaa.gov/cdo-web/api/v2/data",
        startdate=startdate,
        enddate=enddate,
        datasetid="ANNUAL",
        stationid=stationid,
    )

    return df


# GHCNDMS
@mando.command("ncei_ghcndms", formatter_class=HelpFormatter, doctype="numpy")
def ncei_ghcndms_cli(stationid, datatypeid="", startdate="", enddate=""):
    r"""National Centers for Environmental Information (NCEI) GHCND Monthly Summaries.

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

    Parameters
    ----------
    stationid : str
        Station
        ID.

    datatypeid : str
        The following table lists the datatypes
        available for the 'ghcndms' dataset.  If the datatypeid is not
        given defaults to getting all data available at that station.

        +------+-------------------------------------------------------+
        | Code | Description                                           |
        +======+=======================================================+
        | ACMC | Average cloudiness midnight to midnight from          |
        |      | 30-second ceilometer data                             |
        +------+-------------------------------------------------------+
        | ACMH | Average cloudiness midnight to midnight from manual   |
        |      | observations                                          |
        +------+-------------------------------------------------------+
        | ACSC | Average cloudiness sunrise to sunset from 30-second   |
        |      | ceilometer data                                       |
        +------+-------------------------------------------------------+
        | ACSH | Average cloudiness sunrise to sunset from manual      |
        |      | observations                                          |
        +------+-------------------------------------------------------+
        | AWND | Average wind speed                                    |
        +------+-------------------------------------------------------+
        | DAEV | Number of days included in the multiday evaporation   |
        |      | total (MDEV)                                          |
        +------+-------------------------------------------------------+
        | DAPR | Number of days included in the multiday precipitation |
        |      | total (MDPR)                                          |
        +------+-------------------------------------------------------+
        | DASF | Number of days included in the multiday snow fall     |
        |      | total (MDSF)                                          |
        +------+-------------------------------------------------------+
        | DATN | Number of days included in the multiday minimum       |
        |      | temperature (MDTN)                                    |
        +------+-------------------------------------------------------+
        | DATX | Number of days included in the multiday maximum       |
        |      | temperature (MDTX)                                    |
        +------+-------------------------------------------------------+
        | DAWM | Number of days included in the multiday wind movement |
        |      | (MDWM)                                                |
        +------+-------------------------------------------------------+
        | DWPR | Number of days with non-zero precipitation included   |
        |      | in multiday precipitation total (MDPR)                |
        +------+-------------------------------------------------------+
        | EVAP | Evaporation of water from evaporation pan             |
        +------+-------------------------------------------------------+
        | FMTM | Time of fastest mile or fastest 1-minute wind         |
        +------+-------------------------------------------------------+
        | FRGB | Base of frozen ground layer                           |
        +------+-------------------------------------------------------+
        | FRGT | Top of frozen ground layer                            |
        +------+-------------------------------------------------------+
        | FRTH | Thickness of frozen ground layer                      |
        +------+-------------------------------------------------------+
        | GAHT | Difference between river and gauge height             |
        +------+-------------------------------------------------------+
        | MDEV | Multiday evaporation total (use with DAEV)            |
        +------+-------------------------------------------------------+
        | MDPR | Multiday precipitation total (use with DAPR and DWPR, |
        |      | if available)                                         |
        +------+-------------------------------------------------------+
        | MDSF | Multiday snowfall total                               |
        +------+-------------------------------------------------------+
        | MDTN | Multiday minimum temperature (use with DATN)          |
        +------+-------------------------------------------------------+
        | MDTX | Multiday maximum temperature (use with DATX)          |
        +------+-------------------------------------------------------+
        | MDWM | Multiday wind movement                                |
        +------+-------------------------------------------------------+
        | MNPN | Daily minimum temperature of water in an evaporation  |
        |      | pan                                                   |
        +------+-------------------------------------------------------+
        | MXPN | Daily maximum temperature of water in an evaporation  |
        |      | pan                                                   |
        +------+-------------------------------------------------------+
        | PGTM | Peak gust time                                        |
        +------+-------------------------------------------------------+
        | PRCP | Precipitation                                         |
        +------+-------------------------------------------------------+
        | PSUN | Daily percent of possible sunshine for the period     |
        +------+-------------------------------------------------------+
        | SN01 | Minimum soil temperature with unknown cover at 5 cm   |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SN02 | Minimum soil temperature with unknown cover at 10 cm  |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SN03 | Minimum soil temperature with unknown cover at 20 cm  |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SN11 | Minimum soil temperature with grass cover at 5 cm     |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SN12 | Minimum soil temperature with grass cover at 10 cm    |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SN13 | Minimum soil temperature with grass cover at 20 cm    |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SN14 | Minimum soil temperature with grass cover at 50 cm    |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SN21 | Minimum soil temperature with fallow cover at 5 cm    |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SN22 | Minimum soil temperature with fallow cover at 10 cm   |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SN23 | Minimum soil temperature with fallow cover at 20 cm   |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SN31 | Minimum soil temperature with bare ground cover at 5  |
        |      | cm depth                                              |
        +------+-------------------------------------------------------+
        | SN32 | Minimum soil temperature with bare ground cover at 10 |
        |      | cm depth                                              |
        +------+-------------------------------------------------------+
        | SN33 | Minimum soil temperature with bare ground cover at 20 |
        |      | cm depth                                              |
        +------+-------------------------------------------------------+
        | SN34 | Minimum soil temperature with bare ground cover at 50 |
        |      | cm depth                                              |
        +------+-------------------------------------------------------+
        | SN35 | Minimum soil temperature with bare ground cover at    |
        |      | 100 cm depth                                          |
        +------+-------------------------------------------------------+
        | SN36 | Minimum soil temperature with bare ground cover at    |
        |      | 150 cm depth                                          |
        +------+-------------------------------------------------------+
        | SN51 | Minimum soil temperature with sod cover at 5 cm depth |
        +------+-------------------------------------------------------+
        | SN52 | Minimum soil temperature with sod cover at 10 cm      |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SN53 | Minimum soil temperature with sod cover at 20 cm      |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SN54 | Minimum soil temperature with sod cover at 50 cm      |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SN55 | Minimum soil temperature with sod cover at 100 cm     |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SN56 | Minimum soil temperature with sod cover at 150 cm     |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SN57 | Minimum soil temperature with sod cover at 180 cm     |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SN61 | Minimum soil temperature with straw multch cover at 5 |
        |      | cm depth                                              |
        +------+-------------------------------------------------------+
        | SN72 | Minimum soil temperature with grass muck cover at 10  |
        |      | cm depth                                              |
        +------+-------------------------------------------------------+
        | SN81 | Minimum soil temperature with bare muck cover at 5 cm |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SN82 | Minimum soil temperature with bare muck cover at 10   |
        |      | cm depth                                              |
        +------+-------------------------------------------------------+
        | SN83 | Minimum soil temperature with bare muck cover at 20   |
        |      | cm depth                                              |
        +------+-------------------------------------------------------+
        | SNOW | Snowfall                                              |
        +------+-------------------------------------------------------+
        | SNWD | Snow depth                                            |
        +------+-------------------------------------------------------+
        | SX01 | Maximum soil temperature with unknown cover at 5 cm   |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SX02 | Maximum soil temperature with unknown cover at 10 cm  |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SX03 | Maximum soil temperature with unknown cover at 20 cm  |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SX11 | Maximum soil temperature with grass cover at 5 cm     |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SX12 | Maximum soil temperature with grass cover at 10 cm    |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SX13 | Maximum soil temperature with grass cover at 20 cm    |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SX14 | Maximum soil temperature with grass cover at 50 cm    |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SX15 | Maximum soil temperature with grass cover at 100 cm   |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SX17 | Maximum soil temperature with grass cover at 180 cm   |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SX21 | Maximum soil temperature with fallow cover at 5 cm    |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SX22 | Maximum soil temperature with fallow cover at 10 cm   |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SX23 | Maximum soil temperature with fallow cover at 20 cm   |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SX31 | Maximum soil temperature with bare ground cover at 5  |
        |      | cm depth                                              |
        +------+-------------------------------------------------------+
        | SX32 | Maximum soil temperature with bare ground cover at 10 |
        |      | cm depth                                              |
        +------+-------------------------------------------------------+
        | SX33 | Maximum soil temperature with bare ground cover at 20 |
        |      | cm depth                                              |
        +------+-------------------------------------------------------+
        | SX34 | Maximum soil temperature with bare ground cover at 50 |
        |      | cm depth                                              |
        +------+-------------------------------------------------------+
        | SX35 | Maximum soil temperature with bare ground cover at    |
        |      | 100 cm depth                                          |
        +------+-------------------------------------------------------+
        | SX36 | Maximum soil temperature with bare ground cover at    |
        |      | 150 cm depth                                          |
        +------+-------------------------------------------------------+
        | SX51 | Maximum soil temperature with sod cover at 5 cm depth |
        +------+-------------------------------------------------------+
        | SX52 | Maximum soil temperature with sod cover at 10 cm      |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SX53 | Maximum soil temperature with sod cover at 20 cm      |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SX54 | Maximum soil temperature with sod cover at 50 cm      |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SX55 | Maximum soil temperature with sod cover at 100 cm     |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SX56 | Maximum soil temperature with sod cover at 150 cm     |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SX57 | Maximum soil temperature with sod cover at 180 cm     |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SX61 | Maximum soil temperature with straw multch cover at 5 |
        |      | cm depth                                              |
        +------+-------------------------------------------------------+
        | SX72 | Maximum soil temperature with grass muck cover at 10  |
        |      | cm depth                                              |
        +------+-------------------------------------------------------+
        | SX81 | Maximum soil temperature with bare muck cover at 5 cm |
        |      | depth                                                 |
        +------+-------------------------------------------------------+
        | SX82 | Maximum soil temperature with bare muck cover at 10   |
        |      | cm depth                                              |
        +------+-------------------------------------------------------+
        | SX83 | Maximum soil temperature with bare muck cover at 20   |
        |      | cm depth                                              |
        +------+-------------------------------------------------------+
        | TAVG | Average Temperature.                                  |
        +------+-------------------------------------------------------+
        | THIC | Thickness of ice on water                             |
        +------+-------------------------------------------------------+
        | TMAX | Maximum temperature                                   |
        +------+-------------------------------------------------------+
        | TMIN | Minimum temperature                                   |
        +------+-------------------------------------------------------+
        | TOBS | Temperature at the time of observation                |
        +------+-------------------------------------------------------+
        | TSUN | Total sunshine for the period                         |
        +------+-------------------------------------------------------+
        | WDF1 | Direction of fastest 1-minute wind                    |
        +------+-------------------------------------------------------+
        | WDF2 | Direction of fastest 2-minute wind                    |
        +------+-------------------------------------------------------+
        | WDF5 | Direction of fastest 5-second wind                    |
        +------+-------------------------------------------------------+
        | WDFG | Direction of peak wind gust                           |
        +------+-------------------------------------------------------+
        | WDFI | Direction of highest instantaneous wind               |
        +------+-------------------------------------------------------+
        | WDFM | Fastest mile wind direction                           |
        +------+-------------------------------------------------------+
        | WDMV | Total wind movement                                   |
        +------+-------------------------------------------------------+
        | WESD | Water equivalent of snow on the ground                |
        +------+-------------------------------------------------------+
        | WESF | Water equivalent of snowfall                          |
        +------+-------------------------------------------------------+
        | WSF1 | Fastest 1-minute wind speed                           |
        +------+-------------------------------------------------------+
        | WSF2 | Fastest 2-minute wind speed                           |
        +------+-------------------------------------------------------+
        | WSF5 | Fastest 5-second wind speed                           |
        +------+-------------------------------------------------------+
        | WSFG | Peak gust wind speed                                  |
        +------+-------------------------------------------------------+
        | WSFI | Highest instantaneous wind speed                      |
        +------+-------------------------------------------------------+
        | WSFM | Fastest mile wind speed                               |
        +------+-------------------------------------------------------+
        | WT01 | Fog, ice fog, or freezing fog (may include heavy fog) |
        +------+-------------------------------------------------------+
        | WT02 | Heavy fog or heaving freezing fog (not always         |
        |      | distinguished from fog)                               |
        +------+-------------------------------------------------------+
        | WT03 | Thunder                                               |
        +------+-------------------------------------------------------+
        | WT04 | Ice pellets, sleet, snow pellets, or small hail       |
        +------+-------------------------------------------------------+
        | WT05 | Hail (may include small hail)                         |
        +------+-------------------------------------------------------+
        | WT06 | Glaze or rime                                         |
        +------+-------------------------------------------------------+
        | WT07 | Dust, volcanic ash, blowing dust, blowing sand, or    |
        |      | blowing obstruction                                   |
        +------+-------------------------------------------------------+
        | WT08 | Smoke or haze                                         |
        +------+-------------------------------------------------------+
        | WT09 | Blowing or drifting snow                              |
        +------+-------------------------------------------------------+
        | WT10 | Tornado, waterspout, or funnel cloud                  |
        +------+-------------------------------------------------------+
        | WT11 | High or damaging winds                                |
        +------+-------------------------------------------------------+
        | WT12 | Blowing spray                                         |
        +------+-------------------------------------------------------+
        | WT13 | Mist                                                  |
        +------+-------------------------------------------------------+
        | WT14 | Drizzle                                               |
        +------+-------------------------------------------------------+
        | WT15 | Freezing drizzle                                      |
        +------+-------------------------------------------------------+
        | WT16 | Rain (may include freezing rain, drizzle, and         |
        |      | freezing drizzle)                                     |
        +------+-------------------------------------------------------+
        | WT17 | Freezing rain                                         |
        +------+-------------------------------------------------------+
        | WT18 | Snow, snow pellets, snow grains, or ice crystals      |
        +------+-------------------------------------------------------+
        | WT19 | Unknown source of precipitation                       |
        +------+-------------------------------------------------------+
        | WT21 | Ground fog                                            |
        +------+-------------------------------------------------------+
        | WT22 | Ice fog or freezing fog                               |
        +------+-------------------------------------------------------+
        | WV01 | Fog, ice fog, or freezing fog (may include heavy fog) |
        +------+-------------------------------------------------------+
        | WV03 | Thunder                                               |
        +------+-------------------------------------------------------+
        | WV07 | Ash, dust, sand, or other blowing obstruction         |
        +------+-------------------------------------------------------+
        | WV18 | Snow or ice crystals                                  |
        +------+-------------------------------------------------------+
        | WV20 | Rain or snow shower                                   |
        +------+-------------------------------------------------------+

    startdate
        Start date in ISO8601
        format.

    enddate
        End date in ISO8601
        format."""
    tsutils._printiso(
        ncei_ghcndms(
            stationid, datatypeid=datatypeid, startdate=startdate, enddate=enddate
        )
    )


def ncei_ghcndms(stationid, datatypeid="", startdate="", enddate=""):
    r"""National Centers for Environmental Information (NCEI) GHCND Monthly Summaries."""
    df = ncei_cdo_json_to_df(
        r"http://www.ncdc.noaa.gov/cdo-web/api/v2/data",
        startdate=startdate,
        enddate=enddate,
        datasetid="GHCNDMS",
        stationid=stationid,
    )

    return df


ncei_ghcnd_ftp.__doc__ = ncei_ghcnd_ftp_cli.__doc__
ncei_ghcnd.__doc__ = ncei_ghcnd_cli.__doc__
ncei_gsod.__doc__ = ncei_gsod_cli.__doc__
ncei_gsom.__doc__ = ncei_gsom_cli.__doc__
ncei_gsoy.__doc__ = ncei_gsoy_cli.__doc__
ncei_nexrad2.__doc__ = ncei_nexrad2_cli.__doc__
ncei_nexrad3.__doc__ = ncei_nexrad3_cli.__doc__
ncei_normal_ann.__doc__ = ncei_normal_ann_cli.__doc__
ncei_normal_dly.__doc__ = ncei_normal_dly_cli.__doc__
ncei_normal_hly.__doc__ = ncei_normal_hly_cli.__doc__
ncei_normal_mly.__doc__ = ncei_normal_mly_cli.__doc__
ncei_precip_15.__doc__ = ncei_precip_15_cli.__doc__
ncei_precip_hly.__doc__ = ncei_precip_hly_cli.__doc__
ncei_annual.__doc__ = ncei_annual_cli.__doc__
ncei_ghcndms.__doc__ = ncei_ghcndms_cli.__doc__


if __name__ == "__main__":
    r = ncei_ghcnd_ftp(
        station="ASN00075020",
        start_date="2000-01-01",
        end_date="2001-01-01",
    )

    print("ghcnd")
    print(r)

    r = ncei_ghcnd_ftp(
        station="ASN00075020",
        start_date="10 years ago",
        end_date="9 years ago",
    )

    print("ghcnd")
    print(r)

    # http://www.ncdc.noaa.gov/cdo-web/api/v2/data?
    #  datasetid=PRECIP_15&
    #  stationid=COOP:010008&
    #  units=metric&startdate=2010-05-01&enddate=2010-05-31
    r = ncei_cdo_json_to_df(
        r"http://www.ncdc.noaa.gov/cdo-web/api/v2/data",
        startdate="2010-05-01",
        enddate="2010-05-31",
        stationid="COOP:010008",
        datasetid="PRECIP_15",
    )
    print(r)
    mardi = [
        ["GHCND", "GHCND:AE000041196"],
        ["GHCND", "GHCND:USR0000GCOO"],
        ["PRECIP_HLY", "COOP:087440"],
        ["PRECIP_15", "COOP:087440"],
        # ['ANNUAL', 'GHCND:US1MOLN0006'],
        ["GHCNDMS", "GHCND:US1FLAL0004"],
        ["GSOM", "GHCND:US1FLAL0004"],
        ["GSOY", "GHCND:USW00012816"],
        # ['NORMAL_ANN', 'GHCND:USC00083322'],
        ["NORMAL_HLY", "GHCND:USW00013889"],
        ["NORMAL_DLY", "GHCND:USC00084731"],
        ["NORMAL_MLY", "GHCND:USC00086618"],
        # ['NEXRAD3', 'NEXRAD:KJAX'],
        # ['NEXRAD2', 'NEXRAD:KJAX'],
    ]
    for did, sid in mardi:
        startdate = "2010-01-01"
        enddate = "2013-01-01"
        if "NEXRAD" in did:
            startdate = "2000-01-01"
        if "PRECIP_" in did:
            startdate = "2009-01-01"

        r = ncei_cdo_json_to_df(
            r"http://www.ncdc.noaa.gov/cdo-web/api/v2/data",
            startdate=startdate,
            stationid=sid,
            datasetid=did,
        )

        print(did)
        print(r)
