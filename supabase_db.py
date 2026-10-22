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
