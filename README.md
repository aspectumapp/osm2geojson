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
- `log_level` - (default: `'ERROR'`) controls logging level (will print all logs if set as `'INFO'`). More details [here](https://docs.python.org/3/library/logging.html#logging-levels)
- `area_keys` - (default: `None`) defines which keys and values of an area should be saved from the list of OSM tags, see `areaKeys.json` for the defaults
- `polygon_features` - (default: `None`) defines a whitelist/blacklist of features to be included in resulting polygons, see `polygon-features.json` for the defaults
- `raise_on_failure` - (default: `False`) controls whether to throw an exception when geometry generation fails

Other handy methods:

- `overpass_call(str query)` - runs query to overpass-api.de server (retries 5 times in case of error).
- `shape_to_feature(Shape shape, dict properties)` - Converts Shape-object to GeoJSON with passed properties.

**\*Shape-object - for convenience created simple dict to save Shapely object (geometry) and OSM-properties. Structure of this object:**

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

After installing via `pip`, the module may also be used as a `argparse`-based command-line script.
Either use the script name directly or call Python with the `-m` option and the package name:

```sh
osm2geojson --help
```

```sh
python3 -m osm2geojson --help
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

### ToDo

 * Add tests and examples for cli tool
 * Add actions related to cli tool (more info https://github.com/aspectumapp/osm2geojson/pull/32#issuecomment-1073386381)
