"""
ldas_nldas3_for
"""

# Standard library imports
import datetime
import logging
import os
import textwrap
from contextlib import suppress
from typing import Literal

# Third party imports
import fsspec
import pandas as pd
import xarray as xr
from pydantic import validate_call
from tabulate import tabulate as tb

# First party imports
from tsgettoolbox.toolbox_utils.src.toolbox_utils import tsutils

__all__ = [
    "ldas_nldas3_forcing",
]

logger = logging.getLogger(__name__)

# fmt: off
_NLDAS3_FORCING = {
    "Tair": ["Near surface air temperature", "degK"],
    "Qair": ["Near-surface specific humidity", "kg/kg"],
    "PSurf": ["Surface pressure", "Pa"],
    "Wind_N": ["Northward wind", "m/s"],
    "Wind_E": ["Eastward wind", "m/s"],
    "LWdown": ["Downward longwave radiation at the surface", "W/m^2"],
    "SWdown": ["Downward shortwave radiation at the surface", "W/m^2"],
    "Rainf": ["Total precipitation rate", "kg/m"],
}

_NLDAS3_NOAH = {
    "SWnet": [ "Surface net downward shortwave flux", "W/m^2",],
    "LWnet": [ "Surface net downward longwave flux", "W/m^2",],
    "Qle": [ "Surface upward latent heat flux", "W/m^2",],
    "Qh": [ "Surface upward sensible heat flux", "W/m^2",],
    "Qg": [ "Downward heat flux in soil", "W/m^2",],
    "Snowf": [ "Snowfall rate (frozen)", "mm/s",],
    "Rainf": [ "Rainfall rate (liquid)", "mm/s",],
    "Evap": [ "Total evapotranspiration", "mm/s",],
    "Qs": [ "Surface runoff amount", "mm/s",],
    "Qsb": [ "Subsurface runoff amount", "mm/s",],
    "AvgSurfT": [ "Surface temperature", "degK",],
    "AvgSurfT_min": [ "Daily minimum surface temperature", "degK",],
    "AvgSurfT_max": [ "Daily maximum surface temperature", "degK",],
    "SWE": [ "Liquid water content of surface snow", "mm",],
    "SnowDepth": [ "Snow depth", "m",],
    "SoilMoist": [ "Soil moisture - 4 layers [0-10cm; 10-40cm; 40-100cm; 100-200cm]", "m3/m3",],
    "SoilTemp": [ "Soil temperature - 4 layers [0-10cm; 10-40cm; 40-100cm; 100-200cm]", "degK",],
    "PotEvap": [ "Potential evapotranspiration", "mm/s",],
    "VPD": [ "Vapor pressure deficit", "Pa",],
    "TVeg": [ "Vegetation transpiration", "mm/s",],
    "ESoil": [ "Bare soil evaporation", "mm/s",],
    "CanopInt": [ "Total canopy water storage", "mm",],
    "WaterTableD": [ "Water table depth", "m",],
    "TWS": [ "Terrestrial water storage", "mm",],
    "GWS": [ "Groundwater storage", "mm",],
    "SnowFrac": [ "Surface snow area fraction", "[-]",],
    "GPP": [ "Gross primary productivity", "g/m2/s",],
    "NPP": [ "Net primary productivity", "g/m2/s",],
    "NEE": [ "Net ecosystem exchange", "g/m2/s",],
    "LAI": [ "Leaf area index", "[-]",],
}

_NLDAS3_HYMAP = {
    "Streamflow": ["Streamflow", "m3/s"],
    "RiverDepth": ["River depth", "m"],
    "FloodedFrac": ["Flooded fraction", "[-]"],
    "SurfElev": ["Surface water elevation", "m"],
    "SWS": ["Surface water storage", "mm"],
}

_NLDAS3_STATIC = {
    "surface_class": ["Land use and vegetation", "int"],
    "soil_class": ["Soil texture class", "int"],
    "slope": ["Surface slope", "m/m"],
    "aspect": ["Surface aspect", "radians"],
    "latitude": ["Latitude", "degrees"],
    "longitude": ["Longitude", "degrees"],
}
# fmt: on

_UNITS_MAP = {}
_UNITS_MAP.update(_NLDAS3_FORCING)
_UNITS_MAP.update(_NLDAS3_NOAH)
_UNITS_MAP.update(_NLDAS3_HYMAP)
_UNITS_MAP.update(_NLDAS3_STATIC)

_varmap = {
    "NLDAS3": "NLDAS3",
}

_project_start_dates = {
    "NLDAS3": "2001-01-01T00",
}

_project_lat_ranges = {
    "NLDAS3": (7, 72),
}

_project_lon_ranges = {
    "NLDAS3": (-169, -52),
}


def make_units_table(units_dict):
    """
    Make a table of variables for the docstring.

    Parameters
    ----------
    units_dict : dict
        A dictionary mapping variable codes to a list of [description, units].

    Returns
    -------
    str
        A formatted table of variable codes, descriptions, and units.
    """
    new_units_table = [
        [
            f"{key}",
            f"{val[0]}",
            f"{val[1]}",
        ]
        for key, val in units_dict.items()
    ]

    units_table = tb(
        new_units_table,
        tablefmt="grid",
        headers=['LDAS "variables" string', "Description", "Units"],
        maxcolwidths=[None, 25, None],
    )

    return textwrap.indent(units_table.strip(), "            ")


_NLDAS3_NOAH_META = r"""

        +------------------+-----------+-----------+-----------+---------------+
        | Description/Name | Spatial   | Lat Range | Lon Range | Time          |
        +==================+===========+===========+===========+===============+
        | NLDAS V3 NOAH    | 0.01x0.01 | 7, 72     | -169, -52 | daily,        |
        | Hydrology model  |           |           |           | monthly       |
        |                  |           |           |           | 2001-01-01 to |
        |                  |           |           |           | recent        |
        +------------------+-----------+-----------+-----------+---------------+

"""
_NLDAS3_HYMAP_META = r"""

        +------------------+-----------+-----------+-----------+---------------+
        | Description/Name | Spatial   | Lat Range | Lon Range | Time          |
        +==================+===========+===========+===========+===============+
        | NLDAS V3 HYMAP   | 0.01x0.01 | 7, 72     | -169, -52 | daily,        |
        | routing model    |           |           |           | monthly       |
        |                  |           |           |           | 2001-01-01 to |
        |                  |           |           |           | recent        |
        +------------------+-----------+-----------+-----------+---------------+

"""
_NLDAS3_STATIC_META = r"""

        +------------------+-----------+-----------+-----------+---------------+
        | Description/Name | Spatial   | Lat Range | Lon Range | Time          |
        +==================+===========+===========+===========+===============+
        | NLDAS V3 Static  | 0.01x0.01 | 7, 72     | -169, -52 |               |
        | information      |           |           |           |               |
        +------------------+-----------+-----------+-----------+---------------+

"""

NLDAS3_NOAH_FIRST_LINE = "NAmerica:0.01deg:2001-:DM:NLDAS NOAH hydrology model results"
NLDAS3_HYMAP_FIRST_LINE = "NAmerica:0.01deg:2001-:DM:NLDAS HYMAP routing model results"
NLDAS3_STATIC_FIRST_LINE = "NAmerica:0.01deg:2001-::NLDAS static information"

NLDAS3_NOAH_DESCRIPTION = """
        Noah is National Centers for Environmental Prediction/Oregon State
        University/Air Force/Hydrologic Research Lab (Noah) Model

        The community Noah LSM was developed beginning in 1993 through
        a collaboration of investigators from public and private institutions,
        spearheaded by the National Centers for Environmental Prediction.
        Current development efforts are consistent with the land surface scheme
        in Weather Research Forecast (WRF) system, under the Unified Noah LSM
        (Chen et al. 1996; Chen et al. 1997; Koren et al. 1999; Chen et al.
        2001; Ek et al. 2003). Noah is a stand-alone, 1-D column model which
        can be executed in either coupled or uncoupled mode.  The model applies
        finite-difference spatial discretization methods and a Crank-Nicholson
        time-integration scheme to numerically integrate the governing
        equations of the physical processes of the soil-vegetation-snowpack
        medium. Noah has been used operationally in NCEP models since 1996, and
        it continues to be developed at the University Corporation for
        Atmospheric Research and National Center for Atmospheric Research,
        Research Application Laboratory. For more information, go to:
        https://ral.ucar.edu/model/unified-noah-lsm.

        Adler, R.F., G.J. Huffman, A. Chang, R. Ferraro, P. Xie, J. Janowiak,
        B. Rudolf, U. Schneider, S. Curtis, D. Bolvin, A. Gruber, J. Susskind,
        P. Arkin, E. Nelkin 2003: The Version 2 Global Precipitation
        Climatology Project (GPCP) Monthly Precipitation Analysis
        (1979-Present). J. Hydrometeor., 4,1147-1167.

        Berg, A. A., J. S. Famiglietti, J. P. Walker, and P. R. Houser, 2003:
        Impact of bias correction to reanalysis products on simulations of
        North American soil moisture and hydrological fluxes, J. Geophys. Res,
        108 (D16), 4490.

        Chen, F., K. Mitchell, J. Schaake, Y. Xue, H. Pan, V. Koren, Y. Duan,
        M. Ek, and A. Betts, Modeling of land-surface evaporation by four
        schemes and comparison with FIFE observations, J. Geophys. Res.,101
        (D3), 7251-7268, 1996.

        Chen, F., Z. Janjic, and K. Mitchell, Impact of atmospheric surface
        layer parameterization in the new land-surface scheme of the NCEP
        Mesoscale Eta numerical model, Bound.-Layer Meteor., 185, 391-421,
        1997.

        Chen, F. and J.Dudhia, Coupling an Advanced Land Surface-Hydrology
        Model with the Penn State-NCAR MM5 Modeling System. Part I: Model
        Implementation and Sensitivity, Mon. Wea. Rev., 129, 569-585, 2001.

        Derber, J. C., D. F. Parrish, and S. J. Lord, 1991: The new global
        operational analysis system at the National Meteorological Center.
        Weather Forecasting, 6, 538-547.

        Ek, M. B., K. E. Mitchell, Y. Lin, E. Rogers, P. Grunmann, V. Koren, G.
        Gayno, and J. D. Tarpley, Implementation of Noah land surface model
        advances in the National Centers for Environmental Prediction
        operational mesoscale Eta model, J. Geophys. Res., 108(D22), 8851,
        doi:10.1029/2002JD003296, 2003.

        Koren, V., J. Schaake, K. Mitchell, Q. Y. Duan, F. Chen, and J. M.
        Baker, A parameterization of snowpack and frozen ground intended for
        NCEP weather and climate models, J. Geophys. Res.,104, 19569-19585,
        1999.

        Sheffield, J., G. Goteti, and E. F. Wood, 2006: Development of a 50-yr
        high-resolution global dataset of meteorological forcings for land
        surface modeling, J. Climate, 19 (13), 3088-3111.

        Xie P., and P. A. Arkin, 1996: Global precipitation: a 17-year monthly
        analysis based on gauge observations, satellite estimates, and
        numerical model outputs. Bull. Amer. Meteor. Soc., 78, 2539-2558.
"""

NLDAS3_HYMAP_DESCRIPTION = """
"""

NLDAS3_STATIC_DESCRIPTION = """
"""


def normalize_lat_lon(lat, lon):
    """Normalize latitude and longitude values."""
    if lat < _project_lat_ranges["NLDAS3"][0] or lat > _project_lat_ranges["NLDAS3"][1]:
        raise ValueError(
            tsutils.error_wrapper(
                f"Latitude {lat} is out of range for NLDAS3 data. "
                f"Valid range is {_project_lat_ranges['NLDAS3'][0]} to "
                f"{_project_lat_ranges['NLDAS3'][1]}."
            )
        )
    if lon < _project_lon_ranges["NLDAS3"][0] or lon > _project_lon_ranges["NLDAS3"][1]:
        raise ValueError(
            tsutils.error_wrapper(
                f"Longitude {lon} is out of range for NLDAS3 data. "
                f"Valid range is {_project_lon_ranges['NLDAS3'][0]} to "
                f"{_project_lon_ranges['NLDAS3'][1]}."
            )
        )
    return lat, lon


def normalize_start_end_dates(startDate, endDate):
    """Normalize start and end dates."""
    if startDate is None:
        startDate = tsutils.parsedate(_project_start_dates["NLDAS3"])
    else:
        with suppress(TypeError):
            startDate = tsutils.parsedate(startDate)
            startDate = max(
                startDate, tsutils.parsedate(_project_start_dates["NLDAS3"])
            )
    if endDate is None:
        endDate = tsutils.parsedate(
            (datetime.datetime.now(datetime.timezone.utc)).strftime("%Y-%m-%dT%H")
        )
    else:
        endDate = tsutils.parsedate(endDate)
    return startDate, endDate


@tsutils.transform_args(variables=tsutils.make_list)
@validate_call
def ldas_nldas3_forcing(
    lat: float,
    lon: float,
    variables=None,
    startDate=None,
    endDate=None,
    time_interval: Literal["hourly", "daily"] = "hourly",
):
    r"""
    NAmerica:0.01deg:2001-:HDM:NLDAS Meteorological Forcing (surface)

    +------------------+-----------+-----------+-----------+---------------+
    | Description/Name | Spatial   | Lat Range | Lon Range | Time          |
    +==================+===========+===========+===========+===============+
    | NLDAS V3 Forcing | 0.01x0.01 | 7, 72     | -169, -52 | 1 hr, daily,  |
    |                  |           |           |           | monthly       |
    |                  |           |           |           | 2001-01-01 to |
    |                  |           |           |           | recent        |
    +------------------+-----------+-----------+-----------+---------------+

    Baldwin, M., and K.E. Mitchell, 1997: The NCEP hourly multi-sensor U.S.
    precipitation analysis for operations and GCIP research. Preprints,
    13th AMS Conference on Hydrology, pp. 54-55, Am. Meteorol. Soc.,
    Boston, Mass.

    Berg, A.A., J.S. Famiglietti, J.P. Walker, and P.R. Houser, 2003:
    Impact of bias correction to reanalysis products on simulations of
    North American soil moisture and hydrological fluxes.  J. Geophys.
    Res., 108(D16), 4490, doi:10.1029/2002JD003334.

    Cosgrove, B.A., et al., 2003: Real-time and retrospective forcing in
    the North American Land Data Assimilation System (NLDAS) project.  J.
    Geophys. Res., 108(D22), 8842, doi:10.1029/2002JD003118.

    Daly, C., R.P. Neilson, and D.L. Phillips, 1994:
    A statistical-topographic model for mapping climatological
    precipitation over mountainous terrain.  J. Appl. Meteor., 33, 140-158,
    doi:10.1175/1520-0450(1994)033<0140:ASTMFM>2.0.CO;2

    Fulton, R.A., J.P. Breidenbach, D.J. Seo, D.A. Miller, and T. O'Bannon,
    1998: The WSR-88D rainfall algorithm.  Weather and Forecasting, 13,
    377-395.

    Higgins, R.W., J.E. Janowiak and Y. Yao, 1996: A gridded hourly
    precipitation data base for the United States (1963-1993). NCEP/Climate
    Prediction Center Atlas No. 1.

    Higgins, R.W., W. Shi, E. Yarosh, and R. Joyce, 2000: Improved United
    States precipitation quality control system and analysis. NCEP/Climate
    Prediction Center Atlas No. 7.

    Mitchell, K.E., et al., 2004: The multi-institution North American Land
    Data Assimilation System (NLDAS): Utilizing multiple GCIP products and
    partners in a continental distributed hydrological modeling system.  J.
    Geophys. Res., 109, D07S90, doi:10.1029/2003JD003823.

    Mo, K.C., L.-C. Chen, S. Shukla, T.J. Bohn, and D.P. Lettenmaier, 2012:
    Uncertainties in North American Land Data Assimilation Systems over the
    Contiguous United States.  J. Hydrometeor, 13, 996-1009,
    doi:10.1175/JHM-D-11-0132.1

    Pinker, R.T., et al., 2003: Surface radiation budgets in support of the
    GEWEX Continental-Scale International Project (GCIP) and the GEWEX
    Americas Prediction Project (GAPP), including the North American Land
    Data Assimilation System (NLDAS) project.  J. Geophys. Res., 108(D22),
    8844, doi:10.1029/2002JD003301.

    Parameters
    ----------
    lat : float
        Latitude (required): Enter single geographic latitude point. Use
        positive values for the northern hemisphere and negative for the
        southern hemisphere.  The valid range is specified in the table
        above.

    lon : float
        Longitude (required): Enter single geographic longitude point. Use
        positive for the eastern hemisphere and negative for the western
        hemisphere.  The valid range is specified in the table above.

    variables : str
        For the command line a comma separated string of variable codes
        from the following table.  Using the Python API a list of variable
        strings.  Valid variable names are specified in the table below.

        ${units_table}

    startDate : str
        The start date of the time series.::

            Example: --startDate=2001-01-01T05

        If startDate and endDate are None, returns the entire series.
    endDate : str
        The end date of the time series.::

            Example: --endDate=2002-01-05T05

        If startDate and endDate are None, returns the entire series.
    time_interval : str
        The time interval of the data to retrieve. Can be either "hourly"
        or "daily". Defaults to "hourly".
    """
    if os.path.exists("debug_tsgettoolbox"):
        logger.warning(f"{lat=}, {lon=}, {variables=}, {startDate=}, {endDate=}")

    lat, lon = normalize_lat_lon(lat, lon)

    startDate, endDate = normalize_start_end_dates(startDate, endDate)

    ## Set up a reference file system based on the chunk refs stored in
    ## the parquet file. This only loads the metadata needed to create
    ## the impression of a zarr store on the local machine.
    ## This essentially abstracts away the difference between individual
    ## netCDF files on the s3 bucket by mapping zarr chunks to a
    ## combination of URLs and byte offsets/lengths of netCDF chunks
    ## under each URL
    ref_fs = fsspec.filesystem(
        "reference",
        fo=f"s3://nasa-waterinsight/virtual/nldas3_{time_interval}.parq",
        remote_protocol="s3",
        asynchronous=True,
        remote_options={"asynchronous": True, "anon": True},
        target_options={"anon": True},
        lazy=True,
    )

    with xr.open_dataset(
        ref_fs.get_mapper(""),
        engine="zarr",
        decode_times=True,
        backend_kwargs={"consolidated": False},
    ) as ds:
        ## use data coordinates to identify a subset of the data to retrieve.
        sub = ds.sel(lon=lon, lat=lat, method="nearest").sel(
            time=slice(startDate, endDate)
        )

        # Do this here instead of in the loop below to avoid repeated calls to
        # load() for each variable.
        index = sub.time.load()

        ndf = pd.DataFrame()
        for get_var in variables:
            df = pd.DataFrame(
                sub[get_var].load(),
                index=index,
                columns=[f"{get_var}:{_UNITS_MAP[get_var][1]}"],
            )
            df.index.name = "Datetime:UTC"
            df = df.tz_localize("UTC")

            ndf = ndf.combine_first(df)

    return ndf


if __name__ == "__main__":
    r = ldas_nldas3_forcing(
        34,
        -100,
        variables="Tair",
        startDate="2001-01-01T00",
        endDate="2001-02-02T00",
    )

    print("LDAS TEST")
    print(r)

    r = ldas_nldas3_forcing(
        34,
        -100,
        variables=["Tair", "Qair"],
        endDate="2002-01-01",
        time_interval="daily",
    )

    print("LDAS TEST - multiple variables")
    print(r)

    for key in _NLDAS3_FORCING:
        print(key)
        r = ldas_nldas3_forcing(
            31,
            -100,
            variables=key,
            startDate="2013-06-01T09",
            endDate="2014-07-04T21",
            time_interval="daily",
        )
        print(r)
        if len(r.index) == 0:
            continue
        if r.index[0] != pd.Timestamp("2013-06-01T09", tz="UTC"):
            print(
                f"!!!! {r.index[0]} does not equal {pd.Timestamp('2013-06-01T09', tz='UTC')}"
            )
        if r.index[-1] != pd.Timestamp("2014-07-04T21", tz="UTC"):
            print(
                f"!!!! {r.index[-1]} does not equal {pd.Timestamp('2014-07-04T21', tz='UTC')}"
            )
