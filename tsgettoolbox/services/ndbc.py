from __future__ import print_function
from __future__ import absolute_import

import datetime
from base64 import b64decode
from gzip import GzipFile
import logging
import os
from builtins import object
from io import StringIO
from io import BytesIO

from tsgettoolbox.odo import convert
from tsgettoolbox.odo import odo
from tsgettoolbox.odo import resource

import pandas as pd

import requests

from tstoolbox import tsutils


class NDBC(object):
    def __init__(self, url, **query_params):
        self.lmap = {
            "stdmet": "h",
            "cwind": "c",
            "wlevel": "l",
            "ocean": "o",
            "adcp": "a",
            "supl": "s",
            "srad": "r",
        }

        # 'wlevel' header is manipulated and not in self.headermap
        self.headermap = {
            "stdmet": {
                "WDIR": "WDIR:degT",
                "WSPD": "WSPD:m/s",
                "GST": "GST:m/s",
                "WVHT": "WVHT:m",
                "DPD": "DPD:s",
                "APD": "APD:s",
                "MWD": "MWD:degT",
                "PRES": "PRES:hPa",
                "ATMP": "ATMP:degC",
                "WTMP": "WTMP:degC",
                "DEWP": "DEWP:degC",
                "VIS": "VIS:nautical_miles",
                "PTDY": "PTDY:hPa",
                "TIDE": "TIDE:ft",
            },
            "cwind": {
                "WDIR": "WDIR:degT",
                "WSPD": "WSPD:m/s",
                "GDR": "GDR:degT",
                "GST": "GST:m/s",
                "GTIME": "GTIME",
            },
            "ocean": {
                "DEPTH": "DEPTH:m",
                "OTMP": "OTMP:degC",
                "COND": "COND:mS/cm",
                "SAL": "SAL:PSU",
                "O2%": "O2:percent",
                "O2PPM": "O2PPM:ppm",
                "CLCON": "CLCON:ug/l",
                "TURB": "TURB:FTU",
                "PH": "PH:",
                "EH": "EH:mv",
            },
            "adcp": {
                "DEP01": "DEP01:m",
                "DIR01": "DIR01:degT",
                "SPD01": "SPD01:cm/s",
                "DEP02": "DEP02:m",
                "DIR02": "DIR02:degT",
                "SPD02": "SPD02:cm/s",
                "DEP03": "DEP03:m",
                "DIR03": "DIR03:degT",
                "SPD03": "SPD03:cm/s",
                "DEP04": "DEP04:m",
                "DIR04": "DIR04:degT",
                "SPD04": "SPD04:cm/s",
                "DEP05": "DEP05:m",
                "DIR05": "DIR05:degT",
                "SPD05": "SPD05:cm/s",
                "DEP06": "DEP06:m",
                "DIR06": "DIR06:degT",
                "SPD06": "SPD06:cm/s",
                "DEP07": "DEP07:m",
                "DIR07": "DIR07:degT",
                "SPD07": "SPD07:cm/s",
                "DEP08": "DEP08:m",
                "DIR08": "DIR08:degT",
                "SPD08": "SPD08:cm/s",
                "DEP09": "DEP09:m",
                "DIR09": "DIR09:degT",
                "SPD09": "SPD09:cm/s",
                "DEP10": "DEP10:m",
                "DIR10": "DIR10:degT",
                "SPD10": "SPD10:cm/s",
                "DEP11": "DEP11:m",
                "DIR11": "DIR11:degT",
                "SPD11": "SPD11:cm/s",
                "DEP12": "DEP12:m",
                "DIR12": "DIR12:degT",
                "SPD12": "SPD12:cm/s",
                "DEP13": "DEP13:m",
                "DIR13": "DIR13:degT",
                "SPD13": "SPD13:cm/s",
                "DEP14": "DEP14:m",
                "DIR14": "DIR14:degT",
                "SPD14": "SPD14:cm/s",
                "DEP15": "DEP15:m",
                "DIR15": "DIR15:degT",
                "SPD15": "SPD15:cm/s",
                "DEP16": "DEP16:m",
                "DIR16": "DIR16:degT",
                "SPD16": "SPD16:cm/s",
                "DEP17": "DEP17:m",
                "DIR17": "DIR17:degT",
                "SPD17": "SPD17:cm/s",
                "DEP18": "DEP18:m",
                "DIR18": "DIR18:degT",
                "SPD18": "SPD18:cm/s",
                "DEP19": "DEP19:m",
                "DIR19": "DIR19:degT",
                "SPD19": "SPD19:cm/s",
                "DEP20": "DEP20:m",
                "DIR20": "DIR20:degT",
                "SPD20": "SPD20:cm/s",
            },
            "srad": {
                "SRAD1": "SRAD1:w/m2",
                "SWRAD": "SWRAD:w/m2",
                "LWRAD": "LWRAD:w/m2",
            },
        }
        self.rename = {
            "WD": "WDIR:degT",
            "DIR": "WDIR:degT",
            "SPD": "WSPD:m/s",
            "GSP": "GST:m/s",
            "GMN": "GTIME",
            "BARO": "PRES:hPa",
            "H0": "WVHT:m",
            "DOMPD": "DPD:s",
            "AVP": "APD:s",
            "SRAD": "SWRAD",
            "SRAD2": "SWRAD",
            "LRAD": "LWRAD",
            "LRAD1": "LWRAD",
            "BAR": "PRES:hPa",
        }
        for item in self.headermap:
            self.rename.update(self.headermap[item])

        self.url = url
        self.query_params = query_params


# Function to make `resource` know about the new NOS type.
#  https://www.ndbc.noaa.gov/download_data.php?
#      filename=41013h2003.txt.gz&
#      dir=data/historical/stdmet/
#  https://www.ndbc.noaa.gov/download_data.php?
#      filename=4101322018.txt.gz&
#      dir=data/stdmet/Feb/
#  https://www.ndbc.noaa.gov/data/historical/stdmet/41012h2012.txt.gz
#  https://www.ndbc.noaa.gov/data/stdmet/Mar/sauf132018.txt.gz
@resource.register(r"https://www\.ndbc\.noaa\.gov/data/*", priority=17)
def resource_ndbc(uri, **kwargs):
    return NDBC(uri, **kwargs)


def date_parser(*x):
    x = [int(i) for i in x]
    if x[0] < 100:
        x[0] = x[0] + 1900
    return pd.datetime(*x)


mapnumtoname = {
    0: "Jan",
    1: "Feb",
    2: "Mar",
    3: "Apr",
    4: "May",
    5: "Jun",
    6: "Jul",
    7: "Aug",
    8: "Sep",
    9: "Oct",
    10: "Nov",
    11: "Dec",
}


# Function to convert from NDBC type to pd.DataFrame
@convert.register(pd.DataFrame, NDBC)
def ndbc_to_df(data, **kwargs):

    sdate = tsutils.parsedate(data.query_params.pop("startUTC"))
    edate = tsutils.parsedate(data.query_params.pop("endUTC"))

    table = data.query_params["table"]

    df = pd.DataFrame()

    cyear = datetime.datetime.now()
    filenames = []
    for yr in range(sdate.year, edate.year + 1):
        # Yearly
        # https://www.ndbc.noaa.gov/data/historical/stdmet/41012h2012.txt.gz
        filenames.append(
            "/historical/{3}/{0}{1}{2}.txt.gz".format(
                data.query_params["station"], data.lmap[table], yr, table
            )
        )
    if edate.year == cyear.year:
        for mnth in range(edate.month):
            # Monthly
            # https://www.ndbc.noaa.gov/data/stdmet/Mar/sauf132018.txt.gz
            filenames.append(
                "/{3}/{4}/{0}{1}{2}.txt.gz".format(
                    data.query_params["station"],
                    mnth + 1,
                    yr,
                    table,
                    mapnumtoname[mnth],
                )
            )

    for filename in filenames:
        req = requests.get(data.url + filename)

        if os.path.exists("debug_tsgettoolbox"):
            logging.warning(req.url)

        try:
            req.raise_for_status()
        except requests.exceptions.HTTPError:
            continue

        content = BytesIO(req.content)
        content = GzipFile(fileobj=content).read()

        # Test to see if 1 or 2 line header
        f = StringIO(content.decode("utf-8"))
        head1 = f.readline()
        head2 = f.readline()
        f.seek(0)

        words1 = head1.split()
        words2 = head2.split()
        try:
            _ = int(words2[0])
            skiprows = None
        except ValueError:
            skiprows = [1]

        if "mm" == words1[4]:
            parse_dates = {"datetime": [0, 1, 2, 3, 4]}
        else:
            parse_dates = {"datetime": [0, 1, 2, 3]}

        tdf = pd.read_csv(
            f,
            header=0,
            skiprows=skiprows,
            sep=r"\s+",
            parse_dates=parse_dates,
            date_parser=date_parser,
            index_col=0,
            na_values=["MM", 999.0, 99.0, 9999, 99999],
        )

        if len(tdf) > 0:
            tdf.rename(columns=data.rename, inplace=True)
            df = df.append(tdf)

    if len(df) == 0:
        raise ValueError(
            tsutils.error_wrapper(
                """
No data collected/available within this time frame.
"""
            )
        )

    if table == "wlevel":
        df.columns = list(range(0, 55, 6))
        df = pd.DataFrame(df.stack())
        df.index = [i + datetime.timedelta(minutes=j) for i, j in df.index]
        df.index.name = "Datetime"
        df.columns = ["WLEVEL:ft:MLLW"]

    # Clean up the dataframe...
    df = df.sort_index()
    df = df[~df.index.duplicated()]

    df.columns = [i.replace(r"%", "PERCENT") for i in df.columns]

    return df.loc[sdate:edate, :]


if __name__ == "__main__":
    """
    """

    r = resource(
        r"https://www.ndbc.noaa.gov/data/",
        table="stdmet",
        startUTC="2012-01-01T00:00Z",
        endUTC="2012-04-01T00:00Z",
        station="41012",
    )

    as_df = odo(r, pd.DataFrame)
    print("NDBC")
    print(as_df)
    as_df.to_csv("file.csv")
