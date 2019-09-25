import mando

try:
    from mando.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter

from tstoolbox import tsutils


@mando.command("usgs_eddn", formatter_class=HelpFormatter, doctype="numpy")
@tsutils.doc(tsutils.docstrings)
def usgs_eddn_cli(dcp_address, parser, start_date=None, end_date=None):
    r"""Download from the USGS Emergency Data Distribution Network.

    This module provides access to data provided by the United States
    Geological Survey Emergency Data Distribution Network web site.

    The DCP message format includes some header information that is parsed and
    the message body, with a variable number of characters. The format of the
    message body varies widely depending on the manufacturer of the
    transmitter, data logger, sensors, and the technician who programmed the
    DCP. The body can be simple ASCII, sometime with parameter codes and
    time-stamps embedded, sometimes not. The body can also be in
    'Pseudo-Binary' which is character encoding of binary data that uses 6 bits
    of every byte and guarantees that all characters are printable.

    United States Geological Survey: http://www.usgs.gov/
    Emergency Data Distribution Network: http://eddn.usgs.gov/
    http://eddn.usgs.gov/dcpformat.html

    Fetches GOES Satellite DCP messages from USGS Emergency Data Distribution
    Network.

    Parameters
    ----------
    dcp_address
        DCP address or list of DCP addresses to be fetched; lists will be
        joined by a ','.

    parser
        Function that acts on dcp_message, where each row of the dataframe is
        processed and returns a new dataframe containing several rows of
        decoded data. This returned dataframe may have different (but derived)
        timestamps than that the original row. If a string is passed then
        a matching parser function is looked up from ulmo.usgs.eddn.parser.
        The prebuilt functions are "twdb_dot", "twdb_stevens", "twdb_sutron",
        and "twdb_texuni".

    {start_date}

    {end_date}
    """
    tsutils._printiso(
        usgs_eddn(dcp_address, parser, start_date=start_date, end_date=end_date)
    )


def usgs_eddn(dcp_address, parser, start_date=None, end_date=None):
    r"""Download from the USGS Emergency Data Distribution Network."""
    from tsgettoolbox.services.usgs import eddn

    df = eddn.ulmo_df(
        dcp_address=dcp_address, parser=parser, start_date=start_date, end_date=end_date
    )

    return df


usgs_eddn.__doc__ = usgs_eddn_cli.__doc__
