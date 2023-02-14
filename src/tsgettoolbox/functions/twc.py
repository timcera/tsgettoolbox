"""
twc                 US/TX station D:Download Texas Weather Connection
                    (TWC) data.
"""

import cltoolbox
import pandas as pd
from cltoolbox.rst_text_formatter import RSTHelpFormatter as HelpFormatter
from toolbox_utils import tsutils

from tsgettoolbox.ulmo.twc.kbdi.core import get_data

__all__ = ["twc"]


def twc_ulmo_df(county=None, start_date=None, end_date=None):
    """Get data from ulmo.twc.kbdi.core.get_data() and return a dataframe."""
    df = get_data(
        county=county,
        start=pd.to_datetime(start_date),
        end=pd.to_datetime(end_date),
        as_dataframe=True,
    )
    df = df.set_index("date")
    return df


@cltoolbox.command("twc", formatter_class=HelpFormatter)
@tsutils.doc(tsutils.docstrings)
def twc_cli(county, start_date=None, end_date=None):
    r"""US/TX station D:Download Texas Weather Connection (TWC) data.

    This module provides direct access to `Texas Weather Connection`_ `Daily
    Keetch-Byram Drought Index (KBDI)`_ dataset.

    .. _Texas Weather Connection: http://twc.tamu.edu/
    .. _Daily Keetch-Byram Drought Index (KBDI): http://twc.tamu.edu/drought/kbdi

    Parameters
    ----------
    county : ``None`` or str
        If specified, results will be limited to the county corresponding to
        the given 5-character Texas county fips code i.e. 48.
    ${start_date}
    ${end_date}
    """
    tsutils.printiso(twc(county, start_date=start_date, end_date=end_date))


@tsutils.copy_doc(twc_cli)
def twc(county: int, start_date=None, end_date=None):
    r"""Download Texas Weather Connection (TWC) data."""
    return twc_ulmo_df(county=county, start_date=start_date, end_date=end_date)


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
