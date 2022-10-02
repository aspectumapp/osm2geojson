import os
import json
import logging
import traceback
import itertools
from pprint import pformat
from typing import Optional

from shapely.geometry import (GeometryCollection, LineString, MultiLineString,
                              MultiPolygon, Point, Polygon, mapping)
from shapely.geometry.polygon import orient
from shapely.ops import unary_union, linemerge

from .parse_xml import parse as parse_xml


logger = logging.getLogger(__name__)
DEFAULT_POLYGON_FEATURES_FILE = os.path.join(os.path.dirname(__file__), 'polygon-features.json')
DEFAULT_AREA_KEYS_FILE = os.path.join(os.path.dirname(__file__), 'areaKeys.json')

if os.path.exists(DEFAULT_POLYGON_FEATURES_FILE):
    with open(DEFAULT_POLYGON_FEATURES_FILE) as f:
        _default_polygon_features = json.load(f)
else:
    logger.warning("Default polygon features file not found, using empty filter")
    _default_polygon_features = []

if os.path.exists(DEFAULT_AREA_KEYS_FILE):
    with open(DEFAULT_AREA_KEYS_FILE) as f:
        _default_area_keys = json.load(f)['areaKeys']
else:
    logger.warning("Default area keys file not found, using empty filter")
    _default_area_keys = {}


def warning(*args):
    logger.warning(' '.join(args))


def error(*args):
    logger.error(' '.join(args))


def json2geojson(
        data, filter_used_refs=True, log_level='ERROR',
        area_keys: Optional[dict] = None, polygon_features: Optional[list] = None
):
    if isinstance(data, str):
        data = json.loads(data)
    return _json2geojson(data, filter_used_refs, log_level, area_keys, polygon_features)


def xml2geojson(
        xml_str, filter_used_refs=True, log_level='ERROR',
        area_keys: Optional[dict] = None, polygon_features: Optional[list] = None
):
    data = parse_xml(xml_str)
    return _json2geojson(data, filter_used_refs, log_level, area_keys, polygon_features)


def json2shapes(
        data, filter_used_refs=True, log_level='ERROR',
        area_keys: Optional[dict] = None, polygon_features: Optional[list] = None
):
    if isinstance(data, str):
        data = json.loads(data)
    return _json2shapes(data, filter_used_refs, log_level, area_keys, polygon_features)


def xml2shapes(
        xml_str, filter_used_refs=True, log_level='ERROR',
        area_keys: Optional[dict] = None, polygon_features: Optional[list] = None
):
    data = parse_xml(xml_str)
    return _json2shapes(data, filter_used_refs, log_level, area_keys, polygon_features)


def _json2geojson(
        data, filter_used_refs=True, log_level='ERROR',
        area_keys: Optional[dict] = None, polygon_features: Optional[list] = None
):
    features = []
    for shape in _json2shapes(data, filter_used_refs, log_level, area_keys, polygon_features):
        feature = shape_to_feature(shape['shape'], shape['properties'])
        features.append(feature)

    return {
        'type': 'FeatureCollection',
        'features': features
    }


def _json2shapes(
        data, filter_used_refs=True, log_level='ERROR',
        area_keys: Optional[dict] = None, polygon_features: Optional[list] = None
):
    logger.setLevel(log_level)
    shapes = []

    refs = [
        el
        for el in data['elements']
        if el['type'] in ['node', 'way', 'relation']
    ]

    refs_index = build_refs_index(refs)

    for el in data['elements']:
        shape = element_to_shape(el, refs_index, area_keys, polygon_features)
        if shape is not None:
            shapes.append(shape)
        else:
            warning('Element not converted', pformat(el))

    if not filter_used_refs:
        return shapes

    used = {
        ref['id']: ref['used']
        for ref in refs if 'used' in ref
    }
    filtered_shapes = []
    for shape in shapes:
        if 'properties' not in shape:
            warning('Shape without props', pformat(shape))
        if shape['properties']['id'] in used:
            continue
        filtered_shapes.append(shape)

    return filtered_shapes


def element_to_shape(el, refs_index=None, area_keys: Optional[dict] = None, polygon_features: Optional[list] = None):
    t = el['type']
    if t == 'node':
        return node_to_shape(el)
    if t == 'way':
        return way_to_shape(el, refs_index, area_keys, polygon_features)
    if t == 'relation':
        return relation_to_shape(el, refs_index)
    warning('Failed to convert element to shape')
    return None


def _get_ref_name(el_type, id):
    return '%s/%s' % (el_type, id)


def get_ref_name(el):
    return _get_ref_name(el['type'], el['id'])


def _get_ref(el_type, id, refs_index):
    key = _get_ref_name(el_type, id)
    if key in refs_index:
        return refs_index[key]
    warning('Element not found in refs_index', pformat(el_type), pformat(id))
    return None


def get_ref(ref_el, refs_index):
    return _get_ref(ref_el['type'], ref_el['ref'], refs_index)


def get_node_ref(id, refs_index):
    return _get_ref('node', id, refs_index)


def build_refs_index(elements):
    return {
        get_ref_name(el): el
        for el in elements
    }


def node_to_shape(node):
    return {
        'shape': Point(node['lon'], node['lat']),
        'properties': get_element_props(node)
    }


def get_element_props(el, keys: list = None):
    keys = keys or [
        'type',
        'id',
        'tags',
        'nodes',
        'timestamp',
        'user',
        'uid',
        'version'
    ]
    return {
        key: el[key]
        for key in keys
        if key in el
    }


def convert_coords_to_lists(coords):
    if len(coords) < 1:
        return []

    if isinstance(coords[0], float):
        return list(coords)

    return [convert_coords_to_lists(c) for c in coords]


def shape_to_feature(g, props: dict = None):
    props = props or {}
    # shapely returns tuples (we need lists)
    g = mapping(g)
    g['coordinates'] = convert_coords_to_lists(g['coordinates'])
    return {
        "type": "Feature",
        'properties': props,
        "geometry": g
    }


def orient_multipolygon(p):
    p = [orient(geom) for geom in p.geoms]
    return MultiPolygon(p)


def fix_invalid_polygon(p):
    if not p.is_valid:
        logger.info('Invalid geometry! Try to fix with 0 buffer')
        p = p.buffer(0)
        if p.is_valid:
            logger.info('Geometry fixed!')
    return p


def way_to_shape(
        way, refs_index: dict = None,
        area_keys: Optional[dict] = None, polygon_features: Optional[list] = None
):
    refs_index = refs_index or {}
    if 'center' in way:
        center = way['center']
        return {
            'shape': Point(center['lon'], center['lat']),
            'properties': get_element_props(way)
        }

    if 'geometry' in way and len(way['geometry']) > 0:
        coords = [
            [nd['lon'], nd['lat']]
            for nd in way['geometry']
        ]

    elif 'nodes' in way and len(way['nodes']) > 0:
        coords = []
        for ref in way['nodes']:
            node = get_node_ref(ref, refs_index)
            if node:
                node['used'] = way['id']
                coords.append([node['lon'], node['lat']])
            else:
                warning('Node not found in index', pformat(ref), 'for way', pformat(way))
                return None

    elif 'ref' in way:
        ref = get_ref(way, refs_index)
        if not ref:
            warning('Ref for way not found in index', pformat(way))
            return None

        if 'id' in way:
            ref['used'] = way['id']
        elif 'used' in way:
            ref['used'] = way['used']
        else:
            # filter will not work for this situation
            warning('Failed to mark ref as used', pformat(ref), 'for way', pformat(way))
        ref_way = way_to_shape(ref, refs_index, area_keys, polygon_features)
        if ref_way is None:
            warning('Way by ref not converted to shape', pformat(way))
            return None
        coords = (
            ref_way['shape'].exterior
            if isinstance(ref_way['shape'], Polygon)
            else ref_way['shape']
        ).coords

    else:
        # throw exception
        warning('Relation has way without nodes', pformat(way))
        return None

    if len(coords) < 2:
        warning('Not found coords for way', pformat(way))
        return None

    props = get_element_props(way)
    if is_geometry_polygon(way, area_keys, polygon_features):
        try:
            poly = fix_invalid_polygon(Polygon(coords))
            return {
                'shape': poly,
                'properties': props
            }
        except Exception:
            warning('Failed to generate polygon from way', pformat(way))
            return None
    else:
        return {
            'shape': LineString(coords),
            'properties': props
        }


def is_exception(node, area_keys: Optional[dict] = None):
    area_keys = area_keys or _default_area_keys
    for tag in node['tags']:
        if tag in area_keys:
            value = node['tags'][tag]
            return value in area_keys[tag] and area_keys[tag][value]
    return False


def is_same_coords(a, b):
    return a['lat'] == b['lat'] and a['lon'] == b['lon']


def is_geometry_polygon(node, area_keys: Optional[dict] = None, polygon_features: Optional[list] = None):
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

    is_polygon = is_geometry_polygon_without_exceptions(node, polygon_features)
    if is_polygon:
        return not is_exception(node, area_keys)
    else:
        return False


def is_geometry_polygon_without_exceptions(node, polygon_features: Optional[list] = None):
    polygon_features = polygon_features or _default_polygon_features
    tags = node['tags']
    for rule in polygon_features:
        if rule['key'] in tags:
            if rule['polygon'] == 'all':
                return True
            if rule['polygon'] == 'whitelist' and tags[rule['key']] in rule['values']:
                return True
            if rule['polygon'] == 'blacklist':
                return tags[rule['key']] not in rule['values']
    return False


def relation_to_shape(rel, refs_index, area_keys: Optional[dict] = None, polygon_features: Optional[list] = None):
    if 'center' in rel:
        center = rel['center']
        return {
            'shape': Point(center['lon'], center['lat']),
            'properties': get_element_props(rel)
        }

    try:
        if is_geometry_polygon(rel, area_keys, polygon_features):
            return multipolygon_relation_to_shape(rel, refs_index)
        else:
            return multiline_realation_to_shape(rel, refs_index)
    except Exception:
        traceback.print_exc()
        error('Failed to convert relation to shape', pformat(rel))


def multiline_realation_to_shape(
        rel, refs_index,
        area_keys: Optional[dict] = None, polygon_features: Optional[list] = None
):
    lines = []

    if 'members' in rel:
        members = rel['members']
    else:
        found_ref = get_ref(rel, refs_index)
        if not found_ref:
            error('Ref for multiline relation not found in index', pformat(rel))
            return None
        members = found_ref['members']

    for member in members:
        if member['type'] == 'way':
            way_shape = way_to_shape(member, refs_index, area_keys, polygon_features)
        elif member['type'] == 'relation':
            found_member = get_ref(member, refs_index)
            if found_member:
                found_member['used'] = rel['id']
            way_shape = element_to_shape(member, refs_index, area_keys, polygon_features)
        else:
            warning('multiline member not handled', pformat(member))
            continue

        if way_shape is None:
            # throw exception
            warning('Failed to make way in relation', pformat(rel))
            continue

        if isinstance(way_shape['shape'], Polygon):
            # this should not happen on real data
            way_shape['shape'] = LineString(way_shape['shape'].exterior.coords)
        lines.append(way_shape['shape'])

    if len(lines) < 1:
        warning('No lines for multiline relation', pformat(rel))
        return None

    multiline = MultiLineString(lines)
    multiline = linemerge(multiline)
    return {
        'shape': multiline,
        'properties': get_element_props(rel)
    }


def multipolygon_relation_to_shape(
        rel, refs_index,
        area_keys: Optional[dict] = None, polygon_features: Optional[list] = None
):
    # List of Tuple (role, multipolygon)
    shapes = []

    if 'members' in rel:
        members = rel['members']
    else:
        found_ref = get_ref(rel, refs_index)
        if not found_ref:
            error('Ref for multipolygon relation not found in index', pformat(rel))
            return None
        members = found_ref['members']

    for member in members:
        if member['type'] != 'way':
            warning('Multipolygon member not handled', pformat(member))
            continue

        member['used'] = rel['id']

        way_shape = way_to_shape(member, refs_index, area_keys, polygon_features)
        if way_shape is None:
            # throw exception
            warning('Failed to make way', pformat(member), 'in relation', pformat(rel))
            continue

        if isinstance(way_shape['shape'], Polygon):
            way_shape['shape'] = LineString(way_shape['shape'].exterior.coords)

        shapes.append((member['role'], way_shape['shape']))

    multipolygon = _convert_shapes_to_multipolygon(shapes)
    if multipolygon is None:
        warning('Failed to convert computed shapes to multipolygon', pformat(rel))
        return None

    multipolygon = fix_invalid_polygon(multipolygon)
    multipolygon = to_multipolygon(multipolygon)
    multipolygon = orient_multipolygon(multipolygon)  # do we need this?

    if multipolygon is None:
        warning('Failed to fix multipolygon. Report this in github please!', pformat(rel))
        return None

    return {
        'shape': multipolygon,
        'properties': get_element_props(rel)
    }


def to_multipolygon(obj):
    if isinstance(obj, MultiPolygon):
        return obj

    if isinstance(obj, GeometryCollection):
        p = [
            el for el in obj
            if isinstance(el, Polygon)
        ]
        return MultiPolygon(p)

    if isinstance(obj, Polygon):
        return MultiPolygon([obj])

    # throw exception
    warning('Failed to convert to multipolygon', type(obj))
    return None


def _convert_lines_to_multipolygon(lines):
    multi_line = MultiLineString(lines)
    merged_line = linemerge(multi_line)
    if isinstance(merged_line, MultiLineString):
        polygons = []
        for line in merged_line.geoms:
            try:
                poly = Polygon(line)
                if poly.is_valid:
                    polygons.append(poly)
                else:
                    polygons.append(poly.buffer(0))
            except Exception:
                # throw exception
                warning('Failed to build polygon', pformat(line))
        return to_multipolygon(unary_union(polygons))
    try:
        poly = Polygon(merged_line)
    except Exception as e:
        warning('Failed to convert lines to polygon', pformat(e))
        # traceback.print_exc()
        return None
    return to_multipolygon(poly)


def _convert_shapes_to_multipolygon(shapes):
    if len(shapes) < 1:
        warning('Failed to create multipolygon (Empty)')
        return None

    # Intermediate groups
    groups = []
    # New group each time it switches role
    for role, group in itertools.groupby(shapes, lambda s: s[0]):
        groups.append((role, _convert_lines_to_multipolygon([_[1] for _ in group])))

    # Grab the first one.
    first_shape = groups.pop(0)
    if first_shape[0] == 'inner':
        warning('Failed to create multipolygon. First shape should have "outer" role')
        return None

    multipolygon = first_shape[1]
    # Itterate over the rest if there are any
    for role, geom in groups:
        if role == "inner":
            multipolygon = multipolygon.difference(geom)
        else:
            multipolygon = multipolygon.union(geom)

        if multipolygon is None:
            warning('Failed to compute multipolygon. Failing geometry:', role, geom)
            return None

    return multipolygon
