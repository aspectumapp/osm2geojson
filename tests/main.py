import unittest
import json
import os

from .parse_xml import read_data_file
from osm2geojson import overpass_call, xml2geojson, json2geojson

def get_osm_and_geojson_data(name):
    xml_data = read_data_file(name + '.osm')
    geojson_data = read_data_file(name + '.geojson')
    data = xml2geojson(xml_data)
    saved_geojson = json.loads(geojson_data)
    return (data, saved_geojson)

def get_json_and_geojson_data(name):
    json_data = read_data_file(name + '.json')
    geojson_data = read_data_file(name + '.geojson')
    data = json.loads(json_data)
    saved_geojson = json.loads(geojson_data)
    return (data, saved_geojson)

class TestOsm2GeoJsonMethods(unittest.TestCase):
    def test_files_convertation(self):
        """
        Test how xml2geojson converts saved files
        """
        for name in ['empty', 'node', 'way', 'relation', 'map']:
            (data, saved_geojson) = get_osm_and_geojson_data(name)
            self.assertDictEqual(saved_geojson, data)

    def test_parsing_from_overpass(self):
        """
        Test city border convertation to MultiPolygon
        """
        xml = overpass_call('rel(448930); out geom;')
        data = xml2geojson(xml)
        self.assertEqual(len(data['features']), 1)

    def test_issue_4(self):
        (data, saved_geojson) = get_osm_and_geojson_data('issue-4')
        self.assertDictEqual(saved_geojson, data)

    def test_issue_6(self):
        (data, saved_geojson) = get_json_and_geojson_data('issue-6')
        self.assertDictEqual(saved_geojson, json2geojson(data))

    def test_issue_7(self):
        (data, saved_geojson) = get_json_and_geojson_data('issue-7')
        self.assertDictEqual(saved_geojson, json2geojson(data))

if __name__ == '__main__':
    unittest.main()
