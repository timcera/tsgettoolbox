import mando

try:
    from mando.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter

from tstoolbox import tsutils


@mando.command("twc", formatter_class=HelpFormatter, doctype="numpy")
@tsutils.doc(tsutils.docstrings)
def twc_cli(county, start_date=None, end_date=None):
    r"""Download Texas Weather Connection (TWC) data.

    This module provides direct access to `Texas Weather Connection`_ `Daily
    Keetch-Byram Drought Index (KBDI)`_ dataset.

    .. _Texas Weather Connection: http://twc.tamu.edu/
    .. _Daily Keetch-Byram Drought Index (KBDI): http://twc.tamu.edu/drought/kbdi

    Parameters
    ----------
    county: ``None`` or str
        If specified, results will be limited to the county corresponding to
        the given 5-character Texas county fips code i.e. 48.
    {start_date}
    {end_date}
    """
    tsutils._printiso(twc(county, start_date=start_date, end_date=end_date))


def twc(county, start_date=None, end_date=None):
    r"""Download Texas Weather Connection (TWC) data."""
    from tsgettoolbox.services import twc

    df = twc.ulmo_df(county=county, start_date=start_date, end_date=end_date)

    return df


twc.__doc__ = twc_cli.__doc__
