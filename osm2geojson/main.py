from .parse_xml import parse as parse_xml
from shapely.ops import cascaded_union, linemerge
from shapely.geometry import (
    mapping, Polygon, Point, LineString, MultiLineString, MultiPolygon, GeometryCollection
)
from shapely.geometry.polygon import orient
import traceback
import json
import os

dirname = os.path.dirname(__file__)
polygon_features_file = os.path.join(dirname, 'polygon-features.json')
area_keys_file = os.path.join(dirname, 'areaKeys.json')

with open(polygon_features_file) as data:
    polygon_features = json.loads(data.read())

with open(area_keys_file) as data:
    area_keys = json.loads(data.read())['areaKeys']

def json2geojson(data, filter_used_refs=True):
    if isinstance(data, str):
        data = json.loads(data)
    return _json2geojson(data, filter_used_refs)


def xml2geojson(xml_str, filter_used_refs=True):
    data = parse_xml(xml_str)
    return _json2geojson(data, filter_used_refs)


def json2shapes(data, filter_used_refs=True):
    if isinstance(data, str):
        data = json.loads(data)
    return _json2shapes(data, filter_used_refs)


def xml2shapes(xml_str, filter_used_refs=True):
    data = parse_xml(xml_str)
    return _json2shapes(data, filter_used_refs)


def _json2geojson(data, filter_used_refs=True):
    features = []
    for shape in _json2shapes(data, filter_used_refs):
        feature = shape_to_feature(shape['shape'], shape['properties'])
        features.append(feature)

    return {
        'type': 'FeatureCollection',
        'features': features
    }


def _json2shapes(data, filter_used_refs=True):
    shapes = []

    refs = []
    for el in data['elements']:
        if el['type'] in ['node', 'way', 'relation']:
            refs.append(el)
    refs_index = build_refs_index(refs)

    for el in data['elements']:
        shape = element_to_shape(el, refs_index)
        if shape is not None:
            shapes.append(shape)
        else:
            print('Element not converted', el)

    if not filter_used_refs:
        return shapes

    used = {}
    for ref in refs:
        if 'used' in ref:
            used[ref['id']] = ref['used']

    filtered_shapes = []
    for shape in shapes:
        if 'properties' not in shape:
            print(shape)
        if shape['properties']['id'] in used:
            continue
        filtered_shapes.append(shape)

    return filtered_shapes


def element_to_shape(el, refs_index = None):
    t = el['type']
    if t == 'node':
        return node_to_shape(el)
    if t == 'way':
        return way_to_shape(el, refs_index)
    if t == 'relation':
        return relation_to_shape(el, refs_index)
    return None


def build_refs_index(elements):
    obj = {}
    for el in elements:
        obj[el['id']] = el
    return obj


def node_to_shape(node):
    return {
        'shape': Point(node['lon'], node['lat']),
        'properties': get_element_props(node)
    }


def get_element_props(el, keys = ['type', 'id', 'tags']):
    props = {}
    for key in keys:
        if key in el:
            props[key] = el[key]
    return props


def convert_coords_to_lists(coords):
    new_coords = list()
    if len(coords) < 1:
        return new_coords

    if isinstance(coords[0], float):
        return list(coords)

    for c in coords:
        new_coords.append(convert_coords_to_lists(c))
    return new_coords


def shape_to_feature(g, props = {}):
    # shapely returns tuples (we need lists)
    g =  mapping(g)
    g['coordinates'] = convert_coords_to_lists(g['coordinates'])
    return {
        "type": "Feature",
        'properties': props,
        "geometry":g
    }


def orient_multipolygon(p):
    p = [orient(geom, sign=-1.0) for geom in p.geoms]
    return MultiPolygon(p)


def fix_invalid_polygon(p):
    if not p.is_valid:
        print('Invalid geometry! Try to fix with 0 buffer')
        p = p.buffer(0)
        if p.is_valid:
            print('Geometry fixed!')
    return p


def way_to_shape(way, refs_index = {}):
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
                return None

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
        ref_way = way_to_shape(ref, refs_index)
        if ref_way is None:
            print('Way by ref not converted to shape', way)
            return None
        if isinstance(ref_way['shape'], Polygon):
            coords = ref_way['shape'].exterior.coords
        else:
            coords = ref_way['shape'].coords

    else:
        # throw exception
        print('Relation has way without nodes', way)
        return None

    if len(coords) < 2:
        print('Not found coords for way', way)
        return None

    props = get_element_props(way)
    if is_geometry_polygon(way):
        try:
            poly = fix_invalid_polygon(Polygon(coords))
            return {
                'shape': poly,
                'properties': props
            }
        except:
            print('Failed to generate polygon from way', way)
            return None
    else:
        return {
            'shape': LineString(coords),
            'properties': props
        }


def is_exception(node):
    for tag in node['tags']:
        if tag in area_keys:
            value = node['tags'][tag]
            return value in area_keys[tag] and area_keys[tag][value]
    return False


def is_same_coords(a, b):
    return a['lat'] == b['lat'] and a['lon'] == b['lon']


def is_geometry_polygon(node):
    if 'tags' not in node:
        return False
    tags = node['tags']

    if 'area' in tags and tags['area'] == 'no':
        return False

    if 'area' in tags and tags['area'] == 'yes':
        return True

    if 'type' in tags and tags['type'] == 'multipolygon':
        return True

    # Fix for issue #7, but should be handled by id-area-keys or osm-polygon-features
    # For example https://github.com/tyrasd/osm-polygon-features/issues/5
    if 'geometry' in node and not is_same_coords(node['geometry'][0], node['geometry'][-1]):
        return False

    # For issue #7 and situation with barrier=wall
    if 'nodes' in node and node['nodes'][0] != node['nodes'][-1]:
        return False

    is_polygon = is_geometry_polygon_without_exceptions(node)
    if is_polygon:
        return not is_exception(node)
    else:
        return False

def is_geometry_polygon_without_exceptions(node):
    tags = node['tags']
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


def relation_to_shape(rel, refs_index):
    if is_geometry_polygon(rel):
        return multipolygon_relation_to_shape(rel, refs_index)
    else:
        return multiline_realation_to_shape(rel, refs_index)


def multiline_realation_to_shape(rel, refs_index):
    lines = []

    if 'members' in rel:
        members = rel['members']
    else:
        members = refs_index[rel['ref']]['members']

    for member in members:
        if member['type'] == 'way':
            way_shape = way_to_shape(member, refs_index)
        elif member['type'] == 'relation':
            refs_index[member['ref']]['used'] = rel['id']
            way_shape = element_to_shape(member, refs_index)
        else:
            print('multiline member not handled', member)
            continue

        if way_shape is None:
            # throw exception
            print('Failed to make way in relation', rel)
            continue

        if isinstance(way_shape['shape'], Polygon):
            # this should not happen on real data
            way_shape['shape'] = LineString(way_shape['shape'].exterior.coords)
        lines.append(way_shape['shape'])
    if len(lines) < 1:
        return None

    multiline = MultiLineString(lines)
    multiline = linemerge(multiline)
    return {
        'shape': multiline,
        'properties': get_element_props(rel)
    }


def multipolygon_relation_to_shape(rel, refs_index):
    inner = []
    outer = []

    if 'members' in rel:
        members = rel['members']
    else:
        members = refs_index[rel['ref']]['members']

    for member in members:
        if member['type'] != 'way':
            print('multipolygon member not handled', member)
            continue

        member['used'] = rel['id']

        way_shape = way_to_shape(member, refs_index)
        if way_shape is None:
            # throw exception
            print('Failed to make way', member, 'in relation', rel)
            continue

        if isinstance(way_shape['shape'], Polygon):
            way_shape['shape'] = LineString(way_shape['shape'].exterior.coords)

        if member['role'] == 'inner':
            inner.append(way_shape['shape'])
        else:
            outer.append(way_shape['shape'])

    multipolygon = convert_ways_to_multipolygon(outer, inner)
    if multipolygon is None:
        print('Relation not converted to feature', rel)
        return None

    multipolygon = fix_invalid_polygon(multipolygon)
    multipolygon = to_multipolygon(multipolygon)
    multipolygon = orient_multipolygon(multipolygon) # do we need this?

    return {
        'shape': multipolygon,
        'properties': get_element_props(rel)
    }


def to_multipolygon(obj):
    if isinstance(obj, MultiPolygon):
        return obj

    if isinstance(obj, GeometryCollection):
        p = []
        for el in obj:
            if isinstance(el, Polygon):
                p.append(el)
        return MultiPolygon(p)

    if isinstance(obj, Polygon):
        return MultiPolygon([obj])

    # throw exception
    print('Failed to convert to multipolygon', type(obj))
    return None


def _convert_lines_to_multipolygon(lines):
    multi_line = MultiLineString(lines)
    merged_line = linemerge(multi_line)
    if isinstance(merged_line, MultiLineString):
        polygons = []
        for line in merged_line:
            try:
                poly = Polygon(line)
                if poly.is_valid:
                    polygons.append(poly)
                else:
                    polygons.append(poly.buffer(0))
            except:
                # throw exception
                print('Failed to build polygon', line)
        return to_multipolygon(cascaded_union(polygons))
    try:
        poly = Polygon(merged_line)
    except Exception as e:
        print('Failed to convert lines to polygon', e)
        traceback.print_exc()
        return None
    return to_multipolygon(poly)


def convert_ways_to_multipolygon(outer, inner = []):
    if len(outer) < 1:
        # throw exception
        print('Ways not found')
        return None

    outer_polygon = _convert_lines_to_multipolygon(outer)
    if outer_polygon is None:
        return None

    if len(inner) < 1:
        return outer_polygon

    inner_polygon = _convert_lines_to_multipolygon(inner)
    if inner_polygon is None:
        # we need to handle this error in other way
        return outer_polygon
    return to_multipolygon(outer_polygon.difference(inner_polygon))
