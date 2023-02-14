"""
coops               global station 1T,6T,H,D,M: Center for Operational
                    Oceanographic Products and Services
"""

import datetime
import warnings
from collections import defaultdict
from contextlib import suppress
from typing import List, Literal, Optional, Union

import async_retriever as ar
import cltoolbox
import dateutil.parser as parser
import pandas as pd

try:
    from cltoolbox.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter

from toolbox_utils import tsutils

__all__ = ["coops"]

_settings_map = defaultdict(lambda: [{"metric": "", "english": ""}])

# Preliminary or verified water levels, depending on availability.
_settings_map["water_level"] = [
    {"metric": "m", "english": "ft"},
    "6T",
    ["Inferred", "FlatTol", "RateTol", "TempRateTol"],
]

# Air temperature as measured at the station.
_settings_map["air_temperature"] = [
    {"metric": "degC", "english": "degF"},
    "h",
    ["MaxTol", "MinTol", "RateTol"],
]

# Water temperature as measured at the station.
_settings_map["water_temperature"] = [
    {"metric": "degC", "english": "degF"},
    "h",
    ["MaxTol", "MinTol", "RateTol"],
]

# Wind speed, direction, and gusts as measured at the station.
_settings_map["wind"] = [
    {"metric": "m/s", "english": "ft/s"},
    "h",
    ["MaxTol", "RateTol"],
]

# Barometric pressure as measured at the station.
_settings_map["air_pressure"] = [
    {"metric": "mb", "english": "mb"},
    "h",
    ["MaxTol", "MinTol", "RateTol"],
]

# Air Gap (distance between a bridge and the water's surface) at the
# station.
_settings_map["air_gap"] = [
    {"metric": "m", "english": "ft"},
    "h",
    ["o", "FlatTol", "RateTol", "a"],
]

# The water's conductivity as measured at the station.
_settings_map["conductivity"] = [
    {"metric": "mS/cm", "english": "mS/cm"},
    "h",
    ["MaxTol", "MinTol", "RateTol"],
]

# Visibility from the station's visibility sensor. A measure of atmospheric
# clarity.
_settings_map["visibility"] = [
    {"metric": "km", "english": "nm"},
    "h",
    ["MaxTol", "MinTol", "RateTol"],
]

# Relative humidity as measured at the station.
_settings_map["humidity"] = [
    {"metric": "percent", "english": "percent"},
    "h",
    ["MaxTol", "MinTol", "RateTol"],
]

# Salinity and specific gravity data for the station.
_settings_map["salinity"] = [
    {"metric": "PSU", "english": "PSU"},
    "h",
    [""],
]

# Verified hourly height water level data for the station.
_settings_map["hourly_height"] = [
    {"metric": "m", "english": "ft"},
    "h",
    ["Inferred", "LimitTol"],
]

# Verified high/low water level data for the station.
_settings_map["high_low"] = [
    {"metric": "m", "english": "ft"},
    None,
    ["Inferred", "LimitTol"],
]

# Verified daily mean water level data for the station.
_settings_map["daily_mean"] = [
    {"metric": "m", "english": "ft"},
    None,
    ["Inferred", "LimitTol"],
]

# Verified monthly mean water level data for the station.
_settings_map["monthly_mean"] = [
    {"metric": "m", "english": "ft"},
    None,
    [""],
]

# One minute water level data for the station.
_settings_map["one_minute_water_level"] = [
    {"metric": "m", "english": "ft"},
    None,
    [""],
]

# 6 minute predictions water level data for the station.
_settings_map["predictions"] = [
    {"metric": "m", "english": "ft"},
    "h",
    [""],
]

# datums data for the currents stations.
_settings_map["datums"] = [
    {"metric": "m", "english": "ft"},
    None,
    [""],
]

# Currents data for currents stations.
_settings_map["currents"] = [
    {"metric": "m/s", "english": "ft/s"},
    "h",
    [""],
]


@cltoolbox.command("coops", formatter_class=HelpFormatter)
@tsutils.doc(tsutils.docstrings)
def coops_cli(
    station,
    date=None,
    begin_date=None,
    end_date=None,
    range=None,
    product="hourly_height",
    datum="NAVD",
    time_zone="GMT",
    interval="h",
    bin=None,
):
    r"""global station 1T,6T,H,D,M: Center for Operational Oceanographic Products and Services

    CO-OPS web services is at https://tidesandcurrents.noaa.gov/api/. The time
    zone of the returned data depends on the setting of the "time_zone" option.
    The default is "GMT" also known as "UTC".

    Parameters
    ----------
    station
        A 7 character station ID, or a currents station ID.

        Station listings for various products can be viewed at
        https://tidesandcurrents.noaa.gov or viewed on a map at Tides
        & Currents Station Map

    date : str
        [optional, default is None]

        The API understands several parameters related to date ranges. Date
        formats are pretty flexible, however the closer to ISO 8601, the
        better.

        The date related options are 'begin_date', 'end_date', 'date', and
        'range'.  They can be combined in the following 5 ways, but if
        conflicting then follows the table in order.  For example, the 'date'
        option will be used if present regardless of any other option, then
        'range', ...etc.:

        +-------------------+--------------------------------------------------+
        | Parameter Name(s) | Description                                      |
        +===================+==================================================+
        | date              | 'latest', 'today', or 'recent'                   |
        +-------------------+--------------------------------------------------+
        | range             | Specify a number of hours to go back from now    |
        |                   | and retrieve data for that date range            |
        +-------------------+--------------------------------------------------+
        | begin_date and    | Specify a begin date and a number of hours to    |
        | range             | retrieve data starting from that date            |
        +-------------------+--------------------------------------------------+
        | begin_date and    | Specify the date/time range of retrieval         |
        | end_date          |                                                  |
        +-------------------+--------------------------------------------------+
        | end_date and      | Specify an end date and a number of hours to     |
        | range             | retrieve data ending at that date                |
        +-------------------+--------------------------------------------------+

        +--------------------------------------+-----------------+
        | Description of "--date" option       | Option          |
        +======================================+=================+
        | Today's data                         | --date='today'  |
        +--------------------------------------+-----------------+
        | The last 3 days of data              | --date='recent' |
        +--------------------------------------+-----------------+
        | The last data point available within | --date='latest' |
        | the last 18 minutes.                 |                 |
        +--------------------------------------+-----------------+

    begin_date
        [optional, default is None]

        The beginning date for the data.  See explanation with the 'date'
        option on how to use all of the date related parameters.

    end_date
        [optional, default is None]

        The end date for the data.  January 1st, 2012 through January 2nd,
        2012::

            --begin_date='20120101' --end_date='20120102'

        See explanation with the 'date' option on how to use all of the date
        related parameters.

    range
        [optional, default is None]

        Specify the number of hours to go back from now, an 'end_date', or
        forward from a 'begin_date'.

        48 hours beginning on April 15, 2012::

            --begin_date='20120415' --range=48

        48 hours ending on March 17, 2012::

            --end_date='20120307' --range=48

        The last 24 hours from now::

            --range=24

        The last 3 hours from now::

            --range=3

        See explanation with the 'date' option on how to use all of the date
        related parameters.

    product : str
        [optional, default is 'hourly_height']

        Specify the observation requested.

        +------------------------+---------------------------------------------+
        | Option                 | Description                                 |
        +========================+=============================================+
        | water_level            | Six minute preliminary or verified water    |
        |                        | levels, depending on availability.          |
        +------------------------+---------------------------------------------+
        | air_temperature        | Air temperature                             |
        +------------------------+---------------------------------------------+
        | water_temperature      | Water temperature                           |
        +------------------------+---------------------------------------------+
        | wind                   | Wind speed, direction, and gusts            |
        +------------------------+---------------------------------------------+
        | air_gap                | (distance between a bridge and the water's  |
        |                        | surface)                                    |
        +------------------------+---------------------------------------------+
        | conductivity           | The water's conductivity                    |
        +------------------------+---------------------------------------------+
        | visibility             | Visibility from the station's visibility    |
        |                        | sensor. A measure of atmospheric clarity.   |
        +------------------------+---------------------------------------------+
        | humidity               | Relative humidity                           |
        +------------------------+---------------------------------------------+
        | salinity               | Salinity and specific gravity               |
        +------------------------+---------------------------------------------+
        | hourly_height          | Verified hourly height water level data     |
        +------------------------+---------------------------------------------+
        | high_low               | Verified high/low water level data          |
        +------------------------+---------------------------------------------+
        | daily_mean             | Verified daily mean water level data        |
        +------------------------+---------------------------------------------+
        | monthly_mean           | Verified monthly mean water level data      |
        +------------------------+---------------------------------------------+
        | one_minute_water_level | One minute water level data                 |
        +------------------------+---------------------------------------------+
        | predictions            | Six minute predictions water level data     |
        +------------------------+---------------------------------------------+
        | datums                 | datums data                                 |
        +------------------------+---------------------------------------------+
        | currents               | Currents data                               |
        +------------------------+---------------------------------------------+

        The returned data for each "product" documented below is
        derived from
        https://api.tidesandcurrents.noaa.gov/api/prod/responseHelp.html

        product = "water_level"

        +-----------------------------+----------------------------------------+
        | tsgettoolbox Column Name    | Description                            |
        +=============================+========================================+
        | water_level:{units}         | Measurement                            |
        +-----------------------------+----------------------------------------+
        | water_level_sigma:{units}   | Standard deviation of 1 second samples |
        |                             | used to compute the water level height |
        +-----------------------------+----------------------------------------+
        | water_level_CntSigma OR     | if preliminary Count of number of 1    |
        | water_level_Inferred        | second that falls outside a 3-sigma    |
        |                             | band about the mean if verified A flag |
        |                             | that when set to 1 indicates that the  |
        |                             | water level value has been inferred    |
        +-----------------------------+----------------------------------------+
        | water_level_FlatTol         | A flag that when set to 1 indicates    |
        |                             | that the flat tolerance limit was      |
        |                             | exceeded                               |
        +-----------------------------+----------------------------------------+
        | water_level_RateTol         | A flag that when set to 1 indicates    |
        |                             | that the rate of change tolerance      |
        |                             | limit was exceeded                     |
        +-----------------------------+----------------------------------------+
        | water_level_LimitTol OR     | if preliminary A flag that when set to |
        | water_level_TempRateTol     | 1 indicates that either the maximum or |
        |                             | minimum expected value was exceeded if |
        |                             | verified A flag that when set to 1     |
        |                             | indicates that the rate of change in   |
        |                             | temperature tolerance limit was        |
        |                             | exceeded                               |
        +-----------------------------+----------------------------------------+
        | water_level_quality:{units} | Quality Assurance/Quality Control "p"  |
        |                             | = preliminary "v" = verified           |
        +-----------------------------+----------------------------------------+

        product = "air_pressure", "air_temperature", "humidity",
        "water_temperature", or "conductivity"

        +-------------------+--------------------------------------------------+
        | tsgettoolbox      | Description                                      |
        | Column Name       |                                                  |
        +===================+==================================================+
        | {product}:{units} | Measurement                                      |
        +-------------------+--------------------------------------------------+
        | {product}_MaxTol  | A flag that when set to 1 indicates that the     |
        |                   | maximum expected value was exceeded              |
        +-------------------+--------------------------------------------------+
        | {product}_MinTol  | A flag that when set to 1 indicates that the     |
        |                   | minimum expected value was exceeded              |
        +-------------------+--------------------------------------------------+
        | {product}_RateTol | A flag that when set to 1 indicates that the     |
        |                   | rate of change tolerance limit was exceeded      |
        +-------------------+--------------------------------------------------+

        Hourly Height: product = "hourly_height"

        +-----------------------------+----------------------------------------+
        | tsgettoolbox Column Name    | Description                            |
        +=============================+========================================+
        | hourly_height:{units}       | Value - Measured water level height    |
        +-----------------------------+----------------------------------------+
        | hourly_height_sigma:{units} | Sigma - Standard deviation of 1 second |
        |                             | samples used to compute the water      |
        |                             | level height                           |
        +-----------------------------+----------------------------------------+
        | hourly_height_Inferred      | A flag that when set to 1 indicates    |
        |                             | that the water level value has been    |
        |                             | inferred                               |
        +-----------------------------+----------------------------------------+
        | hourly_height_LimitTol      | A flag that when set to 1 indicates    |
        |                             | that either the maximum or minimum     |
        |                             | expected value was exceeded            |
        +-----------------------------+----------------------------------------+

        High Low: product = "high_low"

        +-------------------+--------------------------------------------------+
        | tsgettoolbox      | Description                                      |
        | Column Name       |                                                  |
        +===================+==================================================+
        | high_low:{units}  | Value - Measured water level height              |
        +-------------------+--------------------------------------------------+
        | high_low_Type     | Type - Designation of Water level height. HH =   |
        |                   | Higher High water H = High water L = Low water   |
        |                   | LL = Lower Low water                             |
        +-------------------+--------------------------------------------------+
        | high_low_Inferred | A flag that when set to 1 indicates that the     |
        |                   | water level value has been inferred              |
        +-------------------+--------------------------------------------------+
        | high_low_LimitTol | A flag that when set to 1 indicates that either  |
        |                   | the maximum or minimum expected value was        |
        |                   | exceeded                                         |
        +-------------------+--------------------------------------------------+

        Daily Mean: product = "daily_mean"

        +---------------------+------------------------------------------------+
        | tsgettoolbox Column | Description                                    |
        | Name                |                                                |
        +=====================+================================================+
        | daily_mean:{units}  | Value – Mean hourly data over a 24 hour period |
        +---------------------+------------------------------------------------+
        | daily_mean_Inferred | A flag that when set to 1 indicates that the   |
        |                     | water level value has been inferred            |
        +---------------------+------------------------------------------------+
        | daily_mean_LimitTol | A flag that when set to 1 indicates that       |
        |                     | either the maximum or minimum expected value   |
        |                     | was exceeded                                   |
        +---------------------+------------------------------------------------+

        Monthly Mean: product = "monthly_mean"

        +--------------+-------------------------------------------------------+
        | tsgettoolbox | Description                                           |
        | Column Name  |                                                       |
        +==============+=======================================================+
        | year         | Year                                                  |
        +--------------+-------------------------------------------------------+
        | month        | Month                                                 |
        +--------------+-------------------------------------------------------+
        | highest      | Highest Tide                                          |
        +--------------+-------------------------------------------------------+
        | MHHW         | Mean Higher-High Water                                |
        +--------------+-------------------------------------------------------+
        | MHW          | Mean High Water                                       |
        +--------------+-------------------------------------------------------+
        | MSL          | Mean Sea Level                                        |
        +--------------+-------------------------------------------------------+
        | MTL          | Mean Tide Level                                       |
        +--------------+-------------------------------------------------------+
        | MLW          | Mean Low Water                                        |
        +--------------+-------------------------------------------------------+
        | MLLW         | Mean Lower-Low Water                                  |
        +--------------+-------------------------------------------------------+
        | DTL          | Mean Diurnal Tide Level                               |
        +--------------+-------------------------------------------------------+
        | GT           | Great Diurnal Range                                   |
        +--------------+-------------------------------------------------------+
        | MN           | Mean Range of Tide                                    |
        +--------------+-------------------------------------------------------+
        | DHQ          | Mean Diurnal High Water Inequality                    |
        +--------------+-------------------------------------------------------+
        | DLQ          | Mean Diurnal Low Water Inequality                     |
        +--------------+-------------------------------------------------------+
        | HWI          | Greenwich High Water Interval (in Hours)              |
        +--------------+-------------------------------------------------------+
        | LWI          | Greenwich Low Water Interval (in Hours)               |
        +--------------+-------------------------------------------------------+
        | lowest       | Lowest Tide                                           |
        +--------------+-------------------------------------------------------+
        | inferred     | A flag that when set to 1 indicates that the water    |
        |              | level value has been inferred                         |
        +--------------+-------------------------------------------------------+

        One Minute Water Level: product = "one_minute_water_level"

        +--------------------------------+-------------------------------------+
        | tsgettoolbox Column Name       | Description                         |
        +================================+=====================================+
        | one_minute_water_level:{units} | Value - Measured water level height |
        +--------------------------------+-------------------------------------+

        Tide Predictions: product = "predictions"

        +---------------------+--------------------------------------+
        | tsgettoolbox        |                                      |
        | Column              |                                      |
        | Name                | Description                          |
        +=====================+======================================+
        | predictions:{units} | Value - Predicted water level height |
        +---------------------+--------------------------------------+

        Air Gap: product = "air_gap"

        +-----------------------+----------------------------------------------+
        | tsgettoolbox Column   | Description                                  |
        | Name                  |                                              |
        +=======================+==============================================+
        | air_gap:{units}       | Value - Measured air gap                     |
        +-----------------------+----------------------------------------------+
        | air_gap_sigma:{units} | Sigma - Standard deviation of 1 second       |
        |                       | samples used to compute the air gap          |
        +-----------------------+----------------------------------------------+
        | air_gap_CntSigma      | Count of number of 1 second that falls       |
        |                       | outside a 3-sigma band about the mean        |
        +-----------------------+----------------------------------------------+
        | air_gap_FlatTol       | A flag that when set to 1 indicates that the |
        |                       | flat tolerance limit was exceeded            |
        +-----------------------+----------------------------------------------+
        | air_gap_RateTol       | A flag that when set to 1 indicates that the |
        |                       | rate of change tolerance limit was exceeded  |
        +-----------------------+----------------------------------------------+
        | air_gap_MinMaxTol     | A flag that when set to 1 indicates that     |
        |                       | either the maximum or minimum expected air   |
        |                       | gap limit was exceeded                       |
        +-----------------------+----------------------------------------------+

        Wind: product = "wind"

        +------------------------+---------------------------------------------+
        | tsgettoolbox Column    | Description                                 |
        | Name                   |                                             |
        +========================+=============================================+
        | wind_speed:{units}     | Speed - Measured wind speed                 |
        +------------------------+---------------------------------------------+
        | wind_direction:degrees | Direction - wind direction in degrees       |
        +------------------------+---------------------------------------------+
        | wind_direction:text    | Direction - wind direction in text          |
        +------------------------+---------------------------------------------+
        | wind_gust:{units}      | Gust - Measured wind gust speed             |
        +------------------------+---------------------------------------------+
        | wind{suffix}           | Data Flags - in order of listing "X,R"      |
        |                        | Flags described above                       |
        +------------------------+---------------------------------------------+

        Visibility: product = "visibility"

        +--------------------+-----------------------------+
        | tsgettoolbox       |                             |
        | Column             |                             |
        | Name               | Description                 |
        +====================+=============================+
        | visibility:{units} | Value - Measured visibility |
        +--------------------+-----------------------------+

        Salinity: product = "salinity"

        +------------------+------------------+
        | tsgettoolbox     |                  |
        | Column           |                  |
        | Name             | Description      |
        +==================+==================+
        | salinity:{units} | Salinity         |
        +------------------+------------------+
        | specific_gravity | Specific Gravity |
        +------------------+------------------+

        Currents: product = "currents"

        +----------------------------+-----------------------------------------+
        | tsgettoolbox Column Name   | Description                             |
        +============================+=========================================+
        | currents_speed:{units}     | Speed - Measured current speed          |
        +----------------------------+-----------------------------------------+
        | currents_direction:degrees | Direction - current direction in        |
        |                            | degrees                                 |
        +----------------------------+-----------------------------------------+
        | currents_bin_number        | Bin number                              |
        +----------------------------+-----------------------------------------+

    datum
        [optional, default is 'NAVD']

        Specify the datum that all water levels will be
        reported against.  Note! Datum is mandatory for all water level
        products and defaults to "NAVD".

        +--------+-------------------------------+
        | Option | Description                   |
        +========+===============================+
        | MHHW   | Mean Higher High Water        |
        +--------+-------------------------------+
        | MHW    | Mean High Water               |
        +--------+-------------------------------+
        | MTL    | Mean Tide Level               |
        +--------+-------------------------------+
        | MSL    | Mean Sea Level                |
        +--------+-------------------------------+
        | MLW    | Mean Low Water                |
        +--------+-------------------------------+
        | MLLW   | Mean Lower Low Water          |
        +--------+-------------------------------+
        | NAVD   | North American Vertical Datum |
        +--------+-------------------------------+
        | STND   | Station Datum                 |
        +--------+-------------------------------+

    time_zone
        [optional, default is 'GMT']

        The time zone is specified as 'gmt', 'lst'
        or 'lst_ldt'.

        +---------+------------------------------------------------------------+
        | Option  | Description                                                |
        +=========+============================================================+
        | gmt     | Greenwich Mean Time                                        |
        +---------+------------------------------------------------------------+
        | lst     | Local Standard Time. The time local to the requested       |
        |         | station.                                                   |
        +---------+------------------------------------------------------------+
        | lst_ldt | Local Standard/Local Daylight Time. The time local to the  |
        |         | requested station.                                         |
        +---------+------------------------------------------------------------+

    interval
        [optional, defaults to 'h']

        Deliver the meteorological and prediction data at hourly
        intervals.  Does not override 6 minute intervals for
        --product='water_level' or 1 minute intervals for
        --product='one_minute_water_level'.

        +--------+-----------------------------------------------+
        | Option | Description                                   |
        +========+===============================================+
        | h      | Hourly meteorological data                    |
        +--------+-----------------------------------------------+
        | hilo   | High/low predictions for subordinate stations |
        +--------+-----------------------------------------------+

    bin
        [optional, defaults to None]

        The bin number for the specified currents station Example:'--bin=4'
        Will retrieve data for bin number 4. Note! If a bin is not specified
        for a PORTS station, the data is returned using a predefined real-time
        bin.
    """
    tsutils.printiso(
        coops(
            station,
            date=date,
            begin_date=begin_date,
            end_date=end_date,
            range=range,
            product=product,
            datum=datum,
            time_zone=time_zone,
            interval=interval,
            bin=bin,
        )
    )


deltas = {
    "water_level": 31,
    "air_temperature": 365,
    "water_temperature": 365,
    "wind": 365,
    "air_gap": 31,
    "conductivity": 365,
    "visibility": 365,
    "humidity": 365,
    "salinity": 31,
    "hourly_height": 365,
    "high_low": 365,
    "daily_mean": 3650,
    "monthly_mean": 3650,
    "one_minute_water_level": 4,
    "predictions": 31,
    "datums": 31,
    "currents": 31,
    "air_pressure": 365,
}


@tsutils.transform_args(
    product=tsutils.make_list,
    time_zone=str.upper,
    datum=str.upper,
    begin_date=tsutils.parsedate,
    end_date=tsutils.parsedate,
)
@tsutils.copy_doc(coops_cli)
def coops(
    station: str,
    date: Literal["latest", "today", "recent"] = None,
    begin_date: Optional[pd.Timestamp] = None,
    end_date: Optional[pd.Timestamp] = None,
    range: Optional[int] = None,
    product: Union[
        List[
            Literal[
                "water_level",
                "air_temperature",
                "water_temperature",
                "wind",
                "air_gap",
                "conductivity",
                "visibility",
                "humidity",
                "salinity",
                "hourly_height",
                "high_low",
                "daily_mean",
                "monthly_mean",
                "one_minute_water_level",
                "predictions",
                "datums",
                "currents",
                "air_pressure",
            ]
        ],
        str,
    ] = "hourly_height",
    datum: Literal["MHHW", "MHW", "MTL", "MSL", "MLW", "MLLW", "NAVD", "STND"] = "NAVD",
    time_zone: Literal["GMT", "UTC", "LST", "LST_LDT"] = "GMT",
    interval="h",
    bin=None,
):
    r"""Download Center for Operational Oceanographic Products and Services."""
    disable_caching = False
    params = {
        "station": station,
        "product": product,
        "bin": bin,
        "interval": interval,
        "units": "metric",
        "time_zone": time_zone,
        "datum": datum,
        "format": "json",
        "application": "tsgettoolbox",
        "date": date,
        "begin_date": begin_date,
        "end_date": end_date,
        "range": range,
    }

    if date is not None:
        begin_date = None
        end_date = None
        range = None
        disable_caching = True
    if range is not None and begin_date is None and end_date is None:
        disable_caching = True
    if begin_date is not None and range is not None:
        end_date = None
    if begin_date is not None and end_date is not None:
        range = None

    # Normalize begin_data and end_date to not extend beyond the "established"
    # and "removed" dates of the station.
    if (date is None) and (range is None):
        try:
            station_data = ar.retrieve_json(
                [
                    f"https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/{station}/details.json"
                ],
                [{"params": {"expand": "detail", "units": "english"}}],
            )
        except ar.exceptions.ServiceError:
            station_data = ar.retrieve_json(
                [
                    f"https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/{station}.json"
                ],
                [{"params": {"expand": "detail", "units": "english"}}],
            )
        try:
            test_begin = pd.Timestamp(station_data[0]["established"])
        except KeyError:
            test_begin = pd.Timestamp("1970-01-01")
        if (begin_date is None) or (begin_date < test_begin):
            begin_date = test_begin
        try:
            test_end = pd.Timestamp(station_data[0]["removed"])
        except KeyError:
            test_end = pd.Timestamp(datetime.datetime.utcnow())
        if test_end is pd.NaT:
            test_end = datetime.datetime.utcnow()
        if (end_date is None) or (end_date > test_end):
            end_date = test_end

    if params["begin_date"] is not None:
        params["begin_date"] = params["begin_date"].strftime("%Y%m%d")

    if params["end_date"] is not None:
        params["end_date"] = params["end_date"].strftime("%Y%m%d")

    if len(product) > 1 and "datums" in product:
        raise ValueError(
            tsutils.error_wrapper(
                """
                The "datums" product is not a time-series and can't be mixed
                with other products."
                """
            )
        )

    ndf = pd.DataFrame()
    for produc in product:
        if produc == "datums":
            params["range"] = 1
            params["begin_date"] = None
            params["end_date"] = None

        periods = []
        if params["begin_date"] is not None and params["end_date"] is not None:
            delta = datetime.timedelta(days=deltas[produc])
            period_start = parser.parse(params["begin_date"])
            while period_start < parser.parse(params["end_date"]):
                period_end = min(period_start + delta, parser.parse(params["end_date"]))
                periods.append((period_start, period_end))
                period_start = period_end

        urls = [r"https://tidesandcurrents.noaa.gov/api/datagetter"]
        kwds = [{"params": params}]

        if params["begin_date"] is not None and params["end_date"] is not None:
            urls, kwds = zip(
                *[
                    (
                        r"https://tidesandcurrents.noaa.gov/api/datagetter",
                        {
                            "params": {
                                "station": station,
                                "date": date,
                                "range": range,
                                "product": produc,
                                "bin": bin,
                                "interval": interval,
                                "units": "metric",
                                "time_zone": time_zone,
                                "datum": datum,
                                "begin_date": s.strftime("%Y%m%d"),
                                "end_date": e.strftime("%Y%m%d"),
                                "format": "json",
                                "application": "tsgettoolbox",
                            }
                        },
                    )
                    for s, e in periods
                ]
            )

        kwds = [
            {"params": {k: v for k, v in i["params"].items() if v is not None}}
            for i in kwds
        ]
        resp = ar.retrieve_json(urls, kwds, disable=disable_caching)
        if produc == "datums":
            resp = [i["datums"] for i in resp if "datums" in i]
        elif produc == "predictions":
            resp = [i["predictions"] for i in resp if "predictions" in i]
        else:
            resp = [i["data"] for i in resp if "data" in i]

        if not resp:
            warnings.warn(
                tsutils.error_wrapper(
                    """
                    No data for this product and time frame at this station.
                    """
                )
            )
            return pd.DataFrame()

        resp = [item for sublist in resp for item in sublist]
        resp = pd.DataFrame(resp)
        if produc == "datums":
            resp = resp.set_index("n")
        elif produc == "monthly_mean":
            resp["t"] = pd.to_datetime(resp[["year", "month"]].assign(Day=1))
            resp = resp.drop(["year", "month"], axis="columns")
            resp = resp.set_index("t")
        else:
            resp = resp.set_index("t")

        time_zone_name = params["time_zone"].upper()
        if time_zone_name == "GMT":
            time_zone_name = "UTC"
        resp.index.name = f"Datetime:{time_zone_name}"

        if produc == "datums":
            resp.index.name = "Datums"

        if "f" in resp.columns:
            addcols = resp["f"].str.split(pat=",", expand=True)
            resp = resp.drop("f", axis="columns")
            addcols.columns = _settings_map[produc][2]
            resp = resp.join(addcols)

        units = _settings_map[produc][0][params["units"]]
        if produc in ("wind", "currents"):
            rename_cols = {
                "s": f"{produc}_speed:{units}",
                "g": f"wind_gust:{units}",
            }
            resp = resp.rename(rename_cols, axis="columns")
        elif produc == "salinity":
            rename_cols = {
                "s": f"salinity:{units}",
                "g": "specific_gravity",
            }
            resp = resp.rename(rename_cols, axis="columns")
        rename_cols = {
            "v": f"{produc}:{units}",
            "s": f"{produc}_sigma:{units}",
            "q": f"{produc}_quality",
            "Inferred": f"{produc}_Inferred",
            "MaxTol": f"{produc}_MaxTol",
            "MinTol": f"{produc}_MinTol",
            "LimitTol": f"{produc}_LimitTol",
            "TempRateTol": f"{produc}_TempRateTol",
            "RateTol": f"{produc}_RateTol",
            "ty": f"{produc}_Type",
            "d": f"{produc}_direction:degrees",
            "dr": f"{produc}_direction:text",
            "b": f"{produc}_bin_number",
            "a": f"{produc}_MinMaxTol",
            "o": f"{produc}_CntSigma",
        }
        resp = resp.rename(rename_cols, axis="columns")
        ndf = ndf.join(resp, how="outer")
    with suppress():
        ndf.index = pd.to_datetime(ndf.index)
    return ndf


if __name__ == "__main__":
    """
    https://tidesandcurrents.noaa.gov/api/datagetter?begin_date=20020101
    &end_date=20020102&range=1&station=8720218&product=water_level
    """

    r = coops(
        station="8720218",
        product="water_level",
        time_zone="lst",
        datum="mllw",
        range=20,
        begin_date=None,
        end_date=None,
        date=None,
    )

    print("tidesandcurrents 1 range=20")
    print(r)

    r = coops(
        station="8720218",
        product="water_temperature",
        interval="h",
        time_zone="gmt",
        datum="mllw",
        begin_date="01/10/2002",
        range=2,
        end_date=None,
        date=None,
    )

    print("tidesandcurrents 2 begin_date 01/10/2002 and range=2")
    print(r)

    r = coops(
        station="8720218",
        product="water_level",
        interval="h",
        time_zone="gmt",
        datum="mllw",
        begin_date="01/10/2002",
        range=5,
        end_date=None,
        date=None,
    )

    print("tidesandcurrents 3 begin_date 01/10/2002 and range=5")
    print(r)

    r = coops(
        station="8720218",
        product="air_temperature",
        interval="h",
        time_zone="gmt",
        datum="mllw",
        end_date="01/10/2002",
        range=3,
        begin_date=None,
        date=None,
    )

    print("tidesandcurrents 4 range=3 end_date-01/10/2002")
    print(r)

    r = coops(
        station="8720218",
        product="water_level",
        interval="h",
        time_zone="gmt",
        datum="mllw",
        begin_date="01/10/2002",
        end_date="2003-01-01",
        range=None,
        date=None,
    )

    print("tidesandcurrents 5 begin_date=01/10/2002 end_date=2003/01/01")
    print(r)

    try:
        r = coops(
            station="8720218",
            product="water_level",
            time_zone="gmt",
            datum="mllw",
            begin_date=None,
            end_date=None,
            range=745,
            date=None,
        )
        print(r)
    except ValueError:
        print("Correct ValueError")

    for prod in _settings_map:
        print(f"!!!!{prod}")
        r = coops(
            station="8720218",
            product=prod,
            interval="h",
            time_zone="gmt",
            datum="mllw",
            begin_date="01/10/2002",
            end_date="2003-01-01",
            range=None,
            date=None,
        )

        print(r)

    print("hourly_height and wind")
    r = coops(
        station="8720218",
        product=["hourly_height", "wind"],
        interval="h",
        time_zone="gmt",
        datum="mllw",
        begin_date="01/10/2002",
        end_date="2003-01-01",
        range=None,
        date=None,
    )
    print(r)

    print("hourly_height")
    r = coops(
        station="8720218",
        product="hourly_height",
        time_zone="lst",
        datum="navd",
        begin_date="01/01/2017",
        end_date="2017-12-31",
    )
    print(r)
