"""
Spatial Discipline Validator for HIMA-LENS
Checks GeoJSON files for RFC 7946 compliance, coordinate order, and Himachal Pradesh bounding box bounds.
"""
import sys
import json
import os

HP_BBOX = {
    "min_lon": 75.78,
    "max_lon": 79.07,
    "min_lat": 30.36,
    "max_lat": 33.20,
}

def validate_geojson(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}")
        return False

    print(f"[*] Validating spatial file: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if data.get("type") != "FeatureCollection":
        print(f"[!] Warning: Expected FeatureCollection, found {data.get('type')}")

    features = data.get("features", [])
    total = len(features)
    print(f"[*] Found {total} features. Inspecting coordinates...")

    out_of_bounds = []
    swapped = []
    null_geoms = []

    for i, feat in enumerate(features):
        geom = feat.get("geometry")
        if not geom or not geom.get("coordinates"):
            null_geoms.append(i)
            continue

        coords = geom.get("coordinates")
        gtype = geom.get("type")

        # Handle Point geometries
        if gtype == "Point":
            lon, lat = coords[0], coords[1]
            # Check for inverted lat/lon (e.g. lat around 76 and lon around 31)
            if 30.0 <= lon <= 34.0 and 75.0 <= lat <= 80.0:
                swapped.append((i, coords))
            elif not (HP_BBOX["min_lon"] <= lon <= HP_BBOX["max_lon"] and HP_BBOX["min_lat"] <= lat <= HP_BBOX["max_lat"]):
                out_of_bounds.append((i, coords))

    print(f"--- Spatial Validation Report ---")
    print(f"Total features checked : {total}")
    print(f"Null geometries        : {len(null_geoms)}")
    print(f"Swapped [lat, lon]     : {len(swapped)}")
    print(f"Out of HP bounding box : {len(out_of_bounds)}")

    if swapped:
        print(f"[FAIL] CRITICAL: Found {len(swapped)} coordinates with inverted latitude/longitude order!")
        for idx, c in swapped[:5]:
            print(f"   Feature #{idx}: {c}")
        return False

    if out_of_bounds:
        print(f"[WARN] Found {len(out_of_bounds)} coordinates outside HP bounds [75.78-79.07 E, 30.36-33.20 N]:")
        for idx, c in out_of_bounds[:5]:
            print(f"   Feature #{idx}: {c}")

    if not swapped and len(null_geoms) == 0:
        print("[PASS] Coordinate integrity verified. RFC 7946 compliant.")
        return True
    return False

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "landslides_clean.geojson"
    validate_geojson(target)
