"""
ldas                 grid: Land Data Assimilation System, includes all
                     ldas_* (NLDAS, GLDAS2, TRMM, SMERGE, GRACE, MERRA)
ldas_gldas_noah_v2_0 global 0.25deg 1948-2014 3H:GLDAS NOAH hydrology model results
ldas_gldas_noah_v2_1 global 0.25deg 2000- 3H:GLDAS NOAH hydrology model results
ldas_gldas_noah      deprecated alias to ldas_gldas_noah_v2_1
ldas_grace           NAmerica 0.125deg 2002- 7D:Groundwater and soil
                     moisture from GRACE
ldas_merra           global 0.5x0.625deg 1980- H:MERRA-2 Land surface
                     forcings
ldas_nldas_fora      NAmerica 0.125deg 1979- H:NLDAS Weather Forcing A
                     (surface)
ldas_nldas_noah      NAmerica 0.125deg 1979- H:NLDAS NOAH hydrology model
                     results
ldas_nldas_vic       NAmerica 0.125deg 1979- H:NLDAS VIC hydrology model
                     results
ldas_smerge          global 0.125deg 1997- D:SMERGE-Noah-CCI root zone soil
                     moisture
ldas_trmm_tmpa       global 0.25deg 1997- 3H:TRMM (TMPA) rainfall estimate
"""

import datetime
import itertools
import logging
import netrc
import os
import textwrap
from contextlib import suppress
from io import BytesIO

import async_retriever as ar
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth

# from pandas._libs.lib import no_default
from tabulate import tabulate as tb

from tsgettoolbox import utils
from tsgettoolbox.toolbox_utils.src.toolbox_utils import tsutils

__all__ = [
    "ldas",
    "ldas_gldas_noah",  # alias to ldas_gldas_noah_v2_1
    "ldas_gldas_noah_v2_0",
    "ldas_gldas_noah_v2_1",
    "ldas_grace",
    "ldas_merra",
    "ldas_nldas_fora",
    "ldas_nldas_noah",
    "ldas_nldas_vic",
    "ldas_smerge",
]

# fmt: off
_GLDAS_NOAH_v2_0 = {
    "GLDAS_NOAH025_3H_2_0_AvgSurfT_inst": [ "Average surface skin temperature", "K", ],
    "GLDAS_NOAH025_3H_2_0_ESoil_tavg": [ "Direct evaporation from bare soil", "W/m**2", ],
    "GLDAS_NOAH025_3H_2_0_Evap_tavg": ["Evapotranspiration", "mm/s"],
    "GLDAS_NOAH025_3H_2_0_LWdown_f_tavg": [ "Downward long-wave radiation flux", "W/m**2", ],
    "GLDAS_NOAH025_3H_2_0_PotEvap_tavg": [ "Potential evaporation rate", "W/m**2", ],
    "GLDAS_NOAH025_3H_2_0_Psurf_f_inst": ["Surface air pressure", "Pa"],
    "GLDAS_NOAH025_3H_2_0_Qair_f_inst": ["Specific humidity", "kg/kg"],
    "GLDAS_NOAH025_3H_2_0_Qs_acc": ["Storm surface runoff", "mm"],
    "GLDAS_NOAH025_3H_2_0_Qsb_acc": ["Baseflow-groundwater runoff", "mm"],
    "GLDAS_NOAH025_3H_2_0_Qsm_acc": ["Snow melt", "mm"],
    "GLDAS_NOAH025_3H_2_0_Rainf_f_tavg": [ "Total precipitation rate", "mm/s", ],
    "GLDAS_NOAH025_3H_2_0_Rainf_tavg": ["Rain precipitation rate", "mm/s"],
    "GLDAS_NOAH025_3H_2_0_RootMoist_inst": ["Root zone soil moisture", "mm"],
    "GLDAS_NOAH025_3H_2_0_Snowf_tavg": ["Snow precipitation rate", "mm/s"],
    "GLDAS_NOAH025_3H_2_0_SoilMoi0_10cm_inst": [ "Soil moisture content (0-10 cm)", "mm", ],
    "GLDAS_NOAH025_3H_2_0_SoilMoi100_200cm_inst": [ "Soil moisture content (100-200 cm)", "mm", ],
    "GLDAS_NOAH025_3H_2_0_SoilMoi10_40cm_inst": [ "Soil moisture content (10-40 cm)", "mm", ],
    "GLDAS_NOAH025_3H_2_0_SoilMoi40_100cm_inst": [ "Soil moisture content (40-100 cm)", "mm", ],
    "GLDAS_NOAH025_3H_2_0_SoilTMP0_10cm_inst": [ "Soil temperature (0-10 cm)", "K", ],
    "GLDAS_NOAH025_3H_2_0_SoilTMP100_200cm_inst": [ "Soil temperature (100-200 cm)", "K", ],
    "GLDAS_NOAH025_3H_2_0_SoilTMP10_40cm_inst": [ "Soil temperature (10-40 cm)", "K", ],
    "GLDAS_NOAH025_3H_2_0_SWdown_f_tavg": [ "Downward shortwave radiation flux", "W/m**2", ],
    "GLDAS_NOAH025_3H_2_0_Tair_f_inst": ["Near surface air temperature", "K"],
    "GLDAS_NOAH025_3H_2_0_Wind_f_inst": ["Near surface wind speed", "m/s"],
}

_GLDAS_NOAH_v2_1 = {
    "GLDAS_NOAH025_3H_2_1_AvgSurfT_inst": [ "Average surface skin temperature", "K", ],
    "GLDAS_NOAH025_3H_2_1_ESoil_tavg": ["Soil evaporation", "mm/s"],
    "GLDAS_NOAH025_3H_2_1_Evap_tavg": ["Evapotranspiration", "mm/s"],
    "GLDAS_NOAH025_3H_2_1_LWdown_f_tavg": [ "Downward long-wave radiation flux", "W/m**2", ],
    "GLDAS_NOAH025_3H_2_1_PotEvap_tavg": ["Potential evaporation", "mm/s"],
    "GLDAS_NOAH025_3H_2_1_Psurf_f_inst": ["Surface air pressure", "Pa"],
    "GLDAS_NOAH025_3H_2_1_Qair_f_inst": ["Specific humidity", "kg/kg"],
    "GLDAS_NOAH025_3H_2_1_Qs_acc": ["Storm surface runoff", "mm"],
    "GLDAS_NOAH025_3H_2_1_Qsb_acc": ["Baseflow-groundwater runoff", "mm"],
    "GLDAS_NOAH025_3H_2_1_Qsm_acc": ["Snow melt", "mm"],
    "GLDAS_NOAH025_3H_2_1_Rainf_f_tavg": [ "Total precipitation rate", "mm/s", ],
    "GLDAS_NOAH025_3H_2_1_Rainf_tavg": ["Rain precipitation rate", "mm/s"],
    "GLDAS_NOAH025_3H_2_1_RootMoist_inst": ["Root zone soil moisture", "mm"],
    "GLDAS_NOAH025_3H_2_1_Snowf_tavg": ["Snow precipitation rate", "mm/s"],
    "GLDAS_NOAH025_3H_2_1_SoilMoi0_10cm_inst": [ "Soil moisture content (0-10 cm)", "mm", ],
    "GLDAS_NOAH025_3H_2_1_SoilMoi100_200cm_inst": [ "Soil moisture content (100-200 cm)", "mm", ],
    "GLDAS_NOAH025_3H_2_1_SoilMoi10_40cm_inst": [ "Soil moisture content (10-40 cm)", "mm", ],
    "GLDAS_NOAH025_3H_2_1_SoilMoi40_100cm_inst": [ "Soil moisture content (40-100 cm)", "mm", ],
    "GLDAS_NOAH025_3H_2_1_SoilTMP0_10cm_inst": [ "Soil temperature (0-10 cm)", "K", ],
    "GLDAS_NOAH025_3H_2_1_SoilTMP100_200cm_inst": [ "Soil temperature (100-200 cm)", "K", ],
    "GLDAS_NOAH025_3H_2_1_SoilTMP10_40cm_inst": [ "Soil temperature (10-40 cm)", "K", ],
    "GLDAS_NOAH025_3H_2_1_SWdown_f_tavg": [ "Downward shortwave radiation flux", "W/m**2", ],
    "GLDAS_NOAH025_3H_2_1_Tair_f_inst": ["Near surface air temperature", "K"],
    "GLDAS_NOAH025_3H_2_1_Wind_f_inst": ["Near surface wind speed", "m/s"],
}

_GRACE = {
    "GRACEDADM_CLSM0125US_7D_4_0_gws_inst": [ "Groundwater storage percentile", "percent", ],
    "GRACEDADM_CLSM0125US_7D_4_0_rtzsm_inst": [ "Root zone soil moisture percentile", "percent", ],
    "GRACEDADM_CLSM0125US_7D_4_0_sfsm_inst": [ "Surface soil moisture percentile", "percent", ],
}

_MERRA = {
    "M2I1NXLFO_5_12_4_QLML": ["Surface specific humidity:instant", "1"],
    "M2I1NXLFO_5_12_4_SPEEDLML": ["Surface wind speed:instant", "m/s"],
    "M2I1NXLFO_5_12_4_TLML": [ "Surface air temperature over land:instant", "K", ],
    "M2T1NXFLX_5_12_4_ULML": ["Surface eastward wind:average", "m/s"],
    "M2T1NXFLX_5_12_4_VLML": ["Surface northward wind:average", "m/s"],
    "M2T1NXLFO_5_12_4_LWGAB": [ "Surface absorbed longwave radiation:average", "W/m**2", ],
    "M2T1NXLFO_5_12_4_SWGDN": [ "Incident shortwave radiation land:average", "W/m**2", ],
    "M2T1NXSLV_5_12_4_U50M": [ "50-meter eastward wind:time average", "m/s", ],
    "M2T1NXSLV_5_12_4_V50M": [ "50-meter northward wind:time average", "m/s", ],
}

_NLDAS_FORA = {
    "NLDAS_FORA0125_H_2_0_LWdown": [ "Surface DW longwave radiation flux", "W/m**2", ],
    "NLDAS_FORA0125_H_2_0_PotEvap": ["Potential evaporation", "mm"],
    "NLDAS_FORA0125_H_2_0_PSurf": ["Surface pressure", "Pa"],
    "NLDAS_FORA0125_H_2_0_Qair": [ "2-m above ground specific humidity", "kg/kg", ],
    "NLDAS_FORA0125_H_2_0_Rainf": ["Precipitation hourly total", "mm"],
    "NLDAS_FORA0125_H_2_0_SWdown": [ "Surface DW shortwave radiation flux", "W/m**2", ],
    "NLDAS_FORA0125_H_2_0_Tair": ["2-m above ground temperature", "K"],
    "NLDAS_FORA0125_H_2_0_Wind_E": ["10-m above ground zonal wind", "m/s"],
    "NLDAS_FORA0125_H_2_0_Wind_N": ["10-m above ground meridional wind", "m/s"],
}

_NLDAS_MOSAIC = {
    "NLDAS_MOS0125_H_2_0_Evap": ["Total evapotranspiration", "mm"],
    "NLDAS_MOS0125_H_2_0_Qg": ["Ground heat flux", "W/m**2"],
    "NLDAS_MOS0125_H_2_0_Qle": ["Latent heat flux", "W/m**2"],
    "NLDAS_MOS0125_H_2_0_Qh": ["Sensible heat flux", "W/m**2"],
    "NLDAS_MOS0125_H_2_0_Qs": [ "Surface runoff (non-infiltrating)", "mm", ],
    "NLDAS_MOS0125_H_2_0_Qsb": ["Subsurface runoff (baseflow)", "mm"],
    "NLDAS_MOS0125_H_2_0_SoilM_0_10cm": [ "0-10 cm soil moisture content", "mm", ],
    "NLDAS_MOS0125_H_2_0_SoilM_0_100cm": [ "0-100 cm soil moisture content", "mm", ],
    "NLDAS_MOS0125_H_2_0_SoilM_0_200cm": [ "0-200 cm soil moisture content", "mm", ],
    "NLDAS_MOS0125_H_2_0_SoilM_10_40cm": [ "10-40 cm soil moisture content", "mm", ],
    "NLDAS_MOS0125_H_2_0_SoilM_40_200cm": [ "40-200 cm soil moisture content", "mm", ],
    "NLDAS_MOS0125_H_2_0_SoilT": ["Soil temperature", "K"],
}

_NLDAS_NOAH = {
    "NLDAS_NOAH0125_H_2_0_Evap": ["Total evapotranspiration", "mm"],
    "NLDAS_NOAH0125_H_2_0_LWdown": [ "Surface DW longwave radiation flux", "W/m**2", ],
    "NLDAS_NOAH0125_H_2_0_Qg": ["Ground heat flux", "W/m**2"],
    "NLDAS_NOAH0125_H_2_0_Qh": ["Sensible heat flux", "W/m**2"],
    "NLDAS_NOAH0125_H_2_0_Qle": ["Latent heat flux", "W/m**2"],
    "NLDAS_NOAH0125_H_2_0_Qsb": ["Subsurface runoff (baseflow)", "mm"],
    "NLDAS_NOAH0125_H_2_0_Qs": [ "Surface runoff (non-infiltrating)", "mm", ],
    "NLDAS_NOAH0125_H_2_0_SoilM_0_100cm": [ "0-100 cm soil moisture content", "mm", ],
    "NLDAS_NOAH0125_H_2_0_SoilM_0_10cm": [ "0-10 cm soil moisture content", "mm", ],
    "NLDAS_NOAH0125_H_2_0_SoilM_0_200cm": [ "0-200 cm soil moisture content", "mm", ],
    "NLDAS_NOAH0125_H_2_0_SoilM_100_200cm": [ "100-200 cm soil moisture content", "mm", ],
    "NLDAS_NOAH0125_H_2_0_SoilM_10_40cm": [ "10-40 cm soil moisture content", "mm", ],
    "NLDAS_NOAH0125_H_2_0_SoilM_40_100cm": [ "40-100 cm soil moisture content", "mm", ],
    "NLDAS_NOAH0125_H_2_0_SoilT_0_10cm": ["0-10 cm soil temperature", "K"],
    "NLDAS_NOAH0125_H_2_0_SoilT_100_200cm": [ "100-200 cm soil temperature", "K", ],
    "NLDAS_NOAH0125_H_2_0_SoilT_10_40cm": ["10-40 cm soil temperature", "K"],
    "NLDAS_NOAH0125_H_2_0_SoilT_40_100cm": ["40-100 cm soil temperature", "K"],
    "NLDAS_NOAH0125_H_2_0_SWdown": [ "Surface DW shortwave radiation flux", "W/m**2", ],
}


_NLDAS_VIC = {
    "NLDAS_VIC0125_H_2_0_Evap": ["Total evapotranspiration", "mm"],
    "NLDAS_VIC0125_H_2_0_Qg": ["Ground heat flux", "W/m**2"],
    "NLDAS_VIC0125_H_2_0_Qh": ["Sensible heat flux", "W/m**2"],
    "NLDAS_VIC0125_H_2_0_Qle": ["Latent heat flux", "W/m**2"],
    "NLDAS_VIC0125_H_2_0_Qsb": ["Subsurface runoff (baseflow)", "mm"],
    "NLDAS_VIC0125_H_2_0_Qs": [ "Surface runoff (non-infiltrating)", "mm", ],
    "NLDAS_VIC0125_H_2_0_SoilM_0_100cm": [ "0-100 cm soil moisture content", "mm", ],
    "NLDAS_VIC0125_H_2_0_SoilM_layer1": [ "VIC layer 1 soil moisture content", "mm", ],
    "NLDAS_VIC0125_H_2_0_SoilM_layer2": [ "VIC layer 2 soil moisture content", "mm", ],
    "NLDAS_VIC0125_H_2_0_SoilM_layer3": [ "VIC layer 3 soil moisture content", "mm", ],
    "NLDAS_VIC0125_H_2_0_SoilM_total": [ "VIC total column depth soil moisture content", "mm", ],
    "NLDAS_VIC0125_H_2_0_SoilT_layer1": ["VIC layer 1 soil temperature", "K"],
    "NLDAS_VIC0125_H_2_0_SoilT_layer2": ["VIC layer 3 soil temperature", "K"],
    "NLDAS_VIC0125_H_2_0_SoilT_layer3": ["VIC layer 3 soil temperature", "K"],
}


_SMERGE = {
    "SMERGE_RZSM0_40CM_2_0_CCI_ano": [ "CCI soil moisture anomalies 0-40 cm", "m3/m3", ],
    "SMERGE_RZSM0_40CM_2_0_RZSM": [ "Average soil moisture of 0-40 cm layer", "m3/m3", ],
}
# fmt: on


_UNITS_MAP = {}
_UNITS_MAP.update(_GLDAS_NOAH_v2_0)
_UNITS_MAP.update(_GLDAS_NOAH_v2_1)
_UNITS_MAP.update(_GRACE)
_UNITS_MAP.update(_MERRA)
_UNITS_MAP.update(_NLDAS_FORA)
_UNITS_MAP.update(_NLDAS_MOSAIC)
_UNITS_MAP.update(_NLDAS_NOAH)
_UNITS_MAP.update(_NLDAS_VIC)
_UNITS_MAP.update(_SMERGE)
# _UNITS_MAP.update(_MERRA_UPDATE)

_varmap = {
    "GLDAS": "GLDAS2",
    "GRACEDADM": "GRACE",
    "M2I1NXLFO": "MERRA",
    "M2T1NXFLX": "MERRA",
    "M2T1NXLFO": "MERRA",
    "M2T1NXSLV": "MERRA",
    "NLDAS": "NLDAS2",
    "SMERGE": "SMERGE",
}

_project_start_dates = {
    "GLDAS2_v2_0": "1948-01-01T00",
    "GLDAS2_v2_1": "2000-01-01T00",
    "GRACE": "2002-10-04T00",
    "MERRA": "1980-01-01T00",
    "NLDAS": "1979-01-01T13",
    "NLDAS2": "1979-01-01T13",
    "SMERGE": "1997-01-02T00",
}

_project_sep = {
    "GLDAS2_v2_0": ",",
    "GLDAS2_v2_1": ",",
    "GRACE": ",",
    "MERRA": ",",
    "NLDAS2": ",",
    "NLDAS": ",",
    "SMERGE": ",",
}

_project_header = {
    "GLDAS2_v2_0": None,
    "GLDAS2_v2_1": None,
    "GRACE": None,
    "MERRA": None,
    "NLDAS2": None,
    "NLDAS": None,
    "SMERGE": None,
}

_project_skiprows = {
    "GLDAS2_v2_0": 16,
    "GLDAS2_v2_1": 16,
    "GRACE": 16,
    "MERRA": 16,
    "NLDAS2": 16,
    "NLDAS": 16,
    "SMERGE": 16,
}

_project_index_col = {
    "GLDAS2_v2_0": 0,
    "GLDAS2_v2_1": 0,
    "GRACE": "Datetime",
    "MERRA": "Datetime",
    "NLDAS2": 0,
    "NLDAS": 0,
    "SMERGE": "Datetime",
}

_project_version = {
    "GLDAS2_v2_0": "2.0",
    "GLDAS2_v2_1": "2.1",
    "GRACE": "4.0",
    "MERRA": "5.12.4",
    "NLDAS": "2.0",
    "NLDAS2": "2.0",
    "SMERGE": "2.0",
}


def make_units_table(units_dict):
    """Make a table of units for each variable."""
    new_units_table = [
        [
            f"{key}\n{val[0]}",
            f"{val[1]}",
        ]
        for key, val in units_dict.items()
    ]

    units_table = tb(
        new_units_table,
        tablefmt="grid",
        headers=['LDAS "variables" string Description', "Units"],
    )

    return textwrap.indent(units_table.strip(), "            ")


def foundation_api(
    cli_name,
    units_table="",
    first_line="",
    meta_table="",
):
    """Create a foundation API function returning a function."""

    @tsutils.doc(
        {"units_table": units_table, "first_line": first_line, "meta_table": meta_table}
    )
    def ldas_api(
        lat=None,
        lon=None,
        variables=None,
        startDate=None,
        endDate=None,
        variable=None,
    ):
        # fmt: off
        """
        ${first_line}

        This will download data from a set of water cycle related variables
        (Table 1) from the North American and Global Land Data Assimilation
        Systems (NLDAS and GLDAS, respectively), the Land Parameter Parameter
        Model (LPRM), the Tropical Rainfall Measuring Mission (TRMM), and
        Gravity Recovery and Climate Experiment (GRACE) data assimilation. In
        addition to their access provided by the hydrology community tools,
        selected data rods variables can be searched and accessed through the
        GES DISC search and access user interface, and all data rods variables
        can be accessed via Web services developed by the GES DISC.

        The time zone is always UTC.

        ${meta_table}

        Parameters
        ----------
        lat : float
            Latitude (required): Enter single geographic point by
            latitude.

            Example: --lat=43.1

        lon : float
            Longitude (required): Enter single geographic point by
            longitude.

            Example: --lon=-85.3

        variables : str
            Use the variable codes from the following table:

${units_table}

        startDate : str
            The start date of the time series.::

                Example: --startDate=2001-01-01T05

            If startDate and endDate are None, returns the entire series.
        endDate : str
            The end date of the time series.::

                Example: --endDate=2002-01-05T05

            If startDate and endDate are None, returns the entire series.
        variable : str
            DEPRECATED: use "variables" instead to be consistent across
            "tsgettoolbox"."""
        # fmt: on
        return base_ldas(
            lat,
            lon,
            variables=variables,
            startDate=startDate,
            endDate=endDate,
            variable=variable,
        )

    return ldas_api


_META_HEADER = r"""

        +-------------------------------+-------------+---------------+
        | Description/Name              | Spatial     | Time          |
        +===============================+=============+===============+"""

_GLDAS_NOAH_v2_0_META = r"""
        | GLDAS Noah Land Surface Model | 0.25x0.25   | 3 hour        |
        | GLDAS_NOAH025_3H              | degree      |               |
        | V2.0                          |             |               |
        |                               | -180,-60 to | 1948-01-01 to |
        |                               |  180, 90    | 2014-12-31    |
        +-------------------------------+-------------+---------------+"""
_GLDAS_NOAH_v2_1_META = r"""
        | GLDAS Noah Land Surface Model | 0.25x0.25   | 3 hour        |
        | GLDAS_NOAH025_3H              | degree      |               |
        | V2.1                          |             |               |
        |                               | -180,-60 to | 2000-01-01 to |
        |                               |  180, 90    | recent        |
        +-------------------------------+-------------+---------------+"""
_GRACE_META = r"""
        | Groundwater and Soil Moisture | 0.125x0.125 | 7 day         |
        | Conditions from GRACE         | degree      |               |
        | Data Assimilation             |             |               |
        | GRACEDADM_CLSM0125US_7D       | -125, 25 to | 2002-10-04 to |
        | V4.0                          |  -67, 53    | recent        |
        +-------------------------------+-------------+---------------+"""
_MERRA_META = r"""
        | MERRA-2 2D, Instantaneous,    | 0.5x0.625   | 1 hour        |
        | Land Surface Forcings         | degree      |               |
        | M2I1NXLFO                     |             |               |
        | V5.12.4                       | -180,-90 to | 1980-01-01 to |
        |                               |  180, 90    | recent        |
        +-------------------------------+-------------+---------------+
        | MERRA-2 2D, Time-averaged,    | 0.5x0.625   | 1 hour        |
        | Surface Flux Diagnostics      | degree      |               |
        | M2T1NXFLX                     |             |               |
        | V5.12.4                       | -180,-90 to | 1980-01-01 to |
        |                               |  180, 90    | recent        |
        +-------------------------------+-------------+---------------+
        | MERRA-2 2D, Time-averaged,    | 0.5x0.625   | 1 hour        |
        | Land Surface Forcings         | degree      |               |
        | M2T1NXLFO                     |             |               |
        | V5.12.4                       | -180,-90 to | 1980-01-01 to |
        |                               |  180, 90    | recent        |
        +-------------------------------+-------------+---------------+"""
_NLDAS_FORA_META = r"""
        | NLDAS Primary Forcing Data    | 0.125x0.125 | 1 hour        |
        | NLDAS_FORA0125_H              | degree      |               |
        | V2.0                          |             |               |
        |                               | -125,25 to  | 1979-01-01T13 |
        |                               |  -67,53     | til recent    |
        +-------------------------------+-------------+---------------+"""
_NLDAS_NOAH_META = r"""
        | NLDAS Noah Land Surface Model | 0.125x0.125 | 1 hour        |
        | NLDAS_NOAH0125_H              | degree      |               |
        | V002                          |             |               |
        |                               | -125,25 to  | 1979-01-01T13 |
        |                               |  -67,53     | til recent    |
        +-------------------------------+-------------+---------------+"""
_NLDAS_VIC_META = r"""
        | NLDAS VIC Land Surface Model  | 0.125x0.125 | 1 hour        |
        | NLDAS_VIC0125_H               | degree      |               |
        | V002                          |             |               |
        |                               | -125,25 to  | 1979-01-01T13 |
        |                               |  -67,53     | til recent    |
        +-------------------------------+-------------+---------------+"""
_SMERGE_META = r"""
        | Smerge-Noah-CCI root zone     | 0.125x0.125 | 1 day         |
        | soil moisture 0-40 cm         | degree      |               |
        | SMERGE_RZSM0_40CM             |             |               |
        | V2.0                          | -125, 25 to | 1979-01-02 to |
        |                               |  -67, 53    | recent        |
        +-------------------------------+-------------+---------------+"""

GLDAS_NOAH_v2_0_FIRST_LINE = (
    "global:0.25deg:1948-2014:3H:GLDAS NOAH hydrology model results"
)
GLDAS_NOAH_v2_1_FIRST_LINE = (
    "global:0.25deg:2000-:3H:GLDAS NOAH hydrology model results"
)
GRACE_FIRST_LINE = "NAmerica:0.125deg:2002-:7D:Groundwater and soil moisture from GRACE"
LDAS_FIRST_LINE = "global:grid:::Land Data Assimilation System, includes all ldas_* (NLDAS, GLDAS2, TRMM, SMERGE, GRACE, MERRA)"
MERRA_FIRST_LINE = "global:0.5x0.625deg:1980-:H:MERRA-2 Land surface forcings"
NLDAS_FORA_FIRST_LINE = "NAmerica:0.125deg:1979-:H:NLDAS Weather Forcing A (surface)"
NLDAS_NOAH_FIRST_LINE = "NAmerica:0.125deg:1979-:H:NLDAS NOAH hydrology model results"
NLDAS_VIC_FIRST_LINE = "NAmerica:0.125deg:1979-:H:NLDAS VIC hydrology model results"
SMERGE_FIRST_LINE = "global:0.125deg:1997-:D:SMERGE-Noah-CCI root zone soil moisture"

ldas = foundation_api(
    "ldas",
    units_table=make_units_table(_UNITS_MAP),
    first_line=LDAS_FIRST_LINE,
    meta_table="".join(
        [
            _META_HEADER,
            _GLDAS_NOAH_v2_0_META,
            _GLDAS_NOAH_v2_1_META,
            _GRACE_META,
            _MERRA_META,
            _NLDAS_FORA_META,
            _NLDAS_NOAH_META,
            _SMERGE_META,
        ]
    )
    + "\n",
)

ldas_gldas_noah_v2_0 = foundation_api(
    "ldas_gldas_noah_v2_0",
    units_table=make_units_table(_GLDAS_NOAH_v2_0),
    first_line=GLDAS_NOAH_v2_0_FIRST_LINE,
    meta_table=_META_HEADER + _GLDAS_NOAH_v2_0_META + "\n",
)

ldas_gldas_noah_v2_1 = foundation_api(
    "ldas_gldas_noah_v2_1",
    units_table=make_units_table(_GLDAS_NOAH_v2_1),
    first_line=GLDAS_NOAH_v2_1_FIRST_LINE,
    meta_table=_META_HEADER + _GLDAS_NOAH_v2_1_META + "\n",
)

ldas_gldas_noah = foundation_api(
    "ldas_gldas_noah",
    units_table=make_units_table(_GLDAS_NOAH_v2_1),
    first_line=GLDAS_NOAH_v2_1_FIRST_LINE,
    meta_table=_META_HEADER + _GLDAS_NOAH_v2_1_META + "\n",
)

ldas_grace = foundation_api(
    "ldas_grace",
    units_table=make_units_table(_GRACE),
    first_line=GRACE_FIRST_LINE,
    meta_table=_META_HEADER + _GRACE_META + "\n",
)

ldas_merra = foundation_api(
    "ldas_merra",
    units_table=make_units_table(_MERRA),
    first_line=MERRA_FIRST_LINE,
    meta_table=_META_HEADER + _MERRA_META + "\n",
)

ldas_nldas_fora = foundation_api(
    "ldas_nldas_fora",
    units_table=make_units_table(_NLDAS_FORA),
    first_line=NLDAS_FORA_FIRST_LINE,
    meta_table=_META_HEADER + _NLDAS_FORA_META + "\n",
)

ldas_nldas_noah = foundation_api(
    "ldas_nldas_noah",
    units_table=make_units_table(_NLDAS_NOAH),
    first_line=NLDAS_NOAH_FIRST_LINE,
    meta_table=_META_HEADER + _NLDAS_NOAH_META + "\n",
)

ldas_nldas_vic = foundation_api(
    "ldas_nldas_vic",
    units_table=make_units_table(_NLDAS_VIC),
    first_line=NLDAS_VIC_FIRST_LINE,
    meta_table=_META_HEADER + _NLDAS_VIC_META + "\n",
)

ldas_smerge = foundation_api(
    "ldas_smerge",
    units_table=make_units_table(_SMERGE),
    first_line=SMERGE_FIRST_LINE,
    meta_table=_META_HEADER + _SMERGE_META + "\n",
)


@tsutils.transform_args(variables=tsutils.make_list, variable=tsutils.make_list)
def base_ldas(
    lat,
    lon,
    variables=None,
    startDate=None,
    endDate=None,
    variable=None,
):
    r"""Download data from NLDAS or GLDAS."""
    if variable is not None:
        raise ValueError(
            tsutils.error_wrapper(
                """
                The 'variable' keyword is deprecated. Please use 'variables'
                instead to be consistent with other services in
                tsgettoolbox.
                """
            )
        )

    location = f"[{lat}, {lon}]"

    signin_url = "https://api.giovanni.earthdata.nasa.gov/signin"

    # This will make sure the .netrc file has an entry for
    # urs.earthdata.nasa.gov and if not, will prompt for user
    # credentials and create the .netrc file (if necessary) and populate with
    # the urs.earthdata.nasa.gov entry.
    _ = utils.read_netrc("urs.earthdata.nasa.gov")

    # This gets the token for Earthdata login authentication from the .netrc
    # file.
    token = requests.get(
        signin_url,
        auth=HTTPBasicAuth(
            netrc.netrc().hosts["urs.earthdata.nasa.gov"][0],
            netrc.netrc().hosts["urs.earthdata.nasa.gov"][2],
        ),
        allow_redirects=True,
    ).text.replace('"', "")

    time_series_url = "https://api.giovanni.earthdata.nasa.gov/timeseries"

    ndf = pd.DataFrame()
    nvariables = []
    for var in variables:
        words = var.split(":")
        project = words[0]
        if len(words) == 1:
            # New style where can leave off first ":" separated field.
            project = _varmap[words[0].split("_")[0]]
        if project == "GLDAS2":
            project = "GLDAS2_v2_0" if "_2_0_" in words[-1] else "GLDAS2_v2_1"
        nvariables.append(words[-1])

    if startDate is None:
        startDate = tsutils.parsedate(_project_start_dates[project])
    else:
        with suppress(TypeError):
            startDate = tsutils.parsedate(startDate)
            if startDate < tsutils.parsedate(_project_start_dates[project]):
                startDate = tsutils.parsedate(_project_start_dates[project])
    if endDate is None:
        endDate = tsutils.parsedate(
            (datetime.datetime.now() - datetime.timedelta(days=60)).strftime(
                "%Y-%m-%dT%H"
            )
        )
    else:
        endDate = tsutils.parsedate(endDate)

    periods = []
    delta = datetime.timedelta(days=10000)
    period_start = startDate
    while period_start < endDate:
        period_end = min(period_start + delta, endDate)
        periods.append((period_start, period_end))
        period_start = period_end

    urls, kwds = zip(
        *[
            (
                time_series_url,
                {
                    "params": {
                        "location": location,
                        "data": v,
                        "time": f"{s.strftime('%Y-%m-%dT%H:%M:%S')}/{e.strftime('%Y-%m-%dT%H:%M:%S')}",
                    },
                    "headers": {"authorizationtoken": token},
                },
            )
            for (s, e), v in itertools.product(periods, nvariables)
        ]
    )

    if os.path.exists("debug_tsgettoolbox"):
        logging.warning(f"{urls}, {kwds}")
    resp = ar.retrieve_binary(urls, kwds)

    ndf = pd.DataFrame()
    for response, keyword in zip(resp, kwds):
        names = [
            "Datetime",
            f"{keyword['params']['data'].split(':')[-1]}:{_UNITS_MAP[keyword['params']['data']][1]}",
        ]
        df = pd.read_csv(
            BytesIO(response),
            sep=_project_sep[project],
            header=_project_header[project],
            skiprows=_project_skiprows[project],
            names=names,
            index_col=_project_index_col[project],
            na_values=[-9999, -9999.0, 9999.9],
        )
        df.index = pd.to_datetime(df.index)

        df.index.name = "Datetime:UTC"
        with suppress(TypeError):
            df = df.tz_localize("UTC")
        ndf = ndf.combine_first(df)

    return ndf


if __name__ == "__main__":
    # for key in _UNITS_MAP:
    #     print("LDAS", key)
    #     r = ldas(
    #         31,
    #         -100,
    #         variables=key,
    #         startDate="2013-06-01T09",
    #         endDate="2014-05-04T21",
    #     )
    #     print(r)
    #     time.sleep(20)
    #     r = ldas(
    #         31,
    #         -100,
    #         variables=key[key.index(":") + 1 :],
    #         startDate="2013-06-01T09",
    #         endDate="2014-05-04T21",
    #     )
    #     print(r)
    #     time.sleep(20)
    r = ldas(
        34,
        100,
        variables="GLDAS_NOAH025_3H_2_1_SoilMoi10_40cm_inst",
        startDate="2001-01-01T00",
        endDate="2001-02-02T00",
    )

    print("LDAS TEST")
    print(r)

    r = ldas(
        34,
        100,
        variables="GLDAS_NOAH025_3H_2_1_SoilMoi10_40cm_inst",
        endDate="2001-01-01",
    )

    print("LDAS TEST")
    print(r)

    for key in _NLDAS_FORA:
        print(key)
        r = ldas_nldas_fora(
            31,
            -100,
            variables=key,
            startDate="2013-06-01T09",
            endDate="2014-07-04T21",
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

    r = ldas(
        30,
        100,
        variables="GLDAS_NOAH025_3H_2_1_SoilMoi10_40cm_inst",
        startDate="2016-01-01T00",
        endDate="2016-12-01T00",
    )

    print("LDAS TEST")
    print(r)

    r = ldas(
        34,
        100,
        variables="GLDAS_NOAH025_3H_2_1_SoilMoi10_40cm_inst",
        startDate="5 years ago",
        endDate="4 years ago",
    )

    print("LDAS TEST")
    print(r)

    r = ldas(
        34,
        100,
        variables=[
            "GLDAS_NOAH025_3H_2_1_SoilMoi10_40cm_inst",
            "GLDAS_NOAH025_3H_2_1_Evap_tavg",
        ],
        startDate="5 years ago",
        endDate="4 years ago",
    )
    print(r)
