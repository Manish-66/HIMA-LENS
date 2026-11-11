import os
import sys
# Ensure workspace root is in python path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
CORE_DIR = os.path.join(ROOT_DIR, 'core')
if CORE_DIR not in sys.path:
    sys.path.insert(0, CORE_DIR)

"""
Verification Suite: Multi-Photo Geographic & Optical Coherence Guardrails
Tests:
1. Photogrammetry Engine: EXIF GPS parsing & Haversine distance calculations
2. Backend API: POST /api/reports pairwise EXIF distance check (>250m rejection)
3. Backend API: POST /api/reports metadata coordinate extraction (taking coords from photo metadata)
4. AI Assessment Dossier: INCONSISTENT_MULTI_SITE_IMAGES rejection docket generation
5. Geotechnical Engine: Project Data Model zeroing and civil works suspension
6. Geotechnical Schematic: SVG vector plate with multi-site suppression notice
7. Template Rendering: PWD sheet & BOQ sheet rendering of multi-site inconsistency banner
"""

import io
import json
import sys
from PIL import Image, ExifTags

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import photogrammetry_engine
import ai_assessment
import geotech_engine
import geotech_schematic
from app import app, resolve_nearest_hp_district


def _create_synthetic_jpeg_with_gps(lat: float, lon: float) -> bytes:
    img = Image.new("RGB", (320, 240), color=(120, 160, 200))
    def to_deg_float(val):
        deg = int(abs(val))
        min_f = (abs(val) - deg) * 60
        min_i = int(min_f)
        sec_f = round((min_f - min_i) * 60, 4)
        return (float(deg), float(min_i), float(sec_f))

    exif = img.getexif()
    gps_ifd = exif.get_ifd(ExifTags.IFD.GPSInfo)
    gps_ifd[1] = 'N' if lat >= 0 else 'S'
    gps_ifd[2] = to_deg_float(lat)
    gps_ifd[3] = 'E' if lon >= 0 else 'W'
    gps_ifd[4] = to_deg_float(lon)
    exif[ExifTags.Base.GPSInfo] = gps_ifd

    buf = io.BytesIO()
    img.save(buf, format="JPEG", exif=exif)
    return buf.getvalue()


def _create_plain_jpeg() -> bytes:
    img = Image.new("RGB", (320, 240), color=(180, 180, 180))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def run_guardrail_verification():
    print("=" * 80)
    print("  VERIFYING MULTI-PHOTO SITE COHERENCE & EXIF GPS GUARDRAILS")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # SUITE 1: Photogrammetry Engine EXIF & Haversine
    # -------------------------------------------------------------------------
    print("\n[SUITE 1: Photogrammetry Engine EXIF & Haversine]")
    img_bytes_1 = _create_synthetic_jpeg_with_gps(31.7754, 76.9861)
    img_bytes_2_far = _create_synthetic_jpeg_with_gps(31.7820, 76.9920)
    img_bytes_3_near = _create_synthetic_jpeg_with_gps(31.7756, 76.9863)

    coords_1 = photogrammetry_engine.extract_exif_gps_coordinates(img_bytes_1)
    coords_far = photogrammetry_engine.extract_exif_gps_coordinates(img_bytes_2_far)
    coords_near = photogrammetry_engine.extract_exif_gps_coordinates(img_bytes_3_near)

    assert coords_1 is not None and abs(coords_1[0] - 31.7754) < 0.001
    assert coords_far is not None and abs(coords_far[0] - 31.7820) < 0.001
    assert coords_near is not None and abs(coords_near[0] - 31.7756) < 0.001

    dist_far = photogrammetry_engine.haversine_distance_meters(coords_1[0], coords_1[1], coords_far[0], coords_far[1])
    dist_near = photogrammetry_engine.haversine_distance_meters(coords_1[0], coords_1[1], coords_near[0], coords_near[1])

    print(f"  [✓ PASS] EXIF GPS extraction successful: coords_1 = {coords_1}")
    print(f"  [✓ PASS] Distant pair distance: {dist_far:.1f} m (> 250m threshold)")
    print(f"  [✓ PASS] Co-located pair distance: {dist_near:.1f} m (<= 250m threshold)")
    assert dist_far > 250.0
    assert dist_near <= 250.0

    # -------------------------------------------------------------------------
    # SUITE 2: Backend API POST /api/reports EXIF Delta Check
    # -------------------------------------------------------------------------
    print("\n[SUITE 2: Backend API POST /api/reports EXIF Delta Check]")
    client = app.test_client()

    data_rejected = {
        'latitude': '31.7754',
        'longitude': '76.9861',
        'district': 'Mandi',
        'severity': 'Critical',
        'photos': [
            (io.BytesIO(img_bytes_1), 'photo_site_a.jpg'),
            (io.BytesIO(img_bytes_2_far), 'photo_site_b.jpg'),
        ]
    }
    resp_rej = client.post('/api/reports', data=data_rejected, content_type='multipart/form-data')
    assert resp_rej.status_code == 400, f"Expected 400 for disparate photos, got {resp_rej.status_code}"
    res_json = resp_rej.get_json()
    assert res_json.get("error") == "INCONSISTENT_IMAGE_LOCATIONS"
    print(f"  [✓ PASS] POST /api/reports strictly rejected disparate photos (>250m apart): HTTP 400 {res_json.get('error')}")

    # -------------------------------------------------------------------------
    # SUITE 3: Metadata Coordinate Extraction (Taking Coordinates from Metadata)
    # -------------------------------------------------------------------------
    print("\n[SUITE 3: Metadata Coordinate Extraction (Taking Coordinates from Metadata)]")
    # Submitting with NO latitude/longitude in the form, relying completely on photo EXIF
    data_no_coords = {
        'severity': 'Moderate',
        'description': 'Road cut slip near Pandoh reservoir with photo metadata',
        'photos': [
            (io.BytesIO(img_bytes_1), 'photo_with_gps.jpg'),
        ]
    }
    resp_meta = client.post('/api/reports', data=data_no_coords, content_type='multipart/form-data')
    assert resp_meta.status_code == 201, f"Expected 201 for photo metadata coordinates, got {resp_meta.status_code}: {resp_meta.get_data(as_text=True)}"
    meta_json = resp_meta.get_json()
    created_rep = meta_json.get("report", {})
    assert abs(created_rep.get("latitude") - 31.7754) < 0.001
    assert abs(created_rep.get("longitude") - 76.9861) < 0.001
    assert created_rep.get("coordinates_source") == "photo_metadata_exif"
    assert created_rep.get("district") == "Mandi"
    print(f"  [✓ PASS] POST /api/reports auto-extracted coordinates from photo metadata: ({created_rep.get('latitude')}, {created_rep.get('longitude')})")
    print(f"  [✓ PASS] Report marked with coordinates_source='{created_rep.get('coordinates_source')}', district auto-resolved to '{created_rep.get('district')}'")

    # Submitting with plain photo (no GPS) and no coordinates should return 400
    plain_jpeg = _create_plain_jpeg()
    data_empty_coords = {
        'severity': 'Moderate',
        'photos': [
            (io.BytesIO(plain_jpeg), 'plain_no_gps.jpg'),
        ]
    }
    resp_err = client.post('/api/reports', data=data_empty_coords, content_type='multipart/form-data')
    assert resp_err.status_code == 400
    assert resp_err.get_json().get("error") == "INVALID_COORDINATES"
    print(f"  [✓ PASS] POST /api/reports correctly rejected missing coordinates when photo lacks metadata: HTTP 400 INVALID_COORDINATES")

    # Real-time extraction endpoint POST /api/extract-exif-coords
    resp_api_gps = client.post('/api/extract-exif-coords', data={'photo': (io.BytesIO(img_bytes_1), 'gps.jpg')}, content_type='multipart/form-data')
    assert resp_api_gps.status_code == 200
    gps_data = resp_api_gps.get_json()
    assert gps_data.get("has_gps") is True
    assert abs(gps_data.get("latitude") - 31.7754) < 0.001
    assert abs(gps_data.get("longitude") - 76.9861) < 0.001
    assert gps_data.get("district") == "Mandi"
    assert gps_data.get("is_in_hp") is True
    print(f"  [✓ PASS] POST /api/extract-exif-coords successfully extracted GPS: ({gps_data.get('latitude')}, {gps_data.get('longitude')}), district={gps_data.get('district')}")

    resp_api_nogps = client.post('/api/extract-exif-coords', data={'photo': (io.BytesIO(plain_jpeg), 'no_gps.jpg')}, content_type='multipart/form-data')
    assert resp_api_nogps.status_code == 200
    assert resp_api_nogps.get_json().get("has_gps") is False
    print(f"  [✓ PASS] POST /api/extract-exif-coords correctly reports has_gps=False when image lacks metadata")

    # -------------------------------------------------------------------------
    # SUITE 4: VLM Coherence Rejection Docket Generation
    # -------------------------------------------------------------------------
    print("\n[SUITE 4: VLM Coherence Rejection Docket Generation]")
    raw_report = {
        "report_id": "TEST-DISPARATE-001",
        "latitude": 31.7754,
        "longitude": 76.9861,
        "district": "Mandi",
        "highway": "NH-154",
        "lithology": "Sandstone / Siltstone",
        "photo_urls": [
            "https://storage.supabase.co/photo1.jpg",
            "https://storage.supabase.co/photo2.jpg"
        ]
    }
    dossier = ai_assessment.build_rejected_assessment_dossier(
        raw_report,
        detected_content="Disparate Landslide Sites",
        rejection_reason="Images depict completely different landslide events with distinct lithologies and valley orientations.",
        validation_status="INCONSISTENT_MULTI_SITE_IMAGES"
    )

    assert dossier["validation_status"] == "INCONSISTENT_MULTI_SITE_IMAGES"
    assert dossier["is_landslide_or_terrain"] is False
    assert dossier["is_same_incident"] is False
    assert dossier["financial_summary"]["total_civil_remediation_outlay"] == 0.0
    assert ("MULTI-SITE INCONSISTENCY" in dossier["senior_engineer_remarks"] or 
            "disparate" in dossier["senior_engineer_remarks"].lower())
    print("  [✓ PASS] Dossier correctly marked: validation_status='INCONSISTENT_MULTI_SITE_IMAGES'")
    print(f"  [✓ PASS] is_same_incident={dossier['is_same_incident']}, Outlay=Rs {dossier['financial_summary']['total_civil_remediation_outlay']}")

    # -------------------------------------------------------------------------
    # SUITE 5: Geotechnical Engine PDM Disqualification
    # -------------------------------------------------------------------------
    print("\n[SUITE 5: Geotechnical Engine PDM Disqualification]")
    pdm = geotech_engine.build_project_data_model(dossier=dossier, report=raw_report)
    assert pdm["is_applicable"] is False
    assert pdm["failure_vector"] in ("NON_TERRAIN_REJECTED", "DISQUALIFIED_NON_TERRAIN")
    assert pdm["financial_summary"]["total_civil_remediation_outlay"] == 0.0
    print(f"  [✓ PASS] PDM is_applicable={pdm['is_applicable']}, Outlay=Rs {pdm['financial_summary']['total_civil_remediation_outlay']}")

    # -------------------------------------------------------------------------
    # SUITE 6: Geotechnical Schematic SVG Generation
    # -------------------------------------------------------------------------
    print("\n[SUITE 6: Geotechnical Schematic SVG Generation]")
    svg_output = geotech_schematic.generate_schematic_svg(assessment=dossier, report=raw_report)
    assert "MULTI-SITE INCONSISTENCY" in svg_output
    assert "DISPARATE SITES" in svg_output
    assert "CROSS-SECTION SUPPRESSED" in svg_output
    print(f"  [✓ PASS] Schematic SVG correctly renders Multi-Site Inconsistency Notice ({len(svg_output)} bytes)")

    # -------------------------------------------------------------------------
    # SUITE 7: Template Rendering Check
    # -------------------------------------------------------------------------
    print("\n[SUITE 7: Template Rendering Check]")
    with app.test_request_context():
        from flask import render_template
        normalized_dossier = ai_assessment.normalize_assessment_structure(dossier, raw_report)
        boq = normalized_dossier.get("cost_estimate_boq") or {}
        pwd_html = render_template("pwd_sheet.html", assessment=normalized_dossier, report=raw_report, pdm=pdm, boq=boq)
        boq_html = render_template("boq_sheet.html", assessment=normalized_dossier, report=raw_report, pdm=pdm, boq=boq)

        assert "MULTI-SITE INCONSISTENCY DETECTED" in pwd_html
        assert "DISPARATE SITES" in pwd_html
        assert "DISQUALIFIED" in pwd_html

        assert "MULTI-SITE INCONSISTENCY DETECTED" in boq_html
        assert "DISPARATE SITES" in boq_html

    print(f"  [✓ PASS] PWD Sheet rendered cleanly ({len(pwd_html)} bytes) with active Disparate Sites Alert")
    print(f"  [✓ PASS] BOQ Sheet rendered cleanly ({len(boq_html)} bytes) with active Disparate Sites Alert")

    # Clean up any test records created during test
    from config import COMMUNITY_REPORTS_PATH
    import os
    if os.path.exists(COMMUNITY_REPORTS_PATH):
        try:
            with open(COMMUNITY_REPORTS_PATH, "r", encoding="utf-8") as f:
                records = json.load(f)
            cleaned = [r for r in records if "Road cut slip near Pandoh reservoir" not in r.get("description", "")]
            with open(COMMUNITY_REPORTS_PATH, "w", encoding="utf-8") as f:
                json.dump(cleaned, f, indent=2)
        except Exception:
            pass

    print("\n" + "=" * 80)
    print("  ALL 7 MULTI-PHOTO SITE COHERENCE & METADATA COORDINATE SUITES PASSED PERFECTLY!")
    print("=" * 80)


if __name__ == "__main__":
    run_guardrail_verification()
