"""
Automated data pipeline to extract, reproject, deduplicate, and optimize ArcGIS layers
for HIMA-LENS web GIS visualization.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
import geopandas as gpd
import numpy as np
import pandas as pd
from PIL import Image
from pyproj import Transformer
import rasterio
from rasterio.warp import Resampling, calculate_default_transform, reproject
from shapely.geometry import mapping

ROOT_DIR = Path(__file__).resolve().parent.parent
SCRATCH_DIR = Path(r"C:\Users\Manish kumar\.gemini\antigravity\brain\24ded147-4c0d-4e5b-8d60-d53201155725\scratch")
STATIC_DATA_DIR = ROOT_DIR / "static" / "data"
STATIC_OVERLAYS_DIR = ROOT_DIR / "static" / "overlays"
STATIC_DATA_DIR.mkdir(parents=True, exist_ok=True)
STATIC_OVERLAYS_DIR.mkdir(parents=True, exist_ok=True)


def process_roads():
    print("--- 1. Processing Mandi Roads ---")
    roads_shp = SCRATCH_DIR / "Mandi_roads" / "commondata" / "chapter" / "Mandi all roads.shp"
    if not roads_shp.exists():
        raise FileNotFoundError(f"Roads shapefile not found at {roads_shp}")

    gdf = gpd.read_file(roads_shp)
    print(f"Loaded {len(gdf)} road segments in {gdf.crs}")

    # Reproject to WGS84
    gdf_4326 = gdf.to_crs(epsg=4326)

    # Simplify slightly (0.00008 deg ~ 8m) to ensure 60fps web rendering while maintaining sharp road paths
    gdf_4326["geometry"] = gdf_4326.geometry.simplify(0.00008, preserve_topology=True)

    # Select and rename essential attributes
    out_features = []
    for idx, row in gdf_4326.iterrows():
        geom = row.geometry
        if geom is None or geom.is_empty:
            continue
        work_name = str(row.get("WORK_NAME") or "").strip()
        length_val = row.get("PROPOSED_L")
        try:
            length_km = round(float(length_val), 2) if length_val is not None else None
        except (ValueError, TypeError):
            length_km = None
        category = str(row.get("RoadCatego") or "Rural Road").strip()
        mrl_id = str(row.get("MRL_ID") or idx)

        out_features.append({
            "type": "Feature",
            "properties": {
                "id": mrl_id,
                "name": work_name if work_name else f"Road Segment {mrl_id}",
                "length_km": length_km,
                "category": category,
            },
            "geometry": mapping(geom)
        })

    roads_geojson = {
        "type": "FeatureCollection",
        "features": out_features
    }

    out_file = STATIC_DATA_DIR / "mandi_roads.geojson"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(roads_geojson, f, separators=(",", ":"))
    print(f"Saved {len(out_features)} road segments to {out_file} ({out_file.stat().st_size / (1024*1024):.2f} MB)")


def process_polygons():
    print("\n--- 2. Processing Landslide Polygons ---")
    poly_gdb = SCRATCH_DIR / "Hp_landslide_polygon" / "p20" / "perspective_maps.gdb"
    gdf = gpd.read_file(poly_gdb, layer="Landslidepolygon_hp")
    print(f"Loaded {len(gdf)} polygons statewide in {gdf.crs}")

    # Mandi Polygons (full resolution)
    mandi_gdf = gdf[gdf["DISTRICT"].str.strip().str.lower() == "mandi"].copy()
    print(f"Mandi polygons count: {len(mandi_gdf)}")

    def format_poly_feature(row, idx):
        geom = row.geometry
        if geom is None or geom.is_empty:
            return None
        geo_dict = mapping(geom)
        if geo_dict.get("type") == "MultiPolygon" and len(geo_dict.get("coordinates", [])) == 1:
            geo_dict = {"type": "Polygon", "coordinates": geo_dict["coordinates"][0]}
        return {
            "type": "Feature",
            "properties": {
                "id": f"POLY_{int(row.get('OBJECTID') or idx)}",
                "district": str(row.get("DISTRICT") or "").strip(),
                "state": str(row.get("STATE") or "Himachal Pradesh").strip(),
                "lulc": str(row.get("LULC") or "").strip() or "Not recorded",
                "geomorphology": str(row.get("GEOM") or "").strip() or "Not recorded",
                "material_type": str(row.get("MATERIAL_T") or "").strip() or "Debris / Soil",
                "area_sq_m": round(float(row.get("Shape_Area") or 0) * (111000**2), 1),
                "toposheet": str(row.get("TOPOSHEET") or "").strip(),
            },
            "geometry": geo_dict
        }

    mandi_features = [format_poly_feature(row, i) for i, (_, row) in enumerate(mandi_gdf.iterrows())]
    mandi_features = [f for f in mandi_features if f is not None]

    out_mandi = STATIC_DATA_DIR / "landslide_polygons_mandi.geojson"
    with open(out_mandi, "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": mandi_features}, f, separators=(",", ":"))
    print(f"Saved {len(mandi_features)} Mandi polygons to {out_mandi} ({out_mandi.stat().st_size / (1024*1024):.2f} MB)")

    # Simplified Statewide Polygons (0.0001 deg ~ 11m)
    gdf_simp = gdf.copy()
    gdf_simp["geometry"] = gdf_simp.geometry.simplify(0.0001, preserve_topology=True)
    hp_features = [format_poly_feature(row, i) for i, (_, row) in enumerate(gdf_simp.iterrows())]
    hp_features = [f for f in hp_features if f is not None]

    out_hp = STATIC_DATA_DIR / "landslide_polygons_hp.geojson"
    with open(out_hp, "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": hp_features}, f, separators=(",", ":"))
    print(f"Saved {len(hp_features)} statewide polygons to {out_hp} ({out_hp.stat().st_size / (1024*1024):.2f} MB)")


def process_points_dedup():
    print("\n--- 3. Master Deduplicated Landslide Points ---")
    # Load Mandi detailed field survey (9,399 points)
    df_xlsx = pd.read_excel(ROOT_DIR / "data.xlsx")
    print(f"Loaded {len(df_xlsx)} Mandi field survey records from data.xlsx")

    # Load statewide GSI points from lpkx (6,287 points)
    pts_gdb = SCRATCH_DIR / "Hp_landslide_points" / "p20" / "perspective_maps.gdb"
    pts_gdf = gpd.read_file(pts_gdb, layer="LandslidePoint_hp")
    print(f"Loaded {len(pts_gdf)} GSI statewide points from Hp_landslide_points")

    # 1. Ingest Mandi field survey
    master_features = []
    seen_coords = set()

    for idx, row in df_xlsx.iterrows():
        try:
            lng = float(row["LONGITUDE"])
            lat = float(row["LATITUDE"])
        except (ValueError, TypeError):
            continue
        coord_key = (round(lng, 4), round(lat, 4))
        seen_coords.add(coord_key)

        dist_val = row.get("Distance to Road (m)")
        try:
            dist_road = round(float(dist_val), 1) if pd.notna(dist_val) else None
        except (ValueError, TypeError):
            dist_road = None

        period_val = str(row.get("Period") or "").strip()
        activity_val = str(row.get("ACTIVITY") or "").strip()
        movement_val = str(row.get("MOVEMENT_T") or "").strip()
        material_val = str(row.get("MATERIAL_T") or "").strip()

        master_features.append({
            "type": "Feature",
            "properties": {
                "id": f"MANDI_{int(row.get('OBJECTID_1') or idx)}",
                "district": "Mandi",
                "state": "Himachal Pradesh",
                "activity": activity_val if activity_val and activity_val.lower() != "nan" else "Unknown",
                "style": str(row.get("STYLE") or "").strip() or None,
                "movement_type": movement_val if movement_val and movement_val.lower() != "nan" else "Slide",
                "material_type": material_val if material_val and material_val.lower() != "nan" else "Unknown",
                "period": period_val if period_val and period_val.lower() != "nan" else "Pre-monsoon",
                "year": period_val if period_val and period_val.lower() != "nan" else "Pre-monsoon",
                "distance_to_road_m": dist_road,
                "source": "Mandi Detailed Field Inventory (10m Resolution)"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [round(lng, 6), round(lat, 6)]
            }
        })

    print(f"Ingested {len(master_features)} detailed Mandi points.")

    # 2. Ingest Statewide GSI points (skipping any duplicate coordinates)
    gsi_added = 0
    gsi_duplicates_skipped = 0

    # District normalization map
    dist_map = {
        "sirmour": "Sirmaur",
        "sirmur": "Sirmaur",
        "lahul & spiti": "Lahaul and Spiti",
        "lahaul & spiti": "Lahaul and Spiti",
        "lahul and spiti": "Lahaul and Spiti",
    }

    for idx, row in pts_gdf.iterrows():
        geom = row.geometry
        if geom is None or geom.is_empty:
            continue
        lng, lat = geom.x, geom.y
        coord_key = (round(lng, 4), round(lat, 4))

        if coord_key in seen_coords:
            gsi_duplicates_skipped += 1
            continue

        raw_dist = str(row.get("DISTRICT") or "Unknown").strip()
        norm_dist = dist_map.get(raw_dist.lower(), raw_dist)

        # Skip points located in neighboring states (e.g. Kathua, Doda, Bageshwar, Gurdaspur)
        if norm_dist.lower() in ("kathua", "doda", "bageshwar", "gurdaspur", "udhampur"):
            continue

        seen_coords.add(coord_key)
        gsi_added += 1

        activity = str(row.get("ACTIVITY") or "").strip() or "Active"
        movement = str(row.get("MOVEMENT_T") or "").strip() or "Slide"
        material = str(row.get("MATERIAL_T") or "").strip() or "Rock"
        style = str(row.get("STYLE") or "").strip() or "Single"
        trigger = str(row.get("TRIGGERING") or "").strip() or "Rainfall"
        geology = str(row.get("GEOLOGY") or "").strip() or "Not recorded"
        hydrology = str(row.get("HYDROLOGIC") or "").strip() or "Not recorded"
        landuse = str(row.get("LANDUSE_LA") or "").strip() or "Not recorded"

        slide_no = str(row.get("SLIDE_NO") or f"HP_{idx}").strip()

        master_features.append({
            "type": "Feature",
            "properties": {
                "id": slide_no,
                "district": norm_dist,
                "state": "Himachal Pradesh",
                "activity": activity,
                "style": style,
                "movement_type": movement,
                "material_type": material,
                "period": "Pre-monsoon",
                "year": "Pre-monsoon",
                "triggering": trigger,
                "geology": geology,
                "hydrologic": hydrology,
                "landuse_la": landuse,
                "source": "GSI Statewide Landslide Inventory"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [round(lng, 6), round(lat, 6)]
            }
        })

    print(f"Statewide GSI points added: {gsi_added}")
    print(f"GSI duplicate points skipped: {gsi_duplicates_skipped}")
    print(f"Total deduplicated master points: {len(master_features)}")

    out_clean = ROOT_DIR / "landslides_clean.geojson"
    with open(out_clean, "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": master_features}, f, separators=(",", ":"))
    print(f"Saved master deduplicated points to {out_clean} ({out_clean.stat().st_size / (1024*1024):.2f} MB)")


def process_rasters():
    print("\n--- 4. Generating Transparent Environmental Overlays ---")
    datasets = [
        {
            "name": "lulc",
            "title": "Land Use / Land Cover (2023)",
            "path": SCRATCH_DIR / "Mandi_LULC" / "p20" / "chapter.gdb",
            "out_png": STATIC_OVERLAYS_DIR / "mandi_lulc.png",
            "colormap": {
                0: (0, 0, 0, 0),         # NoData
                1: (65, 155, 223, 210),   # Water
                2: (53, 130, 74, 210),    # Trees / Forest
                5: (228, 150, 53, 210),   # Crops
                7: (196, 40, 27, 210),    # Built Area
                8: (165, 155, 143, 210),  # Bare Ground
                9: (168, 235, 255, 210),  # Snow / Ice
                10: (97, 97, 97, 210),    # Clouds
                11: (226, 207, 135, 210)  # Rangeland
            },
            "legend": [
                {"label": "Forest / Trees", "color": "#35824a"},
                {"label": "Rangeland", "color": "#e2cf87"},
                {"label": "Crops", "color": "#e49635"},
                {"label": "Built Area", "color": "#c4281b"},
                {"label": "Water", "color": "#419bdf"},
                {"label": "Bare Ground", "color": "#a59b8f"},
                {"label": "Snow / Ice", "color": "#a8ebff"}
            ]
        },
        {
            "name": "geomorphology",
            "title": "Geomorphology",
            "path": SCRATCH_DIR / "Mandi_geomorphology" / "p20" / "chapter.gdb",
            "out_png": STATIC_OVERLAYS_DIR / "mandi_geomorphology.png",
            "colormap": {
                0: (0, 0, 0, 0),
                1: (180, 80, 50, 200),    # Highly Dissected Hills
                2: (220, 200, 140, 200),  # Alluvial Plain
                3: (100, 180, 220, 200),  # Flood Plain
                4: (160, 160, 160, 200),  # Anthropogenic
                5: (210, 140, 80, 200),   # Moderately Dissected Hills
                6: (40, 120, 210, 200),   # River
                7: (220, 60, 60, 200),    # Mass Wasting Products
                8: (30, 90, 180, 200),    # Dam / Reservoir
                9: (70, 160, 200, 200),   # Waterbodies
                10: (180, 170, 120, 200), # Piedmont Slope
                11: (220, 240, 255, 200), # Snow Cover
                12: (230, 190, 100, 200)  # Low Dissected Hills
            },
            "legend": [
                {"label": "Highly Dissected Hills", "color": "#b45032"},
                {"label": "Moderately Dissected Hills", "color": "#d28c50"},
                {"label": "Low Dissected Hills", "color": "#e6be64"},
                {"label": "Alluvial / Flood Plain", "color": "#dcc88c"},
                {"label": "Mass Wasting Products", "color": "#dc3c3c"},
                {"label": "Rivers & Waterbodies", "color": "#2878d2"}
            ]
        },
        {
            "name": "lithology",
            "title": "Lithology (Bedrock Geology)",
            "path": SCRATCH_DIR / "Mandi_lithology" / "p20" / "chapter.gdb",
            "out_png": STATIC_OVERLAYS_DIR / "mandi_lithology.png",
            "colormap": {
                0: (0, 0, 0, 0),
                1: (120, 110, 100, 200), 2: (130, 140, 120, 200), 3: (140, 160, 190, 200),
                4: (150, 170, 180, 200), 5: (160, 190, 170, 200), 6: (170, 180, 160, 200),
                7: (180, 170, 150, 200), 8: (190, 140, 130, 200), 9: (200, 130, 150, 200),
                10: (210, 180, 140, 200), 11: (220, 190, 150, 200), 12: (160, 150, 190, 200),
                13: (170, 160, 200, 200), 14: (140, 180, 150, 200), 15: (150, 190, 160, 200),
                16: (200, 170, 130, 200), 17: (210, 160, 120, 200), 18: (190, 150, 110, 200),
                19: (230, 200, 160, 200), 20: (210, 130, 110, 200), 21: (200, 120, 100, 200),
                22: (190, 110, 90, 200),  23: (210, 140, 110, 200), 24: (180, 150, 160, 200),
                25: (160, 180, 160, 200), 26: (170, 160, 180, 200), 27: (200, 180, 140, 200),
                28: (150, 160, 170, 200), 29: (160, 170, 180, 200), 30: (170, 180, 190, 200),
                31: (180, 190, 200, 200)
            },
            "legend": [
                {"label": "Shale, Slate, Quartzite, Dolomite", "color": "#c8b48c"},
                {"label": "Quartzite & Shale Formations", "color": "#c8aa82"},
                {"label": "Sandstone, Clay & Siltstone", "color": "#d2826e"},
                {"label": "Phyllite & Schist Formations", "color": "#96be96"},
                {"label": "Dolomite & Limestone Groups", "color": "#8ca0be"},
                {"label": "Granite, Gneiss & Aplite", "color": "#c88296"}
            ]
        }
    ]

    overlay_meta = {}

    for ds in datasets:
        print(f"Processing raster {ds['name']}...")
        with rasterio.open(ds["path"]) as src:
            dst_crs = "EPSG:4326"
            dst_width = 1400
            dst_height = int(dst_width * (src.height / src.width))

            transform, width, height = calculate_default_transform(
                src.crs, dst_crs, src.width, src.height, *src.bounds,
                dst_width=dst_width, dst_height=dst_height
            )

            dest = np.zeros((height, width), dtype=np.uint8)

            reproject(
                source=rasterio.band(src, 1),
                destination=dest,
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=transform,
                dst_crs=dst_crs,
                resampling=Resampling.nearest
            )

            transformer = Transformer.from_crs(src.crs, dst_crs, always_xy=True)
            minx, miny = transformer.transform(src.bounds.left, src.bounds.bottom)
            maxx, maxy = transformer.transform(src.bounds.right, src.bounds.top)
            bounds = [[round(miny, 6), round(minx, 6)], [round(maxy, 6), round(maxx, 6)]]

            rgba = np.zeros((height, width, 4), dtype=np.uint8)
            cmap = ds["colormap"]
            for val, color in cmap.items():
                mask = (dest == val)
                if np.any(mask):
                    rgba[mask] = color

            img = Image.fromarray(rgba, "RGBA")
            img.save(ds["out_png"], format="PNG", optimize=True)
            alt_png = STATIC_OVERLAYS_DIR / f"{ds['name']}.png"
            if alt_png != ds["out_png"]:
                img.save(alt_png, format="PNG", optimize=True)
            print(f"  Saved {ds['out_png']} and {alt_png} ({ds['out_png'].stat().st_size / 1024:.1f} KB), Bounds: {bounds}")

            overlay_meta[ds["name"]] = {
                "title": ds["title"],
                "url": f"/static/overlays/{ds['name']}.png",
                "bounds": bounds,
                "legend": ds["legend"]
            }

    meta_path = STATIC_OVERLAYS_DIR / "metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(overlay_meta, f, indent=2)
    print(f"Saved raster overlays metadata to {meta_path}")


if __name__ == "__main__":
    try:
        process_roads()
        process_polygons()
        process_points_dedup()
        process_rasters()
        print("\nAll ArcGIS layers successfully processed and optimized for HIMA-LENS!")
    except Exception as e:
        print(f"\nPipeline failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
