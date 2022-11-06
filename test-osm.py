import osm2geojson
import codecs
import json
import os

dirname = '/Users/rapkin/dev/osm2geojson'

def read_data_file(name):
    path = os.path.join(dirname, 'tests/data', name)
    with codecs.open(path, 'r', encoding='utf-8') as data:
        return data.read()

def get_osm_and_geojson_data(name):
    xml_data = read_data_file(name + '.osm')
    geojson_data = read_data_file(name + '.geojson')
    data = osm2geojson.xml2geojson(xml_data, log_level='INFO')
    saved_geojson = json.loads(geojson_data)
    return (data, saved_geojson)


# (data, saved_geojson) = get_osm_and_geojson_data('relation')
# print(data)

josn = osm2geojson.overpass_call('[out:json];rel(id:1741311);out geom;')
data = osm2geojson.json2geojson(josn, log_level='INFO')

f = open("serbia.json", "w")
f.write(json.dumps(json.loads(josn), indent=2))
f.close()

f = open("serbia.geojson", "w")
f.write(json.dumps(data, indent=2))
f.close()
