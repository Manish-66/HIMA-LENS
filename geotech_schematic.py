"""HIMA-LENS Geotechnical ML Schematic Cross-Section Engine.

Translates computer vision observations and geotechnical telemetry into
publication-grade 2D vector cross-section schematics (SVG) conforming to
USGS Circular 1325, Cruden & Varnes (1996), IS:14458, and IRC:SP:48:2023.

Supported failure kinematics:
- Translational / Planar Rock Slide
- Rotational Slump / Circular Overburden Failure
- Rockfall / Block Topple
- Debris Flow / Channelized Mudflow
- Wedge Failure along Intersecting Discontinuities
"""
from __future__ import annotations

import re
from typing import Any


def _extract_angle(angle_str: str | int | float | None, default: int = 57) -> int:
    """Extracts a numeric angle in degrees from text or numeric input."""
    if angle_str is None:
        return default
    if isinstance(angle_str, (int, float)):
        return int(angle_str)
    match = re.search(r"(\d+)", str(angle_str))
    if match:
        val = int(match.group(1))
        if 10 <= val <= 89:
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


def extract_ml_kinematic_parameters(
    assessment: dict[str, Any] | None,
    report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Extracts or derives kinematic geometry parameters from ML vision assessment

    and report telemetry.
    """
    assessment = assessment or {}
    report = report or {}

    obs = assessment.get("observed_features") or {}
    geom = obs.get("optical_geometry") or {}
    slope = assessment.get("slope_characteristics") or {}
    geol = assessment.get("geology") or {}
    road = assessment.get("road_impact") or {}

    # 1. Failure kinematics determination
    raw_mode = (
        geom.get("kinematic_failure_mode")
        or obs.get("usgs_two_term_name")
        or obs.get("failure_movement_observed")
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
    else:
        mode = "translational"
        mode_label = "TRANSLATIONAL PLANAR SLIDE"

    # 2. Angles
    dip_raw = (
        geom.get("slip_surface_dip_deg")
        or geol.get("dip_joints")
        or geol.get("joint_orientation")
    )
    dip_deg = _extract_angle(dip_raw, default=57)

    cut_raw = (
        geom.get("cut_slope_angle_deg")
        or slope.get("cut_slope_angle")
        or obs.get("cut_slope_angle_est")
    )
    cut_deg = _extract_angle(cut_raw, default=66)

    # 3. Dimensions
    formation_w = _extract_width(road.get("width_before"), default=5.25)
    open_w = _extract_width(road.get("width_after"), default=2.30)
    if open_w >= formation_w:
        open_w = round(formation_w * 0.45, 2)

    rock_name = geol.get("prominent_soil_rock") or obs.get("prominent_rock_type") or "Sandstone"

    # 4. Badges & Callouts
    top_badge = f"SLIP PLANE: {dip_deg}° DAYLIGHTING"
    if mode == "rotational_slump":
        top_badge = f"CIRCULAR SLIP ARC &bull; DIP: {dip_deg}°"
    elif mode == "rockfall":
        top_badge = f"SUB-VERTICAL CLIFF &bull; CUT: {cut_deg}°"
    elif mode == "debris_flow":
        top_badge = f"DEBRIS RUNOUT &bull; SLOPE: {cut_deg}°"
    elif mode == "wedge":
        top_badge = f"INTERSECTING JOINTS &bull; PLUNGE: {dip_deg}°"

    return {
        "mode": mode,
        "mode_label": mode_label,
        "dip_deg": dip_deg,
        "cut_deg": cut_deg,
        "cut_angle_str": f"{cut_deg}°–{min(85, cut_deg + 2)}°",
        "formation_w": formation_w,
        "open_w": open_w,
        "rock_name": rock_name,
        "top_badge": top_badge,
        "tension_crack": geom.get("tension_cracks_visible", True),
        "drain_status": geom.get("drain_status") or "Choked with debris",
    }


def generate_schematic_svg(
    assessment: dict[str, Any] | None = None,
    report: dict[str, Any] | None = None,
    unique_suffix: str = "",
) -> str:
    """Generates an engineered 2D vector cross-section SVG (viewBox='0 0 520 226')

    tailored to the geotechnical failure mode and optical parameters.
    """
    params = extract_ml_kinematic_parameters(assessment, report)
    mode = params["mode"]
    dip_deg = params["dip_deg"]
    cut_deg = params["cut_deg"]
    cut_str = params["cut_angle_str"]
    formation_w = params["formation_w"]
    open_w = params["open_w"]
    rock_name = params["rock_name"]
    sfx = f"_{unique_suffix}" if unique_suffix else ""

    hatch_id = f"rockHatch{sfx}"
    debris_id = f"debrisPat{sfx}"

    # Determine rock hatch based on lithology
    rock_lower = rock_name.lower()
    if any(k in rock_lower for k in ("limestone", "dolomite")):
        hatch_lines = (
            f'<pattern id="{hatch_id}" width="12" height="12" patternUnits="userSpaceOnUse">'
            f'<rect width="12" height="12" fill="#f8fafc" />'
            f'<line x1="0" y1="0" x2="12" y2="0" stroke="#cbd5e1" stroke-width="1" />'
            f'<line x1="6" y1="0" x2="6" y2="6" stroke="#cbd5e1" stroke-width="1" />'
            f'<line x1="0" y1="6" x2="12" y2="6" stroke="#cbd5e1" stroke-width="1" />'
            f'<line x1="0" y1="6" x2="0" y2="12" stroke="#cbd5e1" stroke-width="1" />'
            f'<line x1="12" y1="6" x2="12" y2="12" stroke="#cbd5e1" stroke-width="1" />'
            f'</pattern>'
        )
    elif any(k in rock_lower for k in ("phyllite", "schist", "shale")):
        hatch_lines = (
            f'<pattern id="{hatch_id}" width="12" height="6" patternTransform="rotate(30 0 0)" patternUnits="userSpaceOnUse">'
            f'<line x1="0" y1="3" x2="12" y2="3" stroke="#cbd5e1" stroke-width="1.2" stroke-dasharray="4,2" />'
            f'</pattern>'
        )
    else:  # Sandstone / Quartzite / Default
        hatch_lines = (
            f'<pattern id="{hatch_id}" width="10" height="10" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">'
            f'<line x1="0" y1="0" x2="0" y2="10" stroke="#cbd5e1" stroke-width="1.2" />'
            f'</pattern>'
        )

    # Road coordinates: Formation starts at X=290, ends at X=420 (width 130px in SVG)
    road_x_start = 290
    road_x_end = 420
    road_w_px = road_x_end - road_x_start
    road_y = 170

    # Calculate debris encroachment along road formation based on open_w ratio
    ratio_open = max(0.15, min(0.90, open_w / formation_w if formation_w > 0 else 0.45))
    debris_road_x = road_x_start + int((1.0 - ratio_open) * road_w_px)

    # Dispatch to specific kinematic failure mode generator
    if mode == "rotational_slump":
        svg_body = _render_rotational_slump_svg(
            hatch_id=hatch_id,
            debris_id=debris_id,
            dip_deg=dip_deg,
            cut_str=cut_str,
            road_x_start=road_x_start,
            road_x_end=road_x_end,
            debris_road_x=debris_road_x,
            road_y=road_y,
            formation_w=formation_w,
            open_w=open_w,
        )
    elif mode == "rockfall":
        svg_body = _render_rockfall_topple_svg(
            hatch_id=hatch_id,
            debris_id=debris_id,
            dip_deg=dip_deg,
            cut_str=cut_str,
            road_x_start=road_x_start,
            road_x_end=road_x_end,
            debris_road_x=debris_road_x,
            road_y=road_y,
            formation_w=formation_w,
            open_w=open_w,
        )
    elif mode == "debris_flow":
        svg_body = _render_debris_flow_svg(
            hatch_id=hatch_id,
            debris_id=debris_id,
            dip_deg=dip_deg,
            cut_str=cut_str,
            road_x_start=road_x_start,
            road_x_end=road_x_end,
            debris_road_x=debris_road_x,
            road_y=road_y,
            formation_w=formation_w,
            open_w=open_w,
        )
    elif mode == "wedge":
        svg_body = _render_wedge_failure_svg(
            hatch_id=hatch_id,
            debris_id=debris_id,
            dip_deg=dip_deg,
            cut_str=cut_str,
            road_x_start=road_x_start,
            road_x_end=road_x_end,
            debris_road_x=debris_road_x,
            road_y=road_y,
            formation_w=formation_w,
            open_w=open_w,
        )
    else:  # translational
        svg_body = _render_translational_slide_svg(
            hatch_id=hatch_id,
            debris_id=debris_id,
            dip_deg=dip_deg,
            cut_str=cut_str,
            road_x_start=road_x_start,
            road_x_end=road_x_end,
            debris_road_x=debris_road_x,
            road_y=road_y,
            formation_w=formation_w,
            open_w=open_w,
        )

    svg = f"""<svg viewBox="0 0 520 226" xmlns="http://www.w3.org/2000/svg">
  <defs>
    {hatch_lines}
    <pattern id="{debris_id}" width="8" height="8" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1" fill="#d97706" opacity="0.6" />
      <circle cx="6" cy="5" r="1.1" fill="#b45309" opacity="0.7" />
    </pattern>
  </defs>

  <!-- Background Tint -->
  <rect width="520" height="226" fill="#f8fafc" />

{svg_body}
</svg>"""
    return svg


def _render_translational_slide_svg(
    hatch_id: str,
    debris_id: str,
    dip_deg: int,
    cut_str: str,
    road_x_start: int,
    road_x_end: int,
    debris_road_x: int,
    road_y: int,
    formation_w: float,
    open_w: float,
) -> str:
    """Translational Planar Rock Slide along Daylighting Joint."""
    return f"""  <!-- In-situ Bedrock Mass -->
  <path d="M 20 35 L 130 45 L 290 170 L 420 170 L 500 210 L 500 226 L 20 226 Z" fill="url(#{hatch_id})" stroke="#475569" stroke-width="1.2" />

  <!-- Bedrock Joint Discontinuities Dipping {dip_deg} deg -->
  <g stroke="#94a3b8" stroke-width="1" stroke-dasharray="3,3">
    <line x1="110" y1="50" x2="190" y2="175" />
    <line x1="160" y1="70" x2="240" y2="195" />
    <line x1="210" y1="95" x2="290" y2="220" />
  </g>

  <!-- Failure Shear Plane (Dashed Red Line) -->
  <path d="M 150 50 Q 220 110 295 170" fill="none" stroke="#dc2626" stroke-width="2.5" stroke-dasharray="5,3" />

  <!-- Detached Sliding Colluvial Mass -->
  <path d="M 150 50 Q 220 110 295 170 L {debris_road_x} 170 L {debris_road_x - 15} 150 Q 230 90 150 50 Z" fill="#fef3c7" stroke="#d97706" stroke-width="1.4" />
  <path d="M 150 50 Q 220 110 295 170 L {debris_road_x} 170 L {debris_road_x - 15} 150 Q 230 90 150 50 Z" fill="url(#{debris_id})" />

  <!-- Tension Crack at Scarp -->
  <path d="M 150 38 L 150 50 L 146 56" fill="none" stroke="#b91c1c" stroke-width="2.5" />

  <!-- Road Carriageway Pavement -->
  <rect x="{road_x_start}" y="168" width="{road_x_end - road_x_start}" height="5" fill="#334155" />
  <line x1="{debris_road_x}" y1="170" x2="{debris_road_x}" y2="173" stroke="#facc15" stroke-width="1.5" stroke-dasharray="3,2" />

  <!-- Clogged Side Drain Box -->
  <polygon points="290,170 297,177 304,177 304,170" fill="#94a3b8" stroke="#1e293b" stroke-width="1" />
  <circle cx="297" cy="173" r="3" fill="#ef4444" opacity="0.9" />

  <!-- Debris Accumulation Encroaching on Road (Blocked Zone) -->
  <path d="M 290 170 Q {(290 + debris_road_x)//2} 155 {debris_road_x} 170 Z" fill="#d97706" opacity="0.8" />

  <!-- Cut Angle Indicator -->
  <path d="M 268 170 A 25 25 0 0 1 278 145" fill="none" stroke="#092f25" stroke-width="1.3" />
  <text x="236" y="147" font-family="'Manrope', sans-serif" font-size="8.5" font-weight="800" fill="#092f25">{cut_str}</text>

  <!-- Carriageway Constriction Dimensions -->
  <line x1="{road_x_start}" y1="185" x2="{road_x_end}" y2="185" stroke="#0f172a" stroke-width="1" />
  <text x="325" y="195" font-family="'JetBrains Mono', monospace" font-size="7" font-weight="700" fill="#0f172a">Formation: {formation_w:.2f}m</text>

  <line x1="{debris_road_x}" y1="203" x2="{road_x_end}" y2="203" stroke="#16a34a" stroke-width="1.3" />
  <text x="365" y="213" font-family="'JetBrains Mono', monospace" font-size="7" font-weight="800" fill="#15803d">Open: {open_w:.2f}m</text>

  <!-- Callout Badges -->
  <rect x="25" y="10" width="105" height="15" rx="2" fill="#fee2e2" stroke="#f87171" stroke-width="1" />
  <text x="30" y="21" font-family="'Manrope', sans-serif" font-size="7" font-weight="800" fill="#991b1b">DETACHMENT SCARP</text>

  <rect x="110" y="65" width="118" height="15" rx="2" fill="#fee2e2" stroke="#f87171" stroke-width="1" />
  <text x="115" y="76" font-family="'Manrope', sans-serif" font-size="7" font-weight="800" fill="#991b1b">SLIP PLANE (DIP: {dip_deg}&#176;)</text>

  <rect x="210" y="102" width="110" height="15" rx="2" fill="#fef3c7" stroke="#fcd34d" stroke-width="1" />
  <text x="215" y="113" font-family="'Manrope', sans-serif" font-size="7" font-weight="800" fill="#92400e">SLIDING COLLUVIUM</text>"""


def _render_rotational_slump_svg(
    hatch_id: str,
    debris_id: str,
    dip_deg: int,
    cut_str: str,
    road_x_start: int,
    road_x_end: int,
    debris_road_x: int,
    road_y: int,
    formation_w: float,
    open_w: float,
) -> str:
    """Rotational Circular Slump with backward-tilted block and toe heave."""
    return f"""  <!-- In-situ Strata -->
  <path d="M 20 40 L 120 45 L 290 170 L 420 170 L 500 210 L 500 226 L 20 226 Z" fill="url(#{hatch_id})" stroke="#475569" stroke-width="1.2" />

  <!-- Circular Shear Arc Rupture Surface -->
  <path d="M 140 45 Q 180 145 295 170" fill="none" stroke="#dc2626" stroke-width="2.5" stroke-dasharray="5,3" />

  <!-- Rotated Backward-Tilted Slump Block -->
  <path d="M 140 45 Q 180 145 295 170 L {debris_road_x} 170 Q 260 135 155 58 Z" fill="#fef3c7" stroke="#d97706" stroke-width="1.4" />
  <path d="M 140 45 Q 180 145 295 170 L {debris_road_x} 170 Q 260 135 155 58 Z" fill="url(#{debris_id})" />

  <!-- Transverse Tension Cracks at Crown -->
  <path d="M 140 32 L 140 45 L 136 52" fill="none" stroke="#b91c1c" stroke-width="2.5" />
  <path d="M 115 38 L 115 45" fill="none" stroke="#b91c1c" stroke-width="1.8" />
  <path d="M 95 40 L 95 45" fill="none" stroke="#b91c1c" stroke-width="1.5" />

  <!-- Bulging Toe Ridge (Pressure Ridge on Road) -->
  <path d="M 290 170 Q {(290 + debris_road_x)//2} 150 {debris_road_x} 170 Z" fill="#d97706" opacity="0.85" />

  <!-- Reverse Tilt Indicator Arrow -->
  <path d="M 190 85 Q 180 75 165 78" fill="none" stroke="#7c2d12" stroke-width="1.5" marker-end="url(#arrow)" />
  <text x="195" y="88" font-family="'Manrope', sans-serif" font-size="7" font-weight="700" fill="#7c2d12">REVERSE TILT</text>

  <!-- Road Carriageway Pavement -->
  <rect x="{road_x_start}" y="168" width="{road_x_end - road_x_start}" height="5" fill="#334155" />

  <!-- Clogged Side Drain Box -->
  <polygon points="290,170 297,177 304,177 304,170" fill="#94a3b8" stroke="#1e293b" stroke-width="1" />
  <circle cx="297" cy="173" r="3" fill="#ef4444" opacity="0.9" />

  <!-- Cut Angle Indicator -->
  <path d="M 268 170 A 25 25 0 0 1 278 145" fill="none" stroke="#092f25" stroke-width="1.3" />
  <text x="236" y="147" font-family="'Manrope', sans-serif" font-size="8.5" font-weight="800" fill="#092f25">{cut_str}</text>

  <!-- Constriction Dimensions -->
  <line x1="{road_x_start}" y1="185" x2="{road_x_end}" y2="185" stroke="#0f172a" stroke-width="1" />
  <text x="325" y="195" font-family="'JetBrains Mono', monospace" font-size="7" font-weight="700" fill="#0f172a">Formation: {formation_w:.2f}m</text>

  <line x1="{debris_road_x}" y1="203" x2="{road_x_end}" y2="203" stroke="#16a34a" stroke-width="1.3" />
  <text x="365" y="213" font-family="'JetBrains Mono', monospace" font-size="7" font-weight="800" fill="#15803d">Open: {open_w:.2f}m</text>

  <!-- Callout Badges -->
  <rect x="25" y="10" width="112" height="15" rx="2" fill="#fee2e2" stroke="#f87171" stroke-width="1" />
  <text x="30" y="21" font-family="'Manrope', sans-serif" font-size="7" font-weight="800" fill="#991b1b">MAIN SCARP &amp; CRACKS</text>

  <rect x="110" y="100" width="115" height="15" rx="2" fill="#fee2e2" stroke="#f87171" stroke-width="1" />
  <text x="115" y="111" font-family="'Manrope', sans-serif" font-size="7" font-weight="800" fill="#991b1b">CIRCULAR SLIP ARC</text>

  <rect x="225" y="125" width="115" height="15" rx="2" fill="#fef3c7" stroke="#fcd34d" stroke-width="1" />
  <text x="230" y="136" font-family="'Manrope', sans-serif" font-size="7" font-weight="800" fill="#92400e">HEAVED TOE LOBE</text>"""


def _render_rockfall_topple_svg(
    hatch_id: str,
    debris_id: str,
    dip_deg: int,
    cut_str: str,
    road_x_start: int,
    road_x_end: int,
    debris_road_x: int,
    road_y: int,
    formation_w: float,
    open_w: float,
) -> str:
    """Rockfall and Columnar Toppling along Vertical Joints."""
    return f"""  <!-- Steep Rock Cliff Face -->
  <path d="M 20 25 L 180 30 L 220 30 L 260 170 L 420 170 L 500 210 L 500 226 L 20 226 Z" fill="url(#{hatch_id})" stroke="#475569" stroke-width="1.2" />

  <!-- Sub-vertical Columnar Joints -->
  <g stroke="#94a3b8" stroke-width="1.2" stroke-dasharray="4,3">
    <line x1="160" y1="30" x2="200" y2="170" />
    <line x1="200" y1="30" x2="240" y2="170" />
  </g>

  <!-- Open Detachment Tension Fissure -->
  <path d="M 218 30 L 235 110 L 245 155" fill="none" stroke="#dc2626" stroke-width="2.5" />

  <!-- Detached Toppling Column -->
  <polygon points="220,32 238,32 258,135 240,135" fill="#fef3c7" stroke="#d97706" stroke-width="1.4" />

  <!-- Falling Rock Boulders / Trajectory -->
  <g fill="#92400e" stroke="#451a03" stroke-width="1">
    <polygon points="255,110 265,108 268,118 257,120" />
    <polygon points="275,130 288,126 290,138 277,140" />
  </g>
  <path d="M 245 80 Q 275 105 285 150" fill="none" stroke="#f59e0b" stroke-width="1.5" stroke-dasharray="3,2" />

  <!-- Talus Scree Cone Burying Roadway -->
  <path d="M 255 170 L {debris_road_x} 170 L 275 145 Z" fill="#d97706" opacity="0.85" />
  <path d="M 255 170 L {debris_road_x} 170 L 275 145 Z" fill="url(#{debris_id})" />

  <!-- Road Carriageway Pavement -->
  <rect x="{road_x_start}" y="168" width="{road_x_end - road_x_start}" height="5" fill="#334155" />

  <!-- Cut Angle Indicator -->
  <path d="M 245 170 A 25 25 0 0 1 254 145" fill="none" stroke="#092f25" stroke-width="1.3" />
  <text x="215" y="147" font-family="'Manrope', sans-serif" font-size="8.5" font-weight="800" fill="#092f25">{cut_str}</text>

  <!-- Constriction Dimensions -->
  <line x1="{road_x_start}" y1="185" x2="{road_x_end}" y2="185" stroke="#0f172a" stroke-width="1" />
  <text x="325" y="195" font-family="'JetBrains Mono', monospace" font-size="7" font-weight="700" fill="#0f172a">Formation: {formation_w:.2f}m</text>

  <line x1="{debris_road_x}" y1="203" x2="{road_x_end}" y2="203" stroke="#16a34a" stroke-width="1.3" />
  <text x="365" y="213" font-family="'JetBrains Mono', monospace" font-size="7" font-weight="800" fill="#15803d">Open: {open_w:.2f}m</text>

  <!-- Callout Badges -->
  <rect x="25" y="10" width="125" height="15" rx="2" fill="#fee2e2" stroke="#f87171" stroke-width="1" />
  <text x="30" y="21" font-family="'Manrope', sans-serif" font-size="7" font-weight="800" fill="#991b1b">SUB-VERTICAL FISSURE</text>

  <rect x="145" y="55" width="120" height="15" rx="2" fill="#fee2e2" stroke="#f87171" stroke-width="1" />
  <text x="150" y="66" font-family="'Manrope', sans-serif" font-size="7" font-weight="800" fill="#991b1b">TOPPLING ROCK COLUMN</text>

  <rect x="235" y="102" width="115" height="15" rx="2" fill="#fef3c7" stroke="#fcd34d" stroke-width="1" />
  <text x="240" y="113" font-family="'Manrope', sans-serif" font-size="7" font-weight="800" fill="#92400e">TALUS SCREE CONE</text>"""


def _render_debris_flow_svg(
    hatch_id: str,
    debris_id: str,
    dip_deg: int,
    cut_str: str,
    road_x_start: int,
    road_x_end: int,
    debris_road_x: int,
    road_y: int,
    formation_w: float,
    open_w: float,
) -> str:
    """Channelized Debris Flow / Mudflow Fan."""
    return f"""  <!-- Mountain Gully & Bedrock Ribs -->
  <path d="M 20 30 L 100 40 L 200 90 L 290 170 L 420 170 L 500 210 L 500 226 L 20 226 Z" fill="url(#{hatch_id})" stroke="#475569" stroke-width="1.2" />

  <!-- Scoured Erosion Gully Chute -->
  <path d="M 90 35 Q 160 80 230 130 Q 270 155 295 170" fill="none" stroke="#0284c7" stroke-width="3" stroke-dasharray="6,2" />

  <!-- High-Velocity Slurry Runout Fan -->
  <path d="M 120 45 Q 180 95 240 135 L {debris_road_x} 170 L 310 170 Q 220 110 140 50 Z" fill="#fed7aa" stroke="#c2410c" stroke-width="1.4" />
  <path d="M 120 45 Q 180 95 240 135 L {debris_road_x} 170 L 310 170 Q 220 110 140 50 Z" fill="url(#{debris_id})" />

  <!-- Uprooted Timber / Boulder Clasts in Slurry -->
  <line x1="200" y1="115" x2="220" y2="125" stroke="#78350f" stroke-width="2.5" stroke-linecap="round" />
  <circle cx="215" cy="118" r="3.5" fill="#451a03" />
  <circle cx="250" cy="145" r="4.5" fill="#451a03" />
  <circle cx="280" cy="162" r="4" fill="#451a03" />

  <!-- Debris Lobe Overtopping Roadway -->
  <path d="M 285 170 Q {(290 + debris_road_x)//2} 152 {debris_road_x} 170 Z" fill="#ea580c" opacity="0.8" />

  <!-- Road Carriageway Pavement -->
  <rect x="{road_x_start}" y="168" width="{road_x_end - road_x_start}" height="5" fill="#334155" />

  <!-- Choked Culvert Box Indicator -->
  <rect x="290" y="170" width="14" height="8" fill="#64748b" stroke="#0f172a" stroke-width="1" />
  <rect x="292" y="172" width="10" height="4" fill="#ef4444" />

  <!-- Cut Angle Indicator -->
  <path d="M 268 170 A 25 25 0 0 1 278 145" fill="none" stroke="#092f25" stroke-width="1.3" />
  <text x="236" y="147" font-family="'Manrope', sans-serif" font-size="8.5" font-weight="800" fill="#092f25">{cut_str}</text>

  <!-- Constriction Dimensions -->
  <line x1="{road_x_start}" y1="185" x2="{road_x_end}" y2="185" stroke="#0f172a" stroke-width="1" />
  <text x="325" y="195" font-family="'JetBrains Mono', monospace" font-size="7" font-weight="700" fill="#0f172a">Formation: {formation_w:.2f}m</text>

  <line x1="{debris_road_x}" y1="203" x2="{road_x_end}" y2="203" stroke="#16a34a" stroke-width="1.3" />
  <text x="365" y="213" font-family="'JetBrains Mono', monospace" font-size="7" font-weight="800" fill="#15803d">Open: {open_w:.2f}m</text>

  <!-- Callout Badges -->
  <rect x="25" y="10" width="120" height="15" rx="2" fill="#e0f2fe" stroke="#38bdf8" stroke-width="1" />
  <text x="30" y="21" font-family="'Manrope', sans-serif" font-size="7" font-weight="800" fill="#0369a1">SCOURED GULLY CHUTE</text>

  <rect x="140" y="65" width="125" height="15" rx="2" fill="#fee2e2" stroke="#f87171" stroke-width="1" />
  <text x="145" y="76" font-family="'Manrope', sans-serif" font-size="7" font-weight="800" fill="#991b1b">BOULDER/MUD SURCHARGE</text>

  <rect x="235" y="102" width="118" height="15" rx="2" fill="#ffedd5" stroke="#fb923c" stroke-width="1" />
  <text x="240" y="113" font-family="'Manrope', sans-serif" font-size="7" font-weight="800" fill="#c2410c">DEBRIS RUNOUT LOBE</text>"""


def _render_wedge_failure_svg(
    hatch_id: str,
    debris_id: str,
    dip_deg: int,
    cut_str: str,
    road_x_start: int,
    road_x_end: int,
    debris_road_x: int,
    road_y: int,
    formation_w: float,
    open_w: float,
) -> str:
    """Structural Wedge Failure along intersecting joint sets J1 and J2."""
    return f"""  <!-- In-situ Rock Mass -->
  <path d="M 20 35 L 140 45 L 290 170 L 420 170 L 500 210 L 500 226 L 20 226 Z" fill="url(#{hatch_id})" stroke="#475569" stroke-width="1.2" />

  <!-- Intersecting Discontinuity Planes (J1 & J2) -->
  <g stroke="#94a3b8" stroke-width="1.2" stroke-dasharray="3,3">
    <line x1="120" y1="45" x2="270" y2="175" />
    <line x1="180" y1="45" x2="230" y2="185" />
  </g>

  <!-- Line of Intersection Daylighting (Trough Line) -->
  <line x1="150" y1="48" x2="295" y2="170" stroke="#dc2626" stroke-width="2.5" stroke-dasharray="5,3" />

  <!-- Detached Tetrahedral Wedge Mass -->
  <polygon points="150,48 210,95 {debris_road_x},170 290,170" fill="#fef3c7" stroke="#d97706" stroke-width="1.4" />
  <polygon points="150,48 210,95 {debris_road_x},170 290,170" fill="url(#{debris_id})" />

  <!-- Tension Crack at Wedge Apex -->
  <path d="M 150 36 L 150 48" fill="none" stroke="#b91c1c" stroke-width="2.5" />

  <!-- Road Carriageway Pavement -->
  <rect x="{road_x_start}" y="168" width="{road_x_end - road_x_start}" height="5" fill="#334155" />

  <!-- Clogged Drain Box -->
  <polygon points="290,170 297,177 304,177 304,170" fill="#94a3b8" stroke="#1e293b" stroke-width="1" />
  <circle cx="297" cy="173" r="3" fill="#ef4444" opacity="0.9" />

  <!-- Cut Angle Indicator -->
  <path d="M 268 170 A 25 25 0 0 1 278 145" fill="none" stroke="#092f25" stroke-width="1.3" />
  <text x="236" y="147" font-family="'Manrope', sans-serif" font-size="8.5" font-weight="800" fill="#092f25">{cut_str}</text>

  <!-- Constriction Dimensions -->
  <line x1="{road_x_start}" y1="185" x2="{road_x_end}" y2="185" stroke="#0f172a" stroke-width="1" />
  <text x="325" y="195" font-family="'JetBrains Mono', monospace" font-size="7" font-weight="700" fill="#0f172a">Formation: {formation_w:.2f}m</text>

  <line x1="{debris_road_x}" y1="203" x2="{road_x_end}" y2="203" stroke="#16a34a" stroke-width="1.3" />
  <text x="365" y="213" font-family="'JetBrains Mono', monospace" font-size="7" font-weight="800" fill="#15803d">Open: {open_w:.2f}m</text>

  <!-- Callout Badges -->
  <rect x="25" y="10" width="115" height="15" rx="2" fill="#fee2e2" stroke="#f87171" stroke-width="1" />
  <text x="30" y="21" font-family="'Manrope', sans-serif" font-size="7" font-weight="800" fill="#991b1b">WEDGE APEX CRACK</text>

  <rect x="110" y="65" width="125" height="15" rx="2" fill="#fee2e2" stroke="#f87171" stroke-width="1" />
  <text x="115" y="76" font-family="'Manrope', sans-serif" font-size="7" font-weight="800" fill="#991b1b">INTERSECTING JOINTS (J1xJ2)</text>

  <rect x="220" y="102" width="115" height="15" rx="2" fill="#fef3c7" stroke="#fcd34d" stroke-width="1" />
  <text x="225" y="113" font-family="'Manrope', sans-serif" font-size="7" font-weight="800" fill="#92400e">SLIDING WEDGE MASS</text>"""
