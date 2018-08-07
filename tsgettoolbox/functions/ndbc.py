
from odo import odo, resource
import pandas as pd
import mando

try:
    from mando.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter

from tstoolbox import tsutils


@mando.command(formatter_class=HelpFormatter, doctype='numpy')
def ndbc(station,
         observedproperty,
         startUTC,
         endUTC):
    r"""Download from the National Data Buoy Center.

    Download data from the National Data Buoy Center.

    The Active Station List is available at
    http://www.ndbc.noaa.gov/activestations.xml

    This file provides metadata in regards to the current deployment for all
    active stations on the NDBC web site. The metadata includes station ID,
    latitude, longitude, station name, station owner, program to which the
    station belongs, and type of data reported as detailed below::

        met: indicates whether the station has reported meteorological
        data in the past eight hours (y/n).

        currents: indicates whether the station has reported water
        current data in the past eight hours (y/n).

        waterquality: indicates whether the station has reported ocean
        chemistry data in the past eight hours (y/n).

        dart: indicates whether the station has reported water column
        height/tsunami data in the past 24 hours (y/n).

    This file is refreshed every five minutes as needed. Note: The main
    activity that drives changes are: a service visit, establishment of
    a new station, or changes in the type of data received (i.e.
    sensor/station failure) therefore, minimal updates would be expected
    in a 24 hour period.

    Note, the TAO entries do not include the data type attributes (met,
    currents, water quality and dart) but do include a seq attribute for
    syncing access to the TAO web site. The TAO array is the climate
    stations in the equatorial Pacific.

    Parameters
    ----------
    station : str
        A station ID, or a currents
        id.

    observedproperty : str
        The 'observedpropery' is one of the
        following::

            air_pressure_at_sea_level
            air_temperature
            currents
            sea_floor_depth_below_sea_surface
                (water level for tsunami stations)
            sea_water_electrical_conductivity
            sea_water_salinity
            sea_water_temperature
            waves
            winds

        +------------+------------------------------------+
        | Valid Flag | Description                        |
        +============+====================================+
        | 0          | quality not evaluated;             |
        +------------+------------------------------------+
        | 1          | failed quality test;               |
        +------------+------------------------------------+
        | 2          | questionable or suspect data;      |
        +------------+------------------------------------+
        | 3          | good data/passed quality test; and |
        +------------+------------------------------------+
        | 9          | missing data.                      |
        +------------+------------------------------------+

        The 'observedpropery' of 'currents' has several flags.

        +------+----------------------------------------+
        | Flag | Description                            |
        +======+========================================+
        | 1    | overall bin status.                    |
        +------+----------------------------------------+
        | 2    | ADCP Built-In Test (BIT) status.       |
        +------+----------------------------------------+
        | 3    | Error Velocity test status.            |
        +------+----------------------------------------+
        | 4    | Percent Good test status.              |
        +------+----------------------------------------+
        | 5    | Correlation Magnitude test status.     |
        +------+----------------------------------------+
        | 6    | Vertical Velocity test status.         |
        +------+----------------------------------------+
        | 7    | North Horizontal Velocity test status. |
        +------+----------------------------------------+
        | 8    | East Horizontal Velocity test status.  |
        +------+----------------------------------------+
        | 9    | Echo Intensity test status.            |
        +------+----------------------------------------+

    startUTC
        an ISO 8601 date/time string
        (only seconds are optional)

    endUTC
        an ISO 8601 date/time string.
        (only seconds are optional)"""
    from tsgettoolbox.services import ndbc as placeholder

    r = resource(
        r'https://sdf.ndbc.noaa.gov/sos/server.php',
        station=station,
        startUTC=startUTC,
        endUTC=endUTC,
        observedproperty=observedproperty,
    )

    return tsutils.printiso(odo(r, pd.DataFrame))
