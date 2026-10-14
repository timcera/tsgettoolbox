r"""
tsgettoolbox command line/library tools to retrieve time series.

This program is a collection of utilities to download data from various
web services.
"""

__all__ = [
    "cdec",
    "coops",
    "daymet",
    "epa_wqp",
    "fawn",
    "hydstra_catalog",
    "hydstra_stations",
    "hydstra_ts",
    "ldas",
    "ldas_gldas_noah",
    "ldas_gldas_noah_v2_0",
    "ldas_gldas_noah_v2_1",
    "ldas_grace",
    "ldas_merra",
    "ldas_nldas3_forcing",
    "ldas_nldas_fora",
    "ldas_nldas_noah",
    "ldas_nldas_vic",
    "ldas_smerge",
    "metdata",
    "modis",
    "ncei_annual",
    "ncei_ghcnd",
    "ncei_ghcnd_ftp",
    "ncei_ghcndms",
    "ncei_gsod",
    "ncei_gsom",
    "ncei_gsoy",
    "ncei_ish",
    "ncei_nexrad2",
    "ncei_nexrad3",
    "ncei_normal_ann",
    "ncei_normal_dly",
    "ncei_normal_hly",
    "ncei_normal_mly",
    "ncei_precip_15",
    "ncei_precip_hly",
    "ndbc",
    "nwis",
    "nwis_dv",
    "nwis_gwlevels",
    "nwis_iv",
    "nwis_measurements",
    "nwis_peak",
    "nwis_site",
    "nwis_stat",
    "rivergages",
    "terraclimate",
    "terraclimate19812010",
    "terraclimate19912020",
    "twc",
    "unavco",
    "wdfn_agency_codes",
    "wdfn_altitude_datums",
    "wdfn_aquifer_codes",
    "wdfn_aquifer_types",
    "wdfn_channel_measurements",
    "wdfn_citations",
    "wdfn_combined_metadata",
    "wdfn_continuous",
    "wdfn_coordinate_accuracy_codes",
    "wdfn_coordinate_datum_codes",
    "wdfn_coordinate_method_codes",
    "wdfn_counties",
    "wdfn_countries",
    "wdfn_daily",
    "wdfn_field_measurements",
    "wdfn_field_measurements_metadata",
    "wdfn_hydrologic_unit_codes",
    "wdfn_latest_continuous",
    "wdfn_latest_daily",
    "wdfn_latest_field_measurements",
    "wdfn_medium_codes",
    "wdfn_method_categories",
    "wdfn_method_citations",
    "wdfn_methods",
    "wdfn_monitoring_locations",
    "wdfn_national_aquifer_codes",
    "wdfn_parameter_codes",
    "wdfn_peaks",
    "wdfn_read_interval_observations",
    "wdfn_read_normal_observations",
    "wdfn_reliability_codes",
    "wdfn_site_types",
    "wdfn_states",
    "wdfn_statistic_codes",
    "wdfn_time_series_metadata",
    "wdfn_time_series_methods",
    "wdfn_time_series_revisions",
    "wdfn_time_zone_codes",
    "wdfn_topographic_codes",
]

# Local folder imports

try:
    from tsgettoolbox_cdec.cdec import cdec  # noqa: I001
except ImportError:
    cdec = lambda: None
    cdec.__doc__ = "CDEC is not installed. Install tsgettoolbox_cdec."

try:
    from tsgettoolbox_coops.coops import coops  # noqa: I001
except ImportError:
    coops = lambda: None
    coops.__doc__ = "COOPS is not installed. Install tsgettoolbox_coops."

try:
    from tsgettoolbox_daymet.daymet import daymet  # noqa: I001
except ImportError:
    daymet = lambda: None
    daymet.__doc__ = "Daymet is not installed. Install tsgettoolbox_daymet."

try:
    from tsgettoolbox_fawn.fawn import fawn  # noqa: I001
except ImportError:
    fawn = lambda: None
    fawn.__doc__ = "FAWN is not installed. Install tsgettoolbox_fawn."

try:
    # Third party imports
    from tsgettoolbox_hydstra.hydstra import (
        hydstra_catalog,
        hydstra_stations,
        hydstra_ts,
    )
except ImportError:
    hydstra_catalog = lambda: None
    hydstra_catalog.__doc__ = "Hydstra is not installed. Install tsgettoolbox_hydstra."
    hydstra_stations = lambda: None
    hydstra_stations.__doc__ = "Hydstra is not installed. Install tsgettoolbox_hydstra."
    hydstra_ts = lambda: None
    hydstra_ts.__doc__ = "Hydstra is not installed. Install tsgettoolbox_hydstra."

try:
    # Third party imports
    from tsgettoolbox_ldas.ldas import (
        ldas,
        ldas_gldas_noah,
        ldas_gldas_noah_v2_0,
        ldas_gldas_noah_v2_1,
        ldas_grace,
        ldas_merra,
        ldas_nldas_fora,
        ldas_nldas_noah,
        ldas_nldas_vic,
        ldas_smerge,
    )
except ImportError:
    ldas = lambda: None
    ldas.__doc__ = "LDAS is not installed. Install tsgettoolbox_ldas."
    ldas_gldas_noah = lambda: None
    ldas_gldas_noah.__doc__ = (
        "LDAS GLDAS Noah is not installed. Install tsgettoolbox_ldas."
    )
    ldas_gldas_noah_v2_0 = lambda: None
    ldas_gldas_noah_v2_0.__doc__ = (
        "LDAS GLDAS Noah v2.0 is not installed. Install tsgettoolbox_ldas."
    )
    ldas_gldas_noah_v2_1 = lambda: None
    ldas_gldas_noah_v2_1.__doc__ = (
        "LDAS GLDAS Noah v2.1 is not installed. Install tsgettoolbox_ldas."
    )
    ldas_grace = lambda: None
    ldas_grace.__doc__ = "LDAS GRACE is not installed. Install tsgettoolbox_ldas."
    ldas_merra = lambda: None
    ldas_merra.__doc__ = "LDAS MERRA is not installed. Install tsgettoolbox_ldas."
    ldas_nldas_fora = lambda: None
    ldas_nldas_fora.__doc__ = (
        "LDAS NLDAS FORA is not installed. Install tsgettoolbox_ldas."
    )
    ldas_nldas_noah = lambda: None
    ldas_nldas_noah.__doc__ = (
        "LDAS NLDAS Noah is not installed. Install tsgettoolbox_ldas."
    )
    ldas_nldas_vic = lambda: None
    ldas_nldas_vic.__doc__ = (
        "LDAS NLDAS VIC is not installed. Install tsgettoolbox_ldas."
    )
    ldas_smerge = lambda: None
    ldas_smerge.__doc__ = "LDAS SMERGE is not installed. Install tsgettoolbox_ldas."

try:
    # Third party imports
    from tsgettoolbox_metdata.metdata import metdata
except ImportError:
    metdata = lambda: None
    metdata.__doc__ = "MetData is not installed. Install tsgettoolbox_metdata."

try:
    # Third party imports
    from tsgettoolbox_modis.modis import modis
except ImportError:
    modis = lambda: None
    modis.__doc__ = "MODIS is not installed. Install tsgettoolbox_modis."

try:
    # Third party imports
    from tsgettoolbox_ncei.ncei import (
        ncei_annual,
        ncei_ghcnd,
        ncei_ghcnd_ftp,
        ncei_ghcndms,
        ncei_gsod,
        ncei_gsom,
        ncei_gsoy,
        ncei_ish,
        ncei_nexrad2,
        ncei_nexrad3,
        ncei_normal_ann,
        ncei_normal_dly,
        ncei_normal_hly,
        ncei_normal_mly,
        ncei_precip_15,
        ncei_precip_hly,
    )
except ImportError:
    ncei_annual = lambda: None
    ncei_annual.__doc__ = "NCEI Annual is not installed. Install tsgettoolbox_ncei."
    ncei_ghcnd = lambda: None
    ncei_ghcnd.__doc__ = "NCEI GHCND is not installed. Install tsgettoolbox_ncei."
    ncei_ghcnd_ftp = lambda: None
    ncei_ghcnd_ftp.__doc__ = (
        "NCEI GHCND FTP is not installed. Install tsgettoolbox_ncei."
    )
    ncei_ghcndms = lambda: None
    ncei_ghcndms.__doc__ = "NCEI GHCNDMS is not installed. Install tsgettoolbox_ncei."
    ncei_gsod = lambda: None
    ncei_gsod.__doc__ = "NCEI GSOD is not installed. Install tsgettoolbox_ncei."
    ncei_gsom = lambda: None
    ncei_gsom.__doc__ = "NCEI GSOM is not installed. Install tsgettoolbox_ncei."
    ncei_gsoy = lambda: None
    ncei_gsoy.__doc__ = "NCEI GSOY is not installed. Install tsgettoolbox_ncei."
    ncei_ish = lambda: None
    ncei_ish.__doc__ = "NCEI ISH is not installed. Install tsgettoolbox_ncei."
    ncei_nexrad2 = lambda: None
    ncei_nexrad2.__doc__ = "NCEI NEXRAD2 is not installed. Install tsgettoolbox_ncei."
    ncei_nexrad3 = lambda: None
    ncei_nexrad3.__doc__ = "NCEI NEXRAD3 is not installed. Install tsgettoolbox_ncei."
    ncei_normal_ann = lambda: None
    ncei_normal_ann.__doc__ = (
        "NCEI Normal Annual is not installed. Install tsgettoolbox_ncei."
    )
    ncei_normal_dly = lambda: None
    ncei_normal_dly.__doc__ = (
        "NCEI Normal Daily is not installed. Install tsgettoolbox_ncei."
    )
    ncei_normal_hly = lambda: None
    ncei_normal_hly.__doc__ = (
        "NCEI Normal Hourly is not installed. Install tsgettoolbox_ncei."
    )
    ncei_normal_mly = lambda: None
    ncei_normal_mly.__doc__ = (
        "NCEI Normal Monthly is not installed. Install tsgettoolbox_ncei."
    )
    ncei_precip_15 = lambda: None
    ncei_precip_15.__doc__ = (
        "NCEI Precip 15 is not installed. Install tsgettoolbox_ncei."
    )
    ncei_precip_hly = lambda: None
    ncei_precip_hly.__doc__ = (
        "NCEI Precip Hourly is not installed. Install tsgettoolbox_ncei."
    )

try:
    # Third party imports
    from tsgettoolbox_ndbc.ndbc import ndbc
except ImportError:
    ndbc = lambda: None
    ndbc.__doc__ = "NDBC is not installed. Install tsgettoolbox_ndbc"

try:
    # Third party imports
    from tsgettoolbox_nwis.nwis import (
        epa_wqp,
        nwis,
        nwis_dv,
        nwis_gwlevels,
        nwis_iv,
        nwis_measurements,
        nwis_peak,
        nwis_site,
        nwis_stat,
    )
except ImportError:
    epa_wqp = lambda: None
    epa_wqp.__doc__ = "EPA WQP is not installed. Install tsgettoolbox_nwis."
    nwis = lambda: None
    nwis.__doc__ = "NWIS is not installed. Install tsgettoolbox_nwis."
    nwis_dv = lambda: None
    nwis_dv.__doc__ = "NWIS DV is not installed. Install tsgettoolbox_nwis."
    nwis_gwlevels = lambda: None
    nwis_gwlevels.__doc__ = (
        "NWIS GW Levels is not installed. Install tsgettoolbox_nwis."
    )
    nwis_iv = lambda: None
    nwis_iv.__doc__ = "NWIS IV is not installed. Install tsgettoolbox_nwis."
    nwis_measurements = lambda: None
    nwis_measurements.__doc__ = (
        "NWIS Measurements is not installed. Install tsgettoolbox_nwis."
    )
    nwis_peak = lambda: None
    nwis_peak.__doc__ = "NWIS Peak is not installed. Install tsgettoolbox_nwis."
    nwis_site = lambda: None
    nwis_site.__doc__ = "NWIS Site is not installed. Install tsgettoolbox_nwis."
    nwis_stat = lambda: None
    nwis_stat.__doc__ = "NWIS Stat is not installed. Install tsgettoolbox_nwis."

try:
    # Third party imports
    from tsgettoolbox_nldas3.nldas3 import ldas_nldas3_forcing
except ImportError:
    ldas_nldas3_forcing = lambda: None
    ldas_nldas3_forcing.__doc__ = (
        "LDAS NLDAS3 Forcing is not installed. Install tsgettoolbox_nldas3."
    )

try:
    # Third party imports
    from tsgettoolbox_terraclimate.terraclimate import (
        terraclimate,
        terraclimate19812010,
        terraclimate19912020,
    )
except ImportError:
    terraclimate = lambda: None
    terraclimate.__doc__ = (
        "TerraClimate is not installed. Install tsgettoolbox_terraclimate."
    )
    terraclimate19812010 = lambda: None
    terraclimate19812010.__doc__ = (
        "TerraClimate 1981-2010 is not installed. Install tsgettoolbox_terraclimate."
    )
    terraclimate19912020 = lambda: None
    terraclimate19912020.__doc__ = (
        "TerraClimate 1991-2020 is not installed. Install tsgettoolbox_terraclimate."
    )

try:
    # Third party imports
    from tsgettoolbox_rivergages.rivergages import rivergages
except ImportError:
    rivergages = lambda: None
    rivergages.__doc__ = "RiverGages is not installed. Install tsgettoolbox_rivergages."

try:
    # Third party imports
    from tsgettoolbox_twc.twc import twc
except ImportError:
    twc = lambda: None
    twc.__doc__ = "TWC is not installed. Install tsgettoolbox_twc."

try:
    # Third party imports
    from tsgettoolbox_unavco.unavco import unavco
except ImportError:
    unavco = lambda: None
    unavco.__doc__ = "UNAVCO is not installed. Install tsgettoolbox_unavco."

try:
    # Third party imports
    from tsgettoolbox_wdfn.wdfn import (
        wdfn_agency_codes,
        wdfn_altitude_datums,
        wdfn_aquifer_codes,
        wdfn_aquifer_types,
        wdfn_channel_measurements,
        wdfn_citations,
        wdfn_combined_metadata,
        wdfn_continuous,
        wdfn_coordinate_accuracy_codes,
        wdfn_coordinate_datum_codes,
        wdfn_coordinate_method_codes,
        wdfn_counties,
        wdfn_countries,
        wdfn_daily,
        wdfn_field_measurements,
        wdfn_field_measurements_metadata,
        wdfn_hydrologic_unit_codes,
        wdfn_latest_continuous,
        wdfn_latest_daily,
        wdfn_latest_field_measurements,
        wdfn_medium_codes,
        wdfn_method_categories,
        wdfn_method_citations,
        wdfn_methods,
        wdfn_monitoring_locations,
        wdfn_national_aquifer_codes,
        wdfn_parameter_codes,
        wdfn_peaks,
        wdfn_read_interval_observations,
        wdfn_read_normal_observations,
        wdfn_reliability_codes,
        wdfn_site_types,
        wdfn_states,
        wdfn_statistic_codes,
        wdfn_time_series_metadata,
        wdfn_time_series_methods,
        wdfn_time_series_revisions,
        wdfn_time_zone_codes,
        wdfn_topographic_codes,
    )
except ImportError:
    wdfn_agency_codes = lambda: None
    wdfn_agency_codes.__doc__ = (
        "WDFN Agency Codes is not installed. Install tsgettoolbox_wdfn."
    )
    wdfn_altitude_datums = lambda: None
    wdfn_altitude_datums.__doc__ = (
        "WDFN Altitude Datums is not installed. Install tsgettoolbox_wdfn."
    )
    wdfn_aquifer_codes = lambda: None
    wdfn_aquifer_codes.__doc__ = (
        "WDFN Aquifer Codes is not installed. Install tsgettoolbox_wdfn."
    )
    wdfn_aquifer_types = lambda: None
    wdfn_aquifer_types.__doc__ = (
        "WDFN Aquifer Types is not installed. Install tsgettoolbox_wdfn."
    )
    wdfn_channel_measurements = lambda: None
    wdfn_channel_measurements.__doc__ = (
        "WDFN Channel Measurements is not installed. Install tsgettoolbox_wdfn."
    )
    wdfn_citations = lambda: None
    wdfn_citations.__doc__ = (
        "WDFN Citations is not installed. Install tsgettoolbox_wdfn."
    )
    wdfn_combined_metadata = lambda: None
    wdfn_combined_metadata.__doc__ = (
        "WDFN Combined Metadata is not installed. Install tsgettoolbox_wdfn."
    )
    wdfn_continuous = lambda: None
    wdfn_continuous.__doc__ = (
        "WDFN Continuous is not installed. Install tsgettoolbox_wdfn."
    )
    wdfn_coordinate_accuracy_codes = lambda: None
    wdfn_coordinate_accuracy_codes.__doc__ = (
        "WDFN Coordinate Accuracy Codes is not installed. Install tsgettoolbox_wdfn."
    )
    wdfn_coordinate_datum_codes = lambda: None
    wdfn_coordinate_datum_codes.__doc__ = (
        "WDFN Coordinate Datum Codes is not installed. Install tsgettoolbox_wdfn."
    )
    wdfn_coordinate_method_codes = lambda: None
    wdfn_coordinate_method_codes.__doc__ = (
        "WDFN Coordinate Method Codes is not installed. Install tsgettoolbox_wdfn."
    )
    wdfn_counties = lambda: None
    wdfn_counties.__doc__ = "WDFN Counties is not installed. Install tsgettoolbox_wdfn."
    wdfn_countries = lambda: None
    wdfn_countries.__doc__ = (
        "WDFN Countries is not installed. Install tsgettoolbox_wdfn."
    )
    wdfn_daily = lambda: None
    wdfn_daily.__doc__ = "WDFN Daily is not installed. Install tsgettoolbox_wdfn."
    wdfn_field_measurements = lambda: None
    wdfn_field_measurements.__doc__ = (
        "WDFN Field Measurements is not installed. Install tsgettoolbox_wdfn."
    )
    wdfn_field_measurements_metadata = lambda: None
    wdfn_field_measurements_metadata.__doc__ = (
        "WDFN Field Measurements Metadata is not installed. Install tsgettoolbox_wdfn."
    )
    wdfn_hydrologic_unit_codes = lambda: None
    wdfn_hydrologic_unit_codes.__doc__ = (
        "WDFN Hydrologic Unit Codes is not installed. Install tsgettoolbox_wdfn."
    )
    wdfn_latest_continuous = lambda: None
    wdfn_latest_continuous.__doc__ = (
        "WDFN Latest Continuous is not installed. Install tsgettoolbox_wdfn."
    )
    wdfn_latest_daily = lambda: None
    wdfn_latest_daily.__doc__ = (
        "WDFN Latest Daily is not installed. Install tsgettoolbox_wdfn."
    )
    wdfn_latest_field_measurements = lambda: None
    wdfn_latest_field_measurements.__doc__ = (
        "WDFN Latest Field Measurements is not installed. Install tsgettoolbox_wdfn."
    )
    wdfn_medium_codes = lambda: None
    wdfn_medium_codes.__doc__ = (
        "WDFN Medium Codes is not installed. Install tsgettoolbox_wdfn."
    )
    wdfn_method_categories = lambda: None
    wdfn_method_categories.__doc__ = (
        "WDFN Method Categories is not installed. Install tsgettoolbox_wdfn."
    )
    wdfn_method_citations = lambda: None
    wdfn_method_citations.__doc__ = (
        "WDFN Method Citations is not installed. Install tsgettoolbox_wdfn."
    )
    wdfn_methods = lambda: None
    wdfn_methods.__doc__ = "WDFN Methods is not installed. Install tsgettoolbox_wdfn."
    wdfn_monitoring_locations = lambda: None
    wdfn_monitoring_locations.__doc__ = (
        "WDFN Monitoring Locations is not installed. Install tsgettoolbox_wdfn."
    )
    wdfn_national_aquifer_codes = lambda: None
    wdfn_national_aquifer_codes.__doc__ = (
        "WDFN National Aquifer Codes is not installed. Install tsgettoolbox_wdfn."
    )
    wdfn_parameter_codes = lambda: None
    wdfn_parameter_codes.__doc__ = (
        "WDFN Parameter Codes is not installed. Install tsgettoolbox_wdfn."
    )
    wdfn_peaks = lambda: None
    wdfn_peaks.__doc__ = "WDFN Peaks is not installed. Install tsgettoolbox_wdfn."
    wdfn_read_interval_observations = lambda: None
    wdfn_read_interval_observations.__doc__ = (
        "WDFN Read Interval Observations is not installed. Install tsgettoolbox_wdfn."
    )
    wdfn_read_normal_observations = lambda: None
    wdfn_read_normal_observations.__doc__ = (
        "WDFN Read Normal Observations is not installed. Install tsgettoolbox_wdfn."
    )
    wdfn_reliability_codes = lambda: None
    wdfn_reliability_codes.__doc__ = (
        "WDFN Reliability Codes is not installed. Install tsgettoolbox_wdfn."
    )
    wdfn_site_types = lambda: None
    wdfn_site_types.__doc__ = (
        "WDFN Site Types is not installed. Install tsgettoolbox_wdfn."
    )
    wdfn_states = lambda: None
    wdfn_states.__doc__ = "WDFN States is not installed. Install tsgettoolbox_wdfn."
    wdfn_statistic_codes = lambda: None
    wdfn_statistic_codes.__doc__ = (
        "WDFN Statistic Codes is not installed. Install tsgettoolbox_wdfn."
    )
    wdfn_time_series_metadata = lambda: None
    wdfn_time_series_metadata.__doc__ = (
        "WDFN Time Series Metadata is not installed. Install tsgettoolbox_wdfn."
    )
    wdfn_time_series_methods = lambda: None
    wdfn_time_series_methods.__doc__ = (
        "WDFN Time Series Methods is not installed. Install tsgettoolbox_wdfn."
    )
    wdfn_time_series_revisions = lambda: None
    wdfn_time_series_revisions.__doc__ = (
        "WDFN Time Series Revisions is not installed. Install tsgettoolbox_wdfn."
    )
    wdfn_time_zone_codes = lambda: None
    wdfn_time_zone_codes.__doc__ = (
        "WDFN Time Zone Codes is not installed. Install tsgettoolbox_wdfn."
    )
    wdfn_topographic_codes = lambda: None
    wdfn_topographic_codes.__doc__ = (
        "WDFN Topographic Codes is not installed. Install tsgettoolbox_wdfn."
    )
