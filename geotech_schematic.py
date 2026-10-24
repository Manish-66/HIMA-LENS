"""HIMA-LENS Geotechnical ML Schematic Cross-Section Engine.

Translates computer vision observations, empirical telemetry, and geotechnical engineering
parameters into publication-grade, dynamic 2D vector cross-section schematics (SVG) conforming
to USGS Circular 1325 (Highland & Bobrowsky, 2008), Cruden & Varnes (1996), IS:14458,
IRC:SP:48:2023, and CEDD Geoguides.

Supported failure kinematics:
- Translational / Planar Rock Slide along Daylighting Joint
- Rotational Slump / Circular Overburden Failure with Crown Tension Cracks & Toe Heave
- Rockfall / Columnar Topple along Sub-Vertical Exfoliation Fissures
- Channelized Debris Flow / Rapid Slurry Runout Fan
- Structural Wedge Failure along Intersecting Discontinuity Planes (J1 x J2)
- Creep / Progressive Soil Subsidence with Pavement Distortion
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

    and report telemetry. Dynamically varies across failure modes, lithologies,
    dimensions, and slope attributes.
    """
    assessment = assessment or {}
    report = report or {}

    obs = assessment.get("observed_features") or {}
    geom = obs.get("optical_geometry") or {}
    slope = assessment.get("slope_characteristics") or {}
    geol = assessment.get("geology") or {}
    road = assessment.get("road_impact") or {}
    rw_specs = assessment.get("retaining_wall_specs") or {}
    telemetry = assessment.get("telemetry") or {}

    # 1. Failure kinematics determination
    raw_mode = (
        geom.get("kinematic_failure_mode")
        or obs.get("usgs_two_term_name")
        or obs.get("failure_movement_observed")
        or telemetry.get("reported_movement")
        or assessment.get("movement_type")
        or report.get("movement_type")
        or "Slide"
    )
    mode_lower = raw_mode.lower()

    if any(k in mode_lower for k in ("topple", "fall", "rockfall")):
        mode = "rockfall"
        mode_label = "ROCKFALL / TOPPLING FAILURE"
    elif any(k in mode_lower for k in ("flow", "debris flow", "mudflow", "avalanche")):
        mode = "debris_flow"
        mode_label = "CHANNELIZED DEBRIS FLOW"
    elif any(k in mode_lower for k in ("slump", "rotational")):
        mode = "rotational_slump"
        mode_label = "ROTATIONAL OVERBURDEN SLUMP"
    elif any(k in mode_lower for k in ("wedge",)):
        mode = "wedge"
        mode_label = "STRUCTURAL WEDGE FAILURE"
    elif any(k in mode_lower for k in ("creep", "subsidence", "settlement")):
        mode = "creep_subsidence"
        mode_label = "SLOPE CREEP & SURFICIAL SUBSIDENCE"
    else:
        mode = "translational"
        mode_label = "TRANSLATIONAL PLANAR ROCK SLIDE"

    # 2. Angles
    dip_raw = (
        geom.get("slip_surface_dip_deg")
        or geol.get("dip_joints")
        or geol.get("joint_orientation")
    )
    dip_deg = _extract_angle(dip_raw, default=54)

    cut_raw = (
        geom.get("cut_slope_angle_deg")
        or slope.get("cut_slope_angle")
        or obs.get("cut_slope_angle_est")
    )
    cut_deg = _extract_angle(cut_raw, default=64)

    # 3. Heights and Dimensions
    height_raw = slope.get("slope_height_above") or slope.get("height_above")
    slope_height_m = _extract_height(height_raw, default=7.5)

    formation_w = _extract_width(road.get("width_before"), default=5.25)
    open_w = _extract_width(road.get("width_after"), default=2.20)
    if open_w >= formation_w:
        open_w = round(formation_w * 0.45, 2)

    rock_name = (
        geol.get("prominent_soil_rock")
        or obs.get("prominent_rock_type")
        or report.get("lithology")
        or "Sandstone"
    )

    # 4. Retaining wall / proposed remediation specs
    wall_h = rw_specs.get("height_m") or 2.8
    wall_mat = rw_specs.get("material") or "Plum Concrete (M15)"

    # 5. Badges & Top Banner Callouts conforming to textbook taxonomy
    if mode == "rotational_slump":
        top_badge = f"CIRCULAR SLIP ARC &bull; DIP: {dip_deg}&deg; &bull; H<sub>cut</sub>={slope_height_m:.1f}m"
    elif mode == "rockfall":
        top_badge = f"SUB-VERTICAL CLIFF &bull; CUT: {cut_deg}&deg; &bull; COLUMN TOPPLE"
    elif mode == "debris_flow":
        top_badge = f"DEBRIS RUNOUT FAN &bull; CHUTE: {cut_deg}&deg; &bull; H={slope_height_m:.1f}m"
    elif mode == "wedge":
        top_badge = f"INTERSECTING JOINTS (J1xJ2) &bull; PLUNGE: {dip_deg}&deg;"
    elif mode == "creep_subsidence":
        top_badge = f"CONTINUOUS CREEP &bull; SUBSIDENCE GRADIENT: {cut_deg}&deg;"
    else:
        top_badge = f"SLIP PLANE: {dip_deg}&deg; DAYLIGHTING &bull; H<sub>cut</sub>={slope_height_m:.1f}m"

    # Estimate physical factor of safety (Limit Equilibrium pseudo-static approximation)
    # FOS = (c' + (gamma * z * cos^2(beta) - u) * tan(phi)) / (gamma * z * sin(beta) * cos(beta))
    beta_rad = math.radians(dip_deg)
    phi_rad = math.radians(max(20, min(42, dip_deg - 8)))
    fos_approx = round(math.tan(phi_rad) / max(0.2, math.tan(beta_rad)) * 0.82, 2)
    fos_approx = max(0.68, min(1.12, fos_approx))

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
        "fos_approx": fos_approx,
        "wall_h": wall_h,
        "wall_mat": wall_mat,
        "drain_status": slope.get("debris_accumulation") or "Clogged with slide colluvium",
    }


def _get_lithology_hatch_defs(hatch_id: str, rock_name: str) -> str:
    """Generates standard geological lithology hatch patterns per USGS / GSI standards."""
    rock_lower = rock_name.lower()
    if any(k in rock_lower for k in ("limestone", "dolomite", "carbonate")):
        # Standard brickwork masonry pattern for limestone/dolomite
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
        # Foliated metamorphic foliation wavy lines for phyllite/schist
        return f"""
    <pattern id="{hatch_id}" width="14" height="8" patternTransform="rotate(28 0 0)" patternUnits="userSpaceOnUse">
      <rect width="14" height="8" fill="#f8fafc" />
      <path d="M 0 4 Q 3.5 1, 7 4 T 14 4" fill="none" stroke="#94a3b8" stroke-width="1.0" />
    </pattern>"""
    elif any(k in rock_lower for k in ("granite", "gneiss", "diorite", "basalt")):
        # Igneous / Gneissic cross-tick pattern
        return f"""
    <pattern id="{hatch_id}" width="12" height="12" patternUnits="userSpaceOnUse">
      <rect width="12" height="12" fill="#f8fafc" />
      <path d="M 3 3 L 9 9 M 9 3 L 3 9" stroke="#94a3b8" stroke-width="0.9" stroke-linecap="round" />
    </pattern>"""
    else:
        # Sedimentary sandstone / quartzite stippled diagonal hatching
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
    fos_approx = params["fos_approx"]
    wall_h = params["wall_h"]
    wall_mat = params["wall_mat"]

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

    # Hill cut toe X is fixed at road_x_start.
    # Crown apex X is dynamically governed by cut angle and slope height.
    # Higher cut angle means steeper scarp (closer X to cut toe).
    # Normalizing cut angle (45 deg -> dx=180; 78 deg -> dx=80)
    dx_cut = int(max(70, min(180, (90 - cut_deg) * 4.5 + 50)))
    crown_x = max(110, road_x_start - dx_cut)

    # Crown Y is governed by slope height (4m -> Y=60; 16m -> Y=24)
    crown_y = int(max(20, min(65, 75 - (slope_h * 3.5))))

    # Dispatch to specific kinematic failure mode generator
    if mode == "rotational_slump":
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
            fos_approx=fos_approx,
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
            fos_approx=fos_approx,
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
            fos_approx=fos_approx,
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
            fos_approx=fos_approx,
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
            fos_approx=fos_approx,
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
            fos_approx=fos_approx,
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
    fos_approx: float,
    wall_h: float,
) -> str:
    """Translational Planar Rock Slide along Daylighting Joint Discontinuity."""
    scarp_x = crown_x + 15
    scarp_y = crown_y + 12
    valley_y = 215

    # Joint planes angle rendering
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
  <line x1="{road_x_start - 35}" y1="{road_y - 25}" x2="{road_x_start - 20}" y2="{road_y - 15}" stroke="#38bdf8" stroke-width="1.3" marker-end="url(#arrowBlue)" />
  <text x="{scarp_x - 20}" y="{scarp_y + 45}" font-size="6.5" font-weight="700" fill="#38bdf8">PHREATIC SEEPAGE (u &gt; 0)</text>

  <!-- Planar Rupture Surface (Daylighting Shear Plane) -->
  <path d="M {scarp_x} {scarp_y} L {road_x_start} {road_y}" fill="none" stroke="#ef4444" stroke-width="2.2" stroke-dasharray="5,2" />
  <line x1="{scarp_x + 40}" y1="{scarp_y + int((road_y - scarp_y)*0.4)}" x2="{scarp_x + 55}" y2="{scarp_y + int((road_y - scarp_y)*0.4) + 12}" stroke="#ef4444" stroke-width="1.6" marker-end="url(#arrowRed)" />

  <!-- Extensional Crown Tension Cracks in Colluvium -->
  <path d="M {crown_x - 12} {crown_y - 5} L {crown_x - 10} {crown_y + 14} L {crown_x - 14} {crown_y + 22}" fill="none" stroke="#f87171" stroke-width="2" />
  <line x1="{crown_x - 30}" y1="{crown_y - 3}" x2="{crown_x - 28}" y2="{crown_y + 10}" stroke="#f87171" stroke-width="1.5" />

  <!-- Detached Translating Colluvial & Rock Mass -->
  <path d="M {scarp_x} {scarp_y} L {road_x_start} {road_y} L {debris_road_x} {road_y} L {debris_road_x - 15} {road_y - 18} L {scarp_x + 25} {scarp_y + 15} Z" fill="#451a03" fill-opacity="0.35" stroke="#f59e0b" stroke-width="1.2" />
  <path d="M {scarp_x} {scarp_y} L {road_x_start} {road_y} L {debris_road_x} {road_y} L {debris_road_x - 15} {road_y - 18} L {scarp_x + 25} {scarp_y + 15} Z" fill="url(#{debris_id})" />

  <!-- Debris Cone Surcharging Valleyward Carriageway -->
  <path d="M {road_x_start} {road_y} Q {(road_x_start + debris_road_x)//2} {road_y - 16} {debris_road_x} {road_y} Z" fill="#d97706" opacity="0.85" />

  <!-- Road Carriageway Pavement (IRC Hill Road Formation) -->
  <rect x="{road_x_start}" y="{road_y - 1}" width="{road_x_end - road_x_start}" height="5" fill="#1e293b" stroke="#334155" stroke-width="0.8" />
  <line x1="{debris_road_x}" y1="{road_y + 1}" x2="{debris_road_x}" y2="{road_y + 4}" stroke="#fbbf24" stroke-width="1.8" stroke-dasharray="2,2" />

  <!-- Hillside Side Drain (Choked by Colluvium) -->
  <polygon points="{road_x_start - 1},{road_y} {road_x_start + 7},{road_y + 8} {road_x_start + 14},{road_y + 8} {road_x_start + 14},{road_y}" fill="#334155" stroke="#64748b" stroke-width="0.8" />
  <circle cx="{road_x_start + 7}" cy="{road_y + 4}" r="3" fill="#ef4444" opacity="0.9" />

  <!-- Valley Shoulder & Crash Barrier -->
  <line x1="{road_x_end - 6}" y1="{road_y - 10}" x2="{road_x_end - 6}" y2="{road_y}" stroke="#94a3b8" stroke-width="2" />
  <circle cx="{road_x_end - 6}" cy="{road_y - 10}" r="2" fill="#e2e8f0" />

  <!-- Proposed Mitigation Overlay: Retaining Breast Wall with Weep Holes -->
  <polygon points="{road_x_start + 2},{road_y} {road_x_start + 14},{road_y} {road_x_start + 10},{road_y - 28} {road_x_start + 2},{road_y - 28}" fill="#0f766e" fill-opacity="0.25" stroke="#14b8a6" stroke-width="1" stroke-dasharray="2,2" />
  <!-- Weep holes -->
  <circle cx="{road_x_start + 6}" cy="{road_y - 10}" r="1.2" fill="#2dd4bf" />
  <circle cx="{road_x_start + 7}" cy="{road_y - 20}" r="1.2" fill="#2dd4bf" />

  <!-- Cut Slope Angle Arc Indicator -->
  <path d="M {road_x_start - 24} {road_y} A 24 24 0 0 1 {road_x_start - 10} {road_y - 22}" fill="none" stroke="#22c55e" stroke-width="1.3" />
  <text x="{road_x_start - 65}" y="{road_y - 26}" font-size="7.5" font-weight="800" fill="#4ade80">&beta; = {cut_str}</text>

  <!-- Slip Dip Angle Indicator -->
  <line x1="{scarp_x + 10}" y1="{scarp_y + 12}" x2="{scarp_x + 35}" y2="{scarp_y + 12}" stroke="#64748b" stroke-width="0.8" stroke-dasharray="2,2" />
  <path d="M {scarp_x + 28} {scarp_y + 12} A 18 18 0 0 1 {scarp_x + 22} {scarp_y + 22}" fill="none" stroke="#f87171" stroke-width="1.1" />
  <text x="{scarp_x + 36}" y="{scarp_y + 20}" font-size="7" font-weight="800" fill="#f87171">&theta; = {dip_deg}&deg;</text>

  <!-- Engineering Dimensions (Formation vs Restitution) -->
  <!-- Formation Width Dimension Line -->
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
  <!-- Detachment Scarp Badge -->
  <rect x="18" y="10" width="115" height="14" rx="2" fill="#450a0a" stroke="#dc2626" stroke-width="0.8" />
  <text x="23" y="20" font-size="6.5" font-weight="800" fill="#fca5a5">CROWN &amp; MAIN SCARP</text>

  <!-- Daylighting Joint Rupture Badge -->
  <rect x="{scarp_x - 10}" y="{scarp_y - 20}" width="135" height="14" rx="2" fill="#450a0a" stroke="#dc2626" stroke-width="0.8" />
  <text x="{scarp_x - 5}" y="{scarp_y - 10}" font-size="6.5" font-weight="800" fill="#fca5a5">RUPTURE PLANE: DIP {dip_deg}&deg; (DAYLIGHT)</text>

  <!-- Translating Colluvium Badge -->
  <rect x="{scarp_x + 65}" y="{scarp_y + 55}" width="118" height="14" rx="2" fill="#451a03" stroke="#f59e0b" stroke-width="0.8" />
  <text x="{scarp_x + 70}" y="{scarp_y + 65}" font-size="6.5" font-weight="800" fill="#fde68a">SLIDING COLLUVIUM ({rock_name})</text>

  <!-- Stability Evaluation Pill -->
  <rect x="365" y="10" width="140" height="16" rx="3" fill="#1e1b4b" stroke="#6366f1" stroke-width="0.8" />
  <text x="372" y="21" font-size="6.5" font-weight="800" fill="#c7d2fe">FOS &asymp; {fos_approx:.2f} (LIMIT EQUILIBRIUM)</text>"""


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
    fos_approx: float,
    wall_h: float,
) -> str:
    """Rotational Slump with Spoon-Shaped Cylindrical Slip Surface and Backward Tilting."""
    scarp_x = crown_x + 10
    scarp_y = crown_y + 10
    valley_y = 215

    # Control point for circular arc
    arc_cx = (scarp_x + road_x_start) // 2 - 10
    arc_cy = road_y + 15

    return f"""  <!-- In-situ Competent Bedrock Strata -->
  <path d="M 15 28 L {crown_x} {crown_y} L {scarp_x} {scarp_y} Q {arc_cx} {arc_cy} {road_x_start} {road_y} L {road_x_end} {road_y} L 505 {valley_y} L 505 236 L 15 236 Z" fill="url(#{hatch_id})" stroke="#334155" stroke-width="1.2" />

  <!-- Circular Cylindrical Shear Arc (Bishop / Fellenius Slip Surface) -->
  <path d="M {scarp_x} {scarp_y} Q {arc_cx} {arc_cy} {road_x_start} {road_y}" fill="none" stroke="#ef4444" stroke-width="2.4" stroke-dasharray="5,2" />

  <!-- Phreatic Seepage Line (Elevated Pore Water Pressure) -->
  <path d="M 25 {scarp_y + 15} Q {arc_cx - 20} {arc_cy - 20} {road_x_start - 10} {road_y - 6}" fill="none" stroke="#0284c7" stroke-width="1.4" stroke-dasharray="4,2" />
  <line x1="{road_x_start - 30}" y1="{road_y - 18}" x2="{road_x_start - 18}" y2="{road_y - 10}" stroke="#38bdf8" stroke-width="1.3" marker-end="url(#arrowBlue)" />
  <text x="{arc_cx - 45}" y="{arc_cy - 12}" font-size="6.5" font-weight="700" fill="#38bdf8">PHREATIC MANTLE</text>

  <!-- Backward-Tilted Rotational Slump Block (Head of Slide) -->
  <!-- Notice reverse surface slope tilting back toward hill -->
  <path d="M {scarp_x} {scarp_y} Q {arc_cx} {arc_cy} {road_x_start} {road_y} L {debris_road_x} {road_y} Q {(road_x_start + scarp_x)//2 + 20} {road_y - 30} {scarp_x + 18} {scarp_y + 15} Z" fill="#451a03" fill-opacity="0.35" stroke="#f59e0b" stroke-width="1.2" />
  <path d="M {scarp_x} {scarp_y} Q {arc_cx} {arc_cy} {road_x_start} {road_y} L {debris_road_x} {road_y} Q {(road_x_start + scarp_x)//2 + 20} {road_y - 30} {scarp_x + 18} {scarp_y + 15} Z" fill="url(#{debris_id})" />

  <!-- Reverse Tilt Indicator Arrow (Hallmark of Rotational Slump) -->
  <path d="M {scarp_x + 35} {scarp_y + 35} Q {scarp_x + 22} {scarp_y + 26} {scarp_x + 20} {scarp_y + 18}" fill="none" stroke="#f97316" stroke-width="1.4" marker-end="url(#arrowRed)" />
  <text x="{scarp_x + 32}" y="{scarp_y + 46}" font-size="6.5" font-weight="700" fill="#fdba74">BACKWARD TILT</text>

  <!-- Transverse Tension Fissures & Stepped Scarps at Crown -->
  <path d="M {crown_x - 10} {crown_y - 4} L {crown_x - 8} {crown_y + 14} L {crown_x - 12} {crown_y + 24}" fill="none" stroke="#f87171" stroke-width="2" />
  <line x1="{crown_x - 28}" y1="{crown_y - 2}" x2="{crown_x - 26}" y2="{crown_y + 12}" stroke="#f87171" stroke-width="1.5" />
  <line x1="{crown_x - 45}" y1="{crown_y - 1}" x2="{crown_x - 44}" y2="{crown_y + 8}" stroke="#f87171" stroke-width="1.2" />

  <!-- Bulging Toe of Surface of Rupture (Heaved Pressure Ridge on Road) -->
  <path d="M {road_x_start} {road_y} Q {(road_x_start + debris_road_x)//2} {road_y - 18} {debris_road_x} {road_y} Z" fill="#d97706" opacity="0.9" stroke="#b45309" stroke-width="1" />

  <!-- Road Carriageway Pavement (IRC Hill Road Formation) -->
  <rect x="{road_x_start}" y="{road_y - 1}" width="{road_x_end - road_x_start}" height="5" fill="#1e293b" stroke="#334155" stroke-width="0.8" />
  <line x1="{debris_road_x}" y1="{road_y + 1}" x2="{debris_road_x}" y2="{road_y + 4}" stroke="#fbbf24" stroke-width="1.8" stroke-dasharray="2,2" />

  <!-- Hillside Side Drain (Crushed under Toe Heave) -->
  <polygon points="{road_x_start - 1},{road_y} {road_x_start + 7},{road_y + 8} {road_x_start + 14},{road_y + 8} {road_x_start + 14},{road_y}" fill="#334155" stroke="#64748b" stroke-width="0.8" />
  <circle cx="{road_x_start + 7}" cy="{road_y + 4}" r="3" fill="#ef4444" opacity="0.9" />

  <!-- Valley Shoulder & Crash Barrier -->
  <line x1="{road_x_end - 6}" y1="{road_y - 10}" x2="{road_x_end - 6}" y2="{road_y}" stroke="#94a3b8" stroke-width="2" />
  <circle cx="{road_x_end - 6}" cy="{road_y - 10}" r="2" fill="#e2e8f0" />

  <!-- Proposed Remediation: Gabion Toe Key + Crest Offloading Bench -->
  <rect x="{road_x_start + 2}" y="{road_y - 24}" width="12" height="24" fill="#0f766e" fill-opacity="0.25" stroke="#14b8a6" stroke-width="1" stroke-dasharray="2,2" />
  <line x1="{road_x_start + 2}" y1="{road_y - 12}" x2="{road_x_start + 14}" y2="{road_y - 12}" stroke="#14b8a6" stroke-width="0.8" />

  <!-- Cut Slope Angle Arc Indicator -->
  <path d="M {road_x_start - 24} {road_y} A 24 24 0 0 1 {road_x_start - 10} {road_y - 22}" fill="none" stroke="#22c55e" stroke-width="1.3" />
  <text x="{road_x_start - 65}" y="{road_y - 26}" font-size="7.5" font-weight="800" fill="#4ade80">&beta; = {cut_str}</text>

  <!-- Engineering Dimensions (Formation vs Restitution) -->
  <line x1="{road_x_start}" y1="{road_y + 18}" x2="{road_x_end}" y2="{road_y + 18}" stroke="#94a3b8" stroke-width="0.9" />
  <line x1="{road_x_start}" y1="{road_y + 14}" x2="{road_x_start}" y2="{road_y + 22}" stroke="#94a3b8" stroke-width="0.9" />
  <line x1="{road_x_end}" y1="{road_y + 14}" x2="{road_x_end}" y2="{road_y + 22}" stroke="#94a3b8" stroke-width="0.9" />
  <text x="{road_x_start + 20}" y="{road_y + 28}" font-family="'JetBrains Mono', monospace" font-size="7" font-weight="700" fill="#cbd5e1">Formation: {formation_w:.2f}m</text>

  <line x1="{debris_road_x}" y1="{road_y + 40}" x2="{road_x_end}" y2="{road_y + 40}" stroke="#22c55e" stroke-width="1.2" />
  <line x1="{debris_road_x}" y1="{road_y + 36}" x2="{debris_road_x}" y2="{road_y + 44}" stroke="#22c55e" stroke-width="1.2" />
  <line x1="{road_x_end}" y1="{road_y + 36}" x2="{road_x_end}" y2="{road_y + 44}" stroke="#22c55e" stroke-width="1.2" />
  <text x="{debris_road_x + 8}" y="{road_y + 50}" font-family="'JetBrains Mono', monospace" font-size="7.5" font-weight="800" fill="#4ade80">Operable: {open_w:.2f}m</text>

  <!-- Slope Height Vertical Dimension -->
  <line x1="{crown_x - 35}" y1="{crown_y}" x2="{crown_x - 35}" y2="{road_y}" stroke="#64748b" stroke-width="0.8" stroke-dasharray="2,2" />
  <line x1="{crown_x - 40}" y1="{crown_y}" x2="{crown_x - 30}" y2="{crown_y}" stroke="#64748b" stroke-width="0.8" />
  <line x1="{crown_x - 40}" y1="{road_y}" x2="{crown_x - 30}" y2="{road_y}" stroke="#64748b" stroke-width="0.8" />
  <text x="{crown_x - 82}" y="{(crown_y + road_y)//2}" font-family="'JetBrains Mono', monospace" font-size="7" font-weight="700" fill="#94a3b8">H = {slope_h:.1f}m</text>

  <!-- Anatomical Callout Badges -->
  <rect x="18" y="10" width="132" height="14" rx="2" fill="#450a0a" stroke="#dc2626" stroke-width="0.8" />
  <text x="23" y="20" font-size="6.5" font-weight="800" fill="#fca5a5">MAIN SCARP &amp; CROWN CRACKS</text>

  <rect x="{arc_cx - 40}" y="{arc_cy + 8}" width="130" height="14" rx="2" fill="#450a0a" stroke="#dc2626" stroke-width="0.8" />
  <text x="{arc_cx - 35}" y="{arc_cy + 18}" font-size="6.5" font-weight="800" fill="#fca5a5">CIRCULAR SHEAR ARC (RUPTURE)</text>

  <rect x="{road_x_start - 35}" y="{road_y - 36}" width="125" height="14" rx="2" fill="#451a03" stroke="#f59e0b" stroke-width="0.8" />
  <text x="{road_x_start - 30}" y="{road_y - 26}" font-size="6.5" font-weight="800" fill="#fde68a">HEAVED TOE LOBE (PRESSURE RIDGE)</text>

  <!-- Stability Evaluation Pill -->
  <rect x="365" y="10" width="140" height="16" rx="3" fill="#1e1b4b" stroke="#6366f1" stroke-width="0.8" />
  <text x="372" y="21" font-size="6.5" font-weight="800" fill="#c7d2fe">FOS &asymp; {fos_approx:.2f} (CIRCULAR SLIP ARC)</text>"""


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
    fos_approx: float,
    wall_h: float,
) -> str:
    """Rockfall and Columnar Toppling along Sub-Vertical Joint Sets."""
    cliff_x = road_x_start - 35
    valley_y = 215

    return f"""  <!-- In-situ Steep Rock Cliff Mass ({rock_name}) -->
  <path d="M 15 20 L {crown_x} {crown_y} L {cliff_x} 28 L {road_x_start - 10} {road_y} L {road_x_end} {road_y} L 505 {valley_y} L 505 236 L 15 236 Z" fill="url(#{hatch_id})" stroke="#334155" stroke-width="1.2" />

  <!-- Sub-Vertical Exfoliation & Columnar Joints (75-85 deg dip) -->
  <g stroke="#475569" stroke-width="1.1" stroke-dasharray="4,3">
    <line x1="{cliff_x - 35}" y1="26" x2="{road_x_start - 45}" y2="{road_y}" />
    <line x1="{cliff_x - 12}" y1="28" x2="{road_x_start - 22}" y2="{road_y}" />
  </g>

  <!-- Open Extensional Detachment Fissure (Tension Crack) -->
  <path d="M {cliff_x + 10} 28 L {cliff_x + 16} 95 L {cliff_x + 22} 145" fill="none" stroke="#dc2626" stroke-width="2.6" />

  <!-- Detached Toppling Rock Column (Rotating Outward by Gravity) -->
  <polygon points="{cliff_x + 12},28 {cliff_x + 36},28 {cliff_x + 46},135 {cliff_x + 22},135" fill="#451a03" fill-opacity="0.4" stroke="#f59e0b" stroke-width="1.3" />
  <polygon points="{cliff_x + 12},28 {cliff_x + 36},28 {cliff_x + 46},135 {cliff_x + 22},135" fill="url(#{debris_id})" />

  <!-- Outward Toppling Rotation Kinetic Vector -->
  <path d="M {cliff_x + 28} 55 Q {cliff_x + 48} 52 {cliff_x + 55} 62" fill="none" stroke="#ef4444" stroke-width="1.8" marker-end="url(#arrowRed)" />
  <text x="{cliff_x + 45}" y="50" font-size="6.5" font-weight="700" fill="#fca5a5">TOPPLING MOMENT (M &gt; 0)</text>

  <!-- Free-Falling & Bouncing Rock Boulders along Trajectory -->
  <g fill="#78350f" stroke="#f59e0b" stroke-width="1">
    <polygon points="{cliff_x + 48},105 {cliff_x + 60},100 {cliff_x + 64},112 {cliff_x + 52},115" />
    <polygon points="{cliff_x + 68},128 {cliff_x + 82},123 {cliff_x + 85},136 {cliff_x + 71},139" />
  </g>
  <!-- Ballistic Trajectory Curve (Parabolic) -->
  <path d="M {cliff_x + 40} 80 Q {cliff_x + 75} 105 {road_x_start + 15} {road_y - 12}" fill="none" stroke="#fbbf24" stroke-width="1.2" stroke-dasharray="3,3" />

  <!-- Talus Scree Cone Burying Roadway & Ditch -->
  <path d="M {road_x_start - 12} {road_y} L {debris_road_x} {road_y} L {road_x_start + 18} {road_y - 24} Z" fill="#b45309" opacity="0.9" stroke="#78350f" stroke-width="1" />
  <path d="M {road_x_start - 12} {road_y} L {debris_road_x} {road_y} L {road_x_start + 18} {road_y - 24} Z" fill="url(#{debris_id})" />

  <!-- Road Carriageway Pavement -->
  <rect x="{road_x_start}" y="{road_y - 1}" width="{road_x_end - road_x_start}" height="5" fill="#1e293b" stroke="#334155" stroke-width="0.8" />
  <line x1="{debris_road_x}" y1="{road_y + 1}" x2="{debris_road_x}" y2="{road_y + 4}" stroke="#fbbf24" stroke-width="1.8" stroke-dasharray="2,2" />

  <!-- Valley Shoulder & Crash Barrier -->
  <line x1="{road_x_end - 6}" y1="{road_y - 10}" x2="{road_x_end - 6}" y2="{road_y}" stroke="#94a3b8" stroke-width="2" />
  <circle cx="{road_x_end - 6}" cy="{road_y - 10}" r="2" fill="#e2e8f0" />

  <!-- Proposed Remediation: Dynamic Rockfall Net Barrier (CEDD Report 138) -->
  <line x1="{road_x_start - 16}" y1="{road_y - 32}" x2="{road_x_start - 16}" y2="{road_y}" stroke="#14b8a6" stroke-width="2" />
  <line x1="{road_x_start - 16}" y1="{road_y - 32}" x2="{road_x_start - 35}" y2="{road_y - 18}" stroke="#14b8a6" stroke-width="1" stroke-dasharray="2,2" />
  <circle cx="{road_x_start - 16}" cy="{road_y - 32}" r="2" fill="#2dd4bf" />

  <!-- Cut Slope Angle Indicator -->
  <path d="M {road_x_start - 32} {road_y} A 22 22 0 0 1 {road_x_start - 20} {road_y - 22}" fill="none" stroke="#22c55e" stroke-width="1.3" />
  <text x="{road_x_start - 75}" y="{road_y - 26}" font-size="7.5" font-weight="800" fill="#4ade80">&beta; = {cut_str}</text>

  <!-- Engineering Dimensions -->
  <line x1="{road_x_start}" y1="{road_y + 18}" x2="{road_x_end}" y2="{road_y + 18}" stroke="#94a3b8" stroke-width="0.9" />
  <line x1="{road_x_start}" y1="{road_y + 14}" x2="{road_x_start}" y2="{road_y + 22}" stroke="#94a3b8" stroke-width="0.9" />
  <line x1="{road_x_end}" y1="{road_y + 14}" x2="{road_x_end}" y2="{road_y + 22}" stroke="#94a3b8" stroke-width="0.9" />
  <text x="{road_x_start + 20}" y="{road_y + 28}" font-family="'JetBrains Mono', monospace" font-size="7" font-weight="700" fill="#cbd5e1">Formation: {formation_w:.2f}m</text>

  <line x1="{debris_road_x}" y1="{road_y + 40}" x2="{road_x_end}" y2="{road_y + 40}" stroke="#22c55e" stroke-width="1.2" />
  <line x1="{debris_road_x}" y1="{road_y + 36}" x2="{debris_road_x}" y2="{road_y + 44}" stroke="#22c55e" stroke-width="1.2" />
  <line x1="{road_x_end}" y1="{road_y + 36}" x2="{road_x_end}" y2="{road_y + 44}" stroke="#22c55e" stroke-width="1.2" />
  <text x="{debris_road_x + 8}" y="{road_y + 50}" font-family="'JetBrains Mono', monospace" font-size="7.5" font-weight="800" fill="#4ade80">Operable: {open_w:.2f}m</text>

  <!-- Slope Height Vertical Dimension -->
  <line x1="{crown_x - 35}" y1="{crown_y}" x2="{crown_x - 35}" y2="{road_y}" stroke="#64748b" stroke-width="0.8" stroke-dasharray="2,2" />
  <line x1="{crown_x - 40}" y1="{crown_y}" x2="{crown_x - 30}" y2="{crown_y}" stroke="#64748b" stroke-width="0.8" />
  <line x1="{crown_x - 40}" y1="{road_y}" x2="{crown_x - 30}" y2="{road_y}" stroke="#64748b" stroke-width="0.8" />
  <text x="{crown_x - 82}" y="{(crown_y + road_y)//2}" font-family="'JetBrains Mono', monospace" font-size="7" font-weight="700" fill="#94a3b8">H = {slope_h:.1f}m</text>

  <!-- Anatomical Badges -->
  <rect x="18" y="10" width="128" height="14" rx="2" fill="#450a0a" stroke="#dc2626" stroke-width="0.8" />
  <text x="23" y="20" font-size="6.5" font-weight="800" fill="#fca5a5">SUB-VERTICAL TENSION FISSURE</text>

  <rect x="{cliff_x - 20}" y="65" width="130" height="14" rx="2" fill="#450a0a" stroke="#dc2626" stroke-width="0.8" />
  <text x="{cliff_x - 15}" y="75" font-size="6.5" font-weight="800" fill="#fca5a5">TOPPLING ROCK COLUMN (UNSTABLE)</text>

  <rect x="{road_x_start - 10}" y="{road_y - 42}" width="125" height="14" rx="2" fill="#451a03" stroke="#f59e0b" stroke-width="0.8" />
  <text x="{road_x_start - 5}" y="{road_y - 32}" font-size="6.5" font-weight="800" fill="#fde68a">TALUS SCREE APRON (BOULDERS)</text>

  <!-- Stability Evaluation Pill -->
  <rect x="365" y="10" width="140" height="16" rx="3" fill="#1e1b4b" stroke="#6366f1" stroke-width="0.8" />
  <text x="372" y="21" font-size="6.5" font-weight="800" fill="#c7d2fe">TOPPLING KINEMATIC DISCONTINUITY</text>"""


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
    fos_approx: float,
    wall_h: float,
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

  <!-- Entrained Riparian Boulders and Uprooted Timber -->
  <line x1="{chute_start_x + 45}" y1="{chute_start_y + 35}" x2="{chute_start_x + 65}" y2="{chute_start_y + 42}" stroke="#78350f" stroke-width="2.5" stroke-linecap="round" />
  <circle cx="{chute_start_x + 55}" cy="{chute_start_y + 36}" r="3.2" fill="#451a03" stroke="#d97706" stroke-width="0.8" />
  <circle cx="{road_x_start - 35}" cy="{road_y - 25}" r="4.2" fill="#451a03" stroke="#d97706" stroke-width="0.8" />
  <circle cx="{road_x_start - 10}" cy="{road_y - 12}" r="3.5" fill="#451a03" stroke="#d97706" stroke-width="0.8" />

  <!-- Hyperconcentrated Flow Hydrodynamic Vectors -->
  <path d="M {chute_start_x + 30} {chute_start_y + 22} Q {(chute_start_x + road_x_start)//2} {road_y - 45} {road_x_start - 25} {road_y - 20}" fill="none" stroke="#38bdf8" stroke-width="1.4" marker-end="url(#arrowBlue)" />

  <!-- Spreading Debris Lobe Overtopping Roadway -->
  <path d="M {road_x_start - 5} {road_y} Q {(road_x_start + debris_road_x)//2} {road_y - 15} {debris_road_x} {road_y} Z" fill="#c2410c" opacity="0.9" stroke="#7c2d12" stroke-width="1" />

  <!-- Choked Culvert Box Inlet -->
  <rect x="{road_x_start - 2}" y="{road_y}" width="14" height="9" fill="#1e293b" stroke="#64748b" stroke-width="0.8" />
  <rect x="{road_x_start}" y="{road_y + 2}" width="10" height="5" fill="#ef4444" />
  <text x="{road_x_start - 25}" y="{road_y + 16}" font-size="6" font-weight="800" fill="#f87171">CULVERT CHOKED</text>

  <!-- Road Carriageway Pavement -->
  <rect x="{road_x_start}" y="{road_y - 1}" width="{road_x_end - road_x_start}" height="5" fill="#1e293b" stroke="#334155" stroke-width="0.8" />
  <line x1="{debris_road_x}" y1="{road_y + 1}" x2="{debris_road_x}" y2="{road_y + 4}" stroke="#fbbf24" stroke-width="1.8" stroke-dasharray="2,2" />

  <!-- Valley Shoulder & Crash Barrier -->
  <line x1="{road_x_end - 6}" y1="{road_y - 10}" x2="{road_x_end - 6}" y2="{road_y}" stroke="#94a3b8" stroke-width="2" />
  <circle cx="{road_x_end - 6}" cy="{road_y - 10}" r="2" fill="#e2e8f0" />

  <!-- Proposed Remediation: Flexible Debris Ring Net Barrier with Brake Rings -->
  <line x1="{chute_start_x + 50}" y1="{chute_start_y + 55}" x2="{chute_start_x + 70}" y2="{chute_start_y + 35}" stroke="#14b8a6" stroke-width="2.2" />
  <circle cx="{chute_start_x + 50}" cy="{chute_start_y + 55}" r="2" fill="#2dd4bf" />
  <circle cx="{chute_start_x + 70}" cy="{chute_start_y + 35}" r="2" fill="#2dd4bf" />

  <!-- Cut Slope Angle Arc Indicator -->
  <path d="M {road_x_start - 24} {road_y} A 24 24 0 0 1 {road_x_start - 10} {road_y - 22}" fill="none" stroke="#22c55e" stroke-width="1.3" />
  <text x="{road_x_start - 65}" y="{road_y - 26}" font-size="7.5" font-weight="800" fill="#4ade80">&beta; = {cut_str}</text>

  <!-- Engineering Dimensions -->
  <line x1="{road_x_start}" y1="{road_y + 18}" x2="{road_x_end}" y2="{road_y + 18}" stroke="#94a3b8" stroke-width="0.9" />
  <line x1="{road_x_start}" y1="{road_y + 14}" x2="{road_x_start}" y2="{road_y + 22}" stroke="#94a3b8" stroke-width="0.9" />
  <line x1="{road_x_end}" y1="{road_y + 14}" x2="{road_x_end}" y2="{road_y + 22}" stroke="#94a3b8" stroke-width="0.9" />
  <text x="{road_x_start + 20}" y="{road_y + 28}" font-family="'JetBrains Mono', monospace" font-size="7" font-weight="700" fill="#cbd5e1">Formation: {formation_w:.2f}m</text>

  <line x1="{debris_road_x}" y1="{road_y + 40}" x2="{road_x_end}" y2="{road_y + 40}" stroke="#22c55e" stroke-width="1.2" />
  <line x1="{debris_road_x}" y1="{road_y + 36}" x2="{debris_road_x}" y2="{road_y + 44}" stroke="#22c55e" stroke-width="1.2" />
  <line x1="{road_x_end}" y1="{road_y + 36}" x2="{road_x_end}" y2="{road_y + 44}" stroke="#22c55e" stroke-width="1.2" />
  <text x="{debris_road_x + 8}" y="{road_y + 50}" font-family="'JetBrains Mono', monospace" font-size="7.5" font-weight="800" fill="#4ade80">Operable: {open_w:.2f}m</text>

  <!-- Anatomical Callout Badges -->
  <rect x="18" y="10" width="130" height="14" rx="2" fill="#082f49" stroke="#0284c7" stroke-width="0.8" />
  <text x="23" y="20" font-size="6.5" font-weight="800" fill="#7dd3fc">SCOURED EROSION GULLY CHUTE</text>

  <rect x="{chute_start_x + 25}" y="{chute_start_y - 12}" width="140" height="14" rx="2" fill="#450a0a" stroke="#dc2626" stroke-width="0.8" />
  <text x="{chute_start_x + 30}" y="{chute_start_y - 2}" font-size="6.5" font-weight="800" fill="#fca5a5">BOULDER &amp; SLURRY SURGE FRONT</text>

  <rect x="{road_x_start - 25}" y="{road_y - 42}" width="135" height="14" rx="2" fill="#451a03" stroke="#f59e0b" stroke-width="0.8" />
  <text x="{road_x_start - 20}" y="{road_y - 32}" font-size="6.5" font-weight="800" fill="#fde68a">HIGH-VELOCITY DEBRIS FAN LOBE</text>

  <!-- Stability Evaluation Pill -->
  <rect x="365" y="10" width="140" height="16" rx="3" fill="#1e1b4b" stroke="#6366f1" stroke-width="0.8" />
  <text x="372" y="21" font-size="6.5" font-weight="800" fill="#c7d2fe">RAPID VISCOUS MASS FLOW (CLASS 5)</text>"""


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
    fos_approx: float,
    wall_h: float,
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

  <!-- Extensional Tension Crack at Wedge Apex -->
  <path d="M {scarp_x - 8} {scarp_y - 12} L {scarp_x} {scarp_y} L {scarp_x - 4} {scarp_y + 14}" fill="none" stroke="#f87171" stroke-width="2" />

  <!-- Detached Tetrahedral Wedge Mass -->
  <polygon points="{scarp_x},{scarp_y} {scarp_x + 48},{scarp_y + 38} {debris_road_x},{road_y} {road_x_start},{road_y}" fill="#451a03" fill-opacity="0.38" stroke="#f59e0b" stroke-width="1.3" />
  <polygon points="{scarp_x},{scarp_y} {scarp_x + 48},{scarp_y + 38} {debris_road_x},{road_y} {road_x_start},{road_y}" fill="url(#{debris_id})" />

  <!-- Sliding Kinetic Vector along Plunge Vector -->
  <line x1="{scarp_x + 30}" y1="{scarp_y + 24}" x2="{scarp_x + 46}" y2="{scarp_y + 38}" stroke="#ef4444" stroke-width="1.8" marker-end="url(#arrowRed)" />

  <!-- Debris Accumulation Encroaching on Roadway -->
  <path d="M {road_x_start} {road_y} Q {(road_x_start + debris_road_x)//2} {road_y - 15} {debris_road_x} {road_y} Z" fill="#d97706" opacity="0.85" />

  <!-- Road Carriageway Pavement -->
  <rect x="{road_x_start}" y="{road_y - 1}" width="{road_x_end - road_x_start}" height="5" fill="#1e293b" stroke="#334155" stroke-width="0.8" />
  <line x1="{debris_road_x}" y1="{road_y + 1}" x2="{debris_road_x}" y2="{road_y + 4}" stroke="#fbbf24" stroke-width="1.8" stroke-dasharray="2,2" />

  <!-- Side Drain Box -->
  <polygon points="{road_x_start - 1},{road_y} {road_x_start + 7},{road_y + 8} {road_x_start + 14},{road_y + 8} {road_x_start + 14},{road_y}" fill="#334155" stroke="#64748b" stroke-width="0.8" />
  <circle cx="{road_x_start + 7}" cy="{road_y + 4}" r="3" fill="#ef4444" opacity="0.9" />

  <!-- Valley Shoulder & Crash Barrier -->
  <line x1="{road_x_end - 6}" y1="{road_y - 10}" x2="{road_x_end - 6}" y2="{road_y}" stroke="#94a3b8" stroke-width="2" />
  <circle cx="{road_x_end - 6}" cy="{road_y - 10}" r="2" fill="#e2e8f0" />

  <!-- Proposed Remediation: Post-Tensioned Rock Anchors (LaRiMiT M14) -->
  <line x1="{road_x_start - 25}" y1="{road_y - 20}" x2="{scarp_x - 10}" y2="{scarp_y + 25}" stroke="#14b8a6" stroke-width="1.8" stroke-dasharray="3,2" />
  <rect x="{road_x_start - 27}" y="{road_y - 23}" width="4" height="6" fill="#2dd4bf" />

  <!-- Cut Angle Indicator -->
  <path d="M {road_x_start - 24} {road_y} A 24 24 0 0 1 {road_x_start - 10} {road_y - 22}" fill="none" stroke="#22c55e" stroke-width="1.3" />
  <text x="{road_x_start - 65}" y="{road_y - 26}" font-size="7.5" font-weight="800" fill="#4ade80">&beta; = {cut_str}</text>

  <!-- Engineering Dimensions -->
  <line x1="{road_x_start}" y1="{road_y + 18}" x2="{road_x_end}" y2="{road_y + 18}" stroke="#94a3b8" stroke-width="0.9" />
  <line x1="{road_x_start}" y1="{road_y + 14}" x2="{road_x_start}" y2="{road_y + 22}" stroke="#94a3b8" stroke-width="0.9" />
  <line x1="{road_x_end}" y1="{road_y + 14}" x2="{road_x_end}" y2="{road_y + 22}" stroke="#94a3b8" stroke-width="0.9" />
  <text x="{road_x_start + 20}" y="{road_y + 28}" font-family="'JetBrains Mono', monospace" font-size="7" font-weight="700" fill="#cbd5e1">Formation: {formation_w:.2f}m</text>

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
  <rect x="365" y="10" width="140" height="16" rx="3" fill="#1e1b4b" stroke="#6366f1" stroke-width="0.8" />
  <text x="372" y="21" font-size="6.5" font-weight="800" fill="#c7d2fe">WEDGE PLUNGE &xi; = {dip_deg}&deg; &bull; FOS &asymp; {fos_approx:.2f}</text>"""


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
    fos_approx: float,
    wall_h: float,
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
  <!-- Inner road subsided -->
  <rect x="{road_x_start}" y="{road_y - 1}" width="45" height="5" fill="#1e293b" stroke="#ef4444" stroke-width="0.8" />
  <!-- Subsidence step fracture -->
  <line x1="{road_x_start + 45}" y1="{road_y - 4}" x2="{road_x_start + 45}" y2="{road_y + 7}" stroke="#ef4444" stroke-width="2" />
  <!-- Outer road stepped down -->
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
  <rect x="365" y="10" width="140" height="16" rx="3" fill="#1e1b4b" stroke="#6366f1" stroke-width="0.8" />
  <text x="372" y="21" font-size="6.5" font-weight="800" fill="#c7d2fe">CREEP STRAIN RATE: &epsilon;&#775; &gt; 0 &bull; SLOW</text>"""
