import unittest
import json
import os

from .parse_xml import read_data_file
from osm2geojson import overpass_call, xml2geojson

class TestOsm2GeoJsonMethods(unittest.TestCase):
    def test_files_convertation(self):
        """
        Test how xml2geojson converts saved files
        """
        for name in ['empty', 'node', 'way', 'relation']:
            xml_data = read_data_file(name + '.osm')
            geojson_data = read_data_file(name + '.geojson')
            data = xml2geojson(xml_data)
            saved_geojson = json.loads(geojson_data)
            self.assertDictEqual(saved_geojson, data)

    def test_parsing_from_overpass(self):
        """
        Test city border convertation to MultiPolygon
        """
        xml = overpass_call('rel(448930); out geom;')
        data = xml2geojson(xml)
        self.assertEqual(len(data['features']), 1)
