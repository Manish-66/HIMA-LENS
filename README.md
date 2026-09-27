# HIMA-LENS: Himachal Landslide Inventory & Spatial Intelligence System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask%203.0-000000.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Web-GIS](https://img.shields.io/badge/GIS-Leaflet%20%7C%20CesiumJS-10b981.svg?logo=leaflet&logoColor=white)](https://leafletjs.com/)
[![Database](https://img.shields.io/badge/Backend-Supabase%20PostgreSQL-3ecf8e.svg?logo=supabase&logoColor=white)](https://supabase.com/)
[![AI Vision](https://img.shields.io/badge/AI-Google%20Gemini%20Vision-4285F4.svg?logo=google&logoColor=white)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-Academic%20Research-darkgreen.svg)](LICENSE)

**HIMA-LENS** (*Himachal Landslide Exploration & Spatial Intelligence System*) is a full-stack Web-GIS platform and geotechnical decision-support engine developed at the **School of Civil & Environmental Engineering (SCENE), Indian Institute of Technology Mandi (IIT Mandi)**.

The system unifies a catalog of **14,190 verified slope failure occurrences**, **17,122 landslide polygons**, and **2,287 road alignments** across all 12 districts of Himachal Pradesh with interactive 2D/3D geospatial visualization, automated geotechnical multimodal AI assessment, citizen field reporting, and a live statewide landslide news wire.

---

## Key Features

### 1. Dual-Engine 2D/3D Web-GIS Observatory (`/explore`)
- **2D Cartographic Engine (Leaflet 1.9.4)**:
  - Multi-layer basemap support: OpenStreetMap, CartoDB Positron, Esri World Imagery (Satellite), Topographic, and OpenTopoMap.
  - High-performance spatial clustering and interactive filtering by district, trigger type, failure mechanism, and time period.
  - Dynamic radius buffer analysis, coordinate crosshair telemetry, and real-time bounding-box spatial queries.
- **3D Mountain Terrain Visualizer (Cesium Ion)**:
  - Photorealistic 3D digital elevation models (DEM) with 60 FPS tilt, pitch, and cinematic valley perspective views.
  - Seamless toggle between 2D standard planning view and 3D bathymetric/orographic terrain models.

### 2. Live Himachal Landslide & Hazard News Wire (`/feed?tab=news`, `/news`)
- **Automated RSS News Ingestion**: Continuously monitors reputable news and state emergency bulletins (*The Tribune, Hindustan Times, ETV Bharat, NDTV, All India Radio*).
- **Automated Thematic & Spatial Tagging**:
  - Automatically tags reports into **Highway & Transport** (NH-5, NH-21, NH-154 closures), **Flash Flood & Cloudburst**, **Weather & Hazard Alerts** (IMD bulletins), or **Slope Incidents**.
  - Geographically matches dispatches to all 12 districts (*Shimla, Mandi, Kullu, Kinnaur, Kangra, Solan, Chamba, Sirmaur, Bilaspur, Hamirpur, Una, Lahaul & Spiti*).
- **1-Click GIS Jump**: Interactive "Locate on Map" action dispatches coordinates to the Web-GIS for immediate spatial context.
- **Sub-Second Performance**: 15-minute in-memory caching with server-side payload hydration ensures instantaneous 0ms page loads.

### 3. Geotechnical AI Rapid Assessment Engine (`/report`, `ai_assessment.py`)
- **Multimodal Computer Vision**: Powered by Google Gemini 2.5 Flash with prompt engineering aligned with Indian geotechnical standards.
- **Validity & Verification Check**: Differentiates genuine landslide scars from benign hillside photos, road excavations, clear skies, or indoor images.
- **Failure Kinematics**: Identifies kinematic modes per **Varnes (2014)** classification (translational rock slides, rotational slumps, rockfall/toppling, mudflows/debris flows).
- **Dimensional & Debris Estimation**: Estimates failure scarp width ($m$), slope height ($m$), runout length ($m$), and displaced volume ($m^3$).
- **Civil Restoration Protocol**: Generates PWD-compliant emergency remedial actions and permanent structural countermeasures according to **IS:14458** (Plum concrete breast walls, gabion revetments, sub-surface horizontal weep drains, rock-bolting).

### 4. Crowd-Sourced Citizen & Field Reporting (`/report`, `supabase_db.py`)
- Direct integration with **Supabase PostgreSQL** and **Supabase Cloud Storage**.
- Automatic GPS geolocation detection, photograph uploads, and synchronized live map pin generation.
- Dual-tier approval workflow for municipal engineers, researchers, and citizen volunteers.

### 5. Historical Disaster Benchmark Chronology (`/feed`)
- In-depth spatial dossiers for landmark Himalayan disasters:
  - *August 2024 Samej Khad & Rampur Cloudburst Surge*
  - *Monsoon Deluge 2023 (Beas & Sutlej Basin Catastrophes)*
  - *August 2023 Shimla Summer Hill Railway Escarpment Collapse*
  - *July–August 2021 Kinnaur (Nigulsari & Batseri) Rock Avalanches*
  - *August 2017 Kotropi Catastrophic Highway Mudflow (Mandi)*
  - *Comprehensive Statewide Inventory (14,190 Geocoded Entries)*

---

## Spatial Datasets & Inventory Summary

| Dataset Layer | Coverage / Scope | Coordinate System | Features / Entities |
| :--- | :--- | :--- | :--- |
| **Mandi Field Survey** | Mandi District (10m field resolution) | EPSG:4326 (WGS 84) | 9,399 Geocoded Points |
| **GSI Statewide Inventory** | 11 Districts of Himachal Pradesh | EPSG:4326 (WGS 84) | 4,791 Geocoded Points |
| **Consolidated Point Master** | **All 12 Administrative Districts** | **EPSG:4326 (WGS 84)** | **14,190 Total Points** |
| **Landslide Hazard Polygons** | Mandi & High-Risk Corridors | EPSG:4326 (WGS 84) | 17,122 Spatial Polygons |
| **Mandi Road Network** | NH-21, SH & PWD Rural Corridors | EPSG:4326 (WGS 84) | 2,287 Road Segments |
| **District Boundaries** | Esri India 2024 Administrative Survey | EPSG:4326 (WGS 84) | 12 Boundary Polygons |

---

## Geotechnical Standards & Reference Frameworks

The analysis algorithms, scoring mechanisms, and mitigation plans in HIMA-LENS conform to the following national and international engineering standards:
- **IS 14458 (Parts 1–4)**: Guidelines for Retaining Walls for Hill Areas (Gravity, Plum Concrete, and Reinforced Walls).
- **IS 13365 (Parts 1–3)**: Quantitative Rock Mass Classification (RMR and Q-system parameters).
- **IRC:SP:48**: Indian Roads Congress Manual on Hill Road Engineering and Slope Stability Stabilization.
- **Varnes (2014)**: Updated Landslide Classification Scheme for Kinematic Landslide Types and Mechanics.

---

## System Architecture

```
                    ┌────────────────────────────────────────────────────────┐
                    │                      Client Browser                    │
                    │      (Desktop & Mobile Responsive - HTML5 / ES6)       │
                    └───────────┬────────────────────────────────┬───────────┘
                                │                                │
                       HTTP / JSON API                  Tile & Terrain Stream
                                │                                │
                    ┌───────────▼────────────────────────────────▼───────────┐
                    │                  Flask 3.0 Web Application             │
                    │               (Routing, API Endpoints, Cache)          │
                    └───────┬───────────────┬────────────────┬───────────────┘
                            │               │                │
            ┌───────────────▼──────┐ ┌──────▼────────┐ ┌─────▼───────────────┐
            │   Geospatial Data    │ │  Supabase DB  │ │ Google Gemini Vision│
            │  (GeoJSON & Bounds)  │ │  & S3 Storage │ │  (AI Geotech Engine)│
            │ • 14,190 Points      │ │ • Reports DB  │ │ • Varnes Mechanism  │
            │ • 17,122 Polygons    │ │ • Field Photos│ │ • Volume Estimator  │
            │ • 2,287 Road Aligns  │ │ • GPS Synced  │ │ • PWD IS:14458 Plan │
            └──────────────────────┘ └───────────────┘ └─────────────────────┘
                                            │
                                    ┌───────▼────────┐
                                    │ Live RSS News  │
                                    │ Google News HP │
                                    │ 15m Cache + UI │
                                    └────────────────┘
```

---

## Installation & Setup

### Prerequisites
- **Python 3.10+** (Python 3.11 or 3.12 recommended)
- **Git**
- Modern Web Browser (Chrome, Firefox, Edge, Safari)

### 1. Clone the Repository
```bash
git clone https://github.com/Manish-66/HIMA-LENS.git
cd HIMA-LENS
```

### 2. Create and Activate a Virtual Environment
**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` to configure your API keys (all keys are optional for local exploration, but recommended for full functionality):
```env
# Optional: Cesium Ion Token for 3D Terrain Elevation
CESIUM_ION_TOKEN=your_cesium_ion_token

# Optional: Google Gemini API Key for AI PWD Field Assessment
GEMINI_API_KEY=your_gemini_api_key

# Optional: Supabase Credentials for Community Field Reports
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_BUCKET=report-images
```

*(Note: If `CESIUM_ION_TOKEN` is omitted, the 3D globe falls back to the default WGS84 ellipsoid. If `GEMINI_API_KEY` is omitted, the report submission uses local heuristic estimation).*

---

## Running the Application

### Start the Flask Development Server
```bash
python app.py
```
By default, the server launches on **`http://127.0.0.1:5000/`**.

### Dataset Processing Scripts (Optional)
- **Convert & Validate Raw Excel Observations**:
  ```bash
  python convert_xlsx.py
  ```
  *(Processes `data.xlsx`, performs point-in-polygon verification against Esri district boundaries, and outputs `landslides_clean.geojson`).*
- **Verify Administrative Boundaries**:
  ```bash
  python districts.py
  ```

---

## REST API Reference

| Endpoint | Method | Description | Parameters |
| :--- | :--- | :--- | :--- |
| `/api/landslides` | `GET` | GeoJSON FeatureCollection of landslide points | `bounds`, `district`, `period`, `trigger` |
| `/api/summary` | `GET` | Aggregate statistical summary of inventory | None |
| `/api/districts` | `GET` | District-wise incident distribution breakdown | None |
| `/api/news` | `GET` | Real-time Himachal landslide news stream (JSON) | `refresh=1`, `district=`, `category=`, `q=` |
| `/api/reports` | `GET` | Verified community crowd-sourced reports | None |
| `/api/reports/submit` | `POST` | Submit a field report with photo & AI triage | Form-data (`photo`, `district`, `lat`, `lng`) |

---

## Project Structure

```
HIMA-LENS/
│
├── app.py                         # Main Flask application and REST API endpoints
├── config.py                      # Centralized filesystem and environment config
├── ai_assessment.py               # Google Gemini Vision geotechnical AI module
├── supabase_db.py                 # Supabase PostgreSQL and storage client
├── convert_xlsx.py                # Raw Excel-to-GeoJSON cleaning & validation
├── districts.py                   # District boundary verification routines
│
├── landslides_clean.geojson       # Master Point Inventory (14,190 features)
├── district_boundaries.geojson    # 12 Administrative District Outlines (Esri 2024)
├── data.xlsx                      # High-density Mandi field dataset
├── requirements.txt               # Python package dependencies
├── .env.example                   # Environment configuration template
│
├── static/
│   ├── css/
│   │   └── style.css              # Unified HIMA-LENS theme and responsive stylesheet
│   ├── js/
│   │   ├── explore.js             # Leaflet & Cesium 2D/3D map interactions
│   │   └── report.js              # Field reporting and AI analysis script
│   └── data/
│       ├── mandi_roads.geojson    # Road alignment polylines (2,287 features)
│       └── landslide_polygons_*.geojson # Hazard polygon layers (17,122 features)
│
└── templates/
    ├── base.html                  # Base layout with navigation and theme switcher
    ├── index.html                 # Homepage with spatial stats and project overview
    ├── explore.html               # 2D/3D interactive Web-GIS explorer
    ├── feed.html                  # Live News Stream & Historical Chronology Feed
    ├── report.html                # Field report submission & AI assessment tool
    └── about.html                 # Institutional background, team & methodology
```

---

## Research Team & Acknowledgments

- **Developed at**: School of Civil & Environmental Engineering (SCENE), Indian Institute of Technology Mandi (IIT Mandi).
- **Core Focus**: Mountain Hazard Mitigation, Rapid Geotechnical Assessment, Web-GIS Decision Support Systems.
- **Geospatial Data Sources**: Geological Survey of India (GSI), Esri India Administrative Boundaries, OpenStreetMap, and SCENE IIT Mandi Field Survey.

---

## License

This software and accompanying datasets are provided for academic, governmental, and scientific disaster management research. For inquiries or collaboration, please contact the SCENE department at IIT Mandi.
