# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import datetime
import io
import multiprocessing
import os
import xml
from multiprocessing import Pool
from random import randint
from time import sleep

import cftime
import numpy as np
import pandas as pd
import requests
import typic
from haversine import haversine_vector
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from siphon.ncss import NCSS

try:
    import ConfigParser as cp
except ImportError:
    import configparser as cp

from pydap.client import open_url
from tstoolbox import tsutils

from . import appdirs

dirs = appdirs.AppDirs("tsgettoolbox", "tsgettoolbox")


def read_api_key(service):
    # Read in API key
    if not os.path.exists(dirs.user_config_dir):
        os.makedirs(dirs.user_config_dir)
    configfile = os.path.join(dirs.user_config_dir, "config.ini")
    if not os.path.exists(configfile):
        with open(configfile, "w") as fp:
            fp.write(
                """

[{}]
api_key = ReplaceThisStringWithYourKey

""".format(
                    service
                )
            )
    # Make sure read only by user.
    os.chmod(configfile, 0o600)

    inifile = cp.ConfigParser()
    inifile.readfp(open(configfile, "r"))

    try:
        api_key = inifile.get(service, "api_key")
    except BaseException:
        with open(configfile, "a") as fp:
            fp.write(
                """

[{}]
api_key = ReplaceThisStringWithYourKey

""".format(
                    service
                )
            )
        api_key = "ReplaceThisStringWithYourKey"

    inifile.readfp(open(configfile, "r"))
    api_key = inifile.get(service, "api_key")
    if api_key == "ReplaceThisStringWithYourKey":
        raise ValueError(
            """
*
*   Need to edit {}
*   to add your API key that you got from {}.
*
""".format(
                configfile, service
            )
        )

    return api_key


def requests_retry_session(
    retries=3,
    backoff_factor=0.1,
    status_forcelist=(429, 500, 502, 503, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def read_csv(filename):
    sleep(randint(1, 5))
    req = requests_retry_session().get(filename)
    try:
        req.raise_for_status()
        return pd.read_csv(
            io.StringIO(req.content.decode("utf-8")), low_memory=False, parse_dates=True
        )
    except requests.exceptions.HTTPError:
        return pd.DataFrame()


def file_downloader(baseurl, station, startdate=None, enddate=None):
    """Generic NCEI/NOAA file downloader."""
    if startdate is None:
        startdate = datetime.datetime(1901, 1, 1)
    else:
        startdate = pd.to_datetime(startdate)
    if enddate is None:
        enddate = datetime.datetime.now()
    else:
        enddate = pd.to_datetime(enddate)

    station = station.split(":")[-1]

    urls = []
    for year in range(startdate.year, enddate.year + 1):
        urls.append(baseurl.format(**locals()))

    with Pool(processes=os.cpu_count()) as pool:
        # have your pool map the file names to dataframes
        df_list = pool.map(read_csv, urls)

    # reduce the list of dataframes to a single dataframe
    final = pd.concat(df_list)
    final = final.set_index("DATE")
    final.index.name = "Datetime"
    final.index = pd.to_datetime(final.index)
    final = final.sort_index()
    return final[startdate:enddate]


@tsutils.transform_args(start_date=pd.to_datetime, end_date=pd.to_datetime)
def pdap(
    url,
    lat,
    lon,
    latitude_name="lat",
    longitude_name="lon",
    time_name="time",
    variables=None,
    start_date=None,
    end_date=None,
    timeout=30,
):

    import numpy as np
    from haversine import haversine_vector

    if "dods" in url:
        dataset = open_dods(url, timeout=timeout)
    else:
        dataset = open_url(url, timeout=timeout)

    # Determine rlat and rlon index in the grid closest to target (lat, lon).
    lat_vals = dataset[latitude_name][:].data
    lon_vals = dataset[longitude_name][:].data

    nlat, nlon = np.meshgrid(lat_vals, lon_vals)

    nlat = nlat.flatten()
    nlon = nlon.flatten()

    ngrid = list(zip(nlat, nlon))
    distances = haversine_vector([(lat, lon)], ngrid, comb=True)
    closest = np.argmin(distances)

    rlat = int(np.argmax(lat_vals == nlat[closest]))
    rlon = int(np.argmax(lon_vals == nlon[closest]))

    # Get the start_data and end_date squared away.
    from coards import parse

    dtunits = dataset[time_name].attributes["units"]
    datetimes = pd.DatetimeIndex(
        [parse(value, dtunits) for value in dataset["time"][:].data]
    )

    datetimes = datetimes[start_date:end_date]

    # Determine the variable list.
    allvars = list(dataset.keys())
    allvars.remove(latitude_name)
    allvars.remove(longitude_name)
    allvars.remove(time_name)

    if variables is None:
        variables = allvars
    else:
        variables = tsutils.make_list(variables)
        for var in variables:
            if var not in allvars:
                raise ValueError(
                    tsutils.error_wrapper(
                        f"""
The variable "{var}" is not available.  The available variables are "{allvars}".
"""
                    )
                )

    df = pd.DataFrame()
    for dfvar in variables:
        ndf = pd.DataFrame(
            dataset[dfvar][start_date:end_date, rlat, rlon].data, index=datetimes
        )
        df = df.join(ndf, how="outer")
    return df


def dapdownloader(url, lat, lon, var, time_name="date", start_date=None, end_date=None):
    ncss = NCSS(url)

    avail_vars = list(ncss.variables)
    var = tsutils.make_list(var)

    if not var:
        var = avail_vars
    else:
        nvar = []
        for i in avail_vars:
            for j in var:
                if i.lower() == j.lower():
                    nvar.append(i)
        var = nvar

    query = ncss.query()

    if start_date is None:
        start_date = datetime.datetime(1, 1, 1)
    if end_date is None:
        end_date = datetime.datetime(9999, 1, 1)

    if (start_date is None) and (end_date is None):
        query.all_times()
    else:
        query.time_range(start_date, end_date)

    query.variables(*var)

    query.lonlat_point(lon, lat)

    ncss.validate_query(query)

    data = ncss.get_data(query)

    # Sometimes the variable name is different.  Remove all the other keys to
    # arrive at the variable name.
    data_keys = list(data.keys())
    # data_keys.remove(time_name)

    ndf = pd.DataFrame()
    for v in var:
        standard_name = avail_vars[v]["standard_name"]
        lname = avail_vars[v]["lname"]

        meta = ncss.metadata.variables[standard_name]["attributes"]
        scale_factor = meta.get("scale_factor", [1.0])[0]
        offset = meta.get("add_offset", [0.0])[0]
        missing_value = meta.get("missing_value", [None])[0]

        units = meta["units"]
        units = units.replace(" per ", "/")
        units = units.replace("millimeters", "mm")
        units = units.replace("square meter", "m^2")
        units = units.replace("meters", "m")
        units = units.replace("second", "s")
        units = units.replace("Percent", "%")
        units = units.replace("deg C", "degC")

        tdf = (
            pd.DataFrame(data[standard_name], index=data["date"]) * scale_factor
            + offset
        )
        tdf[tdf == missing_value] = None
        tdf.columns = [f"{lname}:{units}"]
        ndf = ndf.join(tdf, how="outer")
    return ndf


@typic.al
def opendap(
    url: str,
    lat: float,
    lon: float,
    variable_map,
    variables=None,
    start_date=None,
    end_date=None,
    tzname="UTC",
    time_name="date",
    missing_value=None,
    lat_name="lat",
    lon_name="lon",
    user_charset="ascii",
    single_var_url=False,
):
    from haversine import haversine_vector

    if variables is None:
        variables = list(variable_map.keys())
        variables.sort()
    else:
        variables = tsutils.make_list(variables)
        for variable in variables:
            if variable not in variable_map:
                raise ValueError(
                    tsutils.error_wrapper(
                        f"""
The variable "{variable}" is not available from this service.  The available
variables are "{variables_map.keys()}"."""
                    )
                )

    if single_var_url is True:
        dataset = open_url(url.format(variables[0]))
    else:
        dataset = open_url(url)

    # Determine lat and lon index in the grid closest to target (lat, lon).
    lat_vals = dataset[lat_name][:].data
    lon_vals = dataset[lon_name][:].data

    nlat, nlon = np.meshgrid(lat_vals, lon_vals)

    nlat = nlat.flatten()
    nlon = nlon.flatten()

    ngrid = list(zip(nlat, nlon))
    distances = haversine_vector([(lat, lon)], ngrid, comb=True)
    closest = np.argmin(distances)

    ilat = int(np.argmax(lat_vals == nlat[closest]))
    ilon = int(np.argmax(lon_vals == nlon[closest]))

    ndf = pd.DataFrame()
    for var in variables:
        if single_var_url is True:
            dataset = open_url(url.format(var))
        try:
            ds = dataset[var]
        except KeyError:
            ds = dataset[variable_map[var]["standard_name"]]

        scale_factor = ds.attributes.get("scale_factor", 1.0)
        add_offset = ds.attributes.get("add_offset", 0.0)
        missing_value = ds.attributes.get("missing_value", missing_value)
        long_name = ds.attributes.get("long_name", "missing_long_name")

        units = ds.attributes["units"]
        # The following normalizes the units string to conform to the 'pint'
        # library.
        units = units.replace(" per ", "/")
        units = units.replace("millimeters", "mm")
        units = units.replace("square meter", "m^2")
        units = units.replace("meters", "m")
        units = units.replace("second", "s")
        units = units.replace("Percent", "%")
        units = units.replace("deg C", "degC")
        units = units.replace("Unitless", "")
        units = units.replace("unitless", "")
        units = {"C": "degC"}.get(units, units)

        time = dataset[time_name]
        try:
            time = cftime.num2pydate(
                time.data[:],
                units=time.attributes["units"],
                calendar=time.attributes.get("calendar", "standard"),
            )
        except ValueError:
            # If the dates are byte strings b"2001-01-01"...
            time = pd.to_datetime([i.decode("ascii") for i in time.data[:]])

        if (start_date is not None) or (end_date is not None):
            tndf = pd.DataFrame(range(len(time)), index=time)
            timedfindex = tndf.index

        if start_date is None:
            start_date_index = None
        else:
            start_date_index = timedfindex.get_loc(
                pd.to_datetime(start_date), method="nearest"
            )

        if end_date is None:
            end_date_index = None
        else:
            end_date_index = timedfindex.get_loc(
                pd.to_datetime(end_date), method="nearest"
            )

        try:
            point = ds.array[
                start_date_index:end_date_index, ilat : ilat + 1, ilon : ilon + 1
            ]
        except AttributeError:
            point = ds.data[
                start_date_index:end_date_index, ilat : ilat + 1, ilon : ilon + 1
            ]

        df = pd.DataFrame(
            np.squeeze(point), index=time[start_date_index:end_date_index]
        )

        df[df == missing_value] = pd.NA
        df = df * scale_factor + add_offset

        df.columns = [f"{variable_map[var]['lname']}:{units}"]
        ndf = ndf.join(df, how="outer")

    if len(ndf.dropna(how="all")) == 0:
        if start_date is None:
            start_date = "beginning of record"
        if end_date is None:
            end_date = "end of record"
        raise ValueError(
            tsutils.error_wrapper(
                f"""
No data is available for lat/lon "{lat}/{lon}" and variables "{variables}"
between {start_date} and {end_date}.
"""
            )
        )

    return ndf


def eopendap(
    url,
    lat,
    lon,
    variables=None,
    variable_map=None,
    start_date=None,
    end_date=None,
    tzname="UTC",
    time_name="date",
    missing_value=None,
):
    variables = tsutils.make_list(variables)

    from erddapy import ERDDAP

    e = ERDDAP(
        server=url,
        protocol="opendap",
        response="csv",
    )

    e.constraints = {
        "time>=": start_date,
        "time<=": end_date,
        "latitude>=": lat,
        "latitude<=": lat,
        "longitude>=": lon,
        "longitude<=": lon,
    }

    df = e.to_pandas(
        index_col=time_name,
        parse_dates=True,
    ).dropna()

    return df


def nopendap(
    url,
    lat,
    lon,
    variables=None,
    variable_map=None,
    start_date=None,
    end_date=None,
    tzname="UTC",
    time_name="date",
    missing_value=None,
):
    variables = tsutils.make_list(variables)

    ncss = NCSS(url)

    avail_vars = list(ncss.variables)
    var = tsutils.make_list(variables)
    if var is None:
        var = avail_vars
        var.sort()
    else:
        nvar = []
        for i in avail_vars:
            for j in var:
                if i.lower() == j.lower():
                    nvar.append(i)
        var = nvar

    query = ncss.query()

    if start_date is None:
        start_date = datetime.datetime(1, 1, 1)
    if end_date is None:
        end_date = datetime.datetime(9999, 1, 1)
    query.time_range(start_date, end_date)

    query.variables(*var)

    query.lonlat_point(lon, lat)

    ncss.validate_query(query)

    data = ncss.get_data(query)

    # Sometimes the variable name is different.  Remove all the other keys to
    # arrive at the variable name.
    data_keys = list(data.keys())
    data_keys.remove(time_name)
    ndf = pd.DataFrame()
    for nv in var:
        v = nv.lower()
        try:
            vmap = variable_map[v]
        except KeyError:
            vmap = {}
            for key, value in variable_map.items():
                vmap[variable_map[key]["lname"]] = value
            vmap = vmap[v]
        standard_name = vmap["standard_name"]
        lname = vmap["lname"]

        meta = ncss.metadata.variables[standard_name]["attributes"]
        scale_factor = meta.get("scale_factor", [1.0])[0]
        offset = meta.get("add_offset", [0.0])[0]
        missing_value = meta.get("missing_value", [missing_value])[0]

        units = meta["units"]

        # The following normalizes the units string to conform to the 'pint'
        # library.
        units = units.replace(" per ", "/")
        units = units.replace("millimeters", "mm")
        units = units.replace("square meter", "m^2")
        units = units.replace("meters", "m")
        units = units.replace("second", "s")
        units = units.replace("Percent", "%")
        units = units.replace("deg C", "degC")

        tdf = (
            pd.DataFrame(data[standard_name], index=data["date"]) * scale_factor
            + offset
        )
        tdf[tdf == missing_value] = None
        tdf.columns = [f"{lname}:{units}"]
        ndf = ndf.join(tdf, how="outer")

    ndf = tsutils.asbestfreq(ndf)

    try:
        ndf.index = ndf.index.tz_localize(tzname)
    except TypeError:
        ndf.index = ndf.index.tz_convert(tzname)

    ndf.index.name = f"Datetime:{tzname}"

    if len(ndf.dropna(how="all")) == 0:
        if start_date is None:
            start_date = "beginning of record"
        if end_date is None:
            end_date = "end of record"
        raise ValueError(
            tsutils.error_wrapper(
                f"""
Returned no data for lat/lon "{lat}/{lon}", variables
"{variables}" between {start_date} and {end_date}.
"""
            )
        )

    return ndf
