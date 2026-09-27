/**
 * HIMA-LENS: HP PWD Field Sheet Interactive AI Assessment Modal
 * Provides on-demand Gemini Vision analysis, interactive parameter tuning,
 * and high-fidelity official PDF generation.
 */

let currentAssessmentData = null;
let activeReportId = null;

function ensurePwdModalInDOM() {
  if (document.getElementById('pwd-assessment-modal')) return;

  const modalHtml = `
    <div id="pwd-assessment-modal" class="pwd-modal-overlay" style="display: none;">
      <div class="pwd-modal-card">
        <div class="pwd-modal-header">
          <div class="title-wrap">
            <span class="pwd-modal-badge">HP PWD AI Assessment</span>
            <div>
              <h3 class="pwd-modal-title">Landslide Technical Field Sheet</h3>
              <div class="pwd-modal-subtitle" id="pwd-modal-sub">Report ID: --</div>
            </div>
          </div>
          <button class="pwd-close-btn" onclick="closePwdAssessmentModal()">&times;</button>
        </div>

        <div class="pwd-modal-body">
          <!-- Loading State -->
          <div id="pwd-loader" class="pwd-loading-state">
            <div class="pwd-scanner-orb"></div>
            <div class="pwd-loading-title">Google Gemini Vision Analysis in Progress</div>
            <p class="pwd-loading-desc">
              Examining photograph, slope cut angle, in-situ rock jointing, carriageway blockage, 
              and computing IRC:SP:48 structural breast wall & earthwork volumes...
            </p>
          </div>

          <!-- Assessment Form (Hidden while loading) -->
          <div id="pwd-form" style="display: none;">
            
            <!-- Section 1: Road & Chainage -->
            <div class="pwd-form-section">
              <div class="pwd-section-head">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
                1. Road Metadata & Chainage
              </div>
              <div class="pwd-grid-2">
                <div class="pwd-field">
                  <label>Road Name / Section</label>
                  <input type="text" id="pwd-inp-road-name">
                </div>
                <div class="pwd-field">
                  <label>Location (Chainage RD)</label>
                  <input type="text" id="pwd-inp-chainage">
                </div>
                <div class="pwd-field">
                  <label>Type of Road</label>
                  <input type="text" id="pwd-inp-road-type">
                </div>
                <div class="pwd-field">
                  <label>Inspection Date</label>
                  <input type="date" id="pwd-inp-date">
                </div>
              </div>
            </div>

            <!-- Section 2: Structural Specifications -->
            <div class="pwd-form-section">
              <div class="pwd-section-head">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg>
                2. Recommended Plum Concrete Breast Wall Sizing
              </div>
              <div class="pwd-grid-3">
                <div class="pwd-field">
                  <label>Height H (meters)</label>
                  <input type="number" step="0.1" id="pwd-inp-wall-h">
                </div>
                <div class="pwd-field">
                  <label>Length L (meters)</label>
                  <input type="number" step="0.5" id="pwd-inp-wall-l">
                </div>
                <div class="pwd-field">
                  <label>Base Width (meters)</label>
                  <input type="number" step="0.05" id="pwd-inp-wall-base">
                </div>
              </div>
              <div class="pwd-field" style="margin-top: 10px;">
                <label>Concrete Grade & Specification</label>
                <input type="text" id="pwd-inp-wall-mat">
              </div>
            </div>

            <!-- Section 3: Earthworks & Emergency Actions -->
            <div class="pwd-form-section">
              <div class="pwd-section-head">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>
                3. Earthworks & Critical Safety Notices
              </div>
              <div class="pwd-grid-2">
                <div class="pwd-field">
                  <label>Estimated Excavation Volume (m³)</label>
                  <input type="number" step="1" id="pwd-inp-exc-vol">
                </div>
                <div class="pwd-field">
                  <label>Traffic Restoration Target</label>
                  <input type="text" id="pwd-inp-traffic">
                </div>
              </div>
              <div class="pwd-field" style="margin-top: 10px;">
                <label>Emergency Machinery Deployment</label>
                <input type="text" id="pwd-inp-machinery">
              </div>
              <div class="pwd-field" style="margin-top: 10px;">
                <label>Geotechnical Observations & Diagnostic Remarks</label>
                <textarea rows="3" id="pwd-inp-remarks"></textarea>
              </div>
            </div>

          </div>
        </div>

        <div class="pwd-modal-footer">
          <button class="pwd-btn pwd-btn-secondary" onclick="closePwdAssessmentModal()">Close</button>
          <div class="pwd-modal-actions">
            <button class="pwd-btn pwd-btn-primary" id="btn-print-official" onclick="submitAndOpenOfficialSheet()">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 6 2 18 2 18 9"></polyline><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path><rect x="6" y="14" width="12" height="8"></rect></svg>
              View &amp; Print Official Sheet
            </button>
          </div>
        </div>
      </div>
    </div>
  `;

  document.body.insertAdjacentHTML('beforeend', modalHtml);

  // Close on background click
  document.getElementById('pwd-assessment-modal').addEventListener('click', (e) => {
    if (e.target.id === 'pwd-assessment-modal') {
      closePwdAssessmentModal();
    }
  });
}

window.openPwdAssessmentModal = async function(reportId) {
  ensurePwdModalInDOM();
  activeReportId = reportId;

  const modal = document.getElementById('pwd-assessment-modal');
  const loader = document.getElementById('pwd-loader');
  const form = document.getElementById('pwd-form');
  const subtitle = document.getElementById('pwd-modal-sub');

  subtitle.innerText = `Report ID: ${reportId}`;
  loader.style.display = 'block';
  form.style.display = 'none';
  modal.style.display = 'flex';

  try {
    const res = await fetch(`/api/reports/${encodeURIComponent(reportId)}/ai-assessment`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });

    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const data = await res.json();

    if (data.success && data.assessment) {
      currentAssessmentData = data.assessment;
      populatePwdForm(data.assessment);
      loader.style.display = 'none';
      form.style.display = 'block';
    } else {
      throw new Error(data.message || 'Failed to generate assessment');
    }
  } catch (err) {
    console.error('Error fetching AI assessment:', err);
    loader.innerHTML = `
      <div style="color: #b91c1c; font-weight: 700; font-size: 15px; margin-bottom: 8px;">Assessment Generation Warning</div>
      <p style="color: #64748b; font-size: 13px;">${err.message || 'Could not reach AI assessment service.'}</p>
      <button class="pwd-btn pwd-btn-primary" style="margin-top: 16px;" onclick="openDirectSheet('${reportId}')">
        Open Standard Form
      </button>
    `;
  }
};

window.closePwdAssessmentModal = function() {
  const modal = document.getElementById('pwd-assessment-modal');
  if (modal) modal.style.display = 'none';
};

function populatePwdForm(assessment) {
  const meta = assessment.road_metadata || {};
  document.getElementById('pwd-inp-road-name').value = meta.road_name || '';
  document.getElementById('pwd-inp-chainage').value = meta.chainage || '';
  document.getElementById('pwd-inp-road-type').value = meta.road_type || 'ODR / Link Road (HP PWD)';
  document.getElementById('pwd-inp-date').value = meta.inspection_date ? meta.inspection_date.slice(0, 10) : new Date().toISOString().slice(0, 10);

  const bw = (assessment.structural_specifications || {}).breast_wall || {};
  document.getElementById('pwd-inp-wall-h').value = bw.height_m || 3.5;
  document.getElementById('pwd-inp-wall-l').value = bw.length_m || 18.0;
  document.getElementById('pwd-inp-wall-base').value = bw.base_width_m || 1.75;
  document.getElementById('pwd-inp-wall-mat').value = bw.material || 'Plum Concrete (M15 / 1:2:4 with 40% plums)';

  const ew = assessment.earthworks_quantification || {};
  document.getElementById('pwd-inp-exc-vol').value = ew.excavation_volume_m3 || 320;

  const safety = assessment.safety_and_immediate_actions || {};
  document.getElementById('pwd-inp-traffic').value = safety.traffic_restoration || 'Restore single-lane traffic within 12-24 hours';
  document.getElementById('pwd-inp-machinery').value = safety.machinery_deployment || '1 No. Heavy Excavator with Rock Breaker & 2 Nos. Tippers';

  document.getElementById('pwd-inp-remarks').value = assessment.field_observations_and_remarks || '';
}

window.submitAndOpenOfficialSheet = function() {
  if (!currentAssessmentData) {
    currentAssessmentData = {};
  }

  // Update assessment data with form inputs
  if (!currentAssessmentData.road_metadata) currentAssessmentData.road_metadata = {};
  currentAssessmentData.road_metadata.road_name = document.getElementById('pwd-inp-road-name').value;
  currentAssessmentData.road_metadata.chainage = document.getElementById('pwd-inp-chainage').value;
  currentAssessmentData.road_metadata.road_type = document.getElementById('pwd-inp-road-type').value;
  currentAssessmentData.road_metadata.inspection_date = document.getElementById('pwd-inp-date').value;

  if (!currentAssessmentData.structural_specifications) currentAssessmentData.structural_specifications = {};
  if (!currentAssessmentData.structural_specifications.breast_wall) currentAssessmentData.structural_specifications.breast_wall = {};
  currentAssessmentData.structural_specifications.breast_wall.height_m = parseFloat(document.getElementById('pwd-inp-wall-h').value) || 3.5;
  currentAssessmentData.structural_specifications.breast_wall.length_m = parseFloat(document.getElementById('pwd-inp-wall-l').value) || 18.0;
  currentAssessmentData.structural_specifications.breast_wall.base_width_m = parseFloat(document.getElementById('pwd-inp-wall-base').value) || 1.75;
  currentAssessmentData.structural_specifications.breast_wall.material = document.getElementById('pwd-inp-wall-mat').value;

  if (!currentAssessmentData.earthworks_quantification) currentAssessmentData.earthworks_quantification = {};
  currentAssessmentData.earthworks_quantification.excavation_volume_m3 = parseFloat(document.getElementById('pwd-inp-exc-vol').value) || 320;

  if (!currentAssessmentData.safety_and_immediate_actions) currentAssessmentData.safety_and_immediate_actions = {};
  currentAssessmentData.safety_and_immediate_actions.traffic_restoration = document.getElementById('pwd-inp-traffic').value;
  currentAssessmentData.safety_and_immediate_actions.machinery_deployment = document.getElementById('pwd-inp-machinery').value;

  currentAssessmentData.field_observations_and_remarks = document.getElementById('pwd-inp-remarks').value;

  // Save to sessionStorage for hydration on the sheet page
  const storageKey = 'himalens_pwd_assessment_' + activeReportId;
  sessionStorage.setItem(storageKey, JSON.stringify(currentAssessmentData));

  // Open the printable sheet in a new tab
  window.open(`/report/pwd-sheet/${encodeURIComponent(activeReportId)}`, '_blank');
  closePwdAssessmentModal();
};

window.openDirectSheet = function(reportId) {
  window.open(`/report/pwd-sheet/${encodeURIComponent(reportId)}`, '_blank');
  closePwdAssessmentModal();
};
