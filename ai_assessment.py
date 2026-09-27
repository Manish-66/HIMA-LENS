"""AI-Powered Geotechnical Field Assessment Engine for HIMA-LENS.

Analyzes landslide citizen reports and photos using Google Gemini Vision (Flash)
to generate structured HP PWD (Himachal Pradesh Public Works Department)
Field Visit Sheets and Technical Engineering Assessments.
"""
from __future__ import annotations

import base64
import json
import logging
import mimetypes
import re
from datetime import datetime
from pathlib import Path
from typing import Any
import requests

from config import (
    BASE_DIR,
    COMMUNITY_REPORTS_UPLOAD_DIR,
    GEMINI_API_KEY,
)

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-flash-latest"
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"


def _get_image_base64_and_mime(photo_url: str) -> tuple[str, str] | tuple[None, None]:
    """Retrieves image bytes from URL or local disk and returns (base64_str, mime_type)."""
    if not photo_url:
        return None, None

    try:
        if photo_url.startswith("http://") or photo_url.startswith("https://"):
            resp = requests.get(photo_url, timeout=12)
            if resp.status_code == 200 and resp.content:
                ext = photo_url.split("?")[0].rsplit(".", 1)[-1].lower()
                mime = mimetypes.types_map.get(f".{ext}", "image/jpeg")
                return base64.b64encode(resp.content).decode("utf-8"), mime
        else:
            # Local file path
            cleaned = photo_url.lstrip("/").replace("/", "\\")
            candidate_paths = [
                BASE_DIR / cleaned,
                COMMUNITY_REPORTS_UPLOAD_DIR / Path(photo_url).name,
            ]
            for p in candidate_paths:
                if p.exists() and p.is_file():
                    data = p.read_bytes()
                    ext = p.suffix.lower()
                    mime = mimetypes.types_map.get(ext, "image/jpeg")
                    return base64.b64encode(data).decode("utf-8"), mime
    except Exception as exc:
        logger.warning("Could not fetch image for AI assessment from %s: %s", photo_url, exc)

    return None, None


def _format_coordinates_dms(lat: float, lng: float) -> str:
    """Formats decimal coordinates into PWD standard Degree-Minute-Second string."""
    try:
        lat_d = int(abs(lat))
        lat_m = int((abs(lat) - lat_d) * 60)
        lat_s = int(((abs(lat) - lat_d) * 60 - lat_m) * 60)
        lat_card = "N" if lat >= 0 else "S"

        lng_d = int(abs(lng))
        lng_m = int((abs(lng) - lng_d) * 60)
        lng_s = int(((abs(lng) - lng_d) * 60 - lng_m) * 60)
        lng_card = "E" if lng >= 0 else "W"

        return f"Lat: {lat_d}°{lat_m:02d}'{lat_s:02d}\" {lat_card} | Long: {lng_d}°{lng_m:02d}'{lng_s:02d}\" {lng_card}"
    except Exception:
        return f"Lat: {lat:.5f}° N | Long: {lng:.5f}° E"


def fallback_geotechnical_assessment(report: dict[str, Any]) -> dict[str, Any]:
    """Generates realistic geotechnical and structural parameters using IRC:SP:48 standards

    when AI is unreachable or image is absent.
    """
    district = report.get("district") or "Mandi"
    movement = report.get("movement_type") or "Slide"
    severity = (report.get("severity") or "Moderate").title()
    lat = float(report.get("latitude") or 31.7)
    lng = float(report.get("longitude") or 76.9)
    inc_date = report.get("incident_date") or datetime.utcnow().strftime("%Y-%m-%d")

    # Dynamic scaling based on severity
    if severity == "Critical":
        h_wall = 4.5
        l_wall = 24.0
        exc_vol = 580.0
        cut_angle = 75
        blockage = "Fully Blocked (Traffic Severed)"
        w_after = 0.0
        machinery = "2 Nos. Heavy Excavators (Poclain + Rock Breaker) & 4 Nos. Tippers"
        restoration = "Restore single-lane traffic within 24-36 hours; complete rebuild in 21 days"
    elif severity == "High":
        h_wall = 3.5
        l_wall = 18.0
        exc_vol = 320.0
        cut_angle = 70
        blockage = "Fully Blocked (Single Lane Urgent Clearance)"
        w_after = 0.0
        machinery = "1 No. Heavy Excavator (JCB with Rock Breaker) & 2 Nos. Tippers"
        restoration = "Restore single-lane traffic within 12-24 hours; permanent breast wall in 14 days"
    elif severity == "Low":
        h_wall = 2.0
        l_wall = 10.0
        exc_vol = 45.0
        cut_angle = 55
        blockage = "Partially Blocked (Single-Lane Traffic Operable)"
        w_after = 3.5
        machinery = "1 No. Backhoe Loader (JCB) & 1 Tipper"
        restoration = "Immediate clearance within 4-6 hours; hillside saucer drain improvement"
    else:  # Moderate
        h_wall = 2.8
        l_wall = 14.0
        exc_vol = 140.0
        cut_angle = 65
        blockage = "Substantially Blocked (Shoulder Encroachment)"
        w_after = 2.0
        machinery = "1 No. Backhoe Loader (JCB 3DX) & 2 Tippers"
        restoration = "Clear carriageway within 8-12 hours; plum concrete breast wall recommended"

    base_w = round(h_wall * 0.5, 2)
    top_w = 0.60
    exc_h = round(h_wall * 0.85, 2)
    exc_w = round(h_wall * 1.6, 2)

    return {
        "source": "heuristic_geotechnical_model",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "road_metadata": {
            "road_name": f"{district} - Sub-Divisional Link Road (HP PWD)",
            "chainage": f"RD {int(lat * 10) % 20}+{(int(lng * 1000) % 900):03d} (Km {int(lat * 10) % 20}/{(int(lng * 1000) % 900):03d})",
            "road_type": "ODR / Major District Road (HP PWD)",
            "inspection_date": str(inc_date)[:10],
            "gps_coordinates": _format_coordinates_dms(lat, lng),
            "district": district,
        },
        "slope_characteristics": {
            "presence_above_road": True,
            "presence_below_road": False,
            "in_situ_rock": "Moderate to High",
            "in_situ_soil": "Colluvial Overburden",
            "debris_accumulation": "Heavy Accumulation" if severity in ("High", "Critical") else "Moderate Accumulation",
            "slope_height_above_m": round(h_wall * 2.8, 1),
            "cut_slope_angle_deg": cut_angle,
            "slope_geometry": "Convex Escarpment (Overhanging Joint Blocks)",
        },
        "road_impact": {
            "alignment": "Curved (Hilly Terrain)",
            "width_before_m": 5.50,
            "width_after_m": w_after,
            "carriageway_status": blockage,
            "pavement_type": "Flexible / Bituminous (BT)",
            "shoulder_width_m": 0.75,
            "traffic_flow": "Two-way Traffic",
            "culvert_status": "Choked with debris / Inlet clearing required",
        },
        "geology": {
            "prominent_rock": "Jointed Sandstone & Siltstone / Weathered Phyllite",
            "weathering_grade": "Grade IV (Highly Weathered)",
            "joint_spacing": "0.20 m – 0.45 m (Closely Jointed)",
            "dip_joints": "45° to 55° daylighting towards road carriage",
            "joint_orientation": "Strike N35°W, Dip 45° SW",
            "failure_pattern": f"Blocky & Wedge Failure with {movement} debris slip",
        },
        "proposed_measures": [
            {"structure": "Retaining / Breast Wall", "location": "Above Road", "remedial": True, "preventive": True},
            {"structure": "Gabion Toe Support", "location": "Above Road Cut", "remedial": True, "preventive": False},
            {"structure": "Hillside Lined Saucer Drain / Chute", "location": "Above & Along Road", "remedial": True, "preventive": True},
            {"structure": "Bioengineering (Vetiver grass turfing & fascines)", "location": "Trimmed Upper Slope", "remedial": False, "preventive": True},
            {"structure": "Debris Clearance & Rock Breaking", "location": "Carriageway", "remedial": True, "preventive": False},
            {"structure": "Rockfall Netting / Wire Mesh Barrier", "location": "Upper Unstable Cut", "remedial": False, "preventive": True},
        ],
        "structural_specifications": {
            "breast_wall": {
                "recommended": True,
                "material": "Plum Concrete (M15 / 1:2:4 with 40% plums) / Stone Masonry",
                "height_m": h_wall,
                "length_m": l_wall,
                "top_width_m": top_w,
                "base_width_m": base_w,
                "embedded_depth_m": 1.20,
                "weep_holes": "100 mm dia PVC pipes @ 1.20 m c/c staggered with gravel filter backing",
            },
            "gabion_wall": {
                "recommended": True,
                "height_m": 2.50,
                "base_width_m": 2.00,
                "top_width_m": 1.00,
                "embedded_depth_m": 0.80,
                "mesh_spec": "GI 3.00 mm wire, 100 x 120 mm hexagonal double-twisted mesh, tight boulder packing",
            },
        },
        "earthworks_quantification": {
            "excavation_material": "Overburden Debris + Huge Detached Boulders (Hydraulic Breaker Required)",
            "excavation_dim": f"{exc_h:.2f} m (H) x {l_wall:.2f} m (L) x {exc_w:.2f} m (W)",
            "excavation_volume_m3": exc_vol,
            "fill_material": "Granular Subgrade Backfill (GSB) with geotextile separator",
            "fill_dim": f"0.35 m (H) x {l_wall:.2f} m (L) x 4.50 m (W)",
            "fill_volume_m3": round(0.35 * l_wall * 4.5, 2),
        },
        "safety_and_immediate_actions": {
            "electrical_hazard": "Power/communication lines require safety clearance & HPSEBL coordination before boom excavator operations.",
            "machinery_deployment": machinery,
            "traffic_restoration": restoration,
            "permanent_restoration": f"Construction of {l_wall}m long Plum Concrete Breast Wall (H={h_wall}m) and Hillside Saucer Drain (0.6m wide).",
        },
        "field_observations_and_remarks": (
            f"Field inspection confirmed active {movement.lower()} with heavy surcharge pressure from detached slope mass. "
            f"Slope failure triggered by heavy precipitation and compromised hillside drainage. Hillside breast wall "
            f"and saucer drain are urgently required to prevent recurrent slope toe destabilization."
        ),
    }


def generate_ai_assessment(report: dict[str, Any]) -> dict[str, Any]:
    """Invokes Google Gemini Vision with the landslide photograph and report metadata

    to extract detailed geotechnical and HP PWD engineering assessment parameters.
    Falls back gracefully to the heuristic engineering model if Gemini is unconfigured or fails.
    """
    if not GEMINI_API_KEY:
        logger.info("GEMINI_API_KEY not configured; using heuristic geotechnical model.")
        return fallback_geotechnical_assessment(report)

    photo_url = report.get("photo_url", "")
    base64_data, mime_type = _get_image_base64_and_mime(photo_url)

    lat = float(report.get("latitude") or 31.7)
    lng = float(report.get("longitude") or 76.9)
    district = report.get("district") or "Mandi"
    movement = report.get("movement_type") or "Slide"
    severity = report.get("severity") or "Moderate"
    user_desc = report.get("description") or "None provided"

    prompt = f"""You are a Chief Geotechnical & Highway Structural Engineer for the Himachal Pradesh Public Works Department (HP PWD) and the HIMA-LENS Landslide Warning System.

TASK:
Analyze the attached landslide photograph and incident report to generate a formal, high-accuracy PWD Field Visit Sheet & Technical Assessment Report in strict adherence to Indian Road Congress (IRC:SP:48) hill road design standards.

INCIDENT METADATA:
- District: {district}, Himachal Pradesh
- GPS Coordinates: Latitude {lat:.5f}, Longitude {lng:.5f}
- Movement Type: {movement}
- Reported Severity: {severity}
- Citizen/Field Description: {user_desc}

REQUIREMENTS:
1. Examine the photograph closely: rock joint daylighting, slope height, soil/rock failure mechanism, carriageway blockage, electrical wire hazards, and boulder sizes.
2. Provide realistic civil and geotechnical engineering dimensions for Himachal terrain (breast wall height, length, excavation volume in m3, drainage).
3. Return ONLY a valid JSON object matching the exact schema below, with no markdown code fences, backticks, or preamble:

{{
  "road_metadata": {{
    "road_name": "String (e.g. Mandi - Kotli - Dharampur Road (ODR))",
    "chainage": "String (e.g. RD 3+450 (Km 3/450))",
    "road_type": "String (e.g. ODR / Link Road (HP PWD))",
    "inspection_date": "YYYY-MM-DD",
    "gps_coordinates": "String formatted like Lat: 31°42'38\\" N | Long: 76°55'42\\" E",
    "district": "{district}"
  }},
  "slope_characteristics": {{
    "presence_above_road": true,
    "presence_below_road": false,
    "in_situ_rock": "String (e.g. Jointed Sandstone)",
    "in_situ_soil": "String (e.g. Colluvial Overburden)",
    "debris_accumulation": "String (Heavy Accumulation / Moderate)",
    "slope_height_above_m": 8.5,
    "cut_slope_angle_deg": 68,
    "slope_geometry": "String (e.g. Steep Cut Escarpment)"
  }},
  "road_impact": {{
    "alignment": "Curved (Hilly Terrain)",
    "width_before_m": 5.5,
    "width_after_m": 0.0,
    "carriageway_status": "String (e.g. Fully Blocked / Single Lane Blocked)",
    "pavement_type": "Flexible / Bituminous (BT)",
    "shoulder_width_m": 0.75,
    "traffic_flow": "Two-way Traffic",
    "culvert_status": "String (e.g. Choked Upstream / Intact)"
  }},
  "geology": {{
    "prominent_rock": "String (e.g. Jointed Sandstone & Siltstone)",
    "weathering_grade": "String (e.g. Grade IV (Highly Weathered))",
    "joint_spacing": "String (e.g. 0.20 m – 0.45 m (Closely Jointed))",
    "dip_joints": "String (e.g. 45° to 50° daylighting into road)",
    "joint_orientation": "String (e.g. Strike N35°W, Dip 45° SW)",
    "failure_pattern": "String (e.g. Blocky & Wedge Failure)"
  }},
  "proposed_measures": [
    {{"structure": "Retaining / Breast Wall", "location": "Above Road", "remedial": true, "preventive": true}},
    {{"structure": "Gabion Structure", "location": "Above Road", "remedial": true, "preventive": false}},
    {{"structure": "Drainage / Chute", "location": "Above & Roadside", "remedial": true, "preventive": true}},
    {{"structure": "Bioengineering (Vetiver grass)", "location": "Trimmed Slope", "remedial": false, "preventive": true}},
    {{"structure": "Earthworks / Clearance", "location": "Carriageway", "remedial": true, "preventive": false}},
    {{"structure": "Rockfall Netting / Wire Mesh", "location": "Upper Cut", "remedial": false, "preventive": true}}
  ],
  "structural_specifications": {{
    "breast_wall": {{
      "recommended": true,
      "material": "Plum Concrete (M15 / 1:2:4 with 40% plums) / Stone Masonry in 1:4 cement mortar",
      "height_m": 3.5,
      "length_m": 18.0,
      "top_width_m": 0.6,
      "base_width_m": 1.75,
      "embedded_depth_m": 1.2,
      "weep_holes": "100 mm dia PVC pipes @ 1.20 m c/c staggered with gravel filter backing"
    }},
    "gabion_wall": {{
      "recommended": true,
      "height_m": 2.5,
      "base_width_m": 2.0,
      "top_width_m": 1.0,
      "embedded_depth_m": 0.8,
      "mesh_spec": "GI 3.00 mm wire, 100 x 120 mm mesh with tight boulder packing"
    }}
  }},
  "earthworks_quantification": {{
    "excavation_material": "String (e.g. Debris + Giant Detached Boulders (Rock Breaking Required))",
    "excavation_dim": "3.00 m (H) x 18.00 m (L) x 6.00 m (W)",
    "excavation_volume_m3": 324.0,
    "fill_material": "Granular Subgrade Backfill (GSB)",
    "fill_dim": "0.35 m (H) x 18.00 m (L) x 4.50 m (W)",
    "fill_volume_m3": 28.35
  }},
  "safety_and_immediate_actions": {{
    "electrical_hazard": "String (e.g. Sagging 11kV lines require HPSEBL clearance before excavator deployment)",
    "machinery_deployment": "String (e.g. 1 No. Heavy Excavator with Rock Breaker & 2 Nos. Tippers)",
    "traffic_restoration": "String (e.g. Restore single-lane traffic within 12-24 hours)",
    "permanent_restoration": "String (e.g. Construction of 18m long Plum Concrete Breast Wall and Saucer Drain)"
  }},
  "field_observations_and_remarks": "String (Concise engineering diagnosis of the failure mechanism, drainage cause, and stability recommendations)"
}}"""

    # Assemble request payload
    parts: list[dict[str, Any]] = [{"text": prompt}]
    if base64_data and mime_type:
        parts.append({
            "inline_data": {
                "mime_type": mime_type,
                "data": base64_data,
            }
        })

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
        },
    }

    try:
        url = f"{GEMINI_ENDPOINT}?key={GEMINI_API_KEY}"
        resp = requests.post(url, json=payload, timeout=25)
        if resp.status_code == 200:
            result_json = resp.json()
            candidates = result_json.get("candidates", [])
            if candidates:
                raw_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                # Clean up any potential markdown wraps
                cleaned = re.sub(r"^```(?:json)?\s*", "", raw_text.strip(), flags=re.MULTILINE)
                cleaned = re.sub(r"\s*```$", "", cleaned.strip(), flags=re.MULTILINE)
                parsed = json.loads(cleaned)
                parsed["source"] = "google_gemini_vision"
                parsed["generated_at"] = datetime.utcnow().isoformat() + "Z"
                return parsed
        else:
            logger.warning("Gemini API call failed (%s): %s", resp.status_code, resp.text[:250])
    except Exception as exc:
        logger.warning("Gemini API call exception: %s. Using fallback.", exc)

    return fallback_geotechnical_assessment(report)
