import xml.etree.ElementTree as ElementTree

default_types = ['node', 'way', 'relation', 'member', 'nd']
optional_meta_fields = ['timestamp', 'version:int', 'changeset:int', 'user', 'uid:int']


def parse_key(key):
    t = 'string'
    parts = key.split(':')
    if len(parts) > 1:
        t = parts[1]
    return parts[0], t


def to_type(v, t):
    if t == 'string':
        return str(v)
    elif t == 'int':
        return int(v)
    elif t == 'float':
        return float(v)
    return v


def with_meta_fields(fields=[]):
    for field in optional_meta_fields:
        if field not in fields:
            fields.append(field)
    return fields


def copy_fields(node, base, optional=[]):
    obj = {}
    for key in base:
        key, t = parse_key(key)
        if key not in node.attrib:
            print(key, 'not found in', node.tag, node.attrib)
        obj[key] = to_type(node.attrib[key], t)
    for key in optional:
        key, t = parse_key(key)
        if key in node.attrib:
            obj[key] = to_type(node.attrib[key], t)
    return obj


def filter_items_by_type(items, types):
    return [i for i in items if i['type'] in types]


def tags_to_obj(tags):
    return {tag['k']: tag['v'] for tag in tags}


def parse_bounds(node):
    return copy_fields(node, [
        'minlat:float',
        'minlon:float',
        'maxlat:float',
        'maxlon:float'
    ])


def parse_count(node):
    bounds, tags, _empty, unhandled = parse_xml_node(node, [])
    item = copy_fields(node, ['id:int'])
    item['type'] = 'count'
    if len(tags) > 0:
        item['tags'] = tags_to_obj(tags)
    return item


def parse_tag(node):
    return copy_fields(node, ['k', 'v'])


def parse_nd(node):
    return copy_fields(node, [], ['ref:int', 'lat:float', 'lon:float'])


def parse_node(node):
    bounds, tags, items, unhandled = parse_xml_node(node)
    item = copy_fields(node, [], with_meta_fields([
        'role',
        'id:int',
        'ref:int',
        'lat:float',
        'lon:float'
    ]))
    item['type'] = 'node'
    if len(tags) > 0:
        item['tags'] = tags_to_obj(tags)
    return item


def parse_way(node):
    bounds, tags, nds, unhandled = parse_xml_node(node, ['nd'])
    geometry = []
    nodes = []
    for nd in nds:
        if 'ref' in nd and 'lat' not in nd and 'lon' not in nd:
            nodes.append(nd['ref'])
        else:
            geometry.append(nd)

    way = copy_fields(node, [], with_meta_fields(['ref:int', 'id:int', 'role']))
    way['type'] = 'way'
    if len(tags) > 0:
        way['tags'] = tags_to_obj(tags)
    if geometry:
        way['geometry'] = geometry
    if nodes:
        way['nodes'] = nodes
    return way


def parse_relation(node):
    bounds, tags, members, unhandled = parse_xml_node(node, ['member'])

    relation = copy_fields(node, [], with_meta_fields(['id:int', 'ref:int', 'role']))
    relation['type'] = 'relation'
    if len(members) > 0:
        relation['members'] = members
    if bounds is not None:
        relation['bounds'] = bounds
    if len(tags) > 0:
        relation['tags'] = tags_to_obj(tags)
    return relation


def format_ojson(elements, unhandled):
    version = 0.6
    generator = None
    timestamp_osm_base = None
    copyright = None

    for node in unhandled:
        if node.tag == 'meta' and 'osm_base' in node.attrib:
            timestamp_osm_base = node.attrib['osm_base']
        elif node.tag == 'note':
            copyright = node.text
        elif node.tag == 'osm':
            if 'version' in node.attrib:
                version = float(node.attrib['version'])
            if 'generator' in node.attrib:
                generator = node.attrib['generator']

    item = {
        'version': version,
        'elements': elements
    }

    if generator is not None:
        item['generator'] = generator
    if copyright is not None:
        item.setdefault('osm3s', {})['copyright'] = copyright
    if timestamp_osm_base is not None:
        item.setdefault('osm3s', {})['timestamp_osm_base'] = timestamp_osm_base

    return item


def parse(xml_str):
    root = ElementTree.fromstring(xml_str)
    if root.tag != 'osm':
        print('OSM root node not found!')
        return None

    bounds, tags, elements, unhandled = parse_xml_node(root, ['node', 'way', 'relation', 'count'])
    unhandled.append(root)
    return format_ojson(elements, unhandled)


def parse_node_type(node, node_type):
    if node_type == 'bounds':
        return parse_bounds(node)

    elif node_type == 'tag':
        return parse_tag(node)

    elif node_type == 'node':
        return parse_node(node)

    elif node_type == 'way':
        return parse_way(node)

    elif node_type == 'relation':
        return parse_relation(node)

    elif node_type == 'member':
        return parse_node_type(node, node.attrib['type'])

    elif node_type == 'nd':
        return parse_nd(node)

    else:
        print('Unhandled node type', node_type)
        return None


def parse_xml_node(root, node_types=default_types):
    bounds = None
    count = None
    tags = []
    items = []
    unhandled = []

    for child in root:
        if child.tag == 'bounds':
            if bounds is not None:
                print('Node bounds should be unique')
            bounds = parse_bounds(child)
        elif child.tag == 'count':
            if count is not None:
                print('Node count should be unique')
            count = parse_count(child)
        else:
            if child.tag == 'tag':
                tags.append(parse_tag(child))
                continue

            if child.tag not in default_types:
                unhandled.append(child)
                continue

            if child.tag in node_types:
                items.append(parse_node_type(child, child.tag))

    if 'count' in node_types and count is not None:
        items.append(count)
    return bounds, tags, items, unhandled
