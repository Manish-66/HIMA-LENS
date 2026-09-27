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
}


def is_supabase_configured() -> bool:
    """Returns True if Supabase URL and API Key are present."""
    return bool(SUPABASE_URL and SUPABASE_KEY)


def _supabase_headers(content_type: str = "application/json") -> dict[str, str]:
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": content_type,
    }


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


def fetch_community_reports() -> list[dict[str, Any]]:
    """Fetches community reports from Supabase DB or falls back to local JSON."""
    if not is_supabase_configured():
        return load_local_reports()

    url = f"{SUPABASE_URL}/rest/v1/community_reports?select=*&order=created_at.desc"
    try:
        resp = requests.get(url, headers=_supabase_headers(), timeout=6)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list):
                return data
        logger.warning(
            "Supabase reports query returned status %s: %s",
            resp.status_code,
            resp.text[:200],
        )
    except Exception as exc:
        logger.warning("Supabase reports query exception: %s. Falling back to local data.", exc)

    return load_local_reports()


def save_community_report(report_data: dict[str, Any]) -> bool:
    """Saves a community report to Supabase DB and local JSON backup."""
    supabase_success = False

    if is_supabase_configured():
        url = f"{SUPABASE_URL}/rest/v1/community_reports"
        headers = _supabase_headers()
        headers["Prefer"] = "return=minimal"
        try:
            resp = requests.post(url, headers=headers, json=report_data, timeout=8)
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


def upload_report_image(file: FileStorage, filename: str) -> str:
    """Uploads report image to Supabase Cloud Storage or local static folder.

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

    if is_supabase_configured():
        upload_url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{unique_filename}"
        headers = _supabase_headers(content_type=content_type)
        headers["x-upsert"] = "true"

        try:
            resp = requests.post(upload_url, headers=headers, data=file_bytes, timeout=12)
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
