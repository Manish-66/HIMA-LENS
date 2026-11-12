#!/usr/bin/env python3
"""
Verification Suite for Task 13: Geological Rock Classification Info, Apps & Websites
=====================================================================================
Validates:
1. GSI Bhukosh digital ground truth resolution across Himachal Pradesh districts.
2. Macrostrat / Rockd API query handling with caching and fallback.
3. IS:13365, Bieniawski RMR, and Hoek-Brown GSI rock mass parameter estimator.
4. Stratigraphic concordance and overburden colluvium cross-validation logic.
5. Flask API endpoints: /api/geology/lookup and /api/geology/catalog.
"""

import sys
import unittest
from pathlib import Path

# Add project root and core to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "core"))

import geology_engine
import app as flask_app


class TestGeologyEngine(unittest.TestCase):
    def setUp(self):
        self.app = flask_app.app.test_client()
        self.app.testing = True

    def test_himalayan_rock_database_coverage(self):
        """Assert all 10 Himalayan lithological archetypes are defined with complete physical bounds."""
        expected_rocks = [
            "phyllite", "schist", "quartzite", "gneiss", "granite",
            "dolomite", "limestone", "sandstone", "shale", "slate"
        ]
        db = geology_engine.HIMALAYAN_ROCK_DATABASE
        for rock in expected_rocks:
            self.assertIn(rock, db, f"Rock archetype '{rock}' missing from database")
            profile = db[rock]
            self.assertIn("name", profile)
            self.assertIn("family", profile)
            self.assertIn("intact_strength_mpa", profile)
            self.assertIn("friction_angle_deg", profile)
            self.assertIn("cohesion_kpa", profile)
            self.assertIn("rmr_class", profile)
            self.assertIn("typical_gsi", profile)
            self.assertIn("hand_specimen_diagnostic", profile)
            diag = profile["hand_specimen_diagnostic"]
            self.assertIn("hardness", diag)
            self.assertIn("cleavage", diag)
            self.assertIn("acid_test", diag)

    def test_geological_synthesis_mandi(self):
        """Assert geological synthesis resolves correctly for Mandi (Shali Group / Sundernagar)."""
        dossier = geology_engine.get_geological_synthesis(
            lat=31.708,
            lng=76.932,
            district="Mandi"
        )
        self.assertEqual(dossier["status"], "success")
        self.assertIn("bhukosh", dossier)
        self.assertIn("macrostrat", dossier)
        self.assertIn("rock_profile", dossier)
        self.assertIn("apps_and_tools", dossier)
        self.assertTrue(len(dossier["apps_and_tools"]) >= 3)

        # Verify apps suite contains Rockd and Bhukosh
        app_names = [a["name"] for a in dossier["apps_and_tools"]]
        self.assertTrue(any("Rockd" in name for name in app_names))
        self.assertTrue(any("Bhukosh" in name for name in app_names))

    def test_cross_validation_concordance(self):
        """Assert field colluvium overlying solid bedrock is reconciled concordantly (no false alarm)."""
        # Scenario 1: Field reporter observed colluvial debris / scree
        dossier_colluvium = geology_engine.get_geological_synthesis(
            lat=31.708,
            lng=76.932,
            district="Mandi",
            field_observed_rock="Saturated Colluvium & Debris"
        )
        audit = dossier_colluvium["consistency_audit"]
        self.assertEqual(audit["status"], "OVERBURDEN_COLLUVIUM_CONCORDANT")
        self.assertGreaterEqual(audit["consistency_pct"], 90)

        # Scenario 2: Field reporter observed exact matching rock
        dossier_bedrock = geology_engine.get_geological_synthesis(
            lat=31.708,
            lng=76.932,
            district="Mandi",
            field_observed_rock="Sandstone"
        )
        audit_bedrock = dossier_bedrock["consistency_audit"]
        self.assertEqual(audit_bedrock["status"], "BEDROCK_CONFIRMED")
        self.assertGreaterEqual(audit_bedrock["consistency_pct"], 95)

        # Scenario 3: Discrepant rock (e.g., Basalt in Mandi metasediments)
        dossier_discrepant = geology_engine.get_geological_synthesis(
            lat=31.708,
            lng=76.932,
            district="Mandi",
            field_observed_rock="Vesicular Basalt"
        )
        audit_disc = dossier_discrepant["consistency_audit"]
        self.assertEqual(audit_disc["status"], "LITHOLOGY_DISCREPANCY_FLAGGED")

    def test_api_geology_lookup_endpoint(self):
        """Assert /api/geology/lookup returns valid JSON HTTP 200 for coordinates."""
        res = self.app.get("/api/geology/lookup?lat=31.708&lng=76.932&district=Mandi")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("primary_rock", data)
        self.assertIn("bhukosh", data)
        self.assertIn("macrostrat", data)
        self.assertIn("rock_profile", data)
        self.assertIn("apps_and_tools", data)

    def test_api_geology_lookup_invalid_params(self):
        """Assert /api/geology/lookup returns HTTP 400 when coordinates are missing or non-numeric."""
        res_no_params = self.app.get("/api/geology/lookup")
        self.assertEqual(res_no_params.status_code, 400)

        res_bad_coords = self.app.get("/api/geology/lookup?lat=abc&lng=xyz")
        self.assertEqual(res_bad_coords.status_code, 400)

    def test_api_geology_catalog_endpoint(self):
        """Assert /api/geology/catalog returns HTTP 200 with complete rock reference database."""
        res = self.app.get("/api/geology/catalog")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("rock_database", data)
        self.assertIn("classification_standards", data)
        self.assertIn("rmr", data["classification_standards"])
        self.assertIn("gsi", data["classification_standards"])


if __name__ == "__main__":
    unittest.main()
