---
name: geo-cartography
description: "Use whenever generating, styling, rendering, or reviewing map figures, GIS layouts, or spatial plates for engineering reports and statutory PPR/DPR documents. Enforces Survey of India (SoI) / GSI cartographic standards, true North arrows, dual graphic bar scales (metric), coordinate graticules (WGS84 / UTM 43N), contour interval labeling, inset regional index maps, and high-contrast hillshade baseplates."
---

# Statutory Cartographic Standards for Engineering Reports
### Survey of India (SoI) & Geological Survey of India (GSI) Alignment

This skill enforces professional cartographic discipline for all map figures, spatial plates, and location figures embedded in statutory engineering reports, specifically Section 3 (*Location Map of Landslide-Prone Area*) of the HPPWD Preliminary Project Report (PPR).

Experienced field engineers and statutory authorities reject raw, unannotated web-map screenshots. Every spatial figure must function as a standalone, legally defensible survey document.

---

## 1. The 7 Mandatory Elements of an Engineering Map Plate

Every map figure embedded in an engineering dossier must contain the following seven components:

```
┌────────────────────────────────────────────────────────────────────────┐
│ [1. FIGURE TITLE & STATIONING]                                         │
│ Location Plan & Geomorphological Terrain Setting • Km 124+800 (NH-154) │
├──────────────────────────────────────────────────────┬─────────────────┤
│                                                      │ [2. NORTH ARROW]│
│                                                      │        ▲ N      │
│                                                      │        │        │
│                                                      ├─────────────────┤
│                                                      │ [3. INSET MAP]  │
│                   PRIMARY MAP CANVAS                 │ Regional Index  │
│             (Hillshade DEM + Orthophoto)             │ District Mandi  │
│                                                      ├─────────────────┤
│                                                      │ [4. LEGEND]     │
│   • Red Dashed: Active Crown Scarp                   │ ─── Carriageway │
│   • Amber Hatch: Displaced Colluvium                 │ ─── Road Scarp  │
│   • Cyan Line: Proposed Crest Catchwater Drain       │ ... Seepage Line│
│                                                      ├─────────────────┤
│                                                      │ [5. SCALE BAR]  │
│                                                      │ 0   25  50  100m│
│                                                      │ █▀▀▀█▀▀▀█▀▀▀▀█  │
│                                                      │ 1:1,000 (at A4) │
├──────────────────────────────────────────────────────┴─────────────────┤
│ [6. GEODETIC DATUM & PROJECTION]                                       │
│ Datum: WGS84 • Projection: UTM Zone 43N (EPSG:32643) • Graticule: 100m │
├────────────────────────────────────────────────────────────────────────┤
│ [7. CITATION & TELEMETRY SIGN-OFF]                                     │
│ Source: HIMA-LENS Telemetry Engine • Survey Date: 2026-10-22 • IIT Mandi│
└────────────────────────────────────────────────────────────────────────┘
```

1. **Title Block & Chainage Identification:** Precise site nomenclature, administrative district, highway number, and exact linear chainage.
2. **True North Arrow:** Clean, standardized vertical vector orientation symbol placed in the upper-right corner.
3. **Dual Metric Graphic Scale Bar:** Never write only *"Scale 1:1000"* (which becomes inaccurate when printed at different sizes or screen resolutions). Always provide an explicit **graphic subdivided bar scale** ($0\text{ m}, 25\text{ m}, 50\text{ m}, 100\text{ m}$).
4. **Symbology Legend:** Exhaustive key explaining every color, line style, and symbol used on the plate.
5. **Regional Inset / Index Map:** Small secondary frame ($1:50,000$ or $1:250,000$ scale) showing the regional position of the site within Himachal Pradesh / District boundaries.
6. **Geodetic Coordinate Frame & Projection Statement:**
   - Coordinate System: WGS84 (EPSG:4326).
   - Projected Grid: UTM Zone 43N (EPSG:32643) for Himachal Pradesh ($75.78^\circ\text{ E} - 79.07^\circ\text{ E}$).
   - Graticule: Border tick marks showing latitude/longitude (DMS) or UTM grid coordinates ($100\text{m}$ or $500\text{m}$ intervals).
7. **Source & Date Attribution:** Sponsoring agency (IIT Mandi / HPPWD), data acquisition source (Cartosat-1 / Copernicus DEM / Field RTK-GPS), and survey date.

---

## 2. Standardized Geotechnical Symbology (GSI / SoI)

When rendering geological features, cut slopes, and failure boundaries:

| Feature | Visual Style | Hex / Color | Standard Note |
| :--- | :--- | :---: | :--- |
| **Crown / Main Scarp** | Bold line with downward hachures | `#dc2626` (Red) | Hachures point in direction of displacement. |
| **Active Sliding Mass** | Semi-transparent stippled/diagonal hatch | `rgba(239, 68, 68, 0.25)` | Delineates unstable colluvial volume. |
| **Bedrock Outcrop** | Diagonal cross-hatch | `#64748b` (Slate) | Joint set dip/strike dip symbols ($\top 42^\circ$). |
| **Seepage Line / Springs** | Solid cyan line with water drop glyphs | `#0284c7` (Sky Blue) | Indicates daylighting perched water table. |
| **Catchwater Drain** | Dash-dot line with directional flow arrows | `#0ea5e9` (Blue) | Prescribed crest runoff diversion. |
| **Soil Nail Wall Zone** | Regular diamond grid points | `#0f172a` (Black dots) | Spacing annotated ($2.0\text{m}\times 2.0\text{m}$). |
| **Road Carriageway** | Double solid boundary lines | `#334155` (Dark Gray) | Lane centerline indicated by dashed white. |

---

## 3. High-Contrast Baseplate & Print Legibility

- **Hillshade Illumination Standard:** Solar azimuth $315^\circ$ (Northwest), solar altitude $45^\circ$. This prevents pseudoscopic relief inversion (where valleys appear as ridges).
- **Monochrome / Photocopier Resilience:** All primary boundary lines must be distinguishable by **line pattern** (solid, dashed, dotted, hachured), not solely by color, ensuring full clarity when photocopied in black & white by field offices.
- **Minimum Text Size on A4 Print:**
  - Figure Title: $11\text{ pt}$ Bold.
  - Coordinate tick marks and labels: $7.5\text{ pt} - 8.5\text{ pt}$ Clean Sans-Serif / JetBrains Mono.
  - Legend items: $8\text{ pt}$.
