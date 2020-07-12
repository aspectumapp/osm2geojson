# osm2geojson

![Test package](https://github.com/aspectumapp/osm2geojson/workflows/Test%20package/badge.svg)

Parse OSM and Overpass JSON with python.
**This library is under development!**

### Usage

Install this package with pip:

```sh
$ pip install osm2geojson
```

If you want to convert OSM xml or Overpass json/xml to Geojson you can import this lib and use one of 4 methods:

- `json2shapes(dict json_from_overpass)` - to convert Overpass json to \*Shape-objects
- `xml2shapes(str xml_from_osm)` - to convert OSM xml or Overpass xml to \*Shape-objects
- `json2geojson(dict json_from_overpass)` - to convert Overpass json to Geojson
- `xml2geojson(str xml_from_osm)` - to convert OSM xml or Overpass xml to Geojson

Additional parameters for all functions:

- `filter_used_refs` - (default: `True`) defines geometry filtration strategy (will return all geometry if set as `False`)
- `log_level` - (default: `'ERROR'`) controlls logging level (will print all logs if set as `'INFO'`). More details [here](https://docs.python.org/3/library/logging.html#logging-levels)

Other handy methods:

- `overpass_call(str query)` - runs query to overpass-api.de server (retries 5 times in case of error).
- `shape_to_feature(Shape shape, dict properties)` - Converts Shape-object to GeoJSON with passed properties.

**\*Shape-object - for convinience created simple dict to save Shapely object (geometry) and OSM-properties. Structure of this object:**

```py
shape_obj = {
    'shape': Point | LineString | Polygon ...,
    'properties': {
        'type': 'relation' | 'node' ...,
        'tags': { ... },
        ...
    }
}
```

### Examples

Convert OSM-xml to Geojson:

```py
import codecs
import osm2geojson

with codecs.open('file.osm', 'r', encoding='utf-8') as data:
    xml = data.read()

geojson = osm2geojson.xml2geojson(xml, filter_used_refs=False, log_level='INFO')
# >> { "type": "FeatureCollection", "features": [ ... ] }
```

Convert OSM-json to Shape-objects:

```py
import codecs
import osm2geojson

with codecs.open('file.json', 'r', encoding='utf-8') as data:
    json = data.read()

shapes_with_props = osm2geojson.json2shapes(json)
# >> [ { "shape": <Shapely-object>, "properties": {...} }, ... ]
```

### Development

Clone project with submodules

```sh
$ git clone --recurse-submodules https://github.com/aspectumapp/osm2geojson.git
```

Setup package

```sh
$ python setup.py develop
```

Run tests

```sh
$ python -m unittest tests
```

Run single test

```sh
$ python tests/main.py TestOsm2GeoJsonMethods.test_barrier_wall
```

Update osm-polygon-features to last version (if you want last version)

```sh
$ ./update-osm-polygon-features.sh
```
