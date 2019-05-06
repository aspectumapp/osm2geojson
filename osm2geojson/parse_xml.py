import xml.etree.ElementTree as ElementTree

def copy_fields(node, base, optional = []):
    obj = {}
    for key in base:
        obj[key] = node.attrib[key]
    for key in optional:
        if key in node.attrib:
            obj[key] = node.attrib[key]
    return obj

def tags_to_obj(tags):
    obj = {}
    for tag in tags:
        obj[tag['k']] = tag['v']
    return obj

def parse_bounds(node):
    return copy_fields(node, ['minlat', 'minlon', 'maxlat', 'maxlon'])

def parse_tag(node):
    return copy_fields(node, ['k', 'v'])

def parse_node(node):
    item = copy_fields(node, [], ['role', 'id', 'ref', 'lat', 'lon'])
    item['type'] = 'node'
    return item

def parse_way(node):
    tags = []
    geometry = []
    nodes = []
    for child in node:
        if child.tag == 'nd':
            if 'ref' in child.attrib:
                nodes.append(int(child.attrib['ref']))
            else:
                geometry.append(copy_fields(child, ['lat', 'lon']))
        elif child.tag == 'tag':
            tags.append(parse_tag(child))
        else:
            print('Way contains wrong child', child.tag)

    item = copy_fields(node, [], ['ref', 'role'])
    item['tags'] = tags_to_obj(tags)
    item['type'] = 'way'
    item['geometry'] = geometry
    item['nodes'] = nodes
    return item

def parse_relation(node):
    # Ignore nodes, ways, relations for relation node
    bounds, tags, nodes, ways, relations, members, unhandled = parse_xml_node(node)

    return {
        'type': 'relation',
        'id': node.attrib['id'],
        'bounds': bounds,
        'tags': tags_to_obj(tags),
        'members': members
    }

def format_josm(nodes, ways, relations, unhandled):
    version = 0.6
    generator = None
    timestamp_osm_base = None
    copyright = None

    for node in unhandled:
        if node.tag == 'meta' and 'osm_base' in node.attrib:
            timestamp_osm_base = node.attrib['osm_base']
        if node.tag == 'note':
            copyright = node.text
        if node.tag == 'osm':
            if 'version' in node.attrib:
                version = float(node.attrib['version'])
            if 'generator' in node.attrib:
                generator = node.attrib['generator']

    item = {
        'version': version,
        'elements': nodes + ways + relations
    }

    if generator is not None:
        item['generator'] = generator
    if copyright is not None or timestamp_osm_base is not None:
        item['osm3s'] = {}
        if copyright is not None:
            item['osm3s']['copyright'] = copyright
        if timestamp_osm_base is not None:
            item['osm3s']['timestamp_osm_base'] = timestamp_osm_base

    return item

def parse(xml_str):
    root = ElementTree.fromstring(xml_str)
    if not root.tag == 'osm':
        print('OSM root node not found!')
        return None

    # Ignore bounds, tags and members for OSM root node
    bounds, tags, nodes, ways, relations, members, unhandled = parse_xml_node(root)
    unhandled.append(root)
    return format_josm(nodes, ways, relations, unhandled)

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

    else:
        print('Unhandled node type', node_type)
        return None

def parse_xml_node(root):
    bounds = None
    unhandled = []
    data = {
        'node': [],
        'way': [],
        'relation': [],
        'tag': [],
        'member': []
    }

    for child in root:
        if child.tag == 'bounds':
            if bounds is not None:
                print('Node bounds should be unique')
            bounds = parse_bounds(child)
        else:
            if child.tag not in data:
                print('Unhandled node', child.tag)
                unhandled.append(child)
                continue
            data[child.tag].append(parse_node_type(child, child.tag))

    return \
        bounds, \
        data['tag'], \
        data['node'], \
        data['way'], \
        data['relation'], \
        data['member'], \
        unhandled
