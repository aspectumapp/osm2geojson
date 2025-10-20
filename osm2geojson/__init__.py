"""osm2geojson - Parse OSM and Overpass JSON with Python.

This library provides functions to convert OpenStreetMap (OSM) data
and Overpass API responses into GeoJSON format.

Main functions:
- xml2geojson: Convert OSM XML to GeoJSON
- json2geojson: Convert Overpass JSON to GeoJSON
- xml2shapes: Convert OSM XML to Shape objects
- json2shapes: Convert Overpass JSON to Shape objects
- shape_to_feature: Convert a Shape object to a GeoJSON Feature
"""

from .helpers import overpass_call, read_data_file
from .main import json2geojson, json2shapes, shape_to_feature, xml2geojson, xml2shapes
from .parse_xml import parse as parse_xml


__version__ = "0.2.9"
__all__ = [
    "json2geojson",
    "json2shapes",
    "overpass_call",
    "parse_xml",
    "read_data_file",
    "shape_to_feature",
    "xml2geojson",
    "xml2shapes",
]
