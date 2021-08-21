# -*- coding: utf-8 -*-
import logging
import os
import textwrap
import time
from argparse import RawTextHelpFormatter as HelpFormatter
from io import BytesIO

import mando
import pandas as pd
from tabulate import tabulate as tb
from tstoolbox import tsutils

from tsgettoolbox import utils

_UNITS_MAP = {
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
    #
    # as of 2020-08-07 has been taken off line to address issues.
    #
    #    "LPRM:LPRM_AMSRE_D_SOILM3.002:opt_depth_c": [
    #        "Optical depth from LPRM AMSRE C-band descending",
    #        "unitless",
    #    ],
    #    "LPRM:LPRM_AMSRE_D_SOILM3.002:opt_depth_x": [
    #        "Optical depth from LPRM AMSRE X-band descending",
    #        "unitless",
    #    ],
    #    "LPRM:LPRM_AMSRE_D_SOILM3.002:sm_c_error": [
    #        "Soil moisture uncertainty of LPRM AMSRE C-band",
    #        "percent",
    #    ],
    #    "LPRM:LPRM_AMSRE_D_SOILM3.002:sm_x_error": [
    #        "Soil moisture uncertainty of LPRM AMSRE X-band",
    #        "percent",
    #    ],
    #    "LPRM:LPRM_AMSRE_D_SOILM3.002:soil_moisture_c": [
    #        "Soil moisture, volumetric, from LPRM AMSRE C-band descending",
    #        "percent",
    #    ],
    #    "LPRM:LPRM_AMSRE_D_SOILM3.002:soil_moisture_x": [
    #        "Soil moisture, volumetric, from LPRM AMSRE X-band descending",
    #        "percent",
    #    ],
    #    "LPRM:LPRM_AMSRE_D_SOILM3.002:Ts": [
    #        "Skin temperature (2mm) from LPRM AMSRE descending",
    #        "K",
    #    ],
    #    "LPRM:LPRM_AMSRE_A_SOILM3.002:opt_depth_c": [
    #        "Optical depth from LPRM AMSRE C-band descending",
    #        "unitless",
    #    ],
    #    "LPRM:LPRM_AMSRE_A_SOILM3.002:opt_depth_x": [
    #        "Optical depth from LPRM AMSRE X-band descending",
    #        "unitless",
    #    ],
    #    "LPRM:LPRM_AMSRE_A_SOILM3.002:sm_c_error": [
    #        "Soil moisture uncertainty of LPRM AMSRE C-band",
    #        "percent",
    #    ],
    #    "LPRM:LPRM_AMSRE_A_SOILM3.002:sm_x_error": [
    #        "Soil moisture uncertainty of LPRM AMSRE X-band",
    #        "percent",
    #    ],
    #    "LPRM:LPRM_AMSRE_A_SOILM3.002:soil_moisture_c": [
    #        "Soil moisture, volumetric, from LPRM AMSRE C-band descending",
    #        "percent",
    #    ],
    #    "LPRM:LPRM_AMSRE_A_SOILM3.002:soil_moisture_x": [
    #        "Soil moisture, volumetric, from LPRM AMSRE X-band descending",
    #        "percent",
    #    ],
    #    "LPRM:LPRM_AMSRE_A_SOILM3.002:Ts": [
    #        "Skin temperature (2mm) from LPRM AMSRE descending",
    #        "K",
    #    ],
    #    "LPRM:LPRM_AMSRE_D_RZSM3.001:soilMoisture": [
    #        "Root Zone Soil Moisture from Palmer Water Balance Model",
    #        "percent",
    #    ],
    #    "LPRM:LPRM_AMSR2_A_SOILM3.001:soil_moisture_c1": [
    #        "Volumetric Soil Moisture from 6.9 GHZ, ascending",
    #        "percent",
    #    ],
    #    "LPRM:LPRM_AMSR2_D_SOILM3.001:soil_moisture_c1": [
    #        "Volumetric Soil Moisture from 6.9 GHZ, descending",
    #        "percent",
    #    ],
    #    "LPRM:LPRM_AMSR2_DS_A_SOILM3.001:soil_moisture_c1": [
    #        "Volumetric Soil Moisture from 6.9 GHZ, ascending",
    #        "percent",
    #    ],
    #    "LPRM:LPRM_AMSR2_DS_D_SOILM3.001:soil_moisture_c1": [
    #        "Volumetric Soil Moisture from 6.9 GHZ, descending",
    #        "percent",
    #    ],
    #    "LPRM:LPRM_TMI_DY_SOILM3.001:opt_depth_x": [
    #        "Optical depth from LPRM/TMI/TRMM X-band",
    #        "unitless",
    #    ],
    #    "LPRM:LPRM_TMI_DY_SOILM3.001:sm_x_error": [
    #        "Uncertainty of Soil Moisture in LPRM/TMI/TRMM X-band",
    #        "m3/m3",
    #    ],
    #    "LPRM:LPRM_TMI_DY_SOILM3.001:soil_moisture_x": [
    #        "Soil Moisture, Volumetric, from LPRM/TMI/TRMM X-band",
    #        "percent",
    #    ],
    #    "LPRM:LPRM_TMI_DY_SOILM3.001:ts": [
    #        "Skin temperature (2mm) from LPRM/TMI/TRMM",
    #        "K",
    #    ],
    #    "LPRM:LPRM_TMI_NT_SOILM3.001:opt_depth_x": [
    #        "Optical depth from LPRM/TMI/TRMM X-band",
    #        "unitless",
    #    ],
    #    "LPRM:LPRM_TMI_NT_SOILM3.001:sm_x_error": [
    #        "Uncertainty of Soil moisture in LPRM/TMI/TRMM X-band",
    #        "m3/m3",
    #    ],
    #    "LPRM:LPRM_TMI_NT_SOILM3.001:soil_moisture_x": [
    #        "Volumetric Soil Moisture from LPRM/TMI/TRMM X-band",
    #        "percent",
    #    ],
    #    "LPRM:LPRM_TMI_NT_SOILM3.001:ts": [
    #        "Skin temperature (2mm) from LPRM/TMI/TRMM",
    #        "K",
    #    ],
    "TRMM:TRMM_3B42.7:precipitation": ["Precipitation", "mm/hr"],
    "SMERGE:SMERGE_RZSM0_40CM_2.0:CCI_ano": [
        "CCI soil moisture anomalies 0-40 cm",
        "m3/m3",
    ],
    "SMERGE:SMERGE_RZSM0_40CM_2.0:RZSM": [
        "Average soil moisture of 0-40 cm layer",
        "m3/m3",
    ],
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
    "MERRA:MST1NXMLD.520:BASEFLOW": ["Baseflow", "mm/s"],
    "MERRA:MST1NXMLD.520:LHLAND": ["Latent heat flux from land", "W/m**2"],
    "MERRA:MST1NXMLD.520:PRECSNO": ["Surface snowfall", "mm/s"],
    "MERRA:MST1NXMLD.520:PRECTOT": ["Total surface precipitation", "mm/s"],
    "MERRA:MST1NXMLD.520:RUNOFF": ["Overland runoff", "mm/s"],
    "MERRA:MST1NXMLD.520:SFMC": ["Top soil layer soil moisture content", "m3/m3"],
    "MERRA:MST1NXMLD.520:SHLAND": ["Sensible heat flux from land", "W/m**2"],
    "MERRA:MST1NXMLD.520:TSOIL1": ["Soil temperature in layer 1", "K"],
}

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

new_units_table = [
    [
        "{}\n{}".format(i[i.index(":") + 1 :], _UNITS_MAP[i][0]),
        "{}".format(_UNITS_MAP[i][1]),
    ]
    for i in _UNITS_MAP
]

units_table = tb(
    new_units_table,
    tablefmt="grid",
    headers=['LDAS "variables" string Description', "Units"],
)

units_table = textwrap.indent(units_table.strip(), "            ")


@mando.command("ldas", formatter_class=HelpFormatter, doctype="numpy")
@tsutils.doc({"units_table": units_table})
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
    """Download data from the Land Data Assimilation System (LDAS).

        This will download data from a set of water cycle related variables
        (Table 1) from the North American and Global Land Data Assimilation
        Systems (NLDAS and GLDAS, respectively), the Land Parameter
        Parameter Model (LPRM), the Tropical Rainfall Measuring Mission
        (TRMM), and Gravity Recovery and Climate Experiment (GRACE) data
        assimilation. In addition to their access provided by the hydrology
        community tools, selected data rods variables can be searched and
        accessed through the GES DISC search and access user interface, and
        all data rods variables can be accessed via Web services developed
        by the GES DISC.

        +-------------------------------+-------------+---------------+
        | Description/Name              | Spatial     | Time          |
        +===============================+=============+===============+
        | NLDAS Primary Forcing Data    | 0.125x0.125 | 1 hour        |
        | NLDAS_FORA0125_H              | degree      |               |
        | V002                          |             |               |
        |                               | -125,25 to  | 1979-01-01T13 |
        |                               |  -67,53     | til recent    |
        +-------------------------------+-------------+---------------+
        | NLDAS Noah Land Surface Model | 0.125x0.125 | 1 hour        |
        | NLDAS_NOAH0125_H              | degree      |               |
        | V002                          |             |               |
        |                               | -125,25 to  | 1979-01-01T13 |
        |                               |  -67,53     | til recent    |
        +-------------------------------+-------------+---------------+
        | GLDAS Noah Land Surface Model | 0.25x0.25   | 3 hour        |
        | GLDAS_NOAH025_3H              | degree      |               |
        | V2.1                          |             |               |
        |                               | -180,-60 to | 2000-01-01 to |
        |                               |  180, 90    | recent        |
        +-------------------------------+-------------+---------------+
        | AMSR-E/Aqua surface           | 25x25 km    | 1 day         |
        | soil moisture                 |             |               |
        | V002                          | -180,-90 to | 2002-06-19 to |
        |                               |  180, 90    | 2011-10-03    |
        +-------------------------------+-------------+---------------+
        | AMSR-E/Aqua root zone         | 25x25 km    | 1 day         |
        | soil moisture                 |             |               |
        | LPRM_AMSRE_D_RZSM3            | -180,-60 to | 2002-06-20 to |
        | V001                          |  180, 60    | 2010-12-31    |
        +-------------------------------+-------------+---------------+
        | AMSR2/GCOM-W1 surface         | 25x25 km    | 1 day         |
        | soil moisture                 |             |               |
        | LPRM_AMSR2_A_SOILM3           | -180,-90 to | 2012-07-19 to |
        | V001                          |  180, 90    | recent        |
        +-------------------------------+-------------+---------------+
        | AMSR2/GCOM-W1 surface         | 25x25 km    | 1 day         |
        | soil moisture                 |             |               |
        | LPRM_AMSR2_D_SOILM3           | -180,-90 to | 2012-07-19 to |
        | V001                          |  180, 90    | recent        |
        +-------------------------------+-------------+---------------+
        | AMSR2/GCOM-W1 surface         | 10x10 km    | 1 day         |
        | soil moisture                 |             |               |
        | LPRM_AMSR2_DS_A_SOILM3        | -180,-90 to | 2012-07-19 to |
        | V001                          |  180, 90    | recent        |
        +-------------------------------+-------------+---------------+
        | ASMR2/GCOM-W1 surface         | 10x10 km    | 1 day         |
        | soil moisture                 |             |               |
        | LPRM_AMSR2_DS_D_SOILM3        | -180,-90 to | 2012-07-19 to |
        | V001                          |  180, 90    | recent        |
        +-------------------------------+-------------+---------------+
        | TMI/TRMM surface              | 25x25 km    | 1 day         |
        | soil moisture                 |             |               |
        | LPRM_TMI_NT_SOILM3            | -180,-40 to | 1997-12-07 to |
        | V001                          |  180, 40    | 2015-04-08    |
        +-------------------------------+-------------+---------------+
        | TMI/TRMM surface              | 25x25 km    | 1 day         |
        | soil moisture                 |             |               |
        | LPRM_TMI_DY_SOILM3            | -180,-40 to | 1997-12-07 to |
        | V001                          |  180, 40    | 2015-04-08    |
        +-------------------------------+-------------+---------------+
        | TRMM (TMPA) Rainfall Estimate | 0.25x0.25   | 3 hour        |
        | TRMM_3B42                     | degree      |               |
        | V7                            |             |               |
        |                               | -180,-50 to | 1997-12-31 to |
        |                               |  180, 50    | recent        |
        +-------------------------------+-------------+---------------+
        | Smerge-Noah-CCI root zone     | 0.125x0.125 | 1 day         |
        | soil moisture 0-40 cm         | degree      |               |
        | SMERGE_RZSM0_40CM             |             |               |
        | V2.0                          | -125, 25 to | 1979-01-02 to |
        |                               |  -67, 53    | recent        |
        +-------------------------------+-------------+---------------+
        | Groundwater and Soil Moisture | 0.125x0.125 | 7 day         |
        | Conditions from GRACE         | degree      |               |
        | Data Assimilation             |             |               |
        | GRACEDADM_CLSM0125US_7D       | -125, 25 to | 2002-10-04 to |
        | V4.0                          |  -67, 53    | recent        |
        +-------------------------------+-------------+---------------+
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
        +-------------------------------+-------------+---------------+
        | MERRA 2D Incremental          | 0.5x0.667   | 1 hour        |
        | Analysis Update               | degree      |               |
        | MST1NXMLD                     |             |               |
        | V5.12.4                       | -180,-90 to | 1980-01-01 to |
        |                               |  180, 90    | 2016-02-29    |
        +-------------------------------+-------------+---------------+

        The time zone is always UTC.

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

    {units_table}
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
            "tsgettoolbox".
    """
    tsutils._printiso(
        ldas(
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


# @tsutils.validator(
#    lat=[float, ["range", [-90.0, 90.0]], 1],
#    lon=[float, ["range", [-180.0, 180.0]], 1],
#    xindex=[int, ["range", [0, None]], 1],
#    yindex=[int, ["range", [0, None]], 1],
#    variable=[str, ["pass", []], None],
#    startDate=[tsutils.parsedate, ["pass", []], 1],
#    endDate=[tsutils.parsedate, ["pass", []], 1],
# )
@tsutils.transform_args(variables=tsutils.make_list, variable=tsutils.make_list)
def ldas(
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
The 'variable' keyword is deprecated. Please use 'variables' instead to be
consistent with other services in tsgettoolbox."""
            )
        )

    if lat is not None and lon is not None:
        location = "GEOM:POINT({}, {})".format(lon, lat)
    elif project == "NLDAS" and xindex is not None and yindex is not None:
        location = "{}:X{:03d}-Y{:03d}".format(project, xindex, yindex)
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

    url = r"https://hydro1.gesdisc.eosdis.nasa.gov/daac-bin/access/timeseries.cgi"

    ndf = pd.DataFrame()
    for var in variables:
        words = var.split(":")
        project = words[0]
        nvariable = var
        if len(words) == 2:
            # New style where can leave off first ":" separated field.
            nvariable = ":".join([_varmap[words[0]]] + words)

        query_params = {}
        query_params["type"] = "asc2"
        query_params["startDate"] = tsutils.parsedate(startDate, strftime="%Y-%m-%dT%H")
        query_params["endDate"] = tsutils.parsedate(endDate, strftime="%Y-%m-%dT%H")
        query_params["location"] = location
        query_params["variable"] = nvariable

        session = utils.requests_retry_session()
        req = session.get(url, params=query_params)

        if os.path.exists("debug_tsgettoolbox"):
            logging.warning(req.url)
        req.raise_for_status()
        if b"ERROR" in req.content:
            raise ValueError(req.content)

        df = pd.read_csv(
            BytesIO(req.content),
            skiprows=40,
            header=None,
            index_col=None,
            delim_whitespace=True,
            na_values=[-9999, -9999.0],
        )
        df.drop(df.index[-1], axis="rows", inplace=True)
        if len(df.columns) == 3:
            df["dt"] = df[0] + "T" + df[1]
            df["dt"] = pd.to_datetime(df["dt"])
            df.set_index("dt", inplace=True)
            df.drop([0, 1], axis="columns", inplace=True)
        else:
            df[0] = pd.to_datetime(df[0])
            df.set_index(0, inplace=True)
        variable_name = query_params["variable"].split(":")[-1]
        unit = _UNITS_MAP[query_params["variable"]][1]
        df.columns = ["{}:{}".format(variable_name, unit)]
        df.index.name = "Datetime:UTC"
        try:
            return df.tz_localize("UTC")
        except TypeError:  # Already UTC
            pass
        ndf = ndf.join(df, how="outer")

    return ndf


ldas.__doc__ = ldas_cli.__doc__


if __name__ == "__main__":
    for key in _UNITS_MAP:
        print("LDAS", key)
        r = ldas(
            variables=key,
            lon=-100,
            lat=31,
            startDate="2013-06-01T09",
            endDate="2014-05-04T21",
        )
        print(r)
        time.sleep(2)
        r = ldas(
            variables=key[key.index(":") + 1 :],
            lon=-100,
            lat=31,
            startDate="2013-06-01T09",
            endDate="2014-05-04T21",
        )
        print(r)
        time.sleep(2)

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
