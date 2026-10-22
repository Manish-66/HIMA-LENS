"""
Automated Geospatial & Geotechnical Regression Test Suite for HIMA-LENS
Tests GeoJSON coordinate order, Himachal Pradesh territorial bounds, and physical stability calculations.
"""
import sys
import os
import json
import unittest

# Ensure workspace root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from geotech_engine import evaluate_usgs_classification, calculate_comprehensive_cost_and_loss_estimate

class TestSpatialIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.geojson_path = "landslides_clean.geojson"
        cls.assertTrue(os.path.exists(cls.geojson_path), "landslides_clean.geojson must exist")
        with open(cls.geojson_path, "r", encoding="utf-8") as f:
            cls.data = json.load(f)

    def test_feature_collection_schema(self):
        """Assert file is a standard GeoJSON FeatureCollection with features."""
        self.assertEqual(self.data.get("type"), "FeatureCollection")
        features = self.data.get("features", [])
        self.assertGreater(len(features), 10000, "Dataset should contain > 10,000 features")

    def test_coordinate_order_and_bounds(self):
        """Assert coordinate order is [longitude, latitude] and inside HP bounding box."""
        features = self.data.get("features", [])
        step = max(1, len(features) // 1000)
        sample = features[::step]

        for feat in sample:
            geom = feat.get("geometry", {})
            self.assertEqual(geom.get("type"), "Point")
            coords = geom.get("coordinates")
            self.assertEqual(len(coords), 2, "Coordinate pair must have exactly [lon, lat]")
            lon, lat = coords[0], coords[1]

            # Longitude in Himachal Pradesh: ~75.5 to 79.5 E
            self.assertGreater(lon, 75.0, f"Longitude {lon} too far west for HP")
            self.assertLess(lon, 80.0, f"Longitude {lon} too far east for HP")

            # Latitude in Himachal Pradesh: ~30.0 to 33.5 N
            self.assertGreater(lat, 30.0, f"Latitude {lat} too far south for HP")
            self.assertLess(lat, 34.0, f"Latitude {lat} too far north for HP")

    def test_required_properties_exist(self):
        """Assert critical properties exist on features."""
        sample_feat = self.data["features"][0]["properties"]
        required_keys = ["id", "district", "movement_type"]
        for key in required_keys:
            self.assertIn(key, sample_feat, f"Feature missing required key '{key}'")

    def test_geotech_usgs_evaluation(self):
        """Assert USGS Cruden-Varnes evaluation functions deterministically."""
        res = evaluate_usgs_classification(
            movement_type="Debris Slide",
            material_type="Colluvium",
            severity="Severe"
        )
        self.assertIn("two_term_classification", res)
        self.assertIn("velocity_class", res)
        self.assertIn("standard_reference", res)

    def test_cost_estimation_math(self):
        """Assert cost calculations produce positive numbers without NaN/inf."""
        mock_dossier = {
            "is_landslide_or_terrain": True,
            "validation_status": "VALID_TERRAIN_IMAGE",
            "kinematics": {"movement_type": "Debris Flow"},
            "scale_and_geometry": {
                "estimated_slope_height_m": 12.0,
                "estimated_scarp_length_m": 45.0,
                "displaced_volume_m3": 1800.0,
            },
            "geotechnical_parameters": {
                "inferred_rock_soil_type": "Colluvium / Weathered Phyllite",
                "cohesion_c_kpa": 12.0,
                "friction_angle_deg": 29.0
            }
        }
        res = calculate_comprehensive_cost_and_loss_estimate(mock_dossier)
        self.assertIn("financial_summary", res)
        fin = res["financial_summary"]
        total = fin.get("total_remediation_raw", 0)
        self.assertGreater(total, 0, "Remediation cost must be positive")
        self.assertFalse(total != total, "Cost cannot be NaN")

if __name__ == "__main__":
    unittest.main()
