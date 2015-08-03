#!/sjr/beodata/local/python_linux/bin/python
'''
tsgettoolbox is a collection of command line tools to retrieve time series.
'''

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys
import os.path
import warnings
from argparse import RawTextHelpFormatter
warnings.filterwarnings('ignore')

from odo import odo, resource
import pandas as pd
import mando

from tstoolbox import tsutils

@mando.command(formatter_class=RawTextHelpFormatter)
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
    '''
    Download data from Center for Operational Oceanographic Products and
    Services (CO-OPS).  Detailed documentation about the National Ocean Service
    CO-OPS web services is at http://tidesandcurrents.noaa.gov/api/

    The API understands several parameters related to date ranges.
    All dates can be formatted as follows:
    YyyyMMdd, yyyyMMdd HH:mm, MM/dd/yyyy, or MM/dd/yyyy HH:mm

    The date related options are 'begin_date', 'end_date', 'date', and 'range'.
    They can be combined in the following 5 ways, but if conflicting then
    follows the table in order.  For example, the 'date' option will be used if
    present regardless of any other option, then 'range', ...etc.:

    |Parameter Name(s)  |Description
    |-------------------|-----------
    |'--date'           |'latest', 'today', or 'recent'.
    |'--range'          |Specify a number of hours to go
    |                   |back from now and retrieve data
    |                   |for that date range
    |'--begin_date' and |Specify a begin date and a number
    |     '--range'     |of hours to retrieve data starting
    |                   |from that date
    |'--begin_date' and |Specify the date/time range of
    |     '--end_date'  |retrieval
    |'--end_date' and a |Specify an end date and a number
    |     '--range'     |of hours to retrieve data ending
    |                   |at that date


    |Maximum Retrieval Time|Data Types
    |----------------------|----------
    |31 days               |All 6 minute data products
    |1 year                |Hourly Height, and High/Low
    |10 years              |Tide Predictions, Daily, and
    |                      |Monthly Means

    :param station <str>: A 7 character station ID, or a currents station ID.
        Specify the station ID with the "station=" parameter.
            Example: '--station=9414290'
        Station listings for various products can be viewed at
        http://tidesandcurrents.noaa.gov or viewed on a map at Tides & Currents
        Station Map
    :param date <str>:
        See explanation above how to use the all or the date related
        parameters.
        'latest': last data point available within the last 18 min,
        'today': data collected today, or
        'recent': data collected in last 72 hours)

        Today's data
            --date='today'
        The last 3 days of data
            --date='recent'
        The last data point available within the last 18 min
            --date='latest'
    :param begin_date <str>:
        See explanation above how to use the all or the date related
        parameters.
        The beginning date for the data.
    :param end_date <str>:
        See explanation above how to use the all or the date related
        parameters.
        The end date for the data.

        January 1st, 2012 through January 2nd, 2012
            --begin_date='20120101' --end_date='20120102'

    :param range <int>:
        See explanation above how to use the all or the date related
        parameters.
        Specify the number of hours to go back from now, an 'end_date', or
        forward from a 'begin_date'.

        48 hours beginning on April 15, 2012
            --begin_date='20120415' --range=48
        48 hours ending on March 17, 2012
            --end_date='20120307' --range=48
        The last 24 hours from now
            --range=24
        The last 3 hours from now
            --range=3

    :param product <str>:
        Specify the data.

        |Option                |Description
        |----------------------|-----------
        |water_level           |Preliminary or verified water
        |                      |levels, depending on
        |                      |availability.
        |air_temperature       |Air temperature
        |water_temperature     |Water temperature
        |wind                  |Wind speed, direction, and
        |                      |gusts
        |air_pressure          |Barometric pressure
        |air_gap               |(distance between a bridge
        |                      |and the water's surface)
        |conductivity          |The water's conductivity
        |visibility            |Visibility from the station's
        |                      |visibility sensor. A measure
        |                      |of atmospheric clarity.
        |humidity              |Relative humidity
        |salinity              |Salinity and specific gravity
        |hourly_height         |Verified hourly height water
        |                      |level data
        |high_low              |Verified high/low water level
        |                      |data
        |daily_mean            |Verified daily mean water
        |                      |level data
        |monthly_mean          |Verified monthly mean water
        |                      |level data
        |one_minute_water_level|One minute water level data
        |predictions           |6 minute predictions water
        |                      |level data
        |datums                |datums data
        |currents              |Currents data
    :param datum <str>:
        Specify the datum that all water levels will be reported against.
        Note! Datum is mandatory for all water level products.

        |Option |Description
        |-------|-----------
        |MHHW   |Mean Higher High Water
        |MHW    |Mean High Water
        |MTL    |Mean Tide Level
        |MSL    |Mean Sea Level
        |MLW    |Mean Low Water
        |MLLW   |Mean Lower Low Water
        |NAVD   |North American Vertical Datum
        |STND   |Station Datum
    :param units <str>:
        Metric or english units.

        |Option  |Description
        |--------|-----------
        |metric  |Metric (Celsius, meters) units
        |english |English (Imperial system) (fahrenheit, feet) units

        The default is 'metric'.
    :param time_zone <str>:
        The time zone is specified as 'gmt', 'lst' or 'lst_ldt'.

        |Option |Description
        |-------|-----------
        |gmt    |Greenwich Mean Time
        |lst    |Local Standard Time. The time
        |       |local to the requested station.
        |lst_ldt|Local Standard/Local Daylight Time.
        |       |The time local to the requested station.
    :param interval <str>:
        Deliver the Meteorological data at hourly intervals.  Does not
        override 6 minute intervals for --product='water_level'.  Defaults
        to 'h'.
    :param bin <int>:
        The bin number for the specified currents station
        Example:'--bin=4' Will retrieve data for bin number 4
        Note! If a bin is not specified for a PORTS station, the data is
        returned using a predefined real-time bin.
    '''
    from tsgettoolbox.services import coops
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


@mando.command(formatter_class=RawTextHelpFormatter)
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
         ):
    '''
    Download time-series from the USGS National Water Information Service
    (NWIS).  There are three main NWIS databases.  The 'tsgettoolbox' can
    currently pull from the Instantaneous Value database (--database-iv) for
    sub-daily interval data starting in 2007, and the Daily Values database
    (--database=dv).  Detailed documnetation is available at
    http://waterdata.usgs.gov/nwis

    Every query requires a major filter. Pick the major filter ('--sites',
    '--stateCd', '--huc', '--bBox', '--countyCd') that best retrieves the data
    for the sites that you are interested in.  You can have only one major
    filter per query. If you specify more than one major filter, you will get
    an error.

    Major Filter
    Select one of
    '--sites', '--stateCd', '--huc', '--bBox', or '--countyCd'.

    Minor Filters
    Additional filters can be applied after specifying a major filter. This
    further reduces the set of expected results. Users are encouraged to use
    minor filters because it allows more efficient use of this service.
    '--parameterCd', '--siteType', '--modifiedSince', '--agencyCd',
    '--siteStatus', '--altMin', '--altMax', '--drainAreaMin', '--drainAreaMax',
    '--aquiferCd', '--localAquiferCd', '--wellDepthMin', '--wellDepthMax',
    '--holeDepthMin', '--holeDepthMax'

    :param sites <str>:
        Want to only query one site? Use sites as your major filter, and put
        only one site number in the list.  Sites are comma separated. Sites may
        be prefixed with an optional agency code followed by a colon. If you
        don't know the site numbers you need, you can find relevant sites with
        the NWIS Mapper (http://wdr.water.usgs.gov/nwisgmap/index.html) or on
        the USGS Water Data for the Nation site.
        (http://waterdata.usgs.ogv/nwis/)

        Can have from 1 to 100 comma separated site numbers.
            --sites=USGS:01646500
            --sites=01646500,06306300
    :param stateCd <str>:
        U.S. postal service (2-digit) state code.  Can have only 1 state code.
        List is available at
        http://www.usps.com/ncsc/lookups/usps_abbreviations.html
            --stateCd=NY
    :param huc <str>:
        A list of hydrologic unit codes (HUC) or watersheds. Only 1 major HUC
        can be specified per request. A major HUC has two digits. Minor HUCs
        must be eight digits in length.  Can have 1 to 10 HUC codes.  List of
        HUCs is available at http://water.usgs.gov/GIS/huc_name.html
            --huc=01,02070010
    :param bBox <str>:
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
        cannot be found using this filter.
            --bBox=-83,36.5,-81,38.5
    :param countyCd <str>:
        A list of county numbers, in a 5 digit numeric format. The first two
        digits of a county's code are the FIPS State Code.
        Can have from 1 to 20 county codes.  The first 2 digits are the FIPS
        State Code (http://www.itl.nist.gov/fipspubs/fip5-2.htm) and the list
        of county codes are at
        http://help.waterdata.usgs.gov/code/county_query?fmt=html
            --countyCd=51059,51061
    :param parameterCd <str>:
        USGS time-series parameter code.  All parameter codes are numeric and 5
        characters in length. Parameter codes are used to identify the
        constituent measured and the units of measure.  Popular codes include
        stage (00065), discharge in cubic feet per second (00060) and water
        temperature in degrees Celsius (00010). Can have from 1 to 100.
        Default: returns all regular time-series for the requested sites.
        Complete list:
        http://help.waterdata.usgs.gov/codes-and-parameters/parameters
            --parameterCd=00060       # discharge, cubic feet per second
            --parameterCd=00060,00065 # discharge, cubic feet per second and
                                      #            gage height in feet
    :param siteType <str>:
        Restricts sites to those having one or more major and/or minor site
        types.  If you request a major site type (ex: &siteType=ST) you will
        get all sub-site types of the same major type as well (in this case,
        ST-CA, ST-DCH and ST-TS).  Can have from 1 to an unlimited number of
        siteType codes.  Default is to return all types.
        List of valid site types: http://help.waterdata.usgs.gov/site_tp_cd
            --siteType=ST       # Streams only
            --siteType=ST,LA-OU # Streams and Land Outcrops only
    :param modifiedSince <str>:
        Returns all values for sites and period of record requested only if any
        values have changed over the last modifiedSince period.  modifiedSince
        is useful if you periodically need to poll a site but are only
        interested in getting data if some of it has changed.
        It is typically be used with period, or startDT/endDT but does not have
        to be. In the latter case, if any values were changed during the
        specified modifiedSince period, only the most recent values would be
        retrieved for those sites. This is a typical usage, since users
        typically are polling a site and only want data if there are new or
        changed measurements.  ISO-8601 duration format is always used.
        There is no default.
        (http://en.wikipedia.org/wiki/ISO_8601#Durations)
            --modifiedSince=PT2H # Retrieves all values for sites and period of
                                 # record requested for any of the requested
                                 # sites and parameters, but only for sites
                                 # where any of the values changed during the
                                 # last two hours.
            --modifiedSince=PT2H --period=P1D # Retrieve all values for sites
                                              # and period of record requested
                                              # for the last 24 hours from now
                                              # only for sites and parameters
                                              # that had any values that
                                              # changed or were added during
                                              # the last two hours.
            --modifiedSince=PT2H --startDt=2010-11-01 --endDt=2010-11-02
                # Retrieve all values for sites and period of record requested
                # for sites and parameters that had values change between
                # midnight site local time on Nov 1st, 2010 and 23:59 on Nov
                # 2nd, 2010 site local time, only if values were changed or
                # added within the last two hours.
    :param agencyCd <str>:
        The list of sites returned are filtered to return only those with the
        provided agency code. The agency code describes the organization that
        maintains the site. Only one agency code is allowed and is optional.
        An authoritative list of agency codes can be found here.
        Default is to return all sites regardless of agency code.
        List: http://help.waterdata.usgs.gov/code/agency_cd_query?fmt=html
            --stateCd=il --agencyCd=USCE # Only US Army Corps of Engineers
                                         # sites in Illinois
    :param siteStatus <str>:
        Selects sites based on whether or not they are active. If a site is
        active, it implies that it is being actively maintained. A site is
        considered active if:
            * it has collected time-series (automated) data within the last 183
              days (6 months), or
            * it has collected discrete (manually collected) data within 397
              days (13 months)
        If it does not meet these criteria, it is considered inactive. Some exceptions apply. If a site is flagged by a USGS water science center as discontinued, it will show as inactive. A USGS science center can also flag a new site as active even if it has not collected any data.
        The default is all (show both active and inactive sites).
        Chose between, 'all', 'active', or 'inactive'.
        Default all - sites of any activity status are returned
            --siteStatus='active'
    :param altMin <float>:
        These arguments allows you to select instantaneous values sites where
        the associated sites' altitude are within a desired altitude, expressed
        in feet. Altitude is based on the datum used at the site.
        Providing a value to altMin (minimum altitude) means you want sites
        that have or exceed the altMin value.
        You may specify decimal feet if precision is critical
        If both the altMin and altMax are specified, sites at or between the
        minimum and maximum altitude are returned.
    :param altMax <float>:
        Providing a value to altMax (maximum altitude) means you want sites
        that have or are less than the altMax value.
            --altMin=1000 --altMax=5000 # Return sites where the altitude is
                                        # 1000 feet or greater and 5000 feet or
                                        # less.
            --altMin=12.5 --altMax=13 # Return sites where the altitude is 12.5
                                      # feet or greater and 13 feet or less.
    :param drainAreaMin <float>:
        These arguments allows you to select principally surface water sites
        where the associated sites' drainage areas (watersheds) are within a
        desired size, expressed in square miles or decimal fractions thereof.
        Providing a value to drainAreaMin (minimum drainage area) means you
        want sites that have or exceed the drainAreaMin value.
        The values may be expressed in decimals
        If both the drainAreaMin and drainAreaMax are specified, sites at or
        between the minimum and maximum drainage areas values specified are
        returned Caution: not all sites are associated with a drainage area.
        Caution: drainage area generally only applies to surface water sites.
        Use with other site types, such as groundwater sites, will likely
        retrieve no results.
    :param drainAreaMax <float>:
        Providing a value to drainAreaMax (maximum drainage area) means you
        want sites that have or are less than the drainAreaMax value.
            --drainAreaMin=1000 --drainAreaMax=5000 # Return sites where the
                                                    # drainage area is 1000
                                                    # square miles or greater
                                                    # and is 5000 square miles
                                                    # or less.
            --drainAreaMin=10.5 --drainAreaMax=10.7 # Return sites where the
                                                    # drainage area is 10.5
                                                    # square miles or greater
                                                    # and is 10.7 square miles
                                                    # or less.
    :param aquiferCd <str>:
        Used to filter sites to those that exist in specified national
        aquifers. Note: not all sites have been associated with national
        aquifers.  Enter one or more national aquifer codes, separated by
        commas.  A national aquifer code is exactly 10 characters.
        You can have up to 1000 aquiferCd codes.
        Complete list: http://water.usgs.gov/ogw/NatlAqCode-reflist.html
            --aquiferCd=S500EDRTRN,N100HGHPLN # returns groundwater sites for
                                              # the Edwards-Trinity aquifer
                                              # system and the High Plains
                                              # national aquifers.

    :param localAquiferCd <str>:
        Used to filter sites to those that exist in specified local aquifers.
        Note: not all sites have been associated with local aquifers.  Enter
        one or more local aquifer codes, separated by commas.  A local aquifer
        code begins with a 2 character state abbreviation (such as TX for
        Texas) followed by a colon followed by the 7 character aquifer code.
        Can have 0 to 1000 comma delimited codes.
        Complete list:
        http://help.waterdata.usgs.gov/code/aqfr_cd_query?fmt=html
        To translate state codes associated with the local aquifer you may need
        this reference: http://www.itl.nist.gov/fipspubs/fip5-2.htm
            --localAquiferCd=AL:111RGLT,AL:111RSDM # returns sites for the
                                                   # Regolith and Saprolite
                                                   # local aquifers in Alabama

    :param wellDepthMin <float>:
        These arguments allows you to select groundwater sites serving data
        recorded automatically where the associated sites' well depth are
        within a desired depth, expressed in feet from the land surface datum.
        Express well depth as a positive number.
        Providing a value to wellDepthMin (minimum well depth) means you want
        sites that have or exceed the wellDepthMin value.
        The values may be expressed in decimals
        If both the wellDepthMin and wellDepthMax are specified, sites at or
        between the minimum and maximum well depth values specified are
        returned wellDepthMax should be greater than or equal to wellDepthMin.
        Caution: well depth applies to groundwater sites only
    :param wellDepthMax <float>:
        Providing a value to wellDepthMax (maximum well depth) means you want
        sites that have or are less than the wellDepthMax value.
             --wellDepthMin=100 --wellDepthMax=500 # Return daily value sites
                                                   # where the well depth is
                                                   # 100 feet or greater and
                                                   # 500 feet or less.
             --wellDepthMin=10.5 --wellDepthMax=10.7 # Return daily value sites
                                                     # where the well depth is
                                                     # 10.5 feet or greater and
                                                     # 10.7 feet or less.
    :param holeDepthMin <float>:
        These arguments allows you to select groundwater sites serving data
        recorded automatically where the associated sites' hole depth are
        within a desired depth, expressed in feet from the land surface datum.
        Express hole depth as a positive number.
        Providing a value to holeDepthMin (minimum hole depth) means you want
        sites that have or exceed the holeDepthMin value.
        The values may be expressed in decimals
        If both the holeDepthMin and holeDepthMax are specified, sites at or
        between the minimum and maximum hole depth values specified are
        returned holeDepthMax should be greater than or equal to holeDepthMin.
        Caution: hole depth applies to groundwater sites only.
    :param holeDepthMax <float>:
        Providing a value to holeDepthMax (maximum hole depth) means you want
        sites that have or are less than the holeDepthMax value.
            --holeDepthMin=100 --holeDepthMax=500 # Return daily values sites
                                                  # where the hole depth is 100
                                                  # feet or greater and 500
                                                  # feet or less.
            --holeDepthMin=10.5 --holeDepthMax=10.7 # Return daily value sites
                                                    # where the hole depth is
                                                    # 10.5 feet or greater and
                                                    # 10.7 feet or less.
    :param period <str>:
        Get a range of values from now by specifying the period argument
        period must be in ISO-8601 Duration format.
        (http://en.wikipedia.org/wiki/ISO_8601#Durations)
        Negative periods (ex: P-T2H) are not allowed
        Data are always returned up to the most recent value, which in the case
        of a predictive gage might be in the future.  When specifying days from
        now, the first value will probably not be at midnight of the first day,
        but somewhat before exactly 24 hours from now.
            --period=PT2H # Retrieve last two hours from now up to most recent
                          # instantaneous value)
            --period=P7D # Retrieve last seven days up from now to most recent
                         # instantaneous value)
    :param startDT <str>:
        Get a range of values from an explicit begin or end date/time   Use the
        startDT and endDT arguments.  Site local time is output, even if
        multiple sites are requested and sites are in different time zones.
        Note that the measurement time zone at a site may not be the same as
        the time zone actually in effect at the site.

        Both startDt and endDt must be in ISO-8601 Date/Time format.
        (http://en.wikipedia.org/wiki/ISO_8601#Dates)
        You can express the date and time in a timezone other than site local
        time if you want as long as it follows the ISO standard. For example,
        you can express the time in Universal time: 2014-03-20T00:00Z.  If
        startDT is supplied and endDT is not, endDT ends with the most recent
        instantaneous value startDT must be chronologically before endDT.

        If startDt shows the date and not the time of day (ex: 2010-09-01) the
        time of midnight site time is assumed (2010-09-01T00:00) If endDt shows
        the date and not the time of day (ex: 2010-09-02) the last minute
        before midnight site time is assumed (2010-09-02T23:59).  Remember,
        only data from October 1, 2007 are currently available.
    :param endDT <str>:
        If endDT is present, startDt must also be present.
            --startDT=2010-11-22 --endDT=2010-11-22 # Full day, from 00:00 to
                                                    # 23:59
            --startDT=2010-11-22T12:00 --endDT=2010-11-22T18:00
            --startDT=2010-11-22 --endDT=2010-11-22
            --startDT=2010-11-22T12:00 # Ends with most recent instantaneous
                                       # value
    :param database <str>:
        One of 'iv' for instantaneous values, and 'dv' for daily values.
        Default is 'dv'.
    '''
    from tsgettoolbox.services import nwis
    if database not in ['iv', 'dv']:
        raise ValueError('''
*
*   The 'database' option must be either 'iv' for instantaneous values, and
*   'dv' for daily values.  You gave {0}.
*
'''.format(database))
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
        endDT=endDT
        )

    return tsutils.printiso(odo(r, pd.DataFrame))

@mando.command(formatter_class=RawTextHelpFormatter)
def daymet(lat,
           lon,
           measuredParams=None,
           year=None,
           ):
    '''
    Download data from the Daymet dataset created by the Oak Ridge National
    Laboratory.  Detailed documentation is at http://daymet.ornl.gov/

    :param lat <float>:
        Latitude (required): Enter single geographic point by latitude, value
        between 52.0N and 14.5N.
            Example: --lat=43.1
    :param lon <float>:
        Longitude (required): Enter single geographic point by longitude, value
        between -131.0W and -53.0W.
            Example: --lon=-85.3
    :param measuredParams <str>:
        CommaSeparatedVariables (optional): Use the abbreviations from the
        following table:

        tmax - maximum temperature, deg C
        tmin - minimum temperature, deg C
        srad - shortwave radiation, W/m2
        vp - vapor pressure, Pa
        swe - snow-water equivalent, kg/m2
        prcp - precipitation, mm
        dayl - daylength, seconds

        Example: --measuredParams=tmax,tmin

        All variables are returned by default.
    :param year <str>:
        CommaSeparatedYears (optional): Current Daymet product (version 2) is
        available from 1980 to the latest full calendar year.
            Example: --years=2012,2013

        All years are returned by default.
    '''
    from tsgettoolbox.services import daymet
    r = resource(
        r'http://daymet.ornl.gov/data/send/saveData',
        measuredParams=measuredParams,
        lat=lat,
        lon=lon,
        year=year,
        )
    return tsutils.printiso(odo(r, pd.DataFrame))

def main():
    ''' Main '''
    if not os.path.exists('debug_tsgettoolbox'):
        sys.tracebacklimit = 0
    mando.main()

if __name__ == '__main__':
    main()
