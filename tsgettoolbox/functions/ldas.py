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

    +-------------------------------+--------+-------------+---------------+
    | Description/Name              | Int    | Spatial     | Period        |
    +===============================+========+=============+===============+
    | NLDAS Primary Forcing Data    | 1 hour | 0.125x0.125 | 1979-01-01T13 |
    | NLDAS_FORA0125_H              |        | degree      | til           |
    | V002                          |        |             | recent        |
    +-------------------------------+--------+-------------+---------------+
    | NLDAS Noah Land Surface Model | 1 hour | 0.125x0.125 | 1979-01-01T13 |
    | NLDAS_NOAH0125_H              |        | degree      | til           |
    | V002                          |        |             | recent        |
    +-------------------------------+--------+-------------+---------------+
    | GLDAS Noah Land Surface Model | 3 hour | 0.25x0.25   |               |
    | GLDAS_NOAH025_3H              |        | degree      |               |
    | V2.1                          |        |             |               |
    +-------------------------------+--------+-------------+---------------+
    | AMSR-E/Aqua surface           | 1 day  | 25x25 km    |               |
    | soil moisture                 |        |             |               |
    | V002                          |        |             |               |
    +-------------------------------+--------+-------------+---------------+
    | AMSR-E/Aqua root zone         | 1 day  | 25x25 km    |               |
    | soil moisture                 |        |             |               |
    | LPRM_AMSRE_D_RZSM3            |        |             |               |
    | V001                          |        |             |               |
    +-------------------------------+--------+-------------+---------------+
    | AMSR2/GCOM-W1 surface         | 1 day  | 25x25 km    |               |
    | soil moisture                 |        |             |               |
    | LPRM_AMSR2_A_SOILM3           |        |             |               |
    | V001                          |        |             |               |
    +-------------------------------+--------+-------------+---------------+
    | AMSR2/GCOM-W1 surface         | 1 day  | 25x25 km    |               |
    | soil moisture                 |        |             |               |
    | LPRM_AMSR2_D_SOILM3           |        |             |               |
    | V001                          |        |             |               |
    +-------------------------------+--------+-------------+---------------+
    | AMSR2/GCOM-W1 surface         | 1 day  | 10x10 km    |               |
    | soil moisture                 |        |             |               |
    | LPRM_AMSR2_DS_A_SOILM3        |        |             |               |
    | V001                          |        |             |               |
    +-------------------------------+--------+-------------+---------------+
    | ASMR2/GCOM-W1 surface         | 1 day  | 10x10 km    |               |
    | soil moisture                 |        |             |               |
    | LPRM_AMSR2_DS_D_SOILM3        |        |             |               |
    | V001                          |        |             |               |
    +-------------------------------+--------+-------------+---------------+
    | TMI/TRMM surface              | 1 day  | 25x25 km    |               |
    | soil moisture                 |        |             |               |
    | LPRM_TMI_NT_SOILM3            |        |             |               |
    | V001                          |        |             |               |
    +-------------------------------+--------+-------------+---------------+
    | TMI/TRMM surface              | 1 day  | 25x25 km    |               |
    | soil moisture                 |        |             |               |
    | LPRM_TMI_DY_SOILM3            |        |             |               |
    | V001                          |        |             |               |
    +-------------------------------+--------+-------------+---------------+
    | TRMM (TMPA) Rainfall Estimate | 3 hour | 0.25x0.25   |               |
    | TRMM_3B42                     |        | degree      |               |
    | V7                            |        |             |               |
    +-------------------------------+--------+-------------+---------------+
    | Smerge-Noah-CCI root zone     | day    | 0.125x0.125 |               |
    | soil moisture 0-40 cm         |        | degree      |               |
    | SMERGE_RZSM0_40CM             |        |             |               |
    | V2.0                          |        |             |               |
    +-------------------------------+--------+-------------+---------------+
    | Groundwater and Soil Moisture | 7 day  | 0.125x0.125 |               |
    | Conditions from GRACE         |        | degree      |               |
    | Data Assimilation             |        |             |               |
    | GRACEDADM_CLSM0125US_7D       |        |             |               |
    | V2.0                          |        |             |               |
    +-------------------------------+--------+-------------+---------------+
    | MERRA-2 2D, Instantaneous,    | 1 hour |             |               |
    | Land Surface Forcings         |        |             |               |
    | M2I1NXLFO                     |        |             |               |
    | V5.12.4                       |        |             |               |
    +-------------------------------+--------+-------------+---------------+
    | MERRA-2 2D, Time-averaged,    | 1 hour |             |               |
    | Surface Flux Diagnostics      |        |             |               |
    | M2T1NXFLX                     |        |             |               |
    | V5.12.4                       |        |             |               |
    +-------------------------------+--------+-------------+---------------+
    | MERRA-2 2D, Time-averaged,    | 1 hour |             |               |
    | Land Surface Forcings         |        |             |               |
    | M2T1NXLFO                     |        |             |               |
    | V5.12.4                       |        |             |               |
    +-------------------------------+--------+-------------+---------------+
    | MERRA 2D Incremental          | 1 hour |             |               |
    | Analysis Update               |        |             |               |
    | MST1NXMLD                     |        |             |               |
    | V5.12.4                       |        |             |               |
    +-------------------------------+--------+-------------+---------------+

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
