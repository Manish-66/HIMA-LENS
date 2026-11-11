"""District-boundary helpers and a reproducible inventory verification command."""
from __future__ import annotations

import json
import math
from collections import Counter
from typing import Any

from config import DATASET_PATH, DISTRICT_BOUNDARIES_PATH


def district_name(feature: dict[str, Any]) -> str:
    properties = feature.get("properties") or {}
    for key in ("district", "name", "lgd_districtname"):
        value = properties.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return "Unknown"


def point_in_ring(point: tuple[float, float], ring: list[list[float]]) -> bool:
    x, y = point
    inside = False
    previous = ring[-1]
    for current in ring:
        x1, y1 = current[:2]
        x2, y2 = previous[:2]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            inside = not inside
        previous = current
    return inside


def point_in_polygon(point: tuple[float, float], rings: list[list[list[float]]]) -> bool:
    return bool(rings) and point_in_ring(point, rings[0]) and not any(point_in_ring(point, hole) for hole in rings[1:])


def point_in_geometry(point: tuple[float, float], geometry: dict[str, Any]) -> bool:
    coordinates = geometry.get("coordinates") or []
    if geometry.get("type") == "Polygon":
        return point_in_polygon(point, coordinates)
    if geometry.get("type") == "MultiPolygon":
        return any(point_in_polygon(point, polygon) for polygon in coordinates)
    return False


def geometry_bounds(geometry: dict[str, Any]) -> tuple[float, float, float, float]:
    points: list[list[float]] = []
    def collect(value):
        if isinstance(value, list) and len(value) >= 2 and isinstance(value[0], (int, float)):
            points.append(value)
        elif isinstance(value, list):
            for item in value: collect(item)
    collect(geometry.get("coordinates") or [])
    xs, ys = [point[0] for point in points], [point[1] for point in points]
    return min(xs), min(ys), max(xs), max(ys)


def prepare_ring(ring: list[list[float]]) -> tuple[tuple[float, float, float, float], dict[int, list]]:
    xs, ys = [point[0] for point in ring], [point[1] for point in ring]
    buckets: dict[int, list] = {}
    previous = ring[-1]
    for current in ring:
        edge = (current[0], current[1], previous[0], previous[1])
        start, end = math.floor(min(current[1], previous[1]) * 100), math.floor(max(current[1], previous[1]) * 100)
        for bucket in range(start, end + 1): buckets.setdefault(bucket, []).append(edge)
        previous = current
    return (min(xs), min(ys), max(xs), max(ys)), buckets


def prepare_geometry(geometry: dict[str, Any]) -> list[list]:
    coordinates = geometry.get("coordinates") or []
    polygons = [coordinates] if geometry.get("type") == "Polygon" else coordinates if geometry.get("type") == "MultiPolygon" else []
    return [[prepare_ring(ring) for ring in polygon] for polygon in polygons]


def point_in_prepared_ring(point: tuple[float, float], prepared_ring) -> bool:
    (west, south, east, north), buckets = prepared_ring
    x, y = point
    if not (west <= x <= east and south <= y <= north): return False
    inside = False
    for x1, y1, x2, y2 in buckets.get(math.floor(y * 100), []):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: inside = not inside
    return inside


def point_in_prepared_geometry(point: tuple[float, float], polygons: list[list]) -> bool:
    return any(rings and point_in_prepared_ring(point, rings[0]) and not any(point_in_prepared_ring(point, hole) for hole in rings[1:]) for rings in polygons)


def classify_features(features: list[dict[str, Any]], boundaries: list[dict[str, Any]]) -> tuple[Counter, list, list]:
    counts: Counter = Counter()
    unmatched, overlaps = [], []
    prepared = [(boundary, geometry_bounds(boundary.get("geometry") or {}), prepare_geometry(boundary.get("geometry") or {})) for boundary in boundaries]
    for feature in features:
        coordinates = (feature.get("geometry") or {}).get("coordinates") or []
        if len(coordinates) < 2:
            unmatched.append(feature)
            continue
        point = (float(coordinates[0]), float(coordinates[1]))
        matches = [boundary for boundary, (west, south, east, north), polygons in prepared if west <= point[0] <= east and south <= point[1] <= north and point_in_prepared_geometry(point, polygons)]
        if len(matches) == 1:
            name = district_name(matches[0])
            counts[name] += 1
            (feature.setdefault("properties", {}))["district"] = name
        elif not matches:
            unmatched.append(feature)
        else:
            overlaps.append((feature, [district_name(boundary) for boundary in matches]))
    return counts, unmatched, overlaps


if __name__ == "__main__":
    inventory = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    boundary_data = json.loads(DISTRICT_BOUNDARIES_PATH.read_text(encoding="utf-8"))
    counts, unmatched, overlaps = classify_features(inventory["features"], boundary_data["features"])
    print(json.dumps({"total": len(inventory["features"]), "district_counts": dict(sorted(counts.items())), "unmatched": len(unmatched), "overlaps": len(overlaps)}, indent=2))
