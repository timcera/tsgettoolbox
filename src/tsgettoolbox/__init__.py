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

    def cdec():
        """CDEC is not installed. Install tsgettoolbox_cdec."""


try:
    from tsgettoolbox_coops.coops import coops  # noqa: I001
except ImportError:

    def coops():
        """COOPS is not installed. Install tsgettoolbox_coops."""


try:
    from tsgettoolbox_daymet.daymet import daymet  # noqa: I001
except ImportError:

    def daymet():
        """Daymet is not installed. Install tsgettoolbox_daymet."""


try:
    from tsgettoolbox_fawn.fawn import fawn  # noqa: I001
except ImportError:

    def fawn():
        """FAWN is not installed. Install tsgettoolbox_fawn."""


try:
    # Third party imports
    from tsgettoolbox_hydstra.hydstra import (
        hydstra_catalog,
        hydstra_stations,
        hydstra_ts,
    )
except ImportError:

    def hydstra_catalog():
        """Hydstra is not installed. Install tsgettoolbox_hydstra."""

    def hydstra_stations():
        """Hydstra is not installed. Install tsgettoolbox_hydstra."""

    def hydstra_ts():
        """Hydstra is not installed. Install tsgettoolbox_hydstra."""


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

    def ldas():
        """LDAS is not installed. Install tsgettoolbox_ldas."""

    def ldas_gldas_noah():
        """LDAS GLDAS Noah is not installed. Install tsgettoolbox_ldas."""

    def ldas_gldas_noah_v2_0():
        """LDAS GLDAS Noah v2.0 is not installed. Install tsgettoolbox_ldas."""

    def ldas_gldas_noah_v2_1():
        """LDAS GLDAS Noah v2.1 is not installed. Install tsgettoolbox_ldas."""

    def ldas_grace():
        """LDAS GRACE is not installed. Install tsgettoolbox_ldas."""

    def ldas_merra():
        """LDAS MERRA is not installed. Install tsgettoolbox_ldas."""

    def ldas_nldas_fora():
        """LDAS NLDAS FORA is not installed. Install tsgettoolbox_ldas."""

    def ldas_nldas_noah():
        """LDAS NLDAS Noah is not installed. Install tsgettoolbox_ldas."""

    def ldas_nldas_vic():
        """LDAS NLDAS VIC is not installed. Install tsgettoolbox_ldas."""

    def ldas_smerge():
        """LDAS SMERGE is not installed. Install tsgettoolbox_ldas."""


try:
    # Third party imports
    from tsgettoolbox_metdata.metdata import metdata
except ImportError:

    def metdata():
        """MetData is not installed. Install tsgettoolbox_metdata."""


try:
    # Third party imports
    from tsgettoolbox_modis.modis import modis
except ImportError:

    def modis():
        """MODIS is not installed. Install tsgettoolbox_modis."""


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

    def ncei_annual():
        """NCEI Annual is not installed. Install tsgettoolbox_ncei."""

    def ncei_ghcnd():
        """NCEI GHCND is not installed. Install tsgettoolbox_ncei."""

    def ncei_ghcnd_ftp():
        """NCEI GHCND FTP is not installed. Install tsgettoolbox_ncei."""

    def ncei_ghcndms():
        """NCEI GHCNDMS is not installed. Install tsgettoolbox_ncei."""

    def ncei_gsod():
        """NCEI GSOD is not installed. Install tsgettoolbox_ncei."""

    def ncei_gsom():
        """NCEI GSOM is not installed. Install tsgettoolbox_ncei."""

    def ncei_gsoy():
        """NCEI GSOY is not installed. Install tsgettoolbox_ncei."""

    def ncei_ish():
        """NCEI ISH is not installed. Install tsgettoolbox_ncei."""

    def ncei_nexrad2():
        """NCEI NEXRAD2 is not installed. Install tsgettoolbox_ncei."""

    def ncei_nexrad3():
        """NCEI NEXRAD3 is not installed. Install tsgettoolbox_ncei."""

    def ncei_normal_ann():
        """NCEI Normal Annual is not installed. Install tsgettoolbox_ncei."""

    def ncei_normal_dly():
        """NCEI Normal Daily is not installed. Install tsgettoolbox_ncei."""

    def ncei_normal_hly():
        """NCEI Normal Hourly is not installed. Install tsgettoolbox_ncei."""

    def ncei_normal_mly():
        """NCEI Normal Monthly is not installed. Install tsgettoolbox_ncei."""

    def ncei_precip_15():
        """NCEI Precip 15 is not installed. Install tsgettoolbox_ncei."""

    def ncei_precip_hly():
        """NCEI Precip Hourly is not installed. Install tsgettoolbox_ncei."""


try:
    # Third party imports
    from tsgettoolbox_ndbc.ndbc import ndbc
except ImportError:

    def ndbc():
        """NDBC is not installed. Install tsgettoolbox_ndbc."""


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

    def epa_wqp():
        """EPA WQP is not installed. Install tsgettoolbox_nwis."""

    def nwis():
        """NWIS is not installed. Install tsgettoolbox_nwis."""

    def nwis_dv():
        """NWIS DV is not installed. Install tsgettoolbox_nwis."""

    def nwis_gwlevels():
        """NWIS GW Levels is not installed. Install tsgettoolbox_nwis."""

    def nwis_iv():
        """NWIS IV is not installed. Install tsgettoolbox_nwis."""

    def nwis_measurements():
        """NWIS Measurements is not installed. Install tsgettoolbox_nwis."""

    def nwis_peak():
        """NWIS Peak is not installed. Install tsgettoolbox_nwis."""

    def nwis_site():
        """NWIS Site is not installed. Install tsgettoolbox_nwis."""

    def nwis_stat():
        """NWIS Stat is not installed. Install tsgettoolbox_nwis."""


try:
    # Third party imports
    from tsgettoolbox_nldas3.nldas3 import ldas_nldas3_forcing
except ImportError:

    def ldas_nldas3_forcing():
        """LDAS NLDAS3 Forcing is not installed. Install tsgettoolbox_nldas3."""


try:
    # Third party imports
    from tsgettoolbox_terraclimate.terraclimate import (
        terraclimate,
        terraclimate19812010,
        terraclimate19912020,
    )
except ImportError:

    def terraclimate():
        """TerraClimate is not installed. Install tsgettoolbox_terraclimate."""

    def terraclimate19812010():
        """TerraClimate 1981-2010 is not installed. Install tsgettoolbox_terraclimate."""

    def terraclimate19912020():
        """TerraClimate 1991-2020 is not installed. Install tsgettoolbox_terraclimate."""


try:
    # Third party imports
    from tsgettoolbox_rivergages.rivergages import rivergages
except ImportError:

    def rivergages():
        """RiverGages is not installed. Install tsgettoolbox_rivergages."""


try:
    # Third party imports
    from tsgettoolbox_twc.twc import twc
except ImportError:

    def twc():
        """TWC is not installed. Install tsgettoolbox_twc."""


try:
    # Third party imports
    from tsgettoolbox_unavco.unavco import unavco
except ImportError:

    def unavco():
        """UNAVCO is not installed. Install tsgettoolbox_unavco."""


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

    def wdfn_agency_codes():
        """WDFN Agency Codes is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_altitude_datums():
        """WDFN Altitude Datums is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_aquifer_codes():
        """WDFN Aquifer Codes is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_aquifer_types():
        """WDFN Aquifer Types is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_channel_measurements():
        """WDFN Channel Measurements is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_citations():
        """WDFN Citations is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_combined_metadata():
        """WDFN Combined Metadata is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_continuous():
        """WDFN Continuous is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_coordinate_accuracy_codes():
        """WDFN Coordinate Accuracy Codes is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_coordinate_datum_codes():
        """WDFN Coordinate Datum Codes is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_coordinate_method_codes():
        """WDFN Coordinate Method Codes is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_counties():
        """WDFN Counties is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_countries():
        """WDFN Countries is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_daily():
        """WDFN Daily is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_field_measurements():
        """WDFN Field Measurements is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_field_measurements_metadata():
        """WDFN Field Measurements Metadata is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_hydrologic_unit_codes():
        """WDFN Hydrologic Unit Codes is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_latest_continuous():
        """WDFN Latest Continuous is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_latest_daily():
        """WDFN Latest Daily is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_latest_field_measurements():
        """WDFN Latest Field Measurements is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_medium_codes():
        """WDFN Medium Codes is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_method_categories():
        """WDFN Method Categories is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_method_citations():
        """WDFN Method Citations is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_methods():
        """WDFN Methods is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_monitoring_locations():
        """WDFN Monitoring Locations is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_national_aquifer_codes():
        """WDFN National Aquifer Codes is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_parameter_codes():
        """WDFN Parameter Codes is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_peaks():
        """WDFN Peaks is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_read_interval_observations():
        """WDFN Read Interval Observations is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_read_normal_observations():
        """WDFN Read Normal Observations is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_reliability_codes():
        """WDFN Reliability Codes is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_site_types():
        """WDFN Site Types is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_states():
        """WDFN States is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_statistic_codes():
        """WDFN Statistic Codes is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_time_series_metadata():
        """WDFN Time Series Metadata is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_time_series_methods():
        """WDFN Time Series Methods is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_time_series_revisions():
        """WDFN Time Series Revisions is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_time_zone_codes():
        """WDFN Time Zone Codes is not installed. Install tsgettoolbox_wdfn."""

    def wdfn_topographic_codes():
        """WDFN Topographic Codes is not installed. Install tsgettoolbox_wdfn."""
