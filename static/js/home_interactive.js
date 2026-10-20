/**
 * HIMA-LENS: Interactive Homepage Ecosystem Controller
 * Drives live AI terminal scenarios, interactive district radar,
 * slope failure anatomy inspector, Leaflet mini-map, and live HPSOR cost calculator.
 */

document.addEventListener("DOMContentLoaded", () => {
    initHeroScannerTerminal();
    initDistrictRadar();
    initSlopeAnatomyInspector();
    initWorkstationTabs();
    initCostCalculatorSandbox();
    initMiniMap();
});

/* ============================================================
   1. HERO AI SCANNER TERMINAL CONTROLLER
============================================================ */
const SCENARIOS = {
    mandi_rock: {
        title: "Mandi-Pandoh Sector NH-21",
        coords: "31.7080° N, 76.9320° E",
        image: "https://lsjnontlkffkneiuxmwx.supabase.co/storage/v1/object/public/report-images/report_df6c4fc035f2_1791793364.jpg",
        usgs: "Translational Rock Slide (Cruden-Varnes Class 5)",
        geology: "Sandstone & Siltstone Interbeds (GSI 53A14)",
        remedy: "Plum Breast Wall H=2.8m + Soil Nails Fe500",
        cost: "₹ 6,99,080",
        costSub: "16 HPSOR Scheduled Packages (Incl. 18% GST)",
        reportId: "HL-CR-37541B33",
        tag: "CRITICAL ROCK SLIDE",
        isDisqualified: false,
        bbox: { top: "18%", left: "20%", width: "55%", height: "55%" }
    },
    mandi_cut: {
        title: "Aut-Larji Corridor Cut Slope",
        coords: "31.6950° N, 77.0120° E",
        image: "https://lsjnontlkffkneiuxmwx.supabase.co/storage/v1/object/public/report-images/report_59610d68c83e_1791793285.jpeg",
        usgs: "Debris Slide & Roadway Encroachment (Class 5)",
        geology: "Dolomitic Limestone & Colluvium (GSI 53E02)",
        remedy: "Gabion Heavy Retention Wall H=3.5m + PVC Sub-Drains",
        cost: "₹ 5,84,320",
        costSub: "Emergency Road Clearance & Retaining Works",
        reportId: "HL-CR-1EE848DD",
        tag: "DEBRIS ROAD BLOCK",
        isDisqualified: false,
        bbox: { top: "25%", left: "15%", width: "65%", height: "50%" }
    },
    kullu_debris: {
        title: "Kullu Valley Approach Corridor",
        coords: "31.8540° N, 77.1230° E",
        image: "https://lsjnontlkffkneiuxmwx.supabase.co/storage/v1/object/public/report-images/report_551bd487fdb4_1791799355.jpg",
        usgs: "Rotational Earth Slide / Colluvial Toe Failure",
        geology: "Chail Phyllite & Weathered Schist (GSI 53E03)",
        remedy: "Catchwater Interceptor Drains + Plum Scour Masonry",
        cost: "₹ 4,62,100",
        costSub: "Hill Drainage & Bio-Turfing Stabilization",
        reportId: "HL-CR-6A9B327E",
        tag: "COLOCATED ACTIVE SLIP",
        isDisqualified: false,
        bbox: { top: "15%", left: "22%", width: "58%", height: "60%" }
    },
    audit_demo: {
        title: "Non-Geological Optical Audit Demo",
        coords: "N/A — Automated Visual Verification",
        image: "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=700&auto=format&fit=crop",
        usgs: "⛔ REJECTED: Non-Geological Subject (Pet / Indoor)",
        geology: "Disqualified (No Himalayan rock strata present)",
        remedy: "N/A — Field Survey Verification Required",
        cost: "₹ 0",
        costSub: "Calculation Suspended per PWD Audit Protocol",
        reportId: "HL-CR-37541B33",
        tag: "⛔ DISQUALIFIED MEDIA",
        isDisqualified: true,
        bbox: { top: "20%", left: "25%", width: "50%", height: "50%" }
    }
};

function initHeroScannerTerminal() {
    const btns = document.querySelectorAll(".scenario-btn");
    const imgEl = document.getElementById("terminal-img");
    const bboxEl = document.getElementById("terminal-bbox");
    const tagEl = document.getElementById("terminal-tag");
    const titleEl = document.getElementById("terminal-title");
    const locEl = document.getElementById("terminal-loc");
    const usgsEl = document.getElementById("terminal-usgs");
    const geolEl = document.getElementById("terminal-geol");
    const remEl = document.getElementById("terminal-rem");
    const costEl = document.getElementById("terminal-cost");
    const costSubEl = document.getElementById("terminal-cost-sub");
    const linkPwd = document.getElementById("terminal-link-pwd");
    const linkBoq = document.getElementById("terminal-link-boq");

    btns.forEach(btn => {
        btn.addEventListener("click", () => {
            btns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            const key = btn.dataset.scenario;
            const data = SCENARIOS[key];
            if (!data) return;

            // Animate laser scan line restart
            const scanline = document.querySelector(".scanline-laser");
            if (scanline) {
                scanline.style.animation = "none";
                setTimeout(() => scanline.style.animation = "", 10);
            }

            if (imgEl) {
                imgEl.style.opacity = "0.4";
                setTimeout(() => {
                    imgEl.src = data.image;
                    imgEl.style.opacity = "1";
                }, 150);
            }

            if (bboxEl) {
                bboxEl.style.top = data.bbox.top;
                bboxEl.style.left = data.bbox.left;
                bboxEl.style.width = data.bbox.width;
                bboxEl.style.height = data.bbox.height;
                bboxEl.style.borderColor = data.isDisqualified ? "#ef4444" : "#2dd4bf";
                bboxEl.style.backgroundColor = data.isDisqualified ? "rgba(239, 68, 68, 0.15)" : "rgba(45, 212, 191, 0.12)";
            }

            if (tagEl) {
                tagEl.textContent = data.tag;
                tagEl.style.borderColor = data.isDisqualified ? "#ef4444" : "#2dd4bf";
                tagEl.style.color = data.isDisqualified ? "#fca5a5" : "#5eead4";
            }

            if (titleEl) titleEl.textContent = data.title;
            if (locEl) locEl.textContent = data.coords;
            if (usgsEl) usgsEl.textContent = data.usgs;
            if (geolEl) geolEl.textContent = data.geology;
            if (remEl) remEl.textContent = data.remedy;
            if (costEl) costEl.textContent = data.cost;
            if (costSubEl) costSubEl.textContent = data.costSub;

            if (linkPwd) linkPwd.href = `/report/pwd-sheet/${data.reportId}`;
            if (linkBoq) linkBoq.href = `/report/boq-sheet/${data.reportId}`;
        });
    });
}


/* ============================================================
   2. DISTRICT RADAR & METRICS CONTROLLER
============================================================ */
const DISTRICT_STATS = {
    "All": { count: 14190, hazard: "STATEWIDE HIGH HAZARD", corridor: "NH-21, NH-05, NH-205, SH-13", geology: "Tertiary Sandstone, Chail Phyllites, Jutogh Gneiss", outlay: "₹ 1,280 Cr", focus: "All 12 Administrative Divisions Cataloged", linkQuery: "all" },
    "Mandi": { count: 9429, hazard: "CRITICAL SEVERE RISK", corridor: "NH-21 (Chandigarh-Manali), Mandi-Kotli Corridor", geology: "Sandstone, Dolomitic Limestone, Deep Colluvium", outlay: "₹ 740 Cr", focus: "Highest Concentration of Roadside Slump Events", linkQuery: "Mandi" },
    "Sirmaur": { count: 1082, hazard: "HIGH VULNERABILITY", corridor: "NH-07 (Paonta Sahib-Shillai), Nahan-Renuka Corridor", geology: "Sub-Himalayan Siwalik Sandstone & Soft Clays", outlay: "₹ 115 Cr", focus: "Active Gutter Scour & Surcharge Overburden", linkQuery: "Sirmaur" },
    "Shimla": { count: 991, hazard: "HIGH MONSOON DISTRESS", corridor: "NH-05 (Hindustan-Tibet Rd), Theog-Rohru SH", geology: "Jutogh Group Metamorphic Schist & Gneiss", outlay: "₹ 130 Cr", focus: "Severe Highway Ridge Cut Slope Instabilities", linkQuery: "Shimla" },
    "Solan": { count: 786, hazard: "MODERATE-HIGH", corridor: "NH-05 (Parwanoo-Solan Multi-Lane Cut)", geology: "Lower Tertiary Krol Limestone & Siltstone", outlay: "₹ 82 Cr", focus: "Engineered 4-Lane Cut Slopes Requiring Nailing", linkQuery: "Solan" },
    "Kangra": { count: 516, hazard: "MODERATE TO HIGH", corridor: "NH-154 (Pathankot-Mandi), Kangra-Dharamshala", geology: "Upper Siwalik Boulders, Conglomerates & Alluvium", outlay: "₹ 58 Cr", focus: "High Precipitation Drainage Surcharge Zones", linkQuery: "Kangra" },
    "Chamba": { count: 492, hazard: "HIGH REMOTE CORRIDOR", corridor: "NH-154A (Pathankot-Chamba-Bharmour)", geology: "Pre-Cambrian Chail Slates, Phyllites & Granites", outlay: "₹ 64 Cr", focus: "Deep River Valley Cleavage Discontinuities", linkQuery: "Chamba" },
    "Kullu": { count: 411, hazard: "CRITICAL GORGE SECTOR", corridor: "NH-21 (Aut-Larji-Kullu-Manali Gorge)", geology: "Central Crystalline Gneiss, Quartzite & Schist", outlay: "₹ 52 Cr", focus: "Steep Canyon Rock Fall Chutes & Debris Cones", linkQuery: "Kullu" },
    "Bilaspur": { count: 197, hazard: "MODERATE", corridor: "NH-205 (Kiratpur-Nerchowk Express Corridor)", geology: "Siwalik Sandstone & Govindsagar Lake Rim", outlay: "₹ 24 Cr", focus: "Reservoir Rim Saturation & Toe Erosion", linkQuery: "Bilaspur" },
    "Kinnaur": { count: 118, hazard: "EXTREME CANYON ROCKFALL", corridor: "NH-05 (Pooh-Khab High Mountain Gorge)", geology: "Vaikrita High-Grade Gneiss, Schist & Pegmatites", outlay: "₹ 38 Cr", focus: "High-Energy Free-Fall Rock Chutes (500 kJ+)", linkQuery: "Kinnaur" },
    "Lahaul And Spiti": { count: 69, hazard: "PERMAFROST & DEBRIS", corridor: "Leh-Manali Highway & Spiti Valley SH", geology: "Tethyan Sedimentary Sequence (Mesozoic Strata)", outlay: "₹ 18 Cr", focus: "Freeze-Thaw Frost Shatter & Glacial Moraines", linkQuery: "Lahaul And Spiti" },
    "Hamirpur": { count: 54, hazard: "LOW-MODERATE", corridor: "SH-39 & Hamirpur-Nadaun Corridor", geology: "Upper Siwalik Friable Sandstone & Shales", outlay: "₹ 7 Cr", focus: "Shallow Road Embankment Shoulder Washouts", linkQuery: "Hamirpur" },
    "Una": { count: 45, hazard: "LOW SURFICIAL", corridor: "NH-503 (Nangal-Una-Mubarikpur)", geology: "Quaternary Alluvium & Siwalik Gravel Beds", outlay: "₹ 5 Cr", focus: "Surficial Rill Erosion on Low Incline Slopes", linkQuery: "Una" }
};

function initDistrictRadar() {
    const pillBtns = document.querySelectorAll(".district-pill-btn");
    const countVal = document.getElementById("radar-count-val");
    const hazardVal = document.getElementById("radar-hazard-val");
    const corridorVal = document.getElementById("radar-corridor-val");
    const geologyVal = document.getElementById("radar-geology-val");
    const outlayVal = document.getElementById("radar-outlay-val");
    const focusVal = document.getElementById("radar-focus-val");
    const actionBtn = document.getElementById("radar-action-btn");

    pillBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            pillBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            const dist = btn.dataset.district;
            const data = DISTRICT_STATS[dist] || DISTRICT_STATS["All"];

            // Animate number count smoothly
            if (countVal) animateValue(countVal, parseInt(countVal.textContent.replace(/,/g, "")) || 0, data.count, 600);
            if (hazardVal) hazardVal.textContent = data.hazard;
            if (corridorVal) corridorVal.textContent = data.corridor;
            if (geologyVal) geologyVal.textContent = data.geology;
            if (outlayVal) outlayVal.textContent = data.outlay;
            if (focusVal) focusVal.textContent = data.focus;

            if (actionBtn) {
                actionBtn.href = data.linkQuery === "all" ? "/explore" : `/explore?district=${encodeURIComponent(data.linkQuery)}`;
                actionBtn.querySelector("span").textContent = `Launch GIS Explorer (${dist})`;
            }
        });
    });
}

function animateValue(obj, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const current = Math.floor(progress * (end - start) + start);
        obj.textContent = current.toLocaleString();
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}


/* ============================================================
   3. INTERACTIVE SLOPE FAILURE ANATOMY INSPECTOR
============================================================ */
const ANATOMY_HOTSPOTS = {
    crown: {
        tag: "01 / KINEMATIC DETACHMENT",
        title: "Crown Tension Fissures & Detachment Scarp",
        standard: "USGS Circular 1325 • Cruden-Varnes (1996)",
        body: "Gravitational stress relief creates sub-vertical extensional tension cracks 5m to 15m uphill of the cut slope crest. When fissure aperture exceeds 15mm under rainfall saturation, progressive shear rupture initiates kinematic downhill displacement.",
        metrics: [
            { lbl: "Diagnostic Feature", val: "Tension Cracks (>15mm aperture)" },
            { lbl: "Failure Kinematics", val: "Translational Planar Slip" },
            { lbl: "Prescribed Action", val: "Crown Unloading & Interceptor Catch Drains" },
            { lbl: "HPSOR Code", val: "MoRTH Section 301 / HPSOR Item 2.1" }
        ]
    },
    joint: {
        tag: "02 / STRUCTURAL GEOLOGY",
        title: "Adverse Daylighting Joint Planes (J1 Dip 59°)",
        standard: "GSI Bhukosh Lithology • IS:14458 Part 1",
        body: "Relict bedding plane discontinuity J1 dips at 59° towards the road valley, daylighting directly into the 64° highway cut face. Because friction angle (φ ≈ 32°) < dip angle (59°) < cut angle (64°), daylighting block sliding is kinematically inevitable without active pinning.",
        metrics: [
            { lbl: "Bedrock Stratigraphy", val: "Massive Sandstone & Siltstone" },
            { lbl: "Joint Set Geometry", val: "Dip 59° Daylight / Strike N35°W" },
            { lbl: "Kinematic Mode", val: "Planar Block Sliding (FOS = 0.88)" },
            { lbl: "Stabilization", val: "Systematic Soil Nails (Fe500 dia 25mm)" }
        ]
    },
    seepage: {
        tag: "03 / HYDROGEOLOGY",
        title: "Perched Phreatic Seepage & Cleft Pressure",
        standard: "IRC:SP:48 Drainage • CEDD TGN 24",
        body: "Monsoon precipitation rapidly infiltrates the porous upper colluvium, pooling above the impermeable sandstone contact. This creates localized perched hydrostatic head, building transient cleft water pressure that drives effective normal stress to zero.",
        metrics: [
            { lbl: "Hydrogeological Vector", val: "Perched Colluvial Water Table" },
            { lbl: "Pore-Pressure Trigger", val: "Loss of Soil Matric Suction" },
            { lbl: "Remedial System", val: "4 Nos Sub-Horizontal PVC Drains (15m)" },
            { lbl: "Filter Protection", val: "Non-woven Geotextile Sock (O90 < 0.1mm)" }
        ]
    },
    wall: {
        tag: "04 / STRUCTURAL TOE ARREST",
        title: "Plum Concrete Breast Wall (H=2.8m, Base=1.4m)",
        standard: "HPPWD HPSOR 4.2 • MoRTH Section 1400",
        body: "Heavy gravity retention wall founded directly into competent bedrock with embedment >= 1.0m. Constructed using M15 grade concrete with 40% clean hard mountain rock plums (150mm to 300mm size) to provide gravity resistance against active earth surcharge.",
        metrics: [
            { lbl: "Structural Dimensions", val: "Height = 2.80m, Base Width = 1.40m" },
            { lbl: "Concrete Specification", val: "M15 Concrete with 40% Plums" },
            { lbl: "Weephole Spacing", val: "100mm dia PVC @ 1.20m c/c Staggered" },
            { lbl: "Unit Rate Regime", val: "HPSOR 4.2 @ ₹ 3,650 per m³" }
        ]
    },
    nails: {
        tag: "05 / INTERNAL REINFORCEMENT",
        title: "Passive Soil Nailing Array & Wire Drapery",
        standard: "Hong Kong CEDD Geoguide 7 • IS:14458",
        body: "High-yield deformed steel rebar (Fe500 dia 25mm) grouted into 100mm diameter rotary-percussive boreholes inclined at 15° downward rake in a 2.0m x 2.0m staggered matrix. Transmits tensile resistance deep behind the potential rupture plane.",
        metrics: [
            { lbl: "Tendon Steel", val: "Fe500 High-Yield Deformed (25mm)" },
            { lbl: "Grid Configuration", val: "2.0m (H) x 2.0m (V) Staggered Pattern" },
            { lbl: "Grout Characteristic", val: "Neat OPC Grout (f_cu >= 30 MPa)" },
            { lbl: "Pullout Verification", val: "2% Sacrificial Proof Loading" }
        ]
    },
    bio: {
        tag: "06 / NATURE-BASED SOLUTIONS",
        title: "Vetiver Bio-Turfing & Coir Blanketing",
        standard: "LaRiMiT Cluster 8 • IRC Hill Road Bioengineering",
        body: "Open-weave 700 GSM coir geotextile erosion blankets pinned over re-profiled 1:1.5 cut slopes, planted with deep-rooting Vetiver contour hedges. Roots penetrate up to 3m vertically into bedrock joints, binding surficial soil and re-establishing natural evapotranspirative matric suction.",
        metrics: [
            { lbl: "Bio-Blanket Spec", val: "100% Biodegradable Coir (700 GSM)" },
            { lbl: "Vegetation Type", val: "Vetiveria zizanioides (Deep Root)" },
            { lbl: "Erosion Prevention", val: "Prevents Surface Rill Raveling" },
            { lbl: "HPSOR Unit Rate", val: "MoRTH Section 305 @ ₹ 145 per m²" }
        ]
    }
};

function initSlopeAnatomyInspector() {
    const nodes = document.querySelectorAll(".hotspot-node");
    const tagEl = document.getElementById("ins-tag");
    const titleEl = document.getElementById("ins-title");
    const codeEl = document.getElementById("ins-code");
    const bodyEl = document.getElementById("ins-body");
    const metricsEl = document.getElementById("ins-metrics");

    nodes.forEach(node => {
        node.addEventListener("click", () => {
            nodes.forEach(n => n.classList.remove("active"));
            node.classList.add("active");

            const key = node.dataset.hotspot;
            const data = ANATOMY_HOTSPOTS[key];
            if (!data) return;

            if (tagEl) tagEl.textContent = data.tag;
            if (titleEl) titleEl.textContent = data.title;
            if (codeEl) codeEl.textContent = data.standard;
            if (bodyEl) bodyEl.textContent = data.body;

            if (metricsEl) {
                metricsEl.innerHTML = data.metrics.map(m => `
                    <div class="inspector-metric-row">
                        <span class="inspector-metric-lbl">${m.lbl}:</span>
                        <span class="inspector-metric-val">${m.val}</span>
                    </div>
                `).join("");
            }
        });
    });
}


/* ============================================================
   4. WORKSTATION TABS CONTROLLER
============================================================ */
function initWorkstationTabs() {
    const tabBtns = document.querySelectorAll(".workstation-tab-btn");
    const panels = document.querySelectorAll(".workstation-panel");

    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            tabBtns.forEach(b => b.classList.remove("active"));
            panels.forEach(p => p.classList.remove("active"));

            btn.classList.add("active");
            const targetId = btn.dataset.tab;
            const targetPanel = document.getElementById(targetId);
            if (targetPanel) targetPanel.classList.add("active");

            // Invalidate Leaflet map size if switching to map tab
            if (targetId === "tab-mini-map" && window.homeMiniMap) {
                setTimeout(() => window.homeMiniMap.invalidateSize(), 150);
            }
        });
    });
}


/* ============================================================
   5. LIVE HPSOR COST CALCULATOR SANDBOX
============================================================ */
function initCostCalculatorSandbox() {
    const sliderH = document.getElementById("calc-h");
    const sliderL = document.getElementById("calc-l");
    const sevPills = document.querySelectorAll(".calc-sev-pill");

    const valH = document.getElementById("calc-val-h");
    const valL = document.getElementById("calc-val-l");
    const valExc = document.getElementById("calc-val-exc");
    const valWall = document.getElementById("calc-val-wall");
    const valNails = document.getElementById("calc-val-nails");
    const valTotalCivil = document.getElementById("calc-val-total");
    const valSdrf = document.getElementById("calc-val-sdrf");

    let currentSeverity = "Moderate";

    function updateCalculations() {
        const H = parseFloat(sliderH ? sliderH.value : 4.5);
        const L = parseFloat(sliderL ? sliderL.value : 25);

        if (valH) valH.textContent = `${H.toFixed(1)} m`;
        if (valL) valL.textContent = `${L.toFixed(0)} m`;

        // Physical Quantities
        const excavationM3 = Math.round(H * L * 1.55);
        const breastWallM3 = Math.round(H * 0.45 * L * 1.25);
        const soilNailsCount = Math.round((H / 2) * (L / 2) * 1.2);

        // Severity Multiplier
        let sevFactor = 1.0;
        if (currentSeverity === "Low") sevFactor = 0.75;
        if (currentSeverity === "High") sevFactor = 1.35;
        if (currentSeverity === "Critical") sevFactor = 1.75;

        // Rates (HPSOR & MoRTH Scheduled Averages)
        const costExcavation = excavationM3 * 260; // MoRTH 301 tipper haulage
        const costWall = breastWallM3 * 3650;      // HPSOR 4.2 Plum Concrete M15
        const costNails = soilNailsCount * 4200;    // MoRTH 1002 Grouted Soil Nails
        const costDrainage = L * 950;              // Sub-drains & catchwater

        const directCivil = Math.round((costExcavation + costWall + costNails + costDrainage) * sevFactor);
        const contingencies = Math.round(directCivil * 0.03);
        const qcTesting = Math.round(directCivil * 0.015);
        const subtotal = directCivil + contingencies + qcTesting;
        const gst = Math.round(subtotal * 0.18);
        const grandCivil = subtotal + gst;

        // SDRF Disaster Allocation estimate
        const sdrfRelief = Math.round(directCivil * 0.65 + 150000);

        if (valExc) valExc.textContent = `${excavationM3.toLocaleString()} m³`;
        if (valWall) valWall.textContent = `${breastWallM3.toLocaleString()} m³`;
        if (valNails) valNails.textContent = `${soilNailsCount} Nos`;
        if (valTotalCivil) valTotalCivil.textContent = `₹ ${grandCivil.toLocaleString("en-IN")}`;
        if (valSdrf) valSdrf.textContent = `₹ ${sdrfRelief.toLocaleString("en-IN")}`;
    }

    if (sliderH) sliderH.addEventListener("input", updateCalculations);
    if (sliderL) sliderL.addEventListener("input", updateCalculations);

    sevPills.forEach(pill => {
        pill.addEventListener("click", () => {
            sevPills.forEach(p => p.classList.remove("active"));
            pill.classList.add("active");
            currentSeverity = pill.dataset.severity;
            updateCalculations();
        });
    });

    updateCalculations();
}


/* ============================================================
   6. EMBEDDED LEAFLET MINI-MAP CONTROLLER
============================================================ */
function initMiniMap() {
    const mapEl = document.getElementById("home-mini-map");
    if (!mapEl || typeof L === "undefined") return;

    const map = L.map("home-mini-map", {
        center: [31.75, 77.15],
        zoom: 8,
        zoomControl: true,
        scrollWheelZoom: false
    });
    window.homeMiniMap = map;

    // CartoDB Dark Matter tiles (matches Himalayan theme)
    L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png", {
        attribution: '&copy; <a href="https://carto.com/">CARTO</a>',
        maxZoom: 16
    }).addTo(map);

    // Add representative landslide hotspots across HP
    const hotspots = [
        { name: "Mandi Pandoh Cut", lat: 31.708, lng: 76.932, sev: "Severe", count: 9429 },
        { name: "Larji Aut Canyon", lat: 31.695, lng: 77.012, sev: "High", count: 180 },
        { name: "Theog Ridge Cut", lat: 31.121, lng: 77.352, sev: "High", count: 991 },
        { name: "Shillai Corridor", lat: 30.652, lng: 77.620, sev: "High", count: 1082 },
        { name: "Dharamshala Escarpment", lat: 32.219, lng: 76.323, sev: "Moderate", count: 516 },
        { name: "Kinnaur Pooh Gorge", lat: 31.755, lng: 78.580, sev: "Extreme", count: 118 },
        { name: "Manali Rohtang Approach", lat: 32.243, lng: 77.189, sev: "Moderate", count: 411 }
    ];

    hotspots.forEach(h => {
        const marker = L.circleMarker([h.lat, h.lng], {
            radius: Math.min(18, Math.max(8, Math.sqrt(h.count) * 0.2)),
            fillColor: h.sev === "Severe" || h.sev === "Extreme" ? "#ef4444" : "#f59e0b",
            color: "#ffffff",
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        }).addTo(map);

        marker.bindPopup(`
            <div style="font-family:'DM Sans',sans-serif;font-size:12px;padding:4px;">
                <strong style="color:#092f25;font-size:13px;">${h.name}</strong><br>
                <span>Severity: <strong style="color:#b45309;">${h.sev}</strong></span><br>
                <span>Records in cluster: <strong>${h.count.toLocaleString()}</strong></span><br>
                <a href="/explore?district=${encodeURIComponent(h.name.split(' ')[0])}" style="color:#0284c7;font-weight:700;display:inline-block;margin-top:6px;">Inspect on Explorer &rarr;</a>
            </div>
        `);
    });
}
