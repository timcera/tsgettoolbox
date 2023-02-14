"""
ldas                grid: Land Data Assimilation System, includes all
                    ldas_* (NLDAS, GLDAS2, TRMM, SMERGE, GRACE, MERRA)
ldas_gldas_noah     global 0.25deg 2000- 3H:GLDAS NOAH hydrology model results
ldas_grace          NAmerica 0.125deg 2002- 7D:Groundwater and soil
                    moisture from GRACE
ldas_merra          global 0.5x0.625deg 1980- H:MERRA-2 Land surface
                    forcings
ldas_merra_update   global 0.5x0.667deg 1980-2016 H:MERRA-2 Analysis
                    update
ldas_nldas_fora     NAmerica 0.125deg 1979- H:NLDAS Weather Forcing A
                    (surface)
ldas_nldas_noah     NAmerica 0.125deg 1979- H:NLDAS NOAH hydrology model
                    results
ldas_smerge         global 0.125deg 1997- D:SMERGE-Noah-CCI root zone soil
                    moisture
ldas_trmm_tmpa      global 0.25deg 1997- 3H:TRMM (TMPA) rainfall estimate
"""

import datetime
import itertools
import logging
import os
import textwrap
from contextlib import suppress
from io import BytesIO

import async_retriever as ar
import cltoolbox
import pandas as pd
from cltoolbox.rst_text_formatter import RSTHelpFormatter as HelpFormatter
from pandas._libs.lib import no_default
from tabulate import tabulate as tb
from toolbox_utils import tsutils

__all__ = [
    "ldas",
    "ldas_gldas_noah",
    "ldas_grace",
    "ldas_merra",
    "ldas_merra_update",
    "ldas_nldas_fora",
    "ldas_nldas_noah",
    "ldas_smerge",
    "ldas_trmm_tmpa",
]

_NLDAS_FORA = {
    "NLDAS:NLDAS_FORA0125_H.002:APCPsfc": ["Precipitation hourly total", "mm"],
    "NLDAS:NLDAS_FORA0125_H.002:DLWRFsfc": [
        "Surface DW longwave radiation flux",
        "W/m**2",
    ],
    "NLDAS:NLDAS_FORA0125_H.002:DSWRFsfc": [
        "Surface DW shortwave radiation flux",
        "W/m**2",
    ],
    "NLDAS:NLDAS_FORA0125_H.002:PEVAPsfc": ["Potential evaporation", "mm"],
    "NLDAS:NLDAS_FORA0125_H.002:SPFH2m": [
        "2-m above ground specific humidity",
        "kg/kg",
    ],
    "NLDAS:NLDAS_FORA0125_H.002:TMP2m": ["2-m above ground temperature", "K"],
    "NLDAS:NLDAS_FORA0125_H.002:UGRD10m": ["10-m above ground zonal wind", "m/s"],
    "NLDAS:NLDAS_FORA0125_H.002:VGRD10m": ["10-m above ground meridional wind", "m/s"],
}
_NLDAS_NOAH = {
    "NLDAS:NLDAS_NOAH0125_H.002:EVPsfc": ["Total evapotranspiration", "mm"],
    "NLDAS:NLDAS_NOAH0125_H.002:GFLUXsfc": ["Ground heat flux", "W/m**2"],
    "NLDAS:NLDAS_NOAH0125_H.002:LHTFLsfc": ["Latent heat flux", "W/m**2"],
    "NLDAS:NLDAS_NOAH0125_H.002:SHTFLsfc": ["Sensible heat flux", "W/m**2"],
    "NLDAS:NLDAS_NOAH0125_H.002:SSRUNsfc": [
        "Surface runoff (non-infiltrating)",
        "mm",
    ],
    "NLDAS:NLDAS_NOAH0125_H.002:BGRUNsfc": ["Subsurface runoff (baseflow)", "mm"],
    "NLDAS:NLDAS_NOAH0125_H.002:SOILM0-10cm": [
        "0-10 cm soil moisture content",
        "mm",
    ],
    "NLDAS:NLDAS_NOAH0125_H.002:SOILM0-100cm": [
        "0-100 cm soil moisture content",
        "mm",
    ],
    "NLDAS:NLDAS_NOAH0125_H.002:SOILM0-200cm": [
        "0-200 cm soil moisture content",
        "mm",
    ],
    "NLDAS:NLDAS_NOAH0125_H.002:SOILM10-40cm": [
        "10-40 cm soil moisture content",
        "mm",
    ],
    "NLDAS:NLDAS_NOAH0125_H.002:SOILM40-100cm": [
        "40-100 cm soil moisture content",
        "mm",
    ],
    "NLDAS:NLDAS_NOAH0125_H.002:SOILM100-200cm": [
        "100-200 cm soil moisture content",
        "mm",
    ],
    "NLDAS:NLDAS_NOAH0125_H.002:TSOIL0-10cm": ["0-10 cm soil temperature", "K"],
}
_GLDAS_NOAH = {
    "GLDAS2:GLDAS_NOAH025_3H_v2.1:AvgSurfT_inst": [
        "Average surface skin temperature",
        "K",
    ],
    "GLDAS2:GLDAS_NOAH025_3H_v2.1:Evap_tavg": ["Evapotranspiration", "mm/s"],
    "GLDAS2:GLDAS_NOAH025_3H_v2.1:Psurf_f_inst": ["Surface air pressure", "Pa"],
    "GLDAS2:GLDAS_NOAH025_3H_v2.1:Qair_f_inst": ["Specific humidity", "kg/kg"],
    "GLDAS2:GLDAS_NOAH025_3H_v2.1:Qs_acc": ["Storm surface runoff", "mm"],
    "GLDAS2:GLDAS_NOAH025_3H_v2.1:Qsb_acc": ["Baseflow-groundwater runoff", "mm"],
    "GLDAS2:GLDAS_NOAH025_3H_v2.1:Rainf_f_tavg": [
        "Total precipitation rate",
        "mm/s",
    ],
    "GLDAS2:GLDAS_NOAH025_3H_v2.1:Rainf_tavg": ["Rain precipitation rate", "mm/s"],
    "GLDAS2:GLDAS_NOAH025_3H_v2.1:Snowf_tavg": ["Snow precipitation rate", "mm/s"],
    "GLDAS2:GLDAS_NOAH025_3H_v2.1:SoilMoi0_10cm_inst": [
        "Soil moisture content (0-10 cm)",
        "mm",
    ],
    "GLDAS2:GLDAS_NOAH025_3H_v2.1:SoilMoi10_40cm_inst": [
        "Soil moisture content (10-40 cm)",
        "mm",
    ],
    "GLDAS2:GLDAS_NOAH025_3H_v2.1:SoilMoi40_100cm_inst": [
        "Soil moisture content (40-100 cm)",
        "mm",
    ],
    "GLDAS2:GLDAS_NOAH025_3H_v2.1:SoilTMP0_10cm_inst": [
        "Soil temperature (0-10 cm)",
        "K",
    ],
    "GLDAS2:GLDAS_NOAH025_3H_v2.1:Tair_f_inst": ["Near surface air temperature", "K"],
    "GLDAS2:GLDAS_NOAH025_3H_v2.1:Wind_f_inst": ["Near surface wind speed", "m/s"],
}
# # Commented out because currently has issues starting in 2020-08-17.
# _LPRM_AMSRE_SURFACE = {
#     "LPRM:LPRM_AMSRE_D_SOILM3.002:opt_depth_c": [
#         "Optical depth from LPRM AMSRE C-band descending",
#         "unitless",
#     ],
#     "LPRM:LPRM_AMSRE_D_SOILM3.002:opt_depth_x": [
#         "Optical depth from LPRM AMSRE X-band descending",
#         "unitless",
#     ],
#     "LPRM:LPRM_AMSRE_D_SOILM3.002:sm_c_error": [
#         "Soil moisture uncertainty of LPRM AMSRE C-band descending",
#         "percent",
#     ],
#     "LPRM:LPRM_AMSRE_D_SOILM3.002:sm_x_error": [
#         "Soil moisture uncertainty of LPRM AMSRE X-band descending",
#         "percent",
#     ],
#     "LPRM:LPRM_AMSRE_D_SOILM3.002:soil_moisture_c": [
#         "Soil moisture, volumetric, from LPRM AMSRE C-band descending",
#         "percent",
#     ],
#     "LPRM:LPRM_AMSRE_D_SOILM3.002:soil_moisture_x": [
#         "Soil moisture, volumetric, from LPRM AMSRE X-band descending",
#         "percent",
#     ],
#     "LPRM:LPRM_AMSRE_D_SOILM3.002:Ts": [
#         "Skin temperature (2mm) from LPRM AMSRE descending",
#         "K",
#     ],
#     "LPRM:LPRM_AMSRE_A_SOILM3.002:opt_depth_c": [
#         "Optical depth from LPRM AMSRE C-band ascending",
#         "unitless",
#     ],
#     "LPRM:LPRM_AMSRE_A_SOILM3.002:opt_depth_x": [
#         "Optical depth from LPRM AMSRE X-band ascending",
#         "unitless",
#     ],
#     "LPRM:LPRM_AMSRE_A_SOILM3.002:sm_c_error": [
#         "Soil moisture uncertainty of LPRM AMSRE C-band ascending",
#         "percent",
#     ],
#     "LPRM:LPRM_AMSRE_A_SOILM3.002:sm_x_error": [
#         "Soil moisture uncertainty of LPRM AMSRE X-band ascending",
#         "percent",
#     ],
#     "LPRM:LPRM_AMSRE_A_SOILM3.002:soil_moisture_c": [
#         "Soil moisture, volumetric, from LPRM AMSRE C-band ascending",
#         "percent",
#     ],
#     "LPRM:LPRM_AMSRE_A_SOILM3.002:soil_moisture_x": [
#         "Soil moisture, volumetric, from LPRM AMSRE X-band ascending",
#         "percent",
#     ],
#     "LPRM:LPRM_AMSRE_A_SOILM3.002:Ts": [
#         "Skin temperature (2mm) from LPRM AMSRE ascending",
#         "K",
#     ],
# }
# _UNITS_MAP.update(_LPRM_AMSR_SURFACE)
#
# _LPRM_AMSR_RZSM3 = {
#     "LPRM:LPRM_AMSRE_D_RZSM3.001:soilMoisture": [
#         "Root Zone Soil Moisture from Palmer Water Balance Model",
#         "percent",
#     ],
# }
# _UNITS_MAP.update(_LPRM_AMSR_RZSM3)
#
# _LPRM_AMSR2_25 = {
#     "LPRM:LPRM_AMSR2_A_SOILM3.001:soil_moisture_c1": [
#         "Volumetric Soil Moisture from 6.9 GHZ, ascending",
#         "percent",
#     ],
#     "LPRM:LPRM_AMSR2_D_SOILM3.001:soil_moisture_c1": [
#         "Volumetric Soil Moisture from 6.9 GHZ, descending",
#         "percent",
#     ],
# }
# _UNITS_MAP.update(_LPRM_AMSR2_25)
#
# _LPRM_AMSR2_10 = {
#     "LPRM:LPRM_AMSR2_DS_A_SOILM3.001:soil_moisture_c1": [
#         "Volumetric Soil Moisture from 6.9 GHZ, ascending",
#         "percent",
#     ],
#     "LPRM:LPRM_AMSR2_DS_D_SOILM3.001:soil_moisture_c1": [
#         "Volumetric Soil Moisture from 6.9 GHZ, descending",
#         "percent",
#     ],
# }
# _UNITS_MAP.update(_LPRM_AMSR2_10)
#
# _TMI_TRMM = {
#     "LPRM:LPRM_TMI_DY_SOILM3.001:opt_depth_x": [
#         "Optical depth from LPRM/TMI/TRMM X-band",
#         "unitless",
#     ],
#     "LPRM:LPRM_TMI_DY_SOILM3.001:sm_x_error": [
#         "Uncertainty of Soil Moisture in LPRM/TMI/TRMM X-band",
#         "m3/m3",
#     ],
#     "LPRM:LPRM_TMI_DY_SOILM3.001:soil_moisture_x": [
#         "Soil Moisture, Volumetric, from LPRM/TMI/TRMM X-band",
#         "percent",
#     ],
#     "LPRM:LPRM_TMI_DY_SOILM3.001:ts": [
#         "Skin temperature (2mm) from LPRM/TMI/TRMM",
#         "K",
#     ],
#     "LPRM:LPRM_TMI_NT_SOILM3.001:opt_depth_x": [
#         "Optical depth from LPRM/TMI/TRMM X-band",
#         "unitless",
#     ],
#     "LPRM:LPRM_TMI_NT_SOILM3.001:sm_x_error": [
#         "Uncertainty of Soil moisture in LPRM/TMI/TRMM X-band",
#         "m3/m3",
#     ],
#     "LPRM:LPRM_TMI_NT_SOILM3.001:soil_moisture_x": [
#         "Volumetric Soil Moisture from LPRM/TMI/TRMM X-band",
#         "percent",
#     ],
#     "LPRM:LPRM_TMI_NT_SOILM3.001:ts": [
#         "Skin temperature (2mm) from LPRM/TMI/TRMM",
#         "K",
#     ],
# }
# _UNITS_MAP.update(_TMI_TRMM)

_TRMM_TMPA = {
    "TRMM:TRMM_3B42.7:precipitation": ["Precipitation", "mm/hr"],
}
_SMERGE = {
    "SMERGE:SMERGE_RZSM0_40CM_2.0:CCI_ano": [
        "CCI soil moisture anomalies 0-40 cm",
        "m3/m3",
    ],
    "SMERGE:SMERGE_RZSM0_40CM_2.0:RZSM": [
        "Average soil moisture of 0-40 cm layer",
        "m3/m3",
    ],
}
_GRACE = {
    "GRACE:GRACEDADM_CLSM0125US_7D.4:gws_inst": [
        "Groundwater storage percentile",
        "percent",
    ],
    "GRACE:GRACEDADM_CLSM0125US_7D.4:rtzsm_inst": [
        "Root zone soil moisture percentile",
        "percent",
    ],
    "GRACE:GRACEDADM_CLSM0125US_7D.4:sfsm_inst": [
        "Surface soil moisture percentile",
        "percent",
    ],
}

_MERRA = {
    "MERRA:M2I1NXLFO.5124:QLML": ["Surface specific humidity:instant", "1"],
    "MERRA:M2I1NXLFO.5124:TLML": [
        "Surface air temperature over land:instant",
        "K",
    ],
    "MERRA:M2I1NXLFO.5124:SPEEDLML": ["Surface wind speed:instant", "m/s"],
    "MERRA:M2T1NXFLX.5124:ULML": ["Surface eastward wind:average", "m/s"],
    "MERRA:M2T1NXFLX.5124:VLML": ["Surface northward wind:average", "m/s"],
    "MERRA:M2T1NXLFO.5124:LWGAB": [
        "Surface absorbed longwave radiation:average",
        "W/m**2",
    ],
    "MERRA:M2T1NXLFO.5124:SWGDN": [
        "Incident shortwave radiation land:average",
        "W/m**2",
    ],
}

_MERRA_UPDATE = {
    "MERRA:MST1NXMLD.520:BASEFLOW": ["Baseflow", "mm/s"],
    "MERRA:MST1NXMLD.520:LHLAND": ["Latent heat flux from land", "W/m**2"],
    "MERRA:MST1NXMLD.520:PRECSNO": ["Surface snowfall", "mm/s"],
    "MERRA:MST1NXMLD.520:PRECTOT": ["Total surface precipitation", "mm/s"],
    "MERRA:MST1NXMLD.520:RUNOFF": ["Overland runoff", "mm/s"],
    "MERRA:MST1NXMLD.520:SFMC": ["Top soil layer soil moisture content", "m3/m3"],
    "MERRA:MST1NXMLD.520:SHLAND": ["Sensible heat flux from land", "W/m**2"],
    "MERRA:MST1NXMLD.520:TSOIL1": ["Soil temperature in layer 1", "K"],
}

_UNITS_MAP = _NLDAS_FORA
_UNITS_MAP.update(_NLDAS_NOAH)
_UNITS_MAP.update(_GLDAS_NOAH)
_UNITS_MAP.update(_TRMM_TMPA)
_UNITS_MAP.update(_SMERGE)
_UNITS_MAP.update(_GRACE)
_UNITS_MAP.update(_MERRA)
_UNITS_MAP.update(_MERRA_UPDATE)

_varmap = {
    "MST1NXMLD.520": "MERRA",
    "M2T1NXLFO.5124": "MERRA",
    "M2T1NXFLX.5124": "MERRA",
    "M2I1NXLFO.5124": "MERRA",
    "GRACEDADM_CLSM0125US_7D.4": "GRACE",
    "GLDAS_NOAH025_3H_v2.1": "GLDAS2",
    "NLDAS_NOAH0125_H.002": "NLDAS",
    "NLDAS_FORA0125_H.002": "NLDAS",
    "LPRM_AMSRE_D_SOILM3.002": "LPRM",
    "LPRM_AMSRE_A_SOILM3.002": "LPRM",
    "LPRM_AMSRE_D_RZSM3.001": "LPRM",
    "LPRM_AMSR2_A_SOILM3.001": "LPRM",
    "LPRM_AMSR2_D_SOILM3.001": "LPRM",
    "LPRM_AMSR2_DS_A_SOILM3.001": "LPRM",
    "LPRM_AMSR2_DS_D_SOILM3.001": "LPRM",
    "LPRM_TMI_DY_SOILM3.001": "LPRM",
    "LPRM_TMI_NT_SOILM3.001": "LPRM",
    "TRMM_3B42.7": "TRMM",
    "SMERGE_RZSM0_40CM_2.0": "SMERGE",
}

_project_start_dates = {
    "MERRA": "1980-01-01T00",
    "GLDAS2": "1948-01-01T00",
    "NLDAS": "1979-01-01T13",
    "TRMM": "1997-12-31T00",
    "SMERGE": "1997-01-02T00",
    "GRACE": "2002-10-04T00",
}

_project_sep = {
    "MERRA": "\t",
    "GLDAS2": "\t",
    "NLDAS": no_default,
    "TRMM": "\t",
    "SMERGE": "\t",
    "GRACE": "\t",
}

_project_header = {
    "MERRA": "infer",
    "GLDAS2": "infer",
    "NLDAS": None,
    "TRMM": "infer",
    "SMERGE": "infer",
    "GRACE": "infer",
}

_project_skiprows = {
    "MERRA": None,
    "GLDAS2": None,
    "NLDAS": 40,
    "TRMM": None,
    "SMERGE": None,
    "GRACE": None,
}

_project_delim_whitespace = {
    "MERRA": False,
    "GLDAS2": False,
    "NLDAS": True,
    "TRMM": False,
    "SMERGE": False,
    "GRACE": False,
}

_project_index_col = {
    "MERRA": "Datetime",
    "GLDAS2": "Datetime",
    "NLDAS": None,
    "TRMM": "Datetime",
    "SMERGE": "Datetime",
    "GRACE": "Datetime",
}


def make_units_table(units_dict):
    """Make a table of units for each variable."""
    new_units_table = [
        [
            f"{key[key.index(':') + 1:]}\n{val[0]}",
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


def foundation_cli(
    cli_name,
    formatter_class=HelpFormatter,
    units_table="",
    first_line="",
    meta_table="",
):
    """Create a foundation CLI function returning a function."""

    @cltoolbox.command(cli_name, formatter_class=formatter_class)
    @tsutils.doc(
        {"units_table": units_table, "first_line": first_line, "meta_table": meta_table}
    )
    def ldas_cli(
        lat=None,
        lon=None,
        xindex=None,
        yindex=None,
        variables=None,
        startDate=None,
        endDate=None,
        variable=None,
    ):
        # fmt: off
        """${first_line}

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
                Should use 'lat' and 'lon' to specify location.

                Latitude (required): Enter single geographic point by
                latitude.::

                    Example: --lat=43.1

                If known, 'xindex' and 'yindex' can be used for the NLDAS grid
                only.
            lon : float
                Should use 'lat' and 'lon' to specify location.

                Longitude (required): Enter single geographic point by
                longitude::

                    Example: --lon=-85.3

                If known, 'xindex' and 'yindex' can be used for the NLDAS grid
                only.
            xindex : int
                It `lat` or `lon` is None, then will try `xindex` and `yindex`.

                Enter the x index of the NLDAS grid.::

                    Example: --xindex=301
            yindex : int
                It `lat` or `lon` is None, then will try `xindex` and `yindex`.

                Enter the y index of the NLDAS grid.::

                    Example: --yindex=80
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
        tsutils.printiso(
            base_ldas(
                lat=lat,
                lon=lon,
                xindex=xindex,
                yindex=yindex,
                variables=variables,
                startDate=startDate,
                endDate=endDate,
                variable=variable,
            )
        )

    return ldas_cli


def foundation_api(cli_function):
    """Create a foundation API function returning a function."""

    @tsutils.copy_doc(cli_function)
    def ldas_api(
        lat=None,
        lon=None,
        xindex=None,
        yindex=None,
        variables=None,
        startDate=None,
        endDate=None,
        variable=None,
    ):
        return base_ldas(
            lat=lat,
            lon=lon,
            xindex=xindex,
            yindex=yindex,
            variables=variables,
            startDate=startDate,
            endDate=endDate,
            variable=variable,
        )

    return ldas_api


_META_HEADER = """        +-------------------------------+-------------+---------------+
        | Description/Name              | Spatial     | Time          |
        +===============================+=============+===============+"""

_NLDAS_FORA_META = """
        | NLDAS Primary Forcing Data    | 0.125x0.125 | 1 hour        |
        | NLDAS_FORA0125_H              | degree      |               |
        | V002                          |             |               |
        |                               | -125,25 to  | 1979-01-01T13 |
        |                               |  -67,53     | til recent    |
        +-------------------------------+-------------+---------------+"""
_NLDAS_NOAH_META = """
        | NLDAS Noah Land Surface Model | 0.125x0.125 | 1 hour        |
        | NLDAS_NOAH0125_H              | degree      |               |
        | V002                          |             |               |
        |                               | -125,25 to  | 1979-01-01T13 |
        |                               |  -67,53     | til recent    |
        +-------------------------------+-------------+---------------+"""
_GLDAS_NOAH_META = """
        | GLDAS Noah Land Surface Model | 0.25x0.25   | 3 hour        |
        | GLDAS_NOAH025_3H              | degree      |               |
        | V2.1                          |             |               |
        |                               | -180,-60 to | 2000-01-01 to |
        |                               |  180, 90    | recent        |
        +-------------------------------+-------------+---------------+"""
# _LPRM_AMSR_SURFACE_META = """
#         | AMSR-E/Aqua surface           | 25x25 km    | 1 day         |
#         | soil moisture                 |             |               |
#         | V002                          | -180,-90 to | 2002-06-19 to |
#         |                               |  180, 90    | 2011-10-03    |
#         +-------------------------------+-------------+---------------+
# """
# _LPRM_AMSR_RZSM3_META = """
#         | AMSR-E/Aqua root zone         | 25x25 km    | 1 day         |
#         | soil moisture                 |             |               |
#         | LPRM_AMSRE_D_RZSM3            | -180,-60 to | 2002-06-20 to |
#         | V001                          |  180, 60    | 2010-12-31    |
#         +-------------------------------+-------------+---------------+"""
# _LPRM_AMSR2_25_META = """
#         | AMSR2/GCOM-W1 surface         | 25x25 km    | 1 day         |
#         | soil moisture                 |             |               |
#         | LPRM_AMSR2_A_SOILM3           | -180,-90 to | 2012-07-19 to |
#         | V001                          |  180, 90    | recent        |
#         +-------------------------------+-------------+---------------+
#         | AMSR2/GCOM-W1 surface         | 25x25 km    | 1 day         |
#         | soil moisture                 |             |               |
#         | LPRM_AMSR2_D_SOILM3           | -180,-90 to | 2012-07-19 to |
#         | V001                          |  180, 90    | recent        |
#         +-------------------------------+-------------+---------------+
# """
# _LPRM_AMSR2_10_META = """
#         | AMSR2/GCOM-W1 surface         | 10x10 km    | 1 day         |
#         | soil moisture                 |             |               |
#         | LPRM_AMSR2_DS_A_SOILM3        | -180,-90 to | 2012-07-19 to |
#         | V001                          |  180, 90    | recent        |
#         +-------------------------------+-------------+---------------+
#         | ASMR2/GCOM-W1 surface         | 10x10 km    | 1 day         |
#         | soil moisture                 |             |               |
#         | LPRM_AMSR2_DS_D_SOILM3        | -180,-90 to | 2012-07-19 to |
#         | V001                          |  180, 90    | recent        |
#         +-------------------------------+-------------+---------------+
# """
# _LPRM_TRMM_META = """
#         | TMI/TRMM surface              | 25x25 km    | 1 day         |
#         | soil moisture                 |             |               |
#         | LPRM_TMI_NT_SOILM3            | -180,-40 to | 1997-12-07 to |
#         | V001                          |  180, 40    | 2015-04-08    |
#         +-------------------------------+-------------+---------------+
#         | TMI/TRMM surface              | 25x25 km    | 1 day         |
#         | soil moisture                 |             |               |
#         | LPRM_TMI_DY_SOILM3            | -180,-40 to | 1997-12-07 to |
#         | V001                          |  180, 40    | 2015-04-08    |
#         +-------------------------------+-------------+---------------+
# """
_TRMM_TMPA_META = """
        | TRMM (TMPA) Rainfall Estimate | 0.25x0.25   | 3 hour        |
        | TRMM_3B42                     | degree      |               |
        | V7                            |             |               |
        |                               | -180,-50 to | 1997-12-31 to |
        |                               |  180, 50    | recent        |
        +-------------------------------+-------------+---------------+"""
_SMERGE_META = """
        | Smerge-Noah-CCI root zone     | 0.125x0.125 | 1 day         |
        | soil moisture 0-40 cm         | degree      |               |
        | SMERGE_RZSM0_40CM             |             |               |
        | V2.0                          | -125, 25 to | 1979-01-02 to |
        |                               |  -67, 53    | recent        |
        +-------------------------------+-------------+---------------+"""
_GRACE_META = """
        | Groundwater and Soil Moisture | 0.125x0.125 | 7 day         |
        | Conditions from GRACE         | degree      |               |
        | Data Assimilation             |             |               |
        | GRACEDADM_CLSM0125US_7D       | -125, 25 to | 2002-10-04 to |
        | V4.0                          |  -67, 53    | recent        |
        +-------------------------------+-------------+---------------+"""
_MERRA_META = """
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
_MERRA_UPDATE_META = """
        | MERRA 2D Incremental          | 0.5x0.667   | 1 hour        |
        | Analysis Update               | degree      |               |
        | MST1NXMLD                     |             |               |
        | V5.12.4                       | -180,-90 to | 1980-01-01 to |
        |                               |  180, 90    | 2016-02-29    |
        +-------------------------------+-------------+---------------+"""

ldas_first_line = "grid: Land Data Assimilation System, includes all ldas_* (NLDAS, GLDAS2, TRMM, SMERGE, GRACE, MERRA)"
nldas_fora_first_line = "NAmerica 0.125deg 1979- H:NLDAS Weather Forcing A (surface)"
nldas_noah_first_line = "NAmerica 0.125deg 1979- H:NLDAS NOAH hydrology model results"
gldas_noah_first_line = "global 0.25deg 2000- 3H:GLDAS NOAH hydrology model results"
# lprm_amsr_rzsm3_first_line = (
#     "global 25km 2002-2010 D:AMSR-E/Aqua root zone soil moisture"
# )
trmm_tmpa_first_line = "global 0.25deg 1997- 3H:TRMM (TMPA) rainfall estimate"
smerge_first_line = "global 0.125deg 1997- D:SMERGE-Noah-CCI root zone soil moisture"
grace_first_line = "NAmerica 0.125deg 2002- 7D:Groundwater and soil moisture from GRACE"
merra_first_line = "global 0.5x0.625deg 1980- H:MERRA-2 Land surface forcings"
merra_update_first_line = "global 0.5x0.667deg 1980-2016 H:MERRA-2 Analysis update"

ldas_cli = foundation_cli(
    "ldas",
    units_table=make_units_table(_UNITS_MAP),
    first_line=ldas_first_line,
    meta_table="".join(
        [
            _META_HEADER,
            _GLDAS_NOAH_META,
            _GRACE_META,
            _MERRA_META,
            _MERRA_UPDATE_META,
            _NLDAS_FORA_META,
            _NLDAS_NOAH_META,
            _SMERGE_META,
            _TRMM_TMPA_META,
        ]
    ),
)
ldas = foundation_api(ldas_cli)

ldas_gldas_noah_cli = foundation_cli(
    "ldas_gldas_noah",
    units_table=make_units_table(_GLDAS_NOAH),
    first_line=gldas_noah_first_line,
    meta_table=_META_HEADER + _GLDAS_NOAH_META,
)
ldas_gldas_noah = foundation_api(ldas_gldas_noah_cli)

ldas_grace_cli = foundation_cli(
    "ldas_grace",
    units_table=make_units_table(_GRACE),
    first_line=grace_first_line,
    meta_table=_META_HEADER + _GRACE_META,
)
ldas_grace = foundation_api(ldas_grace_cli)

ldas_merra_cli = foundation_cli(
    "ldas_merra",
    units_table=make_units_table(_MERRA),
    first_line=merra_first_line,
    meta_table=_META_HEADER + _MERRA_META,
)
ldas_merra = foundation_api(ldas_merra_cli)

ldas_merra_update_cli = foundation_cli(
    "ldas_merra_update",
    units_table=make_units_table(_MERRA_UPDATE),
    first_line=merra_update_first_line,
    meta_table=_META_HEADER + _MERRA_UPDATE_META,
)
ldas_merra_update = foundation_api(ldas_merra_update_cli)

ldas_nldas_fora_cli = foundation_cli(
    "ldas_nldas_fora",
    units_table=make_units_table(_NLDAS_FORA),
    first_line=nldas_fora_first_line,
    meta_table=_META_HEADER + _NLDAS_FORA_META,
)
ldas_nldas_fora = foundation_api(ldas_nldas_fora_cli)

ldas_nldas_noah_cli = foundation_cli(
    "ldas_nldas_noah",
    units_table=make_units_table(_NLDAS_NOAH),
    first_line=nldas_noah_first_line,
    meta_table=_META_HEADER + _NLDAS_NOAH_META,
)
ldas_nldas_noah = foundation_api(ldas_nldas_noah_cli)

# ldas_amsre_rzsm3_cli = foundation_cli(
#     "ldas_amsre_rzsm3",
#     units_table=make_units_table(_LPRM_AMSR_RZSM3),
#     first_line=lprm_amsr_rzsm3_first_line,
#     meta_table=_META_HEADER + _LPRM_AMSR_RZSM3_META,
# )
# ldas_amsre_rzsm3 = foundation_api(ldas_amsre_rzsm3_cli)

ldas_smerge_cli = foundation_cli(
    "ldas_smerge",
    units_table=make_units_table(_SMERGE),
    first_line=smerge_first_line,
    meta_table=_META_HEADER + _SMERGE_META,
)
ldas_smerge = foundation_api(ldas_smerge_cli)

ldas_trmm_tmpa_cli = foundation_cli(
    "ldas_trmm_tmpa",
    units_table=make_units_table(_TRMM_TMPA),
    first_line=trmm_tmpa_first_line,
    meta_table=_META_HEADER + _TRMM_TMPA_META,
)
ldas_trmm_tmpa = foundation_api(ldas_trmm_tmpa_cli)


@tsutils.transform_args(variables=tsutils.make_list, variable=tsutils.make_list)
@tsutils.copy_doc(ldas_cli)
def base_ldas(
    lat=None,
    lon=None,
    xindex=None,
    yindex=None,
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

    if lat is not None and lon is not None:
        location = f"GEOM:POINT({lon}, {lat})"
    elif xindex is not None and yindex is not None:
        location = f"NLDAS:X{xindex:03d}-Y{yindex:03d}"
    else:
        raise ValueError(
            tsutils.error_wrapper(
                f"""
                There is a problem specifying the location.

                Both `lat` and `lon` need to be specified where you have
                "lat={lat}" and "lon={lon}".

                Only for the NLDAS grid can you use `xindex` and `yindex` to
                specify the location.  You have
                "xindex={xindex}" and "yindex={yindex}".
                """
            )
        )

    url = r"https://hydro1.gesdisc.eosdis.nasa.gov/daac-bin/access/timeseries.cgi"

    ndf = pd.DataFrame()
    nvariables = []
    for var in variables:
        words = var.split(":")
        project = words[0]
        if len(words) == 2:
            # New style where can leave off first ":" separated field.
            project = _varmap[words[0]]
            nvariables.append(":".join([project] + words))
        else:
            nvariables.append(var)

    if startDate is None:
        startDate = tsutils.parsedate(_project_start_dates[project])
    else:
        try:
            startDate = tsutils.parsedate(startDate)
            if startDate < tsutils.parsedate(_project_start_dates[project]):
                startDate = tsutils.parsedate(_project_start_dates[project])
        except TypeError:
            pass
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
                url,
                {
                    "params": {
                        "type": "asc2",
                        "location": location,
                        "variable": v,
                        "startDate": s.strftime("%Y-%m-%dT%H"),
                        "endDate": e.strftime("%Y-%m-%dT%H"),
                    }
                },
            )
            for (s, e), v in itertools.product(periods, nvariables)
        ]
    )

    kwds = [
        {"params": {k: v for k, v in i["params"].items() if v is not None}}
        for i in kwds
    ]

    if os.path.exists("debug_tsgettoolbox"):
        logging.warning(f"{urls}, {kwds}")

    resp = ar.retrieve_binary(urls, kwds, max_workers=1)

    joined = [[r, kw] for r, kw in zip(resp, kwds) if b"ERROR" not in r]

    resp = [i[0] for i in joined]
    kw = [i[1] for i in joined]

    ndf = pd.DataFrame()
    for k, r in zip(kw, resp):
        names = None
        if project in ("GLDAS2", "TRMM", "SMERGE", "GRACE", "MERRA"):
            names = [
                "Datetime",
                f"{k['params']['variable'].split(':')[-1]}:{_UNITS_MAP[k['params']['variable']][1]}",
            ]
        df = pd.read_csv(
            BytesIO(r),
            sep=_project_sep[project],
            header=_project_header[project],
            skiprows=_project_skiprows[project],
            delim_whitespace=_project_delim_whitespace[project],
            names=names,
            index_col=_project_index_col[project],
            na_values=[-9999, -9999.0],
        ).dropna()
        df.index = pd.to_datetime(df.index)
        if project == "NLDAS":
            if len(df.columns) == 3:
                df["dt"] = df[0].str.cat(df[1], sep="T")
                df["dt"] = pd.to_datetime(df["dt"])
                df.set_index("dt", inplace=True)
                df.drop([0, 1], axis="columns", inplace=True)
            else:
                df[0] = pd.to_datetime(df[0])
                df.set_index(0, inplace=True)
            variable_name = k["params"]["variable"].split(":")[-1]
            unit = _UNITS_MAP[k["params"]["variable"]][1]
            df.columns = [f"{variable_name}:{unit}"]

        df.index.name = "Datetime:UTC"
        with suppress(TypeError):
            return df.tz_localize("UTC")
        ndf = ndf.combine_first(df)

    return ndf


if __name__ == "__main__":
    # for key in _UNITS_MAP:
    #     print("LDAS", key)
    #     r = ldas(
    #         variables=key,
    #         lon=-100,
    #         lat=31,
    #         startDate="2013-06-01T09",
    #         endDate="2014-05-04T21",
    #     )
    #     print(r)
    #     time.sleep(20)
    #     r = ldas(
    #         variables=key[key.index(":") + 1 :],
    #         lon=-100,
    #         lat=31,
    #         startDate="2013-06-01T09",
    #         endDate="2014-05-04T21",
    #     )
    #     print(r)
    #     time.sleep(20)
    r = ldas(
        variables="GLDAS2:GLDAS_NOAH025_3H_v2.1:SoilMoi10_40cm_inst",
        lon=100,
        lat=34,
    )

    print("LDAS TEST")
    print(r)

    r = ldas(
        variables="GLDAS2:GLDAS_NOAH025_3H_v2.1:SoilMoi10_40cm_inst",
        lon=100,
        lat=34,
        endDate="2001-01-01",
    )

    print("LDAS TEST")
    print(r)

    for key in _UNITS_MAP:
        print(key)
        r = ldas_nldas_noah(
            variables=key[key.index(":") + 1 :],
            lon=-100,
            lat=31,
            startDate="2013-06-01T09",
            endDate="2014-07-04T21",
        )
        print(r)
        if r.index[0] != pd.Timestamp("2013-06-01T09", tz="UTC"):
            print("yeah")
        if r.index[-1] != pd.Timestamp("2014-07-04T21", tz="UTC"):
            print("yeah")

    r = ldas(
        variables="GLDAS2:GLDAS_NOAH025_3H_v2.1:SoilMoi10_40cm_inst",
        lon=100,
        lat=30,
        startDate="2016-01-01T00",
        endDate="2016-12-01T00",
    )

    print("LDAS TEST")
    print(r)

    r = ldas(
        variables="GLDAS2:GLDAS_NOAH025_3H_v2.1:SoilMoi10_40cm_inst",
        lon=100,
        lat=34,
        startDate="5 years ago",
        endDate="4 years ago",
    )

    print("LDAS TEST")
    print(r)

    r = ldas(
        variables=[
            "GLDAS2:GLDAS_NOAH025_3H_v2.1:SoilMoi10_40cm_inst",
            "GLDAS2:GLDAS_NOAH025_3H_v2.1:Evap_tavg",
        ],
        lon=100,
        lat=34,
        startDate="5 years ago",
        endDate="4 years ago",
    )
    print(r)
