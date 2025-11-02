"""
cpc                 US/region W: Climate Prediction Center, Weekly Drought
                    Index
"""

import datetime
import email.utils
import ftplib
import os
import urllib.parse
import warnings
from contextlib import contextmanager
from typing import Optional

import numpy as np
import pandas as pd
import requests
from platformdirs import user_data_dir

from tsgettoolbox.toolbox_utils.src.toolbox_utils import tsutils

__all__ = ["cpc"]

unit_conv = {
    "precipitation": "precipitation:in",
    "temperature": "temperature:degF",
    "potential_evap": "potential_evap:in",
    "runoff": "runoff:in",
    "soil_moisture_upper": "soil_moisture_upper:in",
    "soil_moisture_lower": "soil_moisture_lower:in",
}


def mkdir_if_doesnt_exist(dir_path):
    """makes a directory if it doesn't exist"""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def get_tsget_dir(sub_dir=None):
    return_dir = user_data_dir(appname="tsgettoolbox", ensure_exists=True)
    if sub_dir:
        return_dir = os.path.join(return_dir, sub_dir)
    mkdir_if_doesnt_exist(return_dir)
    return return_dir


# directory where drought data will be stashed
CPC_DROUGHT_DIR = os.path.join(get_tsget_dir(), "cpc/drought")

# state codes (note: these are not FIPS codes)
STATE_CODES = {
    "AL": 1,
    "AZ": 2,
    "AR": 3,
    "CA": 4,
    "CO": 5,
    "CT": 6,
    "DE": 7,
    "FL": 8,
    "GA": 9,
    "IA": 13,
    "ID": 10,
    "IL": 11,
    "IN": 12,
    "KS": 14,
    "KY": 15,
    "LA": 16,
    "MA": 19,
    "MD": 18,
    "ME": 17,
    "MI": 20,
    "MN": 21,
    "MO": 23,
    "MS": 22,
    "MT": 24,
    "NC": 31,
    "ND": 32,
    "NE": 25,
    "NH": 27,
    "NJ": 28,
    "NM": 29,
    "NV": 26,
    "NY": 30,
    "OH": 33,
    "OK": 34,
    "OR": 35,
    "PA": 36,
    "PR": 66,
    "RI": 37,
    "SC": 38,
    "SD": 39,
    "TN": 40,
    "TX": 41,
    "UT": 42,
    "VA": 44,
    "VT": 43,
    "WA": 45,
    "WI": 47,
    "WV": 46,
    "WY": 48,
}


def _parse_rfc_1123_timestamp(timestamp_str):
    return datetime.datetime(*email.utils.parsedate(timestamp_str)[:6])


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


def _as_data_dict(dataframe):
    data_dict = {}
    for state in dataframe["state"].unique():
        state_dict = {}
        state_dataframe = dataframe[dataframe["state"] == state]
        for name, group in state_dataframe.groupby(["state", "climate_division"]):
            _, climate_division = name
            climate_division_data = group.T.drop(["state", "climate_division"])
            values = [_value_dict(value) for k, value in climate_division_data.items()]
            state_dict[climate_division] = values
        data_dict[state] = state_dict
    return data_dict


def _value_dict(value):
    value_dict = value.to_dict()
    value_dict["period"] = str(value_dict["period"])
    return value_dict


def _convert_week_numbers(dataframe):
    """convert a dataframe's week numbers to period objects"""
    weeks = [key for key, group in dataframe.groupby(["year", "week"])]
    periods = [(week[0], week[1], _period_for_week(*week)) for week in weeks]
    period_dataframe = pd.DataFrame(periods, columns=["year", "week", "period"])
    merged = pd.merge(
        dataframe, period_dataframe, left_on=["year", "week"], right_on=["year", "week"]
    )
    column_names = dataframe.columns.tolist()
    column_names.remove("week")
    column_names.remove("year")
    column_names.insert(2, "period")
    return merged[column_names]


def _convert_state_codes(dataframe):
    """adds state abbreviations to a dataframe, based on state codes"""
    state_codes = pd.DataFrame(
        np.array(
            list(STATE_CODES.items()),
            dtype=np.dtype([("state", "|U2"), ("code", int)]),
        )
    )
    merged = pd.merge(
        dataframe, state_codes, left_on="state_code", right_on="code", how="left"
    )
    column_names = dataframe.columns.tolist()
    column_names.remove("state_code")
    column_names.insert(0, "state")
    return merged[column_names]


def _period_for_week(year, week_number):
    """returns a pandas.Period for a given growing season year and week number"""
    first_sunday = _first_sunday(year)
    return pd.Period(first_sunday, freq="W-SAT") + week_number - 1


def _reindex_data(dataframe):
    dataframe = _convert_week_numbers(dataframe)
    dataframe = _convert_state_codes(dataframe)
    return dataframe.set_index(["state", "climate_division", "period"], drop=False)


def _parse_data_file(data_file, palmer_format, year, current_year_flag):
    """
    based on the fortran format strings:
        format2: FORMAT(I4,3I2,F4.1,F4.0,10F6.2,4F6.4,F6.3,10F6.2,F4.0,12F6.2)
        format4: FORMAT(2I4,I2,F4.1,F4.0,10F6.2,4F6.4,F6.3,10F6.2,F4.0,12F6.2)
        format5: FORMAT(2I4,I2,F5.2,F5.1,10F6.2,4F6.4,F6.3,10F6.2,F4.0,12F6.2)
    """
    if palmer_format == "format5":
        delim_sequence = (
            (2, 2, 4, 2, 5, 5)
            + 10 * (6,)
            + 4 * (6,)
            + (6,)
            + 10 * (6,)
            + (4,)
            + 12 * (6,)
        )
        use_columns = (0, 1, 2, 3, 4, 5, 9, 15, 28, 29, 37, 40, 41)
    elif palmer_format == "format4":
        delim_sequence = (
            (2, 2, 4, 2, 4, 4)
            + 10 * (6,)
            + 4 * (6,)
            + (6,)
            + 10 * (6,)
            + (4,)
            + 12 * (6,)
        )
        use_columns = (0, 1, 2, 3, 4, 5, 9, 15, 28, 29, 37, 40, 41)
    elif palmer_format == "format2":
        delim_sequence = (
            (2, 2, 2, 2, 2, 4, 4)
            + 10 * (6,)
            + 4 * (6,)
            + (6,)
            + 10 * (6,)
            + (4,)
            + 12 * (6,)
        )
        use_columns = (0, 1, 2, 3, 5, 6, 10, 16, 29, 30, 38, 41, 42)
    else:
        raise NotImplementedError(
            "we have not implemented the format for given date range"
        )

    dtype = [
        ("state_code", "i1"),
        ("climate_division", "i1"),
        ("year", "i4"),
        ("week", "i4"),
        ("precipitation", "f8"),
        ("temperature", "f8"),
        ("potential_evap", "f8"),
        ("runoff", "f8"),
        ("soil_moisture_upper", "f8"),
        ("soil_moisture_lower", "f8"),
        ("pdsi", "f8"),
        ("cmi", "f8"),
    ]

    data_array = np.genfromtxt(
        data_file, dtype=dtype, delimiter=delim_sequence, usecols=use_columns
    )
    if not current_year_flag:
        data_array["year"] = year
    return pd.DataFrame(data_array)


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
    open_file = open(open_path) if use_bytes is None else open(open_path, "rb")
    yield open_file

    if not leave_open:
        open_file.close()


def _open_data_file(url):
    """returns an open file handle for a data file; downloading if necessary or otherwise using a previously downloaded file"""
    file_name = url.rsplit("/", 1)[-1]
    file_path = os.path.join(CPC_DROUGHT_DIR, file_name)
    return open_file_for_url(url, file_path, check_modified=True, use_bytes=True)


def _get_data_format(year):
    if year >= 2001:
        return "format5"
    return "format4" if 1997 <= year <= 2000 else "format2"


def _first_sunday(year):
    """returns the first Sunday of a growing season, which is the first Sunday
    after the first Wednesday in March
    """
    first_day = datetime.date(year, 3, 1)
    if first_day.weekday() == 6:
        return first_day
    if first_day.weekday() <= 2:
        return first_day - pd.tseries.offsets.Week(weekday=6)
    return first_day + pd.tseries.offsets.Week(weekday=6)


def _week_number(date):
    """returns the growing season week number for a given datetime.date"""
    first_sunday = _first_sunday(date.year)
    date_ts = pd.Timestamp(date)
    first_sunday_ts = pd.Timestamp(first_sunday)
    if date_ts < first_sunday_ts:
        first_sunday_ts = pd.Timestamp(_first_sunday(date.year - 1))
    days_since_first_sunday = (date_ts - first_sunday_ts).days
    return (first_sunday_ts.year, (days_since_first_sunday // 7) + 1)


def _url_exists(url):
    return requests.head(url, timeout=10).status_code == 200


def _get_data_url(year):
    current_year, _ = _week_number(datetime.date.today())
    if year == current_year:
        return ("https://ftp.cpc.ncep.noaa.gov/htdocs/temp4/current.data", True)
    if year == current_year - 1:
        url = (
            f"https://ftp.cpc.ncep.noaa.gov/htdocs/temp2/palmer{str(year)[-2:]}-PRELIM",
            False,
        )
        if not _url_exists(url[0]):
            url = ("https://ftp.cpc.ncep.noaa.gov/htdocs/temp4/current.data", True)
        return url
    if year <= 1985:
        return ("https://ftp.cpc.ncep.noaa.gov/htdocs/temp2/palmer73-85", False)
    url = (
        f"https://ftp.cpc.ncep.noaa.gov/htdocs/temp2/palmer{str(year)[-2:]}",
        False,
    )
    if not _url_exists(url[0]):
        url = (
            f"https://ftp.cpc.ncep.noaa.gov/htdocs/temp2/palmer{str(year)[-2:]}-PRELIM",
            False,
        )
    return url


def convert_date(date):
    """returns a datetime.date object from either a string representation or
    date-like object (datetime.date, datetime.datetime, or pandas.Timestamp)
    """
    return pd.Timestamp(date).to_pydatetime()


def get_data(
    state=None, climate_division=None, start=None, end=None, as_dataframe=False
):
    """
    Retrieve data.

    Parameters
    ----------
    state: ``None`` or str
        If specified, results will be limited to the state corresponding to the
        given 2-character state code.
    climate_division: ``None`` or int
        If specified, results will be limited to the climate division.
    start: ``None`` or date (see :ref:`dates-and-times`)
        Results will be limited to those after the given date. Default is the
        start of the current calendar year.
    end: ``None`` or date (see :ref:`dates-and-times`)
        If specified, results will be limited to data before this date.
    as_dataframe: bool
        If ``False`` (default), a dict with a nested set of dicts will be
        returned with data indexed by state, then climate division. If ``True``
        then a pandas.DataFrame object will be returned.  The pandas dataframe
        is used internally, so setting this to ``True`` is a little bit faster
        as it skips a serialization step.

    Returns
    -------
    data : dict or pandas.Dataframe
        A dict or pandas.DataFrame representing the data. See the
        ``as_dataframe`` parameter for more.
    """

    end_date = (None if end is None else convert_date(end)) or datetime.datetime.now()

    start_date = (None if start is None else convert_date(start)) or datetime.datetime(
        end_date.year, 1, 1
    )

    start_year, _ = _week_number(start_date)
    end_year, _ = _week_number(end_date)

    state_code = STATE_CODES.get(state.upper()) if state else None
    data = None
    for year in range(start_year, end_year + 1):
        url, current_year_flag = _get_data_url(year)
        format_type = _get_data_format(year)
        with _open_data_file(url) as data_file:
            year_data = _parse_data_file(
                data_file, format_type, year, current_year_flag
            )

        if state_code:
            year_data = year_data[year_data["state_code"] == state_code]
        if climate_division:
            year_data = year_data[year_data["climate_division"] == climate_division]

        year_data = _reindex_data(year_data)

        if data is None:
            data = year_data
        else:
            # some data are duplicated (e.g. final data from 2011 stretches into
            # prelim data of 2012), so just take those that are new
            append_index = year_data.index.difference(data.index)
            if len(append_index):
                data = pd.concat([data, year_data.loc[append_index]])

    # restrict results to date range
    period_index = pd.PeriodIndex(data["period"]).to_timestamp()
    periods_in_range = (period_index >= start_date) & (period_index <= end_date)
    data = data[periods_in_range]

    # this does what data.reset_index() should do, but at least as of 0.10.1, that sets
    # will cast period objects to ints
    try:
        data.index = period_index.to_timestamp()
    except AttributeError:
        data.index = np.arange(len(data))
    return data if as_dataframe else _as_data_dict(data)


def tsget_df(state=None, climate_division=None, start_date=None, end_date=None):
    """Get data from tsget.cpc.drought.core.get_data() and return a dataframe."""
    df = get_data(
        state=state,
        climate_division=climate_division,
        start=start_date,
        end=end_date,
        as_dataframe=True,
    )
    df = df.set_index("period")
    df.index = pd.PeriodIndex(df.index)
    df.index.name = "Datetime"
    df.columns = [unit_conv.get(i, i) for i in df.columns]
    df = df.rename(
        {"pdsi": "palmer_drought_severity_index", "cmi": "crop_moisture_index"},
        axis="columns",
    )
    return df


@tsutils.doc(tsutils.docstrings)
def cpc(
    state: Optional[str] = None,
    climate_division: Optional[int] = None,
    start_date=None,
    end_date=None,
):
    r"""US:region::W:Climate Prediction Center, Weekly Drought Index

    Climate Prediction Center:

        www.cpc.ncep.noaa.gov

    Weekly Drought Index:

        www.cpc.ncep.noaa.gov/products/analysis_monitoring/cdus/palmer_drought

    The `climate_division` integer value identifies a portion of the
    desired `state` divided along county boundaries. Maps of the climate
    divisions within each state are at:

    www.cpc.ncep.noaa.gov/products/analysis_monitoring/regional_monitoring/CLIM_DIVS/states_counties_climate-divisions.shtml

    The only way to get a time-series is to specify both `state` and
    `climate_division` keywords.

    Command Line ::

        tsgettoolbox cpc --state=FL --climate_division=1 --start_date 2017-01-01

    Python API ::

        df = tsgettoolbox.cpc(state="FL",
                              climate_division=1,
                              start_date="2017-01-01",
                              end_date="2017-02-01")

    Parameters
    ----------
    state : ``None`` or str
        [optional]

        If specified, results will be limited to the state corresponding to the
        given 2-character state code.

    climate_division : ``None`` or int
        [optional]

        If specified, results will be limited to the climate division.

    ${start_date}

    ${end_date}
    """
    return tsget_df(
        state=state,
        climate_division=climate_division,
        start_date=tsutils.parsedate(start_date),
        end_date=tsutils.parsedate(end_date),
    )


if __name__ == "__main__":
    r = tsget_df(
        state="FL", climate_division=1, start_date="2017-01-01", end_date="2017-10-02"
    )

    print("FL EVERYTHING")
    print(r)
