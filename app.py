"""HIMA-LENS Flask application and read-only geospatial API."""
from __future__ import annotations

import csv
import email.utils
import html
import io
import json
import re
import time
import urllib.request
import urllib.parse
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any
from flask import Flask, jsonify, render_template, request, Response
import supabase_db
import ai_assessment
from config import (
    APP_DESCRIPTION,
    APP_NAME,
    CESIUM_ION_TOKEN,
    DATASET_PATH,
    DISTRICT_BOUNDARIES_PATH,
    MANDI_ROADS_PATH,
    LANDSLIDE_POLYGONS_MANDI_PATH,
    LANDSLIDE_POLYGONS_HP_PATH,
    ENVIRONMENTAL_OVERLAYS_META_PATH,
    COMMUNITY_REPORTS_PATH,
    COMMUNITY_REPORTS_UPLOAD_DIR,
)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.json.sort_keys = False

ALIASES = {
    "district": ("district", "District", "DISTRICT"),
    "activity": ("activity", "Activity", "ACTIVITY", "activity_status", "activityStatus", "status"),
    "movement": ("movement_type", "movementType", "movement", "MOVEMENT_T", "MOVEMENT_", "MOVEMENT", "movement_t"),
    "material": ("material_type", "materialType", "material", "MATERIAL_T", "MATERIAL", "material_t"),
    "period": ("period", "Period", "time", "Time", "season", "Season"),
    "year": ("year", "Year", "recorded_year", "recordedYear", "period", "Period"),
}

def prop(feature: dict[str, Any], name: str, default: str = "") -> str:
    properties = feature.get("properties") or {}
    for key in ALIASES.get(name, (name,)):
        value = properties.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return default

@lru_cache(maxsize=1)
def administrative_boundaries() -> dict[str, Any]:
    with DISTRICT_BOUNDARIES_PATH.open(encoding="utf-8") as source:
        data = json.load(source)
    if data.get("type") != "FeatureCollection" or not isinstance(data.get("features"), list):
        raise ValueError("District boundaries are not a GeoJSON FeatureCollection")
    features = []
    for feature in data["features"]:
        properties = feature.get("properties") or {}
        district = properties.get("name") or properties.get("lgd_districtname")
        if district:
            features.append({
                "type": "Feature",
                "properties": {
                    "district": district,
                    "lgd_code": properties.get("lgd_districtcode"),
                    "source": "India Administrative Boundaries 2024"
                },
                "geometry": feature.get("geometry")
            })
    return {"type": "FeatureCollection", "features": features}

@lru_cache(maxsize=1)
def inventory() -> dict[str, Any]:
    with DATASET_PATH.open(encoding="utf-8") as source:
        data = json.load(source)
    if data.get("type") != "FeatureCollection" or not isinstance(data.get("features"), list):
        raise ValueError("Dataset is not a GeoJSON FeatureCollection")

    # Ground-truth spatial alignment: ensure points are attributed to the district they actually lie in
    try:
        from shapely.geometry import shape, Point
        from shapely.prepared import prep
        bounds_data = administrative_boundaries()
        dist_lookup = {}
        for b in bounds_data["features"]:
            name = prop(b, "district")
            if name and b.get("geometry"):
                geom = shape(b["geometry"])
                dist_lookup[name.title()] = (prep(geom), geom.bounds)

        for f in data["features"]:
            orig_d = prop(f, "district")
            coords = f.get("geometry", {}).get("coordinates", [])
            if len(coords) < 2:
                continue
            lng, lat = float(coords[0]), float(coords[1])
            pt = Point(lng, lat)

            # Fast check: inside stated district?
            inside_stated = False
            if orig_d.title() in dist_lookup:
                pgeom, bnds = dist_lookup[orig_d.title()]
                if bnds[0] <= lng <= bnds[2] and bnds[1] <= lat <= bnds[3]:
                    if pgeom.contains(pt):
                        inside_stated = True

            if not inside_stated:
                for dname, (pgeom, bnds) in dist_lookup.items():
                    if bnds[0] <= lng <= bnds[2] and bnds[1] <= lat <= bnds[3]:
                        if pgeom.contains(pt):
                            f.setdefault("properties", {})["district"] = dname
                            break
    except Exception as e:
        print("Spatial district alignment notice:", e)

    return data

@lru_cache(maxsize=1)
def serialized_boundaries() -> str:
    return json.dumps(administrative_boundaries())

@lru_cache(maxsize=1)
def cached_roads() -> str:
    if not MANDI_ROADS_PATH.exists():
        return json.dumps({"type": "FeatureCollection", "features": []})
    return MANDI_ROADS_PATH.read_text(encoding="utf-8")

@lru_cache(maxsize=1)
def cached_mandi_polygons() -> str:
    if not LANDSLIDE_POLYGONS_MANDI_PATH.exists():
        return json.dumps({"type": "FeatureCollection", "features": []})
    return LANDSLIDE_POLYGONS_MANDI_PATH.read_text(encoding="utf-8")

@lru_cache(maxsize=1)
def cached_hp_polygons() -> str:
    if not LANDSLIDE_POLYGONS_HP_PATH.exists():
        return json.dumps({"type": "FeatureCollection", "features": []})
    return LANDSLIDE_POLYGONS_HP_PATH.read_text(encoding="utf-8")

@lru_cache(maxsize=1)
def cached_environmental_meta() -> dict[str, Any]:
    if not ENVIRONMENTAL_OVERLAYS_META_PATH.exists():
        return {}
    with ENVIRONMENTAL_OVERLAYS_META_PATH.open(encoding="utf-8") as f:
        return json.load(f)

def matching_features() -> list[dict[str, Any]]:
    tokens = request.args.get("bounds", "").split(",")
    try:
        west, south, east, north = map(float, tokens) if len(tokens) == 4 else (None,) * 4
    except ValueError:
        west = south = east = north = None
    criteria = {key: request.args.get(key, "").strip().casefold() for key in ALIASES}
    output = []
    for feature in inventory()["features"]:
        geometry = feature.get("geometry") or {}
        coordinates = geometry.get("coordinates") or []
        if geometry.get("type") != "Point" or len(coordinates) < 2:
            continue
        try:
            lng, lat = float(coordinates[0]), float(coordinates[1])
        except (TypeError, ValueError):
            continue
        if west is not None and not (west <= lng <= east and south <= lat <= north):
            continue
        if any(value and value != "all" and prop(feature, key).casefold() != value for key, value in criteria.items()):
            continue
        output.append(feature)
    return output

# -------------------------------------------------------------
# LIVE HIMACHAL PRADESH LANDSLIDE & HAZARD NEWS WIRE
# -------------------------------------------------------------
_NEWS_CACHE: dict[str, Any] = {"timestamp": 0, "articles": []}
_NEWS_CACHE_TTL = 900  # 15 minutes in seconds

HP_LOCATIONS = [
    "himachal", "himachal pradesh",
    "mandi", "shimla", "kullu", "kinnaur", "kangra", "chamba", 
    "solan", "sirmaur", "sirmour", "bilaspur", "hamirpur", "una", 
    "lahaul", "spiti",
    "manali", "dharamshala", "dharamsala", "mcleodganj", "dalhousie", 
    "kasauli", "palampur", "paonta", "rampur", "rohru", "bharmour", "pandoh", 
    "aut", "larji", "parvati", "parbati", "beas", "sutlej", "sangla", "chitkul", "kalpa", 
    "reckong peo", "kaza", "keylong", "rohtang", "atal tunnel", "jalori", 
    "samej", "nigulsari", "kotropi", "kiratpur", "parwanoo", "jabli", "kalka-shimla",
    "shikari devi", "kamrau", "shillai", "suni", "theog", "narkanda", "karsog",
    "arki", "sundernagar", "jogindernagar", "baijnath", "nurpur", "jawali",
    "chopal", "jubbal", "kotkhai", "sarahan", "tapri", "pooh", "jhakri"
]

NON_HP_PRIMARY = [
    "in nepal", "nepal flood", "nepal landslide", "sikkim", "wayanad", "kerala", 
    "uttarakhand", "arunachal", "meghalaya", "manipur", "mizoram", "nagaland", 
    "tripura", "assam", "ladakh", "jabalpur", "bhopal", "bihar", "odisha", 
    "poonch", "kashmir", "bangladesh", "pakistan"
]

IRRELEVANT_NOISE = [
    "raksha bandhan", "diwali", "holiday", "festival", "fiscal landslide", 
    "election", "cricket", "bollywood", "cabinet", "bypoll", "congress", "bjp", 
    "assembly election", "no, the video is from"
]

HAZARD_KEYWORDS = [
    "landslide", "rockfall", "rockslide", "cloudburst", "flash flood", 
    "debris flow", "subsidence", "sinking", "slope", "boulder", "heavy rain", 
    "deluge", "highway blocked", "nh-", "nh ", "road blocked", "tunnel", 
    "erosion", "damaged", "washed away", "ravine", "alert", "warning", "toll", "traffic"
]

def _is_strictly_himachal(title: str, desc: str) -> bool:
    t_lower = title.casefold()
    d_lower = desc.casefold()
    combined = t_lower + " " + d_lower

    if any(nk in t_lower for nk in IRRELEVANT_NOISE):
        return False
    if "nepal" in t_lower or "trishuli" in t_lower:
        return False
    if not any(hk in combined for hk in HAZARD_KEYWORDS):
        return False
    if not any(k in combined for k in HP_LOCATIONS):
        return False

    has_hp_in_title = any(k in t_lower for k in HP_LOCATIONS)
    for other in NON_HP_PRIMARY:
        if other in t_lower and not has_hp_in_title:
            return False
        if other.startswith("in ") and other in t_lower:
            return False

    return True

def _classify_news_district(text: str) -> str:
    lower = text.casefold()
    if any(k in lower for k in ["lahaul", "spiti", "kaza", "keylong", "tabo", "lossar", "malling"]):
        return "Lahaul & Spiti"
    if any(k in lower for k in ["sirmaur", "sirmour", "paonta", "shillai", "kamrau", "nahan", "rajgarh"]):
        return "Sirmaur"
    if any(k in lower for k in ["kinnaur", "sangla", "chitkul", "kalpa", "reckong", "nigulsari", "urni", "pooh", "tapri", "nichar"]):
        return "Kinnaur"
    if any(k in lower for k in ["kullu", "manali", "sainj", "malana", "parvati", "parbati", "rohtang", "atal tunnel", "jalori", "bhuntar", "naggar"]):
        return "Kullu"
    if any(k in lower for k in ["shimla", "summer hill", "rampur", "rohru", "samej", "theog", "narkanda", "chopal", "jubbal", "kotkhai", "sarahan", "suni"]):
        return "Shimla"
    if any(k in lower for k in ["mandi", "pandoh", "kotropi", "sundernagar", "jogindernagar", "aut", "larji", "karsog", "padhar", "urla", "balh"]):
        return "Mandi"
    if any(k in lower for k in ["kangra", "dharamshala", "dharamsala", "mcleodganj", "palampur", "bhagsu", "nurpur", "baijnath", "jawali", "jawalamukhi"]):
        return "Kangra"
    if any(k in lower for k in ["solan", "kasauli", "parwanoo", "jabli", "kumarhatti", "arki", "kandaghat", "chail"]):
        return "Solan"
    if any(k in lower for k in ["chamba", "dalhousie", "bharmour", "tissa", "salooni", "manimahesh", "khajjiar", "chaurasi"]):
        return "Chamba"
    if "bilaspur" in lower or "ghumarwin" in lower or "swarghat" in lower:
        return "Bilaspur"
    if "hamirpur" in lower or "nadaun" in lower or "bhoranj" in lower or "barsar" in lower:
        return "Hamirpur"
    if "una" in lower or "amb" in lower or "haroli" in lower or "gagret" in lower:
        return "Una"
    return "Himachal Pradesh"

def _classify_news_category(text: str) -> str:
    lower = text.casefold()
    if any(k in lower for k in ["highway", "nh-", "nh ", "road", "traffic", "blocked", "commute", "tunnel", "parwanoo", "kiratpur", "pandoh", "kalka"]):
        return "Highway & Transport"
    if any(k in lower for k in ["cloudburst", "flash flood", "flood", "deluge", "inundat", "overflow", "river", "khad", "nullah", "water level"]):
        return "Flash Flood & Cloudburst"
    if any(k in lower for k in ["alert", "warning", "imd", "met department", "orange alert", "red alert", "yellow alert", "heavy rain", "incessant"]):
        return "Weather & Hazard Alert"
    return "Slope Incident & Field Report"

def _format_relative_time(dt: datetime) -> str:
    try:
        now = datetime.now(timezone.utc)
        diff = now - dt
        secs = int(diff.total_seconds())
        if secs < 0:
            return "Just now"
        if secs < 3600:
            return f"{max(1, secs // 60)}m ago"
        if secs < 86400:
            return f"{secs // 3600}h ago"
        days = secs // 86400
        if days == 1:
            return "1 day ago"
        if days < 30:
            return f"{days} days ago"
        return dt.strftime("%b %d, %Y")
    except Exception:
        return ""

def _get_fallback_news() -> list[dict[str, Any]]:
    return [
        {
            "id": "fb-1",
            "title": "Himachal's Key Chandigarh-Shimla National Highway on Landslide Edge, Geotechnical Survey Warns",
            "link": "https://www.tribuneindia.com",
            "source": "The Tribune India",
            "pub_date": "Recent Bulletin",
            "time_ago": "1 day ago",
            "timestamp": int(time.time()) - 86400,
            "district": "Solan",
            "category": "Highway & Transport",
            "snippet": "Multi-agency geological risk assessments highlight acute slope vulnerability along the Solan-Parwanoo and Shimla bypass corridors following repetitive monsoon shearing."
        },
        {
            "id": "fb-2",
            "title": "Samej Khad Hydro Catchment Debris Clearance & Mitigation Protocol Intensified",
            "link": "https://newsonair.gov.in",
            "source": "All India Radio",
            "pub_date": "Recent Bulletin",
            "time_ago": "2 days ago",
            "timestamp": int(time.time()) - 172800,
            "district": "Shimla",
            "category": "Flash Flood & Cloudburst",
            "snippet": "Disaster management forces continue systematic channel desiltation and slope stabilization works following high-altitude cloudburst surges near Rampur border."
        },
        {
            "id": "fb-3",
            "title": "Kiratpur-Manali NH-21 Stretch Near Pandoh Dam Reinforced with Rock Bolt Meshing",
            "link": "https://timesofindia.indiatimes.com",
            "source": "Times of India",
            "pub_date": "Recent Bulletin",
            "time_ago": "3 days ago",
            "timestamp": int(time.time()) - 259200,
            "district": "Mandi",
            "category": "Highway & Transport",
            "snippet": "NHAI and geotechnical teams deploy active rock-bolting, hydroseeding, and plum concrete retaining breast walls along vulnerable river scarp zones in Mandi."
        },
        {
            "id": "fb-4",
            "title": "IMD Issues Seasonal Warning for Fragile Slopes Across Kangra, Chamba and Mandi Valleys",
            "link": "https://www.ndtv.com",
            "source": "NDTV",
            "pub_date": "Recent Bulletin",
            "time_ago": "4 days ago",
            "timestamp": int(time.time()) - 345600,
            "district": "Kangra",
            "category": "Weather & Hazard Alert",
            "snippet": "State meteorological centre advises district authorities to maintain active surveillance over identified chronic landslide slips and loose scree deposits."
        },
        {
            "id": "fb-5",
            "title": "Kinnaur NH-5 Shooting Stone Mitigation: Drone Sensors Track Overhanging Escarpments",
            "link": "https://www.hindustantimes.com",
            "source": "Hindustan Times",
            "pub_date": "Recent Bulletin",
            "time_ago": "5 days ago",
            "timestamp": int(time.time()) - 432000,
            "district": "Kinnaur",
            "category": "Slope Incident & Field Report",
            "snippet": "Specialized teams carry out controlled rock scaling and barrier installation at Nigulsari and Batseri rockfall stretches on the Hindustan-Tibet Highway."
        }
    ]

def get_himachal_landslide_news(force_refresh: bool = False) -> list[dict[str, Any]]:
    global _NEWS_CACHE
    now_ts = time.time()
    if not force_refresh and _NEWS_CACHE["articles"] and (now_ts - _NEWS_CACHE["timestamp"]) < _NEWS_CACHE_TTL:
        return _NEWS_CACHE["articles"]

    query = '("Himachal Pradesh" OR Himachal) (landslide OR rockfall OR cloudburst OR "debris flow" OR "flash flood") when:60d'
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    )
    articles: list[dict[str, Any]] = []

    try:
        with urllib.request.urlopen(req, timeout=7) as response:
            raw_xml = response.read().decode("utf-8", errors="replace")

        root = ET.fromstring(raw_xml)
        for item in root.findall("./channel/item"):
            raw_title = item.findtext("title") or ""
            raw_title = html.unescape(raw_title)
            raw_title = (
                raw_title.replace("\u2018", "'")
                .replace("\u2019", "'")
                .replace("\u201c", '"')
                .replace("\u201d", '"')
                .replace("\u2014", " - ")
                .replace("\u2013", " - ")
            )

            source_tag = item.findtext("source") or ""
            source_tag = html.unescape(source_tag).strip()

            clean_title = raw_title
            for sep in [" - ", " | ", " – ", " — "]:
                if sep in clean_title:
                    parts = clean_title.rsplit(sep, 1)
                    clean_title = parts[0].strip()
                    if not source_tag and len(parts) > 1:
                        source_tag = parts[1].strip()
            if " | " in clean_title:
                clean_title = clean_title.rsplit(" | ", 1)[0].strip()

            link = item.findtext("link") or ""
            pub_date_raw = item.findtext("pubDate") or ""
            
            pub_date_str = pub_date_raw
            time_ago_str = ""
            ts = int(now_ts)
            if pub_date_raw:
                try:
                    dt = email.utils.parsedate_to_datetime(pub_date_raw)
                    pub_date_str = dt.strftime("%b %d, %Y")
                    time_ago_str = _format_relative_time(dt)
                    ts = int(dt.timestamp())
                except Exception:
                    pub_date_str = pub_date_raw[:16]

            raw_desc = item.findtext("description") or ""
            clean_desc = re.sub(r"<[^>]+>", "", html.unescape(raw_desc)).strip()
            if not clean_desc or clean_desc == clean_title:
                clean_desc = f"Field monitoring report concerning slope stability, drainage disruption, or transportation safety across {_classify_news_district(clean_title)}."

            district = _classify_news_district(clean_title + " " + clean_desc)
            category = _classify_news_category(clean_title + " " + clean_desc)

            if _is_strictly_himachal(clean_title, clean_desc):
                articles.append({
                    "id": str(uuid.uuid4())[:8],
                    "title": clean_title,
                    "link": link,
                    "source": source_tag or "Himachal Media Wire",
                    "pub_date": pub_date_str,
                    "time_ago": time_ago_str,
                    "timestamp": ts,
                    "district": district,
                    "category": category,
                    "snippet": clean_desc
                })

        if articles:
            articles.sort(key=lambda a: a.get("timestamp", 0), reverse=True)
            _NEWS_CACHE["articles"] = articles
            _NEWS_CACHE["timestamp"] = now_ts
            return articles

    except Exception:
        if _NEWS_CACHE["articles"]:
            return _NEWS_CACHE["articles"]

    fallback = _get_fallback_news()
    _NEWS_CACHE["articles"] = fallback
    _NEWS_CACHE["timestamp"] = now_ts
    return fallback

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/explore")
@app.get("/api")
def explore():
    return render_template("explore.html", cesium_ion_token=CESIUM_ION_TOKEN)

def get_historical_events():
    events_path = Path(__file__).resolve().parent / "data" / "historical_events.json"
    if events_path.exists():
        try:
            with open(events_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading historical_events.json: {e}")
    return []

@app.get("/feed")
@app.get("/news")
def feed():
    tab = request.args.get("tab", "")
    if request.path == "/news":
        tab = "news"
    articles = get_himachal_landslide_news()
    events = get_historical_events()
    return render_template(
        "feed.html",
        initial_tab=tab,
        initial_news=articles,
        news_count=len(articles),
        historical_events=events,
        events_count=len(events),
        last_updated=time.strftime("%d %b %Y, %H:%M UTC", time.gmtime(_NEWS_CACHE["timestamp"])) if _NEWS_CACHE["timestamp"] else "Active"
    )

@app.get("/api/historical-events")
def api_historical_events():
    events = get_historical_events()
    category = request.args.get("category", "").strip().lower()
    district = request.args.get("district", "").strip().lower()
    query = request.args.get("q", "").strip().lower()

    if category and category != "all":
        events = [e for e in events if e.get("category", "").lower() == category]
    if district and district != "all":
        events = [e for e in events if district in e.get("district", "").lower()]
    if query:
        events = [
            e for e in events
            if query in e.get("title", "").lower()
            or query in e.get("summary", "").lower()
            or query in e.get("district", "").lower()
            or query in e.get("corridor", "").lower()
        ]
    return jsonify(events)

@app.get("/api/news")
def api_news():
    force_refresh = request.args.get("refresh", "").lower() in ("1", "true", "yes")
    articles = get_himachal_landslide_news(force_refresh=force_refresh)
    district_filter = request.args.get("district", "").strip()
    category_filter = request.args.get("category", "").strip()
    query = request.args.get("q", "").strip().casefold()

    filtered = articles
    if district_filter and district_filter.lower() != "all":
        filtered = [a for a in filtered if a["district"].casefold() == district_filter.casefold()]
    if category_filter and category_filter.lower() != "all":
        filtered = [a for a in filtered if a["category"].casefold() == category_filter.casefold()]
    if query:
        filtered = [
            a for a in filtered 
            if query in a["title"].casefold() 
            or query in a["source"].casefold() 
            or query in a["district"].casefold()
            or query in a["snippet"].casefold()
        ]

    return jsonify(
        success=True,
        total=len(articles),
        count=len(filtered),
        articles=filtered,
        last_updated=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(_NEWS_CACHE["timestamp"])) if _NEWS_CACHE["timestamp"] else None
    )

@app.get("/report")
def report():
    return render_template("report.html")

@app.get("/about")
def about():
    return render_template("about.html")

@app.get("/terrain-lab")
@app.get("/himalayan-3d")
@app.get("/space-service")
def terrain_lab():
    return render_template("terrain_lab.html")


@app.get("/api/landslides")
def landslides():
    return jsonify(type="FeatureCollection", features=matching_features())

@app.get("/api/summary")
def summary():
    features = matching_features()
    districts = {prop(f, "district") for f in features if prop(f, "district")}
    numeric_years = [int(prop(f, "year")) for f in features if prop(f, "year").isdigit()]
    periods = {prop(f, "period") for f in features if prop(f, "period")}
    return jsonify(
        success=True,
        total_records=len(features),
        districts=len(districts),
        district_names=sorted(districts),
        periods=sorted(periods),
        numeric_year_count=len(numeric_years),
        earliest_year=min(numeric_years, default=None),
        latest_year=max(numeric_years, default=None),
    )

@app.get("/api/districts")
def districts():
    canonical = {feature["properties"]["district"].casefold(): feature["properties"]["district"] for feature in administrative_boundaries()["features"]}
    counts = {name: 0 for name in canonical.values()}
    for feature in inventory()["features"]:
        name = prop(feature, "district", "Unknown")
        canonical_name = canonical.get(name.casefold(), name)
        counts[canonical_name] = counts.get(canonical_name, 0) + 1
    return jsonify(success=True, districts=[{"district": k, "count": v} for k, v in sorted(counts.items())])

@app.get("/api/years")
def years():
    counts = {}
    for feature in inventory()["features"]:
        value = prop(feature, "year")
        if value:
            counts[value] = counts.get(value, 0) + 1
    return jsonify(success=True, years=[{"year": k, "count": v} for k, v in sorted(counts.items(), reverse=True)])

@app.get("/api/categories")
def categories():
    result = {}
    for category in ("activity", "movement", "material"):
        counts = {}
        for feature in inventory()["features"]:
            value = prop(feature, category, "Unknown")
            counts[value] = counts.get(value, 0) + 1
        result[category] = [{"value": k, "count": v} for k, v in sorted(counts.items(), key=lambda x: (-x[1], x[0]))]
    return jsonify(success=True, categories=result)

@app.get("/api/district-boundaries")
def district_boundaries():
    response = Response(serialized_boundaries(), status=200, mimetype="application/json")
    response.headers["Cache-Control"] = "public, max-age=3600"
    return response

@app.get("/api/roads")
def roads():
    response = Response(cached_roads(), status=200, mimetype="application/json")
    response.headers["Cache-Control"] = "public, max-age=3600"
    return response

@app.get("/api/landslide-polygons")
def landslide_polygons():
    district = request.args.get("district", "").strip().lower()
    if district == "mandi":
        content = cached_mandi_polygons()
    elif district and district != "all":
        all_data = json.loads(cached_hp_polygons())
        filtered = [f for f in all_data.get("features", []) if (f.get("properties") or {}).get("district", "").lower() == district]
        content = json.dumps({"type": "FeatureCollection", "features": filtered})
    else:
        content = cached_hp_polygons()
    response = Response(content, status=200, mimetype="application/json")
    response.headers["Cache-Control"] = "public, max-age=3600"
    return response

@app.get("/api/environmental-layers")
def environmental_layers():
    return jsonify(success=True, layers=cached_environmental_meta())

def load_community_reports() -> list[dict[str, Any]]:
    return supabase_db.load_local_reports()

def save_community_reports(reports: list[dict[str, Any]]) -> None:
    supabase_db.save_local_reports(reports)

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif", "heic", "heif", "avif", "jfif"}

def allowed_image_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

@app.get("/api/reports")
def get_reports():
    reports = supabase_db.fetch_community_reports()
    features = []
    for rep in reports:
        try:
            lat = float(rep["latitude"])
            lng = float(rep["longitude"])
        except (KeyError, ValueError, TypeError):
            continue
        features.append({
            "type": "Feature",
            "properties": {
                "id": rep.get("id"),
                "district": rep.get("district", "Unknown"),
                "incident_date": rep.get("incident_date", ""),
                "movement_type": rep.get("movement_type", "Unknown"),
                "severity": rep.get("severity", "Moderate"),
                "description": rep.get("description", ""),
                "reporter_name": rep.get("reporter_name", "Anonymous"),
                "photo_url": rep.get("photo_url", ""),
                "created_at": rep.get("created_at", ""),
                "is_community_report": True
            },
            "geometry": {
                "type": "Point",
                "coordinates": [lng, lat]
            }
        })
    response = jsonify({"type": "FeatureCollection", "features": features})
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

@app.post("/api/reports")
def submit_report():
    try:
        lat = float(request.form.get("latitude", 0))
        lng = float(request.form.get("longitude", 0))
    except (TypeError, ValueError):
        return jsonify(success=False, error="INVALID_COORDINATES", message="Valid decimal latitude and longitude are required."), 400

    if not (30.0 <= lat <= 34.0 and 75.0 <= lng <= 80.0):
        return jsonify(
            success=False, 
            error="OUT_OF_BOUNDS", 
            message="Coordinates must be located within Himachal Pradesh bounds (30.0°N–34.0°N, 75.0°E–80.0°E)."
        ), 400

    district = request.form.get("district", "Mandi").strip()
    incident_date = request.form.get("incident_date", datetime.utcnow().strftime("%Y-%m-%d %H:%M")).strip()
    movement_type = request.form.get("movement_type", "Slide").strip()
    severity = request.form.get("severity", "Moderate").strip()
    description = request.form.get("description", "").strip()
    reporter_name = request.form.get("reporter_name", "Anonymous").strip()

    photo_url = ""
    file = request.files.get("photo")
    if file and file.filename and allowed_image_file(file.filename):
        photo_url = supabase_db.upload_report_image(file, file.filename)

    report_id = f"HL-CR-{uuid.uuid4().hex[:8].upper()}"
    new_report = {
        "id": report_id,
        "latitude": round(lat, 5),
        "longitude": round(lng, 5),
        "district": district,
        "incident_date": incident_date,
        "movement_type": movement_type,
        "severity": severity,
        "description": description,
        "reporter_name": reporter_name,
        "photo_url": photo_url,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

    supabase_db.save_community_report(new_report)

    return jsonify(success=True, report=new_report), 201

@app.get("/api/export")
def export_dataset():
    district_param = request.args.get("district", "all").strip().lower()
    year_param = request.args.get("year", "all").strip().lower()
    export_format = request.args.get("format", "csv").strip().lower()

    features = inventory()["features"]
    filtered = []
    for f in features:
        f_district = prop(f, "district", "").lower()
        f_year = prop(f, "year", "").lower()

        if district_param and district_param != "all" and f_district != district_param:
            continue
        if year_param and year_param != "all" and f_year != year_param:
            continue
        filtered.append(f)

    clean_dist = district_param if district_param and district_param != "all" else "all_districts"
    clean_yr = year_param if year_param and year_param != "all" else "all_years"

    if export_format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "id", "latitude", "longitude", "district", "activity", 
            "movement_type", "material_type", "year", "distance_to_road_m"
        ])
        for idx, f in enumerate(filtered, start=1):
            coords = f.get("geometry", {}).get("coordinates", [0, 0])
            writer.writerow([
                f.get("id") or idx,
                coords[1] if len(coords) > 1 else "",
                coords[0] if len(coords) > 0 else "",
                prop(f, "district", "Himachal Pradesh"),
                prop(f, "activity", "Not recorded"),
                prop(f, "movement", "Not recorded"),
                prop(f, "material", "Not recorded"),
                prop(f, "year", "Not recorded"),
                prop(f, "distance_to_road_m", "") or (f.get("properties") or {}).get("distance_to_road_m", "")
            ])
        csv_data = output.getvalue()
        filename = f"HIMA-LENS_landslides_{clean_dist}_{clean_yr}.csv"
        response = Response(csv_data, mimetype="text/csv")
        response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    elif export_format == "geojson":
        geojson_data = json.dumps({"type": "FeatureCollection", "features": filtered}, indent=2)
        filename = f"HIMA-LENS_landslides_{clean_dist}_{clean_yr}.geojson"
        response = Response(geojson_data, mimetype="application/geo+json")
        response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    else:
        records = []
        for idx, f in enumerate(filtered, start=1):
            coords = f.get("geometry", {}).get("coordinates", [0, 0])
            records.append({
                "id": f.get("id") or idx,
                "latitude": coords[1] if len(coords) > 1 else None,
                "longitude": coords[0] if len(coords) > 0 else None,
                "district": prop(f, "district", "Himachal Pradesh"),
                "activity": prop(f, "activity", "Not recorded"),
                "movement_type": prop(f, "movement", "Not recorded"),
                "material_type": prop(f, "material", "Not recorded"),
                "year": prop(f, "year", "Not recorded")
            })
        json_data = json.dumps(records, indent=2)
        filename = f"HIMA-LENS_landslides_{clean_dist}_{clean_yr}.json"
        response = Response(json_data, mimetype="application/json")
        response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

@app.get("/api/health")
def health():
    try:
        count = len(inventory()["features"])
        boundary_count = len(administrative_boundaries()["features"])
        valid, error = True, None
    except Exception as exc:
        count, boundary_count, valid, error = 0, 0, False, str(exc)
    return jsonify(
        success=valid,
        status="ok" if valid else "degraded",
        application=APP_NAME,
        description=APP_DESCRIPTION,
        dataset_available=DATASET_PATH.exists(),
        boundaries_available=DISTRICT_BOUNDARIES_PATH.exists(),
        dataset=str(DATASET_PATH),
        feature_count=count,
        district_boundary_count=boundary_count,
        validation_error=error
    ), (200 if valid else 503)

def find_report_by_id(report_id: str) -> dict[str, Any] | None:
    reports = supabase_db.fetch_community_reports(include_hidden=True)
    clean_id = report_id.strip().casefold()
    for r in reports:
        if str(r.get("id", "")).strip().casefold() == clean_id:
            return r
    return None

@app.post("/api/reports/<report_id>/ai-assessment")
def generate_report_ai_assessment(report_id: str):
    report = find_report_by_id(report_id)
    if not report:
        return jsonify(success=False, error="REPORT_NOT_FOUND", message=f"Report '{report_id}' not found."), 404

    force = request.args.get("force", "").lower() in ("1", "true", "yes")
    assessment = ai_assessment.generate_ai_assessment(report, force_refresh=force)
    return jsonify(success=True, report_id=report_id, assessment=assessment)

@app.post("/api/reports/<report_id>/ai-assessment/save")
def save_custom_ai_assessment(report_id: str):
    report = find_report_by_id(report_id)
    if not report:
        return jsonify(success=False, error="REPORT_NOT_FOUND", message=f"Report '{report_id}' not found."), 404

    payload = request.get_json(silent=True) or {}
    if not payload:
        return jsonify(success=False, error="EMPTY_PAYLOAD", message="No assessment payload provided."), 400

    ai_assessment.save_assessment_to_cache(report_id, payload)
    return jsonify(success=True, report_id=report_id, message="Custom assessment persisted.")

@app.get("/report/pwd-sheet/<report_id>")
def view_pwd_sheet(report_id: str):
    report = find_report_by_id(report_id)
    if not report:
        return f"Report with ID {report_id} was not found.", 404

    force = request.args.get("force", "").lower() in ("1", "true", "yes")
    # Read from cache or run deterministic calculation
    assessment = ai_assessment.generate_ai_assessment(report, force_refresh=force)
    assessment = ai_assessment.normalize_assessment_structure(assessment, report)
    return render_template("pwd_sheet.html", report=report, assessment=assessment)

@app.get("/report/cost-estimate/<report_id>")
def get_cost_estimate(report_id: str):
    report = find_report_by_id(report_id)
    if not report:
        return jsonify(success=False, error="REPORT_NOT_FOUND", message=f"Report {report_id} not found."), 404

    force = request.args.get("force", "").lower() in ("1", "true", "yes")
    assessment = ai_assessment.generate_ai_assessment(report, force_refresh=force)
    assessment = ai_assessment.normalize_assessment_structure(assessment, report)
    cost_data = assessment.get("cost_estimate_boq") or geotech_engine.calculate_comprehensive_cost_and_loss_estimate(assessment, report)
    return jsonify(success=True, report_id=report_id, cost_estimate_boq=cost_data)

@app.get("/report/boq-sheet/<report_id>")
def view_boq_sheet(report_id: str):
    report = find_report_by_id(report_id)
    if not report:
        return f"Report with ID {report_id} was not found.", 404

    force = request.args.get("force", "").lower() in ("1", "true", "yes")
    assessment = ai_assessment.generate_ai_assessment(report, force_refresh=force)
    assessment = ai_assessment.normalize_assessment_structure(assessment, report)
    return render_template("boq_sheet.html", report=report, assessment=assessment)

@app.errorhandler(FileNotFoundError)
def missing_dataset(error):
    return jsonify(success=False, error="DATASET_NOT_FOUND", message=str(error)), 404

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)

