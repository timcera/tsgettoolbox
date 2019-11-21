from tsgettoolbox.odo import odo, resource
import pandas as pd
import mando

try:
    from mando.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter

from tstoolbox import tsutils


@mando.command("modis", formatter_class=HelpFormatter, doctype="numpy")
def modis_cli(lat, lon, product, band, startdate=None, enddate=None):
    r"""Download MODIS derived data.

    This data are derived data sets from MODIS satellite photos.

    MCD12Q1

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

        +----------+-------------------------------+--------+---------+
        | product  | Name                          | Freq.  | Size    |
        |          |                               | (Days) | (Meter) |
        +==========+===============================+========+=========+
        | MCD12Q1  | MODIS/Terra+Aqua Land Cover   | annual |  500    |
        |          | Type Yearly L3                |        |         |
        +----------+-------------------------------+--------+---------+
        | MCD12Q2  | MODIS/Terra+Aqua Land Cover   | annual |  500    |
        |          | Dynamics Yearly L3            |        |         |
        +----------+-------------------------------+--------+---------+
        | MCD15A2H | MODIS/Terra+Aqua Leaf Area    | 8      |  500    |
        |          | Index/FPAR 8-Day L4           |        |         |
        +----------+-------------------------------+--------+---------+
        | MCD15A3H | MODIS/Terra+Aqua Leaf Area    | 4      |  500    |
        |          | Index/FPAR 4-Day L4           |        |         |
        +----------+-------------------------------+--------+---------+
        | MOD09A1  | MODIS/Terra Surface           | 8      |  500    |
        |          | Reflectance 8-Day L3          |        |         |
        +----------+-------------------------------+--------+---------+
        | MOD11A2  | MODIS/Terra Land Surface      | 8      | 1000    |
        |          | Temperature/Emissivity        |        |         |
        |          | 8-Day L3                      |        |         |
        +----------+-------------------------------+--------+---------+
        | MOD13Q1  | MODIS/Terra Vegetation        | 16     |  250    |
        |          | Indices 16-Day L3             |        |         |
        +----------+-------------------------------+--------+---------+
        | MOD15A2H | MODIS/Terra Leaf Area         | 8      |  500    |
        |          | Index/FPAR 8-Day L4           |        |         |
        +----------+-------------------------------+--------+---------+
        | MOD17A2H | MODIS/Terra Gross Primary     | 8      |  500    |
        |          | Production 8-Day L4           |        |         |
        +----------+-------------------------------+--------+---------+
        | MOD17A3H | MODIS/Terra Net Primary       | annual |  500    |
        |          | Production Yearly L4          |        |         |
        +----------+-------------------------------+--------+---------+
        | MYD09A1  | MODIS/Aqua Surface            | 8      |  500    |
        |          | Reflectance 8-Day L3          |        |         |
        +----------+-------------------------------+--------+---------+
        | MYD11A2  | MODIS/Aqua Land Surface       | 8      | 1000    |
        |          | Temperature/Emissivity        |        |         |
        |          | 8-Day L3                      |        |         |
        +----------+-------------------------------+--------+---------+
        | MYD13Q1  | MODIS/Aqua Vegetation         | 16     |  250    |
        |          | Indices 16-Day L3             |        |         |
        +----------+-------------------------------+--------+---------+
        | MYD15A2H | MODIS/Aqua Leaf Area          | 8      |  500    |
        |          | Index/FPAR 8-Day L4           |        |         |
        +----------+-------------------------------+--------+---------+
        | MYD17A2H | MODIS/Aqua Gross Primary      | 8      |  500    |
        |          | Production 8-Day L4           |        |         |
        +----------+-------------------------------+--------+---------+
        | MYD17A3H | MODIS/Aqua Net Primary        | annual |  500    |
        |          | Production Yearly L4          |        |         |
        +----------+-------------------------------+--------+---------+

    band : str
        One of the following. The 'band' selected from the second column must
        match the 'product' in the first column.

        +----------+-----------------------------------------------+
        | product  | band                                          |
        +==========+===============================================+
        | MCD12Q1  | LC_Property_1 (not populated)                 |
        |          | LC_Property_2 (not populated)                 |
        |          | LC_Property_3 (not populated)                 |
        |          | Land_Cover_Type_1                             |
        |          | Land_Cover_Type_2                             |
        |          | Land_Cover_Type_3                             |
        |          | Land_Cover_Type_4                             |
        |          | Land_Cover_Type_5                             |
        |          | Land_Cover_Type_1_Assessment                  |
        |          | Land_Cover_Type_2_Assessment (not populated)  |
        |          | Land_Cover_Type_3_Assessment (not populated)  |
        |          | Land_Cover_Type_4_Assessment                  |
        |          | Land_Cover_Type_5_Assessment (not populated)  |
        |          | Land_Cover_Type_1_Secondary                   |
        |          | Land_Cover_Type_1_Secondary_Percent           |
        |          | (not populated)                               |
        +----------+-----------------------------------------------+
        | MCD12Q2  | NBAR_EVI_Onset_Greenness_Maximum.Num_Modes_02 |
        |          | NBAR_EVI_Onset_Greenness_Minimum.Num_Modes_02 |
        |          | NBAR_EVI_Onset_Greenness_Maximum.Num_Modes_01 |
        |          | NBAR_EVI_Onset_Greenness_Minimum.Num_Modes_01 |
        |          | Onset_Greenness_Minimum.Num_Modes_02          |
        |          | Onset_Greenness_Decrease.Num_Modes_02         |
        |          | Onset_Greenness_Maximum.Num_Modes_02          |
        |          | Onset_Greenness_Increase.Num_Modes_02         |
        |          | Onset_Greenness_Minimum.Num_Modes_01          |
        |          | Onset_Greenness_Decrease.Num_Modes_01         |
        |          | Onset_Greenness_Maximum.Num_Modes_01          |
        |          | Onset_Greenness_Increase.Num_Modes_01         |
        |          | NBAR_EVI_Area.Num_Modes_01                    |
        |          | NBAR_EVI_Area.Num_Modes_02                    |
        +----------+-----------------------------------------------+
        | MCD15A2H | FparExtra_QC                                  |
        |          | FparLai_QC                                    |
        |          | FparStdDev_500m                               |
        |          | LaiStdDev_500m                                |
        |          | Lai_500m                                      |
        |          | Fpar_500m                                     |
        +----------+-----------------------------------------------+
        | MCD15A3H | FparExtra_QC                                  |
        |          | FparLai_QC                                    |
        |          | FparStdDev_500m                               |
        |          | LaiStdDev_500m                                |
        |          | Lai_500m                                      |
        |          | Fpar_500m                                     |
        +----------+-----------------------------------------------+
        | MOD09A1  | sur_refl_day_of_year                          |
        |          | sur_refl_qc_500m                              |
        |          | sur_refl_raz                                  |
        |          | sur_refl_state_500m                           |
        |          | sur_refl_szen                                 |
        |          | sur_refl_vzen                                 |
        |          | sur_refl_b01                                  |
        |          | sur_refl_b02                                  |
        |          | sur_refl_b03                                  |
        |          | sur_refl_b04                                  |
        |          | sur_refl_b05                                  |
        |          | sur_refl_b06                                  |
        |          | sur_refl_b07                                  |
        +----------+-----------------------------------------------+
        | MOD11A2  | Clear_sky_days                                |
        |          | Clear_sky_nights                              |
        |          | Day_view_angl                                 |
        |          | Day_view_time                                 |
        |          | Emis_31                                       |
        |          | Emis_32                                       |
        |          | Night_view_angl                               |
        |          | Night_view_time                               |
        |          | QC_Day                                        |
        |          | QC_Night                                      |
        |          | LST_Day_1km                                   |
        |          | LST_Night_1km                                 |
        +----------+-----------------------------------------------+
        | MOD13Q1  | 250m_16_days_blue_reflectance                 |
        |          | 250m_16_days_MIR_reflectance                  |
        |          | 250m_16_days_NIR_reflectance                  |
        |          | 250m_16_days_pixel_reliability                |
        |          | 250m_16_days_red_reflectance                  |
        |          | 250m_16_days_relative_azimuth_angle           |
        |          | 250m_16_days_sun_zenith_angle                 |
        |          | 250m_16_days_view_zenith_angle                |
        |          | 250m_16_days_VI_Quality                       |
        |          | 250m_16_days_NDVI                             |
        |          | 250m_16_days_EVI                              |
        |          | 250m_16_days_composite_day_of_the_year        |
        +----------+-----------------------------------------------+
        | MOD15A2H | FparExtra_QC                                  |
        |          | FparLai_QC                                    |
        |          | FparStdDev_500m                               |
        |          | LaiStdDev_500m                                |
        |          | Lai_500m                                      |
        |          | Fpar_500m                                     |
        +----------+-----------------------------------------------+
        | MOD17A2H | Psn_QC_500m                                   |
        |          | PsnNet_500m                                   |
        |          | Gpp_500m                                      |
        +----------+-----------------------------------------------+
        | MOD17A3H | Npp_QC_500m                                   |
        |          | Npp_500m                                      |
        +----------+-----------------------------------------------+
        | MYD09A1  | sur_refl_day_of_year                          |
        |          | sur_refl_qc_500m                              |
        |          | sur_refl_raz                                  |
        |          | sur_refl_state_500m                           |
        |          | sur_refl_szen                                 |
        |          | sur_refl_vzen                                 |
        |          | sur_refl_b01                                  |
        |          | sur_refl_b02                                  |
        |          | sur_refl_b03                                  |
        |          | sur_refl_b04                                  |
        |          | sur_refl_b05                                  |
        |          | sur_refl_b06                                  |
        |          | sur_refl_b07                                  |
        +----------+-----------------------------------------------+
        | MYD11A2  | Clear_sky_days                                |
        |          | Clear_sky_nights                              |
        |          | Day_view_angl                                 |
        |          | Day_view_time                                 |
        |          | Emis_31                                       |
        |          | Emis_32                                       |
        |          | Night_view_angl                               |
        |          | Night_view_time                               |
        |          | QC_Day                                        |
        |          | QC_Night                                      |
        |          | LST_Day_1km                                   |
        |          | LST_Night_1km                                 |
        +----------+-----------------------------------------------+
        | MYD13Q1  | 250m_16_days_blue_reflectance                 |
        |          | 250m_16_days_MIR_reflectance                  |
        |          | 250m_16_days_NIR_reflectance                  |
        |          | 250m_16_days_pixel_reliability                |
        |          | 250m_16_days_red_reflectance                  |
        |          | 250m_16_days_relative_azimuth_angle           |
        |          | 250m_16_days_sun_zenith_angle                 |
        |          | 250m_16_days_view_zenith_angle                |
        |          | 250m_16_days_VI_Quality                       |
        |          | 250m_16_days_NDVI                             |
        |          | 250m_16_days_EVI                              |
        |          | 250m_16_days_composite_day_of_the_year        |
        +----------+-----------------------------------------------+
        | MYD15A2H | FparExtra_QC                                  |
        |          | FparLai_QC                                    |
        |          | FparStdDev_500m                               |
        |          | LaiStdDev_500m                                |
        |          | Lai_500m                                      |
        |          | Fpar_500m                                     |
        +----------+-----------------------------------------------+
        | MYD17A2H | Psn_QC_500m                                   |
        |          | PsnNet_500m                                   |
        |          | Gpp_500m                                      |
        +----------+-----------------------------------------------+
        | MYD17A3H | Npp_QC_500m                                   |
        |          | Npp_500m                                      |
        +----------+-----------------------------------------------+

    startdate
        ISO 8601 formatted date string

    enddate
        ISO 8601 formatted date string

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
    tsutils._printiso(
        modis(lat, lon, product, band, startdate=startdate, enddate=enddate)
    )


def modis(lat, lon, product, band, startdate=None, enddate=None):
    r"""Download MODIS derived data."""
    from tsgettoolbox.services import modis as placeholder

    r = resource(
        r"https://modis.ornl.gov/cgi-bin/MODIS/soapservice/MODIS_soapservice.wsdl",
        product=product,
        band=band,
        latitude=lat,
        longitude=lon,
        startdate=startdate,
        enddate=enddate,
    )
    return odo(r, pd.DataFrame)


modis.__doc__ = modis_cli.__doc__
