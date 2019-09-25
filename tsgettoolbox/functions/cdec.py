import mando

try:
    from mando.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter

from tstoolbox import tsutils


@mando.command("cdec", formatter_class=HelpFormatter, doctype="numpy")
@tsutils.doc(tsutils.docstrings)
def cdec_cli(
    station_id, dur_code=None, sensor_num=None, start_date=None, end_date=None
):
    r"""Access data from the `California Department of Water Resources`.

    The web site is called the `California Data Exchange Center`.

    California Department of Water Resources: http://www.water.ca.gov/
    California Data Exchange Center: http://cdec.water.ca.gov

    Downloads data for a set of CDEC station and sensor ids. If either is not
    provided, all available data will be downloaded.

    Parameters
    ----------
    station_id: str
        [optional, default is None]

        Each string is the CDEC station ID and consist of three capital
        letters.

    sensor_num: integer, comma separated integers or ``None``
        [optional, default is None]

        If ``None`` will get all sensors at `station_id`.

        SELECTED CDEC SENSOR NUMBERS (these are not available for all
        sites):

        +------------+-------------------------------------------+
        | sensor_num | Description                               |
        +============+===========================================+
        | 1          | river stage [ft]                          |
        +------------+-------------------------------------------+
        | 2          | precipitation accumulated [in]            |
        +------------+-------------------------------------------+
        | 3          | SWE [in]                                  |
        +------------+-------------------------------------------+
        | 4          | air temperature [F]                       |
        +------------+-------------------------------------------+
        | 5          | EC [ms/cm]                                |
        +------------+-------------------------------------------+
        | 6          | reservoir elevation [ft]                  |
        +------------+-------------------------------------------+
        | 7          | reservoir scheduled release [cfs]         |
        +------------+-------------------------------------------+
        | 8          | full natural flow [cfs]                   |
        +------------+-------------------------------------------+
        | 15         | reservoir storage [af]                    |
        +------------+-------------------------------------------+
        | 20         | flow -- river discharge [cfs]             |
        +------------+-------------------------------------------+
        | 22         | reservoir storage change [af]             |
        +------------+-------------------------------------------+
        | 23         | reservoir outflow [cfs]                   |
        +------------+-------------------------------------------+
        | 24         | Evapotranspiration [in]                   |
        +------------+-------------------------------------------+
        | 25         | water temperature [F]                     |
        +------------+-------------------------------------------+
        | 27         | water turbidity [ntu]                     |
        +------------+-------------------------------------------+
        | 28         | chlorophyll [ug/l]                        |
        +------------+-------------------------------------------+
        | 41         | flow -- mean daily [cfs]                  |
        +------------+-------------------------------------------+
        | 45         | precipitation incremental [in]            |
        +------------+-------------------------------------------+
        | 46         | runoff volume [af]                        |
        +------------+-------------------------------------------+
        | 61         | water dissolved oxygen [mg/l]             |
        +------------+-------------------------------------------+
        | 62         | water pH value [pH]                       |
        +------------+-------------------------------------------+
        | 64         | pan evaporation (incremental) [in]        |
        +------------+-------------------------------------------+
        | 65         | full natural flow [af]                    |
        +------------+-------------------------------------------+
        | 66         | flow -- monthly volume [af]               |
        +------------+-------------------------------------------+
        | 67         | accretions (estimated) [af]               |
        +------------+-------------------------------------------+
        | 71         | spillway discharge [cfs]                  |
        +------------+-------------------------------------------+
        | 74         | lake evaporation (computed) [cfs]         |
        +------------+-------------------------------------------+
        | 76         | reservoir inflow [cfs]                    |
        +------------+-------------------------------------------+
        | 85         | control regulating discharge [cfs]        |
        +------------+-------------------------------------------+
        | 94         | top conservation storage (reservoir) [af] |
        +------------+-------------------------------------------+
        | 100        | water EC [us/cm]                          |
        +------------+-------------------------------------------+

    dur_code: str, comma separated strings, or ``None``
        [optional, default is None]

        Possible values are 'E', 'H', 'D', and 'M' but not
        all of these time resolutions are available at every station.

        +----------+-------------+
        | dur_code | Description |
        +==========+=============+
        | E        | event       |
        +----------+-------------+
        | H        | hourly      |
        +----------+-------------+
        | D        | daily       |
        +----------+-------------+
        | M        | monthly     |
        +----------+-------------+

    {start_date}

    {end_date}

    """
    tsutils._printiso(
        cdec(
            station_id,
            dur_code=dur_code,
            sensor_num=sensor_num,
            start_date=start_date,
            end_date=end_date,
        )
    )


def cdec(station_id, dur_code=None, sensor_num=None, start_date=None, end_date=None):
    r"""Access data from the `California Department of Water Resources`_."""
    from tsgettoolbox.services import cdec

    df = cdec.ulmo_df(
        station_id,
        dur_code=dur_code,
        sensor_num=sensor_num,
        start_date=tsutils.parsedate(start_date),
        end_date=tsutils.parsedate(end_date),
    )
    return df


cdec.__doc__ = cdec_cli.__doc__
