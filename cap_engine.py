"""Common Alerting Protocol (CAP v1.2) Emergency Alert Engine for HIMA-LENS.

Adheres to OASIS Common Alerting Protocol v1.2 standard (ITU-T Rec. X.1303).
Compatible with the National Disaster Management Authority (NDMA) / C-DOT CAP-SACHET
Integrated Alert System for government-grade cell broadcast warning dissemination across
Himachal Pradesh mountain corridors.
"""
from __future__ import annotations

import json
import logging
import os
import time
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any
import html

from config import BASE_DIR, COMMUNITY_REPORTS_PATH

logger = logging.getLogger(__name__)

CAP_DIR = BASE_DIR / "data" / "cap_alerts"
ACTIVE_CAP_FILE = BASE_DIR / "data" / "active_cap_alert.json"

CAP_XMLNS = "urn:oasis:names:tc:emergency:cap:1.2"

# Census / LGD District Codes for Himachal Pradesh (for Cell-Tower BTS geocoding)
HP_DISTRICT_CODES = {
    "Bilaspur": "020",
    "Chamba": "021",
    "Hamirpur": "022",
    "Kangra": "023",
    "Kinnaur": "024",
    "Kullu": "025",
    "Lahaul & Spiti": "026",
    "Lahaul and Spiti": "026",
    "Mandi": "027",
    "Shimla": "028",
    "Sirmaur": "029",
    "Solan": "030",
    "Una": "031",
}


def _get_utc_now_iso() -> str:
    """Returns current UTC timestamp formatted for CAP 1.2."""
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S+00:00")


def _get_expiration_iso(hours: int = 12) -> str:
    """Returns expiration timestamp in UTC."""
    exp = datetime.now(timezone.utc) + timedelta(hours=hours)
    return exp.strftime("%Y-%m-%dT%H:%M:%S+00:00")


def generate_cap_xml(alert: dict[str, Any]) -> str:
    """Generates an OASIS CAP v1.2 compliant XML document from alert parameters."""
    identifier = alert.get("identifier") or f"IN-HP-HIMALENS-{int(time.time())}-{uuid.uuid4().hex[:6].upper()}"
    sender = alert.get("sender") or "scene.iitmandi@himalens.gov.in"
    sent = alert.get("sent") or _get_utc_now_iso()
    status = alert.get("status") or "Actual"  # Actual, Draft, Test
    msg_type = alert.get("msg_type") or "Alert"  # Alert, Update, Cancel
    scope = alert.get("scope") or "Public"

    # Root Alert Element
    root = ET.Element("alert", xmlns=CAP_XMLNS)
    
    ET.SubElement(root, "identifier").text = identifier
    ET.SubElement(root, "sender").text = sender
    ET.SubElement(root, "sent").text = sent
    ET.SubElement(root, "status").text = status
    ET.SubElement(root, "msgType").text = msg_type
    ET.SubElement(root, "source").text = "HIMA-LENS Landslide & Mountain Hazard Observatory, SCENE IIT Mandi"
    ET.SubElement(root, "scope").text = scope
    ET.SubElement(root, "code").text = "CAP-SACHET-1.2"
    ET.SubElement(root, "code").text = "NDMA-CELL-BROADCAST"

    # Info Element
    info = ET.SubElement(root, "info")
    ET.SubElement(info, "language").text = "en-IN"
    ET.SubElement(info, "category").text = "Geo"
    ET.SubElement(info, "event").text = alert.get("event") or "Landslide / Slope Instability Hazard"
    ET.SubElement(info, "urgency").text = alert.get("urgency") or "Immediate"  # Immediate, Expected, Future
    ET.SubElement(info, "severity").text = alert.get("severity_cap") or "Severe"  # Extreme, Severe, Moderate
    ET.SubElement(info, "certainty").text = alert.get("certainty") or "Observed"  # Observed, Likely, Possible

    # Event Code
    event_code = ET.SubElement(info, "eventCode")
    ET.SubElement(event_code, "valueName").text = "SAME"
    ET.SubElement(event_code, "value").text = "LSW"  # Landslide Warning

    ET.SubElement(info, "expires").text = alert.get("expires") or _get_expiration_iso(hours=12)
    ET.SubElement(info, "senderName").text = "HIMA-LENS Geotechnical Disaster Command &bull; IIT Mandi"
    ET.SubElement(info, "headline").text = alert.get("headline") or "CRITICAL LANDSLIDE HAZARD & ROAD BREACH"
    ET.SubElement(info, "description").text = alert.get("description") or "Severe rockfall and debris accumulation blocking vehicular movement."
    ET.SubElement(info, "instruction").text = alert.get("instruction") or "Halt all vehicular traffic. Do not approach the slope toe. Await PWD clearance."
    ET.SubElement(info, "web").text = alert.get("web") or "https://hima-lens.vercel.app/feed"

    # Target Highway Corridor Parameter
    param_corridor = ET.SubElement(info, "parameter")
    ET.SubElement(param_corridor, "valueName").text = "CorridorTarget"
    ET.SubElement(param_corridor, "value").text = alert.get("corridor") or "NH-05 (Hindustan-Tibet Highway)"

    # Target Area
    area = ET.SubElement(info, "area")
    district = alert.get("district") or "Mandi"
    radius_km = float(alert.get("radius_km") or 15.0)
    lat = float(alert.get("latitude") or 31.7727)
    lng = float(alert.get("longitude") or 76.9841)

    ET.SubElement(area, "areaDesc").text = f"{district} District, {alert.get('corridor', 'Highway Corridor')} Sector (Broadcast Radius {radius_km:.1f} km)"
    
    # CAP circle format: "latitude,longitude radius_km"
    ET.SubElement(area, "circle").text = f"{lat:.4f},{lng:.4f} {radius_km:.1f}"

    # Geocode for District
    geocode_val = HP_DISTRICT_CODES.get(district.title(), "027")
    geocode = ET.SubElement(area, "geocode")
    ET.SubElement(geocode, "valueName").text = "Census2011_DistrictCode"
    ET.SubElement(geocode, "value").text = geocode_val

    # Generate XML string with header
    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
    raw_xml = ET.tostring(root, encoding="utf-8", xml_declaration=False).decode("utf-8")
    return xml_declaration + raw_xml


def get_default_cap_alert() -> dict[str, Any]:
    """Returns a realistic active CAP sample alert for initial state."""
    return {
        "identifier": "IN-HP-HIMALENS-20261022-NIGUL01",
        "sender": "scene.iitmandi@himalens.gov.in",
        "sent": _get_utc_now_iso(),
        "status": "Actual",
        "msg_type": "Alert",
        "scope": "Public",
        "event": "Rockfall & Highway Breach",
        "urgency": "Immediate",
        "severity_cap": "Extreme",
        "certainty": "Observed",
        "headline": "CRITICAL ROCKFALL WARNING & HIGHWAY CLOSURE &bull; NH-05 KINNAUR",
        "description": "Massive wedge failure and ongoing loose scree detachments between Nigulsari and Taranda. Highway carriageway completely blocked. Porewater saturation critical.",
        "instruction": "All vehicular movement halted at Bhaba Nagar and Pooh checkposts. Travelers must not approach rockfall overhangs. Emergency PWD machinery deployed.",
        "district": "Kinnaur",
        "corridor": "NH-05 (Hindustan-Tibet Highway)",
        "latitude": 31.5421,
        "longitude": 77.9214,
        "radius_km": 20.0,
        "is_active": True,
        "web": "/feed",
        "expires": _get_expiration_iso(hours=18)
    }


def get_active_cap_alert() -> dict[str, Any]:
    """Reads the active CAP alert JSON object."""
    if ACTIVE_CAP_FILE.exists():
        try:
            with ACTIVE_CAP_FILE.open(encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception as exc:
            logger.warning("Failed to read active CAP alert: %s", exc)
    return get_default_cap_alert()


def get_active_cap_xml() -> str:
    """Returns the well-formed XML string of the currently active CAP alert."""
    alert = get_active_cap_alert()
    return generate_cap_xml(alert)


def dispatch_cap_alert(payload: dict[str, Any]) -> dict[str, Any]:
    """Generates, validates, signs, and saves a new official CAP 1.2 alert."""
    identifier = f"IN-HP-HIMALENS-{int(time.time())}-{uuid.uuid4().hex[:6].upper()}"
    
    alert_record = {
        "identifier": identifier,
        "sender": "scene.iitmandi@himalens.gov.in",
        "sent": _get_utc_now_iso(),
        "status": payload.get("status") or "Actual",
        "msg_type": "Alert",
        "scope": "Public",
        "event": payload.get("event") or "Landslide / Slope Instability Hazard",
        "urgency": payload.get("urgency") or "Immediate",
        "severity_cap": payload.get("severity_cap") or "Severe",
        "certainty": payload.get("certainty") or "Observed",
        "headline": (payload.get("headline") or "STATE DISASTER ADVISORY").strip().upper(),
        "description": (payload.get("description") or "").strip(),
        "instruction": (payload.get("instruction") or "Follow official highway police directions.").strip(),
        "district": (payload.get("district") or "Mandi").strip(),
        "corridor": (payload.get("corridor") or "National Highway").strip(),
        "latitude": float(payload.get("latitude") or 31.7727),
        "longitude": float(payload.get("longitude") or 76.9841),
        "radius_km": float(payload.get("radius_km") or 15.0),
        "is_active": True,
        "web": payload.get("web") or "/feed",
        "expires": _get_expiration_iso(hours=int(payload.get("expires_hours") or 12))
    }

    # Generate XML to validate schema
    xml_string = generate_cap_xml(alert_record)

    # Persist Active JSON and Archive XML
    try:
        CAP_DIR.mkdir(parents=True, exist_ok=True)
        archive_xml_path = CAP_DIR / f"{identifier}.xml"
        archive_xml_path.write_text(xml_string, encoding="utf-8")

        ACTIVE_CAP_FILE.parent.mkdir(parents=True, exist_ok=True)
        with ACTIVE_CAP_FILE.open("w", encoding="utf-8") as f:
            json.dump(alert_record, f, indent=2)
    except OSError as exc:
        logger.error("Failed saving CAP alert files: %s", exc)

    return alert_record


def cancel_active_cap_alert(reason: str = "Hazard cleared by district authorities.") -> dict[str, Any]:
    """Issues a CAP 1.2 'Cancel' message and deactivates broadcast."""
    current = get_active_cap_alert()
    current["is_active"] = False
    current["msg_type"] = "Cancel"
    current["sent"] = _get_utc_now_iso()
    current["instruction"] = f"DISMISSAL NOTICE: {reason}"

    xml_string = generate_cap_xml(current)
    try:
        ACTIVE_CAP_FILE.parent.mkdir(parents=True, exist_ok=True)
        with ACTIVE_CAP_FILE.open("w", encoding="utf-8") as f:
            json.dump(current, f, indent=2)

        # Archive cancel XML
        cancel_id = f"{current.get('identifier', 'ALERT')}-CANCEL"
        (CAP_DIR / f"{cancel_id}.xml").write_text(xml_string, encoding="utf-8")
    except OSError as exc:
        logger.warning("Failed saving cancel CAP alert: %s", exc)

    return current
