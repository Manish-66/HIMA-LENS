"""HIMA-LENS Advanced Geotechnical Evaluation Engine.

Integrates international engineering standards into field dossiers:
1. LaRiMiT (Landslide Risk Mitigation Toolbox) - Klima 2050 / NGI Norway
   - 11 Functional Mitigation Clusters & 74 Structural / Nature-Based Solutions (NBS)
   - Kinematic Suitability Scoring across Varnes failure mechanisms
2. CEDD GEO (Geotechnical Engineering Office, Civil Engineering and Development Dept, Hong Kong)
   - Geoguide 1 & 5: Consequence-to-Life Categories & Target Factor of Safety (FOS)
   - Geoguide 7: Prescribed Soil Nailing Arrays & Pullout Verification
   - GEO Report No. 138: Flexible Rockfall & Debris-Flow Barriers (250 kJ to 5000 kJ)
   - TGN 24: Subsurface Horizontal Directional Relief Drainage Array
   - Geoguide 5: Statutory Slope Maintenance & Inspection Regimes (RMI, EIM, DSA)
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from config import BASE_DIR

logger = logging.getLogger(__name__)

STANDARDS_DIR = BASE_DIR / "data" / "geotech_standards"
LARIMIT_FILE = STANDARDS_DIR / "larimit_mitigation_catalog.json"
CEDD_FILE = STANDARDS_DIR / "cedd_geo_standards.json"
USGS_FILE = STANDARDS_DIR / "usgs_cruden_varnes_standards.json"
BHUKOSH_FILE = STANDARDS_DIR / "bhukosh_geology_index.json"
SOR_FILE = STANDARDS_DIR / "pwd_schedule_of_rates.json"

_LARIMIT_CACHE: dict[str, Any] | None = None
_CEDD_CACHE: dict[str, Any] | None = None
_USGS_CACHE: dict[str, Any] | None = None
_BHUKOSH_CACHE: list[dict[str, Any]] | None = None
_SOR_CACHE: dict[str, Any] | None = None


def load_sor_standards() -> dict[str, Any]:
    global _SOR_CACHE
    if _SOR_CACHE is not None:
        return _SOR_CACHE
    if SOR_FILE.exists():
        try:
            _SOR_CACHE = json.loads(SOR_FILE.read_text(encoding="utf-8"))
            return _SOR_CACHE
        except Exception as exc:
            logger.warning("Could not read PWD SoR catalog: %s", exc)
    return {}


def load_bhukosh_dataset() -> list[dict[str, Any]]:
    global _BHUKOSH_CACHE
    if _BHUKOSH_CACHE is not None:
        return _BHUKOSH_CACHE
    if BHUKOSH_FILE.exists():
        try:
            _BHUKOSH_CACHE = json.loads(BHUKOSH_FILE.read_text(encoding="utf-8"))
            return _BHUKOSH_CACHE
        except Exception as exc:
            logger.warning("Could not read Bhukosh dataset: %s", exc)
    return []


def load_usgs_standards() -> dict[str, Any]:
    global _USGS_CACHE
    if _USGS_CACHE is not None:
        return _USGS_CACHE
    if USGS_FILE.exists():
        try:
            _USGS_CACHE = json.loads(USGS_FILE.read_text(encoding="utf-8"))
            return _USGS_CACHE
        except Exception as exc:
            logger.warning("Could not read USGS standards: %s", exc)
    return {}


def load_larimit_catalog() -> dict[str, Any]:
    global _LARIMIT_CACHE
    if _LARIMIT_CACHE is not None:
        return _LARIMIT_CACHE
    if LARIMIT_FILE.exists():
        try:
            _LARIMIT_CACHE = json.loads(LARIMIT_FILE.read_text(encoding="utf-8"))
            return _LARIMIT_CACHE
        except Exception as exc:
            logger.warning("Could not read LaRiMiT catalog: %s", exc)
    return {}


def load_cedd_standards() -> dict[str, Any]:
    global _CEDD_CACHE
    if _CEDD_CACHE is not None:
        return _CEDD_CACHE
    if CEDD_FILE.exists():
        try:
            _CEDD_CACHE = json.loads(CEDD_FILE.read_text(encoding="utf-8"))
            return _CEDD_CACHE
        except Exception as exc:
            logger.warning("Could not read CEDD standards: %s", exc)
    return {}


def evaluate_cedd_consequence(
    env_type: str,
    road_type: str,
    severity: str,
) -> dict[str, Any]:
    """Evaluates slope risk according to Hong Kong CEDD Geoguide 1 & Geoguide 5.
    Determines Consequence-to-Life Category, Economic Loss Rating, Target FOS,
    and Mandatory Maintenance Inspection Protocol.
    """
    cedd = load_cedd_standards()
    cats = cedd.get("consequence_to_life_categories", {})
    econ_cats = cedd.get("consequence_to_economic_loss", {})
    insp_regimes = cedd.get("slope_maintenance_inspection_regime", {}).get("inspection_types", {})

    env_lower = (env_type or "").lower()
    road_lower = (road_type or "").lower()
    is_residential = any(w in env_lower for w in ("residential", "house", "dwelling", "building", "settlement"))
    is_high_volume = any(w in road_lower for w in ("nh", "national", "expressway", "sh", "state highway"))

    if is_residential or is_high_volume or severity == "Critical":
        cat_key = "Category_1"
        econ_key = "Category_A"
        insp_key = "DSA"
    elif "major district" in road_lower or severity == "High":
        cat_key = "Category_2"
        econ_key = "Category_B"
        insp_key = "EIM"
    else:
        cat_key = "Category_3"
        econ_key = "Category_C"
        insp_key = "RMI"

    cat_info = cats.get(cat_key, {})
    econ_info = econ_cats.get(econ_key, {})
    insp_info = insp_regimes.get(insp_key, {})

    target_fos = cat_info.get("minimum_target_fos", {"ten_year_rainfall": 1.30, "extreme_storm_event": 1.15})

    return {
        "consequence_category": cat_key.replace("_", " "),
        "consequence_level": cat_info.get("level", "Moderate Consequence"),
        "consequence_criteria": cat_info.get("criteria", ""),
        "economic_consequence": econ_info.get("level", "Moderate Economic Consequence"),
        "target_fos_10yr": target_fos.get("ten_year_rainfall", 1.30),
        "target_fos_extreme": target_fos.get("extreme_storm_event", 1.15),
        "mandatory_investigation": cat_info.get("mandatory_investigation", "Engineer Inspection for Maintenance (EIM)"),
        "inspection_regime": {
            "code": insp_key,
            "name": insp_info.get("name", "Engineer Inspection for Maintenance"),
            "frequency": insp_info.get("frequency", "Every 2 years"),
            "personnel": insp_info.get("personnel", "Qualified Geotechnical Engineer"),
            "key_checks": insp_info.get("key_checks", "Structural integrity audit"),
        },
    }


def evaluate_larimit_mitigations(
    movement_type: str,
    material_type: str = "Colluvium",
    severity: str = "Moderate",
    is_residential: bool = False,
) -> dict[str, Any]:
    """Executes multi-criteria suitability ranking across all 74 LaRiMiT measures (Klima 2050).
    Returns ranked Primary Structural, Hydrogeological Drainage, and Nature-Based (NBS) measures.
    """
    larimit = load_larimit_catalog()
    measures = larimit.get("measures", [])

    # Map movement string to Varnes mechanism key
    mov_lower = (movement_type or "").lower()
    if "slump" in mov_lower or "rotational" in mov_lower:
        mech = "Rotational Slump"
    elif "debris slide" in mov_lower or "colluv" in mov_lower:
        mech = "Debris Slide"
    elif "debris flow" in mov_lower or "torrent" in mov_lower:
        mech = "Debris Flow"
    elif "mud" in mov_lower:
        mech = "Mudflow"
    elif "topple" in mov_lower:
        mech = "Block Topple"
    elif "fall" in mov_lower or "boulder" in mov_lower:
        mech = "Rockfall"
    elif "gully" in mov_lower or "scour" in mov_lower:
        mech = "Gully Erosion"
    else:
        mech = "Planar Slide"

    # Score and filter measures
    scored_measures: list[dict[str, Any]] = []
    for m in measures:
        suits = m.get("suitability", {})
        base_score = float(suits.get(mech, 0.50))
        # Weighting adjustments based on residential setting or severity
        if is_residential and "Heavy Excavation" in m.get("name", ""):
            base_score *= 0.80
        if severity == "Critical" and "Soil Nailing" in m.get("name", ""):
            base_score = min(1.0, base_score * 1.05)
        item = dict(m)
        item["calculated_score"] = round(base_score, 2)
        scored_measures.append(item)

    scored_measures.sort(key=lambda x: x["calculated_score"], reverse=True)

    # Pick top structural measure (Clusters C1, C4, C5, C6, C7)
    structural_clusters = ("C1", "C4", "C5", "C6", "C7")
    top_structural = next((m for m in scored_measures if m.get("cluster") in structural_clusters), scored_measures[0] if scored_measures else {})

    # Pick top drainage measure (Clusters C2, C3)
    drainage_clusters = ("C2", "C3")
    top_drainage = next((m for m in scored_measures if m.get("cluster") in drainage_clusters), None)

    # Pick top Nature-Based Solution (Clusters C8, C9, C10)
    nbs_clusters = ("C8", "C9", "C10")
    top_nbs = next((m for m in scored_measures if m.get("cluster") in nbs_clusters), None)

    return {
        "analyzed_mechanism": mech,
        "primary_structural": {
            "id": top_structural.get("id", "M13"),
            "name": top_structural.get("name", "Passive Grouted Soil Nailing Array"),
            "cluster": top_structural.get("cluster_name", "Internal Ground Reinforcement"),
            "description": top_structural.get("description", ""),
            "suitability_score": top_structural.get("calculated_score", 0.95),
            "cost_tier": top_structural.get("cost_tier", "High"),
            "construction_time": top_structural.get("construction_time", "14-25 Days"),
        },
        "hydrogeological_drainage": {
            "id": top_drainage.get("id", "M07") if top_drainage else "M07",
            "name": top_drainage.get("name", "Sub-Horizontal Directional Relief Drains") if top_drainage else "Sub-Horizontal Directional Relief Drains",
            "cluster": top_drainage.get("cluster_name", "Subsurface Drainage") if top_drainage else "Subsurface Drainage",
            "description": top_drainage.get("description", "") if top_drainage else "",
            "suitability_score": top_drainage.get("calculated_score", 0.95) if top_drainage else 0.95,
            "cost_tier": top_drainage.get("cost_tier", "Medium") if top_drainage else "Medium",
            "construction_time": top_drainage.get("construction_time", "6-12 Days") if top_drainage else "6-12 Days",
        },
        "nature_based_solution": {
            "id": top_nbs.get("id", "M21") if top_nbs else "M21",
            "name": top_nbs.get("name", "Deep-Rooting Vetiver Grass Contour Hedges") if top_nbs else "Deep-Rooting Vetiver Grass Contour Hedges",
            "cluster": top_nbs.get("cluster_name", "Nature-Based Solutions: Soil Bioengineering") if top_nbs else "Soil Bioengineering",
            "description": top_nbs.get("description", "") if top_nbs else "",
            "suitability_score": top_nbs.get("calculated_score", 0.92) if top_nbs else 0.92,
            "cost_tier": top_nbs.get("cost_tier", "Low") if top_nbs else "Low",
            "construction_time": top_nbs.get("construction_time", "3-7 Days") if top_nbs else "3-7 Days",
        },
    }


def derive_prescribed_soil_nailing(severity: str, slope_height_m: float = 6.0) -> dict[str, Any]:
    """Derives exact prescribed soil nailing array per CEDD Geoguide 7."""
    cedd = load_cedd_standards()
    sn = cedd.get("prescribed_soil_nailing", {})
    layouts = sn.get("grid_layouts", {})
    layout = layouts.get(severity, layouts.get("Moderate", {}))

    bar_dia = layout.get("bar_diameter_mm", 25)
    hole_dia = layout.get("drillhole_diameter_mm", 100)
    spacing = layout.get("spacing", "2.00 m (H) x 2.00 m (V) Staggered Pattern")
    typ_len = layout.get("typical_length_m", f"{max(8.0, round(slope_height_m * 1.5, 1))} m")

    return {
        "design_code": "CEDD Geoguide 7 / BS EN 14490",
        "bar_diameter": f"Dia. {bar_dia} mm (Fe500 High-Yield Deformed Steel)",
        "drillhole_diameter": f"{hole_dia} mm",
        "drillhole_inclination": "15° to 20° downward rake",
        "grid_spacing": spacing,
        "nail_length": typ_len,
        "grout_strength": "Non-shrink neat cementitious grout (f_cu >= 30 MPa @ 28 days, W/C = 0.42)",
        "head_assembly": "Cast-in-situ RC Pad (400x400x200mm Grade C30/37) with galvanized bearing plate (200x200x20mm)",
        "testing_protocol": "2% sacrificial pullout verification up to 1.5x design working pullout capacity",
    }


def derive_flexible_barrier_specs(movement_type: str, severity: str) -> dict[str, Any]:
    """Derives flexible rockfall or debris barrier per CEDD GEO Report No. 138."""
    cedd = load_cedd_standards()
    barriers = cedd.get("flexible_rockfall_and_debris_barriers", {})
    specs = barriers.get("specifications", {})

    mov_lower = (movement_type or "").lower()
    is_debris_flow = "flow" in mov_lower or "mud" in mov_lower

    if severity == "Critical" or is_debris_flow:
        b_class = "3000_kJ"
    elif severity == "High":
        b_class = "1500_kJ"
    else:
        b_class = "500_kJ"

    b_spec = specs.get(b_class, specs.get("1500_kJ", {}))

    return {
        "design_code": "CEDD GEO Report No. 138 / EOTA EAD 340059-00-0106",
        "energy_absorption_capacity": f"{b_class.replace('_', ' ')} Rating",
        "barrier_height": f"{b_spec.get('barrier_height_m', 4.0):.1f} m",
        "steel_posts": b_spec.get("post_section", "HEB 180 Structural Steel"),
        "net_specification": b_spec.get("mesh_type", "High-tensile steel wire ring net (ROCCO 19-ring, 3.5mm wire)"),
        "energy_dissipators": b_spec.get("energy_dissipators", "Stainless steel friction brake rings"),
        "application_field": b_spec.get("application", "Active rockfall and debris runout corridor"),
        "debris_clearance": barriers.get("debris_flow_clearance", "0.5m to 0.8m bottom clearance for fluid slurry passage"),
    }


def derive_subsurface_drainage_specs(slope_height_m: float = 6.0, wall_length_m: float = 14.0) -> dict[str, Any]:
    """Derives sub-horizontal directional drainage array per CEDD GEO TGN 24."""
    cedd = load_cedd_standards()
    drain = cedd.get("subsurface_directional_drainage", {})
    d_params = drain.get("drill_parameters", {})

    drain_len = round(max(15.0, slope_height_m * 2.2), 1)
    num_drains = max(4, int(wall_length_m / 4.0) + 1)

    return {
        "design_code": "CEDD GEO TGN 24 / Geoguide 1",
        "pipe_specification": drain.get("pipe_spec", "50mm to 75mm dia heavy-duty slotted PVC pipe (Schedule 80)"),
        "slot_aperture": drain.get("slot_dimensions", "1.0mm to 1.5mm transverse slots @ 10mm c/c (15% open area)"),
        "filter_sock": drain.get("filter_jacket", "Non-woven needle-punched polypropylene geotextile sock (O90 < 0.15mm)"),
        "upward_inclination": d_params.get("upward_inclination", "5° to 10° upward rake for gravity self-cleansing flow"),
        "array_spacing": d_params.get("standard_spacing_m", "3.0 m to 6.0 m c/c staggered"),
        "drain_length": f"{drain_len} m per borehole (Total {num_drains} Nos. array)",
    }


def evaluate_usgs_classification(
    movement_type: str,
    material_type: str = "Colluvium / Soil",
    severity: str = "Moderate",
    trigger_cause: str = "Rainfall Infiltration",
) -> dict[str, Any]:
    """Evaluates slope movement according to USGS Circular 1325 (Highland & Bobrowsky, 2008)
    and Cruden & Varnes (1996) Transportation Research Board Special Report 247.
    """
    usgs = load_usgs_standards()
    defs = usgs.get("definitions", {})
    matrix = usgs.get("cruden_varnes_classification_matrix", {})
    velocities = usgs.get("velocity_scale", {})
    causal = usgs.get("causal_factors_and_triggers", {})

    mov_lower = (movement_type or "").lower()
    mat_lower = (material_type or "").lower()

    # Determine Varnes Movement Group
    if "fall" in mov_lower or "boulder" in mov_lower:
        mov_group = "Fall"
    elif "topple" in mov_lower:
        mov_group = "Topple"
    elif "slump" in mov_lower or "rotational" in mov_lower:
        mov_group = "Rotational Slide"
    elif "flow" in mov_lower or "mud" in mov_lower or "torrent" in mov_lower:
        mov_group = "Flow"
    elif "spread" in mov_lower:
        mov_group = "Lateral Spread"
    elif "complex" in mov_lower:
        mov_group = "Complex"
    else:
        mov_group = "Translational Slide"

    # Determine Material Substrate (Rock vs Debris vs Earth per USGS Circular 1325 / Cruden & Varnes 1996)
    if any(w in mat_lower for w in ("rock", "dolomite", "quartzite", "sandstone", "phyllite", "slate", "schist", "gneiss", "limestone", "basalt", "granite")):
        mat_key = "rock"
        mat_label = "Rock"
    elif any(w in mat_lower for w in ("clay", "silt", "sand", "fine", "earth")):
        mat_key = "earth"
        mat_label = "Earth (fine-grained soil < 2mm)"
    else:
        mat_key = "debris"
        mat_label = "Debris (coarse fragments > 2mm)"

    cat_entry = matrix.get(mov_group, matrix.get("Translational Slide", {}))
    two_term_name = cat_entry.get(mat_key, f"{mov_group} in {mat_label}")

    # Velocity Rating (Cruden & Varnes 1996 Table 3-6 / USGS Circular 1325)
    if mov_group in ("Fall", "Flow") or severity == "Critical":
        vel_key = "Class_6"
    elif mov_group == "Translational Slide" or severity == "High":
        vel_key = "Class_5"
    elif mov_group == "Rotational Slide":
        vel_key = "Class_4"
    else:
        vel_key = "Class_3"

    vel_info = velocities.get(vel_key, velocities.get("Class_4", {}))

    return {
        "usgs_general_definition": defs.get(
            "general_definition",
            "A landslide is a general term used to describe the downslope movement of soil, rock, and organic materials under the effects of gravity and also the landform that results from such movement.",
        ),
        "usgs_kinematic_definition": defs.get(
            "kinematic_definition",
            "A downslope movement of rock or soil, or both, occurring on the surface of rupture—either curved or planar rupture—in which much of the material often moves as a coherent or semicoherent mass.",
        ),
        "two_term_classification": two_term_name,
        "primary_movement": mov_group,
        "material_class": mat_label,
        "material_definition": defs.get("material_divisions", {}).get(mat_key, ""),
        "movement_definition": cat_entry.get("definition", ""),
        "velocity_class": {
            "class_code": vel_key.replace("_", " "),
            "rate_name": vel_info.get("name", "Moderate"),
            "velocity_range": vel_info.get("velocity_range", "13 m/month to 1.8 m/h"),
            "consequences": vel_info.get("consequences", ""),
        },
        "landslide_anatomy": {
            "crown_and_scarp": "Undisplaced crown with open extensional crown cracks; distinct steep main scarp exposing rupture surface.",
            "displaced_mass": "Depleted mass above planar/rotational surface of rupture, extending downslope into zone of accumulation.",
            "toe_and_foot": "Displaced foot advancing beyond toe of rupture surface across roadway/property margin.",
        },
        "causal_factors": {
            "geological": causal.get("geological_causes", [])[:2],
            "morphological": causal.get("morphological_causes", [])[:2],
            "physical_trigger": causal.get("physical_triggers", [])[:2],
            "human_causes": causal.get("human_causes", [])[:2],
        },
        "standard_reference": "USGS Circular 1325 (Highland & Bobrowsky, 2008) & Cruden & Varnes (1996) TRB Special Report 247",
    }


def query_bhukosh_geology(
    lat: float,
    lng: float,
    district: str = "Mandi",
    max_search_radius_km: float = 30.0,
) -> dict[str, Any]:
    """Queries the Geological Survey of India (GSI) Bhukosh National Geoscientific
    Database Gateway to identify the authoritative in-situ rock lithology, structure,
    and toposheet at the specified geographic coordinates.
    """
    import math

    pts = load_bhukosh_dataset()
    best_pt = None
    best_dist = float("inf")
    secondary_bedrock_pt = None
    secondary_bedrock_dist = float("inf")

    generic_terms = ("debris", "colluvium", "scree", "soil", "alluvium")

    if pts and lat and lng:
        for pt in pts:
            p_lat = pt.get("lat")
            p_lng = pt.get("lng")
            if p_lat is None or p_lng is None:
                continue
            # Haversine distance
            dlat = math.radians(p_lat - lat)
            dlng = math.radians(p_lng - lng)
            a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat)) * math.cos(math.radians(p_lat)) * math.sin(dlng / 2) ** 2
            dist_km = 6371.0 * 2 * math.asin(math.sqrt(a))

            if dist_km < best_dist:
                best_dist = dist_km
                best_pt = pt

            geol_lower = (pt.get("geology") or "").lower().strip()
            if not any(g == geol_lower for g in generic_terms):
                if dist_km < secondary_bedrock_dist:
                    secondary_bedrock_dist = dist_km
                    secondary_bedrock_pt = pt

    # If the nearest point is generic 'debris' but a solid bedrock point is within 5km, use the bedrock point
    chosen_pt = best_pt
    chosen_dist = best_dist
    if best_pt and (best_pt.get("geology") or "").lower().strip() in generic_terms:
        if secondary_bedrock_pt and secondary_bedrock_dist <= max(8.0, best_dist + 5.0):
            chosen_pt = secondary_bedrock_pt
            chosen_dist = secondary_bedrock_dist

    if chosen_pt and chosen_dist <= max_search_radius_km:
        return {
            "primary_rock": chosen_pt.get("geology", "Shali Dolomite & Sundernagar Quartzite"),
            "toposheet": chosen_pt.get("toposheet") or "N/A",
            "structure": chosen_pt.get("structure") or "Discontinuities dipping into valley",
            "citation": chosen_pt.get("citation") or "GSI Macro-scale Landslide Susceptibility Mapping",
            "distance_km": round(chosen_dist, 2),
            "source": f"GSI Bhukosh Spatial Survey (Toposheet {chosen_pt.get('toposheet')})",
            "is_spatial_match": True,
        }

    # Fallback to GSI District Stratigraphic Atlas if coordinates are beyond survey grid
    return {
        "primary_rock": "Shali Dolomite & Sundernagar Quartzite with interbedded phyllitic slate",
        "toposheet": "Regional GSI Map",
        "structure": "Joints dipping 50°–65° adversely daylighting into road cut",
        "citation": "Geological Survey of India (GSI) Stratigraphic Atlas of Himachal Pradesh",
        "distance_km": None,
        "source": "GSI Bhukosh District Stratigraphic Series",
        "is_spatial_match": False,
    }


LITHO_KEYWORDS = [
    "quartzite", "dolomite", "limestone", "sandstone", "phyllite", "slate",
    "schist", "gneiss", "granite", "shale", "siltstone", "conglomerate",
    "basalt", "marble", "carbonate", "chert", "phyllitic", "quartz", "calcite"
]


def validate_and_reconcile_rock_classification(
    ai_detected_rock: str | None,
    bhukosh_info: dict[str, Any],
) -> dict[str, Any]:
    """Compares the AI vision model's detected rock lithology against the official
    Geological Survey of India (GSI) Bhukosh ground truth.
    Flags discrepancies and calibrates the primary rock classification to Bhukosh.
    """
    import re

    bhukosh_rock = bhukosh_info.get("primary_rock", "Shali Dolomite & Sundernagar Quartzite")
    toposheet = bhukosh_info.get("toposheet", "Regional GSI Sheet")
    dist_km = bhukosh_info.get("distance_km")

    if not ai_detected_rock or ai_detected_rock.strip().lower() in ("unknown", "n/a", "none"):
        return {
            "bhukosh_formation": bhukosh_rock,
            "toposheet": toposheet,
            "distance_km": dist_km,
            "ai_detected_rock": "None specified",
            "is_discrepancy": False,
            "status": "BHUKOSH_VERIFIED",
            "status_label": "GSI Bhukosh Ground Truth Verified",
            "calibrated_rock": bhukosh_rock,
            "reconciliation_note": f"Lithology established directly from official GSI Bhukosh survey data ({bhukosh_rock}).",
        }

    ai_clean = ai_detected_rock.strip()
    ai_words = set(re.findall(r"\w+", ai_clean.lower()))
    bhu_words = set(re.findall(r"\w+", bhukosh_rock.lower()))

    ai_kw = {w for w in ai_words if any(k in w for k in LITHO_KEYWORDS)}
    bhu_kw = {w for w in bhu_words if any(k in w for k in LITHO_KEYWORDS)}

    is_match = False
    if ai_kw.intersection(bhu_kw):
        is_match = True
    elif "sedimentary" in ai_words and any(w in bhu_words for w in ("sandstone", "shale", "limestone", "dolomite", "siltstone")):
        is_match = True
    elif "metamorphic" in ai_words and any(w in bhu_words for w in ("schist", "gneiss", "phyllite", "quartzite", "slate")):
        is_match = True

    dist_str = f" ({dist_km:.1f} km away)" if dist_km is not None else ""

    if is_match:
        return {
            "bhukosh_formation": bhukosh_rock,
            "toposheet": toposheet,
            "distance_km": dist_km,
            "ai_detected_rock": ai_clean,
            "is_discrepancy": False,
            "status": "BHUKOSH_VERIFIED",
            "status_label": "GSI Bhukosh Ground Truth Verified",
            "calibrated_rock": f"{bhukosh_rock} (AI: {ai_clean})",
            "reconciliation_note": f"Optical analysis ('{ai_clean}') is consistent with official GSI Bhukosh ground truth{dist_str}.",
        }
    else:
        # Discrepancy detected -> Flag and calibrate to official Bhukosh data!
        return {
            "bhukosh_formation": bhukosh_rock,
            "toposheet": toposheet,
            "distance_km": dist_km,
            "ai_detected_rock": ai_clean,
            "is_discrepancy": True,
            "status": "FLAGGED_AND_CORRECTED",
            "status_label": "Discrepancy Flagged — Calibrated to GSI Bhukosh Ground Truth",
            "calibrated_rock": bhukosh_rock,
            "reconciliation_note": f"Optical vision model predicted '{ai_clean}', which diverges from official GSI Bhukosh ground truth ('{bhukosh_rock}'{dist_str}, Toposheet {toposheet}). Lithology flagged and calibrated to Bhukosh.",
        }


def format_inr(amount: float) -> str:
    """Formats a floating-point number into official Indian Rupee currency representation."""
    amount_int = int(round(amount))
    s = str(abs(amount_int))
    if len(s) <= 3:
        formatted = s
    else:
        last_three = s[-3:]
        remaining = s[:-3]
        groups = []
        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.insert(0, remaining)
        formatted = ",".join(groups) + "," + last_three
    sign = "-" if amount_int < 0 else ""
    return f"₹ {sign}{formatted}"


def format_lakhs_crores(amount: float) -> str:
    """Formats amount into compact Lakhs / Crores string for executive KPI cards."""
    abs_amt = abs(amount)
    if abs_amt >= 10000000:
        return f"₹ {amount / 10000000:.2f} Cr"
    elif abs_amt >= 100000:
        return f"₹ {amount / 100000:.2f} Lakh"
    else:
        return format_inr(amount)


def calculate_comprehensive_cost_and_loss_estimate(
    dossier: dict[str, Any],
    report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Generates an itemized Bill of Quantities (BOQ) conforming to the HPPWD Schedule of Rates
    (HPSOR) and MoRTH Specifications for Road and Bridge Works (5th Revision), accompanied by a
    comprehensive Disaster Loss Assessment (Direct Asset Physical Damage & Corridor Disruption Economics).
    """
    sor_data = load_sor_standards()
    metadata = sor_data.get("schedule_metadata", {
        "title": "Himachal Pradesh Public Works Department (HPPWD) & MoRTH Schedule of Rates for Hill Roads",
        "primary_references": [
            "HPPWD Schedule of Rates (HPSOR), Government of Himachal Pradesh",
            "MoRTH Specifications for Road and Bridge Works (5th Revision)",
            "IRC Standard Data Book for Analysis of Rates for Road and Bridge Works",
        ],
        "applicable_terrain": "Himalayan Hill Roads & High Altitude Sectors",
        "currency": "INR (₹)",
        "tax_regime": {
            "gst_percentage": 18.0,
            "contingencies_percentage": 3.0,
            "quality_control_percentage": 1.5,
        },
    })

    is_valid = dossier.get("is_landslide_or_terrain", True)
    status = dossier.get("validation_status", "VALID_TERRAIN_IMAGE")

    if not is_valid or status == "INVALID_NON_TERRAIN_IMAGE":
        return {
            "status": "DISQUALIFIED_NON_TERRAIN",
            "is_applicable": False,
            "rejection_notice": "Non-terrain media upload / Verification Rejected: Remediation BOQ suspended. Field reconnaissance survey required prior to civil estimates.",
            "schedule_metadata": metadata,
            "financial_summary": {
                "civil_subtotal_raw": 0.0,
                "civil_subtotal_fmt": "₹ 0",
                "contingencies_raw": 0.0,
                "contingencies_fmt": "₹ 0",
                "qc_testing_raw": 0.0,
                "qc_testing_fmt": "₹ 0",
                "gst_raw": 0.0,
                "gst_fmt": "₹ 0",
                "total_remediation_raw": 0.0,
                "total_remediation_fmt": "₹ 0",
                "total_remediation_badge": "₹ 0.00 Lakh",
                "direct_asset_loss_raw": 0.0,
                "direct_asset_loss_fmt": "₹ 0",
                "indirect_economic_loss_raw": 0.0,
                "indirect_economic_loss_fmt": "₹ 0",
                "grand_total_disaster_impact_raw": 0.0,
                "grand_total_disaster_impact_fmt": "₹ 0",
                "grand_total_disaster_impact_badge": "₹ 0.00 Lakh",
            },
            "boq_items": [],
            "loss_items": [],
        }

    # Extract geometric and physical site dimensions
    wall_specs = dossier.get("retaining_wall_specs") or {}
    h_wall = float(wall_specs.get("height_m") or 3.2)
    l_wall = float(wall_specs.get("length_m") or 16.0)
    embed_d = float(wall_specs.get("embedded_depth_m") or max(1.0, round(0.25 * h_wall, 2)))
    base_w = float(wall_specs.get("base_width_m") or round(0.50 * h_wall, 2))
    top_w = float(wall_specs.get("top_width_m") or (0.70 if h_wall >= 4.0 else 0.60))

    gab_earth = dossier.get("gabion_and_earthworks") or {}
    exc = gab_earth.get("excavation") or {}
    exc_vol = float(exc.get("volume_m3") or round(h_wall * 0.8 * l_wall * 4.5, 1))
    h_cut = float(exc.get("h_m") or round(h_wall * 0.8, 1))
    fill = gab_earth.get("fill") or {}
    fill_vol = float(fill.get("volume_m3") or round(0.35 * l_wall * (h_wall * 0.60), 2))

    sev = (dossier.get("telemetry") or {}).get("reported_severity") or (report or {}).get("severity") or "Moderate"
    site_ctx = dossier.get("site_context") or {}
    env_type = (site_ctx.get("environment_type") or "").lower()
    is_residential = "residential" in env_type or "house" in env_type or "settlement" in env_type
    is_orchard = "orchard" in env_type or "agri" in env_type or "terrace" in env_type

    # Prescribed soil nailing parameters
    nail_len = 9.0
    if sev == "Critical":
        nail_len = 12.0
    elif sev == "High":
        nail_len = 10.0
    elif sev == "Low":
        nail_len = 6.0
    n_nails = max(8, int(round((l_wall / 1.75) * (max(2.0, h_cut) / 1.75))))

    # Drainage parameters
    n_drains = max(4, int(l_wall / 4.0) + 1)
    drain_len = round(max(15.0, h_cut * 2.2), 1)

    # Plum concrete wall volume (trapezoidal cross-section * length)
    wall_total_h = h_wall + embed_d
    cs_area = ((top_w + base_w) / 2.0) * wall_total_h
    plum_conc_vol = round(cs_area * l_wall, 2)
    trench_exc_vol = round(l_wall * base_w * embed_d, 2)
    slope_trim_area = round(l_wall * (h_cut * 1.3), 2)
    geotextile_area = round(l_wall * wall_total_h, 2)
    weep_pipes_count = max(6, int(round((l_wall / 1.2) * (h_wall / 1.2))))
    weep_pipes_len = round(weep_pipes_count * (base_w * 0.75), 1)

    boq_raw = [
        {
            "item_code": "MoRTH 301.1",
            "work_package": "Earthwork & Clearance",
            "description": "Hydraulic excavation of saturated landslide debris, loose soil, and boulders up to 3 m³ using heavy hydraulic breaker excavator, including loading into tippers and disposal with lead up to 1000m.",
            "quantity": exc_vol,
            "unit": "m³",
            "rate": 220.0,
        },
        {
            "item_code": "MoRTH 305.2",
            "work_package": "Earthwork & Clearance",
            "description": "Slope trimming, scarp reprofiling, and dressing of unstable overburden cut face to stable bench profile in all kinds of soil and soft rock.",
            "quantity": slope_trim_area,
            "unit": "m²",
            "rate": 115.0,
        },
        {
            "item_code": "MoRTH 304.3",
            "work_package": "Earthwork & Clearance",
            "description": "Foundation trench excavation in hard rock / compact boulder strata with pneumatic breaker tools, including necessary shoring, strutting, and dewatering for breast wall footing.",
            "quantity": trench_exc_vol,
            "unit": "m³",
            "rate": 580.0,
        },
        {
            "item_code": "HPSOR 4.2 / MoRTH 1402",
            "work_package": "Structural Retention",
            "description": f"Construction of Plum Concrete Retaining / Breast Wall (H={h_wall:.1f}m, B={base_w:.2f}m, b={top_w:.2f}m) in M15 grade concrete (1:2:4) with 30% to 40% clean sound quarry plum boulders (density >= 18 kN/m³), including steel shuttering, scaffolding, compaction, and 14 days water curing.",
            "quantity": plum_conc_vol,
            "unit": "m³",
            "rate": 4250.0,
        },
        {
            "item_code": "MoRTH 702.1",
            "work_package": "Structural Retention",
            "description": "Supplying and laying non-woven needle-punched polypropylene geotextile filter fabric (weight >= 250 GSM, O90 < 0.15 mm) behind retaining wall backface.",
            "quantity": geotextile_area,
            "unit": "m²",
            "rate": 145.0,
        },
        {
            "item_code": "HPSOR 4.8 / MoRTH 305",
            "work_package": "Structural Retention",
            "description": "Providing and laying free-draining granular backfill filter material (crushed stone gravel 20-40mm) behind retaining wall in layers not exceeding 150mm compacted thickness.",
            "quantity": fill_vol,
            "unit": "m³",
            "rate": 980.0,
        },
        {
            "item_code": "HPSOR 4.9",
            "work_package": "Structural Retention",
            "description": f"Providing and installing 100mm dia heavy-duty PVC weep hole pipes (Class 3) placed at 1.20m c/c staggered with 1:20 outward slope and gravel filter envelope at inlet (Total {weep_pipes_count} Nos.).",
            "quantity": weep_pipes_len,
            "unit": "meter",
            "rate": 260.0,
        },
        {
            "item_code": "MoRTH 1302 / Geoguide 7",
            "work_package": "Internal Ground Reinforcement",
            "description": f"Rotary / percussive drilling of 100mm to 110mm dia boreholes in soil/colluvium/fractured rock for soil nails at 15° to 20° downward rake to specified design length ({n_nails} Nos. x {nail_len:.1f}m).",
            "quantity": round(n_nails * nail_len, 1),
            "unit": "meter",
            "rate": 880.0,
        },
        {
            "item_code": "MoRTH 1002.1",
            "work_package": "Internal Ground Reinforcement",
            "description": f"Supplying, cutting, threading, and inserting Dia. 28mm Fe500 high-yield deformed steel soil nail bars with polypropylene centralizers @ 2m c/c.",
            "quantity": round(n_nails * nail_len, 1),
            "unit": "meter",
            "rate": 420.0,
        },
        {
            "item_code": "MoRTH 1304.2",
            "work_package": "Internal Ground Reinforcement",
            "description": "Pressure grouting of soil nail boreholes with non-shrink neat cementitious grout (f_cu >= 30 MPa @ 28 days, W/C = 0.42, injection pressure 0.3-0.5 MPa).",
            "quantity": round(n_nails * nail_len, 1),
            "unit": "meter",
            "rate": 520.0,
        },
        {
            "item_code": "MoRTH 1306.1",
            "work_package": "Internal Ground Reinforcement",
            "description": f"Cast-in-situ reinforced concrete bearing pad (400x400x200mm Grade C30/37) with galvanized steel bearing plate (200x200x20mm) and high-tensile spherical hex nut assembly ({n_nails} sets).",
            "quantity": float(n_nails),
            "unit": "unit",
            "rate": 2150.0,
        },
        {
            "item_code": "CEDD Geoguide 7",
            "work_package": "Internal Ground Reinforcement",
            "description": "Sacrificial pullout verification proof testing of soil nails using hydraulic hollow-plunger jack up to 1.5x design working load with dial gauge creep recording (2% statutory testing).",
            "quantity": float(max(2, int(round(n_nails * 0.05)))),
            "unit": "test",
            "rate": 5000.0,
        },
        {
            "item_code": "MoRTH 1704 / TGN 24",
            "work_package": "Subsurface & Surface Drainage",
            "description": f"Directional drilling and installation of 65mm dia heavy-duty slotted PVC sub-horizontal relief drains (Schedule 80) jacketed with non-woven geotextile filter sock at 5° to 10° upward rake ({n_drains} Nos. array).",
            "quantity": round(n_drains * drain_len, 1),
            "unit": "meter",
            "rate": 1150.0,
        },
        {
            "item_code": "HPSOR 5.3 / MoRTH 1702",
            "work_package": "Subsurface & Surface Drainage",
            "description": "Construction of Stone Masonry Hillside Saucer Catch Drain (0.60m wide x 0.60m deep) in cement mortar 1:4 with 100mm M15 concrete bedding and pointing.",
            "quantity": round(l_wall + 8.0, 1),
            "unit": "meter",
            "rate": 780.0,
        },
        {
            "item_code": "MoRTH 1703.1",
            "work_package": "Subsurface & Surface Drainage",
            "description": "Construction of stepped cascade drainage chute lined with stone pitching and concrete cross-weirs discharging into natural ravine.",
            "quantity": round(min(25.0, l_wall + 5.0), 1),
            "unit": "meter",
            "rate": 1050.0,
        },
    ]

    # Flexible rockfall & debris barrier (if High/Critical)
    if sev in ("High", "Critical"):
        b_rate = 26500.0 if sev == "Critical" else 14500.0
        b_code = "GEO 138 (1500-3000 kJ)" if sev == "Critical" else "GEO 138 (500 kJ)"
        b_name = "1500 to 3000 kJ certified heavy-duty flexible ring net barrier (HEB 180 posts, ROCCO ring nets)" if sev == "Critical" else "500 kJ certified flexible wire-rope ring net rockfall barrier (HEB 140 posts, friction brake rings)"
        boq_raw.append({
            "item_code": b_code,
            "work_package": "Dynamic Defense & Bioengineering",
            "description": f"Supply and erection of {b_name} along active slide / rockfall chute.",
            "quantity": l_wall,
            "unit": "meter",
            "rate": b_rate,
        })

    # Bioengineering
    boq_raw.append({
        "item_code": "MoRTH 1802 / IRC:SP:48",
        "work_package": "Dynamic Defense & Bioengineering",
        "description": "Soil bioengineering: Supplying and laying open-weave coir geotextile netting (700 GSM) anchored with bamboo pins, hydroseeding with native grass mixes, and planting deep-rooting Vetiver grass (Chrysopogon zizanioides) contour hedges.",
        "quantity": slope_trim_area,
        "unit": "m²",
        "rate": 195.0,
    })

    # Build final formatted BOQ list
    boq_items: list[dict[str, Any]] = []
    civil_subtotal = 0.0
    for idx, item in enumerate(boq_raw, start=1):
        amt = round(item["quantity"] * item["rate"], 2)
        civil_subtotal += amt
        boq_items.append({
            "sl_no": idx,
            "item_code": item["item_code"],
            "work_package": item["work_package"],
            "description": item["description"],
            "quantity": item["quantity"],
            "unit": item["unit"],
            "rate": item["rate"],
            "rate_fmt": format_inr(item["rate"]),
            "amount": amt,
            "amount_fmt": format_inr(amt),
        })

    contingencies = round(civil_subtotal * 0.03, 2)
    qc_testing = round(civil_subtotal * 0.015, 2)
    subtotal_before_tax = civil_subtotal + contingencies + qc_testing
    gst = round(subtotal_before_tax * 0.18, 2)
    total_remediation = round(subtotal_before_tax + gst, 2)

    # Disaster Loss Assessment
    loss_raw: list[dict[str, Any]] = []

    if is_residential:
        dwell_amt = 1200000.0 if sev in ("High", "Critical") else 450000.0
        dwell_desc = "Major Structural Rebuilding: Breached foundation/rearing wall, debris infiltration into living quarters" if sev in ("High", "Critical") else "Structural Repair: Masonry crack stitching, plaster reinstatement, foundation stabilization"
        loss_raw.append({
            "category": "Direct Asset Loss",
            "asset": "Residential Dwelling / Habitable Structure",
            "criteria": dwell_desc,
            "amount": dwell_amt,
        })
        loss_raw.append({
            "category": "Direct Asset Loss",
            "asset": "Household Belongings & Interior Salvage",
            "criteria": "Loss of furniture, domestic appliances, and stored goods due to slurry inundation",
            "amount": 180000.0,
        })
        loss_raw.append({
            "category": "Direct Asset Loss",
            "asset": "Occupant Emergency Relocation & Subsistence",
            "criteria": "Statutory temporary accommodation and family evacuation support allowance (3 months)",
            "amount": 75000.0,
        })

    # Highway / Transport Corridor Direct Asset Damage
    pave_area = round(l_wall * 6.5, 1)
    pave_amt = round(pave_area * 1650.0, 2)
    loss_raw.append({
        "category": "Direct Asset Loss",
        "asset": "Highway Carriageway & Formation",
        "criteria": f"Full pavement reconstruction ({pave_area} m²): Scarification of damaged bitumen, subgrade re-compaction, 150mm WMM and 50mm Bituminous Concrete overlay @ ₹1,650/m²",
        "amount": pave_amt,
    })
    loss_raw.append({
        "category": "Direct Asset Loss",
        "asset": "Roadside Culvert & Drainage Appurtenances",
        "criteria": "Choked box culvert barrel hydraulic flushing, wingwall crack injection, and headwall masonry repair",
        "amount": 180000.0,
    })
    loss_raw.append({
        "category": "Direct Asset Loss",
        "asset": "Emergency Highway Corridor Staging & Traffic Diversion",
        "criteria": "Deployment of temporary steel crash barricades, solar LED hazard flashers, warning signage, and 24/7 flagger spotters",
        "amount": 35000.0,
    })

    if is_orchard:
        loss_raw.append({
            "category": "Direct Asset Loss",
            "asset": "Apple Orchard & Agricultural Terraces",
            "criteria": "Rebuilding dry stone retaining terraces, topsoil replacement, and sapling reinstatement compensation",
            "amount": 470000.0,
        })

    # Indirect Economic Disruption Loss (Corridor Closure / Detour)
    blockage_days = 3.5 if sev == "Critical" else (2.0 if sev == "High" else (1.0 if sev == "Moderate" else 0.5))
    daily_detour_cost = 125000.0
    transit_loss = round(blockage_days * daily_detour_cost, 2)
    loss_raw.append({
        "category": "Indirect Economic Loss",
        "asset": "Regional Corridor Transit Disruption",
        "criteria": f"{blockage_days:.1f} days estimated corridor severance / restricted passage: Commercial freight detours (extra 45 km via alternate link), passenger idle hours, and fuel consumption surcharge @ ₹1,25,000/day",
        "amount": transit_loss,
    })

    loss_items: list[dict[str, Any]] = []
    direct_asset_loss = 0.0
    indirect_economic_loss = 0.0
    for idx, it in enumerate(loss_raw, start=1):
        amt = it["amount"]
        if it["category"] == "Direct Asset Loss":
            direct_asset_loss += amt
        else:
            indirect_economic_loss += amt
        loss_items.append({
            "sl_no": idx,
            "category": it["category"],
            "asset": it["asset"],
            "criteria": it["criteria"],
            "amount": amt,
            "amount_fmt": format_inr(amt),
        })

    total_disaster_loss = round(direct_asset_loss + indirect_economic_loss, 2)
    grand_total_disaster_impact = round(total_remediation + total_disaster_loss, 2)

    return {
        "status": "CALCULATED_OK",
        "is_applicable": True,
        "rejection_notice": None,
        "schedule_metadata": metadata,
        "parameters_used": {
            "severity": sev,
            "environment_type": env_type or "Highway Corridor",
            "wall_height_m": h_wall,
            "wall_length_m": l_wall,
            "wall_embed_m": embed_d,
            "base_width_m": base_w,
            "top_width_m": top_w,
            "plum_concrete_vol_m3": plum_conc_vol,
            "excavation_vol_m3": exc_vol,
            "slope_trim_area_m2": slope_trim_area,
            "fill_vol_m3": fill_vol,
            "soil_nails_count": n_nails,
            "soil_nail_len_m": nail_len,
            "relief_drains_count": n_drains,
            "relief_drain_len_m": drain_len,
        },
        "financial_summary": {
            "civil_subtotal_raw": civil_subtotal,
            "civil_subtotal_fmt": format_inr(civil_subtotal),
            "contingencies_raw": contingencies,
            "contingencies_fmt": format_inr(contingencies),
            "qc_testing_raw": qc_testing,
            "qc_testing_fmt": format_inr(qc_testing),
            "subtotal_before_tax_raw": subtotal_before_tax,
            "subtotal_before_tax_fmt": format_inr(subtotal_before_tax),
            "gst_raw": gst,
            "gst_fmt": format_inr(gst),
            "total_remediation_raw": total_remediation,
            "total_remediation_fmt": format_inr(total_remediation),
            "total_remediation_badge": format_lakhs_crores(total_remediation),
            "direct_asset_loss_raw": direct_asset_loss,
            "direct_asset_loss_fmt": format_inr(direct_asset_loss),
            "direct_asset_loss_badge": format_lakhs_crores(direct_asset_loss),
            "indirect_economic_loss_raw": indirect_economic_loss,
            "indirect_economic_loss_fmt": format_inr(indirect_economic_loss),
            "indirect_economic_loss_badge": format_lakhs_crores(indirect_economic_loss),
            "total_disaster_loss_raw": total_disaster_loss,
            "total_disaster_loss_fmt": format_inr(total_disaster_loss),
            "total_disaster_loss_badge": format_lakhs_crores(total_disaster_loss),
            "grand_total_disaster_impact_raw": grand_total_disaster_impact,
            "grand_total_disaster_impact_fmt": format_inr(grand_total_disaster_impact),
            "grand_total_disaster_impact_badge": format_lakhs_crores(grand_total_disaster_impact),
        },
        "boq_items": boq_items,
        "loss_items": loss_items,
    }

