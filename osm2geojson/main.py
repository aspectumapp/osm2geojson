from .parse_xml import parse as parse_xml
from shapely import geometry, ops
import json
import os

dirname = os.path.dirname(__file__)
polygon_features_file = os.path.join(dirname, './polygon-features.json')

with open(polygon_features_file) as data:
    polygon_features = json.loads(data.read())


def json2geojson(data):
    if isinstance(data, str):
        data = json.loads(data)
    return _json2geojson(data)


def xml2geojson(xml_str):
    data = parse_xml(xml_str)
    return _json2geojson(data)


def _json2geojson(data):
    features = []

    refs = []
    for el in data['elements']:
        if el['type'] in ['node', 'way']:
            refs.append(el)
    refs_index = build_refs_index(refs)

    for el in data['elements']:
        feature = element_to_feature(el, refs_index)
        if feature is not None:
            features.append(feature)
        else:
            print('Element not converted', el)

    used = {}
    for ref in refs:
        if 'used' in ref:
            used[ref['id']] = ref['used']

    filtered_features = []
    for f in features:
        if f['properties']['id'] in used:
            continue
        filtered_features.append(f)

    return {
        'type': 'FeatureCollection',
        'features': filtered_features
    }


def element_to_feature(el, refs_index = None):
    t = el['type']
    if t == 'node':
        return node_to_feature(el)
    if t == 'way':
        return way_to_feature(el, refs_index)
    if t == 'relation':
        return relation_to_feature(el, refs_index)
    return None


def build_refs_index(elements):
    obj = {}
    for el in elements:
        obj[el['id']] = el
    return obj


def node_to_feature(node):
    feature = to_feature({
        'type': 'Point',
        'coordinates': [node['lon'], node['lat']]
    })
    feature['properties'] = get_element_props(node)
    return feature


def get_element_props(el, keys = ['type', 'id', 'tags']):
    props = {}
    for key in keys:
        if key in el:
            props[key] = el[key]
    return props


def convert_coords_to_lists(coords):
    if len(coords) < 0:
        return []

    if isinstance(coords[0], float):
        return list(coords)

    new_coords = list()
    for c in coords:
        new_coords.append(convert_coords_to_lists(c))
    return new_coords


def to_feature(g, props = {}):
    # shapely returns tuples (we need lists)
    g['coordinates'] = convert_coords_to_lists(g['coordinates'])
    return {
        "type": "Feature",
        'properties': props,
        "geometry": g
    }


def shape_to_feature(g, props = {}):
    return to_feature(geometry.mapping(g), props)


def multipolygon_to_feature(p, props = {}):
    return shape_to_feature(orient_multipolygon(p), props)


def orient_multipolygon(p):
    p = [geometry.polygon.orient(geom, sign=-1.0) for geom in p.geoms]
    return geometry.MultiPolygon(p)


def way_to_feature(way, refs_index = {}, force_polygon = False):
    coords = []

    if 'geometry' in way and len(way['geometry']) > 0:
        for nd in way['geometry']:
            coords.append([nd['lon'], nd['lat']])

    elif 'nodes' in way and len(way['nodes']) > 0:
        for ref in way['nodes']:
            if ref in refs_index:
                node = refs_index[ref]
                node['used'] = way['id']
                coords.append([node['lon'], node['lat']])
            else:
                print('Node not found in index', ref, 'for way', way)

    elif 'ref' in way:
        if way['ref'] not in refs_index:
            print('Ref for way not found in index', way)
            return None

        ref = refs_index[way['ref']]
        if 'id' in way:
            ref['used'] = way['id']
        elif 'used' in way:
            ref['used'] = way['used']
        else:
            # filter will not work for this situation
            print('Failed to mark ref as used', ref, 'for way', way)
        ref_way = way_to_feature(ref, refs_index)
        if ref_way is None:
            print('Way by ref not converted to feature', way)
            return None
        if ref_way['geometry']['type'] is 'Polygon':
            coords = ref_way['geometry']['coordinates'][0]
        else:
            coords = ref_way['geometry']['coordinates']

    else:
        # throw exception
        print('Relation has way without nodes', way)
        return None

    if len(coords) < 2:
        print('Not found coords for way', way)
        return None

    if force_polygon or is_geometry_polygon(way):
        f = geometry.mapping(geometry.Polygon(coords))
        return to_feature(f, get_element_props(way))
    else:
        return to_feature({
            'type': 'LineString',
            'coordinates': coords
        }, get_element_props(way))


def is_geometry_polygon(node):
    if 'tags' not in node:
        return False
    tags = node['tags']

    if 'type' in tags and tags['type'] == 'multipolygon':
        return True

    for rule in polygon_features:
        if rule['key'] in tags:
            if rule['polygon'] == 'all':
                return True
            if rule['polygon'] == 'whitelist' and tags[rule['key']] in rule['values']:
                return True
            if rule['polygon'] == 'blacklist':
                if tags[rule['key']] in rule['values']:
                    return False
                else:
                    return True
    return False


def relation_to_feature(rel, refs_index):
    if is_geometry_polygon(rel):
        return multipolygon_relation_to_feature(rel, refs_index)
    else:
        return multiline_realation_to_feature(rel, refs_index)


def multiline_realation_to_feature(rel, refs_index):
    lines = []
    for member in rel['members']:
        if member['type'] != 'way':
            print('member not handled', member)
            continue

        way_feature = way_to_feature(member, refs_index)
        if way_feature is None:
            # throw exception
            print('Failed to make way in relation', rel)
            continue

        way = geometry.shape(way_feature['geometry'])
        if isinstance(way, geometry.Polygon):
            # this should not happen on real data
            way = geometry.LineString(way.exterior.coords)
        lines.append(way)
    if len(lines) < 1:
        return None

    multiline = geometry.MultiLineString(lines)
    multiline = ops.linemerge(multiline)
    return shape_to_feature(multiline, get_element_props(rel))


def multipolygon_relation_to_feature(rel, refs_index):
    inner = []
    outer = []

    for member in rel['members']:
        if member['type'] != 'way':
            print('member not handled', member)
            continue

        member['used'] = rel['id']

        way_feature = way_to_feature(member, refs_index, True)
        if way_feature is None:
            # throw exception
            print('Failed to make way', member, 'in relation', rel)
            continue

        way = geometry.shape(way_feature['geometry'])
        if isinstance(way, geometry.Polygon):
            way = geometry.LineString(way.exterior.coords)

        if member['role'] == 'inner':
            inner.append(way)
        else:
            outer.append(way)

    multipolygon = convert_ways_to_multipolygon(outer, inner)
    if multipolygon is None:
        print('Relation not converted to feature', rel)
        return None
    return multipolygon_to_feature(multipolygon, get_element_props(rel))


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
