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
    "GLDAS_NOAH025_3H_2_0_AvgSurfT_inst": ["Average surface skin temperature", "K"],
    "GLDAS_NOAH025_3H_2_0_ESoil_tavg": ["Direct evaporation from bare soil", "W/m**2"],
    "GLDAS_NOAH025_3H_2_0_Evap_tavg": ["Evapotranspiration", "mm/s"],
    "GLDAS_NOAH025_3H_2_0_LWdown_f_tavg": ["Downward long-wave radiation flux", "W/m**2"],
    "GLDAS_NOAH025_3H_2_0_PotEvap_tavg": ["Potential evaporation rate", "W/m**2"],
    "GLDAS_NOAH025_3H_2_0_Psurf_f_inst": ["Surface air pressure", "Pa"],
    "GLDAS_NOAH025_3H_2_0_Qair_f_inst": ["Specific humidity", "kg/kg"],
    "GLDAS_NOAH025_3H_2_0_Qs_acc": ["Storm surface runoff", "mm"],
    "GLDAS_NOAH025_3H_2_0_Qsb_acc": ["Baseflow-groundwater runoff", "mm"],
    "GLDAS_NOAH025_3H_2_0_Qsm_acc": ["Snow melt", "mm"],
    "GLDAS_NOAH025_3H_2_0_Rainf_f_tavg": ["Total precipitation rate", "mm/s"],
    "GLDAS_NOAH025_3H_2_0_Rainf_tavg": ["Rain precipitation rate", "mm/s"],
    "GLDAS_NOAH025_3H_2_0_RootMoist_inst": ["Root zone soil moisture", "mm"],
    "GLDAS_NOAH025_3H_2_0_Snowf_tavg": ["Snow precipitation rate", "mm/s"],
    "GLDAS_NOAH025_3H_2_0_SoilMoi0_10cm_inst": ["Soil moisture content (0-10 cm)", "mm"],
    "GLDAS_NOAH025_3H_2_0_SoilMoi100_200cm_inst": ["Soil moisture content (100-200 cm)", "mm"],
    "GLDAS_NOAH025_3H_2_0_SoilMoi10_40cm_inst": ["Soil moisture content (10-40 cm)", "mm"],
    "GLDAS_NOAH025_3H_2_0_SoilMoi40_100cm_inst": ["Soil moisture content (40-100 cm)", "mm"],
    "GLDAS_NOAH025_3H_2_0_SoilTMP0_10cm_inst": ["Soil temperature (0-10 cm)", "K"],
    "GLDAS_NOAH025_3H_2_0_SoilTMP100_200cm_inst": ["Soil temperature (100-200 cm)", "K"],
    "GLDAS_NOAH025_3H_2_0_SoilTMP10_40cm_inst": ["Soil temperature (10-40 cm)", "K"],
    "GLDAS_NOAH025_3H_2_0_SWdown_f_tavg": ["Downward shortwave radiation flux", "W/m**2"],
    "GLDAS_NOAH025_3H_2_0_Tair_f_inst": ["Near surface air temperature", "K"],
    "GLDAS_NOAH025_3H_2_0_Wind_f_inst": ["Near surface wind speed", "m/s"],
}

_GLDAS_NOAH_v2_1 = {
    "GLDAS_NOAH025_3H_2_1_Albedo_inst": ["Albedo", "percent"],
    "GLDAS_NOAH025_3H_2_1_AvgSurfT_inst": ["Average surface skin temperature", "K"],
    "GLDAS_NOAH025_3H_2_1_CanopInt_inst": ["Plant canopy surface_water", "kg/m**2"],
    "GLDAS_NOAH025_3H_2_1_ECanop_tavg": ["Canopy water evaporation", "W/m**2"],
    "GLDAS_NOAH025_3H_2_1_ESoil_tavg": ["Soil evaporation", "mm/s"],
    "GLDAS_NOAH025_3H_2_1_Evap_tavg": ["Evapotranspiration", "mm/s"],
    "GLDAS_NOAH025_3H_2_1_LWdown_f_tavg": ["Downward long-wave radiation flux", "W/m**2"],
    "GLDAS_NOAH025_3H_2_1_Lwnet_tavg": ["Net long-wave radiation flux", "W/m**2"],
    "GLDAS_NOAH025_3H_2_1_PotEvap_tavg": ["Potential evaporation", "mm/s"],
    "GLDAS_NOAH025_3H_2_1_Psurf_f_inst": ["Surface air pressure", "Pa"],
    "GLDAS_NOAH025_3H_2_1_Qair_f_inst": ["Specific humidity", "kg/kg"],
    "GLDAS_NOAH025_3H_2_1_Qg_tavg": ["Heat flux", "W/m**2"],
    "GLDAS_NOAH025_3H_2_1_Qh_tavg": ["Sensible heat net flux", "W/m**2"],
    "GLDAS_NOAH025_3H_2_1_Qle_tavg": ["Latent heat net flux", "W/m**2"],
    "GLDAS_NOAH025_3H_2_1_Qs_acc": ["Storm surface runoff", "mm"],
    "GLDAS_NOAH025_3H_2_1_Qsb_acc": ["Baseflow-groundwater runoff", "mm"],
    "GLDAS_NOAH025_3H_2_1_Qsm_acc": ["Snow melt", "mm"],
    "GLDAS_NOAH025_3H_2_1_Rainf_f_tavg": ["Total precipitation rate", "mm/s"],
    "GLDAS_NOAH025_3H_2_1_Rainf_tavg": ["Rain precipitation rate", "mm/s"],
    "GLDAS_NOAH025_3H_2_1_RootMoist_inst": ["Root zone soil moisture", "mm"],
    "GLDAS_NOAH025_3H_2_1_SnowDepth_inst": ["Snow depth", "m"],
    "GLDAS_NOAH025_3H_2_1_Snowf_tavg": ["Snow precipitation rate", "mm/s"],
    "GLDAS_NOAH025_3H_2_1_SoilMoi0_10cm_inst": ["Soil moisture content (0-10 cm)", "mm"],
    "GLDAS_NOAH025_3H_2_1_SoilMoi100_200cm_inst": ["Soil moisture content (100-200 cm)", "mm"],
    "GLDAS_NOAH025_3H_2_1_SoilMoi10_40cm_inst": ["Soil moisture content (10-40 cm)", "mm"],
    "GLDAS_NOAH025_3H_2_1_SoilMoi40_100cm_inst": ["Soil moisture content (40-100 cm)", "mm"],
    "GLDAS_NOAH025_3H_2_1_SoilTMP0_10cm_inst": ["Soil temperature (0-10 cm)", "K"],
    "GLDAS_NOAH025_3H_2_1_SoilTMP100_200cm_inst": ["Soil temperature (100-200 cm)", "K"],
    "GLDAS_NOAH025_3H_2_1_SoilTMP10_40cm_inst": ["Soil temperature (10-40 cm)", "K"],
    "GLDAS_NOAH025_3H_2_1_SoilTMP40_100cm_inst": ["Soil temperature (40-100 cm)", "K"],
    "GLDAS_NOAH025_3H_2_1_SWdown_f_tavg": ["Downward shortwave radiation flux", "W/m**2"],
    "GLDAS_NOAH025_3H_2_1_SWE_inst": ["Snow depth water equivalent", "mm"],
    "GLDAS_NOAH025_3H_2_1_Swnet_tavg": ["Net shortwave radiation flux", "W/m**2"],
    "GLDAS_NOAH025_3H_2_1_Tair_f_inst": ["Near surface air temperature", "K"],
    "GLDAS_NOAH025_3H_2_1_Tveg_tavg": ["Transpiration", "W/m**2"],
    "GLDAS_NOAH025_3H_2_1_Wind_f_inst": ["Near surface wind speed", "m/s"],
}

_GRACE = {
    "GRACEDADM_CLSM0125US_7D_4_0_gws_inst": ["Groundwater storage percentile", "percent"],
    "GRACEDADM_CLSM0125US_7D_4_0_rtzsm_inst": ["Root zone soil moisture percentile", "percent"],
    "GRACEDADM_CLSM0125US_7D_4_0_sfsm_inst": ["Surface soil moisture percentile", "percent"],
}

_MERRA = {
    "M2I1NXLFO_5_12_4_HLML": ["Surface layer height:instant", "m"],
    "M2I1NXLFO_5_12_4_PS": ["Surface pressure:instant", "Pa"],
    "M2I1NXLFO_5_12_4_QLML": ["Surface specific humidity:instant", "1"],
    "M2I1NXLFO_5_12_4_SPEEDLML": ["Surface wind speed:instant", "m/s"],
    "M2I1NXLFO_5_12_4_TLML": ["Surface air temperature over land:instant", "K"],
    "M2T1NXFLX_5_12_4_BSTAR": ["Surface buoyancy scale:average", "m/s**2"],
    "M2T1NXFLX_5_12_4_CDH": ["Surface exchange coefficient for heat:average", "mm/s"],
    "M2T1NXFLX_5_12_4_CDM": ["Surface exchange coefficient for momentum:average", "mm/s"],
    "M2T1NXFLX_5_12_4_CDQ": ["Surface exchange coefficient for moisture:average", "mm/s"],
    "M2T1NXFLX_5_12_4_CN": ["Surface neutral drag coefficient:average", "1"],
    "M2T1NXFLX_5_12_4_DISPH": ["Zero plane displacement height:average", "m"],
    "M2T1NXFLX_5_12_4_EFLUX": ["Total latent energy flux:average", "W/m**2"],
    "M2T1NXFLX_5_12_4_EVAP": ["Evaporation from turbulence:average", "mm/s"],
    "M2T1NXFLX_5_12_4_FRCAN": ["Areal fraction of anvil showers:average", "1"],
    "M2T1NXFLX_5_12_4_FRCCN": ["Areal fraction of convective showers:average", "1"],
    "M2T1NXFLX_5_12_4_FRCLS": ["Areal fraction of nonanvil large scale showers:average", "1"],
    "M2T1NXFLX_5_12_4_FRSEAICE": ["Ice covered fraction of tile:average", "1"],
    "M2T1NXFLX_5_12_4_GHTSKIN": ["ground heating for skin temp:average", "W/m**2"],
    "M2T1NXFLX_5_12_4_HFLUX": ["Sensible heat flux from turbulence:average", "W/m**2"],
    "M2T1NXFLX_5_12_4_HLML": ["Surface layer height:average", "m"],
    "M2T1NXFLX_5_12_4_NIRDF": ["Surface downwelling nearinfrared diffuse flux:average", "W/m**2"],
    "M2T1NXFLX_5_12_4_NIRDR": ["Surface downwelling nearinfrared beam flux:average", "W/m**2"],
    "M2T1NXFLX_5_12_4_PBLH": ["Planetary boundary layer height:average", "m"],
    "M2T1NXFLX_5_12_4_PGENTOT": ["total column production of precipitation:average", "mm/s"],
    "M2T1NXFLX_5_12_4_PRECANV": ["Anvil precipitation:average", "mm/s"],
    "M2T1NXFLX_5_12_4_PRECCON": ["Convective precipitation:average", "mm/s"],
    "M2T1NXFLX_5_12_4_PRECLSC": ["Non-anvil large scale precipitation:average", "mm/s"],
    "M2T1NXFLX_5_12_4_PRECSNO": ["Snowfall:average", "mm/s"],
    "M2T1NXFLX_5_12_4_PRECTOTCORR": ["Total precipitation:average", "mm/s"],
    "M2T1NXFLX_5_12_4_PRECTOT": ["Total precipitation:average", "mm/s"],
    "M2T1NXFLX_5_12_4_PREVTOT": ["total column re-evap/subl of precipitation:average", "mm/s"],
    "M2T1NXFLX_5_12_4_QLML": ["Surface specific humidity:average", "1"],
    "M2T1NXFLX_5_12_4_QSH": ["Effective surface specific humidity:average", "kg/kg"],
    "M2T1NXFLX_5_12_4_QSTAR": ["Surface moisture scale:average", "kg/kg"],
    "M2T1NXFLX_5_12_4_RHOA": ["Air density at surface:average", "kg/m**3"],
    "M2T1NXFLX_5_12_4_RISFC": ["Surface bulk Richardson number:average", "1"],
    "M2T1NXFLX_5_12_4_SPEEDMAX": ["Surface wind speed:max", "m/s"],
    "M2T1NXFLX_5_12_4_SPEED": ["Surface wind speed:average", "m/s"],
    "M2T1NXFLX_5_12_4_TAUGWX": ["Surface eastward gravity wave stress:average", "N/m**2"],
    "M2T1NXFLX_5_12_4_TAUGWY": ["Surface northward gravity wave stress:average", "N/m**2"],
    "M2T1NXFLX_5_12_4_TAUX": ["Eastward surface stress:average", "N/m**2"],
    "M2T1NXFLX_5_12_4_TAUY": ["Northward surface stress:average", "N/m**2"],
    "M2T1NXFLX_5_12_4_TCZPBL": ["Transcom planetary boundary layer height:average", "m"],
    "M2T1NXFLX_5_12_4_TLML": ["Surface air temperature:average", "K"],
    "M2T1NXFLX_5_12_4_TSH": ["Effective surface skin temperature:average", "K"],
    "M2T1NXFLX_5_12_4_TSTAR": ["Surface temperature scale:average", "K"],
    "M2T1NXFLX_5_12_4_ULML": ["Surface eastward wind:average", "m/s"],
    "M2T1NXFLX_5_12_4_USTAR": ["Surface velocity scale:average", "m/s"],
    "M2T1NXFLX_5_12_4_VLML": ["Surface northward wind:average", "m/s"],
    "M2T1NXFLX_5_12_4_Z0H": ["Surface roughness for heat:average", "m"],
    "M2T1NXFLX_5_12_4_Z0M": ["Surface roughness:average", "m"],
    "M2T1NXLFO_5_12_4_LWGAB": ["Surface absorbed longwave radiation:average", "W/m**2"],
    "M2T1NXLFO_5_12_4_PARDF": ["surface downwelling par diffuse flux:average", "W/m**2"],
    "M2T1NXLFO_5_12_4_PARDR": ["surface downwelling par beam flux:average", "W/m**2"],
    "M2T1NXLFO_5_12_4_PRECCUCORR": ["liquid water convective precipitation:average", "mm/s"],
    "M2T1NXLFO_5_12_4_PRECLSCORR": ["liquid water large scale precipitation:average", "mm/s"],
    "M2T1NXLFO_5_12_4_PRECSNOCORR": ["Snowfall:average", "mm/s"],
    "M2T1NXLFO_5_12_4_SWGDN": ["Incident shortwave radiation land:average", "W/m**2"],
    "M2T1NXLFO_5_12_4_SWLAND": ["Net shortwave land:average", "W/m**2"],
    "M2T1NXSLV_5_12_4_CLDPRS": ["Cloud top pressure", "Pa"],
    "M2T1NXSLV_5_12_4_CLDTMP": ["Cloud top temperature", "K"],
    "M2T1NXSLV_5_12_4_DISPH": ["Zero plane displacement height", "m"],
    "M2T1NXSLV_5_12_4_H1000": ["Height at 1000 mb", "m"],
    "M2T1NXSLV_5_12_4_H250": ["Height at 250 hPa", "m"],
    "M2T1NXSLV_5_12_4_H500": ["Height at 500 hPa", "m"],
    "M2T1NXSLV_5_12_4_H850": ["Height at 850 hPa", "m"],
    "M2T1NXSLV_5_12_4_OMEGA500": ["Omega at 500 hPa", "Pa/s"],
    "M2T1NXSLV_5_12_4_PBLTOP": ["Pbltop pressure", "Pa"],
    "M2T1NXSLV_5_12_4_PS": ["Surface pressure", "Pa"],
    "M2T1NXSLV_5_12_4_Q250": ["Specific humidity at 250 hPa", "kg/kg"],
    "M2T1NXSLV_5_12_4_Q500": ["Specific humidity at 500 hPa", "kg/kg"],
    "M2T1NXSLV_5_12_4_Q850": ["Specific humidity at 850 hPa", "kg/kg"],
    "M2T1NXSLV_5_12_4_QV10M": ["10-meter specific humidity", "kg/kg"],
    "M2T1NXSLV_5_12_4_QV2M": ["2-meter specific humidity", "kg/kg"],
    "M2T1NXSLV_5_12_4_SLP": ["Sea level pressure", "Pa"],
    "M2T1NXSLV_5_12_4_T10M": ["10-meter air temperature", "K"],
    "M2T1NXSLV_5_12_4_T250": ["Air temperature at 250 hPa", "K"],
    "M2T1NXSLV_5_12_4_T2M": ["2-meter air temperature", "K"],
    "M2T1NXSLV_5_12_4_T2MDEW": ["Dew point temperature at 2 m", "K"],
    "M2T1NXSLV_5_12_4_T2MWET": ["Wet bulb temperature at 2 m", "K"],
    "M2T1NXSLV_5_12_4_T500": ["Air temperature at 500 hPa", "K"],
    "M2T1NXSLV_5_12_4_T850": ["Air temperature at 850 hPa", "K"],
    "M2T1NXSLV_5_12_4_TO3": ["Total column ozone", "Dobsons"],
    "M2T1NXSLV_5_12_4_TOX": ["Total column odd oxygen", "mm"],
    "M2T1NXSLV_5_12_4_TQI": ["Total precipitable ice water", "mm"],
    "M2T1NXSLV_5_12_4_TQL": ["Total precipitable liquid water", "mm"],
    "M2T1NXSLV_5_12_4_TQV": ["Total precipitable water vapor", "mm"],
    "M2T1NXSLV_5_12_4_TROPPB": ["Tropopause pressure based on blended estimate", "Pa"],
    "M2T1NXSLV_5_12_4_TROPPT": ["Tropopause pressure based on thermal estimate", "Pa"],
    "M2T1NXSLV_5_12_4_TROPPV": ["Tropopause pressure based on EPV estimate", "Pa"],
    "M2T1NXSLV_5_12_4_TROPQ": ["Tropopause specific humidity using blended TROPP estimate", "kg/kg"],
    "M2T1NXSLV_5_12_4_TROPT": ["Tropopause temperature using blended TROPP estimate", "K"],
    "M2T1NXSLV_5_12_4_TS": ["Surface skin temperature", "K"],
    "M2T1NXSLV_5_12_4_U10M": ["10-meter eastward wind", "m/s"],
    "M2T1NXSLV_5_12_4_U250": ["Eastward wind at 250 hPa", "m/s"],
    "M2T1NXSLV_5_12_4_U2M": ["2-meter eastward wind", "m/s"],
    "M2T1NXSLV_5_12_4_U500": ["Eastward wind at 500 hPa", "m/s"],
    "M2T1NXSLV_5_12_4_U50M": ["50-meter eastward wind:time average", "m/s"],
    "M2T1NXSLV_5_12_4_U850": ["Eastward wind at 850 hPa", "m/s"],
    "M2T1NXSLV_5_12_4_V10M": ["10-meter northward wind", "m/s"],
    "M2T1NXSLV_5_12_4_V250": ["Northward wind at 250 hPa", "m/s"],
    "M2T1NXSLV_5_12_4_V2M": ["2-meter northward wind", "m/s"],
    "M2T1NXSLV_5_12_4_V500": ["Northward wind at 500 hPa", "m/s"],
    "M2T1NXSLV_5_12_4_V50M": ["50-meter northward wind:time average", "m/s"],
    "M2T1NXSLV_5_12_4_V850": ["Northward wind at 850 hPa", "m/s"],
    "M2T1NXSLV_5_12_4_ZLCL": ["Lifting condensation level", "m"],
    }

_NLDAS_FORA = {
    "NLDAS_FORA0125_H_2_0_CAPE": ["Convective Available Potential Energy", "J/kg"],
    "NLDAS_FORA0125_H_2_0_CRainf_frac": ["Fraction of total precipitation that is convective", "fraction"],
    "NLDAS_FORA0125_H_2_0_LWdown": ["Surface DW longwave radiation flux", "W/m**2"],
    "NLDAS_FORA0125_H_2_0_PotEvap": ["Potential evaporation", "mm"],
    "NLDAS_FORA0125_H_2_0_PSurf": ["Surface pressure", "Pa"],
    "NLDAS_FORA0125_H_2_0_Qair": ["2-m above ground specific humidity", "kg/kg"],
    "NLDAS_FORA0125_H_2_0_Rainf": ["Precipitation hourly total", "mm"],
    "NLDAS_FORA0125_H_2_0_SWdown": ["Surface DW shortwave radiation flux", "W/m**2"],
    "NLDAS_FORA0125_H_2_0_Tair": ["2-m above ground temperature", "K"],
    "NLDAS_FORA0125_H_2_0_Wind_E": ["10-m above ground zonal wind", "m/s"],
    "NLDAS_FORA0125_H_2_0_Wind_N": ["10-m above ground meridional wind", "m/s"],
}

_NLDAS_MOSAIC = {
    "NLDAS_MOS0125_H_2_0_ACond": ["Aerodynamic conductance", "m/s"],
    "NLDAS_MOS0125_H_2_0_Albedo": ["Surface albedo", "%"],
    "NLDAS_MOS0125_H_2_0_AvgSurfT": ["Average surface skin temperature", "K"],
    "NLDAS_MOS0125_H_2_0_CanopInt": ["Plant canopy surface water", "kg/m**2"],
    "NLDAS_MOS0125_H_2_0_CCond": ["Canopy conductance", "m/s"],
    "NLDAS_MOS0125_H_2_0_ECanop": ["Canopy water evaporation", "W/m**2"],
    "NLDAS_MOS0125_H_2_0_ESoil": ["Direct evaporation from bare soil", "W/m**2"],
    "NLDAS_MOS0125_H_2_0_Evap": ["Total evapotranspiration", "mm"],
    "NLDAS_MOS0125_H_2_0_GVEG": ["Green vegetation", "fraction"],
    "NLDAS_MOS0125_H_2_0_LAI": ["Leaf Area Index", "unitless"],
    "NLDAS_MOS0125_H_2_0_LWdown": ["Longwave radiation flux downwards (surface)", "W/m**2"],
    "NLDAS_MOS0125_H_2_0_LWnet": ["Net longwave radiation flux (surface)", "W/m**2"],
    "NLDAS_MOS0125_H_2_0_Qf": ["Snow phase-change heat flux", "W/m**2"],
    "NLDAS_MOS0125_H_2_0_Qg": ["Ground heat flux", "W/m**2"],
    "NLDAS_MOS0125_H_2_0_Qh": ["Sensible heat flux", "W/m**2"],
    "NLDAS_MOS0125_H_2_0_Qle": ["Latent heat flux", "W/m**2"],
    "NLDAS_MOS0125_H_2_0_Qsb": ["Subsurface runoff (baseflow)", "mm"],
    "NLDAS_MOS0125_H_2_0_Qsm": ["Snowmelt", "kg/m**2"],
    "NLDAS_MOS0125_H_2_0_Qs": ["Surface runoff (non-infiltrating)", "mm"],
    "NLDAS_MOS0125_H_2_0_Rainf": ["Liquid precipitation (rainfall)", "kg/m**2"],
    "NLDAS_MOS0125_H_2_0_SMAvail_0_200cm": ["Soil moisture availability (0-200cm)", "%"],
    "NLDAS_MOS0125_H_2_0_SMAvail_0_40cm": ["Soil moisture availability (0-40cm)", "%"],
    "NLDAS_MOS0125_H_2_0_SnowDepth": ["Snow depth", "m"],
    "NLDAS_MOS0125_H_2_0_Snowf": ["Frozen precipitation (snowfall)", "kg/m**2"],
    "NLDAS_MOS0125_H_2_0_SnowFrac": ["Snow cover", "fraction"],
    "NLDAS_MOS0125_H_2_0_SoilM_0_100cm": ["0-100 cm soil moisture content", "mm"],
    "NLDAS_MOS0125_H_2_0_SoilM_0_10cm": ["0-10 cm soil moisture content", "mm"],
    "NLDAS_MOS0125_H_2_0_SoilM_0_200cm": ["0-200 cm soil moisture content", "mm"],
    "NLDAS_MOS0125_H_2_0_SoilM_0_40cm": ["Soil moisture content (0-40cm)", "kg/m**2"],
    "NLDAS_MOS0125_H_2_0_SoilM_10_40cm": ["10-40 cm soil moisture content", "mm"],
    "NLDAS_MOS0125_H_2_0_SoilM_40_200cm": ["40-200 cm soil moisture content", "mm"],
    "NLDAS_MOS0125_H_2_0_SoilT": ["Soil temperature", "K"],
    "NLDAS_MOS0125_H_2_0_Streamflow": ["Streamflow", "m**3/s"],
    "NLDAS_MOS0125_H_2_0_SubSnow": ["Sublimation (evaporation from snow)", "W/m**2"],
    "NLDAS_MOS0125_H_2_0_SWdown": ["Shortwave radiation flux downwards (surface)", "W/m**2"],
    "NLDAS_MOS0125_H_2_0_SWE": ["Snow Water Equivalent", "kg/m**2"],
    "NLDAS_MOS0125_H_2_0_SWnet": ["Net shortwave radiation flux (surface)", "W/m**2"],
    "NLDAS_MOS0125_H_2_0_TVeg": ["Transpiration", "W/m**2"],
    }

_NLDAS_NOAH = {
    "NLDAS_NOAH0125_H_2_0_ACond": ["Aerodynamic conductance", "m/s"],
    "NLDAS_NOAH0125_H_2_0_Albedo": ["Surface albedo", "percent"],
    "NLDAS_NOAH0125_H_2_0_AvgSurfT": ["Average surface skin temperature", "K"],
    "NLDAS_NOAH0125_H_2_0_CanopInt": ["Plant canopy surface water", "mm"],
    "NLDAS_NOAH0125_H_2_0_CCond": ["Canopy conductance", "m/s"],
    "NLDAS_NOAH0125_H_2_0_ECanop": ["Canopy water evaporation", "W/m**2"],
    "NLDAS_NOAH0125_H_2_0_ESoil": ["Direct evaporation from bare soil", "W/m**2"],
    "NLDAS_NOAH0125_H_2_0_Evap": ["Total evapotranspiration", "mm"],
    "NLDAS_NOAH0125_H_2_0_GVEG": ["Green vegetation", "fraction"],
    "NLDAS_NOAH0125_H_2_0_LAI": ["Leaf Area Index", "unitless"],
    "NLDAS_NOAH0125_H_2_0_LWdown": ["Surface downwards longwave radiation flux", "W/m**2"],
    "NLDAS_NOAH0125_H_2_0_LWnet": ["Surface net longwave radiation flux", "W/m**2"],
    "NLDAS_NOAH0125_H_2_0_PotEvap": ["Potential evapotranspiration", "W/m**2"],
    "NLDAS_NOAH0125_H_2_0_Qf": ["Snow phase-change heat flux", "W/m**2"],
    "NLDAS_NOAH0125_H_2_0_Qg": ["Ground heat flux", "W/m**2"],
    "NLDAS_NOAH0125_H_2_0_Qh": ["Sensible heat flux", "W/m**2"],
    "NLDAS_NOAH0125_H_2_0_Qle": ["Latent heat flux", "W/m**2"],
    "NLDAS_NOAH0125_H_2_0_Qsb": ["Subsurface runoff (baseflow)", "mm"],
    "NLDAS_NOAH0125_H_2_0_Qsm": ["Snowmelt", "mm"],
    "NLDAS_NOAH0125_H_2_0_Qs": ["Surface runoff (non-infiltrating)", "mm"],
    "NLDAS_NOAH0125_H_2_0_Rainf": ["Liquid precipitation", "mm"],
    "NLDAS_NOAH0125_H_2_0_RCQ": ["Humidity parameter in canopy conductance", "fraction"],
    "NLDAS_NOAH0125_H_2_0_RCSOL": ["Soil moisture parameter in canopy conductance", "fraction"],
    "NLDAS_NOAH0125_H_2_0_RCS": ["Solar parameter in canopy conductance", "fraction"],
    "NLDAS_NOAH0125_H_2_0_RCT": ["Temperature parameter in canopy conductance", "fraction"],
    "NLDAS_NOAH0125_H_2_0_RootMoist": ["Root zone soil moisture", "mm"],
    "NLDAS_NOAH0125_H_2_0_RSMacr": ["Relative soil moisture availability control factor", "fraction"],
    "NLDAS_NOAH0125_H_2_0_RSmin": ["Minimal stomatal resistance", "s/m"],
    "NLDAS_NOAH0125_H_2_0_SMAvail_0_100cm": ["Soil moisture availability (0-100cm)", "percent"],
    "NLDAS_NOAH0125_H_2_0_SMAvail_0_200cm": ["Soil moisture availability (0-200cm)", "percent"],
    "NLDAS_NOAH0125_H_2_0_SMLiq_0_10cm": ["Liquid soil moisture content (0-10cm)", "mm"],
    "NLDAS_NOAH0125_H_2_0_SMLiq_100_200cm": ["Liquid soil moisture content (100-200cm)", "mm"],
    "NLDAS_NOAH0125_H_2_0_SMLiq_10_40cm": ["Liquid soil moisture content (10-40cm)", "mm"],
    "NLDAS_NOAH0125_H_2_0_SMLiq_40_100cm": ["Liquid soil moisture content (40-100cm)", "mm"],
    "NLDAS_NOAH0125_H_2_0_SnowDepth": ["Snow depth", "m"],
    "NLDAS_NOAH0125_H_2_0_Snowf": ["Frozen precipitation", "mm"],
    "NLDAS_NOAH0125_H_2_0_SnowFrac": ["Snow cover", "fraction"],
    "NLDAS_NOAH0125_H_2_0_SoilM_0_100cm": ["0-100 cm soil moisture content", "mm"],
    "NLDAS_NOAH0125_H_2_0_SoilM_0_10cm": ["0-10 cm soil moisture content", "mm"],
    "NLDAS_NOAH0125_H_2_0_SoilM_0_200cm": ["0-200 cm soil moisture content", "mm"],
    "NLDAS_NOAH0125_H_2_0_SoilM_100_200cm": ["100-200 cm soil moisture content", "mm"],
    "NLDAS_NOAH0125_H_2_0_SoilM_10_40cm": ["10-40 cm soil moisture content", "mm"],
    "NLDAS_NOAH0125_H_2_0_SoilM_40_100cm": ["40-100 cm soil moisture content", "mm"],
    "NLDAS_NOAH0125_H_2_0_SoilT_0_10cm": ["0-10 cm soil temperature", "K"],
    "NLDAS_NOAH0125_H_2_0_SoilT_100_200cm": ["100-200 cm soil temperature", "K"],
    "NLDAS_NOAH0125_H_2_0_SoilT_10_40cm": ["10-40 cm soil temperature", "K"],
    "NLDAS_NOAH0125_H_2_0_SoilT_40_100cm": ["40-100 cm soil temperature", "K"],
    "NLDAS_NOAH0125_H_2_0_Streamflow": ["Streamflow", "m**3/s"],
    "NLDAS_NOAH0125_H_2_0_SubSnow": ["Sublimation (evaporation from snow)", "W/m**2"],
    "NLDAS_NOAH0125_H_2_0_SWdown": ["Surface downwards shortwave radiation flux", "W/m**2"],
    "NLDAS_NOAH0125_H_2_0_SWE": ["Snow Water Equivalent", "mm"],
    "NLDAS_NOAH0125_H_2_0_SWnet": ["Surface net shortwave radiation flux", "W/m**2"],
    "NLDAS_NOAH0125_H_2_0_TVeg": ["Transpiration", "W/m**2"],
}

_NLDAS_VIC = {
    "NLDAS_VIC0125_H_2_0_Evap": ["Total evapotranspiration", "mm"],
    "NLDAS_VIC0125_H_2_0_Qg": ["Ground heat flux", "W/m**2"],
    "NLDAS_VIC0125_H_2_0_Qh": ["Sensible heat flux", "W/m**2"],
    "NLDAS_VIC0125_H_2_0_Qle": ["Latent heat flux", "W/m**2"],
    "NLDAS_VIC0125_H_2_0_Qsb": ["Subsurface runoff (baseflow)", "mm"],
    "NLDAS_VIC0125_H_2_0_Qs": ["Surface runoff (non-infiltrating)", "mm"],
    "NLDAS_VIC0125_H_2_0_SoilM_0_100cm": ["0-100 cm soil moisture content", "mm"],
    "NLDAS_VIC0125_H_2_0_SoilM_layer1": ["VIC layer 1 soil moisture content", "mm"],
    "NLDAS_VIC0125_H_2_0_SoilM_layer2": ["VIC layer 2 soil moisture content", "mm"],
    "NLDAS_VIC0125_H_2_0_SoilM_layer3": ["VIC layer 3 soil moisture content", "mm"],
    "NLDAS_VIC0125_H_2_0_SoilM_total": ["VIC total column depth soil moisture content", "mm"],
    "NLDAS_VIC0125_H_2_0_SoilT_layer1": ["VIC layer 1 soil temperature", "K"],
    "NLDAS_VIC0125_H_2_0_SoilT_layer2": ["VIC layer 3 soil temperature", "K"],
    "NLDAS_VIC0125_H_2_0_SoilT_layer3": ["VIC layer 3 soil temperature", "K"],
}


_SMERGE = {
    "SMERGE_RZSM0_40CM_2_0_CCI_ano": ["CCI soil moisture anomalies 0-40 cm", "m3/m3"],
    "SMERGE_RZSM0_40CM_2_0_RZSM": ["Average soil moisture of 0-40 cm layer", "m3/m3"],
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

_project_lat_ranges = {
    "GLDAS2_v2_0": (-60, 90),
    "GLDAS2_v2_1": (-60, 90),
    "GRACE": (25, 53),
    "MERRA": (-90, 90),
    "NLDAS": (25, 53),
    "NLDAS2": (25, 53),
    "SMERGE": (25, 53),
}

_project_lon_ranges = {
    "GLDAS2_v2_0": (-180, 180),
    "GLDAS2_v2_1": (-180, 180),
    "GRACE": (-125, -67),
    "MERRA": (-180, 180),
    "NLDAS": (-125, -67),
    "NLDAS2": (-125, -67),
    "SMERGE": (-125, -67),
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
    "NLDAS": 16,
    "NLDAS2": 16,
    "SMERGE": 16,
}

_project_index_col = {
    "GLDAS2_v2_0": 0,
    "GLDAS2_v2_1": 0,
    "GRACE": "Datetime",
    "MERRA": "Datetime",
    "NLDAS": 0,
    "NLDAS2": 0,
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


def foundation_api(
    units_table="",
    first_line="",
    meta_table="",
    description="",
):
    """Create a foundation API function returning a function."""

    @tsutils.doc(
        {
            "units_table": units_table,
            "first_line": first_line,
            "meta_table": meta_table,
            "description": description,
        }
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

        The time zone is always UTC.

        ${description}

        ${meta_table}

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

        +---------------------------+-------------+-----------+-----------+---------------+
        | Description/Name          | Spatial     | Lat Range | Lon Range | Time          |
        +===========================+=============+===========+===========+===============+"""

_GLDAS_NOAH_v2_0_META = r"""
        | GLDAS Noah Land Surface   | 0.25x0.25   | -60, 90   | -180, 180 | 3 hour        |
        | Model                     |             |           |           | 1948-01-01 to |
        | GLDAS_NOAH025_3H          |             |           |           | 2014-12-31    |
        | V2.0                      |             |           |           |               |
        +---------------------------+-------------+-----------+-----------+---------------+"""
_GLDAS_NOAH_v2_1_META = r"""
        | GLDAS Noah Land Surface   | 0.25x0.25   | -60, 90   | -180, 180 | 3 hour        |
        | Model                     |             |           |           | 2000-01-01 to |
        | GLDAS_NOAH025_3H          |             |           |           | present       |
        | V2.1                      |             |           |           |               |
        +---------------------------+-------------+-----------+-----------+---------------+"""
_GRACE_META = r"""
        | Groundwater and Soil      | 0.125x0.125 | 25, 53    | -125, -67 | 7 day         |
        | Moisture Conditions from  |             |           |           | 2002-10-04 to |
        | GRACE Data Assimilation   |             |           |           | recent        |
        | GRACEDADM_CLSM0125US_7D   |             |           |           |               |
        | V4.0                      |             |           |           |               |
        +---------------------------+-------------+-----------+-----------+---------------+"""
_MERRA_META = r"""
        | MERRA-2 2D, Instantaneous | 0.5x0.625   | -90, 90   | -180, 180 | 1 hour        |
        | Land Surface Forcings     |             |           |           | 1980-01-01 to |
        | M2I1NXLFO                 |             |           |           | recent        |
        | V5.12.4                   |             |           |           |               |
        +---------------------------+-------------+-----------+-----------+---------------+
        | MERRA-2 2D, Time-averaged | 0.5x0.625   | -90, 90   | -180, 180 | 1 hour        |
        | Surface Flux Diagnostics  |             |           |           | 1980-01-01 to |
        | M2T1NXFLX                 |             |           |           | recent        |
        | V5.12.4                   |             |           |           |               |
        +---------------------------+-------------+-----------+-----------+---------------+
        | MERRA-2 2D, Time-averaged | 0.5x0.625   | -90, 90   | -180, 180 | 1 hour        |
        | Land Surface Forcings     |             |           |           | 1980-01-01 to |
        | M2T1NXLFO                 |             |           |           | recent        |
        | V5.12.4                   |             |           |           |               |
        +---------------------------+-------------+-----------+-----------+---------------+"""
_NLDAS_FORA_META = r"""
        | NLDAS Primary Forcing     | 0.125x0.125 | 25, 53    | -125, -67 | 1 hour        |
        | Data                      |             |           |           | 1979-01-01T13 |
        | NLDAS_FORA0125_H          |             |           |           | till recent   |
        | V2.0                      |             |           |           |               |
        +---------------------------+-------------+-----------+-----------+---------------+"""
_NLDAS_NOAH_META = r"""
        | NLDAS Noah Land Surface   | 0.125x0.125 | 25, 53    | -125, -67 | 1 hour        |
        | Model                     |             |           |           | 1979-01-01T13 |
        | NLDAS_NOAH0125_H          |             |           |           |               |
        | V002                      |             |           |           |               |
        +---------------------------+-------------+-----------+-----------+---------------+"""
_NLDAS_VIC_META = r"""
        | NLDAS VIC Land Surface    | 0.125x0.125 | 25, 53    | -125, -67 | 1 hour        |
        | Model                     |             |           |           | 1979-01-01T13 |
        | NLDAS_VIC0125_H           |             |           |           | till recent   |
        | V002                      |             |           |           |               |
        +---------------------------+-------------+-----------+-----------+---------------+"""
_SMERGE_META = r"""
        | Smerge-Noah-CCI root zone | 0.125x0.125 | 25, 53    | -125, -67 | 1 day         |
        | soil moisture 0-40 cm     |             |           |           | 1979-01-02 to |
        | SMERGE_RZSM0_40CM         |             |           |           | recent        |
        | V2.0                      |             |           |           |               |
        +---------------------------+-------------+-----------+-----------+---------------+"""

GLDAS_NOAH_v2_0_FIRST_LINE = (
    "global:0.25deg:1948-2014:3H:GLDAS NOAH hydrology model results"
)
GLDAS_NOAH_v2_1_FIRST_LINE = (
    "global:0.25deg:2000-:3H:GLDAS NOAH hydrology model results"
)
GRACE_FIRST_LINE = "NAmerica:0.125deg:2002-:7D:Groundwater and soil moisture from GRACE"
LDAS_FIRST_LINE = "global:grid:::Land Data Assimilation System, deprecated, use one of the ldas_* functions instead"
MERRA_FIRST_LINE = "global:0.5x0.625deg:1980-:H:MERRA-2 Land surface forcings"
NLDAS_FORA_FIRST_LINE = "NAmerica:0.125deg:1979-:H:NLDAS Weather Forcing A (surface)"
NLDAS_NOAH_FIRST_LINE = "NAmerica:0.125deg:1979-:H:NLDAS NOAH hydrology model results"
NLDAS_VIC_FIRST_LINE = "NAmerica:0.125deg:1979-:H:NLDAS VIC hydrology model results"
SMERGE_FIRST_LINE = "global:0.125deg:1997-:D:SMERGE-Noah-CCI root zone soil moisture"

GLDAS_NOAH_v2_0_DESCRIPTION = """
        GLDAS Version 2.0 (GLDAS-2.0) Forcing Data Sets

        The  GLDAS-2.0 simulations were forced with the Global Meteorological
        Forcing Data set from Princeton University [Sheffield et al., 2006]
        from 1948 to 2014.

        For more information on GLDAS forcing, please visit
        https://ldas.gsfc.nasa.gov/gldas/forcing-data.

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

GLDAS_NOAH_v2_1_DESCRIPTION = """
        GLDAS Version 2.1 (GLDAS-2.1) Forcing Data Sets

        The GLDAS-2.1 simulations were forced with National Oceanic and
        Atmospheric Administration (NOAA)/Global Data Assimilation System
        (GDAS) atmospheric analysis fields (Derber et al., 1991), the
        disaggregated Global Precipitation Climatology Project (GPCP) V1.3
        Daily Analysis precipitation fields (Adler et al., 2003; Huffman et
        al., 2001), and the Air Force Weather Agency’s AGRicultural
        METeorological modeling system (AGRMET) radiation fields. The
        simulation was only used with GDAS and GPCP from January 2000 to
        February 2001, followed by the addition of AGRMET from March 1, 2001
        onwards.

        For more information on GLDAS forcing, please visit
        https://ldas.gsfc.nasa.gov/gldas/forcing-data.

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
GRACE_DESCRIPTION = """
        The Gravity Recovery and Climate Experiment (GRACE) twin satellites,
        which orbited Earth from 2002 to 2017, made detailed measurements of
        Earth's gravity field and improved investigations about Earth's water
        reservoirs, over land, ice and oceans.

        GRACE measured gravity by relating it to the distance between the two
        satellites. When there was an increase in gravity ahead of the pair,
        the front satellite sped up and the distance between the pair
        increased. When the increased gravity was between the pair, their
        distance decreased; the opposite occurred when there was decreased
        gravity ahead of, or between, the satellite pair.

        The satellites were separated by 220 km, and they could detect changes
        smaller than a micrometer per second in relative velocity. These
        measurements, in conjunction with other data and models, provided
        observations of terrestrial water storage changes, ice-mass variations,
        ocean bottom pressure changes and sea-level variations.

        GRACE was a collaboration of the US and German space agencies (NASA and
        DLR). The key partners were the University of Texas Center for Space
        Research (CSR), the GeoForschungsZentrum (GFZ) Potsdam, and the Jet
        Propulsion Laboratory (JPL).
"""
LDAS_DESCRIPTION = f"""
        This command is deprecated. It has been split up into separate commands
        for each of the different LDAS products.  This command remains only so
        that old scripts don't break.

        Please use the following commands instead:
        {__all__}
"""
MERRA_DESCRIPTION = """
        The Modern-Era Retrospective analysis for Research and Applications,
        Version 2 (MERRA-2) provides data beginning in 1980. It was introduced
        to replace the original MERRA dataset because of the advances made in
        the assimilation system that enable assimilation of modern
        hyperspectral radiance and microwave observations, along with GPS-Radio
        Occultation datasets. It also uses NASA's ozone profile observations
        that began in late 2004. Additional advances in both the GEOS model and
        the GSI assimilation system are included in MERRA-2. Spatial resolution
        remains about the same (about 50 km in the latitudinal direction) as in
        MERRA. Along with the enhancements in the meteorological assimilation,
        MERRA-2 takes some significant steps towards GMAO’s target of an Earth
        System reanalysis. MERRA-2 is the first long-term global reanalysis to
        assimilate space-based observations of aerosols and represent their
        interactions with other physical processes in the climate system.
        MERRA-2 includes a representation of ice sheets over (say) Greenland
        and Antarctica.
"""
NLDAS_FORA_DESCRIPTION = """
        The non-precipitation land-surface forcing fields for NLDAS-2 are
        derived from the analysis fields of the NCEP North American Regional
        Reanalysis (NARR).  NARR consists of: 1) a retrospective dataset
        starting from Jan 1979, and 2) a daily update execution at NCEP. The
        daily update provides a real-time NARR continuation known as the
        Regional Climate Data Assimilation System, or R-CDAS.

        NARR analysis fields are 32-km spatial resolution and 3-hourly temporal
        frequency. Those NARR fields that are utilized to generate NLDAS-2
        forcing fields are spatially interpolated to the finer resolution of
        the NLDAS 1/8th-degree grid and then temporally disaggregated to the
        NLDAS-2 hourly frequency. Additionally, the fields of surface pressure,
        surface downward longwave radiation, near-surface air temperature and
        near-surface specific humidity are adjusted vertically to account for
        the vertical difference between the NARR and NLDAS fields of terrain
        height. This vertical adjustment applies the traditional vertical lapse
        rate of 6.5 K/km for air temperature. The details of the spatial
        interpolation, temporal disaggregation, and vertical adjustment are
        those employed in NLDAS-1, as presented by Cosgrove et al. (2003).

        The hourly land-surface forcing fields for NLDAS-2 are grouped into two
        GRIB files, "File A" and "File B". This is a change from NLDAS-1, which
        had only one hourly forcing file.

        File A contains data for surface, 2 meter, and 10 meter heights.  File
        B contains data for the lowest layer of the model used for data
        assimilation.

        The surface downward shortwave radiation field in File A is
        a bias-corrected field wherein a bias-correction algorithm was applied
        to the NARR surface downward shortwave radiation. This bias correction
        utilizes five years (1996-2000) of the hourly 1/8th-degree GOES-based
        surface downward shortwave radiation fields derived by Pinker et al.
        (2003).

        The precipitation field in File A is not the NARR precipitation
        forcing, but is rather a product of a temporal disaggregation of
        a gauge-only CPC analysis of daily precipitation, performed directly on
        the NLDAS grid and including an orographic adjustment based on the
        widely-applied PRISM climatology.

        The field in File A that gives the fraction of total precipitation that
        is convective is an estimate derived from the following two NARR
        precipitation fields (which are provided in File B): NARR total
        precipitation and NARR convective precipitation (the latter is less
        than or equal to the NARR total precipitation and can be zero). The
        convective fraction of total precipitation and/or the CAPE field in
        File A are used by some land models to estimate the subgrid spatial
        variability of the total precipitation.

        The potential evaporation field in File A is that computed in NARR
        using the modified Penman scheme of Mahrt and Ek (1984). Potential
        evaporation is needed by some land models (such as the SAC model) that
        require potential evaporation as an input forcing.

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
"""
NLDAS_NOAH_DESCRIPTION = """
        The NLDAS-2 Noah land surface model simulations were forced with the
        NLDAS-2 Forcing Data Sets.  More information can be found at
        https://ldas.gsfc.nasa.gov/nldas/v2/models
"""
NLDAS_VIC_DESCRIPTION = """
        The NLDAS-2 Variable Infiltration Capacity (VIC) land surface model
        simulations were forced with the NLDAS-2 Forcing Data Sets.  More
        information can be found at https://ldas.gsfc.nasa.gov/nldas/v2/models
"""
SMERGE_DESCRIPTION = """
        SoilMERGE (SMERGE) is a new root-zone soil moisture (RZSM) product that
        covers the entire continental United States. A fundamental limiting
        factor that constrains agricultural productivity is RZSM. Also
        delineation of RZSM is important for drought monitoring and RZSM is
        considered a critical climate variable.

        This product is developed based on merging NLDAS land surface model
        output with surface satellite retrievals from the European Space Agency
        (ESA) Climate Change Initiative (CCI). Therefore, unlike other
        observational soil moisture products SMERGE spans nearly four decades
        (1979 to 2019). The product has a 0.125o spatial resolution at a daily
        time step.

        A key initial user for SMERGE will be the USDA Northern Plains Regional
        Climate Hub (NPRCH). Stakeholder input will be solicited during the
        initial phases of product development. This effort will maximize the
        utility of SMERGE to diverse users who have an interest in long-term
        analysis of RZSM to support activities in the areas of water and land
        management and within the agricultural sector.
"""

ldas = foundation_api(
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
    description=LDAS_DESCRIPTION,
)

ldas_gldas_noah_v2_0 = foundation_api(
    units_table=make_units_table(_GLDAS_NOAH_v2_0),
    first_line=GLDAS_NOAH_v2_0_FIRST_LINE,
    meta_table=_META_HEADER + _GLDAS_NOAH_v2_0_META + "\n",
    description=GLDAS_NOAH_v2_0_DESCRIPTION,
)

ldas_gldas_noah_v2_1 = foundation_api(
    units_table=make_units_table(_GLDAS_NOAH_v2_1),
    first_line=GLDAS_NOAH_v2_1_FIRST_LINE,
    meta_table=_META_HEADER + _GLDAS_NOAH_v2_1_META + "\n",
    description=GLDAS_NOAH_v2_1_DESCRIPTION,
)

ldas_gldas_noah = foundation_api(
    units_table=make_units_table(_GLDAS_NOAH_v2_1),
    first_line=GLDAS_NOAH_v2_1_FIRST_LINE,
    meta_table=_META_HEADER + _GLDAS_NOAH_v2_1_META + "\n",
    description=GLDAS_NOAH_v2_1_DESCRIPTION,
)

ldas_grace = foundation_api(
    units_table=make_units_table(_GRACE),
    first_line=GRACE_FIRST_LINE,
    meta_table=_META_HEADER + _GRACE_META + "\n",
    description=GRACE_DESCRIPTION,
)

ldas_merra = foundation_api(
    units_table=make_units_table(_MERRA),
    first_line=MERRA_FIRST_LINE,
    meta_table=_META_HEADER + _MERRA_META + "\n",
    description=MERRA_DESCRIPTION,
)

ldas_nldas_fora = foundation_api(
    units_table=make_units_table(_NLDAS_FORA),
    first_line=NLDAS_FORA_FIRST_LINE,
    meta_table=_META_HEADER + _NLDAS_FORA_META + "\n",
    description=NLDAS_FORA_DESCRIPTION,
)

ldas_nldas_noah = foundation_api(
    units_table=make_units_table(_NLDAS_NOAH),
    first_line=NLDAS_NOAH_FIRST_LINE,
    meta_table=_META_HEADER + _NLDAS_NOAH_META + "\n",
    description=NLDAS_NOAH_DESCRIPTION,
)

ldas_nldas_vic = foundation_api(
    units_table=make_units_table(_NLDAS_VIC),
    first_line=NLDAS_VIC_FIRST_LINE,
    meta_table=_META_HEADER + _NLDAS_VIC_META + "\n",
    description=NLDAS_VIC_DESCRIPTION,
)

ldas_smerge = foundation_api(
    units_table=make_units_table(_SMERGE),
    first_line=SMERGE_FIRST_LINE,
    meta_table=_META_HEADER + _SMERGE_META + "\n",
    description=SMERGE_DESCRIPTION,
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

    if lat < _project_lat_ranges[project][0] or lat > _project_lat_ranges[project][1]:
        raise ValueError(
            tsutils.error_wrapper(
                f"Latitude {lat} is out of range for {project} data. "
                f"Valid range is {_project_lat_ranges[project][0]} to "
                f"{_project_lat_ranges[project][1]}."
            )
        )
    if lon < _project_lon_ranges[project][0] or lon > _project_lon_ranges[project][1]:
        raise ValueError(
            tsutils.error_wrapper(
                f"Longitude {lon} is out of range for {project} data. "
                f"Valid range is {_project_lon_ranges[project][0]} to "
                f"{_project_lon_ranges[project][1]}."
            )
        )

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

    r = ldas_gldas_noah(
        30,
        100,
        variables="GLDAS_NOAH025_3H_2_1_PotEvap_tavg",
        startDate="2016-01-01T00",
        endDate="2016-12-01T00",
    )
    print(r)

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
