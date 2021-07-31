# -*- coding: utf-8 -*-
from typing import Optional, Union

import pandas as pd
from mando import command
from tstoolbox import tsutils

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

try:
    from mando.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter


@command("cdec", formatter_class=HelpFormatter, doctype="numpy")
@tsutils.doc(tsutils.docstrings)
def cdec_cli(
    station_id, dur_code=None, sensor_num=None, start_date=None, end_date=None
):
    r"""Access data from the 'California Department of Water Resources'.

    The web site is called the 'California Data Exchange Center'.

    California Department of Water Resources: http://www.water.ca.gov/
    California Data Exchange Center: http://cdec.water.ca.gov

    Downloads data for a set of CDEC station and sensor ids. If either is not
    provided, all available data will be downloaded.

    Parameters
    ----------
    station_id: str
        [optional, default is None]

        Each string is the CDEC station ID and consist of three capital
        letters.

    sensor_num: integer, comma separated integers or ``None``
        [optional, default is None]

        If ``None`` will get all sensors at `station_id`.

        SELECTED CDEC SENSOR NUMBERS (these are not available for all
        sites):

        +------------+-------------------------------------------+
        | sensor_num | Description                               |
        +============+===========================================+
        | 1          | river stage [ft]                          |
        +------------+-------------------------------------------+
        | 2          | precipitation accumulated [in]            |
        +------------+-------------------------------------------+
        | 3          | SWE [in]                                  |
        +------------+-------------------------------------------+
        | 4          | air temperature [F]                       |
        +------------+-------------------------------------------+
        | 5          | EC [ms/cm]                                |
        +------------+-------------------------------------------+
        | 6          | reservoir elevation [ft]                  |
        +------------+-------------------------------------------+
        | 7          | reservoir scheduled release [cfs]         |
        +------------+-------------------------------------------+
        | 8          | full natural flow [cfs]                   |
        +------------+-------------------------------------------+
        | 15         | reservoir storage [af]                    |
        +------------+-------------------------------------------+
        | 20         | flow -- river discharge [cfs]             |
        +------------+-------------------------------------------+
        | 22         | reservoir storage change [af]             |
        +------------+-------------------------------------------+
        | 23         | reservoir outflow [cfs]                   |
        +------------+-------------------------------------------+
        | 24         | Evapotranspiration [in]                   |
        +------------+-------------------------------------------+
        | 25         | water temperature [F]                     |
        +------------+-------------------------------------------+
        | 27         | water turbidity [ntu]                     |
        +------------+-------------------------------------------+
        | 28         | chlorophyll [ug/l]                        |
        +------------+-------------------------------------------+
        | 41         | flow -- mean daily [cfs]                  |
        +------------+-------------------------------------------+
        | 45         | precipitation incremental [in]            |
        +------------+-------------------------------------------+
        | 46         | runoff volume [af]                        |
        +------------+-------------------------------------------+
        | 61         | water dissolved oxygen [mg/l]             |
        +------------+-------------------------------------------+
        | 62         | water pH value [pH]                       |
        +------------+-------------------------------------------+
        | 64         | pan evaporation (incremental) [in]        |
        +------------+-------------------------------------------+
        | 65         | full natural flow [af]                    |
        +------------+-------------------------------------------+
        | 66         | flow -- monthly volume [af]               |
        +------------+-------------------------------------------+
        | 67         | accretions (estimated) [af]               |
        +------------+-------------------------------------------+
        | 71         | spillway discharge [cfs]                  |
        +------------+-------------------------------------------+
        | 74         | lake evaporation (computed) [cfs]         |
        +------------+-------------------------------------------+
        | 76         | reservoir inflow [cfs]                    |
        +------------+-------------------------------------------+
        | 85         | control regulating discharge [cfs]        |
        +------------+-------------------------------------------+
        | 94         | top conservation storage (reservoir) [af] |
        +------------+-------------------------------------------+
        | 100        | water EC [us/cm]                          |
        +------------+-------------------------------------------+

    dur_code: str, comma separated strings, or ``None``
        [optional, default is None]

        Possible values are 'E', 'H', 'D', and 'M' but not
        all of these time resolutions are available at every station.

        +----------+-------------+
        | dur_code | Description |
        +==========+=============+
        | E        | event       |
        +----------+-------------+
        | H        | hourly      |
        +----------+-------------+
        | D        | daily       |
        +----------+-------------+
        | M        | monthly     |
        +----------+-------------+

    {start_date}

    {end_date}

    """
    tsutils._printiso(
        cdec(
            station_id,
            dur_code=dur_code,
            sensor_num=sensor_num,
            start_date=start_date,
            end_date=end_date,
        )
    )


DEFAULT_START_DATE = "01/01/1901"
DEFAULT_END_DATE = "Now"


def get_stations():
    """Fetch information on all CDEC sites.

    Returns
    -------
    df : pandas DataFrame
        a pandas DataFrame (indexed on site id) with station information.

    """
    # I haven't found a better list of stations, seems pretty janky
    # to just have them in a file, and not sure if/when it is updated.
    url = "http://cdec.water.ca.gov/misc/all_stations.csv"
    # the csv is malformed, so some rows think there are 7 fields
    col_names = ["id", "meta_url", "name", "num", "lat", "lon", "junk"]
    df = pd.read_csv(url, names=col_names, header=None, quotechar="'", index_col=0)

    return df


def get_sensors(sensor_id=None):
    """
    Get a list of sensor ids as a DataFrame indexed on sensor number.

    Can be limited by a list of numbers.

    Parameters
    ----------
    sites : iterable of integers or ``None``

    Returns
    -------
    df : pandas DataFrame
        a python dict with site codes mapped to site information

    """
    url = "http://cdec.water.ca.gov/misc/senslist.html"
    df = pd.read_html(url, header=0)[0]
    df.set_index("Sensor No")

    if sensor_id is None:
        return df
    return df.ix[sensor_id]


def get_station_sensors(station_ids=None, sensor_ids=None, resolutions=None):
    """Get available sensors for the given stations.

    Get available sensors, sensor ids and time resolutions. If no station ids
    are provided, all available stations will be used (this is not recommended,
    and will probably take a really long time).

    The list can be limited by a list of sensor numbers, or time resolutions
    if you already know what you want. If none of the provided sensors or
    resolutions are available, an empty DataFrame will be returned for that
    station.

    Parameters
    ----------
    station_ids : iterable of strings or ``None``
    sensor_ids : iterable of integers or ``None``
        check out  or use the ``get_sensors()`` function to see a list of
        available sensor numbers
    resolutions : iterable of strings or ``None``
        Possible values are 'event', 'hourly', 'daily', and 'monthly' but not
        all of these time resolutions are available at every station.

    Returns
    -------
    dict : a python dict
        a python dict with site codes as keys with values containing pandas
        DataFrames of available sensor numbers and metadata.

    """
    station_sensors = {}
    unit_conv = {
        "INCHES": "in",
        "AF": "acre feet",
        "CFS": "cfs",
        "FEET": "ft",
    }

    if station_ids is None:
        station_ids = get_stations().index

    for station_id in station_ids:
        url = "http://cdec.water.ca.gov/dynamicapp/staMeta?station_id={}".format(
            station_id
        )
        sensor_list = pd.read_html(url)[1]
        sensor_list.columns = [
            "sensor_description",
            "sensor_number",
            "duration",
            "plot",
            "data_collection",
            "data_available",
        ]
        v = list(sensor_list["sensor_description"].to_dict().values())
        split = [i.split(",") for i in v]
        var_names = ["_".join(x[:-1]).strip() for x in split]
        units = [x[-1][1:] for x in split]
        units = [unit_conv.get(i, i) for i in units]
        var_names = [":".join([i, j]) for i, j in zip(var_names, units)]
        var_resolution = [x[1:-1] for x in sensor_list["duration"]]

        sensor_list["resolution"] = var_resolution
        sensor_list[
            "variable"
        ] = var_names  # [x + y for x, y in zip(var_names, var_resolution)]

        station_sensors[station_id] = _limit_sensor_list(
            sensor_list, sensor_ids, resolutions
        )

    return station_sensors


def get_data(station_ids=None, sensor_ids=None, resolutions=None, start=None, end=None):
    """Download data for a set of CDEC station and sensor ids.

    If either is not provided, all available data will be downloaded. Be really
    careful with choosing hourly resolution as the data sets are big, and
    CDEC's servers are slow as molasses in winter.

    Parameters
    ----------
    station_ids : iterable of strings or ``None``
    sensor_ids : iterable of integers or ``None``
        check out  or use the ``get_sensors()`` function to see a list of
        available sensor numbers
    resolutions : iterable of strings or ``None``
        Possible values are 'event', 'hourly', 'daily', and 'monthly' but not
        all of these time resolutions are available at every station.

    Returns
    -------
    dict : a python dict
        a python dict with site codes as keys. Values will be nested dicts
        containing all of the sensor/resolution combinations.

    """
    if start is None:
        start_date = pd.Timestamp(DEFAULT_START_DATE).date()
    else:
        start_date = pd.Timestamp(start).date()
    if end is None:
        end_date = pd.Timestamp(DEFAULT_END_DATE).date()
    else:
        end_date = pd.Timestamp(end).date()

    start_date_str = start_date.isoformat()
    end_date_str = end_date.isoformat()

    if station_ids is None:
        station_ids = get_stations().index

    sensors = get_station_sensors(station_ids, sensor_ids, resolutions)

    d = {}

    for station_id, sensor_list in list(sensors.items()):
        station_data = {}

        for _, row in sensor_list.iterrows():
            res = row["resolution"]
            var = row["variable"]
            sensor_id = row["sensor_number"]

            url = (
                "http://cdec.water.ca.gov/dynamicapp/req/CSVDataServlet"
                + "?Stations="
                + station_id
                + "&dur_code="
                + res_to_dur_code_map[res]
                + "&SensorNums="
                + str(sensor_id)
                + "&Start="
                + start_date_str
                + "&End="
                + end_date_str
            )
            station_data[var] = pd.read_csv(
                url,
                parse_dates=["DATE TIME"],
                index_col="DATE TIME",
                na_values="m",
            )["VALUE"]
            station_data[var].columns = ["datetime", "value"]

        d[station_id] = station_data

    return d


def _limit_sensor_list(sensor_list, sensor_ids, resolution):

    if sensor_ids is not None:
        sensor_list = sensor_list[[x in sensor_ids for x in sensor_list.sensor_number]]

    if resolution is not None:
        sensor_list = sensor_list[[x in resolution for x in sensor_list.resolution]]

    return sensor_list


res_to_dur_code_map = {"hourly": "H", "daily": "D", "monthly": "M", "event": "E"}


def download_data(
    station_id, sensor_num=None, dur_code=None, start_date=None, end_date=None
):

    if isinstance(sensor_num, (str, bytes)):
        sensor_num = [int(i) for i in sensor_num.split(".")]
    elif isinstance(sensor_num, int):
        sensor_num = [sensor_num]

    if isinstance(dur_code, (str, bytes)):
        dur_code = dur_code.split(",")

        mapd = {"D": "daily", "E": "event", "H": "hourly", "M": "monthly"}

        dur_code = [mapd[i] for i in dur_code]

    d = get_data(
        [station_id],
        sensor_ids=sensor_num,
        resolutions=dur_code,
        start=start_date,
        end=end_date,
    )

    nd = pd.DataFrame()
    for key in d[station_id]:
        nnd = pd.DataFrame(d[station_id][key])
        nnd.columns = [key]
        nd = nd.join(nnd, how="outer")
    nd.rename(
        lambda x: x.replace(",", "_").replace(" ", "_").replace("__", "_"),
        axis="columns",
        inplace=True,
    )
    nd = nd.tz_localize("UTC").tz_convert("Etc/GMT+8")
    nd.index.name = "Datetime:PST"
    return nd


def cdec(
    station_id: str,
    dur_code: Optional[Union[list, str]] = None,
    sensor_num=None,
    start_date=None,
    end_date=None,
):
    r"""Access data from the `California Department of Water Resources`_."""
    df = download_data(
        station_id,
        dur_code=dur_code,
        sensor_num=sensor_num,
        start_date=tsutils.parsedate(start_date),
        end_date=tsutils.parsedate(end_date),
    )
    return df


cdec.__doc__ = cdec_cli.__doc__


if __name__ == "__main__":
    r = download_data(
        "PAR",
        start_date="2017-01-01",
        end_date="2017-10-02",
        dur_code="D",
        sensor_num=45,
    )

    print("PAR PRECIPITATION")
    print(r)

    r = download_data(
        "PAR",
        start_date="2017-01-01",
        end_date="2017-10-02",
        dur_code="H",
        sensor_num=6,
    )

    print("PAR RESERVOIR VOLUME")
    print(r)

    r = download_data(
        "PAR", start_date="2017-01-01", end_date="2017-10-02", dur_code="H"
    )

    print("PAR HOURLY")
    print(r)

    r = download_data("PAR", start_date="2017-01-01", end_date="2017-10-02")

    print("PAR EVERYTHING")
    print(r)
