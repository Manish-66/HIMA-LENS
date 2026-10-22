---
name: technical-writing
description: "Use whenever drafting, structuring, reviewing, or polishing engineering reports, statutory technical dossiers, Preliminary Project Reports (PPR), Detailed Project Reports (DPR), standard operating procedures (SOP), or geotechnical hazard documentation. Enforces rigorous technical register, SI engineering units, standard citations (USACE, FHWA, Eurocode 7, CIRIA, ASCE/IEEE, CEDD, Klima 2050, IS, IRC, MoRTH), structured tables, and unambiguous professional prose."
---

# Technical Writing & Engineering Dossier Guardrails
### Master Standard for Himalayan Geotechnical & Infrastructure Dossiers

This skill enforces world-class technical precision, statutory structure, and engineering physics integrity across all generated geotechnical reports, project proposals, and Preliminary Project Reports (PPR).

It is strictly trained on and governed by **five external global engineering standards** in addition to statutory Indian codes and regional climate research:

```
AUTHORITATIVE GLOBAL ENGINEERING FOUNDATIONS
├── 1. USACE EM 1110-2-1902 & EM 1110-1-1804 (U.S. Army Corps of Engineers)
│   └── Rigorous limit equilibrium stability (Spencer / Morgenstern-Price), pore pressure ratio (r_u), and FOS criteria.
├── 2. FHWA-NHI-14-007 (GEC 7) & FHWA-NHI-11-032 (Federal Highway Administration)
│   └── Mountain highway slope remediation, soil nail pullout capacity (q_u), strip drainage, and LRFD load factors.
├── 3. Eurocode 7: EN 1997-1 & EN 1997-2 (European Committee for Standardization)
│   └── Dual-report architecture: Ground Investigation Report (GIR) vs Geotechnical Design Report (GDR), characteristic (X_k) vs design (X_d) parameters, and GEO/STR/HYD/SLS limit states.
├── 4. CIRIA C551 & C765 (Construction Industry Research and Information Association, UK)
│   └── 4-Pillar Conceptual Ground Models (CGM) and standardized Geotechnical Risk Registers (GRR).
└── 5. ASCE GSP 180 & IEEE 26514 (American Society of Civil Engineers & IEEE)
    └── 3-Tier epistemic delineation (Facts vs Inferences vs Recommendations), calibrated engineering confidence, SI discipline, and statutory limitation disclaimers.

ADDITIONAL CORE REGIONAL FOUNDATIONS
├── CEDD Geotechnical Engineering Office (Hong Kong) — LPMitP ALARP risk reduction, GEO Pub 1/2009 prescriptive measures, Kwan 2012 debris barriers.
├── Klima 2050 (Norway / NGI / NTNU) — Hydro-meteorological slope failure mechanics, matric suction loss, and catchment-scale runoff interception.
└── Indian Statutory Codes (BIS / IRC / MoRTH / HPPWD) — IS:14458, IS:1893 (Zone IV/V), IRC:SP:48, MoRTH (5th Rev), and HPSOR 2024-25.
```

---

## 1. The Three-Tier Epistemic Delineation (ASCE GSP 180)

To prevent liability, ambiguity, and technical conflation, every section of an engineering report must strictly separate its content into three epistemic tiers:

1. **Tier 1: Factual Observations (Direct Physical Ground Truth)**
   - Only physical observations directly measured, surveyed, photographed, or logged in telemetry.
   - *Syntax:* Objective past passive.
   - *Example:* *"At Station Km 124+800, a detachment scarp of vertical height $2.40\text{ m}$ and transverse width $18.5\text{ m}$ was surveyed. Angular phyllite fragments ($D_{50} = 0.35\text{ m}$) encroached upon $5.20\text{ m}$ of the two-lane carriageway."*

2. **Tier 2: Inferences & Interpretations (Geotechnical Analysis)**
   - Analytical deductions, failure mechanics, and parameter back-analyses derived from Tier 1 facts.
   - *Syntax:* Calibrated engineering confidence stating methodology and tools.
   - *Example:* *"Based on the surveyed scarp inclination of $64^\circ$ and the presence of saturated slickenlines along the basal boundary, the failure is interpreted as a translational debris slide along a pre-existing bedding plane ($dip\text{ }42^\circ / strike\text{ }210^\circ$). Under saturated conditions ($r_u = 0.35$), the calculated static factor of safety is $0.92$, confirming active mobilization."*

3. **Tier 3: Recommendations & Statutory Directives (Action Plan)**
   - Concrete, code-compliant remediation specifications, bills of quantities, and civil works schedules.
   - *Syntax:* Imperative technical directives citing statutory design codes.
   - *Example:* *"It is recommended that a $4.50\text{ m}$ high plum concrete gravity breast wall (complying with IS:14458 Part 2 and MoRTH Section 1000) be constructed along the toe, supported by three rows of sub-horizontal perforated PVC drains ($\phi 75\text{ mm}$) inclined at $5\%$ into the bedrock."*

---

## 2. Factor of Safety & Limit Equilibrium Rules (USACE EM 1110-2-1902)

When evaluating or reporting slope stability:
- **Mandatory Equilibrium Methods:** Limit equilibrium stability must satisfy both force and moment equilibrium (Spencer's or Morgenstern-Price methods).
- **Statutory FOS Thresholds:**
  - Dry / Static Baseline: $FOS \ge 1.50$
  - Monsoon Saturated Steady-Seepage: $FOS \ge 1.30$ to $1.40$
  - Sudden Drawdown / Storm Runoff Surge: $FOS \ge 1.20$
  - Pseudo-Static Seismic (Zone IV/V, $\alpha_h = 0.12 - 0.18$): $FOS \ge 1.15$
- **Pore Water Pressure Reporting:** Forbid vague descriptions like *"wet soil"*. Always report the pore pressure ratio $r_u = \frac{u}{\gamma h}$ or the explicitly modeled phreatic elevation.

---

## 3. Highway Soil Nailing & Remediation Rules (FHWA-NHI-14-007)

When reporting soil nailing or highway slope remediation:
- **Tendon Sizing:** State bar diameter ($\phi 25\text{mm}-32\text{mm}$), steel grade (Fe500D / ASTM A615 Grade 75), and drillhole diameter ($100\text{mm}-150\text{mm}$).
- **Pullout Resistance ($q_u$):** Report unit bond capacity ($r_{po} = \pi D_d q_u$) with lithological justification (e.g., $q_u = 120\text{ kPa}$ in weathered schist; $80\text{ kPa}$ in colluvium).
- **Subsurface Strip Drainage:** Specify $300\text{mm}-450\text{mm}$ wide prefabricated geocomposite drainage strips placed directly against the slope face prior to shotcreting, spaced at $1.5\text{m}-2.0\text{m}$ intervals.
- **Mandatory Verification Testing:** Mandate sacrificial verification pullout tests ($2.0\times$ design load) and proof tests on $5\%$ of production nails ($1.5\times$ design load held for 10 minutes, creep $< 1.0\text{mm}$).

---

## 4. Dual-Report Architecture (Eurocode 7 EN 1997-1 / EN 1997-2)

Technical dossiers must enforce the Eurocode 7 separation:
- **Ground Investigation Report (GIR):** Telemetry, optical plates, lithology, joint dip/strike, precipitation logs, and raw derived parameters.
- **Geotechnical Design Report (GDR):** Derivation of characteristic parameters ($X_k$), application of partial safety factors ($\gamma_m = 1.25$ for $c'$ and $\tan\phi'$), verification of **GEO** (ground failure), **STR** (structural component rupture), **HYD** (hydraulic heave/piping), and **SLS** (allowable lateral deflection $\delta_h \le 0.003H$).

---

## 5. Conceptual Ground Models & Risk Registers (CIRIA C551 & C765)

Every Preliminary Project Report (PPR) must include:
1. **4-Pillar Conceptual Ground Model (CGM):**
   - *Geomorphology:* Catchment slope angle, scarp aspect, and terrain morphology.
   - *Lithology:* Colluvium thickness, bedrock weathering grade (Grade I to VI), joint sets.
   - *Hydrogeology:* Surface runoff concentration, springs, transient seepage boundaries.
   - *Anthropogenic Triggers:* Hill cutting for road expansion, unlined drains, surcharge.
2. **Standardized Geotechnical Risk Register (GRR Table):**
   - Probability ($L: 1-5$) $\times$ Consequence Severity ($S: 1-5$) = Total Risk Score ($1-25$).
   - Explicit identification of receptors (Traffic passengers, pavement, utilities), pre-mitigation risk, prescribed intervention, post-mitigation risk, and statutory action owner (e.g., Executive Engineer HPPWD).

---

## 6. Official 10-Chapter HPPWD PPR Report Architecture

Directly aligned with `PPR Format (HPPWD).docx` and our 5 external standards:

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

## 7. Deep Reference Library

Consult the companion reference dossiers in `.agents/skills/technical-writing/references/`:
1. [`usace_em1110_slope_stability.md`](file:///d:/MTP-main%20-%20Copy/.agents/skills/technical-writing/references/usace_em1110_slope_stability.md) — USACE limit equilibrium and pore-water pressure rules.
2. [`fhwa_gec7_highway_slopes.md`](file:///d:/MTP-main%20-%20Copy/.agents/skills/technical-writing/references/fhwa_gec7_highway_slopes.md) — FHWA highway slope stabilization, soil nail testing, and LRFD factors.
3. [`eurocode7_gir_gdr_standards.md`](file:///d:/MTP-main%20-%20Copy/.agents/skills/technical-writing/references/eurocode7_gir_gdr_standards.md) — Eurocode 7 GIR/GDR architecture and characteristic parameters.
4. [`ciria_c551_conceptual_ground_models.md`](file:///d:/MTP-main%20-%20Copy/.agents/skills/technical-writing/references/ciria_c551_conceptual_ground_models.md) — CIRIA Conceptual Ground Models and Geotechnical Risk Registers.
5. [`asce_ieee_technical_reporting.md`](file:///d:/MTP-main%20-%20Copy/.agents/skills/technical-writing/references/asce_ieee_technical_reporting.md) — ASCE/IEEE Three-Tier Epistemic Delineation and statutory disclaimers.
6. [`cedd_geo_standards.md`](file:///d:/MTP-main%20-%20Copy/.agents/skills/technical-writing/references/cedd_geo_standards.md) — CEDD GEO LPMitP and prescriptive slope measures.
7. [`klima2050_hydro_mechanics.md`](file:///d:/MTP-main%20-%20Copy/.agents/skills/technical-writing/references/klima2050_hydro_mechanics.md) — Klima 2050 hydro-meteorological slope failure mechanics.
8. [`is_irc_morth_codes.md`](file:///d:/MTP-main%20-%20Copy/.agents/skills/technical-writing/references/is_irc_morth_codes.md) — Statutory Indian Codes (BIS, IRC, MoRTH, HPSOR).
9. [`cruden_varnes_taxonomy.md`](file:///d:/MTP-main%20-%20Copy/.agents/skills/technical-writing/references/cruden_varnes_taxonomy.md) — Kinematic Landslide Taxonomy and velocity scales.
10. [`larimit_mitigation_toolbox.md`](file:///d:/MTP-main%20-%20Copy/.agents/skills/technical-writing/references/larimit_mitigation_toolbox.md) — LaRiMiT decision matrices for structural and non-structural countermeasures.
