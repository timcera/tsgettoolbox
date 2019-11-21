from tsgettoolbox.odo import odo, resource
import pandas as pd
import mando

try:
    from mando.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter

from tstoolbox import tsutils


@mando.command("ldas", formatter_class=HelpFormatter, doctype="numpy")
def ldas_cli(
    lat=None,
    lon=None,
    xindex=None,
    yindex=None,
    variable=None,
    startDate=None,
    endDate=None,
):
    r"""Download data from NLDAS or GLDAS.

    The time zone is always UTC.

    Parameters
    ----------
    lat :  float
        Either 'lat' and 'lon', or 'xindex' and
        'yindex' is required.

        Latitude (required): Enter single geographic point by
        latitude.::

            Example: --lat=43.1

    lon : float
        Either 'lat' and 'lon', or 'xindex' and
        'yindex' is required.  Longitude (required): Enter single
        geographic point by longitude::

            Example: --lon=-85.3

    xindex : int
        Either 'lat' and 'lon', or 'xindex' and
        'yindex' is required.  xindex (required if using xindex/yindex):
        Enter the x index of the NLDAS or GLDAS grid.::

            Example: --xindex=301

    yindex : int
        Either 'lat' and 'lon', or 'xindex' and
        'yindex' is required.  yindex (required if using xindex/yindex):
        Enter the y index of the NLDAS or GLDAS grid.::

            Example: --yindex=80

    variable : str
        Use the variable codes from the following table:

        +--------------------------------------------+-----------+
        | LDAS "variable" string Description         | Units     |
        +============================================+===========+
        | NLDAS:NLDAS_FORA0125_H.002:APCPsfc         | kg/m^2    |
        | Precipitation hourly total                 |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_FORA0125_H.002:DLWRFsfc        | W/m^2     |
        | Surface DW longwave radiation flux         |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_FORA0125_H.002:DSWRFsfc        | W/m^2     |
        | Surface DW shortwave radiation flux        |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_FORA0125_H.002:PEVAPsfc        | kg/m^2    |
        | Potential evaporation                      |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_FORA0125_H.002:SPFH2m          | kg/kg     |
        | 2-m above ground specific humidity         |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_FORA0125_H.002:TMP2m           | degK      |
        | 2-m above ground temperature               |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_FORA0125_H.002:UGRD10m         | m/s       |
        | 10-m above ground zonal wind               |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_FORA0125_H.002:VGRD10m         | m/s       |
        | 10-m above ground meridional wind          |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_NOAH0125_H.002:EVPsfc          | kg/m^2    |
        | Total evapotranspiration                   |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_NOAH0125_H.002:GFLUXsfc        | w/m^2     |
        | Ground heat flux                           |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_NOAH0125_H.002:LHTFLsfc        | w/m^2     |
        | Latent heat flux                           |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_NOAH0125_H.002:SHTFLsfc        | w/m^2     |
        | Sensible heat flux                         |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_NOAH0125_H.002:SSRUNsfc        | kg/m^2    |
        | Surface runoff (non-infiltrating)          |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_NOAH0125_H.002:BGRIUNdfc       | kg/m^2    |
        | Subsurface runoff (baseflow)               |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_NOAH0125_H.002:SOILM0-10cm     | kg/m^2    |
        | 0-10 cm soil moisture content              |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_NOAH0125_H.002:SOILM0-100cm    | kg/m^2    |
        | 0-100 cm soil moisture content             |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_NOAH0125_H.002:SOILM0-200cm    | kg/m^2    |
        | 0-200 cm soil moisture content             |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_NOAH0125_H.002:SOILM10-40cm    | kg/m^2    |
        | 10-40 cm soil moisture content             |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_NOAH0125_H.002:SOILM40-100cm   | kg/m^2    |
        | 40-100 cm soil moisture content            |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_NOAH0125_H.002:SOILM100-200cm  | kg/m^2    |
        | 100-200 cm soil moisture content           |           |
        +--------------------------------------------+-----------+
        | NLDAS:NLDAS_NOAH0125_H.002:TSOIL0-10cm     | degK      |
        | 0-10 cm soil temperature                   |           |
        +--------------------------------------------+-----------+
        | GLDAS:GLDAS_NOAH025_3H.001:Evap            | kg/m^2/s  |
        | Evapotranspiration                         |           |
        +--------------------------------------------+-----------+
        | GLDAS:GLDAS_NOAH025_3H.001:precip          | kg/m^s/hr |
        | Precipitation rate                         |           |
        +--------------------------------------------+-----------+
        | GLDAS:GLDAS_NOAH025_3H.001:Rainf           | kg/m^2/s  |
        | Rain rate                                  |           |
        +--------------------------------------------+-----------+
        | GLDAS:GLDAS_NOAH025_3H.001:Snowf           | kg/m^2/s  |
        | Snow rate                                  |           |
        +--------------------------------------------+-----------+
        | GLDAS:GLDAS_NOAH025_3H.001:Qs              | kg/m^2/s  |
        | Surface Runoff                             |           |
        +--------------------------------------------+-----------+
        | GLDAS:GLDAS_NOAH025_3H.001:Qsb             | kg/m^2/s  |
        | Subsurface Runoff                          |           |
        +--------------------------------------------+-----------+
        | GLDAS:GLDAS_NOAH025_3H.001:SOILM0-100cm    | kg/m^2    |
        | 0-100 cm top 1 meter soil moisture content |           |
        +--------------------------------------------+-----------+
        | GLDAS:GLDAS_NOAH025_3H.001:SOILM0-10cm     | kg/m^2    |
        | 0-10 cm layer 1 soil moisture content      |           |
        +--------------------------------------------+-----------+
        | GLDAS:GLDAS_NOAH025_3H.001:SOILM10-40cm    | kg/m^2    |
        | 10-40 cm layer 2 soil moisture content     |           |
        +--------------------------------------------+-----------+
        | GLDAS:GLDAS_NOAH025_3H.001:SOILM40-100cm   | kg/m^2    |
        | 40-100 cm layer 3 soil moisture content    |           |
        +--------------------------------------------+-----------+
        | GLDAS:GLDAS_NOAH025_3H.001:Tair            | degK      |
        | Near surface air temperature               |           |
        +--------------------------------------------+-----------+
        | GLDAS:GLDAS_NOAH025_3H.001:TSOIL0-10cm     | degK      |
        | Average layer 1 soil temperature           |           |
        +--------------------------------------------+-----------+
        | GLDAS:GLDAS_NOAH025_3H.001:Wind            | m/s       |
        | Near surface wind magnitude                |           |
        +--------------------------------------------+-----------+

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
    xindex=[int, ["range", [0,]], 1],
    yindex=[int, ["range", [0,]], 1],
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
    from tsgettoolbox.services import ldas as placeholder

    project = variable.split(":")[0]
    if lat is not None:
        location = "GEOM:POINT({0}, {1})".format(lon, lat)
    else:
        if project == "NLDAS":
            location = "{0}:X{1:03d}-Y{2:03d}".format(project, xindex, yindex)
        else:
            location = "{0}:X{1:04d}-Y{2:03d}".format(project, xindex, yindex)

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
