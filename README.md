# osm2geojson

Parse OSM and Overpass JSON with python.
__This library is under development!__

### Usage

Install this package with pip:

```sh
$ pip install osm2geojson
```

If you want to convert OSM xml or Overpass json/xml to Geojson you can import this lib and use one of 2 methods:

 * `json2geojson(dict json_from_overpass)` - to convert Overpass json to Geojson
 * `xml2geojson(str xml_from_osm)` - to convert OSM xml or Overpass xml to Geojson

__Example:__

```py
import codecs
import osm2geojson

with codecs.open('file.osm', 'r', encoding='utf-8') as data:
    xml = data.read()

geojson = osm2geojson.xml2geojson(xml)
# >> { "type": "FeatureCollection", "features": [ ... ] }
```

### Development

Clone project with submodules

```sh
$ git clone --recurse-submodules https://github.com/eos-vision/osm2geojson.git
```

Setup package

```sh
$ python setup.py develop
```

Run tests

```sh
$ python -m unittest discover
```

Update osm-polygon-features to last version (if you want last version)

```sh
$ ./update-osm-polygon-features.sh
```
