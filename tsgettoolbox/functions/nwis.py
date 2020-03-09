#!/usr/bin/env python
r"""
tsgettoolbox command line/library tools to retrieve time series.

This program is a collection of utilities to download data from various
web services.
"""

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import warnings

from tsgettoolbox.odo import odo, resource
import pandas as pd
import mando

try:
    from mando.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter

from tstoolbox import tsutils

warnings.filterwarnings("ignore")


nwis_docstrings = {
    "filter_descriptions": r"""
    Detailed documentation is available at http://waterdata.usgs.gov/nwis.

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

    Select ONE of::

        '--sites',
        '--stateCd',
        '--huc',
        '--bBox', or
        '--countyCd'

    **Minor Filters**

    Additional filters can be applied after specifying a major filter.
    This further reduces the set of expected results. Users are
    encouraged to use minor filters because it allows more efficient use
    of this service.

    Use as many as desired to limit number of retrieved time series::

        '--agencyCd',
        '--altMax',
        '--altMin',
        '--aquiferCd',
        '--drainAreaMax',
        '--drainAreaMin',
        '--holeDepthMax'
        '--holeDepthMin',
        '--localAquiferCd',
        '--modifiedSince',
        '--parameterCd',
        '--siteStatus',
        '--siteType',
        '--wellDepthMax',
        '--wellDepthMin',
    """,
    "results_ts": r"""
    **Results**

    The column name in the resulting table is made up of
    "agencyCd_siteno_parameterCd", for example "USGS_02248380_00010".
    The agency and parameter codes are described in the `agencyCd` and
    `parameterCd` options below.

    If `includeCodes` option is used, there will also be columns representing
    the data quality codes named "agencyCd_siteno_parameterCd_cd".

    +---------+--------------------------------------------------------+
    | Code    |  Description                                           |
    +=========+========================================================+
    | e       | Value has been edited or estimated by USGS personnel   |
    |         | and is write protected                                 |
    +---------+--------------------------------------------------------+
    | &       | Value was computed from affected unit values           |
    +---------+--------------------------------------------------------+
    | E       | Value was computed from estimated unit values.         |
    +---------+--------------------------------------------------------+
    | A       | Approved for publication -- Processing and review      |
    |         | completed.                                             |
    +---------+--------------------------------------------------------+
    | P       | Provisional data subject to revision.                  |
    +---------+--------------------------------------------------------+
    | <       | The value is known to be less than reported value and  |
    |         | is write protected.                                    |
    +---------+--------------------------------------------------------+
    | >       | The value is known to be greater than reported value   |
    |         | and is write protected.                                |
    +---------+--------------------------------------------------------+
    | 1       | Value is write protected without any remark code to be |
    |         | printed                                                |
    +---------+--------------------------------------------------------+
    | 2       | Remark is write protected without any remark code to   |
    |         | be printed                                             |
    +---------+--------------------------------------------------------+
    |         | No remark (blank)                                      |
    +---------+--------------------------------------------------------+
    | Ssn     | Parameter monitored seasonally                         |
    +---------+--------------------------------------------------------+
    | Ice     | Ice affected                                           |
    +---------+--------------------------------------------------------+
    | Pr      | Partial-record site                                    |
    +---------+--------------------------------------------------------+
    | Rat     | Rating being developed or revised                      |
    +---------+--------------------------------------------------------+
    | Eqp     | Equipment malfunction                                  |
    +---------+--------------------------------------------------------+
    | Fld     | Flood damage                                           |
    +---------+--------------------------------------------------------+
    | Dis     | Data-collection discontinued                           |
    +---------+--------------------------------------------------------+
    | Dry     | Dry                                                    |
    +---------+--------------------------------------------------------+
    | --      | Parameter not determined                               |
    +---------+--------------------------------------------------------+
    | Mnt     | Maintenance in progress                                |
    +---------+--------------------------------------------------------+
    | ZFl     | Zero flow                                              |
    +---------+--------------------------------------------------------+
    | ``***`` | Temporarily unavailable                                |
    +---------+--------------------------------------------------------+
    """,
    "includeCodes": r"""includeCodes
        [optional, default is False]

        Whether or not to include the metadata/quality code column.
        Useful to almost halve the size of the pandas DataFrame.""",
    "sites": r"""sites : str
        [optional, default is None, major site filter]

        Want to only query one site? Use sites as your major filter, and
        put only one site number in the list.  Sites are comma
        separated.  Sites may be prefixed with an optional agency code
        followed by a colon. If you do not know the site numbers you
        need, you can find relevant sites with the NWIS Mapper
        (http://wdr.water.usgs.gov/nwisgmap/index.html) or on the USGS
        Water Data for the Nation site.
        (http://waterdata.usgs.gov/nwis/)

        Can have from 1 to 100 comma separated site numbers::

            --sites=USGS:01646500
            --sites=01646500,06306300""",
    "stateCd": r"""stateCd : str
        [optional, default is None, major site filter]

        U.S. postal service (2-digit) state code.  Can have only 1 state
        code.  List is available at
        http://www.usps.com/ncsc/lookups/usps_abbreviations.html::

            --stateCd=NY""",
    "huc": r"""huc : str
        [optional, default is None, major site filter]

        A list of hydrologic unit codes (HUC) or watersheds.  Only
        1 major HUC can be specified per request.  A major HUC has two
        digits. Minor HUCs must be eight digits in length.  Can have
        1 to 10 HUC codes.  List of HUCs is available at
        http://water.usgs.gov/GIS/huc_name.html::

            --huc=01,02070010""",
    "bBox": r"""bBox :
        [optional, default is None, major site filter]

        A contiguous range of decimal latitude and longitude, starting
        with the west longitude, then the south latitude, then the east
        longitude, and then the north latitude with each value separated
        by a comma. The product of the range of latitude and longitude
        cannot exceed 25 degrees. Whole or decimal degrees must be
        specified, up to six digits of precision. Minutes and seconds
        are not allowed. Remember: western longitude (which includes
        almost all of the United States) is specified in negative
        degrees. Caution: many sites outside the continental US do not
        have latitude and longitude referenced to NAD83 and therefore
        can not be found using these arguments. Certain sites are not
        associated with latitude and longitude due to homeland security
        concerns and cannot be found using this filter.::

            --bBox=-83,36.5,-81,38.5""",
    "countyCd": r"""countyCd :
        [optional, default is None, major site filter]

        A list of county numbers, in a 5 digit numeric format. The first
        two digits of a county's code are the FIPS State Code.  Can have
        from 1 to 20 county codes.  The first 2 digits are the FIPS
        State Code (http://www.itl.nist.gov/fipspubs/fip5-2.htm) and the
        list of county codes are at
        http://help.waterdata.usgs.gov/code/county_query?fmt=html::

            --countyCd=51059,51061""",
    "parameterCd": r"""parameterCd :
        [optional, default is None, minor site filter]

        USGS time-series parameter code.  All parameter codes are
        numeric and 5 characters in length.  Parameter codes are used to
        identify the constituent measured and the units of measure.
        Popular codes include stage (00065), discharge in cubic feet per
        second (00060) and water temperature in degrees Celsius (00010).
        Can request from 1 to 100 "parameterCD"s.  Default: returns all
        regular time-series for the requested sites.

        Complete list::

            http://help.waterdata.usgs.gov/codes-and-parameters/parameters::

            --parameterCd=00060       # discharge, cubic feet
                                      # per second
            --parameterCd=00060,00065 # discharge,
                                      # cubic feet per second
                                      # and gage height in
                                      # feet""",
    "siteType": r"""siteType :
        [optional, default is None, minor site filter]

        Restricts sites to those having one or more major and/or minor
        site types.  If you request a major site type (ex: &siteType=ST)
        you will get all sub-site types of the same major type as well
        (in this case, ST-CA, ST-DCH and ST-TS).  Can have from 1 to an
        unlimited number of siteType codes.  Default is to return all
        types.  List of valid site types:
        http://help.waterdata.usgs.gov/site_tp_cd::

            --siteType=ST       # Streams only
            --siteType=ST,LA-OU # Streams and Land Outcrops only""",
    "modifiedSince": r"""modifiedSince :
        [optional, default is None, minor site filter]

        Returns all values for sites and period of record requested only
        if any values have changed over the last modifiedSince period.
        modifiedSince is useful if you periodically need to poll a site
        but are only interested in getting data if some of it has
        changed.  It is typically be used with period, or startDT/endDT
        but does not have to be. In the latter case, if any values were
        changed during the specified modifiedSince period, only the most
        recent values would be retrieved for those sites. This is
        a typical usage, since users typically are polling a site and
        only want data if there are new or changed measurements.
        ISO-8601 duration format is always used.  There is no default.
        (http://en.wikipedia.org/wiki/ISO_8601#Durations)::

            --modifiedSince=PT2H
                   # Retrieves all values for sites and period of record
                   # requested for any of the requested sites and
                   # parameters, but only for sites where any of the
                   # values changed during the last two hours.
            --modifiedSince=PT2H --period=P1D
                   # Retrieve all values for sites and period of record
                   # requested for the last 24 hours from now only for
                   # sites and parameters that had any values that
                   # changed or were added during the last two hours.
            --modifiedSince=PT2H --startDt=2010-11-01 --endDt=2010-11-02
                   # Retrieve all values for sites and period of record
                   # requested for sites and parameters that had values
                   # change between midnight site local time on Nov 1st,
                   # 2010 and 23:59 on Nov 2nd, 2010 site local time,
                   # only if values were changed or added within the
                   # last two hours.""",
    "agencyCd": r"""agencyCd :
        [optional, default is None, minor site filter]

        The list of sites returned are filtered to return only those
        with the provided agency code. The agency code describes the
        organization that maintains the site. Only one agency code is
        allowed and is optional.  An authoritative list of agency codes
        can be found here.  Default is to return all sites regardless of
        agency code.  List:
        http://help.waterdata.usgs.gov/code/agency_cd_query?fmt=html::

            --stateCd=il --agencyCd=USCE # Only US Army Corps
                                         # of Engineers sites
                                         # in Illinois""",
    "siteStatus": r"""siteStatus :
        [optional, default is None, minor site filter]

        Selects sites based on whether or not they are active. If a site
        is active, it implies that it is being actively maintained.
        A site is considered active if: it has collected time-series
        (automated) data within the last 183 days (6 months), or it has
        collected discrete (manually collected) data within 397 days (13
        months) If it does not meet these criteria, it is considered
        inactive. Some exceptions apply.  If a site is flagged by a USGS
        water science center as discontinued, it will show as inactive.
        A USGS science center can also flag a new site as active even if
        it has not collected any data.  The default is all (show both
        active and inactive sites).  Chose between, 'all', 'active', or
        'inactive'.  Default all - sites of any activity status are
        returned.::

            --siteStatus='active'""",
    "altMin": r"""altMin : float
        [optional, default is None, minor site filter]

        These arguments allows you to select instantaneous values sites
        where the associated sites' altitude are within a desired
        altitude, expressed in feet.  Altitude is based on the datum
        used at the site.  Providing a value to altMin (minimum
        altitude) means you want sites that have or exceed the altMin
        value.  You may specify decimal feet if precision is critical If
        both the altMin and altMax are specified, sites at or between
        the minimum and maximum altitude are returned.""",
    "altMax": r"""altMax : float
        [optional, default is None, minor site filter]

        Providing a value to altMax (maximum altitude) means you want
        sites that have or are less than the altMax value.::

            --altMin=1000 --altMax=5000
                  # Return sites where the altitude is 1000 feet or
                  # greater and 5000 feet or less.
            --altMin=12.5 --altMax=13
                  # Return sites where the altitude is 12.5 feet or
                  # greater and 13 feet or less.""",
    "drainAreaMin": r"""drainAreaMin : float
        [optional, default is None, minor site filter]

        SURFACE WATER SITE ATTRIBUTE

        These arguments allows you to select principally surface water
        sites where the associated sites' drainage areas (watersheds)
        are within a desired size, expressed in square miles or decimal
        fractions thereof.  Providing a value to drainAreaMin (minimum
        drainage area) means you want sites that have or exceed the
        drainAreaMin value.  The values may be expressed in decimals. If
        both the drainAreaMin and drainAreaMax are specified, sites at
        or between the minimum and maximum drainage areas values
        specified are returned Caution: not all sites are associated
        with a drainage area.  Caution: drainage area generally only
        applies to surface water sites.  Use with other site types, such
        as groundwater sites, will likely retrieve no results.""",
    "drainAreaMax": r"""drainAreaMax:  float
        [optional, default is None, minor site filter]

        SURFACE WATER SITE ATTRIBUTE

        Providing a value to drainAreaMax (maximum drainage area) means
        you want sites that have or are less than the drainAreaMax
        value.::

            --drainAreaMin=1000 --drainAreaMax=5000
                                 # Return sites where the drainage area
                                 # is 1000 square miles or greater and
                                 # is 5000 square miles or less.
            --drainAreaMin=10.5 --drainAreaMax=10.7
                                 # Return sites where the drainage area
                                 # is 10.5 square miles or greater and
                                 # is 10.7 square miles or less.""",
    "aquiferCd": r"""aquiferCd
        [optional, default is None, minor site filter]

        Used to filter sites to those that exist in specified national
        aquifers. Note: not all sites have been associated with national
        aquifers.  Enter one or more national aquifer codes, separated
        by commas.  A national aquifer code is exactly 10 characters.
        You can have up to 1000 aquiferCd codes.  Complete list:
        http://water.usgs.gov/ogw/NatlAqCode-reflist.html::

            --aquiferCd=S500EDRTRN,N100HGHPLN
                                  # returns groundwater sites for the
                                  # Edwards-Trinity aquifer system and
                                  # the High Plains national
                                  # aquifers.""",
    "localAquiferCd": r"""localAquiferCd
        [optional, default is None, minor site filter]

        Used to filter sites to those that exist in specified local
        aquifers.  Note: not all sites have been associated with local
        aquifers.  Enter one or more local aquifer codes, separated by
        commas.  A local aquifer code begins with a 2 character state
        abbreviation (such as TX for Texas) followed by a colon followed
        by the 7 character aquifer code.  Can have 0 to 1000 comma
        delimited codes.  Complete list:
        http://help.waterdata.usgs.gov/code/aqfr_cd_query?fmt=html
        To translate state codes associated with the local aquifer you
        may need this reference:
        http://www.itl.nist.gov/fipspubs/fip5-2.htm ::

            --localAquiferCd=AL:111RGLT,AL:111RSDM
                    # returns sites for the Regolith and Saprolite local
                    # aquifers in Alabama""",
    "wellDepthMin": r"""wellDepthMin : float
        [optional, default is None, minor site filter]

        GROUNDWATER SITE ATTRIBUTE

        These arguments allows you to select groundwater sites serving
        data recorded automatically where the associated sites' well
        depth are within a desired depth, expressed in feet from the
        land surface datum.  Express well depth as a positive number.
        Providing a value to wellDepthMin (minimum well depth) means you
        want sites that have or exceed the wellDepthMin value.  The
        values may be expressed in decimals Caution: well depth applies
        to groundwater sites only.::

             --wellDepthMin=100 --wellDepthMax=500
                     # Return daily value sites where the well depth is
                     # 100 feet or greater and 500 feet or less.""",
    "wellDepthMax": r"""wellDepthMax : float
        [optional, default is None, minor site filter]

        GROUNDWATER SITE ATTRIBUTE

        Providing a value to wellDepthMax (maximum well depth) means you
        want sites that have or are less than the wellDepthMax value.::

             --wellDepthMin=10.5 --wellDepthMax=10.7
                     # Return daily value sites where the well depth is
                     # 10.5 feet or greater and 10.7 feet or less.

        If both the wellDepthMin and wellDepthMax are specified, sites
        at or between the minimum and maximum well depth values
        specified are returned wellDepthMax should be greater than or
        equal to wellDepthMin.""",
    "holeDepthMin": r"""holeDepthMin : float
        [optional, default is None, minor site filter]

        GROUNDWATER SITE ATTRIBUTE

        These arguments allows you to select groundwater sites serving
        data recorded automatically where the associated sites' hole
        depth are within a desired depth, expressed in feet from the
        land surface datum.  Express hole depth as a positive number.
        Providing a value to holeDepthMin (minimum hole depth) means you
        want sites that have or exceed the holeDepthMin value.  The
        values may be expressed in decimals Caution: hole depth applies
        to groundwater sites only.""",
    "holeDepthMax": r"""holeDepthMax : float
        [optional, default is None, minor site filter]

        GROUNDWATER SITE ATTRIBUTE

        Providing a value to holeDepthMax (maximum hole depth) means you
        want sites that have or are less than the holeDepthMax value.::

            --holeDepthMin=100 --holeDepthMax=500
                    # Return daily values sites where the hole depth is
                    # 100 feet or greater and 500 feet or less.

            --holeDepthMin=10.5 --holeDepthMax=10.7
                    # Return daily value sites where the hole depth is
                    # 10.5 feet or greater and 10.7 feet or less.

        If both the holeDepthMin and holeDepthMax are specified, sites
        at or between the minimum and maximum hole depth values
        specified are returned holeDepthMax should be greater than or
        equal to holeDepthMin.""",
    "period": r"""period
        [optional, default is None]

        Get a range of values from now by specifying the period argument
        period must be in ISO-8601 Duration format.
        (http://en.wikipedia.org/wiki/ISO_8601#Durations) Negative
        periods (ex: P-T2H) are not allowed.  Data are always returned
        up to the most recent value, which in the case of a predictive
        gage might be in the future.  When specifying days from now, the
        first value will probably not be at midnight of the first day,
        but somewhat before exactly 24 hours from now.::

            --period=PT2H
                  # Retrieve last two hours from now up to most recent
                  # instantaneous value)
            --period=P7D
                  # Retrieve last seven days up from now to most recent
                  # instantaneous value)""",
    "startDT": r"""startDT
        [optional, default is None]

        Get a range of values from an explicit begin or end date/time.
        Use the startDT and endDT arguments.  Site local time is output,
        even if multiple sites are requested and sites are in different
        time zones.  Note that the measurement time zone at a site may
        not be the same as the time zone actually in effect at the site.

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
        1, 2007 are currently available in the 'iv' database.""",
    "endDT": r"""endDT
        [optional, default is None]

        If endDT is present, startDt must also be
        present.::

            --startDT=2010-11-22 --endDT=2010-11-22  # Full day, 00:00 to 23:59
            --startDT=2010-11-22T12:00 --endDT=2010-11-22T18:00
            --startDT=2010-11-22 --endDT=2010-11-22
            --startDT=2010-11-22T12:00  # From "startDT" to most recent
                                        # instantaneous value""",
    "statReportType": r"""statReportType : str
        [optional, default is 'daily']

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
        +----------------+------------------------------------------+""",
    "statType": r"""statType : str
        [optional, default is None, minor site filter]

        Selects sites based on the statistics type(s) desired, such as
        minimum, maximum or mean

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
                percentiles.""",
    "missingData": r"""missingData
        [optional, default is None]

        Used to indicate the rules to follow to generate statistics if
        there are gaps in the period of record during the requested
        statistics period. By default if there are any missing data for
        the report type, the statistic is left blank or null.

        This option does not apply to daily statistics, but optionally
        can be used with monthly and yearly statistics. If used with
        daily statistics, an error will occur.

        Missing data can happen for various reasons including there was
        a technical problem with the gage for part of the time period.

        Enabling this switch will attempt to provide a statistic if
        there is enough data to create one.

        Choice is 'off' or 'on'.""",
    "statisticsCd": r"""statisticsCd
        [optional, default is None]

        The statisticsCd represents how the instantaneous values are
        aggregated.  The statisticsCd is from the following table:

        +-------+------------------------------------+
        | Code  | Description                        |
        +=======+====================================+
        | 00001 | MAXIMUM VALUES                     |
        +-------+------------------------------------+
        | 00002 | MINIMUM VALUES                     |
        +-------+------------------------------------+
        | 00003 | MEAN VALUES                        |
        +-------+------------------------------------+
        | 00004 | VALUES TAKEN BETWEEN 0001 AND 1200 |
        +-------+------------------------------------+
        | 00005 | VALUES TAKEN BETWEEN 1201 AND 2400 |
        +-------+------------------------------------+
        | 00006 | SUMMATION VALUES                   |
        +-------+------------------------------------+
        | 00007 | MODAL VALUES                       |
        +-------+------------------------------------+
        | 00008 | MEDIAN VALUES                      |
        +-------+------------------------------------+
        | 00009 | STANDARD DEVIATION VALUES          |
        +-------+------------------------------------+
        | 00010 | VARIANCE VALUES                    |
        +-------+------------------------------------+
        | 00011 | RANDOM INSTANTANEOUS VALUES        |
        +-------+------------------------------------+
        | 00012 | EQUIVALENT MEAN VALUES             |
        +-------+------------------------------------+
        | 00013 | SKEWNESS VALUES                    |
        +-------+------------------------------------+
        | 00021 | TIDAL HIGH-HIGH VALUES             |
        +-------+------------------------------------+
        | 00022 | TIDAL LOW-HIGH VALUES              |
        +-------+------------------------------------+
        | 00023 | TIDAL HIGH-LOW VALUES              |
        +-------+------------------------------------+
        | 00024 | TIDAL LOW-LOW VALUES               |
        +-------+------------------------------------+
        | 01XXY | XX.Y PERCENTILE                    |
        +-------+------------------------------------+
        | 02LLL | LLL DAY LOW MEAN                   |
        +-------+------------------------------------+
        | 03HHH | HHH DAY HIGH MEAN                  |
        +-------+------------------------------------+
        | 3TTTT | INSTANTANEOUS OBSERVATION AT TTTT  |
        +-------+------------------------------------+""",
    "siteOutput": r"""siteOutput
        [optional, default is None]

        If you would like to see expanded site information, check this
        box.  This argument is ignored for visually oriented output
        formats like Mapper, Google Earth and Google Maps. The default
        is basic. Use expanded to get expanded site information.
        Example: &siteOutput=expanded. Note: for performance reasons,
        &siteOutput=expanded cannot be used if seriesCatalogOutput=true
        or with any values for outputDataTypeCd.""",
    "seriesCatalogOutput": r"""seriesCatalogOutput
        [optional, default is None]

        This argument is ignored for visually oriented output formats
        like Mapper, Google Earth and Google Maps. If you would like to
        see all the period of record information for the sites selected,
        check this box.  You will see detailed information, such as
        a continuous range of dates served by a site for one or more
        data types, for example, the begin and end dates that streamflow
        (parameter 00060) was recorded at a site.  Note: if you select
        any data types for output (see below) the period of record data
        will also appear. In that case specifying this argument is
        unnecessary. The default is false. The only legal values for
        this argument are true and false. Example:
        &seriesCatalogOutput=true.
        &seriesCatalogOutput=true is equivalent to
        &outputDataTypeCd=all. Note: for performance reasons,
        &siteOutput=expanded cannot be used if
        seriesCatalogOutput=true.""",
    "outputDataTypeCd": r"""outputDataTypeCd
        [optional, default is None]

        This will add period of record information to certain output
        formats (GML, RDB and JSON) that summarize information about the
        data types requested.  The default is all data types. Some
        output formats are designed for visual use (Google Earth, Google
        Maps and Mapper).  Consequently with these formats you will not
        see data type code information.

        Default information: If seriesCatalogOutput is true, all period
        of record information is shown by default. If
        seriesCatalogOutput is false, unless you override it using one
        of the values below, no period of record information is shown.

        Note: for performance reasons, &siteOutput=expanded cannot be
        used if with any values for outputDataTypeCd.

        Here are the various output data type codes available. These can
        be selected individually or can be added as comma separated
        values if desired.  Example: &outputDataTypeCd=iv,dv

        +-----+---------------------------------------------------------------+
        | all | default (see above for qualifications). This is equivalent to |
        |     | &seriesCatalogOutput=true.                                    |
        +-----+---------------------------------------------------------------+
        | iv  | Instantaneous values (time-series measurements typically      |
        |     | recorded by automated equipment at frequent intervals (e.g.,  |
        |     | hourly)                                                       |
        +-----+---------------------------------------------------------------+
        | uv  | Unit values (alias for iv)                                    |
        +-----+---------------------------------------------------------------+
        | rt  | Real-time data (alias for iv)                                 |
        +-----+---------------------------------------------------------------+
        | dv  | Daily values (once daily measurements or summarized           |
        |     | information for a particular day, such as daily maximum,      |
        |     | minimum and mean)                                             |
        +-----+---------------------------------------------------------------+
        | pk  | Peaks measurements of water levels and streamflow for surface |
        |     | water sites (such as during floods, may be either an          |
        |     | automated or a manual measurement)                            |
        +-----+---------------------------------------------------------------+
        | sv  | Site visits (irregular manual surface water measurements,     |
        |     | excluding peak measurements)                                  |
        +-----+---------------------------------------------------------------+
        | gw  | Groundwater levels measured at irregular, discrete intervals. |
        |     | For recorded, time series groundwater levels, use iv or id.   |
        +-----+---------------------------------------------------------------+
        | qw  | Water-quality data from discrete sampling events and analyzed |
        |     | in the field or in a laboratory. For recorded time series     |
        |     | water-quality data, use iv or id.                             |
        +-----+---------------------------------------------------------------+
        | id  | Historical instantaneous values (sites in the USGS            |
        |     | Instantaneous Data Archive External Link)                     |
        +-----+---------------------------------------------------------------+
        | aw  | Sites monitored by the USGS Active Groundwater Level Network  |
        |     | External Link                                                 |
        +-----+---------------------------------------------------------------+
        | ad  | Sites included in USGS Annual Water Data Reports External     |
        |     | Link}                                                         |
        +-----+---------------------------------------------------------------+""",
    "siteName": r"""siteName
        [optional, default is None, minor site filter]

        This filter allows you to find a site by its name, using either
        the exact site name or a partial site name. Note that a major
        filter is still required. String matches are case insensitive,
        so if you specify "Boulder" you will retrieve site names with
        "Boulder", "boulder", "BOULDER" as well as many other variants.
        To embed a space, you can use single quotes. Examaple:
        --siteName='Boulder Creek'""",
    "siteNameMatchOperator": r"""siteNameMatchOperator
        [optional, default is None, minor site filter]

        If used, this must be used with siteName. It determines how the
        pattern matching for the site name behaves. Matches are case
        insensitive. The options are::

            start = The string must be at the start of the site name (default)
            any = The string must be contained somewhere in the site name
            exact = The site name must exactly match the string supplied, with
                    the exception that the match is not case sensitive

        Example: &siteNameMatchOperator=any""",
    "hasDataTypeCd": r"""hasDataTypeCd
        [optional, default is None, minor site filter]

        Default is all. Restricts results to those sites that collect
        certain kinds of data. Separate values with commas. Allowed
        values are:

        +-----+---------------------------------------------------------------+
        | all | default (see above for qualifications). This is equivalent to |
        |     | &seriesCatalogOutput=true.                                    |
        +-----+---------------------------------------------------------------+
        | iv  | Instantaneous values (time-series measurements typically      |
        |     | recorded by automated equipment at frequent intervals (e.g.,  |
        |     | hourly)                                                       |
        +-----+---------------------------------------------------------------+
        | uv  | Unit values (alias for iv)                                    |
        +-----+---------------------------------------------------------------+
        | rt  | Real-time data (alias for iv)                                 |
        +-----+---------------------------------------------------------------+
        | dv  | Daily values (once daily measurements or summarized           |
        |     | information for a particular day, such as daily maximum,      |
        |     | minimum and mean)                                             |
        +-----+---------------------------------------------------------------+
        | pk  | Peaks measurements of water levels and streamflow for surface |
        |     | water sites (such as during floods, may be either an          |
        |     | automated or a manual measurement)                            |
        +-----+---------------------------------------------------------------+
        | sv  | Site visits (irregular manual surface water measurements,     |
        |     | excluding peak measurements)                                  |
        +-----+---------------------------------------------------------------+
        | gw  | Groundwater levels measured at irregular, discrete intervals. |
        |     | For recorded, time series groundwater levels, use iv or id.   |
        +-----+---------------------------------------------------------------+
        | qw  | Water-quality data from discrete sampling events and analyzed |
        |     | in the field or in a laboratory. For recorded time series     |
        |     | water-quality data, use iv or id.                             |
        +-----+---------------------------------------------------------------+
        | id  | Historical instantaneous values (sites in the USGS            |
        |     | Instantaneous Data Archive External Link)                     |
        +-----+---------------------------------------------------------------+
        | aw  | Sites monitored by the USGS Active Groundwater Level Network  |
        |     | External Link                                                 |
        +-----+---------------------------------------------------------------+
        | ad  | Sites included in USGS Annual Water Data Reports External     |
        |     | Link                                                          |
        +-----+---------------------------------------------------------------+""",
    "statYearType": r"""statYearType
        [optional, default is None]

        Indicates which kind of year statistics should be created
        against. This only applies when requesting annual statistics,
        i.e.  statReportType=annual. Valid year types codes include:

        +----------+----------------------------------------------------------+
        | calendar | calendar year, i.e. January 1 through December 31        |
        +----------+----------------------------------------------------------+
        | water    | water year, i.e. a year begins October 1 of the previous |
        |          | year and ends September 30 of the current year. This is  |
        |          | the same as a federal fiscal year.                       |
        +----------+----------------------------------------------------------+""",
}


@mando.command("nwis", formatter_class=HelpFormatter, doctype="numpy")
def nwis_cli(
    sites=None,
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
    database="dv",
    statReportType=None,
    statType=None,
    missingData=None,
    statYearType=None,
):
    r"""Deprecated: Use the ``nwis_*`` functions instead.

    This "nwis" function has been split up into individual functions for each
    source database.  This allows for keywords and output to be tailored to
    each specific web service.

    +-------------------+-------------------------------+
    | New Function      | Database Name and Description |
    +===================+===============================+
    | nwis_iv           | Instantaneous Value sub-daily |
    |                   | interval data starting in     |
    |                   | 2007                          |
    +-------------------+-------------------------------+
    | nwis_dv           | Daily Values database         |
    +-------------------+-------------------------------+
    | nwis_stat         | daily/monthly/annual          |
    |                   | statistics                    |
    +-------------------+-------------------------------+
    | nwis_site         | Site metadata                 |
    +-------------------+-------------------------------+
    | nwis_measurements | Field measurements            |
    +-------------------+-------------------------------+
    | nwis_peak         | Peak flow and stage           |
    +-------------------+-------------------------------+
    | nwis_gwlevels     | Ground water levels           |
    +-------------------+-------------------------------+

    This function/sub-command will continue to work, however you should
    change all scripts to use the split out functions.
    """
    tsutils._printiso(
        nwis(
            sites=sites,
            stateCd=stateCd,
            huc=huc,
            bBox=bBox,
            countyCd=countyCd,
            parameterCd=parameterCd,
            period=period,
            startDT=startDT,
            endDT=endDT,
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
            database=database,
            statReportType=statReportType,
            statType=statType,
            missingData=missingData,
            statYearType=statYearType,
        )
    )


def nwis(
    sites=None,
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
    database="dv",
    statReportType=None,
    statType=None,
    missingData=None,
    statYearType=None,
):
    warnings.warn(tsutils.error_wrapper(nwis_cli.__doc__))

    from tsgettoolbox.services.usgs import nwis as placeholder

    if database not in ["iv", "dv", "stat", "measurements", "peak", "site", "gwlevels"]:
        raise ValueError(
            tsutils.error_wrapper(
                r"""
The 'database' option must be either 'iv' for instantaneous values, or 'dv' for
daily values, or 'stat' for daily, monthly, or annual statistics, or
'measurements' for field measurements, 'peak' for peak stage and flow
estimates, 'site' for site metadata, or 'gwlevels' for ground water levels.

You gave {0}.""".format(
                    database
                )
            )
        )
    url = r"http://waterservices.usgs.gov/nwis/{0}/".format(database)
    if database in ["measurements", "peak", "gwlevels"]:
        words = sites.split(",")
        if len(words) != 1:
            raise ValueError(
                tsutils.error_wrapper(
                    r"""
For the 'measurements', 'peak', and 'gwlevels' databases you can only collect
data from one site, you listed {0}.
""".format(
                        len(words)
                    )
                )
            )
        if (
            stateCd is not None
            or huc is not None
            or bBox is not None
            or countyCd is not None
        ):
            raise ValueError(
                tsutils.error_wrapper(
                    r"""
The 'measurements', 'peak', or 'gwlevels' databases can currently only
accept one site using the 'site' keyword.
"""
                )
            )

        if database in ["measurements", "peak"]:
            url = r"http://nwis.waterdata.usgs.gov/XX/nwis/{0}".format(database)
    r = resource(
        url,
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

    return odo(r, pd.DataFrame)


@mando.command("nwis_iv", formatter_class=HelpFormatter, doctype="numpy")
@tsutils.doc(nwis_docstrings)
def nwis_iv_cli(
    sites=None,
    stateCd=None,
    huc=None,
    bBox=None,
    countyCd=None,
    parameterCd=None,
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
    period=None,
    startDT=None,
    endDT=None,
    includeCodes=False,
):
    r"""Download from Instantaneous Values of the USGS NWIS.
    {filter_descriptions}
    {results_ts}
    Parameters
    ----------
    {sites}
    {stateCd}
    {huc}
    {bBox}
    {countyCd}
    {agencyCd}
    {altMax}
    {altMin}
    {aquiferCd}
    {drainAreaMax}
    {drainAreaMin}
    {holeDepthMax}
    {holeDepthMin}
    {localAquiferCd}
    {modifiedSince}
    {parameterCd}
    {siteStatus}
    {siteType}
    {wellDepthMax}
    {wellDepthMin}
    {period}
    {startDT}
    {endDT}
    {includeCodes}"""
    tsutils._printiso(
        nwis_iv(
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
            includeCodes=includeCodes,
        )
    )


def nwis_iv(
    sites=None,
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
    includeCodes=False,
):
    r"""Download from Instantaneous Values of the USGS NWIS."""
    from tsgettoolbox.services.usgs import nwis as placeholder

    url = r"http://waterservices.usgs.gov/nwis/iv/"
    r = resource(
        url,
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
        includeCodes=includeCodes,
    )

    return odo(r, pd.DataFrame)


@mando.command("nwis_dv", formatter_class=HelpFormatter, doctype="numpy")
@tsutils.doc(nwis_docstrings)
def nwis_dv_cli(
    sites=None,
    stateCd=None,
    huc=None,
    bBox=None,
    countyCd=None,
    agencyCd=None,
    altMax=None,
    altMin=None,
    aquiferCd=None,
    drainAreaMax=None,
    drainAreaMin=None,
    holeDepthMax=None,
    holeDepthMin=None,
    localAquiferCd=None,
    modifiedSince=None,
    parameterCd=None,
    siteStatus=None,
    siteType=None,
    wellDepthMax=None,
    wellDepthMin=None,
    startDT=None,
    endDT=None,
    period=None,
    includeCodes=False,
    statisticsCd=None,
):
    r"""Download from the Daily Values database of the USGS NWIS.
    {filter_descriptions}
    {results_ts}
    Parameters
    ----------
    {sites}
    {stateCd}
    {huc}
    {bBox}
    {countyCd}
    {agencyCd}
    {altMax}
    {altMin}
    {aquiferCd}
    {drainAreaMax}
    {drainAreaMin}
    {holeDepthMax}
    {holeDepthMin}
    {localAquiferCd}
    {modifiedSince}
    {parameterCd}
    {siteStatus}
    {siteType}
    {wellDepthMax}
    {wellDepthMin}
    {period}
    {startDT}
    {endDT}
    {includeCodes}
    {statisticsCd}"""
    tsutils._printiso(
        nwis_dv(
            sites=sites,
            stateCd=stateCd,
            huc=huc,
            bBox=bBox,
            countyCd=countyCd,
            parameterCd=parameterCd,
            statisticsCd=statisticsCd,
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
            includeCodes=includeCodes,
        )
    )


def nwis_dv(
    sites=None,
    stateCd=None,
    huc=None,
    bBox=None,
    countyCd=None,
    parameterCd=None,
    statisticsCd=None,
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
    includeCodes=False,
):
    r"""Download from the Daily Values database of the USGS NWIS."""
    from tsgettoolbox.services.usgs import nwis as placeholder

    url = r"http://waterservices.usgs.gov/nwis/dv/"
    r = resource(
        url,
        sites=sites,
        stateCd=stateCd,
        huc=huc,
        bBox=bBox,
        countyCd=countyCd,
        parameterCd=parameterCd,
        statisticsCd=statisticsCd,
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
        includeCodes=includeCodes,
    )

    return odo(r, pd.DataFrame)


@mando.command("nwis_site", formatter_class=HelpFormatter, doctype="numpy")
@tsutils.doc(nwis_docstrings)
def nwis_site_cli(
    sites=None,
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
    siteOutput=None,
    seriesCatalogOutput=None,
    outputDataTypeCd=None,
    siteName=None,
    siteNameMatchOperator=None,
    hasDataTypeCd=None,
):
    r"""Download from the site database of the USGS NWIS.

    This does not return a time-series, but a table of sites.
    {filter_descriptions}
    **Results**

    +---------------------+----------------------------------+
    | Column              | Description                      |
    +=====================+==================================+
    | agency_cd           | Agency                           |
    +---------------------+----------------------------------+
    | site_no             | Site identification number       |
    +---------------------+----------------------------------+
    | station_nm          | Site name                        |
    +---------------------+----------------------------------+
    | site_tp_cd          | Site type                        |
    +---------------------+----------------------------------+
    | dec_lat_va          | Decimal latitude                 |
    +---------------------+----------------------------------+
    | dec_long_va         | Decimal longitude                |
    +---------------------+----------------------------------+
    | coord_acy_cd        | Latitude-longitude accuracy      |
    +---------------------+----------------------------------+
    | dec_coord_datum_cd  | Decimal Latitude-longitude datum |
    +---------------------+----------------------------------+
    | alt_va              | Altitude of Gage/land surface    |
    +---------------------+----------------------------------+
    | alt_acy_va          | Altitude accuracy                |
    +---------------------+----------------------------------+
    | alt_datum_cd        | Altitude datum                   |
    +---------------------+----------------------------------+
    | huc_cd              | Hydrologic unit code             |
    +---------------------+----------------------------------+

    .. _site_tp_cd: https://help.waterdata.usgs.gov/code/site_tp_query?fmt=html
    .. _coord_acy_cd: https://help.waterdata.usgs.gov/code/coord_acy_cd_query?fmt=html
    .. _dec_coord_datum_cd: https://help.waterdata.usgs.gov/code/coord_datum_cd_query?fmt=html
    .. _alt_datum_cd: https://help.waterdata.usgs.gov/code/alt_datum_cd_query?fmt=html
    .. _huc_cd: https://help.waterdata.usgs.gov/code/hucs_query?fmt=html

    Parameters
    ----------
    {sites}
    {stateCd}
    {huc}
    {bBox}
    {countyCd}

    {parameterCd}
    {siteType}
    {modifiedSince}
    {agencyCd}
    {siteStatus}
    {altMin}
    {altMax}
    {drainAreaMin}
    {drainAreaMax}
    {aquiferCd}
    {localAquiferCd}
    {wellDepthMin}
    {wellDepthMax}
    {holeDepthMin}
    {holeDepthMax}

    {period}
    {startDT}
    {endDT}
    {includeCodes}

    {siteOutput}
    {seriesCatalogOutput}
    {outputDataTypeCd}
    {siteName}
    {siteNameMatchOperator}
    {hasDataTypeCd}"""

    tsutils._printiso(
        nwis_site(
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
            siteOutput=siteOutput,
            seriesCatalogOutput=seriesCatalogOutput,
            outputDataTypeCd=outputDataTypeCd,
            siteName=siteName,
            siteNameMatchOperator=siteNameMatchOperator,
            hasDataTypeCd=hasDataTypeCd,
        )
    )


def nwis_site(
    sites=None,
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
    siteOutput=None,
    seriesCatalogOutput=None,
    outputDataTypeCd=None,
    siteName=None,
    siteNameMatchOperator=None,
    hasDataTypeCd=None,
):
    r"""Download from the site database of the USGS NWIS."""
    from tsgettoolbox.services.usgs import nwis as placeholder

    url = r"http://waterservices.usgs.gov/nwis/site/"
    r = resource(
        url,
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
        siteOutput=siteOutput,
        seriesCatalogOutput=seriesCatalogOutput,
        outputDataTypeCd=outputDataTypeCd,
        siteName=siteName,
        siteNameMatchOperator=siteNameMatchOperator,
        hasDataTypeCd=hasDataTypeCd,
    )

    return odo(r, pd.DataFrame)


@mando.command("nwis_gwlevels", formatter_class=HelpFormatter, doctype="numpy")
@tsutils.doc(nwis_docstrings)
def nwis_gwlevels_cli(
    sites=None,
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
    aquiferCd=None,
    localAquiferCd=None,
    wellDepthMin=None,
    wellDepthMax=None,
    holeDepthMin=None,
    holeDepthMax=None,
):
    r"""Download from the Groundwater Levels database of the USGS NWIS.

    {filter_descriptions}
    **Results**

    +---------------+-------------------------------+
    | Column        | Description                   |
    +===============+===============================+
    | agency_cd     | Agency code                   |
    +---------------+-------------------------------+
    | site_no       | USGS site number              |
    +---------------+-------------------------------+
    | site_tp_cd    | Site type code                |
    +---------------+-------------------------------+
    | lev_dt        | Date level measured           |
    +---------------+-------------------------------+
    | lev_tm        | Time level measured           |
    +---------------+-------------------------------+
    | lev_tz_cd     | Time datum                    |
    +---------------+-------------------------------+
    | lev_va        | Water-level value in feet     |
    |               | below land surface            |
    +---------------+-------------------------------+
    | sl_lev_va     | Water-level value in feet     |
    |               | above specific vertical datum |
    +---------------+-------------------------------+
    | sl_datum_cd   | Referenced vertical datum     |
    +---------------+-------------------------------+
    | lev_status_cd | Status                        |
    +---------------+-------------------------------+
    | lev_agency_cd | Measuring agency              |
    +---------------+-------------------------------+

    Parameters
    ----------
    {sites}
    {huc}
    {bBox}
    {countyCd}
    {agencyCd}
    {stateCd}
    {altMin}
    {altMax}
    {aquiferCd}
    {endDT}
    {localAquiferCd}
    {modifiedSince}
    {parameterCd}
    {period}
    {siteStatus}
    {siteType}
    {startDT}
    {holeDepthMin}
    {holeDepthMax}
    {wellDepthMin}
    {wellDepthMax}"""
    tsutils._printiso(
        nwis_gwlevels(
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
            aquiferCd=aquiferCd,
            localAquiferCd=localAquiferCd,
            wellDepthMin=wellDepthMin,
            wellDepthMax=wellDepthMax,
            holeDepthMin=holeDepthMin,
            holeDepthMax=holeDepthMax,
            period=period,
            startDT=startDT,
            endDT=endDT,
        )
    )


def nwis_gwlevels(
    sites=None,
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
    aquiferCd=None,
    localAquiferCd=None,
    wellDepthMin=None,
    wellDepthMax=None,
    holeDepthMin=None,
    holeDepthMax=None,
):
    from tsgettoolbox.services.usgs import nwis as placeholder

    url = r"http://waterservices.usgs.gov/nwis/gwlevels/"
    r = resource(
        url,
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
        aquiferCd=aquiferCd,
        localAquiferCd=localAquiferCd,
        wellDepthMin=wellDepthMin,
        wellDepthMax=wellDepthMax,
        holeDepthMin=holeDepthMin,
        holeDepthMax=holeDepthMax,
        period=period,
        startDT=startDT,
        endDT=endDT,
    )

    return odo(r, pd.DataFrame)


@mando.command("nwis_measurements", formatter_class=HelpFormatter, doctype="numpy")
@tsutils.doc(nwis_docstrings)
def nwis_measurements_cli(
    sites=None,
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
    aquiferCd=None,
    localAquiferCd=None,
    wellDepthMin=None,
    wellDepthMax=None,
    holeDepthMin=None,
    holeDepthMax=None,
):
    r"""Download from the Measurements database of the USGS NWIS.

    {filter_descriptions}
    **Results**

    +---------------------------+-------------------------------------------+
    | Column                    | Description                               |
    +===========================+===========================================+
    | agency_cd                 | Agency code                               |
    +---------------------------+-------------------------------------------+
    | site_no                   | Site number                               |
    +---------------------------+-------------------------------------------+
    | measurement_nu            | Measurement number                        |
    +---------------------------+-------------------------------------------+
    | measurement_dt            | date of measurement (format = MMDDYYYY    |
    |                           | or Month/Day/Year. The user has options   |
    |                           | for the data output format)               |
    +---------------------------+-------------------------------------------+
    | tz_cd                     | Time zone offset. An ANSI SQL/92 time     |
    |                           | zone offset string. Some examples are     |
    |                           | '-07:00' (Eastern), '+02:00' (Eastern     |
    |                           | Europe), and '+03:30' (India).            |
    +---------------------------+-------------------------------------------+
    | q_meas_used_fg            | Flag indicates if the discharge           |
    |                           | measurement is marked used.               |
    +---------------------------+-------------------------------------------+
    | party_nm                  | an indication of who made the             |
    |                           | measurement and is usually populated with |
    |                           | a pair of initials separated with a slash |
    +---------------------------+-------------------------------------------+
    | site_visit_coll_agency_cd | What agency made the measurement at the   |
    |                           | site visit                                |
    +---------------------------+-------------------------------------------+
    | gage_height_va            | gage height as shown on the inside staff  |
    |                           | gage at the site or read off the recorder |
    |                           | inside the gage house in feet             |
    +---------------------------+-------------------------------------------+
    | discharge_va              | the computed discharge in cubic feet per  |
    |                           | second (cfs)                              |
    +---------------------------+-------------------------------------------+
    | measured_rating_diff      | measurement rating codes that denote the  |
    |                           | relative quality of the measurement       |
    +---------------------------+-------------------------------------------+
    | gage_va_change            | The amount the gage height changed while  |
    |                           | the measurement was being made in feet    |
    +---------------------------+-------------------------------------------+
    | gage_va_time              | The amount of time elapsed while the      |
    |                           | measurement was being made in decimal     |
    |                           | hours                                     |
    +---------------------------+-------------------------------------------+
    | control_type_cd           | condition of the rating control at the    |
    |                           | time of the measurement                   |
    +---------------------------+-------------------------------------------+
    | discharge_cd              | The adjustment code for the measured      |
    |                           | discharge                                 |
    +---------------------------+-------------------------------------------+
    | chan_nu                   | The channel number                        |
    +---------------------------+-------------------------------------------+
    | chan_name                 | The channel name                          |
    +---------------------------+-------------------------------------------+
    | meas_type                 | The channel measurement type              |
    +---------------------------+-------------------------------------------+
    | streamflow_method         | The channel discharge measurement method  |
    +---------------------------+-------------------------------------------+
    | velocity_method           | The channel velocity measurement method   |
    +---------------------------+-------------------------------------------+
    | chan_discharge            | The channel discharge in cubic feet per   |
    |                           | second                                    |
    +---------------------------+-------------------------------------------+
    | chan_width                | The channel width in feet                 |
    +---------------------------+-------------------------------------------+
    | chan_area                 | The channel area in square feet           |
    +---------------------------+-------------------------------------------+
    | chan_velocity             | The mean velocity in feet per second      |
    +---------------------------+-------------------------------------------+
    | chan_stability            | The stability of the channel material     |
    +---------------------------+-------------------------------------------+
    | chan_material             | The channel material                      |
    +---------------------------+-------------------------------------------+
    | chan_evenness             | The channel evenness from bank to bank    |
    +---------------------------+-------------------------------------------+
    | long_vel_desc             | The longitudinal velocity description     |
    +---------------------------+-------------------------------------------+
    | horz_vel_desc             | The horizontal velocity description       |
    +---------------------------+-------------------------------------------+
    | vert_vel_desc             | The vertical velocity description         |
    +---------------------------+-------------------------------------------+
    | chan_loc_cd               | The channel location code                 |
    +---------------------------+-------------------------------------------+
    | chan_loc_dist             | The channel location distance             |
    +---------------------------+-------------------------------------------+

    https://help.waterdata.usgs.gov/output-formats#streamflow_measurement_data

    Parameters
    ----------
    {sites}
    {huc}
    {bBox}
    {countyCd}
    {agencyCd}
    {stateCd}
    {altMin}
    {altMax}
    {aquiferCd}
    {endDT}
    {localAquiferCd}
    {modifiedSince}
    {parameterCd}
    {period}
    {siteStatus}
    {siteType}
    {startDT}
    {holeDepthMin}
    {holeDepthMax}
    {wellDepthMin}
    {wellDepthMax}"""
    tsutils._printiso(
        nwis_measurements(
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
            aquiferCd=aquiferCd,
            localAquiferCd=localAquiferCd,
            wellDepthMin=wellDepthMin,
            wellDepthMax=wellDepthMax,
            holeDepthMin=holeDepthMin,
            holeDepthMax=holeDepthMax,
            period=period,
            startDT=startDT,
            endDT=endDT,
        )
    )


def nwis_measurements(
    sites=None,
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
    aquiferCd=None,
    localAquiferCd=None,
    wellDepthMin=None,
    wellDepthMax=None,
    holeDepthMin=None,
    holeDepthMax=None,
):
    r"""Download from the Measurements database of the USGS NWIS."""
    from tsgettoolbox.services.usgs import nwis as placeholder

    url = r"http://nwis.waterdata.usgs.gov/XX/nwis/measurements"
    r = resource(
        url,
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
        aquiferCd=aquiferCd,
        localAquiferCd=localAquiferCd,
        wellDepthMin=wellDepthMin,
        wellDepthMax=wellDepthMax,
        holeDepthMin=holeDepthMin,
        holeDepthMax=holeDepthMax,
        period=period,
        startDT=startDT,
        endDT=endDT,
    )

    return odo(r, pd.DataFrame)


@mando.command("nwis_peak", formatter_class=HelpFormatter, doctype="numpy")
@tsutils.doc(nwis_docstrings)
def nwis_peak_cli(
    sites=None,
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
    aquiferCd=None,
    localAquiferCd=None,
    wellDepthMin=None,
    wellDepthMax=None,
    holeDepthMin=None,
    holeDepthMax=None,
):
    r"""Download from the Peak database of the USGS NWIS.

    {filter_descriptions}
    **Results**

    +---------------+--------------------------------------------+
    | Column        | Description                                |
    +===============+============================================+
    | agency_cd     | Agency Code                                |
    +---------------+--------------------------------------------+
    | site_no       | USGS station number                        |
    +---------------+--------------------------------------------+
    | peak_dt       | Date of peak streamflow                    |
    |               |   (format YYYY-MM-DD)                      |
    +---------------+--------------------------------------------+
    | peak_tm       | Time of peak streamflow                    |
    |               |   (24 hour format, 00:00 - 23:59)          |
    +---------------+--------------------------------------------+
    | peak_va       | Annual peak streamflow value in cfs        |
    +---------------+--------------------------------------------+
    | peak_cd       | Peak Discharge-Qualification codes         |
    |               |   (see explanation below)                  |
    +---------------+--------------------------------------------+
    | gage_ht       | Gage height for the associated peak        |
    |               |   streamflow in feet                       |
    +---------------+--------------------------------------------+
    | gage_ht_cd    | Gage height qualification codes            |
    +---------------+--------------------------------------------+
    | year_last_pk  | Peak streamflow reported is the highest    |
    |               |   since this year                          |
    +---------------+--------------------------------------------+
    | ag_dt         | Date of maximum gage-height for water year |
    |               |   (if not concurrent with peak)            |
    +---------------+--------------------------------------------+
    | ag_tm         | Time of maximum gage-height for water year |
    |               |   (if not concurrent with peak)            |
    +---------------+--------------------------------------------+
    | ag_gage_ht    | maximum Gage height for water year in feet |
    |               |   (if not concurrent with peak)            |
    +---------------+--------------------------------------------+
    | ag_gage_ht_cd | maximum Gage height code                   |
    +---------------+--------------------------------------------+

    Peak Streamflow-Qualification Codes(peak_cd):
    +---------+---------------------------------------------------+
    | peak_cd | Description                                          |
    +=========+======================================================+
    | 1       | Discharge is a Maximum Daily Average                 |
    +---------+------------------------------------------------------+
    | 2       | Discharge is an Estimate                             |
    +---------+------------------------------------------------------+
    | 3       | Discharge affected by Dam Failure                    |
    +---------+------------------------------------------------------+
    | 4       | Discharge less than indicated value,                 |
    |         |   which is Minimum Recordable Discharge at this site |
    +---------+------------------------------------------------------+
    | 5       | Discharge affected to unknown degree by              |
    |         |   Regulation or Diversion                            |
    +---------+------------------------------------------------------+
    | 6       | Discharge affected by Regulation or Diversion        |
    +---------+------------------------------------------------------+
    | 7       | Discharge is an Historic Peak                        |
    +---------+------------------------------------------------------+
    | 8       | Discharge actually greater than indicated value      |
    +---------+------------------------------------------------------+
    | 9       | Discharge due to Snowmelt, Hurricane,                |
    |         |   Ice-Jam or Debris Dam breakup                      |
    +---------+------------------------------------------------------+
    | A       | Year of occurrence is unknown or not exact           |
    +---------+------------------------------------------------------+
    | B       | Month or Day of occurrence is unknown or not exact   |
    +---------+------------------------------------------------------+
    | C       | All or part of the record affected by Urbanization,  |
    |         |    Mining, Agricultural changes, Channelization,     |
    |         |    or other                                          |
    +---------+------------------------------------------------------+
    | D       | Base Discharge changed during this year              |
    +---------+------------------------------------------------------+
    | E       | Only Annual Maximum Peak available for this year     |
    +---------+------------------------------------------------------+

    Gage height qualification codes(gage_ht_cd,ag_gage_ht_cd):
    +---------------+------------------------------------------------+
    | gage_ht_cd    | Description                                    |
    | ag_gage_ht_cd |                                                |
    +===============+================================================+
    | 1             | Gage height affected by backwater              |
    +---------------+------------------------------------------------+
    | 2             | Gage height not the maximum for the year       |
    +---------------+------------------------------------------------+
    | 3             | Gage height at different site and(or) datum    |
    +---------------+------------------------------------------------+
    | 4             | Gage height below minimum recordable elevation |
    +---------------+------------------------------------------------+
    | 5             | Gage height is an estimate                     |
    +---------------+------------------------------------------------+
    | 6             | Gage datum changed during this year            |
    +---------------+------------------------------------------------+

    Parameters
    ----------
    {sites}
    {huc}
    {bBox}
    {countyCd}
    {agencyCd}
    {stateCd}
    {altMin}
    {altMax}
    {aquiferCd}
    {endDT}
    {localAquiferCd}
    {modifiedSince}
    {parameterCd}
    {period}
    {siteStatus}
    {siteType}
    {startDT}
    {holeDepthMin}
    {holeDepthMax}
    {wellDepthMin}
    {wellDepthMax}"""
    tsutils._printiso(
        nwis_peak(
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
            aquiferCd=aquiferCd,
            localAquiferCd=localAquiferCd,
            wellDepthMin=wellDepthMin,
            wellDepthMax=wellDepthMax,
            holeDepthMin=holeDepthMin,
            holeDepthMax=holeDepthMax,
            period=period,
            startDT=startDT,
            endDT=endDT,
        )
    )


def nwis_peak(
    sites=None,
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
    aquiferCd=None,
    localAquiferCd=None,
    wellDepthMin=None,
    wellDepthMax=None,
    holeDepthMin=None,
    holeDepthMax=None,
):
    r"""Download from the Peak database of the USGS NWIS."""
    from tsgettoolbox.services.usgs import nwis as placeholder

    url = r"http://nwis.waterdata.usgs.gov/XX/nwis/peak"
    r = resource(
        url,
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
        aquiferCd=aquiferCd,
        localAquiferCd=localAquiferCd,
        wellDepthMin=wellDepthMin,
        wellDepthMax=wellDepthMax,
        holeDepthMin=holeDepthMin,
        holeDepthMax=holeDepthMax,
        period=period,
        startDT=startDT,
        endDT=endDT,
    )

    return odo(r, pd.DataFrame)


@mando.command("nwis_stat", formatter_class=HelpFormatter, doctype="numpy")
@tsutils.doc(nwis_docstrings)
def nwis_stat_cli(
    sites=None,
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
    statReportType=None,
    statType=None,
    missingData=None,
    statYearType=None,
):
    r"""Download from the Statistic database of the USGS NWIS.

    {filter_descriptions}
    **Returns**

    This returns a pandas DataFrame if using the Python API, or a text table to
    standard out if using the command line interface.  Both will have columns
    named according to the following table.

    +--------------+----------------+-----------------------------------------+
    | Column Name  | statReportType | Description                             |
    +==============+================+=========================================+
    | agency_cd    | all            | Agency code                             |
    +--------------+----------------+-----------------------------------------+
    | site_no      | all            | Site identification number              |
    +--------------+----------------+-----------------------------------------+
    | parameter_cd | all            | Parameter code                          |
    +--------------+----------------+-----------------------------------------+
    | station_nm   | all            | Site name                               |
    +--------------+----------------+-----------------------------------------+
    | loc_web_ds   | all            | Additional measurement description      |
    +--------------+----------------+-----------------------------------------+
    | year_nu      | monthly        | The year for which the statistics       |
    |              | annual         | apply.                                  |
    +--------------+----------------+-----------------------------------------+
    | month_nu     | monthly        | The month for which the statistics      |
    |              | daily          | apply.                                  |
    +--------------+----------------+-----------------------------------------+
    | day_nu       | daily          | The day for which the statistics apply. |
    +--------------+----------------+-----------------------------------------+
    | begin_yr     | daily          | First water year of data of daily mean  |
    |              |                | values for this day.                    |
    +--------------+----------------+-----------------------------------------+
    | end_yr       | daily          | Last water year of data of daily mean   |
    |              |                | values for this day.                    |
    +--------------+----------------+-----------------------------------------+
    | count_nu     | all            | Number of values used in the            |
    |              |                | calculation.                            |
    +--------------+----------------+-----------------------------------------+
    | max_va_yr    | daily          | Water year in which the maximum value   |
    |              |                | occurred.                               |
    +--------------+----------------+-----------------------------------------+
    | max_va       | daily          | Maximum of daily mean values for        |
    |              |                | this day.                               |
    +--------------+----------------+-----------------------------------------+
    | min_va_yr    | daily          | Water year in which the minimum value   |
    |              |                | occurred.                               |
    +--------------+----------------+-----------------------------------------+
    | min_va       | daily          | Minimum of daily mean values for        |
    |              |                | this day.                               |
    +--------------+----------------+-----------------------------------------+
    | mean_va      | all            | Mean of daily mean values for this day. |
    +--------------+----------------+-----------------------------------------+
    | p05_va       | daily          | 05 percentile of daily mean values for  |
    |              |                | this day.                               |
    +--------------+----------------+-----------------------------------------+
    | p10_va       | daily          | 10 percentile of daily mean values for  |
    |              |                | this day.                               |
    +--------------+----------------+-----------------------------------------+
    | p20_va       | daily          | 20 percentile of daily mean values for  |
    |              |                | this day.                               |
    +--------------+----------------+-----------------------------------------+
    | p25_va       | daily          | 25 percentile of daily mean values for  |
    |              |                | this day.                               |
    +--------------+----------------+-----------------------------------------+
    | p50_va       | daily          | 50 percentile (median) of daily         |
    |              |                | mean values for this day.               |
    +--------------+----------------+-----------------------------------------+
    | p75_va       | daily          | 75 percentile of daily mean values for  |
    |              |                | this day.                               |
    +--------------+----------------+-----------------------------------------+
    | p80_va       | daily          | 80 percentile of daily mean values for  |
    |              |                | this day.                               |
    +--------------+----------------+-----------------------------------------+
    | p90_va       | daily          | 90 percentile of daily mean values for  |
    |              |                | this day.                               |
    +--------------+----------------+-----------------------------------------+
    | p95_va       | daily          | 95 percentile of daily mean values for  |
    |              |                | this day.                               |
    +--------------+----------------+-----------------------------------------+

    Parameters
    ----------
    {sites}
    {agencyCd}
    {altMin}
    {altMax}
    {aquiferCd}
    {endDT}
    {localAquiferCd}
    {modifiedSince}
    {parameterCd}
    {period}
    {siteStatus}
    {siteType}
    {startDT}
    {drainAreaMin}
    {drainAreaMax}
    {holeDepthMin}
    {holeDepthMax}
    {wellDepthMin}
    {wellDepthMax}
    {statReportType}
    {statType}
    {missingData}
    {statYearType}"""
    tsutils._printiso(
        nwis_stat(
            sites=sites,
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
    )


def nwis_stat(
    sites=None,
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
    statReportType=None,
    statType=None,
    missingData=None,
    statYearType=None,
):
    r"""Download from the Statistic database of the USGS NWIS."""
    from tsgettoolbox.services.usgs import nwis as placeholder

    url = r"http://waterservices.usgs.gov/nwis/stat/"
    r = resource(
        url,
        sites=sites,
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

    return odo(r, pd.DataFrame)


@mando.command("epa_wqp", formatter_class=HelpFormatter, doctype="numpy")
@tsutils.doc(nwis_docstrings)
def epa_wqp_cli(
    bBox=None,
    lat=None,
    lon=None,
    within=None,
    countrycode=None,
    statecode=None,
    countycode=None,
    siteType=None,
    organization=None,
    siteid=None,
    huc=None,
    sampleMedia=None,
    characteristicType=None,
    characteristicName=None,
    pCode=None,
    activityId=None,
    startDateLo=None,
    startDateHi=None,
):
    r"""Download from the EPA Water Quality Portal.

    All of the keywords could be considered as subtractive filters of the
    stations.  Some of the keywords can result in very large number of stations
    being downloaded.

    Parameters
    ----------
    {bBox}
    lat : float
        [optional, default is None]

        Latitude for radial search, expressed in decimal degrees, WGS84

        The `lat`, `lon`, and `within` arguments are used together to form
        a circle on the Earth's surface for locating data-collection stations.
        Many stations outside the continental US do not have latitude and
        longitude referenced to WGS84 and therefore cannot be found using these
        parameters.

    lon : float
        [optional, default is None]

        Longitude for radial search, expressed in decimal degrees, WGS84

        The `lat`, `lon`, and `within` arguments are used together to form
        a circle on the Earth's surface for locating data-collection stations.
        Many stations outside the continental US do not have latitude and
        longitude referenced to WGS84 and therefore cannot be found using these
        parameters.

    within : float
        [optional, default is None]

        Distance for radial search, expressed in decimal miles

        The `lat`, `lon`, and `within` arguments are used together to form
        a circle on the Earth's surface for locating data-collection stations.
        Many stations outside the continental US do not have latitude and
        longitude referenced to WGS84 and therefore cannot be found using these
        parameters.

    countrycode : str
        [optional, default is None]

        Two-character Federal Information Processing Standard (FIPS) country
        code. (see domain service for available codes)

        FIPS country codes were established by the National Institute of
        Standards, publication 5-2.

    statecode : str
        [optional, default is None]

        Two-character Federal Information Processing Standard (FIPS) country
        code, followed bu a ":", followed by a two-digit FIPS state code. (see
        domain service for available codes)

        FIPS state codes were established by the National Institute of
        Standards, publication 5-2.

    countycode : str
        [optional, default is None]

        Two-character Federal Information Processing Standard (FIPS) country
        code, followed by a ":", followed by a two-digit FIPS state code,
        followed by a ":", followed by a three-digit FIPS county code. (see
        domain service for available codes)

        FIPS county codes were established by the National Institute of
        Standards, publication 5-2.

    siteType : str
        [optional, default is None]

        One or more case-sensitive site types, separated by semicolons. (see
        domain service for available site types)

        Restrict retrieval to stations with specified site type (location in
        the hydrologic cycle).  The MonitoringLocationTypeName for individual
        records may provide more detailed information about the type of
        individual stations.

    organization : str
        [optional, default is None]

        For USGS organization IDs, append an upper-case postal-service state
        abbreviation to "USGS-" to identify the USGS office managing the data
        collection station records. However, a few US states are serviced by
        one USGS office.::

            USGS-MA = Massachusetts and Rhode Island
            USGS-MD = Maryland, Delaware, and the District of Columbia
            USGS-PR = Caribbean Islands
            USGS-HI = Pacific Islands

        (see domain service for available organization IDs)

        USGS offices sometimes provide data for stations outside the political
        boundaries associated with the office's organization code. Use the
        statecode or countycode arguments to search for stations located within
        those political boundaries.

    siteid : str
        [optional, default is None]

        Concatenate an agency code, a hyphen ("-"), and a site-identification
        number.

        Each data collection station is assigned a unique
        site-identification number. Other agencies often use different site
        identification numbers for the same stations.

    {huc}

    sampleMedia : str
        [optional, default is None]

        One or more case-sensitive sample media, separated by semicolons. (see
        domain service for available sample media)

        Sample media are broad general classes, and may be subdivided in the
        retrieved data. Examine the data elements ActivityMediaName,
        ActivityMediaSubdivisionName, and ResultSampleFractionText for more
        detailed information.

    characteristicType : str
        [optional, default is None]

        One or more case-sensitive characteristic types (groupings) separated
        by semicolons. (see domain service for available characteristic types)

        These groups will be expanded as part of the ongoing collaboration
        between USGS and USEPA.

    characteristicName : str
        [optional, default is None]

        One or more case-sensitive characteristic names, separated by
        semicolons. (see domain service for available characteristic names)

        Characteristic names identify different types of environmental
        measurements. The names are derived from the USEPA Substance Registry
        System (SRS). USGS uses parameter codes for the same purpose and has
        associated most parameters to SRS names.

    pCode : str
        [optional, default is None]

        One or more five-digit USGS parameter codes, separated by semicolons.
        This is equivalent to "parameterCd" used in other USGS web services.

    activityId : str
        [optional, default is None]

        One or more case-sensitive activity IDs, separated by semicolons.
        Designator that uniquely identifies an activity within an organization.

    startDateLo : str
        [optional, default is None]

        Date of earliest desired data-collection activity.  A very wide range
        of date strings can be used but the closer to ISO 8601 the better.

    startDateHi : str
        [optional, default is None]

        Date of last desired data-collection activity.  A very wide range of
        date strings can be used but the closer to ISO 8601 the better."""
    tsutils._printiso(
        epa_wqp(
            bBox=bBox,
            lat=lat,
            lon=lon,
            within=within,
            countrycode=countrycode,
            statecode=statecode,
            countycode=countycode,
            siteType=siteType,
            organization=organization,
            siteid=siteid,
            huc=huc,
            sampleMedia=sampleMedia,
            characteristicType=characteristicType,
            characteristicName=characteristicName,
            pCode=pCode,
            activityId=activityId,
            startDateLo=startDateLo,
            startDateHi=startDateHi,
        )
    )


def epa_wqp(
    bBox=None,
    lat=None,
    lon=None,
    within=None,
    countrycode=None,
    statecode=None,
    countycode=None,
    siteType=None,
    organization=None,
    siteid=None,
    huc=None,
    sampleMedia=None,
    characteristicType=None,
    characteristicName=None,
    pCode=None,
    activityId=None,
    startDateLo=None,
    startDateHi=None,
):
    from tsgettoolbox.services.epa import wqp as placeholder

    url = r"https://www.waterqualitydata.us/Result/search"
    r = resource(
        url,
        bBox=bBox,
        lat=lat,
        lon=lon,
        within=within,
        countrycode=countrycode,
        statecode=statecode,
        countycode=countycode,
        siteType=siteType,
        organization=organization,
        siteid=siteid,
        huc=huc,
        sampleMedia=sampleMedia,
        characteristicType=characteristicType,
        characteristicName=characteristicName,
        pCode=pCode,
        activityId=activityId,
        startDateLo=startDateLo,
        startDateHi=startDateHi,
    )

    return odo(r, pd.DataFrame)


nwis.__doc__ = nwis_cli.__doc__

nwis_iv.__doc__ = nwis_iv_cli.__doc__
nwis_dv.__doc__ = nwis_dv_cli.__doc__
nwis_site.__doc__ = nwis_site_cli.__doc__
nwis_gwlevels.__doc__ = nwis_gwlevels_cli.__doc__
nwis_measurements.__doc__ = nwis_measurements_cli.__doc__
nwis_peak.__doc__ = nwis_peak_cli.__doc__
nwis_stat.__doc__ = nwis_stat_cli.__doc__
epa_wqp.__doc__ = epa_wqp_cli.__doc__
