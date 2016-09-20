#!/usr/bin/env python
"""tsgettoolbox command line/library tools to retrieve time series.

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


@mando.command(formatter_class=HelpFormatter)
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
          bin=None,
         ):
    """
    Download from Center for Operational Oceanographic Products and Services.

    CO-OPS web services is at http://tidesandcurrents.noaa.gov/api/.
    The time zone of the returned data depends on the setting of the
    "time_zone" option.  The default is "GMT" also known as "UTC".

    :param station <str>:  A 7 character station ID, or a currents
        station ID.  Specify the station ID with the "station="
        parameter.::

            Example: '--station=9414290'

        Station listings for various products can be viewed at
        http://tidesandcurrents.noaa.gov or viewed on a map at Tides
        & Currents Station Map
    :param date <str>:  The API understands several parameters related
        to date ranges.  All dates can be formatted as follows::

            YyyyMMdd
            yyyyMMdd HH:mm
            MM/dd/yyyy
            MM/dd/yyyy HH:mm

        The date related options are 'begin_date',
        'end_date', 'date', and 'range'.  They can be
        combined in the following 5 ways, but if
        conflicting then follows the table in order.
        For example, the 'date' option will be used if
        present regardless of any other option, then
        'range', ...etc.:

        +--------------------+--------------------------------+
        | Parameter Name(s)  | Description                    |
        +====================+================================+
        | '--date'           | 'latest', 'today', or 'recent' |
        +--------------------+--------------------------------+
        | '--range'          | Specify a number of hours      |
        |                    | to go back from now and        |
        |                    | retrieve data for that date    |
        |                    | range                          |
        +--------------------+--------------------------------+
        | '--begin_date' and | Specify a begin date and       |
        | '--range'          | a number of hours to           |
        |                    | retrieve data starting from    |
        |                    | that date                      |
        +--------------------+--------------------------------+
        | '--begin_date' and | Specify the date/time range    |
        | '--end_date'       | of retrieval                   |
        +--------------------+--------------------------------+
        | '--end_date' and a | Specify an end date and        |
        | '--range'          | a number of hours to           |
        |                    | retrieve data ending at        |
        |                    | that date                      |
        +--------------------+--------------------------------+

        +-------------------+------------------------------+
        | Maximum Retrieval | Data Types                   |
        +===================+==============================+
        | 31 days           | All 6 minute data products   |
        +-------------------+------------------------------+
        | 1 year            | Hourly Height, and High/Low  |
        +-------------------+------------------------------+
        | 10 years          | Tide Predictions, Daily, and |
        |                   | Monthly Means                |
        +-------------------+------------------------------+

        +--------------------------------+-----------------+
        | Description of "--date" option | Option          |
        +================================+=================+
        | Today's data                   | --date='today'  |
        +--------------------------------+-----------------+
        | The last 3 days of data        | --date='recent' |
        +--------------------------------+-----------------+
        | The last data point            | --date='latest' |
        | available within the           |                 |
        | last 18 minutes.               |                 |
        +--------------------------------+-----------------+

    :param begin_date <str>:  The beginning date for the data.  See
        explanation with the 'date' option on how to use all of the date
        related parameters.
    :param end_date <str>:  The end date for the data.  January 1st,
        2012 through January 2nd, 2012::

            --begin_date='20120101' --end_date='20120102'

        See explanation with the 'date' option on how to use all of the
        date related parameters.
    :param range <int>:  Specify the number of hours to go back from
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
    :param product <str>:  Specify the data.

        +------------------------+----------------------------+
        | Option                 | Description                |
        +========================+============================+
        | water_level            | Preliminary or verified    |
        |                        | water levels, depending    |
        |                        | on availability.           |
        +------------------------+----------------------------+
        | air_temperature        | Air temperature            |
        +------------------------+----------------------------+
        | water_temperature      | Water temperature          |
        +------------------------+----------------------------+
        | wind                   | Wind speed, direction,     |
        |                        | and gusts                  |
        +------------------------+----------------------------+
        | air_gap                | (distance between          |
        |                        | a bridge and the water's   |
        |                        | surface)                   |
        +------------------------+----------------------------+
        | conductivity           | The water's conductivity   |
        +------------------------+----------------------------+
        | visibility             | Visibility from the        |
        |                        | station's visibility       |
        |                        | sensor. A measure of       |
        |                        | atmospheric clarity.       |
        +------------------------+----------------------------+
        | humidity               | Relative humidity          |
        +------------------------+----------------------------+
        | salinity               | Salinity and specific      |
        |                        | gravity                    |
        +------------------------+----------------------------+
        | hourly_height          | Verified hourly height     |
        |                        | water level data           |
        +------------------------+----------------------------+
        | high_low               | Verified high/low water    |
        |                        | level data                 |
        +------------------------+----------------------------+
        | daily_mean             | Verified daily mean        |
        |                        | water level data           |
        +------------------------+----------------------------+
        | monthly_mean           | Verified monthly mean      |
        |                        | water level data           |
        +------------------------+----------------------------+
        | one_minute_water_level | One minute water level     |
        |                        | data                       |
        +------------------------+----------------------------+
        | predictions            | 6 minute predictions       |
        |                        | water level data           |
        +------------------------+----------------------------+
        | datums                 | datums data                |
        +------------------------+----------------------------+
        | currents               | Currents data              |
        +------------------------+----------------------------+

    :param datum <str>:  Specify the datum that all water levels will be
        reported against.  Note! Datum is mandatory for all water level
        products.

        +---------+--------------------------------+
        | Option  | Description                    |
        +=========+================================+
        | MHHW    | Mean Higher High Water         |
        +---------+--------------------------------+
        | MHW     | Mean High Water                |
        +---------+--------------------------------+
        | MTL     | Mean Tide Level                |
        +---------+--------------------------------+
        | MSL     | Mean Sea Level                 |
        +---------+--------------------------------+
        | MLW     | Mean Low Water                 |
        +---------+--------------------------------+
        | MLLW    | Mean Lower Low Water           |
        +---------+--------------------------------+
        | NAVD    | North American Vertical Datum  |
        +---------+--------------------------------+
        | STND    | Station Datum                  |
        +---------+--------------------------------+

    :param units <str>:  Metric or english units.

        ======== ===========
        Option   Description
        ======== ===========
        metric   Metric (Celsius, meters) units
        english  English (Imperial system) (fahrenheit, feet) units
        ======== ===========

        The default is 'metric'.
    :param time_zone <str>:  The time zone is specified as 'gmt', 'lst'
        or 'lst_ldt'.

        +---------+------------------------------------------+
        | Option  | Description                              |
        +=========+==========================================+
        | gmt     | Greenwich Mean Time                      |
        +---------+------------------------------------------+
        | lst     | Local Standard Time. The time            |
        |         | local to the requested station.          |
        +---------+------------------------------------------+
        | lst_ldt | Local Standard/Local Daylight Time.      |
        |         | The time local to the requested station. |
        +---------+------------------------------------------+

    :param interval <str>:  Deliver the Meteorological data at hourly
        intervals.  Does not override 6 minute intervals for
        --product='water_level'.  Defaults to 'h'.
    :param bin <int>:  The bin number for the specified currents station
        Example:'--bin=4' Will retrieve data for bin number 4. Note! If
        a bin is not specified for a PORTS station, the data is returned
        using a predefined real-time bin.
    """
    from tsgettoolbox.services import coops as placeholder
    r = resource(
        r'http://tidesandcurrents.noaa.gov/api/datagetter',
        station=station,
        date=date,
        begin_date=begin_date,
        end_date=end_date,
        range=range,
        product=product,
        datum=datum,
        units=units,
        time_zone=time_zone,
        interval=interval,
        bin=bin,
        )
    return tsutils.printiso(odo(r, pd.DataFrame))


@mando.command(formatter_class=HelpFormatter)
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
         statYearType=None,
        ):
    """
    Download from the USGS National Water Information Service (NWIS).

    There are three main NWIS databases.  The 'tsgettoolbox' can
    currently pull from the Instantaneous Value database (--database-iv)
    for sub-daily interval data starting in 2007, the Daily Values
    database (--database=dv), or the Statistics database for
    daily/monthly/annual statistics.  Detailed documnetation is
    available at http://waterdata.usgs.gov/nwis.

    Site local time is output, even if multiple sites are requested and
    sites are in different time zones.  Note that the measurement time
    zone at a site may not be the same as the time zone actually in
    effect at the site.

    Every query requires a major filter. Pick the major filter
    ('--sites', '--stateCd', '--huc', '--bBox', '--countyCd') that best
    retrieves the data for the sites that you are interested in.  You
    can have only one major filter per query. If you specify more than
    one major filter, you will get an error.

    Major Filter
    ============
    Select one of::

        '--sites',
        '--stateCd',
        '--huc',
        '--bBox', or
        '--countyCd'

    Minor Filters
    =============
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

    :param sites <str>:  Want to only query one site? Use sites as your
        major filter, and put only one site number in the list.  Sites
        are comma separated. Sites may be prefixed with an optional
        agency code followed by a colon. If you don't know the site
        numbers you need, you can find relevant sites with the NWIS
        Mapper (http://wdr.water.usgs.gov/nwisgmap/index.html) or on the
        USGS Water Data for the Nation site.
        (http://waterdata.usgs.ogv/nwis/)

        Can have from 1 to 100 comma separated site numbers::

            --sites=USGS:01646500
            --sites=01646500,06306300

    :param stateCd <str>:  U.S. postal service (2-digit) state code.
        Can have only 1 state code.  List is available at
        http://www.usps.com/ncsc/lookups/usps_abbreviations.html::

            --stateCd=NY

    :param huc <str>:  A list of hydrologic unit codes (HUC) or
        watersheds.  Only 1 major HUC can be specified per request.
        A major HUC has two digits. Minor HUCs must be eight digits in
        length.  Can have 1 to 10 HUC codes.  List of HUCs is available
        at http://water.usgs.gov/GIS/huc_name.html::

            --huc=01,02070010

    :param bBox <str>:  A contiguous range of decimal latitude and
        longitude, starting with the west longitude, then the south
        latitude, then the east longitude, and then the north latitude
        with each value separated by a comma. The product of the range
        of latitude and longitude cannot exceed 25 degrees. Whole or
        decimal degrees must be specified, up to six digits of
        precision. Minutes and seconds are not allowed. Remember:
        western longitude (which includes almost all of the United
        States) is specified in negative degrees. Caution: many sites
        outside the continental US do not have latitude and longitude
        referenced to NAD83 and therefore can not be found using these
        arguments. Certain sites are not associated with latitude and
        longitude due to homeland security concerns and cannot be found
        using this filter.::

            --bBox=-83,36.5,-81,38.5

    :param countyCd <str>:  A list of county numbers, in a 5 digit
        numeric format. The first two digits of a county's code are the
        FIPS State Code.  Can have from 1 to 20 county codes.  The first
        2 digits are the FIPS State Code
        (http://www.itl.nist.gov/fipspubs/fip5-2.htm) and the list of
        county codes are at
        http://help.waterdata.usgs.gov/code/county_query?fmt=html::

            --countyCd=51059,51061

    :param parameterCd <str>:  USGS time-series parameter code.  All
        parameter codes are numeric and 5 characters in length.
        Parameter codes are used to identify the constituent measured
        and the units of measure.  Popular codes include stage (00065),
        discharge in cubic feet per second (00060) and water temperature
        in degrees Celsius (00010). Can have from 1 to 100.  Default:
        returns all regular time-series for the requested sites.
        Complete list:
        http://help.waterdata.usgs.gov/codes-and-parameters/parameters::

            --parameterCd=00060       # discharge, cubic feet
                                      # per second
            --parameterCd=00060,00065 # discharge,
                                      # cubic feet per second
                                      # and gage height in
                                      # feet

    :param siteType <str>:  Restricts sites to those having one or more
        major and/or minor site types.  If you request a major site type
        (ex: &siteType=ST) you will get all sub-site types of the same
        major type as well (in this case, ST-CA, ST-DCH and ST-TS).  Can
        have from 1 to an unlimited number of siteType codes.  Default
        is to return all types.  List of valid site types:
        http://help.waterdata.usgs.gov/site_tp_cd::

            --siteType=ST       # Streams only
            --siteType=ST,LA-OU # Streams and Land Outcrops only

    :param modifiedSince <str>:  Returns all values for sites and period
        of record requested only if any values have changed over the
        last modifiedSince period.  modifiedSince is useful if you
        periodically need to poll a site but are only interested in
        getting data if some of it has changed.  It is typically be used
        with period, or startDT/endDT but does not have to be. In the
        latter case, if any values were changed during the specified
        modifiedSince period, only the most recent values would be
        retrieved for those sites. This is a typical usage, since users
        typically are polling a site and only want data if there are new
        or changed measurements.  ISO-8601 duration format is always
        used.  There is no default.
        (http://en.wikipedia.org/wiki/ISO_8601#Durations)::

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

    :param agencyCd <str>:  The list of sites returned are filtered to
        return only those with the provided agency code. The agency code
        describes the organization that maintains the site. Only one
        agency code is allowed and is optional.  An authoritative list
        of agency codes can be found here.  Default is to return all
        sites regardless of agency code.  List:
        http://help.waterdata.usgs.gov/code/agency_cd_query?fmt=html::

            --stateCd=il --agencyCd=USCE # Only US Army Corps
                                         # of Engineers sites
                                         # in Illinois

    :param siteStatus <str>:  Selects sites based on whether or not they
        are active. If a site is active, it implies that it is being
        actively maintained. A site is considered active if: * it has
        collected time-series (automated) data within the last 183 days
        (6 months), or * it has collected discrete (manually collected)
        data within 397 days (13 months) If it does not meet these
        criteria, it is considered inactive. Some exceptions apply. If
        a site is flagged by a USGS water science center as
        discontinued, it will show as inactive. A USGS science center
        can also flag a new site as active even if it has not collected
        any data.  The default is all (show both active and inactive
        sites).  Chose between, 'all', 'active', or 'inactive'.  Default
        all - sites of any activity status are returned.::

            --siteStatus='active'

    :param altMin <float>:  These arguments allows you to select
        instantaneous values sites where the associated sites' altitude
        are within a desired altitude, expressed in feet.  Altitude is
        based on the datum used at the site.  Providing a value to
        altMin (minimum altitude) means you want sites that have or
        exceed the altMin value.  You may specify decimal feet if
        precision is critical If both the altMin and altMax are
        specified, sites at or between the minimum and maximum altitude
        are returned.
    :param altMax <float>:  Providing a value to altMax (maximum
        altitude) means you want sites that have or are less than the
        altMax value.::

            --altMin=1000 --altMax=5000 # Return sites where
                                        # the altitude is
                                        # 1000 feet or
                                        # greater and 5000
                                        # feet or less.
            --altMin=12.5 --altMax=13 # Return sites where the
                                      # altitude is 12.5 feet
                                      # or greater and 13 feet
                                      # or less.

    :param drainAreaMin <float>:  These arguments allows you to select
        principally surface water sites where the associated sites'
        drainage areas (watersheds) are within a desired size, expressed
        in square miles or decimal fractions thereof.  Providing a value
        to drainAreaMin (minimum drainage area) means you want sites
        that have or exceed the drainAreaMin value.  The values may be
        expressed in decimals. If both the drainAreaMin and drainAreaMax
        are specified, sites at or between the minimum and maximum
        drainage areas values specified are returned Caution: not all
        sites are associated with a drainage area.  Caution: drainage
        area generally only applies to surface water sites.  Use with
        other site types, such as groundwater sites, will likely
        retrieve no results.
    :param drainAreaMax <float>:  Providing a value to drainAreaMax
        (maximum drainage area) means you want sites that have or are
        less than the drainAreaMax value.::

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

    :param aquiferCd <str>:  Used to filter sites to those that exist in
        specified national aquifers. Note: not all sites have been
        associated with national aquifers.  Enter one or more national
        aquifer codes, separated by commas.  A national aquifer code is
        exactly 10 characters.  You can have up to 1000 aquiferCd codes.
        Complete list:
        http://water.usgs.gov/ogw/NatlAqCode-reflist.html::

            --aquiferCd=S500EDRTRN,N100HGHPLN
                                  # returns groundwater sites
                                  # for the Edwards-Trinity
                                  # aquifer system and the
                                  # High Plains national
                                  # aquifers.

    :param localAquiferCd <str>:  Used to filter sites to those that
        exist in specified local aquifers.  Note: not all sites have
        been associated with local aquifers.  Enter one or more local
        aquifer codes, separated by commas.  A local aquifer code begins
        with a 2 character state abbreviation (such as TX for Texas)
        followed by a colon followed by the 7 character aquifer code.
        Can have 0 to 1000 comma delimited codes.  Complete list:
        http://help.waterdata.usgs.gov/code/aqfr_cd_query?fmt=html To
        translate state codes associated with the local aquifer you may
        need this reference: http://www.itl.nist.gov/fipspubs/fip5-2.htm

            --localAquiferCd=AL:111RGLT,AL:111RSDM
                    # returns sites for the Regolith and
                    # Saprolite local aquifers in Alabama

    :param wellDepthMin <float>:  These arguments allows you to select
        groundwater sites serving data recorded automatically where the
        associated sites' well depth are within a desired depth,
        expressed in feet from the land surface datum.  Express well
        depth as a positive number.  Providing a value to wellDepthMin
        (minimum well depth) means you want sites that have or exceed
        the wellDepthMin value.  The values may be expressed in decimals
        If both the wellDepthMin and wellDepthMax are specified, sites
        at or between the minimum and maximum well depth values
        specified are returned wellDepthMax should be greater than or
        equal to wellDepthMin.  Caution: well depth applies to
        groundwater sites only
    :param wellDepthMax <float>:  Providing a value to wellDepthMax
        (maximum well depth) means you want sites that have or are less
        than the wellDepthMax value.::

             --wellDepthMin=100 --wellDepthMax=500
                     # Return daily value sites where the well
                     # depth is 100 feet or greater and 500
                     # feet or less.
             --wellDepthMin=10.5 --wellDepthMax=10.7
                     # Return daily value sites where the well
                     # depth is 10.5 feet or greater and 10.7
                     # feet or less.

    :param holeDepthMin <float>:  These arguments allows you to select
        groundwater sites serving data recorded automatically where the
        associated sites' hole depth are within a desired depth,
        expressed in feet from the land surface datum.  Express hole
        depth as a positive number.  Providing a value to holeDepthMin
        (minimum hole depth) means you want sites that have or exceed
        the holeDepthMin value.  The values may be expressed in decimals
        If both the holeDepthMin and holeDepthMax are specified, sites
        at or between the minimum and maximum hole depth values
        specified are returned holeDepthMax should be greater than or
        equal to holeDepthMin.  Caution: hole depth applies to
        groundwater sites only.
    :param holeDepthMax <float>:  Providing a value to holeDepthMax
        (maximum hole depth) means you want sites that have or are less
        than the holeDepthMax value.::

            --holeDepthMin=100 --holeDepthMax=500
                    # Return daily values sites where the
                    # hole depth is 100 feet or greater and
                    # 500 feet or less.
            --holeDepthMin=10.5 --holeDepthMax=10.7
                    # Return daily value sites where the hole
                    # depth is 10.5 feet or greater and 10.7
                    # feet or less.

    :param period <str>:  Get a range of values from now by specifying
        the period argument period must be in ISO-8601 Duration format.
        (http://en.wikipedia.org/wiki/ISO_8601#Durations) Negative
        periods (ex: P-T2H) are not allowed Data are always returned up
        to the most recent value, which in the case of a predictive gage
        might be in the future.  When specifying days from now, the
        first value will probably not be at midnight of the first day,
        but somewhat before exactly 24 hours from now.::

            --period=PT2H # Retrieve last two hours from now
                          # up to most recent
                             # instantaneous value)
            --period=P7D # Retrieve last seven days up from
                         # now to most recent instantaneous
                         # value)

    :param startDT <str>:  Get a range of values from an explicit begin
        or end date/time   Use the startDT and endDT arguments.  Site
        local time is output, even if multiple sites are requested and
        sites are in different time zones.  Note that the measurement
        time zone at a site may not be the same as the time zone
        actually in effect at the site.

        Both startDt and endDt must be in ISO-8601 Date/Time format.
        (http://en.wikipedia.org/wiki/ISO_8601#Dates) You can express
        the date and time in a timezone other than site local time if
        you want as long as it follows the ISO standard. For example,
        you can express the time in Universal time: 2014-03-20T00:00Z.
        If startDT is supplied and endDT is not, endDT ends with the
        most recent instantaneous value. startDT must be chronologically
        before endDT.

        If startDt shows the date and not the time of day (ex:
        2010-09-01) the time of midnight site time is assumed
        (2010-09-01T00:00) If endDt shows the date and not the time of
        day (ex: 2010-09-02) the last minute before midnight site time
        is assumed (2010-09-02T23:59).  Remember, only data from October
        1, 2007 are currently available.
    :param endDT <str>:  If endDT is present, startDt must also be
        present.::

            --startDT=2010-11-22 --endDT=2010-11-22 # Full day,
                                                    # from
                                                    # 00:00 to
                                                    # 23:59
            --startDT=2010-11-22T12:00 --endDT=2010-11-22T18:00
            --startDT=2010-11-22 --endDT=2010-11-22
            --startDT=2010-11-22T12:00 # Ends with most recent
                                       # instantaneous value
    :param database <str>:  One of 'iv' for instantaneous values, 'dv'
        for daily values, or 'stat' for daily/monthly/annual statistics.
        Default is 'dv'.
    :param statReportType <str>:  The type of statistics desired. Valid
        statistic report types include::

            daily - daily statistics (default)
                    statistic across years
            monthly - monthly statistics (monthly time-series)
            annual - annual statistics, based on either
                     calendar year or water year, as defined
                     by statYearType. If statYearType is not
                     provided, calendar year statistics are
                     assumed. (annual time-series)

        Default is 'daily'.
    :param statType <str>:  Selects sites based on the statistics
        type(s) desired, such as minimum, maximum or mean

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

    :param missingData <str>:  Used to indicate the rules to follow to
        generate statistics if there are gaps in the period of record
        during the requested statistics period. By default if there are
        any missing data for the report type, the statistic is left
        blank or null.

        This option does not apply to daily statistics, but optionally
        can be used with monthly and yearly statistics. If used with
        daily statistics, an error will occur.

        Missing data can happen for various reasons including there was
        a technical problem with the gage for part of the time period.

        Enabling this switch will attempt to provide a statistic if
        there is enough data to create one.

        Choice is 'off' or 'on'.
    :param statYearType <str>:  Indicates which kind of year statistics
        should be created against. This only applies when requesting
        annual statistics, i.e. statReportType=annual. Valid year types
        codes include::

            calendar - calendar year, i.e. January 1 through
                       December 31
            water - water year, i.e. a year begins October 1 of
                    the previous year and ends September 30 of
                    the current year. This is the same as
                    a federal fiscal year.
    """
    from tsgettoolbox.services import nwis as placeholder
    if database not in ['iv', 'dv', 'stat']:
        raise ValueError("""
*
*   The 'database' option must be either 'iv' for instantaneous values, and
*   'dv' for daily values, or 'stat' for daily, monthly, or annual statistics.
*   You gave {0}.
*
""".format(database))
    r = resource(
        r'http://waterservices.usgs.gov/nwis/{0}/'.format(database),
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
        statYearType=statYearType,
        )

    return tsutils.printiso(odo(r, pd.DataFrame))


@mando.command(formatter_class=HelpFormatter)
def ghcnd(station,
          start_date=None,
          end_date=None,
         ):
    """
    Download from the Global Historical Climatology Network - Daily.

    If you use this data, please read
    ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt about "How to cite".

    GHCN (Global Historical Climatology Network)-Daily is an integrated
    database of daily climate summaries from land surface stations across the
    globe. Like its monthly counterpart (GHCN-Monthly) , GHCN-Daily is
    comprised of daily climate records from numerous sources that have been
    integrated and subjected to a common suite of quality assurance reviews.

    GHCN-Daily now contains records from over 75000 stations in 180 countries
    and territories. Numerous daily variables are provided, including maximum
    and minimum temperature, total daily precipitation, snowfall, and snow
    depth; however, about two thirds of the stations report precipitation only.
    Both the record length and period of record vary by station and cover
    intervals ranging from less than year to more than 175 years.

    The dataset is regularly reconstructed (usually every weekend) from its
    20-plus data source components to ensure that GHCN-Daily is generally in
    sync with its growing list of constituent sources. During this process,
    quality assurance checks are applied to the full dataset. On most weekdays,
    GHCN-Daily station data are updated when possible from a variety of data
    streams, which also undergo a suite of quality checks.

    Some of the data provided here are based on data exchanged under the World
    Meteorological Organization (WMO) World Weather Watch Program according to
    WMO Resolution 40 (Cg-XII). This allows WMO member countries to place
    restrictions on the use or re-export of their data for commercial purposes
    outside of the receiving country. Those countries' data summaries and
    products which are available here are intended for free and unrestricted
    use in research, education, and other non-commercial activities. For
    non-U.S. locations' data, the data or any derived product shall not be
    provided to other users or be used for the re-export of commercial
    services.

    :param station <str>: The station id. from the first column of
        ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt
    :param start_date <str>:  The start date of the time series.::

            Example: --start_date=2001-01-01

        If start_date and end_date are None, returns the entire series.
    :param end_date <str>:  The end date of the time series.::

            Example: --end_date=2001-01-05

        If start_date and end_date are None, returns the entire series.
    """
    from tsgettoolbox.services import ghcnd as placeholder
    r = resource(
        r'ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/all',
        station=station,
        start_date=start_date,
        end_date=end_date,
        )
    return tsutils.printiso(odo(r, pd.DataFrame))


@mando.command(formatter_class=HelpFormatter)
def daymet(lat,
           lon,
           measuredParams=None,
           year=None,
          ):
    """
    Download data from Daymet created by the Oak Ridge National Laboratory.

    Detailed documentation is at http://daymet.ornl.gov/.  Since this is
    daily data, it covers midnight to midnight based on local time.

    :param lat <float>: Latitude (required): Enter single geographic
        point by latitude, value between 52.0N and 14.5N.::

            Example: --lat=43.1
    :param lon <float>: Longitude (required): Enter single geographic
        point by longitude, value between -131.0W and -53.0W.::

            Example: --lon=-85.3
    :param measuredParams <str>:  CommaSeparatedVariables (optional):
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
    :param year <str>:  CommaSeparatedYears (optional): Current Daymet
        product (version 2) is available from 1980 to the latest full
        calendar year.::

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


@mando.command(formatter_class=HelpFormatter)
def ldas(lat=None,
         lon=None,
         xindex=None,
         yindex=None,
         variable=None,
         startDate=None,
         endDate=None,
        ):
    """
    Download data from NLDAS or GLDAS.

    The time zone is always UTC.

    :param lat <float>:  Either 'lat' and 'lon', or 'xindex' and
        'yindex' is required.

        Latitude (required): Enter single geographic point by
        latitude.::

            Example: --lat=43.1
    :param lon <float>:  Either 'lat' and 'lon', or 'xindex' and
        'yindex' is required.  Longitude (required): Enter single
        geographic point by longitude::

            Example: --lon=-85.3
    :param xindex <int>:  Either 'lat' and 'lon', or 'xindex' and
        'yindex' is required.  xindex (required if using xindex/yindex):
        Enter the x index of the NLDAS or GLDAS grid.::

            Example: --xindex=301
    :param yindex <int>:  Either 'lat' and 'lon', or 'xindex' and
        'yindex' is required.
     yindex (required if using xindex/yindex): Enter the y index of the
        NLDAS or GLDAS grid.::

            Example: --yindex=80
    :param variable <str>:  Use the variable codes from the following table:

        NLDAS:NLDAS_FORA0125_H.002:APCPsfc
            Precipitation hourly total                 kg/m^2

        NLDAS:NLDAS_FORA0125_H.002:DLWRFsfc
            Surface DW longwave radiation flux         W/m^2

        NLDAS:NLDAS_FORA0125_H.002:DSWRFsfc
            Surface DW shortwave radiation flux        W/m^2

        NLDAS:NLDAS_FORA0125_H.002:PEVAPsfc
            Potential evaporation                      kg/m^2

        NLDAS:NLDAS_FORA0125_H.002:SPFH2m
            2-m above ground specific humidity         kg/kg

        NLDAS:NLDAS_FORA0125_H.002:TMP2m
            2-m above ground temperature               K

        NLDAS:NLDAS_FORA0125_H.002:UGRD10m
            10-m above ground zonal wind               m/s

        NLDAS:NLDAS_FORA0125_H.002:VGRD10m
            10-m above ground meridional wind          m/s

        NLDAS:NLDAS_NOAH0125_H.002:EVPsfc
            Total evapotranspiration                   kg/m^2

        NLDAS:NLDAS_NOAH0125_H.002:GFLUXsfc
            Ground heat flux                           w/m^2

        NLDAS:NLDAS_NOAH0125_H.002:LHTFLsfc
            Latent heat flux                           w/m^2

        NLDAS:NLDAS_NOAH0125_H.002:SHTFLsfc
            Sensible heat flux                         w/m^2

        NLDAS:NLDAS_NOAH0125_H.002:SSRUNsfc
            Surface runoff (non-infiltrating)          kg/m^2

        NLDAS:NLDAS_NOAH0125_H.002:BGRIUNdfc
            Subsurface runoff (baseflow)               kg/m^2

        NLDAS:NLDAS_NOAH0125_H.002:SOILM0-10cm
            0-10 cm soil moisture content              kg/m^2

        NLDAS:NLDAS_NOAH0125_H.002:SOILM0-100cm
            0-100 cm soil moisture content             kg/m^2

        NLDAS:NLDAS_NOAH0125_H.002:SOILM0-200cm
            0-200 cm soil moisture content             kg/m^2

        NLDAS:NLDAS_NOAH0125_H.002:SOILM10-40cm
            10-40 cm soil moisture content             kg/m^2

        NLDAS:NLDAS_NOAH0125_H.002:SOILM40-100cm
            40-100 cm soil moisture content            kg/m^2

        NLDAS:NLDAS_NOAH0125_H.002:SOILM100-200cm
            100-200 cm soil moisture content           kg/m^2

        NLDAS:NLDAS_NOAH0125_H.002:TSOIL0-10cm
            0-10 cm soil temperature                   K

        GLDAS:GLDAS_NOAH025_3H.001:Evap
            Evapotranspiration                         kg/m^2/s

        GLDAS:GLDAS_NOAH025_3H.001:precip
            Precipitation rate                         kg/m^s/hr

        GLDAS:GLDAS_NOAH025_3H.001:Rainf
            Rain rate                                  kg/m^2/s

        GLDAS:GLDAS_NOAH025_3H.001:Snowf
            Snow rate                                  kg/m^2/s

        GLDAS:GLDAS_NOAH025_3H.001:Qs
            Surface Runoff                             kg/m^2/s

        GLDAS:GLDAS_NOAH025_3H.001:Qsb
            Subsurface Runoff                          kg/m^2/s

        GLDAS:GLDAS_NOAH025_3H.001:SOILM0-100cm
            0-100 cm top 1 meter soil moisture content kg/m^2

        GLDAS:GLDAS_NOAH025_3H.001:SOILM0-10cm
            0-10 cm layer 1 soil moisture content      kg/m^2

        GLDAS:GLDAS_NOAH025_3H.001:SOILM10-40cm
            10-40 cm layer 2 soil moisture content     kg/m^2

        GLDAS:GLDAS_NOAH025_3H.001:SOILM40-100cm
            40-100 cm layer 3 soil moisture content    kg/m^2

        GLDAS:GLDAS_NOAH025_3H.001:Tair
            Near surface air temperature               K

        GLDAS:GLDAS_NOAH025_3H.001:TSOIL0-10cm
            Average layer 1 soil temperature           K

        GLDAS:GLDAS_NOAH025_3H.001:Wind
            Near surface wind magnitude                m/s

    :param startDate <str>:  The start date of the time series.::

            Example: --startDate=2001-01-01T05

        If startDate and endDate are None, returns the entire series.
    :param endDate <str>:  The end date of the time series.::

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
        r'http://hydro1.sci.gsfc.nasa.gov/daac-bin/access/timeseries.cgi',
        variable=variable,
        location=location,
        startDate=startDate,
        endDate=endDate,
        )
    return tsutils.printiso(odo(r, pd.DataFrame))


@mando.command(formatter_class=HelpFormatter)
def forecast_io(latitude,
                longitude,
                time=None,
                database='hourly',
                extend=None,
                units='us',
                lang='en'
               ):
    """
    Download data from http://forecast.io.

    Detailed documentation about the Forecast.io service is at
    https://developer.forecast.io/docs/v2 You have to get an API key
    from https://developer.forecast.io/.

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

    Only defined for 'currently' data
    ---------------------------------
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

    Only defined for 'daily' data
    -----------------------------
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

    Only defined for 'hourly' and 'daily' data
    ------------------------------------------
    precipAccumulation::

     The amount of snowfall accumulation expected to occur on the given
     day, in inches. (If no accumulation is expected, this property
     will not be defined.)

    Defined for every dataset except 'daily'
    ----------------------------------------
    apparentTemperature::

     A numerical value representing the apparent (or 'feels like')
     temperature at the given time in degrees Fahrenheit.

    temperature::

     A numerical value representing the temperature at the given time
     in degrees Fahrenheit.

    :param latitude <float>:  Latitude (required): Enter single
        geographic point by latitude.::

            Example: --latitude=43.1
    :param longitude <float>:  Longitude (required): Enter single
        geographic point by longitude::

            Example: --longitude=-85.3
    :param time <str>:  TIME should either be a UNIX time (that is,
        seconds since midnight GMT on 1 Jan 1970) or a string formatted
        as follows: [YYYY]-[MM]-[DD]T[HH]:[MM]:[SS] (with an optional
        time zone formatted as Z for GMT time or {+,-}[HH][MM] for an
        offset in hours or minutes). For the latter format, if no
        timezone is present, local time (at the provided latitude and
        longitude) is assumed.  (This string format is a subset of ISO
        8601 time. An as example, 2013-05-06T12:00:00-0400.)

        The default is None, which uses the current time.
    :param database <str>:  The database to draw the data from.  This is
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
    :param extend <str>:   If set to 'hourly' and --database='hourly'
        then will get an hourly forecast for the next week.
    :param units <str>:  Specify the units for the data.

        +-----------------------+---------------------------+
        | Option                | Description               |
        +=======================+===========================+
        | us (default)          | Imperial units            |
        +-----------------------+---------------------------+
        | si                    | SI units                  |
        +-----------------------+---------------------------+
        | ca                    | Identical to SI           |
        |                       | except windSpeed          |
        |                       | is in km/hr               |
        +-----------------------+---------------------------+
        | uk (deprecated)       |                           |
        +-----------------------+---------------------------+
        | uk2                   | Identical to SI           |
        |                       | except windSpeed          |
        |                       | is in miles/hr and        |
        |                       | nearestStormDistance      |
        |                       | and visibility are        |
        |                       | in miles                  |
        +-----------------------+---------------------------+
        | auto                  | Selects the relevant      |
        |                       | units automatically       |
        |                       | according to location     |
        +-----------------------+---------------------------+

    :param lang <str>:  Return text summaries in the desired language.
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
    from tsgettoolbox.services import forecast_io as placeholder
    r = resource(
        r'https://api.forecast.io/forecast',
        latitude=latitude,
        longitude=longitude,
        database=database,
        time=time,
        extend=extend,
        units=units,
        lang=lang,
        )
    return tsutils.printiso(odo(r, pd.DataFrame))


@mando.command(formatter_class=HelpFormatter)
def unavco(station,
           database='met',
           starttime=None,
           endtime=None,
          ):
    """
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
       C), relative humidity(%), wind direction(degrees), wind
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

    :param station <str>:  Unavco station identifier
    :param database <met>:  Database to pull from.  One of 'met',
        'pore_temperature', 'pore_pressure', 'tilt', 'strain'.  The
        default is 'met'.
    :param starttime <str>:  Start date in ISO8601 format.
    :param endtime <str>:  End date in ISO8601 format.
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


def main():
    """Main function."""
    if not os.path.exists('debug_tsgettoolbox'):
        sys.tracebacklimit = 0
    mando.main()

if __name__ == '__main__':
    main()
