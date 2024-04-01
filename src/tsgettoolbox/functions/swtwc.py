"""
swtwc               US/region station:USACE Southwest Division, Tulsa
                    Water Control
"""

import datetime
from io import StringIO

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

__all__ = ["swtwc"]


def _split_line(line, n):
    return [line[i : i + n].strip() for i in range(0, len(line), n)][:-1]


def convert_date(date):
    """returns a datetime.date object from either a string representation or
    date-like object (datetime.date, datetime.datetime, or pandas.Timestamp)
    """
    return pd.Timestamp(date).date()


def _convert_datetime(s, year):
    fmt = "%m/%d %H:%M"
    return datetime.datetime.strptime(s, fmt).replace(year=year)


def dict_from_dataframe(dataframe):
    if isinstance(dataframe.index, pd.PeriodIndex):
        dataframe.index = dataframe.index.to_timestamp().astype("str")
    if isinstance(dataframe.index, pd.DatetimeIndex):
        dataframe.index = [str(i) for i in dataframe.index]

    if pd.__version__ >= "0.13.0":
        return dataframe.where((pd.notnull(dataframe)), None).to_dict(orient="index")

    for column_name in dataframe.columns:
        dataframe[column_name][pd.isnull(dataframe[column_name])] = None
    return dataframe.T.to_dict()


def get_station_data(station_code, date=None, as_dataframe=False):
    """
    Fetch data for a station at a given date.

    Parameters
    ----------
    station_code: str
        The station code to fetch data for. A list of stations can be retrieved with
        ``get_stations()``
    date : ``None`` or date (see :ref:`dates-and-times`)
        The date of the data to be queried. If date is ``None`` (default), then
        data for the current day is retreived.
    as_dataframe : bool
        This determines what format values are returned as. If ``False``
        (default), the values dict will be a dict with timestamps as keys mapped
        to a dict of gauge variables and values. If ``True`` then the values
        dict will be a pandas.DataFrame object containing the equivalent
        information.

    Returns
    -------
    data_dict : dict
        A dict containing station information and values.
    """

    if date is None:
        date_str = "current"
        year = datetime.date.today().year
    else:
        date = convert_date(date)
        date_str = date.strftime("%Y%m%d")
        year = date.year

    filename = f"{station_code}.{date_str}.html"
    data_url = f"https://www.swt-wc.usace.army.mil/webdata/gagedata/{filename}"

    # requests without User-Agent header get rejected
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"
    }
    resp = requests.get(data_url, headers=headers, timeout=60)
    soup = BeautifulSoup(resp.content)
    pre = soup.find("pre")
    if pre is None:
        error_msg = f"no data could be found for station code {station_code} and date {date} (url: {data_url})"
        raise ValueError(error_msg)
    sio = StringIO(str(pre.text.strip()))

    first_line = sio.readline()
    split = first_line[8:].strip().split()

    station_dict = {"code": split[0], "description": " ".join(split[1:])}
    second_line = sio.readline()
    station_dict["station_type"] = second_line.strip().split(":")[1].strip()

    notes = []

    while 1:
        next_line = sio.readline()
        if ":" in next_line:
            notes.append(next_line.strip())
        else:
            break

    if notes:
        station_dict["notes"] = "\n".join(notes)

    variable_names = _split_line(sio.readline()[11:], 10)
    variable_units = _split_line(sio.readline()[11:], 10)
    variable_sources = _split_line(sio.readline()[11:], 10)

    station_dict["variables"] = {
        name: {"unit": unit, "source": source}
        for name, unit, source in zip(variable_names, variable_units, variable_sources)
    }

    station_dict["timezone"] = sio.readline().strip().strip("()")
    column_names = ["datetime"] + variable_names
    widths = [14] + ([10] * len(variable_names))
    converters = {
        variable_name: lambda x: float(x) if x != "----" else np.nan
        for variable_name in variable_names
    }
    date_parser = lambda x: _convert_datetime(x, year)
    dataframe = pd.read_fwf(
        sio,
        names=column_names,
        widths=widths,
        index_col=["datetime"],
        na_values=["----"],
        converters=converters,
        parse_dates=True,
        date_parser=date_parser,
    )

    # parse out rows that are all nans (e.g. end of "current" page)
    dataframe = dataframe[~np.isnan(dataframe.T.sum())]

    if as_dataframe:
        station_dict["values"] = dataframe
    else:
        station_dict["values"] = dict_from_dataframe(dataframe)

    return station_dict


def swtwc(station_code, date=None):
    """US/region:station:::USACE Southwest Division, Tulsa Water Control

    Parameters
    ----------
    station_code
        The station code.
    date
        The date for the downloaded data.
    """
    date = datetime.datetime.now() if date is None else pd.to_datetime(date)
    alldict = get_station_data(station_code, date=date, as_dataframe=True)
    df = alldict["values"]
    df.columns = [f"{i}:{alldict['variables'][i]['unit']}" for i in df.columns]
    df.columns = [i.replace("  ", "_").replace(" ", "_") for i in df.columns]
    return df.tz_localize(alldict["timezone"])
