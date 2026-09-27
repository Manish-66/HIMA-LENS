/**
 * HIMA-LENS: Technical Assessment & AI Field Dossier Modal Controller
 * Strictly grounded visual analysis using Google Gemini Vision.
 * 100% compliant with HIMA-LENS design tokens and SVG iconography.
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
            <div class="pwd-brand-logo-badge">HL</div>
            <div>
              <h3 class="pwd-modal-title">
                HIMA&middot;LENS Assessment
                <span class="pwd-modal-badge">AI Reviewed</span>
              </h3>
              <div class="pwd-modal-subtitle" id="pwd-modal-sub">REF: --</div>
            </div>
          </div>
          <button type="button" class="pwd-close-btn" onclick="closePwdAssessmentModal()" aria-label="Close dialog">&times;</button>
        </div>

        <div class="pwd-modal-body">
          <!-- Loading State -->
          <div id="pwd-loader" class="pwd-loading-state">
            <div class="pwd-scanner-orb">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="2" y1="12" x2="22" y2="12"></line>
                <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
              </svg>
            </div>
            <div class="pwd-loading-title">Analyzing Photographic Evidence</div>
            <p class="pwd-loading-desc">
              Examining visible slope detachment scarps, unconsolidated colluvium, carriageway encroachment, 
              and synthesizing grounded geotechnical observations...
            </p>
          </div>

          <!-- Assessment Form (Hidden while loading) -->
          <div id="pwd-form" style="display: none;">
            
            <!-- Section 1: Incident Telemetry -->
            <div class="pwd-form-section">
              <div class="pwd-section-head">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
                1. Incident Telemetry &amp; Location
              </div>
              <div class="pwd-grid-2">
                <div class="pwd-field">
                  <label>District Region</label>
                  <input type="text" id="pwd-inp-district">
                </div>
                <div class="pwd-field">
                  <label>Observed Failure Type</label>
                  <input type="text" id="pwd-inp-movement">
                </div>
                <div class="pwd-field">
                  <label>Field Contributor</label>
                  <input type="text" id="pwd-inp-reporter">
                </div>
                <div class="pwd-field">
                  <label>Observer Field Notes</label>
                  <input type="text" id="pwd-inp-notes">
                </div>
              </div>
            </div>

            <!-- Section 2: Visual Evidence Analysis -->
            <div class="pwd-form-section">
              <div class="pwd-section-head">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                2. Visual Photographic Evidence
              </div>
              <div class="pwd-field">
                <label>Visible Material Composition</label>
                <input type="text" id="pwd-inp-mat">
              </div>
              <div class="pwd-grid-2" style="margin-top: 10px;">
                <div class="pwd-field">
                  <label>Slope Condition &amp; Scarp</label>
                  <input type="text" id="pwd-inp-slope">
                </div>
                <div class="pwd-field">
                  <label>Roadway Disruption Status</label>
                  <input type="text" id="pwd-inp-infra">
                </div>
              </div>
              <div class="pwd-field" style="margin-top: 10px;">
                <label>Moisture, Drainage &amp; Secondary Risks</label>
                <input type="text" id="pwd-inp-drain">
              </div>
            </div>

            <!-- Section 3: Plain-Language Incident Explanation (Citizen & Field Summary) -->
            <div class="pwd-form-section">
              <div class="pwd-section-head">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                3. Plain-Language Explanation (Non-Technical Public &amp; Field Guide)
              </div>
              <div class="pwd-field">
                <label>Briefing Title</label>
                <input type="text" id="pwd-inp-plain-title">
              </div>
              <div class="pwd-field" style="margin-top: 10px;">
                <label>What Happened (Simple Terms)</label>
                <textarea rows="2" id="pwd-inp-plain-what"></textarea>
              </div>
              <div class="pwd-grid-2" style="margin-top: 10px;">
                <div class="pwd-field">
                  <label>Why It Happened</label>
                  <input type="text" id="pwd-inp-plain-why">
                </div>
                <div class="pwd-field">
                  <label>Roadway Blockage &amp; Impact</label>
                  <input type="text" id="pwd-inp-plain-road">
                </div>
              </div>
              <div class="pwd-field" style="margin-top: 10px;">
                <label>What Needs To Be Done (Remedy)</label>
                <input type="text" id="pwd-inp-plain-remedy">
              </div>
            </div>

            <!-- Section 4: Technical Synthesis Remarks -->
            <div class="pwd-form-section">
              <div class="pwd-section-head">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>
                4. Technical Synthesis Remarks
              </div>
              <div class="pwd-field">
                <textarea rows="3" id="pwd-inp-synthesis"></textarea>
              </div>
            </div>

          </div>
        </div>

        <div class="pwd-modal-footer">
          <button type="button" class="pwd-btn pwd-btn-secondary" onclick="closePwdAssessmentModal()">Close</button>
          <div class="pwd-modal-actions">
            <button type="button" class="pwd-btn pwd-btn-primary" id="btn-print-official" onclick="submitAndOpenOfficialSheet()">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 6 2 18 2 18 9"></polyline><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path><rect x="6" y="14" width="12" height="8"></rect></svg>
              <span>View &amp; Print Report</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  `;

  document.body.insertAdjacentHTML('beforeend', modalHtml);

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

  subtitle.innerText = `REF: ${reportId}`;
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
      <div style="color: #bd5151; font-weight: 700; font-size: 14px; margin-bottom: 6px;">Telemetry Processing Notice</div>
      <p style="color: #50605a; font-size: 12.5px;">${err.message || 'Could not reach assessment service. You can still inspect the baseline report.'}</p>
      <button type="button" class="pwd-btn pwd-btn-primary" style="margin-top: 14px;" onclick="openDirectSheet('${reportId}')">
        Open Baseline Report
      </button>
    `;
  }
};

window.closePwdAssessmentModal = function() {
  const modal = document.getElementById('pwd-assessment-modal');
  if (modal) modal.style.display = 'none';
};

function populatePwdForm(assessment) {
  const tel = assessment.telemetry || {};
  document.getElementById('pwd-inp-district').value = tel.district || '';
  document.getElementById('pwd-inp-movement').value = tel.reported_movement || '';
  document.getElementById('pwd-inp-reporter').value = tel.reporter_name || '';
  document.getElementById('pwd-inp-notes').value = tel.user_notes || '';

  const vis = assessment.visual_analysis || {};
  document.getElementById('pwd-inp-mat').value = vis.material_composition || '';
  document.getElementById('pwd-inp-slope').value = vis.slope_condition || '';
  document.getElementById('pwd-inp-infra').value = vis.infrastructure_impact || '';
  document.getElementById('pwd-inp-drain').value = vis.drainage_and_seepage || '';

  const ple = assessment.plain_language_explanation || {};
  if (document.getElementById('pwd-inp-plain-title')) document.getElementById('pwd-inp-plain-title').value = ple.summary_title || '';
  if (document.getElementById('pwd-inp-plain-what')) document.getElementById('pwd-inp-plain-what').value = ple.what_happened || '';
  if (document.getElementById('pwd-inp-plain-why')) document.getElementById('pwd-inp-plain-why').value = ple.why_it_happened || '';
  if (document.getElementById('pwd-inp-plain-road')) document.getElementById('pwd-inp-plain-road').value = ple.road_and_travel_impact || '';
  if (document.getElementById('pwd-inp-plain-remedy')) document.getElementById('pwd-inp-plain-remedy').value = ple.what_needs_to_be_done || '';

  document.getElementById('pwd-inp-synthesis').value = assessment.synthesis_remarks || '';
}

window.submitAndOpenOfficialSheet = function() {
  if (!currentAssessmentData) {
    currentAssessmentData = {};
  }

  if (!currentAssessmentData.telemetry) currentAssessmentData.telemetry = {};
  currentAssessmentData.telemetry.district = document.getElementById('pwd-inp-district').value;
  currentAssessmentData.telemetry.reported_movement = document.getElementById('pwd-inp-movement').value;
  currentAssessmentData.telemetry.reporter_name = document.getElementById('pwd-inp-reporter').value;
  currentAssessmentData.telemetry.user_notes = document.getElementById('pwd-inp-notes').value;

  if (!currentAssessmentData.visual_analysis) currentAssessmentData.visual_analysis = {};
  currentAssessmentData.visual_analysis.material_composition = document.getElementById('pwd-inp-mat').value;
  currentAssessmentData.visual_analysis.slope_condition = document.getElementById('pwd-inp-slope').value;
  currentAssessmentData.visual_analysis.infrastructure_impact = document.getElementById('pwd-inp-infra').value;
  currentAssessmentData.visual_analysis.drainage_and_seepage = document.getElementById('pwd-inp-drain').value;

  if (!currentAssessmentData.plain_language_explanation) currentAssessmentData.plain_language_explanation = {};
  if (document.getElementById('pwd-inp-plain-title')) currentAssessmentData.plain_language_explanation.summary_title = document.getElementById('pwd-inp-plain-title').value;
  if (document.getElementById('pwd-inp-plain-what')) currentAssessmentData.plain_language_explanation.what_happened = document.getElementById('pwd-inp-plain-what').value;
  if (document.getElementById('pwd-inp-plain-why')) currentAssessmentData.plain_language_explanation.why_it_happened = document.getElementById('pwd-inp-plain-why').value;
  if (document.getElementById('pwd-inp-plain-road')) currentAssessmentData.plain_language_explanation.road_and_travel_impact = document.getElementById('pwd-inp-plain-road').value;
  if (document.getElementById('pwd-inp-plain-remedy')) currentAssessmentData.plain_language_explanation.what_needs_to_be_done = document.getElementById('pwd-inp-plain-remedy').value;

  currentAssessmentData.synthesis_remarks = document.getElementById('pwd-inp-synthesis').value;

  const storageKey = 'himalens_assessment_' + activeReportId;
  sessionStorage.setItem(storageKey, JSON.stringify(currentAssessmentData));

  window.open(`/report/pwd-sheet/${encodeURIComponent(activeReportId)}`, '_blank');
  closePwdAssessmentModal();
};

window.openDirectSheet = function(reportId) {
  window.open(`/report/pwd-sheet/${encodeURIComponent(reportId)}`, '_blank');
  closePwdAssessmentModal();
};
