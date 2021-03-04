#!/usr/bin/env python
r"""
tsgettoolbox command line/library tools to retrieve time series.

This program is a collection of utilities to download data from various
web services.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from .functions.cdec import cdec
from .functions.coops import coops
from .functions.cpc import cpc
from .functions.daymet import daymet
from .functions.fawn import fawn
from .functions.ldas import ldas
from .functions.modis import modis
from .functions.ncdc import ncdc_annual
from .functions.ncdc import ncdc_ghcnd
from .functions.ncdc import ncdc_ghcnd_ftp
from .functions.ncdc import ncdc_ghcndms
from .functions.ncdc import ncdc_gs
from .functions.ncdc import ncdc_nexrad2
from .functions.ncdc import ncdc_nexrad3
from .functions.ncdc import ncdc_normal_ann
from .functions.ncdc import ncdc_normal_dly
from .functions.ncdc import ncdc_normal_hly
from .functions.ncdc import ncdc_normal_mly
from .functions.ncdc import ncdc_precip_15
from .functions.ncdc import ncdc_precip_hly
from .functions.ndbc import ndbc
from .functions.nwis import epa_wqp
from .functions.nwis import nwis
from .functions.nwis import nwis_dv
from .functions.nwis import nwis_gwlevels
from .functions.nwis import nwis_iv
from .functions.nwis import nwis_measurements
from .functions.nwis import nwis_peak
from .functions.nwis import nwis_site
from .functions.nwis import nwis_stat
from .functions.twc import twc
from .functions.unavco import unavco
from .functions.usgs_eddn import usgs_eddn

import os.path
import sys
import warnings

import mando

try:
    from mando.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter

from tstoolbox import tsutils

warnings.filterwarnings("ignore")


@mando.command()
def about():
    r"""Print out information about tsgettoolbox and the system."""
    tsutils.about(__name__)


def main():
    r"""Main function."""
    if not os.path.exists("debug_tsgettoolbox"):
        sys.tracebacklimit = 0
    mando.main()


if __name__ == "__main__":
    main()
