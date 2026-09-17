"""Central, filesystem-safe configuration for HIMA-LENS."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

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
DATASET_PATH = BASE_DIR / "landslides_clean.geojson"
LEGACY_DATASET_PATH = (
    (BASE_DIR / "old_data.geojson")
    if (BASE_DIR / "old_data.geojson").exists()
    else (BASE_DIR / "landslides_legacy.geojson")
)
MANDI_WORKBOOK_PATH = BASE_DIR / "data.xlsx"
DISTRICT_BOUNDARIES_PATH = BASE_DIR / "district_boundaries.geojson"
MANDI_ROADS_PATH = BASE_DIR / "static" / "data" / "mandi_roads.geojson"
LANDSLIDE_POLYGONS_MANDI_PATH = BASE_DIR / "static" / "data" / "landslide_polygons_mandi.geojson"
LANDSLIDE_POLYGONS_HP_PATH = BASE_DIR / "static" / "data" / "landslide_polygons_hp.geojson"
ENVIRONMENTAL_OVERLAYS_META_PATH = BASE_DIR / "static" / "overlays" / "metadata.json"
COMMUNITY_REPORTS_PATH = BASE_DIR / "data" / "community_reports.json"
COMMUNITY_REPORTS_UPLOAD_DIR = BASE_DIR / "static" / "uploads" / "reports"
APP_NAME = "HIMA-LENS"
APP_DESCRIPTION = "Himachal Pradesh Landslide Inventory & Exploration System"
# Optional: set CESIUM_ION_TOKEN in the environment for photoreal terrain.
# Do not commit a real token into this repository.
CESIUM_ION_TOKEN = os.environ.get("CESIUM_ION_TOKEN", "").strip()
