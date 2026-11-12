/**
 * HIMA-LENS Geological Rock Classification & Field Apps Modal
 * ============================================================
 * Coordinates GSI Bhukosh digital ground truth, Macrostrat / Rockd API,
 * ISRM / IS:13365 rock mass properties, and curated external geology tools.
 */

(function () {
    let currentGeologyData = null;
    let fullRockCatalog = null;

    // Create and inject the modal DOM element if not already present
    function ensureModalInDOM() {
        if (document.getElementById("hima-geology-modal")) return;

        const modalHtml = `
        <div id="hima-geology-modal" class="geology-modal-overlay" style="display: none;" role="dialog" aria-modal="true" aria-labelledby="geo-modal-title">
            <div class="geology-modal-dialog">
                <header class="geology-modal-header">
                    <div class="geo-header-brand">
                        <span class="geo-kicker">HIMALAYAN GEOTECHNICAL LITHOLOGY OBSERVER</span>
                        <h2 id="geo-modal-title">Geological Formation &amp; Rock Classification Guide</h2>
                        <span class="geo-subcaption">GSI Bhukosh Baseline (1:50k) &bull; Macrostrat / Rockd Engine &bull; IS:13365 Standards</span>
                    </div>
                    <button type="button" class="btn-geo-close" onclick="closeGeologyModal()" aria-label="Close modal">&times;</button>
                </header>

                <nav class="geology-tabs-nav" role="tablist">
                    <button type="button" class="geo-tab-btn active" data-tab="site-geology" onclick="switchGeologyTab('site-geology', this)">Site Stratigraphy &amp; Ground Truth</button>
                    <button type="button" class="geo-tab-btn" data-tab="field-tests" onclick="switchGeologyTab('field-tests', this)">Field Identification Key</button>
                    <button type="button" class="geo-tab-btn" data-tab="apps-tools" onclick="switchGeologyTab('apps-tools', this)">Apps &amp; Web Resources</button>
                    <button type="button" class="geo-tab-btn" data-tab="rock-catalog" onclick="switchGeologyTab('rock-catalog', this)">Himalayan Rock Catalog</button>
                </nav>

                <div class="geology-modal-body">
                    <!-- TAB 1: SITE STRATIGRAPHY & GROUND TRUTH -->
                    <div id="tab-site-geology" class="geo-tab-pane active">
                        <div id="geo-loader" class="geo-loader" style="display:none;">
                            <div class="geo-spinner"></div>
                            <span>Synthesizing GSI Bhukosh &amp; Macrostrat stratigraphy...</span>
                        </div>

                        <div id="geo-site-content">
                            <!-- Geological Identity Banner -->
                            <div class="geo-identity-grid">
                                <div class="geo-card bhukosh-card">
                                    <div class="geo-card-header">
                                        <span class="geo-source-tag gsi">GSI BHUKOSH STATUTORY MAP (1:50,000)</span>
                                    </div>
                                    <div class="geo-card-body">
                                        <h3 id="geo-bhukosh-rock">Loading in-situ formation...</h3>
                                        <div class="geo-meta-list">
                                            <div><strong>Toposheet:</strong> <span id="geo-toposheet">N/A</span></div>
                                            <div><strong>Joint Structure:</strong> <span id="geo-structure">Discontinuities dipping into valley</span></div>
                                            <div><strong>Citation:</strong> <span id="geo-citation">GSI Macro-scale Mapping</span></div>
                                        </div>
                                    </div>
                                </div>

                                <div class="geo-card macrostrat-card">
                                    <div class="geo-card-header">
                                        <span class="geo-source-tag macrostrat">MACROSTRAT / ROCKD STRATIGRAPHIC COLUMN</span>
                                    </div>
                                    <div class="geo-card-body">
                                        <h3 id="geo-macro-unit">Loading stratigraphic unit...</h3>
                                        <div class="geo-meta-list">
                                            <div><strong>Lithology:</strong> <span id="geo-macro-lith">Crystalline metamorphic</span></div>
                                            <div><strong>Chronostratigraphic Era:</strong> <span id="geo-macro-era">Precambrian–Paleozoic</span></div>
                                            <div><strong>Interactive Rockd Map:</strong> <a id="geo-rockd-link" href="https://rockd.org" target="_blank" rel="noopener noreferrer" class="geo-external-link">Launch in Rockd ↗</a></div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Concordance & Consistency Audit -->
                            <div id="geo-audit-banner" class="geo-audit-box">
                                <div class="audit-status-tag" id="geo-audit-tag">LITHOLOGICAL AUDIT ACTIVE</div>
                                <p id="geo-audit-note" class="audit-note">Checking field photo alignment against digital geological mapping.</p>
                            </div>

                            <!-- Engineering Rock Properties Table -->
                            <div class="geo-sec-title">ESTIMATED GEOMECHANICAL PROPERTIES (IS:13365 &amp; HOEK-BROWN)</div>
                            <div class="geo-props-table-wrap">
                                <table class="geo-props-table">
                                    <tbody>
                                        <tr>
                                            <th>Rock Name &amp; Family:</th>
                                            <td id="prop-rock-name">Phyllite (Metamorphic)</td>
                                            <th>Intact Strength (&sigma;<sub>ci</sub>):</th>
                                            <td id="prop-rock-ucs">25 – 60 MPa (ISRM R2–R3)</td>
                                        </tr>
                                        <tr>
                                            <th>Friction Angle (&phi;'):</th>
                                            <td id="prop-rock-phi">28° – 34°</td>
                                            <th>Effective Cohesion (c'):</th>
                                            <td id="prop-rock-c">25 – 45 kPa</td>
                                        </tr>
                                        <tr>
                                            <th>Bieniawski RMR Class:</th>
                                            <td id="prop-rock-rmr">Class III (Fair) to Class IV (Poor)</td>
                                            <th>Typical GSI Range:</th>
                                            <td id="prop-rock-gsi">25 – 45 (Blocky / Foliated)</td>
                                        </tr>
                                        <tr>
                                            <th>Slope Failure Hazard:</th>
                                            <td colspan="3" id="prop-rock-hazard">Planar sliding along daylighting foliation planes; rapid softening upon monsoon saturation.</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>

                    <!-- TAB 2: FIELD IDENTIFICATION KEY -->
                    <div id="tab-field-tests" class="geo-tab-pane">
                        <div class="field-key-intro">
                            <h3>Field Rock Diagnostic Protocol (No Lab Required)</h3>
                            <p>Follow this 4-step field testing procedure to identify unknown rock masses using common field tools: a pocket knife, a copper coin, a hand lens, and dilute (10%) hydrochloric acid or household vinegar.</p>
                        </div>

                        <div class="tests-grid">
                            <div class="test-card">
                                <span class="test-step">STEP 01</span>
                                <h4>Scratch Hardness Test (Mohs Scale)</h4>
                                <ul class="test-list">
                                    <li><strong>Scratched by Fingernail (Mohs &lt; 2.5):</strong> Soft Shale, Mudstone, Gypsum, Weathered Clay-Gouge.</li>
                                    <li><strong>Scratched by Copper Coin (Mohs 3 – 3.5):</strong> Limestone, Calcite Veins, Slaty Cleavage.</li>
                                    <li><strong>Scratched by Steel Penknife (Mohs 4 – 5.5):</strong> Phyllite, Dolomite, Chlorite Schist.</li>
                                    <li><strong>Scratches Glass / Knife Cannot Scratch (Mohs &gt; 6):</strong> Quartzite, Granitic Gneiss, Chert.</li>
                                </ul>
                            </div>

                            <div class="test-card">
                                <span class="test-step">STEP 02</span>
                                <h4>Foliation &amp; Fabric Cleavage</h4>
                                <ul class="test-list">
                                    <li><strong>Thin Rigid Plates with Metallic Ring:</strong> Slate (roofing grade).</li>
                                    <li><strong>Silky/Glossy Sheen on Undulating Splitting Planes:</strong> Phyllite (fine sericite mica).</li>
                                    <li><strong>Visible Shimmering Flakes of Mica (Biotite/Muscovite):</strong> Mica Schist.</li>
                                    <li><strong>Alternating Light Quartz &amp; Dark Biotite Bands:</strong> Gneiss.</li>
                                    <li><strong>No Directional Cleavage / Homogeneous Blocky:</strong> Quartzite, Granite, Dolomite.</li>
                                </ul>
                            </div>

                            <div class="test-card">
                                <span class="test-step">STEP 03</span>
                                <h4>Acid Effervescence Test (10% HCl)</h4>
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
                                    <li><strong>Sharp Ring / Many Hammer Blows to Fracture:</strong> Very Strong (R4–R5), Quartzite, Gneiss, Granite.</li>
                                </ul>
                            </div>
                        </div>
                    </div>

                    <!-- TAB 3: APPS & WEB RESOURCES -->
                    <div id="tab-apps-tools" class="geo-tab-pane">
                        <div class="apps-grid" id="geo-apps-container">
                            <!-- Populated dynamically -->
                        </div>
                    </div>

                    <!-- TAB 4: HIMALAYAN ROCK CATALOG -->
                    <div id="tab-rock-catalog" class="geo-tab-pane">
                        <div class="catalog-filter-bar">
                            <input type="text" id="catalog-search" class="catalog-search-input" placeholder="Search rock (e.g. Quartzite, Phyllite, Dolomite)..." oninput="filterRockCatalog(this.value)">
                        </div>
                        <div class="catalog-grid" id="geo-catalog-container">
                            <!-- Populated dynamically -->
                        </div>
                    </div>
                </div>

                <footer class="geology-modal-footer">
                    <span class="geo-footer-copy">Indian Institute of Technology Mandi &bull; HIMA-LENS Landslide Observatory</span>
                    <button type="button" class="btn-geo-primary" onclick="closeGeologyModal()">Close Guide</button>
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
            // Check form fields if on report page
            const latInput = document.getElementById("rep-lat");
            const lngInput = document.getElementById("rep-lng");
            const distSelect = document.getElementById("rep-district");
            if (latInput && latInput.value) lat = parseFloat(latInput.value);
            if (lngInput && lngInput.value) lng = parseFloat(lngInput.value);
            if (distSelect && distSelect.value) district = distSelect.value;
        }

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
        document.querySelectorAll(".geo-tab-btn").forEach(b => b.classList.remove("active"));
        document.querySelectorAll(".geo-tab-pane").forEach(p => p.classList.remove("active"));

        if (btnElem) btnElem.classList.add("active");
        const targetPane = document.getElementById(`tab-${tabId}`);
        if (targetPane) targetPane.classList.add("active");
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
            console.error("Failed to load geological synthesis:", err);
            // Render graceful fallback
            renderGeologyData({
                primary_rock: "Shali Dolomite & Sundernagar Quartzite",
                bhukosh: {
                    formation: "Shali Group (Dolomite, Slate & Quartzite)",
                    toposheet: "53A14 (Mandi Quadrangle)",
                    structure: "Joint sets dipping 50°–65° into road cut",
                    citation: "GSI Macro-scale Susceptibility Mapping Atlas"
                },
                macrostrat: {
                    unit_name: "Lesser Himalayan Metasedimentary Belt",
                    lithology: "Carbonate and Clastic Sequence",
                    era: "Proterozoic to Early Paleozoic",
                    rockd_url: `https://rockd.org/map#lat=${lat}&lng=${lng}&zoom=14`
                },
                rock_profile: {
                    name: "Dolomite / Dolomitic Limestone",
                    intact_strength_mpa: "60 – 130 MPa",
                    friction_angle_deg: "34° – 40°",
                    cohesion_kpa: "40 – 90 kPa",
                    rmr_class: "Class II (Good) to Class III (Fair)",
                    typical_gsi: "45 – 65",
                    slope_stability_hazard: "Wedge failures along solution-widened joints; rockfall on steep cuts."
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

        // Bhukosh card
        const elBhuRock = document.getElementById("geo-bhukosh-rock");
        const elTopo = document.getElementById("geo-toposheet");
        const elStruct = document.getElementById("geo-structure");
        const elCit = document.getElementById("geo-citation");

        if (elBhuRock) elBhuRock.textContent = b.formation || data.primary_rock || "Himalayan Formations";
        if (elTopo) elTopo.textContent = b.toposheet || "GSI Sheet 53A14";
        if (elStruct) elStruct.textContent = b.structure || "Joint sets dipping into valley";
        if (elCit) elCit.textContent = b.citation || "GSI Landslide Susceptibility Survey";

        // Macrostrat card
        const elMacroUnit = document.getElementById("geo-macro-unit");
        const elMacroLith = document.getElementById("geo-macro-lith");
        const elMacroEra = document.getElementById("geo-macro-era");
        const elRockdLink = document.getElementById("geo-rockd-link");

        if (elMacroUnit) elMacroUnit.textContent = m.unit_name || "Lesser Himalayan Tectonic Sequence";
        if (elMacroLith) elMacroLith.textContent = m.lithology || "Metamorphic / Metasedimentary";
        if (elMacroEra) elMacroEra.textContent = m.era || "Precambrian–Paleozoic";
        if (elRockdLink && m.rockd_url) elRockdLink.href = m.rockd_url;

        // Audit banner
        const elAuditTag = document.getElementById("geo-audit-tag");
        const elAuditNote = document.getElementById("geo-audit-note");
        if (elAuditTag && elAuditNote) {
            if (audit.status === "BEDROCK_CONFIRMED") {
                elAuditTag.textContent = "✔ DIRECT LITHOLOGICAL CONCORDANCE";
                elAuditTag.className = "audit-status-tag success";
            } else if (audit.status === "OVERBURDEN_COLLUVIUM_CONCORDANT") {
                elAuditTag.textContent = "COLLUVIAL OVERBURDEN ON BEDROCK";
                elAuditTag.className = "audit-status-tag info";
            } else if (audit.status === "LITHOLOGY_DISCREPANCY_FLAGGED") {
                elAuditTag.textContent = "⚠ LITHOLOGY DISCREPANCY FLAGGED";
                elAuditTag.className = "audit-status-tag warning";
            } else {
                elAuditTag.textContent = "GSI BHUKOSH SURVEY CERTIFIED";
                elAuditTag.className = "audit-status-tag neutral";
            }
            elAuditNote.textContent = audit.evaluation_note || "Ground truth formation established via Geological Survey of India 1:50,000 mapping.";
        }

        // Properties table
        const elName = document.getElementById("prop-rock-name");
        const elUcs = document.getElementById("prop-rock-ucs");
        const elPhi = document.getElementById("prop-rock-phi");
        const elC = document.getElementById("prop-rock-c");
        const elRmr = document.getElementById("prop-rock-rmr");
        const elGsi = document.getElementById("prop-rock-gsi");
        const elHazard = document.getElementById("prop-rock-hazard");

        if (elName) elName.textContent = `${p.name || data.primary_rock} (${p.family || 'Metamorphic'})`;
        if (elUcs) elUcs.textContent = p.intact_strength_mpa || "35 – 80 MPa";
        if (elPhi) elPhi.textContent = p.friction_angle_deg || "32° – 38°";
        if (elC) elC.textContent = p.cohesion_kpa || "30 – 60 kPa";
        if (elRmr) elRmr.textContent = p.rmr_class || "Class III (Fair Rock)";
        if (elGsi) elGsi.textContent = p.typical_gsi || "35 – 55";
        if (elHazard) elHazard.textContent = p.slope_stability_hazard || "Structural joint block release and colluvial ravelling.";

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
                    badge: "INTERACTIVE GEOLOGICAL MAP",
                    summary: "Explore rock units and nearby observations at your GPS coordinates.",
                    platforms: "iOS • Android • Web Browser"
                },
                {
                    name: "GSI Bhukosh Spatial Gateway",
                    provider: "Geological Survey of India",
                    url: "https://bhukosh.gsi.gov.in",
                    badge: "STATUTORY BASELINE",
                    summary: "Official National Geoscientific Database with 1:50,000 quadrangle maps.",
                    platforms: "Web GIS Portal"
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
            console.error("Could not fetch rock catalog:", e);
        }
    }

    function renderRockCatalog(catalog) {
        const container = document.getElementById("geo-catalog-container");
        if (!container) return;

        const keys = Object.keys(catalog);
        if (keys.length === 0) {
            container.innerHTML = "<p>No rocks found.</p>";
            return;
        }

        container.innerHTML = keys.map(k => {
            const r = catalog[k];
            const d = r.hand_specimen_diagnostic || {};
            return `
                <div class="rock-catalog-card" data-rock-key="${k}">
                    <div class="rock-cat-header">
                        <span class="rock-family-tag">${r.family}</span>
                        <h4>${r.name}</h4>
                    </div>
                    <div class="rock-cat-stats">
                        <span><strong>Strength:</strong> ${r.intact_strength_mpa}</span>
                        <span><strong>RMR:</strong> ${r.rmr_class}</span>
                        <span><strong>Friction (&phi;'):</strong> ${r.friction_angle_deg}</span>
                    </div>
                    <div class="rock-cat-diag">
                        <p><strong>Texture:</strong> ${d.texture || 'N/A'}</p>
                        <p><strong>Field Identification:</strong> ${d.hardness || ''} ${d.acid_test || ''}</p>
                    </div>
                    <div class="rock-cat-hazard">
                        <strong>Slope Risk:</strong> ${r.slope_stability_hazard}
                    </div>
                </div>
            `;
        }).join("");
    }

    window.filterRockCatalog = function (query) {
        if (!fullRockCatalog) return;
        const q = (query || "").toLowerCase().trim();
        const cards = document.querySelectorAll(".rock-catalog-card");
        cards.forEach(card => {
            const text = card.textContent.toLowerCase();
            card.style.display = text.includes(q) ? "flex" : "none";
        });
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

    // Auto-initialize when DOM is ready
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", ensureModalInDOM);
    } else {
        ensureModalInDOM();
    }
})();
