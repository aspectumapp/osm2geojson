from .parse_xml import parse as parse_xml
from shapely import geometry, ops
import json


def json2geojson(data):
    if isinstance(data, str):
        data = json.loads(data)
    return _json2geojson(data)


def xml2geojson(xml_str):
    data = parse_xml(xml_str)
    return _json2geojson(data)


def _json2geojson(data):
    features = []

    nodes = []
    ways = []
    relations = []
    other = []

    for el in data['elements']:
        t = el['type']
        if t == 'node':
            nodes.append(el)
        elif t == 'way':
            ways.append(el)
        elif t == 'relation':
            relations.append(el)
        else:
            other.append(el)

    for node in nodes:
        features.append(node_to_feature(node))

    for rel in relations:
        features.append(relation_to_feature(rel))

    return {
        'type': 'FeatureCollection',
        'features': features
    }


def build_nodes_index(nodes):
    obj = {}
    for node in nodes:
        obj[node['id']] = node
    return obj


def node_to_feature(node):
    return {
        'type': 'Feature',
        'properties': {
            'type': 'node',
            'id': node['id'],
            'tags': node['tags']
        },
        'geometry': {
            'type': 'Point',
            'coordinates': [node['lon'], node['lat']]
        }
    }


def to_feature(g):
    return {
        "type": "Feature",
        'properties': {},
        "geometry": geometry.mapping(g)
    }


def multipolygon_to_feature(p):
    return to_feature(orient_multipolygon(p))


def orient_multipolygon(p):
    p = [geometry.polygon.orient(geom, sign=-1.0) for geom in p.geoms]
    return geometry.MultiPolygon(p)


def relation_to_feature(rel):
    geometry_type = 'LineString'
    if rel['tags']['type'] == 'boundary':
        geometry_type = 'Polygon'

    inner = []
    outer = []

    for member in rel['members']:
        if member['type'] != 'way':
            print('member not handled', member)
            continue

        coords = []
        for nd in member['geometry']:
            coords.append([nd['lon'], nd['lat']])
        way = geometry.shape({
            'type': 'LineString',
            'coordinates': coords
        })
        if member['role'] == 'inner':
            inner.append(way)
        else:
            outer.append(way)

    multipolygon = convert_ways_to_multipolygon(outer, inner)
    feature = multipolygon_to_feature(multipolygon)
    feature['properties'] = {
        'type': 'relation',
        'id': rel['id'],
        'tags': rel['tags']
    }
    return feature


def to_multipolygon(obj):
    if isinstance(obj, geometry.MultiPolygon):
        return obj

    if isinstance(obj, geometry.GeometryCollection):
        p = []
        for el in obj:
            if isinstance(el, geometry.Polygon):
                p.append(el)
        return geometry.MultiPolygon(p)

    if isinstance(obj, geometry.Polygon):
        return geometry.MultiPolygon([obj])

    # throw exception
    print('Failed to convert to multipolygon', type(obj))
    return None


def merge_polygons_to_multipolygon(polygons):
    merged = ops.cascaded_union(polygons)
    return to_multipolygon(merged)


def _convert_lines_to_multipolygon(lines):
    multi_line = geometry.MultiLineString(lines)
    merged_line = ops.linemerge(multi_line)
    if isinstance(merged_line, geometry.MultiLineString):
        polygons = []
        for line in merged_line:
            try:
                poly = geometry.Polygon(line)
                if poly.is_valid:
                    polygons.append(poly)
                else:
                    polygons.append(poly.buffer(0))
            except:
                # throw exception
                print('Failed to build polygon', line)
        return merge_polygons_to_multipolygon(polygons)
    return geometry.MultiPolygon([geometry.Polygon(merged_line)])


def convert_ways_to_multipolygon(outer, inner = []):
    if len(outer) < 1:
        # throw exception
        print('Ways not found')
        return None

    outer_polygon = _convert_lines_to_multipolygon(outer)
    if len(inner) < 1:
        return outer_polygon

    inner_polygon = _convert_lines_to_multipolygon(inner)
    return to_multipolygon(outer_polygon.difference(inner_polygon))
