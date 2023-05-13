r"""
tsgettoolbox command line/library tools to retrieve time series.

This program is a collection of utilities to download data from various
web services.
"""

import warnings

warnings.filterwarnings("ignore")


from .functions.cdec import cdec
from .functions.coops import coops
from .functions.cpc import cpc
from .functions.daymet import daymet
from .functions.fawn import fawn
from .functions.hydstra import hydstra_catalog, hydstra_stations, hydstra_ts
from .functions.ldas import (
    ldas,
    ldas_gldas_noah,
    ldas_grace,
    ldas_merra,
    ldas_merra_update,
    ldas_nldas_fora,
    ldas_nldas_noah,
    ldas_smerge,
    ldas_trmm_tmpa,
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
from .functions.swtwc import swtwc
from .functions.terraclimate import terraclimate
from .functions.terraclimate2C import terraclimate2C
from .functions.terraclimate4C import terraclimate4C
from .functions.terraclimate19611990 import terraclimate19611990
from .functions.terraclimate19812010 import terraclimate19812010
from .functions.topowx import topowx, topowx_daily
from .functions.twc import twc
from .functions.unavco import unavco
from .functions.usgs_flet import usgs_flet_narr, usgs_flet_stns


def main():
    r"""Main function."""
    # from argparse import RawTextHelpFormatter as HelpFormatter
    import datetime
    import os.path
    import sys

    import cltoolbox
    import pandas as pd
    from cltoolbox.rst_text_formatter import RSTHelpFormatter as HelpFormatter
    from toolbox_utils import tsutils

    if not os.path.exists("debug_tsgettoolbox"):
        sys.tracebacklimit = 0

    @cltoolbox.command("cdec", formatter_class=HelpFormatter)
    @tsutils.copy_doc(cdec)
    def cdec_cli(
        station_id, dur_code=None, sensor_num=None, start_date=None, end_date=None
    ):
        tsutils.printiso(
            cdec(
                station_id,
                dur_code=dur_code,
                sensor_num=sensor_num,
                start_date=start_date,
                end_date=end_date,
            )
        )

    @cltoolbox.command("coops", formatter_class=HelpFormatter)
    @tsutils.copy_doc(coops)
    def coops_cli(
        station,
        date=None,
        begin_date=None,
        end_date=None,
        range=None,
        product="hourly_height",
        datum="NAVD",
        time_zone="GMT",
        interval="h",
        bin=None,
    ):
        tsutils.printiso(
            coops(
                station,
                date=date,
                begin_date=begin_date,
                end_date=end_date,
                range=range,
                product=product,
                datum=datum,
                time_zone=time_zone,
                interval=interval,
                bin=bin,
            )
        )

    @cltoolbox.command("cpc", formatter_class=HelpFormatter)
    @tsutils.copy_doc(cpc)
    def cpc_cli(state=None, climate_division=None, start_date=None, end_date=None):
        tsutils.printiso(
            cpc(
                state=state,
                climate_division=climate_division,
                start_date=start_date,
                end_date=end_date,
            )
        )

    @cltoolbox.command("daymet", formatter_class=HelpFormatter)
    @tsutils.copy_doc(daymet)
    def daymet_cli(
        lat,
        lon,
        start_date=pd.Timestamp("1980-01-01"),
        end_date=None,
        years=None,
        measuredParams="all",
        time_scale="daily",
        snow=False,
        pet_soil_heat=0.0,
        pet_alpha=1.26,
    ):
        tsutils.printiso(
            daymet(
                lat,
                lon,
                start_date=start_date,
                end_date=end_date,
                years=years,
                measuredParams=measuredParams,
                time_scale=time_scale,
                snow=snow,
                pet_soil_heat=pet_soil_heat,
                pet_alpha=pet_alpha,
            )
        )

    @cltoolbox.command("fawn", formatter_class=HelpFormatter)
    @tsutils.copy_doc(fawn)
    def fawn_cli(
        stations,
        variables,
        reportType,
        start_date=datetime.datetime(1998, 1, 1),
        end_date=datetime.datetime.now(),
    ):
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
        """Create a foundation CLI function returning a function."""

        @cltoolbox.command(cli_name, formatter_class=formatter_class)
        @tsutils.copy_doc(function)
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
            tsutils.printiso(
                function(
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

    ldas_cli = foundation_cli(ldas, "ldas")

    ldas_gldas_noah_cli = foundation_cli(ldas_gldas_noah, "ldas_gldas_noah")

    ldas_grace_cli = foundation_cli(ldas_grace, "ldas_grace")

    ldas_merra_cli = foundation_cli(ldas_merra, "ldas_merra")

    ldas_merra_update_cli = foundation_cli(ldas_merra_update, "ldas_merra_update")

    ldas_nldas_fora_cli = foundation_cli(ldas_nldas_fora, "ldas_nldas_fora")

    ldas_nldas_noah_cli = foundation_cli(ldas_nldas_noah, "ldas_nldas_noah")

    # ldas_amsre_rzsm3_cli = foundation_cli(ldas_amsre_rzsm3)

    ldas_smerge_cli = foundation_cli(ldas_smerge, "ldas_smerge")

    ldas_trmm_tmpa_cli = foundation_cli(ldas_trmm_tmpa, "ldas_trmm_tmpa")

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

    @cltoolbox.command("swtwc", formatter_class=HelpFormatter)
    @tsutils.copy_doc(swtwc)
    def swtwc_cli(station_code, date=None):
        tsutils.printiso(swtwc(station_code, date=date))

    @cltoolbox.command("terraclimate19611990", formatter_class=HelpFormatter)
    @tsutils.copy_doc(terraclimate19611990)
    def terraclimate19611990_cli(
        lat: float,
        lon: float,
        variables=None,
        start_date=None,
        end_date=None,
    ):
        tsutils.printiso(
            terraclimate19611990(
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

    @cltoolbox.command("terraclimate2C", formatter_class=HelpFormatter)
    @tsutils.copy_doc(terraclimate2C)
    def terraclimate2C_cli(
        lat: float,
        lon: float,
        variables=None,
        start_date=None,
        end_date=None,
    ):
        tsutils.printiso(
            terraclimate2C(
                lat,
                lon,
                variables=variables,
                start_date=start_date,
                end_date=end_date,
            )
        )

    @cltoolbox.command("terraclimate4C", formatter_class=HelpFormatter)
    @tsutils.copy_doc(terraclimate4C)
    def terraclimate4C_cli(
        lat: float,
        lon: float,
        variables=None,
        start_date=None,
        end_date=None,
    ):
        tsutils.printiso(
            terraclimate4C(
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

    @cltoolbox.command("topowx", formatter_class=HelpFormatter)
    @tsutils.copy_doc(topowx)
    def topowx_cli(
        lat,
        lon,
        variables=None,
        start_date=None,
        end_date=None,
    ):
        tsutils.printiso(
            topowx(
                lat,
                lon,
                variables=variables,
                start_date=start_date,
                end_date=end_date,
            )
        )

    @cltoolbox.command("topowx_daily", formatter_class=HelpFormatter)
    @tsutils.copy_doc(topowx_daily)
    def topowx_daily_cli(
        lat,
        lon,
        variables=None,
        start_date=None,
        end_date=None,
    ):
        tsutils.printiso(
            topowx_daily(
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

    @cltoolbox.command("usgs_flet_narr", formatter_class=HelpFormatter)
    @tsutils.copy_doc(usgs_flet_narr)
    def usgs_flet_narr_cli(
        lat,
        lon,
        variables=None,
        start_date=None,
        end_date=None,
    ):
        tsutils.printiso(
            usgs_flet_narr(
                lat,
                lon,
                variables=variables,
                start_date=start_date,
                end_date=end_date,
            )
        )

    @cltoolbox.command("usgs_flet_stns", formatter_class=HelpFormatter)
    @tsutils.copy_doc(usgs_flet_stns)
    def usgs_flet_stns_cli(
        lat,
        lon,
        variables=None,
        start_date=None,
        end_date=None,
    ):
        tsutils.printiso(
            usgs_flet_stns(
                lat,
                lon,
                variables=variables,
                start_date=start_date,
                end_date=end_date,
            )
        )

    @cltoolbox.command("about")
    def about():
        r"""Print out information about tsgettoolbox and the system."""
        from toolbox_utils import tsutils

        tsutils.about(__name__)

    cltoolbox.main()


if __name__ == "__main__":
    main()
