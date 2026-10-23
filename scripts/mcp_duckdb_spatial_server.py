#!/usr/bin/env python3
"""HIMA-LENS DuckDB Spatial Model Context Protocol (MCP) Server.

Implements Model Context Protocol (JSON-RPC 2.0 over Stdio) for Antigravity.
Exposes zero-token spatial querying, analytical geospatial SQL, buffer analysis,
and direct querying of GeoJSON/Shapefile/Parquet datasets via DuckDB Spatial.
"""
import sys
import json
import os
import duckdb

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Initialize in-memory DuckDB with spatial extension pre-loaded
con = duckdb.connect()
con.execute("INSTALL spatial; LOAD spatial;")

TOOLS = [
    {
        "name": "duckdb_spatial_sql",
        "description": "Executes analytical geospatial SQL queries using DuckDB Spatial (ST_Point, ST_Intersects, ST_Distance, ST_Buffer, ST_Within, ST_Area, etc.). Returns results as JSON records.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "SQL query to execute with DuckDB Spatial extension active."
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "duckdb_query_geojson",
        "description": "Runs high-performance analytical SQL directly against local GeoJSON files (e.g. landslides_clean.geojson, district_boundaries.geojson) via DuckDB ST_Read without loading multi-megabyte files into memory.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "geojson_path": {
                    "type": "string",
                    "description": "Relative path to GeoJSON file (e.g., 'landslides_clean.geojson' or 'static/data/mandi_roads.geojson')."
                },
                "where_clause": {
                    "type": "string",
                    "description": "Optional SQL WHERE filter (e.g. \"district = 'Mandi'\" or \"severity = 'High'\")."
                },
                "columns": {
                    "type": "string",
                    "description": "Comma-separated columns to select (default: '*').",
                    "default": "*"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum records to return (default: 10, max: 50).",
                    "default": 10
                }
            },
            "required": ["geojson_path"]
        }
    },
    {
        "name": "duckdb_proximity_search",
        "description": "Finds spatial features (e.g., historical landslides or roads) within a given radius in meters from a target [longitude, latitude] coordinate using spherical ST_Distance_Spheroid.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "target_lon": {"type": "number", "description": "Target longitude (e.g. 76.93)"},
                "target_lat": {"type": "number", "description": "Target latitude (e.g. 31.71)"},
                "radius_km": {"type": "number", "description": "Search radius in kilometers (default: 5.0)", "default": 5.0},
                "limit": {"type": "integer", "description": "Maximum records (default: 5)", "default": 5}
            },
            "required": ["target_lon", "target_lat"]
        }
    }
]


def handle_duckdb_spatial_sql(args):
    query = args.get("query", "").strip()
    if not query:
        return {"error": "Empty query provided"}
    try:
        # Prevent destructive operations
        lower = query.lower()
        if any(w in lower for w in ["drop ", "delete ", "update ", "alter ", "insert "]):
            return {"error": "Write operations not permitted in read-only spatial server."}
        
        rel = con.execute(query)
        cols = [desc[0] for desc in rel.description]
        rows = rel.fetchmany(100)
        
        records = []
        for r in rows:
            rec = {}
            for col_name, val in zip(cols, r):
                if isinstance(val, (bytes, bytearray)):
                    rec[col_name] = f"<GEOMETRY_BYTES_{len(val)}B>"
                else:
                    rec[col_name] = val
            records.append(rec)
            
        return {"row_count": len(records), "columns": cols, "records": records}
    except Exception as e:
        return {"error": str(e)}


def handle_duckdb_query_geojson(args):
    rel_path = args.get("geojson_path", "").strip()
    where_clause = args.get("where_clause", "").strip()
    cols = args.get("columns", "*").strip()
    limit = min(50, max(1, int(args.get("limit", 10))))

    full_path = os.path.join(ROOT_DIR, rel_path) if not os.path.isabs(rel_path) else rel_path
    if not os.path.exists(full_path):
        return {"error": f"File not found: {rel_path}"}

    # Normalize Windows backslashes for DuckDB string literal
    norm_path = full_path.replace("\\", "/")

    sql = f"SELECT {cols} FROM ST_Read('{norm_path}')"
    if where_clause:
        sql += f" WHERE {where_clause}"
    sql += f" LIMIT {limit}"

    return handle_duckdb_spatial_sql({"query": sql})


def handle_duckdb_proximity(args):
    lon = float(args.get("target_lon"))
    lat = float(args.get("target_lat"))
    radius_km = float(args.get("radius_km", 5.0))
    limit = min(20, max(1, int(args.get("limit", 5))))

    data_path = os.path.join(ROOT_DIR, "landslides_clean.geojson").replace("\\", "/")
    
    # 1 degree lat approx 111km; filter bbox first for index speed
    d_lat = radius_km / 111.0
    d_lon = radius_km / (111.0 * math.cos(math.radians(lat)) + 1e-6)

    min_lon, max_lon = lon - d_lon, lon + d_lon
    min_lat, max_lat = lat - d_lat, lat + d_lat

    sql = f"""
    SELECT 
        id, district, location, movement_type, severity,
        ST_X(geom) AS lon, ST_Y(geom) AS lat,
        ROUND(ST_Distance_Sphere(geom, ST_Point({lon}, {lat})) / 1000.0, 2) AS distance_km
    FROM ST_Read('{data_path}')
    WHERE ST_X(geom) BETWEEN {min_lon} AND {max_lon}
      AND ST_Y(geom) BETWEEN {min_lat} AND {max_lat}
    ORDER BY distance_km ASC
    LIMIT {limit};
    """
    return handle_duckdb_spatial_sql({"query": sql})


def main():
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        try:
            req = json.loads(line)
        except Exception:
            continue

        method = req.get("method")
        msg_id = req.get("id")

        if method == "initialize":
            res = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "hima-lens-duckdb-spatial", "version": "1.0.0"}
            }
            resp = {"jsonrpc": "2.0", "id": msg_id, "result": res}
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        elif method == "tools/list":
            resp = {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}}
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        elif method == "tools/call":
            params = req.get("params", {})
            name = params.get("name")
            args = params.get("arguments", {})

            if name == "duckdb_spatial_sql":
                result = handle_duckdb_spatial_sql(args)
            elif name == "duckdb_query_geojson":
                result = handle_duckdb_query_geojson(args)
            elif name == "duckdb_proximity_search":
                result = handle_duckdb_proximity(args)
            else:
                result = {"error": f"Unknown tool: {name}"}

            resp = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                }
            }
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
