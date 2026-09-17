"""HIMA-LENS Flask application and read-only geospatial API."""
from __future__ import annotations

import csv
import io
import json
import time
import uuid
from datetime import datetime
from functools import lru_cache
from typing import Any
from flask import Flask, jsonify, render_template, request, Response
from config import (
    APP_DESCRIPTION,
    APP_NAME,
    CESIUM_ION_TOKEN,
    DATASET_PATH,
    DISTRICT_BOUNDARIES_PATH,
    MANDI_ROADS_PATH,
    LANDSLIDE_POLYGONS_MANDI_PATH,
    LANDSLIDE_POLYGONS_HP_PATH,
    ENVIRONMENTAL_OVERLAYS_META_PATH,
    COMMUNITY_REPORTS_PATH,
    COMMUNITY_REPORTS_UPLOAD_DIR,
)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.json.sort_keys = False

ALIASES = {
    "district": ("district", "District", "DISTRICT"),
    "activity": ("activity", "Activity", "ACTIVITY", "activity_status", "activityStatus", "status"),
    "movement": ("movement_type", "movementType", "movement", "MOVEMENT_T", "MOVEMENT_", "MOVEMENT", "movement_t"),
    "material": ("material_type", "materialType", "material", "MATERIAL_T", "MATERIAL", "material_t"),
    "period": ("period", "Period", "time", "Time", "season", "Season"),
    "year": ("year", "Year", "recorded_year", "recordedYear", "period", "Period"),
}

def prop(feature: dict[str, Any], name: str, default: str = "") -> str:
    properties = feature.get("properties") or {}
    for key in ALIASES.get(name, (name,)):
        value = properties.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return default

@lru_cache(maxsize=1)
def inventory() -> dict[str, Any]:
    with DATASET_PATH.open(encoding="utf-8") as source:
        data = json.load(source)
    if data.get("type") != "FeatureCollection" or not isinstance(data.get("features"), list):
        raise ValueError("Dataset is not a GeoJSON FeatureCollection")
    return data

@lru_cache(maxsize=1)
def administrative_boundaries() -> dict[str, Any]:
    with DISTRICT_BOUNDARIES_PATH.open(encoding="utf-8") as source:
        data = json.load(source)
    if data.get("type") != "FeatureCollection" or not isinstance(data.get("features"), list):
        raise ValueError("District boundaries are not a GeoJSON FeatureCollection")
    features = []
    for feature in data["features"]:
        properties = feature.get("properties") or {}
        district = properties.get("name") or properties.get("lgd_districtname")
        if district:
            features.append({
                "type": "Feature",
                "properties": {
                    "district": district,
                    "lgd_code": properties.get("lgd_districtcode"),
                    "source": "India Administrative Boundaries 2024"
                },
                "geometry": feature.get("geometry")
            })
    return {"type": "FeatureCollection", "features": features}

@lru_cache(maxsize=1)
def serialized_boundaries() -> str:
    return json.dumps(administrative_boundaries())

@lru_cache(maxsize=1)
def cached_roads() -> str:
    if not MANDI_ROADS_PATH.exists():
        return json.dumps({"type": "FeatureCollection", "features": []})
    return MANDI_ROADS_PATH.read_text(encoding="utf-8")

@lru_cache(maxsize=1)
def cached_mandi_polygons() -> str:
    if not LANDSLIDE_POLYGONS_MANDI_PATH.exists():
        return json.dumps({"type": "FeatureCollection", "features": []})
    return LANDSLIDE_POLYGONS_MANDI_PATH.read_text(encoding="utf-8")

@lru_cache(maxsize=1)
def cached_hp_polygons() -> str:
    if not LANDSLIDE_POLYGONS_HP_PATH.exists():
        return json.dumps({"type": "FeatureCollection", "features": []})
    return LANDSLIDE_POLYGONS_HP_PATH.read_text(encoding="utf-8")

@lru_cache(maxsize=1)
def cached_environmental_meta() -> dict[str, Any]:
    if not ENVIRONMENTAL_OVERLAYS_META_PATH.exists():
        return {}
    with ENVIRONMENTAL_OVERLAYS_META_PATH.open(encoding="utf-8") as f:
        return json.load(f)

def matching_features() -> list[dict[str, Any]]:
    tokens = request.args.get("bounds", "").split(",")
    try:
        west, south, east, north = map(float, tokens) if len(tokens) == 4 else (None,) * 4
    except ValueError:
        west = south = east = north = None
    criteria = {key: request.args.get(key, "").strip().casefold() for key in ALIASES}
    output = []
    for feature in inventory()["features"]:
        geometry = feature.get("geometry") or {}
        coordinates = geometry.get("coordinates") or []
        if geometry.get("type") != "Point" or len(coordinates) < 2:
            continue
        try:
            lng, lat = float(coordinates[0]), float(coordinates[1])
        except (TypeError, ValueError):
            continue
        if west is not None and not (west <= lng <= east and south <= lat <= north):
            continue
        if any(value and value != "all" and prop(feature, key).casefold() != value for key, value in criteria.items()):
            continue
        output.append(feature)
    return output

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/explore")
@app.get("/api")
def explore():
    return render_template("explore.html", cesium_ion_token=CESIUM_ION_TOKEN)

@app.get("/feed")
def feed():
    return render_template("feed.html")

@app.get("/report")
def report():
    return render_template("report.html")

@app.get("/about")
def about():
    return render_template("about.html")

@app.get("/api/landslides")
def landslides():
    return jsonify(type="FeatureCollection", features=matching_features())

@app.get("/api/summary")
def summary():
    features = matching_features()
    districts = {prop(f, "district") for f in features if prop(f, "district")}
    numeric_years = [int(prop(f, "year")) for f in features if prop(f, "year").isdigit()]
    periods = {prop(f, "period") for f in features if prop(f, "period")}
    return jsonify(
        success=True,
        total_records=len(features),
        districts=len(districts),
        district_names=sorted(districts),
        periods=sorted(periods),
        numeric_year_count=len(numeric_years),
        earliest_year=min(numeric_years, default=None),
        latest_year=max(numeric_years, default=None),
    )

@app.get("/api/districts")
def districts():
    canonical = {feature["properties"]["district"].casefold(): feature["properties"]["district"] for feature in administrative_boundaries()["features"]}
    counts = {name: 0 for name in canonical.values()}
    for feature in inventory()["features"]:
        name = prop(feature, "district", "Unknown")
        canonical_name = canonical.get(name.casefold(), name)
        counts[canonical_name] = counts.get(canonical_name, 0) + 1
    return jsonify(success=True, districts=[{"district": k, "count": v} for k, v in sorted(counts.items())])

@app.get("/api/years")
def years():
    counts = {}
    for feature in inventory()["features"]:
        value = prop(feature, "year")
        if value:
            counts[value] = counts.get(value, 0) + 1
    return jsonify(success=True, years=[{"year": k, "count": v} for k, v in sorted(counts.items(), reverse=True)])

@app.get("/api/categories")
def categories():
    result = {}
    for category in ("activity", "movement", "material"):
        counts = {}
        for feature in inventory()["features"]:
            value = prop(feature, category, "Unknown")
            counts[value] = counts.get(value, 0) + 1
        result[category] = [{"value": k, "count": v} for k, v in sorted(counts.items(), key=lambda x: (-x[1], x[0]))]
    return jsonify(success=True, categories=result)

@app.get("/api/district-boundaries")
def district_boundaries():
    response = Response(serialized_boundaries(), status=200, mimetype="application/json")
    response.headers["Cache-Control"] = "public, max-age=3600"
    return response

@app.get("/api/roads")
def roads():
    response = Response(cached_roads(), status=200, mimetype="application/json")
    response.headers["Cache-Control"] = "public, max-age=3600"
    return response

@app.get("/api/landslide-polygons")
def landslide_polygons():
    district = request.args.get("district", "").strip().lower()
    if district == "mandi":
        content = cached_mandi_polygons()
    elif district and district != "all":
        all_data = json.loads(cached_hp_polygons())
        filtered = [f for f in all_data.get("features", []) if (f.get("properties") or {}).get("district", "").lower() == district]
        content = json.dumps({"type": "FeatureCollection", "features": filtered})
    else:
        content = cached_hp_polygons()
    response = Response(content, status=200, mimetype="application/json")
    response.headers["Cache-Control"] = "public, max-age=3600"
    return response

@app.get("/api/environmental-layers")
def environmental_layers():
    return jsonify(success=True, layers=cached_environmental_meta())

def load_community_reports() -> list[dict[str, Any]]:
    if not COMMUNITY_REPORTS_PATH.exists():
        return []
    try:
        with COMMUNITY_REPORTS_PATH.open(encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []

def save_community_reports(reports: list[dict[str, Any]]) -> None:
    COMMUNITY_REPORTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with COMMUNITY_REPORTS_PATH.open("w", encoding="utf-8") as f:
        json.dump(reports, f, indent=2)

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}

def allowed_image_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

@app.get("/api/reports")
def get_reports():
    reports = load_community_reports()
    features = []
    for rep in reports:
        try:
            lat = float(rep["latitude"])
            lng = float(rep["longitude"])
        except (KeyError, ValueError, TypeError):
            continue
        features.append({
            "type": "Feature",
            "properties": {
                "id": rep.get("id"),
                "district": rep.get("district", "Unknown"),
                "incident_date": rep.get("incident_date", ""),
                "movement_type": rep.get("movement_type", "Unknown"),
                "severity": rep.get("severity", "Moderate"),
                "description": rep.get("description", ""),
                "reporter_name": rep.get("reporter_name", "Anonymous"),
                "photo_url": rep.get("photo_url", ""),
                "created_at": rep.get("created_at", ""),
                "is_community_report": True
            },
            "geometry": {
                "type": "Point",
                "coordinates": [lng, lat]
            }
        })
    return jsonify({"type": "FeatureCollection", "features": features})

@app.post("/api/reports")
def submit_report():
    try:
        lat = float(request.form.get("latitude", 0))
        lng = float(request.form.get("longitude", 0))
    except (TypeError, ValueError):
        return jsonify(success=False, error="INVALID_COORDINATES", message="Valid decimal latitude and longitude are required."), 400

    if not (30.0 <= lat <= 34.0 and 75.0 <= lng <= 80.0):
        return jsonify(
            success=False, 
            error="OUT_OF_BOUNDS", 
            message="Coordinates must be located within Himachal Pradesh bounds (30.0°N–34.0°N, 75.0°E–80.0°E)."
        ), 400

    district = request.form.get("district", "Mandi").strip()
    incident_date = request.form.get("incident_date", datetime.utcnow().strftime("%Y-%m-%d %H:%M")).strip()
    movement_type = request.form.get("movement_type", "Slide").strip()
    severity = request.form.get("severity", "Moderate").strip()
    description = request.form.get("description", "").strip()
    reporter_name = request.form.get("reporter_name", "Anonymous").strip()

    photo_url = ""
    file = request.files.get("photo")
    if file and file.filename and allowed_image_file(file.filename):
        COMMUNITY_REPORTS_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        ext = file.filename.rsplit(".", 1)[1].lower()
        unique_filename = f"report_{uuid.uuid4().hex[:12]}_{int(time.time())}.{ext}"
        save_path = COMMUNITY_REPORTS_UPLOAD_DIR / unique_filename
        file.save(str(save_path))
        photo_url = f"/static/uploads/reports/{unique_filename}"

    report_id = f"HL-CR-{uuid.uuid4().hex[:8].upper()}"
    new_report = {
        "id": report_id,
        "latitude": round(lat, 5),
        "longitude": round(lng, 5),
        "district": district,
        "incident_date": incident_date,
        "movement_type": movement_type,
        "severity": severity,
        "description": description,
        "reporter_name": reporter_name,
        "photo_url": photo_url,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

    reports = load_community_reports()
    reports.insert(0, new_report)
    save_community_reports(reports)

    return jsonify(success=True, report=new_report), 201

@app.get("/api/export")
def export_dataset():
    district_param = request.args.get("district", "all").strip().lower()
    year_param = request.args.get("year", "all").strip().lower()
    export_format = request.args.get("format", "csv").strip().lower()

    features = inventory()["features"]
    filtered = []
    for f in features:
        f_district = prop(f, "district", "").lower()
        f_year = prop(f, "year", "").lower()

        if district_param and district_param != "all" and f_district != district_param:
            continue
        if year_param and year_param != "all" and f_year != year_param:
            continue
        filtered.append(f)

    clean_dist = district_param if district_param and district_param != "all" else "all_districts"
    clean_yr = year_param if year_param and year_param != "all" else "all_years"

    if export_format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "id", "latitude", "longitude", "district", "activity", 
            "movement_type", "material_type", "year", "distance_to_road_m"
        ])
        for idx, f in enumerate(filtered, start=1):
            coords = f.get("geometry", {}).get("coordinates", [0, 0])
            writer.writerow([
                f.get("id") or idx,
                coords[1] if len(coords) > 1 else "",
                coords[0] if len(coords) > 0 else "",
                prop(f, "district", "Himachal Pradesh"),
                prop(f, "activity", "Not recorded"),
                prop(f, "movement", "Not recorded"),
                prop(f, "material", "Not recorded"),
                prop(f, "year", "Not recorded"),
                prop(f, "distance_to_road_m", "") or (f.get("properties") or {}).get("distance_to_road_m", "")
            ])
        csv_data = output.getvalue()
        filename = f"HIMA-LENS_landslides_{clean_dist}_{clean_yr}.csv"
        response = Response(csv_data, mimetype="text/csv")
        response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    elif export_format == "geojson":
        geojson_data = json.dumps({"type": "FeatureCollection", "features": filtered}, indent=2)
        filename = f"HIMA-LENS_landslides_{clean_dist}_{clean_yr}.geojson"
        response = Response(geojson_data, mimetype="application/geo+json")
        response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    else:
        records = []
        for idx, f in enumerate(filtered, start=1):
            coords = f.get("geometry", {}).get("coordinates", [0, 0])
            records.append({
                "id": f.get("id") or idx,
                "latitude": coords[1] if len(coords) > 1 else None,
                "longitude": coords[0] if len(coords) > 0 else None,
                "district": prop(f, "district", "Himachal Pradesh"),
                "activity": prop(f, "activity", "Not recorded"),
                "movement_type": prop(f, "movement", "Not recorded"),
                "material_type": prop(f, "material", "Not recorded"),
                "year": prop(f, "year", "Not recorded")
            })
        json_data = json.dumps(records, indent=2)
        filename = f"HIMA-LENS_landslides_{clean_dist}_{clean_yr}.json"
        response = Response(json_data, mimetype="application/json")
        response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

@app.get("/api/health")
def health():
    try:
        count = len(inventory()["features"])
        boundary_count = len(administrative_boundaries()["features"])
        valid, error = True, None
    except Exception as exc:
        count, boundary_count, valid, error = 0, 0, False, str(exc)
    return jsonify(
        success=valid,
        status="ok" if valid else "degraded",
        application=APP_NAME,
        description=APP_DESCRIPTION,
        dataset_available=DATASET_PATH.exists(),
        boundaries_available=DISTRICT_BOUNDARIES_PATH.exists(),
        dataset=str(DATASET_PATH),
        feature_count=count,
        district_boundary_count=boundary_count,
        validation_error=error
    ), (200 if valid else 503)

@app.errorhandler(FileNotFoundError)
def missing_dataset(error):
    return jsonify(success=False, error="DATASET_NOT_FOUND", message=str(error)), 404

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)

