r"""
tsgettoolbox command line/library tools to retrieve time series.

This program is a collection of utilities to download data from various
web services.
"""

__all__ = [
    "cdec",
    "coops",
    "daymet",
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

# Standard library imports
import inspect
import warnings
from functools import wraps

# Local folder imports
from .functions.cdec import cdec
from .functions.coops import coops
from .functions.daymet import daymet
from .functions.fawn import fawn
from .functions.hydstra import hydstra_catalog, hydstra_stations, hydstra_ts
from .functions.ldas import (
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
from .functions.metdata import metdata
from .functions.modis import modis
from .functions.ncei import (
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
from .functions.ndbc import ndbc
from .functions.nwis import (
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
from .functions.rivergages import rivergages
from .functions.terraclimate import terraclimate
from .functions.terraclimate19812010 import terraclimate19812010
from .functions.terraclimate19912020 import terraclimate19912020
from .functions.twc import twc
from .functions.unavco import unavco
from .functions.usgs_wdfn.usgs_wdfn import (
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
    import datetime
    import os.path
    import sys

    # Third party imports
    import cltoolbox
    import pandas as pd
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
    @tsutils.copy_doc(daymet)
    def daymet_cli(
        lat,
        lon,
        start_date=None,
        end_date=None,
        years=None,
        measuredParams="all",
    ):
        if start_date is None:
            start_date = pd.Timestamp("1980-01-01")
        tsutils.printiso(
            daymet(
                lat,
                lon,
                start_date=start_date,
                end_date=end_date,
                years=years,
                measuredParams=measuredParams,
            )
        )

    @cltoolbox.command("fawn", formatter_class=HelpFormatter)
    @tsutils.copy_doc(fawn)
    def fawn_cli(
        stations,
        variables,
        reportType,
        start_date=None,
        end_date=None,
    ):
        if start_date is None:
            start_date = datetime.datetime(1998, 1, 1, tzinfo=datetime.timezone.utc)
        if end_date is None:
            end_date = datetime.datetime.now(datetime.timezone.utc)
        tsutils.printiso(
            fawn(
                stations,
                variables,
                reportType,
                start_date=start_date,
                end_date=end_date,
            )
        )

    @cltoolbox.command("hydstra_ts", formatter_class=HelpFormatter)
    @tsutils.copy_doc(hydstra_ts)
    def hydstra_ts_cli(
        server,
        station,
        variable,
        start_time,
        end_time,
        interval="day",
        provisional=False,
        datasource=None,
        aggcode=None,
        quality=False,
        maxqual=254,
    ):
        tsutils.printiso(
            hydstra_ts(
                server,
                station,
                variable,
                start_time,
                end_time,
                interval=interval,
                provisional=provisional,
                datasource=datasource,
                aggcode=aggcode,
                quality=quality,
                maxqual=maxqual,
            )
        )

    @cltoolbox.command("hydstra_catalog", formatter_class=HelpFormatter)
    @tsutils.copy_doc(hydstra_catalog)
    def hydstra_catalog_cli(server, station, isleep=0, tablefmt="csv"):
        catalogdf = hydstra_catalog(server, station, isleep=isleep)
        tsutils.printiso(catalogdf, tablefmt=tablefmt, headers="keys", showindex=False)

    @cltoolbox.command("hydstra_stations", formatter_class=HelpFormatter)
    @tsutils.copy_doc(hydstra_stations)
    def hydstra_stations_cli(server, activeonly=False, latlong=False, tablefmt="csv"):
        sitedf = hydstra_stations(server, activeonly=activeonly, latlong=latlong)
        tsutils.printiso(sitedf, headers="keys", tablefmt=tablefmt, showindex=False)

    def foundation_cli(
        function,
        cli_name,
        formatter_class=HelpFormatter,
    ):
        """Create a foundation CLI function for LDAS returning a function."""

        @cltoolbox.command(cli_name, formatter_class=formatter_class)
        @tsutils.copy_doc(function)
        def ldas_cli(
            lat=None,
            lon=None,
            variables=None,
            startDate=None,
            endDate=None,
            variable=None,
        ):
            tsutils.printiso(
                function(
                    lat,
                    lon,
                    variables=variables,
                    startDate=startDate,
                    endDate=endDate,
                    variable=variable,
                )
            )

        return ldas_cli

    ldas_cli = foundation_cli(ldas, "ldas")  # noqa: F841

    ldas_gldas_noah_cli = foundation_cli(ldas_gldas_noah, "ldas_gldas_noah")  # noqa: F841

    ldas_gldas_noah_v2_0_cli = foundation_cli(  # noqa: F841
        ldas_gldas_noah_v2_0, "ldas_gldas_noah_v2_0"
    )

    ldas_gldas_noah_v2_1_cli = foundation_cli(  # noqa: F841
        ldas_gldas_noah_v2_1, "ldas_gldas_noah_v2_1"
    )

    ldas_grace_cli = foundation_cli(ldas_grace, "ldas_grace")  # noqa: F841

    ldas_merra_cli = foundation_cli(ldas_merra, "ldas_merra")  # noqa: F841

    ldas_nldas_fora_cli = foundation_cli(ldas_nldas_fora, "ldas_nldas_fora")  # noqa: F841

    ldas_nldas_noah_cli = foundation_cli(ldas_nldas_noah, "ldas_nldas_noah")  # noqa: F841

    ldas_nldas_vic_cli = foundation_cli(ldas_nldas_vic, "ldas_nldas_vic")  # noqa: F841

    ldas_smerge_cli = foundation_cli(ldas_smerge, "ldas_smerge")  # noqa: F841

    @cltoolbox.command("metdata", formatter_class=HelpFormatter)
    @tsutils.copy_doc(metdata)
    def metdata_cli(
        lat,
        lon,
        variables=None,
        start_date=None,
        end_date=None,
    ):
        tsutils.printiso(
            metdata(
                lat,
                lon,
                variables=variables,
                start_date=start_date,
                end_date=end_date,
            )
        )

    @cltoolbox.command("modis", formatter_class=HelpFormatter)
    @tsutils.copy_doc(modis)
    def modis_cli(lat, lon, product, band, start_date=None, end_date=None):
        tsutils.printiso(
            modis(lat, lon, product, band, start_date=start_date, end_date=end_date)
        )

    @cltoolbox.command("ncei_ghcnd_ftp", formatter_class=HelpFormatter)
    @tsutils.copy_doc(ncei_ghcnd_ftp)
    def ncei_ghcnd_ftp_cli(stationid, start_date=None, end_date=None):
        tsutils.printiso(
            ncei_ghcnd_ftp(stationid, start_date=start_date, end_date=end_date),
        )

    # 1763-01-01, 2016-11-05, Daily Summaries             , 1    , GHCND
    @cltoolbox.command("ncei_ghcnd", formatter_class=HelpFormatter)
    @tsutils.copy_doc(ncei_ghcnd)
    def ncei_ghcnd_cli(stationid, start_date=None, end_date=None):
        tsutils.printiso(
            ncei_ghcnd(stationid, start_date=start_date, end_date=end_date),
        )

    @cltoolbox.command("ncei_gsod", formatter_class=HelpFormatter)
    @tsutils.copy_doc(ncei_gsod)
    def ncei_gsod_cli(stationid, start_date=None, end_date=None):
        tsutils.printiso(
            ncei_gsod(stationid, start_date=start_date, end_date=end_date),
        )

    # 1763-01-01, 2016-09-01, Global Summary of the Month , 1    , GSOM
    @cltoolbox.command("ncei_gsom", formatter_class=HelpFormatter)
    @tsutils.copy_doc(ncei_gsom)
    def ncei_gsom_cli(stationid, start_date=None, end_date=None):
        tsutils.printiso(
            ncei_gsom(
                stationid,
                start_date=start_date,
                end_date=end_date,
            ),
        )

    # 1763-01-01, 2016-01-01, Global Summary of the Year  , 1    , GSOY
    @cltoolbox.command("ncei_gsoy", formatter_class=HelpFormatter)
    @tsutils.copy_doc(ncei_gsoy)
    def ncei_gsoy_cli(stationid, start_date=None, end_date=None):
        tsutils.printiso(
            ncei_gsoy(
                stationid,
                start_date=start_date,
                end_date=end_date,
            ),
        )

    # 1991-06-05, 2016-11-06, Weather Radar (Level II)    , 0.95 , NEXRAD2
    # @cltoolbox.command('ncei_nexrad2', formatter_class=HelpFormatter)
    def ncei_nexrad2_cli(stationid, start_date=None, end_date=None):
        tsutils.printiso(
            ncei_nexrad2(stationid, start_date=start_date, end_date=end_date),
        )

    # 1991-06-05, 2016-11-06, Weather Radar (Level III)   , 0.95 , NEXRAD3
    # @cltoolbox.command('ncei_nexrad3',formatter_class=HelpFormatter)
    def ncei_nexrad3_cli(stationid, start_date=None, end_date=None):
        return tsutils.printiso(
            ncei_nexrad3(stationid, start_date=start_date, end_date=end_date),
        )

    # 2010-01-01, 2010-01-01, Normals Annual/Seasonal     , 1    , NORMAL_ANN
    @cltoolbox.command("ncei_normal_ann", formatter_class=HelpFormatter)
    @tsutils.copy_doc(ncei_normal_ann)
    def ncei_normal_ann_cli(stationid):
        tsutils.printiso(ncei_normal_ann(stationid))

    # 2010-01-01, 2010-12-31, Normals Daily               , 1    , NORMAL_DLY
    @cltoolbox.command("ncei_normal_dly", formatter_class=HelpFormatter)
    @tsutils.copy_doc(ncei_normal_dly)
    def ncei_normal_dly_cli(stationid):
        tsutils.printiso(ncei_normal_dly(stationid))

    # 2010-01-01, 2010-12-31, Normals Hourly              , 1    , NORMAL_HLY
    @cltoolbox.command("ncei_normal_hly", formatter_class=HelpFormatter)
    @tsutils.copy_doc(ncei_normal_hly)
    def ncei_normal_hly_cli(stationid):
        tsutils.printiso(ncei_normal_hly(stationid))

    # 2010-01-01, 2010-12-01, Normals Monthly             , 1    , NORMAL_MLY
    @cltoolbox.command("ncei_normal_mly", formatter_class=HelpFormatter)
    @tsutils.copy_doc(ncei_normal_mly)
    def ncei_normal_mly_cli(stationid):
        tsutils.printiso(ncei_normal_mly(stationid))

    # 1970-05-12, 2014-01-01, Precipitation 15 Minute     , 0.25 , PRECIP_15
    @cltoolbox.command("ncei_precip_15", formatter_class=HelpFormatter)
    @tsutils.copy_doc(ncei_precip_15)
    def ncei_precip_15_cli(stationid, start_date=None, end_date=None):
        tsutils.printiso(
            ncei_precip_15(stationid, start_date=start_date, end_date=end_date),
        )

    # 1900-01-01, 2014-01-01, Precipitation Hourly        , 1    , PRECIP_HLY
    @cltoolbox.command("ncei_precip_hly", formatter_class=HelpFormatter)
    @tsutils.copy_doc(ncei_precip_hly)
    def ncei_precip_hly_cli(stationid, start_date=None, end_date=None):
        tsutils.printiso(
            ncei_precip_hly(stationid, start_date=start_date, end_date=end_date),
        )

    # ANNUAL
    @cltoolbox.command("ncei_annual", formatter_class=HelpFormatter)
    @tsutils.copy_doc(ncei_annual)
    def ncei_annual_cli(stationid, start_date=None, end_date=None):
        tsutils.printiso(
            ncei_annual(stationid, start_date=start_date, end_date=end_date),
        )

    # GHCNDMS
    @cltoolbox.command("ncei_ghcndms", formatter_class=HelpFormatter)
    @tsutils.copy_doc(ncei_ghcndms)
    def ncei_ghcndms_cli(stationid, start_date=None, end_date=None):
        tsutils.printiso(
            ncei_ghcndms(stationid, start_date=start_date, end_date=end_date),
        )

    @cltoolbox.command("ncei_ish", formatter_class=HelpFormatter)
    @tsutils.copy_doc(ncei_ish)
    def ncei_ish_cli(stationid, start_date=None, end_date=None):
        tsutils.printiso(
            ncei_ish(stationid, start_date=start_date, end_date=end_date),
        )

    # @cltoolbox.command("ncei_cirs", formatter_class=HelpFormatter)
    # @tsutils.copy_doc(ncei_cirs)
    # def ncei_cirs_cli(elements=None, by_state=False, location_names="abbr"):
    #     tsutils.printiso(
    #         ncei_cirs(
    #             elements=elements, by_state=by_state, location_names=location_names
    #         )
    #     )

    @cltoolbox.command("ndbc", formatter_class=HelpFormatter)
    @tsutils.copy_doc(ndbc)
    def ndbc_cli(station, table, startUTC, endUTC=None):
        tsutils.printiso(ndbc(station, table, startUTC, endUTC=endUTC))

    @cltoolbox.command("nwis", formatter_class=HelpFormatter)
    @tsutils.copy_doc(nwis)
    def nwis_cli(
        sites=None,
        stateCd=None,
        huc=None,
        bBox=None,
        countyCd=None,
        parameterCd=None,
        period=None,
        startDT=None,
        endDT=None,
        siteType=None,
        modifiedSince=None,
        agencyCd=None,
        siteStatus=None,
        altMin=None,
        altMax=None,
        drainAreaMin=None,
        drainAreaMax=None,
        aquiferCd=None,
        localAquiferCd=None,
        wellDepthMin=None,
        wellDepthMax=None,
        holeDepthMin=None,
        holeDepthMax=None,
        database="dv",
        statReportType=None,
        statType=None,
        missingData=None,
        statYearType=None,
    ):
        tsutils.printiso(
            nwis(
                sites=sites,
                stateCd=stateCd,
                huc=huc,
                bBox=bBox,
                countyCd=countyCd,
                parameterCd=parameterCd,
                period=period,
                startDT=startDT,
                endDT=endDT,
                siteType=siteType,
                modifiedSince=modifiedSince,
                agencyCd=agencyCd,
                siteStatus=siteStatus,
                altMin=altMin,
                altMax=altMax,
                drainAreaMin=drainAreaMin,
                drainAreaMax=drainAreaMax,
                aquiferCd=aquiferCd,
                localAquiferCd=localAquiferCd,
                wellDepthMin=wellDepthMin,
                wellDepthMax=wellDepthMax,
                holeDepthMin=holeDepthMin,
                holeDepthMax=holeDepthMax,
                database=database,
                statReportType=statReportType,
                statType=statType,
                missingData=missingData,
                statYearType=statYearType,
            )
        )

    @cltoolbox.command("nwis_iv", formatter_class=HelpFormatter)
    @tsutils.copy_doc(nwis_iv)
    def nwis_iv_cli(
        sites=None,
        stateCd=None,
        huc=None,
        bBox=None,
        countyCd=None,
        parameterCd=None,
        siteType=None,
        modifiedSince=None,
        agencyCd=None,
        siteStatus=None,
        altMin=None,
        altMax=None,
        drainAreaMin=None,
        drainAreaMax=None,
        aquiferCd=None,
        localAquiferCd=None,
        wellDepthMin=None,
        wellDepthMax=None,
        holeDepthMin=None,
        holeDepthMax=None,
        period=None,
        startDT=None,
        endDT=None,
        include_codes=False,
    ):
        tsutils.printiso(
            nwis_iv(
                sites=sites,
                stateCd=stateCd,
                huc=huc,
                bBox=bBox,
                countyCd=countyCd,
                parameterCd=parameterCd,
                siteType=siteType,
                modifiedSince=modifiedSince,
                agencyCd=agencyCd,
                siteStatus=siteStatus,
                altMin=altMin,
                altMax=altMax,
                drainAreaMin=drainAreaMin,
                drainAreaMax=drainAreaMax,
                aquiferCd=aquiferCd,
                localAquiferCd=localAquiferCd,
                wellDepthMin=wellDepthMin,
                wellDepthMax=wellDepthMax,
                holeDepthMin=holeDepthMin,
                holeDepthMax=holeDepthMax,
                period=period,
                startDT=startDT,
                endDT=endDT,
                include_codes=include_codes,
            )
        )

    @cltoolbox.command("nwis_dv", formatter_class=HelpFormatter)
    @tsutils.copy_doc(nwis_dv)
    def nwis_dv_cli(
        sites=None,
        stateCd=None,
        huc=None,
        bBox=None,
        countyCd=None,
        agencyCd=None,
        altMax=None,
        altMin=None,
        aquiferCd=None,
        drainAreaMax=None,
        drainAreaMin=None,
        holeDepthMax=None,
        holeDepthMin=None,
        localAquiferCd=None,
        modifiedSince=None,
        parameterCd=None,
        siteStatus=None,
        siteType=None,
        wellDepthMax=None,
        wellDepthMin=None,
        startDT=None,
        endDT=None,
        period=None,
        include_codes=False,
        statisticsCd=None,
    ):
        tsutils.printiso(
            nwis_dv(
                sites=sites,
                stateCd=stateCd,
                huc=huc,
                bBox=bBox,
                countyCd=countyCd,
                parameterCd=parameterCd,
                statisticsCd=statisticsCd,
                siteType=siteType,
                modifiedSince=modifiedSince,
                agencyCd=agencyCd,
                siteStatus=siteStatus,
                altMin=altMin,
                altMax=altMax,
                drainAreaMin=drainAreaMin,
                drainAreaMax=drainAreaMax,
                aquiferCd=aquiferCd,
                localAquiferCd=localAquiferCd,
                wellDepthMin=wellDepthMin,
                wellDepthMax=wellDepthMax,
                holeDepthMin=holeDepthMin,
                holeDepthMax=holeDepthMax,
                period=period,
                startDT=startDT,
                endDT=endDT,
                include_codes=include_codes,
            )
        )

    @cltoolbox.command("nwis_site", formatter_class=HelpFormatter)
    @tsutils.copy_doc(nwis_site)
    def nwis_site_cli(
        sites=None,
        stateCd=None,
        huc=None,
        bBox=None,
        countyCd=None,
        parameterCd=None,
        period=None,
        startDT=None,
        endDT=None,
        siteType=None,
        modifiedSince=None,
        agencyCd=None,
        siteStatus=None,
        altMin=None,
        altMax=None,
        drainAreaMin=None,
        drainAreaMax=None,
        aquiferCd=None,
        localAquiferCd=None,
        wellDepthMin=None,
        wellDepthMax=None,
        holeDepthMin=None,
        holeDepthMax=None,
        siteOutput=None,
        seriesCatalogOutput=None,
        outputDataTypeCd=None,
        siteName=None,
        siteNameMatchOperator=None,
        hasDataTypeCd=None,
    ):
        tsutils.printiso(
            nwis_site(
                sites=sites,
                stateCd=stateCd,
                huc=huc,
                bBox=bBox,
                countyCd=countyCd,
                parameterCd=parameterCd,
                siteType=siteType,
                modifiedSince=modifiedSince,
                agencyCd=agencyCd,
                siteStatus=siteStatus,
                altMin=altMin,
                altMax=altMax,
                drainAreaMin=drainAreaMin,
                drainAreaMax=drainAreaMax,
                aquiferCd=aquiferCd,
                localAquiferCd=localAquiferCd,
                wellDepthMin=wellDepthMin,
                wellDepthMax=wellDepthMax,
                holeDepthMin=holeDepthMin,
                holeDepthMax=holeDepthMax,
                period=period,
                startDT=startDT,
                endDT=endDT,
                siteOutput=siteOutput,
                seriesCatalogOutput=seriesCatalogOutput,
                outputDataTypeCd=outputDataTypeCd,
                siteName=siteName,
                siteNameMatchOperator=siteNameMatchOperator,
                hasDataTypeCd=hasDataTypeCd,
            )
        )

    @cltoolbox.command("nwis_gwlevels", formatter_class=HelpFormatter)
    @tsutils.copy_doc(nwis_gwlevels)
    def nwis_gwlevels_cli(
        sites=None,
        stateCd=None,
        huc=None,
        bBox=None,
        countyCd=None,
        parameterCd=None,
        period=None,
        startDT=None,
        endDT=None,
        siteType=None,
        modifiedSince=None,
        agencyCd=None,
        siteStatus=None,
        altMin=None,
        altMax=None,
        aquiferCd=None,
        localAquiferCd=None,
        wellDepthMin=None,
        wellDepthMax=None,
        holeDepthMin=None,
        holeDepthMax=None,
    ):
        tsutils.printiso(
            nwis_gwlevels(
                sites=sites,
                stateCd=stateCd,
                huc=huc,
                bBox=bBox,
                countyCd=countyCd,
                parameterCd=parameterCd,
                siteType=siteType,
                modifiedSince=modifiedSince,
                agencyCd=agencyCd,
                siteStatus=siteStatus,
                altMin=altMin,
                altMax=altMax,
                aquiferCd=aquiferCd,
                localAquiferCd=localAquiferCd,
                wellDepthMin=wellDepthMin,
                wellDepthMax=wellDepthMax,
                holeDepthMin=holeDepthMin,
                holeDepthMax=holeDepthMax,
                period=period,
                startDT=startDT,
                endDT=endDT,
            )
        )

    @cltoolbox.command("nwis_measurements", formatter_class=HelpFormatter)
    @tsutils.copy_doc(nwis_measurements)
    def nwis_measurements_cli(
        sites=None,
        stateCd=None,
        huc=None,
        bBox=None,
        countyCd=None,
        parameterCd=None,
        period=None,
        startDT=None,
        endDT=None,
        siteType=None,
        modifiedSince=None,
        agencyCd=None,
        siteStatus=None,
        altMin=None,
        altMax=None,
        aquiferCd=None,
        localAquiferCd=None,
        wellDepthMin=None,
        wellDepthMax=None,
        holeDepthMin=None,
        holeDepthMax=None,
    ):
        tsutils.printiso(
            nwis_measurements(
                sites=sites,
                stateCd=stateCd,
                huc=huc,
                bBox=bBox,
                countyCd=countyCd,
                parameterCd=parameterCd,
                siteType=siteType,
                modifiedSince=modifiedSince,
                agencyCd=agencyCd,
                siteStatus=siteStatus,
                altMin=altMin,
                altMax=altMax,
                aquiferCd=aquiferCd,
                localAquiferCd=localAquiferCd,
                wellDepthMin=wellDepthMin,
                wellDepthMax=wellDepthMax,
                holeDepthMin=holeDepthMin,
                holeDepthMax=holeDepthMax,
                period=period,
                startDT=startDT,
                endDT=endDT,
            )
        )

    @cltoolbox.command("nwis_peak", formatter_class=HelpFormatter)
    @tsutils.copy_doc(nwis_peak)
    def nwis_peak_cli(
        sites=None,
        stateCd=None,
        huc=None,
        bBox=None,
        countyCd=None,
        parameterCd=None,
        period=None,
        startDT=None,
        endDT=None,
        siteType=None,
        modifiedSince=None,
        agencyCd=None,
        siteStatus=None,
        altMin=None,
        altMax=None,
        aquiferCd=None,
        localAquiferCd=None,
        wellDepthMin=None,
        wellDepthMax=None,
        holeDepthMin=None,
        holeDepthMax=None,
    ):
        tsutils.printiso(
            nwis_peak(
                sites=sites,
                stateCd=stateCd,
                huc=huc,
                bBox=bBox,
                countyCd=countyCd,
                parameterCd=parameterCd,
                siteType=siteType,
                modifiedSince=modifiedSince,
                agencyCd=agencyCd,
                siteStatus=siteStatus,
                altMin=altMin,
                altMax=altMax,
                aquiferCd=aquiferCd,
                localAquiferCd=localAquiferCd,
                wellDepthMin=wellDepthMin,
                wellDepthMax=wellDepthMax,
                holeDepthMin=holeDepthMin,
                holeDepthMax=holeDepthMax,
                period=period,
                startDT=startDT,
                endDT=endDT,
            )
        )

    @cltoolbox.command("nwis_stat", formatter_class=HelpFormatter)
    @tsutils.copy_doc(nwis_stat)
    def nwis_stat_cli(
        sites=None,
        parameterCd=None,
        period=None,
        startDT=None,
        endDT=None,
        siteType=None,
        modifiedSince=None,
        agencyCd=None,
        siteStatus=None,
        altMin=None,
        altMax=None,
        drainAreaMin=None,
        drainAreaMax=None,
        aquiferCd=None,
        localAquiferCd=None,
        wellDepthMin=None,
        wellDepthMax=None,
        holeDepthMin=None,
        holeDepthMax=None,
        statReportType=None,
        statType=None,
        missingData=None,
        statYearType=None,
    ):
        tsutils.printiso(
            nwis_stat(
                sites=sites,
                parameterCd=parameterCd,
                siteType=siteType,
                modifiedSince=modifiedSince,
                agencyCd=agencyCd,
                siteStatus=siteStatus,
                altMin=altMin,
                altMax=altMax,
                drainAreaMin=drainAreaMin,
                drainAreaMax=drainAreaMax,
                aquiferCd=aquiferCd,
                localAquiferCd=localAquiferCd,
                wellDepthMin=wellDepthMin,
                wellDepthMax=wellDepthMax,
                holeDepthMin=holeDepthMin,
                holeDepthMax=holeDepthMax,
                period=period,
                startDT=startDT,
                endDT=endDT,
                statReportType=statReportType,
                statType=statType,
                missingData=missingData,
                statYearType=statYearType,
            )
        )

    @cltoolbox.command("epa_wqp", formatter_class=HelpFormatter)
    @tsutils.copy_doc(epa_wqp)
    def epa_wqp_cli(
        bBox=None,
        lat=None,
        lon=None,
        within=None,
        countrycode=None,
        statecode=None,
        countycode=None,
        siteType=None,
        organization=None,
        siteid=None,
        huc=None,
        sampleMedia=None,
        characteristicType=None,
        characteristicName=None,
        pCode=None,
        activityId=None,
        startDateLo=None,
        startDateHi=None,
    ):
        tsutils.printiso(
            epa_wqp(
                bBox=bBox,
                lat=lat,
                lon=lon,
                within=within,
                countrycode=countrycode,
                statecode=statecode,
                countycode=countycode,
                siteType=siteType,
                organization=organization,
                siteid=siteid,
                huc=huc,
                sampleMedia=sampleMedia,
                characteristicType=characteristicType,
                characteristicName=characteristicName,
                pCode=pCode,
                activityId=activityId,
                startDateLo=startDateLo,
                startDateHi=startDateHi,
            )
        )

    @cltoolbox.command("rivergages", formatter_class=HelpFormatter)
    @tsutils.copy_doc(rivergages)
    def rivergages_cli(station_code, parameter, start_date=None, end_date=None):
        ndf = rivergages(
            station_code, parameter, start_date=start_date, end_date=end_date
        )
        tsutils.printiso(ndf)

    @cltoolbox.command("terraclimate19912020", formatter_class=HelpFormatter)
    @tsutils.copy_doc(terraclimate19912020)
    def terraclimate19912020_cli(
        lat: float,
        lon: float,
        variables=None,
        start_date=None,
        end_date=None,
    ):
        tsutils.printiso(
            terraclimate19912020(
                lat,
                lon,
                variables=variables,
                start_date=start_date,
                end_date=end_date,
            )
        )

    @cltoolbox.command("terraclimate19812010", formatter_class=HelpFormatter)
    @tsutils.copy_doc(terraclimate19812010)
    def terraclimate19812010_cli(
        lat: float,
        lon: float,
        variables=None,
        start_date=None,
        end_date=None,
    ):
        tsutils.printiso(
            terraclimate19812010(
                lat,
                lon,
                variables=variables,
                start_date=start_date,
                end_date=end_date,
            )
        )

    @cltoolbox.command("terraclimate", formatter_class=HelpFormatter)
    @tsutils.copy_doc(terraclimate)
    def terraclimate_cli(
        lat: float,
        lon: float,
        variables=None,
        start_date=None,
        end_date=None,
    ):
        tsutils.printiso(
            terraclimate(
                lat,
                lon,
                variables=variables,
                start_date=start_date,
                end_date=end_date,
            )
        )

    @cltoolbox.command("twc", formatter_class=HelpFormatter)
    @tsutils.copy_doc(twc)
    def twc_cli(county, start_date=None, end_date=None):
        tsutils.printiso(twc(county, start_date=start_date, end_date=end_date))

    @cltoolbox.command("unavco", formatter_class=HelpFormatter)
    @tsutils.copy_doc(unavco)
    def unavco_cli(station, database="met", starttime=None, endtime=None):
        tsutils.printiso(
            unavco(station, database=database, starttime=starttime, endtime=endtime)
        )

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
