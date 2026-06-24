r"""
tsgettoolbox command line/library tools to retrieve time series.

This program is a collection of utilities to download data from various
web services.
"""

__all__ = [
    "cdec",
    "coops",
    "cpc",
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
    "swtwc",
    "terraclimate",
    "terraclimate2C",
    "terraclimate4C",
    "terraclimate19611990",
    "terraclimate19812010",
    "terraclimate19912020",
    "twc",
    "unavco",
]

# Local folder imports
from .functions.cdec import cdec
from .functions.coops import coops
from .functions.cpc import cpc
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
from .functions.swtwc import swtwc
from .functions.terraclimate import terraclimate
from .functions.terraclimate2C import terraclimate2C
from .functions.terraclimate4C import terraclimate4C
from .functions.terraclimate19611990 import terraclimate19611990
from .functions.terraclimate19812010 import terraclimate19812010
from .functions.terraclimate19912020 import terraclimate19912020
from .functions.twc import twc
from .functions.unavco import unavco
