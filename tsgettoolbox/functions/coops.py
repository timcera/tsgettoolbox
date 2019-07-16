import mando
from tsgettoolbox.odo import odo, resource
import pandas as pd

try:
    from mando.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter

from tstoolbox import tsutils


@mando.command("coops", formatter_class=HelpFormatter, doctype="numpy")
@tsutils.doc(tsutils.docstrings)
def coops_cli(
    station,
    date=None,
    begin_date=None,
    end_date=None,
    range=None,
    product="water_level",
    datum="NAVD",
    time_zone="GMT",
    interval="h",
    bin=None,
):
    r"""Download Center for Operational Oceanographic Products and Services.

    CO-OPS web services is at http://tidesandcurrents.noaa.gov/api/.  The time
    zone of the returned data depends on the setting of the "time_zone" option.
    The default is "GMT" also known as "UTC".

    Parameters
    ----------
    station
        A 7 character station ID, or a currents station ID.  Specify the
        station ID with the "station=" parameter.::

            Example: '--station=9414290'

        Station listings for various products can be viewed at
        http://tidesandcurrents.noaa.gov or viewed on a map at Tides & Currents
        Station Map

    date : str
        [optional, default is None]

        The API understands several parameters related to date ranges.  Date
        formats are pretty flexible, however the closer to ISO 8601, the
        better.

        The date related options are 'begin_date', 'end_date', 'date', and
        'range'.  They can be combined in the following 5 ways, but if
        conflicting then follows the table in order.  For example, the 'date'
        option will be used if present regardless of any other option, then
        'range', ...etc.:

        +--------------------+---------------------------------------+
        | Parameter Name(s)  | Description                           |
        +====================+=======================================+
        | '--date'           | 'latest', 'today', or 'recent'        |
        +--------------------+---------------------------------------+
        | '--range'          | Specify a number of hours to go back  |
        |                    | from now and retrieve data for that   |
        |                    | date range                            |
        +--------------------+---------------------------------------+
        | '--begin_date' and | Specify a begin date and a number of  |
        | '--range'          | hours to retrieve data starting from  |
        |                    | that date                             |
        +--------------------+---------------------------------------+
        | '--begin_date' and | Specify the date/time range of        |
        | '--end_date'       | retrieval                             |
        +--------------------+---------------------------------------+
        | '--end_date' and a | Specify an end date and a number of   |
        | '--range'          | hours to retrieve data ending at that |
        |                    | date                                  |
        +--------------------+---------------------------------------+

        +-------------------+--------------------------------------+
        | Maximum Retrieval | Data Types                           |
        +===================+======================================+
        | 31 days           | All 6 minute data products           |
        +-------------------+--------------------------------------+
        | 1 year            | Hourly Height, and High/Low          |
        +-------------------+--------------------------------------+
        | 10 years          | Tide Predictions, Daily, and Monthly |
        |                   | Means                                |
        +-------------------+--------------------------------------+

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
        [optional, default is 'water_level']

        Specify the observation requested.  If not specified will download all
        data from that station.

        +------------------------+-------------------------------------+
        | Option                 | Description                         |
        +========================+=====================================+
        | water_level            | Preliminary or verified water       |
        |                        | levels, depending on availability.  |
        +------------------------+-------------------------------------+
        | air_temperature        | Air temperature                     |
        +------------------------+-------------------------------------+
        | water_temperature      | Water temperature                   |
        +------------------------+-------------------------------------+
        | wind                   | Wind speed, direction, and gusts    |
        +------------------------+-------------------------------------+
        | air_gap                | (distance between a bridge and the  |
        |                        | water's surface)                    |
        +------------------------+-------------------------------------+
        | conductivity           | The water's conductivity            |
        +------------------------+-------------------------------------+
        | visibility             | Visibility from the station's       |
        |                        | visibility sensor. A measure of     |
        |                        | atmospheric clarity.                |
        +------------------------+-------------------------------------+
        | humidity               | Relative humidity                   |
        +------------------------+-------------------------------------+
        | salinity               | Salinity and specific gravity       |
        +------------------------+-------------------------------------+
        | hourly_height          | Verified hourly height water level  |
        |                        | data                                |
        +------------------------+-------------------------------------+
        | high_low               | Verified high/low water level data  |
        +------------------------+-------------------------------------+
        | daily_mean             | Verified daily mean water level     |
        |                        | data                                |
        +------------------------+-------------------------------------+
        | monthly_mean           | Verified monthly mean water level   |
        |                        | data                                |
        +------------------------+-------------------------------------+
        | one_minute_water_level | One minute water level data         |
        +------------------------+-------------------------------------+
        | predictions            | 6 minute predictions water level    |
        |                        | data                                |
        +------------------------+-------------------------------------+
        | datums                 | datums data                         |
        +------------------------+-------------------------------------+
        | currents               | Currents data                       |
        +------------------------+-------------------------------------+

        Possible water level height variables:

        +-------+----------------------------------------------------------+
        | Name  | Description                                              |
        +=======+==========================================================+
        | Sigma | Standard deviation of 1 second samples used to compute   |
        |       | the water level height                                   |
        +-------+----------------------------------------------------------+
        | O     | Count of number of samples that fall outside a 3-sigma   |
        |       | band about the mean                                      |
        +-------+----------------------------------------------------------+
        | I     | A flag that indicates that the water level value has     |
        |       | been inferred.                                           |
        +-------+----------------------------------------------------------+
        | F     | A flag that when set to 1 indicates that the flat        |
        |       | tolerance limit was exceeded                             |
        +-------+----------------------------------------------------------+
        | R     | A flag that when set to 1 indicates that the rate of     |
        |       | change tolerance limit was exceeded                      |
        +-------+----------------------------------------------------------+
        | T     | A flag that when set to 1 indicates that the temperature |
        |       | difference tolerance limit was exceeded                  |
        +-------+----------------------------------------------------------+
        | L     | A flag that when set to 1 indicates that either the      |
        |       | maximum or minimum expected water level height limit     |
        |       | was exceeded                                             |
        +-------+----------------------------------------------------------+

        Meteorological and ancillary data variables:

        +------+------------------------------------------------------+
        | Name | Description                                          |
        +======+======================================================+
        | X    | A flag that when set to 1 indicates that the maximum |
        |      | value was exceeded                                   |
        +------+------------------------------------------------------+
        | N    | A flag that when set to 1 indicates that the minimum |
        |      | expected value was exceeded                          |
        +------+------------------------------------------------------+
        | R    | A flag that when set to 1 indicates that the rate of |
        |      | change tolerance limit was exceeded                  |
        +------+------------------------------------------------------+

    datum
        [optional, default is 'NAVD']

        Specify the datum that all water levels will be
        reported against.  Note! Datum is mandatory for all water level
        products.

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

        +---------+----------------------------------------------------+
        | Option  | Description                                        |
        +=========+====================================================+
        | gmt     | Greenwich Mean Time                                |
        +---------+----------------------------------------------------+
        | lst     | Local Standard Time. The time local to the         |
        |         | requested station.                                 |
        +---------+----------------------------------------------------+
        | lst_ldt | Local Standard/Local Daylight Time. The time local |
        |         | to the requested station.                          |
        +---------+----------------------------------------------------+

    interval
        [optional, defaults to 'h']

        Deliver the Meteorological data at hourly intervals.  Does not override
        6 minute intervals for --product='water_level'.

    bin
        [optional, defaults to None]

        The bin number for the specified currents station Example:'--bin=4'
        Will retrieve data for bin number 4. Note! If a bin is not specified
        for a PORTS station, the data is returned using a predefined real-time
        bin.

    """
    tsutils._printiso(
        coops_cli(
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


def coops(
    station,
    date=None,
    begin_date=None,
    end_date=None,
    range=None,
    product="water_level",
    datum="NAVD",
    time_zone="GMT",
    interval="h",
    bin=None,
):
    r"""Download Center for Operational Oceanographic Products and Services."""
    from tsgettoolbox.services import coops as placeholder

    r = resource(
        r"http://tidesandcurrents.noaa.gov/api/datagetter",
        station=station,
        date=date,
        begin_date=begin_date,
        end_date=end_date,
        range=range,
        product=product,
        datum=datum,
        units="metric",
        time_zone=time_zone,
        interval=interval,
        bin=bin,
    )
    return odo(r, pd.DataFrame)
