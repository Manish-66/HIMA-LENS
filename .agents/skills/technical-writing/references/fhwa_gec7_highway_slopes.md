# FHWA-NHI-14-007 (GEC 7) & FHWA-NHI-11-032: Highway Slope Remediation
### External Standard 2 for Technical Writing & Engineering Reporting

Sourced from the Federal Highway Administration (FHWA), U.S. Department of Transportation, including **FHWA-NHI-14-007** (Geotechnical Engineering Circular No. 7: *Soil Nail Walls Reference Manual*) and **FHWA-NHI-11-032** (GEC No. 3: *LRFD Seismic Analysis and Design of Transportation Geotechnical Features and Structural Foundations*).

---

## 1. Highway Geotechnical Assessment & Reporting Standards

FHWA establishes strict reporting protocols for road-corridor slope stability and disaster repair projects. Every technical document submitted for highway remediation must provide:

### A. Road Sector Telemetry Identification
- **Route Designation & Classification:** E.g., National Highway (NH-154), State Highway (SH), Major District Road (MDR).
- **Exact Linear Referencing (Stationing / Chainage):** Measured to the nearest millimeter/centimeter (e.g., `Chainage Km 124+800.00`).
- **Right-of-Way (ROW) Limits & Encroachment:** Specific measurement of slope toe encroachment into the formation width, paved shoulder, and carriageway travel lanes.

### B. Load and Resistance Factor Design (LRFD) Framework
Under FHWA doctrine, slope stabilization must verify limit states using factored resistance:
$$R_d = \phi_R \cdot R_n \ge \sum \gamma_i \cdot Q_i$$
Where:
- $\phi_R$ = Resistance factor (typically $0.65 - 0.75$ for static soil nail pullout; $0.90$ for tensile rebar rupture).
- $\gamma_i$ = Load factors for dead load ($EV = 1.35$), live load ($LS = 1.75$), and active earth pressure ($EH = 1.50$).

---

## 2. FHWA Soil Nail Wall Design Documentation (GEC 7)

When reporting a soil nailing design for an active mountain slope, the dossier must include four explicit design parameters:

### 1. Tendon & Grout Column Geometry:
- **Bar Diameter & Grade:** ASTM A615 Grade 60 ($f_y = 420\text{ MPa}$) or Grade 75 ($f_y = 520\text{ MPa}$), or Indian Fe500D.
- **Drillhole Diameter ($D_d$):** Typically $100\text{ mm}$ to $150\text{ mm}$ ($4-6\text{ inches}$).
- **Length Pattern:** Uniform length ($L \approx 0.7H - 1.0H$) or stepped length with upper nails extended past the active zone into stable competent bedrock/colluvium.

### 2. Ultimate Pullout Resistance ($q_u$):
The technical report must state the nominal pullout capacity per unit bond length:
$$r_{po} = \pi \cdot D_d \cdot q_u$$
Typical validated ranges for Himalayan lithology:
- Dense weathered schist / phyllite: $q_u = 100\text{ kPa} - 180\text{ kPa}$.
- Coarse residual colluvium / gravel: $q_u = 70\text{ kPa} - 120\text{ kPa}$.
- Sandstone / meta-sandstone: $q_u = 200\text{ kPa} - 450\text{ kPa}$.

### 3. Facing System Details:
- **Initial / Temporary Facing:** $75\text{ mm}-100\text{ mm}$ fiber-reinforced or welded wire mesh ($WWM\text{ }152\times 152\text{ MW}19/\text{MW}19$) shotcrete applied within 12 hours of bench excavation.
- **Permanent Architectural Facing:** $150\text{ mm}-200\text{ mm}$ cast-in-place (CIP) reinforced concrete or high-durability sculpted shotcrete with integral strip drains.

### 4. Integrated Strip Drainage:
- Geocomposite vertical drainage strips (width $300\text{ mm}-450\text{ mm}$) placed directly against the excavated face at regular horizontal intervals ($1.5\text{ m}-2.0\text{ m}$) behind the shotcrete facing, discharging to footing collector pipes with daylight outfalls.

---

## 3. FHWA Verification Testing Protocols in Technical Reports

Any technical remediation dossier must prescribe mandatory field verification testing:
1. **Verification (Sacrificial) Pullout Tests:** Minimum 2 to 3 nails installed in representative strata and loaded to $2.0\times$ design load or ultimate pullout failure to confirm $q_u$ assumptions before production nailing starts.
2. **Proof Tests:** Minimum $5\%$ of total production nails tested incrementally to $1.5\times$ design load and held for 10 minutes to verify creep rates ($< 1.0\text{ mm}$ creep movement between 1 and 10 minutes).
