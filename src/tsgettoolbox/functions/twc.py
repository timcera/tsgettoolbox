"""
twc                 US/TX station D:Download Texas Weather Connection
                    (TWC) data.
"""

import datetime
import email.utils
import ftplib
import os
import urllib.parse
import warnings
from contextlib import contextmanager
from io import StringIO

import async_retriever as ar
import numpy as np
import pandas as pd
import requests
from toolbox_utils import tsutils

from tsgettoolbox.utils import dirs

__all__ = ["twc"]

CSV_SWITCHOVER = pd.Timestamp("2016-10-01")


def _get_text_url(date):
    return f"http://twc.tamu.edu/weather_images/summ/summ{date.strftime('%Y%m%d')}.txt"


def _parse_text_file(data_file):
    """
    example:
        COUNTY                        KBDI_AVG   KBDI_MAX    KBDI_MIN
                ----------------------------------------------------------------
                ANDERSON                         262       485        47
                ANDREWS                          485       614       357
                ...
    """

    dtype = [
        ("county", "|U15"),
        ("avg", "i4"),
        ("max", "i4"),
        ("min", "i4"),
    ]

    if not data_file.readline().lower().startswith(b"county"):
        return pd.DataFrame()
    data_file.seek(0)

    data_array = np.genfromtxt(
        data_file,
        delimiter=[31, 11, 11, 11],
        dtype=dtype,
        skip_header=2,
        skip_footer=1,
        autostrip=True,
    )
    return pd.DataFrame(data_array)


def _parse_csv_file(data_file):
    """
    example:
        County,Min,Max,Average,Change
        Anderson,429,684,559,+5
        Andrews,92,356,168,+7
    """

    if not data_file.readline().lower().startswith(b"county"):
        return pd.DataFrame()
    data_file.seek(0)

    dataframe = pd.read_csv(data_file)
    dataframe.columns = dataframe.columns.str.lower()
    dataframe = dataframe.rename(columns={"average": "avg"})
    dataframe.county = dataframe.county.str.upper()
    dataframe = dataframe[["county", "avg", "max", "min"]]

    return dataframe


def _path_last_modified(path):
    """returns a datetime.datetime object representing the last time the file at
    a given path was last modified
    """
    if not os.path.exists(path):
        return None

    return datetime.datetime.utcfromtimestamp(os.path.getmtime(path))


def _request_file_size_matches(request, path):
    """returns True if request content-length header matches file size"""
    content_length = request.headers.get("content-length")
    return bool(content_length and int(content_length) == os.path.getsize(path))


def _parse_rfc_1123_timestamp(timestamp_str):
    return datetime.datetime(*email.utils.parsedate(timestamp_str)[:6])


def _request_is_newer_than_file(request, path):
    """returns true if a request's last-modified header is more recent than a
    file's last modified timestamp
    """
    path_last_modified = _path_last_modified(path)

    if path_last_modified is None:
        return True

    if not request.headers.get("last-modified"):
        warnings.warn(
            f"no last-modified date for request: {request.url}, downloading file again"
        )
        return True

    request_last_modified = _parse_rfc_1123_timestamp(
        request.headers.get("last-modified")
    )
    return request_last_modified > path_last_modified


def _ftp_download_if_new(url, path, check_modified=True):
    parsed = urllib.parse.urlparse(url)
    ftp = ftplib.FTP(parsed.netloc, "anonymous")
    directory, filename = parsed.path.rsplit("/", 1)
    ftp_last_modified = _ftp_last_modified(ftp, parsed.path)
    ftp_file_size = _ftp_file_size(ftp, parsed.path)

    if not os.path.exists(path) or os.path.getsize(path) != ftp_file_size:
        _ftp_download_file(ftp, parsed.path, path)
    elif check_modified and _path_last_modified(path) < ftp_last_modified:
        _ftp_download_file(ftp, parsed.path, path)


def _ftp_download_file(ftp, ftp_path, local_path):
    with open(local_path, "wb") as f:
        ftp.retrbinary(f"RETR {ftp_path}", f.write)


def _ftp_file_size(ftp, file_path):
    ftp.sendcmd("TYPE I")
    return ftp.size(file_path)


def _ftp_last_modified(ftp, file_path):
    timestamp = ftp.sendcmd(f"MDTM {file_path}").split()[-1]
    return datetime.datetime.strptime(timestamp, "%Y%m%d%H%M%S")


def mkdir_if_doesnt_exist(dir_path):
    """makes a directory if it doesn't exist"""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def _http_download_file(url, path):
    request = requests.get(url, timeout=60)
    mkdir_if_doesnt_exist(os.path.dirname(path))
    chunk_size = 64 * 1024
    with open(path, "wb") as f:
        for content in request.iter_content(chunk_size):
            f.write(content)


def _http_download_if_new(url, path, check_modified):
    head = requests.head(url, timeout=60)
    if not os.path.exists(path) or not _request_file_size_matches(head, path):
        _http_download_file(url, path)
    elif check_modified and _request_is_newer_than_file(head, path):
        _http_download_file(url, path)


def download_if_new(url, path, check_modified=True):
    """downloads the file located at `url` to `path`, if check_modified is True
    it will only download if the url's last-modified header has a more recent
    date than the filesystem's last modified date for the file
    """
    parsed = urllib.parse.urlparse(url)

    if os.path.exists(path) and not check_modified:
        return

    if parsed.scheme.startswith("ftp"):
        _ftp_download_if_new(url, path, check_modified)
    elif parsed.scheme.startswith("http"):
        _http_download_if_new(url, path, check_modified)
    else:
        raise NotImplementedError("only ftp and http urls are currently implemented")


@contextmanager
def open_file_for_url(url, path, check_modified=True, use_file=None, use_bytes=None):
    """Context manager that returns an open file handle for a data file;
    downloading if necessary or otherwise using a previously downloaded file.
    File downloading will be short-circuited if use_file is either a file path
    or an open file-like object (i.e. file handler or StringIO obj), in which
    case the file handler pointing to use_file is returned - if use_file is a
    file handler then the handler won't be closed upon exit.
    """
    leave_open = False

    if use_file is None:
        download_if_new(url, path, check_modified)
        open_path = path

    elif hasattr(use_file, "read"):
        leave_open = True
        yield use_file
    else:
        open_path = use_file
    if use_bytes is None:
        open_file = open(open_path)
    else:
        open_file = open(open_path, "rb")

    yield open_file

    if not leave_open:
        open_file.close()

    """Context manager that returns an open file handle for a data file;
    downloading if necessary or otherwise using a previously downloaded file.
    File downloading will be short-circuited if use_file is either a file path
    or an open file-like object (i.e. file handler or StringIO obj), in which
    case the file handler pointing to use_file is returned - if use_file is a
    file handler then the handler won't be closed upon exit.
    """
    leave_open = False

    if use_file is None:
        download_if_new(url, path, check_modified)
        open_path = path

    elif hasattr(use_file, "read"):
        leave_open = True
        yield use_file
    else:
        open_path = use_file
    if use_bytes is None:
        open_file = open(open_path)
    else:
        open_file = open(open_path, "rb")

    yield open_file

    if not leave_open:
        open_file.close()


def _open_data_file(url, data_dir):
    """returns an open file handle for a data file; downloading if necessary or
    otherwise using a previously downloaded file
    """
    file_name = url.rsplit("/", 1)[-1]
    file_path = os.path.join(data_dir, file_name)
    return open_file_for_url(url, file_path, check_modified=True, use_bytes=True)


def _get_csv_url(date):
    return f"http://twc.tamu.edu/weather_images/summ/summ{date.strftime('%Y%m%d')}.csv"


def _date_dataframe(date, data_dir):
    if date.to_timestamp() < CSV_SWITCHOVER:
        url = _get_text_url(date)
        print(url)
        print(data_dir)
        with _open_data_file(url, data_dir) as data_file:
            date_df = _parse_text_file(data_file)
    else:
        url = _get_csv_url(date)
        with _open_data_file(url, data_dir) as data_file:
            date_df = _parse_csv_file(data_file)

    date_df["date"] = pd.Period(date, freq="D")

    return date_df


# fips codes from http://www.census.gov/geo/www/ansi/national.txt
# with names adjusted to match twc kbdi: DEWITT --> DE WITT
codes = {
    "ANDERSON": 48001,
    "ANDREWS": 48003,
    "ANGELINA": 48005,
    "ARANSAS": 48007,
    "ARCHER": 48009,
    "ARMSTRONG": 48011,
    "ATASCOSA": 48013,
    "AUSTIN": 48015,
    "BAILEY": 48017,
    "BANDERA": 48019,
    "BASTROP": 48021,
    "BAYLOR": 48023,
    "BEE": 48025,
    "BELL": 48027,
    "BEXAR": 48029,
    "BLANCO": 48031,
    "BORDEN": 48033,
    "BOSQUE": 48035,
    "BOWIE": 48037,
    "BRAZORIA": 48039,
    "BRAZOS": 48041,
    "BREWSTER": 48043,
    "BRISCOE": 48045,
    "BROOKS": 48047,
    "BROWN": 48049,
    "BURLESON": 48051,
    "BURNET": 48053,
    "CALDWELL": 48055,
    "CALHOUN": 48057,
    "CALLAHAN": 48059,
    "CAMERON": 48061,
    "CAMP": 48063,
    "CARSON": 48065,
    "CASS": 48067,
    "CASTRO": 48069,
    "CHAMBERS": 48071,
    "CHEROKEE": 48073,
    "CHILDRESS": 48075,
    "CLAY": 48077,
    "COCHRAN": 48079,
    "COKE": 48081,
    "COLEMAN": 48083,
    "COLLIN": 48085,
    "COLLINGSWORTH": 48087,
    "COLORADO": 48089,
    "COMAL": 48091,
    "COMANCHE": 48093,
    "CONCHO": 48095,
    "COOKE": 48097,
    "CORYELL": 48099,
    "COTTLE": 48101,
    "CRANE": 48103,
    "CROCKETT": 48105,
    "CROSBY": 48107,
    "CULBERSON": 48109,
    "DALLAM": 48111,
    "DALLAS": 48113,
    "DAWSON": 48115,
    "DE WITT": 48123,
    "DEAF SMITH": 48117,
    "DELTA": 48119,
    "DENTON": 48121,
    "DEWITT": 48123,
    "DICKENS": 48125,
    "DIMMIT": 48127,
    "DONLEY": 48129,
    "DUVAL": 48131,
    "EASTLAND": 48133,
    "ECTOR": 48135,
    "EDWARDS": 48137,
    "EL PASO": 48141,
    "ELLIS": 48139,
    "ERATH": 48143,
    "FALLS": 48145,
    "FANNIN": 48147,
    "FAYETTE": 48149,
    "FISHER": 48151,
    "FLOYD": 48153,
    "FOARD": 48155,
    "FORT BEND": 48157,
    "FRANKLIN": 48159,
    "FREESTONE": 48161,
    "FRIO": 48163,
    "GAINES": 48165,
    "GALVESTON": 48167,
    "GARZA": 48169,
    "GILLESPIE": 48171,
    "GLASSCOCK": 48173,
    "GOLIAD": 48175,
    "GONZALES": 48177,
    "GRAY": 48179,
    "GRAYSON": 48181,
    "GREGG": 48183,
    "GRIMES": 48185,
    "GUADALUPE": 48187,
    "HALE": 48189,
    "HALL": 48191,
    "HAMILTON": 48193,
    "HANSFORD": 48195,
    "HARDEMAN": 48197,
    "HARDIN": 48199,
    "HARRIS": 48201,
    "HARRISON": 48203,
    "HARTLEY": 48205,
    "HASKELL": 48207,
    "HAYS": 48209,
    "HEMPHILL": 48211,
    "HENDERSON": 48213,
    "HIDALGO": 48215,
    "HILL": 48217,
    "HOCKLEY": 48219,
    "HOOD": 48221,
    "HOPKINS": 48223,
    "HOUSTON": 48225,
    "HOWARD": 48227,
    "HUDSPETH": 48229,
    "HUNT": 48231,
    "HUTCHINSON": 48233,
    "IRION": 48235,
    "JACK": 48237,
    "JACKSON": 48239,
    "JASPER": 48241,
    "JEFF DAVIS": 48243,
    "JEFFERSON": 48245,
    "JIM HOGG": 48247,
    "JIM WELLS": 48249,
    "JOHNSON": 48251,
    "JONES": 48253,
    "KARNES": 48255,
    "KAUFMAN": 48257,
    "KENDALL": 48259,
    "KENEDY": 48261,
    "KENT": 48263,
    "KERR": 48265,
    "KIMBLE": 48267,
    "KING": 48269,
    "KINNEY": 48271,
    "KLEBERG": 48273,
    "KNOX": 48275,
    "LA SALLE": 48283,
    "LAMAR": 48277,
    "LAMB": 48279,
    "LAMPASAS": 48281,
    "LAVACA": 48285,
    "LEE": 48287,
    "LEON": 48289,
    "LIBERTY": 48291,
    "LIMESTONE": 48293,
    "LIPSCOMB": 48295,
    "LIVE OAK": 48297,
    "LLANO": 48299,
    "LOVING": 48301,
    "LUBBOCK": 48303,
    "LYNN": 48305,
    "MADISON": 48313,
    "MARION": 48315,
    "MARTIN": 48317,
    "MASON": 48319,
    "MATAGORDA": 48321,
    "MAVERICK": 48323,
    "MCCULLOCH": 48307,
    "MCLENNAN": 48309,
    "MCMULLEN": 48311,
    "MEDINA": 48325,
    "MENARD": 48327,
    "MIDLAND": 48329,
    "MILAM": 48331,
    "MILLS": 48333,
    "MITCHELL": 48335,
    "MONTAGUE": 48337,
    "MONTGOMERY": 48339,
    "MOORE": 48341,
    "MORRIS": 48343,
    "MOTLEY": 48345,
    "NACOGDOCHES": 48347,
    "NAVARRO": 48349,
    "NEWTON": 48351,
    "NOLAN": 48353,
    "NUECES": 48355,
    "OCHILTREE": 48357,
    "OLDHAM": 48359,
    "ORANGE": 48361,
    "PALO PINTO": 48363,
    "PANOLA": 48365,
    "PARKER": 48367,
    "PARMER": 48369,
    "PECOS": 48371,
    "POLK": 48373,
    "POTTER": 48375,
    "PRESIDIO": 48377,
    "RAINS": 48379,
    "RANDALL": 48381,
    "REAGAN": 48383,
    "REAL": 48385,
    "RED RIVER": 48387,
    "REEVES": 48389,
    "REFUGIO": 48391,
    "ROBERTS": 48393,
    "ROBERTSON": 48395,
    "ROCKWALL": 48397,
    "RUNNELS": 48399,
    "RUSK": 48401,
    "SABINE": 48403,
    "SAN AUGUSTINE": 48405,
    "SAN JACINTO": 48407,
    "SAN PATRICIO": 48409,
    "SAN SABA": 48411,
    "SCHLEICHER": 48413,
    "SCURRY": 48415,
    "SHACKELFORD": 48417,
    "SHELBY": 48419,
    "SHERMAN": 48421,
    "SMITH": 48423,
    "SOMERVELL": 48425,
    "STARR": 48427,
    "STEPHENS": 48429,
    "STERLING": 48431,
    "STONEWALL": 48433,
    "SUTTON": 48435,
    "SWISHER": 48437,
    "TARRANT": 48439,
    "TAYLOR": 48441,
    "TERRELL": 48443,
    "TERRY": 48445,
    "THROCKMORTON": 48447,
    "TITUS": 48449,
    "TOM GREEN": 48451,
    "TRAVIS": 48453,
    "TRINITY": 48455,
    "TYLER": 48457,
    "UPSHUR": 48459,
    "UPTON": 48461,
    "UVALDE": 48463,
    "VAL VERDE": 48465,
    "VAN ZANDT": 48467,
    "VICTORIA": 48469,
    "WALKER": 48471,
    "WALLER": 48473,
    "WARD": 48475,
    "WASHINGTON": 48477,
    "WEBB": 48479,
    "WHARTON": 48481,
    "WHEELER": 48483,
    "WICHITA": 48485,
    "WILBARGER": 48487,
    "WILLACY": 48489,
    "WILLIAMSON": 48491,
    "WILSON": 48493,
    "WINKLER": 48495,
    "WISE": 48497,
    "WOOD": 48499,
    "YOAKUM": 48501,
    "YOUNG": 48503,
    "ZAPATA": 48505,
    "ZAVALA": 48507,
}
inv_codes = {v: k for k, v in codes.items()}


def _as_data_dict(df):
    df["date"] = df["date"].map(str)
    county_dict = {}
    for county in df["fips"].unique():
        county_df = df[df["fips"] == county]
        county_data = county_df.T.drop(["fips"])
        values = [v.to_dict() for k, v in county_data.items()]
        county_dict[county] = values

    return county_dict

    df["date"] = df["date"].map(str)
    county_dict = {}
    for county in df["fips"].unique():
        county_df = df[df["fips"] == county]
        county_data = county_df.T.drop(["fips"])
        values = [v.to_dict() for k, v in county_data.items()]
        county_dict[county] = values

    return county_dict


def convert_date(date):
    """returns a datetime.date object from either a string representation or
    date-like object (datetime.date, datetime.datetime, or pandas.Timestamp)
    """
    return pd.Timestamp(date).date()


@tsutils.transform_args(county=tsutils.make_list)
def get_data(county, start=None, end=None):
    """
    Retrieve data.

    Parameters
    ----------
    county : ``None`` or str
        If specified, results will be limited to the county corresponding to the
        given 5-character Texas county fips code i.e. 48???.
    start : ``None`` or date (see :ref:`dates-and-times`)
        Results will be limited to data on or after this date. Default is the
        start of the calendar year for the end date.
    end : ``None`` or date (see :ref:`dates-and-times`)
        Results will be limited to data on or before this date. Default is the
        current date.

    Returns
    -------
    data : pandas.Dataframe
        A pandas.DataFrame representing the data.
    """
    end_date = datetime.date.today() if end is None else convert_date(end)
    if start is None:
        start_date = datetime.date(end_date.year, 1, 1)
    else:
        start_date = convert_date(start)

    dates = pd.date_range(start_date, end_date, freq="D")

    text_dates = dates[dates < CSV_SWITCHOVER]
    csv_dates = dates[dates >= CSV_SWITCHOVER]

    county = [inv_codes.get(c, c) for c in county]

    data_df = []
    for date in text_dates:
        resp = (
            pd.read_fwf(
                StringIO(
                    ar.retrieve_text(
                        [
                            f"https://twc.tamu.edu/weather_images/summ/summ{date.strftime('%Y%m%d')}.txt"
                        ]
                    )[0]
                ),
                skiprows=[0, 1],
                header=None,
                index_col=0,
            )
            .dropna()
            .loc[county, :]
        )
        resp.columns = ["KBDI_AVG", "KBDI_MAX", "KBDI_MIN"]
        resp = resp.unstack()
        resp = resp.transpose()
        print(resp)
        break

    print(df)
    fips_df = _fips_dataframe()
    df = pd.merge(df, fips_df, left_on="county", right_on="name")
    del df["name"]

    if county:
        df = df[df["fips"] == county]

    return df if as_dataframe else _as_data_dict(df)


def twc_tsget_df(county=None, start_date=None, end_date=None):
    df = get_data(
        county=county,
        start=pd.to_datetime(start_date),
        end=pd.to_datetime(end_date),
    )
    df = df.set_index("date")
    return df


@tsutils.doc(tsutils.docstrings)
def twc(county: int, start_date=None, end_date=None):
    r"""US/TX:station::D:Download Texas Weather Connection (TWC) data.

    This module provides direct access to `Texas Weather Connection`_ `Daily
    Keetch-Byram Drought Index (KBDI)`_ dataset.

    .. _Texas Weather Connection: http://twc.tamu.edu/
    .. _Daily Keetch-Byram Drought Index (KBDI): http://twc.tamu.edu/drought/kbdi

    Parameters
    ----------
    county : ``None`` or str
        If specified, results will be limited to the county corresponding to
        the given 5-character Texas county fips code i.e. 48.
    ${start_date}
    ${end_date}
    """
    return twc_tsget_df(county=county, start_date=start_date, end_date=end_date)


if __name__ == "__main__":
    r = twc_tsget_df(48501, start_date="2015-11-04", end_date="2015-12-05")

    print("UB EVERYTHING")
    print(r)
