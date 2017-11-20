#!/usr/bin/env python
r"""tsgettoolbox command line/library tools to retrieve time series.
This program is a collection of utilities to download data from various
web services.
"""

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys
import os.path
import warnings

from odo import odo, resource
import pandas as pd
import mando

try:
    from mando.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter

from tstoolbox import tsutils

warnings.filterwarnings('ignore')


@mando.command()
def about():
    r"""Print out information about tsgettoolbox and the system.
    """
    tsutils.about(__name__)


@mando.command(formatter_class=HelpFormatter, doctype='numpy')
@tsutils.doc(tsutils.docstrings)
def cpc(state=None,
        climate_division=None,
        start_date=None,
        end_date=None):
    """
    This module provides direct access to Climate Prediction Center, Weekly
    Drought Index dataset.

    Climate Prediction Center: http://www.cpc.ncep.noaa.gov/
    Weekly Drought Index: http://www.cpc.ncep.noaa.gov/products/analysis_monitoring/cdus/palmer_drought/

    Parameters
    ----------
    state : ``None`` or str
        If specified, results will be limited to the state corresponding to the
        given 2-character state code.
    climate_division : ``None`` or int
        If specified, results will be limited to the climate division.
    {start_date}
    {end_date}

    """
    from tsgettoolbox.services import cpc
    df = cpc.ulmo_df(
         state=state,
         climate_division=climate_division,
         start_date=tsutils.parsedate(start_date),
         end_date=tsutils.parsedate(end_date))
    return tsutils.printiso(df)


@mando.command(formatter_class=HelpFormatter, doctype='numpy')
@tsutils.doc(tsutils.docstrings)
def cdec(station_id,
         dur_code=None,
         sensor_num=None,
         start_date=None,
         end_date=None):
    r"""
    This module provides access to data provided by the `California Department
    of Water Resources`_ `California Data Exchange Center`_ web site.

    .. _California Department of Water Resources: http://www.water.ca.gov/
    .. _California Data Exchange Center: http://cdec.water.ca.gov

    Downloads data for a set of CDEC station and sensor ids. If either is not
    provided, all available data will be downloaded.

    Parameters
    ----------
    station_id: str
        Each string is the CDEC station ID and consist of three capital
        letters.
    sensor_num: integer, comma separated integers or ``None``

        If ``None`` will get all sensors at `station_id`.

        SELECTED CDEC SENSOR NUMBERS (these are not available for all
        sites):

        +------------+--------------------------------------------+
        | sensor_num | Description                                |
        +============+============================================+
        | 1          |  river stage [ft]                          |
        +------------+--------------------------------------------+
        | 2          |  precipitation accumulated [in]            |
        +------------+--------------------------------------------+
        | 3          |  SWE [in]                                  |
        +------------+--------------------------------------------+
        | 4          |  air temperature [F]                       |
        +------------+--------------------------------------------+
        | 5          |  EC [ms/cm]                                |
        +------------+--------------------------------------------+
        | 6          |  reservoir elevation [ft]                  |
        +------------+--------------------------------------------+
        | 7          |  reservoir scheduled release [cfs]         |
        +------------+--------------------------------------------+
        | 8          |  full natural flow [cfs]                   |
        +------------+--------------------------------------------+
        | 15         |  reservoir storage [af]                    |
        +------------+--------------------------------------------+
        | 20         |  flow -- river discharge [cfs]             |
        +------------+--------------------------------------------+
        | 22         |  reservoir storage change [af]             |
        +------------+--------------------------------------------+
        | 23         |  reservoir outflow [cfs]                   |
        +------------+--------------------------------------------+
        | 24         |  Evapotranspiration [in]                   |
        +------------+--------------------------------------------+
        | 25         |  water temperature [F]                     |
        +------------+--------------------------------------------+
        | 27         |  water turbidity [ntu]                     |
        +------------+--------------------------------------------+
        | 28         |  chlorophyll [ug/l]                        |
        +------------+--------------------------------------------+
        | 41         |  flow -- mean daily [cfs]                  |
        +------------+--------------------------------------------+
        | 45         |  precipitation incremental [in]            |
        +------------+--------------------------------------------+
        | 46         |  runoff volume [af]                        |
        +------------+--------------------------------------------+
        | 61         |  water dissolved oxygen [mg/l]             |
        +------------+--------------------------------------------+
        | 62         |  water pH value [pH]                       |
        +------------+--------------------------------------------+
        | 64         |  pan evaporation (incremental) [in]        |
        +------------+--------------------------------------------+
        | 65         |  full natural flow [af]                    |
        +------------+--------------------------------------------+
        | 66         |  flow -- monthly volume [af]               |
        +------------+--------------------------------------------+
        | 67         |  accretions (estimated) [af]               |
        +------------+--------------------------------------------+
        | 71         |  spillway discharge [cfs]                  |
        +------------+--------------------------------------------+
        | 74         |  lake evaporation (computed) [cfs]         |
        +------------+--------------------------------------------+
        | 76         |  reservoir inflow [cfs]                    |
        +------------+--------------------------------------------+
        | 85         |  control regulating discharge [cfs]        |
        +------------+--------------------------------------------+
        | 94         |  top conservation storage (reservoir) [af] |
        +------------+--------------------------------------------+
        | 100        |  water EC [us/cm]                          |
        +------------+--------------------------------------------+

    dur_code: str, comma separated strings, or ``None``
        Possible values are 'E', 'H', 'D', and 'M' but not
        all of these time resolutions are available at every station.

        +----------+-------------+
        | dur_code | Description |
        +==========+=============+
        | E        | event       |
        +----------+-------------+
        | H        | hourly      |
        +----------+-------------+
        | D        | daily       |
        +----------+-------------+
        | M        | monthly     |
        +----------+-------------+

    {start_date}
    {end_date}

    """
    from tsgettoolbox.services import cdec
    df = cdec.ulmo_df(
        station_id,
        dur_code=dur_code,
        sensor_num=sensor_num,
        start_date=tsutils.parsedate(start_date),
        end_date=tsutils.parsedate(end_date),
    )
    return tsutils.printiso(df)


@mando.command(formatter_class=HelpFormatter, doctype='numpy')
def coops(station,
          date=None,
          begin_date=None,
          end_date=None,
          range=None,
          product='water_level',
          datum='NAVD',
          units='metric',
          time_zone='GMT',
          interval='h',
          bin=None):
    r"""Download from Center for Operational Oceanographic Products and Services.

    CO-OPS web services is at http://tidesandcurrents.noaa.gov/api/.
    The time zone of the returned data depends on the setting of the
    "time_zone" option.  The default is "GMT" also known as "UTC".

    Parameters
    ----------
    station
        A 7 character station ID, or a currents
        station ID.  Specify the station ID with the "station="
        parameter.::

            Example: '--station=9414290'

        Station listings for various products can be viewed at
        http://tidesandcurrents.noaa.gov or viewed on a map at Tides
        & Currents Station Map
    date
        The API understands several parameters related
        to date ranges.  All dates can be formatted as follows::

            YyyyMMdd
            yyyyMMdd HH:mm
            MM/dd/yyyy
            MM/dd/yyyy HH:mm

        The date related options are 'begin_date', 'end_date', 'date',
        and 'range'.  They can be combined in the following 5 ways, but
        if conflicting then follows the table in order.  For example,
        the 'date' option will be used if present regardless of any
        other option, then 'range', ...etc.:

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
        The beginning date for the data.  See
        explanation with the 'date' option on how to use all of the date
        related parameters.

    end_date
        The end date for the data.  January 1st,
        2012 through January 2nd, 2012::

            --begin_date='20120101' --end_date='20120102'

        See explanation with the 'date' option on how to use all of the
        date related parameters.
    range
        Specify the number of hours to go back from
        now, an 'end_date', or forward from a 'begin_date'.

        48 hours beginning on April 15, 2012::

            --begin_date='20120415' --range=48

        48 hours ending on March 17, 2012::

            --end_date='20120307' --range=48

        The last 24 hours from now::

            --range=24

        The last 3 hours from now::

            --range=3

        See explanation with the 'date' option on how to use all of the
        date related parameters.

    product
        Specify the
        data.

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

    datum
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

    units
        Metric or english
        units.

        +---------+----------------------------------------------------+
        | Option  | Description                                        |
        +=========+====================================================+
        | metric  | Metric (Celsius, meters) units                     |
        +---------+----------------------------------------------------+
        | english | English (Imperial system) (fahrenheit, feet) units |
        +---------+----------------------------------------------------+

        The default is 'metric'.

    time_zone
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
        Deliver the Meteorological data at hourly
        intervals.  Does not override 6 minute intervals for
        --product='water_level'.  Defaults to 'h'.
    bin
        The bin number for the specified currents station
        Example:'--bin=4' Will retrieve data for bin number 4. Note! If
        a bin is not specified for a PORTS station, the data is returned
        using a predefined real-time bin.
    """
    from tsgettoolbox.services import coops as placeholder
    r = resource(
        r'http://tidesandcurrents.noaa.gov/api/datagetter',
        station=station,
        date=date,
        begin_date=tsutils.parsedate(begin_date),
        end_date=tsutils.parsedate(end_date),
        range=range,
        product=product,
        datum=datum,
        units=units,
        time_zone=time_zone,
        interval=interval,
        bin=bin,
    )
    return tsutils.printiso(odo(r, pd.DataFrame))


@mando.command(formatter_class=HelpFormatter, doctype='numpy')
def nwis(sites=None,
         stateCd=None,
         huc=None,
         bBox=None,
         countyCd=None,
         parameterCd=None,
         period=None,
         startDT=None,
         endDT=None,
         siteType=None,
         modifiedSince=None,
         agencyCd=None,
         siteStatus=None,
         altMin=None,
         altMax=None,
         drainAreaMin=None,
         drainAreaMax=None,
         aquiferCd=None,
         localAquiferCd=None,
         wellDepthMin=None,
         wellDepthMax=None,
         holeDepthMin=None,
         holeDepthMax=None,
         database='dv',
         statReportType=None,
         statType=None,
         missingData=None,
         statYearType=None):
    r"""
    Download from the USGS National Water Information Service (NWIS).

    Available databases:

    +--------------+-------------------------------+
    | --database=  | Database Name and Description |
    +==============+===============================+
    | iv           | Instantaneous Value sub-daily |
    |              | interval data starting in     |
    |              | 2007                          |
    +--------------+-------------------------------+
    | dv           | Daily Values database         |
    +--------------+-------------------------------+
    | stat         | daily/monthly/annual          |
    |              | statistics                    |
    +--------------+-------------------------------+
    | site         | Site metadata                 |
    +--------------+-------------------------------+
    | measurements | Field measurements            |
    +--------------+-------------------------------+
    | peak         | Peak flow and stage           |
    +--------------+-------------------------------+

    tsgettoolbox further can download the field measurements from
    a single site at a time using "--database=measurements" and peak
    measurements using "--database=peak".

    Detailed documnetation is available at
    http://waterdata.usgs.gov/nwis.

    Site local time is output, even if multiple sites are requested and
    sites are in different time zones.  Note that the measurement time
    zone at a site may not be the same as the time zone actually in
    effect at the site.

    Every query requires a major filter. Pick the major filter
    ('--sites', '--stateCd', '--huc', '--bBox', '--countyCd') that best
    retrieves the data for the sites that you are interested in.  You
    can have only one major filter per query. If you specify more than
    one major filter, you will get an error.

    **Major Filter**

    Select one of::

        '--sites',
        '--stateCd',
        '--huc',
        '--bBox', or
        '--countyCd'

    **Minor Filters**

    Additional filters can be applied after specifying a major filter. This
    further reduces the set of expected results. Users are encouraged to use
    minor filters because it allows more efficient use of this service.

    Use as many as desired to limit number of retrieved time series::

        '--parameterCd',
        '--siteType',
        '--modifiedSince',
        '--agencyCd',
        '--siteStatus',
        '--altMin',
        '--altMax',
        '--drainAreaMin',
        '--drainAreaMax',
        '--aquiferCd',
        '--localAquiferCd',
        '--wellDepthMin',
        '--wellDepthMax',
        '--holeDepthMin',
        '--holeDepthMax'

    The column name in the resulting table is made up of
    "USGS_SITE_CODE-parameterCd-statistic_code", for example
    "02248380-00010-00001".  The parameter code is described in the
    "parameterCd" option below.  The statistic code is described in the
    following table:

    +-------+---------------------+------------------------------------+
    | Code  | Name                | Description                        |
    +=======+=====================+====================================+
    | 00001 | MAXIMUM             | MAXIMUM VALUES                     |
    +-------+---------------------+------------------------------------+
    | 00002 | MINIMUM             | MINIMUM VALUES                     |
    +-------+---------------------+------------------------------------+
    | 00003 | MEAN                | MEAN VALUES                        |
    +-------+---------------------+------------------------------------+
    | 00004 | AM                  | VALUES TAKEN BETWEEN 0001 AND 1200 |
    +-------+---------------------+------------------------------------+
    | 00005 | PM                  | VALUES TAKEN BETWEEN 1201 AND 2400 |
    +-------+---------------------+------------------------------------+
    | 00006 | SUM                 | SUMMATION VALUES                   |
    +-------+---------------------+------------------------------------+
    | 00007 | MODE                | MODAL VALUES                       |
    +-------+---------------------+------------------------------------+
    | 00008 | MEDIAN              | MEDIAN VALUES                      |
    +-------+---------------------+------------------------------------+
    | 00009 | STD                 | STANDARD DEVIATION VALUES          |
    +-------+---------------------+------------------------------------+
    | 00010 | VARIANCE            | VARIANCE VALUES                    |
    +-------+---------------------+------------------------------------+
    | 00011 | INSTANTANEOUS       | RANDOM INSTANTANEOUS VALUES        |
    +-------+---------------------+------------------------------------+
    | 00012 | EQUIVALENT MEAN     | EQUIVALENT MEAN VALUES             |
    +-------+---------------------+------------------------------------+
    | 00013 | SKEWNESS            | SKEWNESS VALUES                    |
    +-------+---------------------+------------------------------------+
    | 00021 | TIDAL HIGH-HIGH     | TIDAL HIGH-HIGH VALUES             |
    +-------+---------------------+------------------------------------+
    | 00022 | TIDAL LOW-HIGH      | TIDAL LOW-HIGH VALUES              |
    +-------+---------------------+------------------------------------+
    | 00023 | TIDAL HIGH-LOW      | TIDAL HIGH-LOW VALUES              |
    +-------+---------------------+------------------------------------+
    | 00024 | TIDAL LOW-LOW       | TIDAL LOW-LOW VALUES               |
    +-------+---------------------+------------------------------------+
    | 01XXY | XX.Y PERCENTILE     | XX.Y PERCENTILE                    |
    +-------+---------------------+------------------------------------+
    | 02LLL | LLL DAY LOW MEAN    | LLL DAY LOW MEAN                   |
    +-------+---------------------+------------------------------------+
    | 03HHH | HHH DAY HIGH MEAN   | HHH DAY HIGH MEAN                  |
    +-------+---------------------+------------------------------------+
    | 3TTTT | OBSERVATION AT TTTT | INSTANTANEOUS OBSERVATION AT TTTT  |
    +-------+---------------------+------------------------------------+

    The detailed table is at https://help.waterdata.usgs.gov/stat_code

    Parameters
    ----------
    sites : str
        Want to only query one site? Use sites as your
        major filter, and put only one site number in the list.  Sites
        are comma separated. Sites may be prefixed with an optional
        agency code followed by a colon. If you don't know the site
        numbers you need, you can find relevant sites with the NWIS
        Mapper (http://wdr.water.usgs.gov/nwisgmap/index.html) or on the
        USGS Water Data for the Nation site.
        (http://waterdata.usgs.gov/nwis/)

        Can have from 1 to 100 comma separated site numbers::

            --sites=USGS:01646500
            --sites=01646500,06306300

    stateCd : str
        U.S. postal service (2-digit) state code.  Can have only 1 state code.
        List is available at
        http://www.usps.com/ncsc/lookups/usps_abbreviations.html::

            --stateCd=NY

    huc : str
        A list of hydrologic unit codes (HUC) or watersheds.  Only 1 major HUC
        can be specified per request.  A major HUC has two digits. Minor HUCs
        must be eight digits in length.  Can have 1 to 10 HUC codes.  List of
        HUCs is available at http://water.usgs.gov/GIS/huc_name.html::

            --huc=01,02070010

    bBox :
        A contiguous range of decimal latitude and longitude, starting with the
        west longitude, then the south latitude, then the east longitude, and
        then the north latitude with each value separated by a comma. The
        product of the range of latitude and longitude cannot exceed 25
        degrees. Whole or decimal degrees must be specified, up to six digits
        of precision. Minutes and seconds are not allowed. Remember: western
        longitude (which includes almost all of the United States) is specified
        in negative degrees. Caution: many sites outside the continental US do
        not have latitude and longitude referenced to NAD83 and therefore can
        not be found using these arguments. Certain sites are not associated
        with latitude and longitude due to homeland security concerns and
        cannot be found using this filter.::

            --bBox=-83,36.5,-81,38.5

    countyCd :
        A list of county numbers, in a 5 digit numeric format. The first two
        digits of a county's code are the FIPS State Code.  Can have from 1 to
        20 county codes.  The first 2 digits are the FIPS State Code
        (http://www.itl.nist.gov/fipspubs/fip5-2.htm) and the list of county
        codes are at
        http://help.waterdata.usgs.gov/code/county_query?fmt=html::

            --countyCd=51059,51061

    parameterCd :
        USGS time-series parameter code.  All parameter codes are numeric and
        5 characters in length.  Parameter codes are used to identify the
        constituent measured and the units of measure.  Popular codes include
        stage (00065), discharge in cubic feet per second (00060) and water
        temperature in degrees Celsius (00010). Can request from 1 to 100
        "parameterCD"s.  Default: returns all regular time-series for the
        requested sites.

        Complete list:
        http://help.waterdata.usgs.gov/codes-and-parameters/parameters::

            --parameterCd=00060       # discharge, cubic feet
                                      # per second
            --parameterCd=00060,00065 # discharge,
                                      # cubic feet per second
                                      # and gage height in
                                      # feet

    siteType :
        Restricts sites to those having one or more major and/or minor site
        types.  If you request a major site type (ex: &siteType=ST) you will
        get all sub-site types of the same major type as well (in this case,
        ST-CA, ST-DCH and ST-TS).  Can have from 1 to an unlimited number of
        siteType codes.  Default is to return all types.  List of valid site
        types: http://help.waterdata.usgs.gov/site_tp_cd::

            --siteType=ST       # Streams only
            --siteType=ST,LA-OU # Streams and Land Outcrops only

    modifiedSince :
        Returns all values for sites and period of record requested only if any
        values have changed over the last modifiedSince period.  modifiedSince
        is useful if you periodically need to poll a site but are only
        interested in getting data if some of it has changed.  It is typically
        be used with period, or startDT/endDT but does not have to be. In the
        latter case, if any values were changed during the specified
        modifiedSince period, only the most recent values would be retrieved
        for those sites. This is a typical usage, since users typically are
        polling a site and only want data if there are new or changed
        measurements.  ISO-8601 duration format is always used.  There is no
        default.  (http://en.wikipedia.org/wiki/ISO_8601#Durations)::

            --modifiedSince=PT2H # Retrieves all values for
                                 # sites and period of
                                 # record requested for
                                 # any of the requested
                                 # sites and parameters, but
                                 # only for sites where any
                                 # of the values changed
                                 # during the
                                 # last two hours.
            --modifiedSince=PT2H --period=P1D
                                 # Retrieve all values for
                                 # sites and period of record
                                 # requested for the last 24
                                 # hours from now only for
                                 # sites and parameters that
                                 # had any values that
                                 # changed or were added
                                 # during the last two hours.
            --modifiedSince=PT2H --startDt=2010-11-01 --endDt=2010-11-02
                   # Retrieve all values for sites and period
                   # of record requested for sites and
                   # parameters that had values change
                   # between midnight site local time on Nov
                   # 1st, 2010 and 23:59 on Nov 2nd, 2010
                   # site local time, only if values were
                   # changed or added within the last two
                   # hours.

    agencyCd :
        The list of sites returned are filtered to return only those with the
        provided agency code. The agency code describes the organization that
        maintains the site. Only one agency code is allowed and is optional.
        An authoritative list of agency codes can be found here.  Default is to
        return all sites regardless of agency code.  List:
        http://help.waterdata.usgs.gov/code/agency_cd_query?fmt=html::

            --stateCd=il --agencyCd=USCE # Only US Army Corps
                                         # of Engineers sites
                                         # in Illinois

    siteStatus :
        Selects sites based on whether or not they are active. If a site is
        active, it implies that it is being actively maintained. A site is
        considered active if: * it has collected time-series (automated) data
        within the last 183 days (6 months), or * it has collected discrete
        (manually collected) data within 397 days (13 months) If it does not
        meet these criteria, it is considered inactive. Some exceptions apply.
        If a site is flagged by a USGS water science center as discontinued, it
        will show as inactive. A USGS science center can also flag a new site
        as active even if it has not collected any data.  The default is all
        (show both active and inactive sites).  Chose between, 'all', 'active',
        or 'inactive'.  Default all - sites of any activity status are
        returned.::

            --siteStatus='active'

    altMin : float
        These arguments allows you to select instantaneous values sites where
        the associated sites' altitude are within a desired altitude, expressed
        in feet.  Altitude is based on the datum used at the site.  Providing
        a value to altMin (minimum altitude) means you want sites that have or
        exceed the altMin value.  You may specify decimal feet if precision is
        critical If both the altMin and altMax are specified, sites at or
        between the minimum and maximum altitude are returned.

    altMax : float
        Providing a value to altMax (maximum altitude) means you want sites
        that have or are less than the altMax value.::

            --altMin=1000 --altMax=5000 # Return sites where
                                        # the altitude is
                                        # 1000 feet or
                                        # greater and 5000
                                        # feet or less.
            --altMin=12.5 --altMax=13 # Return sites where the
                                      # altitude is 12.5 feet
                                      # or greater and 13 feet
                                      # or less.

    drainAreaMin : float
        These arguments allows you to select principally surface water sites
        where the associated sites' drainage areas (watersheds) are within
        a desired size, expressed in square miles or decimal fractions thereof.
        Providing a value to drainAreaMin (minimum drainage area) means you
        want sites that have or exceed the drainAreaMin value.  The values may
        be expressed in decimals. If both the drainAreaMin and drainAreaMax are
        specified, sites at or between the minimum and maximum drainage areas
        values specified are returned Caution: not all sites are associated
        with a drainage area.  Caution: drainage area generally only applies to
        surface water sites.  Use with other site types, such as groundwater
        sites, will likely retrieve no results.

    drainAreaMax:  float
        Providing a value to drainAreaMax (maximum drainage area) means you
        want sites that have or are less than the drainAreaMax value.::

            --drainAreaMin=1000 --drainAreaMax=5000
                                 # Return sites where the
                                 # drainage area is 1000
                                 # square miles or greater
                                 # and is 5000 square miles
                                 # or less.
            --drainAreaMin=10.5 --drainAreaMax=10.7
                                 # Return sites where the
                                 # drainage area is 10.5
                                 # square miles or greater
                                 # and is 10.7 square miles
                                 # or less.

    aquiferCd
        Used to filter sites to those that exist in specified national
        aquifers. Note: not all sites have been associated with national
        aquifers.  Enter one or more national aquifer codes, separated by
        commas.  A national aquifer code is exactly 10 characters.  You can
        have up to 1000 aquiferCd codes.  Complete list:
        http://water.usgs.gov/ogw/NatlAqCode-reflist.html::

            --aquiferCd=S500EDRTRN,N100HGHPLN
                                  # returns groundwater sites
                                  # for the Edwards-Trinity
                                  # aquifer system and the
                                  # High Plains national
                                  # aquifers.

    localAquiferCd
        Used to filter sites to those that exist in specified local aquifers.
        Note: not all sites have been associated with local aquifers.  Enter
        one or more local aquifer codes, separated by commas.  A local aquifer
        code begins with a 2 character state abbreviation (such as TX for
        Texas) followed by a colon followed by the 7 character aquifer code.
        Can have 0 to 1000 comma delimited codes.  Complete list:
        http://help.waterdata.usgs.gov/code/aqfr_cd_query?fmt=html To translate
        state codes associated with the local aquifer you may need this
        reference: http://www.itl.nist.gov/fipspubs/fip5-2.htm ::

            --localAquiferCd=AL:111RGLT,AL:111RSDM
                    # returns sites for the Regolith and
                    # Saprolite local aquifers in Alabama

    wellDepthMin : float
        These arguments allows you to select groundwater sites serving data
        recorded automatically where the associated sites' well depth are
        within a desired depth, expressed in feet from the land surface datum.
        Express well depth as a positive number.  Providing a value to
        wellDepthMin (minimum well depth) means you want sites that have or
        exceed the wellDepthMin value.  The values may be expressed in decimals
        Caution: well depth applies to groundwater sites only.::

             --wellDepthMin=100 --wellDepthMax=500
                     # Return daily value sites where the well
                     # depth is 100 feet or greater and 500
                     # feet or less.

    wellDepthMax : float
        Providing a value to wellDepthMax (maximum well depth)
        means you want sites that have or are less than the wellDepthMax
        value.::

             --wellDepthMin=10.5 --wellDepthMax=10.7
                     # Return daily value sites where the well
                     # depth is 10.5 feet or greater and 10.7
                     # feet or less.

        If both the wellDepthMin and wellDepthMax are specified, sites at or
        between the minimum and maximum well depth values specified are
        returned wellDepthMax should be greater than or equal to wellDepthMin.

    holeDepthMin : float
        These arguments allows you to select groundwater sites serving data
        recorded automatically where the associated sites' hole depth are
        within a desired depth, expressed in feet from the land surface datum.
        Express hole depth as a positive number.  Providing a value to
        holeDepthMin (minimum hole depth) means you want sites that have or
        exceed the holeDepthMin value.  The values may be expressed in decimals
        Caution: hole depth applies to groundwater sites only.

    holeDepthMax : float
        Providing a value to holeDepthMax (maximum hole depth) means you want
        sites that have or are less than the holeDepthMax value.::

            --holeDepthMin=100 --holeDepthMax=500
                    # Return daily values sites where the
                    # hole depth is 100 feet or greater and
                    # 500 feet or less.

            --holeDepthMin=10.5 --holeDepthMax=10.7
                    # Return daily value sites where the hole
                    # depth is 10.5 feet or greater and 10.7
                    # feet or less.

        If both the holeDepthMin and holeDepthMax are specified, sites at or
        between the minimum and maximum hole depth values specified are
        returned holeDepthMax should be greater than or equal to holeDepthMin.

    period
        Get a range of values from now by specifying the period argument period
        must be in ISO-8601 Duration format.
        (http://en.wikipedia.org/wiki/ISO_8601#Durations) Negative periods (ex:
        P-T2H) are not allowed Data are always returned up to the most recent
        value, which in the case of a predictive gage might be in the future.
        When specifying days from now, the first value will probably not be at
        midnight of the first day, but somewhat before exactly 24 hours from
        now.::

            --period=PT2H # Retrieve last two hours from now
                          # up to most recent
                          # instantaneous value)
            --period=P7D # Retrieve last seven days up from
                         # now to most recent instantaneous
                         # value)

    startDT
        Get a range of values from an explicit begin or end date/time.  Use the
        startDT and endDT arguments.  Site local time is output, even if
        multiple sites are requested and sites are in different time zones.
        Note that the measurement time zone at a site may not be the same as
        the time zone actually in effect at the site.

        Both startDt and endDt must be in ISO-8601 Date/Time format.
        (http://en.wikipedia.org/wiki/ISO_8601#Dates) You can express the date
        and time in a timezone other than site local time if you want as long
        as it follows the ISO standard. For example, you can express the time
        in Universal time: 2014-03-20T00:00Z.  If startDT is supplied and endDT
        is not, endDT ends with the most recent instantaneous value. startDT
        must be chronologically before endDT.

        If startDt shows the date and not the time of day (ex: 2010-09-01) the
        time of midnight site time is assumed (2010-09-01T00:00) If endDt shows
        the date and not the time of day (ex: 2010-09-02) the last minute
        before midnight site time is assumed (2010-09-02T23:59).  Remember,
        only data from October 1, 2007 are currently available in the 'iv'
        database.

    endDT
        If endDT is present, startDt must also be
        present.::

            --startDT=2010-11-22 --endDT=2010-11-22 # Full day, 00:00 to 23:59
            --startDT=2010-11-22T12:00 --endDT=2010-11-22T18:00
            --startDT=2010-11-22 --endDT=2010-11-22
            --startDT=2010-11-22T12:00 # Most recent instantaneous value

    database : str
        If using the 'measurements' or 'peak' database option you can download
        data from only one site at a time.  Default is 'dv'.

        +--------------+----------------------------------------+
        | database     | Description                            |
        +==============+========================================+
        | iv           | instantaneous, if continuously sampled |
        |              | then interval is sub-daily             |
        +--------------+----------------------------------------+
        | dv           | daily values (default)                 |
        +--------------+----------------------------------------+
        | stat         | daily/monthly/annual statistics        |
        |              | depending on statReportType option     |
        +--------------+----------------------------------------+
        | site         | site metadata                          |
        +--------------+----------------------------------------+
        | measurements | field measurements                     |
        +--------------+----------------------------------------+
        | peak         | peak                                   |
        +--------------+----------------------------------------+

    statReportType : str
        The type of statistics desired. Valid statistic report types
        include:

        +----------------+------------------------------------------+
        | statReportType | Description                              |
        +----------------+------------------------------------------+
        | daily          | daily statistics (default)               |
        |                | statistic across years                   |
        +----------------+------------------------------------------+
        | monthly        | monthly statistics (monthly time-series) |
        +----------------+------------------------------------------+
        | annual         | annual statistics, based on either       |
        |                | calendar year or water year, as defined  |
        |                | by statYearType. If statYearType is not  |
        |                | provided, calendar year statistics are   |
        |                | assumed. (annual time-series)            |
        +----------------+------------------------------------------+

        Default is 'daily'.

    statType : str
        Selects sites based on the statistics type(s) desired, such as minimum,
        maximum or mean

        For all statReportType types include::

            mean - arithmetic mean or average
            all - selects all available statistics

        For daily statistics you can also specify::

            min - minimum, or smallest value found for the
                  daily statistics
            max - maximum, or largest value found for the
                  daily statistics
            median - the numerical value separating the higher
                     half of a the data from the lower half,
                     same as specifying P50. If used median
                     will be represented by the column name
                     p50_va.
            P05, P10, P20, P25, P50, P75, P80, P90, P95
                with the number indicating percentile. Note:
                the service can calculate only these
                percentiles.

    missingData
        Used to indicate the rules to follow to generate statistics if there
        are gaps in the period of record during the requested statistics
        period. By default if there are any missing data for the report type,
        the statistic is left blank or null.

        This option does not apply to daily statistics, but optionally can be
        used with monthly and yearly statistics. If used with daily statistics,
        an error will occur.

        Missing data can happen for various reasons including there was
        a technical problem with the gage for part of the time period.

        Enabling this switch will attempt to provide a statistic if there is
        enough data to create one.

        Choice is 'off' or 'on'.

    statYearType
        Indicates which kind of year statistics should be created against. This
        only applies when requesting annual statistics, i.e.
        statReportType=annual. Valid year types codes include::

            calendar - calendar year, i.e. January 1 through
                       December 31
            water - water year, i.e. a year begins October 1 of
                    the previous year and ends September 30 of
                    the current year. This is the same as
                    a federal fiscal year.

    """
    from tsgettoolbox.services.usgs import nwis as placeholder
    if database not in ['iv',
                        'dv',
                        'stat',
                        'measurements',
                        'peak',
                        'site']:
        raise ValueError(r"""
*
*   The 'database' option must be either 'iv' for instantaneous values,
*   or 'dv' for daily values, or 'stat' for daily, monthly, or annual
*   statistics, or 'measurements' for field measurements, pr 'peak' for
*   peak stage and flow estimates, or 'site' for site metadata.
*   You gave {0}.
*
""".format(database))
    url = r'http://waterservices.usgs.gov/nwis/{0}/'.format(database)
    if database in ['measurements', 'peak']:
        words = sites.split(',')
        if len(words) != 1:
            raise ValueError(r"""
*
*   For the 'measurements' and 'peak' databases you can only collect
*   data from one site, you listed {0}.
*
""".format(len(words)))
        if (stateCd is not None or
            huc is not None or
            bBox is not None or
                countyCd is not None):
            raise ValueError(r"""
*
*   The 'measurements' or 'peak' database can currently only accept one
*   site using the 'site' keyword.
*
""")

        url = r'http://nwis.waterdata.usgs.gov/XX/nwis/{0}'.format(database)
    r = resource(url,
                 sites=sites,
                 stateCd=stateCd,
                 huc=huc,
                 bBox=bBox,
                 countyCd=countyCd,
                 parameterCd=parameterCd,
                 siteType=siteType,
                 modifiedSince=modifiedSince,
                 agencyCd=agencyCd,
                 siteStatus=siteStatus,
                 altMin=altMin,
                 altMax=altMax,
                 drainAreaMin=drainAreaMin,
                 drainAreaMax=drainAreaMax,
                 aquiferCd=aquiferCd,
                 localAquiferCd=localAquiferCd,
                 wellDepthMin=wellDepthMin,
                 wellDepthMax=wellDepthMax,
                 holeDepthMin=holeDepthMin,
                 holeDepthMax=holeDepthMax,
                 period=period,
                 startDT=startDT,
                 endDT=endDT,
                 statReportType=statReportType,
                 statType=statType,
                 missingData=missingData,
                 statYearType=statYearType)

    return tsutils.printiso(odo(r, pd.DataFrame))


@mando.command(formatter_class=HelpFormatter, doctype='numpy')
def daymet(lat,
           lon,
           measuredParams=None,
           year=None):
    r"""
    Download data from Daymet by the Oak Ridge National Laboratory.

    Detailed documentation is at http://daymet.ornl.gov/.  Since this is
    daily data, it covers midnight to midnight based on local time.

    Parameters
    ----------
    lat : float
        Latitude (required): Enter single geographic
        point by latitude, value between 52.0N and 14.5N.::

            Example: --lat=43.1

    lon : float
        Longitude (required): Enter single geographic
        point by longitude, value between -131.0W and -53.0W.::

            Example: --lon=-85.3

    measuredParams:  CommaSeparatedVariables (optional)
        Use the abbreviations from the following table:

        +----------------+-----------------------+---------+
        | measuredParams | Description           | Unit    |
        +================+=======================+=========+
        | tmax           | maximum temperature   | deg C   |
        +----------------+-----------------------+---------+
        | tmin           | minimum temperature   | deg C   |
        +----------------+-----------------------+---------+
        | srad           | shortwave radiation   | W/m2    |
        +----------------+-----------------------+---------+
        | vp             | vapor pressure        | Pa      |
        +----------------+-----------------------+---------+
        | swe            | snow-water equivalent | kg/m2   |
        +----------------+-----------------------+---------+
        | prcp           | precipitation         | mm      |
        +----------------+-----------------------+---------+
        | dayl           | daylength             | seconds |
        +----------------+-----------------------+---------+

         Example: --measuredParams=tmax,tmin

         All variables are returned by default.
    year :  CommaSeparatedYears (optional):
        Current Daymet product (version 2) is available from 1980 to the latest
        full calendar year.::

            Example: --years=2012,2013

         All years are returned by default.
    """
    from tsgettoolbox.services import daymet as placeholder
    r = resource(
        r'http://daymet.ornl.gov/data/send/saveData',
        measuredParams=measuredParams,
        lat=lat,
        lon=lon,
        year=year,
    )
    return tsutils.printiso(odo(r, pd.DataFrame))


@mando.command(formatter_class=HelpFormatter, doctype='numpy')
def ldas(lat=None,
         lon=None,
         xindex=None,
         yindex=None,
         variable=None,
         startDate=None,
         endDate=None):
    r"""
    Download data from NLDAS or GLDAS.

    The time zone is always UTC.

    Parameters
    ----------
    lat :  float
        Either 'lat' and 'lon', or 'xindex' and
        'yindex' is required.

        Latitude (required): Enter single geographic point by
        latitude.::

            Example: --lat=43.1

    lon : float
        Either 'lat' and 'lon', or 'xindex' and
        'yindex' is required.  Longitude (required): Enter single
        geographic point by longitude::

            Example: --lon=-85.3

    xindex : int
        Either 'lat' and 'lon', or 'xindex' and
        'yindex' is required.  xindex (required if using xindex/yindex):
        Enter the x index of the NLDAS or GLDAS grid.::

            Example: --xindex=301

    yindex : int
        Either 'lat' and 'lon', or 'xindex' and
        'yindex' is required.  yindex (required if using xindex/yindex):
        Enter the y index of the NLDAS or GLDAS grid.::

            Example: --yindex=80

    variable : str
        Use the variable codes from the following table:

        +--------------------------------------------+-----------+
        | LDAS "variable" string Description         | Units     |
        +============================================+===========+
        | NLDAS:NLDAS_FORA0125_H.002:APCPsfc         | kg/m^2    |
        | Precipitation hourly total                 |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_FORA0125_H.002:DLWRFsfc        | W/m^2     |
        | Surface DW longwave radiation flux         |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_FORA0125_H.002:DSWRFsfc        | W/m^2     |
        | Surface DW shortwave radiation flux        |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_FORA0125_H.002:PEVAPsfc        | kg/m^2    |
        | Potential evaporation                      |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_FORA0125_H.002:SPFH2m          | kg/kg     |
        | 2-m above ground specific humidity         |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_FORA0125_H.002:TMP2m           | K         |
        | 2-m above ground temperature               |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_FORA0125_H.002:UGRD10m         | m/s       |
        | 10-m above ground zonal wind               |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_FORA0125_H.002:VGRD10m         | m/s       |
        | 10-m above ground meridional wind          |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_NOAH0125_H.002:EVPsfc          | kg/m^2    |
        | Total evapotranspiration                   |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_NOAH0125_H.002:GFLUXsfc        | w/m^2     |
        | Ground heat flux                           |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_NOAH0125_H.002:LHTFLsfc        | w/m^2     |
        | Latent heat flux                           |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_NOAH0125_H.002:SHTFLsfc        | w/m^2     |
        | Sensible heat flux                         |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_NOAH0125_H.002:SSRUNsfc        | kg/m^2    |
        | Surface runoff (non-infiltrating)          |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_NOAH0125_H.002:BGRIUNdfc       | kg/m^2    |
        | Subsurface runoff (baseflow)               |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_NOAH0125_H.002:SOILM0-10cm     | kg/m^2    |
        | 0-10 cm soil moisture content              |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_NOAH0125_H.002:SOILM0-100cm    | kg/m^2    |
        | 0-100 cm soil moisture content             |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_NOAH0125_H.002:SOILM0-200cm    | kg/m^2    |
        | 0-200 cm soil moisture content             |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_NOAH0125_H.002:SOILM10-40cm    | kg/m^2    |
        | 10-40 cm soil moisture content             |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_NOAH0125_H.002:SOILM40-100cm   | kg/m^2    |
        | 40-100 cm soil moisture content            |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_NOAH0125_H.002:SOILM100-200cm  | kg/m^2    |
        | 100-200 cm soil moisture content           |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_NOAH0125_H.002:TSOIL0-10cm     | K         |
        | 0-10 cm soil temperature                   |           |
        +--------------------------------------------+-----------+
        | GLDAS:GLDAS_NOAH025_3H.001:Evap            | kg/m^2/s  |
        | Evapotranspiration                         |           |
        +--------------------------------------------+-----------+
        | GLDAS:GLDAS_NOAH025_3H.001:precip          | kg/m^s/hr |
        | Precipitation rate                         |           |
        +--------------------------------------------+-----------+
        | GLDAS:GLDAS_NOAH025_3H.001:Rainf           | kg/m^2/s  |
        | Rain rate                                  |           |
        +--------------------------------------------+-----------+
        | GLDAS:GLDAS_NOAH025_3H.001:Snowf           | kg/m^2/s  |
        | Snow rate                                  |           |
        +--------------------------------------------+-----------+
        | GLDAS:GLDAS_NOAH025_3H.001:Qs              | kg/m^2/s  |
        | Surface Runoff                             |           |
        +--------------------------------------------+-----------+
        | GLDAS:GLDAS_NOAH025_3H.001:Qsb             | kg/m^2/s  |
        | Subsurface Runoff                          |           |
        +--------------------------------------------+-----------+
        | GLDAS:GLDAS_NOAH025_3H.001:SOILM0-100cm    | kg/m^2    |
        | 0-100 cm top 1 meter soil moisture content |           |
        +--------------------------------------------+-----------+
        | GLDAS:GLDAS_NOAH025_3H.001:SOILM0-10cm     | kg/m^2    |
        | 0-10 cm layer 1 soil moisture content      |           |
        +--------------------------------------------+-----------+
        | GLDAS:GLDAS_NOAH025_3H.001:SOILM10-40cm    | kg/m^2    |
        | 10-40 cm layer 2 soil moisture content     |           |
        +--------------------------------------------+-----------+
        | GLDAS:GLDAS_NOAH025_3H.001:SOILM40-100cm   | kg/m^2    |
        | 40-100 cm layer 3 soil moisture content    |           |
        +--------------------------------------------+-----------+
        | GLDAS:GLDAS_NOAH025_3H.001:Tair            | K         |
        | Near surface air temperature               |           |
        +--------------------------------------------+-----------+
        | GLDAS:GLDAS_NOAH025_3H.001:TSOIL0-10cm     | K         |
        | Average layer 1 soil temperature           |           |
        +--------------------------------------------+-----------+
        | GLDAS:GLDAS_NOAH025_3H.001:Wind            | m/s       |
        | Near surface wind magnitude                |           |
        +--------------------------------------------+-----------+

    startDate : str
        The start date of the time series.::

            Example: --startDate=2001-01-01T05

        If startDate and endDate are None, returns the entire series.

    endDate : str
        The end date of the time series.::

            Example: --startDate=2001-01-05T05

        If startDate and endDate are None, returns the entire series.
    """
    from tsgettoolbox.services import ldas as placeholder
    project = variable.split(':')[0]
    if lat is not None:
        location = 'GEOM:POINT({0}, {1})'.format(lon, lat)
    else:
        if project == 'NLDAS':
            location = '{0}:X{1:03d}-Y{2:03d}'.format(project, xindex, yindex)
        else:
            location = '{0}:X{1:04d}-Y{2:03d}'.format(project, xindex, yindex)

    r = resource(
        r'https://hydro1.gesdisc.eosdis.nasa.gov/daac-bin/access/timeseries.cgi',
        variable=variable,
        location=location,
        startDate=startDate,
        endDate=endDate,
    )
    return tsutils.printiso(odo(r, pd.DataFrame))


@mando.command(formatter_class=HelpFormatter, doctype='numpy')
def darksky(latitude,
            longitude,
            time=None,
            database='hourly',
            extend=None,
            units='us',
            lang='en'):
    r"""
    Powered by Dark Sky https://darksky.net/poweredby/

    Powered by Dark Sky https://darksky.net/poweredby/

    Documentation: https://darksky.net/dev/docs

    Registration: https://darksky.net/dev/register

    The time zone of the returned data is dependent on the format of the
    "time" option.  If there is an ISO8601 representation of the time
    zone in the "time" option then that is the time zone of the returned
    data.  If "time" is None or does not explicitly define a time zone,
    the returned data is in the local time zone of the latitude and
    longitude.

    There isn't an absolutely consistent set of data returned for all
    areas, or all databases.  The returned values will be some subset of
    the following list:

    summary::

     A human-readable text summary of this data point.

    icon::

     A machine-readable text summary of this data |point, suitable for
     selecting an icon for display. If defined, this property will have
     one of the following values: 'clear-day', 'clear-night', 'rain',
     'snow', 'sleet', 'wind', 'fog', 'cloudy', 'partly-cloudy-day', or
     'partly-cloudy-night'.  (Developers should ensure that a sensible
     default is defined, as additional values, such as hail,
     thunderstorm, or tornado, may be defined in the future.)

    precipIntensity::

     A numerical value representing the average expected intensity (in
     inches of liquid water per hour) of precipitation occurring at the
     given time conditional on probability (that is, assuming any
     precipitation occurs at all). A very rough guide is that a value
     of 0 in./hr. corresponds to no precipitation, 0.002 in./hr.
     corresponds to very light precipitation, 0.017 in./hr. corresponds
     to light precipitation, 0.1 in./hr. corresponds to moderate
     precipitation, and 0.4 in./hr. corresponds to heavy precipitation.

    precipProbability::

     A numerical value between 0 and 1 (inclusive) representing the
     probability of precipitation occuring at the given time.

    precipType::

     A string representing the type of precipitation occurring at the
     given time. If defined, this property will have one of the
     following values: rain, snow, sleet (which applies to each of
     freezing rain, ice pellets, and 'wintery mix'), or hail. (If
     precipIntensity is zero, then this property will not be defined.)

    dewPoint::

     A numerical value representing the dew point at the given time in
     degrees Fahrenheit.

    windSpeed::

     A numerical value representing the wind speed in miles per hour.

    windBearing::

     A numerical value representing the direction that the wind is
     coming from in degrees, with true north at 0 degree and
     progressing clockwise. (If windSpeed is zero, then this value will
     not be defined.)

    cloudCover::

     A numerical value between 0 and 1 (inclusive) representing the
     percentage of sky occluded by clouds. A value of 0 corresponds to
     clear sky, 0.4 to scattered clouds, 0.75 to broken cloud cover,
     and 1 to completely overcast skies.

    humidity::

     A numerical value between 0 and 1 (inclusive) representing the
     relative humidity.

    pressure::

     A numerical value representing the sea-level air pressure in
     millibars.

    visibility::

     A numerical value representing the average visibility in miles,
     capped at 10 miles.

    ozone::

     A numerical value representing the columnar density of total
     atmospheric ozone at the given time in Dobson units.

    **Only defined for 'currently' data**

    nearestStormDistance::

     A numerical value representing the distance to the nearest storm
     in miles. (This value is very approximate and should not be used
     in scenarios requiring accurate results. In particular, a storm
     distance of zero doesn't necessarily refer to a storm at the
     requested location, but rather a storm in the vicinity of that
     location.)

    nearestStormBearing::

     A numerical value representing the direction of the nearest storm
     in degrees, with true north at 0 degree and progressing clockwise.
     (If nearestStormDistance is zero, then this value will not be
     defined. The caveats that apply to nearestStormDistance also apply
     to this value.)

    **Only defined for 'daily' data**

    sunriseTime/sunsetTime::

     The last sunrise before and first sunset after the solar noon
     closest to local noon on the given day.  (Note: near the poles,
     these may occur on a different day entirely!)

    moonPhase::

     A number representing the fractional part of the lunation number
     of the given day. This can be thought of as the 'percentage
     complete' of the current lunar month: a value of 0 represents
     a new moon, a value of 0.25 represents a first quarter moon,
     a value of 0.5 represents a full moon, and a value of 0.75
     represents a last quarter moon. (The ranges in between these
     represent waxing crescent, waxing gibbous, waning gibbous, and
     waning crescent moons, respectively.)

    precipIntensityMax, and precipIntensityMaxTime::

     Numerical values representing the maximumum expected intensity of
     precipitation on the given day in inches of liquid water per hour.

    temperatureMin, temperatureMinTime, temperatureMax,
    and temperatureMaxTime::

     Numerical values representing the minimum and maximumum
     temperatures (and the UNIX times at which they occur) on the given
     day in degrees Fahrenheit.

    apparentTemperatureMin, apparentTemperatureMinTime,
    apparentTemperatureMax, and
    apparentTemperatureMaxTime::

     Numerical values representing the minimum and maximumum apparent
     temperatures and the times at which they occur on the given day in
     degrees Fahrenheit.

    **Only defined for 'hourly' and 'daily' data**

    precipAccumulation::

     The amount of snowfall accumulation expected to occur on the given
     day, in inches. (If no accumulation is expected, this property
     will not be defined.)

    **Defined for every dataset except 'daily'**

    apparentTemperature::

     A numerical value representing the apparent (or 'feels like')
     temperature at the given time in degrees Fahrenheit.

    temperature::

     A numerical value representing the temperature at the given time
     in degrees Fahrenheit.

    Parameters
    ----------
    latitude : float
        Latitude (required): Enter single geographic point by
        latitude.

    longitude : float
        Longitude (required): Enter single geographic point by
        longitude.

    time
        TIME should either be a UNIX time (that is,
        seconds since midnight GMT on 1 Jan 1970) or a string formatted
        as follows: [YYYY]-[MM]-[DD]T[HH]:[MM]:[SS] (with an optional
        time zone formatted as Z for GMT time or {+,-}[HH][MM] for an
        offset in hours or minutes). For the latter format, if no
        timezone is present, local time (at the provided latitude and
        longitude) is assumed.  (This string format is a subset of ISO
        8601 time. An as example, 2013-05-06T12:00:00-0400.)

        The default is None, which uses the current time.

    database
        The database to draw the data from.  This is
        slightly different than the typical Forecast.io request, which
        would normally send back all data from all databases.  Typically
        though the 'tsgettoolbox' and siblings expect a single time
        increment in a dataset.  This isn't a hard rule, just
        a tradition.  So pick a database from 'currently', 'minutely',
        'hourly', 'daily', 'alerts', or 'flags'.  The 'currently'
        database is the default and is the current conditions.
        'minutely' give minute by minute forecast from the current time
        for the next hour, 'hourly' gives hourly forecast for the next
        two days (unless --extend='hourly' option is given), and 'daily'
        gives a forecast day by day for the next week.

    extend
        If set to 'hourly' and --database='hourly'
        then will get an hourly forecast for the next week.

    units : str
        Specify the units for the
        data.

        +-----------------+--------------------------------------------+
        | Option          | Description                                |
        +=================+============================================+
        | us (default)    | Imperial units                             |
        +-----------------+--------------------------------------------+
        | si              | SI units                                   |
        +-----------------+--------------------------------------------+
        | ca              | Identical to SI except windSpeed is in     |
        |                 | km/hr                                      |
        +-----------------+--------------------------------------------+
        | uk (deprecated) |                                            |
        +-----------------+--------------------------------------------+
        | uk2             | Identical to SI except windSpeed is in     |
        |                 | miles/hr and nearestStormDistance and      |
        |                 | visibility are in miles                    |
        +-----------------+--------------------------------------------+
        | auto            | Selects the relevant units automatically   |
        |                 | according to location                      |
        +-----------------+--------------------------------------------+

    lang : str
        Return text summaries in the desired language.
        (Please be advised that units in the summary will be set
        according to the units option, above, so be sure to set both
        options as needed.)

        +-------------+-------------------+
        | lang= code  | Language          |
        +=============+===================+
        | ar          | Arabic            |
        +-------------+-------------------+
        | bs          | Bosnian           |
        +-------------+-------------------+
        | de          | German            |
        +-------------+-------------------+
        | en          | English (default) |
        +-------------+-------------------+
        | es          | Spanish           |
        +-------------+-------------------+
        | fr          | French            |
        +-------------+-------------------+
        | it          | Italian           |
        +-------------+-------------------+
        | nl          | Dutch             |
        +-------------+-------------------+
        | pl          | Polish            |
        +-------------+-------------------+
        | pt          | Portuguese        |
        +-------------+-------------------+
        | ru          | Russian           |
        +-------------+-------------------+
        | sk          | Slovak            |
        +-------------+-------------------+
        | sv          | Swedish           |
        +-------------+-------------------+
        | tet         | Tetum             |
        +-------------+-------------------+
        | tr          | Turkish           |
        +-------------+-------------------+
        | uk          | Ukrainian         |
        +-------------+-------------------+
        | x-pig-latin | Igpay Atinlay     |
        +-------------+-------------------+
        | zh          | Chinese           |
        +-------------+-------------------+

    """

    from tsgettoolbox.services import darksky as placeholder
    r = resource(
        r'https://api.darksky.net/forecast',
        latitude=latitude,
        longitude=longitude,
        database=database,
        time=time,
        extend=extend,
        units=units,
        lang=lang,
    )
    return tsutils.printiso(odo(r, pd.DataFrame))


@mando.command(formatter_class=HelpFormatter, doctype='numpy')
def forecast_io(latitude,
                longitude,
                time=None,
                database='hourly',
                extend=None,
                units='us',
                lang='en'):
    r""" DEPRECATED: please use 'darksky'.

    The forecast_io service changed names to 'darksky'.  See documentation
    under the darksky service.

    Parameters
    ----------
    latitude
        See documentation under the darksky
        service.

    longitude
        See documentation under the darksky
        service.

    time
        See documentation under the darksky
        service.

    database
        See documentation under the darksky
        service.

    extend
        See documentation under the darksky
        service.

    units
        See documentation under the darksky
        service.

    lang
        See documentation under the darksky
        service.

    """
    return darksky(latitude,
                   longitude,
                   time=time,
                   database=database,
                   extend=extend,
                   units=units,
                   lang=lang)


@mando.command(formatter_class=HelpFormatter, doctype='numpy')
def unavco(station,
           database='met',
           starttime=None,
           endtime=None):
    r"""
    Download data from the Unavco web services.

    Detailed information at:
    http://www.unavco.com/data/web-services/web-services.html

    The "database" option defines different return data.

    met::

       Returns hourly meteorological data for the specified station and
       timeframe.  Pressure, temperature, humidity, wind speed and
       direction are provided as averages of all the samples taken per
       hour. Rain and hail are totals for the hour. The sample count is
       the number of samples taken per hour.

       Stations are configured to sample either at 1 minute or 5 minute
       intervals and the user can determine which by looking at the
       sample counts over several hours to see if they approach 12 or
       60.

       Returns: sample timestamp, pressure (mbar), temperature (degree
       C), relative humidity(per cent), wind direction(degrees), wind
       speed(m/s), rain(0.1mm), hail(hits), sample count

    pore_temperature::

       Pore pressure and temperature readings are collected by pore
       pressure sensors co-located with borehole strainmeters. Tilt data
       is collected by shallow borehole tiltmeters co-located with
       borehole strainmeters and seismic stations.

       Get pore temperature for the specified stations and time range.

       Returns: sample time, temperature(degree C)

    pore_pressure::

       Pore pressure and temperature readings are collected by pore
       pressure sensors co-located with borehole strainmeters. Tilt data
       is collected by shallow borehole tiltmeters co-located with
       borehole strainmeters and seismic stations.

       Get pore pressure for the specified stations and time range.

       Returns: sample time, pressure (hPa)

    tilt::

       Get tilt data for specified stations and time range.

       Returns: DateTime, X-axis tilt (microRadians), Y-axis tilt
       (microRadians), Temperature (degree C), Voltage(v)

    strain::

       Geodetic strain data is collected by four-component deep borehole
       tensor strainmeters that record transient deformation signals
       yielding information about the physical properties of the
       surrounding rock.

       Borehole strainmeters measure very small changes in the dimension
       of a borehole at depths ranging from 100m to 250m. The Plate
       Boundary Observatory uses a instrument developed and constructed
       by GTSM Technologies which measure the change in borehole
       diameter along three azimuths separated by 120 degrees
       perpendicular to the borehole.

       Get borehole strain data for the borehole strainmeter station
       identified.  This data is low rate, 5 minute sample, level
       2 uncorrected and corrected strain data. Corrected values are the
       uncorrected strain minus the effects of the tidal signal and
       barometric pressure.

       Returns: DateTime, Gauge 0 uncorrected microstrain, Gauge
       1 corrected microstrain, Gauge 1 uncorrected microstrain, Gauge
       1 corrected microstrain, Gauge 2 microstrain, Gauge 2 corrected
       microstrain, Gauge 3 microstrain, Gauge 3 corrected microstrain,
       Eee+Enn uncorrected microstrain, Eee+Enn corrected microstrain,
       Eee-Enn uncorrected microstrain, Eee-Enn corrected microstrain,
       2Ene uncorrected microstrain, 2Ene corrected microstrain.

    Parameters
    ----------
    station
        Unavco station identifier
    database : str
        Database to pull from.  One of 'met', 'pore_temperature',
        'pore_pressure', 'tilt', 'strain'.  The default is 'met'.
    starttime
        Start date in ISO8601 format.
    endtime
        End date in ISO8601 format.
    """
    from tsgettoolbox.services import unavco as placeholder
    map_db_to_url = {
        'met': r'http://web-services.unavco.org:80/met/data',
        'pore_temperaure': r'http://web-services.unavco.org:80'
                           '/pore/data/temperature',
        'pore_pressure': r'http://web-services.unavco.org:80'
                         '/pore/data/pressure',
        'tilt': r'http://web-services.unavco.org:80/tilt/data',
        'strain': r'http://web-services.unavco.org:80/strain/data/L2',
    }
    r = resource(
        map_db_to_url[database],
        station=station,
        starttime=starttime,
        endtime=endtime,
    )
    return tsutils.printiso(odo(r, pd.DataFrame))


@mando.command(formatter_class=HelpFormatter, doctype='numpy')
@tsutils.doc(tsutils.docstrings)
def ncdc_ghcnd_ftp(station,
                   start_date=None,
                   end_date=None):
    r"""
    Download from the Global Historical Climatology Network - Daily.

    If you use this data, please read
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
    | TMAX | Temperature MAX (1/10 degree C)                          |
    +------+----------------------------------------------------------+
    | TMIN | Temperature MIN (1/10 degree C)                          |
    +------+----------------------------------------------------------+
    | PRCP | PReCiPitation (tenths of mm)                             |
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
    | AWND | Average daily wind speed (tenths of meters per second)   |
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
    | EVAP | Evaporation of water from evaporation pan (tenths of mm) |
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
    | MDEV | Multiday evaporation total (tenths of mm; use with DAEV) |
    +------+----------------------------------------------------------+
    | MDPR | Multiday precipitation total (tenths of mm; use with     |
    |      | DAPR and DWPR, if available)                             |
    +------+----------------------------------------------------------+
    | MDSF | Multiday snowfall total                                  |
    +------+----------------------------------------------------------+
    | MDTN | Multiday minimum temperature (tenths of degrees C; use   |
    |      | with DATN)                                               |
    +------+----------------------------------------------------------+
    | MDTX | Multiday maximum temperature (tenths of degress C; use   |
    |      | with DATX)                                               |
    +------+----------------------------------------------------------+
    | MDWM | Multiday wind movement (km)                              |
    +------+----------------------------------------------------------+
    | MNPN | Daily minimum temperature of water in an evaporation pan |
    |      | (tenths of degrees C)                                    |
    +------+----------------------------------------------------------+
    | MXPN | Daily maximum temperature of water in an evaporation pan |
    |      | (tenths of degrees C)                                    |
    +------+----------------------------------------------------------+
    | PGTM | Peak gust time (hours and minutes, i.e., HHMM)           |
    +------+----------------------------------------------------------+
    | PSUN | Daily percent of possible sunshine (percent)             |
    +------+----------------------------------------------------------+
    | TAVG | Average temperature (tenths of degrees C) [Note that     |
    |      | TAVG from source 'S' corresponds to an average for the   |
    |      | period ending at 2400 UTC rather than local midnight]    |
    +------+----------------------------------------------------------+
    | THIC | Thickness of ice on water (tenths of mm)                 |
    +------+----------------------------------------------------------+
    | TOBS | Temperature at the time of observation (tenths of        |
    |      | degrees C)                                               |
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
    | WESD | Water equivalent of snow on the ground (tenths of mm)    |
    +------+----------------------------------------------------------+
    | WESF | Water equivalent of snowfall (tenths of mm)              |
    +------+----------------------------------------------------------+
    | WSF1 | Fastest 1-minute wind speed (tenths of meters per        |
    |      | second)                                                  |
    +------+----------------------------------------------------------+
    | WSF2 | Fastest 2-minute wind speed (tenths of meters per        |
    |      | second)                                                  |
    +------+----------------------------------------------------------+
    | WSF5 | Fastest 5-second wind speed (tenths of meters per        |
    |      | second)                                                  |
    +------+----------------------------------------------------------+
    | WSFG | Peak gust wind speed (tenths of meters per second)       |
    +------+----------------------------------------------------------+
    | WSFI | Highest instantaneous wind speed (tenths of meters per   |
    |      | second)                                                  |
    +------+----------------------------------------------------------+
    | WSFM | Fastest mile wind speed (tenths of meters per second)    |
    +------+----------------------------------------------------------+
    | SN*# | Minimum soil temperature (tenths of degrees C) where *   |
    |      | corresponds to a code for ground cover and # corresponds |
    |      | to a code for soil depth.                                |
    +------+----------------------------------------------------------+
    |      | Ground cover codes include the following:                |
    +------+----------------------------------------------------------+
    |      | 0 = unknown                                              |
    +------+----------------------------------------------------------+
    |      | 1 = grass                                                |
    +------+----------------------------------------------------------+
    |      | 2 = fallow                                               |
    +------+----------------------------------------------------------+
    |      | 3 = bare ground                                          |
    +------+----------------------------------------------------------+
    |      | 4 = brome grass                                          |
    +------+----------------------------------------------------------+
    |      | 5 = sod                                                  |
    +------+----------------------------------------------------------+
    |      | 6 = straw mulch                                          |
    +------+----------------------------------------------------------+
    |      | 7 = grass muck                                           |
    +------+----------------------------------------------------------+
    |      | 8 = bare muck                                            |
    +------+----------------------------------------------------------+
    |      | Depth codes include the following:                       |
    +------+----------------------------------------------------------+
    |      | 1 = 5 cm                                                 |
    +------+----------------------------------------------------------+
    |      | 2 = 10 cm                                                |
    +------+----------------------------------------------------------+
    |      | 3 = 20 cm                                                |
    +------+----------------------------------------------------------+
    |      | 4 = 50 cm                                                |
    +------+----------------------------------------------------------+
    |      | 5 = 100 cm                                               |
    +------+----------------------------------------------------------+
    |      | 6 = 150 cm                                               |
    +------+----------------------------------------------------------+
    |      | 7 = 180 cm                                               |
    +------+----------------------------------------------------------+
    | SX*# | Maximum soil temperature (tenths of degrees C) where *   |
    |      | corresponds to a code for ground cover and # corresponds |
    |      | to a code for soil depth. See SN*# for ground cover and  |
    |      | depth codes.                                             |
    +------+----------------------------------------------------------+
    | WT** | Weather Type where ** has one of the following values:   |
    +------+----------------------------------------------------------+
    |      | 01 = Fog, ice fog, or freezing fog (may include heavy    |
    |      | fog)                                                     |
    +------+----------------------------------------------------------+
    |      | 02 = Heavy fog or heaving freezing fog (not always       |
    |      | distinguished from fog)                                  |
    +------+----------------------------------------------------------+
    |      | 03 = Thunder                                             |
    +------+----------------------------------------------------------+
    |      | 04 = Ice pellets, sleet, snow pellets, or small hail     |
    +------+----------------------------------------------------------+
    |      | 05 = Hail (may include small hail)                       |
    +------+----------------------------------------------------------+
    |      | 06 = Glaze or rime                                       |
    +------+----------------------------------------------------------+
    |      | 07 = Dust, volcanic ash, blowing dust, blowing sand, or  |
    |      | blowing obstruction                                      |
    +------+----------------------------------------------------------+
    |      | 08 = Smoke or haze                                       |
    +------+----------------------------------------------------------+
    |      | 09 = Blowing or drifting snow                            |
    +------+----------------------------------------------------------+
    |      | 10 = Tornado, waterspout, or funnel cloud                |
    +------+----------------------------------------------------------+
    |      | 11 = High or damaging winds                              |
    +------+----------------------------------------------------------+
    |      | 12 = Blowing spray                                       |
    +------+----------------------------------------------------------+
    |      | 13 = Mist                                                |
    +------+----------------------------------------------------------+
    |      | 14 = Drizzle                                             |
    +------+----------------------------------------------------------+
    |      | 15 = Freezing drizzle                                    |
    +------+----------------------------------------------------------+
    |      | 16 = Rain (may include freezing rain, drizzle, and       |
    |      | freezing drizzle)                                        |
    +------+----------------------------------------------------------+
    |      | 17 = Freezing rain                                       |
    +------+----------------------------------------------------------+
    |      | 18 = Snow, snow pellets, snow grains, or ice crystals    |
    +------+----------------------------------------------------------+
    |      | 19 = Unknown source of precipitation                     |
    +------+----------------------------------------------------------+
    |      | 21 = Ground fog                                          |
    +------+----------------------------------------------------------+
    |      | 22 = Ice fog or freezing fog                             |
    +------+----------------------------------------------------------+
    | WV** | Weather in the Vicinity where ** has one of the          |
    |      | following values:                                        |
    +------+----------------------------------------------------------+
    |      | 01 = Fog, ice fog, or freezing fog (may include heavy    |
    |      | fog)                                                     |
    +------+----------------------------------------------------------+
    |      | 03 = Thunder                                             |
    +------+----------------------------------------------------------+
    |      | 07 = Ash, dust, sand, or other blowing obstruction       |
    +------+----------------------------------------------------------+
    |      | 18 = Snow or ice crystals                                |
    +------+----------------------------------------------------------+
    |      | 20 = Rain or snow shower                                 |
    +------+----------------------------------------------------------+

    Parameters
    ----------
    station
        The station id. from the first column of
        ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt
    {start_date}
    {end_date}
    """
    from tsgettoolbox.services.ncdc import ghcnd as placeholder
    r = resource(
        r'ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/all',
        station=station,
        start_date=start_date,
        end_date=end_date,
    )
    return tsutils.printiso(odo(r, pd.DataFrame))


# 1763-01-01, 2016-11-05, Daily Summaries             , 1    , GHCND
@mando.command(formatter_class=HelpFormatter, doctype='numpy')
def ncdc_ghcnd(stationid,
               datatypeid='',
               startdate='',
               enddate=''):
    r"""
    Download from the Global Historical Climatology Network - Daily.
    Requires registration and free API key.

    If you use this data, please read
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
    countries data summaries and products which are available here are
    intended for free and unrestricted use in research, education, and
    other non-commercial activities. For non-U.S. locations data, the
    data or any derived product shall not be provided to other users or
    be used for the re-export of commercial services.

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
        The following table lists the datatypes available for the 'ghcnd'
        dataset.  If the datatypeid is not given defaults to getting all data
        available at that station for the time period requested.

        The five core values are:

        +------+-------------------------------------------------------+
        | Code | Description                                           |
        +======+=======================================================+
        | TMAX | Temperature MAX (1/10 degree C)                       |
        +------+-------------------------------------------------------+
        | TMIN | Temperature MIN (1/10 degree C)                       |
        +------+-------------------------------------------------------+
        | PRCP | PReCiPitation (tenths of mm)                          |
        +------+-------------------------------------------------------+
        | SNOW | SNOWfall (mm)                                         |
        +------+-------------------------------------------------------+
        | SNWD | SNoW Depth (mm)                                       |
        +------+-------------------------------------------------------+

        Other possible data collected:

        +------+-------------------------------------------------------+
        | Code | Description                                           |
        +======+=======================================================+
        | ACMC | Average cloudiness midnight to midnight from          |
        |      | 30-second ceilometer data (percent)                   |
        +------+-------------------------------------------------------+
        | ACMH | Average cloudiness midnight to midnight from manual   |
        |      | observations (percent)                                |
        +------+-------------------------------------------------------+
        | ACSC | Average cloudiness sunrise to sunset from 30-second   |
        |      | ceilometer data (percent)                             |
        +------+-------------------------------------------------------+
        | ACSH | Average cloudiness sunrise to sunset from manual      |
        |      | observations (percent)                                |
        +------+-------------------------------------------------------+
        | AWDR | Average daily wind direction (degrees)                |
        +------+-------------------------------------------------------+
        | AWND | Average daily wind speed (tenths of meters per        |
        |      | second)                                               |
        +------+-------------------------------------------------------+
        | DAEV | Number of days included in the multiday evaporation   |
        |      | total (MDEV)                                          |
        +------+-------------------------------------------------------+
        | DAPR | Number of days included in the multiday precipitation |
        |      | total (MDPR)                                          |
        +------+-------------------------------------------------------+
        | DASF | Number of days included in the multiday snowfall      |
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
        | EVAP | Evaporation of water from evaporation pan (tenths of  |
        |      | mm)                                                   |
        +------+-------------------------------------------------------+
        | FMTM | Time of fastest mile or fastest 1-minute wind (hours  |
        |      | and minutes, i.e., HHMM)                              |
        +------+-------------------------------------------------------+
        | FRGB | Base of frozen ground layer (cm)                      |
        +------+-------------------------------------------------------+
        | FRGT | Top of frozen ground layer (cm)                       |
        +------+-------------------------------------------------------+
        | FRTH | Thickness of frozen ground layer (cm)                 |
        +------+-------------------------------------------------------+
        | GAHT | Difference between river and gauge height (cm)        |
        +------+-------------------------------------------------------+
        | MDEV | Multiday evaporation total (tenths of mm; use with    |
        |      | DAEV)                                                 |
        +------+-------------------------------------------------------+
        | MDPR | Multiday precipitation total (tenths of mm; use with  |
        |      | DAPR and DWPR, if available)                          |
        +------+-------------------------------------------------------+
        | MDSF | Multiday snowfall total                               |
        +------+-------------------------------------------------------+
        | MDTN | Multiday minimum temperature (tenths of degrees C;    |
        |      | use with DATN)                                        |
        +------+-------------------------------------------------------+
        | MDTX | Multiday maximum temperature (tenths of degress C;    |
        |      | use with DATX)                                        |
        +------+-------------------------------------------------------+
        | MDWM | Multiday wind movement (km)                           |
        +------+-------------------------------------------------------+
        | MNPN | Daily minimum temperature of water in an evaporation  |
        |      | pan (tenths of degrees C)                             |
        +------+-------------------------------------------------------+
        | MXPN | Daily maximum temperature of water in an evaporation  |
        |      | pan (tenths of degrees C)                             |
        +------+-------------------------------------------------------+
        | PGTM | Peak gust time (hours and minutes, i.e., HHMM)        |
        +------+-------------------------------------------------------+
        | PSUN | Daily percent of possible sunshine (percent)          |
        +------+-------------------------------------------------------+
        | TAVG | Average temperature (tenths of degrees C) [Note that  |
        |      | TAVG from source 'S' corresponds to an average for    |
        |      | the period ending at 2400 UTC rather than local       |
        |      | midnight]                                             |
        +------+-------------------------------------------------------+
        | THIC | Thickness of ice on water (tenths of mm)              |
        +------+-------------------------------------------------------+
        | TOBS | Temperature at the time of observation (tenths of     |
        |      | degrees C)                                            |
        +------+-------------------------------------------------------+
        | TSUN | Daily total sunshine (minutes)                        |
        +------+-------------------------------------------------------+
        | WDF1 | Direction of fastest 1-minute wind (degrees)          |
        +------+-------------------------------------------------------+
        | WDF2 | Direction of fastest 2-minute wind (degrees)          |
        +------+-------------------------------------------------------+
        | WDF5 | Direction of fastest 5-second wind (degrees)          |
        +------+-------------------------------------------------------+
        | WDFG | Direction of peak wind gust (degrees)                 |
        +------+-------------------------------------------------------+
        | WDFI | Direction of highest instantaneous wind (degrees)     |
        +------+-------------------------------------------------------+
        | WDFM | Fastest mile wind direction (degrees)                 |
        +------+-------------------------------------------------------+
        | WDMV | 24-hour wind movement (km)                            |
        +------+-------------------------------------------------------+
        | WESD | Water equivalent of snow on the ground (tenths of mm) |
        +------+-------------------------------------------------------+
        | WESF | Water equivalent of snowfall (tenths of mm)           |
        +------+-------------------------------------------------------+
        | WSF1 | Fastest 1-minute wind speed (tenths of meters per     |
        |      | second)                                               |
        +------+-------------------------------------------------------+
        | WSF2 | Fastest 2-minute wind speed (tenths of meters per     |
        |      | second)                                               |
        +------+-------------------------------------------------------+
        | WSF5 | Fastest 5-second wind speed (tenths of meters per     |
        |      | second)                                               |
        +------+-------------------------------------------------------+
        | WSFG | Peak gust wind speed (tenths of meters per second)    |
        +------+-------------------------------------------------------+
        | WSFI | Highest instantaneous wind speed (tenths of meters    |
        |      | per second)                                           |
        +------+-------------------------------------------------------+
        | WSFM | Fastest mile wind speed (tenths of meters per second) |
        +------+-------------------------------------------------------+
        | SN*# | Minimum soil temperature (tenths of degrees C) where  |
        |      | * corresponds to a code for ground cover and #        |
        |      | corresponds to a code for soil depth.                 |
        +------+-------------------------------------------------------+
        |      | Ground cover codes include the following:             |
        +------+-------------------------------------------------------+
        |      | 0 = unknown                                           |
        +------+-------------------------------------------------------+
        |      | 1 = grass                                             |
        +------+-------------------------------------------------------+
        |      | 2 = fallow                                            |
        +------+-------------------------------------------------------+
        |      | 3 = bare ground                                       |
        +------+-------------------------------------------------------+
        |      | 4 = brome grass                                       |
        +------+-------------------------------------------------------+
        |      | 5 = sod                                               |
        +------+-------------------------------------------------------+
        |      | 6 = straw mulch                                       |
        +------+-------------------------------------------------------+
        |      | 7 = grass muck                                        |
        +------+-------------------------------------------------------+
        |      | 8 = bare muck                                         |
        +------+-------------------------------------------------------+
        |      | Depth codes include the following:                    |
        +------+-------------------------------------------------------+
        |      | 1 = 5 cm                                              |
        +------+-------------------------------------------------------+
        |      | 2 = 10 cm                                             |
        +------+-------------------------------------------------------+
        |      | 3 = 20 cm                                             |
        +------+-------------------------------------------------------+
        |      | 4 = 50 cm                                             |
        +------+-------------------------------------------------------+
        |      | 5 = 100 cm                                            |
        +------+-------------------------------------------------------+
        |      | 6 = 150 cm                                            |
        +------+-------------------------------------------------------+
        |      | 7 = 180 cm                                            |
        +------+-------------------------------------------------------+
        | SX*# | Maximum soil temperature (tenths of degrees C) where  |
        |      | * corresponds to a code for ground cover and #        |
        |      | corresponds to a code for soil depth. See SN*# for    |
        |      | ground cover and depth codes.                         |
        +------+-------------------------------------------------------+
        | WT** | Weather Type where ** has one of the following        |
        |      | values:                                               |
        +------+-------------------------------------------------------+
        |      | 01 = Fog, ice fog, or freezing fog (may include heavy |
        |      | fog)                                                  |
        +------+-------------------------------------------------------+
        |      | 02 = Heavy fog or heaving freezing fog (not always    |
        |      | distinguished from fog)                               |
        +------+-------------------------------------------------------+
        |      | 03 = Thunder                                          |
        +------+-------------------------------------------------------+
        |      | 04 = Ice pellets, sleet, snow pellets, or small hail  |
        +------+-------------------------------------------------------+
        |      | 05 = Hail (may include small hail)                    |
        +------+-------------------------------------------------------+
        |      | 06 = Glaze or rime                                    |
        +------+-------------------------------------------------------+
        |      | 07 = Dust, volcanic ash, blowing dust, blowing sand,  |
        |      | or blowing obstruction                                |
        +------+-------------------------------------------------------+
        |      | 08 = Smoke or haze                                    |
        +------+-------------------------------------------------------+
        |      | 09 = Blowing or drifting snow                         |
        +------+-------------------------------------------------------+
        |      | 10 = Tornado, waterspout, or funnel cloud             |
        +------+-------------------------------------------------------+
        |      | 11 = High or damaging winds                           |
        +------+-------------------------------------------------------+
        |      | 12 = Blowing spray                                    |
        +------+-------------------------------------------------------+
        |      | 13 = Mist                                             |
        +------+-------------------------------------------------------+
        |      | 14 = Drizzle                                          |
        +------+-------------------------------------------------------+
        |      | 15 = Freezing drizzle                                 |
        +------+-------------------------------------------------------+
        |      | 16 = Rain (may include freezing rain, drizzle, and    |
        |      | freezing drizzle)                                     |
        +------+-------------------------------------------------------+
        |      | 17 = Freezing rain                                    |
        +------+-------------------------------------------------------+
        |      | 18 = Snow, snow pellets, snow grains, or ice crystals |
        +------+-------------------------------------------------------+
        |      | 19 = Unknown source of precipitation                  |
        +------+-------------------------------------------------------+
        |      | 21 = Ground fog                                       |
        +------+-------------------------------------------------------+
        |      | 22 = Ice fog or freezing fog                          |
        +------+-------------------------------------------------------+
        | WV** | Weather in the Vicinity where ** has one of the       |
        |      | following values:                                     |
        +------+-------------------------------------------------------+
        |      | 01 = Fog, ice fog, or freezing fog (may include heavy |
        |      | fog)                                                  |
        +------+-------------------------------------------------------+
        |      | 03 = Thunder                                          |
        +------+-------------------------------------------------------+
        |      | 07 = Ash, dust, sand, or other blowing obstruction    |
        +------+-------------------------------------------------------+
        |      | 18 = Snow or ice crystals                             |
        +------+-------------------------------------------------------+
        |      | 20 = Rain or snow shower                              |
        +------+-------------------------------------------------------+

    startdate
        Start date in ISO8601 format.

    enddate
        End date in ISO8601 format.

    """
    from tsgettoolbox.services.ncdc import cdo as placeholder

    r = resource(
        r'http://www.ncdc.noaa.gov/cdo-web/api/v2/data',
        startdate=startdate,
        enddate=enddate,
        datasetid='GHCND',
        stationid=stationid,
    )

    return tsutils.printiso(odo(r, pd.DataFrame))


# 1763-01-01, 2016-09-01, Global Summary of the Month , 1    , GSOM
# 1763-01-01, 2016-01-01, Global Summary of the Year  , 1    , GSOY
@mando.command(formatter_class=HelpFormatter, doctype='numpy')
def ncdc_gs(stationid,
            database,
            datatypeid='',
            startdate='',
            enddate=''):
    r"""
    National Climatic Data Center Global Summary of the MONTH (GSOM)
    https://gis.ncdc.noaa.gov/all-records/catalog/search/resource/details.page
    Cite this dataset when used as a source: Lawrimore, Jay (2016). Global
    Summary of the Month, Version 1.0. [indicate subset used]. NOAA National
    Centers for Environmental Information. DOI:10.7289/V5QV3JJ5

    National Climatic Data Center Global Summary of the YEAR (GSOY)
    https://gis.ncdc.noaa.gov/all-records/catalog/search/resource/details.page?id=gov.noaa.ncdc:C00947
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
    "NCDC Summary of the Month". There are unique elements that are produced
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
        This is the NCDC
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
        +------+-------------------------------------------------------+
        | MNyz | Monthly/Annual Mean of daily minimum soil temperature |
        |      | given in Celsius or Fahrenheit depending on user      |
        |      | specification. Missing if more than 5 days within the |
        |      | month are missing or flagged or if more than 3        |
        |      | consecutive values within the month are missing or    |
        |      | flagged. DaysMissing: Flag indicating number of days  |
        |      | missing or flagged (from 1 to 5).                     |
        +------+-------------------------------------------------------+
        | HXyz | Highest maximum soil temperature for the month/year   |
        |      | given in Celsius or Fahrenheit depending on user      |
        |      | specification. Missing if more than 5 days within the |
        |      | month are missing or flagged or if more than 3        |
        |      | consecutive values within the month are missing or    |
        |      | flagged. DaysMissing: Flag indicating number of days  |
        |      | missing or flagged (from 1 to 5).                     |
        +------+-------------------------------------------------------+
        | HNyz | Highest minimum soil temperature for the month/year   |
        |      | given in Celsius or Fahrenheit depending on user      |
        |      | specification. Missing if more than 5 days within the |
        |      | month are missing or flagged or if more than 3        |
        |      | consecutive values within the month are missing or    |
        |      | flagged. DaysMissing: Flag indicating number of days  |
        |      | missing or flagged (from 1 to 5).                     |
        +------+-------------------------------------------------------+
        | LXyz | Lowest maximum soil temperature for the month/year    |
        |      | given in Celsius or Fahrenheit depending on user      |
        |      | specification. Missing if more than 5 days within the |
        |      | month are missing or flagged or if more than 3        |
        |      | consecutive values within the month are missing or    |
        |      | flagged. DaysMissing: Flag indicating number of days  |
        |      | missing or flagged (from 1 to 5).                     |
        +------+-------------------------------------------------------+
        | LNyz | Lowest minimum soil temperature for the month/year    |
        |      | given in Celsius or Fahrenheit depending on user      |
        |      | specification. Missing if more than 5 days within the |
        |      | month are missing or flagged or if more than 3        |
        |      | consecutive values within the month are missing or    |
        |      | flagged. DaysMissing: Flag indicating number of days  |
        |      | missing or flagged (from 1 to 5).                     |
        +------+-------------------------------------------------------+
        |      | "y" values for HXyz, HNyz, LXyz, and LNyz are as      |
        |      | follows:                                              |
        +------+-------------------------------------------------------+
        |      | 1=grass                                               |
        +------+-------------------------------------------------------+
        |      | 2=fallow                                              |
        +------+-------------------------------------------------------+
        |      | 3=bare ground                                         |
        +------+-------------------------------------------------------+
        |      | 4=brome grass                                         |
        +------+-------------------------------------------------------+
        |      | 5=sod                                                 |
        +------+-------------------------------------------------------+
        |      | 6=straw mulch                                         |
        +------+-------------------------------------------------------+
        |      | 7=grass muck                                          |
        +------+-------------------------------------------------------+
        |      | 8=bare muck                                           |
        +------+-------------------------------------------------------+
        |      | 0=unknown                                             |
        +------+-------------------------------------------------------+
        |      | "z" values for HXyz, HNyz, LXyz, and LNyz are as      |
        |      | follows:                                              |
        +------+-------------------------------------------------------+
        |      | 1= 2 inches or 5 centimeters depth                    |
        +------+-------------------------------------------------------+
        |      | 2= 4 inches or 10 centimeters depth                   |
        +------+-------------------------------------------------------+
        |      | 3= 8 inches or 20 centimeters depth                   |
        +------+-------------------------------------------------------+
        |      | 4= 20 inches or 50 centimeters depth                  |
        +------+-------------------------------------------------------+
        |      | 5= 40 inches or 100 centimeters depth                 |
        +------+-------------------------------------------------------+
        |      | 6= 60 inches or 150 centimeters depth                 |
        +------+-------------------------------------------------------+
        |      | 7= 72 inches or 180 centimeters depth                 |
        +------+-------------------------------------------------------+
        |      | other=unknown                                         |
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
        +------+-------------------------------------------------------+
        |      | "x" values for HXyz, HNyz, LXyz, and LNyz are as      |
        |      | follows:                                              |
        +------+-------------------------------------------------------+
        |      | 0 = first minimum temperature <= 32 degrees           |
        |      | Fahrenheit/0 degrees Celsius                          |
        +------+-------------------------------------------------------+
        |      | 1 = first minimum temperature <= 28 degrees           |
        |      | Fahrenheit/-2.2 degrees Celsius                       |
        +------+-------------------------------------------------------+
        |      | 2 = first minimum temperature <= 24 degrees           |
        |      | Fahrenheit/-4.4 degrees Celsius                       |
        +------+-------------------------------------------------------+
        |      | 3 = first minimum temperature <= 20 degrees           |
        |      | Fahrenheit/-6.7 degrees Celsius                       |
        +------+-------------------------------------------------------+
        |      | 4 = first minimum temperature <= 16 degrees           |
        |      | Fahrenheit/-8.9 degrees Celsius                       |
        +------+-------------------------------------------------------+
        |      | 5 = last minimum temperature <= 32 degrees            |
        |      | Fahrenheit/0 degrees Celsius                          |
        +------+-------------------------------------------------------+
        |      | 6 = last minimum temperature <= 28 degrees            |
        |      | Fahrenheit/-2.2 degrees Celsius                       |
        +------+-------------------------------------------------------+
        |      | 7 = last minimum temperature <= 24 degrees            |
        |      | Fahrenheit/-4.4 degrees Celsius                       |
        +------+-------------------------------------------------------+
        |      | 8 = last minimum temperature <= 20 degrees            |
        |      | Fahrenheit/-6.7 degrees Celsius                       |
        +------+-------------------------------------------------------+
        |      | 9 = last minimum temperature <= 16 degrees            |
        |      | Fahrenheit/-8.9 degrees Celsius                       |
        +------+-------------------------------------------------------+

    startdate
        Start date in ISO8601 format.

    enddate
        End date in ISO8601 format.
    """

    from tsgettoolbox.services.ncdc import cdo as placeholder

    r = resource(
        r'http://www.ncdc.noaa.gov/cdo-web/api/v2/data',
        startdate=startdate,
        enddate=enddate,
        datasetid=database,
        stationid=stationid,
    )

    return tsutils.printiso(odo(r, pd.DataFrame))


# 1991-06-05, 2016-11-06, Weather Radar (Level II)    , 0.95 , NEXRAD2
# @mando.command(formatter_class=HelpFormatter, doctype='numpy')
def ncdc_nexrad2(stationid,
                 datatypeid='',
                 startdate='',
                 enddate=''):
    r"""
    National Climatic Data Center NEXRAD Level II
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
    observation/element is missing.

    """
    from tsgettoolbox.services.ncdc import cdo as placeholder

    r = resource(
        r'http://www.ncdc.noaa.gov/cdo-web/api/v2/data',
        startdate=startdate,
        enddate=enddate,
        datasetid='NEXRAD2',
        stationid=stationid,
    )

    return tsutils.printiso(odo(r, pd.DataFrame))


# 1991-06-05, 2016-11-06, Weather Radar (Level III)   , 0.95 , NEXRAD3
# @mando.command(formatter_class=HelpFormatter, doctype='numpy')
def ncdc_nexrad3(stationid,
                 datatypeid='',
                 startdate='',
                 enddate=''):
    r"""
    National Climatic Data Center NEXRAD Level III
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
    observation/element is missing.

    """
    from tsgettoolbox.services.ncdc import cdo as placeholder

    r = resource(
        r'http://www.ncdc.noaa.gov/cdo-web/api/v2/data',
        startdate=startdate,
        enddate=enddate,
        datasetid='NEXRAD3',
        stationid=stationid,
    )

    return tsutils.printiso(odo(r, pd.DataFrame))


# 2010-01-01, 2010-01-01, Normals Annual/Seasonal     , 1    , NORMAL_ANN
@mando.command(formatter_class=HelpFormatter, doctype='numpy')
def ncdc_normal_ann(stationid,
                    datatypeid='',
                    startdate='',
                    enddate=''):
    r"""
    National Climatic Data Center annual normals
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
    |       | computed using a pseudonormals approach or derived from  |
    |       | monthly pseudonormals.                                   |
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
        The is the NCDC
        station ID.

    datatypeid : str
        The following table lists the datatypes available for the annual
        dataset.  If the datatypeid is not given defaults to getting all data
        available at that station.

        +-------------------------+------------------------------------+
        | Code                    | Description                        |
        +=========================+====================================+
        | ANN-CLDD-BASE45         | Average annual                     |
        |                         | cooling degree days with base 45F  |
        +-------------------------+------------------------------------+
        | ANN-CLDD-BASE50         | Average annual                     |
        |                         | cooling degree days with base 50F  |
        +-------------------------+------------------------------------+
        | ANN-CLDD-BASE55         | Average annual                     |
        |                         | cooling degree days with base 55F  |
        +-------------------------+------------------------------------+
        | ANN-CLDD-BASE57         | Average annual                     |
        |                         | cooling degree days with base 57F  |
        +-------------------------+------------------------------------+
        | ANN-CLDD-BASE60         | Average annual                     |
        |                         | cooling degree days with base 60F  |
        +-------------------------+------------------------------------+
        | ANN-CLDD-BASE70         | Average annual                     |
        |                         | cooling degree days with base 70F  |
        +-------------------------+------------------------------------+
        | ANN-CLDD-BASE72         | Average annual                     |
        |                         | cooling degree days with base 72F  |
        +-------------------------+------------------------------------+
        | ANN-CLDD-NORMAL         | Average annual                     |
        |                         | cooling degree days with base 65F  |
        +-------------------------+------------------------------------+
        | ANN-DUTR-NORMAL         | Average annual                     |
        |                         | diurnal temperature range          |
        +-------------------------+------------------------------------+
        | ANN-GRDD-BASE40         | Average annual                     |
        |                         | growing degree days with base 40F  |
        +-------------------------+------------------------------------+
        | ANN-GRDD-BASE45         | Average annual                     |
        |                         | growing degree days with base 45F  |
        +-------------------------+------------------------------------+
        | ANN-GRDD-BASE50         | Average annual                     |
        |                         | growing degree days with base 50F  |
        +-------------------------+------------------------------------+
        | ANN-GRDD-BASE55         | Average annual                     |
        |                         | growing degree days with base 55F  |
        +-------------------------+------------------------------------+
        | ANN-GRDD-BASE57         | Average annual                     |
        |                         | growing degree days with base 57F  |
        +-------------------------+------------------------------------+
        | ANN-GRDD-BASE60         | Average annual                     |
        |                         | growing degree days with base 60F  |
        +-------------------------+------------------------------------+
        | ANN-GRDD-BASE65         | Average annual                     |
        |                         | growing degree days with base 65F  |
        +-------------------------+------------------------------------+
        | ANN-GRDD-BASE70         | Average annual                     |
        |                         | growing degree days with base 70F  |
        +-------------------------+------------------------------------+
        | ANN-GRDD-BASE72         | Average annual                     |
        |                         | growing degree days with base 72F  |
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
        |                         | precipitation totals forDecember-  |
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
        | SON-TMIN-AVGNDS-LSTH000 | Average number of days             |
        |                         | per autumn where tmin is less than |
        |                         | or equal to 0F                     |
        +-------------------------+------------------------------------+
        | SON-TMIN-AVGNDS-LSTH010 | Average number of days             |
        |                         | per autumn where tmin is less than |
        |                         | or equal to 10F                    |
        +-------------------------+------------------------------------+
        | SON-TMIN-AVGNDS-LSTH020 | Average number of days             |
        |                         | per autumn where tmin is less than |
        |                         | or equal to 20F                    |
        +-------------------------+------------------------------------+
        | SON-TMIN-AVGNDS-LSTH032 | Average number of days             |
        |                         | per autumn where tmin is less than |
        |                         | or equal to 32F                    |
        +-------------------------+------------------------------------+
        | SON-TMIN-AVGNDS-LSTH040 | Average number of days             |
        |                         | per autumn where tmin is less than |
        |                         | or equal to 40F                    |
        +-------------------------+------------------------------------+
        | SON-TMIN-AVGNDS-LSTH050 | Average number of days             |
        |                         | per autumn where tmin is less than |
        |                         | or equal to 50F                    |
        +-------------------------+------------------------------------+
        | SON-TMIN-AVGNDS-LSTH060 | Average number of days             |
        |                         | per autumn where tmin is less than |
        |                         | or equal to 60F                    |
        +-------------------------+------------------------------------+
        | SON-TMIN-AVGNDS-LSTH070 | Average number of days             |
        |                         | per autumn where tmin is less than |
        |                         | or equal to 70F                    |
        +-------------------------+------------------------------------+
        | SON-TMIN-NORMAL         | Average autumn                     |
        |                         | minimum temperature                |
        +-------------------------+------------------------------------+

    startdate
        Many different formats can be used here for the date
        string, however the closest to ISO8601, the better.

    enddate
        Many different formats can be used here for the date
        string, however the closest to ISO8601, the better.
    """
    from tsgettoolbox.services.ncdc import cdo as placeholder

    r = resource(
        r'http://www.ncdc.noaa.gov/cdo-web/api/v2/data',
        startdate=startdate,
        enddate=enddate,
        datasetid='NORMAL_ANN',
        stationid=stationid,
    )

    return tsutils.printiso(odo(r, pd.DataFrame))


# 2010-01-01, 2010-12-31, Normals Daily               , 1    , NORMAL_DLY
@mando.command(formatter_class=HelpFormatter, doctype='numpy')
def ncdc_normal_dly(stationid,
                    datatypeid='',
                    startdate='',
                    enddate=''):
    r"""
    National Climatic Data Center Daily Normals
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
        End date in ISO8601 format.

    """
    from tsgettoolbox.services.ncdc import ncdc as placeholder

    r = resource(
        r'http://www.ncdc.noaa.gov/cdo-web/api/v2/data',
        startdate=startdate,
        enddate=enddate,
        datasetid='NORMAL_DLY',
        stationid=stationid,
    )

    return tsutils.printiso(odo(r, pd.DataFrame))


# 2010-01-01, 2010-12-31, Normals Hourly              , 1    , NORMAL_HLY
@mando.command(formatter_class=HelpFormatter, doctype='numpy')
def ncdc_normal_hly(stationid,
                    datatypeid='',
                    startdate='',
                    enddate=''):
    r"""
    National Climatic Data Center GHCND Monthly Summaries
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
        End date in ISO8601 format.


    """
    from tsgettoolbox.services.ncdc import cdo as placeholder

    r = resource(
        r'http://www.ncdc.noaa.gov/cdo-web/api/v2/data',
        startdate=startdate,
        enddate=enddate,
        datasetid='NORMAL_HLY',
        stationid=stationid,
    )

    return tsutils.printiso(odo(r, pd.DataFrame))


# 2010-01-01, 2010-12-01, Normals Monthly             , 1    , NORMAL_MLY
@mando.command(formatter_class=HelpFormatter, doctype='numpy')
def ncdc_normal_mly(stationid,
                    datatypeid='',
                    startdate='',
                    enddate=''):
    r"""
    National Climatic Data Center GHCND Monthly Summaries
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
        format.

    """
    from tsgettoolbox.services.ncdc import cdo as placeholder

    r = resource(
        r'http://www.ncdc.noaa.gov/cdo-web/api/v2/data',
        startdate=startdate,
        enddate=enddate,
        datasetid='NORMAL_MLY',
        stationid=stationid,
    )

    return tsutils.printiso(odo(r, pd.DataFrame))


# 1970-05-12, 2014-01-01, Precipitation 15 Minute     , 0.25 , PRECIP_15
@mando.command(formatter_class=HelpFormatter, doctype='numpy')
def ncdc_precip_15(stationid,
                   datatypeid='',
                   startdate='',
                   enddate=''):
    r"""
    National Climatic Data Center 15 minute precipitation
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
        format.

    """
    from tsgettoolbox.services.ncdc import cdo as placeholder

    r = resource(
        r'http://www.ncdc.noaa.gov/cdo-web/api/v2/data',
        startdate=startdate,
        enddate=enddate,
        datasetid='PRECIP_15',
        stationid=stationid,
    )

    return tsutils.printiso(odo(r, pd.DataFrame))


# 1900-01-01, 2014-01-01, Precipitation Hourly        , 1    , PRECIP_HLY
@mando.command(formatter_class=HelpFormatter, doctype='numpy')
def ncdc_precip_hly(stationid,
                    datatypeid='',
                    startdate='',
                    enddate=''):
    r"""
    National Climatic Data Center hourly precipitation
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
        End date in ISO8601 format.

    """
    from tsgettoolbox.services.ncdc import cdo as placeholder

    r = resource(
        r'http://www.ncdc.noaa.gov/cdo-web/api/v2/data',
        startdate=startdate,
        enddate=enddate,
        datasetid='PRECIP_HLY',
        stationid=stationid,
    )

    return tsutils.printiso(odo(r, pd.DataFrame))


# ANNUAL
@mando.command(formatter_class=HelpFormatter, doctype='numpy')
def ncdc_annual(stationid,
                datatypeid='',
                startdate='', enddate=''):
    r"""
    National Climatic Data Center annual data summaries
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
        End date in ISO8601 format.

    """
    from tsgettoolbox.services.ncdc import cdo as placeholder

    r = resource(
        r'http://www.ncdc.noaa.gov/cdo-web/api/v2/data',
        startdate=startdate,
        enddate=enddate,
        datasetid='ANNUAL',
        stationid=stationid,
    )

    return tsutils.printiso(odo(r, pd.DataFrame))


# GHCNDMS
@mando.command(formatter_class=HelpFormatter, doctype='numpy')
def ncdc_ghcndms(stationid,
                 datatypeid='',
                 startdate='',
                 enddate=''):
    r"""
    National Climatic Data Center GHCND Monthly Summaries
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
       format.

    """
    from tsgettoolbox.services.ncdc import cdo as placeholder

    r = resource(
        r'http://www.ncdc.noaa.gov/cdo-web/api/v2/data',
        startdate=startdate,
        enddate=enddate,
        datasetid='GHCNDMS',
        stationid=stationid,
    )

    return tsutils.printiso(odo(r, pd.DataFrame))


@mando.command(formatter_class=HelpFormatter, doctype='numpy')
def ndbc(station,
         observedproperty,
         startUTC,
         endUTC):
    r"""Download from the National Data Buoy Center

    Download data from the National Data Buoy Center.

    The Active Station List is available at
    http://www.ndbc.noaa.gov/activestations.xml

    This file provides metadata in regards to the current deployment for all
    active stations on the NDBC web site. The metadata includes station ID,
    latitude, longitude, station name, station owner, program to which the
    station belongs, and type of data reported as detailed below::

        met: indicates whether the station has reported meteorological
        data in the past eight hours (y/n).

        currents: indicates whether the station has reported water
        current data in the past eight hours (y/n).

        waterquality: indicates whether the station has reported ocean
        chemistry data in the past eight hours (y/n).

        dart: indicates whether the station has reported water column
        height/tsunami data in the past 24 hours (y/n).

    This file is refreshed every five minutes as needed. Note: The main
    activity that drives changes are: a service visit, establishment of
    a new station, or changes in the type of data received (i.e.
    sensor/station failure) therefore, minimal updates would be expected
    in a 24 hour period.

    Note, the TAO entries do not include the data type attributes (met,
    currents, water quality and dart) but do include a seq attribute for
    syncing access to the TAO web site. The TAO array is the climate
    stations in the equatorial Pacific.

    Parameters
    ----------
    station : str
        A station ID, or a currents
        id.

    observedproperty : str
        The 'observedpropery' is one of the
        following::

            air_pressure_at_sea_level
            air_temperature
            currents
            sea_floor_depth_below_sea_surface (water level for tsunami stations)
            sea_water_electrical_conductivity
            sea_water_salinity
            sea_water_temperature
            waves
            winds

        +------------+------------------------------------+
        | Valid Flag | Description                        |
        +============+====================================+
        | 0          | quality not evaluated;             |
        +------------+------------------------------------+
        | 1          | failed quality test;               |
        +------------+------------------------------------+
        | 2          | questionable or suspect data;      |
        +------------+------------------------------------+
        | 3          | good data/passed quality test; and |
        +------------+------------------------------------+
        | 9          | missing data.                      |
        +------------+------------------------------------+

        The 'observedpropery' of 'currents' has several flags.

        +------+----------------------------------------+
        | Flag | Description                            |
        +======+========================================+
        | 1    | overall bin status.                    |
        +------+----------------------------------------+
        | 2    | ADCP Built-In Test (BIT) status.       |
        +------+----------------------------------------+
        | 3    | Error Velocity test status.            |
        +------+----------------------------------------+
        | 4    | Percent Good test status.              |
        +------+----------------------------------------+
        | 5    | Correlation Magnitude test status.     |
        +------+----------------------------------------+
        | 6    | Vertical Velocity test status.         |
        +------+----------------------------------------+
        | 7    | North Horizontal Velocity test status. |
        +------+----------------------------------------+
        | 8    | East Horizontal Velocity test status.  |
        +------+----------------------------------------+
        | 9    | Echo Intensity test status.            |
        +------+----------------------------------------+

    startUTC
        an ISO 8601 date/time string
        (only seconds are optional)

    endUTC
        an ISO 8601 date/time string.
        (only seconds are optional)

    """
    from tsgettoolbox.services import ndbc as placeholder

    r = resource(
        r'http://sdf.ndbc.noaa.gov/sos/server.php',
        station=station,
        startUTC=startUTC,
        endUTC=endUTC,
        observedproperty=observedproperty,
    )

    return tsutils.printiso(odo(r, pd.DataFrame))


@mando.command(formatter_class=HelpFormatter, doctype='numpy')
@tsutils.doc(tsutils.docstrings)
def usgs_eddn(dcp_address,
              parser,
              start_date=None,
              end_date=None):
    r"""Download from the USGS Emergency Data Distribution Network

    This module provides access to data provided by the United States
    Geological Survey Emergency Data Distribution Network web site.

    The DCP message format includes some header information that is parsed
    and the message body, with a variable number of characters. The format of
    the message body varies widely depending on the manufacturer of the
    transmitter, data logger, sensors, and the technician who programmed the
    DCP. The body can be simple ASCII, sometime with parameter codes and
    time-stamps embedded, sometimes not. The body can also be in
    'Pseudo-Binary' which is character encoding of binary data that uses 6 bits
    of every byte and guarantees that all characters are printable.

    United States Geological Survey: http://www.usgs.gov/
    Emergency Data Distribution Network: http://eddn.usgs.gov/
    http://eddn.usgs.gov/dcpformat.html

    Fetches GOES Satellite DCP messages from USGS Emergency Data Distribution
    Network.

    Parameters
    ----------
    dcp_address
        DCP address or list of DCP addresses to be fetched; lists will be
        joined by a ','.

    parser
        function that acts on dcp_message each row of the dataframe and returns
        a new dataframe containing several rows of decoded data. This returned
        dataframe may have different (but derived) timestamps than that the
        original row. If a string is passed then a matching parser function is
        looked up from ulmo.usgs.eddn.parser.  The prebuilt functions are
        "twdb_dot", "twdb_stevens", "twdb_sutron", and "twdb_texuni".

    {start_date}

    {end_date}

    """
    from tsgettoolbox.services.usgs import eddn

    df = eddn.ulmo_df(
        dcp_address=dcp_address,
        parser=parser,
        start_date=start_date,
        end_date=end_date)

    return tsutils.printiso(df)


@mando.command(formatter_class=HelpFormatter, doctype='numpy')
@tsutils.doc(tsutils.docstrings)
def lcra_hydromet(site_code,
                  parameter_code,
                  start_date=None,
                  end_date=None,
                  dam_site_location='head'):
    r"""Fetches site parameter data

    This module provides access to hydrologic and climate data in the Colorado
    River Basin (Texas) provided by the Lower Colorado River Authority
    Hydromet web site and web service.

    http://www.lcra.org

    http://hydromet.lcra.org

    Parameters
    ----------
    site_code
        The LCRA site code (four chars long) of the site you want to query data
        for.
    parameter_code
        LCRA parameter
        code.

        +----------------+---------------------------------------+
        | parameter_code | Description                           |
        +----------------+---------------------------------------+
        | stage          | the level of water above a benchmark  |
        |                | in feet                               |
        +----------------+---------------------------------------+
        | flow           | streamflow in cubic feet per second   |
        +----------------+---------------------------------------+
        | pc             | precipitation in inches               |
        +----------------+---------------------------------------+
        | temp           | air temperature in degrees fahrenheit |
        +----------------+---------------------------------------+
        | rhumid         | air relative humidity as percentage   |
        +----------------+---------------------------------------+
        | cndvty         | water electrical conductivity in      |
        |                | micromhos                             |
        +----------------+---------------------------------------+
        | tds            | total suspended solids                |
        +----------------+---------------------------------------+
        | windsp         | wind speed miles per hour             |
        +----------------+---------------------------------------+
        | winddir        | wind direction in degrees azimuth     |
        +----------------+---------------------------------------+
        | upperbasin     | ALL Upper Basin flow and water levels |
        +----------------+---------------------------------------+
        | lowerbasin     | ALL Lower Basin flow and water levels |
        +----------------+---------------------------------------+

    {start_date}
    {end_date}
    dam_site_location : str
        'head' (default) or 'tail'
        The site location relative to the dam.  Not used for `upperbasin`
        and `lowerbasin` parameters.

    """
    from tsgettoolbox.services.lcra import hydromet

    df = hydromet.ulmo_df(site_code,
                          parameter_code,
                          start_date=start_date,
                          end_date=end_date,
                          dam_site_location=dam_site_location)

    return tsutils.printiso(df)


@mando.command(formatter_class=HelpFormatter, doctype='numpy')
@tsutils.doc(tsutils.docstrings)
def lcra_wq(site_code,
            historical=True,
            start_date=None,
            end_date=None):
    r"""
    Fetches historical or near real-time (for some sites) data

    This module provides access to data provided by the Lower Colorado
    River Authority Water Quality web site.

    Lower Colorado River Authority: http://www.lcra.org

    Water Quality: http://waterquality.lcra.org/

    Parameters
    ----------
    site_code
        The site code to fetch data for. The following bay sites also have
        near real-time data available if `historical` option is set to False.

        +--------------------+-----------------+
        | Near Real-Time     | Name            |
        | (historical=False) |                 |
        | site_code          |                 |
        +====================+=================+
        | 6977               | Matagorda 4SSW  |
        +--------------------+-----------------+
        | 6985               | Matagorda 7 SW  |
        +--------------------+-----------------+
        | 6990               | Matagorda 8 SSW |
        +--------------------+-----------------+
        | 6996               | Matagorda 9 SW  |
        +--------------------+-----------------+

    historical
        Flag to indicate whether to get historical or near real-time data from
        the bay sites.
    {start_date}
    {end_date}

    """
    from tsgettoolbox.services.lcra import wq

    df = wq.ulmo_df(site_code=site_code,
                    historical=historical,
                    start_date=start_date,
                    end_date=end_date)

    return tsutils.printiso(df)


@mando.command(formatter_class=HelpFormatter, doctype='numpy')
@tsutils.doc(tsutils.docstrings)
def twc(county,
        start_date=None,
        end_date=None):
    r"""
    Fetches Texas weather data

    This module provides direct access to `Texas Weather Connection`_ `Daily
    Keetch-Byram Drought Index (KBDI)`_ dataset.

    .. _Texas Weather Connection: http://twc.tamu.edu/
    .. _Daily Keetch-Byram Drought Index (KBDI): http://twc.tamu.edu/drought/kbdi

    Parameters
    ----------
    county: ``None`` or str
        If specified, results will be limited to the county corresponding to the
        given 5-character Texas county fips code i.e. 48???.
    {start_date}
    {end_date}

    """
    from tsgettoolbox.services import twc

    df = twc.ulmo_df(county=county,
                     start_date=start_date,
                     end_date=end_date)

    return tsutils.printiso(df)


@mando.command(formatter_class=HelpFormatter, doctype='numpy')
def modis(lat,
          lon,
          product,
          band,
          startdate=None,
          enddate=None):
    r"""Download MODIS derived data.

    This data are derived data sets from MODIS satellite photos.

    MCD12Q1

    The MODIS Land Cover Type product contains five classification
    schemes, which describe land cover properties derived from
    observations spanning a year's input of Terra- and Aqua-MODIS
    data.  The primary land cover scheme identifies 17 land cover
    classes defined by the International Geosphere Biosphere
    Programme (IGBP), which includes 11 natural vegetation classes,
    3 developed and mosaicked land classes, and three non-vegetated
    land classes.

    The MODIS Terra + Aqua Land Cover Type Yearly L3 Global 500
    m SIN Grid product incorporates five different land cover
    classification schemes, derived through a supervised
    decision-tree classification method.

    V051 Land Cover Type products are produced with revised training
    data and certain algorithm refinements.  For further details,
    please consult the following paper:

    Friedl, M. A., Sulla-Menashe, D., Tan, B., Schneider, A.,
    Ramankutty, N., Sibley, A., and Huang, X. (2010). MODIS
    Collection 5 global land cover: Algorithm refinements and
    characterization of new datasets. Remote Sensing of Environment,
    114, 168-182.

    Land Cover Datasets

    +-------------------+----------+---------------------------+
    | Band              | Abbrev   | Description               |
    +===================+==========+===========================+
    | Land_Cover_Type_1 | IGBP     | global vegetation         |
    |                   |          | classification scheme     |
    +-------------------+----------+---------------------------+
    | Land_Cover_Type_2 | UMD      | University of Maryland    |
    |                   |          | scheme                    |
    +-------------------+----------+---------------------------+
    | Land_Cover_Type_3 | LAI/fPAR | MODIS-derived scheme      |
    +-------------------+----------+---------------------------+
    | Land_Cover_Type_4 | NPP      | MODIS-derived Net Primary |
    |                   |          | Production (NPP) scheme   |
    +-------------------+----------+---------------------------+
    | Land_Cover_Type_5 | PFT      | Plant Functional Type     |
    |                   |          | (PFT) scheme              |
    +-------------------+----------+---------------------------+

    Land Cover Types Description

    +------+-----------+-----------+-----------+-----------+-----------+
    | Code | IGBP      | UMD       | LAI/fPAR  | NPP       | PFT       |
    +======+===========+===========+===========+===========+===========+
    | 0    | Water     | Water     | Water     | Water     | Water     |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 1    | Evergreen | Evergreen | Grasses/  | Evergreen | Evergreen |
    |      | Needle    | Needle    | Cereal    | Needle    | Needle    |
    |      | leaf      | leaf      | crop      | leaf      | leaf      |
    |      | forest    | forest    |           |           |           |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 2    | Evergreen | Evergreen | Shrub     | Evergreen | Evergreen |
    |      | Broadleaf | Broadleaf |           | Broadleaf | Broadleaf |
    |      | forest    | forest    |           |           |           |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 3    | Deciduous | Deciduous | Broadleaf | Deciduous | Deciduous |
    |      | Needle    | Needle    | crop      | Needle    | Needle    |
    |      | leaf      | leaf      |           | leaf      | leaf      |
    |      | forest    | forest    |           |           |           |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 4    | Deciduous | Deciduous | Savanna   | Deciduous | Deciduous |
    |      | Broadleaf | Broadleaf |           | Broadleaf | Broadleaf |
    |      | forest    | forest    |           |           |           |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 5    | Mixed     | Mixed     | Evergreen | Annual    | Shrub     |
    |      | forest    | forest    | Broadleaf | Broadleaf |           |
    |      |           |           | forest    |           |           |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 6    | Closed    | Closed    | Deciduous | Annual    | Grassland |
    |      | shrubland | shrubland | Broadleaf | grass     |           |
    |      |           |           | forest    |           |           |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 7    | Open      | Open      | Evergreen | Non-      | Cereal    |
    |      | shrubland | shrubland | Needle    | vegetated | crops     |
    |      |           |           | leaf      | land      |           |
    |      |           |           | forest    |           |           |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 8    | Woody     | Woody     | Deciduous | Urban     | Broad-    |
    |      | savanna   | savanna   | Needle    |           | leaf      |
    |      |           |           | leaf      |           | crops     |
    |      |           |           | forest    |           |           |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 9    | Savanna   | Savanna   | Non-      |           | Urban and |
    |      |           |           | vegetated |           | built-up  |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 10   | Grassland | Grassland | Urban     |           | Snow and  |
    |      |           |           |           |           | ice       |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 11   | Permanent |           |           |           | Barren or |
    |      | wetlands  |           |           |           | sparse    |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 12   | Croplands | Cropland  |           |           |           |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 13   | Urban and | Urban and |           |           |           |
    |      | built-up  | built-up  |           |           |           |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 14   | Cropland  |           |           |           |           |
    |      | /Natural  |           |           |           |           |
    |      | mosaic    |           |           |           |           |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 15   | Snow and  |           |           |           |           |
    |      | ice       |           |           |           |           |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 16   | Barren or | Barren or |           |           |           |
    |      | sparsely  | sparsely  |           |           |           |
    |      | vegetated | vegetated |           |           |           |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 254  | Unclassi  | Unclassi  | Unclassi  | Unclassi  | Unclassi  |
    |      | fied      | fied      | fied      | fied      | fies      |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 255  | Fill      | Fill      | Fill      | Fill      | Fill      |
    |      | Value     | Value     | Value     | Value     | Value     |
    +------+-----------+-----------+-----------+-----------+-----------+

    Citation

    Citation instructions are from https://modis.ornl.gov/citation.html

    When using subsets of MODIS Land Products from the ORNL DAAC, please
    use the following citation format:

    Citation: Single Site

    Format (single site):

    ORNL DAAC 2008. MODIS Collection 5 Land Products Global Subsetting
    and Visualization Tool. ORNL DAAC, Oak Ridge, Tennessee, USA.
    Accessed Month dd, yyyy. Subset obtained for [Product name] product
    at [Lat],[Lon], time period: [Start date] to [End date], and subset
    size: [Width] x [Height] km. http://dx.doi.org/10.3334/ORNLDAAC/1241

    Example (single site):

    ORNL DAAC. 2008. MODIS Collection 5 Land Products Global Subsetting
    and Visualization Tool. ORNL DAAC, Oak Ridge, Tennessee, USA.
    Accessed August 25, 2015. Subset obtained for MOD13Q1 product at
    39.497N,107.3028W, time period: 2000-02-18 to 2015-07-28, and subset
    size: 0.25 x 0.25 km. http://dx.doi.org/10.3334/ORNLDAAC/1241

    Notes:

    The coordinates used in the citation are the Latitude and Longitude
    (decimal degrees) specified by the user when the order is placed,
    trimmed to 4 decimal places.  The citation is also sent in the email
    along with data retrieval instructions after the order is processed.
    BibTeX (.bib) file is available for download on the data
    visualization and download page (see screenshot below).

    Citation: Multiple Sites

    Format (multiple sites, clustered together):

    ORNL DAAC 2008. MODIS Collection 5 Land Products Global Subsetting
    and Visualization Tool. ORNL DAAC, Oak Ridge, Tennessee, USA.
    Accessed Month dd, yyyy. Subset obtained for [Product name] product
    at various sites in Spatial Range: N=DD.DD, S=DD.DD, E=DDD.DD,
    W=DDD.DD, time period: [Start date] to [End date], and subset size:
    [Width] x [Height] km. http://dx.doi.org/10.3334/ORNLDAAC/1241

    Example (multiple sites, clustered together):

    ORNL DAAC. 2008. MODIS Collection 5 Land Products Global Subsetting
    and Visualization Tool. ORNL DAAC, Oak Ridge, Tennessee, USA.
    Accessed August 25, 2015. Subset obtained for MOD13Q1 product at
    various sites in Spatial Range: N=39.49N, S=39.25N, E=107.42W,
    W=106.48W, time period: 2000-02-18 to 2015-07-28, and subset size:
    0.25 x 0.25 km. http://dx.doi.org/10.3334/ORNLDAAC/1241

    Notes:

    "Spatial Range: N=DD.DD, S=DD.DD, E=DDD.DD, W=DDD.DD" is the
    bounding box for the site locations used for requesting subsets.

    Please cite each product separately.

    The coordinates used in the citation are the Latitude and Longitude
    (decimal degrees) specified by the user when the order is placed,
    trimmed to 4 decimal places.  The citation is also sent in the email
    along with data retrieval instructions after the order is processed.
    BibTeX (.bib) file is available for download on the data
    visualization and download page. Please modify it manually for
    multiple sites.

    Parameters
    ----------
    lat : float
        Latitude (required): Enter single geographic point by
        latitude.

    lon : float
        Longitude (required): Enter single geographic point by
        longitude.

    product : str
        One of the following values in the 'product'
        column.

        +---------+------------------------------------+--------+------+
        | product | Name                               | Freq   | Size |
        |         |                                    | (days) | (m)  |
        +=========+====================================+========+======+
        | MCD12Q1 | MODIS/Terra+Aqua Land Cover (LC)   | annual | 500  |
        |         | Type Yearly L3 Global 500m SIN     |        |      |
        |         | Grid                               |        |      |
        +---------+------------------------------------+--------+------+
        | MCD12Q2 | MODIS/Terra+Aqua Land Cover        | annual | 500  |
        |         | Dynamics (LCD) Yearly L3 Global    |        |      |
        |         | 500m SIN Grid                      |        |      |
        +---------+------------------------------------+--------+------+
        | MCD43A1 | MODIS/Terra+Aqua BRDF/Albedo       | 16     | 500  |
        |         | (BRDF/MCD43A1) 16-Day L3 Global    |        |      |
        |         | 500m SIN Grid                      |        |      |
        +---------+------------------------------------+--------+------+
        | MCD43A2 | MODIS/Terra+Aqua BRDF/Model        | 16     | 500  |
        |         | Quality (BRDF/MCD43A2) 16-Day L3   |        |      |
        |         | Global 500m SIN Grid V005          |        |      |
        +---------+------------------------------------+--------+------+
        | MCD43A4 | MODIS/Terra+Aqua Nadir BRDF-       | 16     | 500  |
        |         | Adjusted Reflectance (NBAR) 16-Day |        |      |
        |         | L3 Global 500m SIN Grid            |        |      |
        +---------+------------------------------------+--------+------+
        | MOD09A1 | MODIS/Terra Surface Reflectance    | 8      | 500  |
        |         | (SREF) 8-Day L3 Global 500m SIN    |        |      |
        |         | Grid                               |        |      |
        +---------+------------------------------------+--------+------+
        | MOD11A2 | MODIS/Terra Land Surface           | 8      | 1000 |
        |         | Temperature/Emissivity (LST) 8-Day |        |      |
        |         | L3 Global 1km SIN Grid             |        |      |
        +---------+------------------------------------+--------+------+
        | MOD13Q1 | MODIS/Terra Vegetation Indices     | 16     | 250  |
        |         | (NDVI/EVI) 16-Day L3 Global 250m   |        |      |
        |         | SIN Grid [Collection 5]            |        |      |
        +---------+------------------------------------+--------+------+
        | MOD15A2 | Leaf Area Index (LAI) and Fraction | 8      | 1000 |
        |         | of Photosynthetically Active       |        |      |
        |         | Radiation (FPAR) 8-Day Composite   |        |      |
        |         | [Collection 5]                     |        |      |
        +---------+------------------------------------+--------+------+
        | MOD16A2 | MODIS/Terra Evapotranspiration     | 8      | 1000 |
        |         | (ET) 8-Day L4 Global Collection 5  |        |      |
        +---------+------------------------------------+--------+------+
        | MOD17A2 | MODIS/Terra Gross Primary          | 8      | 1000 |
        |         | Production (GPP) 8-Day L4 Global   |        |      |
        |         | [Collection 5.1]                   |        |      |
        +---------+------------------------------------+--------+------+
        | MOD17A3 | MODIS/Terra Net Primary Production | annual | 1000 |
        |         | (NPP) Yearly L4 Global 1km SIN     |        |      |
        |         | Grid                               |        |      |
        +---------+------------------------------------+--------+------+
        | MYD09A1 | MODIS/Aqua Surface Reflectance     | 8      | 500  |
        |         | (SREF) 8-Day L3 Global 500m SIN    |        |      |
        |         | Grid                               |        |      |
        +---------+------------------------------------+--------+------+
        | MYD11A2 | MODIS/Aqua Land Surface            | 8      | 1000 |
        |         | Temperature/Emissivity (LST)8-Day  |        |      |
        |         | L3 Global 1km SIN Grid             |        |      |
        +---------+------------------------------------+--------+------+
        | MYD13Q1 | MODIS/Aqua Vegetation Indices      | 16     | 250  |
        |         | (NDVI/EVI) 16-Day L3 Global 1km    |        |      |
        |         | SIN Grid                           |        |      |
        +---------+------------------------------------+--------+------+
        | MYD15A2 | MODIS/Aqua Leaf Area Index (LAI)   | 8      | 1000 |
        |         | and Fraction of Photosynthetically |        |      |
        |         | Active Radiation (FPAR) 8 Day      |        |      |
        |         | Composite                          |        |      |
        +---------+------------------------------------+--------+------+
        | MYD17A2 | MODIS/Aqua Gross Primary           | 8      | 1000 |
        |         | Production (GPP) 8 Day L4 Global   |        |      |
        +---------+------------------------------------+--------+------+

    band : str
        One of the following. The 'band' selected from the second column must
        match the 'product' in the first column.

        +------------+-------------------------------------------------+
        | product    | band                                            |
        +============+=================================================+
        | MCD12Q1    | LC_Property_1  (not populated)                  |
        +------------+-------------------------------------------------+
        |            | LC_Property_2  (not populated)                  |
        +------------+-------------------------------------------------+
        |            | LC_Property_3  (not populated)                  |
        +------------+-------------------------------------------------+
        |            | Land_Cover_Type_1 (See Land Cover Datasets and  |
        |            | Land Cover Types tables)                        |
        +------------+-------------------------------------------------+
        |            | Land_Cover_Type_2 (See Land Cover Datasets and  |
        |            | Land Cover Types tables)                        |
        +------------+-------------------------------------------------+
        |            | Land_Cover_Type_3 (See Land Cover Datasets and  |
        |            | Land Cover Types tables)                        |
        +------------+-------------------------------------------------+
        |            | Land_Cover_Type_4 (See Land Cover Datasets and  |
        |            | Land Cover Types tables)                        |
        +------------+-------------------------------------------------+
        |            | Land_Cover_Type_5 (See Land Cover Datasets and  |
        |            | Land Cover Types tables)                        |
        +------------+-------------------------------------------------+
        |            | Land_Cover_Type_1_Assessment (per cent)         |
        +------------+-------------------------------------------------+
        |            | Land_Cover_Type_2_Assessment (not populated)    |
        +------------+-------------------------------------------------+
        |            | Land_Cover_Type_3_Assessment (not populated)    |
        +------------+-------------------------------------------------+
        |            | Land_Cover_Type_4_Assessment (not populated)    |
        +------------+-------------------------------------------------+
        |            | Land_Cover_Type_5_Assessment (not populated)    |
        +------------+-------------------------------------------------+
        |            | Land_Cover_Type_1_Secondary (See Land Cover     |
        |            | Datasets and Land Cover Types tables)           |
        +------------+-------------------------------------------------+
        |            | Land_Cover_Type_1_Secondary_Percent (not        |
        |            | populated)                                      |
        +------------+-------------------------------------------------+
        | MCD12Q2    | NBAR_EVI_Onset_Greenness_Maximum.Num_Modes_02   |
        +------------+-------------------------------------------------+
        |            | NBAR_EVI_Onset_Greenness_Minimum.Num_Modes_02   |
        +------------+-------------------------------------------------+
        |            | NBAR_EVI_Onset_Greenness_Maximum.Num_Modes_01   |
        +------------+-------------------------------------------------+
        |            | NBAR_EVI_Onset_Greenness_Minimum.Num_Modes_01   |
        +------------+-------------------------------------------------+
        |            | Onset_Greenness_Minimum.Num_Modes_02            |
        +------------+-------------------------------------------------+
        |            | Onset_Greenness_Decrease.Num_Modes_02           |
        +------------+-------------------------------------------------+
        |            | Onset_Greenness_Maximum.Num_Modes_02            |
        +------------+-------------------------------------------------+
        |            | Onset_Greenness_Increase.Num_Modes_02           |
        +------------+-------------------------------------------------+
        |            | Onset_Greenness_Minimum.Num_Modes_01            |
        +------------+-------------------------------------------------+
        |            | Onset_Greenness_Decrease.Num_Modes_01           |
        +------------+-------------------------------------------------+
        |            | Onset_Greenness_Maximum.Num_Modes_01            |
        +------------+-------------------------------------------------+
        |            | Onset_Greenness_Increase.Num_Modes_01           |
        +------------+-------------------------------------------------+
        |            | NBAR_EVI_Area.Num_Modes_01                      |
        +------------+-------------------------------------------------+
        |            | NBAR_EVI_Area.Num_Modes_02                      |
        +------------+-------------------------------------------------+
        | MCD43A1    | BRDF_Albedo_Parameters_Band1.Num_Parameters_01  |
        +------------+-------------------------------------------------+
        |            | BRDF_Albedo_Parameters_Band1.Num_Parameters_02  |
        +------------+-------------------------------------------------+
        |            | BRDF_Albedo_Parameters_Band1.Num_Parameters_03  |
        +------------+-------------------------------------------------+
        |            | BRDF_Albedo_Parameters_Band2.Num_Parameters_01  |
        +------------+-------------------------------------------------+
        |            | BRDF_Albedo_Parameters_Band2.Num_Parameters_02  |
        +------------+-------------------------------------------------+
        |            | BRDF_Albedo_Parameters_Band2.Num_Parameters_03  |
        +------------+-------------------------------------------------+
        |            | BRDF_Albedo_Parameters_Band3.Num_Parameters_01  |
        +------------+-------------------------------------------------+
        |            | BRDF_Albedo_Parameters_Band3.Num_Parameters_02  |
        +------------+-------------------------------------------------+
        |            | BRDF_Albedo_Parameters_Band3.Num_Parameters_03  |
        +------------+-------------------------------------------------+
        |            | BRDF_Albedo_Parameters_Band4.Num_Parameters_01  |
        +------------+-------------------------------------------------+
        |            | BRDF_Albedo_Parameters_Band4.Num_Parameters_02  |
        +------------+-------------------------------------------------+
        |            | BRDF_Albedo_Parameters_Band4.Num_Parameters_03  |
        +------------+-------------------------------------------------+
        |            | BRDF_Albedo_Parameters_Band5.Num_Parameters_01  |
        +------------+-------------------------------------------------+
        |            | BRDF_Albedo_Parameters_Band5.Num_Parameters_02  |
        +------------+-------------------------------------------------+
        |            | BRDF_Albedo_Parameters_Band5.Num_Parameters_03  |
        +------------+-------------------------------------------------+
        |            | BRDF_Albedo_Parameters_Band6.Num_Parameters_01  |
        +------------+-------------------------------------------------+
        |            | BRDF_Albedo_Parameters_Band6.Num_Parameters_02  |
        +------------+-------------------------------------------------+
        |            | BRDF_Albedo_Parameters_Band6.Num_Parameters_03  |
        +------------+-------------------------------------------------+
        |            | BRDF_Albedo_Parameters_Band7.Num_Parameters_01  |
        +------------+-------------------------------------------------+
        |            | BRDF_Albedo_Parameters_Band7.Num_Parameters_02  |
        +------------+-------------------------------------------------+
        |            | BRDF_Albedo_Parameters_Band7.Num_Parameters_03  |
        +------------+-------------------------------------------------+
        |            | BRDF_Albedo_Parameters_vis.Num_Parameters_01    |
        +------------+-------------------------------------------------+
        |            | BRDF_Albedo_Parameters_vis.Num_Parameters_02    |
        +------------+-------------------------------------------------+
        |            | BRDF_Albedo_Parameters_vis.Num_Parameters_03    |
        +------------+-------------------------------------------------+
        |            | BRDF_Albedo_Parameters_nir.Num_Parameters_01    |
        +------------+-------------------------------------------------+
        |            | BRDF_Albedo_Parameters_nir.Num_Parameters_02    |
        +------------+-------------------------------------------------+
        |            | BRDF_Albedo_Parameters_nir.Num_Parameters_03    |
        +------------+-------------------------------------------------+
        |            | BRDF_Albedo_Parameters_shortwave.               |
        |            | Num_Parameters_01                               |
        +------------+-------------------------------------------------+
        |            | BRDF_Albedo_Parameters_shortwave.               |
        |            | Num_Parameters_02                               |
        +------------+-------------------------------------------------+
        |            | BRDF_Albedo_Parameters_shortwave.               |
        |            | Num_Parameters_03                               |
        +------------+-------------------------------------------------+
        |            | BRDF_Shape_Indicators.Num_Shape_Fields_01       |
        +------------+-------------------------------------------------+
        |            | BRDF_Shape_Indicators.Num_Shape_Fields_02       |
        +------------+-------------------------------------------------+
        |            | BRDF_Shape_Indicators.Num_Shape_Fields_03       |
        +------------+-------------------------------------------------+
        |            | BRDF_Shape_Indicators.Num_Shape_Fields_04       |
        +------------+-------------------------------------------------+
        | MCD43A2    | BRDF_Albedo_Quality                             |
        +------------+-------------------------------------------------+
        |            | BRDF_Albedo_Ancillary                           |
        +------------+-------------------------------------------------+
        |            | BRDF_Albedo_Band_Quality                        |
        +------------+-------------------------------------------------+
        |            | Snow_BRDF_Albedo                                |
        +------------+-------------------------------------------------+
        | MCD43A4    | Nadir_Reflectance_Band1                         |
        +------------+-------------------------------------------------+
        |            | Nadir_Reflectance_Band2                         |
        +------------+-------------------------------------------------+
        |            | Nadir_Reflectance_Band3                         |
        +------------+-------------------------------------------------+
        |            | Nadir_Reflectance_Band4                         |
        +------------+-------------------------------------------------+
        |            | Nadir_Reflectance_Band5                         |
        +------------+-------------------------------------------------+
        |            | Nadir_Reflectance_Band6                         |
        +------------+-------------------------------------------------+
        |            | Nadir_Reflectance_Band7                         |
        +------------+-------------------------------------------------+
        | MOD09A1    | sur_refl_day_of_year                            |
        +------------+-------------------------------------------------+
        |            | sur_refl_qc_500m                                |
        +------------+-------------------------------------------------+
        |            | sur_refl_raz                                    |
        +------------+-------------------------------------------------+
        |            | sur_refl_state_500m                             |
        +------------+-------------------------------------------------+
        |            | sur_refl_szen                                   |
        +------------+-------------------------------------------------+
        |            | sur_refl_vzen                                   |
        +------------+-------------------------------------------------+
        |            | sur_refl_b01                                    |
        +------------+-------------------------------------------------+
        |            | sur_refl_b02                                    |
        +------------+-------------------------------------------------+
        |            | sur_refl_b03                                    |
        +------------+-------------------------------------------------+
        |            | sur_refl_b04                                    |
        +------------+-------------------------------------------------+
        |            | sur_refl_b05                                    |
        +------------+-------------------------------------------------+
        |            | sur_refl_b06                                    |
        +------------+-------------------------------------------------+
        |            | sur_refl_b07                                    |
        +------------+-------------------------------------------------+
        | MOD11A2    | Clear_sky_days                                  |
        +------------+-------------------------------------------------+
        |            | Clear_sky_nights                                |
        +------------+-------------------------------------------------+
        |            | Day_view_angl                                   |
        +------------+-------------------------------------------------+
        |            | Day_view_time                                   |
        +------------+-------------------------------------------------+
        |            | Emis_31                                         |
        +------------+-------------------------------------------------+
        |            | Emis_32                                         |
        +------------+-------------------------------------------------+
        |            | Night_view_angl                                 |
        +------------+-------------------------------------------------+
        |            | Night_view_time                                 |
        +------------+-------------------------------------------------+
        |            | QC_Day                                          |
        +------------+-------------------------------------------------+
        |            | QC_Night                                        |
        +------------+-------------------------------------------------+
        |            | LST_Day_1km                                     |
        +------------+-------------------------------------------------+
        |            | LST_Night_1km                                   |
        +------------+-------------------------------------------------+
        | MOD13Q1    | 250m_16_days_blue_reflectance                   |
        +------------+-------------------------------------------------+
        |            | 250m_16_days_MIR_reflectance                    |
        +------------+-------------------------------------------------+
        |            | 250m_16_days_NIR_reflectance                    |
        +------------+-------------------------------------------------+
        |            | 250m_16_days_pixel_reliability                  |
        +------------+-------------------------------------------------+
        |            | 250m_16_days_red_reflectance                    |
        +------------+-------------------------------------------------+
        |            | 250m_16_days_relative_azimuth_angle             |
        +------------+-------------------------------------------------+
        |            | 250m_16_days_sun_zenith_angle                   |
        +------------+-------------------------------------------------+
        |            | 250m_16_days_view_zenith_angle                  |
        +------------+-------------------------------------------------+
        |            | 250m_16_days_VI_Quality                         |
        +------------+-------------------------------------------------+
        |            | 250m_16_days_NDVI                               |
        +------------+-------------------------------------------------+
        |            | 250m_16_days_EVI                                |
        +------------+-------------------------------------------------+
        |            | 250m_16_days_composite_day_of_the_year          |
        +------------+-------------------------------------------------+
        | MOD15A2    | FparExtra_QC                                    |
        +------------+-------------------------------------------------+
        |            | FparLai_QC                                      |
        +------------+-------------------------------------------------+
        |            | FparStdDev_1km                                  |
        +------------+-------------------------------------------------+
        |            | LaiStdDev_1km                                   |
        +------------+-------------------------------------------------+
        |            | Lai_1km                                         |
        +------------+-------------------------------------------------+
        |            | Fpar_1km                                        |
        +------------+-------------------------------------------------+
        | MOD15A2GFS | FparExtra_QC                                    |
        +------------+-------------------------------------------------+
        |            | FparLai_QC                                      |
        +------------+-------------------------------------------------+
        |            | FparStdDev_1km                                  |
        +------------+-------------------------------------------------+
        |            | LaiStdDev_1km                                   |
        +------------+-------------------------------------------------+
        |            | Lai_1km                                         |
        +------------+-------------------------------------------------+
        |            | Fpar_1km                                        |
        +------------+-------------------------------------------------+
        | MOD16A2    | ET_1km                                          |
        +------------+-------------------------------------------------+
        |            | LE_1km                                          |
        +------------+-------------------------------------------------+
        |            | PET_1km                                         |
        +------------+-------------------------------------------------+
        |            | PLE_1km                                         |
        +------------+-------------------------------------------------+
        |            | ET_QC_1km                                       |
        +------------+-------------------------------------------------+
        | MOD17A2_51 | Psn_QC_1km                                      |
        +------------+-------------------------------------------------+
        |            | PsnNet_1km                                      |
        +------------+-------------------------------------------------+
        |            | Gpp_1km                                         |
        +------------+-------------------------------------------------+
        | MOD17A3    | Gpp_Npp_QC_1km                                  |
        +------------+-------------------------------------------------+
        |            | Npp_1km                                         |
        +------------+-------------------------------------------------+
        |            | Gpp_1km                                         |
        +------------+-------------------------------------------------+
        | MYD09A1    | sur_refl_day_of_year                            |
        +------------+-------------------------------------------------+
        |            | sur_refl_qc_500m                                |
        +------------+-------------------------------------------------+
        |            | sur_refl_raz                                    |
        +------------+-------------------------------------------------+
        |            | sur_refl_state_500m                             |
        +------------+-------------------------------------------------+
        |            | sur_refl_szen                                   |
        +------------+-------------------------------------------------+
        |            | sur_refl_vzen                                   |
        +------------+-------------------------------------------------+
        |            | sur_refl_b01                                    |
        +------------+-------------------------------------------------+
        |            | sur_refl_b02                                    |
        +------------+-------------------------------------------------+
        |            | sur_refl_b03                                    |
        +------------+-------------------------------------------------+
        |            | sur_refl_b04                                    |
        +------------+-------------------------------------------------+
        |            | sur_refl_b05                                    |
        +------------+-------------------------------------------------+
        |            | sur_refl_b06                                    |
        +------------+-------------------------------------------------+
        |            | sur_refl_b07                                    |
        +------------+-------------------------------------------------+
        | MYD11A2    | Clear_sky_days                                  |
        +------------+-------------------------------------------------+
        |            | Clear_sky_nights                                |
        +------------+-------------------------------------------------+
        |            | Day_view_angl                                   |
        +------------+-------------------------------------------------+
        |            | Day_view_time                                   |
        +------------+-------------------------------------------------+
        |            | Emis_31                                         |
        +------------+-------------------------------------------------+
        |            | Emis_32                                         |
        +------------+-------------------------------------------------+
        |            | Night_view_angl                                 |
        +------------+-------------------------------------------------+
        |            | Night_view_time                                 |
        +------------+-------------------------------------------------+
        |            | QC_Day                                          |
        +------------+-------------------------------------------------+
        |            | QC_Night                                        |
        +------------+-------------------------------------------------+
        |            | LST_Day_1km                                     |
        +------------+-------------------------------------------------+
        |            | LST_Night_1km                                   |
        +------------+-------------------------------------------------+
        | MYD13Q1    | 250m_16_days_blue_reflectance                   |
        +------------+-------------------------------------------------+
        |            | 250m_16_days_MIR_reflectance                    |
        +------------+-------------------------------------------------+
        |            | 250m_16_days_NIR_reflectance                    |
        +------------+-------------------------------------------------+
        |            | 250m_16_days_pixel_reliability                  |
        +------------+-------------------------------------------------+
        |            | 250m_16_days_red_reflectance                    |
        +------------+-------------------------------------------------+
        |            | 250m_16_days_relative_azimuth_angle             |
        +------------+-------------------------------------------------+
        |            | 250m_16_days_sun_zenith_angle                   |
        +------------+-------------------------------------------------+
        |            | 250m_16_days_view_zenith_angle                  |
        +------------+-------------------------------------------------+
        |            | 250m_16_days_VI_Quality                         |
        +------------+-------------------------------------------------+
        |            | 250m_16_days_NDVI                               |
        +------------+-------------------------------------------------+
        |            | 250m_16_days_EVI                                |
        +------------+-------------------------------------------------+
        |            | 250m_16_days_composite_day_of_the_year          |
        +------------+-------------------------------------------------+
        | MYD15A2    | FparExtra_QC                                    |
        +------------+-------------------------------------------------+
        |            | FparLai_QC                                      |
        +------------+-------------------------------------------------+
        |            | FparStdDev_1km                                  |
        +------------+-------------------------------------------------+
        |            | LaiStdDev_1km                                   |
        +------------+-------------------------------------------------+
        |            | Lai_1km                                         |
        +------------+-------------------------------------------------+
        |            | Fpar_1km                                        |
        +------------+-------------------------------------------------+

    startdate
        ISO 8601 formatted date string

    enddate
        ISO 8601 formatted date string

"""
    from tsgettoolbox.services import modis as placeholder

    r = resource(
        r'http://daacmodis.ornl.gov/cgi-bin/MODIS/GLBVIZ_1_Glb_subset/MODIS_webservice.wsdl',
        product=product,
        band=band,
        lat=lat,
        lon=lon,
        startdate=startdate,
        enddate=enddate)
    return tsutils.printiso(odo(r, pd.DataFrame))


def main():
    r"""Main function."""
    if not os.path.exists('debug_tsgettoolbox'):
        sys.tracebacklimit = 0
    mando.main()


if __name__ == '__main__':
    main()
