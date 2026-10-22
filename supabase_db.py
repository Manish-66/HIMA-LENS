"""Database and cloud storage adapter for HIMA-LENS community reports.

Supports Supabase PostgreSQL (via PostgREST) and Supabase Cloud Storage.
Falls back seamlessly to local disk and JSON storage when Supabase is not configured
or during offline local development.
"""
from __future__ import annotations

import json
import logging
import mimetypes
import os
import time
import uuid
from typing import Any
from werkzeug.datastructures import FileStorage

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from config import (
    COMMUNITY_REPORTS_PATH,
    COMMUNITY_REPORTS_UPLOAD_DIR,
    SUPABASE_BUCKET,
    SUPABASE_KEY,
    SUPABASE_URL,
)

logger = logging.getLogger(__name__)

MIME_TYPE_MAP = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "webp": "image/webp",
    "gif": "image/gif",
    "heic": "image/heic",
    "heif": "image/heif",
    "avif": "image/avif",
    "jfif": "image/jpeg",
}

_session: requests.Session | None = None


def _get_session() -> requests.Session:
    """Returns a thread-safe, pooled requests.Session with connection pooling and retries."""
    global _session
    if _session is None:
        _session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(pool_connections=10, pool_maxsize=20, max_retries=retries)
        _session.mount("https://", adapter)
        _session.mount("http://", adapter)
    return _session


def is_supabase_configured() -> bool:
    """Returns True if Supabase URL and API Key are present."""
    return bool(SUPABASE_URL and SUPABASE_KEY)


def _supabase_headers(content_type: str = "application/json") -> dict[str, str]:
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": content_type,
    }


def is_valid_image_bytes(data: bytes) -> bool:
    """Validates image magic bytes to protect against MIME spoofing and payload injection."""
    if not data or len(data) < 12:
        return False
    # JPEG magic bytes (FF D8 FF)
    if data.startswith(b"\xff\xd8\xff"):
        return True
    # PNG magic bytes (89 50 4E 47 0D 0A 1A 0A)
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return True
    # GIF magic bytes
    if data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
        return True
    # WebP magic bytes (RIFF....WEBP)
    if data.startswith(b"RIFF") and len(data) >= 12 and data[8:12] == b"WEBP":
        return True
    # HEIC / HEIF / AVIF magic bytes (ftyp box)
    if len(data) >= 16 and data[4:8] == b"ftyp":
        brand = data[8:12].lower()
        if brand in (b"heic", b"heix", b"hevc", b"heim", b"mif1", b"msf1", b"avif", b"avis"):
            return True
    # Fallback to PIL Image.verify if available
    try:
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(data))
        img.verify()
        return True
    except Exception:
        pass
    return False


def load_local_reports() -> list[dict[str, Any]]:
    """Loads reports from local JSON fallback file."""
    if not COMMUNITY_REPORTS_PATH.exists():
        return []
    try:
        with COMMUNITY_REPORTS_PATH.open(encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception as exc:
        logger.warning("Failed to read local reports JSON: %s", exc)
        return []


def save_local_reports(reports: list[dict[str, Any]]) -> None:
    """Saves reports to local JSON fallback file safely."""
    try:
        COMMUNITY_REPORTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with COMMUNITY_REPORTS_PATH.open("w", encoding="utf-8") as f:
            json.dump(reports, f, indent=2)
    except OSError as exc:
        logger.warning("Local filesystem write skipped (serverless environment): %s", exc)


def fetch_community_reports(include_hidden: bool = False) -> list[dict[str, Any]]:
    """Fetches community reports from Supabase DB or falls back to local JSON.

    If include_hidden is False, filters out records with is_hidden=True or
    status in ('hidden', 'archived', 'rejected', 'deleted').
    """
    if not is_supabase_configured():
        reports = load_local_reports()
    else:
        url = f"{SUPABASE_URL}/rest/v1/community_reports?select=*&order=created_at.desc"
        try:
            resp = _get_session().get(url, headers=_supabase_headers(), timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                reports = data if isinstance(data, list) else load_local_reports()
            else:
                logger.warning(
                    "Supabase reports query returned status %s: %s",
                    resp.status_code,
                    resp.text[:200],
                )
                reports = load_local_reports()
        except Exception as exc:
            logger.warning("Supabase reports query exception: %s. Falling back to local data.", exc)
            reports = load_local_reports()

    if include_hidden:
        return reports

    visible_reports = []
    for r in reports:
        # Check boolean is_hidden column
        is_hidden_val = r.get("is_hidden")
        if is_hidden_val is True or str(is_hidden_val).strip().lower() in ("true", "1"):
            continue
        # Check text status column
        status_val = str(r.get("status") or "").strip().lower()
        if status_val in ("hidden", "archived", "rejected", "deleted"):
            continue
        visible_reports.append(r)

    return visible_reports


def fetch_report_by_id(report_id: str) -> dict[str, Any] | None:
    """Fetches a single community report by its unique ID.

    Queries Supabase directly with `?id=eq.<id>` to avoid full-table scans.
    Falls back to scanning local reports if unconfigured or offline.
    """
    clean_id = (report_id or "").strip()
    if not clean_id:
        return None

    if is_supabase_configured():
        url = f"{SUPABASE_URL}/rest/v1/community_reports?id=eq.{clean_id}&limit=1"
        try:
            resp = _get_session().get(url, headers=_supabase_headers(), timeout=5)
            if resp.status_code == 200:
                rows = resp.json()
                if isinstance(rows, list) and len(rows) > 0:
                    return rows[0]
            else:
                logger.warning(
                    "Supabase single report lookup returned status %s: %s",
                    resp.status_code,
                    resp.text[:200],
                )
        except Exception as exc:
            logger.warning("Supabase single report lookup exception: %s. Falling back to local data.", exc)

    # Local fallback
    clean_id_lower = clean_id.casefold()
    for r in load_local_reports():
        if str(r.get("id", "")).strip().casefold() == clean_id_lower:
            return r
    return None


def save_community_report(report_data: dict[str, Any]) -> bool:
    """Saves a community report to Supabase DB and local JSON backup."""
    supabase_success = False

    if is_supabase_configured():
        url = f"{SUPABASE_URL}/rest/v1/community_reports"
        headers = _supabase_headers()
        headers["Prefer"] = "return=minimal"
        try:
            resp = _get_session().post(url, headers=headers, json=report_data, timeout=8)
            if resp.status_code in (200, 201):
                supabase_success = True
            else:
                logger.warning(
                    "Supabase report insert returned %s: %s",
                    resp.status_code,
                    resp.text[:200],
                )
        except Exception as exc:
            logger.warning("Supabase report insert exception: %s", exc)

    # Always attempt local backup (works during local dev; safely handled on serverless)
    local_reports = load_local_reports()
    local_reports.insert(0, report_data)
    save_local_reports(local_reports)

    return supabase_success if is_supabase_configured() else True


def save_report_assessment(report_id: str, assessment: dict[str, Any]) -> bool:
    """Persists geotechnical AI assessment dossier into the report's `ai_assessment` JSONB column.

    Enables persistence across stateless/serverless cold starts (Vercel) and mirrors
    to local fallback file.
    """
    clean_id = (report_id or "").strip()
    if not clean_id or not assessment:
        return False

    supabase_success = False
    if is_supabase_configured():
        url = f"{SUPABASE_URL}/rest/v1/community_reports?id=eq.{clean_id}"
        headers = _supabase_headers()
        headers["Prefer"] = "return=minimal"
        try:
            resp = _get_session().patch(url, headers=headers, json={"ai_assessment": assessment}, timeout=8)
            if resp.status_code in (200, 204):
                supabase_success = True
            else:
                logger.warning(
                    "Supabase report assessment update returned %s: %s",
                    resp.status_code,
                    resp.text[:200],
                )
        except Exception as exc:
            logger.warning("Supabase report assessment update exception: %s", exc)

    # Mirror to local fallback file
    local_reports = load_local_reports()
    updated = False
    clean_id_lower = clean_id.casefold()
    for r in local_reports:
        if str(r.get("id", "")).strip().casefold() == clean_id_lower:
            r["ai_assessment"] = assessment
            updated = True
            break
    if updated:
        save_local_reports(local_reports)

    return supabase_success if is_supabase_configured() else True


def update_report_status(report_id: str, status: str, is_hidden: bool | None = None) -> bool:
    """Updates the moderation status ('verified', 'active', 'hidden', 'rejected') of a report."""
    clean_id = (report_id or "").strip()
    if not clean_id:
        return False

    clean_status = (status or "active").strip().lower()
    if is_hidden is None:
        is_hidden = (clean_status in ("hidden", "rejected", "deleted"))

    update_payload: dict[str, Any] = {
        "status": clean_status,
        "is_hidden": is_hidden,
    }

    supabase_ok = False
    if is_supabase_configured():
        url = f"{SUPABASE_URL}/rest/v1/community_reports?id=eq.{clean_id}"
        headers = _supabase_headers()
        headers["Prefer"] = "return=minimal"
        try:
            resp = _get_session().patch(url, headers=headers, json=update_payload, timeout=8)
            if resp.status_code in (200, 204):
                supabase_ok = True
            elif "status" in resp.text and "Could not find" in resp.text:
                # If remote Supabase schema hasn't run the migration adding 'status', patch with 'is_hidden'
                fallback_resp = _get_session().patch(url, headers=headers, json={"is_hidden": is_hidden}, timeout=8)
                if fallback_resp.status_code in (200, 204):
                    supabase_ok = True
            else:
                logger.warning("Supabase report status update returned %s: %s", resp.status_code, resp.text[:200])
        except Exception as exc:
            logger.warning("Supabase report status update exception: %s", exc)

    # Local fallback update
    local_reports = load_local_reports()
    updated = False
    clean_id_lower = clean_id.casefold()
    for r in local_reports:
        if str(r.get("id", "")).strip().casefold() == clean_id_lower:
            r["status"] = clean_status
            r["is_hidden"] = is_hidden
            updated = True
            break
    if not updated and supabase_ok:
        rep = fetch_report_by_id(clean_id)
        if rep:
            rep["status"] = clean_status
            rep["is_hidden"] = is_hidden
            local_reports.insert(0, rep)
            updated = True
    if updated:
        save_local_reports(local_reports)

    return True if (supabase_ok or updated) else False


def delete_report(report_id: str) -> bool:
    """Permanently deletes a community report by ID."""
    clean_id = (report_id or "").strip()
    if not clean_id:
        return False

    supabase_ok = False
    if is_supabase_configured():
        url = f"{SUPABASE_URL}/rest/v1/community_reports?id=eq.{clean_id}"
        headers = _supabase_headers()
        try:
            resp = _get_session().delete(url, headers=headers, timeout=8)
            if resp.status_code in (200, 204):
                supabase_ok = True
            else:
                logger.warning("Supabase report delete returned %s: %s", resp.status_code, resp.text[:200])
        except Exception as exc:
            logger.warning("Supabase report delete exception: %s", exc)

    # Local fallback delete
    local_reports = load_local_reports()
    clean_id_lower = clean_id.casefold()
    initial_len = len(local_reports)
    filtered = [r for r in local_reports if str(r.get("id", "")).strip().casefold() != clean_id_lower]
    deleted_local = (len(filtered) < initial_len)
    if deleted_local:
        save_local_reports(filtered)

    return True if (supabase_ok or deleted_local) else False


BROADCAST_FILE = COMMUNITY_REPORTS_PATH.parent / "active_broadcast.json"

DEFAULT_BROADCAST = {
    "is_active": True,
    "title": "REGIONAL PRECIPITATION ADVISORY",
    "message": "High porewater saturation active along Mandi & Kinnaur highway corridors. PWD rapid clearance teams dispatched.",
    "severity": "warning",
    "link": "/feed",
    "updated_at": "2026-10-22T06:00:00Z"
}


def get_active_broadcast() -> dict[str, Any]:
    """Retrieves the active highway/geotechnical emergency broadcast bulletin."""
    if BROADCAST_FILE.exists():
        try:
            with BROADCAST_FILE.open(encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception as exc:
            logger.debug("Failed reading broadcast file: %s", exc)
    return DEFAULT_BROADCAST


def set_active_broadcast(
    title: str,
    message: str,
    severity: str = "critical",
    link: str = "",
    is_active: bool = True
) -> dict[str, Any]:
    """Sets or broadcasts a statewide emergency hazard alert."""
    broadcast_data = {
        "is_active": bool(is_active),
        "title": (title or "EMERGENCY HAZARD NOTICE").strip().upper(),
        "message": (message or "").strip(),
        "severity": (severity or "critical").strip().lower(),
        "link": (link or "").strip(),
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    try:
        BROADCAST_FILE.parent.mkdir(parents=True, exist_ok=True)
        with BROADCAST_FILE.open("w", encoding="utf-8") as f:
            json.dump(broadcast_data, f, indent=2)
    except OSError as exc:
        logger.warning("Failed writing broadcast file: %s", exc)
    return broadcast_data


def dismiss_active_broadcast() -> bool:
    """Dismisses/deactivates the live emergency broadcast."""
    current = get_active_broadcast()
    current["is_active"] = False
    try:
        with BROADCAST_FILE.open("w", encoding="utf-8") as f:
            json.dump(current, f, indent=2)
        return True
    except OSError as exc:
        logger.warning("Failed dismissing broadcast: %s", exc)
        return False


def upload_report_image(file: FileStorage, filename: str) -> str:
    """Uploads report image to Supabase Cloud Storage or local static folder.

    Validates binary header magic bytes to prevent MIME spoofing.
    Returns the public URL of the uploaded image, or an empty string on failure.
    """
    if not filename or not file:
        return ""

    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "jpg"
    unique_filename = f"report_{uuid.uuid4().hex[:12]}_{int(time.time())}.{ext}"
    content_type = MIME_TYPE_MAP.get(ext) or mimetypes.guess_type(filename)[0] or "image/jpeg"

    # Read binary content
    file.seek(0)
    file_bytes = file.read()

    # Validate image magic bytes
    if not is_valid_image_bytes(file_bytes):
        logger.warning("Rejected upload: file '%s' failed image magic byte verification.", filename)
        return ""

    if is_supabase_configured():
        upload_url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{unique_filename}"
        headers = _supabase_headers(content_type=content_type)
        headers["x-upsert"] = "false"  # Immutability: prevent overwriting existing assets

        try:
            resp = _get_session().post(upload_url, headers=headers, data=file_bytes, timeout=12)
            if resp.status_code in (200, 201):
                public_cdn_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{unique_filename}"
                return public_cdn_url
            logger.warning(
                "Supabase image upload failed with status %s: %s",
                resp.status_code,
                resp.text[:200],
            )
        except Exception as exc:
            logger.warning("Supabase image upload exception: %s", exc)

    # Local fallback save (used in local dev or if Supabase is unconfigured)
    try:
        COMMUNITY_REPORTS_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        save_path = COMMUNITY_REPORTS_UPLOAD_DIR / unique_filename
        with save_path.open("wb") as f:
            f.write(file_bytes)
        return f"/static/uploads/reports/{unique_filename}"
    except OSError as exc:
        logger.warning("Local image write skipped: %s", exc)
        return ""


def record_analytics_event(
    event_type: str,
    district: str,
    severity: str = "Moderate",
    movement_type: str = "Unknown",
    metadata: dict[str, Any] | None = None
) -> bool:
    """Inserts a telemetry event to Supabase analytics_events or falls back locally."""
    event_data = {
        "event_type": event_type,
        "district": district or "Unknown",
        "severity": severity or "Moderate",
        "movement_type": movement_type or "Unknown",
        "metadata": metadata or {},
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    if is_supabase_configured():
        url = f"{SUPABASE_URL}/rest/v1/analytics_events"
        headers = _supabase_headers()
        headers["Prefer"] = "return=minimal"
        try:
            resp = _get_session().post(url, headers=headers, json=event_data, timeout=5)
            if resp.status_code in (200, 201):
                return True
        except Exception as exc:
            logger.debug("Failed recording analytics event to Supabase: %s", exc)
    return False


def fetch_analytics_summary(district: str = "all", time_range: str = "7d") -> dict[str, Any]:
    """Computes real-time analytics aggregation across reports and telemetry.

    Returns structured metrics, district risk density, movement classification breakdown,
    and recent activity ledger for the Admin Analytics Dashboard.
    """
    reports = fetch_community_reports(include_hidden=True)

    # Filter by district if not 'all'
    if district and district.lower() != "all":
        target = district.casefold()
        reports = [r for r in reports if str(r.get("district", "")).casefold() == target]

    total_reports = len(reports)
    critical_count = sum(1 for r in reports if str(r.get("severity", "")).lower() in ("critical", "high"))
    ai_dossiers_count = sum(1 for r in reports if isinstance(r.get("ai_assessment"), dict) and r["ai_assessment"])

    # Calculate estimated mitigation cost
    total_est_cost = 0.0
    for r in reports:
        assessment = r.get("ai_assessment")
        if isinstance(assessment, dict):
            boq = assessment.get("cost_estimate_boq")
            if isinstance(boq, dict):
                try:
                    total_est_cost += float(boq.get("total_cost_inr") or 0.0)
                except (ValueError, TypeError):
                    pass

    # Baseline calculation if BOQs not yet generated (~15 Lakh INR per critical/high slope stabilization)
    if total_est_cost == 0.0 and total_reports > 0:
        total_est_cost = (critical_count * 1500000.0) + ((total_reports - critical_count) * 450000.0)

    # District distribution
    district_counts: dict[str, int] = {}
    for r in reports:
        d = (r.get("district") or "Unknown").title()
        district_counts[d] = district_counts.get(d, 0) + 1

    district_dist = [
        {"district": d, "count": count, "percentage": round((count / max(total_reports, 1)) * 100, 1)}
        for d, count in sorted(district_counts.items(), key=lambda x: x[1], reverse=True)
    ]

    # Movement type distribution
    movement_counts: dict[str, int] = {}
    for r in reports:
        m = (r.get("movement_type") or "Slide").title()
        movement_counts[m] = movement_counts.get(m, 0) + 1

    movement_dist = [
        {"movement": m, "count": count, "percentage": round((count / max(total_reports, 1)) * 100, 1)}
        for m, count in sorted(movement_counts.items(), key=lambda x: x[1], reverse=True)
    ]

    return {
        "kpis": {
            "total_reports": total_reports,
            "critical_hazards": critical_count,
            "ai_dossiers_count": ai_dossiers_count,
            "ai_coverage_pct": round((ai_dossiers_count / max(total_reports, 1)) * 100, 1),
            "estimated_cost_inr": total_est_cost,
            "estimated_cost_cr": round(total_est_cost / 10000000.0, 2),
        },
        "district_distribution": district_dist,
        "movement_distribution": movement_dist,
        "recent_reports": reports[:20]
    }

