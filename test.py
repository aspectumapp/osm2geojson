from osm2geojson import overpass_call, xml2geojson
import json

xml = overpass_call('rel(448930); out geom;')
geojson = xml2geojson(xml)
print(json.dumps(geojson))
