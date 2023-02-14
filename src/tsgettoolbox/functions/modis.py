"""
modis               global 250m,500m,1000m 2000- 4D,8D,16D,A:Download
                    MODIS derived data.
"""

import datetime
import json

import async_retriever as ar
import cltoolbox
import numpy as np
import pandas as pd
from cltoolbox.rst_text_formatter import RSTHelpFormatter as HelpFormatter
from toolbox_utils import tsutils

__all__ = ["modis"]

_MISSING = {
    "MU": -9999,
    "PE": 255,
    "PS": 0,
    "SE": -9999,
    "V1": -9999,
    "V2": -9999,
    "LC_Prop1": 255,
    "LC_Prop1_Assessment": 255,
    "LC_Prop2": 255,
    "LC_Prop2_Assessment": 255,
    "LC_Prop3": 255,
    "LC_Prop3_Assessment": 255,
    "LC_Type1": 255,
    "LC_Type2": 255,
    "LC_Type3": 255,
    "LC_Type4": 255,
    "LC_Type5": 255,
    "LW": 255,
    "QC": 255,
    "Dormancy.Num_Modes_01": 32767,
    "Dormancy.Num_Modes_02": 32767,
    "EVI_Amplitude.Num_Modes_01": 32767,
    "EVI_Amplitude.Num_Modes_02": 32767,
    "EVI_Area.Num_Modes_01": 32767,
    "EVI_Area.Num_Modes_02": 32767,
    "EVI_Minimum.Num_Modes_01": 32767,
    "EVI_Minimum.Num_Modes_02": 32767,
    "Greenup.Num_Modes_01": 32767,
    "Greenup.Num_Modes_02": 32767,
    "Maturity.Num_Modes_01": 32767,
    "Maturity.Num_Modes_02": 32767,
    "MidGreendown.Num_Modes_01": 32767,
    "MidGreendown.Num_Modes_02": 32767,
    "MidGreenup.Num_Modes_01": 32767,
    "MidGreenup.Num_Modes_02": 32767,
    "NumCycles": 32767,
    "QA_Detailed.Num_Modes_01": 32767,
    "QA_Detailed.Num_Modes_02": 32767,
    "QA_Overall.Num_Modes_01": 32767,
    "QA_Overall.Num_Modes_02": 32767,
    "FparExtra_QC": 255,
    "FparLai_QC": 255,
    "FparStdDev_500m": 255,
    "Fpar_500m": 255,
    "LaiStdDev_500m": 255,
    "Lai_500m": 255,
    "Kgeo": -32767,
    "Kiso": -32767,
    "Kvol": -32767,
    "Sur_albedo": -28672,
    "UpdateDay": 255,
    "BDRF_Albedo_Band_Mandatory_Quality_Band1": 255,
    "BDRF_Albedo_Band_Mandatory_Quality_Band2": 255,
    "BDRF_Albedo_Band_Mandatory_Quality_Band3": 255,
    "BDRF_Albedo_Band_Mandatory_Quality_Band4": 255,
    "BDRF_Albedo_Band_Mandatory_Quality_Band5": 255,
    "BDRF_Albedo_Band_Mandatory_Quality_Band6": 255,
    "BDRF_Albedo_Band_Mandatory_Quality_Band7": 255,
    "BDRF_Albedo_Band_Mandatory_Quality_nir": 255,
    "BDRF_Albedo_Band_Mandatory_Quality_shortwave": 255,
    "BDRF_Albedo_Band_Mandatory_Quality_vis": 255,
    "BRDF_Albedo_Parameters_Band1": 32767,
    "BRDF_Albedo_Parameters_Band2": 32767,
    "BRDF_Albedo_Parameters_Band3": 32767,
    "BRDF_Albedo_Parameters_Band4": 32767,
    "BRDF_Albedo_Parameters_Band5": 32767,
    "BRDF_Albedo_Parameters_Band6": 32767,
    "BRDF_Albedo_Parameters_Band7": 32767,
    "BRDF_Albedo_Parameters_nir": 32767,
    "BRDF_Albedo_Parameters_shortwave": 32767,
    "BRDF_Albedo_Parameters_vis": 32767,
    "BRDF_Albedo_Band_Mandatory_Quality_Band1": 255,
    "BRDF_Albedo_Band_Mandatory_Quality_Band2": 255,
    "BRDF_Albedo_Band_Mandatory_Quality_Band3": 255,
    "BRDF_Albedo_Band_Mandatory_Quality_Band4": 255,
    "BRDF_Albedo_Band_Mandatory_Quality_Band5": 255,
    "BRDF_Albedo_Band_Mandatory_Quality_Band6": 255,
    "BRDF_Albedo_Band_Mandatory_Quality_Band7": 255,
    "Nadir_Reflectance_Band1": 32767,
    "Nadir_Reflectance_Band2": 32767,
    "Nadir_Reflectance_Band3": 32767,
    "Nadir_Reflectance_Band4": 32767,
    "Nadir_Reflectance_Band5": 32767,
    "Nadir_Reflectance_Band6": 32767,
    "Nadir_Reflectance_Band7": 32767,
    "Burn_Date": -1,
    "Burn_Date_Uncertainty": 0,
    "First_Day": -1,
    "Last_Day": -1,
    "sur_refl_b01": -28672,
    "sur_refl_b02": -28672,
    "sur_refl_b03": -28672,
    "sur_refl_b04": -28672,
    "sur_refl_b05": -28672,
    "sur_refl_b06": -28672,
    "sur_refl_b07": -28672,
    "sur_refl_day_of_year": -1,
    "sur_refl_qc_500m": -1,
    "sur_refl_raz": 0,
    "sur_refl_state_500m": 65535,
    "sur_refl_szen": 0,
    "sur_refl_vzen": 0,
    "Clear_sky_days": 0,
    "Clear_sky_nights": 0,
    "Day_view_angl": 255,
    "Day_view_time": 255,
    "Emis_31": 0,
    "Emis_32": 0,
    "LST_Day_1km": 0,
    "LST_Night_1km": 0,
    "Night_view_angl": 255,
    "Night_view_time": 255,
    "250m_16_days_blue_reflectance": -1000,
    "250m_16_days_composite_day_of_the_year": -1,
    "250m_16_days_EVI": -3000,
    "250m_16_days_MIR_reflectance": -1000,
    "250m_16_days_NDVI": -3000,
    "250m_16_days_NIR_reflectance": -1000,
    "250m_16_days_pixel_reliability": -1,
    "250m_16_days_red_reflectance": -1000,
    "250m_16_days_relative_azimuth_angle": -4000,
    "250m_16_days_sun_zenith_angle": -10000,
    "250m_16_days_view_zenith_angle": -10000,
    "250m_16_days_VI_Quality": -1,
    "FireMask": 0,
    "ET_500m": 32767,
    "ET_QC_500m": 255,
    "LE_500m": 32767,
    "PET_500m": 32767,
    "PLE_500m": 32767,
    "Gpp_500m": 32767,
    "PsnNet_500m": 32767,
    "Psn_QC_500m": 255,
    "Npp_500m": 32767,
    "Npp_QC_500m": 255,
    "Emis_29": 0,
    "LST_Day_1KM": 0,
    "LST_Night_1KM": 0,
    "View_Angle_Day": 255,
    "View_Angle_Night": 255,
    "View_Time_Day": 255,
    "View_Time_Night": 255,
    "Cloud": 0,
    "Percent_NonTree_Vegetation": 253,
    "Percent_NonVegetated": 253,
    "Percent_NonVegetated_SD": -100,
    "Percent_Tree_Cover": 253,
    "Percent_Tree_Cover_SD": -100,
    "Quality": 0,
    "EVI_Quality": -1,
    "SIF_740_daily_corr": -999,
    "SIF_740_daily_corr_SD": -999,
    "sif_ann": -999,
    "RelativeAzimuth": 0,
    "SensorZenith": 0,
    "SolarZenith": 0,
    "SurfReflect_Day_Of_Year": 65535,
    "SurfReflect_M1": -28672,
    "SurfReflect_M10": -28672,
    "SurfReflect_M11": -28672,
    "SurfReflect_M2": -28672,
    "SurfReflect_M3": -28672,
    "SurfReflect_M4": -28672,
    "SurfReflect_M5": -28672,
    "SurfReflect_M7": -28672,
    "SurfReflect_M8": -28672,
    "SurfReflect_QC": 4294967295,
    "SurfReflect_State": 65535,
    "SurfReflect_I1": -28672,
    "SurfReflect_I2": -28672,
    "SurfReflect_I3": -28672,
    "SurfReflect_QC_500m": 65535,
    "SurfReflect_State_500m": 65535,
    "500_m_16_days_blue_reflectance": -1000,
    "500_m_16_days_composite_day_of_the_year": -1,
    "500_m_16_days_EVI": -15000,
    "500_m_16_days_EVI2": -15000,
    "500_m_16_days_green_reflectance": -1000,
    "500_m_16_days_NDVI": -15000,
    "500_m_16_days_NIR_reflectance": -1000,
    "500_m_16_days_pixel_reliability": -4,
    "500_m_16_days_red_reflectance": -1000,
    "500_m_16_days_relative_azimuth_angle": -20000,
    "500_m_16_days_sun_zenith_angle": -20000,
    "500_m_16_days_SWIR1_reflectance": -1000,
    "500_m_16_days_SWIR2_reflectance": -1000,
    "500_m_16_days_SWIR3_reflectance": -1000,
    "500_m_16_days_view_zenith_angle": -20000,
    "500_m_16_days_VI_Quality": 65535,
    "Fpar": 255,
    "FparStdDev": 255,
    "Lai": 255,
    "LaiStdDev": 255,
    "Emis_14": 0,
    "Emis_15": 0,
    "Emis_16": 0,
    "QC_Day": 0,
    "QC_Night": 0,
    "Cycle_1.Date_Mid_Greenup_Phase_1": 32767,
    "Cycle_1.Date_Mid_Senescence_Phase_1": 32767,
    "Cycle_1.EVI2_Growing_Season_Area_1": 32767,
    "Cycle_1.EVI2_Onset_Greenness_Increase_1": 32767,
    "Cycle_1.EVI2_Onset_Greenness_Maximum_1": 32767,
    "Cycle_1.GLSP_QC_1": 255,
    "Cycle_1.Greenness_Agreement_Growing_Season_1": 255,
    "Cycle_1.Growing_Season_Length_1": 32767,
    "Cycle_1.Onset_Greenness_Decrease_1": 32767,
    "Cycle_1.Onset_Greenness_Increase_1": 32767,
    "Cycle_1.Onset_Greenness_Maximum_1": 32767,
    "Cycle_1.Onset_Greenness_Minimum_1": 32767,
    "Cycle_1.PGQ_Growing_Season_1": 255,
    "Cycle_1.PGQ_Onset_Greenness_Decrease_1": 255,
    "Cycle_1.PGQ_Onset_Greenness_Increase_1": 255,
    "Cycle_1.PGQ_Onset_Greenness_Maximum_1": 255,
    "Cycle_1.PGQ_Onset_Greenness_Minimum_1": 255,
    "Cycle_1.Rate_Greenness_Decrease_1": 32767,
    "Cycle_1.Rate_Greenness_Increase_1": 32767,
    "Cycle_2.Date_Mid_Greenup_Phase_2": 32767,
    "Cycle_2.Date_Mid_Senescence_Phase_2": 32767,
    "Cycle_2.EVI2_Growing_Season_Area_2": 32767,
    "Cycle_2.EVI2_Onset_Greenness_Increase_2": 32767,
    "Cycle_2.EVI2_Onset_Greenness_Maximum_2": 32767,
    "Cycle_2.GLSP_QC_2": 255,
    "Cycle_2.Greenness_Agreement_Growing_Season_2": 255,
    "Cycle_2.Growing_Season_Length_2": 32767,
    "Cycle_2.Onset_Greenness_Decrease_2": 32767,
    "Cycle_2.Onset_Greenness_Increase_2": 32767,
    "Cycle_2.Onset_Greenness_Maximum_2": 32767,
    "Cycle_2.Onset_Greenness_Minimum_2": 32767,
    "Cycle_2.PGQ_Growing_Season_2": 255,
    "Cycle_2.PGQ_Onset_Greenness_Decrease_2": 255,
    "Cycle_2.PGQ_Onset_Greenness_Increase_2": 255,
    "Cycle_2.PGQ_Onset_Greenness_Maximum_2": 255,
    "Cycle_2.PGQ_Onset_Greenness_Minimum_2": 255,
    "Cycle_2.Rate_Greenness_Decrease_2": 32767,
    "Cycle_2.Rate_Greenness_Increase_2": 32767,
}

_SCALE = {
    "EVI_Amplitude.Num_Modes_01": 0.0001,
    "EVI_Amplitude.Num_Modes_02": 0.0001,
    "EVI_Area.Num_Modes_01": 0.1,
    "EVI_Area.Num_Modes_02": 0.1,
    "EVI_Minimum.Num_Modes_01": 0.0001,
    "EVI_Minimum.Num_Modes_02": 0.0001,
    "FparStdDev_500m": 0.01,
    "Fpar_500m": 0.01,
    "LaiStdDev_500m": 0.1,
    "Lai_500m": 0.1,
    "Kgeo": 0.0001,
    "Kiso": 0.0001,
    "Kvol": 0.0001,
    "Sur_albedo": 0.0001,
    "nir_actual": 0.001,
    "nir_black": 0.001,
    "nir_white": 0.001,
    "shortwave_actual": 0.001,
    "shortwave_black": 0.001,
    "shortwave_white": 0.001,
    "vis_actual": 0.001,
    "vis_black": 0.001,
    "vis_white": 0.001,
    "BRDF_Albedo_Parameters_Band1": 0.001,
    "BRDF_Albedo_Parameters_Band2": 0.001,
    "BRDF_Albedo_Parameters_Band3": 0.001,
    "BRDF_Albedo_Parameters_Band4": 0.001,
    "BRDF_Albedo_Parameters_Band5": 0.001,
    "BRDF_Albedo_Parameters_Band6": 0.001,
    "BRDF_Albedo_Parameters_Band7": 0.001,
    "BRDF_Albedo_Parameters_nir": 0.001,
    "BRDF_Albedo_Parameters_shortwave": 0.001,
    "BRDF_Albedo_Parameters_vis": 0.001,
    "Nadir_Reflectance_Band1": 0.0001,
    "Nadir_Reflectance_Band2": 0.0001,
    "Nadir_Reflectance_Band3": 0.0001,
    "Nadir_Reflectance_Band4": 0.0001,
    "Nadir_Reflectance_Band5": 0.0001,
    "Nadir_Reflectance_Band6": 0.0001,
    "Nadir_Reflectance_Band7": 0.0001,
    "sur_refl_b01": 0.0001,
    "sur_refl_b02": 0.0001,
    "sur_refl_b03": 0.0001,
    "sur_refl_b04": 0.0001,
    "sur_refl_b05": 0.0001,
    "sur_refl_b06": 0.0001,
    "sur_refl_b07": 0.0001,
    "sur_refl_raz": 0.01,
    "sur_refl_szen": 0.01,
    "sur_refl_vzen": 0.01,
    "Day_view_time": 0.1,
    "Emis_31": 0.002,
    "Emis_32": 0.002,
    "LST_Day_1km": 0.02,
    "LST_Night_1km": 0.02,
    "Night_view_time": 0.1,
    "250m_16_days_blue_reflectance": 0.0001,
    "250m_16_days_EVI": 0.0001,
    "250m_16_days_MIR_reflectance": 0.0001,
    "250m_16_days_NDVI": 0.0001,
    "250m_16_days_NIR_reflectance": 0.0001,
    "250m_16_days_red_reflectance": 0.0001,
    "250m_16_days_relative_azimuth_angle": 0.1,
    "250m_16_days_sun_zenith_angle": 0.01,
    "250m_16_days_view_zenith_angle": 0.01,
    "ET_500m": 0.1,
    "LE_500m": 10000.0,
    "PET_500m": 0.1,
    "PLE_500m": 10000.0,
    "Gpp_500m": 0.0001,
    "PsnNet_500m": 0.0001,
    "Npp_500m": 0.0001,
    "Emis_29": 0.002,
    "LST_Day_1KM": 0.02,
    "LST_Night_1KM": 0.02,
    "View_Time_Day": 0.1,
    "View_Time_Night": 0.1,
    "Percent_NonVegetated_SD": 0.01,
    "Percent_Tree_Cover_SD": 0.01,
    "RelativeAzimuth": 0.01,
    "SensorZenith": 0.01,
    "SolarZenith": 0.01,
    "SurfReflect_M1": 0.0001,
    "SurfReflect_M10": 0.0001,
    "SurfReflect_M11": 0.0001,
    "SurfReflect_M2": 0.0001,
    "SurfReflect_M3": 0.0001,
    "SurfReflect_M4": 0.0001,
    "SurfReflect_M5": 0.0001,
    "SurfReflect_M7": 0.0001,
    "SurfReflect_M8": 0.0001,
    "SurfReflect_I1": 0.0001,
    "SurfReflect_I2": 0.0001,
    "SurfReflect_I3": 0.0001,
    "500_m_16_days_blue_reflectance": 0.0001,
    "500_m_16_days_EVI": 0.0001,
    "500_m_16_days_EVI2": 0.0001,
    "500_m_16_days_green_reflectance": 0.0001,
    "500_m_16_days_NDVI": 0.0001,
    "500_m_16_days_NIR_reflectance": 0.0001,
    "500_m_16_days_red_reflectance": 0.0001,
    "500_m_16_days_relative_azimuth_angle": 0.01,
    "500_m_16_days_sun_zenith_angle": 0.01,
    "500_m_16_days_SWIR1_reflectance": 0.0001,
    "500_m_16_days_SWIR2_reflectance": 0.0001,
    "500_m_16_days_SWIR3_reflectance": 0.0001,
    "500_m_16_days_view_zenith_angle": 0.01,
    "Fpar": 0.01,
    "FparStdDev": 0.01,
    "Lai": 0.1,
    "LaiStdDev": 0.1,
    "Emis_14": 0.002,
    "Emis_15": 0.002,
    "Emis_16": 0.002,
    "Cycle_1.EVI2_Growing_Season_Area_1": 0.01,
    "Cycle_1.EVI2_Onset_Greenness_Increase_1": 0.0001,
    "Cycle_1.EVI2_Onset_Greenness_Maximum_1": 0.0001,
    "Cycle_1.Rate_Greenness_Decrease_1": 0.0001,
    "Cycle_1.Rate_Greenness_Increase_1": 0.0001,
    "Cycle_2.EVI2_Growing_Season_Area_2": 0.01,
    "Cycle_2.EVI2_Onset_Greenness_Increase_2": 0.0001,
    "Cycle_2.EVI2_Onset_Greenness_Maximum_2": 0.0001,
    "Cycle_2.Rate_Greenness_Decrease_2": 0.0001,
    "Cycle_2.Rate_Greenness_Increase_2": 0.0001,
}

_OFFSET = {
    "Day_view_angl": -65.0,
    "Emis_31": 0.49,
    "Emis_32": 0.49,
    "Night_view_angl": -65.0,
    "Emis_29": 0.49,
    "View_Angle_Day": -65.0,
    "View_Angle_Night": -65.0,
    "Emis_14": 0.49,
    "Emis_15": 0.49,
    "Emis_16": 0.49,
}

_UNITS = {
    "ESIavg": "ratio_ET/PET",
    "PET": "W/m^2",
    "WUEavg": "ratio_GPP/ET",
    "counts": "counts",
    "elev_lowestmode_mean": "meters",
    "elev_lowestmode_stddev": "meters",
    "rh100_mean": "meters",
    "rh100_stddev": "meters",
    "MU": "Mg/ha",
    "NC": "counts",
    "NS": "counts",
    "PE": "percent",
    "SE": "Mg/ha",
    "LC_Prop1": "class",
    "LC_Prop1_Assessment": "percent",
    "LC_Prop2": "class",
    "LC_Prop2_Assessment": "percent",
    "LC_Prop3": "class",
    "LC_Prop3_Assessment": "percent",
    "LC_Type1": "class",
    "LC_Type2": "class",
    "LC_Type3": "class",
    "LC_Type4": "class",
    "LC_Type5": "class",
    "LW": "class",
    "QC": "quality-flag",
    "Dormancy.Num_Modes_01": "days_since_1970-01-01",
    "Dormancy.Num_Modes_02": "days_since_1970-01-01",
    "EVI_Amplitude.Num_Modes_01": "NBAR-EVI2",
    "EVI_Amplitude.Num_Modes_02": "NBAR-EVI2",
    "EVI_Area.Num_Modes_01": "NBAR-EVI2",
    "EVI_Area.Num_Modes_02": "NBAR-EVI2",
    "EVI_Minimum.Num_Modes_01": "NBAR-EVI2",
    "EVI_Minimum.Num_Modes_02": "NBAR-EVI2",
    "Greenup.Num_Modes_01": "days_since_1970-01-01",
    "Greenup.Num_Modes_02": "days_since_1970-01-01",
    "Maturity.Num_Modes_01": "days_since_1970-01-01",
    "Maturity.Num_Modes_02": "days_since_1970-01-01",
    "MidGreendown.Num_Modes_01": "days_since_1970-01-01",
    "MidGreendown.Num_Modes_02": "days_since_1970-01-01",
    "MidGreenup.Num_Modes_01": "days_since_1970-01-01",
    "MidGreenup.Num_Modes_02": "days_since_1970-01-01",
    "FparExtra_QC": "class-flag",
    "FparLai_QC": "class-flag",
    "FparStdDev_500m": "percent",
    "Fpar_500m": "percent",
    "LaiStdDev_500m": "m^2/m^2",
    "Lai_500m": "m^2/m^2",
    "BDRF_Albedo_Band_Mandatory_Quality_Band1": "bit_field",
    "BDRF_Albedo_Band_Mandatory_Quality_Band2": "bit_field",
    "BDRF_Albedo_Band_Mandatory_Quality_Band3": "bit_field",
    "BDRF_Albedo_Band_Mandatory_Quality_Band4": "bit_field",
    "BDRF_Albedo_Band_Mandatory_Quality_Band5": "bit_field",
    "BDRF_Albedo_Band_Mandatory_Quality_Band6": "bit_field",
    "BDRF_Albedo_Band_Mandatory_Quality_Band7": "bit_field",
    "BDRF_Albedo_Band_Mandatory_Quality_nir": "bit_field",
    "BDRF_Albedo_Band_Mandatory_Quality_shortwave": "bit_field",
    "BDRF_Albedo_Band_Mandatory_Quality_vis": "bit_field",
    "BRDF_Albedo_Band_Mandatory_Quality_Band1": "concatenated flags",
    "BRDF_Albedo_Band_Mandatory_Quality_Band2": "concatenated flags",
    "BRDF_Albedo_Band_Mandatory_Quality_Band3": "concatenated flags",
    "BRDF_Albedo_Band_Mandatory_Quality_Band4": "concatenated flags",
    "BRDF_Albedo_Band_Mandatory_Quality_Band5": "concatenated flags",
    "BRDF_Albedo_Band_Mandatory_Quality_Band6": "concatenated flags",
    "BRDF_Albedo_Band_Mandatory_Quality_Band7": "concatenated flags",
    "Burn_Date": "day_of_year",
    "Burn_Date_Uncertainty": "days",
    "First_Day": "day_of_year",
    "Last_Day": "day_of_year",
    "QA": "bit_field",
    "sur_refl_b01": "reflectance",
    "sur_refl_b02": "reflectance",
    "sur_refl_b03": "reflectance",
    "sur_refl_b04": "reflectance",
    "sur_refl_b05": "reflectance",
    "sur_refl_b06": "reflectance",
    "sur_refl_b07": "reflectance",
    "sur_refl_day_of_year": "day_of_year",
    "sur_refl_qc_500m": "bit_field",
    "sur_refl_raz": "degree",
    "sur_refl_state_500m": "bit_field",
    "sur_refl_szen": "degree",
    "sur_refl_vzen": "degree",
    "Day_view_angl": "degree",
    "Day_view_time": "hrs",
    "LST_Day_1km": "degK",
    "LST_Night_1km": "degK",
    "Night_view_angl": "degree",
    "Night_view_time": "hrs",
    "250m_16_days_blue_reflectance": "reflectance",
    "250m_16_days_composite_day_of_the_year": "day_of_year",
    "250m_16_days_MIR_reflectance": "reflectance",
    "250m_16_days_NIR_reflectance": "reflectance",
    "250m_16_days_pixel_reliability": "rank",
    "250m_16_days_red_reflectance": "reflectance",
    "250m_16_days_relative_azimuth_angle": "degrees",
    "250m_16_days_sun_zenith_angle": "degrees",
    "250m_16_days_view_zenith_angle": "degrees",
    "250m_16_days_VI_Quality": "bit_field",
    "FireMask": "class-flag",
    "ET_500m": "kg/m^2/8day",
    "LE_500m": "J/m^2/day",
    "PET_500m": "kg/m^2/8day",
    "PLE_500m": "J/m^2/day",
    "Gpp_500m": "kgC/m^2/8day",
    "PsnNet_500m": "kgC/m^2/8day",
    "Npp_500m": "kg_C/m^2",
    "Npp_QC_500m": "percentage",
    "LST_Day_1KM": "degK",
    "LST_Night_1KM": "degK",
    "View_Angle_Day": "degree",
    "View_Angle_Night": "degree",
    "View_Time_Day": "hrs",
    "View_Time_Night": "hrs",
    "Cloud": "bit_field",
    "Percent_NonTree_Vegetation": "percent",
    "Percent_NonVegetated": "percent",
    "Percent_NonVegetated_SD": "percent",
    "Percent_Tree_Cover": "percent",
    "Percent_Tree_Cover_SD": "percent",
    "Quality": "bit_field",
    "EVI_Quality": "bit_field",
    "SIF_740_daily_corr": "mW/m2/nm/sr",
    "SIF_740_daily_corr_SD": "mW/m2/nm/sr",
    "sif_ann": "mW/m2/nm/sr",
    "RelativeAzimuth": "degree",
    "SensorZenith": "degree",
    "SolarZenith": "degree",
    "SurfReflect_Day_Of_Year": "day_of_year",
    "SurfReflect_M1": "reflectance",
    "SurfReflect_M10": "reflectance",
    "SurfReflect_M11": "reflectance",
    "SurfReflect_M2": "reflectance",
    "SurfReflect_M3": "reflectance",
    "SurfReflect_M4": "reflectance",
    "SurfReflect_M5": "reflectance",
    "SurfReflect_M7": "reflectance",
    "SurfReflect_M8": "reflectance",
    "SurfReflect_QC": "bit_field",
    "SurfReflect_State": "bit_field",
    "SurfReflect_I1": "reflectance",
    "SurfReflect_I2": "reflectance",
    "SurfReflect_I3": "reflectance",
    "SurfReflect_QC_500m": "bit_field",
    "SurfReflect_State_500m": "bit_field",
    "500_m_16_days_blue_reflectance": "reflectance",
    "500_m_16_days_composite_day_of_the_year": "day_of_year",
    "500_m_16_days_green_reflectance": "reflectance",
    "500_m_16_days_NIR_reflectance": "reflectance",
    "500_m_16_days_pixel_reliability": "rank",
    "500_m_16_days_red_reflectance": "reflectance",
    "500_m_16_days_relative_azimuth_angle": "degrees",
    "500_m_16_days_sun_zenith_angle": "degrees",
    "500_m_16_days_SWIR1_reflectance": "reflectance",
    "500_m_16_days_SWIR2_reflectance": "reflectance",
    "500_m_16_days_SWIR3_reflectance": "reflectance",
    "500_m_16_days_view_zenith_angle": "degrees",
    "500_m_16_days_VI_Quality": "bit_field",
    "Fpar": "fraction",
    "FparStdDev": "fraction",
    "Lai": "m^2/m^2",
    "LaiStdDev": "m^2/m^2",
    "Cycle_1.Date_Mid_Greenup_Phase_1": "day_of_year",
    "Cycle_1.Date_Mid_Senescence_Phase_1": "day_of_year",
    "Cycle_1.EVI2_Growing_Season_Area_1": "EVI2",
    "Cycle_1.EVI2_Onset_Greenness_Increase_1": "EVI2",
    "Cycle_1.EVI2_Onset_Greenness_Maximum_1": "EVI2",
    "Cycle_1.Growing_Season_Length_1": "number_of_days",
    "Cycle_1.Onset_Greenness_Decrease_1": "day_of_year",
    "Cycle_1.Onset_Greenness_Increase_1": "day_of_year",
    "Cycle_1.Onset_Greenness_Maximum_1": "day_of_year",
    "Cycle_1.Onset_Greenness_Minimum_1": "day_of_year",
    "Cycle_1.Rate_Greenness_Decrease_1": "EVI2/day",
    "Cycle_1.Rate_Greenness_Increase_1": "EVI2/day",
    "Cycle_2.Date_Mid_Greenup_Phase_2": "day_of_year",
    "Cycle_2.Date_Mid_Senescence_Phase_2": "day_of_year",
    "Cycle_2.EVI2_Growing_Season_Area_2": "EVI2",
    "Cycle_2.EVI2_Onset_Greenness_Increase_2": "EVI2",
    "Cycle_2.EVI2_Onset_Greenness_Maximum_2": "EVI2",
    "Cycle_2.Growing_Season_Length_2": "number_of_days",
    "Cycle_2.Onset_Greenness_Decrease_2": "day_of_year",
    "Cycle_2.Onset_Greenness_Increase_2": "day_of_year",
    "Cycle_2.Onset_Greenness_Maximum_2": "day_of_year",
    "Cycle_2.Onset_Greenness_Minimum_2": "day_of_year",
    "Cycle_2.Rate_Greenness_Decrease_2": "EVI2/day",
    "Cycle_2.Rate_Greenness_Increase_2": "EVI2/day",
}

_VALID_RANGE = {
    "ESIavg": [0, 2],
    "PET": [0, 2000],
    "WUEavg": [0, 20],
    "LC_Prop1": [1, 43],
    "LC_Prop1_Assessment": [0, 100],
    "LC_Prop2": [1, 40],
    "LC_Prop2_Assessment": [0, 100],
    "LC_Prop3": [1, 51],
    "LC_Prop3_Assessment": [0, 100],
    "LC_Type1": [1, 17],
    "LC_Type2": [0, 15],
    "LC_Type3": [0, 10],
    "LC_Type4": [0, 8],
    "LC_Type5": [0, 11],
    "LW": [1, 2],
    "QC": [0, 10],
    "Dormancy.Num_Modes_01": [11138, 32766],
    "Dormancy.Num_Modes_02": [11138, 32766],
    "EVI_Amplitude.Num_Modes_01": [0, 10000],
    "EVI_Amplitude.Num_Modes_02": [0, 10000],
    "EVI_Area.Num_Modes_01": [0, 3700],
    "EVI_Area.Num_Modes_02": [0, 3700],
    "EVI_Minimum.Num_Modes_01": [0, 10000],
    "EVI_Minimum.Num_Modes_02": [0, 10000],
    "Greenup.Num_Modes_01": [11138, 32766],
    "Greenup.Num_Modes_02": [11138, 32766],
    "Maturity.Num_Modes_01": [11138, 32766],
    "Maturity.Num_Modes_02": [11138, 32766],
    "MidGreendown.Num_Modes_01": [11138, 32766],
    "MidGreendown.Num_Modes_02": [11138, 32766],
    "MidGreenup.Num_Modes_01": [11138, 32766],
    "MidGreenup.Num_Modes_02": [11138, 32766],
    "NumCycles": [0, 7],
    "QA_Detailed.Num_Modes_01": [0, 16383],
    "QA_Detailed.Num_Modes_02": [0, 16383],
    "QA_Overall.Num_Modes_01": [0, 3],
    "QA_Overall.Num_Modes_02": [0, 3],
    "FparExtra_QC": [0, 254],
    "FparLai_QC": [0, 254],
    "FparStdDev_500m": [0, 100],
    "Fpar_500m": [0, 100],
    "LaiStdDev_500m": [0, 100],
    "Lai_500m": [0, 100],
    "Kgeo": [-32766, 32767],
    "Kiso": [-32766, 32767],
    "Kvol": [-32766, 32767],
    "Sur_albedo": [-100, 16000],
    "UpdateDay": [0, 254],
    "BDRF_Albedo_Band_Mandatory_Quality_Band1": [0, 254],
    "BDRF_Albedo_Band_Mandatory_Quality_Band2": [0, 254],
    "BDRF_Albedo_Band_Mandatory_Quality_Band3": [0, 254],
    "BDRF_Albedo_Band_Mandatory_Quality_Band4": [0, 254],
    "BDRF_Albedo_Band_Mandatory_Quality_Band5": [0, 254],
    "BDRF_Albedo_Band_Mandatory_Quality_Band6": [0, 254],
    "BDRF_Albedo_Band_Mandatory_Quality_Band7": [0, 254],
    "BDRF_Albedo_Band_Mandatory_Quality_nir": [0, 254],
    "BDRF_Albedo_Band_Mandatory_Quality_shortwave": [0, 254],
    "BDRF_Albedo_Band_Mandatory_Quality_vis": [0, 254],
    "BRDF_Albedo_Parameters_Band1": [0, 32766],
    "BRDF_Albedo_Parameters_Band2": [0, 32766],
    "BRDF_Albedo_Parameters_Band3": [0, 32766],
    "BRDF_Albedo_Parameters_Band4": [0, 32766],
    "BRDF_Albedo_Parameters_Band5": [0, 32766],
    "BRDF_Albedo_Parameters_Band6": [0, 32766],
    "BRDF_Albedo_Parameters_Band7": [0, 32766],
    "BRDF_Albedo_Parameters_nir": [0, 32766],
    "BRDF_Albedo_Parameters_shortwave": [0, 32766],
    "BRDF_Albedo_Parameters_vis": [0, 32766],
    "BRDF_Albedo_Band_Mandatory_Quality_Band1": [0, 254],
    "BRDF_Albedo_Band_Mandatory_Quality_Band2": [0, 254],
    "BRDF_Albedo_Band_Mandatory_Quality_Band3": [0, 254],
    "BRDF_Albedo_Band_Mandatory_Quality_Band4": [0, 254],
    "BRDF_Albedo_Band_Mandatory_Quality_Band5": [0, 254],
    "BRDF_Albedo_Band_Mandatory_Quality_Band6": [0, 254],
    "BRDF_Albedo_Band_Mandatory_Quality_Band7": [0, 254],
    "Nadir_Reflectance_Band1": [0, 32766],
    "Nadir_Reflectance_Band2": [0, 32766],
    "Nadir_Reflectance_Band3": [0, 32766],
    "Nadir_Reflectance_Band4": [0, 32766],
    "Nadir_Reflectance_Band5": [0, 32766],
    "Nadir_Reflectance_Band6": [0, 32766],
    "Nadir_Reflectance_Band7": [0, 32766],
    "Burn_Date": [0, 366],
    "Burn_Date_Uncertainty": [0, 100],
    "First_Day": [1, 366],
    "Last_Day": [1, 366],
    "QA": [0, 6],
    "sur_refl_b01": [-100, 16000],
    "sur_refl_b02": [-100, 16000],
    "sur_refl_b03": [-100, 16000],
    "sur_refl_b04": [-100, 16000],
    "sur_refl_b05": [-100, 16000],
    "sur_refl_b06": [-100, 16000],
    "sur_refl_b07": [-100, 16000],
    "sur_refl_day_of_year": [0, 366],
    "sur_refl_qc_500m": [0, 4294966531],
    "sur_refl_raz": [-18000, 18000],
    "sur_refl_state_500m": [0, 57343],
    "sur_refl_szen": [0, 18000],
    "sur_refl_vzen": [0, 18000],
    "Clear_sky_days": [1, 255],
    "Clear_sky_nights": [1, 255],
    "Day_view_angl": [0, 130],
    "Day_view_time": [0, 240],
    "Emis_31": [1, 255],
    "Emis_32": [1, 255],
    "LST_Day_1km": [7500, 65535],
    "LST_Night_1km": [7500, 65535],
    "Night_view_angl": [0, 130],
    "Night_view_time": [0, 240],
    "QC_Day": [1, 255],
    "QC_Night": [1, 255],
    "250m_16_days_blue_reflectance": [0, 10000],
    "250m_16_days_composite_day_of_the_year": [1, 366],
    "250m_16_days_EVI": [-2000, 10000],
    "250m_16_days_MIR_reflectance": [0, 10000],
    "250m_16_days_NDVI": [-2000, 10000],
    "250m_16_days_NIR_reflectance": [0, 10000],
    "250m_16_days_pixel_reliability": [0, 3],
    "250m_16_days_red_reflectance": [0, 10000],
    "250m_16_days_relative_azimuth_angle": [-3600, 3600],
    "250m_16_days_sun_zenith_angle": [-9000, 9000],
    "250m_16_days_view_zenith_angle": [-9000, 9000],
    "250m_16_days_VI_Quality": [0, 65534],
    "FireMask": [1, 9],
    "ET_500m": [-32767, 32700],
    "ET_QC_500m": [0, 254],
    "LE_500m": [-32767, 32700],
    "PET_500m": [-32767, 32700],
    "PLE_500m": [-32767, 32700],
    "Gpp_500m": [0, 30000],
    "PsnNet_500m": [-30000, 30000],
    "Psn_QC_500m": [0, 254],
    "Npp_500m": [-30000, 32700],
    "Npp_QC_500m": [0, 100],
    "Emis_29": [1, 255],
    "LST_Day_1KM": [7500, 65535],
    "LST_Night_1KM": [7500, 65535],
    "View_Angle_Day": [0, 130],
    "View_Angle_Night": [0, 130],
    "View_Time_Day": [0, 240],
    "View_Time_Night": [0, 240],
    "Cloud": [0, 255],
    "Percent_NonTree_Vegetation": [0, 100],
    "Percent_NonVegetated": [0, 100],
    "Percent_NonVegetated_SD": [0, 10000],
    "Percent_Tree_Cover": [0, 100],
    "Percent_Tree_Cover_SD": [0, 10000],
    "Quality": [0, 255],
    "RelativeAzimuth": [-18000, 18000],
    "SensorZenith": [0, 18000],
    "SolarZenith": [0, 18000],
    "SurfReflect_Day_Of_Year": [1, 366],
    "SurfReflect_M1": [-100, 16000],
    "SurfReflect_M10": [-100, 16000],
    "SurfReflect_M11": [-100, 16000],
    "SurfReflect_M2": [-100, 16000],
    "SurfReflect_M3": [-100, 16000],
    "SurfReflect_M4": [-100, 16000],
    "SurfReflect_M5": [-100, 16000],
    "SurfReflect_M7": [-100, 16000],
    "SurfReflect_M8": [-100, 16000],
    "SurfReflect_QC": [0, 2147483647],
    "SurfReflect_State": [0, 13311],
    "SurfReflect_I1": [-100, 16000],
    "SurfReflect_I2": [-100, 16000],
    "SurfReflect_I3": [-100, 16000],
    "SurfReflect_QC_500m": [0, 32767],
    "SurfReflect_State_500m": [0, 13311],
    "500_m_16_days_blue_reflectance": [0, 10000],
    "500_m_16_days_composite_day_of_the_year": [1, 366],
    "500_m_16_days_EVI": [-10000, 10000],
    "500_m_16_days_EVI2": [-10000, 10000],
    "500_m_16_days_green_reflectance": [0, 10000],
    "500_m_16_days_NDVI": [-10000, 10000],
    "500_m_16_days_NIR_reflectance": [0, 10000],
    "500_m_16_days_pixel_reliability": [0, 11],
    "500_m_16_days_red_reflectance": [0, 10000],
    "500_m_16_days_relative_azimuth_angle": [-18000, 18000],
    "500_m_16_days_sun_zenith_angle": [0, 18000],
    "500_m_16_days_SWIR1_reflectance": [0, 10000],
    "500_m_16_days_SWIR2_reflectance": [0, 10000],
    "500_m_16_days_SWIR3_reflectance": [0, 10000],
    "500_m_16_days_view_zenith_angle": [0, 18000],
    "500_m_16_days_VI_Quality": [0, 65534],
    "Fpar": [0, 100],
    "FparStdDev": [0, 100],
    "Lai": [0, 100],
    "LaiStdDev": [0, 100],
    "Emis_14": [1, 255],
    "Emis_15": [1, 255],
    "Emis_16": [1, 255],
    "Cycle_1.Date_Mid_Greenup_Phase_1": [1, 32766],
    "Cycle_1.Date_Mid_Senescence_Phase_1": [1, 32766],
    "Cycle_1.EVI2_Growing_Season_Area_1": [1, 32766],
    "Cycle_1.EVI2_Onset_Greenness_Increase_1": [1, 10000],
    "Cycle_1.EVI2_Onset_Greenness_Maximum_1": [1, 10000],
    "Cycle_1.GLSP_QC_1": [0, 100],
    "Cycle_1.Greenness_Agreement_Growing_Season_1": [0, 100],
    "Cycle_1.Growing_Season_Length_1": [1, 366],
    "Cycle_1.Onset_Greenness_Decrease_1": [1, 32766],
    "Cycle_1.Onset_Greenness_Increase_1": [1, 32766],
    "Cycle_1.Onset_Greenness_Maximum_1": [1, 32766],
    "Cycle_1.Onset_Greenness_Minimum_1": [1, 32766],
    "Cycle_1.PGQ_Growing_Season_1": [1, 100],
    "Cycle_1.PGQ_Onset_Greenness_Decrease_1": [1, 100],
    "Cycle_1.PGQ_Onset_Greenness_Increase_1": [1, 100],
    "Cycle_1.PGQ_Onset_Greenness_Maximum_1": [1, 100],
    "Cycle_1.PGQ_Onset_Greenness_Minimum_1": [1, 100],
    "Cycle_1.Rate_Greenness_Decrease_1": [1, 32766],
    "Cycle_1.Rate_Greenness_Increase_1": [1, 32766],
    "Cycle_2.Date_Mid_Greenup_Phase_2": [1, 32766],
    "Cycle_2.Date_Mid_Senescence_Phase_2": [1, 32766],
    "Cycle_2.EVI2_Growing_Season_Area_2": [1, 32766],
    "Cycle_2.EVI2_Onset_Greenness_Increase_2": [1, 10000],
    "Cycle_2.EVI2_Onset_Greenness_Maximum_2": [1, 10000],
    "Cycle_2.GLSP_QC_2": [0, 100],
    "Cycle_2.Greenness_Agreement_Growing_Season_2": [0, 100],
    "Cycle_2.Growing_Season_Length_2": [1, 366],
    "Cycle_2.Onset_Greenness_Decrease_2": [1, 32766],
    "Cycle_2.Onset_Greenness_Increase_2": [1, 32766],
    "Cycle_2.Onset_Greenness_Maximum_2": [1, 32766],
    "Cycle_2.Onset_Greenness_Minimum_2": [1, 32766],
    "Cycle_2.PGQ_Growing_Season_2": [1, 100],
    "Cycle_2.PGQ_Onset_Greenness_Decrease_2": [1, 100],
    "Cycle_2.PGQ_Onset_Greenness_Increase_2": [1, 100],
    "Cycle_2.PGQ_Onset_Greenness_Maximum_2": [1, 100],
    "Cycle_2.PGQ_Onset_Greenness_Minimum_2": [1, 100],
    "Cycle_2.Rate_Greenness_Decrease_2": [1, 32766],
    "Cycle_2.Rate_Greenness_Increase_2": [1, 32766],
}


def date_parser(strdates):
    """Parse a list of dates in the format YYYYDDD, where DDD is day of year."""
    return [
        datetime.date.fromordinal(
            datetime.datetime(int(i[1:5]), 1, 1).toordinal() + int(i[5:]) - 1
        )
        for i in strdates
    ]


@cltoolbox.command("modis", formatter_class=HelpFormatter)
@tsutils.doc(tsutils.docstrings)
def modis_cli(lat, lon, product, band, start_date=None, end_date=None):
    r"""global 250m,500m,1000m 2000- 4D,8D,16D,A:Download MODIS derived data.

    This data are derived data sets from MODIS satellite photos.

    The MODIS Land Cover Type product contains five classification
    schemes, which describe land cover properties derived from
    observations spanning a year's input of Terra- and Aqua-MODIS
    data.  The primary land cover scheme identifies 17 land cover
    classes defined by the International Geosphere Biosphere
    Programme (IGBP), which includes 11 natural vegetation classes,
    3 developed and mosaicked land classes, and three non-vegetated
    land classes.

    The MODIS Terra + Aqua Land Cover Type Yearly L3 Global 500
    m SIN Grid product incorporates five different land cover
    classification schemes, derived through a supervised
    decision-tree classification method.

    V051 Land Cover Type products are produced with revised training
    data and certain algorithm refinements.  For further details,
    please consult the following paper:

    Friedl, M. A., Sulla-Menashe, D., Tan, B., Schneider, A.,
    Ramankutty, N., Sibley, A., and Huang, X. (2010). MODIS
    Collection 5 global land cover: Algorithm refinements and
    characterization of new datasets. Remote Sensing of Environment,
    114, 168-182.

    Land Cover Datasets

    +-------------------+----------+---------------------------+
    | Band              | Abbrev   | Description               |
    +===================+==========+===========================+
    | Land_Cover_Type_1 | IGBP     | global vegetation         |
    |                   |          | classification scheme     |
    +-------------------+----------+---------------------------+
    | Land_Cover_Type_2 | UMD      | University of Maryland    |
    |                   |          | scheme                    |
    +-------------------+----------+---------------------------+
    | Land_Cover_Type_3 | LAI/fPAR | MODIS-derived scheme      |
    +-------------------+----------+---------------------------+
    | Land_Cover_Type_4 | NPP      | MODIS-derived Net Primary |
    |                   |          | Production (NPP) scheme   |
    +-------------------+----------+---------------------------+
    | Land_Cover_Type_5 | PFT      | Plant Functional Type     |
    |                   |          | (PFT) scheme              |
    +-------------------+----------+---------------------------+

    Land Cover Types Description

    +------+-----------+-----------+-----------+-----------+-----------+
    | Code | IGBP      | UMD       | LAI/fPAR  | NPP       | PFT       |
    +======+===========+===========+===========+===========+===========+
    | 0    | Water     | Water     | Water     | Water     | Water     |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 1    | Evergreen | Evergreen | Grasses/  | Evergreen | Evergreen |
    |      | Needle    | Needle    | Cereal    | Needle    | Needle    |
    |      | leaf      | leaf      | crop      | leaf      | leaf      |
    |      | forest    | forest    |           |           |           |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 2    | Evergreen | Evergreen | Shrub     | Evergreen | Evergreen |
    |      | Broadleaf | Broadleaf |           | Broadleaf | Broadleaf |
    |      | forest    | forest    |           |           |           |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 3    | Deciduous | Deciduous | Broadleaf | Deciduous | Deciduous |
    |      | Needle    | Needle    | crop      | Needle    | Needle    |
    |      | leaf      | leaf      |           | leaf      | leaf      |
    |      | forest    | forest    |           |           |           |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 4    | Deciduous | Deciduous | Savanna   | Deciduous | Deciduous |
    |      | Broadleaf | Broadleaf |           | Broadleaf | Broadleaf |
    |      | forest    | forest    |           |           |           |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 5    | Mixed     | Mixed     | Evergreen | Annual    | Shrub     |
    |      | forest    | forest    | Broadleaf | Broadleaf |           |
    |      |           |           | forest    |           |           |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 6    | Closed    | Closed    | Deciduous | Annual    | Grassland |
    |      | shrubland | shrubland | Broadleaf | grass     |           |
    |      |           |           | forest    |           |           |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 7    | Open      | Open      | Evergreen | Non-      | Cereal    |
    |      | shrubland | shrubland | Needle    | vegetated | crops     |
    |      |           |           | leaf      | land      |           |
    |      |           |           | forest    |           |           |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 8    | Woody     | Woody     | Deciduous | Urban     | Broad-    |
    |      | savanna   | savanna   | Needle    |           | leaf      |
    |      |           |           | leaf      |           | crops     |
    |      |           |           | forest    |           |           |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 9    | Savanna   | Savanna   | Non-      |           | Urban and |
    |      |           |           | vegetated |           | built-up  |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 10   | Grassland | Grassland | Urban     |           | Snow and  |
    |      |           |           |           |           | ice       |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 11   | Permanent |           |           |           | Barren or |
    |      | wetlands  |           |           |           | sparse    |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 12   | Croplands | Cropland  |           |           |           |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 13   | Urban and | Urban and |           |           |           |
    |      | built-up  | built-up  |           |           |           |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 14   | Cropland  |           |           |           |           |
    |      | /Natural  |           |           |           |           |
    |      | mosaic    |           |           |           |           |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 15   | Snow and  |           |           |           |           |
    |      | ice       |           |           |           |           |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 16   | Barren or | Barren or |           |           |           |
    |      | sparsely  | sparsely  |           |           |           |
    |      | vegetated | vegetated |           |           |           |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 254  | Unclassi  | Unclassi  | Unclassi  | Unclassi  | Unclassi  |
    |      | fied      | fied      | fied      | fied      | fies      |
    +------+-----------+-----------+-----------+-----------+-----------+
    | 255  | Fill      | Fill      | Fill      | Fill      | Fill      |
    |      | Value     | Value     | Value     | Value     | Value     |
    +------+-----------+-----------+-----------+-----------+-----------+

    Parameters
    ----------
    lat : float
        Latitude (required): Enter single geographic point by
        latitude.

    lon : float
        Longitude (required): Enter single geographic point by
        longitude.

    product : str
        One of the following values in the 'product'
        column.

        +--------------+---------------------------+-------------+--------------+
        | product      | Description               | Frequency   |   Resolution |
        |              |                           |             |          (m) |
        +==============+===========================+=============+==============+
        | ECO4ESIPTJPL | ECOSTRESS Evaporative     | Varies      |           70 |
        |              | Stress Index PT-JPL (ESI) |             |              |
        +--------------+---------------------------+-------------+--------------+
        | ECO4WUE      | ECOSTRESS Water Use       | Varies      |           70 |
        |              | Efficiency (WUE)          |             |              |
        +--------------+---------------------------+-------------+--------------+
        | GEDI03       | GEDI Gridded Land Surface | One-time    |         1000 |
        |              | Metrics (LSM)             |             |              |
        +--------------+---------------------------+-------------+--------------+
        | GEDI04_B     | GEDI Gridded Aboveground  | One-time    |         1000 |
        |              | Biomass Density (AGBD)    |             |              |
        +--------------+---------------------------+-------------+--------------+
        | MCD12Q1      | MODIS/Terra+Aqua Land     | Yearly      |          500 |
        |              | Cover Type (LC)           |             |              |
        +--------------+---------------------------+-------------+--------------+
        | MCD12Q2      | MODIS/Terra+Aqua Land     | Yearly      |          500 |
        |              | Cover Dynamics (LCD)      |             |              |
        +--------------+---------------------------+-------------+--------------+
        | MCD15A2H     | MODIS/Terra+Aqua Leaf     | 8-Day       |          500 |
        |              | Area Index/FPAR           |             |              |
        |              | (LAI/FPAR)                |             |              |
        +--------------+---------------------------+-------------+--------------+
        | MCD15A3H     | MODIS/Terra+Aqua Leaf     | 4-Day       |          500 |
        |              | Area Index/FPAR           |             |              |
        |              | (LAI/FPAR)                |             |              |
        +--------------+---------------------------+-------------+--------------+
        | MCD19A3      | MODIS/Terra+Aqua BRDF     | 8-Day       |         1000 |
        |              | Model Parameters (MAIAC)  |             |              |
        +--------------+---------------------------+-------------+--------------+
        | MCD43A       | MODIS/Terra+Aqua BRDF and | Daily       |          500 |
        |              | Calculated Albedo         |             |              |
        |              | (BRDF/MCD43A)             |             |              |
        +--------------+---------------------------+-------------+--------------+
        | MCD43A1      | MODIS/Terra+Aqua          | Daily       |          500 |
        |              | BRDF/Albedo Model         |             |              |
        |              | Parameters (BRDF)         |             |              |
        +--------------+---------------------------+-------------+--------------+
        | MCD43A4      | MODIS/Terra+Aqua Nadir    | Daily       |          500 |
        |              | BRDF-Adjusted Reflectance |             |              |
        |              | (NBAR)                    |             |              |
        +--------------+---------------------------+-------------+--------------+
        | MCD64A1      | MODIS/Terra+Aqua Burned   | Monthly     |          500 |
        |              | Area (Burned Area)        |             |              |
        +--------------+---------------------------+-------------+--------------+
        | MOD09A1      | MODIS/Terra Surface       | 8-Day       |          500 |
        |              | Reflectance (SREF)        |             |              |
        +--------------+---------------------------+-------------+--------------+
        | MOD11A2      | MODIS/Terra Land Surface  | 8-Day       |         1000 |
        |              | Temperature and           |             |              |
        |              | Emissivity (LST)          |             |              |
        +--------------+---------------------------+-------------+--------------+
        | MOD13Q1      | MODIS/Terra Vegetation    | 16-Day      |          250 |
        |              | Indices (NDVI/EVI)        |             |              |
        +--------------+---------------------------+-------------+--------------+
        | MOD14A2      | MODIS/Terra Thermal       | 8-Day       |         1000 |
        |              | Anomalies/Fire (Fire)     |             |              |
        +--------------+---------------------------+-------------+--------------+
        | MOD15A2H     | MODIS/Terra Leaf Area     | 8-Day       |          500 |
        |              | Index/FPAR (LAI/FPAR)     |             |              |
        +--------------+---------------------------+-------------+--------------+
        | MOD16A2      | MODIS/Terra Net           | 8-Day       |          500 |
        |              | Evapotranspiration (ET)   |             |              |
        +--------------+---------------------------+-------------+--------------+
        | MOD17A2H     | MODIS/Terra Gross Primary | 8-Day       |          500 |
        |              | Productivity (GPP)        |             |              |
        +--------------+---------------------------+-------------+--------------+
        | MOD17A3HGF   | MODIS/Terra Net Primary   | Yearly      |          500 |
        |              | Production Gap-Filled     |             |              |
        |              | (NPP)                     |             |              |
        +--------------+---------------------------+-------------+--------------+
        | MOD21A2      | MODIS/Terra Land Surface  | 8-Day       |         1000 |
        |              | Temperature/3-Band        |             |              |
        |              | Emissivity (LSTE)         |             |              |
        +--------------+---------------------------+-------------+--------------+
        | MOD44B       | MODIS/Terra Vegetation    | Yearly      |          250 |
        |              | Continuous Fields (VCF)   |             |              |
        +--------------+---------------------------+-------------+--------------+
        | MYD09A1      | MODIS/Aqua Surface        | 8-Day       |          500 |
        |              | Reflectance (SREF)        |             |              |
        +--------------+---------------------------+-------------+--------------+
        | MYD11A2      | MODIS/Aqua Land Surface   | 8-Day       |         1000 |
        |              | Temperature and           |             |              |
        |              | Emissivity (LST)          |             |              |
        +--------------+---------------------------+-------------+--------------+
        | MYD13Q1      | MODIS/Aqua Vegetation     | 16-Day      |          250 |
        |              | Indices (NDVI/EVI)        |             |              |
        +--------------+---------------------------+-------------+--------------+
        | MYD14A2      | MODIS/Aqua Thermal        | 8-Day       |         1000 |
        |              | Anomalies/Fire (Fire)     |             |              |
        +--------------+---------------------------+-------------+--------------+
        | MYD15A2H     | MODIS/Aqua Leaf Area      | 8-Day       |          500 |
        |              | Index/FPAR (LAI/FPAR)     |             |              |
        +--------------+---------------------------+-------------+--------------+
        | MYD16A2      | MODIS/Aqua Net            | 8-Day       |          500 |
        |              | Evapotranspiration (ET)   |             |              |
        +--------------+---------------------------+-------------+--------------+
        | MYD17A2H     | MODIS/Aqua Gross Primary  | 8-Day       |          500 |
        |              | Productivity (GPP)        |             |              |
        +--------------+---------------------------+-------------+--------------+
        | MYD17A3HGF   | MODIS/Aqua Net Primary    | Yearly      |          500 |
        |              | Production Gap-Filled     |             |              |
        |              | (NPP)                     |             |              |
        +--------------+---------------------------+-------------+--------------+
        | MYD21A2      | MODIS/Aqua Land Surface   | 8-Day       |         1000 |
        |              | Temperature/3-Band        |             |              |
        |              | Emissivity (LSTE)         |             |              |
        +--------------+---------------------------+-------------+--------------+
        | SIF005       | SIF Estimates from Fused  | Monthly     |         5000 |
        |              | SCIAMACHY and GOME-2      |             |              |
        |              | (SIF)                     |             |              |
        +--------------+---------------------------+-------------+--------------+
        | SIF_ANN      | SIF Estimates from OCO-2  | 16-day      |         5000 |
        |              | SIF and MODIS (SIF)       |             |              |
        +--------------+---------------------------+-------------+--------------+
        | VNP09A1      | VIIRS/S-NPP Surface       | 8-Day       |         1000 |
        |              | Reflectance (SREF)        |             |              |
        +--------------+---------------------------+-------------+--------------+
        | VNP09H1      | VIIRS/S-NPP Surface       | 8-Day       |          500 |
        |              | Reflectance (SREF)        |             |              |
        +--------------+---------------------------+-------------+--------------+
        | VNP13A1      | VIIRS/S-NPP Vegetation    | 16-Day      |          500 |
        |              | Indices (NDVI/EVI)        |             |              |
        +--------------+---------------------------+-------------+--------------+
        | VNP15A2H     | VIIRS/S-NPP Leaf Area     | 8-Day       |          500 |
        |              | Index/FPAR (LAI/FPAR)     |             |              |
        +--------------+---------------------------+-------------+--------------+
        | VNP21A2      | VIIRS/S-NPP Land Surface  | 8-Day       |         1000 |
        |              | Temperature and           |             |              |
        |              | Emissivity (LSTE)         |             |              |
        +--------------+---------------------------+-------------+--------------+
        | VNP22Q2      | VIIRS/S-NPP Land Cover    | Yearly      |          500 |
        |              | Dynamics (LCD)            |             |              |
        +--------------+---------------------------+-------------+--------------+

    band : str
        One of the following. The 'band' selected from the first column must
        match the 'product' keyword in the table title.

        ECO4ESIPTJPL

        +--------+------------------------------+--------------+---------+
        | band   | Description                  | Units        | Range   |
        +========+==============================+==============+=========+
        | ESIavg | Evaporative Stress Index     | ratio_ET/PET | 0 to    |
        |        |                              |              | 2       |
        +--------+------------------------------+--------------+---------+
        | PET    | Potential Evapotranspiration | W/m^2        | 0 to    |
        |        |                              |              | 2000    |
        +--------+------------------------------+--------------+---------+

        ECO4WUE

        +--------+----------------------+--------------+---------+
        | band   | Description          | Units        | Range   |
        +========+======================+==============+=========+
        | WUEavg | Water Use Efficiency | ratio_GPP/ET | 0 to    |
        |        |                      |              | 20      |
        +--------+----------------------+--------------+---------+

        GEDI03

        +------------------------+--------------------------------+---------+
        | band                   | Description                    | Units   |
        +========================+================================+=========+
        | counts                 | count of valid laser           | counts  |
        |                        | footprints                     |         |
        +------------------------+--------------------------------+---------+
        | elev_lowestmode_mean   | mean elevation of the lowest   | meters  |
        |                        | mode                           |         |
        +------------------------+--------------------------------+---------+
        | elev_lowestmode_stddev | stddev elevation of the lowest | meters  |
        |                        | mode                           |         |
        +------------------------+--------------------------------+---------+
        | rh100_mean             | mean 100th percentile of       | meters  |
        |                        | waveform energy relative to    |         |
        |                        | ground                         |         |
        +------------------------+--------------------------------+---------+
        | rh100_stddev           | stddev 100th percentile of     | meters  |
        |                        | waveform energy relative to    |         |
        |                        | ground                         |         |
        +------------------------+--------------------------------+---------+

        GEDI04_B

        +--------+------------------------------+---------+
        | band   | Description                  | Units   |
        +========+==============================+=========+
        | MI     | mode of interference         |         |
        +--------+------------------------------+---------+
        | MU     | mean aboveground biomass     | Mg/ha   |
        |        | density                      |         |
        +--------+------------------------------+---------+
        | NC     | number of clusters           | counts  |
        +--------+------------------------------+---------+
        | NS     | number of samples            | counts  |
        +--------+------------------------------+---------+
        | PE     | standard error as a fraction | percent |
        |        | of the estimated mean AGBD   |         |
        +--------+------------------------------+---------+
        | PS     | prediction stratum           |         |
        +--------+------------------------------+---------+
        | QF     | quality flag                 |         |
        +--------+------------------------------+---------+
        | SE     | mean aboveground biomass     | Mg/ha   |
        |        | density standard error       |         |
        +--------+------------------------------+---------+
        | V1     | variance component 1         |         |
        +--------+------------------------------+---------+
        | V2     | variance component 2         |         |
        +--------+------------------------------+---------+

        MCD12Q1

        +---------------------+--------------------------------+--------------+---------+
        | band                | Description                    | Units        | Range   |
        +=====================+================================+==============+=========+
        | LC_Prop1            | FAO-Land Cover Classification  | class        | 1 to    |
        |                     | System 1 (LCCS1) land cover    |              | 43      |
        |                     | layer                          |              |         |
        +---------------------+--------------------------------+--------------+---------+
        | LC_Prop1_Assessment | LCCS1 land cover layer         | percent      | 0 to    |
        |                     | confidence                     |              | 100     |
        +---------------------+--------------------------------+--------------+---------+
        | LC_Prop2            | FAO-LCCS2 land use layer       | class        | 1 to    |
        |                     |                                |              | 40      |
        +---------------------+--------------------------------+--------------+---------+
        | LC_Prop2_Assessment | LCCS2 land use layer           | percent      | 0 to    |
        |                     | confidence                     |              | 100     |
        +---------------------+--------------------------------+--------------+---------+
        | LC_Prop3            | FAO-LCCS3 surface hydrology    | class        | 1 to    |
        |                     | layer                          |              | 51      |
        +---------------------+--------------------------------+--------------+---------+
        | LC_Prop3_Assessment | LCCS3 surface hydrology layer  | percent      | 0 to    |
        |                     | confidence                     |              | 100     |
        +---------------------+--------------------------------+--------------+---------+
        | LC_Type1            | Land Cover Type 1: Annual      | class        | 1 to    |
        |                     | International Geosphere-       |              | 17      |
        |                     | Biosphere Programme (IGBP)     |              |         |
        |                     | classification                 |              |         |
        +---------------------+--------------------------------+--------------+---------+
        | LC_Type2            | Land Cover Type 2: Annual      | class        | 0 to    |
        |                     | University of Maryland (UMD)   |              | 15      |
        |                     | classification                 |              |         |
        +---------------------+--------------------------------+--------------+---------+
        | LC_Type3            | Land Cover Type 3: Annual Leaf | class        | 0 to    |
        |                     | Area Index (LAI)               |              | 10      |
        |                     | classification                 |              |         |
        +---------------------+--------------------------------+--------------+---------+
        | LC_Type4            | Land Cover Type 4: Annual      | class        | 0 to    |
        |                     | BIOME-Biogeochemical Cycles    |              | 8       |
        |                     | (BGC) classification           |              |         |
        +---------------------+--------------------------------+--------------+---------+
        | LC_Type5            | Land Cover Type 5: Annual      | class        | 0 to    |
        |                     | Plant Functional Types         |              | 11      |
        |                     | classification                 |              |         |
        +---------------------+--------------------------------+--------------+---------+
        | LW                  | Binary land (class 2) / water  | class        | 1 to    |
        |                     | (class 1) mask derived from    |              | 2       |
        |                     | MOD44W                         |              |         |
        +---------------------+--------------------------------+--------------+---------+
        | QC                  | Product quality flags          | quality-flag | 0 to    |
        |                     |                                |              | 10      |
        +---------------------+--------------------------------+--------------+---------+

        MCD12Q2

        +----------------------------+-----------------------------+-----------------------+----------+
        | band                       | Description                 | Units                 | Range    |
        +============================+=============================+=======================+==========+
        | Dormancy.Num_Modes_01      | Onset Dormancy              | days_since_1970-01-01 | 11138 to |
        |                            |                             |                       | 32766    |
        +----------------------------+-----------------------------+-----------------------+----------+
        | Dormancy.Num_Modes_02      | Onset Dormancy              | days_since_1970-01-01 | 11138 to |
        |                            |                             |                       | 32766    |
        +----------------------------+-----------------------------+-----------------------+----------+
        | EVI_Amplitude.Num_Modes_01 | EVI Amplitude               | NBAR-EVI2             | 0 to     |
        |                            |                             |                       | 10000    |
        +----------------------------+-----------------------------+-----------------------+----------+
        | EVI_Amplitude.Num_Modes_02 | EVI Amplitude               | NBAR-EVI2             | 0 to     |
        |                            |                             |                       | 10000    |
        +----------------------------+-----------------------------+-----------------------+----------+
        | EVI_Area.Num_Modes_01      | EVI Area                    | NBAR-EVI2             | 0 to     |
        |                            |                             |                       | 3700     |
        +----------------------------+-----------------------------+-----------------------+----------+
        | EVI_Area.Num_Modes_02      | EVI Area                    | NBAR-EVI2             | 0 to     |
        |                            |                             |                       | 3700     |
        +----------------------------+-----------------------------+-----------------------+----------+
        | EVI_Minimum.Num_Modes_01   | Minimum EVI                 | NBAR-EVI2             | 0 to     |
        |                            |                             |                       | 10000    |
        +----------------------------+-----------------------------+-----------------------+----------+
        | EVI_Minimum.Num_Modes_02   | Minimum EVI                 | NBAR-EVI2             | 0 to     |
        |                            |                             |                       | 10000    |
        +----------------------------+-----------------------------+-----------------------+----------+
        | Greenup.Num_Modes_01       | Onset Greenness Increase    | days_since_1970-01-01 | 11138 to |
        |                            |                             |                       | 32766    |
        +----------------------------+-----------------------------+-----------------------+----------+
        | Greenup.Num_Modes_02       | Onset Greenness Increase    | days_since_1970-01-01 | 11138 to |
        |                            |                             |                       | 32766    |
        +----------------------------+-----------------------------+-----------------------+----------+
        | Maturity.Num_Modes_01      | Onset Maturity              | days_since_1970-01-01 | 11138 to |
        |                            |                             |                       | 32766    |
        +----------------------------+-----------------------------+-----------------------+----------+
        | Maturity.Num_Modes_02      | Onset Maturity              | days_since_1970-01-01 | 11138 to |
        |                            |                             |                       | 32766    |
        +----------------------------+-----------------------------+-----------------------+----------+
        | MidGreendown.Num_Modes_01  | Middle Greenness Decrease   | days_since_1970-01-01 | 11138 to |
        |                            |                             |                       | 32766    |
        +----------------------------+-----------------------------+-----------------------+----------+
        | MidGreendown.Num_Modes_02  | Middle Greenness Decrease   | days_since_1970-01-01 | 11138 to |
        |                            |                             |                       | 32766    |
        +----------------------------+-----------------------------+-----------------------+----------+
        | MidGreenup.Num_Modes_01    | Middle Greenness Increase   | days_since_1970-01-01 | 11138 to |
        |                            |                             |                       | 32766    |
        +----------------------------+-----------------------------+-----------------------+----------+
        | MidGreenup.Num_Modes_02    | Middle Greenness Increase   | days_since_1970-01-01 | 11138 to |
        |                            |                             |                       | 32766    |
        +----------------------------+-----------------------------+-----------------------+----------+
        | NumCycles                  | Number of Cycles            |                       | 0 to     |
        |                            |                             |                       | 7        |
        +----------------------------+-----------------------------+-----------------------+----------+
        | QA_Detailed.Num_Modes_01   | Quality Assessment Detailed |                       | 0 to     |
        |                            |                             |                       | 16383    |
        +----------------------------+-----------------------------+-----------------------+----------+
        | QA_Detailed.Num_Modes_02   | Quality Assessment Detailed |                       | 0 to     |
        |                            |                             |                       | 16383    |
        +----------------------------+-----------------------------+-----------------------+----------+
        | QA_Overall.Num_Modes_01    | Quality Assessment Overall  |                       | 0 to     |
        |                            |                             |                       | 3        |
        +----------------------------+-----------------------------+-----------------------+----------+
        | QA_Overall.Num_Modes_02    | Quality Assessment Overall  |                       | 0 to     |
        |                            |                             |                       | 3        |
        +----------------------------+-----------------------------+-----------------------+----------+

        MCD15A2H

        +-----------------+--------------------------------+------------+---------+
        | band            | Description                    | Units      | Range   |
        +=================+================================+============+=========+
        | FparExtra_QC    | Extra detail Quality for LAI   | class-flag | 0 to    |
        |                 | and FPAR                       |            | 254     |
        +-----------------+--------------------------------+------------+---------+
        | FparLai_QC      | Quality for LAI and FPAR       | class-flag | 0 to    |
        |                 |                                |            | 254     |
        +-----------------+--------------------------------+------------+---------+
        | FparStdDev_500m | Standard deviation of FPAR     | percent    | 0 to    |
        |                 |                                |            | 100     |
        +-----------------+--------------------------------+------------+---------+
        | Fpar_500m       | Fraction of photosynthetically | percent    | 0 to    |
        |                 | active radiation               |            | 100     |
        +-----------------+--------------------------------+------------+---------+
        | LaiStdDev_500m  | Standard deviation for LAI     | m^2/m^2    | 0 to    |
        |                 |                                |            | 100     |
        +-----------------+--------------------------------+------------+---------+
        | Lai_500m        | Leaf area index                | m^2/m^2    | 0 to    |
        |                 |                                |            | 100     |
        +-----------------+--------------------------------+------------+---------+

        MCD15A3H

        +-----------------+--------------------------------+------------+---------+
        | band            | Description                    | Units      | Range   |
        +=================+================================+============+=========+
        | FparExtra_QC    | Extra detail Quality for LAI   | class-flag | 0 to    |
        |                 | and FPAR                       |            | 254     |
        +-----------------+--------------------------------+------------+---------+
        | FparLai_QC      | Quality for LAI and FPAR       | class-flag | 0 to    |
        |                 |                                |            | 254     |
        +-----------------+--------------------------------+------------+---------+
        | FparStdDev_500m | Standard deviation of FPAR     | percent    | 0 to    |
        |                 |                                |            | 100     |
        +-----------------+--------------------------------+------------+---------+
        | Fpar_500m       | Fraction of photosynthetically | percent    | 0 to    |
        |                 | active radiation               |            | 100     |
        +-----------------+--------------------------------+------------+---------+
        | LaiStdDev_500m  | Standard deviation for LAI     | m^2/m^2    | 0 to    |
        |                 |                                |            | 100     |
        +-----------------+--------------------------------+------------+---------+
        | Lai_500m        | Leaf area index                | m^2/m^2    | 0 to    |
        |                 |                                |            | 100     |
        +-----------------+--------------------------------+------------+---------+

        MCD19A3

        +------------+------------------------------+-----------+
        | band       | Description                  | Range     |
        +============+==============================+===========+
        | Kgeo       | RTLS geometric kernel        | -32766 to |
        |            | parameter for bands 1-8      | 32767     |
        +------------+------------------------------+-----------+
        | Kiso       | RTLS isotropic kernel        | -32766 to |
        |            | parameter for bands 1-8      | 32767     |
        +------------+------------------------------+-----------+
        | Kvol       | RTLS volumetric kernel       | -32766 to |
        |            | parameter for bands 1-8      | 32767     |
        +------------+------------------------------+-----------+
        | Sur_albedo | Surface albedo for bands 1-8 | -100 to   |
        |            |                              | 16000     |
        +------------+------------------------------+-----------+
        | UpdateDay  | Number of days since last    | 0 to      |
        |            | update to the current day    | 254       |
        +------------+------------------------------+-----------+

        MCD43A

        +------------------+----------------------------+
        | band             | Description                |
        +==================+============================+
        | nir_actual       | Blue-sky albedo nir        |
        +------------------+----------------------------+
        | nir_black        | Black-sky albedo nir       |
        +------------------+----------------------------+
        | nir_white        | White-sky albedo nir       |
        +------------------+----------------------------+
        | shortwave_actual | Blue-sky albedo shortwave  |
        +------------------+----------------------------+
        | shortwave_black  | Black-sky albedo shortwave |
        +------------------+----------------------------+
        | shortwave_white  | White-sky albedo shortwave |
        +------------------+----------------------------+
        | vis_actual       | Blue-sky albedo vis        |
        +------------------+----------------------------+
        | vis_black        | Black-sky albedo vis       |
        +------------------+----------------------------+
        | vis_white        | White-sky albedo vis       |
        +------------------+----------------------------+

        MCD43A1

        +----------------------------------------------+----------------------+-----------+---------+
        | band                                         | Description          | Units     | Range   |
        +==============================================+======================+===========+=========+
        | BDRF_Albedo_Band_Mandatory_Quality_Band1     | Quality Band1        | bit_field | 0 to    |
        |                                              |                      |           | 254     |
        +----------------------------------------------+----------------------+-----------+---------+
        | BDRF_Albedo_Band_Mandatory_Quality_Band2     | Quality Band2        | bit_field | 0 to    |
        |                                              |                      |           | 254     |
        +----------------------------------------------+----------------------+-----------+---------+
        | BDRF_Albedo_Band_Mandatory_Quality_Band3     | Quality Band3        | bit_field | 0 to    |
        |                                              |                      |           | 254     |
        +----------------------------------------------+----------------------+-----------+---------+
        | BDRF_Albedo_Band_Mandatory_Quality_Band4     | Quality Band4        | bit_field | 0 to    |
        |                                              |                      |           | 254     |
        +----------------------------------------------+----------------------+-----------+---------+
        | BDRF_Albedo_Band_Mandatory_Quality_Band5     | Quality Band5        | bit_field | 0 to    |
        |                                              |                      |           | 254     |
        +----------------------------------------------+----------------------+-----------+---------+
        | BDRF_Albedo_Band_Mandatory_Quality_Band6     | Quality Band6        | bit_field | 0 to    |
        |                                              |                      |           | 254     |
        +----------------------------------------------+----------------------+-----------+---------+
        | BDRF_Albedo_Band_Mandatory_Quality_Band7     | Quality Band7        | bit_field | 0 to    |
        |                                              |                      |           | 254     |
        +----------------------------------------------+----------------------+-----------+---------+
        | BDRF_Albedo_Band_Mandatory_Quality_nir       | Quality nir          | bit_field | 0 to    |
        |                                              |                      |           | 254     |
        +----------------------------------------------+----------------------+-----------+---------+
        | BDRF_Albedo_Band_Mandatory_Quality_shortwave | Quality shortwave    | bit_field | 0 to    |
        |                                              |                      |           | 254     |
        +----------------------------------------------+----------------------+-----------+---------+
        | BDRF_Albedo_Band_Mandatory_Quality_vis       | Quality vis          | bit_field | 0 to    |
        |                                              |                      |           | 254     |
        +----------------------------------------------+----------------------+-----------+---------+
        | BRDF_Albedo_Parameters_Band1                 | Parameters Band1     |           | 0 to    |
        |                                              |                      |           | 32766   |
        +----------------------------------------------+----------------------+-----------+---------+
        | BRDF_Albedo_Parameters_Band2                 | Parameters Band2     |           | 0 to    |
        |                                              |                      |           | 32766   |
        +----------------------------------------------+----------------------+-----------+---------+
        | BRDF_Albedo_Parameters_Band3                 | Parameters Band3     |           | 0 to    |
        |                                              |                      |           | 32766   |
        +----------------------------------------------+----------------------+-----------+---------+
        | BRDF_Albedo_Parameters_Band4                 | Parameters Band4     |           | 0 to    |
        |                                              |                      |           | 32766   |
        +----------------------------------------------+----------------------+-----------+---------+
        | BRDF_Albedo_Parameters_Band5                 | Parameters Band5     |           | 0 to    |
        |                                              |                      |           | 32766   |
        +----------------------------------------------+----------------------+-----------+---------+
        | BRDF_Albedo_Parameters_Band6                 | Parameters Band6     |           | 0 to    |
        |                                              |                      |           | 32766   |
        +----------------------------------------------+----------------------+-----------+---------+
        | BRDF_Albedo_Parameters_Band7                 | Parameters Band7     |           | 0 to    |
        |                                              |                      |           | 32766   |
        +----------------------------------------------+----------------------+-----------+---------+
        | BRDF_Albedo_Parameters_nir                   | Parameters nir       |           | 0 to    |
        |                                              |                      |           | 32766   |
        +----------------------------------------------+----------------------+-----------+---------+
        | BRDF_Albedo_Parameters_shortwave             | Parameters shortwave |           | 0 to    |
        |                                              |                      |           | 32766   |
        +----------------------------------------------+----------------------+-----------+---------+
        | BRDF_Albedo_Parameters_vis                   | Parameters vis       |           | 0 to    |
        |                                              |                      |           | 32766   |
        +----------------------------------------------+----------------------+-----------+---------+

        MCD43A4

        +------------------------------------------+-------------------------+--------------------+---------+
        | band                                     | Description             | Units              | Range   |
        +==========================================+=========================+====================+=========+
        | BRDF_Albedo_Band_Mandatory_Quality_Band1 | Quality Band1           | concatenated flags | 0 to    |
        |                                          |                         |                    | 254     |
        +------------------------------------------+-------------------------+--------------------+---------+
        | BRDF_Albedo_Band_Mandatory_Quality_Band2 | Quality Band2           | concatenated flags | 0 to    |
        |                                          |                         |                    | 254     |
        +------------------------------------------+-------------------------+--------------------+---------+
        | BRDF_Albedo_Band_Mandatory_Quality_Band3 | Quality Band3           | concatenated flags | 0 to    |
        |                                          |                         |                    | 254     |
        +------------------------------------------+-------------------------+--------------------+---------+
        | BRDF_Albedo_Band_Mandatory_Quality_Band4 | Quality Band4           | concatenated flags | 0 to    |
        |                                          |                         |                    | 254     |
        +------------------------------------------+-------------------------+--------------------+---------+
        | BRDF_Albedo_Band_Mandatory_Quality_Band5 | Quality Band5           | concatenated flags | 0 to    |
        |                                          |                         |                    | 254     |
        +------------------------------------------+-------------------------+--------------------+---------+
        | BRDF_Albedo_Band_Mandatory_Quality_Band6 | Quality Band6           | concatenated flags | 0 to    |
        |                                          |                         |                    | 254     |
        +------------------------------------------+-------------------------+--------------------+---------+
        | BRDF_Albedo_Band_Mandatory_Quality_Band7 | Quality Band7           | concatenated flags | 0 to    |
        |                                          |                         |                    | 254     |
        +------------------------------------------+-------------------------+--------------------+---------+
        | Nadir_Reflectance_Band1                  | Nadir Reflectance Band1 |                    | 0 to    |
        |                                          |                         |                    | 32766   |
        +------------------------------------------+-------------------------+--------------------+---------+
        | Nadir_Reflectance_Band2                  | Nadir Reflectance Band2 |                    | 0 to    |
        |                                          |                         |                    | 32766   |
        +------------------------------------------+-------------------------+--------------------+---------+
        | Nadir_Reflectance_Band3                  | Nadir Reflectance Band3 |                    | 0 to    |
        |                                          |                         |                    | 32766   |
        +------------------------------------------+-------------------------+--------------------+---------+
        | Nadir_Reflectance_Band4                  | Nadir Reflectance Band4 |                    | 0 to    |
        |                                          |                         |                    | 32766   |
        +------------------------------------------+-------------------------+--------------------+---------+
        | Nadir_Reflectance_Band5                  | Nadir Reflectance Band5 |                    | 0 to    |
        |                                          |                         |                    | 32766   |
        +------------------------------------------+-------------------------+--------------------+---------+
        | Nadir_Reflectance_Band6                  | Nadir Reflectance Band6 |                    | 0 to    |
        |                                          |                         |                    | 32766   |
        +------------------------------------------+-------------------------+--------------------+---------+
        | Nadir_Reflectance_Band7                  | Nadir Reflectance Band7 |                    | 0 to    |
        |                                          |                         |                    | 32766   |
        +------------------------------------------+-------------------------+--------------------+---------+

        MCD64A1

        +-----------------------+------------------------------+-------------+---------+
        | band                  | Description                  | Units       | Range   |
        +=======================+==============================+=============+=========+
        | Burn_Date             | ordinal day of burn          | day_of_year | 0 to    |
        |                       |                              |             | 366     |
        +-----------------------+------------------------------+-------------+---------+
        | Burn_Date_Uncertainty | uncertainty in day of burn   | days        | 0 to    |
        |                       |                              |             | 100     |
        +-----------------------+------------------------------+-------------+---------+
        | First_Day             | first day of reliable change | day_of_year | 1 to    |
        |                       | detection                    |             | 366     |
        +-----------------------+------------------------------+-------------+---------+
        | Last_Day              | last day of reliable change  | day_of_year | 1 to    |
        |                       | detection                    |             | 366     |
        +-----------------------+------------------------------+-------------+---------+
        | QA                    | quality assurance indicators | bit_field   | 0 to    |
        |                       |                              |             | 255     |
        +-----------------------+------------------------------+-------------+---------+

        MOD09A1

        +----------------------+--------------------------------+-------------+------------+
        | band                 | Description                    | Units       | Range      |
        +======================+================================+=============+============+
        | sur_refl_b01         | Surface reflectance for band 1 | reflectance | -100 to    |
        |                      |                                |             | 16000      |
        +----------------------+--------------------------------+-------------+------------+
        | sur_refl_b02         | Surface reflectance for band 2 | reflectance | -100 to    |
        |                      |                                |             | 16000      |
        +----------------------+--------------------------------+-------------+------------+
        | sur_refl_b03         | Surface reflectance for band 3 | reflectance | -100 to    |
        |                      |                                |             | 16000      |
        +----------------------+--------------------------------+-------------+------------+
        | sur_refl_b04         | Surface reflectance for band 4 | reflectance | -100 to    |
        |                      |                                |             | 16000      |
        +----------------------+--------------------------------+-------------+------------+
        | sur_refl_b05         | Surface reflectance for band 5 | reflectance | -100 to    |
        |                      |                                |             | 16000      |
        +----------------------+--------------------------------+-------------+------------+
        | sur_refl_b06         | Surface reflectance for band 6 | reflectance | -100 to    |
        |                      |                                |             | 16000      |
        +----------------------+--------------------------------+-------------+------------+
        | sur_refl_b07         | Surface reflectance for band 7 | reflectance | -100 to    |
        |                      |                                |             | 16000      |
        +----------------------+--------------------------------+-------------+------------+
        | sur_refl_day_of_year | Surface reflectance day of     | day_of_year | 0 to       |
        |                      | year                           |             | 366        |
        +----------------------+--------------------------------+-------------+------------+
        | sur_refl_qc_500m     | Surface reflectance 500m       | bit_field   | 0 to       |
        |                      | quality control flags          |             | 4294966531 |
        +----------------------+--------------------------------+-------------+------------+
        | sur_refl_raz         | Relative azimuth               | degree      | -18000 to  |
        |                      |                                |             | 18000      |
        +----------------------+--------------------------------+-------------+------------+
        | sur_refl_state_500m  | Surface reflectance 500m state | bit_field   | 0 to       |
        |                      | flags                          |             | 57343      |
        +----------------------+--------------------------------+-------------+------------+
        | sur_refl_szen        | Solar zenith                   | degree      | 0 to       |
        |                      |                                |             | 18000      |
        +----------------------+--------------------------------+-------------+------------+
        | sur_refl_vzen        | View zenith                    | degree      | 0 to       |
        |                      |                                |             | 18000      |
        +----------------------+--------------------------------+-------------+------------+

        MOD11A2

        +------------------+--------------------------------+---------+---------+
        | band             | Description                    | Range   | Units   |
        +==================+================================+=========+=========+
        | Clear_sky_days   | Day clear-sky coverage         | 1 to    |         |
        |                  |                                | 255     |         |
        +------------------+--------------------------------+---------+---------+
        | Clear_sky_nights | Night clear-sky coverage       | 1 to    |         |
        |                  |                                | 255     |         |
        +------------------+--------------------------------+---------+---------+
        | Day_view_angl    | View zenith angle of day       | 0 to    | degree  |
        |                  | observation                    | 130     |         |
        +------------------+--------------------------------+---------+---------+
        | Day_view_time    | Local time of day observation  | 0 to    | hrs     |
        |                  |                                | 240     |         |
        +------------------+--------------------------------+---------+---------+
        | Emis_31          | Band 31 emissivity             | 1 to    |         |
        |                  |                                | 255     |         |
        +------------------+--------------------------------+---------+---------+
        | Emis_32          | Band 32 emissivity             | 1 to    |         |
        |                  |                                | 255     |         |
        +------------------+--------------------------------+---------+---------+
        | LST_Day_1km      | Daytime Land Surface           | 7500 to | degK    |
        |                  | Temperature                    | 65535   |         |
        +------------------+--------------------------------+---------+---------+
        | LST_Night_1km    | Night Land Surface Temperature | 7500 to | degK    |
        |                  |                                | 65535   |         |
        +------------------+--------------------------------+---------+---------+
        | Night_view_angl  | View zenith angle of night     | 0 to    | degree  |
        |                  | observation                    | 130     |         |
        +------------------+--------------------------------+---------+---------+
        | Night_view_time  | Local time of night            | 0 to    | hrs     |
        |                  | observation                    | 240     |         |
        +------------------+--------------------------------+---------+---------+
        | QC_Day           | Daytime LST Quality Indicators | 0 to    |         |
        |                  |                                | 255     |         |
        +------------------+--------------------------------+---------+---------+
        | QC_Night         | Nighttime LST Quality          | 0 to    |         |
        |                  | indicators                     | 255     |         |
        +------------------+--------------------------------+---------+---------+

        MOD13Q1

        +----------------------------------------+-------------------------------+-------------+----------+
        | band                                   | Description                   | Units       | Range    |
        +========================================+===============================+=============+==========+
        | 250m_16_days_blue_reflectance          | Surface Reflectance Band 3    | reflectance | 0 to     |
        |                                        |                               |             | 10000    |
        +----------------------------------------+-------------------------------+-------------+----------+
        | 250m_16_days_composite_day_of_the_year | Day of year VI pixel          | day_of_year | 1 to     |
        |                                        |                               |             | 366      |
        +----------------------------------------+-------------------------------+-------------+----------+
        | 250m_16_days_EVI                       | 16 day EVI average            |             | -2000 to |
        |                                        |                               |             | 10000    |
        +----------------------------------------+-------------------------------+-------------+----------+
        | 250m_16_days_MIR_reflectance           | Surface Reflectance Band 7    | reflectance | 0 to     |
        |                                        |                               |             | 10000    |
        +----------------------------------------+-------------------------------+-------------+----------+
        | 250m_16_days_NDVI                      | 16 day NDVI average           |             | -2000 to |
        |                                        |                               |             | 10000    |
        +----------------------------------------+-------------------------------+-------------+----------+
        | 250m_16_days_NIR_reflectance           | Surface Reflectance Band 2    | reflectance | 0 to     |
        |                                        |                               |             | 10000    |
        +----------------------------------------+-------------------------------+-------------+----------+
        | 250m_16_days_pixel_reliability         | Quality reliability of VI     | rank        | 0 to     |
        |                                        | pixel                         |             | 3        |
        +----------------------------------------+-------------------------------+-------------+----------+
        | 250m_16_days_red_reflectance           | Surface Reflectance Band 1    | reflectance | 0 to     |
        |                                        |                               |             | 10000    |
        +----------------------------------------+-------------------------------+-------------+----------+
        | 250m_16_days_relative_azimuth_angle    | Relative azimuth angle of VI  | degrees     | -3600 to |
        |                                        | pixel                         |             | 3600     |
        +----------------------------------------+-------------------------------+-------------+----------+
        | 250m_16_days_sun_zenith_angle          | Sun zenith angle of VI pixel  | degrees     | -9000 to |
        |                                        |                               |             | 9000     |
        +----------------------------------------+-------------------------------+-------------+----------+
        | 250m_16_days_view_zenith_angle         | View zenith angle of VI Pixel | degrees     | -9000 to |
        |                                        |                               |             | 9000     |
        +----------------------------------------+-------------------------------+-------------+----------+
        | 250m_16_days_VI_Quality                | VI quality indicators         | bit_field   | 0 to     |
        |                                        |                               |             | 65534    |
        +----------------------------------------+-------------------------------+-------------+----------+

        MOD14A2

        +----------+---------------+------------+---------+
        | band     | Description   | Units      | Range   |
        +==========+===============+============+=========+
        | FireMask | fire mask     | class-flag | 1 to    |
        |          |               |            | 9       |
        +----------+---------------+------------+---------+
        | QA       | pixel quality | bit_field  | 0 to    |
        |          |               |            | 6       |
        +----------+---------------+------------+---------+

        MOD15A2H

        +-----------------+--------------------------------+------------+---------+
        | band            | Description                    | Units      | Range   |
        +=================+================================+============+=========+
        | FparExtra_QC    | Extra detail Quality for LAI   | class-flag | 0 to    |
        |                 | and FPAR                       |            | 254     |
        +-----------------+--------------------------------+------------+---------+
        | FparLai_QC      | Quality for LAI and FPAR       | class-flag | 0 to    |
        |                 |                                |            | 254     |
        +-----------------+--------------------------------+------------+---------+
        | FparStdDev_500m | Standard deviation for FPAR    | percent    | 0 to    |
        |                 |                                |            | 100     |
        +-----------------+--------------------------------+------------+---------+
        | Fpar_500m       | Fraction of photosynthetically | percent    | 0 to    |
        |                 | active radiation               |            | 100     |
        +-----------------+--------------------------------+------------+---------+
        | LaiStdDev_500m  | Standard deviation for LAI     | m^2/m^2    | 0 to    |
        |                 |                                |            | 100     |
        +-----------------+--------------------------------+------------+---------+
        | Lai_500m        | Leaf area index                | m^2/m^2    | 0 to    |
        |                 |                                |            | 100     |
        +-----------------+--------------------------------+------------+---------+

        MOD16A2

        +------------+------------------------------+-------------+-----------+
        | band       | Description                  | Units       | Range     |
        +============+==============================+=============+===========+
        | ET_500m    | Evapotranspiration           | kg/m^2/8day | -32767 to |
        |            |                              |             | 32700     |
        +------------+------------------------------+-------------+-----------+
        | ET_QC_500m | QC for ET/LE                 |             | 0 to      |
        |            |                              |             | 254       |
        +------------+------------------------------+-------------+-----------+
        | LE_500m    | Latent heat flux (LE)        | J/m^2/day   | -32767 to |
        |            |                              |             | 32700     |
        +------------+------------------------------+-------------+-----------+
        | PET_500m   | Potential evapotranspiration | kg/m^2/8day | -32767 to |
        |            |                              |             | 32700     |
        +------------+------------------------------+-------------+-----------+
        | PLE_500m   | Potential latent heat flux   | J/m^2/day   | -32767 to |
        |            | (LE)                         |             | 32700     |
        +------------+------------------------------+-------------+-----------+

        MOD17A2H

        +-------------+--------------------------+--------------+-----------+
        | band        | Description              | Units        | Range     |
        +=============+==========================+==============+===========+
        | Gpp_500m    | Gross Primary Production | kgC/m^2/8day | 0 to      |
        |             |                          |              | 30000     |
        +-------------+--------------------------+--------------+-----------+
        | PsnNet_500m | Net Photosynthesis       | kgC/m^2/8day | -30000 to |
        |             |                          |              | 30000     |
        +-------------+--------------------------+--------------+-----------+
        | Psn_QC_500m | Quality Control bits     |              | 0 to      |
        |             |                          |              | 254       |
        +-------------+--------------------------+--------------+-----------+

        MOD17A3HGF

        +-------------+--------------------------+------------+-----------+
        | band        | Description              | Units      | Range     |
        +=============+==========================+============+===========+
        | Npp_500m    | Net Primary Productivity | kg_C/m^2   | -30000 to |
        |             |                          |            | 32700     |
        +-------------+--------------------------+------------+-----------+
        | Npp_QC_500m | Quality Control Bits     | percentage | 0 to      |
        |             |                          |            | 100       |
        +-------------+--------------------------+------------+-----------+

        MOD21A2

        +------------------+--------------------------------+---------+---------+
        | band             | Description                    | Range   | Units   |
        +==================+================================+=========+=========+
        | Emis_29          | Band 29 emissivity             | 1 to    |         |
        |                  |                                | 255     |         |
        +------------------+--------------------------------+---------+---------+
        | Emis_31          | Band 31 emissivity             | 1 to    |         |
        |                  |                                | 255     |         |
        +------------------+--------------------------------+---------+---------+
        | Emis_32          | Band 32 emissivity             | 1 to    |         |
        |                  |                                | 255     |         |
        +------------------+--------------------------------+---------+---------+
        | LST_Day_1KM      | 8-day daytime 1km grid Land-   | 7500 to | degK    |
        |                  | surface Temperature            | 65535   |         |
        +------------------+--------------------------------+---------+---------+
        | LST_Night_1KM    | 8-day nighttime 1km grid Land- | 7500 to | degK    |
        |                  | surface Temperature            | 65535   |         |
        +------------------+--------------------------------+---------+---------+
        | QC_Day           | Quality control for daytime    | 0 to    |         |
        |                  | LST and emissivity             | 255     |         |
        +------------------+--------------------------------+---------+---------+
        | QC_Night         | Quality control for nighttime  | 0 to    |         |
        |                  | LST and emissivity             | 255     |         |
        +------------------+--------------------------------+---------+---------+
        | View_Angle_Day   | Average view zenith angle of   | 0 to    | degree  |
        |                  | daytime temperature            | 130     |         |
        +------------------+--------------------------------+---------+---------+
        | View_Angle_Night | Average view zenith angle of   | 0 to    | degree  |
        |                  | nighttime temperature          | 130     |         |
        +------------------+--------------------------------+---------+---------+
        | View_Time_Day    | Average time of daytime        | 0 to    | hrs     |
        |                  | observation                    | 240     |         |
        +------------------+--------------------------------+---------+---------+
        | View_Time_Night  | Average time of nighttime      | 0 to    | hrs     |
        |                  | observation                    | 240     |         |
        +------------------+--------------------------------+---------+---------+

        MOD44B

        +----------------------------+----------------------------+-----------+---------+
        | band                       | Description                | Units     | Range   |
        +============================+============================+===========+=========+
        | Cloud                      | Cloud cover indicators     | bit_field | 0 to    |
        |                            |                            |           | 255     |
        +----------------------------+----------------------------+-----------+---------+
        | Percent_NonTree_Vegetation | Percent nontree vegetation | percent   | 0 to    |
        |                            |                            |           | 100     |
        +----------------------------+----------------------------+-----------+---------+
        | Percent_NonVegetated       | Percent non-vegetated      | percent   | 0 to    |
        |                            |                            |           | 100     |
        +----------------------------+----------------------------+-----------+---------+
        | Percent_NonVegetated_SD    | percent non-vegetated SD   | percent   | 0 to    |
        |                            |                            |           | 10000   |
        +----------------------------+----------------------------+-----------+---------+
        | Percent_Tree_Cover         | Percent tree cover         | percent   | 0 to    |
        |                            |                            |           | 100     |
        +----------------------------+----------------------------+-----------+---------+
        | Percent_Tree_Cover_SD      | percent tree cover SD      | percent   | 0 to    |
        |                            |                            |           | 10000   |
        +----------------------------+----------------------------+-----------+---------+
        | Quality                    | Quality Control indicators | bit_field | 0 to    |
        |                            |                            |           | 255     |
        +----------------------------+----------------------------+-----------+---------+

        MYD09A1

        +----------------------+--------------------------------+-------------+------------+
        | band                 | Description                    | Units       | Range      |
        +======================+================================+=============+============+
        | sur_refl_b01         | Surface reflectance for band 1 | reflectance | -100 to    |
        |                      |                                |             | 16000      |
        +----------------------+--------------------------------+-------------+------------+
        | sur_refl_b02         | Surface reflectance for band 2 | reflectance | -100 to    |
        |                      |                                |             | 16000      |
        +----------------------+--------------------------------+-------------+------------+
        | sur_refl_b03         | Surface reflectance for band 3 | reflectance | -100 to    |
        |                      |                                |             | 16000      |
        +----------------------+--------------------------------+-------------+------------+
        | sur_refl_b04         | Surface reflectance for band 4 | reflectance | -100 to    |
        |                      |                                |             | 16000      |
        +----------------------+--------------------------------+-------------+------------+
        | sur_refl_b05         | Surface reflectance for band 5 | reflectance | -100 to    |
        |                      |                                |             | 16000      |
        +----------------------+--------------------------------+-------------+------------+
        | sur_refl_b06         | Surface reflectance for band 6 | reflectance | -100 to    |
        |                      |                                |             | 16000      |
        +----------------------+--------------------------------+-------------+------------+
        | sur_refl_b07         | Surface reflectance for band 7 | reflectance | -100 to    |
        |                      |                                |             | 16000      |
        +----------------------+--------------------------------+-------------+------------+
        | sur_refl_day_of_year | Surface reflectance day of     | day_of_year | 0 to       |
        |                      | year                           |             | 366        |
        +----------------------+--------------------------------+-------------+------------+
        | sur_refl_qc_500m     | Surface reflectance 500m       | bit_field   | 0 to       |
        |                      | quality control flags          |             | 4294966531 |
        +----------------------+--------------------------------+-------------+------------+
        | sur_refl_raz         | Relative azimuth               | degree      | -18000 to  |
        |                      |                                |             | 18000      |
        +----------------------+--------------------------------+-------------+------------+
        | sur_refl_state_500m  | Surface reflectance 500m state | bit_field   | 0 to       |
        |                      | flags                          |             | 57343      |
        +----------------------+--------------------------------+-------------+------------+
        | sur_refl_szen        | Solar zenith                   | degree      | 0 to       |
        |                      |                                |             | 18000      |
        +----------------------+--------------------------------+-------------+------------+
        | sur_refl_vzen        | View zenith                    | degree      | 0 to       |
        |                      |                                |             | 18000      |
        +----------------------+--------------------------------+-------------+------------+

        MYD11A2

        +------------------+--------------------------------+---------+---------+
        | band             | Description                    | Range   | Units   |
        +==================+================================+=========+=========+
        | Clear_sky_days   | Day clear-sky coverage         | 1 to    |         |
        |                  |                                | 255     |         |
        +------------------+--------------------------------+---------+---------+
        | Clear_sky_nights | Night clear-sky coverage       | 1 to    |         |
        |                  |                                | 255     |         |
        +------------------+--------------------------------+---------+---------+
        | Day_view_angl    | View zenith angle of day       | 0 to    | degree  |
        |                  | observation                    | 130     |         |
        +------------------+--------------------------------+---------+---------+
        | Day_view_time    | Local time of day observation  | 0 to    | hrs     |
        |                  |                                | 240     |         |
        +------------------+--------------------------------+---------+---------+
        | Emis_31          | Band 31 emissivity             | 1 to    |         |
        |                  |                                | 255     |         |
        +------------------+--------------------------------+---------+---------+
        | Emis_32          | Band 32 emissivity             | 1 to    |         |
        |                  |                                | 255     |         |
        +------------------+--------------------------------+---------+---------+
        | LST_Day_1km      | Daytime Land Surface           | 7500 to | degK    |
        |                  | Temperature                    | 65535   |         |
        +------------------+--------------------------------+---------+---------+
        | LST_Night_1km    | Night Land Surface Temperature | 7500 to | degK    |
        |                  |                                | 65535   |         |
        +------------------+--------------------------------+---------+---------+
        | Night_view_angl  | View zenith angle of night     | 0 to    | degree  |
        |                  | observation                    | 130     |         |
        +------------------+--------------------------------+---------+---------+
        | Night_view_time  | Local time of night            | 0 to    | hrs     |
        |                  | observation                    | 240     |         |
        +------------------+--------------------------------+---------+---------+
        | QC_Day           | Daytime LST Quality Indicators | 0 to    |         |
        |                  |                                | 255     |         |
        +------------------+--------------------------------+---------+---------+
        | QC_Night         | Nighttime LST Quality          | 0 to    |         |
        |                  | indicators                     | 255     |         |
        +------------------+--------------------------------+---------+---------+

        MYD13Q1

        +----------------------------------------+-------------------------------+-------------+----------+
        | band                                   | Description                   | Units       | Range    |
        +========================================+===============================+=============+==========+
        | 250m_16_days_blue_reflectance          | Surface Reflectance Band 3    | reflectance | 0 to     |
        |                                        |                               |             | 10000    |
        +----------------------------------------+-------------------------------+-------------+----------+
        | 250m_16_days_composite_day_of_the_year | Day of year VI pixel          | day_of_year | 1 to     |
        |                                        |                               |             | 366      |
        +----------------------------------------+-------------------------------+-------------+----------+
        | 250m_16_days_EVI                       | 16 day EVI average            |             | -2000 to |
        |                                        |                               |             | 10000    |
        +----------------------------------------+-------------------------------+-------------+----------+
        | 250m_16_days_MIR_reflectance           | Surface Reflectance Band 7    | reflectance | 0 to     |
        |                                        |                               |             | 10000    |
        +----------------------------------------+-------------------------------+-------------+----------+
        | 250m_16_days_NDVI                      | 16 day NDVI average           |             | -2000 to |
        |                                        |                               |             | 10000    |
        +----------------------------------------+-------------------------------+-------------+----------+
        | 250m_16_days_NIR_reflectance           | Surface Reflectance Band 2    | reflectance | 0 to     |
        |                                        |                               |             | 10000    |
        +----------------------------------------+-------------------------------+-------------+----------+
        | 250m_16_days_pixel_reliability         | Quality reliability of VI     | rank        | 0 to     |
        |                                        | pixel                         |             | 3        |
        +----------------------------------------+-------------------------------+-------------+----------+
        | 250m_16_days_red_reflectance           | Surface Reflectance Band 1    | reflectance | 0 to     |
        |                                        |                               |             | 10000    |
        +----------------------------------------+-------------------------------+-------------+----------+
        | 250m_16_days_relative_azimuth_angle    | Relative azimuth angle of VI  | degrees     | -3600 to |
        |                                        | pixel                         |             | 3600     |
        +----------------------------------------+-------------------------------+-------------+----------+
        | 250m_16_days_sun_zenith_angle          | Sun zenith angle of VI pixel  | degrees     | -9000 to |
        |                                        |                               |             | 9000     |
        +----------------------------------------+-------------------------------+-------------+----------+
        | 250m_16_days_view_zenith_angle         | View zenith angle of VI Pixel | degrees     | -9000 to |
        |                                        |                               |             | 9000     |
        +----------------------------------------+-------------------------------+-------------+----------+
        | 250m_16_days_VI_Quality                | VI quality indicators         | bit_field   | 0 to     |
        |                                        |                               |             | 65534    |
        +----------------------------------------+-------------------------------+-------------+----------+

        MYD14A2

        +----------+---------------+------------+---------+
        | band     | Description   | Units      | Range   |
        +==========+===============+============+=========+
        | FireMask | fire mask     | class-flag | 1 to    |
        |          |               |            | 9       |
        +----------+---------------+------------+---------+
        | QA       | pixel quality | bit_field  | 0 to    |
        |          |               |            | 6       |
        +----------+---------------+------------+---------+

        MYD15A2H

        +-----------------+--------------------------------+------------+---------+
        | band            | Description                    | Units      | Range   |
        +=================+================================+============+=========+
        | FparExtra_QC    | Extra detail Quality for LAI   | class-flag | 0 to    |
        |                 | and FPAR                       |            | 254     |
        +-----------------+--------------------------------+------------+---------+
        | FparLai_QC      | Quality for LAI and FPAR       | class-flag | 0 to    |
        |                 |                                |            | 254     |
        +-----------------+--------------------------------+------------+---------+
        | FparStdDev_500m | Standard deviation for FPAR    | percent    | 0 to    |
        |                 |                                |            | 100     |
        +-----------------+--------------------------------+------------+---------+
        | Fpar_500m       | Fraction of photosynthetically | percent    | 0 to    |
        |                 | active radiation               |            | 100     |
        +-----------------+--------------------------------+------------+---------+
        | LaiStdDev_500m  | Standard deviation for LAI     | m^2/m^2    | 0 to    |
        |                 |                                |            | 100     |
        +-----------------+--------------------------------+------------+---------+
        | Lai_500m        | Leaf area index                | m^2/m^2    | 0 to    |
        |                 |                                |            | 100     |
        +-----------------+--------------------------------+------------+---------+

        MYD16A2

        +------------+------------------------------+-------------+-----------+
        | band       | Description                  | Units       | Range     |
        +============+==============================+=============+===========+
        | ET_500m    | Evapotranspiration           | kg/m^2/8day | -32767 to |
        |            |                              |             | 32700     |
        +------------+------------------------------+-------------+-----------+
        | ET_QC_500m | QC for ET/LE                 |             | 0 to      |
        |            |                              |             | 254       |
        +------------+------------------------------+-------------+-----------+
        | LE_500m    | Latent heat flux (LE)        | J/m^2/day   | -32767 to |
        |            |                              |             | 32700     |
        +------------+------------------------------+-------------+-----------+
        | PET_500m   | Potential evapotranspiration | kg/m^2/8day | -32767 to |
        |            |                              |             | 32700     |
        +------------+------------------------------+-------------+-----------+
        | PLE_500m   | Potential latent heat flux   | J/m^2/day   | -32767 to |
        |            | (LE)                         |             | 32700     |
        +------------+------------------------------+-------------+-----------+

        MYD17A2H

        +-------------+--------------------------+--------------+-----------+
        | band        | Description              | Units        | Range     |
        +=============+==========================+==============+===========+
        | Gpp_500m    | Gross Primary Production | kgC/m^2/8day | 0 to      |
        |             |                          |              | 30000     |
        +-------------+--------------------------+--------------+-----------+
        | PsnNet_500m | Net Photosynthesis       | kgC/m^2/8day | -30000 to |
        |             |                          |              | 30000     |
        +-------------+--------------------------+--------------+-----------+
        | Psn_QC_500m | Quality Control bits     |              | 0 to      |
        |             |                          |              | 254       |
        +-------------+--------------------------+--------------+-----------+

        MYD17A3HGF

        +-------------+--------------------------+------------+-----------+
        | band        | Description              | Units      | Range     |
        +=============+==========================+============+===========+
        | Npp_500m    | Net Primary Productivity | kg_C/m^2   | -30000 to |
        |             |                          |            | 32700     |
        +-------------+--------------------------+------------+-----------+
        | Npp_QC_500m | Quality Control Bits     | percentage | 0 to      |
        |             |                          |            | 100       |
        +-------------+--------------------------+------------+-----------+

        MYD21A2

        +------------------+--------------------------------+---------+---------+
        | band             | Description                    | Range   | Units   |
        +==================+================================+=========+=========+
        | Emis_29          | Band 29 emissivity             | 1 to    |         |
        |                  |                                | 255     |         |
        +------------------+--------------------------------+---------+---------+
        | Emis_31          | Band 31 emissivity             | 1 to    |         |
        |                  |                                | 255     |         |
        +------------------+--------------------------------+---------+---------+
        | Emis_32          | Band 32 emissivity             | 1 to    |         |
        |                  |                                | 255     |         |
        +------------------+--------------------------------+---------+---------+
        | LST_Day_1KM      | 8-day daytime 1km grid Land-   | 7500 to | degK    |
        |                  | surface Temperature            | 65535   |         |
        +------------------+--------------------------------+---------+---------+
        | LST_Night_1KM    | 8-day nighttime 1km grid Land- | 7500 to | degK    |
        |                  | surface Temperature            | 65535   |         |
        +------------------+--------------------------------+---------+---------+
        | QC_Day           | Quality control for daytime    | 0 to    |         |
        |                  | LST and emissivity             | 255     |         |
        +------------------+--------------------------------+---------+---------+
        | QC_Night         | Quality control for nighttime  | 0 to    |         |
        |                  | LST and emissivity             | 255     |         |
        +------------------+--------------------------------+---------+---------+
        | View_Angle_Day   | Average view zenith angle of   | 0 to    | degree  |
        |                  | daytime temperature            | 130     |         |
        +------------------+--------------------------------+---------+---------+
        | View_Angle_Night | Average view zenith angle of   | 0 to    | degree  |
        |                  | nighttime temperature          | 130     |         |
        +------------------+--------------------------------+---------+---------+
        | View_Time_Day    | Average time of daytime        | 0 to    | hrs     |
        |                  | observation                    | 240     |         |
        +------------------+--------------------------------+---------+---------+
        | View_Time_Night  | Average time of nighttime      | 0 to    | hrs     |
        |                  | observation                    | 240     |         |
        +------------------+--------------------------------+---------+---------+

        SIF005

        +-----------------------+--------------------------------+-------------+
        | band                  | Description                    | Units       |
        +=======================+================================+=============+
        | EVI_Quality           | MODIS enhanced vegetation      | bit_field   |
        |                       | index quality flag             |             |
        +-----------------------+--------------------------------+-------------+
        | SIF_740_daily_corr    | daily corrected SIF at 740nm   | mW/m2/nm/sr |
        +-----------------------+--------------------------------+-------------+
        | SIF_740_daily_corr_SD | uncertainty of daily corrected | mW/m2/nm/sr |
        |                       | SIF at 740nm                   |             |
        +-----------------------+--------------------------------+-------------+

        SIF_ANN

        +---------+--------------------------------+-------------+
        | band    | Description                    | Units       |
        +=========+================================+=============+
        | sif_ann | mean solar-induced chlorophyll | mW/m2/nm/sr |
        |         | fluorescence modeled by an ANN |             |
        +---------+--------------------------------+-------------+

        VNP09A1

        +-------------------------+------------------------------+-------------+------------+
        | band                    | Description                  | Units       | Range      |
        +=========================+==============================+=============+============+
        | RelativeAzimuth         | Relative azimuth             | degree      | -18000 to  |
        |                         |                              |             | 18000      |
        +-------------------------+------------------------------+-------------+------------+
        | SensorZenith            | View zenith                  | degree      | 0 to       |
        |                         |                              |             | 18000      |
        +-------------------------+------------------------------+-------------+------------+
        | SolarZenith             | Solar zenith                 | degree      | 0 to       |
        |                         |                              |             | 18000      |
        +-------------------------+------------------------------+-------------+------------+
        | SurfReflect_Day_Of_Year | Surface reflectance day of   | day_of_year | 1 to       |
        |                         | year                         |             | 366        |
        +-------------------------+------------------------------+-------------+------------+
        | SurfReflect_M1          | Surface reflectance for band | reflectance | -100 to    |
        |                         | M1                           |             | 16000      |
        +-------------------------+------------------------------+-------------+------------+
        | SurfReflect_M10         | Surface reflectance for band | reflectance | -100 to    |
        |                         | M10                          |             | 16000      |
        +-------------------------+------------------------------+-------------+------------+
        | SurfReflect_M11         | Surface reflectance for band | reflectance | -100 to    |
        |                         | M11                          |             | 16000      |
        +-------------------------+------------------------------+-------------+------------+
        | SurfReflect_M2          | Surface reflectance for band | reflectance | -100 to    |
        |                         | M2                           |             | 16000      |
        +-------------------------+------------------------------+-------------+------------+
        | SurfReflect_M3          | Surface reflectance for band | reflectance | -100 to    |
        |                         | M3                           |             | 16000      |
        +-------------------------+------------------------------+-------------+------------+
        | SurfReflect_M4          | Surface reflectance for band | reflectance | -100 to    |
        |                         | M4                           |             | 16000      |
        +-------------------------+------------------------------+-------------+------------+
        | SurfReflect_M5          | Surface reflectance for band | reflectance | -100 to    |
        |                         | M5                           |             | 16000      |
        +-------------------------+------------------------------+-------------+------------+
        | SurfReflect_M7          | Surface reflectance for band | reflectance | -100 to    |
        |                         | M7                           |             | 16000      |
        +-------------------------+------------------------------+-------------+------------+
        | SurfReflect_M8          | Surface reflectance for band | reflectance | -100 to    |
        |                         | M8                           |             | 16000      |
        +-------------------------+------------------------------+-------------+------------+
        | SurfReflect_QC          | Surface reflectance quality  | bit_field   | 0 to       |
        |                         | control flags                |             | 2147483647 |
        +-------------------------+------------------------------+-------------+------------+
        | SurfReflect_State       | Surface reflectance state    | bit_field   | 0 to       |
        |                         | flags                        |             | 13311      |
        +-------------------------+------------------------------+-------------+------------+

        VNP09H1

        +------------------------+--------------------------------+-------------+---------+
        | band                   | Description                    | Units       | Range   |
        +========================+================================+=============+=========+
        | SurfReflect_I1         | Surface reflectance for band   | reflectance | -100 to |
        |                        | I1                             |             | 16000   |
        +------------------------+--------------------------------+-------------+---------+
        | SurfReflect_I2         | Surface reflectance for band   | reflectance | -100 to |
        |                        | I2                             |             | 16000   |
        +------------------------+--------------------------------+-------------+---------+
        | SurfReflect_I3         | Surface reflectance for band   | reflectance | -100 to |
        |                        | I3                             |             | 16000   |
        +------------------------+--------------------------------+-------------+---------+
        | SurfReflect_QC_500m    | Surface reflectance 250m       | bit_field   | 0 to    |
        |                        | quality control flags          |             | 32767   |
        +------------------------+--------------------------------+-------------+---------+
        | SurfReflect_State_500m | Surface reflectance 250m state | bit_field   | 0 to    |
        |                        | flags                          |             | 13311   |
        +------------------------+--------------------------------+-------------+---------+

        VNP13A1

        +-----------------------------------------+-------------------------------+-------------+-----------+
        | band                                    | Description                   | Units       | Range     |
        +=========================================+===============================+=============+===========+
        | 500_m_16_days_blue_reflectance          | Blue band (M3 478-498 nm)     | reflectance | 0 to      |
        |                                         | reflectance                   |             | 10000     |
        +-----------------------------------------+-------------------------------+-------------+-----------+
        | 500_m_16_days_composite_day_of_the_year | Day of the year               | day_of_year | 1 to      |
        |                                         |                               |             | 366       |
        +-----------------------------------------+-------------------------------+-------------+-----------+
        | 500_m_16_days_EVI                       | 16 day EVI average            |             | -10000 to |
        |                                         |                               |             | 10000     |
        +-----------------------------------------+-------------------------------+-------------+-----------+
        | 500_m_16_days_EVI2                      | 16 day EVI2 average           |             | -10000 to |
        |                                         |                               |             | 10000     |
        +-----------------------------------------+-------------------------------+-------------+-----------+
        | 500_m_16_days_green_reflectance         | Green band (M4 545-565 nm)    | reflectance | 0 to      |
        |                                         | reflectance                   |             | 10000     |
        +-----------------------------------------+-------------------------------+-------------+-----------+
        | 500_m_16_days_NDVI                      | 16 day NDVI average           |             | -10000 to |
        |                                         |                               |             | 10000     |
        +-----------------------------------------+-------------------------------+-------------+-----------+
        | 500_m_16_days_NIR_reflectance           | NIR band (I2 846-885 nm)      | reflectance | 0 to      |
        |                                         | reflectance                   |             | 10000     |
        +-----------------------------------------+-------------------------------+-------------+-----------+
        | 500_m_16_days_pixel_reliability         | Quality reliability           | rank        | 0 to      |
        |                                         |                               |             | 11        |
        +-----------------------------------------+-------------------------------+-------------+-----------+
        | 500_m_16_days_red_reflectance           | Red band (I1 600-680 nm)      | reflectance | 0 to      |
        |                                         | reflectance                   |             | 10000     |
        +-----------------------------------------+-------------------------------+-------------+-----------+
        | 500_m_16_days_relative_azimuth_angle    | Relative azimuth angle        | degrees     | -18000 to |
        |                                         |                               |             | 18000     |
        +-----------------------------------------+-------------------------------+-------------+-----------+
        | 500_m_16_days_sun_zenith_angle          | Sun zenith angle              | degrees     | 0 to      |
        |                                         |                               |             | 18000     |
        +-----------------------------------------+-------------------------------+-------------+-----------+
        | 500_m_16_days_SWIR1_reflectance         | SWIR1 band (M8 1230-1250 nm)  | reflectance | 0 to      |
        |                                         | reflectance                   |             | 10000     |
        +-----------------------------------------+-------------------------------+-------------+-----------+
        | 500_m_16_days_SWIR2_reflectance         | SWIR2 band (M10 1580-1640 nm) | reflectance | 0 to      |
        |                                         | reflectance                   |             | 10000     |
        +-----------------------------------------+-------------------------------+-------------+-----------+
        | 500_m_16_days_SWIR3_reflectance         | SWIR3 band (M11 2225-2275 nm) | reflectance | 0 to      |
        |                                         | reflectance                   |             | 10000     |
        +-----------------------------------------+-------------------------------+-------------+-----------+
        | 500_m_16_days_view_zenith_angle         | View zenith angle             | degrees     | 0 to      |
        |                                         |                               |             | 18000     |
        +-----------------------------------------+-------------------------------+-------------+-----------+
        | 500_m_16_days_VI_Quality                | VI quality indicators         | bit_field   | 0 to      |
        |                                         |                               |             | 65534     |
        +-----------------------------------------+-------------------------------+-------------+-----------+

        VNP15A2H

        +--------------+--------------------------------+------------+---------+
        | band         | Description                    | Units      | Range   |
        +==============+================================+============+=========+
        | Fpar         | Fraction of photosynthetically | fraction   | 0 to    |
        |              | active radiation               |            | 100     |
        +--------------+--------------------------------+------------+---------+
        | FparExtra_QC | Extra detail Quality for LAI   | class-flag | 0 to    |
        |              | and FPAR                       |            | 254     |
        +--------------+--------------------------------+------------+---------+
        | FparLai_QC   | Quality for LAI and FPAR       | class-flag | 0 to    |
        |              |                                |            | 254     |
        +--------------+--------------------------------+------------+---------+
        | FparStdDev   | Standard deviation for FPAR    | fraction   | 0 to    |
        |              |                                |            | 100     |
        +--------------+--------------------------------+------------+---------+
        | Lai          | Leaf area index                | m^2/m^2    | 0 to    |
        |              |                                |            | 100     |
        +--------------+--------------------------------+------------+---------+
        | LaiStdDev    | Standard deviation for LAI     | m^2/m^2    | 0 to    |
        |              |                                |            | 100     |
        +--------------+--------------------------------+------------+---------+

        VNP21A2

        +------------------+-------------------------------+---------+---------+
        | band             | Description                   | Units   | Range   |
        +==================+===============================+=========+=========+
        | Emis_14          | Average Band 14 emissivity    |         | 1 to    |
        |                  |                               |         | 255     |
        +------------------+-------------------------------+---------+---------+
        | Emis_15          | Average Band 15 emissivity    |         | 1 to    |
        |                  |                               |         | 255     |
        +------------------+-------------------------------+---------+---------+
        | Emis_16          | Average Band 16 emissivity    |         | 1 to    |
        |                  |                               |         | 255     |
        +------------------+-------------------------------+---------+---------+
        | LST_Day_1KM      | Daytime Land-surface          | degK    | 7500 to |
        |                  | Temperature                   |         | 65535   |
        +------------------+-------------------------------+---------+---------+
        | LST_Night_1KM    | Nighttime Land-surface        | degK    | 7500 to |
        |                  | Temperature                   |         | 65535   |
        +------------------+-------------------------------+---------+---------+
        | QC_Day           | Quality control for daytime   |         | 1 to    |
        |                  | LST and emissivity            |         | 255     |
        +------------------+-------------------------------+---------+---------+
        | QC_Night         | Quality control for nighttime |         | 1 to    |
        |                  | LST and emissivity            |         | 255     |
        +------------------+-------------------------------+---------+---------+
        | View_Angle_Day   | Average view zenith angle of  | degree  | 0 to    |
        |                  | daytime temperature           |         | 130     |
        +------------------+-------------------------------+---------+---------+
        | View_Angle_Night | Average view zenith angle of  | degree  | 0 to    |
        |                  | nighttime temperature         |         | 130     |
        +------------------+-------------------------------+---------+---------+
        | View_Time_Day    | Average time of daytime       | hrs     | 0 to    |
        |                  | observation                   |         | 240     |
        +------------------+-------------------------------+---------+---------+
        | View_Time_Night  | Average time of nighttime     | hrs     | 0 to    |
        |                  | observation                   |         | 240     |
        +------------------+-------------------------------+---------+---------+

        VNP22Q2

        +----------------------------------------------+--------------------------------+----------------+---------+
        | band                                         | Description                    | Units          | Range   |
        +==============================================+================================+================+=========+
        | Cycle_1.Date_Mid_Greenup_Phase_1             | Date at a mid-greenup phase    | day_of_year    | 1 to    |
        |                                              |                                |                | 32766   |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_1.Date_Mid_Senescence_Phase_1          | Date at a mid-senescence phase | day_of_year    | 1 to    |
        |                                              |                                |                | 32766   |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_1.EVI2_Growing_Season_Area_1           | Integrated EVI2 during a       | EVI2           | 1 to    |
        |                                              | growing season                 |                | 32766   |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_1.EVI2_Onset_Greenness_Increase_1      | EVI2 value at greenup onset    | EVI2           | 1 to    |
        |                                              |                                |                | 10000   |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_1.EVI2_Onset_Greenness_Maximum_1       | EVI2 value at maturity onset   | EVI2           | 1 to    |
        |                                              |                                |                | 10000   |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_1.GLSP_QC_1                            | Global Land Surface Phenology  |                | 0 to    |
        |                                              | Quality Control                |                | 100     |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_1.Greenness_Agreement_Growing_Season_1 | EVI2 agreement between modeled |                | 0 to    |
        |                                              | values and raw observations    |                | 100     |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_1.Growing_Season_Length_1              | Growing Season Length          | number_of_days | 1 to    |
        |                                              |                                |                | 366     |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_1.Onset_Greenness_Decrease_1           | Date at which canopy greenness | day_of_year    | 1 to    |
        |                                              | begins to decrease             |                | 32766   |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_1.Onset_Greenness_Increase_1           | Date of onset of greenness     | day_of_year    | 1 to    |
        |                                              | increase                       |                | 32766   |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_1.Onset_Greenness_Maximum_1            | Date at which canopy greenness | day_of_year    | 1 to    |
        |                                              | approaches its seasonal        |                | 32766   |
        |                                              | maximum                        |                |         |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_1.Onset_Greenness_Minimum_1            | Date at which canopy greenness | day_of_year    | 1 to    |
        |                                              | reaches a minimum              |                | 32766   |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_1.PGQ_Growing_Season_1                 | Proportion of good quality     |                | 1 to    |
        |                                              | observations during a growing  |                | 100     |
        |                                              | season                         |                |         |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_1.PGQ_Onset_Greenness_Decrease_1       | Proportion of good quality     |                | 1 to    |
        |                                              | around senescence onset        |                | 100     |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_1.PGQ_Onset_Greenness_Increase_1       | Proportion of good quality     |                | 1 to    |
        |                                              | around greenup onset           |                | 100     |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_1.PGQ_Onset_Greenness_Maximum_1        | Proportion of good quality     |                | 1 to    |
        |                                              | around maturity onset          |                | 100     |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_1.PGQ_Onset_Greenness_Minimum_1        | Proportion of good quality     |                | 1 to    |
        |                                              | around dormancy onset          |                | 100     |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_1.Rate_Greenness_Decrease_1            | Rates of change in EVI2 values | EVI2/day       | 1 to    |
        |                                              | during a senesce phase         |                | 32766   |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_1.Rate_Greenness_Increase_1            | Rates of change in EVI2 values | EVI2/day       | 1 to    |
        |                                              | during a greenup phase         |                | 32766   |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_2.Date_Mid_Greenup_Phase_2             | Date at a mid-greenup phase    | day_of_year    | 1 to    |
        |                                              |                                |                | 32766   |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_2.Date_Mid_Senescence_Phase_2          | Date at a mid-senescence phase | day_of_year    | 1 to    |
        |                                              |                                |                | 32766   |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_2.EVI2_Growing_Season_Area_2           | Integrated EVI2 during a       | EVI2           | 1 to    |
        |                                              | growing season                 |                | 32766   |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_2.EVI2_Onset_Greenness_Increase_2      | EVI2 value at greenup onset    | EVI2           | 1 to    |
        |                                              |                                |                | 10000   |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_2.EVI2_Onset_Greenness_Maximum_2       | EVI2 value at maturity onset   | EVI2           | 1 to    |
        |                                              |                                |                | 10000   |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_2.GLSP_QC_2                            | Global Land Surface Phenology  |                | 0 to    |
        |                                              | Quality Control                |                | 100     |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_2.Greenness_Agreement_Growing_Season_2 | EVI2 agreement between modeled |                | 0 to    |
        |                                              | values and raw observations    |                | 100     |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_2.Growing_Season_Length_2              | Growing Season Length          | number_of_days | 1 to    |
        |                                              |                                |                | 366     |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_2.Onset_Greenness_Decrease_2           | Date at which canopy greenness | day_of_year    | 1 to    |
        |                                              | begins to decrease             |                | 32766   |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_2.Onset_Greenness_Increase_2           | Date of onset of greenness     | day_of_year    | 1 to    |
        |                                              | increase                       |                | 32766   |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_2.Onset_Greenness_Maximum_2            | Date at which canopy greenness | day_of_year    | 1 to    |
        |                                              | approaches its seasonal        |                | 32766   |
        |                                              | maximum                        |                |         |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_2.Onset_Greenness_Minimum_2            | Date at which canopy greenness | day_of_year    | 1 to    |
        |                                              | reaches a minimum              |                | 32766   |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_2.PGQ_Growing_Season_2                 | Proportion of good quality     |                | 1 to    |
        |                                              | observations during a growing  |                | 100     |
        |                                              | season                         |                |         |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_2.PGQ_Onset_Greenness_Decrease_2       | Proportion of good quality     |                | 1 to    |
        |                                              | around senescence onset        |                | 100     |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_2.PGQ_Onset_Greenness_Increase_2       | Proportion of good quality     |                | 1 to    |
        |                                              | around greenup onset           |                | 100     |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_2.PGQ_Onset_Greenness_Maximum_2        | Proportion of good quality     |                | 1 to    |
        |                                              | around maturity onset          |                | 100     |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_2.PGQ_Onset_Greenness_Minimum_2        | Proportion of good quality     |                | 1 to    |
        |                                              | around dormancy onset          |                | 100     |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_2.Rate_Greenness_Decrease_2            | Rates of change in EVI2 values | EVI2/day       | 1 to    |
        |                                              | during a senesce phase         |                | 32766   |
        +----------------------------------------------+--------------------------------+----------------+---------+
        | Cycle_2.Rate_Greenness_Increase_2            | Rates of change in EVI2 values | EVI2/day       | 1 to    |
        |                                              | during a greenup phase         |                | 32766   |
        +----------------------------------------------+--------------------------------+----------------+---------+

    ${start_date}

    ${end_date}

    Notes
    -----
    Citation instructions are from https://modis.ornl.gov/citation.html

    When using subsets of MODIS Land Products from the ORNL DAAC, please
    use the following citation format:

    Citation: Single Site

    Format (single site):

    ORNL DAAC 2008. MODIS Collection 5 Land Products Global Subsetting
    and Visualization Tool. ORNL DAAC, Oak Ridge, Tennessee, USA.
    Accessed Month dd, yyyy. Subset obtained for [Product name] product
    at [Lat],[Lon], time period: [Start date] to [End date], and subset
    size: [Width] x [Height] km. http://dx.doi.org/10.3334/ORNLDAAC/1241

    Single site:

    ORNL DAAC. 2008. MODIS Collection 5 Land Products Global Subsetting
    and Visualization Tool. ORNL DAAC, Oak Ridge, Tennessee, USA.
    Accessed August 25, 2015. Subset obtained for MOD13Q1 product at
    39.497N,107.3028W, time period: 2000-02-18 to 2015-07-28, and subset
    size: 0.25 x 0.25 km. http://dx.doi.org/10.3334/ORNLDAAC/1241

    Citation: Multiple Sites

    Format (multiple sites, clustered together):

    ORNL DAAC 2008. MODIS Collection 5 Land Products Global Subsetting
    and Visualization Tool. ORNL DAAC, Oak Ridge, Tennessee, USA.
    Accessed Month dd, yyyy. Subset obtained for [Product name] product
    at various sites in Spatial Range: N=DD.DD, S=DD.DD, E=DDD.DD,
    W=DDD.DD, time period: [Start date] to [End date], and subset size:
    [Width] x [Height] km. http://dx.doi.org/10.3334/ORNLDAAC/1241

    Multiple sites, clustered together:

    ORNL DAAC. 2008. MODIS Collection 5 Land Products Global Subsetting
    and Visualization Tool. ORNL DAAC, Oak Ridge, Tennessee, USA.
    Accessed August 25, 2015. Subset obtained for MOD13Q1 product at
    various sites in Spatial Range: N=39.49N, S=39.25N, E=107.42W,
    W=106.48W, time period: 2000-02-18 to 2015-07-28, and subset size:
    0.25 x 0.25 km. http://dx.doi.org/10.3334/ORNLDAAC/1241
    "Spatial Range: N=DD.DD, S=DD.DD, E=DDD.DD, W=DDD.DD" is the
    bounding box for the site locations used for requesting subsets.

    Please cite each product separately.

    The coordinates used in the citation are the Latitude and Longitude
    (decimal degrees) specified by the user when the order is placed,
    trimmed to 4 decimal places.  The citation is also sent in the email
    along with data retrieval instructions after the order is processed.
    BibTeX (.bib) file is available for download on the data
    visualization and download page. Please modify it manually for
    multiple sites.
    """
    tsutils.printiso(
        modis(lat, lon, product, band, start_date=start_date, end_date=end_date)
    )


@tsutils.copy_doc(modis_cli)
def modis(lat, lon, product, band, start_date=None, end_date=None):
    r"""Download MODIS derived data."""
    query_params = {
        "latitude": lat,
        "longitude": lon,
        "product": product,
        "band": band,
        "startdate": pd.to_datetime("1900-01-01T00")
        if start_date is None
        else tsutils.parsedate(start_date),
    }

    if end_date is None:
        query_params["enddate"] = datetime.datetime.now()
    else:
        query_params["enddate"] = tsutils.parsedate(end_date)

    products_url = "https://modis.ornl.gov/rst/api/v1/products?tool=GlobalSubset"
    r = ar.retrieve_text([products_url])[0]
    r = json.loads(r)
    pdf = pd.json_normalize(r, record_path=["products"])
    products = pdf["product"].to_list()

    if query_params["product"] not in products:
        raise ValueError(
            tsutils.error_wrapper(
                f"""
                Available products at the current time are: {products}.

                You gave {query_params['product']}.
                """
            )
        )

    band_url = f"https://modis.ornl.gov/rst/api/v1/{query_params['product']}/bands"
    r = ar.retrieve_text([band_url])[0]
    r = json.loads(r)
    bdf = pd.json_normalize(r, record_path=["bands"])
    bands = bdf["band"].to_list()

    if query_params["band"] not in bands:
        raise ValueError(
            tsutils.error_wrapper(
                f"""
                'band' argument must be in the following list for 'product'
                = {query_params['product']}. {bands}.

                You gave me {query_params['band']}.
                """
            )
        )

    start_date = query_params["startdate"]
    end_date = query_params["enddate"]

    dates_url = f"https://modis.ornl.gov/rst/api/v1/{query_params['product']}/dates?latitude={query_params['latitude']}&longitude={query_params['longitude']}"
    r = ar.retrieve_text([dates_url])[0]
    r = json.loads(r)
    ddf = pd.json_normalize(r, record_path=["dates"])
    modis_date = ddf["modis_date"].to_numpy()
    dates = ddf["calendar_date"].to_list()
    dates = [pd.to_datetime(i) for i in dates]

    dr = np.array(dates)

    start_date = max(start_date, dr[0])

    enddate = min(end_date, dr[-1])

    mask = (dr >= start_date) & (dr <= enddate)
    dates = modis_date[mask]
    dates = [dates[i : i + 10] for i in range(0, len(dates), 10)]
    subset_url = [
        f"https://modis.ornl.gov/rst/api/v1/{query_params['product']}/subset?band={query_params['band']}&latitude={query_params['latitude']}&longitude={query_params['longitude']}&startDate={i[0]}&endDate={i[-1]}&kmAboveBelow=0&kmLeftRight=0"
        for i in dates
    ]
    r = ar.retrieve_text(subset_url)
    sdf = [pd.json_normalize(json.loads(i), record_path=["subset"]) for i in r]
    sdf = pd.concat(sdf)

    sdf = sdf.drop(["modis_date", "tile", "proc_date"], axis="columns")

    sdf["data"] = sdf["data"].apply(lambda x: x[0])

    sdf = sdf.set_index(["calendar_date", "band"])

    sdf = sdf.unstack()

    sdf.columns = [y for x, y in sdf.columns]

    for col in sdf.columns:
        sdf[col] = sdf[col].replace(_MISSING.get(col, pd.NA))
        sdf.loc[sdf[col] < _VALID_RANGE[col][0], col] = pd.NA
        sdf.loc[sdf[col] > _VALID_RANGE[col][1], col] = pd.NA
        sdf[col] = sdf[col] * _SCALE.get(col, 1.0) + _OFFSET.get(col, 0.0)

    sdf.index.name = "Datetime"
    sdf.columns = [f"{i}:{_UNITS.get(i, '')}" for i in sdf.columns]
    return sdf


if __name__ == "__main__":
    r = modis(
        product="MOD13Q1",
        band="250m_16_days_NDVI",
        lat=40.0,
        lon=-110.0,
        start_date="2002-06-01T09",
        end_date="2003-05-04T21",
    )

    print("modis")
    print(r)

    r = modis(
        product="MOD15A2H",
        band="LaiStdDev_500m",
        lat=29.65,
        lon=-82.32,
        start_date="3 years ago",
        end_date="2 years ago",
    )

    print("modis")
    print(r)
