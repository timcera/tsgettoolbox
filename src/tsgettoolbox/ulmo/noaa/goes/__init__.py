"""
NOAA `GOES Data Collection System`_
Access to data stream transmitted via GOES satellite.

.. _GOES Data Collection System: https://www.noaasis.noaa.gov/GOES/GOES_DCS/goes_dcs.html
"""

__all__ = ["decode", "get_data"]
from .core import decode, get_data
