---
name: geotech-validator
description: "Use whenever writing, reviewing, or testing geotechnical slope stability models, Cruden & Varnes kinematics taxonomies, Factor of Safety (FOS) limit equilibrium equations, rainfall threshold intensity-duration curves, or HPPWD civil remediation schedules. Enforces physical property bounds and prevents generative model hallucination in geotech calculations."
---

# Geotechnical Physics & Kinematics Validation Guardrails

This skill enforces engineering physics integrity across `geotech_engine.py`, `ai_assessment.py`, and disaster advisory outputs.

## 1. Physical Parameter Boundaries

When AI or heuristics estimate mountain soil/rock properties in Himachal Pradesh:
*   **Effective Friction Angle ($\phi'$):**
    *   Himalayan colluvium / residual debris: $22^\circ \le \phi' \le 34^\circ$.
    *   Jointed metamorphic bedrock (Schist/Phyllite/Gneiss): $30^\circ \le \phi' \le 45^\circ$.
    *   *Hard Ban:* Any $\phi' < 12^\circ$ or $\phi' > 50^\circ$ is physically invalid.
*   **Effective Cohesion ($c'$):**
    *   Dry/unsaturated debris: $5\text{ kPa} \le c' \le 25\text{ kPa}$.
    *   Intact rock mass: $25\text{ kPa} \le c' \le 120\text{ kPa}$.
    *   *Hard Ban:* Negative cohesion ($c' < 0$) or $c' > 200\text{ kPa}$ in shallow colluvium.
*   **Unit Weight ($\gamma$):**
    *   Natural soil/debris: $17\text{ kN/m}^3 \le \gamma \le 22\text{ kN/m}^3$.
    *   Saturated soil: $19\text{ kN/m}^3 \le \gamma \le 24\text{ kN/m}^3$.

## 2. Limit Equilibrium Factor of Safety ($FOS$)

For planar / infinite slope translational failure:
$$FOS = \frac{c' + (\gamma \cdot z \cdot \cos^2\beta - u)\tan\phi'}{\gamma \cdot z \cdot \sin\beta \cdot \cos\beta}$$
Where:
*   $\beta$ = Slope angle in degrees (HP road cut slopes typically $35^\circ$ to $70^\circ$).
*   $z$ = Slip surface depth in meters ($1.5\text{m}$ to $8.0\text{m}$).
*   $u$ = Pore water pressure ($\text{kPa}$) = $m \cdot \gamma_w \cdot z \cdot \cos^2\beta$.

### Sanity Checks:
*   If slope angle $\beta > \phi'$ and $c' \approx 0$, then dry slope $FOS < 1.0$ (Imminent failure).
*   During saturated monsoon conditions ($m \approx 1$), $FOS$ drops by $\approx 40\%$ to $55\%$.
*   *Hard Ban:* Generating $FOS > 4.0$ on a steep active landslide slope ($> 40^\circ$) is an AI hallucination.

## 3. Cruden & Varnes (1996) Movement Taxonomy

Only approved standard Cruden & Varnes movement types and materials are permitted:
*   **Materials:** `Rock`, `Debris` (coarse soil $>20\%$ gravel), `Earth` (fine soil).
*   **Movement Types:** `Fall`, `Topple`, `Slide (Rotational)`, `Slide (Translational)`, `Spread`, `Flow`.
*   Combinations: e.g., `Debris Flow`, `Rock Fall`, `Rotational Slump`. Avoid non-standard terms like "Mud tumble" or "Dirt collapse".

## 4. HPPWD Civil Countermeasures Taxonomy

Mitigation cost estimations in `ai_assessment.py` must use standard Himachal Pradesh PWD engineering units:
1.  **Drainage:** Horizontal perforated drains (L/m), Catchwater drains (m), Subsurface French drains.
2.  **Reinforcement:** Self-drilling soil nails ($25\text{mm}$ to $32\text{mm}$ dia, $6\text{m}$ to $12\text{m}$ depth), High-tensile steel wire mesh (Tecco / Maccaferri $\text{m}^2$).
3.  **Retaining Structures:** Plum concrete gravity walls ($1:2:4$ or $1:3:6$), Gabion wire crates with stone pitching ($\text{m}^3$), RCC cantilever walls.
4.  **Bio-engineering:** Vetiver grass hydro-seeding, brush layering, jute geo-textile matting ($\text{m}^2$).
