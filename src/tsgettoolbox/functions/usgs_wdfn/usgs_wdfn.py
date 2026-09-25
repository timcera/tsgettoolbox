"""
wdfn_agency_codes(*args, **kwargs):
wdfn_altitude_datums(*args, **kwargs):
wdfn_aquifer_codes(*args, **kwargs):
wdfn_aquifer_types(*args, **kwargs):
wdfn_channel_measurements(*args, **kwargs):
wdfn_citations(*args, **kwargs):
wdfn_combined_metadata(*args, **kwargs):
wdfn_continuous(*args, **kwargs):
wdfn_coordinate_accuracy_codes(*args, **kwargs):
wdfn_coordinate_datum_codes(*args, **kwargs):
wdfn_coordinate_method_codes(*args, **kwargs):
wdfn_counties(*args, **kwargs):
wdfn_countries(*args, **kwargs):
wdfn_daily(*args, **kwargs):
wdfn_field_measurements_metadata(*args, **kwargs):
wdfn_field_measurements(*args, **kwargs):
wdfn_hydrologic_unit_codes(*args, **kwargs):
wdfn_latest_continuous(*args, **kwargs):
wdfn_latest_daily(*args, **kwargs):
wdfn_latest_field_measurements(*args, **kwargs):
wdfn_medium_codes(*args, **kwargs):
wdfn_method_categories(*args, **kwargs):
wdfn_method_citations(*args, **kwargs):
wdfn_methods(*args, **kwargs):
wdfn_monitoring_locations(*args, **kwargs):
wdfn_national_aquifer_codes(*args, **kwargs):
wdfn_parameter_codes(*args, **kwargs):
wdfn_peaks(*args, **kwargs):
wdfn_reliability_codes(*args, **kwargs):
wdfn_site_types(*args, **kwargs):
wdfn_states(*args, **kwargs):
wdfn_statistic_codes(*args, **kwargs):
wdfn_time_series_metadata(*args, **kwargs):
wdfn_time_series_methods(*args, **kwargs):
wdfn_time_series_revisions(*args, **kwargs):
wdfn_time_zone_codes(*args, **kwargs):
wdfn_topographic_codes(*args, **kwargs):
"""

# Standard library imports
import datetime as dt
import inspect
import re
import textwrap
import warnings
from collections import OrderedDict
from pathlib import Path
from typing import Any, Literal
from urllib.parse import quote

# Third party imports
import async_retriever as ar
import numpy as np
import pandas as pd

# First party imports
from tsgettoolbox import utils

__all__ = [
    "wdfn_agency_codes",
    "wdfn_altitude_datums",
    "wdfn_aquifer_codes",
    "wdfn_aquifer_types",
    "wdfn_channel_measurements",
    "wdfn_citations",
    "wdfn_combined_metadata",
    "wdfn_continuous",
    "wdfn_coordinate_accuracy_codes",
    "wdfn_coordinate_datum_codes",
    "wdfn_coordinate_method_codes",
    "wdfn_counties",
    "wdfn_countries",
    "wdfn_daily",
    "wdfn_field_measurements",
    "wdfn_field_measurements_metadata",
    "wdfn_hydrologic_unit_codes",
    "wdfn_latest_continuous",
    "wdfn_latest_daily",
    "wdfn_latest_field_measurements",
    "wdfn_medium_codes",
    "wdfn_method_categories",
    "wdfn_method_citations",
    "wdfn_methods",
    "wdfn_monitoring_locations",
    "wdfn_national_aquifer_codes",
    "wdfn_parameter_codes",
    "wdfn_peaks",
    "wdfn_reliability_codes",
    "wdfn_site_types",
    "wdfn_states",
    "wdfn_statistic_codes",
    "wdfn_time_series_metadata",
    "wdfn_time_series_methods",
    "wdfn_time_series_revisions",
    "wdfn_time_zone_codes",
    "wdfn_topographic_codes",
]

warnings.filterwarnings("ignore")

utils.set_cache_env("usgs_wdfn")

_ts_databases = [
    "channel-measurements",
    "continuous",
    "daily",
    "field-measurements",
    "latest-continuous",
    "latest-daily",
    "latest-field-measurements",
    "peaks",
]


def make_list_all_str(value):
    """
    Convert a value to a list of strings.

    If the value is a string, it is split on commas and returned as a list of
    strings.  If the value is a list or tuple, it is returned as a list of
    strings.  If the value is None, an empty list is returned.  If the value
    is any other type, it is returned as a list of strings.
    """
    if isinstance(value, str):
        return [i.strip() for i in value.split(",")]
    if isinstance(value, (list, tuple)):
        return [str(i) for i in value]
    return [] if value is None else [str(value)]


def docstring_wrapper(text, indent=4):
    """
    Wrap a docstring to 75 characters and indent it by 8 spaces.

    Used primarily by the "wdfn_*" functions to reformat the help strings into
    docstring format.

      - accounts for single-level lists, and
      - keeps links on a single line.
    """
    nline = []
    for lne in text.splitlines():
        line = lne.strip()
        if not line:
            nline.append("")
            continue
        if line[0] in ["-", "*", "+"]:
            nline.extend(
                iter(
                    textwrap.wrap(
                        line,
                        width=75,
                        initial_indent=" " * (indent + 8),
                        subsequent_indent=" " * (indent + 10),
                    )
                )
            )
        else:
            nline.extend(
                iter(
                    textwrap.wrap(
                        line,
                        width=75,
                        initial_indent=" " * (indent + 4),
                        subsequent_indent=" " * (indent + 4),
                    )
                )
            )
    rtext = "\n".join(nline)
    for match in [
        re.search(r"(?s)(\[http.*?\][\n ]*\(http.*?\))", rtext),
        re.search(r"(?s)(\][\n ]*\(http.*?\))", rtext),
    ]:
        if match:
            for lne in match.groups():
                rtext = rtext.replace(
                    lne, lne.strip().replace("\n", "").replace(" ", "")
                )
    return rtext


def wdfn(db_name, **kwargs):
    """
    Retrieve data.

    This function is a wrapper around the USGS Water Data for the Nation API.
    It takes keyword arguments that correspond to the queryable parameters
    in the API.  The function will call the appropriate function to retrieve
    the data and return a pandas DataFrame.

    Parameters
    ----------
    **kwargs : dict
        Keyword arguments that correspond to the queryable parameters in the
        API.  See the docstring for each of the functions generated by the
        wdfn_factory decorator for more information on the available queryable
        parameters.
    """
    netrc_key = "api.waterdata.usgs.gov"
    # This will make sure the .netrc file has an entry for WDFN and if not,
    # will prompt for user credentials and create the .netrc file (if
    # necessary) and populate with the usgs_wdfn entry.  This is required for
    # the USGS Water Data for the Nation API.
    _email, token = utils.read_netrc(netrc_key)

    # Set default keyword values.
    if db_name in ["read_normal_observations", "read_interval_observations"]:
        kwargs["page_size"] = 10000
        kwargs["mime_type"] = "application/json"
        if db_name == "read_interval_observations":
            url = "https://api.waterdata.usgs.gov/statistics/v0/observationIntervals"
            kwargs["interval_type"] = kwargs.get("interval_type", "M")
        elif db_name == "read_normal_observations":
            url = "https://api.waterdata.usgs.gov/statistics/v0/observationNormals"
            kwargs["normal_type"] = kwargs.get("normal_type", "DOY")
    else:
        kwargs["limit"] = 50000
        kwargs["f"] = "json"
        url = f"https://api.waterdata.usgs.gov/ogcapi/v0/collections/{db_name}/items"

    time_delta = {
        "channel-measurements": dt.timedelta(days=3660),
        "continuous": dt.timedelta(minutes=15 * 49000),
        "daily": dt.timedelta(days=49000),
        "field-measurements": dt.timedelta(days=3660),
        "latest-continuous": dt.timedelta(minutes=15 * 49000),
        "latest-daily": dt.timedelta(days=49000),
        "latest-field-measurements": dt.timedelta(days=3660),
        "peaks": dt.timedelta(days=3660),
    }

    # pop off tsgettoolbox specific keywords that are not part of the WDFN API.
    ts_return_style = kwargs.pop("ts_return_style", "compact")

    if ts_return_style not in ["compact", "full"]:
        raise ValueError(
            f"Invalid ts_return_style: {ts_return_style}.  Must be 'compact' or 'full'."
        )

    monitoring_location_ids = [""]
    if ("monitoring_location_id" in kwargs) or ("monitoring_location_number" in kwargs):
        """Convert monitoring_location_number entries to monitoring_location_id."""
        agency_code = kwargs.get("agency_code", "USGS")
        monitoring_location_ids = (
            make_list_all_str(kwargs.get("monitoring_location_id", []))
            or [
                f"{agency_code}-{i}"
                for i in make_list_all_str(kwargs.get("monitoring_location_number", []))
            ]
            or [""]
        )
    if "monitoring_location_number" in kwargs:
        kwargs.pop("monitoring_location_number")

    parameter_codes = make_list_all_str(kwargs.get("parameter_code", [])) or [""]

    periods = [""]
    if "time" in kwargs:
        input_start, input_end = kwargs["time"].split("/")
        input_start = None if input_start == ".." else pd.to_datetime(input_start)
        input_end = None if input_end == ".." else pd.to_datetime(input_end)
        if input_start is None:
            input_start = pd.to_datetime("1900-01-01")
        if input_end is None:
            input_end = pd.Timestamp.now()

        periods = []
        period_start = input_start
        while period_start < input_end:
            period_end = min(period_start + time_delta[db_name], input_end)
            periods.append(
                f"{period_start.strftime('%Y-%m-%dT%H:%M:%S')}/{period_end.strftime('%Y-%m-%dT%H:%M:%S')}"
            )
            period_start = period_end

    kwargs_url = {key: quote(str(val)) for key, val in kwargs.items() if val}

    urls, kwds = zip(
        *(
            (
                url,
                {
                    "params": kwargs_url
                    | {
                        key: value
                        for key, value in {
                            "time": period,
                            "monitoring_location_id": monitoring_location_id,
                            "parameter_code": parameter_code,
                        }.items()
                        if value
                    },
                    "headers": {"X-Api-Key": token},
                },
            )
            for period in periods
            for monitoring_location_id in monitoring_location_ids
            for parameter_code in parameter_codes
        )
    )
    all_responses = ar.retrieve_json(urls, kwds)

    collect = []
    for resp in all_responses:
        if "links" in resp:
            for link in resp["links"]:
                if link["rel"] == "next":
                    raise ValueError(
                        f"Query returned more than {len(resp['features'])} records.  "
                        f"Please use a more restrictive query."
                    )
        inner = pd.json_normalize(resp["features"]).reset_index()
        collect.append(inner)

    collect = pd.concat(collect, ignore_index=True, sort=False)
    collect.columns = [i.split(".")[-1] for i in collect.columns]

    if ts_return_style == "compact":
        collect = collect.drop(
            columns=[
                "type",
                "geometry",
                "time_series_id",
                "approval_status",
                "id",
                "coordinates",
                "last_modified",
                "qualifier",
                "field_measurements_series_id",
                "time_of_day",
                "day",
                "month",
                "year",
            ],
            errors="ignore",
        )

        if "time" in collect.columns:
            time_col = "time"

        if "data" in collect.columns:
            """Comes from 'read_normal_observations' or 'read_interval_observations'."""
            collect = collect.explode("data")
            collect = pd.concat(
                [collect, pd.json_normalize(collect["data"])], axis="columns"
            )
            collect = collect.drop(columns=["data"])
            # The json_normalize will create a "values" column id just exploded
            # the current "values" column.  So rename the current "values" column
            # to "values_exploded" to be able to drop "values_exploded".
            collect = collect.rename(columns={"values": "values_exploded"})
            collect = collect.explode("values_exploded")
            collect = pd.concat(
                [collect, pd.json_normalize(collect["values_exploded"])], axis="columns"
            )
            collect = collect.drop(columns=["values_exploded"])

            collect = collect.drop(
                columns=[
                    "monitoring_location_name",
                    "site_type",
                    "site_type_code",
                    "country_code",
                    "state_code",
                    "county_code",
                    "parent_time_series_id",
                    "parent_statistic_id",
                    "parent_statistic_name",
                    "end_date",
                    "interval_type",
                    "computation_id",
                    "time_of_year_type",
                ],
                errors="ignore",
            )
            if "percentiles" in collect.columns:
                collect = collect.explode(["percentiles", "values"])
                collect["value"] = collect["value"].fillna(collect["values"])
                collect = collect.drop(columns=["values"])
            if "start_date" in collect.columns:
                time_col = "start_date"
                collect["start_date"] = pd.to_datetime(collect["start_date"])

        # Do it this way to enforce a particular order.
        stack_col_names = []
        if "monitoring_location_id" in collect.columns:
            stack_col_names.append("monitoring_location_id")
        if "parameter_code" in collect.columns:
            stack_col_names.append("parameter_code")
        if "statistic_id" in collect.columns:
            stack_col_names.append("statistic_id")
        if "computation" in collect.columns:
            stack_col_names.append("computation")
        if "percentiles" in collect.columns:
            stack_col_names.append("percentiles")
        if "unit_of_measure" in collect.columns:
            stack_col_names.append("unit_of_measure")

        if "time_of_year" in collect.columns:
            time_col = "time_of_year"
        collect = collect.sort_values(stack_col_names + [time_col])
        collect = collect.set_index(stack_col_names + [time_col])
        collect = collect.loc[~collect.index.duplicated()]
        collect = collect.unstack(level=stack_col_names)
        pretty_names = []
        for col in collect.columns:
            cols = []
            for i in col[1:-1]:
                if pd.isna(i):
                    cols.append("")
                elif i == "5":  # Need to make more generic - only captures percentile 5
                    cols.append("05")
                else:
                    cols.append(str(i))
            units = f":{col[-1]}"
            if "value" not in col[0]:
                units = ""
            pretty_names.append(
                f"{'_'.join(cols)}_{col[0]}{units}".replace("__", "_")
                .replace("_value", "")
                .replace("_arithmetic_mean", "_mean")
            )
        collect.columns = pretty_names

        id_cols = set()
        for col in collect.columns:
            id_cols.add(tuple(col.split("_")[:2]))
        for id_col in id_cols:
            for duplicate_data_columns in [
                [
                    col
                    for col in collect.columns
                    if "_sample_count" in col and tuple(col.split("_")[:2]) == id_col
                ],
                [
                    col
                    for col in collect.columns
                    if "_approval_status" in col and tuple(col.split("_")[:2]) == id_col
                ],
            ]:
                if duplicate_data_columns:
                    common_prefix = "_".join(duplicate_data_columns[0].split("_")[:2])
                    collect = collect.rename(
                        columns={
                            duplicate_data_columns[
                                0
                            ]: f"{common_prefix}_{duplicate_data_columns[0].split('_')[-1]}"
                        }
                    )
                    collect = collect.drop(
                        columns=duplicate_data_columns, errors="ignore"
                    )
        collect = collect.sort_index(axis="columns")

    return collect


def wdfn_factory(function_name):
    """
    Decorator to create functions specified by the "queries" as keywords.

    1. Read in the json file that contains the queries and their metadata.
    2. Create a function that has a keyword for each query and a docstring that contains the metadata.
    3. The function will call the appropriate function to retrieve the data and return a pandas DataFrame.

    """
    json_file = Path(__file__).parent / f"{function_name}_queryables.json"
    json_to_python_type = {
        "string": str,
        "integer": int,
        "number": float,
        "boolean": bool,
    }

    # The query name is the index of the "keywords" DataFrame.
    #
    # The name of the query is the index of the "keywords" DataFrame, the
    # "title" and "description" columns are used to create the docstring for
    # the function.  The "type" and "enum" are used to create type hints for
    # the keyword arguments.  Currently other columns in the "keywords"
    # DataFrame are ignored.
    fkeywords = pd.read_json(json_file, orient="records")
    keywords = pd.json_normalize(fkeywords["properties"]).set_index(fkeywords.index)

    if function_name in [
        "channel-measurements",
        "continuous",
        "daily",
        "field-measurements",
        "latest-continuous",
        "latest-daily",
        "latest-field-measurements",
        "peaks",
    ]:
        added_keywords = pd.DataFrame(
            data=[
                [
                    np.nan,
                    np.nan,
                    "ts_return_style",
                    "string",
                    "Return style, either 'compact' or 'full'",
                    ["compact", "full"],
                    "compact",
                ],
            ],
            columns=[
                "format",
                "x-ogc-role",
                "title",
                "type",
                "description",
                "enum",
                "default",
            ],
            index=["ts_return_style"],
        )
        keywords = pd.concat([keywords, added_keywords])

    parameters = OrderedDict()
    for query_name, row in keywords.iterrows():
        # Create the parameter for the function.
        param_type = json_to_python_type.get(row["type"], Any)

        if "enum" in row and isinstance(row["enum"], (list, tuple)):
            param_type = Literal[tuple(row["enum"])]

        parameters[query_name] = inspect.Parameter(
            query_name,
            inspect.Parameter.KEYWORD_ONLY,
            annotation=param_type,
            default=row["default"]
            if ("default" in row) and (row["default"] is not np.nan)  # noqa: PLW0177
            else None,
        )

    docstring = "    Parameters\n    ----------\n"
    for query_name, row in keywords.iterrows():
        if "description" in row:
            description = row["description"]
        elif "title" in row:
            description = row["title"]
        if query_name == "geometry":
            # For some reason, the geometry parameter has a blank description
            # in the json file, so we will add it manually.
            description = "The geometry parameter is used to filter the results by a specific geographic area.  The value should be a GeoJSON geometry object."
        description = (
            docstring_wrapper(description) if isinstance(description, str) else ""
        )

        # Create the docstring for the function.
        docstring += f"    {query_name}:\n{description}\n"

    def outer_func(inner_func):
        # Set keyword arguments for the function based on the "keywords"
        # DataFrame.
        sig = inspect.signature(inner_func)
        sig = sig.replace(parameters=list(parameters.values()))
        inner_func.__signature__ = sig

        docstring_header = docstring_wrapper(inner_func.__doc__, indent=0) or ""
        inner_func.__doc__ = docstring_header + "\n\n" + docstring

        return inner_func

    return outer_func


@wdfn_factory("agency-codes")
def wdfn_agency_codes(*args, **kwargs):
    """
    US:station:::USGS WDFN Agency codes as table

    Code identifying the agency or organization used for site information,
    data sources, and permitting agencies. Agency codes are fixed values
    assigned by the National Water Information System (NWIS).
    """
    return wdfn("agency-codes", *args, **kwargs)


@wdfn_factory("altitude-datums")
def wdfn_altitude_datums(*args, **kwargs):
    """
    US:station:::USGS WDFN Altitude datums as table

    The recommended vertical datum is NAVD88 (North American Vertical Datum
    of 1988) where applicable as stated in Office of Information Technical
    Memo 2002.01. NGVD29 (National Geodetic Vertical Datum of 1929) and
    NAVD88 are the only datums that can be converted on output. NWIS uses
    the North American Vertical Datum Conversions (VERTCON) of the National
    Geodetic Survey to convert from NGVD29 to NAVD88 or vice versa.
    Conversions to or from other vertical datums are not available.
    """
    return wdfn("altitude-datums", *args, **kwargs)


@wdfn_factory("aquifer-codes")
def wdfn_aquifer_codes(*args, **kwargs):
    """
    US:station:::USGS WDFN Aquifer codes as table

    Local aquifers in USGS data are identified by an aquifer name and
    geohydrologic unit code (a three-digit number related to the age of the
    formation, followed by a 4 or 5 character abbreviation for the geologic
    unit or aquifer name). For the age of formation (aquifer age),
    generally the smaller the number represents the younger the
    geohydrologic unit. Aquifer names and the definition of an aquifer can
    be very subjective. One rock unit may be called different aquifer names
    by different people. Local aquifers and layered aquifers are often
    grouped into larger named regional aquifers or aquifer systems. For
    example, the National Northern Atlantic Coastal Plain aquifer system
    (National aquifer) consists of five layered regional aquifers. Each
    regional aquifer is divided into two or more aquifers which may have
    a different name in each of the states in which the aquifer is found.
    """
    return wdfn("aquifer-codes", *args, **kwargs)


@wdfn_factory("aquifer-types")
def wdfn_aquifer_types(*args, **kwargs):
    """
    US:station:::USGS WDFN Aquifer types as table

    Groundwater occurs in aquifers under two different conditions. Where
    water only partly fills an aquifer, the upper surface is free to rise
    and decline. These aquifers are referred to as unconfined (or
    water-table) aquifers. Where water completely fills an aquifer that is
    overlain by a confining bed, the aquifer is referred to as a confined
    (or artesian) aquifer. When a confined aquifer is penetrated by a well,
    the water level in the well will rise above the top of the aquifer (but
    not necessarily above land surface).
    """
    return wdfn("aquifer-types", *args, **kwargs)


@wdfn_factory("channel-measurements")
def wdfn_channel_measurements(*args, **kwargs):
    """
    US:station::E:USGS WDFN Channel measurements as time-series

    Channel measurements taken as part of streamflow field measurements.
    """
    return wdfn("channel-measurements", *args, **kwargs)


@wdfn_factory("citations")
def wdfn_citations(*args, **kwargs):
    """
    US:station:::USGS WDFN Citations as table

    Citations associated with water measurement methods.
    """
    return wdfn("citations", *args, **kwargs)


@wdfn_factory("combined-metadata")
def wdfn_combined_metadata(*args, **kwargs):
    """
    US:station:::USGS WDFN Combined metadata as table

    This endpoint combines metadata from timeseries and field measurements
    collections by site.
    """
    return wdfn("citations", *args, **kwargs)


@wdfn_factory("continuous")
def wdfn_continuous(*args, **kwargs):
    """
    US:station::E:USGS WDFN Continuous data as time-series

    Continuous data are collected via automated sensors installed at
    a monitoring location. They are collected at a high frequency and often
    at a fixed 15-minute interval. Depending on the specific monitoring
    location, the data may be transmitted automatically via telemetry and
    be available on WDFN within minutes of collection, while other times
    the delivery of data may be delayed if the monitoring location does not
    have the capacity to automatically transmit data. Continuous data are
    described by parameter name and parameter code (pcode). These data
    might also be referred to as "instantaneous values" or "IV".
    """
    return wdfn("continuous", *args, **kwargs)


@wdfn_factory("coordinate-accuracy-codes")
def wdfn_coordinate_accuracy_codes(*args, **kwargs):
    """
    US:station:::USGS WDFN Coordinate accuracy codes as table

    Appropriate code on the schedule to indicate the accuracy of the
    latitude-longitude values.
    """
    return wdfn("coordinate-accuracy-codes", *args, **kwargs)


@wdfn_factory("coordinate-datum-codes")
def wdfn_coordinate_datum_codes(*args, **kwargs):
    """
    US:station:::USGS WDFN Coordinate datum codes as table

    Horizontal datum code for the latitude/longitude coordinates. There are
    currently more than 300 horizontal datums available for entry.
    """
    return wdfn("coordinate-datum-codes", *args, **kwargs)


@wdfn_factory("coordinate-method-codes")
def wdfn_coordinate_method_codes(*args, **kwargs):
    """
    US:station:::USGS WDFN Coordinate method codes as table

    Methods used to determine latitude-longitude values.
    """
    return wdfn("coordinate-method-codes", *args, **kwargs)


@wdfn_factory("counties")
def wdfn_counties(*args, **kwargs):
    """
    US:station:::USGS WDFN Counties as table

    The name of the county or county equivalent (parish, borough, planning
    reagion, etc.) in which the site is located. List includes Census
    Bureau FIPS county codes, names and associated Country and State.
    """
    return wdfn("counties", *args, **kwargs)


@wdfn_factory("countries")
def wdfn_countries(*args, **kwargs):
    """
    US:station:::USGS WDFN Countries as table

    FIPS country codes and names.
    """
    return wdfn("countries", *args, **kwargs)


@wdfn_factory("daily")
def wdfn_daily(*args, **kwargs):
    """
    US:station::D:USGS WDFN Daily data as time-series

    Daily data provide one data value to represent water conditions for the
    day. Throughout much of the history of the USGS, the primary water data
    available was daily data collected manually at the monitoring location
    once each day. With improved availability of computer storage and
    automated transmission of data, the daily data published today are
    generally a statistical summary or metric of the continuous data
    collected each day, such as the daily mean, minimum, or maximum value.
    Daily data are automatically calculated from the continuous data of the
    same parameter code and are described by parameter code and a statistic
    code. These data have also been referred to as “daily values” or “DV”.
    """
    return wdfn("daily", *args, **kwargs)


@wdfn_factory("field-measurements-metadata")
def wdfn_field_measurements_metadata(*args, **kwargs):
    """
    US:station:::USGS WDFN Field measurements metadata as table

    This endpoint provides metadata about field measurement collections,
    including when the earliest and most recent observations for
    a parameter occurred at a monitoring location and its units.
    """
    return wdfn("field-measurements-metadata", *args, **kwargs)


@wdfn_factory("field-measurements")
def wdfn_field_measurements(*args, **kwargs):
    """
    US:station::E:USGS WDFN Field measurements as time-series

    Field measurements are physically measured values collected during
    a visit to the monitoring location. Field measurements consist of
    measurements of gage height and discharge, and readings of groundwater
    levels, and are primarily used as calibration readings for the
    automated sensors collecting continuous data. They are collected at
    a low frequency, and delivery of the data in WDFN may be delayed due to
    data processing time.
    """
    return wdfn("field-measurements", *args, **kwargs)


@wdfn_factory("hydrologic-unit-codes")
def wdfn_hydrologic_unit_codes(*args, **kwargs):
    """
    US:station:::USGS WDFN Hydrologic unit codes as table

    Hydrologic units are geographic areas representing part or all of
    a surface drainage basin or distinct hydrologic feature identified by
    a unique number (HUC), and a name. The United States is divided and
    sub-divided into successively smaller hydrologic units which are
    classified into four levels: regions, sub-regions, accounting units,
    and cataloging units. Each unit consists of two to eight digits based
    on the four levels of classification in the hydrologic unit system.
    Additional information can be found at
    <https://water.usgs.gov/GIS/huc.html>.
    """
    return wdfn("hydrologic-unit-codes", *args, **kwargs)


@wdfn_factory("latest-continuous")
def wdfn_latest_continuous(*args, **kwargs):
    """
    US:station::E:USGS WDFN Latest continuous data as time-series

    This endpoint provides the most recent observation for each time series
    of continuous data. Continuous data are collected via automated sensors
    installed at a monitoring location. They are collected at a high
    frequency and often at a fixed 15-minute interval. Depending on the
    specific monitoring location, the data may be transmitted automatically
    via telemetry and be available on WDFN within minutes of collection,
    while other times the delivery of data may be delayed if the monitoring
    location does not have the capacity to automatically transmit data.
    Continuous data are described by parameter name and parameter code.
    These data might also be referred to as "instantaneous values" or "IV"
    """
    return wdfn("latest-continuous", *args, **kwargs)


@wdfn_factory("latest-daily")
def wdfn_latest_daily(*args, **kwargs):
    """
    US:station::D:USGS WDFN Latest daily data as time-series

    Daily data provide one data value to represent water conditions for the
    day. Throughout much of the history of the USGS, the primary water data
    available was daily data collected manually at the monitoring location
    once each day. With improved availability of computer storage and
    automated transmission of data, the daily data published today are
    generally a statistical summary or metric of the continuous data
    collected each day, such as the daily mean, minimum, or maximum value.
    Daily data are automatically calculated from the continuous data of the
    same parameter code and are described by parameter code and a statistic
    code. These data have also been referred to as “daily values” or “DV”.
    """
    return wdfn("latest-daily", *args, **kwargs)


@wdfn_factory("latest-field-measurements")
def wdfn_latest_field_measurements(*args, **kwargs):
    """
    US:station::E:USGS WDFN Latest field measurements as time-series

    Field measurements are physically measured values collected during
    a visit to the monitoring location. Field measurements consist of
    measurements of gage height and discharge, and readings of groundwater
    levels, and are primarily used as calibration readings for the
    automated sensors collecting continuous data. They are collected at
    a low frequency, and delivery of the data in WDFN may be delayed due to
    data processing time.
    """
    return wdfn("latest-daily", *args, **kwargs)


@wdfn_factory("medium-codes")
def wdfn_medium_codes(*args, **kwargs):
    """
    US:station:::USGS WDFN Medium codes as table

    Medium refers to the specific environmental medium from which the
    sample was collected. Medium type differs from site type because one
    site type, such as surface water, could have data for several media,
    such as water, bottom sediment, fish tissue, and others.
    """
    return wdfn("medium-codes", *args, **kwargs)


@wdfn_factory("method-categories")
def wdfn_method_categories(*args, **kwargs):
    """
    US:station:::USGS WDFN Method categories as table

    Categorical standards for methods describing the associated data's
    appropriateness for an intended use.
    """
    return wdfn("method-categories", *args, **kwargs)


@wdfn_factory("method-citations")
def wdfn_method_citations(*args, **kwargs):
    """
    US:station:::USGS WDFN Method citations as table

    Citation identifiers for water measurement methods.
    """
    return wdfn("method-citations", *args, **kwargs)


@wdfn_factory("methods")
def wdfn_methods(*args, **kwargs):
    """
    US:station:::USGS WDFN Methods as table

    Water measurement or water-quality analytical methods. Codes and
    descriptions defining a method for calculating or measuring the value
    of a water quality or quantity parameter. Method codes are associated
    with one or many parameter codes.
    """
    return wdfn("methods", *args, **kwargs)


@wdfn_factory("monitoring-locations")
def wdfn_monitoring_locations(*args, **kwargs):
    """
    US:station:::USGS WDFN Monitoring locations as table

    Location information is basic information about the monitoring location
    including the name, identifier, agency responsible for data collection,
    and the date the location was established. It also includes information
    about the type of location, such as stream, lake, or groundwater, and
    geographic information about the location, such as state, county,
    latitude and longitude, and hydrologic unit code (HUC).
    """
    return wdfn("monitoring-locations", *args, **kwargs)


@wdfn_factory("national-aquifer-codes")
def wdfn_national_aquifer_codes(*args, **kwargs):
    """
    US:station:::USGS WDFN National aquifer codes as table

    National aquifers are the principal aquifers or aquifer systems in the
    United States, defined as regionally extensive aquifers or aquifer
    systems that have the potential to be used as a source of potable
    water.
    """
    return wdfn("national-aquifer-codes", *args, **kwargs)


@wdfn_factory("parameter-codes")
def wdfn_parameter_codes(*args, **kwargs):
    """
    US:station:::USGS WDFN Parameter codes as table

    Parameter codes are 5-digit codes and associated descriptions used to
    identify the constituent measured and the units of measure. Some
    parameter code definitions include information about the sampling
    matrix, fraction, and methods used to measure the constituent. Some
    parameters are fixed-value (fxd) numeric codes having textual meaning
    (for example: parameter code 00041 is a weather code parameter, code of
    60 means rain), but more commonly represent a numeric value for
    chemical, physical, or biological data.
    """
    return wdfn("parameter-codes", *args, **kwargs)


@wdfn_factory("peaks")
def wdfn_peaks(*args, **kwargs):
    """
    US:station::E:USGS WDFN Peaks as time-series

    Annual peak flow values are the maximum instantaneous streamflow values
    recorded at a particular site for the entire water year from October
    1 to September 30. Note that the annual peak flow value may not occur
    at the same time the maximum water level occurs due to conditions such
    as backwater, tidal fluctuations, etc.
    """
    return wdfn("peaks", *args, **kwargs)


@wdfn_factory("reliability-codes")
def wdfn_reliability_codes(*args, **kwargs):
    """
    US:station:::USGS WDFN Reliability codes as table

    Code indicating the reliability of the data available for the site.
    """
    return wdfn("parameter-codes", *args, **kwargs)


@wdfn_factory("site-types")
def wdfn_site_types(*args, **kwargs):
    """
    US:station:::USGS WDFN Site types as table

    The hydrologic cycle setting or a man-made feature thought to affect
    the hydrologic conditions measured at a site. Primary and secondary
    site types associated with data collection sites. All sites have
    a primary site type, and may additionally have a secondary site type
    that further describes the location.
    """
    return wdfn("site-types", *args, **kwargs)


@wdfn_factory("states")
def wdfn_states(*args, **kwargs):
    """
    US:station:::USGS WDFN States as table

    State name or territory. Includes U.S. states and foreign entities
    classified under FIPS as 'Principal Administrative Divisions'.
    """
    return wdfn("states", *args, **kwargs)


@wdfn_factory("statistic-codes")
def wdfn_statistic_codes(*args, **kwargs):
    """
    US:station:::USGS WDFN Statistic codes as table

    Statistic codes.
    """
    return wdfn("statistic-codes", *args, **kwargs)


@wdfn_factory("time-series-metadata")
def wdfn_time_series_metadata(*args, **kwargs):
    """
    US:station:::USGS WDFN Time series metadata as table

    Daily data and continuous measurements are grouped into time series,
    which represent a collection of observations of a single parameter,
    potentially aggregated using a standard statistic, at a single
    monitoring location. This endpoint provides metadata about those time
    series, including their operational thresholds, units of measurement,
    and when the earliest and most recent observations in a time series
    occurred.
    """
    return wdfn("time-series-metadata", *args, **kwargs)


@wdfn_factory("time-series-methods")
def wdfn_time_series_methods(*args, **kwargs):
    """
    US:station:::USGS WDFN Time series methods as table

    The measurement or computation method in effect for a time series over
    a given interval. A time series can have many methods over its history;
    each record here represents one contiguous interval during which
    a single method was used. This collection is non-spatial: method
    records carry no geometry, so bbox/spatial filters are not supported.
    """
    return wdfn("time-series-methods", *args, **kwargs)


@wdfn_factory("time-series-revisions")
def wdfn_time_series_revisions(*args, **kwargs):
    """
    US:station::E:USGS WDFN Time series revisions as time-series

    Approved water data are considered published record, but on occasion
    changes or deletions (revisions) must be made to data after they are
    approved. Data revisions are rare because of USGS quality assurance
    practices, including documentation of all data before they are
    officially approved. This field contains text explanations for data
    revisions on a specific time series. Changes to data also are indicated
    with revision qualifier codes alongside the data. Text explanations
    before 2017 are not necessarily available online, but can be requested.
    This collection is non-spatial: revision records carry no geometry, so
    bbox/spatial filters are not supported.
    """
    return wdfn("time-series-revisions", *args, **kwargs)


@wdfn_factory("time-zone-codes")
def wdfn_time_zone_codes(*args, **kwargs):
    """
    US:station:::USGS WDFN Time zone codes as table

    The ISO 8601 standard defines time zone offsets as a numerical value
    added to a local time to convert it to Coordinated Universal Time
    (UTC), either as +hh:mm or -hh:mm, or represented by the letter Z to
    explicitly indicate UTC. For example, +05:30 means 5 hours and 30
    minutes ahead of UTC, while -08:00 means 8 hours behind UTC. The offset
    Z specifically signifies UTC.
    """
    return wdfn("time-zone-codes", *args, **kwargs)


@wdfn_factory("topographic-codes")
def wdfn_topographic_codes(*args, **kwargs):
    """
    US:station:::USGS WDFN Topographic codes as table

    The code that best describes the topographic setting in which the site
    is located. Topographic setting refers to the geomorphic features in
    the vicinity of the site.
    """
    return wdfn("topographic-codes", *args, **kwargs)


@wdfn_factory("read_normal_observations")
def wdfn_read_normal_observations(*args, **kwargs):
    """
    US:station::DM:USGS WDFN Statistical normal observations

    Day of year statistics
    Day of year statistics are calculated based on all approved historic
    observations for a numeric day of the year. For example, January 1,
    is day 1 of a calendar year and December 31 is day 365 of a non-leap
    year.

    Day of year statistics represent the expected conditions for
    a generic day of the year at a location based on approved historical
    observations.

    Day of year statistics available include the daily mean of daily
    means, daily maximum of daily means, daily median of daily means,
    daily minimum of daily means, and daily percentiles of daily means
    based on the same numeric day of the year in the period of record.

    Month of year statistics
    Month of year statistics are calculated based on all approved
    historic observations within a given month. For example, all October
    data ever collected and approved at a monitoring location would be
    included in one set of monthly statistics.

    Month of year statistics represent the expected conditions for
    a generic month of the year at a location based on approved
    historical observations.

    Month of year statistics available include monthly mean of daily
    means, monthly median of daily means, monthly maximum of daily
    means, monthly minimum of daily means, and monthly percentiles of
    daily means based on the same month in the period of record.
    """
    return wdfn("read_normal_observations", *args, **kwargs)


@wdfn_factory("read_interval_observations")
def wdfn_read_interval_observations(*args, **kwargs):
    """
    US:station::MA:USGS WDFN Statistical interval obs as time-series

    Monthly statistics
    Monthly statistics are calculated based on the approved data for
    a specific month. These statistics are reported for each month of
    each year available. For example, statistics would be available for
    June 1984.

    Monthly statistics represent the conditions that existed for
    a specific month when data was collected.

    Monthly statistics available include mean of daily means, maximum of
    daily means, median of daily means, minimum of daily means, and
    percentiles for of daily mean data for each specific month in the
    period of record.

    Annual statistics
    Annual statistics are calculated based on yearly records of approved
    data.

    Annual statistics are calculated for calendar years (starting
    January 1) and water years (starting October 1).

    Annual statistics represent the conditions that existed for
    a specific year (calendar or water) when data was collected.

    Annual statistics available include mean of daily means, maximum of
    daily means, median of daily means, minimum of daily means, and
    percentiles of daily means for each specific year in the period of
    record.
    """
    return wdfn("read_interval_observations", *args, **kwargs)


if __name__ == "__main__":
    try:
        print("USGS_GWLEVELS single")
        R = wdfn_field_measurements(
            monitoring_location_number="375907091432201",
            time="2017-01-01/2017-12-30",
        )
        print(R)
    except ValueError as e:
        print("Error: ", e)

    try:
        print("USGS_GWLEVELS multiple")
        R = wdfn_field_measurements(
            hydrologic_unit_code="03110201",
            time="2017-01-01/2017-12-30",
        )
        print(R)
    except ValueError as e:
        print("Error: ", e)

    print("USGS_IV single over a year")
    R = wdfn_continuous(
        monitoring_location_number="02325000",
        time="2015-07-01/2016-07-30",
    )
    print(R)

    print("USGS_IV single")
    R = wdfn_continuous(
        monitoring_location_number="02325000",
        time="2015-07-01/2015-07-30",
    )
    print(R)

    print("USGS_IV multiple")
    R = wdfn_continuous(
        monitoring_location_number="02325000,02239501",
        time="2015-07-01/2015-07-30",
    )
    print(R)

    print("USGS_DV")
    R = wdfn_daily(
        monitoring_location_number="02325000",
        time="2015-07-01/2015-07-30",
    )
    print(R)

    print("USGS_DV multiple")
    R = wdfn_daily(
        monitoring_location_number="02325000,02239501",
        time="2015-07-01/2015-07-30",
    )
    print(R)

    print("USGS_DAILY_STAT single")
    R = wdfn_read_interval_observations(monitoring_location_number="02325000")
    print(R)
    print(R.columns)

#    print("USGS_DAILY_STAT multiple")
#    R = wdfn_read_interval_observations(monitoring_location_number="02325000,02239501")
#    print(R)
#    print(R.columns)
#
#    print("USGS_MONTHLY_STAT single")
#    R = wdfn_read_normal_observations(
#        monitoring_location_number="01646500",
#        normal_type="MOY",
#    )
#    print(R)
#    print(R.columns)
#
#    print("USGS_MONTHLY_STAT single")
#    R = wdfn_read_normal_observations(
#        monitoring_location_number="01646500",
#        normal_type="DOY",
#    )
#    print(R)
#    print(R.columns)
#
#    print("USGS_MONTHLY_STAT multiple")
#    R = wdfn_read_interval_observations(
#        monitoring_location_number="02325000,01646500",
#        interval_type="WY",
#    )
#    print(R)
#    print(R.columns)
#
#    print("USGS_MONTHLY_STAT multiple")
#    R = wdfn_read_interval_observations(
#        monitoring_location_number="02325000,01646500",
#        interval_type="CY",
#    )
#    print(R)
#
#    print("USGS_ANNUAL_STAT single")
#    R = wdfn_read_interval_observations(
#        monitoring_location_number="01646500",
#        interval_type="WY",
#    )
#    print(R)
#
#    print("USGS_ANNUAL_STAT multple")
#    R = wdfn_read_interval_observations(
#        monitoring_location_number="01646500,02239501",
#        interval_type="WY",
#    )
#    print(R)
