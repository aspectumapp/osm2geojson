import unittest
import codecs
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
        self.assertEqual(josm['version'], 0.6)
        self.assertEqual(josm['elements'], [])

    def test_map(self):
        """
        Test parsing of usual map
        """
        xml = read_data_file('map.osm')
        josm = parse_xml(xml)

        self.assertIsInstance(josm, dict)
        self.assertEqual(josm['version'], 0.6)
        print(josm)

if __name__ == '__main__':
    unittest.main()
