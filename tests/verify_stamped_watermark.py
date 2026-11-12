import sys
sys.path.insert(0, '.')

from app import app
from core.supabase_db import fetch_report_by_id
import core.ai_assessment as ai_assessment
import core.stamped_evidence as stamped_evidence

def test_stamping_and_routes():
    test_ids = ["IITM-CR-6A9B327E", "IITM-CR-7510D90F", "IITM-CR-4A7AFCF5", "IITM-CR-9952AEAC"]
    
    print("=== 1. VERIFYING STRICT SOURCE OF TRUTH & STAMPING ===")
    for rep_id in test_ids:
        rep = fetch_report_by_id(rep_id)
        if not rep:
            print(f"Skipping {rep_id} (not found in DB)")
            continue
        
        # Verify extraction of coordinates and datetime
        coords = ai_assessment._extract_report_coordinates(rep)
        date_str, time_str = ai_assessment._extract_survey_datetime(rep)
        print(f"\nReport: {rep_id}")
        print(f"  Submitted lat/lng: {rep.get('latitude')}, {rep.get('longitude')}")
        print(f"  Extracted coords:  {coords[0]:.5f} N, {coords[1]:.5f} E")
        print(f"  Submitted inc_dt:  {rep.get('incident_date')}")
        print(f"  Extracted dt/tm:   {date_str} • {time_str}")
        print(f"  Submitted district:{rep.get('district')}")
        
        telem = {
            "coordinates_dec": f"{coords[0]:.5f}° N, {coords[1]:.5f}° E",
            "report_reference": rep_id,
            "inspection_date": date_str,
            "timestamp_time": time_str,
            "district": rep.get("district") or "Mandi"
        }
        
        photo_url = rep.get("photo_url")
        if photo_url:
            stamped = stamped_evidence.get_stamped_image_url(photo_url, rep_id, 0, telem, force_refresh=True)
            print(f"  Stamped URL:       {stamped}")
            full_p = stamped_evidence.STAMPED_DIR / f"stamped_{rep_id}_0.jpg"
            if full_p.exists():
                print(f"  File size on disk: {full_p.stat().st_size:,} bytes")
                from PIL import Image
                with Image.open(full_p) as im:
                    print(f"  Dimensions:        {im.size[0]}x{im.size[1]} px")
            else:
                print(f"  WARNING: File {full_p} not created!")

    print("\n=== 2. VERIFYING FLASK ROUTES & TEMPLATE SANITIZATION ===")
    client = app.test_client()
    
    # Test PWD sheet for 6A9B
    resp = client.get("/report/pwd-sheet/IITM-CR-6A9B327E")
    assert resp.status_code == 200, f"Expected 200 but got {resp.status_code}"
    html = resp.get_data(as_text=True)
    
    # Verify outside frames are purged from Section 10 body
    assert 'class="photo-top-bar"' not in html, "ERROR: class='photo-top-bar' still present in HTML body!"
    assert 'class="photo-caption-bar"' not in html, "ERROR: class='photo-caption-bar' still present in HTML body!"
    assert 'class="sec10-split-plate"' not in html, "ERROR: class='sec10-split-plate' still present in HTML body!"
    
    # Verify no double watermark when stamped photo is loaded
    if "stamped_IITM-CR-6A9B327E_0.jpg" in html:
        # In section 10, photo-survey-watermark should NOT be rendered
        sec10_snippet = html[html.find("10. Field Photographic Evidence"):html.find("11. Empirical")]
        assert "photo-survey-watermark" not in sec10_snippet, "ERROR: Duplicate photo-survey-watermark rendered over stamped photo in Section 10!"
        print("  PASS: Section 10 is free of outside frames (.photo-top-bar, .photo-caption-bar) and duplicate HTML watermark.")

    # Test Stamped Photo Endpoint
    photo_resp = client.get("/api/reports/IITM-CR-6A9B327E/stamped-photo/0")
    assert photo_resp.status_code == 200, f"Expected 200 from stamped photo endpoint, got {photo_resp.status_code}"
    assert photo_resp.content_type == "image/jpeg", f"Expected image/jpeg, got {photo_resp.content_type}"
    print(f"  PASS: /api/reports/IITM-CR-6A9B327E/stamped-photo/0 served valid JPEG ({len(photo_resp.data):,} bytes).")

    # Test report.html modal
    report_resp = client.get("/report")
    assert report_resp.status_code == 200
    report_html = report_resp.get_data(as_text=True)
    assert 'id="detail-coords-box"' in report_html, "ERROR: detail-coords-box ID missing from report.html!"
    print("  PASS: /report modal template verified.")

    print("\nALL VERIFICATION CHECKS PASSED PERFECTLY!")

if __name__ == "__main__":
    test_stamping_and_routes()
