from __future__ import print_function
from __future__ import absolute_import

import logging
import os
from builtins import object
from io import BytesIO

from tsgettoolbox.odo import convert
from tsgettoolbox.odo import odo
from tsgettoolbox.odo import resource

import pandas as pd

import requests

from tstoolbox import tsutils

_UNITS_MAP = {
    "NLDAS:NLDAS_FORA0125_H.002:APCPsfc": ["Precipitation hourly total", "kg/m2"],
    "NLDAS:NLDAS_FORA0125_H.002:DLWRFsfc": [
        "Surface DW longwave radiation flux",
        "W/m2",
    ],
    "NLDAS:NLDAS_FORA0125_H.002:DSWRFsfc": [
        "Surface DW shortwave radiation flux",
        "W/m2",
    ],
    "NLDAS:NLDAS_FORA0125_H.002:PEVAPsfc": ["Potential evaporation", "kg/m2"],
    "NLDAS:NLDAS_FORA0125_H.002:SPFH2m": [
        "2-m above ground specific humidity",
        "kg/kg",
    ],
    "NLDAS:NLDAS_FORA0125_H.002:TMP2m": ["2-m above ground temperature", "K"],
    "NLDAS:NLDAS_FORA0125_H.002:UGRD10m": ["10-m above ground zonal wind", "m/s"],
    "NLDAS:NLDAS_FORA0125_H.002:VGRD10m": ["10-m above ground meridional wind", "m/s"],
    "NLDAS:NLDAS_NOAH0125_H.002:EVPsfc": ["Total evapotranspiration", "kg/m2"],
    "NLDAS:NLDAS_NOAH0125_H.002:GFLUXsfc": ["Ground heat flux", "W/m2"],
    "NLDAS:NLDAS_NOAH0125_H.002:LHTFLsfc": ["Latent heat flux", "W/m2"],
    "NLDAS:NLDAS_NOAH0125_H.002:SHTFLsfc": ["Sensible heat flux", "W/m2"],
    "NLDAS:NLDAS_NOAH0125_H.002:SSRUNsfc": [
        "Surface runoff (non-infiltrating)",
        "kg/m2",
    ],
    "NLDAS:NLDAS_NOAH0125_H.002:BGRUNsfc": ["Subsurface runoff (baseflow)", "kg/m2"],
    "NLDAS:NLDAS_NOAH0125_H.002:SOILM0-10cm": [
        "0-10 cm soil moisture content",
        "kg/m2",
    ],
    "NLDAS:NLDAS_NOAH0125_H.002:SOILM0-100cm": [
        "0-100 cm soil moisture content",
        "kg/m2",
    ],
    "NLDAS:NLDAS_NOAH0125_H.002:SOILM0-200cm": [
        "0-200 cm soil moisture content",
        "kg/m2",
    ],
    "NLDAS:NLDAS_NOAH0125_H.002:SOILM10-40cm": [
        "10-40 cm soil moisture content",
        "kg/m2",
    ],
    "NLDAS:NLDAS_NOAH0125_H.002:SOILM40-100cm": [
        "40-100 cm soil moisture content",
        "kg/m2",
    ],
    "NLDAS:NLDAS_NOAH0125_H.002:SOILM100-200cm": [
        "100-200 cm soil moisture content",
        "kg/m2",
    ],
    "NLDAS:NLDAS_NOAH0125_H.002:TSOIL0-10cm": ["0-10 cm soil temperature", "K"],
    "GLDAS2:GLDAS_NOAH025_3H_v2.1:AvgSurfT_inst": [
        "Average surface skin temperature",
        "K",
    ],
    "GLDAS2:GLDAS_NOAH025_3H_v2.1:Evap_tavg": ["Evapotranspiration", "kg/m2/s"],
    "GLDAS2:GLDAS_NOAH025_3H_v2.1:Psurf_f_inst": ["Surface air pressure", "Pa"],
    "GLDAS2:GLDAS_NOAH025_3H_v2.1:Qair_f_inst": ["Specific humidity", "kg/kg"],
    "GLDAS2:GLDAS_NOAH025_3H_v2.1:Qs_acc": ["Storm surface runoff", "kg/m2"],
    "GLDAS2:GLDAS_NOAH025_3H_v2.1:Qsb_acc": ["Baseflow-groundwater runoff", "kg/m2"],
    "GLDAS2:GLDAS_NOAH025_3H_v2.1:Rainf_f_tavg": [
        "Total precipitation rate",
        "kg/m2/s",
    ],
    "GLDAS2:GLDAS_NOAH025_3H_v2.1:Rainf_tavg": ["Rain precipitation rate", "kg/m2/s"],
    "GLDAS2:GLDAS_NOAH025_3H_v2.1:Snowf_tavg": ["Snow precipitation rate", "kg/m2/s"],
    "GLDAS2:GLDAS_NOAH025_3H_v2.1:SoilMoi0_10cm_inst": [
        "Soil moisture content (0-10 cm underground)",
        "kg/m2",
    ],
    "GLDAS2:GLDAS_NOAH025_3H_v2.1:SoilMoi10_40cm_inst": [
        "Soil moisture content (10-40 cm underground)",
        "kg/m2",
    ],
    "GLDAS2:GLDAS_NOAH025_3H_v2.1:SoilMoi40_100cm_inst": [
        "Soil moisture content (40-100 cm underground)",
        "kg/m2",
    ],
    "GLDAS2:GLDAS_NOAH025_3H_v2.1:SoilTMP0_10cm_inst": [
        "Soil temperature (0-10 cm underground)",
        "K",
    ],
    "GLDAS2:GLDAS_NOAH025_3H_v2.1:Tair_f_inst": ["Near surface air temperature", "K"],
    "GLDAS2:GLDAS_NOAH025_3H_v2.1:Wind_f_inst": ["Near surface wind speed", "m/s"],
    "LPRM:LPRM_AMSRE_D_SOILM3.002:opt_depth_c": [
        "Optical depth from LPRM AMSRE C-band descending",
        "unitless",
    ],
    "LPRM:LPRM_AMSRE_D_SOILM3.002:opt_depth_x": [
        "Optical depth from LPRM AMSRE X-band descending",
        "unitless",
    ],
    "LPRM:LPRM_AMSRE_D_SOILM3.002:sm_c_error": [
        "Soil moisture uncertainty of LPRM AMSRE C-band",
        "percent",
    ],
    "LPRM:LPRM_AMSRE_D_SOILM3.002:sm_x_error": [
        "Soil moisture uncertainty of LPRM AMSRE X-band",
        "percent",
    ],
    "LPRM:LPRM_AMSRE_D_SOILM3.002:soil_moisture_c": [
        "Soil moisture, volumetric, from LPRM AMSRE C-band descending",
        "percent",
    ],
    "LPRM:LPRM_AMSRE_D_SOILM3.002:soil_moisture_x": [
        "Soil moisture, volumetric, from LPRM AMSRE X-band descending",
        "percent",
    ],
    "LPRM:LPRM_AMSRE_D_SOILM3.002:Ts": [
        "Skin temperature (2mm) from LPRM AMSRE descending",
        "K",
    ],
    "LPRM:LPRM_AMSRE_A_SOILM3.002:opt_depth_c": [
        "Optical depth from LPRM AMSRE C-band descending",
        "unitless",
    ],
    "LPRM:LPRM_AMSRE_A_SOILM3.002:opt_depth_x": [
        "Optical depth from LPRM AMSRE X-band descending",
        "unitless",
    ],
    "LPRM:LPRM_AMSRE_A_SOILM3.002:sm_c_error": [
        "Soil moisture uncertainty of LPRM AMSRE C-band",
        "percent",
    ],
    "LPRM:LPRM_AMSRE_A_SOILM3.002:sm_x_error": [
        "Soil moisture uncertainty of LPRM AMSRE X-band",
        "percent",
    ],
    "LPRM:LPRM_AMSRE_A_SOILM3.002:soil_moisture_c": [
        "Soil moisture, volumetric, from LPRM AMSRE C-band descending",
        "percent",
    ],
    "LPRM:LPRM_AMSRE_A_SOILM3.002:soil_moisture_x": [
        "Soil moisture, volumetric, from LPRM AMSRE X-band descending",
        "percent",
    ],
    "LPRM:LPRM_AMSRE_A_SOILM3.002:Ts": [
        "Skin temperature (2mm) from LPRM AMSRE descending",
        "K",
    ],
    "LPRM:LPRM_AMSRE_D_RZSM3.001:soilMoisture": [
        "Root Zone Soil Moisture from Palmer Water Balance Model",
        "percent",
    ],
    "LPRM:LPRM_AMSR2_A_SOILM3.001:soil_moisture_c1": [
        "Volumetric Soil Moisture from 6.9 GHZ, ascending",
        "percent",
    ],
    "LPRM:LPRM_AMSR2_D_SOILM3.001:soil_moisture_c1": [
        "Volumetric Soil Moisture from 6.9 GHZ, descending",
        "percent",
    ],
    "LPRM:LPRM_AMSR2_DS_A_SOILM3.001:soil_moisture_c1": [
        "Volumetric Soil Moisture from 6.9 GHZ, ascending",
        "percent",
    ],
    "LPRM:LPRM_AMSR2_DS_D_SOILM3.001:soil_moisture_c1": [
        "Volumetric Soil Moisture from 6.9 GHZ, descending",
        "percent",
    ],
    "LPRM:LPRM_TMI_DY_SOILM3.001:opt_depth_x": [
        "Optical depth from LPRM/TMI/TRMM X-band",
        "unitless",
    ],
    "LPRM:LPRM_TMI_DY_SOILM3.001:sm_x_error": [
        "Uncertainty of Soil Moisture in LPRM/TMI/TRMM X-band",
        "m3/m3",
    ],
    "LPRM:LPRM_TMI_DY_SOILM3.001:soil_moisture_x": [
        "Soil Moisture, Volumetric, from LPRM/TMI/TRMM X-band",
        "percent",
    ],
    "LPRM:LPRM_TMI_DY_SOILM3.001:ts": [
        "Skin temperature (2mm) from LPRM/TMI/TRMM",
        "K",
    ],
    "LPRM:LPRM_TMI_NT_SOILM3.001:opt_depth_x": [
        "Optical depth from LPRM/TMI/TRMM X-band",
        "unitless",
    ],
    "LPRM:LPRM_TMI_NT_SOILM3.001:sm_x_error": [
        "Uncertainty of Soil moisture in LPRM/TMI/TRMM X-band",
        "m3/m3",
    ],
    "LPRM:LPRM_TMI_NT_SOILM3.001:soil_moisture_x": [
        "Volumetric Soil Moisture from LPRM/TMI/TRMM X-band",
        "percent",
    ],
    "LPRM:LPRM_TMI_NT_SOILM3.001:ts": [
        "Skin temperature (2mm) from LPRM/TMI/TRMM",
        "K",
    ],
    "TRMM:TRMM_3B42.7:precipitation": ["Precipitation", "mm/hr"],
    "SMERGE:SMERGE_RZSM0_40CM_2.0:CCI_ano": [
        "CCI derived soil moisture anomalies of 0-40 cm layer",
        "m3/m3",
    ],
    "SMERGE:SMERGE_RZSM0_40CM_2.0:RZSM": [
        "Average soil moisture of 0-40 cm layer",
        "m3/m3",
    ],
    "GRACE:GRACEDADM_CLSM0125US_7D.2:gws_inst": [
        "Groundwater storage percentile",
        "percent",
    ],
    "GRACE:GRACEDADM_CLSM0125US_7D.2:rtzsm_inst": [
        "Root zone soil moisture percentile",
        "percent",
    ],
    "GRACE:GRACEDADM_CLSM0125US_7D.2:sfsm_inst": [
        "Surface soil moisture percentile",
        "percent",
    ],
    "MERRA:M2I1NXLFO.5124:QLML": ["Surface specific humidity, Instantaneous", "1"],
    "MERRA:M2I1NXLFO.5124:TLML": [
        "Surface air temperature over land, Instantaneous",
        "K",
    ],
    "MERRA:M2I1NXLFO.5124:SPEEDLML": ["Surface wind speed, Instantaneous", "m/s"],
    "MERRA:M2T1NXFLX.5124:ULML": ["Surface eastward wind, time average", "m/s"],
    "MERRA:M2T1NXFLX.5124:VLML": ["Surface northward wind, time average", "m/s"],
    "MERRA:M2T1NXLFO.5124:LWGAB": [
        "Surface absorbed longwave radiation, time average",
        "W/m2",
    ],
    "MERRA:M2T1NXLFO.5124:SWGDN": [
        "Incident shortwave radiation land, time average",
        "W/m2",
    ],
    "MERRA:MST1NXMLD.520:BASEFLOW": ["Baseflow", "kg/m2/s"],
    "MERRA:MST1NXMLD.520:LHLAND": ["Latent heat flux from land", "W/m2"],
    "MERRA:MST1NXMLD.520:PRECSNO": ["Surface snowfall", "kg/m2/s"],
    "MERRA:MST1NXMLD.520:PRECTOT": ["Total surface precipitation", "kg/m2/s"],
    "MERRA:MST1NXMLD.520:RUNOFF": ["Overland runoff", "kg/m2/s"],
    "MERRA:MST1NXMLD.520:SFMC": ["Top soil layer soil moisture content", "m3/m3"],
    "MERRA:MST1NXMLD.520:SHLAND": ["Sensible heat flux from land", "W/m2"],
    "MERRA:MST1NXMLD.520:TSOIL1": ["Soil temperature in layer 1", "K"],
}

# LDAS


class LDAS(object):
    def __init__(self, url, **query_params):
        query_params["type"] = "asc2"
        self.url = url
        self.query_params = query_params
        self.query_params["startDate"] = tsutils.parsedate(
            self.query_params["startDate"], strftime="%Y-%m-%dT%H"
        )
        self.query_params["endDate"] = tsutils.parsedate(
            self.query_params["endDate"], strftime="%Y-%m-%dT%H"
        )


# Function to make `resource` know about the new Daymet type.
# http://hydro1.gesdisc.eosdis.nasa.gov/daac-bin/access/timeseries.cgi?variable=GLDAS:GLDAS_NOAH025_3H.001:SOILM10-40cm&location=GEOM:POINT%28-99.875,%2031.125%29&startDate=2010-06-01T09&endDate=2015-05-04T21&type=asc2
#
# https://hydro1.gesdisc.eosdis.nasa.gov/daac-bin/access/timeseries.cgi?variable=NLDAS:NLDAS_FORA0125_H.002:APCPsfc&location=NLDAS:X304-Y071&startDate=2015-01-01T00&endDate=2015-06-20T23&type=asc2
#  http://hydro1.gesdisc.eosdis.nasa.gov/daac-bin/access/timeseries.cgi?variable=NLDAS:NLDAS_FORA0125_H.002:APCPsfc&location=NLDAS:X304-Y071&startDate=2015-01-01T00&endDate=2015-06-20T23&type=asc2


@resource.register(
    r"https://hydro1\.gesdisc\.eosdis\.nasa\.gov/daac-bin/access/timeseries\.cgi.*",
    priority=17,
)
def resource_ldas(uri, **kwargs):
    return LDAS(uri, **kwargs)


def _parse_ldas_dates(date, hour):
    try:
        return pd.to_datetime(date) + pd.to_timedelta(pd.np.int(hour[:-1]), "h")
    except (TypeError, ValueError):
        return pd.NaT


# Function to convert from LDAS type to pd.DataFrame


@convert.register(pd.DataFrame, LDAS)
def ldas_to_df(data, **kwargs):
    req = requests.get(data.url, params=data.query_params)
    if os.path.exists("debug_tsgettoolbox"):
        logging.warning(req.url)
    req.raise_for_status()

    df = pd.read_table(
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
    variable_name = data.query_params["variable"].split(":")[-1]
    unit = _UNITS_MAP[data.query_params["variable"]][1]
    df.columns = ["{0}:{1}".format(variable_name, unit)]
    df.index.name = "Datetime:UTC"
    try:
        return df.tz_localize("UTC")
    except TypeError:  # Already UTC
        return df


if __name__ == "__main__":
    # ?variable=GLDAS:GLDAS_NOAH025_3H.001:SOILM10-40cm&
    # location=GEOM:POINT%28-99.875,%2031.125%29&
    # startDate=2010-06-01T09&endDate=2015-05-04T21&type=asc2
    #
    for key in _UNITS_MAP:
        try:
            r = resource(
                r"https://hydro1.gesdisc.eosdis.nasa.gov/daac-bin/access/timeseries.cgi",
                variable=key,
                location="GEOM:POINT(-100, 31)",
                startDate="2013-06-01T09",
                endDate="2014-05-04T21",
            )

            as_df = odo(r, pd.DataFrame)
        except:
            r = resource(
                r"https://hydro1.gesdisc.eosdis.nasa.gov/daac-bin/access/timeseries.cgi",
                variable=key,
                location="GEOM:POINT(-100, 31)",
                startDate="2002-06-01T09",
                endDate="2003-05-04T21",
            )

            as_df = odo(r, pd.DataFrame)
        print("LDAS", key)
        print(as_df)
#
#     r = resource(
#         r'https://hydro1.gesdisc.eosdis.nasa.gov/daac-bin/access/timeseries.cgi',
#         variable='GLDAS:GLDAS_NOAH025_3H.001:SOILM10-40cm',
#         location='GEOM:POINT(104.2, 35.86)',
#         startDate='2016-01-01T00',
#         endDate='2016-12-01T00'
#     )
#
#     as_df = odo(r, pd.DataFrame)
#     print('LDAS TEST')
#     print(as_df)
#
#     r = resource(
#         r'https://hydro1.gesdisc.eosdis.nasa.gov/daac-bin/access/timeseries.cgi',
#         variable='GLDAS2:GLDAS_NOAH025_3H_v2.1:SOILM10-40cm',
#         location='GEOM:POINT(104.2, 35.86)',
#         startDate='5 years ago',
#         endDate='4 years ago'
#     )
#
#     as_df = odo(r, pd.DataFrame)
#     print('LDAS TEST')
#     print(as_df)
