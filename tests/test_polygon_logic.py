import unittest

from osm2geojson.main import is_geometry_polygon, is_geometry_polygon_without_exceptions


class TestIsGeometryPolygon(unittest.TestCase):
    """
    Unit tests for is_geometry_polygon - the main function that determines
    if an element should be rendered as a polygon.

    This function handles high-precedence tags (area, type=multipolygon),
    geometry validation, and delegates to is_geometry_polygon_without_exceptions
    for whitelist/blacklist rule evaluation.
    """

    def test_no_tags_returns_false(self):
        """
        Test that elements without tags are not polygons.
        """
        node = {}
        result = is_geometry_polygon(node)
        self.assertFalse(result, "Element without tags should NOT be a polygon")

    def test_area_no_highest_precedence(self):
        """
        Test that area=no takes precedence over everything.
        Example: area=no + type=multipolygon + building=yes
        Should NOT be a polygon because area=no is checked first.
        """
        node = {"tags": {"area": "no", "type": "multipolygon", "building": "yes"}}
        result = is_geometry_polygon(node)
        self.assertFalse(result, "area=no should override type=multipolygon and other polygon tags")

    def test_area_yes_overrides_blacklist(self):
        """
        Test that area=yes takes precedence over blacklisted tags.
        Example: area=yes + highway=steps (blacklisted)
        Should be a polygon because area=yes is checked first.
        """
        node = {"tags": {"area": "yes", "highway": "steps"}}
        result = is_geometry_polygon(node)
        self.assertTrue(result, "area=yes should override blacklisted tags")

    def test_area_no_overrides_whitelist(self):
        """
        Test that area=no takes precedence over whitelisted tags.
        Example: area=no + building=yes (whitelist "all")
        Should NOT be a polygon because area=no is checked first.
        """
        node = {"tags": {"area": "no", "building": "yes"}}
        result = is_geometry_polygon(node)
        self.assertFalse(result, "area=no should override whitelisted tags")

    def test_area_yes_makes_anything_polygon(self):
        """
        Test that area=yes makes even things with no other polygon tags into polygons.
        Example: area=yes + name=Something
        Should be a polygon.
        """
        node = {"tags": {"area": "yes", "name": "Random Feature"}}
        result = is_geometry_polygon(node)
        self.assertTrue(result, "area=yes should make any feature a polygon")

    def test_type_multipolygon_makes_polygon(self):
        """
        Test that type=multipolygon makes element a polygon.
        Should be a polygon.
        """
        node = {"tags": {"type": "multipolygon", "name": "Some relation"}}
        result = is_geometry_polygon(node)
        self.assertTrue(result, "type=multipolygon should make element a polygon")

    def test_type_multipolygon_overrides_blacklist(self):
        """
        Test that type=multipolygon takes precedence over blacklisted tags.
        Example: type=multipolygon + highway=steps (blacklisted)
        Should be a polygon.
        """
        node = {"tags": {"type": "multipolygon", "highway": "steps"}}
        result = is_geometry_polygon(node)
        self.assertTrue(result, "type=multipolygon should override blacklisted tags")

    def test_open_geometry_returns_false(self):
        """
        Test that elements with non-closed geometry are not polygons.
        If first and last coords don't match, should NOT be a polygon.
        """
        node = {
            "tags": {"building": "yes"},
            "geometry": [
                {"lat": 0.0, "lon": 0.0},
                {"lat": 0.0, "lon": 1.0},
                {"lat": 1.0, "lon": 1.0},
                {"lat": 1.0, "lon": 0.5},  # Different from first point
            ],
        }
        result = is_geometry_polygon(node)
        self.assertFalse(result, "Element with open geometry should NOT be a polygon")

    def test_closed_geometry_with_polygon_tags(self):
        """
        Test that elements with closed geometry and polygon tags are polygons.
        """
        node = {
            "tags": {"building": "yes"},
            "geometry": [
                {"lat": 0.0, "lon": 0.0},
                {"lat": 0.0, "lon": 1.0},
                {"lat": 1.0, "lon": 1.0},
                {"lat": 0.0, "lon": 0.0},  # Same as first point
            ],
        }
        result = is_geometry_polygon(node)
        self.assertTrue(result, "Element with closed geometry and polygon tags should be a polygon")

    def test_area_other_value_falls_through(self):
        """
        Test that area with values other than yes/no falls through to normal logic.
        Example: area=unknown + highway=steps (blacklisted)
        Should NOT be a polygon (blacklist applies).
        """
        node = {"tags": {"area": "unknown", "highway": "steps"}}
        result = is_geometry_polygon(node)
        self.assertFalse(result, "area=unknown should fall through to normal blacklist logic")


class TestIsGeometryPolygonWithoutExceptions(unittest.TestCase):
    """
    Unit tests for is_geometry_polygon_without_exceptions - a helper function
    that applies whitelist/blacklist rules from polygon-features.json.

    This function is called by is_geometry_polygon after higher-precedence
    checks (area tag, geometry validation) have been performed.

    These tests verify the precedence rules for whitelist/blacklist logic.
    """

    def test_blacklist_precedence_over_whitelist(self):
        """
        Test that blacklist rules take precedence over whitelist rules.
        Example: indoor=yes (whitelist "all") + highway=steps (blacklist)
        Should be NOT a polygon because blacklist takes precedence.
        """
        node = {"tags": {"indoor": "yes", "highway": "steps"}}
        result = is_geometry_polygon_without_exceptions(node)
        self.assertFalse(
            result,
            "Element with blacklisted tag should NOT be a polygon, even with whitelisted tags",
        )

    def test_neither_whitelist_nor_blacklist(self):
        """
        Test behavior when a tag has both whitelist and blacklist rules,
        but the value matches neither.
        Example: highway=trunk (not in whitelist [rest_area, services, etc], not in blacklist [steps])
        Should be NOT a polygon (default behavior).
        """
        node = {"tags": {"highway": "trunk"}}
        result = is_geometry_polygon_without_exceptions(node)
        self.assertFalse(
            result, "Element with tag value not in whitelist or blacklist should NOT be a polygon"
        )

    def test_whitelist_match(self):
        """
        Test that whitelisted values are correctly identified as polygons.
        Example: highway=rest_area (whitelisted)
        Should be a polygon.
        """
        node = {"tags": {"highway": "rest_area"}}
        result = is_geometry_polygon_without_exceptions(node)
        self.assertTrue(result, "Element with whitelisted tag should be a polygon")

    def test_all_rule(self):
        """
        Test that "polygon: all" rules work correctly.
        Example: building=yes
        Should be a polygon.
        """
        node = {"tags": {"building": "yes"}}
        result = is_geometry_polygon_without_exceptions(node)
        self.assertTrue(result, "Element with 'all' rule tag should be a polygon")

    def test_blacklist_match(self):
        """
        Test that blacklisted values are correctly identified as NOT polygons.
        Example: natural=coastline (blacklisted)
        Should be NOT a polygon.
        """
        node = {"tags": {"natural": "coastline"}}
        result = is_geometry_polygon_without_exceptions(node)
        self.assertFalse(result, "Element with blacklisted tag should NOT be a polygon")

    def test_no_relevant_tags(self):
        """
        Test default behavior when element has no tags matching any rules.
        Example: name=Something (not in any polygon rules)
        Should be NOT a polygon (default).
        """
        node = {"tags": {"name": "Something Random"}}
        result = is_geometry_polygon_without_exceptions(node)
        self.assertFalse(result, "Element with no relevant polygon tags should NOT be a polygon")


if __name__ == "__main__":
    unittest.main()
