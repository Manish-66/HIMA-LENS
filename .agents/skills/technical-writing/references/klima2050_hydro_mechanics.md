# Klima 2050 (Norway) Hydro-Meteorological Mechanics
### Reference Document for Technical Writing & Slope Engineering Dossiers

Sourced from the Centre for Research-based Innovation (SFI) **Klima 2050** (*Risk reduction through climate adaptation of buildings and infrastructure*), Norwegian Geotechnical Institute (NGI), and NTNU.

---

## 1. Scope & Work Package 3 (WP3) Taxonomy

Klima 2050 WP3 focuses on **Landslides Triggered by Hydro-Meteorological Processes**, specifically:
- Water-induced shallow planar debris slides and slides in residual/weathered soils.
- Channelized debris flows and slush flows.
- Progressive destabilization caused by prolonged antecedent rainfall and extreme precipitation events.

---

## 2. Fundamental Slope Destabilization Mechanics

### A. The Effective Stress Principle under Water Infiltration
In unsaturated steep terrain, slope stability is governed by Bishop's extended effective stress equation:
$$\sigma' = (\sigma - u_a) + \chi(u_a - u_w)$$
Where:
- $(u_a - u_w)$ = Matric suction (negative pore water pressure), which provides apparent cohesion ($c_\psi$) holding unsaturated steep slopes in equilibrium at angles steeper than the internal friction angle ($\beta > \phi'$).
- $\chi$ = Effective stress parameter, decreasing from $1$ (fully saturated) to $0$ (completely dry).

### B. The Failure Mechanism Chain (Water-Induced)
1. **Pre-Triggering Saturation (Antecedent Moisture):** Prolonged low-intensity rainfall increases the degree of saturation ($S_r$), reducing matric suction to near zero.
2. **Peak Intensity Infiltration:** Heavy, intense downpours exceed the infiltration capacity of surface vegetation, developing transient perched water tables above impermeable bedrock or dense phyllite interfaces.
3. **Pore Pressure Surge ($u > 0$):** Positive pore water pressure develops along the slip boundary, drastically lowering effective normal stress $\sigma'$ and reducing shear resistance:
   $$\tau_f = c' + (\sigma_n - u)\tan\phi'$$
4. **Triggering Shear Mobilization:** When shear stress $\tau = \gamma \cdot z \cdot \sin\beta \cdot \cos\beta$ exceeds shear strength $\tau_f$, instantaneous shear failure occurs ($FOS < 1.0$), rapidly liquefying into a fast-moving debris avalanche or debris flow.

---

## 3. Hydro-Meteorological Precipitation Thresholds

Klima 2050 and NGI establish intensity-duration ($I$-$D$) power-law curves for shallow slope instability:
$$I = \alpha \cdot D^{-\beta}$$
Where:
- $I$ = Rainfall intensity ($\text{mm/h}$).
- $D$ = Rainfall duration ($\text{hours}$).
- $\alpha, \beta$ = Regional climate-morphology parameters.

### Operational Alert Levels (Norwegian & Himalayan Alignment):
- **Green (Normal):** Soil saturation $< 50\%$; no unusual slope movement.
- **Yellow (Advisory):** Soil saturation $50\%-75\%$ with 24-hour rainfall $> 45\text{ mm}$; localized shallow creep and tension cracking along steep road cuts.
- **Orange (Warning):** Soil saturation $> 75\%$ with anticipated 24-hour rainfall $> 80\text{ mm}$; widespread shallow slips, debris avalanches, and carriageway blockages.
- **Red (Critical Emergency):** Antecedent precipitation index (API) saturated ($> 90\%$) with peak 3-hour rainfall $> 50\text{ mm}$; catastrophic debris flows, major structural failures, and immediate mandatory road closures.

---

## 4. Water Management & Nature-Based Solutions (NBS)

Klima 2050 mandates that **water management is the first and most cost-effective line of defense** in mountain slope engineering:

### A. Surface Runoff Interception
- **Catchwater Drains:** Installed along the slope crown outside the tension crack zone to collect overland catchment sheetwash before it enters the landslide scarp.
- **Chute Drains & Stepped Cascades:** Rapidly transfer intercepted runoff down the slope face into natural culverts/streams, equipped with energy dissipators (baffle blocks / rip-rap stilling basins) to prevent toe scour.

### B. Nature-Based Slope Bio-Engineering
- **Vegetative Evapotranspiration:** Deep-rooting shrubs and grasses (e.g., Vetiver grass, Alnus nepalensis) extract soil moisture, increasing soil suction during sunny periods.
- **Root Mechanical Reinforcement:** Root fibers generate additional apparent cohesion ($\Delta c_{root} \approx 2\text{ kPa} - 12\text{ kPa}$) in the top $1.0\text{ m}-2.5\text{ m}$ shallow colluvial zone.
- **Jute & Coir Geo-textile Matting:** Biodegradable mesh pinned to bare cuts prevents raindrop splash detachment and surface rill erosion while vegetation establishes.
