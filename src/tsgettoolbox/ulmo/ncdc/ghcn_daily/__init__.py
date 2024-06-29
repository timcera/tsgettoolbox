"""
`National Climatic Data Center`_ `Global Historical Climate Network -
Daily`_ dataset

.. _National Climatic Data Center: http://www.ncdc.noaa.gov
.. _Global Historical Climate Network - Daily: http://www.ncdc.noaa.gov/oa/climate/ghcn-daily/
"""

__all__ = ["get_data", "get_stations"]
from .core import get_data, get_stations
