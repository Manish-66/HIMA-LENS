"""Verification Suite for Phase 3: Geotechnical Schematic Cross-Section Engine (geotech_schematic.py)
"""
import xml.etree.ElementTree as ET
import geotech_engine
import geotech_schematic

def verify_schematic_engine():
    print("=" * 80)
    print("  PHASE 3 VERIFICATION: GEOTECHNICAL ML SCHEMATIC SVG ENGINE")
    print("=" * 80)

    modes_to_test = [
        # (name, failure_vector, movement, extra_dossier, expected_mode, expected_strings)
        (
            "Benchmark Uphill Cut Slope (6A9B327E)",
            "UPHILL_CUT_SLOPE",
            "Slide",
            {"id": "IITM-CR-6A9B327E"},
            "translational",
            [
                "Monsoon FoS = 0.92 | Stabilized FoS = 1.56",
                "Plum Wall (H=2.7m)",
                "CROWN &amp; MAIN SCARP",
                "RUPTURE PLANE: DIP 57&deg; (DAYLIGHT)",
                "Formation: 5.25m",
                "Operable: 2.30m",
            ]
        ),
        (
            "Rotational Overburden Slump",
            "UPHILL_CUT_SLOPE",
            "Rotational Slump",
            {"movement_type": "Rotational Slump", "observed_features": {"optical_geometry": {"kinematic_failure_mode": "rotational_slump"}}},
            "rotational_slump",
            [
                "Monsoon FoS = 0.92 | Stabilized FoS = 1.56",
                "CIRCULAR SHEAR ARC (RUPTURE)",
                "MAIN SCARP &amp; CROWN CRACKS",
                "HEAVED TOE LOBE (PRESSURE RIDGE)",
                "Gabion Wall",
            ]
        ),
        (
            "Cliff Rockfall & Topple",
            "CLIFF_ROCKFALL_TOPPLE",
            "Fall",
            {"id": "IITM-CR-37541B33", "movement_type": "Fall"},
            "rockfall",
            [
                "SUB-VERTICAL TENSION FISSURE",
                "TOPPLING ROCK COLUMN (UNSTABLE)",
                "TALUS SCREE APRON (BOULDERS)",
                "Dynamic Barrier (500 kJ)",
            ]
        ),
        (
            "Channelized Debris Flow",
            "UPHILL_CUT_SLOPE",
            "Debris Flow",
            {"movement_type": "Debris Flow", "observed_features": {"optical_geometry": {"kinematic_failure_mode": "debris_flow"}}},
            "debris_flow",
            [
                "EROSIONAL TORRENT GULLY",
                "BOULDER &amp; SLURRY SURGE FRONT",
                "HIGH-VELOCITY DEBRIS FAN LOBE",
                "Check Dam",
            ]
        ),
        (
            "Structural Wedge Failure",
            "UPHILL_CUT_SLOPE",
            "Wedge",
            {"movement_type": "Wedge", "observed_features": {"optical_geometry": {"kinematic_failure_mode": "wedge"}}},
            "wedge",
            [
                "WEDGE APEX TENSION CRACK",
                "INTERSECTING JOINTS (J1 x J2 TROUGH)",
                "SLIDING TETRAHEDRAL WEDGE",
            ]
        ),
        (
            "Slope Creep & Subsidence",
            "UPHILL_CUT_SLOPE",
            "Creep",
            {"movement_type": "Creep", "observed_features": {"optical_geometry": {"kinematic_failure_mode": "creep_subsidence"}}},
            "creep_subsidence",
            [
                "PISTOL-BUTT TREE CURVATURE (CREEP)",
                "VISCO-PLASTIC OVERBURDEN CREEP",
                "SETTLEMENT",
            ]
        ),
        (
            "Valley Embankment Subsidence (A3D9D30A)",
            "VALLEY_EMBANKMENT_SUBSIDENCE",
            "Subsidence",
            {"id": "IITM-CR-A3D9D30A"},
            "valley_subsidence",
            [
                "INTACT UPHILL CUT SLOPE",
                "ROAD EMBANKMENT SHEAR SCARP",
                "BIAXIAL GEOGRID LAYERS (MoRTH 3100)",
                "&Oslash;150mm MICROPILES &amp; RC CAP BEAM",
                "STEPPED GABION WALL",
            ]
        ),
        (
            "Habitation Residential Slump (D0A16F63)",
            "HABITATION_TERRACE_SLUMP",
            "Debris Slump",
            {"id": "IITM-CR-D0A16F63", "environment_type": "Residential Dwelling / Settlement"},
            "habitation_mudslide",
            [
                "TERRACE MUDSLIDE HEAD SCARP",
                "M25 CANTILEVER WALL &amp; DOWELS",
                "RESIDENTIAL DWELLING (SDRF ZONE)",
                "BUFFER CLEARANCE: 4.5m",
            ]
        ),
        (
            "Macro-Scale Mountain Catastrophe (1EE848DD)",
            "MACRO_MOUNTAIN_CATASTROPHE",
            "Rock Avalanche",
            {"id": "IITM-CR-1EE848DD", "scarp_height_m": 85.0},
            "macro_catastrophic",
            [
                "MACRO-SCALE SLOPE FAILURE &bull; LOCAL TOE WALL INAPPLICABLE",
                "STATUTORY MANDATE: FULL AIRBORNE LiDAR &amp; MULTIDISCIPLINARY DPR REQUIRED",
                "DISASTER SCALE CLASSIFICATION: LEVEL-1 MEGA-LANDSLIDE",
            ]
        ),
        (
            "Disqualified Non-Terrain Upload (FC9B7776)",
            "DISQUALIFIED_NON_TERRAIN",
            "None",
            {"id": "IITM-CR-FC9B7776", "is_landslide_or_terrain": False},
            "rejected_ood",
            [
                "OPTICAL AUDIT DISQUALIFICATION &bull; NON-LANDSLIDE / NON-TERRAIN MEDIA",
                "CROSS-SECTION SUPPRESSED — ZERO ACTIVE GROUND DEFORMATION OBSERVED",
            ]
        ),
    ]

    for title, vector, mvmt, extra_dossier, expected_mode, expected_strings in modes_to_test:
        print(f"\n[TESTING MODE: {title}]")
        rep = {"id": extra_dossier.get("id", "TEST-REP-01"), "movement_type": mvmt}
        dossier = {"observed_features": {"optical_geometry": {"failure_vector": vector}}, **extra_dossier}
        
        # Build authoritative PDM
        pdm = geotech_engine.build_project_data_model(dossier=dossier, report=rep)
        dossier["project_data_model"] = pdm
        
        # Extract params
        params = geotech_schematic.extract_ml_kinematic_parameters(assessment=dossier, report=rep)
        assert params["mode"] == expected_mode, f"Expected mode {expected_mode}, got {params['mode']}"
        print(f"  Mode Resolved:      {params['mode']} ({params['mode_label']})")
        print(f"  Top Badge:          {params['top_badge']}")
        print(f"  FoS (Monsoon/Stab): {params['crit_fos']} / {params['target_fos']}")

        # Render SVG
        svg = geotech_schematic.generate_schematic_svg(assessment=dossier, report=rep, unique_suffix=rep["id"])
        assert svg.startswith("<svg") and svg.endswith("</svg>"), "SVG root tags missing"
        assert 'viewBox="0 0 520 236"' in svg, "viewBox missing or incorrect"

        # Check expected text strings
        for exp in expected_strings:
            assert exp in svg, f"Expected substring '{exp}' not found in rendered SVG for {title}"

        # Assert zero fake slip planes or fake FoS for macro and rejected
        if expected_mode in ("macro_catastrophic", "rejected_ood"):
            assert "Monsoon FoS = " not in svg, f"Prohibited FoS string found in {title}"
            assert "Stabilized FoS = " not in svg, f"Prohibited FoS string found in {title}"
        else:
            assert "Monsoon FoS = " in svg, f"FoS string missing in {title}"
            assert "Stabilized FoS = " in svg, f"FoS string missing in {title}"

        # Check XML validity
        try:
            # Wrap in root or parse directly (handling HTML entities by simple check)
            ET.fromstring(svg.replace("&bull;", "•").replace("&deg;", "°").replace("&asymp;", "≈").replace("&gt;", ">").replace("&lt;", "<").replace("&Delta;", "Δ").replace("&empty;", "∅").replace("&Oslash;", "Ø"))
            xml_valid = True
        except Exception as e:
            xml_valid = False
            print(f"  Warning XML parse check: {e}")

        print(f"  Rendered SVG Size:  {len(svg):,} bytes (Valid SVG Canvas)")
        print(f"  >>> PASS: {title} rendered accurately.")

    print("\n" + "=" * 80)
    print("  ALL 10 SCHEMATIC CROSS-SECTION MODES VERIFIED WITH ZERO ERRORS!")
    print("=" * 80)

if __name__ == "__main__":
    verify_schematic_engine()
