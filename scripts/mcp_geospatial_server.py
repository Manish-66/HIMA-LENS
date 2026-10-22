#!/usr/bin/env python3
"""
HIMA-LENS Geospatial & Geotechnical Model Context Protocol (MCP) Server
Implements Model Context Protocol (JSON-RPC 2.0 over Stdio) for Antigravity.
Exposes zero-token spatial querying, coordinate validation, geotechnical FOS calculation, and live precipitation.
"""
import sys
import json
import math
import os
import urllib.request

# Territorial Bbox for Himachal Pradesh
HP_BBOX = {"min_lon": 75.78, "max_lon": 79.07, "min_lat": 30.36, "max_lat": 33.20}

# Path to landslides clean GeoJSON
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(ROOT_DIR, "landslides_clean.geojson")

TOOLS = [
    {
        "name": "query_spatial_inventory",
        "description": "Filters and queries HIMA-LENS landslide records without loading the 6MB GeoJSON into agent context. Returns summarized metadata and up to N records.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "district": {"type": "string", "description": "Optional district filter (e.g., Mandi, Shimla, Kullu, Kangra)"},
                "movement_type": {"type": "string", "description": "Optional movement type (e.g., Slide, Flow, Fall, Topple)"},
                "limit": {"type": "integer", "description": "Maximum number of records to return (default: 5, max: 20)", "default": 5}
            }
        }
    },
    {
        "name": "validate_coordinates",
        "description": "Validates longitude and latitude against RFC 7946 GeoJSON order and Himachal Pradesh territory [75.78-79.07 E, 30.36-33.20 N]. Flags inverted lat/lon.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "longitude": {"type": "number", "description": "Longitude in decimal degrees (e.g., 76.93)"},
                "latitude": {"type": "number", "description": "Latitude in decimal degrees (e.g., 31.71)"}
            },
            "required": ["longitude", "latitude"]
        }
    },
    {
        "name": "calculate_slope_fos",
        "description": "Computes deterministic limit-equilibrium Factor of Safety (FOS) for translational mountain slope failure.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "slope_angle_deg": {"type": "number", "description": "Slope inclination angle in degrees (e.g. 35.0)"},
                "depth_m": {"type": "number", "description": "Depth to slip plane in meters (e.g. 3.0)"},
                "cohesion_kpa": {"type": "number", "description": "Effective soil/debris cohesion in kPa (e.g. 10.0)"},
                "friction_angle_deg": {"type": "number", "description": "Effective friction angle phi in degrees (e.g. 28.0)"},
                "unit_weight_kn_m3": {"type": "number", "description": "Soil unit weight in kN/m3 (default: 20.0)", "default": 20.0},
                "water_ratio": {"type": "number", "description": "Pore pressure ratio ru (0.0=dry, 0.5=partially saturated, 1.0=fully saturated)", "default": 0.3}
            },
            "required": ["slope_angle_deg", "depth_m", "cohesion_kpa", "friction_angle_deg"]
        }
    },
    {
        "name": "fetch_himalayan_precipitation",
        "description": "Queries live and recent rainfall data from Open-Meteo for any coordinate in Himachal Pradesh to assess monsoon threshold triggers.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number", "description": "Latitude (e.g., 31.7087 for Mandi)"},
                "longitude": {"type": "number", "description": "Longitude (e.g., 76.9321 for Mandi)"},
                "past_days": {"type": "integer", "description": "Number of antecedent days to inspect (default: 3)", "default": 3}
            },
            "required": ["latitude", "longitude"]
        }
    }
]

def handle_query_inventory(args):
    dist_filter = (args.get("district") or "").lower()
    mov_filter = (args.get("movement_type") or "").lower()
    limit = min(args.get("limit", 5), 20)

    if not os.path.exists(DATA_PATH):
        return {"error": f"Dataset file not found at {DATA_PATH}"}

    matched = []
    total_matched = 0

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    for feat in data.get("features", []):
        props = feat.get("properties", {})
        d = (props.get("district") or "").lower()
        m = (props.get("movement_type") or "").lower()

        if dist_filter and dist_filter not in d:
            continue
        if mov_filter and mov_filter not in m:
            continue

        total_matched += 1
        if len(matched) < limit:
            matched.append({
                "id": props.get("id"),
                "district": props.get("district"),
                "movement_type": props.get("movement_type"),
                "material_type": props.get("material_type"),
                "coordinates": feat.get("geometry", {}).get("coordinates")
            })

    return {
        "status": "success",
        "total_matched": total_matched,
        "returned_count": len(matched),
        "sample_records": matched
    }

def handle_validate_coordinates(args):
    lon = float(args.get("longitude", 0))
    lat = float(args.get("latitude", 0))

    # Inverted check
    if 30.0 <= lon <= 34.0 and 75.0 <= lat <= 80.0:
        return {
            "valid": False,
            "error": f"INVERTED_COORDINATES: Given lon={lon}, lat={lat}. Longitude in HP must be ~76-79°E and Latitude ~30-33°N. Swap coordinates to [lon={lat}, lat={lon}]."
        }

    in_bbox = (HP_BBOX["min_lon"] <= lon <= HP_BBOX["max_lon"]) and (HP_BBOX["min_lat"] <= lat <= HP_BBOX["max_lat"])

    return {
        "valid": in_bbox,
        "longitude": lon,
        "latitude": lat,
        "within_himachal_pradesh": in_bbox,
        "note": "RFC 7946 GeoJSON order [longitude, latitude] respected." if in_bbox else "Coordinate lies outside Himachal Pradesh territorial extent."
    }

def handle_calculate_fos(args):
    beta = math.radians(float(args["slope_angle_deg"]))
    phi = math.radians(float(args["friction_angle_deg"]))
    c = float(args["cohesion_kpa"])
    z = float(args["depth_m"])
    gamma = float(args.get("unit_weight_kn_m3", 20.0))
    m = float(args.get("water_ratio", 0.3))
    gamma_w = 9.81

    driving_shear = gamma * z * math.sin(beta) * math.cos(beta)
    if driving_shear <= 0:
        return {"fos": 99.0, "status": "Horizontal / Indeterminate"}

    u = m * gamma_w * z * (math.cos(beta) ** 2)
    effective_normal = (gamma * z * (math.cos(beta) ** 2)) - u
    resisting_shear = c + max(0, effective_normal) * math.tan(phi)
    fos = resisting_shear / driving_shear

    status = "Critically Unstable (FOS < 1.0)" if fos < 1.0 else ("Marginally Stable (1.0 <= FOS < 1.3)" if fos < 1.3 else "Stable (FOS >= 1.3)")

    return {
        "fos": round(fos, 3),
        "status": status,
        "driving_shear_kpa": round(driving_shear, 2),
        "resisting_shear_kpa": round(resisting_shear, 2),
        "effective_normal_stress_kpa": round(effective_normal, 2),
        "pore_pressure_kpa": round(u, 2)
    }

def handle_fetch_precipitation(args):
    lat = float(args["latitude"])
    lon = float(args["longitude"])
    past_days = int(args.get("past_days", 3))

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=precipitation&past_days={past_days}&forecast_days=1&timezone=Asia%2FKolkata"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "HIMA-LENS-MCP/1.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        hourly_precip = data.get("hourly", {}).get("precipitation", [])
        total_precip_mm = round(sum(hourly_precip), 2)
        peak_intensity_mm_h = round(max(hourly_precip) if hourly_precip else 0, 2)

        return {
            "status": "success",
            "coordinates": {"latitude": lat, "longitude": lon},
            "past_days_accumulated_rainfall_mm": total_precip_mm,
            "peak_hourly_intensity_mm_per_hr": peak_intensity_mm_h,
            "threshold_advisory": "HIGH MONSOON HAZARD" if total_precip_mm > 100 else ("ELEVATED DEBRIS FLOW RISK" if total_precip_mm > 40 else "NORMAL / LOW RISK")
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def process_request(req):
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "hima-lens-geospatial", "version": "1.0.0"}
            }
        }
    elif method == "notifications/initialized":
        return None
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": TOOLS}
        }
    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})

        if name == "query_spatial_inventory":
            res = handle_query_inventory(args)
        elif name == "validate_coordinates":
            res = handle_validate_coordinates(args)
        elif name == "calculate_slope_fos":
            res = handle_calculate_fos(args)
        elif name == "fetch_himalayan_precipitation":
            res = handle_fetch_precipitation(args)
        else:
            res = {"error": f"Unknown tool: {name}"}

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": json.dumps(res, indent=2)}]
            }
        }
    else:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"}
        }

def main():
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            res = process_request(req)
            if res:
                sys.stdout.write(json.dumps(res) + "\n")
                sys.stdout.flush()
        except Exception as e:
            err_res = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}
            sys.stdout.write(json.dumps(err_res) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
