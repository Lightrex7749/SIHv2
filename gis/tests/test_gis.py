"""
DrishtiSetu — GIS Data & Land-Use Conflict Unit Tests (Member 3)
"""

import unittest
from gis.service import (
    get_habitations,
    get_habitation_by_id,
    get_relocation_sites,
    get_layer_geojson,
    get_risk_layers_manifest,
)
from gis.conflict import check_land_use_conflict


class TestGISData(unittest.TestCase):
    def test_habitations_retrieval(self):
        habs = get_habitations()
        self.assertGreaterEqual(len(habs), 4)
        joshimath = get_habitation_by_id("H001")
        self.assertIsNotNone(joshimath)
        self.assertEqual(joshimath["district"], "Chamoli")
        self.assertEqual(joshimath["state"], "Uttarakhand")

    def test_relocation_sites_and_conflict_flag(self):
        sites = get_relocation_sites()
        self.assertGreaterEqual(len(sites), 3)

        # Site S001 (Dhak Plateau) must NOT have land-use conflict
        s1 = next(s for s in sites if s["site_id"] == "S001")
        self.assertFalse(s1["land_use_conflict"])

        # Site S003 (Nanda Devi Buffer) MUST have land-use conflict
        s3 = next(s for s in sites if s["site_id"] == "S003")
        self.assertTrue(s3["land_use_conflict"])
        self.assertIsNotNone(s3["land_use_conflict_reason"])
        self.assertIn("Nanda Devi", s3["land_use_conflict_reason"])

    def test_geojson_layers_validity(self):
        hab_geojson = get_layer_geojson("habitations")
        self.assertEqual(hab_geojson["type"], "FeatureCollection")
        self.assertGreater(len(hab_geojson["features"]), 0)

        red_zones = get_layer_geojson("red-zones")
        self.assertEqual(red_zones["type"], "FeatureCollection")
        self.assertGreater(len(red_zones["features"]), 0)

        conflict_zones = get_layer_geojson("land-use-conflict")
        self.assertEqual(conflict_zones["type"], "FeatureCollection")
        self.assertGreater(len(conflict_zones["features"]), 0)

    def test_conflict_point_check(self):
        # Point inside Nanda Devi buffer zone
        has_conflict, reason, zone = check_land_use_conflict(30.50, 79.68)
        self.assertTrue(has_conflict)
        self.assertIn("Nanda Devi", reason)

        # Point in safe Chamoli terrace
        has_conflict, reason, zone = check_land_use_conflict(30.28, 79.15)
        self.assertFalse(has_conflict)
        self.assertIsNone(reason)


if __name__ == "__main__":
    unittest.main()
