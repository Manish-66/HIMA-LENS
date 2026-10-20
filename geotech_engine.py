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

_LARIMIT_CACHE: dict[str, Any] | None = None
_CEDD_CACHE: dict[str, Any] | None = None
_USGS_CACHE: dict[str, Any] | None = None


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
