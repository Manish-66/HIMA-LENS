---
name: technical-writing
description: "Use whenever drafting, structuring, reviewing, or polishing engineering reports, statutory technical dossiers, Preliminary Project Reports (PPR), Detailed Project Reports (DPR), standard operating procedures (SOP), or geotechnical hazard documentation. Enforces rigorous technical register, SI engineering units, standard citations (IS, IRC, MoRTH, CEDD, Klima 2050, USGS), structured tables, and unambiguous professional prose."
---

# Technical Writing & Engineering Dossier Guardrails
### Master Standard for Himalayan Geotechnical & Infrastructure Dossiers

This skill enforces world-class technical precision, statutory structure, and engineering physics integrity across all generated geotechnical reports, project proposals, and Preliminary Project Reports (PPR).

It is strictly grounded in **five authoritative international and national engineering standards**:
1. **CEDD Geotechnical Engineering Office (Hong Kong):** Landslip Prevention and Mitigation Programme (LPMitP), GEO Publication No. 1/2009 (*Prescriptive Measures for Man-Made Slopes and Retaining Walls*), GEO Report No. 299 (*Flexible Debris Barriers*), Geoguide 1 & Geoguide 5 (*Slope Practice & Inspections*).
2. **Klima 2050 (Norway / NGI / NTNU):** Work Package 3 (*Landslides Triggered by Hydro-Meteorological Processes*), effective stress pore-pressure surge dynamics, unsaturated matric suction loss, and catchment-scale water management.
3. **USGS Circular 1325 (Highland & Bobrowsky) & Cruden & Varnes (1996):** International kinematic landslide classification, morphological anatomy, and standard velocity scales.
4. **Bureau of Indian Standards (BIS) & Indian Roads Congress (IRC):** IS:14458 (*Retaining Walls for Hill Roads*, Parts 1–4), IS:1893 (*Seismic Criteria for Zone IV/V*), and IRC:SP:48 (*Hill Road Manual*).
5. **MoRTH Specifications (5th Revision) & HPPWD Technical Code (HPSOR 2024-25):** Standard civil remediation specifications, rate schedules, plum concrete, and gabion wire revetments.

---

## 1. Mandatory Technical Register & Writing Discipline

### A. Impersonal Objective Engineering Voice
- Write strictly in third-person impersonal or passive voice:
  - *Correct:* "A planar translational failure was observed within the unconsolidated colluvium."
  - *Incorrect:* "We noticed a big slide on the road."
- Eliminate colloquialisms, hand-waving, and sensationalist adjectives:
  - Banned terms: *huge*, *massive*, *very dangerous*, *a lot of dirt*, *terrible crash*, *soon*.
  - Approved terms: *active translational slump*, *unconsolidated colluvial debris ($\approx 420\text{ m}^3$)*, *high-consequence slope sector*, *encroaching $6.5\text{ m}$ onto the formation width*.

### B. Dimensional & Quantitative Rigor
Never describe a physical parameter without numerical dimensions or SI units:
- **Chainage:** E.g., `Km 124.800 (NH-154)` or `Chainage 12+450`.
- **Coordinates:** WGS84 decimal degrees ($31.77271^\circ\text{ N}, 76.98416^\circ\text{ E}$) accompanied by Degree-Minute-Second (DMS) string.
- **Slope Geometry:** Slope height ($H\text{ in meters}$), inclination ($\beta\text{ in degrees } ^\circ$), scarp depth ($z\text{ in meters}$), aspect/azimuth.
- **Discharge / Hydrology:** Flow rate ($\text{m}^3/\text{s}$), 24-hour antecedent rainfall ($\text{mm}$), hydraulic gradient.
- **Geotechnical Properties:** Unit weight ($\gamma\text{ in kN/m}^3$), effective cohesion ($c'\text{ in kPa}$), effective friction angle ($\phi'\text{ in degrees } ^\circ$).

---

## 2. Technical Taxonomy Standards

### A. Cruden & Varnes (1996) Movement Taxonomy
Every failure must be categorized strictly by **Material** + **Movement**:
- **Materials:** `Rock`, `Debris` (coarse soil $>20\%$ gravel), `Earth` (fine soil $>80\%$ fines).
- **Movement:** `Fall`, `Topple`, `Slide (Rotational)`, `Slide (Translational)`, `Lateral Spread`, `Flow`.
- *Example:* `Translational Debris Slide`, `Channelized Debris Flow`, `Rotational Rock Slump`.

### B. Morphological Terminology (USGS Circular 1325)
Standardized naming of failure components:
`Crown`, `Main Scarp`, `Flanks (Left/Right)`, `Surface of Rupture`, `Displaced Mass`, `Toe of Rupture`, `Toe of Surface of Separation`, `Accumulation Zone`, `Transverse Fissures`, `Tension Cracks`.

### C. Hydro-Mechanics Terminology (Klima 2050)
- **Matric Suction Loss:** Reduction of negative pore pressure $(u_a - u_w)$ during wetting front infiltration.
- **Pore Water Pressure Surge ($u > 0$):** Development of transient positive pore pressure reducing effective stress ($\sigma' = \sigma - u$).
- **Antecedent Precipitation Index (API):** Pre-storm cumulative moisture saturation conditioning the slope.
- **Preferential Seepage Paths:** Water concentration along bedrock-colluvium interfaces or joint planes.

### D. Prescriptive Stabilization (CEDD GEO Publication 1/2009)
- **Prescriptive Soil Nailing:** Sub-horizontal drillholes ($10^\circ-20^\circ$ downward inclination), $\phi 25\text{mm}-32\text{mm}$ high-yield steel bars, cementitious grout ($f_{cu} \ge 30\text{ MPa}$), diamond grid ($1.5\text{m}\times 1.5\text{m}$ to $2.0\text{m}\times 2.0\text{m}$).
- **Sub-horizontal Drains:** Perforated HDPE/uPVC ($\phi 75\text{mm}$), minimum $5\%$ upward gradient, geotextile wrapped.
- **Flexible Barriers (Kwan 2012 / GEO 299):** High-tensile steel ring nets ($1770\text{ MPa}$), energy absorption ($500\text{ kJ}-5000\text{ kJ}$), brake rings.

---

## 3. Preliminary Project Report (PPR) Architecture

When producing or updating an official Preliminary Project Report (PPR) for HPPWD:

```
├── COVER / STATUTORY TITLE HEADER
│   ├── Document Title: Preliminary Project Report on Slope Stabilization & Hazard Remediation
│   ├── Client: Himachal Pradesh Public Works Department (HPPWD), Govt. of Himachal Pradesh
│   ├── Investigating / Academic Agency: Indian Institute of Technology Mandi (IIT Mandi)
│   └── Statutory Reference: IITM-CR-XXXX
│
├── SALIENT FEATURES MATRIX (MANDATORY TABLE 1)
│   ├── S. No. | Parameter | Specific Field Detail
│   ├── 1. Project Title: Remediation & Slope Stabilization of [Road Name / Location]
│   ├── 1. Project Location: Village/City, Block, District, State, GPS Coordinates
│   ├── 2. Duration of Project: E.g., 6 Months (Pre-Monsoon Fast-Track Completion)
│   ├── 3. Hazard to be Mitigated: Standard Cruden & Varnes Classification
│   ├── 4. Methodology to Mitigate Hazard: Limit equilibrium stability analysis, field telemetry, GSI Bhukosh audit
│   └── 5. Mitigation Measure: Integrated Structural & Non-Structural Countermeasures
│
└── 10 NUMBERED TECHNICAL CHAPTERS
    ├── 1. General (Regional connectivity, corridor importance, mountain terrain context)
    ├── 2. History, Salient Features & Project Overview (Historical failure recurrence, monsoon triggers)
    ├── 3. Location Map & Terrain Setting (Georeferenced site plate, slope cut geometry, drainage basin)
    ├── 4. Hazard Profile of Project Site (Geological lithology, joint sets, pore pressure, seepage)
    ├── 5. Project Rationale (Lifeline corridor vulnerability, public safety, economic disruption)
    ├── 6. Risk Assessment (Vulnerability matrix, infrastructure loss audit, secondary hazards)
    ├── 7. Stakeholder Analysis (HPPWD, DDMA, Traffic Police, Local Community, Contractors)
    ├── 8. Mitigation Measures (Structural: retaining walls, soil nailing, drainage; Non-Structural: bio-engineering, early warning)
    ├── 9. Project Activities & Work Breakdown (Phase I to Phase IV execution steps)
    ├── 10. Implementation Plan & Milestones (Pre-monsoon schedule, civil works Gantt timeline)
    └── Statutory Disclaimer Notice (Geotechnical subsurface variability and physical validation limits)
```

---

## 4. Technical Writing Quality Checklist

Before finalizing any report or dossier, verify:
- [ ] **Zero Hyperbole:** No emotional adjectives; all hazard levels justified by physical criteria.
- [ ] **Quantified Geometry:** Slope height, angle, failure volume, and chainage explicitly stated.
- [ ] **Dual Taxonomy:** Landslide classification uses Cruden & Varnes material + kinematics.
- [ ] **Hydro-Mechanical Grounding:** Explains failure through effective stress and pore water pressure (Klima 2050).
- [ ] **Statutory Standards Cited:** References IS:14458, IRC:SP:48, MoRTH 5th Rev, and CEDD GEO Publication 1/2009.
- [ ] **Balanced Mitigation:** Combines structural countermeasure (wall/nails), hydraulic control (drains), and bio-engineering.
- [ ] **Standard Table Formats:** Left-aligned text, right-aligned numbers and currency, explicit units in column headers.
- [ ] **Institutional Framing:** Explicitly credited to Indian Institute of Technology Mandi (IIT Mandi) and HPPWD without deprecated acronyms.
