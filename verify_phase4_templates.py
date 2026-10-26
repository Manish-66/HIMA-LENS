"""Verification Suite for Phase 4: Dynamic HTML Template Bindings.
Renders all 3 templates across all 6 archetypes and validates content.
"""
from flask import Flask, render_template
import jinja2
import html
import geotech_engine
import geotech_schematic
import ai_assessment
from app import app

def verify_all_templates():
    print("=" * 80)
    print("  PHASE 4 VERIFICATION: DYNAMIC HTML TEMPLATE BINDINGS ACROSS ALL ARCHETYPES")
    print("=" * 80)

    test_cases = [
        {
            "id": "IITM-CR-6A9B327E",
            "name": "Benchmark Uphill Cut Slope",
            "report": {"id": "IITM-CR-6A9B327E", "district": "Mandi", "movement_type": "Slide"},
            "dossier": {
                "id": "IITM-CR-6A9B327E",
                "telemetry": {"site_road_name": "Mandi Sector — Major District Road (MDR), Chainage RD 17+432 (Km 17/432)", "location_chainage": "RD 17+432 (Km 17/432)"},
                "road_impact": {"carriageway_status": "Restricted Single-Lane (5.25m formation -> 2.30m operable)"},
                "observed_features": {"optical_geometry": {"failure_vector": "UPHILL_CUT_SLOPE"}},
            },
            "expected_ppr": ["Plum Concrete Breast Wall", "20 Nos.", "5 Nos. × 15m"],
            "expected_dsr": ["Above road: Yes", "Mandi Sector", "Page 2 of 2"],
            "expected_boq": ["₹ 11,84,152", "₹ 16,11,414"],
        },
        {
            "id": "IITM-CR-A3D9D30A",
            "name": "Valley Road Embankment Subsidence",
            "report": {"id": "IITM-CR-A3D9D30A", "district": "Shimla", "movement_type": "Subsidence"},
            "dossier": {
                "id": "IITM-CR-A3D9D30A",
                "observed_features": {
                    "optical_geometry": {
                        "failure_vector": "VALLEY_EMBANKMENT_SUBSIDENCE",
                        "scarp_height_m": 7.5,
                        "affected_length_m": 25.0,
                    }
                },
                "road_impact": {"carriageway_status": "Outer Lane Subsided (Single Lane Operable)"},
            },
            "expected_ppr": ["Stepped PVC-Coated Wire Gabion Retaining Wall", "RC Micropiles", "biaxial polymeric geogrid"],
            "expected_dsr": ["Below road: Yes", "Fill: Yes"],
            "expected_boq": ["Gabion", "Micropile"],
        },
        {
            "id": "IITM-CR-37541B33",
            "name": "Cliff Rockfall & Topple",
            "report": {"id": "IITM-CR-37541B33", "district": "Kinnaur", "movement_type": "Fall"},
            "dossier": {
                "id": "IITM-CR-37541B33",
                "observed_features": {
                    "optical_geometry": {
                        "failure_vector": "CLIFF_ROCKFALL_TOPPLE",
                        "scarp_height_m": 16.0,
                        "affected_length_m": 24.0,
                        "cut_slope_angle_deg": 78.0,
                    }
                },
                "road_impact": {"carriageway_status": "Talus Scree Obstructing Corridor"},
            },
            "expected_ppr": ["Rock Mass Scaling", "Crest Anchor Bolting", "Dynamic Flexible Ring-Net Rockfall Catch Barrier"],
            "expected_dsr": ["Above road: Yes", "Cut: Yes"],
            "expected_boq": ["rock bolts", "Catch Barrier"],
        },
        {
            "id": "IITM-CR-D0A16F63",
            "name": "Habitation Residential Terrace Slump",
            "report": {"id": "IITM-CR-D0A16F63", "district": "Kangra", "movement_type": "Slide"},
            "dossier": {
                "id": "IITM-CR-D0A16F63",
                "environment_type": "Residential Dwelling / Settlement",
                "observed_features": {
                    "optical_geometry": {
                        "failure_vector": "HABITATION_TERRACE_SLUMP",
                        "scarp_height_m": 6.4,
                        "affected_length_m": 20.0,
                    }
                },
            },
            "expected_ppr": ["Residential Dwelling Settlement Zone", "M25 RC Cantilever Debris Deflector Wall", "Upper Terrace Doweling"],
            "expected_dsr": ["Residential Settlement Access", "Page 2 of 2"],
            "expected_boq": ["Debris Deflector Wall"],
        },
        {
            "id": "IITM-CR-1EE848DD",
            "name": "Macro-Scale Mountain Catastrophe",
            "report": {"id": "IITM-CR-1EE848DD", "district": "Kullu", "movement_type": "Debris Flow"},
            "dossier": {
                "id": "IITM-CR-1EE848DD",
                "observed_features": {
                    "optical_geometry": {
                        "failure_vector": "MACRO_MOUNTAIN_CATASTROPHE",
                        "scarp_height_m": 85.0,
                        "estimated_volume_m3": 25000.0,
                    }
                },
            },
            "expected_ppr": ["LEVEL-1 MULTIDISCIPLINARY DPR RECONNAISSANCE MANDATE"],
            "expected_dsr": ["Slope & Material Characteristics", "Page 2 of 2"],
            "expected_boq": ["CIVIL WORKS ESTIMATION SUSPENDED", "MACRO-SCALE CATASTROPHIC SLOPE FAILURE"],
        },
        {
            "id": "IITM-CR-FC9B7776",
            "name": "Disqualified Non-Terrain / False Alarm",
            "report": {"id": "IITM-CR-FC9B7776", "district": "Shimla", "movement_type": "None"},
            "dossier": {
                "id": "IITM-CR-FC9B7776",
                "is_landslide_or_terrain": False,
                "validation_status": "INVALID_NON_TERRAIN_IMAGE",
                "observed_features": {
                    "optical_geometry": {
                        "failure_vector": "DISQUALIFIED_NON_TERRAIN",
                    }
                },
            },
            "expected_ppr": ["OPTICAL AUDIT DISQUALIFICATION"],
            "expected_dsr": ["OPTICAL AUDIT DISQUALIFICATION", "Page 2 of 2"],
            "expected_boq": ["CIVIL WORKS ESTIMATION SUSPENDED"],
        },
    ]

    with app.test_request_context():
        for tc in test_cases:
            print(f"\n[TESTING TEMPLATES FOR: {tc['name']} ({tc['id']})]")
            rep = tc["report"]
            raw_dossier = tc["dossier"]
            dossier = ai_assessment.normalize_assessment_structure(raw_dossier, rep)
            dossier["schematic_svg"] = geotech_schematic.generate_schematic_svg(dossier, rep, unique_suffix=rep["id"])

            # 1. Render PPR
            html_ppr = render_template("pwd_sheet.html", report=rep, assessment=dossier)
            un_ppr = html.unescape(html_ppr)
            print(f"  PPR rendered cleanly ({len(html_ppr):,} bytes)")
            for exp in tc["expected_ppr"]:
                assert exp in html_ppr or exp in un_ppr, f"PPR failed to contain expected string: '{exp}'"

            # 2. Render DSR
            html_dsr = render_template("archive/pwd_sheet_v1.html", report=rep, assessment=dossier)
            un_dsr = html.unescape(html_dsr)
            print(f"  DSR rendered cleanly ({len(html_dsr):,} bytes)")
            for exp in tc["expected_dsr"]:
                assert exp in html_dsr or exp in un_dsr, f"DSR failed to contain expected string: '{exp}'"

            # 3. Render BOQ
            html_boq = render_template("boq_sheet.html", report=rep, assessment=dossier)
            un_boq = html.unescape(html_boq)
            print(f"  BOQ rendered cleanly ({len(html_boq):,} bytes)")
            for exp in tc["expected_boq"]:
                assert exp in html_boq or exp in un_boq, f"BOQ failed to contain expected string: '{exp}'"

            print(f"  >>> PASS: All 3 templates verified for {tc['name']}.")

    print("\n" + "=" * 80)
    print("  ALL 3 TEMPLATES RENDER PERFECTLY ACROSS ALL 6 GEOTECHNICAL ARCHETYPES!")
    print("=" * 80)

if __name__ == "__main__":
    verify_all_templates()
