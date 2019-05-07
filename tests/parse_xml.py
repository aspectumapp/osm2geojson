import unittest
import codecs
import json
import os

from osm2geojson.parse_xml import parse as parse_xml

dirname = os.path.dirname(__file__)

def read_data_file(name):
    path = os.path.join(dirname, 'data', name)
    with codecs.open(path, 'r', encoding='utf-8') as data:
        return data.read()

class TestParseXmlMethods(unittest.TestCase):
    def test_empty_tag(self):
        """
        Test parsing of empty <osm> tag
        """
        xml = read_data_file('empty.osm')
        josm = parse_xml(xml)

        self.assertIsInstance(josm, dict)
        # Use version 0.6 as default
        self.assertEqual(josm['version'], 0.6)
        self.assertEqual(josm['elements'], [])

    def test_node(self):
        """
        Test parsing node
        """
        xml = read_data_file('node.osm')
        josm = parse_xml(xml)

        self.assertIsInstance(josm, dict)
        self.assertIsInstance(josm['elements'], list)
        self.assertEqual(len(josm['elements']), 1)

        node = josm['elements'][0]
        self.assertIsInstance(node, dict)
        self.assertEqual(node['type'], 'node')
        self.assertEqual(node['id'], 1)
        self.assertAlmostEqual(node['lat'], 1.234)
        self.assertAlmostEqual(node['lon'], 4.321)

    def test_way(self):
        """
        Test parsing way
        """
        xml = read_data_file('way.osm')
        josm = parse_xml(xml)

        self.assertIsInstance(josm, dict)
        self.assertIsInstance(josm['elements'], list)
        self.assertEqual(len(josm['elements']), 4)

        way = josm['elements'][0]

        self.assertIsInstance(way, dict)
        self.assertEqual(way['type'], 'way')
        self.assertEqual(way['id'], 1)
        self.assertIsInstance(way['nodes'], list)
        self.assertEqual(way['nodes'], [2, 3, 4])

    def test_relation(self):
        """
        Test parsing relation
        """
        xml = read_data_file('relation.osm')
        josm = parse_xml(xml)

        self.assertIsInstance(josm, dict)
        self.assertIsInstance(josm['elements'], list)
        self.assertEqual(len(josm['elements']), 10)

        relation = josm['elements'][0]

        self.assertIsInstance(relation, dict)
        self.assertEqual(relation['type'], 'relation')
        self.assertEqual(relation['id'], 1)
        self.assertIsInstance(relation['members'], list)
        self.assertEqual(len(relation['members']), 2)
        self.assertEqual(relation['tags'], { 'type': 'multipolygon' })

    def test_map(self):
        """
        Test parsing of usual map
        """
        xml = read_data_file('map.osm')
        josm = parse_xml(xml)

        self.assertIsInstance(josm, dict)
        self.assertEqual(josm['version'], 0.6)

    def test_all_files(self):
        """
        Test parsing of all files and compare with json version
        """
        self.maxDiff = None
        for name in ['empty', 'node', 'way', 'map', 'relation']:
            xml_data = read_data_file(name + '.osm')
            json_data = read_data_file(name + '.json')
            josm_xml = parse_xml(xml_data)
            josm_json = json.loads(json_data)

            if 'version' not in josm_json:
                del josm_xml['version']

            self.assertDictEqual(josm_json, josm_xml)

if __name__ == '__main__':
    unittest.main()
