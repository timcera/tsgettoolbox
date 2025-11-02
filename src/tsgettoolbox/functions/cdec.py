"""
cdec                US/CA station I,H,D,M: California Department of Water
                    Resources
"""

import datetime
import warnings
from pathlib import Path
from typing import Optional, Union

import pandas as pd

from tsgettoolbox.toolbox_utils.src.toolbox_utils import tsutils

__all__ = ["cdec"]

dur_code_map = {
    "daily": "D",
    "event": "E",
    "hourly": "H",
    "monthly": "M",
    "d": "D",
    "e": "E",
    "h": "H",
    "m": "M",
}

fname_code_map = {
    "D": "daily",
    "E": "event",
    "H": "hourly",
    "M": "monthly",
}

sensor_num_map = {
    "river_stage": 1,
    "stage": 1,
    "precipitation": 2,
    "swe": 3,
    "snow_water_equivalent": 3,
    "air_temperature": 4,
    "ec": 5,
    "reservoir_elevation": 6,
    "reservoir_scheduled_release": 7,
    "full_natural_flow:cfs": 8,
    "reservoir_storage": 15,
    "flow": 20,
    "reservoir_storage_change": 22,
    "reservoir_outflow": 23,
    "evapotranspiration": 24,
    "water_temperature": 25,
    "water_turbidity": 27,
    "turbidity": 27,
    "chlorophyll": 28,
    "flow_daily": 41,
    "precipitation incremental": 45,
    "runoff_volume": 46,
    "dissolved_oxygen": 61,
    "water_dissolved_oxygen": 61,
    "do": 61,
    "ph": 62,
    "pan_evaporation": 64,
    "full_natural_flow:acre_ft": 65,
    "flow_monthly": 66,
    "accretions": 67,
    "spillway_discharge": 71,
    "spillway_flow": 71,
    "lake_evaporation": 74,
    "evaporation": 74,
    "reservoir_inflow": 76,
    "control_regulating_discharge": 85,
    "top_conservation_storage": 94,
    "water_ec": 100,
}


DEFAULT_START_DATE = "01/01/1901"


def get_stations():
    """
    Fetch information on all CDEC sites.

    Returns
    -------
    df : pandas DataFrame
        a pandas DataFrame (indexed on site id) with station information.

    """
    # I haven't found a better list of stations, seems pretty janky
    # to just have them in a file, and not sure if/when it is updated.
    url = "http://cdec.water.ca.gov/misc/all_stations.csv"
    # the csv is malformed, so some rows think there are 7-8 fields
    return pd.read_csv(
        url,
        names=["id", "meta_url"],
        usecols=[0, 1],
        header=None,
        quotechar="'",
        index_col=0,
    )


def get_sensors(sensor_id=None):
    """
    Get a list of sensor ids as a DataFrame indexed on sensor number.

    Can be limited by a list of numbers.

    Parameters
    ----------
    sensor_id : iterable of integers or ``None``

    Returns
    -------
    df : pandas DataFrame
        a python dict with site codes mapped to site information
    """

    url = "http://cdec.water.ca.gov/misc/senslist.html"
    df = pd.read_html(url, header=0)[0]
    df.set_index("Sensor No")

    return df if sensor_id is None else df.loc[sensor_id]


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
        url = f"http://cdec.water.ca.gov/dynamicapp/staMeta?station_id={station_id}"

        try:
            sensor_list = pd.read_html(url, match="Sensor Description")[0]
        except ValueError:
            sensor_list = pd.read_html(url)[0]

        try:
            sensor_list.columns = ["sensor_id", "variable", "resolution", "timerange"]
        except ValueError:
            sensor_list.columns = [
                "variable",
                "sensor_id",
                "resolution",
                "varcode",
                "method",
                "timerange",
            ]

        v = list(sensor_list["variable"].to_dict().values())
        split = [i.split(",") for i in v]
        var_names = [" ".join([i.strip() for i in x][:-1]).strip() for x in split]
        var_names = [i.replace(" ", "_") for i in var_names]
        units = [x[-1][1:] for x in split]
        units = [unit_conv.get(i, i) for i in units]
        var_names = [":".join([i, j]) for i, j in zip(var_names, units)]
        var_resolution = [x[1:-1] for x in sensor_list["resolution"]]
        sensor_list["resolution"] = var_resolution
        sensor_list["variable"] = var_names
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
    if sensor_ids:
        sensor_ids = [
            sensor_num_map.get(str(i).lower(), i) for i in tsutils.make_list(sensor_ids)
        ]

    if start is None:
        start_date = pd.Timestamp(DEFAULT_START_DATE).date()
    else:
        start_date = pd.Timestamp(start).date()
    if end is None:
        end_date = (
            pd.to_datetime(datetime.datetime.utcnow())
            .tz_localize("UTC")
            .tz_convert("America/Los_Angeles")
        )
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
            sensor_id = row["sensor_id"]

            url = f"http://cdec.water.ca.gov/dynamicapp/req/CSVDataServlet?Stations={station_id}&dur_code={dur_code_map[res]}&SensorNums={sensor_id}&Start={start_date_str}&End={end_date_str}"
            if Path("debug_tsgettoolbox").exists():
                print(url)
            station_data[var] = pd.read_csv(
                url,
                parse_dates=["DATE TIME"],
                index_col="DATE TIME",
                na_values=["m", "---"],
            )["VALUE"]
            station_data[var].columns = ["datetime", "value"]

        d[station_id] = station_data

    return d


def _limit_sensor_list(sensor_list, sensor_ids, resolution):
    """Limit the sensor list to the provided sensor ids and resolutions."""
    if sensor_ids is not None:
        sensor_list = sensor_list[[x in sensor_ids for x in sensor_list.sensor_id]]

    if resolution is not None:
        ncode = [fname_code_map[i] for i in resolution]
        sensor_list = sensor_list[sensor_list["resolution"].isin(ncode)]
    if len(sensor_list) == 0:
        warnings.warn(
            f"There are no sensors in the list {sensor_ids} with any of the resolutions {resolution}."
        )
    return sensor_list


def download_data(
    station_id, sensor_nums=None, dur_code=None, start_date=None, end_date=None
):
    """Download data for a single CDEC station and sensor id."""
    if isinstance(sensor_nums, (str, bytes)):
        sensor_nums = [
            int(sensor_num_map.get(i.lower(), i)) for i in sensor_nums.split(".")
        ]
    elif isinstance(sensor_nums, int):
        sensor_nums = [sensor_nums]

    if isinstance(dur_code, (str, bytes)):
        dur_code = dur_code.split(",")

        dur_code = [dur_code_map.get(i.lower(), i) for i in dur_code]

    d = get_data(
        [station_id],
        sensor_ids=tsutils.make_list(sensor_nums),
        resolutions=tsutils.make_list(dur_code),
        start=start_date,
        end=end_date,
    )

    nd = pd.DataFrame()
    for key, value in d[station_id].items():
        nnd = pd.DataFrame(value)
        nnd.columns = [key]
        nd = nd.join(nnd, how="outer")
    nd.rename(
        lambda x: x.replace(",", "_")
        .replace(" ", "_")
        .replace("__", "_")
        .replace("DEG_F", "degF"),
        axis="columns",
        inplace=True,
    )
    nd = nd.tz_localize("Etc/GMT+8")

    nd = nd.astype("float64")
    nd = nd.convert_dtypes()

    nd.index.name = "Datetime:PST"
    return nd


@tsutils.doc(tsutils.docstrings)
def cdec(
    station_id: str,
    dur_code: Optional[Union[list, str]] = None,
    sensor_nums=None,
    start_date=None,
    end_date=None,
):
    """US/CA:station::E,H,D,M:California Department of Water Resources

    The primary function of the California Data Exchange Center (CDEC) is to
    facilitate the collection, storage, and exchange of hydrologic and climate
    information to support real-time flood management and water supply needs in
    California.

    California Department of Water Resources: http://www.water.ca.gov/
    California Data Exchange Center: http://cdec.water.ca.gov

    Downloads data for a set of CDEC station and sensor ids. If either is not
    provided, all available data will be downloaded.

    Parameters
    ----------
    station_id : str
        [optional, default is None]

        Each string is the CDEC station ID and consist of three capital
        letters.

    sensor_nums : int, str, list of int or str, or ``None``
        [optional, default is None]

        If ``None`` will get all sensors at `station_id`.

        SELECTED CDEC SENSOR NUMBERS (these are not available for all
        sites):

        +-------------+-------------------------------------------+
        | sensor_nums | Description                               |
        +=============+===========================================+
        | 1           | river stage [ft]                          |
        +-------------+-------------------------------------------+
        | 2           | precipitation accumulated [in]            |
        +-------------+-------------------------------------------+
        | 3           | SWE [in]                                  |
        +-------------+-------------------------------------------+
        | 4           | air temperature [F]                       |
        +-------------+-------------------------------------------+
        | 5           | EC [ms/cm]                                |
        +-------------+-------------------------------------------+
        | 6           | reservoir elevation [ft]                  |
        +-------------+-------------------------------------------+
        | 7           | reservoir scheduled release [cfs]         |
        +-------------+-------------------------------------------+
        | 8           | full natural flow [cfs]                   |
        +-------------+-------------------------------------------+
        | 15          | reservoir storage [af]                    |
        +-------------+-------------------------------------------+
        | 20          | flow -- river discharge [cfs]             |
        +-------------+-------------------------------------------+
        | 22          | reservoir storage change [af]             |
        +-------------+-------------------------------------------+
        | 23          | reservoir outflow [cfs]                   |
        +-------------+-------------------------------------------+
        | 24          | Evapotranspiration [in]                   |
        +-------------+-------------------------------------------+
        | 25          | water temperature [F]                     |
        +-------------+-------------------------------------------+
        | 27          | water turbidity [ntu]                     |
        +-------------+-------------------------------------------+
        | 28          | chlorophyll [ug/l]                        |
        +-------------+-------------------------------------------+
        | 41          | flow -- mean daily [cfs]                  |
        +-------------+-------------------------------------------+
        | 45          | precipitation incremental [in]            |
        +-------------+-------------------------------------------+
        | 46          | runoff volume [af]                        |
        +-------------+-------------------------------------------+
        | 61          | water dissolved oxygen [mg/l]             |
        +-------------+-------------------------------------------+
        | 62          | water pH value [pH]                       |
        +-------------+-------------------------------------------+
        | 64          | pan evaporation (incremental) [in]        |
        +-------------+-------------------------------------------+
        | 65          | full natural flow [af]                    |
        +-------------+-------------------------------------------+
        | 66          | flow -- monthly volume [af]               |
        +-------------+-------------------------------------------+
        | 67          | accretions (estimated) [af]               |
        +-------------+-------------------------------------------+
        | 71          | spillway discharge [cfs]                  |
        +-------------+-------------------------------------------+
        | 74          | lake evaporation (computed) [cfs]         |
        +-------------+-------------------------------------------+
        | 76          | reservoir inflow [cfs]                    |
        +-------------+-------------------------------------------+
        | 85          | control regulating discharge [cfs]        |
        +-------------+-------------------------------------------+
        | 94          | top conservation storage (reservoir) [af] |
        +-------------+-------------------------------------------+
        | 100         | water EC [us/cm]                          |
        +-------------+-------------------------------------------+

    dur_code : str, comma separated strings, or ``None``
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

    ${start_date}

    ${end_date}

    """
    return download_data(
        station_id,
        dur_code=dur_code,
        sensor_nums=sensor_nums,
        start_date=tsutils.parsedate(start_date),
        end_date=tsutils.parsedate(end_date),
    )


if __name__ == "__main__":
    r = cdec(
        "PAR",
        start_date="2017-01-01",
        end_date="2017-02-02",
        dur_code="daily",
        sensor_nums=45,
    )

    print("PAR PRECIPITATION")
    print(r)

    r = cdec(
        "PAR",
        start_date="2020-01-01",
        end_date="2020-10-02",
        dur_code="H",
        sensor_nums=6,
    )

    print("PAR RESERVOIR ELEVATION")
    print(r)

    r = cdec("PAR", start_date="2017-01-01", end_date="2017-10-02", dur_code="H")

    print("PAR HOURLY")
    print(r)

    r = cdec("PAR", start_date="2017-01-01", end_date="2017-10-02")

    print("PAR EVERYTHING")
    print(r)
