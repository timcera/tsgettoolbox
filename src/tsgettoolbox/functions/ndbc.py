"""
ndbc                US station T,6T,10T,15T,H,D:Download historical from
                    the National Data Buoy Center.
"""

import datetime
from contextlib import suppress
from gzip import GzipFile
from io import BytesIO, StringIO

import async_retriever as ar
import cltoolbox
import pandas as pd
from cltoolbox.rst_text_formatter import RSTHelpFormatter as HelpFormatter
from toolbox_utils import tsutils

__all__ = ["ndbc"]

_lmap = {
    "stdmet": "h",
    "cwind": "c",
    "wlevel": "l",
    "ocean": "o",
    "adcp": "a",
    "supl": "s",
    "srad": "r",
}

# 'wlevel' header is manipulated and not in self.headermap
_headermap = {
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
_rename = {
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
for value in _headermap.values():
    _rename.update(value)

_mapnumtoname = {
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


class BadGzipFile(OSError):
    """Exception raised in some cases for invalid gzip files."""


def date_parser(*x):
    """Parse a list of year strings into datetime objects."""
    x = [int(i) for i in x]
    if x[0] < 100:
        x[0] = x[0] + 1900
    return datetime.datetime(*x)


def ndbc_to_df(url, **query_params):
    """Read NDBC data into a pandas DataFrame."""
    sdate = tsutils.parsedate(query_params.pop("startUTC"))
    edate = tsutils.parsedate(query_params.pop("endUTC"))
    if edate is None:
        edate = pd.Timestamp.utcnow()

    table = query_params["table"]

    df = pd.DataFrame()

    cyear = datetime.datetime.now()
    filenames = []
    for yr in range(sdate.year, edate.year + 1):
        # Yearly
        # https://www.ndbc.noaa.gov/data/historical/stdmet/41012h2012.txt.gz
        filenames.append(
            f"{url}/historical/{table}/{query_params['station']}{_lmap[table]}{yr}.txt.gz"
        )
    if edate.year == cyear.year:
        filenames.extend(
            f"{url}/{table}/{_mapnumtoname[mnth]}/{query_params['station']}{mnth+1}{yr}.txt.gz"
            for mnth in range(edate.month)
        )

    resp = ar.retrieve_binary(filenames, [{}] * len(filenames))
    resp = [BytesIO(i) for i in resp]
    nresp = []
    for i in resp:
        with suppress(BadGzipFile):
            nresp.append(GzipFile(fileobj=i).read())

    skiprows = []
    parse_dates = []
    for r in nresp:
        f = StringIO(r.decode("utf-8"))
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

        if words1[4] == "mm":
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
            tdf.rename(columns=_rename, inplace=True)
            df = pd.concat([df, tdf])

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

    df = df.tz_localize("UTC")
    return df.loc[sdate:edate, :]


@cltoolbox.command("ndbc", formatter_class=HelpFormatter)
def ndbc_cli(station, table, startUTC, endUTC=None):
    r"""US station T,6T,10T,15T,H,D:Download historical from the National Data Buoy Center.

    Download historical data from the National Data Buoy Center.

    The Active Station List is available at
    http://www.ndbc.noaa.gov/activestations.xml

    When accessing Historical data files, the measurements are generally in
    metric units, as described below, and cannot be changed.

    Historical files show times in UTC only.

    Parameters
    ----------
    station : str
        Five-digit WMO Station Identifier, used since 1976. ID's can be
        reassigned to future deployments within the same 1 degree square.

    table : str
        The 'table' option is one of the
        following:

        +--------+--------------------------------+
        | table  | Description                    |
        +========+================================+
        | adcp   | Ocean Current data             |
        +--------+--------------------------------+
        | cwind  | Continuous Wind Data           |
        +--------+--------------------------------+
        | ocean  | Oceanographic Data             |
        +--------+--------------------------------+
        | srad   | Solar Radiation Data           |
        +--------+--------------------------------+
        | stdmet | Standard Meteorology Table     |
        +--------+--------------------------------+
        | supl   | Supplemental Measurements Data |
        +--------+--------------------------------+
        | wlevel | Water Level Data               |
        +--------+--------------------------------+

        'adcp' Ocean Current Data

        +-----------------+----------------------------------------------------+
        | Variable        | Description                                        |
        +=================+====================================================+
        | DEP01,DEP02,... | The distance from the sea surface to the middle of |
        |                 | the depth cells, or bins, measured in meters.      |
        +-----------------+----------------------------------------------------+
        | DIR01,DIR02,... | The direction the ocean current is flowing toward. |
        |                 | 0-360 degrees, 360 is due north, 0 means no        |
        |                 | measurable current.                                |
        +-----------------+----------------------------------------------------+
        | SPD01,SPD02,... | The speed of the ocean current measured in cm/s.   |
        +-----------------+----------------------------------------------------+

        'cwind' Continuous Winds

        +-------+--------------------------------------------------------------+
        | Code  | Description                                                  |
        +=======+==============================================================+
        | WDIR  | Ten-minute average wind direction measurements in degrees    |
        |       | clockwise from true North. (DIR in Historical files)         |
        +-------+--------------------------------------------------------------+
        | WSPD  | Ten-minute average wind speed values in m/s. (SPD in         |
        |       | Historical files)                                            |
        +-------+--------------------------------------------------------------+
        | GDR   | Direction, in degrees clockwise from true North, of the GST, |
        |       | reported at the last hourly 10-minute segment.               |
        +-------+--------------------------------------------------------------+
        | GST   | Maximum 5-second peak gust during the measurement hour,      |
        |       | reported at the last hourly 10-minute segment.               |
        +-------+--------------------------------------------------------------+
        | GTIME | The minute of the hour that the GSP occurred, reported at    |
        |       | the last hourly 10-minute segment.                           |
        +-------+--------------------------------------------------------------+

        'ocean' Oceanographic Data

        +-----------+----------------------------------------------------------+
        | Code      | Description                                              |
        +===========+==========================================================+
        | DEPTH     | Depth (meters) at which measurements are taken.          |
        +-----------+----------------------------------------------------------+
        | OTMP      | The direct measurement (Celsius) of the Ocean            |
        |           | Temperature (as opposed to the indirect measurement (see |
        |           | WTMP above)).                                            |
        +-----------+----------------------------------------------------------+
        | COND      | Conductivity is a measure of the electrical conductivity |
        |           | properties of seawater in milliSiemens per centimeter.   |
        +-----------+----------------------------------------------------------+
        | SAL       | Salinity is computed by a known functional relationship  |
        |           | between the measured electrical conductivity of seawater |
        |           | (CON), temperature (OTMP) and pressure. Salinity is      |
        |           | computed using the Practical Salinity Scale of 1978      |
        |           | (PSS78) and reported in Practical Salinity Units.        |
        +-----------+----------------------------------------------------------+
        | O2PERCENT | Dissolved oxygen as a percentage.                        |
        +-----------+----------------------------------------------------------+
        | O2PPM     | Dissolved oxygen in parts per million.                   |
        +-----------+----------------------------------------------------------+
        | CLCON     | Chlorophyll concentration in micrograms per liter        |
        |           | (ug/l).                                                  |
        +-----------+----------------------------------------------------------+
        | TURB      | Turbidity is an expression of the optical property that  |
        |           | causes light to be scattered and absorbed rather than    |
        |           | transmitted in straight lines through the sample (APHA   |
        |           | 1980). Units are Formazine Turbidity Units (FTU).        |
        +-----------+----------------------------------------------------------+
        | PH        | A measure of the acidity or alkalinity of the seawater.  |
        +-----------+----------------------------------------------------------+
        | EH        | Redox (oxidation and reduction) potential of seawater in |
        |           | millivolts.                                              |
        +-----------+----------------------------------------------------------+

        'srad' Shortwave Radiation

        +-------+--------------------------------------------------------------+
        | Code  | Description                                                  |
        +=======+==============================================================+
        | SRAD1 | Average shortwave radiation in watts per square meter for    |
        | SWRAD | the preceding hour. Sample frequency is 2 times per second   |
        |       | (2 Hz).  If present, SRAD1 is from a LI-COR LI-200           |
        |       | pyranometer sensor, and SWRAD is from an Eppley PSP          |
        |       | Precision Spectral Pyranometer.                              |
        +-------+--------------------------------------------------------------+
        | LWRAD | Average downwelling longwave radiation in watts per square   |
        |       | meter for the preceding hour. Sample frequency is 2 times    |
        |       | per second (2 Hz). If present, LWRAD is from an Eppley PIR   |
        |       | Precision Infrared Radiometer.                               |
        +-------+--------------------------------------------------------------+

        'stdmet' Standard Meteorology Table

        +------+---------------------------------------------------------------+
        | Code | Description                                                   |
        +======+===============================================================+
        | WDIR | Wind direction (the direction the wind is coming from in      |
        |      | degrees clockwise from true N) during the same period used    |
        |      | for WSPD. See Wind Averaging Methods                          |
        +------+---------------------------------------------------------------+
        | WSPD | Wind speed (m/s) averaged over an eight-minute period for     |
        |      | buoys and a two-minute period for land stations. Reported     |
        |      | Hourly. See Wind Averaging Methods.                           |
        +------+---------------------------------------------------------------+
        | GST  | Peak 5 or 8 second gust speed (m/s) measured during the       |
        |      | eight-minute or two-minute period. The 5 or 8 second period   |
        |      | can be determined by payload, See the Sensor Reporting,       |
        |      | Sampling, and Accuracy section.                               |
        +------+---------------------------------------------------------------+
        | WVHT | Significant wave height (meters) is calculated as the average |
        |      | of the highest one-third of all of the wave heights during    |
        |      | the 20-minute sampling period. See the Wave Measurements      |
        |      | section.                                                      |
        +------+---------------------------------------------------------------+
        | DPD  | Dominant wave period (seconds) is the period with the maximum |
        |      | wave energy. See the Wave Measurements section.               |
        +------+---------------------------------------------------------------+
        | APD  | Average wave period (seconds) of all waves during the         |
        |      | 20-minute period. See the Wave Measurements section.          |
        +------+---------------------------------------------------------------+
        | MWD  | The direction from which the waves at the dominant period     |
        |      | (DPD) are coming. The units are degrees from true North       |
        |      | increasing clockwise, with North as 0 (zero) degree East as   |
        |      | 90 degrees. See the Wave Measurements section.                |
        +------+---------------------------------------------------------------+
        | PRES | Sea level pressure (hPa). For C-MAN sites and Great Lakes     |
        |      | buoys, the recorded pressure is reduced to sea level using    |
        |      | the method described in NWS Technical Procedure Bulletin 291  |
        |      | (11/14/80).  ( labeled BAR in Historical files)               |
        +------+---------------------------------------------------------------+
        | ATMP | Air temperature (Celsius). For sensor heights on buoys, see   |
        |      | Hull Descriptions. For sensor heights at C-MAN stations, see  |
        |      | C-MAN Sensor Locations                                        |
        +------+---------------------------------------------------------------+
        | WTMP | Sea surface temperature (Celsius). For buoys the depth is     |
        |      | referenced to the hull's waterline. For fixed platforms it    |
        |      | varies with tide, but is referenced to, or near Mean Lower    |
        |      | Low Water (MLLW).                                             |
        +------+---------------------------------------------------------------+
        | DEWP | Dewpoint temperature taken at the same height as the air      |
        |      | temperature measurement.                                      |
        +------+---------------------------------------------------------------+
        | VIS  | Station visibility (nautical miles). Note that buoy stations  |
        |      | are limited to reports from 0 to 1.6 nmi.                     |
        +------+---------------------------------------------------------------+
        | PTDY | Pressure Tendency is the direction (plus or minus) and the    |
        |      | amount of pressure change (hPa)for a three hour period ending |
        |      | at the time of observation. (not in Historical files)         |
        +------+---------------------------------------------------------------+
        | TIDE | The water level in feet above or below Mean Lower Low Water   |
        |      | (MLLW).                                                       |
        +------+---------------------------------------------------------------+

        'supl' Supplemental Measurements Data

        +-------+--------------------------------------------------------------+
        | Code  | Description                                                  |
        +=======+==============================================================+
        | PRES  | Lowest recorded 1 minute atmospheric pressure for the hour   |
        |       | to the nearest 0.1 hPa.                                      |
        +-------+--------------------------------------------------------------+
        | PTIME | The time at which PRES occurred (hour and minute).           |
        +-------+--------------------------------------------------------------+
        | WSPD  | Highest recorded 1 minute wind speed for the hour to the     |
        |       | nearest 0.1 m/s.                                             |
        +-------+--------------------------------------------------------------+
        | WDIR  | WSPD corresponding direction to the nearest degree.          |
        +-------+--------------------------------------------------------------+
        | WTIME | The time at which WSPD occurred (hour and minute).           |
        +-------+--------------------------------------------------------------+

        'wlevel' Water Level

        +--------+-------------------------------------------------------------+
        | Code   | Description                                                 |
        +========+=============================================================+
        | WLEVEL | Six-minute water levels representing the height, in feet,   |
        |        | of the water above or below Mean Lower Low Water (MLLW),    |
        |        | offset by 10 ft. to prevent negative values. Please         |
        |        | subtract 10 ft. from every value to obtain the true water   |
        |        | level value, in reference to MLLW.                          |
        +--------+-------------------------------------------------------------+

    startUTC
        an ISO 8601 date/time string
        (only seconds are optional)

    endUTC
        [optional, default to None implies now]

        an ISO 8601 date/time string.
        (only seconds are optional)

    """
    tsutils.printiso(ndbc(station, table, startUTC, endUTC=endUTC))


@tsutils.copy_doc(ndbc_cli)
def ndbc(station, table, startUTC, endUTC=None):
    r"""Download historical from the National Data Buoy Center."""
    return ndbc_to_df(
        r"https://www.ndbc.noaa.gov/data/",
        table=table,
        station=station,
        startUTC=startUTC,
        endUTC=endUTC,
    )


if __name__ == "__main__":
    """ """

    df = ndbc_to_df(
        r"https://www.ndbc.noaa.gov/data/",
        table="stdmet",
        startUTC="2020-01-01T00:00Z",
        endUTC="2020-05-01T00:00Z",
        station="pfdc1",
    )

    print("NDBC")
    print(df)
    df.to_csv("file.csv")
