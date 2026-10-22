# Graph Report - MTP-main - Copy  (2026-10-22)

## Corpus Check
- 104 files · ~535,931 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 29 file(s) not represented in the graph (top: .lpkx 6, .geojson 6, .toml 4)

## Summary
- 1774 nodes · 3876 edges · 100 communities (92 shown, 8 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 85 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `956b5c11`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- initGlobalBar
- modern-screenshot.umd.js
- explore.js
- mountSvelteComponentVariant
- districts.py
- app.py
- initPageChat
- el
- initGlobalBar
- documentRefForElement
- cap_engine.py
- renderDesignVisual
- supabase_db.py
- ai_assessment.py
- ai_assessment.py
- json
- new-work.md
- Responsive Design
- createLiveBrowserDomHelpers
- HIMA-LENS: Himachal Landslide Inventory & Spatial Intelligence System
- onboard.md
- clarify.md
- Rules
- During the session
- Capabilities
- The Toolkit
- connectSSE
- onAnnotDown
- createLiveBrowserSessionState
- resolveLiveInjectionAnchor
- process_arcgis_layers.py
- post
- HimalayanTerrainShowcase
- animate.md
- live.md
- Handle `generate`
- New visual work
- HimalayanTerrainShowcase
- Generate Report
- impeccable/SKILL.md
- optimize.md
- Impeccable Asset Producer
- Scan mode (approach C: auto-extract, then confirm descriptive language)
- $impeccable hooks
- syncEditBadgeHitProxies
- critique.md
- Simplify the Design
- Hardening Dimensions
- compilerOptions
- scheduleAcceptCleanup
- Nielsen's 10 Heuristics
- Generate Combined Critique Report
- document.md
- polish.md
- quieter.md
- convert_xlsx.py
- Init flow
- report.js
- Common Cognitive Load Violations
- iOS platform
- Operate mode depth (and Read notes)
- Shape
- updateBarContent
- Impeccable Documenter
- Android platform
- colorize.md
- Persona-Based Design Testing
- Extract Flow
- live-browser.js
- doctor.md
- Generate Report
- Cognitive Load Assessment
- Impeccable Finish Reviewer
- Impeccable Manual Edit Applier
- live-browser-ignores.js
- Diagnostic Scan
- handleManualEditActivity
- Visualize: Direction Comps & Asset Production
- captureElementToBlob
- Region map
- MANDATORY PRE-RESPONSE SKILL RESOLUTION PROTOCOL (HARD INVARIANT)
- Ponytail
- Heuristics Scoring Guide
- Operate
- scopeCssBlock
- vercel.json
- show-me/SKILL.md
- resumeSession
- resumeSession
- supabase_setup.sql
- syncPageChatFocus
- adapt.native.md
- 2. Permitted Extraction Patterns
- Geotechnical Physics & Kinematics Validation Guardrails
- Spatial Discipline & Coordinate Integrity Guardrails
- missing_dataset

## God Nodes (most connected - your core abstractions)
1. `connectSSE()` - 34 edges
2. `setLiveState()` - 33 edges
3. `resumeSession()` - 33 edges
4. `showToast()` - 31 edges
5. `initGlobalBar()` - 30 edges
6. `el()` - 29 edges
7. `buildInsertConfigureRow()` - 28 edges
8. `handleKeyDown()` - 27 edges
9. `cleanup()` - 27 edges
10. `injectSvelteComponentsFromManifest()` - 26 edges

## Surprising Connections (you probably didn't know these)
- `Step 1: Run the pass` --references--> `summary()`  [INFERRED]
  .agents/skills/impeccable/reference/doctor.md → app.py
- `Comp-led: the comp is a measured contract` --references--> `text()`  [INFERRED]
  .agents/skills/impeccable/reference/new-work.md → convert_xlsx.py
- `Painted material` --references--> `text()`  [INFERRED]
  .agents/skills/impeccable/reference/region-map.md → convert_xlsx.py
- `$impeccable hooks` --references--> `text()`  [INFERRED]
  .agents/skills/impeccable/reference/hooks.md → convert_xlsx.py
- `teardown()` --indirect_call--> `stopFocusOutIntoChrome()`  [INFERRED]
  .agents/skills/impeccable/scripts/live-browser.js → .agents/skills/impeccable/scripts/live-browser-dom.js

## Import Cycles
- None detected.

## Communities (100 total, 8 thin omitted)

### Community 0 - "initGlobalBar"
Cohesion: 0.14
Nodes (36): beginNewLiveConfiguration(), cancelEditingToPicking(), cancelInsertConfigure(), clearAnnotations(), clearInsertPicking(), closeTunePopover(), enterEditingMode(), exitConfigureToPicking() (+28 more)

### Community 1 - "modern-screenshot.umd.js"
Cohesion: 0.09
Nodes (55): ae(), be(), bt(), Ce(), s(), Ct(), de(), dt() (+47 more)

### Community 2 - "explore.js"
Cohesion: 0.10
Nodes (57): allFeatures, applyFilters(), districtName(), districtStyle(), drawer(), fetchJSON(), filteredFeatures, focusCesiumOnMap() (+49 more)

### Community 3 - "mountSvelteComponentVariant"
Cohesion: 0.14
Nodes (19): applyOriginalAttrsToSvelteAnchor(), commitAcceptedSvelteComponentToDom(), componentModuleCandidates(), describeMountFailure(), detectDevServerBase(), findInsertAnchorInDom(), findLiveElementForSvelteManifest(), importFirstReachable() (+11 more)

### Community 4 - "districts.py"
Cohesion: 0.24
Nodes (11): classify_features(), district_name(), geometry_bounds(), collect(), point_in_geometry(), point_in_polygon(), point_in_prepared_geometry(), point_in_prepared_ring() (+3 more)

### Community 5 - "app.py"
Cohesion: 0.07
Nodes (45): about(), administrative_boundaries(), api_admin_metrics(), api_historical_events(), api_news(), cached_categories_data(), cached_default_summary(), cached_district_polygons() (+37 more)

### Community 6 - "initPageChat"
Cohesion: 0.12
Nodes (38): armPageChatForTyping(), buildSteerProcessingDots(), buildSteerQueueHint(), clearSteerAwaitTimer(), collapsePageChat(), expandPageChat(), finishVoiceSession(), focusPageChatInput() (+30 more)

### Community 7 - "el"
Cohesion: 0.08
Nodes (45): actionLabel(), bindConfigureCountPillTooltip(), bindConfigureInlineControlHover(), bindConfigureModifierPillHover(), buildConfigureActionControl(), buildConfigureCountControl(), buildConfigureRow(), buildConfigureSubmitButton() (+37 more)

### Community 8 - "initGlobalBar"
Cohesion: 0.13
Nodes (22): agentHasWorkInFlight(), agentStatusText(), barPaletteForTheme(), brandMarkSvg(), detectPageTheme(), stopFocusOutIntoChrome(), ensureAgentPollTooltip(), hideAgentPollTooltip() (+14 more)

### Community 9 - "documentRefForElement"
Cohesion: 0.10
Nodes (27): addManualContextText(), canRestoreManualEditElement(), collectManualContextPieces(), walk(), contextElementForManualEdit(), copyEditContainerContext(), copyEditLeafContext(), directMixedTextRestoreNodes() (+19 more)

### Community 10 - "cap_engine.py"
Cohesion: 0.10
Nodes (12): admin_command_console(), get_cap_json(), get_cap_xml_feed(), cancel_active_cap_alert(), dispatch_cap_alert(), generate_cap_xml(), get_active_cap_alert(), get_active_cap_xml() (+4 more)

### Community 11 - "renderDesignVisual"
Cohesion: 0.07
Nodes (43): buildCollapsible(), buildColorModels(), buildDesignHeader(), buildListHtml(), buildRadiiModels(), buildTypographyModels(), copyToClipboard(), cssSafe() (+35 more)

### Community 12 - "supabase_db.py"
Cohesion: 0.09
Nodes (22): allowed_image_file(), get_reports(), load_community_reports(), save_community_reports(), submit_report(), delete_report(), fetch_analytics_summary(), fetch_community_reports() (+14 more)

### Community 13 - "ai_assessment.py"
Cohesion: 0.11
Nodes (17): build_rejected_assessment_dossier(), deep_merge(), fallback_visual_assessment(), _format_coordinates_dms(), generate_ai_assessment(), get_cached_assessment(), _get_http_session(), _get_image_base64_and_mime() (+9 more)

### Community 14 - "ai_assessment.py"
Cohesion: 0.07
Nodes (20): _clean_hazard_prefix(), compute_deterministic_engineering_dossier(), _get_hash_seed(), calculate_comprehensive_cost_and_loss_estimate(), derive_flexible_barrier_specs(), derive_prescribed_soil_nailing(), derive_subsurface_drainage_specs(), evaluate_cedd_consequence() (+12 more)

### Community 15 - "json"
Cohesion: 0.15
Nodes (8): slice_geojson(), validate_geojson(), handle_calculate_fos(), handle_fetch_precipitation(), handle_query_inventory(), handle_validate_coordinates(), main(), process_request()

### Community 16 - "new-work.md"
Cohesion: 0.12
Nodes (15): Recommended Actions, Craft (deprecated alias), Apply, Live-mode signature params, Set the spatial thesis, Two isolated assessments, Verify, Visitor mode (+7 more)

### Community 17 - "Responsive Design"
Cohesion: 0.08
Nodes (25): Assess Adaptation Challenge, Breakpoints: Content-Driven, Content Adaptation, Desktop Adaptation (Mobile → Desktop), Detect Input Method, Not Just Screen Size, Email Adaptation (Web → Email), Implement Adaptations, Layout Adaptation Patterns (+17 more)

### Community 18 - "createLiveBrowserDomHelpers"
Cohesion: 0.11
Nodes (23): collectEditableTextRows(), visit(), createLiveBrowserDomHelpers(), activeElementDeep(), cloneWithoutChrome(), copyTextViaSelection(), cssId(), liveUiRoot() (+15 more)

### Community 19 - "HIMA-LENS: Himachal Landslide Inventory & Spatial Intelligence System"
Cohesion: 0.08
Nodes (23): 1. Clone the Repository, 1. Dual-Engine 2D/3D Web-GIS Observatory (`/explore`), 2. Create and Activate a Virtual Environment, 2. Live Himachal Landslide & Hazard News Wire (`/feed?tab=news`, `/news`), 3. Geotechnical AI Rapid Assessment Engine (`/report`, `ai_assessment.py`), 3. Install Dependencies, 4. Configure Environment Variables, 4. Crowd-Sourced Citizen & Field Reporting (`/report`, `supabase_db.py`) (+15 more)

### Community 20 - "onboard.md"
Cohesion: 0.09
Nodes (22): Assess Onboarding Needs, Context Over Ceremony, Contextual Help, Design Onboarding Experiences, Documentation & Help, Empty State Design, Feature Discovery & Adoption, Guided Tours & Walkthroughs (+14 more)

### Community 21 - "clarify.md"
Cohesion: 0.18
Nodes (10): Actions and navigation, Audit the language, Errors and permissions, Forms, Help and instructional text, Loading, empty, and success states, Rewrite by function, Set the message hierarchy (+2 more)

### Community 22 - "Rules"
Cohesion: 0.09
Nodes (20): caveman, Example output, How to invoke, See also, What it does, 1. Answer first, 2. Kill ceremony, 3. Short word (+12 more)

### Community 23 - "During the session"
Cohesion: 0.09
Nodes (19): ADR Format, Numbering, Optional sections, Template, What qualifies, When to offer an ADR, GLOSSARY.md Format, Rules (+11 more)

### Community 24 - "Capabilities"
Cohesion: 0.09
Nodes (21): Application Security Testing, Behavioral Traits, Capabilities, Cloud Security, Compliance & Governance, DevSecOps & Security Automation, Do not use this skill when, Emerging Security Technologies (+13 more)

### Community 25 - "The Toolkit"
Cohesion: 0.10
Nodes (20): Animate complex properties, Assess What "Extraordinary" Means Here, For data-heavy interfaces, For functional UI, For performance-critical UI, For visual/marketing surfaces, Implement with Discipline, Interact with the device (+12 more)

### Community 26 - "connectSSE"
Cohesion: 0.13
Nodes (34): abandonForeignSession(), abandonSupersededGo(), abortSvelteComponentInjection(), cleanup(), cleanupAcceptedSession(), clearHandled(), clearScrollY(), clearSession() (+26 more)

### Community 27 - "onAnnotDown"
Cohesion: 0.16
Nodes (20): beginEditPin(), buildAnnotationsForCapture(), buildPinElement(), cancelEditingPin(), clampPlaceholderSize(), finalizeEditingPin(), initAnnotOverlay(), localCoords() (+12 more)

### Community 28 - "createLiveBrowserSessionState"
Cohesion: 0.19
Nodes (17): createLiveBrowserSessionState(), clearHandled(), clearScrollY(), clearSession(), isHandled(), loadSession(), markHandled(), nextCheckpointRevision() (+9 more)

### Community 29 - "resolveLiveInjectionAnchor"
Cohesion: 0.16
Nodes (19): buildSvelteExpressionTextMap(), buildSveltePropValuesFromLiveElement(), buildSveltePropValuesV2(), cloneWithoutElements(), collectTextNodes(), collectVisibleTexts(), cssEscapeIdent(), elementMatchesOriginalMarkup() (+11 more)

### Community 30 - "process_arcgis_layers.py"
Cohesion: 0.18
Nodes (4): process_points_dedup(), process_polygons(), process_rasters(), process_roads()

### Community 31 - "post"
Cohesion: 0.10
Nodes (11): admin_cancel_cap(), admin_delete_report(), admin_dismiss_broadcast(), admin_dispatch_cap(), admin_set_broadcast(), admin_trigger_ai(), admin_update_report_status(), inject_global_data() (+3 more)

### Community 33 - "animate.md"
Cohesion: 0.12
Nodes (14): Accessibility and control, Choose material by meaning, Find the job, Implement to the runtime, Set the motion thesis, Timing and easing, Verify, Visitor mode (+6 more)

### Community 34 - "live.md"
Cohesion: 0.07
Nodes (26): Step 1: Parse the request, Step 2: Reuse the page, then start, Step 3: Generate, Step 4: Accept and close, Cleanup, Exit, First-time setup, Handle `accept` (+18 more)

### Community 35 - "Handle `generate`"
Cohesion: 0.12
Nodes (16): 1. Read the screenshot (if present), 2. Wrap the element, 3. Load the action's reference, 4. Plan three variants: identity first, then mode, then axes, 5. Apply the freeform prompt (if present), 6. Deliver variants, 7. Parameters (composition-sized, 0-4 per variant), 8. Signal done (+8 more)

### Community 36 - "New visual work"
Cohesion: 0.14
Nodes (14): 1. Decide what is already true, 2. Ask what will change the work, 3. Choose the right amount of invention, 4. Commit the world, 5. Record the decision, 6. Build with full commitment, 7. Inspect and finish, Both paths (+6 more)

### Community 38 - "Generate Report"
Cohesion: 0.13
Nodes (14): 1. Accessibility (A11y), 2. Performance, 3. Theming, 4. Responsive Design, 5. Implementation Integrity (CRITICAL), Audit Health Score, Detailed Findings by Severity, Diagnostic Scan (+6 more)

### Community 39 - "impeccable/SKILL.md"
Cohesion: 0.10
Nodes (15): Before you finish, Scope is sovereign, The amplification, The skeleton test, Why it reads flat, Craft floor, Refuse, Verify (+7 more)

### Community 40 - "optimize.md"
Cohesion: 0.14
Nodes (13): Animation Performance, Assess Performance Issues, Core Web Vitals Optimization, Cumulative Layout Shift (CLS < 0.1), Interaction to Next Paint (INP < 200ms), Largest Contentful Paint (LCP < 2.5s), Loading Performance, Network Optimization (+5 more)

### Community 41 - "Impeccable Asset Producer"
Cohesion: 0.15
Nodes (11): Act on the receipt, Assemble and review, Plan and asset review, Plan, capture, serve, Core Rule, Decision Comps, Impeccable Asset Producer, Input Contract (+3 more)

### Community 42 - "Scan mode (approach C: auto-extract, then confirm descriptive language)"
Cohesion: 0.15
Nodes (13): Component translation rules, Narrative mapping, Scan mode (approach C: auto-extract, then confirm descriptive language), Schema, Step 1: Find the design assets, Step 2: Auto-extract what can be auto-extracted, Step 2b: Stage the frontmatter, Step 3: Ask the user for qualitative language (+5 more)

### Community 43 - "$impeccable hooks"
Cohesion: 0.33
Nodes (6): Constraints, Failure modes, Flow, $impeccable hooks, Routing, Triage findings

### Community 44 - "syncEditBadgeHitProxies"
Cohesion: 0.31
Nodes (9): bindEditBadgeProxy(), editBadgeProxyTargets(), initEditBadge(), initEditBadgeHitProxies(), proxyMouseEvent(), setImportantStyle(), styleEditBadgeProxy(), syncEditBadgeHitProxies() (+1 more)

### Community 45 - "critique.md"
Cohesion: 0.17
Nodes (11): Action Summary, Ask the User, Assessment A: Design Review, Assessment B: Detector + Browser Evidence, Assessment Orchestration, Deliver the Report, Hard Invariants, Persist the Snapshot (+3 more)

### Community 46 - "Simplify the Design"
Cohesion: 0.17
Nodes (11): Assess Current State, Code Simplification, Content Simplification, Document Removed Complexity, Information Architecture, Interaction Simplification, Layout Simplification, Plan Simplification (+3 more)

### Community 47 - "Hardening Dimensions"
Cohesion: 0.17
Nodes (11): Accessibility Resilience, Assess Hardening Needs, Edge Cases & Boundary Conditions, Error Handling, Hardening Dimensions, Input Validation & Sanitization, Internationalization (i18n), Performance Resilience (+3 more)

### Community 48 - "compilerOptions"
Cohesion: 0.17
Nodes (11): compilerOptions, lib, module, noEmitOnError, outDir, rootDir, skipLibCheck, sourceMap (+3 more)

### Community 49 - "scheduleAcceptCleanup"
Cohesion: 0.31
Nodes (11): acceptedDomAlreadyClean(), clearHandledWrapperReloadStamp(), deferredRecoverySuperseded(), ensureAcceptedDomClean(), findAcceptedRuntimeWrappers(), handledWrapperReloadKey(), reloadAfterMissingAcceptedDom(), restoreAcceptedDomFromSnapshot() (+3 more)

### Community 50 - "Nielsen's 10 Heuristics"
Cohesion: 0.18
Nodes (11): 10. Help and Documentation, 1. Visibility of System Status, 2. Match Between System and Real World, 3. User Control and Freedom, 4. Consistency and Standards, 5. Error Prevention, 6. Recognition Rather Than Recall, 7. Flexibility and Efficiency of Use (+3 more)

### Community 51 - "Generate Combined Critique Report"
Cohesion: 0.18
Nodes (11): Design Health Score, Design Specificity Verdict, Generate Combined Critique Report, Minor Observations, Overall Impression, Persona Red Flags, Priority Issues, Questions to Consider (+3 more)

### Community 52 - "document.md"
Cohesion: 0.18
Nodes (10): Pitfalls, Seed mode, Step 1: Route through new-work's workshop, Step 2: Write seed DESIGN.md, Step 3: Confirm, Style guidelines, The frontmatter: token schema, The markdown body: eight sections (canonical order) (+2 more)

### Community 53 - "polish.md"
Cohesion: 0.18
Nodes (10): 1. Establish the system, 2. Gather the evidence, 3. Triage, 4. Polish the whole path, 5. Verify and finish, Color, imagery, and icons, Content and code, Flow and hierarchy (+2 more)

### Community 54 - "quieter.md"
Cohesion: 0.18
Nodes (10): Assess Current State, Color Refinement, Composition Refinement, Motion Reduction, Plan Refinement, Refine the Design, Simplification, Verify Quality (+2 more)

### Community 55 - "convert_xlsx.py"
Cohesion: 0.42
Nodes (7): legacy_features(), mandi_features(), normalize_activity(), normalize_material(), normalize_movement(), normalize_period(), text()

### Community 56 - "Init flow"
Cohesion: 0.20
Nodes (10): Completion gate, Init flow, Step 1: Load current state, Step 2: Explore the project, Step 3: Interview for product truth, Step 4: Write PRODUCT.md, Step 5: Record workflow defaults, Step 6: Wrap up or resume (+2 more)

### Community 57 - "report.js"
Cohesion: 0.29
Nodes (5): escapeHtml(), initMap(), loadRecentReports(), openReportDetail(), updateCoordinates()

### Community 58 - "Common Cognitive Load Violations"
Cohesion: 0.22
Nodes (9): 1. The Wall of Options, 2. The Memory Bridge, 3. The Hidden Navigation, 4. The Jargon Barrier, 5. The Visual Noise Floor, 6. The Inconsistent Pattern, 7. The Multi-Task Demand, 8. The Context Switch (+1 more)

### Community 59 - "iOS platform"
Cohesion: 0.22
Nodes (9): Color & materials, Components & controls, iOS platform, Layout & structure, Motion, The iOS slop test, Touch targets, Typography (+1 more)

### Community 60 - "Operate mode depth (and Read notes)"
Cohesion: 0.22
Nodes (9): Color, Components, Layout, Motion, Operate mode depth (and Read notes), Product constraints, Product permissions, The product slop test (+1 more)

### Community 61 - "Shape"
Cohesion: 0.22
Nodes (8): Cadence, Confirm and stop, Phase 1: Discovery interview, Phase 2: Resolve the design direction, Phase 3: Write the brief, Round 1: purpose, people, and outcome, Round 2: material, behavior, and boundaries, Shape

### Community 62 - "updateBarContent"
Cohesion: 0.10
Nodes (29): applyConfigureBarChrome(), applyPlaceholderDimensions(), buildCyclingRow(), buildSavingRow(), commitAcceptedVariantToDom(), cycleVariant(), cyclingCounterText(), cyclingShownVariant() (+21 more)

### Community 63 - "Impeccable Documenter"
Cohesion: 0.40
Nodes (4): Impeccable Documenter, Input Contract, Output Contract, Workflow

### Community 64 - "Android platform"
Cohesion: 0.25
Nodes (8): Android platform, Color & theming, Components & motion, Layout & structure, The Android slop test, Touch targets, Typography, Verifying the build

### Community 65 - "colorize.md"
Cohesion: 0.25
Nodes (7): Apply at system scale, Audit before choosing, Choose a strategy, Contrast and perception, Live-mode signature params, Verify, Visitor mode

### Community 66 - "Persona-Based Design Testing"
Cohesion: 0.25
Nodes (8): 1. Impatient Power User: "Alex", 2. Confused First-Timer: "Jordan", 3. Accessibility-Dependent User: "Sam", 4. Deliberate Stress Tester: "Riley", 5. Distracted Mobile User: "Casey", Persona-Based Design Testing, Project-Specific Personas, Selecting Personas

### Community 67 - "Extract Flow"
Cohesion: 0.25
Nodes (7): Extract Flow, Step 1: Discover the Design System, Step 2: Identify Patterns, Step 3: Plan Extraction, Step 4: Extract & Enrich, Step 5: Migrate, Step 6: Document

### Community 68 - "live-browser.js"
Cohesion: 0.05
Nodes (70): applyGlobalBarLabelState(), applyLiveBarPreference(), applyParamDefaults(), applyParamValue(), applyPlaceholderSizingStyles(), buildInsertPlaceholderSnapshotFromDom(), buildLocatorForLeaf(), buildParamsPanel() (+62 more)

### Community 69 - "doctor.md"
Cohesion: 0.25
Nodes (7): Monorepo notes, Opting out of the boot check, Step 1: Run the pass, Step 2: Act by severity, Step 3: Deprecated fields are binding, Step 4: Do not overclaim on truth drift, What this owns, and what it does not

### Community 70 - "Generate Report"
Cohesion: 0.29
Nodes (7): Audit Health Score, Detailed Findings by Severity, Executive Summary, Generate Report, Patterns & Systemic Issues, Platform Conformance Verdict, Positive Findings

### Community 71 - "Cognitive Load Assessment"
Cohesion: 0.29
Nodes (7): Cognitive Load Assessment, Cognitive Load Checklist, Extraneous Load: Bad Design, Germane Load: Learning Effort, Intrinsic Load: The Task Itself, The Working Memory Rule, Three Types of Cognitive Load

### Community 72 - "Impeccable Finish Reviewer"
Cohesion: 0.29
Nodes (6): Checks, in order, Disposition, Impeccable Finish Reviewer, Input Contract, Output Contract, Verdict Pass

### Community 73 - "Impeccable Manual Edit Applier"
Cohesion: 0.29
Nodes (6): Checks, Entry Atomicity, Impeccable Manual Edit Applier, Input Contract, Output Contract, Workflow

### Community 75 - "live-browser-ignores.js"
Cohesion: 0.52
Nodes (6): globToRegex(), matchesScope(), normalizeIgnoreRule(), normalizeIgnoreValue(), pageCandidates(), resolveDetectIgnores()

### Community 76 - "Diagnostic Scan"
Cohesion: 0.33
Nodes (6): 1. Accessibility (VoiceOver / TalkBack), 2. Performance, 3. Appearance & Theming, 4. Platform Conformance (CRITICAL), 5. Adaptivity, Diagnostic Scan

### Community 77 - "handleManualEditActivity"
Cohesion: 0.11
Nodes (42): actOnAgentTarget(), agentTargetBusyReason(), agentTargetOverlayGone(), agentTargetTaken(), claimAgentTarget(), claimAndActOnAgentTarget(), clearStoredManualApplyState(), declineAgentTargetBusy() (+34 more)

### Community 78 - "Visualize: Direction Comps & Asset Production"
Cohesion: 0.33
Nodes (5): After approval: the comp becomes a spec, Generate three compositional options, One approval point, Plates and provenance, Visualize: Direction Comps & Asset Production

### Community 79 - "captureElementToBlob"
Cohesion: 0.11
Nodes (23): averageRgb01(), bufferToBase64(), captureChromeNodes(), captureElementFromRenderedAncestor(), captureElementToBlob(), collectFontCssText(), compileShader(), cssColorToRgb01() (+15 more)

### Community 80 - "Region map"
Cohesion: 0.40
Nodes (4): Containment, Painted material, Region map, What varies independently

### Community 81 - "MANDATORY PRE-RESPONSE SKILL RESOLUTION PROTOCOL (HARD INVARIANT)"
Cohesion: 0.33
Nodes (5): 1. Step 0: Pre-Task Skill Resolution Gate, 2. Skill Trigger & Execution Matrix, 3. Pre-Send Compliance Filter, Absolute Invariant, MANDATORY PRE-RESPONSE SKILL RESOLUTION PROTOCOL (HARD INVARIANT)

### Community 82 - "Ponytail"
Cohesion: 0.40
Nodes (4): Before you write, Levels, Ponytail, The smallest complete change

### Community 83 - "Heuristics Scoring Guide"
Cohesion: 0.50
Nodes (4): Heuristics Scoring Guide, Issue Severity (P0–P3), Reference Material, Score Summary

### Community 84 - "Operate"
Cohesion: 0.14
Nodes (9): Comps, Directions, Operate, Comps, Directions, Persuade and Experience, Comps, Directions (+1 more)

### Community 85 - "scopeCssBlock"
Cohesion: 0.33
Nodes (6): findMatchingCssBrace(), prefixCssSelectors(), scopeCssBlock(), shouldScopeNestedCssAtRule(), splitCssSelectorList(), unwrapSvelteGlobalSelector()

### Community 86 - "vercel.json"
Cohesion: 0.50
Nodes (3): builds, routes, version

### Community 90 - "resumeSession"
Cohesion: 0.15
Nodes (21): applySavedSessionMeta(), clampVariantIndex(), findActiveSessionSummary(), findAdoptableServerSession(), findAnyVariantsWrapper(), injectVariantsFromSource(), isFrameworkComponentPreviewMode(), isJsxSourceFile() (+13 more)

### Community 91 - "resumeSession"
Cohesion: 0.15
Nodes (39): applyEditing(), cancelEditing(), captureAndEmit(), clearMountErrorCard(), completeParameterGenerationIfReady(), completeParameterPublication(), completeSourceInjection(), disableInlineEdit() (+31 more)

### Community 92 - "supabase_setup.sql"
Cohesion: 0.29
Nodes (11): idx_analytics_created, idx_analytics_type_district, idx_community_reports_created_at, idx_community_reports_geom, idx_community_reports_status, idx_rollups_date, public.analytics_daily_rollups, public.analytics_events (+3 more)

### Community 93 - "syncPageChatFocus"
Cohesion: 0.29
Nodes (11): attachSteerFocusDebug(), attachSteerFocusGuard(), clearSteerFocusRecoverTimer(), focusConfigureInput(), notePagePointerDown(), pageHasHostTextSelection(), scheduleSteerFocusRecover(), shouldFocusSteerChat() (+3 more)

### Community 94 - "adapt.native.md"
Cohesion: 0.25
Nodes (7): Adaptation Strategies, Assess Adaptation Challenge, Implement & Verify, Orientation & foldables, Phone → Tablet (iPad / large screens), Platform → platform (iOS ↔ Android), Web → native (porting a website or web app)

### Community 98 - "2. Permitted Extraction Patterns"
Cohesion: 0.25
Nodes (7): 1. Absolute Ingestion Ban, 2. Permitted Extraction Patterns, 3. Safe Verification Reflex, Data Diet & Context Token Protection, Pattern A: Fast CLI Slicer, Pattern B: GeoPandas / Pyogrio Stream, Pattern C: Tailored Filter Queries

### Community 99 - "Geotechnical Physics & Kinematics Validation Guardrails"
Cohesion: 0.29
Nodes (6): 1. Physical Parameter Boundaries, 2. Limit Equilibrium Factor of Safety ($FOS$), 3. Cruden & Varnes (1996) Movement Taxonomy, 4. HPPWD Civil Countermeasures Taxonomy, Geotechnical Physics & Kinematics Validation Guardrails, Sanity Checks:

### Community 100 - "Spatial Discipline & Coordinate Integrity Guardrails"
Cohesion: 0.29
Nodes (6): 1. Absolute Rule: Coordinate Order (RFC 7946 vs Leaflet/MapLibre), 2. Himachal Pradesh Territorial Bounding Box, 3. Coordinate Reference Systems (CRS) & Projections, 4. PostGIS SQL Generation Standards, 5. Automated Validation Helper, Spatial Discipline & Coordinate Integrity Guardrails

## Knowledge Gaps
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Step 1: Run the pass` connect `doctor.md` to `app.py`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `initGlobalBar()` (e.g. with `hideAgentPollTooltip()` and `onDetectMessage()`) actually correct?**
  _`initGlobalBar()` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Should `initGlobalBar` be split into smaller, more focused modules?**
  _Cohesion score 0.13513513513513514 - nodes in this community are weakly interconnected._
- **Why does `summary()` connect `app.py` to `doctor.md`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **Should `modern-screenshot.umd.js` be split into smaller, more focused modules?**
  _Cohesion score 0.08897243107769423 - nodes in this community are weakly interconnected._
- **Why does `text()` connect `convert_xlsx.py` to `Region map`, `$impeccable hooks`, `New visual work`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Should `explore.js` be split into smaller, more focused modules?**
  _Cohesion score 0.09701928696668614 - nodes in this community are weakly interconnected._