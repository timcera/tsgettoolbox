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

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from siphon.ncss import NCSS

try:
    import ConfigParser as cp
except ImportError:
    import configparser as cp

from tstoolbox import tsutils

from tsgettoolbox import appdirs

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


def dapdownloader(url, lat, lon, var, avail_vars, start_date, end_date):
    sleep(1.0 / randint(1, 10))  # staggered access to url

    for u in tsutils.make_list(url):
        try:
            ncss = NCSS(u.format(**locals()))
            break
        except xml.etree.ElementTree.ParseError:
            pass

    var = tsutils.make_list(var)

    query = ncss.query()
    query.add_lonlat()
    query.lonlat_point(lon, lat)
    if start_date is None:
        start_date = datetime.datetime(1, 1, 1)
    if end_date is None:
        end_date = datetime.datetime(9999, 1, 1)
    query.time_range(start_date, end_date)
    query.variables(*[avail_vars[i]["standard_name"] for i in tsutils.make_list(var)])

    data = ncss.get_data(query)

    # Sometimes the variable name is different.  Remove all the other keys to
    # arrive at the variable name.
    data_keys = list(data.keys())
    data_keys.remove("lat")
    data_keys.remove("lon")
    data_keys.remove("date")

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


def opendap(
    url,
    variables,
    lat,
    lon,
    avail_vars,
    start_date=None,
    end_date=None,
    tzname="UTC",
    all_vars_at_url=True,
):
    if not variables:
        variables = avail_vars.keys()

    variables = tsutils.make_list(variables)

    inv_vars = {v["lname"]: k for k, v in avail_vars.items()}

    nvars = []
    for i in variables:
        aval = ""
        if i in avail_vars:
            aval = i
        elif i in inv_vars:
            aval = inv_vars[i]
        if aval:
            nvars.append(aval)
        else:
            raise ValueError(
                tsutils.error_wrapper(
                    f"""
The variable {i} must be in {avail_vars.keys()} or in {inv_vars.keys()}."""
                )
            )

    if len(nvars) == 1:
        ndf = dapdownloader(url, lat, lon, nvars[0], avail_vars, start_date, end_date)
    elif all_vars_at_url is True:
        ndf = dapdownloader(url, lat, lon, nvars, avail_vars, start_date, end_date)
    else:
        tasks = []
        for var in nvars:
            tasks.append((url, lat, lon, var, avail_vars, start_date, end_date))

        with multiprocessing.Pool() as pool:
            results = pool.starmap(dapdownloader, tasks)

        ndf = pd.concat(results, axis="columns", join="outer")

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
                """
Returned no data for lat/lon "{lat}/{lon}", variables
"{variables}" between {start_date} and {end_date}.
""".format(
                    **locals()
                )
            )
        )

    return ndf
