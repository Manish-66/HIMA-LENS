"""HIMA-LENS Multimodal AI Vision & Geotechnical Assessment Engine.

Performs strict, honest visual analysis of citizen landslide photographs using
Google Gemini Vision. Validates whether the image is actually a geological slope/terrain.
If a non-landslide image (dog, selfie, phone screenshot, indoor object) is submitted,
it explicitly flags it and rejects hallucinating slope parameters.
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

# Ordered list of robust multimodal vision models with automated fallback
GEMINI_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
]


def _get_image_base64_and_mime(photo_url: str) -> tuple[str, str] | tuple[None, None]:
    """Retrieves image bytes from URL or local disk and returns (base64_str, mime_type)."""
    if not photo_url:
        return None, None

    try:
        if photo_url.startswith("http://") or photo_url.startswith("https://"):
            resp = requests.get(photo_url, timeout=14)
            if resp.status_code == 200 and resp.content:
                ext = photo_url.split("?")[0].rsplit(".", 1)[-1].lower()
                mime = mimetypes.types_map.get(f".{ext}", "image/jpeg")
                return base64.b64encode(resp.content).decode("utf-8"), mime
        else:
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
    """Formats decimal coordinates into standard Degree-Minute-Second string."""
    try:
        lat_d = int(abs(lat))
        lat_m = int((abs(lat) - lat_d) * 60)
        lat_s = int(((abs(lat) - lat_d) * 60 - lat_m) * 60)
        lat_card = "N" if lat >= 0 else "S"

        lng_d = int(abs(lng))
        lng_m = int((abs(lng) - lng_d) * 60)
        lng_s = int(((abs(lng) - lng_d) * 60 - lng_m) * 60)
        lng_card = "E" if lng >= 0 else "W"

        return f"{lat_d}°{lat_m:02d}'{lat_s:02d}\" {lat_card}, {lng_d}°{lng_m:02d}'{lng_s:02d}\" {lng_card}"
    except Exception:
        return f"{lat:.5f}° N, {lng:.5f}° E"


def fallback_visual_assessment(report: dict[str, Any]) -> dict[str, Any]:
    """Fallback when AI is completely unreachable. Does NOT fabricate fake slope features

    if no terrain can be confirmed.
    """
    district = report.get("district") or "Himachal Pradesh"
    movement = report.get("movement_type") or "Landslide"
    severity = (report.get("severity") or "Moderate").title()
    lat = float(report.get("latitude") or 31.7)
    lng = float(report.get("longitude") or 76.9)
    inc_date = report.get("incident_date") or datetime.utcnow().strftime("%Y-%m-%d")
    user_desc = report.get("description") or "Citizen field telemetry observation."

    has_photo = bool(report.get("photo_url"))

    return {
        "is_landslide_or_terrain": True if not has_photo else True,
        "validation_status": "TELEMETRY_UNVERIFIED",
        "detected_content": "Field observation submitted by citizen" if not has_photo else "Pending AI optical verification",
        "source": "HIMA-LENS Telemetry Engine",
        "generated_at": datetime.utcnow().strftime("%d %b %Y, %H:%M UTC"),
        "telemetry": {
            "report_id": report.get("id") or "HL-CR-RECORD",
            "district": district,
            "coordinates": _format_coordinates_dms(lat, lng),
            "decimal_coordinates": f"{lat:.5f}° N, {lng:.5f}° E",
            "reported_date": str(inc_date)[:16].replace("T", " "),
            "reported_movement": movement,
            "reported_severity": severity,
            "reporter_name": report.get("reporter_name") or "Anonymous Observer",
            "user_notes": user_desc,
        },
        "visual_analysis": {
            "visible_failure_type": f"{movement} (Citizen Reported)",
            "material_composition": "Pending on-site geological classification",
            "slope_condition": "Reported slope instability in " + district,
            "infrastructure_impact": f"{severity} severity reported by observer",
            "drainage_and_seepage": "Requires on-site drainage inspection",
            "secondary_hazard_risk": "Subject to weather conditions and field evaluation",
        },
        "geotechnical_parameters": {
            "slope_height": "Requires total station / lidar field survey",
            "slope_angle": "Requires clinometer field measurement",
            "rock_structure": "Requires on-site geological strike/dip mapping",
            "debris_volume": "Requires volumetric cross-section survey",
        },
        "recommended_interventions": [
            {"measure": "Ground Field Inspection", "priority": "High", "details": "Deploy local sub-division team to verify reported hazard."},
            {"measure": "Citizen Report Verification", "priority": "Medium", "details": "Validate reported coordinates and roadway clearance status."},
        ],
        "synthesis_remarks": (
            f"Citizen observation recorded for {district} ({severity} {movement.lower()}). "
            f"AI optical verification was unavailable at generation time. Field inspection required to verify terrain impact."
        ),
    }


def generate_ai_assessment(report: dict[str, Any]) -> dict[str, Any]:
    """Invokes Google Gemini Vision with strict instructions:

    1. Determine whether the image actually depicts a landslide or geological slope.
    2. If NOT a landslide (e.g. pet dog, smartphone screenshot, selfie, indoor object),
       reject and clearly identify what the image actually depicts.
    3. If YES, extract ONLY what is genuinely visible in the photograph.
    """
    photo_url = report.get("photo_url", "")
    base64_data, mime_type = _get_image_base64_and_mime(photo_url)

    lat = float(report.get("latitude") or 31.7)
    lng = float(report.get("longitude") or 76.9)
    district = report.get("district") or "Himachal Pradesh"
    movement = report.get("movement_type") or "Landslide"
    severity = report.get("severity") or "Moderate"
    user_desc = report.get("description") or "None recorded"
    report_id = report.get("id") or "HL-CR-RECORD"
    reporter = report.get("reporter_name") or "Anonymous Observer"
    inc_date = report.get("incident_date") or datetime.utcnow().strftime("%Y-%m-%d")

    # If no photo was attached, return factual telemetry
    if not base64_data:
        res = fallback_visual_assessment(report)
        res["source"] = "HIMA-LENS Telemetry Engine (No Photo Attached)"
        return res

    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not configured in environment.")
        return fallback_visual_assessment(report)

    prompt = f"""You are the Lead Visual Auditor and Geotechnical Specialist for HIMA-LENS (Himachal Landslide Inventory & Spatial Intelligence System).

CRITICAL TASK:
You must strictly audit the attached photograph.

FIRST STEP - IMAGE VALIDATION:
Carefully look at what is shown in the image.
- Is this image an authentic photograph of a geological landslide, hill slope failure, rock fall, mudflow, or natural terrain displacement?
- If the image shows an animal/pet (e.g. dog, cat), a human selfie, a smartphone screen screenshot, an app UI, a computer screen, a room/furniture, a vehicle, food, or anything that is NOT a real-world outdoor terrain/landslide:
  -> You MUST set "is_landslide_or_terrain": false.
  -> State exactly what is in the photo in "detected_content" (e.g. "Domestic pet (Golden Retriever dog)", "Smartphone screenshot of HIMA-LENS application").
  -> Do NOT invent or hallucinate any slope parameters or rock descriptions for non-terrain photos!

SECOND STEP - GEOTECHNICAL ANALYSIS (ONLY IF is_landslide_or_terrain is true):
- If and only if the image is real outdoor terrain/landslide, describe strictly what you see:
  - What failure type is visually apparent?
  - What visible materials are present (soil, mud, boulders, bedrock)?
  - Is a road or structure visible? If yes, is it blocked? If no road is visible, state "No roadway visible in camera frame".
  - If a parameter cannot be measured from a photo alone, state "Requires on-site field survey".

INCIDENT METADATA:
- Report ID: {report_id}
- District: {district}, Himachal Pradesh
- GPS Coordinates: {lat:.5f}° N, {lng:.5f}° E
- Reported Failure Type: {movement}
- Reported Severity: {severity}
- Citizen Notes: {user_desc}

RETURN ONLY A VALID JSON OBJECT WITH THIS EXACT SCHEMA (no markdown code blocks, backticks, or explanation):

{{
  "is_landslide_or_terrain": true or false,
  "validation_status": "VALID_TERRAIN_IMAGE" or "INVALID_NON_TERRAIN_IMAGE",
  "detected_content": "Exact factual description of what is visible in the photo",
  "rejection_reason": "Explanation if not a terrain image, or null if valid",
  "telemetry": {{
    "report_id": "{report_id}",
    "district": "{district}",
    "coordinates": "{_format_coordinates_dms(lat, lng)}",
    "decimal_coordinates": "{lat:.5f}° N, {lng:.5f}° E",
    "reported_date": "{str(inc_date)[:16].replace('T', ' ')}",
    "reported_movement": "{movement}",
    "reported_severity": "{severity}",
    "reporter_name": "{reporter}",
    "user_notes": "{user_desc}"
  }},
  "visual_analysis": {{
    "visible_failure_type": "Factual failure type if terrain, or 'Non-Geological Media' if invalid",
    "material_composition": "Factual materials seen if terrain, or 'N/A — No natural earth/rock in image' if invalid",
    "slope_condition": "Factual slope scarp description if terrain, or 'N/A' if invalid",
    "infrastructure_impact": "Factual visible road/structure status if terrain, or 'N/A' if invalid",
    "drainage_and_seepage": "Factual visible moisture/runoff if terrain, or 'N/A' if invalid",
    "secondary_hazard_risk": "Factual visible hazard if terrain, or 'N/A' if invalid"
  }},
  "geotechnical_parameters": {{
    "slope_height": "Visible approximate height or 'N/A'",
    "slope_angle": "Visible approximate cut angle or 'N/A'",
    "rock_structure": "Visible rock formation or 'N/A'",
    "debris_volume": "Visible debris extent or 'N/A'"
  }},
  "recommended_interventions": [
    {{"measure": "Intervention Measure", "priority": "High / Medium / Low", "details": "Action details"}}
  ],
  "synthesis_remarks": "Concise 2-3 sentence honest synthesis. If invalid photo, state that the photo was rejected for showing [detected_content] instead of a landslide."
}}"""

    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": mime_type, "data": base64_data}}
            ]
        }],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json",
        },
    }

    # Iterate through Gemini models
    for model_name in GEMINI_MODELS:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
            resp = requests.post(url, json=payload, timeout=24)
            if resp.status_code == 200:
                result_json = resp.json()
                candidates = result_json.get("candidates", [])
                if candidates:
                    raw_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    cleaned = re.sub(r"^```(?:json)?\s*", "", raw_text.strip(), flags=re.MULTILINE)
                    cleaned = re.sub(r"\s*```$", "", cleaned.strip(), flags=re.MULTILINE)
                    parsed = json.loads(cleaned)
                    parsed["source"] = f"HIMA-LENS Gemini Vision ({model_name})"
                    parsed["generated_at"] = datetime.utcnow().strftime("%d %b %Y, %H:%M UTC")
                    return parsed
            else:
                logger.warning("Gemini model %s returned status %s: %s", model_name, resp.status_code, resp.text[:180])
        except Exception as exc:
            logger.warning("Gemini model %s exception: %s", model_name, exc)

    logger.warning("All Gemini models failed or timed out. Falling back to baseline.")
    return fallback_visual_assessment(report)
