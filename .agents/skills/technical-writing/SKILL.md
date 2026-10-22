---
name: technical-writing
description: "Use whenever drafting, structuring, reviewing, or polishing engineering reports, statutory technical dossiers, Preliminary Project Reports (PPR), Detailed Project Reports (DPR), standard operating procedures (SOP), or geotechnical hazard documentation. Enforces rigorous technical register, SI engineering units, standard citations (IS, IRC, MoRTH), structured tables, and unambiguous professional prose."
---

# Technical Writing & Engineering Dossier Guardrails

This skill enforces high-precision engineering prose, statutory structure, and rigorous technical communication standards across all generated reports, project proposals, and technical documentation.

---

## 1. Core Principles of Technical Writing

1. **Objective Impersonal Register:**
   - Write in formal third-person passive or impersonal voice (*"A planar failure was observed..."*, *"The prescribed stabilization schedule comprises..."*).
   - Ban colloquialisms, emotional hyperbole, conversational fluff, and hand-waving (*"huge landslide"*, *"very dangerous"*, *"a lot of debris"*).
   - Use precise geotechnical/structural qualifiers: *"Unconsolidated debris accumulation ($\approx 420\text{ m}^3$) encroaching upon $6.5\text{ m}$ of the two-lane carriageway"*.

2. **Unambiguous Quantitative Specificity:**
   - Every physical observation must include quantified estimates or measured ranges:
     - **Chainage:** E.g., `Km 124.800` or `Chainage 12+450`.
     - **Coordinates:** WGS84 decimal degrees ($31.77271^\circ\text{ N}, 76.98416^\circ\text{ E}$) and DMS.
     - **Slope Geometry:** Slope height ($H\text{ in meters}$), slope inclination ($\beta\text{ in degrees } ^\circ$), scarp depth ($z\text{ in meters}$).
     - **Material Sizing:** $D_{50}$ boulder diameters, matrix gravel/sand/silt percentages.
     - **Discharge/Hydrology:** Flow rate ($\text{m}^3/\text{s}$), rainfall intensity ($\text{mm/hr}$), antecedent saturation.

3. **Standard Statutory & Academic Citations:**
   Always ground remediation, design, and investigations in relevant statutory codes:
   - **IS:14458 (Parts 1–4):** Guidelines for design and construction of retaining walls for hill roads.
   - **IRC:SP:48:** Hill Road Manual (Indian Roads Congress).
   - **MoRTH Specifications (5th Revision):** Specifications for Road and Bridge Works (Section 300, 1000, 1100).
   - **IS:1893 (Part 1):** Criteria for Earthquake Resistant Design of Structures (Seismic Zone IV/V for Himachal Pradesh).
   - **Disaster Management Act 2005 & NDMA Guidelines:** Management of Landslides and Snow Avalanches.
   - **Cruden & Varnes (1996) / USGS Circular 1325:** Kinematic Landslide Taxonomy.

---

## 2. Preliminary Project Report (PPR) Architecture

When drafting or rendering a Preliminary Project Report (PPR) for HPPWD or disaster authorities:

### A. Cover & Statutory Title Header
- **Document Title:** Preliminary Project Report (PPR) on Slope Stabilization & Hazard Remediation.
- **Client / Sponsoring Agency:** E.g., Himachal Pradesh Public Works Department (HPPWD), Government of Himachal Pradesh.
- **Executing / Investigating Agency:** Indian Institute of Technology Mandi (IIT Mandi).
- **Date & Statutory Reference Code:** E.g., `IITM-CR-XXXX` or `PPR/HPPWD/MND/2026/XX`.

### B. Salient Features Matrix (Mandatory Table)
Every PPR must open with an executive salient features matrix:
| S. No. | Parameter | Specific Field Detail |
| :--- | :--- | :--- |
| 1 | **Project Title** | Remediation & Slope Stabilization at [Road Name / Location] |
| 2 | **Project Location** | Village/City, Block, District, State, GPS Coordinates |
| 3 | **Executing Division** | HPPWD National Highway / State Highway Division |
| 4 | **Duration of Project** | E.g., 6 Months / 12 Months (including pre-monsoon execution) |
| 5 | **Hazard to be Mitigated** | Cruden & Varnes classification (e.g., Active Translational Debris Slide) |
| 6 | **Methodology** | Field telemetry, drone photogrammetry, limit equilibrium stability analysis |
| 7 | **Remediation Category** | Integrated Structural & Non-Structural Countermeasures |

### C. Standard 10-Point Technical Chapters
1. **1. General:** Background, geographical setting, regional connectivity importance, vulnerability context.
2. **2. History & Project Overview:** Failure chronology, historical reactivation cycles, seasonal triggers.
3. **3. Location Map & Terrain Setting:** Catchment morphology, elevation profile, road cut geometry, optical aerial plates.
4. **4. Hazard Profile of Project Site:** Structural geological audit, discontinuity orientation, joint sets, groundwater seepage, Lithological unit (Bhukosh / GSI).
5. **5. Project Rationale:** Socio-economic justification, lifeline road vulnerability, disruption to tourism, horticulture, and essential supplies.
6. **6. Risk Assessment:** Multi-criteria vulnerability assessment (Loss of life risk, economic infrastructure damage valuation, secondary damming hazards).
7. **7. Stakeholder Analysis:** Roles of HPPWD, District Administration / DDMA, Police/Traffic management, Local communities, Contractors.
8. **8. Mitigation Measures (Structural & Non-Structural):**
   - *Structural:* Plum concrete gravity walls, gabion stone revetments, self-drilling soil nails, high-tensile wire mesh netting, horizontal bore drains.
   - *Non-Structural:* Bio-engineering (Vetiver grass, hydro-seeding), surface catchwater interception drains, early warning crack sensors.
9. **9. Project Activities & Work Breakdown (WBS):** Phase I (Site investigation & earthworks), Phase II (Subsurface drainage & foundation), Phase III (Structural installation), Phase IV (Bio-engineering & audit).
10. **10. Implementation Plan & Milestones:** Chronological schedule, pre-monsoon target completion window, statutory engineering sign-off.
11. **Disclaimer:** Statutory technical limitation notice regarding geotechnical subsurface variability and physical validation.

---

## 3. Formatting & Visual Hierarchy Standards

- **Headings:** Decimal hierarchical numbering (`1.`, `1.1`, `1.1.1`). Never jump levels.
- **Tables:** 
  - Every table must have a concise title and standard column alignments (Text: left; Numbers/Amounts: right; Codes/Sl: center).
  - Explicit units in column headers (e.g., `Length (m)`, `Volume (m³)`, `Rate (₹/m³)`).
- **Callouts & Notes:**
  - `CRITICAL DIRECTIVE`: For immediate life-safety closures or severe instability alerts.
  - `STATUTORY CODE`: Highlighting compliance with IS/IRC mandates.
- **Language Verification:**
  - Avoid split infinitives or ambiguous pronoun references (*"it was determined"*, clarify what "it" represents).
  - Use standardized civil terms: *carriageway*, *formation width*, *toe erosion*, *scarp*, *colluvium*, *weep holes*, *catchwater drain*.
