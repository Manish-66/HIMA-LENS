/**
 * HIMA-LENS Interactive Geotechnical Glossary & Symbol Definitions Engine
 * Provides instant, non-intrusive hover definitions for technical engineering terms,
 * landslide kinematics, and map symbols across the platform.
 */
(function () {
    "use strict";

    const GLOSSARY = {
        // Map Symbols & Kinematics (Cruden & Varnes 1996 / GSI NLSM)
        "active": {
            symbol: "▲",
            title: "Active Landslide",
            standard: "Cruden & Varnes (1996) / GSI NLSM",
            def: "A landslide that is currently moving."
        },
        "reactivated": {
            symbol: "▲",
            title: "Reactivated Landslide",
            standard: "Cruden & Varnes (1996) / GSI NLSM",
            def: "An active landslide that is moving again after being inactive."
        },
        "suspended": {
            symbol: "⏸",
            title: "Suspended Landslide",
            standard: "Cruden & Varnes (1996) / GSI NLSM",
            def: "A landslide that has moved within the last annual cycle (12 months), but is not moving at present."
        },
        "dormant": {
            symbol: "○",
            title: "Dormant Landslide",
            standard: "Cruden & Varnes (1996) / GSI NLSM",
            def: "An inactive landslide that can be reactivated by its original causes or other causes."
        },
        "stabilized": {
            symbol: "✔",
            title: "Stabilized Landslide",
            standard: "Cruden & Varnes (1996) / GSI NLSM",
            def: "An inactive landslide that has been permanently protected from its original causes by artificial remedial works."
        },
        "relict": {
            symbol: "○",
            title: "Relict Landslide",
            standard: "Cruden & Varnes (1996) / GSI NLSM",
            def: "An inactive landslide that developed under climatic or geomorphological conditions considerably different from those at present."
        },
        "fall": {
            symbol: "▼",
            title: "Fall (Rockfall)",
            standard: "Cruden & Varnes (1996) / Varnes (1978)",
            def: "Detachment of soil or rock from a steep slope along a surface on which little or no shear displacement takes place, descending mainly through the air by falling, bouncing, or rolling."
        },
        "topple": {
            symbol: "↷",
            title: "Topple",
            standard: "Cruden & Varnes (1996) / Varnes (1978)",
            def: "Forward rotation out of the slope of a mass of soil or rock about a point or axis below the center of gravity of the displaced mass."
        },
        "slide": {
            symbol: "■",
            title: "Slide (Rotational / Translational)",
            standard: "Cruden & Varnes (1996) / Varnes (1978)",
            def: "Downslope movement of a soil or rock mass occurring dominantly on surfaces of rupture or on relatively thin zones of intense shear strain."
        },
        "flow": {
            symbol: "◆",
            title: "Flow (Debris Flow / Mudflow)",
            standard: "Cruden & Varnes (1996) / Varnes (1978)",
            def: "Spatially continuous movement in which shear surfaces are short-lived, closely spaced, and usually not preserved, behaving like a viscous liquid."
        },
        "debris": {
            symbol: "●",
            title: "Debris (Material)",
            standard: "Cruden & Varnes (1996) / GSI NLSM",
            def: "Unconsolidated material containing 20% to 80% particles larger than 2 mm (coarse gravel and boulders mixed with soil)."
        },
        "rock": {
            symbol: "⛰",
            title: "Rock (Material)",
            standard: "Cruden & Varnes (1996) / GSI NLSM",
            def: "A hard or firm mass that was intact and in-situ prior to slope failure displacement."
        },

        // Geotechnical Stability & Mitigation
        "fos": {
            symbol: "FoS",
            title: "Factor of Safety (FoS)",
            standard: "IS:14458 Part 2 / Eurocode 7",
            def: "Ratio of shear strength (resisting forces) to shear stress (driving forces). FoS < 1.0 indicates active slope failure; FoS ≥ 1.30 is the statutory target for hill road stability."
        },
        "breast-wall": {
            symbol: "BW",
            title: "Plum Concrete Breast Wall",
            standard: "IS:14458 Part 2 / IRC:SP:48",
            def: "Gravity retaining structure constructed at the toe of a cut slope scarp to retain toe wash, built with M15 plum concrete and 40% clean hard rock plums."
        },
        "retaining-wall": {
            symbol: "RW",
            title: "Toe Retaining Wall",
            standard: "IS:14458 Part 1 & 2",
            def: "Rigid gravity structure designed to resist lateral earth pressure of unstable mountain overburden and support roadway formation."
        },
        "gabion": {
            symbol: "GW",
            title: "Wire-Mesh Gabion Retaining Wall",
            standard: "MoRTH Section 2504 / IS:16014",
            def: "Flexible, permeable wire mesh crates hand-packed with boulders. Accommodates differential valley settlement and provides natural hydrostatic relief."
        },
        "soil-nailing": {
            symbol: "SN",
            title: "Soil Nailing & Rock Bolting",
            standard: "MoRTH Section 3100 / FHWA GEC 7",
            def: "Pattern of passive grouted steel reinforcement bars (Fe500D) drilled deep into bedrock to transfer shear loads across slip surfaces into stable ground."
        },
        "bioengineering": {
            symbol: "BIO",
            title: "Vegetative Bioengineering",
            standard: "HPPWD Bio-Engineering Manual / IS:14458",
            def: "Slope protection using natural 700 GSM coir netting, hydroseeding, and live brush layering (Vitex negundo, Adhatoda vasica) to arrest superficial erosion."
        },
        "seepage": {
            symbol: "H₂O",
            title: "Groundwater Seepage & Cleft Pressure",
            standard: "IRC:SP:48 / IS:14458",
            def: "Sub-surface groundwater emerging along rock contact joints, generating hydrostatic cleft pore pressure that destabilizes the slope face during monsoon rains."
        },
        "scarp": {
            symbol: "SC",
            title: "Failure Scarp & Crown",
            standard: "IS:14458 Part 1",
            def: "Steep, exposed rupture surface at the upper boundary of the landslide where the displaced mass detached from undisturbed ground."
        },
        "relief-drains": {
            symbol: "RD",
            title: "Sub-Horizontal Deep Relief Drains",
            standard: "IRC:SP:48 / FHWA",
            def: "Perforated PVC pipes (Ø75mm) drilled into bedrock at 5°–10° upward rake with geotextile filter socks to bleed hydrostatic pore water pressure."
        },

        // Hazard Severity
        "critical": {
            symbol: "🔴",
            title: "Critical Severity (Full Blockade)",
            standard: "HPPWD Hill Road SOP",
            def: "Complete roadway formation loss or obstruction (>75% width blocked). Traffic severed across the corridor; urgent multi-agency clearance required."
        },
        "high": {
            symbol: "🟠",
            title: "High Severity (Major Restriction)",
            standard: "HPPWD Hill Road SOP",
            def: "Severe landslide encroachment reducing road to restricted single-lane shuttle transit with active rolling stone hazard."
        },
        "moderate": {
            symbol: "🟡",
            title: "Moderate Severity (Partial Disruption)",
            standard: "HPPWD Hill Road SOP",
            def: "Partial shoulder or roadside ditch blockage; operable single/dual formation width maintained with tension cracking."
        },
        "low": {
            symbol: "🟢",
            title: "Low Severity (Localized Ravelling)",
            standard: "HPPWD Hill Road SOP",
            def: "Minor cut slope ravelling or loose talus wash confined to the inner ditch without impeding vehicular transit."
        }
    };

    // Keyword aliases
    GLOSSARY["active-key"] = GLOSSARY["active"];
    GLOSSARY["fall-key"] = GLOSSARY["fall"];
    GLOSSARY["slide-key"] = GLOSSARY["slide"];
    GLOSSARY["flow-key"] = GLOSSARY["flow"];
    GLOSSARY["debris-key"] = GLOSSARY["debris"];
    GLOSSARY["rockfall"] = GLOSSARY["fall"];
    GLOSSARY["topple"] = GLOSSARY["fall"];
    GLOSSARY["mudslide"] = GLOSSARY["slide"];
    GLOSSARY["debris-flow"] = GLOSSARY["flow"];
    GLOSSARY["colluvium"] = GLOSSARY["debris"];
    GLOSSARY["factor of safety"] = GLOSSARY["fos"];
    GLOSSARY["breast wall"] = GLOSSARY["breast-wall"];
    GLOSSARY["retaining wall"] = GLOSSARY["retaining-wall"];
    GLOSSARY["gabion wall"] = GLOSSARY["gabion"];
    GLOSSARY["soil nailing"] = GLOSSARY["soil-nailing"];
    GLOSSARY["rock bolts"] = GLOSSARY["soil-nailing"];
    GLOSSARY["pore water pressure"] = GLOSSARY["seepage"];

    let tooltipEl = null;
    let hideTimer = null;
    let currentTarget = null;

    function getOrCreateTooltip() {
        if (!tooltipEl) {
            tooltipEl = document.createElement("div");
            tooltipEl.id = "hima-glossary-tooltip";
            tooltipEl.className = "hima-glossary-tooltip";
            tooltipEl.setAttribute("role", "tooltip");
            tooltipEl.setAttribute("aria-hidden", "true");
            document.body.appendChild(tooltipEl);

            tooltipEl.addEventListener("mouseenter", function () {
                if (hideTimer) clearTimeout(hideTimer);
            });
            tooltipEl.addEventListener("mouseleave", function () {
                hideTooltip();
            });
        }
        return tooltipEl;
    }

    function resolveTermData(el) {
        if (!el) return null;
        // 1. Direct data-glossary attribute
        let key = el.getAttribute("data-glossary") || el.getAttribute("data-term");
        if (key && GLOSSARY[key.toLowerCase().trim()]) {
            return GLOSSARY[key.toLowerCase().trim()];
        }

        // 2. Class-based check (e.g. active-key, fall-key)
        for (const cls of el.classList) {
            if (GLOSSARY[cls.toLowerCase()]) {
                return GLOSSARY[cls.toLowerCase()];
            }
        }

        // 3. Text content matching
        const text = (el.innerText || el.textContent || "").toLowerCase().trim();
        for (const [k, v] of Object.entries(GLOSSARY)) {
            if (text === k || text.includes(k)) {
                return v;
            }
        }
        return null;
    }

    function showTooltip(target, termData) {
        if (!termData) return;
        const tt = getOrCreateTooltip();
        if (hideTimer) clearTimeout(hideTimer);
        currentTarget = target;

        tt.innerHTML = `
            <div class="hima-tt-header">
                <span class="hima-tt-symbol">${termData.symbol}</span>
                <div class="hima-tt-title-wrap">
                    <span class="hima-tt-title">${termData.title}</span>
                    <span class="hima-tt-standard">${termData.standard}</span>
                </div>
            </div>
            <div class="hima-tt-body">${termData.def}</div>
        `;

        tt.classList.add("visible");
        tt.setAttribute("aria-hidden", "false");

        // Compute position using getBoundingClientRect
        const rect = target.getBoundingClientRect();
        const ttWidth = 260; // Expected tooltip max-width
        const margin = 10;

        let left = rect.left + (rect.width / 2) - (ttWidth / 2);
        // Bounds checking
        if (left < margin) left = margin;
        if (left + ttWidth > window.innerWidth - margin) {
            left = window.innerWidth - ttWidth - margin;
        }

        let top = rect.bottom + 8;
        // If bottom overflows viewport, position above target
        if (top + 120 > window.innerHeight && rect.top > 120) {
            top = rect.top - 105;
            tt.classList.add("pos-top");
            tt.classList.remove("pos-bottom");
        } else {
            tt.classList.add("pos-bottom");
            tt.classList.remove("pos-top");
        }

        tt.style.left = `${Math.round(left)}px`;
        tt.style.top = `${Math.round(top)}px`;
    }

    function hideTooltip() {
        if (hideTimer) clearTimeout(hideTimer);
        hideTimer = setTimeout(function () {
            if (tooltipEl) {
                tooltipEl.classList.remove("visible");
                tooltipEl.setAttribute("aria-hidden", "true");
            }
            currentTarget = null;
        }, 120);
    }

    // Global delegation for mouseover
    document.addEventListener("mouseover", function (e) {
        const target = e.target.closest("[data-glossary], .glossary-term, .legend-chip, .tech-term");
        if (target) {
            const data = resolveTermData(target);
            if (data) {
                target.style.cursor = "help";
                showTooltip(target, data);
            }
        }
    });

    document.addEventListener("mouseout", function (e) {
        const target = e.target.closest("[data-glossary], .glossary-term, .legend-chip, .tech-term");
        if (target && target === currentTarget) {
            hideTooltip();
        }
    });

    // Touch support for mobile devices
    document.addEventListener("click", function (e) {
        const target = e.target.closest("[data-glossary], .glossary-term, .legend-chip, .tech-term");
        if (target) {
            const data = resolveTermData(target);
            if (data) {
                if (currentTarget === target && tooltipEl && tooltipEl.classList.contains("visible")) {
                    hideTooltip();
                } else {
                    showTooltip(target, data);
                }
            }
        } else if (tooltipEl && !e.target.closest("#hima-glossary-tooltip")) {
            hideTooltip();
        }
    });
})();
