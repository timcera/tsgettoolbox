"""
    ulmo.usace.rivergages.core
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module provides access to data provided by the `United States Army
    Corps of Engineers`_ `Rivergages`_ web site.

    .. _United States Army Corps of Engineers: http://www.usace.army.mil/
    .. _Rivergages: http://rivergages.mvr.usace.army.mil/WaterControl/new/layout.cfm
"""
import datetime
import os.path

import requests
from bs4 import BeautifulSoup

from tsgettoolbox.ulmo import util

USACE_RIVERGAGES_DIR = os.path.join(util.get_ulmo_dir(), "usace/rivergages/")
URL = "https://rivergages.mvr.usace.army.mil/WaterControl/datamining2.cfm"
DEFAULT_START_DATE = datetime.date(1800, 1, 1)


def get_stations():
    path = os.path.join(USACE_RIVERGAGES_DIR, "datamining_field_list.cfm")

    with util.open_file_for_url(URL, path, use_bytes=True) as f:
        soup = BeautifulSoup(f, features="lxml")
        options = soup.find("select", id="fld_station").find_all("option")
        stations = _parse_options(options)

    return stations


def get_station_data(
    station_code, parameter, start=None, end=None, min_value=None, max_value=None
):
    if min_value is None:
        min_value = -9000000
    if max_value is None:
        max_value = 9000000
    start_date = DEFAULT_START_DATE if start is None else util.convert_date(start)
    end_date = datetime.date.today() if end is None else util.convert_date(end)
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

    req = requests.post(
        URL, params=dict(sid=station_code), data=form_data, verify=False
    )
    soup = BeautifulSoup(req.content, features="lxml")
    data_table = soup.find("table").find_all("table")[-1]

    return dict([_parse_value(value_tr) for value_tr in data_table.find_all("tr")[2:]])


def get_station_parameters(station_code):
    req = requests.get(URL, params=dict(sid=station_code), verify=False)
    soup = BeautifulSoup(req.content, features="lxml")

    options = soup.find("select", id="fld_parameter").find_all()
    return _parse_options(options)


def _format_date(date):
    return f"{date.month}/{date.day}/{date.year}"


def _parse_options(options):
    return {
        option.attrs.get("value"): option.text.strip()
        for option in options
        if option.attrs.get("value") != ""
    }


def _parse_value(value_tr):
    date_td, value_td = value_tr.find_all("td")

    return (util.convert_date(date_td.text), float(value_td.text))
