"""
tsgettoolbox utility functions.
"""

import configparser as cp
import datetime
import io
import os
from multiprocessing import Pool

import cftime
import numpy as np
import pandas as pd
import requests
from dapclient.client import open_dods_url, open_url
from haversine import haversine_vector
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from siphon.ncss import NCSS
from toolbox_utils import tsutils

from tsgettoolbox import appdirs

__all__ = []

dirs = appdirs.AppDirs("tsgettoolbox", "tsgettoolbox")


def read_api_key(service):
    """Read API key from file if exists else create key place holder."""
    if not os.path.exists(dirs.user_config_dir):
        os.makedirs(dirs.user_config_dir)
    configfile = os.path.join(dirs.user_config_dir, "config.ini")
    if not os.path.exists(configfile):
        with open(configfile, "w", encoding="ascii") as fpconfig:
            fpconfig.write(
                f"""

[{service}]
api_key = ReplaceThisStringWithYourKey

"""
            )
    # Make sure read only by user.
    os.chmod(configfile, 0o600)

    inifile = cp.ConfigParser()
    inifile.readfp(open(configfile, encoding="ascii"))

    try:
        api_key = inifile.get(service, "api_key")
    except BaseException:
        with open(configfile, "a", encoding="ascii") as fpconfig:
            fpconfig.write(
                f"""

[{service}]
api_key = ReplaceThisStringWithYourKey

"""
            )
        api_key = "ReplaceThisStringWithYourKey"

    inifile.readfp(open(configfile, encoding="ascii"))
    api_key = inifile.get(service, "api_key")
    if api_key == "ReplaceThisStringWithYourKey":
        raise ValueError(
            f"""
*
*   Need to edit {configfile}
*   to add your API key that you got from {service}.
*
"""
        )

    return api_key


def requests_retry_session(
    retries=3,
    backoff_factor=0.1,
    status_forcelist=(429, 500, 502, 503, 504),
    session=None,
):
    """Retry requests session."""
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
    """Read csv file."""
    req = requests_retry_session().get(filename)
    try:
        req.raise_for_status()
        return pd.read_csv(
            io.StringIO(req.content.decode("utf-8")),
            low_memory=False,
            parse_dates=True,
            converters={"REPORT_TYPE": str.strip},
        )
    except requests.exceptions.HTTPError:
        return pd.DataFrame()


def file_downloader(baseurl, station, startdate=None, enddate=None):
    """Generic NCEI/NOAA file downloader."""
    if startdate:
        startdate = pd.to_datetime(startdate)
    else:
        startdate = pd.to_datetime("1901-01-01")
    if enddate:
        enddate = pd.to_datetime(enddate)
    else:
        enddate = datetime.datetime.now()

    station = station.split(":")[-1]
    urls = []
    for year in range(startdate.year, enddate.year + 1):
        url = baseurl.format(station=station, year=year)
        urls.append(url)

    with Pool(processes=os.cpu_count()) as pool:
        # have your pool map the file names to dataframes
        df_list = pool.map(read_csv, urls)

    final = pd.concat(df_list)
    final = final.set_index("DATE")
    final.index.name = "Datetime"
    final.index = pd.to_datetime(final.index)
    final = final.sort_index()
    return final[startdate:enddate]


def dapdownloader(url, lat, lon, var, start_date=None, end_date=None):
    """Download data from a OpenDAP server using NCSS."""
    for u in tsutils.make_list(url):
        try:
            ncss = NCSS(u.format(**locals()))
            break
        except xml.etree.ElementTree.ParseError:
            pass

    avail_vars = list(ncss.variables)
    var = tsutils.make_list(var)

    if not var:
        var = avail_vars
    else:
        nvar = []
        for i in avail_vars:
            nvar.extend(i for j in var if i.lower() == j.lower())
        var = nvar

    query = ncss.query()

    if start_date is None:
        start_date = datetime.datetime(1, 1, 1)
    if end_date is None:
        end_date = datetime.datetime(9999, 1, 1)
    query.time_range(start_date, end_date)
    query.variables(*var)

    if tsutils.make_list(lon) == 2 and tsutils.make_list(lat) == 2:
        query.lonlat_box(lon[0], lon[1], lat[0], lat[1])
    else:
        query.lonlat_point(lon, lat)

    ncss.validate_query(query)

    data = ncss.get_data(query)

    # Sometimes the variable name is different.  Remove all the other keys to
    # arrive at the variable name.

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
    url: str,
    lat: float,
    lon: float,
    variable_map,
    variables=None,
    start_date=None,
    end_date=None,
    time_name="date",
    missing_value=None,
    lat_name="lat",
    lon_name="lon",
    single_var_url=False,
    tzname="UTC",
):
    """Read data from a OpenDAP server using dapclient."""
    if variables is None:
        variables = sorted(variable_map.keys())
    else:
        variables = tsutils.make_list(variables)
        for variable in variables:
            if variable not in variable_map:
                raise ValueError(
                    tsutils.error_wrapper(
                        f"""
                        The variable "{variable}" is not available from this
                        service.  The available variables are
                        "{variable_map.keys()}".
                        """
                    )
                )

    # Need to download lat and lon data to determine the closest grid point.
    # If the url is a single variable url, it doesn't matter which variable is
    # used to download the lat and lon data.  So use the first.
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

        # EXAMPLE CONTENTS OF TYPICAL ds.attributes
        # ds.attributes.units: mm
        # ds.attributes.description: Daily Accumulated Precipitation
        # ds.attributes.long_name: pr
        # ds.attributes.standard_name: pr
        # ds.attributes.dimensions: lon lat time
        # ds.attributes.grid_mapping: crs
        # ds.attributes.coordinate_system: WGS84,EPSG:4326

        # The following normalizes the units string to conform to the 'pint'
        # library.
        units = ds.attributes.get("units", "").replace(" per ", "/")
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
            time_units = time.attributes.get("units", "")
            calendar = time.attributes.get("calendar", "standard")
            time = cftime.num2pydate(
                time.data[:],
                units=time_units,
                calendar=calendar,
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
            start_date_index = timedfindex.get_indexer(
                [pd.to_datetime(start_date)], method="nearest"
            )[0]

        if end_date is None:
            end_date_index = None
        else:
            end_date_index = timedfindex.get_indexer(
                [pd.to_datetime(end_date)], method="nearest"
            )[0]

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
        df = df * ds.attributes.get("scale_factor", 1.0) + ds.attributes.get(
            "add_offset", 0.0
        )

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
                No data is available for lat/lon "{lat}/{lon}" and variables
                "{variables}" between {start_date} and {end_date}.
                """
            )
        )
    try:
        ndf.index = ndf.index.tz_localize(tzname)
    except TypeError:
        ndf.index = ndf.index.tz_convert(tzname)

    ndf.index.name = f"Datetime:{tzname}"

    return ndf


def erddap(
    url,
    lat,
    lon,
    variables=None,
    start_date=None,
    end_date=None,
    time_name="date",
    single_var_url=False,
):
    """Download data from an ERDDAP server."""
    variables = tsutils.make_list(variables)

    from erddapy import ERDDAP

    if single_var_url is True:
        url = url.format(variables[0])

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

    return e.to_pandas(
        index_col=time_name,
        parse_dates=True,
    ).dropna()


# Uses NCSS and is slow...
def nopendap(
    url,
    lat,
    lon,
    variable_map,
    variables=None,
    start_date=None,
    end_date=None,
    tzname="UTC",
    time_name="date",
    missing_value=None,
    single_var_url=False,
):
    """Download data from a OPeNDAP server using NCSS."""
    variables = tsutils.make_list(variables)

    if single_var_url is True:
        cdf = pd.DataFrame()
        for var in variables:
            rdf = opendap(
                url.format(var),
                lat,
                lon,
                variable_map,
                variables=None,
                start_date=start_date,
                end_date=end_date,
                time_name=time_name,
                missing_value=missing_value,
                single_var_url=False,
            )
            cdf = cdf.join(rdf, how="outer")
        return cdf

    ncss = NCSS(url)

    avail_vars = list(ncss.variables)
    var = tsutils.make_list(variables)
    if var is None:
        var = avail_vars
        var.sort()
    else:
        nvar = []
        for i in avail_vars:
            nvar.extend(i for j in var if i.lower() == j.lower())
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
            vmap = {
                variable_map[key]["lname"]: value for key, value in variable_map.items()
            }

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
