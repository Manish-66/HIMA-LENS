# Eurocode 7 (EN 1997-1 & EN 1997-2): GIR & GDR Architecture
### External Standard 3 for Technical Writing & Engineering Reporting

Sourced from the European Committee for Standardization (CEN) standard **EN 1997-1** (*Eurocode 7: Geotechnical design — Part 1: General rules*) and **EN 1997-2** (*Part 2: Ground investigation and testing*).

---

## 1. Dual-Report Structural Architecture

Eurocode 7 establishes the most rigorous international reporting structure by strictly dividing documentation into two distinct deliverables:

```
EUROCODE 7 REPORTING ARCHITECTURE
├── 1. GROUND INVESTIGATION REPORT (GIR) [EN 1997-2]
│   ├── Part 1: Factual Account of All Field & Laboratory Work
│   │   ├── Borehole / trial pit logs, optical evidence, chainage survey
│   │   ├── Ground water level records, in-situ testing data
│   │   └── Factual lab test certificates (moisture, grading, direct shear)
│   └── Part 2: Geotechnical Evaluation of Information
│       ├── Geological review, geomorphological interpretation
│       ├── Identification of anomalous or unfavorable ground conditions
│       └── Derived values of parameters with stated uncertainties
│
└── 2. GEOTECHNICAL DESIGN REPORT (GDR) [EN 1997-1]
    ├── Cross-reference to GIR (binding factual baseline)
    ├── Structural actions (permanent, variable, environmental, seismic)
    ├── Derivation of Characteristic Values ($X_k$) from derived values
    ├── Selection of Partial Factors ($\gamma_m, \gamma_F, \gamma_R$) per Design Approach
    ├── Verification of Ultimate Limit States (GEO, STR, EQU, UPL, HYD)
    ├── Verification of Serviceability Limit States (SLS deformations)
    └── Supervision, Monitoring & Maintenance Plan
```

---

## 2. Derivation of Characteristic vs Design Parameter Values

In technical reporting, Eurocode 7 strictly forbids confusing measured values, characteristic values, and design values:

1. **Derived Value ($X_{derived}$):** The raw laboratory or empirical property directly calculated from test data (e.g., laboratory triaxial friction angle $\phi'_{lab} = 32.4^\circ$).
2. **Characteristic Value ($X_k$):** A cautious estimate of the value affecting the occurrence of the limit state:
   - For a failure surface involving a large volume of ground (spatial averaging across the sliding body): $X_k$ is the **mean value** with a $95\%$ statistical confidence interval.
   - For localized failure (e.g., single nail pullout or toe punching): $X_k$ is the **lower $5\%$ fractile value**.
3. **Design Value ($X_d$):** The characteristic value divided by the statutory partial material safety factor:
   $$X_d = \frac{X_k}{\gamma_m}$$
   Where partial factors under Design Approach 1 (DA1) / Design Approach 2 (DA2) are:
   - Shearing resistance tangent: $\gamma_{\phi'} = 1.25$.
   - Effective cohesion: $\gamma_{c'} = 1.25$.
   - Undrained shear strength: $\gamma_{cu} = 1.40$.
   - Weight density: $\gamma_\gamma = 1.00$.

---

## 3. Mandatory Limit State Checks in the Technical Report

Every slope engineering calculation in the report must formally report verification against the standard Eurocode limit states:
- **GEO Limit State:** Failure or excessive deformation of the ground (slope sliding along rotational or planar shear surface).
  $$\sum E_d \le \sum R_d$$
- **STR Limit State:** Internal failure or excessive deformation of the structural elements (bending rupture of retaining wall stem, shear failure of soil nail rebar, tearing of wire mesh netting).
- **HYD Limit State:** Hydraulic heave, internal erosion, or piping caused by hydraulic gradients (seepage discharge along slope toe).
- **SLS Limit State:** Post-construction displacement verification (horizontal crest lateral deflection $\delta_h \le 0.003H$; carriageway vertical settlement $\delta_v \le 25\text{ mm}$).
