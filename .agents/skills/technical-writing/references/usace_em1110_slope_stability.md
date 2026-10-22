# USACE EM 1110-2-1902: Slope Stability & Geotechnical Investigation
### External Standard 1 for Technical Writing & Engineering Reporting

Sourced from the U.S. Army Corps of Engineers (USACE) Engineer Manual **EM 1110-2-1902** (*Slope Stability*) and **EM 1110-1-1804** (*Geotechnical Investigations for Engineering Reports*).

---

## 1. Static Equilibrium Analysis & Factor of Safety Criteria

USACE mandates that all slope stability assessments for civil infrastructure must satisfy complete static equilibrium (both force and moment equilibrium):

### A. Approved Limit Equilibrium Methods
- **Spencer's Method:** Satisfies all conditions of static equilibrium (forces and moments) assuming parallel interslice force inclinations. Applicable to general circular and non-circular slip surfaces.
- **Morgenstern-Price Method:** Satisfies all equilibrium conditions with variable interslice force function $f(x)$ relating interslice shear to normal forces ($X = \lambda \cdot f(x) \cdot E$). Preferred for complex composite shear surfaces with strong contrast between colluvium and bedrock.
- *Strict USACE Ban:* Simplified Ordinary Method of Slices (Fellenius) is prohibited for final engineering design due to extreme numerical conservatism in deep slip surfaces and numerical error in high pore-pressure regimes.

### B. Standard Factor of Safety ($FOS$) Benchmarks
Reports must evaluate and explicitly report the $FOS$ against the following standard loading conditions:
1. **End-of-Construction / Dry Baseline:** $FOS \ge 1.50$ (Static, uninhibited condition).
2. **Maximum Continuous Seepage / Monsoon Saturated:** $FOS \ge 1.30$ to $1.40$ (Steady-state phreatic surface developed from peak rainfall infiltration).
3. **Rapid Drawdown / Runoff Surge:** $FOS \ge 1.20$ to $1.30$ (Rapid removal of external stabilizing water pressure while high pore pressure remains trapped in the slope).
4. **Pseudo-Static Earthquake Condition:** $FOS \ge 1.10$ to $1.15$ with design horizontal seismic coefficient $\alpha_h$.

---

## 2. Pore Water Pressure Parameterization ($r_u$ and Phreatic Profiles)

When reporting groundwater conditions in geotechnical reports, USACE forbids generic statements like *"groundwater is present"*. Instead, reports must specify:
1. **Pore Pressure Ratio ($r_u$):**
   $$r_u = \frac{u}{\gamma \cdot h}$$
   Where $u$ is pore water pressure, $\gamma$ is total unit weight, and $h$ is depth to slip surface.
   - Dry conditions: $r_u = 0.0$.
   - Moderate seepage: $r_u = 0.15 - 0.25$.
   - Severe monsoon saturation with artesian head in fractured bedrock: $r_u \ge 0.40 - 0.50$.
2. **Piezometric Phreatic Surface Line:** Plotted explicitly on cross-sections indicating observed steady-state vs transient perched water tables.

---

## 3. USACE Geotechnical Reporting Protocol

Under EM 1110-1-1804, a professional geotechnical investigation dossier must follow a strict five-part sequence:
1. **Site Physiography & Geomorphology:** Regional geology, slope inclination, drainage divide, rock outcrop mapping.
2. **Subsurface Exploration Data:** Drill hole logs, core recovery ratio ($CRR$), Rock Quality Designation ($RQD$), Standard Penetration Test ($N$-values).
3. **Material Property Justification:** Clear derivation of Mohr-Coulomb shear parameters ($c', \phi'$) from triaxial shear ($CU/CD$), direct shear, or calibrated empirical back-analysis.
4. **Critical Slip Surface Delineation:** Coordinates of entry point (crown scarp), exit point (toe breakout), and radius/curvature of critical slip boundary.
5. **Remediation Calculations:** Quantitative verification that the proposed engineered intervention restores $FOS$ to the statutory threshold ($\ge 1.50$).
