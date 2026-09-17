"""Build the consolidated inventory; legacy Mandi is replaced by data.xlsx."""
from __future__ import annotations

import json
import math
from typing import Any
import pandas as pd
from config import DATASET_PATH, DISTRICT_BOUNDARIES_PATH, LEGACY_DATASET_PATH, MANDI_WORKBOOK_PATH
from districts import classify_features

FIELD_ALIASES = {
    "district": ("district", "District", "DISTRICT"),
    "activity": ("activity", "Activity", "ACTIVITY", "activity_status", "activityStatus", "status"),
    "movement_type": ("movement_type", "movementType", "movement", "movement_t", "MOVEMENT_T", "MOVEMENT_", "MOVEMENT"),
    "material_type": ("material_type", "materialType", "material", "MATERIAL_T", "MATERIAL"),
    "year": ("year", "Year", "period", "Period", "recorded_year", "recordedYear"),
}


def text(row: Any, *keys: str, default: str = "") -> str:
    for key in keys:
        value = row.get(key)
        if value is not None and not pd.isna(value) and str(value).strip():
            return str(value).strip()
    return default


def normalize_material(val: str) -> str:
    cleaned = (val or "").strip()
    if not cleaned or cleaned.lower() in ("none", "0", "nan", "unknown"):
        return "Unknown"
    if cleaned.casefold() in ("rock cum debris", "rock cum debris"):
        return "Rock cum debris"
    return cleaned.capitalize() if cleaned.islower() else cleaned


def normalize_movement(val: str) -> str:
    cleaned = (val or "").strip()
    if not cleaned or cleaned.lower() in ("none", "0", "nan", "unknown"):
        return "Unknown"
    lower = cleaned.lower()
    if "slide" in lower and "road" in lower:
        return "Slide (Road Subsidence)"
    if "slide" in lower and ("area" in lower or lower in ("slide (r)", "landslide")):
        return "Slide"
    return cleaned.capitalize() if cleaned.islower() else cleaned


def normalize_activity(val: str) -> str:
    cleaned = (val or "").strip()
    if not cleaned or cleaned.lower() in ("none", "0", "nan", "unknown"):
        return "Unknown"
    return cleaned.capitalize() if cleaned.islower() else cleaned


def normalize_period(val: str) -> str:
    cleaned = (val or "").strip()
    if not cleaned or cleaned.lower() in ("none", "0", "nan", "unknown", "historical"):
        return "Historical"
    lower = cleaned.lower()
    if "pre" in lower:
        return "Pre-monsoon"
    if "post" in lower:
        return "Post-monsoon"
    return cleaned


def legacy_features(boundaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not LEGACY_DATASET_PATH.exists():
        print(f"No legacy source at {LEGACY_DATASET_PATH}; exporting Mandi records only.")
        return []

    print(f"Loading legacy source from {LEGACY_DATASET_PATH}...")
    with LEGACY_DATASET_PATH.open(encoding="utf-8") as source:
        raw_features = json.load(source).get("features", [])

    # Spatial classification to ensure district is accurately identified for all points
    classify_features(raw_features, boundaries)

    # Filter out Mandi records so data.xlsx strictly supersedes legacy Mandi
    non_mandi = [
        f for f in raw_features
        if str((f.get("properties") or {}).get("district", "")).strip().casefold() != "mandi"
    ]

    print(f"Retained {len(non_mandi):,} non-Mandi features from legacy dataset.")
    output = []
    for idx, feature in enumerate(non_mandi, 1):
        props = dict(feature.get("properties") or {})
        district = props.get("district", "Unknown")
        activity = normalize_activity(props.get("activity"))
        movement = normalize_movement(props.get("movement_t") or props.get("movement_type"))
        material = normalize_material(props.get("material_t") or props.get("material_type"))
        period = normalize_period(props.get("time") or props.get("period"))

        year_val = props.get("year")
        if year_val is not None and str(year_val).strip() and str(year_val).strip().isdigit():
            year_str = str(int(float(year_val)))
        else:
            year_str = period

        dist_road = None
        if props.get("dist_road") is not None:
            try:
                dist_road = round(float(props["dist_road"]), 1)
            except (ValueError, TypeError):
                pass

        compact_props = {
            "id": props.get("id_land") or f"LEG_{idx}",
            "district": district,
            "state": props.get("state") or "Himachal Pradesh",
            "activity": activity,
            "style": str(props.get("style") or "").strip() or None,
            "movement_type": movement,
            "material_type": material,
            "period": period,
            "year": year_str,
            "distance_to_road_m": dist_road,
            "triggering": str(props.get("triggering") or "").strip() or None,
            "geology": str(props.get("geology") or "").strip() or None,
            "hydrologic": str(props.get("hydrologic") or "").strip() or None,
            "landuse_la": str(props.get("landuse_la") or "").strip() or None,
            "depth": props.get("depth"),
            "ls_area": props.get("ls_area"),
            "ls_volume": props.get("ls_volume"),
            "source": "Statewide Inventory",
        }
        output.append({
            "type": "Feature",
            "geometry": feature.get("geometry"),
            "properties": compact_props
        })
    return output


def mandi_features() -> list[dict[str, Any]]:
    print(f"Loading Mandi detailed dataset from {MANDI_WORKBOOK_PATH}...")
    table = pd.read_excel(MANDI_WORKBOOK_PATH)
    table.columns = [str(c).strip() for c in table.columns]
    output = []
    for idx, row in table.iterrows():
        try:
            lat, lng = float(row["LATITUDE"]), float(row["LONGITUDE"])
            if not (math.isfinite(lat) and math.isfinite(lng) and -90 <= lat <= 90 and -180 <= lng <= 180):
                continue
        except (KeyError, TypeError, ValueError):
            continue

        district = text(row, "DISTRICT", default="Mandi")
        activity = normalize_activity(text(row, "ACTIVITY"))
        movement = normalize_movement(text(row, "MOVEMENT_T", "MOVEMENT_", "MOVEMENT"))
        material = normalize_material(text(row, "MATERIAL_T", "MATERIAL"))
        period = normalize_period(text(row, "Period", default="Historical"))

        road_dist = None
        if pd.notna(row.get("Distance to Road (m)")):
            try:
                road_dist = round(float(row["Distance to Road (m)"]), 1)
            except (ValueError, TypeError):
                pass

        obj_id = int(row["OBJECTID_1"]) if pd.notna(row.get("OBJECTID_1")) else idx + 1

        props = {
            "id": obj_id,
            "district": district,
            "state": text(row, "STATE", default="Himachal Pradesh"),
            "activity": activity,
            "style": text(row, "STYLE") or None,
            "movement_type": movement,
            "material_type": material,
            "period": period,
            "year": period,
            "distance_to_road_m": road_dist,
            "source": "Mandi Detailed Field Inventory",
        }
        output.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lng, lat]},
            "properties": props
        })
    print(f"Loaded {len(output):,} Mandi features from workbook.")
    return output


if __name__ == "__main__":
    with DISTRICT_BOUNDARIES_PATH.open(encoding="utf-8") as source:
        boundaries = json.load(source)["features"]

    features = legacy_features(boundaries) + mandi_features()
    counts, unmatched, overlaps = classify_features(features, boundaries)
    if unmatched or overlaps:
        raise ValueError(f"District assignment failed: {len(unmatched)} unmatched, {len(overlaps)} overlapping")

    with DATASET_PATH.open("w", encoding="utf-8") as destination:
        json.dump({"type": "FeatureCollection", "features": features}, destination, ensure_ascii=False)

    print(f"Successfully wrote {len(features):,} records to {DATASET_PATH}")
    print(f"District breakdown: {dict(sorted(counts.items()))}")
