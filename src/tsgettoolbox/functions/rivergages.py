"""
rivergages          US station:USACE river gages
"""

import datetime
import email.utils
import ftplib
import os
import urllib.parse
import warnings
from contextlib import contextmanager

import pandas as pd
import requests
from bs4 import BeautifulSoup
from platformdirs import user_data_dir

from tsgettoolbox.toolbox_utils.src.toolbox_utils import tsutils

URL = "http://rivergages.mvr.usace.army.mil/WaterControl/datamining2.cfm"
DEFAULT_START_DATE = datetime.date(1800, 1, 1)

__all__ = ["rivergages"]

# def get_station_data(station_code, parameter, start=None, end=None,
#         min_value=None, max_value=None):


def mkdir_if_doesnt_exist(dir_path):
    """makes a directory if it doesn't exist"""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def get_tsget_dir(sub_dir=None):
    return_dir = user_data_dir("tsgettoolbox", "tsgettoolbox")
    if sub_dir:
        return_dir = os.path.join(return_dir, sub_dir)
    mkdir_if_doesnt_exist(return_dir)
    return return_dir


USACE_RIVERGAGES_DIR = get_tsget_dir("usace/rivergages/")


def _parse_options(options):
    return {
        option.attrs.get("value"): option.text.strip()
        for option in options
        if option.attrs.get("value") != ""
    }


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
    open_file = open(open_path) if use_bytes is None else open(open_path, "rb")
    yield open_file

    if not leave_open:
        open_file.close()


def get_stations():
    path = os.path.join(USACE_RIVERGAGES_DIR, "datamining_field_list.cfm")

    with open_file_for_url(URL, path, use_bytes=True) as f:
        soup = BeautifulSoup(f)
        options = soup.find("select", id="fld_station").find_all("option")
        stations = _parse_options(options)

    return stations


def _format_date(date):
    return f"{date.month:02}/{date.day:02}/{date.year}"


def convert_date(date):
    """returns a datetime.date object from either a string representation or
    date-like object (datetime.date, datetime.datetime, or pandas.Timestamp)
    """
    return pd.Timestamp(date).date()


def _parse_value(value_tr):
    date_td, value_td = value_tr.find_all("td")

    return (convert_date(date_td.text), float(value_td.text))


def get_station_data(
    station_code, parameter, start=None, end=None, min_value=None, max_value=None
):
    if min_value is None:
        min_value = -9000000
    if max_value is None:
        max_value = 9000000
    start_date = DEFAULT_START_DATE if start is None else convert_date(start)
    end_date = datetime.date.today() if end is None else convert_date(end)
    start_date_str = _format_date(start_date)
    end_date_str = _format_date(end_date)

    form_data = {
        "fld_station": station_code,
        "fld_parameter": parameter,
        "fld_from": min_value,
        "fld_to": max_value,
        "fld_fromdate": start_date_str,
        "fld_todate": end_date_str,
        "hdn_excel": "",
    }

    req = requests.post(URL, params=dict(sid=station_code), data=form_data, timeout=60)
    soup = BeautifulSoup(req.content)
    data_table = soup.find("table").find_all("table")[-1]

    return dict([_parse_value(value_tr) for value_tr in data_table.find_all("tr")[2:]])


def get_station_parameters(station_code):
    req = requests.get(URL, params=dict(sid=station_code), timeout=60)
    soup = BeautifulSoup(req.content)

    options = soup.find("select", id="fld_parameter").find_all()
    return _parse_options(options)


def rivergages(station_code, parameter, start_date=None, end_date=None):
    """US:station:::USACE river gages

    Stage and flow from systems managed by the U.S. Army Corps of Engineers.

    Parameters
    ----------
    station_code : str
        The station code for the
        station.
    parameter : str
        Parameter
        code.
    start_date
        The start date of the desired
        time-series.
    end_date
        The end data of the desired
        time-series.
    """
    tstations = get_stations()
    if station_code not in tstations:
        raise ValueError(
            tsutils.error_wrapper(
                f"""
                Station code {station_code} not in available stations:
                {tstations.keys}
                """
            )
        )

    tparameters = get_station_parameters(station_code)
    if parameter not in tparameters:
        raise ValueError(
            tsutils.error_wrapper(
                f"""
                Parameter code {parameter} not in available parameters at
                station {station_code}: {tparameters}
                """
            )
        )
    df = get_station_data(
        station_code,
        parameter,
        start=pd.to_datetime(start_date),
        end=pd.to_datetime(end_date),
    )
    df = pd.DataFrame.from_dict(df, orient="index")
    df.sort_index(inplace=True)
    df.index.name = "Datetime"
    df.columns = [f"{station_code}_{parameter}"]
    return df


if __name__ == "__main__":
    r = rivergages("BIVO1", "HL", start_date="2015-11-04", end_date="2015-12-05")

    print("BIVOI HL")
    print(r)
