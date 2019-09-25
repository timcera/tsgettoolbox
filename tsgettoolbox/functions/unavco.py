from tsgettoolbox.odo import odo, resource
import pandas as pd
import mando

try:
    from mando.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter

from tstoolbox import tsutils


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
    from tsgettoolbox.services import unavco as placeholder

    map_db_to_url = {
        "met": r"http://web-services.unavco.org:80/met/data",
        "pore_temperaure": r"http://web-services.unavco.org:80"
        "/pore/data/temperature",
        "pore_pressure": r"http://web-services.unavco.org:80" "/pore/data/pressure",
        "tilt": r"http://web-services.unavco.org:80/tilt/data",
        "strain": r"http://web-services.unavco.org:80/strain/data/L2",
    }
    r = resource(
        map_db_to_url[database], station=station, starttime=starttime, endtime=endtime
    )
    return odo(r, pd.DataFrame)


unavco.__doc__ = unavco_cli.__doc__
