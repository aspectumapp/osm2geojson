#!/usr/bin/env python3

import os
import sys
import json
import argparse
from typing import Optional

from .main import json2geojson, json2shapes, xml2geojson, xml2shapes


def setup_parser() -> argparse.ArgumentParser:
    def existing_file(v: str) -> str:
        if not os.path.exists(v):
            raise ValueError(v)
        return v

    def optional_file(v: Optional[str] = None) -> Optional[str]:
        if v is None:
            return None
        return existing_file(v)

    parser = argparse.ArgumentParser(prog=__package__)
    parser.add_argument(
        "infile",
        type=existing_file,
        help="OSM or Overpass JSON file to convert to GeoJSON or shape JSON"
    )
    parser.add_argument(
        "outfile",
        help="write output of the processing to the specified file (uses stdout for '-')"
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="allow overwriting of existing file"
    )
    logging = parser.add_mutually_exclusive_group()
    logging.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="suppress logging output"
    )
    logging.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="enable verbose logging output"
    )
    parser.add_argument(
        "-i",
        "--indent",
        type=int,
        metavar="N",
        default=None,
        help="indentation using N spaces for the output file (defaults to none)"
    )
    # TODO: Overpass JSON is fine, but what about Overpass XML?
    parser.add_argument(
        "--reader",
        choices=("osm", "overpass", "auto"),
        default="auto",
        help="specify the input file format (either OSM or Overpass JSON), defaults to auto-detect"
    )
    parser.add_argument(
        "--format",
        choices=("geo", "shape"),
        default="geojson",
        help="specify the output format (either GeoJSON or shape JSON), defaults to GeoJSON"
    )
    parser.add_argument(
        "--no-unused-filter",
        action="store_false",
        dest="filter_used_refs",
        help="don't filter unused references (only in shape JSON)"
    )
    parser.add_argument(
        "--areas",
        type=optional_file,
        default=None,
        metavar="file",
        help="JSON file defining the keys that should be included from areas (uses defaults if omitted)"
    )
    parser.add_argument(
        "--polygons",
        type=optional_file,
        default=None,
        metavar="file",
        help="JSON file defining the allowed/restricted polygon features (uses defaults if omitted)"
    )
    return parser


def main(args=None) -> int:
    parser = setup_parser()
    args = parser.parse_args(args)

    parser_function = None
    if args.reader == "auto":
        if args.infile.endswith((".osm", ".xml")):
            parser_function = xml2geojson
            if args.format == "shape":
                parser_function = xml2shapes
        elif args.infile.endswith((".shape", ".json")):
            parser_function = json2geojson
            if args.format == "shape":
                parser_function = json2shapes
        else:
            # default of converting OSM to GeoJSON which may fail for invalid inputs
            parser_function = xml2geojson
    elif args.reader == "osm":
        parser_function = xml2geojson
        if args.format == "shape":
            parser_function = xml2shapes
    elif args.reader == "overpass":
        parser_function = json2geojson
        if args.format == "shape":
            parser_function = json2shapes

    if parser_function is None:
        print("Unspecified parser function. Consider using --format and --reader.", file=sys.stderr)
        return 1
    if args.outfile != "-" and os.path.exists(args.outfile) and not args.force:
        print(
            "Output file '{}' already exists. Consider using -f to force overwriting.".format(args.outfile),
            file=sys.stderr
        )
        return 1

    with open(args.infile) as f:
        data = f.read()

    log_level = "WARNING"
    if args.quiet:
        log_level = "CRITICAL"
    elif args.verbose:
        log_level = "DEBUG"

    area_keys = None
    if args.areas:
        with open(args.areas) as f:
            area_keys = json.load(f)
            if "areaKeys" in area_keys and len(area_keys) == 1:
                area_keys = area_keys["areaKeys"]
    polygon_features = None
    if args.polygons:
        with open(args.polygons) as f:
            polygon_features = json.load(f)

    result = parser_function(
        data,
        filter_used_refs=args.filter_used_refs,
        log_level=log_level,
        area_keys=area_keys,
        polygon_features=polygon_features
    )

    indent = args.indent
    if indent and indent < 0:
        indent = None
    if args.outfile == "-":
        target = sys.stdout
    else:
        target = open(args.outfile, "w")

    code = 0
    try:
        print(json.dumps(result, indent=indent), file=target)
    except (TypeError, ValueError) as exc:
        print(exc, file=sys.stderr)
        print("Falling back to raw dumping the object...", file=sys.stderr)
        print(result, file=target)
        code = 1

    if args.outfile != "-":
        target.flush()
        target.close()
    return code


exit(main(sys.argv[1:]))
