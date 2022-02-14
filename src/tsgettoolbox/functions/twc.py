# -*- coding: utf-8 -*-
import mando

try:
    from mando.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter

import pandas as pd
import typic
from tstoolbox import tsutils

from tsgettoolbox.ulmo.twc.kbdi.core import get_data


def twc_ulmo_df(county=None, start_date=None, end_date=None):

    df = get_data(
        county=county,
        start=pd.to_datetime(start_date),
        end=pd.to_datetime(end_date),
        as_dataframe=True,
    )
    df = df.set_index("date")
    return df


@mando.command("twc", formatter_class=HelpFormatter, doctype="numpy")
@tsutils.doc(tsutils.docstrings)
def twc_cli(county, start_date=None, end_date=None):
    r"""station: Download Texas Weather Connection (TWC) data.

    This module provides direct access to `Texas Weather Connection`_ `Daily
    Keetch-Byram Drought Index (KBDI)`_ dataset.

    .. _Texas Weather Connection: http://twc.tamu.edu/
    .. _Daily Keetch-Byram Drought Index (KBDI): http://twc.tamu.edu/drought/kbdi

    Parameters
    ----------
    county: ``None`` or str
        If specified, results will be limited to the county corresponding to
        the given 5-character Texas county fips code i.e. 48.
    ${start_date}
    ${end_date}
    """
    tsutils._printiso(twc(county, start_date=start_date, end_date=end_date))


@typic.al
def twc(county: int, start_date=None, end_date=None):
    r"""Download Texas Weather Connection (TWC) data."""
    df = twc_ulmo_df(county=county, start_date=start_date, end_date=end_date)

    return df


twc.__doc__ = twc_cli.__doc__


if __name__ == "__main__":
    #    import time
    #
    #    r = ulmo_df('blah',
    #                'upperbasin')
    #
    #    print('UB EVERYTHING')
    #    print(r)
    #
    #    time.sleep(20)

    r = twc_ulmo_df(48501, start_date="2015-11-04", end_date="2015-12-05")

    print("UB EVERYTHING")
    print(r)
