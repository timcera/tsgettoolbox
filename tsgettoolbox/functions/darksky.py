from tsgettoolbox.odo import odo, resource
import pandas as pd
import mando

try:
    from mando.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter

from tstoolbox import tsutils


@mando.command("darksky", formatter_class=HelpFormatter, doctype="numpy")
def darksky_cli(
    latitude, longitude, time=None, database="hourly", extend=None, lang="en"
):
    r"""Data from the Dark Sky forecast service.

    Powered by Dark Sky https://darksky.net/poweredby/

    Documentation: https://darksky.net/dev/docs

    Registration: https://darksky.net/dev/register

    The time zone of the returned data is dependent on the format of the
    "time" option.  If there is an ISO8601 representation of the time
    zone in the "time" option then that is the time zone of the returned
    data.  If "time" is None or does not explicitly define a time zone,
    the returned data is in the local time zone of the latitude and
    longitude.

    There isn't an absolutely consistent set of data returned for all
    areas, or all databases.  The returned values will be some subset of
    the following list:

    summary::

     A human-readable text summary of this data point.

    icon::

     A machine-readable text summary of this data |point, suitable for
     selecting an icon for display. If defined, this property will have
     one of the following values: 'clear-day', 'clear-night', 'rain',
     'snow', 'sleet', 'wind', 'fog', 'cloudy', 'partly-cloudy-day', or
     'partly-cloudy-night'.  (Developers should ensure that a sensible
     default is defined, as additional values, such as hail,
     thunderstorm, or tornado, may be defined in the future.)

    precipIntensity::

     A numerical value representing the average expected intensity (in
     inches of liquid water per hour) of precipitation occurring at the
     given time conditional on probability (that is, assuming any
     precipitation occurs at all). A very rough guide is that a value of
     0 in./hr. corresponds to no precipitation, 0.002 in./hr.
     corresponds to very light precipitation, 0.017 in./hr. corresponds
     to light precipitation, 0.1 in./hr. corresponds to moderate
     precipitation, and 0.4 in./hr. corresponds to heavy precipitation.

    precipProbability::

     A numerical value between 0 and 1 (inclusive) representing the
     probability of precipitation occuring at the given time.

    precipType::

     A string representing the type of precipitation occurring at the
     given time. If defined, this property will have one of the
     following values: rain, snow, sleet (which applies to each of
     freezing rain, ice pellets, and 'wintery mix'), or hail. (If
     precipIntensity is zero, then this property will not be defined.)

    dewPoint::

     A numerical value representing the dew point at the given time in
     degrees Fahrenheit.

    windSpeed::

     A numerical value representing the wind speed in miles per hour.

    windBearing::

     A numerical value representing the direction that the wind is
     coming from in degrees, with true north at 0 degree and
     progressing clockwise. (If windSpeed is zero, then this value will
     not be defined.)

    cloudCover::

     A numerical value between 0 and 1 (inclusive) representing the
     percentage of sky occluded by clouds. A value of 0 corresponds to
     clear sky, 0.4 to scattered clouds, 0.75 to broken cloud cover,
     and 1 to completely overcast skies.

    humidity::

     A numerical value between 0 and 1 (inclusive) representing the
     relative humidity.

    pressure::

     A numerical value representing the sea-level air pressure in
     millibars.

    visibility::

     A numerical value representing the average visibility in miles,
     capped at 10 miles.

    ozone::

     A numerical value representing the columnar density of total
     atmospheric ozone at the given time in Dobson units.

    **Only defined for 'currently' data**

    nearestStormDistance::

     A numerical value representing the distance to the nearest storm
     in miles. (This value is very approximate and should not be used
     in scenarios requiring accurate results. In particular, a storm
     distance of zero doesn't necessarily refer to a storm at the
     requested location, but rather a storm in the vicinity of that
     location.)

    nearestStormBearing::

     A numerical value representing the direction of the nearest storm
     in degrees, with true north at 0 degree and progressing clockwise.
     (If nearestStormDistance is zero, then this value will not be
     defined. The caveats that apply to nearestStormDistance also apply
     to this value.)

    **Only defined for 'daily' data**

    sunriseTime/sunsetTime::

     The last sunrise before and first sunset after the solar noon
     closest to local noon on the given day.  (Note: near the poles,
     these may occur on a different day entirely!)

    moonPhase::

     A number representing the fractional part of the lunation number
     of the given day. This can be thought of as the 'percentage
     complete' of the current lunar month: a value of 0 represents
     a new moon, a value of 0.25 represents a first quarter moon,
     a value of 0.5 represents a full moon, and a value of 0.75
     represents a last quarter moon. (The ranges in between these
     represent waxing crescent, waxing gibbous, waning gibbous, and
     waning crescent moons, respectively.)

    precipIntensityMax, and precipIntensityMaxTime::

     Numerical values representing the maximumum expected intensity of
     precipitation on the given day in inches of liquid water per hour.

    temperatureMin, temperatureMinTime, temperatureMax,
    and temperatureMaxTime::

     Numerical values representing the minimum and maximumum
     temperatures (and the UNIX times at which they occur) on the given
     day in degrees Fahrenheit.

    apparentTemperatureMin, apparentTemperatureMinTime,
    apparentTemperatureMax, and
    apparentTemperatureMaxTime::

     Numerical values representing the minimum and maximumum apparent
     temperatures and the times at which they occur on the given day in
     degrees Fahrenheit.

    **Only defined for 'hourly' and 'daily' data**

    precipAccumulation::

     The amount of snowfall accumulation expected to occur on the given
     day, in inches. (If no accumulation is expected, this property
     will not be defined.)

    **Defined for every dataset except 'daily'**

    apparentTemperature::

     A numerical value representing the apparent (or 'feels like')
     temperature at the given time in degrees Fahrenheit.

    temperature::

     A numerical value representing the temperature at the given time
     in degrees Fahrenheit.

    Parameters
    ----------
    latitude : float
        Latitude (required): Enter single geographic point by
        latitude.

    longitude : float
        Longitude (required): Enter single geographic point by
        longitude.

    time
        TIME should either be a UNIX time (that is, seconds since
        midnight GMT on 1 Jan 1970) or a string formatted as follows:
        [YYYY]-[MM]-[DD]T[HH]:[MM]:[SS] (with an optional time zone
        formatted as Z for GMT time or {+,-}[HH][MM] for an offset in
        hours or minutes). For the latter format, if no timezone is
        present, local time (at the provided latitude and longitude) is
        assumed.  (This string format is a subset of ISO 8601 time. An
        as example, 2013-05-06T12:00:00-0400.)

        The default is None, which uses the current time.

    database
        The database to draw the data from.  This is slightly different
        than the typical Forecast.io request, which would normally send
        back all data from all databases.  Typically though the
        'tsgettoolbox' and siblings expect a single time increment in
        a dataset.  This isn't a hard rule, just a tradition.  So pick
        a database from 'currently', 'minutely', 'hourly', 'daily',
        'alerts', or 'flags'.  The 'currently' database is the default
        and is the current conditions.  'minutely' give minute by minute
        forecast from the current time for the next hour, 'hourly' gives
        hourly forecast for the next two days (unless --extend='hourly'
        option is given), and 'daily' gives a forecast day by day for
        the next week.

    extend
        If set to 'hourly' and --database='hourly' then will get an
        hourly forecast for the next week.

    lang : str
        Return text summaries in the desired language.  (Please be
        advised that units in the summary will be set according to the
        units option, above, so be sure to set both options as needed.)

        +-------------+-------------------+
        | lang= code  | Language          |
        +=============+===================+
        | ar          | Arabic            |
        +-------------+-------------------+
        | bs          | Bosnian           |
        +-------------+-------------------+
        | de          | German            |
        +-------------+-------------------+
        | en          | English (default) |
        +-------------+-------------------+
        | es          | Spanish           |
        +-------------+-------------------+
        | fr          | French            |
        +-------------+-------------------+
        | it          | Italian           |
        +-------------+-------------------+
        | nl          | Dutch             |
        +-------------+-------------------+
        | pl          | Polish            |
        +-------------+-------------------+
        | pt          | Portuguese        |
        +-------------+-------------------+
        | ru          | Russian           |
        +-------------+-------------------+
        | sk          | Slovak            |
        +-------------+-------------------+
        | sv          | Swedish           |
        +-------------+-------------------+
        | tet         | Tetum             |
        +-------------+-------------------+
        | tr          | Turkish           |
        +-------------+-------------------+
        | uk          | Ukrainian         |
        +-------------+-------------------+
        | x-pig-latin | Igpay Atinlay     |
        +-------------+-------------------+
        | zh          | Chinese           |
        +-------------+-------------------+

    """
    tsutils._printiso(
        darksky(
            latitude, longitude, time=time, database=database, extend=extend, lang=lang
        )
    )


@tsutils.validator(
    latitude=[float, ["range", [-90.0, 90.0]], 1],
    longitude=[float, ["range", [-180.0, 180.0]], 1],
    time=[tsutils.parsedate, ["pass", []], 1],
    database=[
        str,
        ["domain", ["currently", "minutely", "hourly", "daily", "alerts", "flags"]],
        1,
    ],
    extend=[str, ["domain", ["hourly"]], 1],
    lang=[
        str,
        [
            "domain",
            [
                "ar",
                "bs",
                "de",
                "en",
                "es",
                "fr",
                "it",
                "nl",
                "pl",
                "pt",
                "ru",
                "sk",
                "sv",
                "tet",
                "tr",
                "uk",
                "x-pig-latin",
                "zh",
            ],
        ],
        1,
    ],
)
def darksky(latitude, longitude, time=None, database="hourly", extend=None, lang="en"):
    r"""Data from the Dark Sky forecast service."""
    from tsgettoolbox.services import darksky as placeholder

    r = resource(
        r"https://api.darksky.net/forecast",
        latitude=latitude,
        longitude=longitude,
        database=database,
        time=time,
        extend=extend,
        units="si",
        lang=lang,
    )
    return odo(r, pd.DataFrame)


@mando.command(formatter_class=HelpFormatter, doctype="numpy")
def forecast_io(
    latitude, longitude, time=None, database="hourly", extend=None, lang="en"
):
    r"""DEPRECATED: please use 'darksky'.

    The forecast_io service changed names to 'darksky'.  See documentation
    under the darksky service.

    Parameters
    ----------
    latitude
        See documentation under the darksky
        service.

    longitude
        See documentation under the darksky
        service.

    time
        See documentation under the darksky
        service.

    database
        See documentation under the darksky
        service.

    extend
        See documentation under the darksky
        service.

    lang
        See documentation under the darksky
        service.

    """
    return darksky(
        latitude, longitude, time=time, database=database, extend=extend, lang=lang
    )


darksky.__doc__ = darksky_cli.__doc__
