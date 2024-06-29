"""
`National Climatic Data Center`_ `Global Summary of the Day`_ dataset

.. _National Climatic Data Center: http://www.ncdc.noaa.gov
.. _Global Summary of the Day: http://www.ncdc.noaa.gov/oa/gsod.html
"""

__all__ = ["get_data", "get_stations"]
from .core import get_data, get_stations
