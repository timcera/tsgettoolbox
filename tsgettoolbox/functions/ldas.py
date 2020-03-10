from tsgettoolbox.odo import odo, resource
import pandas as pd
import mando
from tabulate import tabulate as tb

try:
    from mando.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter

from tstoolbox import tsutils

from tsgettoolbox.services import ldas as placeholder

new_units_table = [
    [
        "{0}\n{1}".format(i, placeholder._UNITS_MAP[i][0]),
        "{0}".format(placeholder._UNITS_MAP[i][1]),
    ]
    for i in placeholder._UNITS_MAP
]

units_table = tb(
    new_units_table,
    tablefmt="grid",
    headers=['LDAS "variable" string Description', "Units"],
)

units_table = "\n".join(["        {0}".format(i) for i in units_table.split("\n")])


@mando.command("ldas", formatter_class=HelpFormatter, doctype="numpy")
@tsutils.doc({"units_table": units_table})
def ldas_cli(
    lat=None,
    lon=None,
    xindex=None,
    yindex=None,
    variable=None,
    startDate=None,
    endDate=None,
):
    r"""Download data from LDAS.

    Available data sources are:

    +-------------------------------+----------+---------------+---------+
    | Description/Name              | Interval | Spatial       | Version |
    +===============================+==========+===============+=========+
    | NLDAS Primary Forcing Data    | 1 hour   | 0.125 x 0.125 | V002    |
    | NLDAS_FORA0125_H              |          | degree        |         |
    +-------------------------------+----------+---------------+---------+
    | NLDAS Noah Land Surface Model | 1 hour   | 0.125 x 0.125 | V002    |
    | NLDAS_NOAH0125_H              |          | degree        |         |
    +-------------------------------+----------+---------------+---------+
    | GLDAS Noah Land Surface Model | 3 hour   | 0.25 x 0.25   | V2.1    |
    | GLDAS_NOAH025_3H              |          | degree        |         |
    +-------------------------------+----------+---------------+---------+
    | AMSR-E/Aqua surface           | 1 day    | 25 x 25 km    | V002    |
    | soil moisture                 |          |               |         |
    +-------------------------------+----------+---------------+---------+
    | AMSR-E/Aqua root zone         | 1 day    | 25 x 25 km    | V001    |
    | soil moisture                 |          |               |         |
    | LPRM_AMSRE_D_RZSM3            |          |               |         |
    +-------------------------------+----------+---------------+---------+
    | AMSR2/GCOM-W1 surface         | 1 day    | 25 x 25 km    | V001    |
    | soil moisture                 |          |               |         |
    | LPRM_AMSR2_A_SOILM3           |          |               |         |
    +-------------------------------+----------+---------------+---------+
    | AMSR2/GCOM-W1 surface         | 1 day    | 25 x 25 km    | V001    |
    | soil moisture                 |          |               |         |
    | LPRM_AMSR2_D_SOILM3           |          |               |         |
    +-------------------------------+----------+---------------+---------+
    | AMSR2/GCOM-W1 surface         | 1 day    | 10 x 10 km    | V001    |
    | soil moisture                 |          |               |         |
    | LPRM_AMSR2_DS_A_SOILM3        |          |               |         |
    +-------------------------------+----------+---------------+---------+
    | ASMR2/GCOM-W1 surface         | 1 day    | 10 x 10 km    | V001    |
    | soil moisture                 |          |               |         |
    | LPRM_AMSR2_DS_D_SOILM3        |          |               |         |
    +-------------------------------+----------+---------------+---------+
    | TMI/TRMM surface              | 1 day    | 25 x 25 km    | V001    |
    | soil moisture                 |          |               |         |
    | LPRM_TMI_NT_SOILM3            |          |               |         |
    +-------------------------------+----------+---------------+---------+
    | TMI/TRMM surface              | 1 day    | 25 x 25 km    | V001    |
    | soil moisture                 |          |               |         |
    | LPRM_TMI_DY_SOILM3            |          |               |         |
    +-------------------------------+----------+---------------+---------+
    | TRMM (TMPA) Rainfall Estimate | 3 hour   | 0.25 x 0.25   | V7      |
    | TRMM_3B42                     |          | degree        |         |
    +-------------------------------+----------+---------------+---------+
    | Smerge-Noah-CCI root zone     | day      | 0.125 x 0.125 | V2.0    |
    | soil moisture 0-40 cm         |          | degree        |         |
    | SMERGE_RZSM0_40CM             |          |               |         |
    +-------------------------------+----------+---------------+---------+
    | Groundwater and Soil Moisture | 7 day    | 0.125 x 0.125 | V2.0    |
    | Conditions from GRACE         |          | degree        |         |
    | Data Assimilation             |          |               |         |
    | GRACEDADM_CLSM0125US_7D       |          |               |         |
    +-------------------------------+----------+---------------+---------+
    | MERRA-2 2D, Instantaneous,    | 1 hour   |               | V5.12.4 |
    | Land Surface Forcings         |          |               |         |
    | M2I1NXLFO                     |          |               |         |
    +-------------------------------+----------+---------------+---------+
    | MERRA-2 2D, Time-averaged,    | 1 hour   |               | V5.12.4 |
    | Surface Flux Diagnostics      |          |               |         |
    | M2T1NXFLX                     |          |               |         |
    +-------------------------------+----------+---------------+---------+
    | MERRA-2 2D, Time-averaged,    | 1 hour   |               | V5.12.4 |
    | Land Surface Forcings         |          |               |         |
    | M2T1NXLFO                     |          |               |         |
    +-------------------------------+----------+---------------+---------+
    | MERRA 2D Incremental          | 1 hour   |               | V5.2.0  |
    | Analysis Update               |          |               |         |
    | MST1NXMLD                     |          |               |         |
    +-------------------------------+----------+---------------+---------+

    The time zone is always UTC.

    Parameters
    ----------
    lat :  float
        Should use 'lat' and 'lon' to specify location.

        Latitude (required): Enter single geographic point by latitude.::

            Example: --lat=43.1

        If known, 'xindex' and 'yindex' can be used for the NLDAS grid only.
    lon : float
        Should use 'lat' and 'lon' to specify location.

        Longitude (required): Enter single geographic point by longitude::

            Example: --lon=-85.3

        If known, 'xindex' and 'yindex' can be used for the NLDAS grid only.
    xindex : int
        It `lat` or `lon` is None, then will try `xindex` and `yindex`.

        Enter the x index of the NLDAS grid.::

            Example: --xindex=301

    yindex : int
        It `lat` or `lon` is None, then will try `xindex` and `yindex`.

        Enter the y index of the NLDAS grid.::

            Example: --yindex=80

    variable : str
        Use the variable codes from the following table:

{units_table}

    startDate : str
        The start date of the time series.::

            Example: --startDate=2001-01-01T05

        If startDate and endDate are None, returns the entire series.

    endDate : str
        The end date of the time series.::

            Example: --endDate=2002-01-05T05

        If startDate and endDate are None, returns the entire series.
    """
    tsutils._printiso(
        ldas(
            lat=lat,
            lon=lon,
            xindex=xindex,
            yindex=yindex,
            variable=variable,
            startDate=startDate,
            endDate=endDate,
        )
    )


@tsutils.validator(
    lat=[float, ["range", [-90.0, 90.0]], 1],
    lon=[float, ["range", [-180.0, 180.0]], 1],
    xindex=[int, ["range", [0, None]], 1],
    yindex=[int, ["range", [0, None]], 1],
    variable=[str, ["pass", []], None],
    startDate=[tsutils.parsedate, ["pass", []], 1],
    endDate=[tsutils.parsedate, ["pass", []], 1],
)
def ldas(
    lat=None,
    lon=None,
    xindex=None,
    yindex=None,
    variable=None,
    startDate=None,
    endDate=None,
):
    r"""Download data from NLDAS or GLDAS."""
    project = variable.split(":")[0]
    if lat is not None and lon is not None:
        location = "GEOM:POINT({0}, {1})".format(lon, lat)
    elif project == "NLDAS" and xindex is not None and yindex is not None:
        location = "{0}:X{1:03d}-Y{2:03d}".format(project, xindex, yindex)
    else:
        raise ValueError(
            tsutils.error_wrapper(
                """
There is a problem specifying the location.

Both `lat` and `lon` need to be specified where you have "lat={lat}" and
"lon={lon}".

Only for the NLDAS grid can you use `xindex` and `yindex` to specify the
location.  You have the grid "{project}" and "xindex={xindex}" and
"yindex={yindex}".
""".format(
                    **locals()
                )
            )
        )

    ndf = pd.DataFrame()
    for cnt, var in enumerate(tsutils.make_list(variable)):
        r = resource(
            r"https://hydro1.gesdisc.eosdis.nasa.gov/daac-bin/access/timeseries.cgi",
            variable=var,
            location=location,
            startDate=startDate,
            endDate=endDate,
        )
        ndf = ndf.join(odo(r, pd.DataFrame), how="outer", rsuffix="_{0}".format(cnt))

    return ndf


ldas.__doc__ = ldas_cli.__doc__
