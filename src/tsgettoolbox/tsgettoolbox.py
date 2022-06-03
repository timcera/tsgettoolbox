# -*- coding: utf-8 -*-
r"""
tsgettoolbox command line/library tools to retrieve time series.

This program is a collection of utilities to download data from various
web services.
"""
from __future__ import absolute_import, division, print_function

import os.path
import sys
import warnings

import mando

warnings.filterwarnings("ignore")


@mando.command()
def about():
    r"""Print out information about tsgettoolbox and the system."""
    from tstoolbox import tsutils

    tsutils.about(__name__)


def main():
    r"""Main function."""
    if not os.path.exists("debug_tsgettoolbox"):
        sys.tracebacklimit = 0
    mando.main()


if __name__ == "__main__":
    main()
