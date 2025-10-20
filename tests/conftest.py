"""Pytest configuration and fixtures for osm2geojson tests."""

import json
from pathlib import Path
from typing import Tuple

import pytest


@pytest.fixture
def data_dir() -> Path:
    """Return the path to the test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def read_data_file(data_dir):
    """Fixture to read test data files."""

    def _read_file(filename: str) -> str:
        """Read a test data file and return its contents."""
        file_path = data_dir / filename
        with open(file_path, encoding="utf-8") as f:
            return f.read()

    return _read_file


@pytest.fixture
def load_json_data(read_data_file):
    """Fixture to load JSON data from test files."""

    def _load_json(filename: str) -> dict:
        """Load and parse JSON from a test data file."""
        content = read_data_file(filename)
        return json.loads(content)

    return _load_json


@pytest.fixture
def get_osm_and_geojson(read_data_file):
    """
    Fixture that returns a function to load OSM XML and expected GeoJSON.

    Returns a tuple of (converted_geojson, expected_geojson).
    """
    from osm2geojson import xml2geojson

    def _get_data(name: str) -> Tuple[dict, dict]:
        """Load OSM and GeoJSON data for a given test case name."""
        xml_data = read_data_file(f"{name}.osm")
        geojson_data = read_data_file(f"{name}.geojson")
        converted = xml2geojson(xml_data)
        expected = json.loads(geojson_data)
        return converted, expected

    return _get_data


@pytest.fixture
def get_json_and_geojson(read_data_file):
    """
    Fixture that returns a function to load Overpass JSON and expected GeoJSON.

    Returns a tuple of (overpass_json, expected_geojson).
    """

    def _get_data(name: str) -> Tuple[dict, dict]:
        """Load JSON and GeoJSON data for a given test case name."""
        json_data = read_data_file(f"{name}.json")
        geojson_data = read_data_file(f"{name}.geojson")
        overpass_json = json.loads(json_data)
        expected_geojson = json.loads(geojson_data)
        return overpass_json, expected_geojson

    return _get_data
