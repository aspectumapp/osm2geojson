# osm2geojson

Parse OSM and Overpass JSON with python.

### Usage

Install this package with pip:

```sh
$ pip install osm2geojson
```

If you want to convert OSM xml or Overpass json/xml to Geojson you can import this lib and use one of 2 methods:

 * `json2geojson` - to convert Overpass json to Geojson
 * `xml2geojson` - to convert OSM xml or Overpass xml to Geojson

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

Setup package

```sh
$ python setup.py develop
```

Run tests

```sh
$ python -m unittest discover
```
