# -*- coding: utf-8 -*-
import datetime
import logging
import os
from gzip import GzipFile
from io import BytesIO, StringIO

import mando
import pandas as pd

try:
    from mando.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter

from tstoolbox import tsutils

from tsgettoolbox import utils

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
for item in _headermap:
    _rename.update(_headermap[item])


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


def date_parser(*x):
    x = [int(i) for i in x]
    if x[0] < 100:
        x[0] = x[0] + 1900
    return datetime.datetime(*x)


def ndbc_to_df(url, **query_params):

    sdate = tsutils.parsedate(query_params.pop("startUTC"))
    edate = tsutils.parsedate(query_params.pop("endUTC"))

    table = query_params["table"]

    df = pd.DataFrame()

    cyear = datetime.datetime.now()
    filenames = []
    for yr in range(sdate.year, edate.year + 1):
        # Yearly
        # https://www.ndbc.noaa.gov/data/historical/stdmet/41012h2012.txt.gz
        filenames.append(
            "/historical/{3}/{0}{1}{2}.txt.gz".format(
                query_params["station"], _lmap[table], yr, table
            )
        )
    if edate.year == cyear.year:
        for mnth in range(edate.month):
            # Monthly
            # https://www.ndbc.noaa.gov/data/stdmet/Mar/sauf132018.txt.gz
            filenames.append(
                "/{3}/{4}/{0}{1}{2}.txt.gz".format(
                    query_params["station"],
                    mnth + 1,
                    yr,
                    table,
                    _mapnumtoname[mnth],
                )
            )

    for filename in filenames:
        session = utils.requests_retry_session()
        req = session.get(url + filename)

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

    df = df.tz_localize("UTC")
    return df.loc[sdate:edate, :]


@mando.command("ndbc", formatter_class=HelpFormatter, doctype="numpy")
def ndbc_cli(station, table, startUTC, endUTC):
    r"""station: Download historical from the National Data Buoy Center.

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
        +--------+--------------------------------+
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

        +-----------------+--------------------------------------------------+
        | Variable        | Description                                      |
        +-----------------+--------------------------------------------------+
        | DEP01,DEP02,... | The distance from the sea surface to the middle  |
        |                 | of the depth cells, or bins, measured in meters. |
        +-----------------+--------------------------------------------------+
        | DIR01,DIR02,... | The direction the ocean current is flowing       |
        |                 | toward. 0-360 degrees, 360 is due north, 0 means |
        |                 | no measurable current.                           |
        +-----------------+--------------------------------------------------+
        | SPD01,SPD02,... | The speed of the ocean current measured in cm/s. |
        +-----------------+--------------------------------------------------+

        'cwind' Continuous Winds

        +----------+---------------------------------------------------------+
        | Variable | Description                                             |
        +----------+---------------------------------------------------------+
        | WDIR     | Ten-minute average wind direction measurements in       |
        |          | degrees clockwise from true North. (DIR in Historical   |
        |          | files)                                                  |
        +----------+---------------------------------------------------------+
        | WSPD     | Ten-minute average wind speed values in m/s. (SPD in    |
        |          | Historical files)                                       |
        +----------+---------------------------------------------------------+
        | GDR      | Direction, in degrees clockwise from true North, of the |
        |          | GST, reported at the last hourly 10-minute segment.     |
        +----------+---------------------------------------------------------+
        | GST      | Maximum 5-second peak gust during the measurement hour, |
        |          | reported at the last hourly 10-minute segment.          |
        +----------+---------------------------------------------------------+
        | GTIME    | The minute of the hour that the GSP occurred, reported  |
        |          | at the last hourly 10-minute segment.                   |
        +----------+---------------------------------------------------------+

        'ocean' Oceanographic Data

        +-----------+----------------------------------------------------------+
        | Variable  | Description                                              |
        +-----------+----------------------------------------------------------+
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

        +--------------+-------------------------------------------------+
        | Variable     | Description                                     |
        +--------------+-------------------------------------------------+
        | SRAD1, SWRAD | Average shortwave radiation in watts per square |
        |              | meter for the preceding hour. Sample frequency  |
        |              | is 2 times per second (2 Hz).  If present,      |
        |              | SRAD1 is from a LI-COR LI-200 pyranometer       |
        |              | sensor, and SWRAD is from an Eppley             |
        |              | PSP Precision Spectral Pyranometer.             |
        +--------------+-------------------------------------------------+
        | LWRAD        | Average downwelling longwave radiation in watts |
        |              | per square meter for the preceding hour. Sample |
        |              | frequency is 2 times per second (2 Hz). If      |
        |              | present, LWRAD is from an Eppley PIR Precision  |
        |              | Infrared Radiometer.                            |
        +--------------+-------------------------------------------------+

        'stdmet' Standard Meteorology Table

        +----------+----------------------------------------------------------+
        | Variable | Description                                              |
        +----------+----------------------------------------------------------+
        | WDIR     | Wind direction (the direction the wind is coming from in |
        |          | degrees clockwise from true N) during the same period    |
        |          | used for WSPD. See Wind Averaging Methods                |
        +----------+----------------------------------------------------------+
        | WSPD     | Wind speed (m/s) averaged over an eight-minute period    |
        |          | for buoys and a two-minute period for land stations.     |
        |          | Reported Hourly. See Wind Averaging Methods.             |
        +----------+----------------------------------------------------------+
        | GST      | Peak 5 or 8 second gust speed (m/s) measured during the  |
        |          | eight-minute or two-minute period. The 5 or 8 second     |
        |          | period can be determined by payload, See the Sensor      |
        |          | Reporting, Sampling, and Accuracy section.               |
        +----------+----------------------------------------------------------+
        | WVHT     | Significant wave height (meters) is calculated as the    |
        |          | average of the highest one-third of all of the wave      |
        |          | heights during the 20-minute sampling period. See the    |
        |          | Wave Measurements section.                               |
        +----------+----------------------------------------------------------+
        | DPD      | Dominant wave period (seconds) is the period with the    |
        |          | maximum wave energy. See the Wave Measurements section.  |
        +----------+----------------------------------------------------------+
        | APD      | Average wave period (seconds) of all waves during the    |
        |          | 20-minute period. See the Wave Measurements section.     |
        +----------+----------------------------------------------------------+
        | MWD      | The direction from which the waves at the dominant       |
        |          | period (DPD) are coming. The units are degrees from      |
        |          | true North increasing clockwise, with North as 0 (zero)  |
        |          | degree East as 90 degrees. See the Wave Measurements     |
        |          | section.                                                 |
        +----------+----------------------------------------------------------+
        | PRES     | Sea level pressure (hPa). For C-MAN sites and Great      |
        |          | Lakes buoys, the recorded pressure is reduced to sea     |
        |          | level using the method described in NWS Technical        |
        |          | Procedure Bulletin 291 (11/14/80).  ( labeled BAR in     |
        |          | Historical files)                                        |
        +----------+----------------------------------------------------------+
        | ATMP     | Air temperature (Celsius). For sensor heights on buoys,  |
        |          | see Hull Descriptions. For sensor heights at C-MAN       |
        |          | stations, see C-MAN Sensor Locations                     |
        +----------+----------------------------------------------------------+
        | WTMP     | Sea surface temperature (Celsius). For buoys the depth   |
        |          | is referenced to the hull's waterline. For fixed         |
        |          | platforms it varies with tide, but is referenced to, or  |
        |          | near Mean Lower Low Water (MLLW).                        |
        +----------+----------------------------------------------------------+
        | DEWP     | Dewpoint temperature taken at the same height as the air |
        |          | temperature measurement.                                 |
        +----------+----------------------------------------------------------+
        | VIS      | Station visibility (nautical miles). Note that buoy      |
        |          | stations are limited to reports from 0 to 1.6 nmi.       |
        +----------+----------------------------------------------------------+
        | PTDY     | Pressure Tendency is the direction (plus or minus) and   |
        |          | the amount of pressure change (hPa)for a three hour      |
        |          | period ending at the time of observation. (not in        |
        |          | Historical files)                                        |
        +----------+----------------------------------------------------------+
        | TIDE     | The water level in feet above or below Mean Lower Low    |
        |          | Water (MLLW).                                            |
        +----------+----------------------------------------------------------+

        'supl' Supplemental Measurements Data

        +----------+----------------------------------------------------------+
        | Variable | Description                                              |
        +----------+----------------------------------------------------------+
        | PRES     | Lowest recorded 1 minute atmospheric pressure for the    |
        |          | hour to the nearest 0.1 hPa.                             |
        +----------+----------------------------------------------------------+
        | PTIME    | The time at which PRES occurred (hour and minute).       |
        +----------+----------------------------------------------------------+
        | WSPD     | Highest recorded 1 minute wind speed for the hour to the |
        |          | nearest 0.1 m/s.                                         |
        +----------+----------------------------------------------------------+
        | WDIR     | WSPD corresponding direction to the nearest degree.      |
        +----------+----------------------------------------------------------+
        | WTIME    | The time at which WSPD occurred (hour and minute).       |
        +----------+----------------------------------------------------------+

        'wlevel' Water Level

        +----------+-----------------------------------------------+
        | Variable | Description                                   |
        +----------+-----------------------------------------------+
        | WLEVEL   | Six-minute water levels representing the      |
        |          | height, in feet, of the water above or below  |
        |          | Mean Lower Low Water (MLLW), offset by 10 ft. |
        |          | to prevent negative values. Please subtract   |
        |          | 10 ft. from every value to obtain the true    |
        |          | water level value, in reference to MLLW.      |
        +----------+-----------------------------------------------+

    startUTC
        an ISO 8601 date/time string
        (only seconds are optional)

    endUTC
        an ISO 8601 date/time string.
        (only seconds are optional)

    """
    extra_docstring = """
        Derived Met Values

        +----------+----------------------------------------------------------+
        | Variable | Description                                              |
        +----------+----------------------------------------------------------+
        | HEAT     | For more information on heat index, please see the NWS   |
        |          | Heat Wave page.                                          |
        +----------+----------------------------------------------------------+
        | CHILL    | Please note that NDBC uses unadjusted winds to calculate |
        |          | wind chill. The winds are calculated at anemometer       |
        |          | height. For more information on wind chill, please see   |
        |          | the NWS Wind Chill Temperature Index.                    |
        +----------+----------------------------------------------------------+
        | ICE      | Estimated ice accretion in inches per hour based on an   |
        |          | algorithm developed by Overland and Pease at the Pacific |
        |          | Marine Environmental Laboratory in the mid-1980s. The    |
        |          | algorithm relates icing to the presently observed wind   |
        |          | speed, air temperature, and sea surface temperature. The |
        |          | method is designed for trawlers in the 20 to 75 meter    |
        |          | length range, underway at normal speeds in open seas and |
        |          | not heading downwind. In general, NWS forecasters        |
        |          | translate ice accretion rates to the following           |
        |          | categories:                                              |
        +----------+----------------------------------------------------------+
        |          | light: 0.0 to 0.24 inches of ice accretion/hour;         |
        +----------+----------------------------------------------------------+
        |          | moderate: 0.25 to 0.8 inches/hour; and                   |
        +----------+----------------------------------------------------------+
        |          | heavy: greater than 0.8 inches/hour.                     |
        +----------+----------------------------------------------------------+
        | WSPD10   | The estimation of Wind Speed (WSPD) measurement raised   |
        |          | or lowered to a height of 10 meters. NDBC uses the       |
        |          | method of Liu et al., 1979: Bulk parameterization of     |
        |          | air-sea exchanges in heat and water vapor including      |
        |          | molecular constraints at the interface, Journal of       |
        |          | Atmospheric Science, 36, pp. 1722-1735.                  |
        +----------+----------------------------------------------------------+
        | WSPD20   | The estimation of Wind Speed (WSPD) measurement raised   |
        |          | or lowered to a height of 20 meters. NDBC uses the       |
        |          | method of Liu et al., 1979: Bulk parameterization of     |
        |          | air-sea exchanges in heat and water vapor including      |
        |          | molecular constraints at the interface, Journal of       |
        |          | Atmospheric Science, 36, pp. 1722-1735.                  |
        +----------+----------------------------------------------------------+


        Spectral Wave Data

        The header line contains the frequency bins in Hz.

        +-----------+----------------------------------------------------+
        | Variable  | Description                                        |
        +-----------+----------------------------------------------------+
        | frequency | Energy in (meter*meter)/Hz, for each frequency bin |
        | bin       | (typically from 0.03 Hz to 0.40 Hz).               |
        +-----------+----------------------------------------------------+

        #YY  MM DD hh mm alpha1_1 (freq_1) alpha1_2 (freq_2) alpha1_3 (freq_3) ... >
        2014 09 11 17 00 999.0 (0.033) 999.0 (0.038) 999.0 (0.043) ...>
        #YY  MM DD hh mm alpha2_1 (freq_1) alpha2_2 (freq_2) alpha2_3 (freq_3) ... >
        2014 09 11 17 00 999.0 (0.033) 999.0 (0.038) 999.0 (0.043) ...
        #YY  MM DD hh mm r1_1 (freq_1) r1_2 (freq_2) r1_3 (freq_3) ... >
        2014 09 11 17 00 999.00 (0.033) 999.00 (0.038) 999.00 (0.043) ...>
        #YY  MM DD hh mm r2_1 (freq_1) r2_2 (freq_2) r2_3 (freq_3) ... >
        2014 09 11 17 00 999.00 (0.033) 999.00 (0.038) 999.00 (0.043) ...>

        Spectral wave direction | Mean wave direction, in degrees from true
        North, for each frequency bin. A list of directional stations is
        available.

        Directional Wave Spectrum | = C11(f) * D(f,A), f=frequency (Hz),
        A=Azimuth angle measured clockwise from true North to the direction
        wave is from.

        D(f,A) = (1/PI)*(0.5+R1*COS(A-ALPHA1)+R2*COS(2*(A-ALPHA2))). R1 and R2
        are the first and second normalized polar coordinates of the Fourier
        coefficients and are nondimensional. ALPHA1 and ALPHA2 are respectively
        mean and principal wave directions.

        In terms of Longuet-Higgins Fourier Coefficients
        R1 = (SQRT(a1*a1+b1*b1))/a0
        R2 = (SQRT(a2*a2+b2*b2))/a0
        ALPHA1 = 270.0-ARCTAN(b1,a1)
        ALPHA2 = 270.0-(0.5*ARCTAN(b2,a2)+{0. or 180.})

        Notes

        The R1 and R2 values in the monthly and yearly historical data files
        are scaled by 100, a carryover from how the data are transported to the
        archive centers. The units are hundredths, so the R1 and R2 values in
        those files should be multiplied by 0.01.

        D(f,A) can take on negative values because of the trigonometric sine
        and cosine functions. There are several approaches to prevent or deal
        with the negative values. For more information and discussion of some
        approaches see: Use of advanced directional wave spectra analysis
        methods, M. D. Earle, K. E. Steele, and D. W. C. Wang, Ocean
        Engineering, Volume 26, Issue 12, December 1999, Pages 1421-1434.

        ALPHA2 has ambiguous results in using the arctangent function with the
        Fourier Coefficients,b 2 ,a 2 . When necessary, NDBC adds 180 degrees
        to ALPHA2 in order to minimize the difference between ALPHA 1 and
        ALPHA2.


        Ocean Current Data (Expanded ADCP format)

        +--------------+----------------------------------------------------+
        | Variable     | Description                                        |
        +--------------+----------------------------------------------------+
        | I            | Instrument Number: Stations may have more than one |
        |              | ADCP instrument. This field distinguishes these    |
        |              | instruments by number.  Valid values are 0-9, with |
        |              | 0 being reserved for surface measurements.         |
        +--------------+----------------------------------------------------+
        | Bin          | The bin number, ranging from 1 to 128, where 1 is  |
        |              | the bin closest to the transducer head.            |
        +--------------+----------------------------------------------------+
        | Depth        | The distance from the sea surface to the middle of |
        |              | the depth cells, or bins, measured in meters.      |
        +--------------+----------------------------------------------------+
        | Dir          | The direction the ocean current is flowing toward. |
        |              | 0-360 degrees, 360 is due north, 0 means no        |
        |              | measurable current.                                |
        +--------------+----------------------------------------------------+
        | Speed        | The speed of the ocean current measured in cm/s.   |
        +--------------+----------------------------------------------------+
        | ErrVl        | The error velocity measured in cm/s.               |
        +--------------+----------------------------------------------------+
        | VerVl        | The vertical velocity of the ocean current         |
        |              | measured in cm/s.                                  |
        +--------------+----------------------------------------------------+
        | PERCENTGood3 | The percentage of three-beam solutions that are    |
        |              | good.                                              |
        +--------------+----------------------------------------------------+
        | PERCENTGood4 | The percentage of four-beam solutions that are     |
        |              | good.                                              |
        +--------------+----------------------------------------------------+
        | PERCENTGoodE | The percentage of transformations rejected.        |
        +--------------+----------------------------------------------------+
        | EI1          | The echo intensity values for the beam 1. Valid    |
        |              | values are 0 to 255.                               |
        +--------------+----------------------------------------------------+
        | EI2          | The echo intensity values for the beam 2. Valid    |
        |              | values are 0 to 255.                               |
        +--------------+----------------------------------------------------+
        | EI3          | The echo intensity values for the beam 3. Valid    |
        |              | values are 0 to 255.                               |
        +--------------+----------------------------------------------------+
        | EI4          | The echo intensity values for the beam 4. Valid    |
        |              | values are 0 to 255.                               |
        +--------------+----------------------------------------------------+
        | CM1          | The correlation magnitude values for the beam 1.   |
        |              | Valid values are 0 to 255.                         |
        +--------------+----------------------------------------------------+
        | CM2          | The correlation magnitude values for the beam 2.   |
        |              | Valid values are 0 to 255.                         |
        +--------------+----------------------------------------------------+
        | CM3          | The correlation magnitude values for the beam 3.   |
        |              | Valid values are 0 to 255.                         |
        +--------------+----------------------------------------------------+
        | CM4          | The correlation magnitude values for the beam 4.   |
        |              | Valid values are 0 to 255.                         |
        +--------------+----------------------------------------------------+
        | Flags        | The nine quality flags represent the results of    |
        |              | the following quality tests based on their         |
        |              | position in the flags field.                       |
        +--------------+----------------------------------------------------+
        |              | Flag 1: overall bin status.                        |
        +--------------+----------------------------------------------------+
        |              | Flag 2: ADCP Built-In Test (BIT) status.           |
        +--------------+----------------------------------------------------+
        |              | Flag 3: Error Velocity test status.                |
        +--------------+----------------------------------------------------+
        |              | Flag 4: Percent Good test status.                  |
        +--------------+----------------------------------------------------+
        |              | Flag 5: Correlation Magnitude test status.         |
        +--------------+----------------------------------------------------+
        |              | Flag 6: Vertical Velocity test status.             |
        +--------------+----------------------------------------------------+
        |              | Flag 7: North Horizontal Velocity test status.     |
        +--------------+----------------------------------------------------+
        |              | Flag 8: East Horizontal Velocity test status.      |
        +--------------+----------------------------------------------------+
        |              | Flag 9: Echo Intensity test status.                |
        +--------------+----------------------------------------------------+
        |              | Valid values are:                                  |
        +--------------+----------------------------------------------------+
        |              | 0 = quality not evaluated;                         |
        +--------------+----------------------------------------------------+
        |              | 1 = failed quality test;                           |
        +--------------+----------------------------------------------------+
        |              | 2 = questionable or suspect data;                  |
        +--------------+----------------------------------------------------+
        |              | 3 = good data/passed quality test; and             |
        +--------------+----------------------------------------------------+
        |              | 9 = missing                                   |
        +--------------+----------------------------------------------------+

        Marsh-McBirney Current Measurements

        +----------+-------------------------------------------------------+
        | Variable | Description                                           |
        +----------+-------------------------------------------------------+
        | DIR      | Direction the current is flowing TOWARDS, measured in |
        |          | degrees clockwise from North.                         |
        +----------+-------------------------------------------------------+
        | SPD      | Current speed in cm/s.                                |
        +----------+-------------------------------------------------------+

        DART (Tsunameters) Measurements

        +----------+-----------------------------------+
        | Variable | Description                       |
        +----------+-----------------------------------+
        | T        | Measurement Type:                 |
        +----------+-----------------------------------+
        |          | 1 = 15-minute measurement;        |
        +----------+-----------------------------------+
        |          | 2 = 1-minute measurement; and     |
        +----------+-----------------------------------+
        |          | 3 = 15-second measurement.        |
        +----------+-----------------------------------+
        | HEIGHT   | Height of water column in meters. |
        +----------+-----------------------------------+

        24-Hour Rain Measurements

        +----------+-----------------------------------------------------+
        | Variable | Description                                         |
        +----------+-----------------------------------------------------+
        | RATE     | Average precipitation rate in units of millimeters  |
        |          | per hour over 24-hour period from 00:00 to 23:59.99 |
        |          | GMT.                                                |
        +----------+-----------------------------------------------------+
        | PCT      | Percentage of 144 ten-minute periods within a 24    |
        |          | hour period with a measurable accumulation of       |
        |          | precipitation.                                      |
        +----------+-----------------------------------------------------+
        | SDev     | ---                                                 |
        +----------+-----------------------------------------------------+
        | Flag     | In the case of 24-hour rainfall measurements,       |
        |          | a flag is assigned when over half of the 10-minute  |
        |          | measurements from which it is derived are flagged.  |
        +----------+-----------------------------------------------------+

        Hourly Rain Measurements

        +----------+----------------------------------------------------+
        | Variable | Description                                        |
        +----------+----------------------------------------------------+
        | ACCUM    | Total accumulation of precipitation in units of    |
        |          | millimeters on station during the 60-minute period |
        |          | from minute 0 to minute 59:59.99 of the hour.      |
        +----------+----------------------------------------------------+
        | Flag     | In the case of one-hour accumulation, a flag is    |
        |          | assigned when over half of the 10-minute           |
        |          | measurements from which it is derived have been    |
        |          | flagged.                                           |
        +----------+----------------------------------------------------+

        10-Minute Rain Measurements

        +----------+----------------------------------------------------+
        | Variable | Description                                        |
        +----------+----------------------------------------------------+
        | RATE     | Rain rate in units of millimeters per hour on      |
        |          | station over the 10-minute period from 5 minutes   |
        |          | before to 4 minutes 59.99 seconds after the time   |
        |          | with which it is associated.                       |
        +----------+----------------------------------------------------+
        | Flag     | In the case of 10-minute rainfall measurements,    |
        |          | a flag is assigned to any measurement when either  |
        |          | the -5 or +5 minute rain measurement from which it |
        |          | is derived is missing or obviously an error.       |
        +----------+----------------------------------------------------+

        Housekeeping Measurements

        +----------+------------------------------------------------------+
        | Variable | Description                                          |
        +----------+------------------------------------------------------+
        | BATTV    | Hourly Average Battery Voltage (volts)               |
        | BATTCURR | Hourly Average Battery Current (amperes)             |
        | BATTTEMP | Hourly Average Battery Temperature (degrees Celsius) |
        | REMCAP   | Remaining Battery Capacity (ampere-hours)            |
        +----------+------------------------------------------------------+
        """
    tsutils._printiso(ndbc(station, table, startUTC, endUTC))


def ndbc(station, table, startUTC, endUTC):
    r"""Download historical from the National Data Buoy Center."""
    df = ndbc_to_df(
        r"https://www.ndbc.noaa.gov/data/",
        table=table,
        station=station,
        startUTC=startUTC,
        endUTC=endUTC,
    )

    return df


ndbc.__doc__ = ndbc_cli.__doc__


if __name__ == "__main__":
    """ """

    df = ndbc_to_df(
        r"https://www.ndbc.noaa.gov/data/",
        table="stdmet",
        startUTC="2012-01-01T00:00Z",
        endUTC="2012-04-01T00:00Z",
        station="41012",
    )

    print("NDBC")
    print(df)
    df.to_csv("file.csv")
