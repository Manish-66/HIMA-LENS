---
name: spatial-discipline
description: "Use whenever working with spatial datasets, GeoJSON files, GIS coordinates, map projections (CRS), bounding boxes, or PostGIS spatial queries. Enforces RFC 7946 [lon, lat] coordinate order, Himachal Pradesh spatial bounding box bounds [75.78, 30.36, 79.07, 33.20], projection transformations (EPSG:4326 vs UTM Zone 43N EPSG:32643), and topological geometry validity."
---

# Spatial Discipline & Coordinate Integrity Guardrails

This skill establishes strict validation rules for GIS, GeoJSON, and PostGIS engineering across HIMA-LENS.

## 1. Absolute Rule: Coordinate Order (RFC 7946 vs Leaflet/MapLibre)

*   **GeoJSON Standard (RFC 7946):** Coordinate pairs in GeoJSON geometries MUST strictly follow `[longitude, latitude]` (Eastings, Northings):
    ```json
    { "type": "Point", "coordinates": [76.9321, 31.7087] }
    ```
*   **Common Trap:** Leaflet, Google Maps, and human speech use `(latitude, longitude)`. Inverting coordinates will place Himalayan landslide records into the Indian Ocean or Antarctica.
*   **Verification:**
    *   First coordinate must be Longitude ($\sim 75^\circ$ to $79^\circ$).
    *   Second coordinate must be Latitude ($\sim 30^\circ$ to $33^\circ$).

## 2. Himachal Pradesh Territorial Bounding Box

All landslide inventory points and hazard wire alerts must fall inside the administrative boundary of Himachal Pradesh:
*   **Minimum Longitude (West):** `75.78° E`
*   **Maximum Longitude (East):** `79.07° E`
*   **Minimum Latitude (South):** `30.36° N`
*   **Maximum Latitude (North):** `33.20° N`

Any point with $\text{latitude} < 30.0$ or $\text{latitude} > 34.0$ or $\text{longitude} < 75.0$ or $\text{longitude} > 80.0$ is corrupted, swapped, or an invalid entry.

## 3. Coordinate Reference Systems (CRS) & Projections

*   **Display & Storage (EPSG:4326):**
    *   WGS84 Geographic coordinates in decimal degrees.
    *   Used for GeoJSON storage, API transfer, and MapLibre/Cesium rendering.
    *   *Warning:* Never calculate slope lengths, buffer radii, or runout distances directly in decimal degrees! $1^\circ$ longitude in Mandi is $\approx 94.7\text{ km}$, while $1^\circ$ latitude is $\approx 110.9\text{ km}$.
*   **Metric Geotechnical Computations (EPSG:32643 - UTM Zone 43N):**
    *   Himachal Pradesh lies in UTM Zone 43N (`EPSG:32643`).
    *   When computing scarp widths, crown-to-toe runout distance, or buffer zones in meters, project coordinates to `EPSG:32643`.

## 4. PostGIS SQL Generation Standards

When writing PostGIS queries or migrations for Supabase:
*   Always use `ST_MakePoint(longitude, latitude)` — Longitude goes first!
*   Always define SRID: `ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)`.
*   For metric distance queries without reprojection, cast geometry to geography:
    ```sql
    -- Landslides within 5km of a road point:
    SELECT id, district, movement_type
    FROM community_reports
    WHERE ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint(76.93, 31.71), 4326)::geography, 5000);
    ```
*   Always ensure spatial index exists:
    ```sql
    CREATE INDEX IF NOT EXISTS idx_community_reports_geom ON public.community_reports USING GIST (geom);
    ```

## 5. Automated Validation Helper

Run the built-in validator script on any spatial file:
```powershell
python .agents/skills/spatial-discipline/scripts/validate_spatial.py landslides_clean.geojson
```
