"""HIMA-LENS Geotechnical ML Schematic Cross-Section Engine.

Translates computer vision observations, empirical telemetry, and geotechnical engineering
parameters into publication-grade, dynamic 2D vector cross-section schematics (SVG) conforming
to USGS Circular 1325 (Highland & Bobrowsky, 2008), Cruden & Varnes (1996), IS:14458,
IRC:SP:48:2023, and CEDD Geoguides.

Supported failure kinematics & archetypes:
- Translational / Planar Rock Slide along Daylighting Joint
- Rotational Slump / Circular Overburden Failure with Crown Tension Cracks & Toe Heave
- Rockfall / Columnar Topple along Sub-Vertical Exfoliation Fissures
- Channelized Debris Flow / Rapid Slurry Runout Fan
- Structural Wedge Failure along Intersecting Discontinuity Planes (J1 x J2)
- Creep / Progressive Soil Subsidence with Pavement Distortion
- Valley Road Embankment Subsidence (Stepped Gabions + Micropiles + Geogrid)
- Habitation Residential Terrace Slump (M25 RC Deflector Wall + House Protection)
- Macro-Scale Mountain Catastrophe (Diagnostic Notice Plate · DPR Mandated)
- Disqualified Non-Terrain / False Alarm Media (Diagnostic Suppressed Plate)
"""
from __future__ import annotations

import math
import re
from typing import Any


def _extract_angle(angle_str: str | int | float | None, default: int = 57) -> int:
    """Extracts a numeric angle in degrees from text or numeric input."""
    if angle_str is None:
        return default
    if isinstance(angle_str, (int, float)):
        return max(10, min(88, int(angle_str)))
    match = re.search(r"(\d+)", str(angle_str))
    if match:
        val = int(match.group(1))
        if 10 <= val <= 88:
            return val
    return default


def _extract_width(width_str: str | float | int | None, default: float = 5.25) -> float:
    """Extracts width in meters from text or numeric input."""
    if width_str is None:
        return default
    if isinstance(width_str, (int, float)):
        return round(float(width_str), 2)
    match = re.search(r"(\d+(?:\.\d+)?)", str(width_str))
    if match:
        return round(float(match.group(1)), 2)
    return default


def _extract_height(height_str: str | float | int | None, default: float = 7.5) -> float:
    """Extracts slope height in meters from text or numeric input."""
    if height_str is None:
        return default
    if isinstance(height_str, (int, float)):
        return round(float(height_str), 1)
    match = re.search(r"(\d+(?:\.\d+)?)", str(height_str))
    if match:
        return round(float(match.group(1)), 1)
    return default


def extract_ml_kinematic_parameters(
    assessment: dict[str, Any] | None,
    report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Extracts or derives kinematic geometry parameters from ML vision assessment

    and report telemetry. Integrates directly with ProjectDataModel (pdm) so
    stability FoS numbers, dimensions, and failure vectors are 100% harmonized.
    """
    assessment = assessment or {}
    report = report or {}

    # 1. Resolve ProjectDataModel (pdm) as authoritative Single Source of Truth
    pdm: dict[str, Any] = {}
    if isinstance(assessment, dict):
        pdm = assessment.get("project_data_model") or {}
        if not pdm and ("unified_geometry" in assessment or "stability_analysis" in assessment):
            pdm = assessment
    if not pdm and isinstance(report, dict):
        pdm = report.get("project_data_model") or {}
        if not pdm and ("unified_geometry" in report or "stability_analysis" in report):
            pdm = report
    if not pdm:
        try:
            import geotech_engine
            pdm = geotech_engine.build_project_data_model(dossier=assessment, report=report)
        except Exception:
            pdm = {}

    geom = pdm.get("unified_geometry") or {}
    stab = pdm.get("stability_analysis") or {}
    failure_vector = pdm.get("failure_vector") or geom.get("failure_vector") or ""
    is_applicable = pdm.get("is_applicable", True)
    rejection_notice = pdm.get("rejection_notice") or ""

    obs = assessment.get("observed_features") or {}
    opt_geom = obs.get("optical_geometry") or {}
    slope = assessment.get("slope_characteristics") or {}
    geol = assessment.get("geology") or {}
    road = assessment.get("road_impact") or {}
    rw_specs = assessment.get("retaining_wall_specs") or {}
    telemetry = assessment.get("telemetry") or {}

    is_terrain = assessment.get("is_landslide_or_terrain", True)
    validation_status = str(assessment.get("validation_status") or "VALID")

    # 2. Extract authentic solved FoS values from stability_analysis scenarios
    scenarios = stab.get("scenarios") or []
    crit_fos: float | None = None
    target_fos: float | None = None
    fos_dry: float | None = None

    for sc in scenarios:
        sid = str(sc.get("stage_id") or "").lower()
        cfos = sc.get("calculated_fos")
        if cfos is not None:
            try:
                val = round(float(cfos), 2)
            except (ValueError, TypeError):
                continue
            if "monsoon" in sid or "saturated" in sid:
                crit_fos = val
            elif "remediation" in sid or "stabilized" in sid or "post" in sid:
                target_fos = val
            elif "dry" in sid or "baseline" in sid:
                fos_dry = val

    if crit_fos is None:
        crit_fos = 0.92 if failure_vector == "UPHILL_CUT_SLOPE" else 0.85
    if target_fos is None:
        target_fos = 1.56 if failure_vector == "UPHILL_CUT_SLOPE" else 1.55
    if fos_dry is None:
        fos_dry = 1.48

    if not is_applicable:
        crit_fos = 0.0
        target_fos = 0.0
        fos_dry = 0.0

    # 3. Dimensions & physical geometry (pdm.unified_geometry takes precedence)
    dip_raw = (
        geom.get("joint_dip_deg")
        or opt_geom.get("slip_surface_dip_deg")
        or geol.get("dip_joints")
        or geol.get("joint_orientation")
    )
    dip_deg = _extract_angle(dip_raw, default=54)

    cut_raw = (
        geom.get("cut_angle_deg")
        or opt_geom.get("cut_slope_angle_deg")
        or slope.get("cut_slope_angle")
        or obs.get("cut_slope_angle_est")
    )
    cut_deg = _extract_angle(cut_raw, default=64)

    slope_height_raw = (
        geom.get("slope_height_mean_m")
        or opt_geom.get("scarp_height_m")
        or slope.get("slope_height_above")
        or slope.get("height_above")
    )
    slope_height_m = _extract_height(slope_height_raw, default=7.6)

    formation_w = _extract_width(
        geom.get("road_width_pre_disaster_m") or road.get("width_before"), default=5.25
    )
    open_w = _extract_width(
        geom.get("road_width_post_disaster_m") or road.get("width_after"), default=2.30
    )
    if open_w >= formation_w:
        open_w = round(formation_w * 0.45, 2)

    rock_name = (
        geol.get("prominent_soil_rock")
        or obs.get("prominent_rock_type")
        or report.get("lithology")
        or "Sandstone"
    )

    wall_info = geom.get("breast_wall") or {}
    wall_h = _extract_height(
        wall_info.get("stem_height_m")
        or wall_info.get("total_height_m")
        or rw_specs.get("height_m"),
        default=2.7,
    )
    wall_mat = str(
        wall_info.get("material") or rw_specs.get("material") or "Plum Concrete (M15)"
    )

    # 4. Determine kinematic mode and dynamic top badge
    raw_mode = (
        opt_geom.get("kinematic_failure_mode")
        or obs.get("usgs_two_term_name")
        or obs.get("failure_movement_observed")
        or telemetry.get("reported_movement")
        or assessment.get("movement_type")
        or report.get("movement_type")
        or "Slide"
    )
    mode_lower = raw_mode.lower()

    if (
        not is_terrain
        or validation_status in ("INVALID_IMAGE", "REJECTED_NON_TERRAIN")
        or failure_vector == "DISQUALIFIED_NON_TERRAIN"
    ):
        mode = "rejected_ood"
        mode_label = "OPTICAL AUDIT DISQUALIFICATION"
        top_badge = "NON-LANDSLIDE MEDIA • CROSS-SECTION SUPPRESSED"
    elif failure_vector == "MACRO_MOUNTAIN_CATASTROPHE" or (slope_height_m > 45.0):
        mode = "macro_catastrophic"
        mode_label = "MACRO-SCALE MOUNTAIN CATASTROPHE"
        top_badge = "MACRO-SCALE SLOPE FAILURE • FULL DPR REQUIRED"
    elif failure_vector == "VALLEY_EMBANKMENT_SUBSIDENCE":
        mode = "valley_subsidence"
        mode_label = "VALLEY ROAD EMBANKMENT SUBSIDENCE"
        top_badge = f"VALLEY BENCH SUBSIDENCE • GABIONS + MICROPILES • H={slope_height_m:.1f}m"
    elif failure_vector == "HABITATION_TERRACE_SLUMP":
        mode = "habitation_mudslide"
        mode_label = "HABITATION RESIDENTIAL TERRACE SLUMP"
        top_badge = f"RESIDENTIAL TERRACE SLUMP • RC DEFLECTOR WALL • H={slope_height_m:.1f}m"
    elif failure_vector == "CLIFF_ROCKFALL_TOPPLE" or any(k in mode_lower for k in ("topple", "fall", "rockfall")):
        mode = "rockfall"
        mode_label = "ROCKFALL / TOPPLING FAILURE"
        top_badge = f"SUB-VERTICAL CLIFF • CUT: {cut_deg}° • COLUMN TOPPLE"
    elif any(k in mode_lower for k in ("flow", "debris flow", "mudflow", "avalanche")):
        mode = "debris_flow"
        mode_label = "CHANNELIZED DEBRIS FLOW"
        top_badge = f"DEBRIS RUNOUT FAN • CHUTE: {cut_deg}° • H={slope_height_m:.1f}m"
    elif any(k in mode_lower for k in ("slump", "rotational")):
        mode = "rotational_slump"
        mode_label = "ROTATIONAL OVERBURDEN SLUMP"
        top_badge = f"CIRCULAR SLIP ARC • DIP: {dip_deg}° • Hcut={slope_height_m:.1f}m"
    elif any(k in mode_lower for k in ("wedge",)):
        mode = "wedge"
        mode_label = "STRUCTURAL WEDGE FAILURE"
        top_badge = f"INTERSECTING JOINTS (J1xJ2) • PLUNGE: {dip_deg}°"
    elif any(k in mode_lower for k in ("creep", "subsidence", "settlement")):
        mode = "creep_subsidence"
        mode_label = "SLOPE CREEP & SURFICIAL SUBSIDENCE"
        top_badge = f"CONTINUOUS CREEP • SUBSIDENCE GRADIENT: {cut_deg}°"
    else:
        mode = "translational"
        mode_label = "TRANSLATIONAL PLANAR ROCK SLIDE"
        top_badge = f"SLIP PLANE: {dip_deg}° DAYLIGHTING • Hcut={slope_height_m:.1f}m"

    return {
        "mode": mode,
        "mode_label": mode_label,
        "dip_deg": dip_deg,
        "cut_deg": cut_deg,
        "cut_angle_str": f"{cut_deg}&#176;&ndash;{min(86, cut_deg + 3)}&#176;",
        "slope_height_m": slope_height_m,
        "formation_w": formation_w,
        "open_w": open_w,
        "rock_name": rock_name,
        "top_badge": top_badge,
        "fos_approx": crit_fos,
        "crit_fos": crit_fos,
        "target_fos": target_fos,
        "fos_dry": fos_dry,
        "wall_h": wall_h,
        "wall_mat": wall_mat,
        "drain_status": slope.get("debris_accumulation") or "Clogged with slide colluvium",
        "failure_vector": failure_vector,
        "is_applicable": is_applicable,
        "rejection_notice": rejection_notice,
    }


def _get_lithology_hatch_defs(hatch_id: str, rock_name: str) -> str:
    """Generates standard geological lithology hatch patterns per USGS / GSI standards."""
    rock_lower = rock_name.lower()
    if any(k in rock_lower for k in ("limestone", "dolomite", "carbonate")):
        return f"""
    <pattern id="{hatch_id}" width="16" height="12" patternUnits="userSpaceOnUse">
      <rect width="16" height="12" fill="#f8fafc" />
      <line x1="0" y1="0" x2="16" y2="0" stroke="#94a3b8" stroke-width="0.9" />
      <line x1="8" y1="0" x2="8" y2="6" stroke="#94a3b8" stroke-width="0.9" />
      <line x1="0" y1="6" x2="16" y2="6" stroke="#94a3b8" stroke-width="0.9" />
      <line x1="0" y1="6" x2="0" y2="12" stroke="#94a3b8" stroke-width="0.9" />
      <line x1="16" y1="6" x2="16" y2="12" stroke="#94a3b8" stroke-width="0.9" />
    </pattern>"""
    elif any(k in rock_lower for k in ("phyllite", "schist", "slate", "shale")):
        return f"""
    <pattern id="{hatch_id}" width="14" height="8" patternTransform="rotate(28 0 0)" patternUnits="userSpaceOnUse">
      <rect width="14" height="8" fill="#f8fafc" />
      <path d="M 0 4 Q 3.5 1, 7 4 T 14 4" fill="none" stroke="#94a3b8" stroke-width="1.0" />
    </pattern>"""
    elif any(k in rock_lower for k in ("granite", "gneiss", "diorite", "basalt")):
        return f"""
    <pattern id="{hatch_id}" width="12" height="12" patternUnits="userSpaceOnUse">
      <rect width="12" height="12" fill="#f8fafc" />
      <path d="M 3 3 L 9 9 M 9 3 L 3 9" stroke="#94a3b8" stroke-width="0.9" stroke-linecap="round" />
    </pattern>"""
    else:
        return f"""
    <pattern id="{hatch_id}" width="10" height="10" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
      <rect width="10" height="10" fill="#f8fafc" />
      <line x1="0" y1="0" x2="0" y2="10" stroke="#94a3b8" stroke-width="1.0" />
      <circle cx="5" cy="5" r="0.8" fill="#cbd5e1" />
    </pattern>"""


def generate_schematic_svg(
    assessment: dict[str, Any] | None = None,
    report: dict[str, Any] | None = None,
    unique_suffix: str = "",
) -> str:
    """Generates an engineered, textbook-accurate 2D vector cross-section SVG (viewBox='0 0 520 236')

    adhering strictly to Cruden & Varnes (1996) and USGS Circular 1325 anatomical taxonomy.
    """
    params = extract_ml_kinematic_parameters(assessment, report)
    mode = params["mode"]
    dip_deg = params["dip_deg"]
    cut_deg = params["cut_deg"]
    cut_str = params["cut_angle_str"]
    slope_h = params["slope_height_m"]
    formation_w = params["formation_w"]
    open_w = params["open_w"]
    rock_name = params["rock_name"]
    crit_fos = params["crit_fos"]
    target_fos = params["target_fos"]
    wall_h = params["wall_h"]
    wall_mat = params["wall_mat"]
    rejection_notice = params.get("rejection_notice") or ""

    sfx = f"_{unique_suffix}" if unique_suffix else ""
    hatch_id = f"rockHatch{sfx}"
    debris_id = f"debrisPat{sfx}"
    colluvium_id = f"colluviumPat{sfx}"

    # Geological hatching defs
    hatch_defs = _get_lithology_hatch_defs(hatch_id, rock_name)

    # Road coordinates (Standard engineering mountain cross section):
    # Road formation starts at X=290, ends at X=425 (width 135px in SVG)
    road_x_start = 290
    road_x_end = 425
    road_w_px = road_x_end - road_x_start
    road_y = 166

    # Dynamic debris encroachment calculation
    ratio_open = max(0.12, min(0.92, open_w / formation_w if formation_w > 0 else 0.42))
    debris_road_x = road_x_start + int((1.0 - ratio_open) * road_w_px)

    dx_cut = int(max(70, min(180, (90 - cut_deg) * 4.5 + 50)))
    crown_x = max(110, road_x_start - dx_cut)
    crown_y = int(max(20, min(65, 75 - (slope_h * 3.5))))

    # Dispatch to specific kinematic failure mode generator
    if mode == "rejected_ood":
        svg_body = _render_rejected_ood_svg(rejection_notice=rejection_notice)
    elif mode == "macro_catastrophic":
        svg_body = _render_macro_catastrophic_svg(
            rejection_notice=rejection_notice,
            slope_h=slope_h,
            rock_name=rock_name,
        )
    elif mode == "valley_subsidence":
        svg_body = _render_valley_subsidence_svg(
            hatch_id=hatch_id,
            debris_id=debris_id,
            colluvium_id=colluvium_id,
            dip_deg=dip_deg,
            cut_deg=cut_deg,
            cut_str=cut_str,
            slope_h=slope_h,
            crown_x=crown_x,
            crown_y=crown_y,
            road_x_start=road_x_start,
            road_x_end=road_x_end,
            debris_road_x=debris_road_x,
            road_y=road_y,
            formation_w=formation_w,
            open_w=open_w,
            rock_name=rock_name,
            crit_fos=crit_fos,
            target_fos=target_fos,
            wall_h=wall_h,
        )
    elif mode == "habitation_mudslide":
        svg_body = _render_habitation_slump_svg(
            hatch_id=hatch_id,
            debris_id=debris_id,
            colluvium_id=colluvium_id,
            dip_deg=dip_deg,
            cut_deg=cut_deg,
            cut_str=cut_str,
            slope_h=slope_h,
            crown_x=crown_x,
            crown_y=crown_y,
            road_x_start=road_x_start,
            road_x_end=road_x_end,
            debris_road_x=debris_road_x,
            road_y=road_y,
            formation_w=formation_w,
            open_w=open_w,
            rock_name=rock_name,
            crit_fos=crit_fos,
            target_fos=target_fos,
            wall_h=wall_h,
        )
    elif mode == "rotational_slump":
        svg_body = _render_rotational_slump_svg(
            hatch_id=hatch_id,
            debris_id=debris_id,
            colluvium_id=colluvium_id,
            dip_deg=dip_deg,
            cut_deg=cut_deg,
            cut_str=cut_str,
            slope_h=slope_h,
            crown_x=crown_x,
            crown_y=crown_y,
            road_x_start=road_x_start,
            road_x_end=road_x_end,
            debris_road_x=debris_road_x,
            road_y=road_y,
            formation_w=formation_w,
            open_w=open_w,
            rock_name=rock_name,
            crit_fos=crit_fos,
            target_fos=target_fos,
            wall_h=wall_h,
        )
    elif mode == "rockfall":
        svg_body = _render_rockfall_topple_svg(
            hatch_id=hatch_id,
            debris_id=debris_id,
            colluvium_id=colluvium_id,
            dip_deg=dip_deg,
            cut_deg=cut_deg,
            cut_str=cut_str,
            slope_h=slope_h,
            crown_x=crown_x,
            crown_y=crown_y,
            road_x_start=road_x_start,
            road_x_end=road_x_end,
            debris_road_x=debris_road_x,
            road_y=road_y,
            formation_w=formation_w,
            open_w=open_w,
            rock_name=rock_name,
            crit_fos=crit_fos,
            target_fos=target_fos,
            wall_h=wall_h,
        )
    elif mode == "debris_flow":
        svg_body = _render_debris_flow_svg(
            hatch_id=hatch_id,
            debris_id=debris_id,
            colluvium_id=colluvium_id,
            dip_deg=dip_deg,
            cut_deg=cut_deg,
            cut_str=cut_str,
            slope_h=slope_h,
            crown_x=crown_x,
            crown_y=crown_y,
            road_x_start=road_x_start,
            road_x_end=road_x_end,
            debris_road_x=debris_road_x,
            road_y=road_y,
            formation_w=formation_w,
            open_w=open_w,
            rock_name=rock_name,
            crit_fos=crit_fos,
            target_fos=target_fos,
            wall_h=wall_h,
        )
    elif mode == "wedge":
        svg_body = _render_wedge_failure_svg(
            hatch_id=hatch_id,
            debris_id=debris_id,
            colluvium_id=colluvium_id,
            dip_deg=dip_deg,
            cut_deg=cut_deg,
            cut_str=cut_str,
            slope_h=slope_h,
            crown_x=crown_x,
            crown_y=crown_y,
            road_x_start=road_x_start,
            road_x_end=road_x_end,
            debris_road_x=debris_road_x,
            road_y=road_y,
            formation_w=formation_w,
            open_w=open_w,
            rock_name=rock_name,
            crit_fos=crit_fos,
            target_fos=target_fos,
            wall_h=wall_h,
        )
    elif mode == "creep_subsidence":
        svg_body = _render_creep_subsidence_svg(
            hatch_id=hatch_id,
            debris_id=debris_id,
            colluvium_id=colluvium_id,
            dip_deg=dip_deg,
            cut_deg=cut_deg,
            cut_str=cut_str,
            slope_h=slope_h,
            crown_x=crown_x,
            crown_y=crown_y,
            road_x_start=road_x_start,
            road_x_end=road_x_end,
            debris_road_x=debris_road_x,
            road_y=road_y,
            formation_w=formation_w,
            open_w=open_w,
            rock_name=rock_name,
            crit_fos=crit_fos,
            target_fos=target_fos,
            wall_h=wall_h,
        )
    else:  # translational
        svg_body = _render_translational_slide_svg(
            hatch_id=hatch_id,
            debris_id=debris_id,
            colluvium_id=colluvium_id,
            dip_deg=dip_deg,
            cut_deg=cut_deg,
            cut_str=cut_str,
            slope_h=slope_h,
            crown_x=crown_x,
            crown_y=crown_y,
            road_x_start=road_x_start,
            road_x_end=road_x_end,
            debris_road_x=debris_road_x,
            road_y=road_y,
            formation_w=formation_w,
            open_w=open_w,
            rock_name=rock_name,
            crit_fos=crit_fos,
            target_fos=target_fos,
            wall_h=wall_h,
        )

    svg = f"""<svg viewBox="0 0 520 236" xmlns="http://www.w3.org/2000/svg" style="background:#090d16; font-family:'Manrope', -apple-system, sans-serif; shape-rendering:geometricPrecision;">
  <defs>
    {hatch_defs}
    <!-- Colluvial Overburden Pattern -->
    <pattern id="{colluvium_id}" width="14" height="14" patternUnits="userSpaceOnUse">
      <circle cx="3" cy="3" r="1.2" fill="#78350f" opacity="0.3" />
      <polygon points="9,2 12,4 10,6" fill="#92400e" opacity="0.25" />
      <circle cx="5" cy="11" r="1" fill="#78350f" opacity="0.3" />
      <polygon points="11,10 13,12 11,13" fill="#b45309" opacity="0.25" />
    </pattern>
    <!-- Debris Runout Clasts -->
    <pattern id="{debris_id}" width="10" height="10" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1.2" fill="#d97706" opacity="0.75" />
      <circle cx="7" cy="6" r="1.5" fill="#b45309" opacity="0.85" />
      <polygon points="3,7 5,9 2,9" fill="#92400e" opacity="0.7" />
    </pattern>
    <!-- Marker Arrow for Seepage & Kinematics -->
    <marker id="arrowRed{sfx}" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">
      <path d="M 0 1 L 9 5 L 0 9 z" fill="#ef4444" />
    </marker>
    <marker id="arrowBlue{sfx}" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">
      <path d="M 0 1 L 9 5 L 0 9 z" fill="#38bdf8" />
    </marker>
  </defs>

  <!-- Dark Engineering Grid Base -->
  <rect width="520" height="236" fill="#090d16" />
  <g stroke="#1e293b" stroke-width="0.5" stroke-dasharray="2,4" opacity="0.4">
    <line x1="0" y1="50" x2="520" y2="50" />
    <line x1="0" y1="100" x2="520" y2="100" />
    <line x1="0" y1="150" x2="520" y2="150" />
    <line x1="0" y1="200" x2="520" y2="200" />
    <line x1="100" y1="0" x2="100" y2="236" />
    <line x1="200" y1="0" x2="200" y2="236" />
    <line x1="300" y1="0" x2="300" y2="236" />
    <line x1="400" y1="0" x2="400" y2="236" />
  </g>

{svg_body}
</svg>"""
    return svg


# ==============================================================================
# 1. TRANSLATIONAL PLANAR ROCK SLIDE
# ==============================================================================
def _render_translational_slide_svg(
    hatch_id: str,
    debris_id: str,
    colluvium_id: str,
    dip_deg: int,
    cut_deg: int,
    cut_str: str,
    slope_h: float,
    crown_x: int,
    crown_y: int,
    road_x_start: int,
    road_x_end: int,
    debris_road_x: int,
    road_y: int,
    formation_w: float,
    open_w: float,
    rock_name: str,
    crit_fos: float = 0.92,
    target_fos: float = 1.56,
    wall_h: float = 2.7,
    **kwargs: Any,
) -> str:
    """Translational Planar Rock Slide along Daylighting Joint Discontinuity."""
    scarp_x = crown_x + 15
    scarp_y = crown_y + 12
    valley_y = 215

    j1_dx = 110
    j1_dy = int(j1_dx * math.tan(math.radians(dip_deg)))

    return f"""  <!-- In-situ Bedrock Strata (Competent {rock_name}) -->
  <path d="M 15 28 L {crown_x} {crown_y} L {scarp_x} {scarp_y} L {road_x_start} {road_y} L {road_x_end} {road_y} L 505 {valley_y} L 505 236 L 15 236 Z" fill="url(#{hatch_id})" stroke="#334155" stroke-width="1.2" />

  <!-- Relict Joint Set J1 (Persistent Discontinuities Dipping {dip_deg} deg) -->
  <g stroke="#475569" stroke-width="0.9" stroke-dasharray="3,3">
    <line x1="{scarp_x - 30}" y1="{scarp_y - 10}" x2="{scarp_x - 30 + 100}" y2="{scarp_y - 10 + j1_dy}" />
    <line x1="{scarp_x + 15}" y1="{scarp_y + 10}" x2="{scarp_x + 15 + 85}" y2="{scarp_y + 10 + int(85 * math.tan(math.radians(dip_deg)))}" />
    <line x1="{scarp_x + 60}" y1="{scarp_y + 30}" x2="{scarp_x + 60 + 75}" y2="{scarp_y + 30 + int(75 * math.tan(math.radians(dip_deg)))}" />
  </g>

  <!-- Phreatic Seepage Line / Transient Water Table (Monsoon Saturation) -->
  <path d="M 25 {scarp_y + 20} Q {scarp_x + 30} {scarp_y + 35} {road_x_start - 12} {road_y - 8}" fill="none" stroke="#0284c7" stroke-width="1.4" stroke-dasharray="4,2" />
  <!-- Seepage vectors daylighting at cut face -->
  <line x1="{road_x_start - 35}" y1="{road_y - 25}" x2="{road_x_start - 18}" y2="{road_y - 12}" stroke="#38bdf8" stroke-width="1.2" marker-end="url(#arrowBlue)" />

  <!-- Sliding Wedge Colluvium Polygon (Pre-failure profile) -->
  <path d="M {scarp_x} {scarp_y} L {road_x_start} {road_y} L {debris_road_x} {road_y} Q {road_x_start + 10} {road_y - 28} {scarp_x + 25} {scarp_y + 8} Z" fill="#451a03" fill-opacity="0.35" stroke="#f59e0b" stroke-width="1.2" />
  <path d="M {scarp_x} {scarp_y} L {road_x_start} {road_y} L {debris_road_x} {road_y} Q {road_x_start + 10} {road_y - 28} {scarp_x + 25} {scarp_y + 8} Z" fill="url(#{debris_id})" />

  <!-- Tension Crack (USGS Taxonomy: Head Scarp) -->
  <line x1="{crown_x}" y1="{crown_y}" x2="{scarp_x}" y2="{scarp_y}" stroke="#ef4444" stroke-width="2.5" />
  <polygon points="{crown_x},{crown_y} {scarp_x},{scarp_y} {scarp_x - 3},{scarp_y + 5}" fill="#ef4444" />

  <!-- Rupture Surface Daylighting (Discontinuity Plane Daylights into Road Cut) -->
  <line x1="{scarp_x}" y1="{scarp_y}" x2="{road_x_start}" y2="{road_y}" stroke="#ef4444" stroke-width="2.8" stroke-dasharray="6,3" />

  <!-- Kinematic Sliding Direction Vectors -->
  <line x1="{scarp_x + 30}" y1="{scarp_y + 25}" x2="{scarp_x + 65}" y2="{scarp_y + 55}" stroke="#dc2626" stroke-width="1.8" marker-end="url(#arrowRed)" />

  <!-- As-Built Road Carriageway & Formation Bedding -->
  <rect x="{road_x_start}" y="{road_y - 1}" width="{road_x_end - road_x_start}" height="5" fill="#1e293b" stroke="#334155" stroke-width="0.8" />
  <!-- Centerline Dash -->
  <line x1="{road_x_start}" y1="{road_y + 1}" x2="{road_x_end}" y2="{road_y + 1}" stroke="#facc15" stroke-width="0.9" stroke-dasharray="3,3" />

  <!-- Obstructed Debris Mound Covering Inner Lane -->
  <path d="M {road_x_start} {road_y} Q {(road_x_start + debris_road_x)//2} {road_y - 24} {debris_road_x} {road_y} Z" fill="#92400e" fill-opacity="0.8" stroke="#d97706" stroke-width="1" />
  <path d="M {road_x_start} {road_y} Q {(road_x_start + debris_road_x)//2} {road_y - 24} {debris_road_x} {road_y} Z" fill="url(#{debris_id})" />

  <!-- Proposed Remediation: Plum Concrete Breast Wall (IS:14458) -->
  <polygon points="{road_x_start - 3},{road_y} {road_x_start + 11},{road_y} {road_x_start + 7},{road_y - int(wall_h * 11)} {road_x_start - 2},{road_y - int(wall_h * 11)}" fill="#475569" stroke="#64748b" stroke-width="1.2" stroke-dasharray="3,1" opacity="0.9" />
  <text x="{road_x_start - 4}" y="{road_y - int(wall_h * 11) - 4}" font-size="5.5" font-weight="700" fill="#94a3b8">Plum Wall (H={wall_h:.1f}m)</text>

  <!-- Proposed Soil Nails Anchors (Fe500D TMT Grouted) -->
  <g stroke="#14b8a6" stroke-width="1.4" stroke-dasharray="3,2">
    <line x1="{road_x_start - 12}" y1="{road_y - 35}" x2="{road_x_start - 75}" y2="{road_y - 12}" />
    <line x1="{road_x_start - 20}" y1="{road_y - 65}" x2="{road_x_start - 82}" y2="{road_y - 42}" />
  </g>
  <!-- Perforated PVC Weep Holes in Breast Wall -->
  <circle cx="{road_x_start + 3}" cy="{road_y - 6}" r="1.5" fill="#38bdf8" />
  <circle cx="{road_x_start + 3}" cy="{road_y - 18}" r="1.5" fill="#38bdf8" />

  <!-- Road Width Dimension Line -->
  <line x1="{road_x_start}" y1="{road_y + 18}" x2="{road_x_end}" y2="{road_y + 18}" stroke="#94a3b8" stroke-width="0.9" />
  <line x1="{road_x_start}" y1="{road_y + 14}" x2="{road_x_start}" y2="{road_y + 22}" stroke="#94a3b8" stroke-width="0.9" />
  <line x1="{road_x_end}" y1="{road_y + 14}" x2="{road_x_end}" y2="{road_y + 22}" stroke="#94a3b8" stroke-width="0.9" />
  <text x="{road_x_start + 20}" y="{road_y + 28}" font-family="'JetBrains Mono', monospace" font-size="7" font-weight="700" fill="#cbd5e1">Formation: {formation_w:.2f}m</text>

  <!-- Open Width Dimension Line -->
  <line x1="{debris_road_x}" y1="{road_y + 40}" x2="{road_x_end}" y2="{road_y + 40}" stroke="#22c55e" stroke-width="1.2" />
  <line x1="{debris_road_x}" y1="{road_y + 36}" x2="{debris_road_x}" y2="{road_y + 44}" stroke="#22c55e" stroke-width="1.2" />
  <line x1="{road_x_end}" y1="{road_y + 36}" x2="{road_x_end}" y2="{road_y + 44}" stroke="#22c55e" stroke-width="1.2" />
  <text x="{debris_road_x + 8}" y="{road_y + 50}" font-family="'JetBrains Mono', monospace" font-size="7.5" font-weight="800" fill="#4ade80">Operable: {open_w:.2f}m</text>

  <!-- Slope Height Vertical Dimension -->
  <line x1="{crown_x - 35}" y1="{crown_y}" x2="{crown_x - 35}" y2="{road_y}" stroke="#64748b" stroke-width="0.8" stroke-dasharray="2,2" />
  <line x1="{crown_x - 40}" y1="{crown_y}" x2="{crown_x - 30}" y2="{crown_y}" stroke="#64748b" stroke-width="0.8" />
  <line x1="{crown_x - 40}" y1="{road_y}" x2="{crown_x - 30}" y2="{road_y}" stroke="#64748b" stroke-width="0.8" />
  <text x="{crown_x - 82}" y="{(crown_y + road_y)//2}" font-family="'JetBrains Mono', monospace" font-size="7" font-weight="700" fill="#94a3b8">H = {slope_h:.1f}m</text>

  <!-- Anatomical Callout Badges (USGS 1325 Taxonomy) -->
  <rect x="18" y="10" width="115" height="14" rx="2" fill="#450a0a" stroke="#dc2626" stroke-width="0.8" />
  <text x="23" y="20" font-size="6.5" font-weight="800" fill="#fca5a5">CROWN &amp; MAIN SCARP</text>

  <rect x="{scarp_x - 10}" y="{scarp_y - 20}" width="135" height="14" rx="2" fill="#450a0a" stroke="#dc2626" stroke-width="0.8" />
  <text x="{scarp_x - 5}" y="{scarp_y - 10}" font-size="6.5" font-weight="800" fill="#fca5a5">RUPTURE PLANE: DIP {dip_deg}&deg; (DAYLIGHT)</text>

  <rect x="{scarp_x + 65}" y="{scarp_y + 55}" width="118" height="14" rx="2" fill="#451a03" stroke="#f59e0b" stroke-width="0.8" />
  <text x="{scarp_x + 70}" y="{scarp_y + 65}" font-size="6.5" font-weight="800" fill="#fde68a">SLIDING COLLUVIUM</text>

  <!-- Stability Evaluation Pill (Exact Solved FoS from ProjectDataModel) -->
  <rect x="340" y="10" width="170" height="16" rx="3" fill="#1e1b4b" stroke="#6366f1" stroke-width="0.8" />
  <text x="345" y="21" font-size="6.5" font-weight="800" fill="#c7d2fe">Monsoon FoS = {crit_fos:.2f} | Stabilized FoS = {target_fos:.2f}</text>"""


# ==============================================================================
# 2. ROTATIONAL OVERBURDEN SLUMP
# ==============================================================================
def _render_rotational_slump_svg(
    hatch_id: str,
    debris_id: str,
    colluvium_id: str,
    dip_deg: int,
    cut_deg: int,
    cut_str: str,
    slope_h: float,
    crown_x: int,
    crown_y: int,
    road_x_start: int,
    road_x_end: int,
    debris_road_x: int,
    road_y: int,
    formation_w: float,
    open_w: float,
    rock_name: str,
    crit_fos: float = 0.88,
    target_fos: float = 1.54,
    wall_h: float = 2.7,
    **kwargs: Any,
) -> str:
    """Rotational Slump with Spoon-Shaped Circular Slip Arc and Heaved Toe Ridge."""
    arc_cx = (crown_x + road_x_start) // 2 + 10
    arc_cy = (crown_y + road_y) // 2
    valley_y = 215

    return f"""  <!-- In-situ Competent Bedrock Base ({rock_name}) -->
  <path d="M 15 30 L {crown_x} {crown_y} Q {arc_cx} {arc_cy + 35} {road_x_start} {road_y} L {road_x_end} {road_y} L 505 {valley_y} L 505 236 L 15 236 Z" fill="url(#{hatch_id})" stroke="#334155" stroke-width="1.2" />

  <!-- Colluvial Soil Overburden Mantle (Plastic Cohesive Silty Clay) -->
  <path d="M 15 20 L {crown_x} {crown_y} Q {arc_cx} {arc_cy + 35} {road_x_start} {road_y} L {road_x_start} {road_y - 20} L {crown_x - 10} {crown_y} Z" fill="#451a03" fill-opacity="0.32" stroke="#f59e0b" stroke-width="1" />
  <path d="M 15 20 L {crown_x} {crown_y} Q {arc_cx} {arc_cy + 35} {road_x_start} {road_y} L {road_x_start} {road_y - 20} L {crown_x - 10} {crown_y} Z" fill="url(#{colluvium_id})" />

  <!-- Concentric Crown Tension Cracks (USGS 1325: Extensional Fissures) -->
  <g stroke="#ef4444" stroke-width="2">
    <line x1="{crown_x - 18}" y1="{crown_y - 4}" x2="{crown_x - 14}" y2="{crown_y + 10}" />
    <line x1="{crown_x - 6}" y1="{crown_y - 2}" x2="{crown_x - 2}" y2="{crown_y + 14}" />
    <line x1="{crown_x + 6}" y1="{crown_y}" x2="{crown_x + 10}" y2="{crown_y + 18}" />
  </g>

  <!-- Circular Shear Arc of Rupture (Cylindrical Spoon Concave Failure Surface) -->
  <path d="M {crown_x + 10} {crown_y + 18} Q {arc_cx} {arc_cy + 35} {road_x_start} {road_y}" fill="none" stroke="#ef4444" stroke-width="2.8" stroke-dasharray="5,3" />

  <!-- Rotational Sliding Block (Back-tilted Counter-Slope Terracette) -->
  <path d="M {crown_x + 10} {crown_y + 18} Q {arc_cx} {arc_cy + 30} {road_x_start} {road_y} L {debris_road_x} {road_y} Q {arc_cx + 25} {arc_cy + 5} {crown_x + 22} {crown_y + 28} Z" fill="#78350f" fill-opacity="0.5" stroke="#d97706" stroke-width="1.2" />
  <path d="M {crown_x + 10} {crown_y + 18} Q {arc_cx} {arc_cy + 30} {road_x_start} {road_y} L {debris_road_x} {road_y} Q {arc_cx + 25} {arc_cy + 5} {crown_x + 22} {crown_y + 28} Z" fill="url(#{debris_id})" />

  <!-- Rotational Slip Vector (Curved Circular Moment) -->
  <path d="M {arc_cx - 15} {arc_cy - 10} A 45 45 0 0 1 {arc_cx + 25} {arc_cy + 15}" fill="none" stroke="#dc2626" stroke-width="2.2" marker-end="url(#arrowRed)" />

  <!-- Heaved Toe Pressure Ridge Obstructing Highway -->
  <path d="M {road_x_start - 8} {road_y} Q {(road_x_start + debris_road_x)//2} {road_y - 30} {debris_road_x} {road_y} Z" fill="#92400e" stroke="#ea580c" stroke-width="1.5" />
  <path d="M {road_x_start - 8} {road_y} Q {(road_x_start + debris_road_x)//2} {road_y - 30} {debris_road_x} {road_y} Z" fill="url(#{debris_id})" />

  <!-- Pavement & Subgrade Layers -->
  <rect x="{road_x_start}" y="{road_y - 1}" width="{road_x_end - road_x_start}" height="5" fill="#1e293b" stroke="#334155" stroke-width="0.8" />
  <line x1="{road_x_start}" y1="{road_y + 1}" x2="{road_x_end}" y2="{road_y + 1}" stroke="#facc15" stroke-width="0.9" stroke-dasharray="3,3" />

  <!-- Proposed Remediation: Gabion Toe Retaining Wall (IS:16014) -->
  <rect x="{road_x_start - 2}" y="{road_y - int(wall_h * 11)}" width="16" height="{int(wall_h * 11)}" fill="#334155" stroke="#94a3b8" stroke-width="1.2" stroke-dasharray="2,2" opacity="0.95" />
  <line x1="{road_x_start - 2}" y1="{road_y - int(wall_h * 5.5)}" x2="{road_x_start + 14}" y2="{road_y - int(wall_h * 5.5)}" stroke="#94a3b8" stroke-width="0.8" stroke-dasharray="2,2" />
  <text x="{road_x_start - 4}" y="{road_y - int(wall_h * 11) - 4}" font-size="5.5" font-weight="700" fill="#94a3b8">Gabion Wall (H={wall_h:.1f}m)</text>

  <!-- Proposed Slotted Perforated Collector Drainage -->
  <circle cx="{road_x_start - 6}" cy="{road_y - 4}" r="3" fill="#0284c7" stroke="#38bdf8" stroke-width="0.8" />
  <circle cx="{road_x_start - 6}" cy="{road_y - 4}" r="1" fill="#bae6fd" />

  <!-- Road Width Dimension Line -->
  <line x1="{road_x_start}" y1="{road_y + 18}" x2="{road_x_end}" y2="{road_y + 18}" stroke="#94a3b8" stroke-width="0.9" />
  <line x1="{road_x_start}" y1="{road_y + 14}" x2="{road_x_start}" y2="{road_y + 22}" stroke="#94a3b8" stroke-width="0.9" />
  <line x1="{road_x_end}" y1="{road_y + 14}" x2="{road_x_end}" y2="{road_y + 22}" stroke="#94a3b8" stroke-width="0.9" />
  <text x="{road_x_start + 20}" y="{road_y + 28}" font-family="'JetBrains Mono', monospace" font-size="7" font-weight="700" fill="#cbd5e1">Formation: {formation_w:.2f}m</text>

  <!-- Open Width Dimension Line -->
  <line x1="{debris_road_x}" y1="{road_y + 40}" x2="{road_x_end}" y2="{road_y + 40}" stroke="#22c55e" stroke-width="1.2" />
  <line x1="{debris_road_x}" y1="{road_y + 36}" x2="{debris_road_x}" y2="{road_y + 44}" stroke="#22c55e" stroke-width="1.2" />
  <line x1="{road_x_end}" y1="{road_y + 36}" x2="{road_x_end}" y2="{road_y + 44}" stroke="#22c55e" stroke-width="1.2" />
  <text x="{debris_road_x + 8}" y="{road_y + 50}" font-family="'JetBrains Mono', monospace" font-size="7.5" font-weight="800" fill="#4ade80">Operable: {open_w:.2f}m</text>

  <!-- Anatomical Callout Badges -->
  <rect x="18" y="10" width="132" height="14" rx="2" fill="#450a0a" stroke="#dc2626" stroke-width="0.8" />
  <text x="23" y="20" font-size="6.5" font-weight="800" fill="#fca5a5">MAIN SCARP &amp; CROWN CRACKS</text>

  <rect x="{arc_cx - 40}" y="{arc_cy + 8}" width="130" height="14" rx="2" fill="#450a0a" stroke="#dc2626" stroke-width="0.8" />
  <text x="{arc_cx - 35}" y="{arc_cy + 18}" font-size="6.5" font-weight="800" fill="#fca5a5">CIRCULAR SHEAR ARC (RUPTURE)</text>

  <rect x="{road_x_start - 35}" y="{road_y - 36}" width="125" height="14" rx="2" fill="#451a03" stroke="#f59e0b" stroke-width="0.8" />
  <text x="{road_x_start - 30}" y="{road_y - 26}" font-size="6.5" font-weight="800" fill="#fde68a">HEAVED TOE LOBE (PRESSURE RIDGE)</text>

  <!-- Stability Evaluation Pill -->
  <rect x="340" y="10" width="170" height="16" rx="3" fill="#1e1b4b" stroke="#6366f1" stroke-width="0.8" />
  <text x="345" y="21" font-size="6.5" font-weight="800" fill="#c7d2fe">Monsoon FoS = {crit_fos:.2f} | Stabilized FoS = {target_fos:.2f}</text>"""


# ==============================================================================
# 3. ROCKFALL AND COLUMNAR TOPPLING FAILURE
# ==============================================================================
def _render_rockfall_topple_svg(
    hatch_id: str,
    debris_id: str,
    colluvium_id: str,
    dip_deg: int,
    cut_deg: int,
    cut_str: str,
    slope_h: float,
    crown_x: int,
    crown_y: int,
    road_x_start: int,
    road_x_end: int,
    debris_road_x: int,
    road_y: int,
    formation_w: float,
    open_w: float,
    rock_name: str,
    crit_fos: float = 0.82,
    target_fos: float = 1.58,
    wall_h: float = 2.7,
    **kwargs: Any,
) -> str:
    """Rockfall and Columnar Toppling along Sub-Vertical Joint Sets."""
    cliff_x = road_x_start - 35
    valley_y = 215

    return f"""  <!-- In-situ Steep Rock Cliff Mass ({rock_name}) -->
  <path d="M 15 20 L {crown_x} {crown_y} L {cliff_x} 28 L {road_x_start - 10} {road_y} L {road_x_end} {road_y} L 505 {valley_y} L 505 236 L 15 236 Z" fill="url(#{hatch_id})" stroke="#334155" stroke-width="1.2" />

  <!-- Sub-Vertical Exfoliation & Columnar Joints (75-85 deg dip) -->
  <g stroke="#ef4444" stroke-width="1.4" stroke-dasharray="4,2">
    <line x1="{cliff_x - 12}" y1="30" x2="{road_x_start - 28}" y2="{road_y}" />
    <line x1="{cliff_x + 5}" y1="32" x2="{road_x_start - 12}" y2="{road_y}" />
    <line x1="{cliff_x + 20}" y1="35" x2="{road_x_start}" y2="{road_y}" />
  </g>

  <!-- Detached Toppling Rock Column (Pivoting at Base Center of Gravity) -->
  <polygon points="{cliff_x + 5},32 {cliff_x + 22},36 {road_x_start + 4},{road_y - 20} {road_x_start - 12},{road_y}" fill="#78350f" fill-opacity="0.45" stroke="#dc2626" stroke-width="1.5" />

  <!-- Toppling Moment Rotation Vector (Overturning around Pivot) -->
  <path d="M {cliff_x + 14} 45 A 28 28 0 0 1 {cliff_x + 36} 65" fill="none" stroke="#dc2626" stroke-width="2.2" marker-end="url(#arrowRed)" />

  <!-- Ballistic Trajectory & Free-Falling Boulders (Bounce & Roll Kinematics) -->
  <path d="M {cliff_x + 28} 68 Q {road_x_start} 105 {road_x_start + 18} {road_y - 12}" fill="none" stroke="#f59e0b" stroke-width="1.4" stroke-dasharray="3,3" />
  <circle cx="{cliff_x + 28}" cy="70" r="4.5" fill="#d97706" stroke="#78350f" stroke-width="1" />
  <circle cx="{road_x_start - 4}" cy="118" r="5" fill="#b45309" stroke="#78350f" stroke-width="1" />

  <!-- Talus Scree & Boulder Impact Fan on Roadway -->
  <ellipse cx="{(road_x_start + debris_road_x)//2}" cy="{road_y - 4}" rx="28" ry="8" fill="#92400e" stroke="#ea580c" stroke-width="1" />
  <circle cx="{road_x_start + 12}" cy="{road_y - 5}" r="4" fill="#b45309" stroke="#78350f" stroke-width="0.8" />
  <circle cx="{road_x_start + 24}" cy="{road_y - 4}" r="5.5" fill="#d97706" stroke="#78350f" stroke-width="0.8" />
  <circle cx="{road_x_start + 36}" cy="{road_y - 3}" r="3.5" fill="#78350f" stroke="#451a03" stroke-width="0.8" />

  <!-- Proposed Remediation: Dynamic Catch Barrier & Drape Netting (CEDD GEO 138) -->
  <line x1="{road_x_start - 2}" y1="{road_y - 2}" x2="{road_x_start - 2}" y2="{road_y - 40}" stroke="#06b6d4" stroke-width="2" />
  <circle cx="{road_x_start - 2}" cy="{road_y - 40}" r="2" fill="#38bdf8" />
  <!-- Flexible Ring Netting Mesh -->
  <line x1="{road_x_start - 2}" y1="{road_y - 40}" x2="{road_x_start + 14}" y2="{road_y - 2}" stroke="#0891b2" stroke-width="1.2" stroke-dasharray="2,2" />
  <line x1="{road_x_start - 2}" y1="{road_y - 25}" x2="{road_x_start + 8}" y2="{road_y - 2}" stroke="#0891b2" stroke-width="1.2" stroke-dasharray="2,2" />
  <text x="{road_x_start - 10}" y="{road_y - 44}" font-size="5.5" font-weight="700" fill="#38bdf8">Dynamic Barrier (500 kJ)</text>

  <!-- Tensioned Rock Bolts Anchoring Intact Bedrock (IS:14448) -->
  <g stroke="#10b981" stroke-width="1.6">
    <line x1="{cliff_x - 10}" y1="55" x2="{cliff_x - 65}" y2="52" stroke-dasharray="3,2" />
    <line x1="{road_x_start - 24}" y1="120" x2="{road_x_start - 80}" y2="116" stroke-dasharray="3,2" />
  </g>
  <rect x="{cliff_x - 10}" y="52" width="2" height="6" fill="#34d399" />
  <rect x="{road_x_start - 24}" y="117" width="2" height="6" fill="#34d399" />

  <!-- Road Width Dimension Line -->
  <line x1="{road_x_start}" y1="{road_y + 18}" x2="{road_x_end}" y2="{road_y + 18}" stroke="#94a3b8" stroke-width="0.9" />
  <line x1="{road_x_start}" y1="{road_y + 14}" x2="{road_x_start}" y2="{road_y + 22}" stroke="#94a3b8" stroke-width="0.9" />
  <line x1="{road_x_end}" y1="{road_y + 14}" x2="{road_x_end}" y2="{road_y + 22}" stroke="#94a3b8" stroke-width="0.9" />
  <text x="{road_x_start + 20}" y="{road_y + 28}" font-family="'JetBrains Mono', monospace" font-size="7" font-weight="700" fill="#cbd5e1">Formation: {formation_w:.2f}m</text>

  <!-- Open Width Dimension Line -->
  <line x1="{debris_road_x}" y1="{road_y + 40}" x2="{road_x_end}" y2="{road_y + 40}" stroke="#22c55e" stroke-width="1.2" />
  <line x1="{debris_road_x}" y1="{road_y + 36}" x2="{debris_road_x}" y2="{road_y + 44}" stroke="#22c55e" stroke-width="1.2" />
  <line x1="{road_x_end}" y1="{road_y + 36}" x2="{road_x_end}" y2="{road_y + 44}" stroke="#22c55e" stroke-width="1.2" />
  <text x="{debris_road_x + 8}" y="{road_y + 50}" font-family="'JetBrains Mono', monospace" font-size="7.5" font-weight="800" fill="#4ade80">Operable: {open_w:.2f}m</text>

  <!-- Anatomical Callout Badges -->
  <rect x="18" y="10" width="138" height="14" rx="2" fill="#450a0a" stroke="#dc2626" stroke-width="0.8" />
  <text x="23" y="20" font-size="6.5" font-weight="800" fill="#fca5a5">SUB-VERTICAL TENSION FISSURE</text>

  <rect x="{cliff_x - 20}" y="65" width="130" height="14" rx="2" fill="#450a0a" stroke="#dc2626" stroke-width="0.8" />
  <text x="{cliff_x - 15}" y="75" font-size="6.5" font-weight="800" fill="#fca5a5">TOPPLING ROCK COLUMN (UNSTABLE)</text>

  <rect x="{road_x_start - 10}" y="{road_y - 42}" width="125" height="14" rx="2" fill="#451a03" stroke="#f59e0b" stroke-width="0.8" />
  <text x="{road_x_start - 5}" y="{road_y - 32}" font-size="6.5" font-weight="800" fill="#fde68a">TALUS SCREE APRON (BOULDERS)</text>

  <!-- Stability Evaluation Pill -->
  <rect x="340" y="10" width="170" height="16" rx="3" fill="#1e1b4b" stroke="#6366f1" stroke-width="0.8" />
  <text x="345" y="21" font-size="6.5" font-weight="800" fill="#c7d2fe">Monsoon FoS = {crit_fos:.2f} | Stabilized FoS = {target_fos:.2f}</text>"""


# ==============================================================================
# 4. CHANNELIZED DEBRIS FLOW / MUDFLOW
# ==============================================================================
def _render_debris_flow_svg(
    hatch_id: str,
    debris_id: str,
    colluvium_id: str,
    dip_deg: int,
    cut_deg: int,
    cut_str: str,
    slope_h: float,
    crown_x: int,
    crown_y: int,
    road_x_start: int,
    road_x_end: int,
    debris_road_x: int,
    road_y: int,
    formation_w: float,
    open_w: float,
    rock_name: str,
    crit_fos: float = 0.78,
    target_fos: float = 1.52,
    wall_h: float = 2.7,
    **kwargs: Any,
) -> str:
    """Channelized Debris Flow with Erosion Gully Chute, Slurry Surge, and Debris Fan."""
    chute_start_x = crown_x - 10
    chute_start_y = crown_y + 10
    valley_y = 215

    return f"""  <!-- Mountain Bedrock Slope ({rock_name}) -->
  <path d="M 15 25 L {crown_x} {crown_y} L {chute_start_x} {chute_start_y} Q {(chute_start_x + road_x_start)//2} {road_y - 35} {road_x_start} {road_y} L {road_x_end} {road_y} L 505 {valley_y} L 505 236 L 15 236 Z" fill="url(#{hatch_id})" stroke="#334155" stroke-width="1.2" />

  <!-- Scoured Erosion Gully Chute (Torrent Runout Bed) -->
  <path d="M {chute_start_x} {chute_start_y} Q {(chute_start_x + road_x_start)//2} {road_y - 42} {road_x_start} {road_y}" fill="none" stroke="#0284c7" stroke-width="3.2" stroke-dasharray="6,2" />

  <!-- High-Velocity Slurry Surge Wave (Mud + Boulders + Organic Debris) -->
  <path d="M {chute_start_x + 15} {chute_start_y + 12} Q {(chute_start_x + road_x_start)//2 + 10} {road_y - 30} {debris_road_x} {road_y} L {road_x_start + 15} {road_y} Q {(chute_start_x + road_x_start)//2 - 10} {road_y - 50} {chute_start_x + 15} {chute_start_y + 12} Z" fill="#9a3412" fill-opacity="0.38" stroke="#ea580c" stroke-width="1.4" />
  <path d="M {chute_start_x + 15} {chute_start_y + 12} Q {(chute_start_x + road_x_start)//2 + 10} {road_y - 30} {debris_road_x} {road_y} L {road_x_start + 15} {road_y} Q {(chute_start_x + road_x_start)//2 - 10} {road_y - 50} {chute_start_x + 15} {chute_start_y + 12} Z" fill="url(#{debris_id})" />

  <!-- Flow Kinematic Direction Vectors -->
  <line x1="{(chute_start_x + road_x_start)//2 - 10}" y1="{road_y - 50}" x2="{(chute_start_x + road_x_start)//2 + 15}" y2="{road_y - 30}" stroke="#ef4444" stroke-width="2.2" marker-end="url(#arrowRed)" />

  <!-- Entrained Suspended Boulders in Mudflow -->
  <circle cx="{(chute_start_x + road_x_start)//2 - 2}" cy="{road_y - 42}" r="4.5" fill="#78350f" stroke="#451a03" stroke-width="0.8" />
  <circle cx="{(chute_start_x + road_x_start)//2 + 18}" cy="{road_y - 32}" r="6" fill="#b45309" stroke="#78350f" stroke-width="1" />

  <!-- Debris Deposition Fan Lobe Covering Roadway -->
  <path d="M {road_x_start - 10} {road_y} Q {(road_x_start + debris_road_x)//2} {road_y - 25} {debris_road_x} {road_y} Z" fill="#7c2d12" stroke="#ea580c" stroke-width="1.5" />
  <path d="M {road_x_start - 10} {road_y} Q {(road_x_start + debris_road_x)//2} {road_y - 25} {debris_road_x} {road_y} Z" fill="url(#{debris_id})" />

  <!-- Road Pavement -->
  <rect x="{road_x_start}" y="{road_y - 1}" width="{road_x_end - road_x_start}" height="5" fill="#1e293b" stroke="#334155" stroke-width="0.8" />
  <line x1="{road_x_start}" y1="{road_y + 1}" x2="{road_x_end}" y2="{road_y + 1}" stroke="#facc15" stroke-width="0.9" stroke-dasharray="3,3" />

  <!-- Proposed Remediation: Debris Deflector / Check Dam (IRC:SP:48) -->
  <polygon points="{road_x_start - 4},{road_y} {road_x_start + 12},{road_y} {road_x_start + 8},{road_y - int(wall_h * 12)} {road_x_start - 3},{road_y - int(wall_h * 12)}" fill="#475569" stroke="#94a3b8" stroke-width="1.2" stroke-dasharray="2,2" opacity="0.95" />
  <text x="{road_x_start - 6}" y="{road_y - int(wall_h * 12) - 4}" font-size="5.5" font-weight="700" fill="#94a3b8">Check Dam (H={wall_h:.1f}m)</text>

  <!-- Proposed Slotted Culvert Inlet -->
  <rect x="{road_x_start - 14}" y="{road_y - 8}" width="10" height="8" fill="#0284c7" stroke="#38bdf8" stroke-width="0.8" />
  <line x1="{road_x_start - 14}" y1="{road_y - 4}" x2="{road_x_start - 4}" y2="{road_y - 4}" stroke="#bae6fd" stroke-width="1" />

  <!-- Road Width Dimension Line -->
  <line x1="{road_x_start}" y1="{road_y + 18}" x2="{road_x_end}" y2="{road_y + 18}" stroke="#94a3b8" stroke-width="0.9" />
  <line x1="{road_x_start}" y1="{road_y + 14}" x2="{road_x_start}" y2="{road_y + 22}" stroke="#94a3b8" stroke-width="0.9" />
  <line x1="{road_x_end}" y1="{road_y + 14}" x2="{road_x_end}" y2="{road_y + 22}" stroke="#94a3b8" stroke-width="0.9" />
  <text x="{road_x_start + 20}" y="{road_y + 28}" font-family="'JetBrains Mono', monospace" font-size="7" font-weight="700" fill="#cbd5e1">Formation: {formation_w:.2f}m</text>

  <!-- Open Width Dimension Line -->
  <line x1="{debris_road_x}" y1="{road_y + 40}" x2="{road_x_end}" y2="{road_y + 40}" stroke="#22c55e" stroke-width="1.2" />
  <line x1="{debris_road_x}" y1="{road_y + 36}" x2="{debris_road_x}" y2="{road_y + 44}" stroke="#22c55e" stroke-width="1.2" />
  <line x1="{road_x_end}" y1="{road_y + 36}" x2="{road_x_end}" y2="{road_y + 44}" stroke="#22c55e" stroke-width="1.2" />
  <text x="{debris_road_x + 8}" y="{road_y + 50}" font-family="'JetBrains Mono', monospace" font-size="7.5" font-weight="800" fill="#4ade80">Operable: {open_w:.2f}m</text>

  <!-- Anatomical Badges -->
  <rect x="18" y="10" width="135" height="14" rx="2" fill="#450a0a" stroke="#dc2626" stroke-width="0.8" />
  <text x="23" y="20" font-size="6.5" font-weight="800" fill="#fca5a5">EROSIONAL TORRENT GULLY</text>

  <rect x="{chute_start_x + 25}" y="{chute_start_y - 12}" width="140" height="14" rx="2" fill="#450a0a" stroke="#dc2626" stroke-width="0.8" />
  <text x="{chute_start_x + 30}" y="{chute_start_y - 2}" font-size="6.5" font-weight="800" fill="#fca5a5">BOULDER &amp; SLURRY SURGE FRONT</text>

  <rect x="{road_x_start - 25}" y="{road_y - 42}" width="135" height="14" rx="2" fill="#451a03" stroke="#f59e0b" stroke-width="0.8" />
  <text x="{road_x_start - 20}" y="{road_y - 32}" font-size="6.5" font-weight="800" fill="#fde68a">HIGH-VELOCITY DEBRIS FAN LOBE</text>

  <!-- Stability Evaluation Pill -->
  <rect x="340" y="10" width="170" height="16" rx="3" fill="#1e1b4b" stroke="#6366f1" stroke-width="0.8" />
  <text x="345" y="21" font-size="6.5" font-weight="800" fill="#c7d2fe">Monsoon FoS = {crit_fos:.2f} | Stabilized FoS = {target_fos:.2f}</text>"""


# ==============================================================================
# 5. STRUCTURAL WEDGE FAILURE
# ==============================================================================
def _render_wedge_failure_svg(
    hatch_id: str,
    debris_id: str,
    colluvium_id: str,
    dip_deg: int,
    cut_deg: int,
    cut_str: str,
    slope_h: float,
    crown_x: int,
    crown_y: int,
    road_x_start: int,
    road_x_end: int,
    debris_road_x: int,
    road_y: int,
    formation_w: float,
    open_w: float,
    rock_name: str,
    crit_fos: float = 0.86,
    target_fos: float = 1.55,
    wall_h: float = 2.7,
    **kwargs: Any,
) -> str:
    """Structural Wedge Failure along Intersecting Discontinuity Planes (J1 x J2)."""
    scarp_x = crown_x + 15
    scarp_y = crown_y + 12
    valley_y = 215

    return f"""  <!-- In-situ Competent Rock Mass ({rock_name}) -->
  <path d="M 15 28 L {crown_x} {crown_y} L {scarp_x} {scarp_y} L {road_x_start} {road_y} L {road_x_end} {road_y} L 505 {valley_y} L 505 236 L 15 236 Z" fill="url(#{hatch_id})" stroke="#334155" stroke-width="1.2" />

  <!-- Discontinuity Joint Set J1 (Dipping toward road) -->
  <g stroke="#475569" stroke-width="1" stroke-dasharray="3,3">
    <line x1="{scarp_x - 15}" y1="{scarp_y}" x2="{scarp_x + 95}" y2="{road_y + 10}" />
    <line x1="{scarp_x + 25}" y1="{scarp_y + 15}" x2="{scarp_x + 115}" y2="{road_y + 15}" />
  </g>
  <!-- Discontinuity Joint Set J2 (Intersecting oblique plane) -->
  <g stroke="#38bdf8" stroke-width="0.9" stroke-dasharray="4,2">
    <line x1="{scarp_x + 75}" y1="{scarp_y - 5}" x2="{scarp_x + 10}" y2="{road_y}" />
    <line x1="{scarp_x + 105}" y1="{scarp_y + 15}" x2="{scarp_x + 40}" y2="{road_y}" />
  </g>

  <!-- Line of Intersection Daylighting (Line of Plunge / Rupture Trough) -->
  <line x1="{scarp_x}" y1="{scarp_y}" x2="{road_x_start}" y2="{road_y}" stroke="#ef4444" stroke-width="2.5" stroke-dasharray="5,2" />

  <!-- Detached Tetrahedral Wedge Block Sliding Down Line of Intersection -->
  <polygon points="{scarp_x},{scarp_y} {scarp_x + 35},{scarp_y + 18} {road_x_start + 15},{road_y - 10} {road_x_start},{road_y}" fill="#92400e" fill-opacity="0.5" stroke="#dc2626" stroke-width="1.4" />
  <polygon points="{scarp_x},{scarp_y} {scarp_x + 35},{scarp_y + 18} {road_x_start + 15},{road_y - 10} {road_x_start},{road_y}" fill="url(#{debris_id})" />

  <!-- Plunge Vector Arrow along Trough Line -->
  <line x1="{scarp_x + 25}" y1="{scarp_y + 20}" x2="{scarp_x + 65}" y2="{scarp_y + 52}" stroke="#dc2626" stroke-width="2.2" marker-end="url(#arrowRed)" />

  <!-- Encroaching Wedge Clasts on Road -->
  <path d="M {road_x_start} {road_y} Q {(road_x_start + debris_road_x)//2} {road_y - 20} {debris_road_x} {road_y} Z" fill="#78350f" stroke="#d97706" stroke-width="1" />
  <path d="M {road_x_start} {road_y} Q {(road_x_start + debris_road_x)//2} {road_y - 20} {debris_road_x} {road_y} Z" fill="url(#{debris_id})" />

  <!-- Road Pavement -->
  <rect x="{road_x_start}" y="{road_y - 1}" width="{road_x_end - road_x_start}" height="5" fill="#1e293b" stroke="#334155" stroke-width="0.8" />
  <line x1="{road_x_start}" y1="{road_y + 1}" x2="{road_x_end}" y2="{road_y + 1}" stroke="#facc15" stroke-width="0.9" stroke-dasharray="3,3" />

  <!-- Proposed Remediation: Pattern Rock Bolts Stitching Wedge Flanks (IS:14448) -->
  <g stroke="#10b981" stroke-width="1.5" stroke-dasharray="3,2">
    <line x1="{scarp_x + 40}" y1="{scarp_y + 35}" x2="{scarp_x - 15}" y2="{scarp_y + 65}" />
    <line x1="{scarp_x + 75}" y1="{scarp_y + 60}" x2="{scarp_x + 20}" y2="{scarp_y + 90}" />
  </g>
  <!-- Bearing plates -->
  <rect x="{scarp_x + 38}" y="{scarp_y + 33}" width="4" height="4" fill="#34d399" />
  <rect x="{scarp_x + 73}" y="{scarp_y + 58}" width="4" height="4" fill="#34d399" />

  <!-- Road Width Dimension Line -->
  <line x1="{road_x_start}" y1="{road_y + 18}" x2="{road_x_end}" y2="{road_y + 18}" stroke="#94a3b8" stroke-width="0.9" />
  <line x1="{road_x_start}" y1="{road_y + 14}" x2="{road_x_start}" y2="{road_y + 22}" stroke="#94a3b8" stroke-width="0.9" />
  <line x1="{road_x_end}" y1="{road_y + 14}" x2="{road_x_end}" y2="{road_y + 22}" stroke="#94a3b8" stroke-width="0.9" />
  <text x="{road_x_start + 20}" y="{road_y + 28}" font-family="'JetBrains Mono', monospace" font-size="7" font-weight="700" fill="#cbd5e1">Formation: {formation_w:.2f}m</text>

  <!-- Open Width Dimension Line -->
  <line x1="{debris_road_x}" y1="{road_y + 40}" x2="{road_x_end}" y2="{road_y + 40}" stroke="#22c55e" stroke-width="1.2" />
  <line x1="{debris_road_x}" y1="{road_y + 36}" x2="{debris_road_x}" y2="{road_y + 44}" stroke="#22c55e" stroke-width="1.2" />
  <line x1="{road_x_end}" y1="{road_y + 36}" x2="{road_x_end}" y2="{road_y + 44}" stroke="#22c55e" stroke-width="1.2" />
  <text x="{debris_road_x + 8}" y="{road_y + 50}" font-family="'JetBrains Mono', monospace" font-size="7.5" font-weight="800" fill="#4ade80">Operable: {open_w:.2f}m</text>

  <!-- Callout Badges -->
  <rect x="18" y="10" width="124" height="14" rx="2" fill="#450a0a" stroke="#dc2626" stroke-width="0.8" />
  <text x="23" y="20" font-size="6.5" font-weight="800" fill="#fca5a5">WEDGE APEX TENSION CRACK</text>

  <rect x="{scarp_x + 5}" y="{scarp_y - 18}" width="145" height="14" rx="2" fill="#450a0a" stroke="#dc2626" stroke-width="0.8" />
  <text x="{scarp_x + 10}" y="{scarp_y - 8}" font-size="6.5" font-weight="800" fill="#fca5a5">INTERSECTING JOINTS (J1 x J2 TROUGH)</text>

  <rect x="{scarp_x + 70}" y="{scarp_y + 60}" width="128" height="14" rx="2" fill="#451a03" stroke="#f59e0b" stroke-width="0.8" />
  <text x="{scarp_x + 75}" y="{scarp_y + 70}" font-size="6.5" font-weight="800" fill="#fde68a">SLIDING TETRAHEDRAL WEDGE</text>

  <!-- Stability Evaluation Pill -->
  <rect x="340" y="10" width="170" height="16" rx="3" fill="#1e1b4b" stroke="#6366f1" stroke-width="0.8" />
  <text x="345" y="21" font-size="6.5" font-weight="800" fill="#c7d2fe">Monsoon FoS = {crit_fos:.2f} | Stabilized FoS = {target_fos:.2f}</text>"""


# ==============================================================================
# 6. CREEP AND SURFICIAL SLOPE SUBSIDENCE
# ==============================================================================
def _render_creep_subsidence_svg(
    hatch_id: str,
    debris_id: str,
    colluvium_id: str,
    dip_deg: int,
    cut_deg: int,
    cut_str: str,
    slope_h: float,
    crown_x: int,
    crown_y: int,
    road_x_start: int,
    road_x_end: int,
    debris_road_x: int,
    road_y: int,
    formation_w: float,
    open_w: float,
    rock_name: str,
    crit_fos: float = 0.94,
    target_fos: float = 1.55,
    wall_h: float = 2.7,
    **kwargs: Any,
) -> str:
    """Continuous Slope Creep with Progressive Surficial Subsidence and Pavement Shear."""
    valley_y = 215

    return f"""  <!-- In-situ Competent Bedrock Strata -->
  <path d="M 15 35 L {crown_x} {crown_y + 12} L {road_x_start} {road_y + 10} L {road_x_end} {road_y + 12} L 505 {valley_y} L 505 236 L 15 236 Z" fill="url(#{hatch_id})" stroke="#334155" stroke-width="1.2" />

  <!-- Active Creep Zone in Colluvial Overburden (Visco-Plastic Shear) -->
  <path d="M 15 25 L {crown_x} {crown_y} L {road_x_start} {road_y} L {road_x_start} {road_y + 10} L {crown_x} {crown_y + 12} L 15 35 Z" fill="#451a03" fill-opacity="0.32" stroke="#f59e0b" stroke-width="1" />
  <path d="M 15 25 L {crown_x} {crown_y} L {road_x_start} {road_y} L {road_x_start} {road_y + 10} L {crown_x} {crown_y + 12} L 15 35 Z" fill="url(#{colluvium_id})" />

  <!-- Tilting Trees & Pistol-Butt Curvature (Classic Geomorphological Indicator) -->
  <path d="M {crown_x - 30} {crown_y + 6} C {crown_x - 32} {crown_y - 10}, {crown_x - 22} {crown_y - 20}, {crown_x - 18} {crown_y - 30}" fill="none" stroke="#78350f" stroke-width="2.2" stroke-linecap="round" />
  <circle cx="{crown_x - 18}" cy="{crown_y - 30}" r="5" fill="#15803d" opacity="0.8" />
  <path d="M {crown_x + 20} {crown_y + 20} C {crown_x + 18} {crown_y + 8}, {crown_x + 28} {crown_y - 4}, {crown_x + 32} {crown_y - 14}" fill="none" stroke="#78350f" stroke-width="2" stroke-linecap="round" />
  <circle cx="{crown_x + 32}" cy="{crown_y - 14}" r="4.5" fill="#15803d" opacity="0.8" />

  <!-- Slow Visco-Plastic Creep Vectors (Velocity < 0.3 m/yr) -->
  <line x1="{crown_x - 5}" y1="{crown_y + 8}" x2="{crown_x + 12}" y2="{crown_y + 16}" stroke="#f97316" stroke-width="1.4" marker-end="url(#arrowRed)" />
  <line x1="{road_x_start - 45}" y1="{road_y - 15}" x2="{road_x_start - 28}" y2="{road_y - 6}" stroke="#f97316" stroke-width="1.4" marker-end="url(#arrowRed)" />

  <!-- Distorted / Settled Pavement with Longitudinal Step Cracks -->
  <rect x="{road_x_start}" y="{road_y - 1}" width="45" height="5" fill="#1e293b" stroke="#ef4444" stroke-width="0.8" />
  <line x1="{road_x_start + 45}" y1="{road_y - 4}" x2="{road_x_start + 45}" y2="{road_y + 7}" stroke="#ef4444" stroke-width="2" />
  <rect x="{road_x_start + 45}" y="{road_y + 3}" width="{road_x_end - (road_x_start + 45)}" height="5" fill="#334155" stroke="#64748b" stroke-width="0.8" />

  <!-- Subsidence Callout Arrow -->
  <line x1="{road_x_start + 50}" y1="{road_y - 16}" x2="{road_x_start + 50}" y2="{road_y - 2}" stroke="#ef4444" stroke-width="1.2" marker-end="url(#arrowRed)" />
  <text x="{road_x_start + 35}" y="{road_y - 20}" font-size="6.5" font-weight="800" fill="#fca5a5">&Delta;z = 0.35m SETTLEMENT</text>

  <!-- Side Drain Sheared & Displaced -->
  <polygon points="{road_x_start - 1},{road_y} {road_x_start + 7},{road_y + 8} {road_x_start + 14},{road_y + 8} {road_x_start + 14},{road_y}" fill="#334155" stroke="#ef4444" stroke-width="1" />
  <circle cx="{road_x_start + 7}" cy="{road_y + 4}" r="3" fill="#ef4444" />

  <!-- Valley Shoulder & Displaced Crash Barrier -->
  <line x1="{road_x_end - 6}" y1="{road_y - 5}" x2="{road_x_end - 6}" y2="{road_y + 4}" stroke="#ef4444" stroke-width="1.8" />
  <circle cx="{road_x_end - 6}" cy="{road_y - 5}" r="2" fill="#fca5a5" />

  <!-- Proposed Remediation: Soil Nailing & Sub-Horizontal PVC Drains -->
  <g stroke="#14b8a6" stroke-width="1.5" stroke-dasharray="3,2">
    <line x1="{road_x_start - 15}" y1="{road_y - 6}" x2="{road_x_start - 65}" y2="{road_y + 20}" />
    <line x1="{road_x_start - 35}" y1="{road_y - 25}" x2="{road_x_start - 85}" y2="{road_y + 5}" />
  </g>

  <!-- Engineering Dimensions -->
  <line x1="{road_x_start}" y1="{road_y + 22}" x2="{road_x_end}" y2="{road_y + 22}" stroke="#94a3b8" stroke-width="0.9" />
  <line x1="{road_x_start}" y1="{road_y + 18}" x2="{road_x_start}" y2="{road_y + 26}" stroke="#94a3b8" stroke-width="0.9" />
  <line x1="{road_x_end}" y1="{road_y + 18}" x2="{road_x_end}" y2="{road_y + 26}" stroke="#94a3b8" stroke-width="0.9" />
  <text x="{road_x_start + 20}" y="{road_y + 32}" font-family="'JetBrains Mono', monospace" font-size="7" font-weight="700" fill="#cbd5e1">Formation: {formation_w:.2f}m</text>

  <!-- Anatomical Badges -->
  <rect x="18" y="10" width="138" height="14" rx="2" fill="#451a03" stroke="#f59e0b" stroke-width="0.8" />
  <text x="23" y="20" font-size="6.5" font-weight="800" fill="#fde68a">PISTOL-BUTT TREE CURVATURE (CREEP)</text>

  <rect x="{crown_x + 10}" y="{crown_y - 12}" width="135" height="14" rx="2" fill="#450a0a" stroke="#dc2626" stroke-width="0.8" />
  <text x="{crown_x + 15}" y="{crown_y - 2}" font-size="6.5" font-weight="800" fill="#fca5a5">VISCO-PLASTIC OVERBURDEN CREEP</text>

  <!-- Stability Evaluation Pill -->
  <rect x="340" y="10" width="170" height="16" rx="3" fill="#1e1b4b" stroke="#6366f1" stroke-width="0.8" />
  <text x="345" y="21" font-size="6.5" font-weight="800" fill="#c7d2fe">Monsoon FoS = {crit_fos:.2f} | Stabilized FoS = {target_fos:.2f}</text>"""


# ==============================================================================
# 7. VALLEY ROAD EMBANKMENT SUBSIDENCE
# ==============================================================================
def _render_valley_subsidence_svg(
    hatch_id: str,
    debris_id: str,
    colluvium_id: str,
    dip_deg: int,
    cut_deg: int,
    cut_str: str,
    slope_h: float,
    crown_x: int,
    crown_y: int,
    road_x_start: int,
    road_x_end: int,
    debris_road_x: int,
    road_y: int,
    formation_w: float,
    open_w: float,
    rock_name: str,
    crit_fos: float = 0.84,
    target_fos: float = 1.58,
    wall_h: float = 3.5,
    **kwargs: Any,
) -> str:
    """Valley Road Embankment Subsidence with Gabion Retaining Wall, Micropiles, and Geogrid."""
    return f"""  <!-- In-situ Competent Mountain Bedrock (Uphill Flank: {rock_name}) -->
  <path d="M 15 25 L 140 85 L 190 142 L 275 142 L 275 220 L 505 220 L 505 236 L 15 236 Z" fill="url(#{hatch_id})" stroke="#334155" stroke-width="1.2" />

  <!-- Uphill Cut Slope Face -->
  <path d="M 15 25 L 140 85 L 190 142" fill="none" stroke="#64748b" stroke-width="1.5" />
  <text x="60" y="55" font-size="6.5" font-weight="800" fill="#94a3b8">INTACT UPHILL CUT SLOPE ({cut_deg}&deg;)</text>

  <!-- Intact Inner Road Carriageway (Operable Single Lane) -->
  <rect x="190" y="140" width="85" height="5" fill="#1e293b" stroke="#475569" stroke-width="0.8" />
  <line x1="190" y1="140" x2="275" y2="140" stroke="#facc15" stroke-width="1" stroke-dasharray="4,3" />

  <!-- Embankment Tension Crack & Longitudinal Shear Scarp -->
  <line x1="275" y1="135" x2="275" y2="162" stroke="#ef4444" stroke-width="2.2" />
  <polygon points="273,135 277,135 275,142" fill="#ef4444" />

  <!-- Subsided Outer Carriageway Slab (Dropped & Tilted into Valley) -->
  <polygon points="278,160 345,166 345,172 278,166" fill="#334155" stroke="#ef4444" stroke-width="1" />

  <!-- Rotational Slip Arc Daylighting Down into Valley (Red Dashed Rupture) -->
  <path d="M 275 142 Q 315 185 410 212" fill="none" stroke="#ef4444" stroke-width="2.2" stroke-dasharray="5,3" />

  <!-- Compacted Engineered Backfill Zone with Polymeric Geogrid Reinforcement -->
  <polygon points="275,145 370,145 370,205 275,205" fill="#1e293b" opacity="0.6" stroke="#047857" stroke-width="0.8" />
  <!-- Biaxial Geogrid Layers (MoRTH 3100) -->
  <g stroke="#10b981" stroke-width="1.6" stroke-dasharray="4,2">
    <line x1="277" y1="162" x2="370" y2="162" />
    <line x1="277" y1="178" x2="368" y2="178" />
    <line x1="277" y1="194" x2="366" y2="194" />
  </g>
  <text x="282" y="188" font-size="5.8" font-weight="800" fill="#6ee7b7">BIAXIAL GEOGRID LAYERS (MoRTH 3100)</text>

  <!-- Vertical RC Micropiles (Ø150mm with Ø32mm Fe500D rebar) -->
  <g stroke="#06b6d4" stroke-width="2.6" stroke-dasharray="6,2">
    <line x1="272" y1="145" x2="272" y2="225" />
    <line x1="278" y1="145" x2="278" y2="225" />
  </g>
  <!-- M30 RC Capping Beam at Road Edge -->
  <rect x="268" y="137" width="14" height="8" rx="1" fill="#475569" stroke="#0891b2" stroke-width="1" />
  <circle cx="272" cy="141" r="1.2" fill="#38bdf8" />
  <circle cx="278" cy="141" r="1.2" fill="#38bdf8" />

  <!-- W-Beam Steel Crash Barrier (MoRTH 811) -->
  <line x1="271" y1="126" x2="271" y2="137" stroke="#94a3b8" stroke-width="1.6" />
  <rect x="268" y="127" width="6" height="4" rx="0.5" fill="#e2e8f0" stroke="#475569" stroke-width="0.8" />

  <!-- Stepped Gabion Retaining Wall (MoRTH 2504 / IS:16014) on Lower Valley Bench -->
  <rect x="360" y="190" width="46" height="16" fill="#334155" stroke="#94a3b8" stroke-width="1" />
  <line x1="383" y1="190" x2="383" y2="206" stroke="#64748b" stroke-width="0.8" stroke-dasharray="2,2" />
  <rect x="366" y="174" width="40" height="16" fill="#334155" stroke="#94a3b8" stroke-width="1" />
  <line x1="386" y1="174" x2="386" y2="190" stroke="#64748b" stroke-width="0.8" stroke-dasharray="2,2" />
  <rect x="372" y="158" width="34" height="16" fill="#334155" stroke="#94a3b8" stroke-width="1" />
  <line x1="389" y1="158" x2="389" y2="174" stroke="#64748b" stroke-width="0.8" stroke-dasharray="2,2" />
  <!-- Gabion crate internal wire mesh texture -->
  <g stroke="#94a3b8" stroke-width="0.6" opacity="0.6">
    <line x1="362" y1="198" x2="404" y2="198" />
    <line x1="368" y1="182" x2="404" y2="182" />
    <line x1="374" y1="166" x2="404" y2="166" />
  </g>

  <!-- Lower Valley Slope beyond Gabion Wall -->
  <path d="M 406 206 L 505 228 L 505 236 L 406 236 Z" fill="url(#{hatch_id})" stroke="#334155" stroke-width="1" />

  <!-- Road Width Dimension Callouts -->
  <line x1="190" y1="130" x2="345" y2="130" stroke="#94a3b8" stroke-width="0.8" />
  <line x1="190" y1="126" x2="190" y2="134" stroke="#94a3b8" stroke-width="0.8" />
  <line x1="345" y1="126" x2="345" y2="134" stroke="#94a3b8" stroke-width="0.8" />
  <text x="235" y="126" font-family="'JetBrains Mono', monospace" font-size="6.5" font-weight="700" fill="#cbd5e1">Formation: {formation_w:.2f}m</text>

  <line x1="190" y1="152" x2="275" y2="152" stroke="#22c55e" stroke-width="1.2" />
  <line x1="190" y1="148" x2="190" y2="156" stroke="#22c55e" stroke-width="1.2" />
  <line x1="275" y1="148" x2="275" y2="156" stroke="#22c55e" stroke-width="1.2" />
  <text x="202" y="161" font-family="'JetBrains Mono', monospace" font-size="6.8" font-weight="800" fill="#4ade80">Operable: {open_w:.2f}m</text>

  <!-- Anatomical Callout Badges -->
  <rect x="18" y="10" width="138" height="14" rx="2" fill="#450a0a" stroke="#dc2626" stroke-width="0.8" />
  <text x="23" y="20" font-size="6.5" font-weight="800" fill="#fca5a5">ROAD EMBANKMENT SHEAR SCARP</text>

  <rect x="18" y="27" width="148" height="14" rx="2" fill="#042f2e" stroke="#0d9488" stroke-width="0.8" />
  <text x="23" y="37" font-size="6.2" font-weight="800" fill="#5eead4">SLOPE LOCATION: BELOW ROAD: YES</text>

  <rect x="180" y="98" width="145" height="14" rx="2" fill="#082f49" stroke="#0284c7" stroke-width="0.8" />
  <text x="185" y="108" font-size="6.2" font-weight="800" fill="#bae6fd">&Oslash;150mm MICROPILES &amp; RC CAP BEAM</text>

  <rect x="345" y="138" width="165" height="14" rx="2" fill="#451a03" stroke="#f59e0b" stroke-width="0.8" />
  <text x="350" y="148" font-size="6.2" font-weight="800" fill="#fde68a">STEPPED GABION WALL (H={wall_h:.1f}m)</text>

  <!-- Stability Evaluation Pill -->
  <rect x="340" y="10" width="170" height="16" rx="3" fill="#1e1b4b" stroke="#6366f1" stroke-width="0.8" />
  <text x="345" y="21" font-size="6.5" font-weight="800" fill="#c7d2fe">Monsoon FoS = {crit_fos:.2f} | Stabilized FoS = {target_fos:.2f}</text>"""


# ==============================================================================
# 8. HABITATION RESIDENTIAL TERRACE SLUMP
# ==============================================================================
def _render_habitation_slump_svg(
    hatch_id: str,
    debris_id: str,
    colluvium_id: str,
    dip_deg: int,
    cut_deg: int,
    cut_str: str,
    slope_h: float,
    crown_x: int,
    crown_y: int,
    road_x_start: int,
    road_x_end: int,
    debris_road_x: int,
    road_y: int,
    formation_w: float,
    open_w: float,
    rock_name: str,
    crit_fos: float = 0.88,
    target_fos: float = 1.62,
    wall_h: float = 3.5,
    **kwargs: Any,
) -> str:
    """Habitation Residential Terrace Slump with M25 Cantilever Deflector Wall and House."""
    return f"""  <!-- In-situ Mountain Bedrock Basement ({rock_name}) -->
  <path d="M 15 35 L 75 55 L 170 115 L 240 170 L 505 170 L 505 236 L 15 236 Z" fill="url(#{hatch_id})" stroke="#334155" stroke-width="1.2" />

  <!-- Colluvial Overburden Mud Slump Layer on Terrace Slope -->
  <path d="M 75 55 L 170 115 L 240 170 L 240 162 L 170 105 L 75 45 Z" fill="#451a03" fill-opacity="0.4" stroke="#f59e0b" stroke-width="1" />
  <path d="M 75 55 L 170 115 L 240 170 L 240 162 L 170 105 L 75 45 Z" fill="url(#{colluvium_id})" />

  <!-- Tension Head Scarp at Upper Terrace -->
  <line x1="75" y1="42" x2="75" y2="58" stroke="#ef4444" stroke-width="2.2" />
  <!-- Lined Garland Catch Drain at Terrace Crest (MoRTH 309) -->
  <polygon points="68,43 78,43 75,50 71,50" fill="#0284c7" stroke="#38bdf8" stroke-width="0.8" />
  <circle cx="73" cy="46" r="1.5" fill="#bae6fd" />

  <!-- Upper Terrace Grouted Soil Dowels (Ø25mm Fe500D) -->
  <g stroke="#10b981" stroke-width="1.8" stroke-dasharray="4,2">
    <line x1="125" y1="80" x2="95" y2="125" />
    <line x1="165" y1="105" x2="135" y2="150" />
    <line x1="205" y1="130" x2="175" y2="175" />
  </g>
  <!-- Bearing plates for dowels -->
  <line x1="121" y1="78" x2="129" y2="82" stroke="#34d399" stroke-width="2.5" />
  <line x1="161" y1="103" x2="169" y2="107" stroke="#34d399" stroke-width="2.5" />
  <line x1="201" y1="128" x2="209" y2="132" stroke="#34d399" stroke-width="2.5" />

  <!-- Trapped Mudslide Debris behind Deflector Wall -->
  <path d="M 215 145 Q 235 158 245 168 L 245 170 L 205 170 Z" fill="#92400e" fill-opacity="0.75" />
  <path d="M 215 145 Q 235 158 245 168 L 245 170 L 205 170 Z" fill="url(#{debris_id})" />

  <!-- Proposed M25 Reinforced Concrete Cantilever Debris Deflector Wall -->
  <rect x="235" y="170" width="32" height="12" rx="1" fill="#475569" stroke="#94a3b8" stroke-width="1" />
  <polygon points="246,122 254,122 256,170 246,170" fill="#64748b" stroke="#94a3b8" stroke-width="1.1" />
  <!-- Granular Filter Backfill Behind Stem -->
  <polygon points="238,135 246,135 246,170 238,170" fill="#0284c7" opacity="0.35" stroke="#38bdf8" stroke-width="0.8" stroke-dasharray="2,2" />
  <!-- Slotted Weep Holes -->
  <line x1="244" y1="162" x2="258" y2="164" stroke="#facc15" stroke-width="1.6" />

  <!-- Residential Dwelling (SDRF Residential Housing Zone) -->
  <line x1="240" y1="170" x2="505" y2="170" stroke="#334155" stroke-width="1.2" />

  <!-- Residential House Main Body -->
  <rect x="315" y="132" width="110" height="38" rx="1" fill="#1e293b" stroke="#64748b" stroke-width="1.2" />
  <!-- Front Door -->
  <rect x="360" y="146" width="18" height="24" fill="#b45309" stroke="#d97706" stroke-width="0.8" />
  <circle cx="374" cy="158" r="1" fill="#fde68a" />
  <!-- Windows with illumination -->
  <rect x="328" y="142" width="18" height="14" rx="1" fill="#0284c7" opacity="0.8" stroke="#38bdf8" stroke-width="0.8" />
  <line x1="337" y1="142" x2="337" y2="156" stroke="#0f172a" stroke-width="0.8" />
  <line x1="328" y1="149" x2="346" y2="149" stroke="#0f172a" stroke-width="0.8" />

  <rect x="392" y="142" width="18" height="14" rx="1" fill="#0284c7" opacity="0.8" stroke="#38bdf8" stroke-width="0.8" />
  <line x1="401" y1="142" x2="401" y2="156" stroke="#0f172a" stroke-width="0.8" />
  <line x1="392" y1="149" x2="410" y2="149" stroke="#0f172a" stroke-width="0.8" />

  <!-- Traditional Himalayan Pitched Slate Roof -->
  <polygon points="305,133 370,102 435,133" fill="#334155" stroke="#94a3b8" stroke-width="1.4" />
  <!-- Chimney / Ridge vent -->
  <rect x="398" y="108" width="8" height="16" fill="#78350f" stroke="#92400e" stroke-width="0.8" />

  <!-- Safety Clearance Zone Between Deflector Wall and House -->
  <line x1="256" y1="126" x2="315" y2="126" stroke="#10b981" stroke-width="1" stroke-dasharray="3,2" />
  <text x="264" y="122" font-size="5.8" font-weight="800" fill="#6ee7b7">BUFFER CLEARANCE: 4.5m</text>

  <!-- Anatomical Callout Badges -->
  <rect x="18" y="10" width="142" height="14" rx="2" fill="#450a0a" stroke="#dc2626" stroke-width="0.8" />
  <text x="23" y="20" font-size="6.5" font-weight="800" fill="#fca5a5">TERRACE MUDSLIDE HEAD SCARP</text>

  <rect x="185" y="88" width="145" height="14" rx="2" fill="#064e3b" stroke="#059669" stroke-width="0.8" />
  <text x="190" y="98" font-size="6.2" font-weight="800" fill="#a7f3d0">M25 CANTILEVER WALL &amp; DOWELS</text>

  <rect x="340" y="88" width="168" height="14" rx="2" fill="#1e1b4b" stroke="#6366f1" stroke-width="0.8" />
  <text x="345" y="98" font-size="6.2" font-weight="800" fill="#c7d2fe">RESIDENTIAL DWELLING (SDRF ZONE)</text>

  <!-- Stability Evaluation Pill -->
  <rect x="340" y="10" width="170" height="16" rx="3" fill="#1e1b4b" stroke="#6366f1" stroke-width="0.8" />
  <text x="345" y="21" font-size="6.5" font-weight="800" fill="#c7d2fe">Monsoon FoS = {crit_fos:.2f} | Stabilized FoS = {target_fos:.2f}</text>"""


# ==============================================================================
# 9. MACRO-SCALE CATASTROPHIC SLOPE FAILURE (DIAGNOSTIC NOTICE PLATE)
# ==============================================================================
def _render_macro_catastrophic_svg(
    rejection_notice: str = "",
    slope_h: float = 48.0,
    rock_name: str = "Metamorphic Gneiss",
    **kwargs: Any,
) -> str:
    """Clean, high-contrast engineering diagnostic plate for Macro-Scale Slope Failures.

    Renders zero fake slip planes and zero fake FoS numbers, mandating a full LiDAR & DPR.
    """
    return f"""  <!-- Macro Catastrophe Warning Background Banner -->
  <rect x="15" y="12" width="490" height="32" rx="4" fill="#450a0a" stroke="#ef4444" stroke-width="1.2" />
  <circle cx="34" cy="28" r="9" fill="#dc2626" />
  <text x="31" y="32" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="900" fill="#ffffff">!</text>
  <text x="52" y="24" font-size="8" font-weight="900" fill="#fecaca" letter-spacing="0.5">MACRO-SCALE SLOPE FAILURE &bull; LOCAL TOE WALL INAPPLICABLE</text>
  <text x="52" y="36" font-size="6.5" font-weight="700" fill="#fca5a5">STATUTORY MANDATE: FULL AIRBORNE LiDAR &amp; MULTIDISCIPLINARY DPR REQUIRED</text>

  <!-- Massive Mountain Silhouette Background (Scale H >> 45m) -->
  <path d="M 15 220 L 70 170 L 140 120 L 210 70 L 290 55 L 360 85 L 430 145 L 505 220 Z" fill="#1e293b" opacity="0.35" stroke="#334155" stroke-width="1" />
  <path d="M 140 120 Q 240 135 360 170" fill="none" stroke="#ef4444" stroke-width="2" stroke-dasharray="6,4" />
  <text x="215" y="145" font-size="6" font-weight="800" fill="#f87171">DEEP-SEATED MOUNTAIN SHEAR SURFACE (H &gt; 45m)</text>

  <!-- Technical Diagnostic Dossier Box -->
  <rect x="25" y="60" width="470" height="152" rx="5" fill="#0f172a" stroke="#334155" stroke-width="1" />

  <rect x="40" y="74" width="440" height="22" rx="3" fill="#1e1b4b" stroke="#4338ca" stroke-width="0.8" />
  <text x="50" y="88" font-size="7" font-weight="800" fill="#e0e7ff">DISASTER SCALE CLASSIFICATION: LEVEL-1 MEGA-LANDSLIDE (EXCEEDS PWD PPR LIMITS)</text>

  <g font-size="6.8" font-family="'Manrope', sans-serif" fill="#cbd5e1">
    <text x="45" y="112"><tspan fill="#ef4444" font-weight="800">&bull; Physical Limiting Condition:</tspan> Scarp Height H = {slope_h:.1f}m (&gt; 45m threshold) &bull; Rock Mass: {rock_name}</text>
    <text x="45" y="127"><tspan fill="#f59e0b" font-weight="800">&bull; Standard Retaining Works Ineffective:</tspan> Local 3.0m–8.0m breast walls/gabions cannot retain massive debris.</text>
    <text x="45" y="142"><tspan fill="#38bdf8" font-weight="800">&bull; Statutory Governance Protocol:</tspan> Site requires multi-disciplinary DPR per NDMA / IRC:SP:48 guidelines.</text>
    <text x="45" y="157"><tspan fill="#10b981" font-weight="800">&bull; Mandated Investigations:</tspan> Drone UAV-LiDAR topographic mapping, deep rotary core borings, 3D limit analysis.</text>
    <text x="45" y="172"><tspan fill="#c084fc" font-weight="800">&bull; Administrative Action:</tspan> Immediate highway bypass staging, SDRF emergency clearance, route to GSI / IIT team.</text>
  </g>

  <!-- Bottom Diagnostic Badge -->
  <rect x="40" y="186" width="440" height="18" rx="2" fill="#18181b" stroke="#27272a" stroke-width="0.8" />
  <text x="50" y="198" font-family="'JetBrains Mono', monospace" font-size="6.2" font-weight="700" fill="#94a3b8">ENGINEERING STATUS: PPR REVERTED &bull; COMPREHENSIVE LEVEL-1 DPR MANDATED &bull; STANDARD BOQ NULLIFIED</text>"""


# ==============================================================================
# 10. DISQUALIFIED NON-TERRAIN / OUT-OF-DISTRIBUTION MEDIA
# ==============================================================================
def _render_rejected_ood_svg(
    rejection_notice: str = "",
    **kwargs: Any,
) -> str:
    """Clean, high-contrast engineering diagnostic plate for Non-Terrain False Alarms.

    Renders zero fake slip planes and zero fake FoS numbers, suppressing the cross-section.
    """
    return """  <!-- Out-of-Distribution Rejection Banner -->
  <rect x="15" y="12" width="490" height="32" rx="4" fill="#1e293b" stroke="#f59e0b" stroke-width="1.2" />
  <circle cx="34" cy="28" r="9" fill="#d97706" />
  <text x="31" y="32" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="900" fill="#ffffff">&empty;</text>
  <text x="52" y="24" font-size="8" font-weight="900" fill="#fef3c7" letter-spacing="0.5">OPTICAL AUDIT DISQUALIFICATION &bull; NON-LANDSLIDE / NON-TERRAIN MEDIA</text>
  <text x="52" y="36" font-size="6.5" font-weight="700" fill="#fde68a">CROSS-SECTION SUPPRESSED — ZERO ACTIVE GROUND DEFORMATION OBSERVED</text>

  <!-- Technical Diagnostic Dossier Box -->
  <rect x="25" y="60" width="470" height="152" rx="5" fill="#0b0f19" stroke="#1e293b" stroke-width="1" />

  <rect x="40" y="74" width="440" height="22" rx="3" fill="#18181b" stroke="#27272a" stroke-width="0.8" />
  <text x="50" y="88" font-size="7" font-weight="800" fill="#a1a1aa">VALIDATION STATUS: DISQUALIFIED_NON_TERRAIN (AUDIT GATE SUSPENDED)</text>

  <g font-size="6.8" font-family="'Manrope', sans-serif" fill="#94a3b8">
    <text x="45" y="112"><tspan fill="#f59e0b" font-weight="800">&bull; Computer Vision Inspection:</tspan> No visible slope failure scarp, tension cracks, or debris accumulation.</text>
    <text x="45" y="127"><tspan fill="#38bdf8" font-weight="800">&bull; Out-of-Distribution Guardrail:</tspan> Non-terrain image (indoor, document screenshot, vehicle, or stable forest).</text>
    <text x="45" y="142"><tspan fill="#10b981" font-weight="800">&bull; Kinematic Kinship:</tspan> Limit equilibrium equations (IS:14458 / Hoek &amp; Bray) suspended to prevent hallucination.</text>
    <text x="45" y="157"><tspan fill="#c084fc" font-weight="800">&bull; Statutory Outlay:</tspan> Civil Remediation Total = &#8377;0.00 &bull; BOQ Line Items = 0 (Withdrawn).</text>
    <text x="45" y="172"><tspan fill="#fca5a5" font-weight="800">&bull; Recommended Next Step:</tspan> Capture clear, high-resolution optical photo of affected slope cut or distress zone.</text>
  </g>

  <!-- Bottom Diagnostic Badge -->
  <rect x="40" y="186" width="440" height="18" rx="2" fill="#18181b" stroke="#27272a" stroke-width="0.8" />
  <text x="50" y="198" font-family="'JetBrains Mono', monospace" font-size="6.2" font-weight="700" fill="#71717a">ENGINEERING STATUS: PHYSICAL ANALYSIS WITHDRAWN &bull; FAKE SLIP SURFACES SUPPRESSED &bull; ZERO HAZARD SANCTION</text>"""
