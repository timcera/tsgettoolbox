"""
`National Climatic Data Center`_ `Climate Index Reference Sequential
(CIRS)`_ drought dataset

.. _National Climatic Data Center: http://www.ncdc.noaa.gov
.. _Climate Index Reference Sequential (CIRS): http://www1.ncdc.noaa.gov/pub/data/cirs/
"""

__all__ = ["get_data"]
# Local folder imports
from .core import get_data
