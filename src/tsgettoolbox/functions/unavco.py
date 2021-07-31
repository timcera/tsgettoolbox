# -*- coding: utf-8 -*-
import logging
import os
from io import BytesIO

import mando
import pandas as pd
import requests

try:
    from mando.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter

from tstoolbox import tsutils


def unavco_to_df(url, **query_params):
    try:
        station = query_params.pop("station")
    except KeyError:
        raise KeyError(
            """
*
*   The station keyword is required.  You have given me
*   {}.
*
""".format(
                query_params
            )
        )
    url = "{}/{}/beta".format(url, station)
    if "/met/" in url or "/strain/" in url:
        comment = None
    else:
        comment = "#"
    query_params["starttime"] = tsutils.parsedate(query_params["starttime"]).isoformat()
    query_params["endtime"] = tsutils.parsedate(query_params["endtime"]).isoformat()
    query_params["tsFormat"] = "iso8601"

    req = requests.get(url, params=query_params)
    if os.path.exists("debug_tsgettoolbox"):
        logging.warning(req.url)
    df = pd.read_csv(
        BytesIO(req.content),
        header=0,
        index_col=0,
        parse_dates=[0],
        comment=comment,
        skiprows=5,
    )
    df.columns = [
        "unavco-{}".format(
            i.strip()
            .replace(" ", "_")
            .replace("(", ":")
            .replace(")", "")
            .replace("deg._C", "degC")
        )
        for i in df.columns
    ]
    df.index.name = "Datetime:UTC"
    return df


@mando.command("unavco", formatter_class=HelpFormatter, doctype="numpy")
def unavco_cli(station, database="met", starttime=None, endtime=None):
    r"""Download data from the Unavco web services.

    Detailed information at:
    http://www.unavco.com/data/web-services/web-services.html

    The "database" option defines different return data.

    met::

       Returns hourly meteorological data for the specified station and
       timeframe.  Pressure, temperature, humidity, wind speed and
       direction are provided as averages of all the samples taken per
       hour. Rain and hail are totals for the hour. The sample count is
       the number of samples taken per hour.

       Stations are configured to sample either at 1 minute or 5 minute
       intervals and the user can determine which by looking at the
       sample counts over several hours to see if they approach 12 or
       60.

       Returns: sample timestamp, pressure (mbar), temperature (degree
       C), relative humidity(per cent), wind direction(degrees), wind
       speed(m/s), rain(0.1mm), hail(hits), sample count

    pore_temperature::

       Pore pressure and temperature readings are collected by pore
       pressure sensors co-located with borehole strainmeters. Tilt data
       is collected by shallow borehole tiltmeters co-located with
       borehole strainmeters and seismic stations.

       Get pore temperature for the specified stations and time range.

       Returns: sample time, temperature(degree C)

    pore_pressure::

       Pore pressure and temperature readings are collected by pore
       pressure sensors co-located with borehole strainmeters. Tilt data
       is collected by shallow borehole tiltmeters co-located with
       borehole strainmeters and seismic stations.

       Get pore pressure for the specified stations and time range.

       Returns: sample time, pressure (hPa)

    tilt::

       Get tilt data for specified stations and time range.

       Returns: DateTime, X-axis tilt (microRadians), Y-axis tilt
       (microRadians), Temperature (degree C), Voltage(v)

    strain::

       Geodetic strain data is collected by four-component deep borehole
       tensor strainmeters that record transient deformation signals
       yielding information about the physical properties of the
       surrounding rock.

       Borehole strainmeters measure very small changes in the dimension
       of a borehole at depths ranging from 100m to 250m. The Plate
       Boundary Observatory uses a instrument developed and constructed
       by GTSM Technologies which measure the change in borehole
       diameter along three azimuths separated by 120 degrees
       perpendicular to the borehole.

       Get borehole strain data for the borehole strainmeter station
       identified.  This data is low rate, 5 minute sample, level
       2 uncorrected and corrected strain data. Corrected values are the
       uncorrected strain minus the effects of the tidal signal and
       barometric pressure.

       Returns: DateTime, Gauge 0 uncorrected microstrain, Gauge
       1 corrected microstrain, Gauge 1 uncorrected microstrain, Gauge
       1 corrected microstrain, Gauge 2 microstrain, Gauge 2 corrected
       microstrain, Gauge 3 microstrain, Gauge 3 corrected microstrain,
       Eee+Enn uncorrected microstrain, Eee+Enn corrected microstrain,
       Eee-Enn uncorrected microstrain, Eee-Enn corrected microstrain,
       2Ene uncorrected microstrain, 2Ene corrected microstrain.

    Parameters
    ----------
    station
        Unavco station identifier
    database : str
        Database to pull from.  One of 'met', 'pore_temperature',
        'pore_pressure', 'tilt', 'strain'.  The default is 'met'.
    starttime
        Start date in ISO8601 format.
    endtime
        End date in ISO8601 format.
    """
    tsutils._printiso(
        unavco(station, database=database, starttime=starttime, endtime=endtime)
    )


def unavco(station, database="met", starttime=None, endtime=None):
    r"""Download data from the Unavco web services."""
    map_db_to_url = {
        "met": r"http://web-services.unavco.org:80/met/data",
        "pore_temperaure": r"http://web-services.unavco.org:80"
        "/pore/data/temperature",
        "pore_pressure": r"http://web-services.unavco.org:80" "/pore/data/pressure",
        "tilt": r"http://web-services.unavco.org:80/tilt/data",
        "strain": r"http://web-services.unavco.org:80/strain/data/L2",
    }
    df = unavco_to_df(
        map_db_to_url[database], station=station, starttime=starttime, endtime=endtime
    )
    return df


unavco.__doc__ = unavco_cli.__doc__


if __name__ == "__main__":
    df = unavco_to_df(
        r"http://web-services.unavco.org:80/met/data",
        station="P005",
        starttime="2012-05-01T00:00:00",
        endtime="2012-05-02T23:59:59",
    )

    print("Unavco_met")
    print(df)

    df = unavco_to_df(
        r"http://web-services.unavco.org:80/pore/data/temperature",
        station="B078",
        starttime="2012-05-02T00:00:00",
        endtime="2012-05-02T23:59:59",
    )

    print("Unavco_pore_temperature")
    print(df)

    df = unavco_to_df(
        r"http://web-services.unavco.org:80/pore/data/pressure",
        station="B078",
        starttime="2012-05-02T00:00:00",
        endtime="2012-05-02T23:59:59",
    )

    print("Unavco_pore_pressure")
    print(df)

    df = unavco_to_df(
        r"http://web-services.unavco.org:80/tilt/data",
        station="P693",
        starttime="2012-05-01T00:00:00",
        endtime="2012-05-01T01:00:00",
    )

    print("Unavco_tilt")
    print(df)

    df = unavco_to_df(
        r"http://web-services.unavco.org:80/strain/data/L2",
        station="B007",
        starttime="2012-05-01T00:00:00",
        endtime="2012-05-01T23:59:59",
    )

    print("Unavco_strain")
    print(df)
