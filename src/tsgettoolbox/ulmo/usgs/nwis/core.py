# -*- coding: utf-8 -*-
"""
    ulmo.usgs.core
    ~~~~~~~~~~~~~~

    This module provides direct access to `USGS National Water Information
    System`_ web services.

    .. _USGS National Water Information System: http://waterdata.usgs.gov/nwis

"""

import contextlib
import datetime
import io
import logging

import isodate
import requests

from tsgettoolbox.ulmo import util
from tsgettoolbox.ulmo.waterml import v1_1 as wml

INSTANTANEOUS_URL = "http://waterservices.usgs.gov/nwis/iv/"
DAILY_URL = "http://waterservices.usgs.gov/nwis/dv/"

# configure logging
LOG_FORMAT = "%(message)s"
logging.basicConfig(format=LOG_FORMAT)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def get_sites(
    service=None,
    input_file=None,
    sites=None,
    state_code=None,
    huc=None,
    bounding_box=None,
    county_code=None,
    parameter_code=None,
    site_type=None,
    **kwargs,
):
    """Fetches site information from USGS services.
    See the `USGS Site Service`_ documentation for a detailed description of options.
    For convenience, major options have been included with pythonic names.
    At least one major filter must be specified. Options that are not listed
    below may be provided as extra kwargs (i.e. keyword='argument') and will be
    passed along with the web services request. These extra keywords must match
    the USGS names exactly. The `USGS Site Service`_ website describes available
    keyword names and argument formats.

    .. _USGS Site Service: http://waterservices.usgs.gov/rest/Site-Service.html

    .. note::
        Only the options listed below have been tested and you may have mixed
        results retrieving data with extra options specified. Currently ulmo
        requests and parses data in the WaterML 1.x format. Some options are not
        available in this format.

    Parameters
    ----------
    service : {``None``, 'instantaneous', 'iv', 'daily', 'dv'}
        The service to use, either "instantaneous", "daily", or `None`
        (default).  If set to ``None``, then both services are used.  The
        abbreviations "iv" and "dv" can be used for "instantaneous" and "daily",
        respectively.
    input_file : ``None``, file path or file object
        If ``None`` (default), then the NWIS web services will be queried, but
        if a file is passed then this file will be used instead of requesting
        data from the NWIS web services.
    sites : str, iterable of strings or ``None``
        A major filter. The site(s) to use; lists will be joined by a ','.
        At least one major filter must be specified.
    state_code : str or ``None``
        A major filter. Two-letter state code used in ``stateCd`` parameter.
        At least one major filter must be specified.
    county_code : str, iterable of strings or ``None``
        A major filter. The 5 digit FIPS county code(s) used in the countyCd parameter;
        lists will be joined by a ','.
        At least one major filter must be specified.
    huc : str, iterable of strings or ``None``
        A major filter. The hydrologic unit code(s) to use; lists will be joined by a ','.
        At least one major filter must be specified.
    bounding_box : str, iterable of strings or ``None``
        A major filter. This bounding box used in the bBox parameter. The format is
        westernmost longitude, southernmost latitude, easternmost longitude, northernmost
        latitude; lists will be joined by a ','.
        At least one major filter must be specified.
    parameter_code : str, iterable of strings or ``None``
        Optional filter. Parameter code(s) that will be passed as the ``parameterCd`` parameter;
        lists will be joined by a ','. This parameter represents the following USGS website
        input: Sites serving parameter codes
    site_type : str, iterable of strings or ``None``
        Optional filter. The type(s) of site used in ``siteType`` parameter;
        lists will be joined by a ','.

    Returns
    -------
    return_sites : dict
        a python dict with site codes mapped to site information
    """
    if input_file is None:
        # Checking to see if the correct amount of major filters are being used.
        # The NWIS site requires only one major filter to be used at a time.
        major_filters = [sites, state_code, huc, bounding_box, county_code]

        if not any(major_filters):
            error_msg = (
                "*At least one* of the following major filters must be supplied: "
                "sites, state_code, huc, bounding_box, country_code."
            )
            raise ValueError(error_msg)

        if len([_f for _f in major_filters if _f]) > 1:
            error_msg = (
                "*Only one* of the following major filters can be supplied:"
                "sites, state_code, huc, bounding_box, country_code."
            )
            raise ValueError(error_msg)

        url_params = {"format": "waterml"}

        if state_code:
            url_params["stateCd"] = state_code

        if sites:
            url_params["sites"] = _as_str(sites)

        if huc:
            url_params["hucs"] = _as_str(huc)

        if bounding_box:
            url_params["bBox"] = _as_str(bounding_box)

        if county_code:
            url_params["countyCd"] = _as_str(county_code)

        if site_type:
            url_params["siteType"] = _as_str(site_type)

        if parameter_code:
            url_params["parameterCd"] = _as_str(parameter_code)

        url_params |= kwargs

        if not service:
            return_sites = {}
            for service in ["daily", "instantaneous"]:
                new_sites = get_sites(
                    sites=sites,
                    state_code=state_code,
                    huc=huc,
                    bounding_box=bounding_box,
                    county_code=county_code,
                    parameter_code=parameter_code,
                    site_type=site_type,
                    service=service,
                    input_file=input_file,
                    **kwargs,
                )
                return_sites |= new_sites
            return return_sites

        url = _get_service_url(service)
        log.info(f"making request for sites: {url}")
        req = requests.get(url, params=url_params)
        log.info(f"processing data from request: {req.request.url}")
        req.raise_for_status()
        input_file = io.BytesIO(util.to_bytes(req.content))

    with _open_input_file(input_file) as content_io:
        return_sites = wml.parse_site_infos(content_io)

    return_sites = {
        code: _extract_site_properties(site) for code, site in return_sites.items()
    }

    return return_sites


def get_site_data(
    site_code,
    service=None,
    parameter_code=None,
    statistic_code=None,
    start=None,
    end=None,
    period=None,
    modified_since=None,
    input_file=None,
    methods=None,
    **kwargs,
):
    """Fetches site data.

    Parameters
    ----------
    site_code : str
        The site code of the site you want to query data for.
    service : {``None``, 'instantaneous', 'iv', 'daily', 'dv'}
        The service to use, either "instantaneous", "daily", or ``None``
        (default).  If set to ``None``, then both services are used.  The
        abbreviations "iv" and "dv" can be used for "instantaneous" and "daily",
        respectively.
    parameter_code : str
        Parameter code(s) that will be passed as the parameterCd parameter.
    statistic_code : str
        Statistic code(s) that will be passed as the statCd parameter
    start : ``None`` or datetime (see :ref:`dates-and-times`)
        Start of a date range for a query. This parameter is mutually exclusive
        with period (you cannot use both). It should not be older than
        1910-1-1 for 'iv' and 1851-1-1 for 'dv' services.
    end : ``None`` or datetime (see :ref:`dates-and-times`)
        End of a date range for a query. This parameter is mutually exclusive
        with period (you cannot use both).
    period : {``None``, str, datetime.timedelta}
        Period of time to use for requesting data. This will be passed along as
        the period parameter. This can either be 'all' to signal that you'd like
        the entire period of record (down to 1910-1-1 for 'iv', 1851-1-1 for 'dv'),
        or string in ISO 8601 period format (e.g. 'P1Y2M21D' for a period of one year,
        two months and 21 days) or it can be a datetime.timedelta object representing
        the period of time. This parameter is mutually exclusive with start/end dates.
    modified_since : ``None`` or datetime.timedelta
        Passed along as the modifiedSince parameter.
    input_file : ``None``, file path or file object
        If ``None`` (default), then the NWIS web services will be queried, but
        if a file is passed then this file will be used instead of requesting
        data from the NWIS web services.
    methods : ``None``, str or Python dict
        If ``None`` (default), it's assumed that there is a single method for
        each parameter. This raises an error if more than one method ids are
        encountered. If str, this is the method id for the requested
        parameter/s and can use "all" if method ids are not known beforehand. If
        dict, provide the parameter_code to method id mapping. Parameter's
        method id is specific to site.

    Returns
    -------
    data_dict : dict
        a python dict with parameter codes mapped to value dicts
    """
    url_params = {"format": "waterml", "site": site_code}
    if type(parameter_code) is str:
        url_params["parameterCd"] = parameter_code
    elif type(parameter_code) is list:
        url_params["parameterCd"] = ",".join(parameter_code)
    if statistic_code:
        url_params["statCd"] = statistic_code
    if modified_since:
        url_params["modifiedSince"] = isodate.duration_isoformat(modified_since)

    if start is not None and end is not None and period is not None:
        raise ValueError(
            "must use either a date range with start/end OR a " "period, but not both"
        )
    if period is not None:
        if isinstance(period, str):
            if period == "all":
                if service in ("iv", "instantaneous"):
                    start = datetime.datetime(1910, 1, 1)
                elif service in ("dv", "daily"):
                    start = datetime.datetime(1851, 1, 1)
            else:
                url_params["period"] = period
        elif isinstance(period, datetime.timedelta):
            url_params["period"] = isodate.duration_isoformat(period)

    if service in ("dv", "daily"):
        datetime_formatter = isodate.date_isoformat
    else:
        datetime_formatter = isodate.datetime_isoformat
    if start is not None:
        start_datetime = util.convert_datetime(start)
        url_params["startDT"] = datetime_formatter(start_datetime)
    if end is not None:
        end_datetime = util.convert_datetime(end)
        url_params["endDT"] = datetime_formatter(end_datetime)

    if service is not None:
        url_params |= kwargs
        values = _get_site_values(
            service, url_params, input_file=input_file, methods=methods
        )
    else:
        kw = dict(
            parameter_code=parameter_code,
            statistic_code=statistic_code,
            start=start,
            end=end,
            period=period,
            modified_since=modified_since,
            input_file=input_file,
            methods=methods,
        )
        kw |= kwargs
        values = get_site_data(site_code, service="daily", **kw)
        values.update(get_site_data(site_code, service="instantaneous", **kw))

    return values


def _as_str(arg):
    """if arg is a list, convert to comma delimited string"""
    return arg if isinstance(arg, str) else ",".join(arg)


def _extract_site_properties(site):
    rename_properties = [
        ("county_cd", "county"),
        ("huc_cd", "huc"),
        ("site_type_cd", "site_type"),
        ("state_cd", "state_code"),
    ]
    site_properties = site["site_property"]
    for old, new in rename_properties:
        if old in site_properties:
            site[new] = site_properties[old]
            del site_properties[old]

    if len(site_properties) == 0:
        del site["site_property"]
    else:
        site["site_property"] = site_properties

    return site


def _get_service_url(service):
    if service in ("daily", "dv"):
        return DAILY_URL
    if service in ("instantaneous", "iv"):
        return INSTANTANEOUS_URL
    raise ValueError(
        "service must be either 'daily' ('dv') or " "'instantaneous' ('iv')"
    )


def _get_site_values(service, url_params, input_file=None, methods=None):
    """downloads and parses values for a site

    returns a values dict containing variable and data values
    """
    if input_file is None:
        query_isodate = isodate.datetime_isoformat(datetime.datetime.now())
        service_url = _get_service_url(service)

        try:
            req = requests.get(service_url, params=url_params)
        except requests.exceptions.ConnectionError:
            log.info(
                f"There was a connection error with query:\n\t{service_url}\n\t{url_params}"
            )
            return {}
        log.info(f"processing data from request: {req.request.url}")

        if req.status_code != 200:
            return {}
        input_file = io.BytesIO(util.to_bytes(req.content))
    else:
        query_isodate = None

    with _open_input_file(input_file) as content_io:
        data_dict = wml.parse_site_values(content_io, query_isodate, methods=methods)

        for variable_dict in list(data_dict.values()):
            variable_dict["site"] = _extract_site_properties(variable_dict["site"])

    return data_dict


@contextlib.contextmanager
def _open_input_file(input_file):
    """helper context manager. If input_file is a string then it yields an open
    file handler, closing it afterwards. If input_file is already a file handler
    then it just yields the same file handler without closing.
    """
    if isinstance(input_file, str):
        with open(input_file, "rb") as content_io:
            yield content_io
    elif hasattr(input_file, "read"):
        yield input_file
