import mando

try:
    from mando.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter

from tstoolbox import tsutils


@mando.command("cpc", formatter_class=HelpFormatter, doctype="numpy")
@tsutils.doc(tsutils.docstrings)
def cpc_cli(state=None, climate_division=None, start_date=None, end_date=None):
    r"""Access Climate Prediction Center, Weekly Drought Index dataset.

    Climate Prediction Center: http://www.cpc.ncep.noaa.gov/
    Weekly Drought Index: http://www.cpc.ncep.noaa.gov/products/analysis_monitoring/cdus/palmer_drought/

    Command Line ::

        tsgettoolbox cpc --state=FL --start_date 2017-01-01

    Python API ::

        df = tsgettoolbox.cpc("FL",
                              start_date="2017-01-01",
                              end_date="2017-02-01")

    Parameters
    ----------
    state : ``None`` or str
        [optional]

        If specified, results will be limited to the state corresponding to the
        given 2-character state code.

    climate_division : ``None`` or int
        [optional]

        If specified, results will be limited to the climate division.

    {start_date}

    {end_date}

    """
    tsutils._printiso(
        cpc(
            state=state,
            climate_division=climate_division,
            start_date=start_date,
            end_date=end_date,
        )
    )


def cpc(state=None, climate_division=None, start_date=None, end_date=None):
    r"""Access Climate Prediction Center, Weekly Drought Index dataset."""
    from tsgettoolbox.services import cpc

    df = cpc.ulmo_df(
        state=state,
        climate_division=climate_division,
        start_date=tsutils.parsedate(start_date),
        end_date=tsutils.parsedate(end_date),
    )
    return df


cpc.__doc__ = cpc_cli.__doc__
