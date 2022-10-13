r"""
tsgettoolbox command line/library tools to retrieve time series.

This program is a collection of utilities to download data from various
web services.
"""

import warnings

import cltoolbox

warnings.filterwarnings("ignore")


@cltoolbox.command()
def about():
    r"""Print out information about tsgettoolbox and the system."""
    from toolbox_utils import tsutils

    tsutils.about(__name__)


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
    import os.path
    import sys

    if not os.path.exists("debug_tsgettoolbox"):
        sys.tracebacklimit = 0
    cltoolbox.main()


if __name__ == "__main__":
    main()
