"""
cpc                 US/region W: Climate Prediction Center, Weekly Drought
                    Index
"""

from typing import Optional

from tsgettoolbox.toolbox_utils.src.toolbox_utils import tsutils

__all__ = ["cpc"]


@tsutils.doc(tsutils.docstrings)
def cpc(
    state: Optional[str] = None,
    climate_division: Optional[int] = None,
    start_date=None,
    end_date=None,
):
    r"""DISCONTINUED US:region::W:Climate Prediction Center, Weekly Drought Index

    DISCONTINUED: The CPC Drought Index data source has been discontinued by
                  the CPC.

    Climate Prediction Center:

        www.cpc.ncep.noaa.gov

    Weekly Drought Index:

        www.cpc.ncep.noaa.gov/products/analysis_monitoring/cdus/palmer_drought

    The `climate_division` integer value identifies a portion of the
    desired `state` divided along county boundaries. Maps of the climate
    divisions within each state are at:

    www.cpc.ncep.noaa.gov/products/analysis_monitoring/regional_monitoring/CLIM_DIVS/states_counties_climate-divisions.shtml

    The only way to get a time-series is to specify both `state` and
    `climate_division` keywords.

    Command Line ::

        tsgettoolbox cpc --state=FL --climate_division=1 --start_date 2017-01-01

    Python API ::

        df = tsgettoolbox.cpc(state="FL",
                              climate_division=1,
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

    ${start_date}

    ${end_date}
    """
    raise NotImplementedError("""
        The CPC Drought Index data source has been discontinued by the CPC.

        You can use the tsgettoolbox "metdata", "ncei", or "terraclimate"
        functions to get the Palmer Drought Severity Index (PDSI).
        """)
