"""Central, filesystem-safe configuration for HIMA-LENS."""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Ensure core engines and workspace root are in python path
CORE_DIR = BASE_DIR / "core"
if CORE_DIR.exists() and str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

def load_local_env(path: Path) -> None:
    """Minimal .env reader; process environment values remain authoritative."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key and key not in os.environ:
            os.environ[key] = value.strip().strip('"').strip("'")

# Load only the project-local .env file; environment variables still take precedence.
load_local_env(BASE_DIR / ".env")
DATASET_PATH = (
    BASE_DIR / "data" / "landslides_clean.geojson"
    if (BASE_DIR / "data" / "landslides_clean.geojson").exists()
    else BASE_DIR / "landslides_clean.geojson"
)
LEGACY_DATASET_PATH = (
    (BASE_DIR / "data" / "old_data.geojson")
    if (BASE_DIR / "data" / "old_data.geojson").exists()
    else (BASE_DIR / "old_data.geojson")
)
MANDI_WORKBOOK_PATH = (
    BASE_DIR / "data" / "data.xlsx"
    if (BASE_DIR / "data" / "data.xlsx").exists()
    else BASE_DIR / "data.xlsx"
)
DISTRICT_BOUNDARIES_PATH = (
    BASE_DIR / "data" / "district_boundaries.geojson"
    if (BASE_DIR / "data" / "district_boundaries.geojson").exists()
    else BASE_DIR / "district_boundaries.geojson"
)
MANDI_ROADS_PATH = BASE_DIR / "static" / "data" / "mandi_roads.geojson"
LANDSLIDE_POLYGONS_MANDI_PATH = BASE_DIR / "static" / "data" / "landslide_polygons_mandi.geojson"
LANDSLIDE_POLYGONS_HP_PATH = BASE_DIR / "static" / "data" / "landslide_polygons_hp.geojson"
ENVIRONMENTAL_OVERLAYS_META_PATH = BASE_DIR / "static" / "overlays" / "metadata.json"
COMMUNITY_REPORTS_PATH = BASE_DIR / "data" / "community_reports.json"
COMMUNITY_REPORTS_UPLOAD_DIR = BASE_DIR / "static" / "uploads" / "reports"
APP_NAME = "HIMA-LENS"
APP_DESCRIPTION = "Himachal Pradesh Landslide Inventory & Exploration System"

# Cesium Ion 3D Globe Token
DEFAULT_CESIUM_ION_TOKEN = ""
CESIUM_ION_TOKEN = os.environ.get("CESIUM_ION_TOKEN", "").strip() or DEFAULT_CESIUM_ION_TOKEN

# Supabase Database & Cloud Storage
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "").strip() or os.environ.get("SUPABASE_ANON_KEY", "").strip()
SUPABASE_BUCKET = os.environ.get("SUPABASE_BUCKET", "report-images").strip()

# Google Gemini Vision API for Geotechnical AI Assessment
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

# Roboflow Foundation Vision & SAM-3 Segmentation API
ROBOFLOW_API_KEY = os.environ.get("ROBOFLOW_API_KEY", "").strip()
ROBOFLOW_WORKSPACE = os.environ.get("ROBOFLOW_WORKSPACE", "").strip()
ROBOFLOW_INFER_URL = os.environ.get("ROBOFLOW_INFER_URL", "https://infer.roboflow.com").strip().rstrip("/")
ANNOTATED_PLATES_DIR = BASE_DIR / "static" / "uploads" / "annotated"


