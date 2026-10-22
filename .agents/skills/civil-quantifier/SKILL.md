---
name: civil-quantifier
description: "Use whenever computing, verifying, or drafting civil engineering quantities, bills of quantities (BOQ), earthwork volumetrics, structural steel takeoff, or schedule of rates (SOR) cost estimates for hill roads and slope stabilization. Enforces Simpson's prismoidal formulas, MoRTH measurement rules, IS:1200 method of measurement, HPPWD HPSOR 2024-25 rates, and material contingency buffers."
---

# Civil Engineering Quantity Takeoff & Cost Estimation Guardrails
### MoRTH (5th Rev), IS:1200 & HPPWD Schedule of Rates (HPSOR 2024-25)

This skill enforces exact mathematical rigor, physical measurement standards, and rate analysis formulas for civil remediation quantities and cost schedules in Preliminary Project Reports (PPR), Detailed Project Reports (DPR), and loss valuation dossiers.

Experienced PWD Executive Engineers and Chief Engineers routinely cross-examine quantity derivations. Every calculation in Section 8 & 9 of the PPR must be auditable down to basic geometric formulas.

---

## 1. Earthwork & Failure Colluvium Volumetrics

Under **IS:1200 (Part 1 - Earthwork)** and **MoRTH Section 300**:

### A. Prismoidal Formula (Simpson's Rule - Mandatory for Non-Uniform Cuts)
When end cross-sectional areas $A_1$ and $A_2$ differ by more than $20\%$, the Average End-Area method introduces severe errors. Reports must apply the Prismoidal Formula:
$$V = \frac{L}{6} \cdot (A_1 + 4A_m + A_2)$$
Where:
- $L$ = Linear station length / distance between cross-sections ($\text{m}$).
- $A_1, A_2$ = Cross-sectional areas at consecutive stations ($\text{m}^2$).
- $A_m$ = Cross-sectional area calculated at mid-length using average cross-sectional dimensions ($\text{m}^2$).

### B. Average End-Area Method (Uniform Cross-Sections Only)
$$V = \frac{A_1 + A_2}{2} \cdot L$$

### C. Swell (Bulking) & Compaction Factors
- **In-situ weathered phyllite/schist rock excavation:** Bulking factor $= 1.25 - 1.35$ (Loose haul volume is $25\%-35\%$ greater than in-situ cut volume).
- **Colluvial debris backfill:** Compaction shrinkage factor $= 0.85 - 0.90$ (Requires $10\%-15\%$ more loose material to achieve $95\%$ Proctor density).

---

## 2. Retaining & Breast Wall Structural Quantities (IS:14458)

For a standard gravity retaining or breast wall of height $H$, top width $b_{top}$, base width $b_{base}$, and wall length $L_w$:

```
        b_top
       ┌─────┐
       │     │ \
       │     │   \  Back Batter (1:10 to 1:6)
       │     │     \
       │     │       \
Front  │     │         \
Batter │     │           \
(1:3   │     │             \
 to    │     │               \
 1:6)  │     │                 \
       └────────────────────────┘
                 b_base
```

### A. Concrete / Masonry Volume ($V_w$):
$$A_{section} = \frac{b_{top} + b_{base}}{2} \cdot H$$
$$V_w = A_{section} \cdot L_w$$

### B. Plum Concrete Volume Split (HPSOR Item 04.08):
- **Nominal Mix Concrete ($1:3:6$ or $1:2:4$):** $60\%$ of total volume $= 0.60 \cdot V_w\text{ m}^3$.
- **Hard Sound Stone Plums ($100\text{mm}-150\text{mm}$):** $40\%$ of total volume $= 0.40 \cdot V_w\text{ m}^3$ (Weight $= 0.40 \cdot V_w \cdot 2.40\text{ tonnes}$).

### C. Backfill Filter Medium (IS:14458 Part 2):
- Graded gravel/crushed stone filter layer of thickness $t_f = 0.30\text{ m}$ placed behind the back face:
  $$V_{filter} = t_f \cdot \sqrt{H^2 + (b_{base} - b_{top})^2} \cdot L_w \approx 0.30 \cdot (1.05H) \cdot L_w$$
- **Non-Woven Geotextile Layer:** Area $= \text{Slope length along back of wall} \cdot L_w \cdot 1.10\text{ (overlap)}$.

### D. Weep Holes & Drainage (MoRTH Section 1000):
- Minimum internal diameter: $100\text{ mm}$ perforated PVC pipe.
- Staggered spacing: $1.50\text{ m}$ horizontal $\times 1.50\text{ m}$ vertical.
  $$N_{weep} = \left\lfloor \frac{L_w}{1.50} \right\rfloor \cdot \left\lfloor \frac{H - 0.50}{1.50} \right\rfloor$$
- Total PVC pipe length $= N_{weep} \cdot (b_{mid} + 0.15\text{ m})$.
- Geotextile filter wrap: $0.50\text{ m} \times 0.50\text{ m}$ patch per weep hole inlet $= 0.25\text{ m}^2 \times N_{weep}$.

---

## 3. Soil Nailing & Facings Takeoff (FHWA GEC 7 / MoRTH Section 1000)

For a soil-nailed slope of face area $A_{slope}$, with nail horizontal spacing $S_h$, vertical spacing $S_v$, and uniform nail length $L_n$:

### A. Number of Nails & Total Drilling:
$$N_{nails} = \left( \left\lfloor \frac{\text{Length}}{S_h} \right\rfloor + 1 \right) \cdot \left( \left\lfloor \frac{\text{Slope Height}}{S_v} \right\rfloor + 1 \right)$$
$$\text{Total Drilling Depth } (L_{drill}) = N_{nails} \cdot L_n\text{ (linear meters)}$$

### B. High-Yield Steel Rebar Weight (IS:1786 / ASTM A615):
Standard structural rebar weight formula:
$$w = \frac{D^2}{162} \text{ kg/m}$$
- $\phi 25\text{ mm}$ rebar: $w = 3.858\text{ kg/m} \rightarrow W_{steel} = L_{drill} \cdot 3.858 \cdot 1.05\text{ (lap/waste)}\text{ kg}$.
- $\phi 32\text{ mm}$ rebar: $w = 6.321\text{ kg/m} \rightarrow W_{steel} = L_{drill} \cdot 6.321 \cdot 1.05\text{ kg}$.

### C. Cementitious Grout Volume (Drillhole Diameter $D_d = 100\text{mm}-150\text{mm}$):
$$V_{grout} = \frac{\pi}{4} \cdot D_d^2 \cdot L_{drill} \cdot 1.15\text{ (overbreak allowance)}$$
- Cement consumption ($w/c = 0.45$): $\approx 1,350\text{ kg cement per m}^3\text{ of neat grout}$ ($\approx 27\text{ bags of } 50\text{kg per m}^3$).

### D. High-Tensile Steel Wire Mesh Netting ($1770\text{ MPa}$):
$$\text{Netting Area } (A_{net}) = A_{slope} \cdot 1.10\text{ (10\% seam overlap & anchor margin)}$$
- Boundary wire ropes ($\phi 16\text{mm}$): Perimeter of slope face $+ 20\%$ anchoring loop tails.

---

## 4. Rate Analysis & Statutory Cost Build-Up (HPSOR 2024-25)

The total project financial estimation in Section 10 of the PPR must be structured into an official statutory abstract of cost:

```
STATUTORY ESTIMATE ARCHITECTURE
├── 1. Sub-Total Direct Civil Works Cost (Sum of all HPSOR Items)
│   ├── Item 02.11: Earthwork & Colluvium Excavation
│   ├── Item 04.08: Plum Concrete Retaining / Breast Wall
│   ├── Item 05.02: Heavy Galvanized PVC-Coated Gabion Revetments
│   ├── Item 08.19: Self-Drilling High-Yield Soil Nailing
│   ├── Item 08.24: High-Tensile Wire Mesh Protection
│   ├── Item 03.35: Sub-surface Horizontal Perforated Drains
│   ├── Item 03.12: Lined Crest Catchwater & Chute Drains
│   └── Item 14.02: Bio-engineering Hydroseeding & Jute Matting
│
├── 2. Regional / Hill Terrain Loading
│   └── High Altitude & Mountain Lead Allowance (+10% for elevation >1500m)
│
├── 3. Sub-Total Base Civil Cost (A)
│
├── 4. Statutory Overheads & Add-Ons
│   ├── Physical Contingencies (3.0% of A)
│   ├── Quality Control & Geotechnical Instrumentation Monitoring (1.5% of A)
│   ├── Building and Other Construction Workers (BOCW) Labour Welfare Cess (1.0% of A)
│   └── Goods and Services Tax (GST) (18.0% of A)
│
└── 5. GRAND TOTAL ESTIMATED PROJECT COST (Statutory Sanction Amount)
```
