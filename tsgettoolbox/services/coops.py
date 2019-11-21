from __future__ import print_function
from __future__ import absolute_import

import logging
import os
from builtins import object
from collections import defaultdict
from io import BytesIO

from tsgettoolbox.odo import convert
from tsgettoolbox.odo import odo
from tsgettoolbox.odo import resource

import pandas as pd

import requests

from tstoolbox import tsutils

# NOAA/NOS Tides and Currents
# pd.read_csv('http://tidesandcurrents.noaa.gov/api/datagetter?
# begin_date=20130101&
# end_date=20130101&
# station=8454000&
# product=water_level&
# datum=mllw&
# units=metric&
# time_zone=gmt&
# application=web_services&
# format=csv',
#  index_col=0)


class NOS(object):
    def __init__(self, url, **query_params):
        params = {}
        # params["interval"] = "h"
        # params["units"] = "metric"
        # params["time_zone"] = "gmt"
        # params["datum"] = "mllw"
        params.update(query_params)
        try:
            params["begin_date"] = tsutils.parsedate(
                query_params["begin_date"], strftime="%Y%m%d"
            )
        except KeyError:
            pass
        try:
            params["end_date"] = tsutils.parsedate(
                query_params["end_date"], strftime="%Y%m%d"
            )
        except KeyError:
            pass
        params["format"] = "csv"
        params["application"] = "tsgettoolbox"
        self.url = url
        self.query_params = params


# Function to make `resource` know about the new NOS type.
@resource.register(r"http(s)?://tidesandcurrents\.noaa\.gov.*", priority=17)
def resource_nos(uri, **kwargs):
    return NOS(uri, **kwargs)


def core(data):
    req = requests.get(data.url, params=data.query_params)

    if os.path.exists("debug_tsgettoolbox"):
        logging.warning(req.url)
    req.raise_for_status()

    if (
        b"Error" in req.content
        or b"Wrong" in req.content
        or b"Range limit" in req.content
    ):
        df = pd.DataFrame()
        error = req.content
    else:
        df = pd.read_csv(BytesIO(req.content), index_col=0, parse_dates=True)
        error = ""
    return df, error


# Function to convert from NOS type to pd.DataFrame
@convert.register(pd.DataFrame, NOS)
def nos_to_df(data, **kwargs):
    settings_map = defaultdict(lambda: [{"metric": "", "english": ""}])
    settings_map["water_level"] = [
        {"metric": "m", "english": "ft"},
        "h",
    ]  # Preliminary or verified
    # water levels, depending
    # on availability.
    settings_map["air_temperature"] = [
        {"metric": "degC", "english": "degF"},
        "h",
    ]  # Air temperature
    # as measured at
    # the station.
    settings_map["water_temperature"] = [
        {"metric": "degC", "english": "degF"},
        "h",
    ]  # Water temperature
    # as measured at
    # the station.
    settings_map["wind"] = [{"metric": "m/s", "english": "ft/s"}, "h"]  # Wind speed,
    # direction, and gusts
    # as measured at the
    # station.
    settings_map["air_pressure"] = [
        {"metric": "mb", "english": "mb"},
        "h",
    ]  # Barometric pressure as
    # measured at the station.
    settings_map["air_gap"] = [
        {"metric": "m", "english": "ft"},
        "h",
    ]  # Air Gap (distance
    # between a bridge and the
    # water's surface) at the
    # station.
    settings_map["conductivity"] = [
        {"metric": "mS/cm", "english": "mS/cm"},
        "h",
    ]  # The water's
    # conductivity as
    # measured at the
    # station.
    settings_map["visibility"] = [
        {"metric": "km", "english": "nm"},
        "h",
    ]  # Visibility from the
    # station's visibility
    # sensor. A measure of
    # atmospheric clarity.
    settings_map["humidity"] = [
        {"metric": "percent", "english": "percent"},
        "h",
    ]  # Relative
    # humidity as
    # measured at
    # the station.
    settings_map["salinity"] = [
        {"metric": "PSU", "english": "PSU"},
        "h",
    ]  # Salinity and specific
    # gravity data for the
    # station.
    settings_map["hourly_height"] = [
        {"metric": "m", "english": "ft"},
        "h",
    ]  # Verified hourly height
    # water level data for the
    # station.
    settings_map["high_low"] = [
        {"metric": "m", "english": "ft"},
        None,
    ]  # Verified high/low water
    # level data for the
    # station.
    settings_map["daily_mean"] = [
        {"metric": "m", "english": "ft"},
        None,
    ]  # Verified daily mean
    # water level data for
    # the station.
    settings_map["monthly_mean"] = [
        {"metric": "m", "english": "ft"},
        None,
    ]  # Verified monthly mean
    # water level data for
    # the station.
    settings_map["one_minute_water_level"] = [
        {"metric": "m", "english": "ft"},
        None,
    ]  # One minute water level
    # data for the station.
    settings_map["predictions"] = [
        {"metric": "m", "english": "ft"},
        "h",
    ]  # 6 minute predictions
    # water level data for the
    # station.
    settings_map["datums"] = [
        {"metric": "m", "english": "ft"},
        None,
    ]  # datums data for the
    # currents stations.

    settings_map["currents"] = [
        {"metric": "m/s", "english": "ft/s"},
        "h",
    ]  # Currents data for
    # currents stations.

    if data.query_params["date"] is not None:
        ndf, error = core(data)
    elif (
        data.query_params["range"] is not None
        and data.query_params["begin_date"] is None
        and data.query_params["end_date"] is None
    ):
        ndf, error = core(data)
    elif (
        data.query_params["begin_date"] is not None
        and data.query_params["range"] is not None
    ):
        ndf, error = core(data)
    elif (
        data.query_params["begin_date"] is not None
        and data.query_params["end_date"] is not None
    ):
        sdate = tsutils.parsedate(data.query_params["begin_date"])
        edate = tsutils.parsedate(data.query_params["end_date"])

        ndf = pd.DataFrame()
        testdate = sdate
        while testdate < edate:
            data.query_params["begin_date"] = testdate.strftime("%Y%m%d")

            testdate = testdate + pd.Timedelta(days=31)
            if testdate > edate:
                testdate = edate

            data.query_params["end_date"] = testdate.strftime("%Y%m%d")

            df, error = core(data)
            ndf = ndf.combine_first(df)
    elif (
        data.query_params["end_date"] is not None
        and data.query_params["range"] is not None
    ):
        ndf, error = core(data)

    if len(ndf) == 0:
        raise ValueError(
            tsutils.error_wrapper(
                """
COOPS service returned the error "{0}".
""".format(
                    error
                )
            )
        )

    new_column_names = []
    for icolumn_name in ndf.columns:
        ncolumn_name = icolumn_name.lower().strip().replace(" ", "_")
        units = settings_map[ncolumn_name][0][data.query_params["units"]]
        unitstr = ncolumn_name
        if units != "":
            unitstr = ":".join([ncolumn_name, units])
        new_column_names.append(("NOS", data.query_params["station"], unitstr))
    ndf.columns = ["-".join(i).rstrip("-") for i in new_column_names]
    time_zone_name = data.query_params["time_zone"].upper()
    if time_zone_name == "GMT":
        time_zone_name = "UTC"
    ndf = ndf.tz_localize(time_zone_name)
    ndf.index.name = "Datetime:{0}".format(time_zone_name)
    return ndf


if __name__ == "__main__":
    """
    http://tidesandcurrents.noaa.gov/api/datagetter?begin_date=20020101
    &end_date=20020102&range=1&station=8720218&product=water_level
    """

    r = resource(
        r"http://tidesandcurrents.noaa.gov/api/datagetter",
        station="8720218",
        product="water_level",
        interval="h",
        units="metric",
        time_zone="gmt",
        datum="mllw",
        range=20,
        begin_date=None,
        end_date=None,
        date=None,
    )

    as_df = odo(r, pd.DataFrame)
    print("tidesandcurrents")
    print(as_df)

    r = resource(
        r"http://tidesandcurrents.noaa.gov/api/datagetter",
        station="8720218",
        product="water_temperature",
        interval="h",
        units="metric",
        time_zone="gmt",
        datum="mllw",
        begin_date="01/10/2002",
        range=2,
        end_date=None,
        date=None,
    )

    as_df = odo(r, pd.DataFrame)
    print("tidesandcurrents")
    print(as_df)

    r = resource(
        r"http://tidesandcurrents.noaa.gov/api/datagetter",
        station="8720218",
        product="water_level",
        interval="h",
        units="metric",
        time_zone="gmt",
        datum="mllw",
        begin_date="01/10/2002",
        range=5,
        end_date=None,
        date=None,
    )

    as_df = odo(r, pd.DataFrame)
    print("tidesandcurrents")
    print(as_df)

    r = resource(
        r"http://tidesandcurrents.noaa.gov/api/datagetter",
        station="8720218",
        product="air_temperature",
        interval="h",
        units="metric",
        time_zone="gmt",
        datum="mllw",
        end_date="01/10/2002",
        range=3,
        begin_date=None,
        date=None,
    )

    as_df = odo(r, pd.DataFrame)
    print("tidesandcurrents")
    print(as_df)

    r = resource(
        r"http://tidesandcurrents.noaa.gov/api/datagetter",
        station="8720218",
        product="water_level",
        interval="h",
        units="metric",
        time_zone="gmt",
        datum="mllw",
        begin_date="01/10/2002",
        end_date="2003-01-01",
        range=None,
        date=None,
    )

    as_df = odo(r, pd.DataFrame)
    print("tidesandcurrents")
    print(as_df)

    try:
        r = resource(
            r"http://tidesandcurrents.noaa.gov/api/datagetter",
            station="8720218",
            product="water_level",
            units="metric",
            time_zone="gmt",
            datum="mllw",
            begin_date=None,
            end_date=None,
            range=745,
            date=None,
        )
        as_df = odo(r, pd.DataFrame)
    except ValueError:
        print("Correct ValueError")
