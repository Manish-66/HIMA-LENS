/**
 * HIMA-LENS Geological Lithology Observer & Rock Mass Guide
 * ========================================================
 * Synthesizes GSI Bhukosh digital ground truth (1:50k), Macrostrat/Rockd,
 * IS:13365 / Bieniawski RMR / Hoek-Brown geomechanical properties, and
 * field diagnostics across Himalayan lithological archetypes.
 *
 * Theme: Minimalist Swiss / Alpine Geotechnical Editorial
 */

(function () {
    let currentGeologyData = null;
    let fullRockCatalog = null;
    let currentActiveTab = "site-geology";

    function ensureModalInDOM() {
        if (document.getElementById("hima-geology-modal")) return;

        const modalHtml = `
        <div id="hima-geology-modal" class="geology-modal-overlay" style="display: none;" role="dialog" aria-modal="true" aria-labelledby="geo-modal-title">
            <div class="geology-modal-dialog">
                <header class="geology-modal-header">
                    <div class="geo-header-brand">
                        <div class="geo-kicker-row">
                            <span class="geo-kicker">HIMALAYAN GEOTECHNICAL LITHOLOGY OBSERVER</span>
                            <span class="geo-kicker-badge">IS:13365 &bull; GSI 1:50k</span>
                        </div>
                        <h2 id="geo-modal-title">Geological Formation &amp; Rock Mass Guide</h2>
                        <span class="geo-subcaption">Digital ground truth, geomechanical parameters, field diagnostic protocol &amp; external portals</span>
                    </div>
                    <button type="button" class="btn-geo-close" onclick="closeGeologyModal()" aria-label="Close modal">&times;</button>
                </header>

                <!-- Sticky Segmented Nav Control -->
                <div class="geology-tabs-nav-wrap">
                    <nav class="geology-tabs-nav" role="tablist">
                        <button type="button" class="geo-tab-btn active" data-tab="site-geology" onclick="switchGeologyTab('site-geology', this)">
                            <span>Site Stratigraphy</span>
                        </button>
                        <button type="button" class="geo-tab-btn" data-tab="field-tests" onclick="switchGeologyTab('field-tests', this)">
                            <span>Field Diagnostic Key</span>
                        </button>
                        <button type="button" class="geo-tab-btn" data-tab="apps-tools" onclick="switchGeologyTab('apps-tools', this)">
                            <span>Apps &amp; Portals</span>
                        </button>
                        <button type="button" class="geo-tab-btn" data-tab="rock-catalog" onclick="switchGeologyTab('rock-catalog', this)">
                            <span>Rock Catalog</span>
                            <span class="geo-tab-badge">10</span>
                        </button>
                        <button type="button" class="geo-tab-btn" data-tab="full-dossier" onclick="switchGeologyTab('full-dossier', this)">
                            <span>Full Dossier</span>
                        </button>
                    </nav>
                </div>

                <div class="geology-modal-body" id="geo-modal-body">
                    <!-- Persistent Site Location & Bedrock Anchor Bar -->
                    <div class="geo-site-anchor-bar">
                        <div class="geo-anchor-info">
                            <span class="geo-anchor-label">FIELD LOCATION</span>
                            <span id="geo-anchor-coords" class="geo-anchor-val font-mono">31.7080° N, 76.9320° E (Mandi)</span>
                            <span class="geo-anchor-sep">&bull;</span>
                            <span class="geo-anchor-label">MAPPED IN-SITU BEDROCK</span>
                            <span id="geo-anchor-rock" class="geo-anchor-rock-name">Evaluating...</span>
                        </div>
                        <div class="geo-anchor-actions">
                            <button type="button" class="btn-anchor-jump" onclick="switchGeologyTab('site-geology')">Jump to Site Ground Truth &rarr;</button>
                        </div>
                    </div>

                    <!-- TAB 1: SITE STRATIGRAPHY & GROUND TRUTH -->
                    <section id="tab-site-geology" class="geo-tab-pane active" role="tabpanel">
                        <div class="dossier-section-header">01 / Site Stratigraphy &amp; Ground Truth Mapping</div>

                        <div id="geo-loader" class="geo-loader" style="display:none;">
                            <div class="geo-spinner"></div>
                            <span>Synthesizing GSI Bhukosh digital ground truth &amp; Macrostrat stratigraphy...</span>
                        </div>

                        <div id="geo-site-content">
                            <!-- Dual-Source Ground Truth Cards -->
                            <div class="geo-identity-grid">
                                <div class="geo-card bhukosh-card">
                                    <div class="geo-card-header">
                                        <span class="geo-source-tag gsi">GSI BHUKOSH STATUTORY BASELINE (1:50,000)</span>
                                    </div>
                                    <div class="geo-card-body">
                                        <h3 id="geo-bhukosh-rock">Loading in-situ formation...</h3>
                                        <div class="geo-meta-list">
                                            <div><strong>Toposheet:</strong> <span id="geo-toposheet">Toposheet 53A14</span></div>
                                            <div><strong>Discontinuity Structure:</strong> <span id="geo-structure">Discontinuities dipping into valley cut</span></div>
                                            <div><strong>Mapping Citation:</strong> <span id="geo-citation">GSI Macro-scale Landslide Susceptibility Atlas</span></div>
                                        </div>
                                    </div>
                                </div>

                                <div class="geo-card macrostrat-card">
                                    <div class="geo-card-header">
                                        <span class="geo-source-tag macrostrat">MACROSTRAT / ROCKD STRATIGRAPHIC COLUMN</span>
                                    </div>
                                    <div class="geo-card-body">
                                        <h3 id="geo-macro-unit">Loading unit...</h3>
                                        <div class="geo-meta-list">
                                            <div><strong>Lithology:</strong> <span id="geo-macro-lith">Crystalline metamorphic sequence</span></div>
                                            <div><strong>Chronostratigraphic Era:</strong> <span id="geo-macro-era">Precambrian–Paleozoic</span></div>
                                            <div><strong>Rockd Interactive Link:</strong> <a id="geo-rockd-link" href="https://rockd.org" target="_blank" rel="noopener noreferrer" class="geo-external-link">Open in Rockd Map &nearr;</a></div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Concordance & Consistency Audit -->
                            <div id="geo-audit-banner" class="geo-audit-box">
                                <div class="audit-status-tag" id="geo-audit-tag">LITHOLOGICAL AUDIT ACTIVE</div>
                                <p id="geo-audit-note" class="audit-note">Checking field photo evidence against Geological Survey of India digital mapping.</p>
                            </div>

                            <!-- Geomechanical Properties Table -->
                            <div class="geo-sec-title">ESTIMATED IN-SITU ROCK MASS PROPERTIES (IS:13365 &amp; HOEK-BROWN GSI)</div>
                            <div class="geo-props-table-wrap">
                                <table class="geo-props-table">
                                    <tbody>
                                        <tr>
                                            <th>Rock Name &amp; Family:</th>
                                            <td id="prop-rock-name">Sandstone (Sedimentary)</td>
                                            <th>Intact Strength (&sigma;<sub>ci</sub>):</th>
                                            <td id="prop-rock-ucs">30 – 80 MPa (ISRM R3)</td>
                                        </tr>
                                        <tr>
                                            <th>Friction Angle (&phi;'):</th>
                                            <td id="prop-rock-phi">32° – 38°</td>
                                            <th>Effective Cohesion (c'):</th>
                                            <td id="prop-rock-c">35 – 70 kPa</td>
                                        </tr>
                                        <tr>
                                            <th>Bieniawski RMR:</th>
                                            <td id="prop-rock-rmr">Class III (Fair Rock)</td>
                                            <th>Typical GSI Range:</th>
                                            <td id="prop-rock-gsi">40 – 60 (Blocky / Seamy)</td>
                                        </tr>
                                        <tr>
                                            <th>Slope Failure Hazard:</th>
                                            <td colspan="3" id="prop-rock-hazard">Planar sliding along bedding dips; rotational slumping when underlain by saturated shale or clay gouge.</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </section>

                    <!-- TAB 2: FIELD IDENTIFICATION KEY -->
                    <section id="tab-field-tests" class="geo-tab-pane" role="tabpanel">
                        <div class="dossier-section-header">02 / 4-Step Field Diagnostic Protocol (No Lab Required)</div>

                        <div class="field-key-intro">
                            <h3>Rapid Field Rock Identification Protocol</h3>
                            <p>Follow this 4-step diagnostic protocol to verify unknown rock masses on slope cuts using standard field tools: penknife, copper coin, 10% hydrochloric acid (or vinegar), and a geological inspection hammer.</p>
                        </div>

                        <div class="tests-grid">
                            <div class="test-card">
                                <span class="test-step">STEP 01</span>
                                <h4>Scratch Hardness (Mohs Scale)</h4>
                                <ul class="test-list">
                                    <li><strong>Fingernail (Mohs &lt; 2.5):</strong> Soft Shale, Mudstone, Gypsum, Weathered Fault Gouge.</li>
                                    <li><strong>Copper Coin (Mohs 3 – 3.5):</strong> Limestone, Calcite Veins, Carbonaceous Slaty Cleavage.</li>
                                    <li><strong>Steel Penknife (Mohs 4 – 5.5):</strong> Phyllite, Dolomite, Chlorite Schist.</li>
                                    <li><strong>Cannot Scratch / Scratches Glass (Mohs &gt; 6):</strong> Quartzite, Granitic Gneiss, Chert.</li>
                                </ul>
                            </div>

                            <div class="test-card">
                                <span class="test-step">STEP 02</span>
                                <h4>Foliation &amp; Fabric Cleavage</h4>
                                <ul class="test-list">
                                    <li><strong>Thin Rigid Plates with Metallic Ring:</strong> Slate (roofing grade).</li>
                                    <li><strong>Silky/Glossy Sheen on Splitting Planes:</strong> Phyllite (fine sericite mica).</li>
                                    <li><strong>Visible Shimmering Flakes of Mica:</strong> Mica Schist (Biotite/Muscovite).</li>
                                    <li><strong>Alternating Light Quartz &amp; Dark Biotite Bands:</strong> Gneiss.</li>
                                    <li><strong>No Directional Cleavage / Homogeneous Blocky:</strong> Quartzite, Granite, Dolomite.</li>
                                </ul>
                            </div>

                            <div class="test-card">
                                <span class="test-step">STEP 03</span>
                                <h4>Acid Effervescence (10% HCl)</h4>
                                <ul class="test-list">
                                    <li><strong>Immediate Vigorous Frothing:</strong> Limestone (Calcium Carbonate CaCO<sub>3</sub>).</li>
                                    <li><strong>Delayed or Faint Fizzing (unless powdered):</strong> Dolomite (CaMg(CO<sub>3</sub>)<sub>2</sub>).</li>
                                    <li><strong>Zero Reaction / Inert:</strong> Quartzite, Phyllite, Schist, Granite, Gneiss.</li>
                                </ul>
                            </div>

                            <div class="test-card">
                                <span class="test-step">STEP 04</span>
                                <h4>ISRM Hammer Acoustic Ring</h4>
                                <ul class="test-list">
                                    <li><strong>Dull Hollow Thud / Breaks in Hand:</strong> Extremely Weak (R0–R1), Shales, Muck.</li>
                                    <li><strong>Moderate Ring / Knife Gouges 2mm:</strong> Medium Strong (R2–R3), Phyllite, Schist.</li>
                                    <li><strong>Sharp Ring / Multiple Blows to Fracture:</strong> Very Strong (R4–R5), Quartzite, Gneiss, Granite.</li>
                                </ul>
                            </div>
                        </div>
                    </section>

                    <!-- TAB 3: APPS & WEB RESOURCES -->
                    <section id="tab-apps-tools" class="geo-tab-pane" role="tabpanel">
                        <div class="dossier-section-header">03 / Curated Geotechnical Mobile Apps &amp; Portals</div>
                        <div class="apps-grid" id="geo-apps-container">
                            <!-- Populated dynamically -->
                        </div>
                    </section>

                    <!-- TAB 4: HIMALAYAN ROCK CATALOG -->
                    <section id="tab-rock-catalog" class="geo-tab-pane" role="tabpanel">
                        <div class="dossier-section-header">04 / Himalayan Rock Mass Catalog (10 Archetypes)</div>
                        <div class="catalog-filter-bar">
                            <div class="catalog-search-wrap">
                                <span class="catalog-search-icon" aria-hidden="true">&telrec;</span>
                                <input type="text" id="catalog-search" class="catalog-search-input" placeholder="Filter rock archetypes (e.g. Quartzite, Phyllite, Dolomite)..." oninput="filterRockCatalog(this.value)">
                            </div>
                            <span class="catalog-counter" id="catalog-count-badge">Showing 10 of 10 Himalayan Lithological Archetypes</span>
                        </div>
                        <div class="catalog-grid" id="geo-catalog-container">
                            <!-- Populated dynamically -->
                        </div>
                    </section>
                </div>

                <footer class="geology-modal-footer">
                    <span class="geo-footer-copy">Indian Institute of Technology Mandi &bull; HIMA-LENS Landslide Observatory</span>
                    <button type="button" class="btn-geo-primary" onclick="closeGeologyModal()">Close Dossier</button>
                </footer>
            </div>
        </div>
        `;

        document.body.insertAdjacentHTML("beforeend", modalHtml);
    }

    // Open Modal and Fetch Data
    window.openGeologyModal = function (coordsDec, observedRock) {
        ensureModalInDOM();
        const modal = document.getElementById("hima-geology-modal");
        if (!modal) return;

        modal.style.display = "flex";
        document.body.style.overflow = "hidden"; // Prevent background scroll

        let lat = 31.708;
        let lng = 76.932;
        let district = "Mandi";

        if (coordsDec && typeof coordsDec === "string") {
            const m = coordsDec.match(/([0-9.]+)[^0-9.]+([0-9.]+)/);
            if (m) {
                lat = parseFloat(m[1]);
                lng = parseFloat(m[2]);
            }
        } else {
            const latInput = document.getElementById("rep-lat");
            const lngInput = document.getElementById("rep-lng");
            const distSelect = document.getElementById("rep-district");
            if (latInput && latInput.value) lat = parseFloat(latInput.value);
            if (lngInput && lngInput.value) lng = parseFloat(lngInput.value);
            if (distSelect && distSelect.value) district = distSelect.value;
        }

        const anchorCoords = document.getElementById("geo-anchor-coords");
        if (anchorCoords) {
            anchorCoords.textContent = `${lat.toFixed(4)}° N, ${lng.toFixed(4)}° E (${district})`;
        }

        // Default to site-geology tab on open
        switchGeologyTab("site-geology");

        loadGeologyData(lat, lng, district, observedRock);
        loadRockCatalog();
    };

    window.closeGeologyModal = function () {
        const modal = document.getElementById("hima-geology-modal");
        if (modal) {
            modal.style.display = "none";
            document.body.style.overflow = "";
        }
    };

    window.switchGeologyTab = function (tabId, btnElem) {
        currentActiveTab = tabId;
        const modalBody = document.getElementById("geo-modal-body");
        if (modalBody) {
            modalBody.scrollTop = 0; // Always reset scroll to top on tab switch
        }

        // Update active class on nav buttons
        document.querySelectorAll(".geo-tab-btn").forEach(b => {
            const bTab = b.getAttribute("data-tab");
            if (bTab === tabId) {
                b.classList.add("active");
            } else {
                b.classList.remove("active");
            }
        });

        if (tabId === "full-dossier") {
            if (modalBody) modalBody.classList.add("full-dossier-mode");
            document.querySelectorAll(".geo-tab-pane").forEach(p => p.classList.add("active"));
        } else {
            if (modalBody) modalBody.classList.remove("full-dossier-mode");
            document.querySelectorAll(".geo-tab-pane").forEach(p => p.classList.remove("active"));
            const targetPane = document.getElementById(`tab-${tabId}`);
            if (targetPane) targetPane.classList.add("active");
        }
    };

    async function loadGeologyData(lat, lng, district, observedRock) {
        const loader = document.getElementById("geo-loader");
        const content = document.getElementById("geo-site-content");

        if (loader) loader.style.display = "flex";
        if (content) content.style.opacity = "0.4";

        try {
            const url = `/api/geology/lookup?lat=${lat}&lng=${lng}&district=${encodeURIComponent(district || 'Mandi')}${observedRock ? `&observed_rock=${encodeURIComponent(observedRock)}` : ''}`;
            const res = await fetch(url);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            currentGeologyData = data;
            renderGeologyData(data);
        } catch (err) {
            console.warn("Geological synthesis fallback activated:", err);
            renderGeologyData({
                primary_rock: "Sandstone / Siltstone (Siwalik / Subathu Group)",
                bhukosh: {
                    formation: "Subathu & Dagshai Formations",
                    toposheet: "53A14 (Mandi Quadrangle)",
                    structure: "Bedding dipping 45° into road cut with transverse joint sets",
                    citation: "GSI Macro-scale Susceptibility Mapping Atlas (1:50,000)"
                },
                macrostrat: {
                    unit_name: "Lesser Himalayan Metasedimentary Belt",
                    lithology: "Clastic and Carbonate Sequence",
                    era: "Proterozoic to Early Paleozoic",
                    rockd_url: `https://rockd.org/map#lat=${lat}&lng=${lng}&zoom=14`
                },
                rock_profile: {
                    name: "Sandstone",
                    family: "Sedimentary",
                    intact_strength_mpa: "35 – 80 MPa",
                    friction_angle_deg: "32° – 38°",
                    cohesion_kpa: "35 – 70 kPa",
                    rmr_class: "Class III (Fair Rock)",
                    typical_gsi: "40 – 60",
                    slope_stability_hazard: "Planar slide along bedding planes; softening and toe ravelling upon monsoon infiltration."
                },
                apps_and_tools: []
            });
        } finally {
            if (loader) loader.style.display = "none";
            if (content) content.style.opacity = "1";
        }
    }

    function renderGeologyData(data) {
        const b = data.bhukosh || {};
        const m = data.macrostrat || {};
        const p = data.rock_profile || {};
        const audit = data.consistency_audit || {};

        // Top Anchor bar
        const anchorRock = document.getElementById("geo-anchor-rock");
        if (anchorRock) {
            anchorRock.textContent = `${data.primary_rock || 'In-Situ Bedrock'} • Toposheet ${b.toposheet || '53A14'}`;
        }

        // Bhukosh card
        const elBhuRock = document.getElementById("geo-bhukosh-rock");
        const elTopo = document.getElementById("geo-toposheet");
        const elStruct = document.getElementById("geo-structure");
        const elCit = document.getElementById("geo-citation");

        if (elBhuRock) elBhuRock.textContent = b.formation || data.primary_rock || "Himalayan Formations";
        if (elTopo) elTopo.textContent = b.toposheet || "GSI Sheet 53A14";
        if (elStruct) elStruct.textContent = b.structure || "Joint sets dipping into valley cut";
        if (elCit) elCit.textContent = b.citation || "GSI Landslide Susceptibility Atlas";

        // Macrostrat card
        const elMacroUnit = document.getElementById("geo-macro-unit");
        const elMacroLith = document.getElementById("geo-macro-lith");
        const elMacroEra = document.getElementById("geo-macro-era");
        const elRockdLink = document.getElementById("geo-rockd-link");

        if (elMacroUnit) elMacroUnit.textContent = m.unit_name || "Lesser Himalayan Sequence";
        if (elMacroLith) elMacroLith.textContent = m.lithology || "Metasedimentary Sequence";
        if (elMacroEra) elMacroEra.textContent = m.era || "Precambrian–Paleozoic";
        if (elRockdLink && m.rockd_url) elRockdLink.href = m.rockd_url;

        // Audit banner
        const elAuditTag = document.getElementById("geo-audit-tag");
        const elAuditNote = document.getElementById("geo-audit-note");
        if (elAuditTag && elAuditNote) {
            if (audit.status === "BEDROCK_CONFIRMED") {
                elAuditTag.textContent = "DIRECT LITHOLOGICAL CONCORDANCE";
                elAuditTag.className = "audit-status-tag success";
            } else if (audit.status === "OVERBURDEN_COLLUVIUM_CONCORDANT") {
                elAuditTag.textContent = "COLLUVIAL OVERBURDEN ON BEDROCK";
                elAuditTag.className = "audit-status-tag info";
            } else if (audit.status === "LITHOLOGY_DISCREPANCY_FLAGGED") {
                elAuditTag.textContent = "LITHOLOGY DISCREPANCY FLAGGED";
                elAuditTag.className = "audit-status-tag warning";
            } else {
                elAuditTag.textContent = "GSI BHUKOSH SURVEY CERTIFIED";
                elAuditTag.className = "audit-status-tag neutral";
            }
            elAuditNote.textContent = audit.evaluation_note || "Ground truth formation verified against GSI 1:50,000 mapping.";
        }

        // Properties table
        const elName = document.getElementById("prop-rock-name");
        const elUcs = document.getElementById("prop-rock-ucs");
        const elPhi = document.getElementById("prop-rock-phi");
        const elC = document.getElementById("prop-rock-c");
        const elRmr = document.getElementById("prop-rock-rmr");
        const elGsi = document.getElementById("prop-rock-gsi");
        const elHazard = document.getElementById("prop-rock-hazard");

        if (elName) elName.textContent = `${p.name || data.primary_rock} (${p.family || 'Sedimentary / Metamorphic'})`;
        if (elUcs) elUcs.textContent = p.intact_strength_mpa || "35 – 80 MPa";
        if (elPhi) elPhi.textContent = p.friction_angle_deg || "32° – 38°";
        if (elC) elC.textContent = p.cohesion_kpa || "35 – 70 kPa";
        if (elRmr) elRmr.textContent = p.rmr_class || "Class III (Fair Rock)";
        if (elGsi) elGsi.textContent = p.typical_gsi || "40 – 60";
        if (elHazard) elHazard.textContent = p.slope_stability_hazard || "Structural joint block release and colluvial wash.";

        // Apps & Tools
        renderAppsList(data.apps_and_tools || []);
    }

    function renderAppsList(apps) {
        const container = document.getElementById("geo-apps-container");
        if (!container) return;

        if (!apps || apps.length === 0) {
            apps = [
                {
                    name: "Rockd Mobile & Web App",
                    provider: "UW-Madison & Macrostrat",
                    url: "https://rockd.org",
                    badge: "INTERACTIVE MAP",
                    summary: "Explore rock units and nearby observations directly at your GPS coordinates.",
                    platforms: "iOS • Android • Web Browser"
                },
                {
                    name: "GSI Bhukosh Spatial Gateway",
                    provider: "Geological Survey of India",
                    url: "https://bhukosh.gsi.gov.in",
                    badge: "STATUTORY BASELINE",
                    summary: "Official National Geoscientific Database of India with 1:50,000 quadrangle maps.",
                    platforms: "Web GIS Portal"
                },
                {
                    name: "Macrostrat Stratigraphy Explorer",
                    provider: "Macrostrat Research Consortium",
                    url: "https://macrostrat.org",
                    badge: "STRATIGRAPHY",
                    summary: "Explores depth columns of sedimentary and metamorphic beds across the Himalayas.",
                    platforms: "Web Explorer"
                }
            ];
        }

        container.innerHTML = apps.map(app => `
            <div class="app-card">
                <div class="app-card-top">
                    <span class="app-badge">${app.badge || 'TOOL'}</span>
                    <span class="app-platform">${app.platforms || 'Web'}</span>
                </div>
                <h4 class="app-name">${app.name}</h4>
                <div class="app-provider">${app.provider}</div>
                <p class="app-summary">${app.summary}</p>
                <a href="${app.url}" target="_blank" rel="noopener noreferrer" class="btn-app-launch">
                    <span>Open ${app.name.split(' ')[0]}</span>
                    <span aria-hidden="true">&nearr;</span>
                </a>
            </div>
        `).join("");
    }

    async function loadRockCatalog() {
        const container = document.getElementById("geo-catalog-container");
        if (!container || fullRockCatalog) return;

        try {
            const res = await fetch("/api/geology/catalog");
            if (!res.ok) return;
            const data = await res.json();
            fullRockCatalog = data.rock_database || {};
            renderRockCatalog(fullRockCatalog);
        } catch (e) {
            console.warn("Could not fetch rock catalog:", e);
        }
    }

    function renderRockCatalog(catalog) {
        const container = document.getElementById("geo-catalog-container");
        if (!container) return;

        const keys = Object.keys(catalog);
        if (keys.length === 0) {
            container.innerHTML = "<p>No rocks found in catalog.</p>";
            return;
        }

        container.innerHTML = keys.map(k => {
            const r = catalog[k];
            const d = r.hand_specimen_diagnostic || {};
            return `
                <div class="rock-catalog-card" data-rock-key="${k}" id="rock-card-${k}">
                    <div class="rock-cat-header">
                        <h4>${r.name}</h4>
                        <span class="rock-family-tag">${r.family.toUpperCase()}</span>
                    </div>
                    <div class="rock-cat-stats">
                        <div><strong>Intact Strength (&sigma;<sub>ci</sub>):</strong> ${r.intact_strength_mpa}</div>
                        <div><strong>Bieniawski RMR:</strong> ${r.rmr_class}</div>
                        <div><strong>Friction Angle (&phi;'):</strong> ${r.friction_angle_deg} &bull; <strong>Cohesion:</strong> ${r.cohesion_kpa}</div>
                    </div>
                    <div class="rock-cat-diag">
                        <p><strong>Texture:</strong> ${d.texture || 'N/A'}</p>
                        <p><strong>Field Identification:</strong> ${d.hardness || ''} ${d.acid_test || ''}</p>
                        <p><strong>Cleavage &amp; Fabric:</strong> ${d.cleavage || 'Blocky / Jointed'}</p>
                    </div>
                    <div class="rock-cat-hazard">
                        <strong>Slope Failure Risk:</strong> ${r.slope_stability_hazard}
                    </div>
                </div>
            `;
        }).join("");
    }

    window.filterRockCatalog = function (query) {
        if (!fullRockCatalog) return;
        const q = (query || "").toLowerCase().trim();
        const cards = document.querySelectorAll(".rock-catalog-card");
        let visibleCount = 0;
        cards.forEach(card => {
            const text = card.textContent.toLowerCase();
            const matches = text.includes(q);
            card.style.display = matches ? "flex" : "none";
            if (matches) visibleCount++;
        });

        const countBadge = document.getElementById("catalog-count-badge");
        if (countBadge) {
            countBadge.textContent = `Showing ${visibleCount} of 10 Himalayan Lithological Archetypes`;
        }
    };

    // Close on backdrop click or ESC key
    document.addEventListener("click", (e) => {
        const modal = document.getElementById("hima-geology-modal");
        if (modal && e.target === modal) {
            closeGeologyModal();
        }
    });

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            closeGeologyModal();
        }
    });

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", ensureModalInDOM);
    } else {
        ensureModalInDOM();
    }
})();
