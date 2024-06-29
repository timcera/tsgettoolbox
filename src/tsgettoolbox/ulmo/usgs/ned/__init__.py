"""
`National Elevation Dataset (NED)`_ services (Raster)

.. _National Elevation Dataset (NED): http://ned.usgs.gov
"""

__all__ = ["get_available_layers", "get_raster", "get_raster_availability"]

from .core import get_available_layers, get_raster, get_raster_availability
