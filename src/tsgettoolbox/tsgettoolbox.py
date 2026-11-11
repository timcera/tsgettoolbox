r"""
tsgettoolbox command line/library tools to retrieve time series.

This program is a collection of utilities to download data from various
web services.
"""

# Standard library imports
import inspect
import warnings
from functools import wraps

# Local folder imports
from . import (
    cdec,
    coops,
    daymet,
    epa_wqp,
    fawn,
    hydstra_catalog,
    hydstra_stations,
    hydstra_ts,
    ldas,
    ldas_gldas_noah,
    ldas_gldas_noah_v2_0,
    ldas_gldas_noah_v2_1,
    ldas_grace,
    ldas_merra,
    ldas_nldas3_forcing,
    ldas_nldas_fora,
    ldas_nldas_noah,
    ldas_nldas_vic,
    ldas_smerge,
    metdata,
    modis,
    ncei_annual,
    ncei_ghcnd,
    ncei_ghcnd_ftp,
    ncei_ghcndms,
    ncei_gsod,
    ncei_gsom,
    ncei_gsoy,
    ncei_ish,
    ncei_normal_ann,
    ncei_normal_dly,
    ncei_normal_hly,
    ncei_normal_mly,
    ncei_precip_15,
    ncei_precip_hly,
    ndbc,
    nwis,
    nwis_dv,
    nwis_gwlevels,
    nwis_iv,
    nwis_measurements,
    nwis_peak,
    nwis_site,
    nwis_stat,
    rivergages,
    terraclimate,
    terraclimate19812010,
    terraclimate19912020,
    twc,
    unavco,
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
)
from .toolbox_utils.src.toolbox_utils import tsutils

warnings.filterwarnings("ignore")


def cli_decorator(base_func):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            parameters = inspect.signature(base_func).parameters
            parameter_names = tuple(parameters)

            positional_kwargs = dict(zip(parameter_names, args))
            positional_kwargs.update(kwargs)

            tsutils.printiso(base_func(**positional_kwargs))

        sig = inspect.signature(base_func)
        wrapper.__signature__ = sig
        wrapper.__doc__ = base_func.__doc__
        return wrapper

    return decorator


def main():
    r"""Main function."""
    # from argparse import RawTextHelpFormatter as HelpFormatter
    # Standard library imports
    import os.path
    import sys

    # Third party imports
    import cltoolbox
    from cltoolbox.rst_text_formatter import RSTHelpFormatter as HelpFormatter

    # Local folder imports
    from .toolbox_utils.src.toolbox_utils import tsutils

    if not os.path.exists("debug_tsgettoolbox"):
        sys.tracebacklimit = 0

    @cltoolbox.command("cdec", formatter_class=HelpFormatter)
    @cli_decorator(cdec)
    def cdec_cli(*args, **kwargs):
        """CDEC_CLI"""

    @cltoolbox.command("coops", formatter_class=HelpFormatter)
    @cli_decorator(coops)
    def coops_cli(*args, **kwargs):
        """COOPS"""

    @cltoolbox.command("daymet", formatter_class=HelpFormatter)
    @cli_decorator(daymet)
    def daymet_cli(*args, **kwargs):
        """DAYMET"""

    @cltoolbox.command("epa_wqp", formatter_class=HelpFormatter)
    @cli_decorator(epa_wqp)
    def epa_wqp_cli(*args, **kwargs):
        """EPA_WQP"""

    @cltoolbox.command("fawn", formatter_class=HelpFormatter)
    @cli_decorator(fawn)
    def fawn_cli(*args, **kwargs):
        """FAWN"""

    @cltoolbox.command("hydstra_catalog", formatter_class=HelpFormatter)
    @cli_decorator(hydstra_catalog)
    def hydstra_catalog_cli(*args, **kwargs):
        """HYDSTRA_CATALOG"""

    @cltoolbox.command("hydstra_stations", formatter_class=HelpFormatter)
    @cli_decorator(hydstra_stations)
    def hydstra_stations_cli(*args, **kwargs):
        """HYDSTRA_STATIONS"""

    @cltoolbox.command("hydstra_ts", formatter_class=HelpFormatter)
    @cli_decorator(hydstra_ts)
    def hydstra_ts_cli(*args, **kwargs):
        """HYDSTRA_TS"""

    @cltoolbox.command("ldas", formatter_class=HelpFormatter)
    @cli_decorator(ldas)
    def ldas_cli(*args, **kwargs):
        """LDAS"""

    @cltoolbox.command("ldas_gldas_noah", formatter_class=HelpFormatter)
    @cli_decorator(ldas_gldas_noah)
    def ldas_gldas_noah_cli(*args, **kwargs):
        """LDAS_GLDA_NOAH"""

    @cltoolbox.command("ldas_gldas_noah_v2_0", formatter_class=HelpFormatter)
    @cli_decorator(ldas_gldas_noah_v2_0)
    def ldas_gldas_noah_v2_0_cli(*args, **kwargs):
        """LDAS_GLDA_NOAH_V2_0"""

    @cltoolbox.command("ldas_gldas_noah_v2_1", formatter_class=HelpFormatter)
    @cli_decorator(ldas_gldas_noah_v2_1)
    def ldas_gldas_noah_v2_1_cli(*args, **kwargs):
        """LDAS_GLDA_NOAH_V2_1"""

    @cltoolbox.command("ldas_grace", formatter_class=HelpFormatter)
    @cli_decorator(ldas_grace)
    def ldas_grace_cli(*args, **kwargs):
        """LDAS_GRACE"""

    @cltoolbox.command("ldas_merra", formatter_class=HelpFormatter)
    @cli_decorator(ldas_merra)
    def ldas_merra_cli(*args, **kwargs):
        """LDAS_MERRA"""

    @cltoolbox.command("ldas_nldas3_forcing", formatter_class=HelpFormatter)
    @cli_decorator(ldas_nldas3_forcing)
    def ldas_nldas3_forcing_cli(*args, **kwargs):
        """LDAS_NLDAS3_FORCING"""

    @cltoolbox.command("ldas_nldas_fora", formatter_class=HelpFormatter)
    @cli_decorator(ldas_nldas_fora)
    def ldas_nldas_fora_cli(*args, **kwargs):
        """LDAS_NLDAS_FORA"""

    @cltoolbox.command("ldas_nldas_noah", formatter_class=HelpFormatter)
    @cli_decorator(ldas_nldas_noah)
    def ldas_nldas_noah_cli(*args, **kwargs):
        """LDAS_NLDAS_NOAH"""

    @cltoolbox.command("ldas_nldas_vic", formatter_class=HelpFormatter)
    @cli_decorator(ldas_nldas_vic)
    def ldas_nldas_vic_cli(*args, **kwargs):
        """LDAS_NLDAS_VIC"""

    @cltoolbox.command("ldas_smerge", formatter_class=HelpFormatter)
    @cli_decorator(ldas_smerge)
    def ldas_smerge_cli(*args, **kwargs):
        """LDAS_SMERGE"""

    @cltoolbox.command("metdata", formatter_class=HelpFormatter)
    @cli_decorator(metdata)
    def metdata_cli(*args, **kwargs):
        """METDATA"""

    @cltoolbox.command("modis", formatter_class=HelpFormatter)
    @cli_decorator(modis)
    def modis_cli(*args, **kwargs):
        """MODIS"""

    @cltoolbox.command("ncei_annual", formatter_class=HelpFormatter)
    @cli_decorator(ncei_annual)
    def ncei_annual_cli(*args, **kwargs):
        """NCEI_ANNUAL"""

    @cltoolbox.command("ncei_ghcnd", formatter_class=HelpFormatter)
    @cli_decorator(ncei_ghcnd)
    def ncei_ghcnd_cli(*args, **kwargs):
        """NCEI_GHCND"""

    @cltoolbox.command("ncei_ghcnd_ftp", formatter_class=HelpFormatter)
    @cli_decorator(ncei_ghcnd_ftp)
    def ncei_ghcnd_ftp_cli(*args, **kwargs):
        """NCEI_GHCND_FTP"""

    @cltoolbox.command("ncei_ghcndms", formatter_class=HelpFormatter)
    @cli_decorator(ncei_ghcndms)
    def ncei_ghcndms_cli(*args, **kwargs):
        """NCEI_GHCNDMS"""

    @cltoolbox.command("ncei_gsod", formatter_class=HelpFormatter)
    @cli_decorator(ncei_gsod)
    def ncei_gsod_cli(*args, **kwargs):
        """NCEI_GSOD"""

    @cltoolbox.command("ncei_gsom", formatter_class=HelpFormatter)
    @cli_decorator(ncei_gsom)
    def ncei_gsom_cli(*args, **kwargs):
        """NCEI_GSOM"""

    @cltoolbox.command("ncei_gsoy", formatter_class=HelpFormatter)
    @cli_decorator(ncei_gsoy)
    def ncei_gsoy_cli(*args, **kwargs):
        """NCEI_GSOY"""

    @cltoolbox.command("ncei_ish", formatter_class=HelpFormatter)
    @cli_decorator(ncei_ish)
    def ncei_ish_cli(*args, **kwargs):
        """NCEI_ISH"""

    @cltoolbox.command("ncei_normal_ann", formatter_class=HelpFormatter)
    @cli_decorator(ncei_normal_ann)
    def ncei_normal_ann_cli(*args, **kwargs):
        """NCEI_NORMAL_ANN"""

    @cltoolbox.command("ncei_normal_dly", formatter_class=HelpFormatter)
    @cli_decorator(ncei_normal_dly)
    def ncei_normal_dly_cli(*args, **kwargs):
        """NCEI_NORMAL_DLY"""

    @cltoolbox.command("ncei_normal_hly", formatter_class=HelpFormatter)
    @cli_decorator(ncei_normal_hly)
    def ncei_normal_hly_cli(*args, **kwargs):
        """NCEI_NORMAL_HLY"""

    @cltoolbox.command("ncei_normal_mly", formatter_class=HelpFormatter)
    @cli_decorator(ncei_normal_mly)
    def ncei_normal_mly_cli(*args, **kwargs):
        """NCEI_NORMAL_MLY"""

    @cltoolbox.command("ncei_precip_15", formatter_class=HelpFormatter)
    @cli_decorator(ncei_precip_15)
    def ncei_precip_15_cli(*args, **kwargs):
        """NCEI_PRECIP_15"""

    @cltoolbox.command("ncei_precip_hly", formatter_class=HelpFormatter)
    @cli_decorator(ncei_precip_hly)
    def ncei_precip_hly_cli(*args, **kwargs):
        """NCEI_PRECIP_HLY"""

    @cltoolbox.command("ndbc", formatter_class=HelpFormatter)
    @cli_decorator(ndbc)
    def ndbc_cli(*args, **kwargs):
        """NDBC"""

    @cltoolbox.command("nwis", formatter_class=HelpFormatter)
    @cli_decorator(nwis)
    def nwis_cli(*args, **kwargs):
        """NWIS"""

    @cltoolbox.command("nwis_dv", formatter_class=HelpFormatter)
    @cli_decorator(nwis_dv)
    def nwis_dv_cli(
        *args,
        **kwargs,
    ):
        """NWIS_DV"""

    @cltoolbox.command("nwis_gwlevels", formatter_class=HelpFormatter)
    @cli_decorator(nwis_gwlevels)
    def nwis_gwlevels_cli(*args, **kwargs):
        """NWIS_GWLEVELS"""

    @cltoolbox.command("nwis_iv", formatter_class=HelpFormatter)
    @cli_decorator(nwis_iv)
    def nwis_iv_cli(*args, **kwargs):
        """NWIS_IV"""

    @cltoolbox.command("nwis_measurements", formatter_class=HelpFormatter)
    @cli_decorator(nwis_measurements)
    def nwis_measurements_cli(*args, **kwargs):
        """NWIS_MEASUREMENTS"""

    @cltoolbox.command("nwis_peak", formatter_class=HelpFormatter)
    @cli_decorator(nwis_peak)
    def nwis_peak_cli(*args, **kwargs):
        """NWIS_PEAK"""

    @cltoolbox.command("nwis_site", formatter_class=HelpFormatter)
    @cli_decorator(nwis_site)
    def nwis_site_cli(*args, **kwargs):
        """NWIS_SITE"""

    @cltoolbox.command("nwis_stat", formatter_class=HelpFormatter)
    @cli_decorator(nwis_stat)
    def nwis_stat_cli(*args, **kwargs):
        """NWIS_STAT"""

    @cltoolbox.command("rivergages", formatter_class=HelpFormatter)
    @cli_decorator(rivergages)
    def rivergages_cli(*args, **kwargs):
        """RIVERGAGES"""

    @cltoolbox.command("terraclimate19912020", formatter_class=HelpFormatter)
    @cli_decorator(terraclimate19912020)
    def terraclimate19912020_cli(
        *args,
        **kwargs,
    ):
        """TERRACLIMATE19912020"""

    @cltoolbox.command("terraclimate19812010", formatter_class=HelpFormatter)
    @cli_decorator(terraclimate19812010)
    def terraclimate19812010_cli(
        *args,
        **kwargs,
    ):
        """TERRACLIMATE19812010"""

    @cltoolbox.command("terraclimate", formatter_class=HelpFormatter)
    @cli_decorator(terraclimate)
    def terraclimate_cli(
        *args,
        **kwargs,
    ):
        """TERRACLIMATE"""

    @cltoolbox.command("twc", formatter_class=HelpFormatter)
    @cli_decorator(twc)
    def twc_cli(*args, **kwargs):
        """TWC"""

    @cltoolbox.command("unavco", formatter_class=HelpFormatter)
    @cli_decorator(unavco)
    def unavco_cli(*args, **kwargs):
        """UNAVCO"""

    @cltoolbox.command("wdfn_agency_codes")
    @cli_decorator(wdfn_agency_codes)
    def wdfn_agency_codes_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_altitude_datums")
    @cli_decorator(wdfn_altitude_datums)
    def wdfn_altitude_datums_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_aquifer_codes")
    @cli_decorator(wdfn_aquifer_codes)
    def wdfn_aquifer_codes_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_aquifer_types")
    @cli_decorator(wdfn_aquifer_types)
    def wdfn_aquifer_types_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_channel_measurements")
    @cli_decorator(wdfn_channel_measurements)
    def wdfn_channel_measurements_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_citations")
    @cli_decorator(wdfn_citations)
    def wdfn_citations_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_combined_metadata")
    @cli_decorator(wdfn_combined_metadata)
    def wdfn_combined_metadata_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_continuous")
    @cli_decorator(wdfn_continuous)
    def wdfn_continuous_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_coordinate_accuracy_codes")
    @cli_decorator(wdfn_coordinate_accuracy_codes)
    def wdfn_coordinate_accuracy_codes_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_coordinate_datum_codes")
    @cli_decorator(wdfn_coordinate_datum_codes)
    def wdfn_coordinate_datum_codes_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_coordinate_method_codes")
    @cli_decorator(wdfn_coordinate_method_codes)
    def wdfn_coordinate_method_codes_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_counties")
    @cli_decorator(wdfn_counties)
    def wdfn_counties_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_countries")
    @cli_decorator(wdfn_countries)
    def wdfn_countries_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_daily")
    @cli_decorator(wdfn_daily)
    def wdfn_daily_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_field_measurements")
    @cli_decorator(wdfn_field_measurements)
    def wdfn_field_measurements_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_field_measurements_metadata")
    @cli_decorator(wdfn_field_measurements_metadata)
    def wdfn_field_measurements_metadata_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_hydrologic_unit_codes")
    @cli_decorator(wdfn_hydrologic_unit_codes)
    def wdfn_hydrologic_unit_codes_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_latest_continuous")
    @cli_decorator(wdfn_latest_continuous)
    def wdfn_latest_continuous_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_latest_daily")
    @cli_decorator(wdfn_latest_daily)
    def wdfn_latest_daily_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_latest_field_measurements")
    @cli_decorator(wdfn_latest_field_measurements)
    def wdfn_latest_field_measurements_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_medium_codes")
    @cli_decorator(wdfn_medium_codes)
    def wdfn_medium_codes_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_method_categories")
    @cli_decorator(wdfn_method_categories)
    def wdfn_method_categories_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_method_citations")
    @cli_decorator(wdfn_method_citations)
    def wdfn_method_citations_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_methods")
    @cli_decorator(wdfn_methods)
    def wdfn_methods_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_monitoring_locations")
    @cli_decorator(wdfn_monitoring_locations)
    def wdfn_monitoring_locations_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_national_aquifer_codes")
    @cli_decorator(wdfn_national_aquifer_codes)
    def wdfn_national_aquifer_codes_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_parameter_codes")
    @cli_decorator(wdfn_parameter_codes)
    def wdfn_parameter_codes_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_peaks")
    @cli_decorator(wdfn_peaks)
    def wdfn_peaks_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_reliability_codes")
    @cli_decorator(wdfn_reliability_codes)
    def wdfn_reliability_codes_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_site_types")
    @cli_decorator(wdfn_site_types)
    def wdfn_site_types_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_states")
    @cli_decorator(wdfn_states)
    def wdfn_states_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_statistic_codes")
    @cli_decorator(wdfn_statistic_codes)
    def wdfn_statistic_codes_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_time_series_metadata")
    @cli_decorator(wdfn_time_series_metadata)
    def wdfn_time_series_metadata_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_time_series_methods")
    @cli_decorator(wdfn_time_series_methods)
    def wdfn_time_series_methods_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_time_series_revisions")
    @cli_decorator(wdfn_time_series_revisions)
    def wdfn_time_series_revisions_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_time_zone_codes")
    @cli_decorator(wdfn_time_zone_codes)
    def wdfn_time_zone_codes_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_read_normal_observations")
    @cli_decorator(wdfn_read_normal_observations)
    def read_normal_observations_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("wdfn_read_interval_observations")
    @cli_decorator(wdfn_read_interval_observations)
    def wdfn_read_interval_observations_cli(*args, **kwargs):
        """WDFN"""

    @cltoolbox.command("about")
    def about():
        r"""Print out information about tsgettoolbox and the system."""
        tsutils.about(__name__)

    cltoolbox.main()


if __name__ == "__main__":
    main()
