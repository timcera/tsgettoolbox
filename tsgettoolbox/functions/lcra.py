import mando

try:
    from mando.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter

from tstoolbox import tsutils


@mando.command("lcra_hydromet", formatter_class=HelpFormatter, doctype="numpy")
@tsutils.doc(tsutils.docstrings)
def lcra_hydromet_cli(
    site_code, parameter_code, start_date=None, end_date=None, dam_site_location="head"
):
    r"""Hydrometeorologic data from the Lower Colorado River Authority.

    This module provides access to hydrologic and climate data in the Colorado
    River Basin (Texas) provided by the Lower Colorado River Authority Hydromet
    web site and web service.

    http://www.lcra.org

    http://hydromet.lcra.org

    Parameters
    ----------
    site_code
        The LCRA site code (four chars long) of the site you want to query data
        for.
    parameter_code
        LCRA parameter
        code.

        +----------------+---------------------------------------+
        | parameter_code | Description                           |
        +----------------+---------------------------------------+
        | stage          | the level of water above a benchmark  |
        |                | in feet                               |
        +----------------+---------------------------------------+
        | flow           | streamflow in cubic feet per second   |
        +----------------+---------------------------------------+
        | pc             | precipitation in inches               |
        +----------------+---------------------------------------+
        | temp           | air temperature in degrees fahrenheit |
        +----------------+---------------------------------------+
        | rhumid         | air relative humidity as percentage   |
        +----------------+---------------------------------------+
        | cndvty         | water electrical conductivity in      |
        |                | micromhos                             |
        +----------------+---------------------------------------+
        | tds            | total suspended solids                |
        +----------------+---------------------------------------+
        | windsp         | wind speed miles per hour             |
        +----------------+---------------------------------------+
        | winddir        | wind direction in degrees azimuth     |
        +----------------+---------------------------------------+
        | upperbasin     | ALL Upper Basin flow and water levels |
        +----------------+---------------------------------------+
        | lowerbasin     | ALL Lower Basin flow and water levels |
        +----------------+---------------------------------------+

    {start_date}
    {end_date}
    dam_site_location : str
        'head' (default) or 'tail'
        The site location relative to the dam.  Not used for `upperbasin`
        and `lowerbasin` parameters.
    """
    tsutils._printiso(
        lcra_hydromet(
            site_code,
            parameter_code,
            start_date=start_date,
            end_date=end_date,
            dam_site_location=dam_site_location,
        )
    )


def lcra_hydromet(
    site_code, parameter_code, start_date=None, end_date=None, dam_site_location="head"
):
    r"""Hydrometeorologic data from the Lower Colorado River Authority."""
    from tsgettoolbox.services.lcra import hydromet

    df = hydromet.ulmo_df(
        site_code,
        parameter_code,
        start_date=start_date,
        end_date=end_date,
        dam_site_location=dam_site_location,
    )

    return df


@mando.command("lcra_wq", formatter_class=HelpFormatter, doctype="numpy")
@tsutils.doc(tsutils.docstrings)
def lcra_wq_cli(site_code, historical=True, start_date=None, end_date=None):
    r"""Access data from the Lower Colorado River Authority Water Quality.

    Fetches historical or near real-time (for some sites) data.

    Lower Colorado River Authority: http://www.lcra.org

    Water Quality: http://waterquality.lcra.org/

    Parameters
    ----------
    site_code
        The site code to fetch data for. The following bay sites also have near
        real-time data available if `historical` option is set to False.

        +--------------------+-----------------+
        | Near Real-Time     | Name            |
        | (historical=False) |                 |
        | site_code          |                 |
        +====================+=================+
        | 6977               | Matagorda 4SSW  |
        +--------------------+-----------------+
        | 6985               | Matagorda 7 SW  |
        +--------------------+-----------------+
        | 6990               | Matagorda 8 SSW |
        +--------------------+-----------------+
        | 6996               | Matagorda 9 SW  |
        +--------------------+-----------------+

    historical
        Flag to indicate whether to get historical or near real-time data from
        the bay sites.
    {start_date}
    {end_date}"""
    tsutils._printiso(
        lcra_wq(site_code, historical=historical, start_date=start_date, end_date=None)
    )


def lcra_wq(site_code, historical=True, start_date=None, end_date=None):
    r"""Access data from the Lower Colorado River Authority Water Quality."""
    from tsgettoolbox.services.lcra import wq

    df = wq.ulmo_df(
        site_code=site_code,
        historical=historical,
        start_date=start_date,
        end_date=end_date,
    )

    return df


lcra_hydromet.__doc__ = lcra_hydromet_cli.__doc__
lcra_wq.__doc__ = lcra_wq_cli.__doc__
