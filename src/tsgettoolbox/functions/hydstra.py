"""
hydstra_ts          Kisters Hydstra Webservice - time series values
hydstra_catalog     Kisters Hydstra Webservice - variable catalog for a
                    station
hydstra_stations    Kisters Hydstra Webservice - station list for a server
"""

import cltoolbox
import pandas as pd
from cltoolbox.rst_text_formatter import RSTHelpFormatter as HelpFormatter
from toolbox_utils import tsutils

from tsgettoolbox import hydstra_utils as hu

hydstra_docstrings = {
    "server": r"""server
        Server name or base URL of Hydstra webserver.  This can be either
        a direct URL (normally up to but not including a '?') or it can be one
        of the following predetermined server names.

        +-------------+--------------------------------------------------------+
        | Name        | Description                                            |
        +=============+========================================================+
        | sjrwmd      | St. Johns Water Management District, Florida, USA      |
        |             | https://secure.sjrwmd.com/hydweb/cgi/webservice.exe    |
        +-------------+--------------------------------------------------------+
        | orangeco_ca | Orange County Public Works, California USA             |
        |             | http://Hydstra.OCPublicWorks.com/cgi/webservice.exe    |
        +-------------+--------------------------------------------------------+""",
    "station": r"""station
        This should be the short 'station identifier', not the longer 'station
        name'.""",
    "variable": r"""variable
        Name of variable or numeric variable code.  The list of available
        variables varies by server.  The following is a typical list of names
        and their associated numeric codes::

            Rainfall:in:             11.10
            Water_Elev_NAVD88:ft:   227.10
            Gauge Height:ft:        233.10
            Discharge:cfs:          262.17

        Other available variable codes for a given station can be determined
        using the hydstra_catalog command.""",
    "start_time": r"""start_time
        Date and time for start of requested period in ISO format.  For daily
        and longer intervals, use YYYY-MM-DD.  For sub-daily, use
        YYYY-MM-DD-hh-mm or YYYY-MM-DD-hh-mm-ss if necessary.""",
    "end_time": r"""end_time
        Date and time for end of requested period in ISO format.  For daily and
        longer intervals, use YYYY-MM-DD.  For sub-daily, use YYYY-MM-DD-hh-mm
        or YYYY-MM-DD-hh-mm-ss if necessary.""",
    "interval": r"""interval
        Time step of data to return.  Valid values are: year, month, day, hour,
        minute, second""",
    "provisional": r"""provisional
        Boolean: False (default) to skip provisional data. True to include it.
        In many cases, this means datasources A and AB respectively.
        Details may vary by server.""",
    "datasource": r"""datasource
        Hydstra databases include an attribute called 'datasource'.
        A given variable may be present as multiple timeseries with different
        datasources, each with various available periods of record and
        levels of quality assurance.

        For some servers, certain datasources are reserved for internal
        workflows and may be skipped by the hydstra_catalog command.

        Default is 'A' (for 'Archive') if not including provisional data.  The
        default for provisional data may vary by server.  For instance::

            sjrwmd          The default for including recent non-QA'ed
                            provisional data is 'AB', which returns the full
                            span, distinguished by different quality codes.  To
                            get only the provisional data, the 'X' datasource
                            would be used. There may be overlap in the time
                            spans of 'A' and 'X', during which the 'A' should
                            be preferred.

            orangeco_ca     There is no 'AB' datasource.  The 'TELEMETRY'
                            datasource contains the provisional data, which can
                            overlap with the 'A' datasource

        Required if provisional data is requested.""",
    "aggcode": r"""aggcode
        Aggregation code. defaults to 'tot' for rainfall, 'mean' for elevation
        and discharge.  Other values vary by server.  Required if variable
        specified by numeric code.""",
    "quality": r"""quality
        Boolean: False (default) provides no quality information.
        True to add a column containing a numeric quality code 0 to 255.
        Definitions of codes may vary by server.""",
    "maxqual": r"""maxqual
        Highest allowable numeric quality code, above which the value is
        considered missing.  May be specified even if a separate quality column
        is not requested.""",
    "tablefmt": r"""tablefmt
        Format for site or catalog table.  Allowable values include plain
        (default), csv, or any allowed value for the Python tabulate
        package.""",
    "isleep": r"""isleep
        Integer seconds to sleep between webservice calls to create the catalog
        table.  Default is zero.

        If HTTP errors occur, it may be due to web calls that come too fast, if
        the server is configured to interpret rapid calls as
        a denial-of-service attack.  If this happens, increase isleep.""",
    "activeonly": r"""activeonly
        Boolean: False (default) returns all stations.
        True returns only active stations.""",
    "latlong": r"""latlong
        Boolean: False (default) omits latitude and longitude from station
        table.  True includes them.""",
}


@cltoolbox.command("hydstra_ts", formatter_class=HelpFormatter)
@tsutils.doc(hydstra_docstrings)
def hydstra_ts_cli(
    server,
    station,
    variable,
    start_time,
    end_time,
    interval="day",
    provisional=False,
    datasource=None,
    aggcode=None,
    quality=False,
    maxqual=254,
):
    r"""global station:Kisters Hydstra Webservice - time series values

    Hydstra databases are generally organized into stations, datasources,
    and variables.

    Parameters
    ----------
    ${server}
    ${station}
    ${variable}
    ${start_time}
    ${end_time}
    ${interval}
    ${provisional}
    ${datasource}
    ${aggcode}
    ${quality}
    ${maxqual}

    """
    tsutils.printiso(
        hydstra_ts(
            server,
            station,
            variable,
            start_time,
            end_time,
            interval=interval,
            provisional=provisional,
            datasource=datasource,
            aggcode=aggcode,
            quality=quality,
            maxqual=maxqual,
        )
    )


@tsutils.copy_doc(hydstra_ts_cli)
def hydstra_ts(
    server,
    station,
    variable,
    start_time,
    end_time,
    interval="day",
    provisional=False,
    datasource=None,
    aggcode=None,
    quality=False,
    maxqual=254,
):
    """global station:Kisters Hydstra Webservice - time series values"""
    urlbase = hu.hydstra_get_server_url(server)
    variables = hu.hydstra_get_server_vars(server)
    sdate = tsutils.parsedate(start_time)
    edate = tsutils.parsedate(end_time)
    isdate = hu.datetime_to_dateint(sdate)
    iedate = hu.datetime_to_dateint(edate)
    # print(urlbase, variables, sdate, edate, isdate, iedate)

    # print('initial datasource: ', datasource)

    if datasource is None:
        if provisional is True:
            if server == "sjrwmd":
                datasource = "AB"
            elif server == "orangeco_ca":
                datasource = "TELEMETRY"
            else:
                raise ValueError(
                    tsutils.error_wrapper(
                        """
                        Must provide provisional datasource for this server.
                        """
                    )
                )
                datasource = ""  # for now, this presumably causes a 404 on the URL call
        else:
            datasource = "A"

    # check if variable in list, otherwise assume is a code and use directly
    try:
        varcode = variables[variable][0]
        directcode = False
    except KeyError:
        varcode = variable
        directcode = True

    if aggcode is None:
        if directcode is True:
            raise ValueError(
                tsutils.error_wrapper(
                    """
                    Must provide aggcode if supplying a variable code directly.
                    """
                )
            )
            datatype = ""
        try:
            datatype = variables[variable][1]
        except KeyError:
            datatype = aggcode
    else:
        # aggcode used directly, perhaps overriding default
        datatype = aggcode

    if datasource != "" and datatype != "":
        timeseries = hu.hydstra_get_ts(
            urlbase,
            station,
            datasource,
            datatype,
            isdate,
            iedate,
            varcode,
            interval=interval,
            quality=quality,
            maxqual=maxqual,
        )
    else:
        timeseries = pd.DataFrame()
    return timeseries


@cltoolbox.command("hydstra_catalog", formatter_class=HelpFormatter)
@tsutils.doc(hydstra_docstrings)
def hydstra_catalog_cli(server, station, tablefmt="csv", isleep=0):
    r"""global station:Kisters Hydstra Webservice - variable catalog for a station

    Creates a table of datasources and variables available for a station,
    including periods of record for each.

    Parameters
    ----------
    ${server}
    ${station}
    ${tablefmt}
    ${isleep}

    """
    catalogdf = hydstra_catalog(server, station, isleep=isleep)
    tsutils.printiso(catalogdf, tablefmt=tablefmt, headers="keys", showindex=False)


@tsutils.copy_doc(hydstra_catalog_cli)
def hydstra_catalog(server, site_id, isleep=5):
    """global station:Kisters Hydstra Webservice - variable catalog for a station"""
    urlbase = hu.hydstra_get_server_url(server)
    skipds = hu.hydstra_get_server_skipds(server)
    catalogdf = hu.hydstra_get_station_catalog(
        urlbase, site_id, SkipDataSources=skipds, isleep=isleep
    )
    return catalogdf


@cltoolbox.command("hydstra_stations", formatter_class=HelpFormatter)
@tsutils.doc(hydstra_docstrings)
def hydstra_stations_cli(server, activeonly=False, latlong=False, tablefmt="csv"):
    r"""global station:Kisters Hydstra Webservice - station list for a server

    Creates a table of stations available on the server.

    Parameters
    ----------
    ${server}
    ${activeonly}
    ${latlong}
    ${tablefmt}"""
    sitedf = hydstra_stations(server, activeonly=activeonly, latlong=latlong)
    tsutils.printiso(sitedf, headers="keys", tablefmt=tablefmt, showindex=False)


@tsutils.copy_doc(hydstra_stations_cli)
def hydstra_stations(server, activeonly=False, latlong=True):
    """global station:Kisters Hydstra Webservice - station list for a server"""
    urlbase = hu.hydstra_get_server_url(server)
    sitedf = hu.hydstra_get_stations(urlbase, activeonly=activeonly, latlong=latlong)
    return sitedf


if __name__ == "__main__":
    df = hydstra_ts(
        "orangeco_ca", "ALAMEDA", "11.50", "2015-01-01", "2016-01-01", aggcode="tot"
    )
    print(df)
    df = hydstra_ts(
        "orangeco_ca",
        "ALAMEDA",
        "11.50",
        "2014-12-31",
        "2020-01-01",
        aggcode="tot",
        interval="year",
    )
    print(df)
    df = hydstra_ts(
        "sjrwmd", "00530220", "Water_Elev_NAVD88:ft", "2000-01-01", "2001-01-01"
    )
    print(df)
    df = hydstra_ts(
        "sjrwmd",
        "00530220",
        "Water_Elev_NAVD88:ft",
        "2000-01-01",
        "2001-01-01",
        aggcode="maxmin",
        interval="month",
    )
    print(df)
