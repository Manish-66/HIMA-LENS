import sys
from pathlib import Path

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import geotech_engine

def verify_phase2():
    print("=" * 80)
    print("  PHASE 2 VERIFICATION: DYNAMIC GEOTECHNICAL ARCHETYPES IN GEOTECH_ENGINE.PY")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # 1. BENCHMARK: Uphill Cut-Slope Colluvial Slide (IITM-CR-6A9B327E)
    # -------------------------------------------------------------------------
    print("\n[ARCHETYPE 1: BENCHMARK UPHILL CUT SLOPE (IITM-CR-6A9B327E)]")
    r_bench = {"id": "IITM-CR-6A9B327E", "district": "Mandi", "latitude": 31.708, "longitude": 76.932}
    pdm_bench = geotech_engine.build_project_data_model(r_bench)
    
    assert pdm_bench["is_applicable"] is True
    assert pdm_bench["failure_vector"] == "UPHILL_CUT_SLOPE"
    assert len(pdm_bench["boq_items"]) == 18
    assert pdm_bench["financial_summary"]["civil_subtotal_raw"] == 960304.90
    assert pdm_bench["financial_summary"]["total_remediation_raw"] == 1184151.97
    assert pdm_bench["financial_summary"]["direct_asset_loss_raw"] == 302262.50
    assert pdm_bench["financial_summary"]["indirect_economic_loss_raw"] == 125000.00
    assert pdm_bench["financial_summary"]["statutory_sanction_total_raw"] == 1486414.47
    print(f"  Status:             {pdm_bench['status']}")
    print(f"  Failure Vector:     {pdm_bench['failure_vector']}")
    print(f"  Wall Structure:     Plum Concrete Breast Wall M15 (Vol: {pdm_bench['unified_geometry']['breast_wall']['total_concrete_vol_m3']} m³)")
    print(f"  Soil Nails:         {pdm_bench['unified_geometry']['upper_slope_and_nails']['total_nails_count']} Nos. (Drilling: {pdm_bench['unified_geometry']['upper_slope_and_nails']['total_drilling_length_m']} m)")
    print(f"  Base Subtotal A:    ₹{pdm_bench['financial_summary']['civil_subtotal_raw']:,.2f}")
    print(f"  Total Remediation:  ₹{pdm_bench['financial_summary']['total_remediation_raw']:,.2f} ({pdm_bench['financial_summary']['total_remediation_badge']})")
    print(f"  Statutory Sanction: ₹{pdm_bench['financial_summary']['statutory_sanction_total_raw']:,.2f}")
    print("  >>> PASS: Benchmark IITM-CR-6A9B327E math is 100% verified.")

    # -------------------------------------------------------------------------
    # 2. VALLEY EMBANKMENT SUBSIDENCE (IITM-CR-A3D9D30A)
    # -------------------------------------------------------------------------
    print("\n[ARCHETYPE 2: VALLEY ROAD EMBANKMENT SUBSIDENCE (IITM-CR-A3D9D30A)]")
    r_sub = {"id": "IITM-CR-A3D9D30A", "movement": "Subsidence", "district": "Shimla", "latitude": 31.10, "longitude": 77.20}
    d_sub = {
        "slope_characteristics": {"presence_above": False, "presence_below": True},
        "observed_features": {
            "optical_geometry": {
                "failure_vector": "VALLEY_EMBANKMENT_SUBSIDENCE",
                "scarp_height_m": 7.50,
                "affected_length_m": 22.00,
                "carriageway_formation_m": 5.50,
                "carriageway_open_m": 2.10,
            }
        }
    }
    pdm_sub = geotech_engine.build_project_data_model(dossier=d_sub, report=r_sub)
    assert pdm_sub["is_applicable"] is True
    assert pdm_sub["failure_vector"] == "VALLEY_EMBANKMENT_SUBSIDENCE"
    assert len(pdm_sub["boq_items"]) == 12
    # Verify gabion + micropile + crash barrier items exist
    item_codes = [it["item_code"] for it in pdm_sub["boq_items"]]
    assert any("2504" in c or "Gabion" in it["description"] for it, c in zip(pdm_sub["boq_items"], item_codes))
    assert any("1200" in c for c in item_codes)
    assert any("811" in c for c in item_codes)
    print(f"  Status:             {pdm_sub['status']}")
    print(f"  Failure Vector:     {pdm_sub['failure_vector']}")
    print(f"  Retention System:   Stepped Gabion Wall (Vol: {pdm_sub['unified_geometry']['breast_wall']['total_concrete_vol_m3']} m³) + Micropiles")
    print(f"  BOQ Items:          {len(pdm_sub['boq_items'])} items (MoRTH 2504, 1200, 811, 3100)")
    print(f"  Base Subtotal A:    ₹{pdm_sub['financial_summary']['civil_subtotal_raw']:,.2f}")
    print(f"  Total Remediation:  ₹{pdm_sub['financial_summary']['total_remediation_raw']:,.2f} ({pdm_sub['financial_summary']['total_remediation_badge']})")
    print(f"  Statutory Sanction: ₹{pdm_sub['financial_summary']['statutory_sanction_total_raw']:,.2f}")
    print("  >>> PASS: Valley subsidence design & BOQ verified.")

    # -------------------------------------------------------------------------
    # 3. CLIFF ROCKFALL & BLOCK TOPPLE (IITM-CR-37541B33)
    # -------------------------------------------------------------------------
    print("\n[ARCHETYPE 3: CLIFF ROCKFALL & TOPPLE (IITM-CR-37541B33)]")
    r_rock = {"id": "IITM-CR-37541B33", "movement": "Fall", "district": "Kinnaur", "latitude": 31.60, "longitude": 78.30}
    d_rock = {
        "observed_features": {
            "optical_geometry": {
                "failure_vector": "CLIFF_ROCKFALL_TOPPLE",
                "scarp_height_m": 16.00,
                "affected_length_m": 24.00,
                "cut_slope_angle_deg": 78.0,
                "boulder_max_dia_m": 1.60,
            }
        }
    }
    pdm_rock = geotech_engine.build_project_data_model(dossier=d_rock, report=r_rock)
    assert pdm_rock["is_applicable"] is True
    assert pdm_rock["failure_vector"] == "CLIFF_ROCKFALL_TOPPLE"
    assert len(pdm_rock["boq_items"]) == 11
    # Check NO coir bio-turfing on rock cliff
    assert not any("coir" in it["description"].lower() for it in pdm_rock["boq_items"])
    # Check Rock bolts and Flexible catch barrier exist
    assert any("Rock Bolt" in it["work_package"] or "14448" in it["item_code"] for it in pdm_rock["boq_items"])
    assert any("GEO 138" in it["item_code"] for it in pdm_rock["boq_items"])
    print(f"  Status:             {pdm_rock['status']}")
    print(f"  Failure Vector:     {pdm_rock['failure_vector']}")
    print(f"  Stabilization:      Rope-Access Scaling + Tensioned Rock Bolts + Wire-Rope Drape + Catch Barrier")
    print(f"  BOQ Items:          {len(pdm_rock['boq_items'])} items (IS:13365, MoRTH 3100, CEDD GEO 138)")
    print(f"  Base Subtotal A:    ₹{pdm_rock['financial_summary']['civil_subtotal_raw']:,.2f}")
    print(f"  Total Remediation:  ₹{pdm_rock['financial_summary']['total_remediation_raw']:,.2f} ({pdm_rock['financial_summary']['total_remediation_badge']})")
    print(f"  Statutory Sanction: ₹{pdm_rock['financial_summary']['statutory_sanction_total_raw']:,.2f}")
    print("  >>> PASS: Cliff rockfall solution verified (zero plum wall, zero grass).")

    # -------------------------------------------------------------------------
    # 4. HABITATION TERRACE MUDSLUMP (IITM-CR-D0A16F63)
    # -------------------------------------------------------------------------
    print("\n[ARCHETYPE 4: HABITATION RESIDENTIAL TERRACE SLUMP (IITM-CR-D0A16F63)]")
    r_hab = {"id": "IITM-CR-D0A16F63", "environment_type": "Residential Dwelling / Settlement", "district": "Kangra", "latitude": 32.20, "longitude": 76.30}
    d_hab = {
        "environment_type": "Residential Dwelling / Settlement",
        "observed_features": {
            "optical_geometry": {
                "failure_vector": "HABITATION_TERRACE_SLUMP",
                "scarp_height_m": 5.00,
                "affected_length_m": 15.00,
            }
        }
    }
    pdm_hab = geotech_engine.build_project_data_model(dossier=d_hab, report=r_hab)
    assert pdm_hab["is_applicable"] is True
    assert pdm_hab["failure_vector"] == "HABITATION_TERRACE_SLUMP"
    assert len(pdm_hab["boq_items"]) == 13
    assert pdm_hab["financial_summary"]["indirect_economic_loss_raw"] == 0.0, "Residential site must have 0.0 indirect freight detour loss!"
    assert pdm_hab["financial_summary"]["direct_asset_loss_raw"] == 315000.00
    # Verify M25 RC Cantilever wall + soil dowels
    assert any("Cantilever" in it["description"] or "Deflector" in it["description"] for it in pdm_hab["boq_items"])
    assert any("dowel" in it["description"].lower() for it in pdm_hab["boq_items"])
    print(f"  Status:             {pdm_hab['status']}")
    print(f"  Failure Vector:     {pdm_hab['failure_vector']}")
    print(f"  Retention System:   M25 RC Cantilever Debris Deflector Wall + Terrace Grouted Dowels")
    print(f"  Direct Asset Loss:  ₹{pdm_hab['financial_summary']['direct_asset_loss_raw']:,.2f} (SDRF Housing Norms)")
    print(f"  Indirect Detour:    ₹{pdm_hab['financial_summary']['indirect_economic_loss_raw']:,.2f} (Rural Settlement Zero Freight)")
    print(f"  Total Remediation:  ₹{pdm_hab['financial_summary']['total_remediation_raw']:,.2f} ({pdm_hab['financial_summary']['total_remediation_badge']})")
    print(f"  Statutory Sanction: ₹{pdm_hab['financial_summary']['statutory_sanction_total_raw']:,.2f}")
    print("  >>> PASS: Habitation mudslide design & SDRF losses verified.")

    # -------------------------------------------------------------------------
    # 5. MACRO MOUNTAIN CATASTROPHE (IITM-CR-1EE848DD)
    # -------------------------------------------------------------------------
    print("\n[ARCHETYPE 5: MACRO-SCALE MOUNTAIN CATASTROPHE (IITM-CR-1EE848DD)]")
    r_macro = {"id": "IITM-CR-1EE848DD", "district": "Kullu", "latitude": 32.00, "longitude": 77.20}
    d_macro = {
        "observed_features": {
            "optical_geometry": {
                "failure_vector": "MACRO_MOUNTAIN_CATASTROPHE",
                "scarp_height_m": 72.00,
                "affected_length_m": 140.00,
                "debris_volume_m3": 15000.0,
            }
        }
    }
    pdm_macro = geotech_engine.build_project_data_model(dossier=d_macro, report=r_macro)
    assert pdm_macro["is_applicable"] is False
    assert pdm_macro["status"] == "SUSPENDED_MACRO_SCALE_DPR_REQUIRED"
    assert len(pdm_macro["boq_items"]) == 0
    assert pdm_macro["financial_summary"]["civil_subtotal_raw"] == 0.0
    assert pdm_macro["financial_summary"]["total_remediation_raw"] == 0.0
    assert pdm_macro["rejection_notice"] is not None
    assert "MACRO-SCALE CATASTROPHIC" in pdm_macro["rejection_notice"]
    print(f"  Status:             {pdm_macro['status']}")
    print(f"  Applicable:         {pdm_macro['is_applicable']}")
    print(f"  BOQ Items:          {len(pdm_macro['boq_items'])} (Legally Suspended)")
    print(f"  Civil Outlay:       ₹{pdm_macro['financial_summary']['total_remediation_raw']:,.2f}")
    print(f"  Rejection Notice:   {pdm_macro['rejection_notice'][:120]}...")
    print("  >>> PASS: Macro mountain catastrophe cleanly routed to Level-1 DPR mandate.")

    # -------------------------------------------------------------------------
    # 6. DISQUALIFIED NON-TERRAIN / STABLE FALSE ALARM (IITM-CR-FC9B7776)
    # -------------------------------------------------------------------------
    print("\n[ARCHETYPE 6: DISQUALIFIED NON-TERRAIN / FALSE ALARM (IITM-CR-FC9B7776)]")
    r_ood = {"id": "IITM-CR-FC9B7776", "district": "Shimla", "latitude": 31.10, "longitude": 77.10}
    d_ood = {"is_landslide_or_terrain": False, "validation_status": "NON_LANDSLIDE_STABLE_TERRAIN"}
    pdm_ood = geotech_engine.build_project_data_model(dossier=d_ood, report=r_ood)
    assert pdm_ood["is_applicable"] is False
    assert pdm_ood["status"] == "DISQUALIFIED_NON_TERRAIN"
    assert len(pdm_ood["boq_items"]) == 0
    assert pdm_ood["financial_summary"]["civil_subtotal_raw"] == 0.0
    assert pdm_ood["financial_summary"]["total_remediation_raw"] == 0.0
    assert pdm_ood["stability_analysis"]["scenarios"][0]["calculated_fos"] == 0.0
    print(f"  Status:             {pdm_ood['status']}")
    print(f"  Applicable:         {pdm_ood['is_applicable']}")
    print(f"  BOQ Items:          {len(pdm_ood['boq_items'])}")
    print(f"  Civil Outlay:       ₹{pdm_ood['financial_summary']['total_remediation_raw']:,.2f}")
    print(f"  FoS:                {pdm_ood['stability_analysis']['scenarios'][0]['calculated_fos']}")
    print("  >>> PASS: Non-terrain false alarm disqualified cleanly.")

    print("\n" + "=" * 80)
    print("  ALL 6 ARCHETYPES ARE MATHEMATICALLY RECONCILED AND FUNCTIONING FLAWLESSLY!")
    print("=" * 80)

if __name__ == "__main__":
    verify_phase2()
