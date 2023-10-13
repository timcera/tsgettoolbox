"""
Collection of utilities to support Hydstra data access.
"""

import ast
import datetime as dt
import sys
import urllib.error as ue
from time import sleep

import pandas as pd
import requests

SJR_Variables = {
    "Rainfall:in": ("11.10", "tot"),
    "Water_Elev_NAVD88:ft": ("227.10", "mean"),
    "Gauge Height:ft": ("233.10", "mean"),
    "Discharge:cfs": ("262.17", "mean"),
}

# update this from occat.csv
OC_Variables = {
    "Rainfall:in": ("11.10", "tot"),
    "Water_Elev_NAVD88:ft": ("227.10", "mean"),
    "Gauge Height:ft": ("233.10", "mean"),
    "Discharge:cfs": ("262.17", "mean"),
}

# maybe a union of the two above?  or intersect?
Gen_Variables = {
    "Rainfall:in": ("11.10", "tot"),
    "Water_Elev_NAVD88:ft": ("227.10", "mean"),
    "Gauge Height:ft": ("233.10", "mean"),
    "Discharge:cfs": ("262.17", "mean"),
}

SJR_SkipDataSources = [
    "QA",
    "MD",
    "EOM",
    "Reg_Schedule",
    "WEIR_FLOW",
    "SWFWMD_Outgoing",
    "MERGE",
    "Perc",
    "DATATRANS",
]

# check occat.csv to see if any seem necessary
OC_SkipDataSources = []

# leave general blank - up to user to know what they're asking for
Gen_SkipDataSources = []


def row_datestring_to_datetime(row):
    """Convert a row of a dataframe to a datetime object."""
    date_int64 = row["time"]
    return dateint_to_datetime(date_int64)


def dateint_to_datetime(date_int64):
    """Convert a date integer to a datetime object."""
    strf = f"{date_int64}"
    year = int(strf[:4])
    month = int(strf[4:6])
    day = int(strf[6:8])
    hour = int(strf[8:10])
    minute = int(strf[10:12])
    second = int(strf[12:14])
    return dt.datetime(year, month, day, hour, minute, second)


def datetime_to_dateint(dattim):
    """Convert a datetime object to a date integer."""
    year = dattim.year
    month = dattim.month
    day = dattim.day
    hour = dattim.hour
    minute = dattim.minute
    second = dattim.second
    date_str = f"{year:04}{month:02}{day:02}{hour:02}{minute:02}{second:02}"
    return int(date_str)


def hydstra_get_ts(
    urlbase,
    station,
    datasource,
    datatype,
    start_time,
    end_time,
    var,
    interval="day",
    quality=True,
    maxqual=254,
):
    """Get a time series from Hydstra."""
    # set additonal parameters and create URL
    func = "get_ts_traces"
    fmt = "csv"
    url = f"{urlbase}?{{'function':{func},'version':'2','params':{{'site_list':'{station}','datasource':'{datasource}','var_list':{var},'start_time':{start_time},'end_time':{end_time},'data_type':{datatype},'interval':{interval},'multiplier':'1'}}}}&format={fmt}"
    # print(url)
    # send URL to get raw dataframe from hydstra web service
    try:
        df = pd.read_csv(
            url, encoding="cp1252", encoding_errors="replace", dtype={"site": str}
        )
    except NameError:
        df = _extracted_from_hydstra_get_ts_25("GetTs: NameError on URL\n", url)
    except ue.HTTPError:
        df = _extracted_from_hydstra_get_ts_25("GetTs: HTTPError on URL\n", url)
        return df

    # postprocess into final dataframe
    # print(df)

    # drop rows with quality code too high
    # create header for value column from station and variable name
    stationid = df.at[0, "site"]
    varnam = df.at[0, "varname"].replace(" ", "")
    headerval = f"{stationid}_{varnam}_value"
    df = df.rename(columns={"value": headerval})

    df.drop(df[df["quality"] > maxqual].index, inplace=True)

    if quality:
        headerqual = f"{stationid}_{varnam}_quality"
        df = df.rename(columns={"quality": headerqual})
    else:
        df = df.drop(columns=["quality"])
    df["Datetime"] = df.apply(row_datestring_to_datetime, axis=1)
    df = df.set_index("Datetime")
    df = df.drop(columns=["site", "varname", "var", "time"])
    return df


# TODO Rename this here and in `hydstra_get_ts`
def _extracted_from_hydstra_get_ts_25(arg0, url):
    sys.stderr.write(arg0)
    sys.stderr.write("    " + url)
    return pd.DataFrame()


def hydstra_get_json_response(url):
    """Get a JSON response from Hydstra."""
    rdict = {}
    # call url to get response text in nested json
    try:
        response = requests.get(url).text
    except NameError:
        return _extracted_from_hydstra_get_json_response_8(
            "GetJsonResponse: NameError on URL \n", url, rdict
        )
    except ue.HTTPError:
        return _extracted_from_hydstra_get_json_response_8(
            "GetJsonResponse: HTTPError on URL\n", url, rdict
        )
    except SyntaxError:
        return _extracted_from_hydstra_get_json_response_8(
            "GetJsonResponse: SyntaxError on URL\n", url, rdict
        )
    # convert response text from json to dictionary
    # this function seems more reliable than native json library
    # for nested jason, and safer than eval()
    try:
        ldict = ast.literal_eval(response)
    except SyntaxError:
        sys.stderr.write("GetJsonResponse: Syntax error parsing response\n")
        sys.stderr.write(f"    {response}")
        sys.stderr.write("    {url}")
        return rdict

    # dictionary now has a key 'error_num', and if none, also a key 'return'
    # check for request error
    if ldict["error_num"] != 0:
        # no 'return' dictionary - just display error message
        sys.stderr.write("GetJsonResponse Error: " + str(ldict["error_num"]))
        sys.stderr.write("    " + ldict["error_msg"])
        sys.stderr.write("    " + url)
        sys.stderr.write(f"    {response}")
    else:
        # parse return object, which is another dictionary
        rdict = ldict["return"]
    return rdict


# TODO Rename this here and in `hydstra_get_json_response`
def _extracted_from_hydstra_get_json_response_8(arg0, url, rdict):
    sys.stderr.write(arg0)
    sys.stderr.write(f"    {url}")
    return rdict


def _process(url, desired_key):
    """Process a URL and return a value."""
    varlist = []
    rdict = hydstra_get_json_response(url)
    try:
        numsites = len(rdict["sites"])
        if numsites == 0:
            return _extracted_from__process_8(
                desired_key, ": Zero stations in database:", rdict, url
            )
    except KeyError:
        return _extracted_from__process_8(
            desired_key, ": KeyError on Sites:", rdict, url
        )
    if numsites == 1:
        sdict = rdict["sites"][0]
        vlist = sdict[desired_key]
        numv = len(vlist)
        varlist = [vlist[i] for i in range(numv)]
    else:
        sys.stderr.write(
            f"Get{desired_key}: {numsites} stations given - bug? {str(rdict)}"
        )
    return varlist


# TODO Rename this here and in `_process`
def _extracted_from__process_8(desired_key, arg1, rdict, url):
    sys.stderr.write(f"Get{desired_key}{arg1}{str(rdict)}")
    sys.stderr.write(f"    {url}")
    return []


def hydstra_get_variables(urlbase, stationid, datasource):
    """Get a list of variables for a station."""
    func = "get_variable_list"
    url = f"{urlbase}?{{'function':{func},'version':'1','params':{{'site_list':'{stationid}','datasource':'{datasource}'}}}}&format=json"

    return _process(url, "variables")


def hydstra_get_stations(urlbase, activeonly=False, latlong=True):
    """Get a list of stations."""
    func = "get_db_info"
    url = f"{urlbase}?{{'function':{func},'version':'3','params':{{'table_name':'site','field_list':['station','stname','latitude','longitude','active'],'return_type':'array'}}}}&format=csv"
    try:
        dbdf = pd.read_csv(url, encoding="cp1252", encoding_errors="replace")
    except NameError:
        dbdf = _extracted_from_hydstra_get_stations_8("GetTs: NameError on URL\n", url)
    except ue.HTTPError:
        dbdf = _extracted_from_hydstra_get_stations_8("GetTs: HTTPError on URL\n", url)
    if activeonly:
        dbdf = dbdf[dbdf["active"] is True]
    if not latlong:
        dbdf = dbdf.drop(columns=["latitude", "longitude"])

    return dbdf


# TODO Rename this here and in `hydstra_get_stations`
def _extracted_from_hydstra_get_stations_8(arg0, url):
    sys.stderr.write(arg0)
    sys.stderr.write(f"    {url}")
    return pd.DataFrame()


def hydstra_get_datasources(urlbase, stationid):
    """Get a list of data sources for a station."""
    func = "get_datasources_by_site"
    url = f"{urlbase}?{{'function':{func},'version':'1','params':{{'site_list':'{stationid}'}}}}&format=json"

    return _process(url, "datasources")


def hydstra_get_station_catalog(urlbase, stationid, SkipDataSources=None, isleep=0):
    """Get a catalog of data for a station."""
    if SkipDataSources is None:
        SkipDataSources = []
    # initialize dataframe and catalog headers
    icat = 0
    catalog = pd.DataFrame()
    headers = [
        "Station",
        "DataSource",
        "VariableCode",
        "VariableName",
        "VariableDescrip",
        "Units",
        "StartDateTime",
        "EndDateTime",
    ]
    for i in range(8):
        catalog.insert(i, column=headers[i], value="")

    dsrclist = hydstra_get_datasources(urlbase, stationid)
    # print("Got datasources: ", stationid, dsrclist)
    for dsource in dsrclist:
        sleep(isleep)
        skipthisds = dsource in SkipDataSources
        if not skipthisds:
            for skipds in SkipDataSources:
                if skipds in dsource:
                    skipthisds = True
        if not skipthisds:
            # skip over nonstandard data sources not intended for public use
            varlist = hydstra_get_variables(urlbase, stationid, dsource)
            # print('Got variables: ', stationid, dsource, varlist)
            for var in varlist:
                icat += 1
                newrow = pd.DataFrame(
                    {
                        "Station": stationid,
                        "DataSource": dsource,
                        "VariableCode": var["variable"],
                        "VariableName": var["name"],
                        "VariableDescrip": var["subdesc"],
                        "Units": var["units"],
                        "StartDateTime": dateint_to_datetime(var["period_start"]),
                        "EndDateTime": dateint_to_datetime(var["period_end"]),
                    },
                    index=[0],
                )
                catalog = pd.concat([catalog, newrow], axis=0)
    return catalog


def hydstra_get_all_catalog(urlbase, activeonly=False, istart=0, iend=-1, isleep=3):
    """Get a catalog of data for all stations."""
    # initialize dataframe and catalog headers
    catalog = pd.DataFrame()
    headers = [
        "Station",
        "DataSource",
        "VariableCode",
        "VariableName",
        "VariableDescrip",
        "Units",
        "StartDateTime",
        "EndDateTime",
    ]
    for i in range(8):
        catalog.insert(i, column=headers[i], value="")

    # get stations
    stationdf = hydstra_get_stations(urlbase, activeonly)
    # print('Got stations: ', len(stationdf))

    istop = len(stationdf) if iend == -1 else max(len(stationdf), iend)
    for i in range(istart, istop):
        stationid = stationdf.at[i, "station"]
        # print(stationid, " in station loop", i, istart, istop)
        station_cat = hydstra_get_station_catalog(urlbase, stationid, isleep=isleep)
        if i == istart:
            catalog = station_cat
        else:
            catalog = pd.concat([catalog, station_cat], axis=0)
    print(len(catalog), catalog)
    return catalog


def hydstra_get_server_url(server):
    """Get the URL for a Hydstra server."""
    servdict = {
        "sjrwmd": "https://secure.sjrwmd.com/hydweb/cgi/webservice.exe",
        "orangeco_ca": "http://Hydstra.OCPublicWorks.com/cgi/webservice.exe",
    }
    return servdict.get(server, server)


def hydstra_get_server_vars(server):
    """Get the variables for a Hydstra server."""
    if server == "orangeco_ca":
        return OC_Variables
    elif server == "sjrwmd":
        return SJR_Variables
    else:
        return Gen_Variables


def hydstra_get_server_skipds(server):
    """Get the data sources to skip for a Hydstra server."""
    if server == "orangeco_ca":
        return OC_SkipDataSources
    elif server == "sjrwmd":
        return SJR_SkipDataSources
    else:
        return Gen_SkipDataSources
