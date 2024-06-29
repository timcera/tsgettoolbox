"""
Access to data provided by the `United States Army
Corps of Engineers`_ - `Tulsa District Water Control`_ web site.

.. _United States Army Corps of Engineers: http://www.usace.army.mil/
.. _Tulsa District Water Control: http://www.swt-wc.usace.army.mil/
"""

__all__ = ["get_station_data", "get_stations"]
from .core import get_station_data, get_stations
