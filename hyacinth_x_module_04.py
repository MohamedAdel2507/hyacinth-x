"""
HYACINTH-X | Module 04 — Zero-Waste Manager
Standalone Streamlit module for residue valorization, water recovery, CO₂ management, and circularity indicators.
Daily-flow basis: kg/day (water: kg/day ≈ L/day) or Hourly-flow basis: kg/hour.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

APP_TITLE = "HYACINTH-X | Module 04 — Zero-Waste Manager"


def find_nested_val(data: Any, target_keys: list[str]) -> float | None:
    """Search recursively for target keys in dictionaries, returning the first float-convertible match."""
    if not isinstance(data, dict):
        return None
    for k in target_keys:
        if k in data and data[k] is not None:
            try:
                return float(data[k])
            except (ValueError, TypeError):
                pass
    for v in data.values():
        if isinstance(v, dict):
            found = find_nested_val(v, target_keys)
            if found is not None:
                return found
    return None


def main() -> None:
    try:
        st.set_page_config(page_title="HYACINTH-X | Module 04", page_icon="♻️", layout="wide")
    except Exception:
        pass

    st.title("♻️ HYACINTH-X | Module 04 — Zero-Waste Manager")
    st.caption("Residue valorization • Water recovery • CO₂ management • Circularity indicators")

    st.info(
        "This module is a screening-level mass-flow manager. Inputs may be imported from a Module 02 JSON export "
        "or entered manually. Replace assumptions with measured or literature-supported values before reporting."
    )

    with st.sidebar:
        st.header("Run basis")
        basis = st.selectbox("Time basis", ["Daily (kg/day)", "Hourly (kg/hour)"], index=0, key="m4_time_basis")
        unit = "kg/day" if basis.startswith("Daily") else "kg/hour"
        st.caption("Water flows are expressed as mass; 1 kg water ≈ 1 L at ordinary conditions.")

    st.header("1) Process streams")
    st.write("Enter the mass flow rates of the streams leaving the process. If you have not linked Module 02 yet, use the manual inputs below.")
    uploaded = st.file_uploader("Optional: import a JSON file containing Module 02 outputs", type=["json"], key="m4_uploader")

    # Handle JSON loading with session state synchronization so widget values update immediately
    if uploaded is not None:
        file_sig = f"{uploaded.name}_{uploaded.size}"
        if st.session_state.get("_m4_last_loaded_sig") != file_sig:
            try:
                uploaded.seek(0)
                imported = json.load(uploaded)
                st.session_state["_m4_last_loaded_sig"] = file_sig
                st.session_state["_m4_imported_data"] = imported

                # Stream inputs mapping
                stream_keys = {
                    "m4_lignin": ["lignin_residue", "lignin_rich_residue", "lignin", "Lignin"],
                    "m4_other_residue": ["other_residue", "solid_residue", "unconverted_biomass", "Other / extractives", "other", "Other"],
                    "m4_ash": ["ash_residue", "ash", "Ash", "inorganic_solids"],
                    "m4_wastewater": ["wastewater", "wastewater_flow", "process_wastewater", "water_waste"],
                    "m4_co2": ["co2_generated", "co2", "CO2", "co2_estimate"],
                    "m4_additional_stream": ["other_discard", "other_waste", "discard_streams"],
                }
                for widget_key, target_keys in stream_keys.items():
                    val = find_nested_val(imported, target_keys)
                    if val is not None:
                        st.session_state[widget_key] = float(val)

                # Optional allocation sliders mapping (if importing from Module 04 results)
                alloc_keys = {
                    "m4_l_energy": ["lignin_energy"],
                    "m4_l_material": ["lignin_material"],
                    "m4_l_char": ["lignin_char"],
                    "m4_o_compost": ["other_compost"],
                    "m4_o_energy": ["other_energy"],
                    "m4_o_material": ["other_material"],
                    "m4_a_reuse": ["ash_reuse"],
                    "m4_a_disposal": ["ash_disposal"],
                    "m4_water_recycle": ["water_recycle", "water_recycle_fraction"],
                    "m4_water_treatment": ["water_treatment", "water_treatment_fraction"],
                    "m4_co2_capture": ["co2_capture", "co2_capture_fraction"],
                    "m4_co2_use": ["co2_use", "co2_use_fraction"],
                }
                for widget_key, target_keys in alloc_keys.items():
                    val = find_nested_val(imported, target_keys)
                    if val is not None:
                        st.session_state[widget_key] = int(round(float(val)))

                st.success("JSON loaded. Matching stream keys and parameters have been populated.")
                st.rerun()
            except Exception as e:
                st.error(f"Could not read JSON: {e}")
    else:
        st.session_state["_m4_last_loaded_sig"] = None

    # Ensure default session state values exist
    default_inputs = {
        "m4_lignin": 0.0,
        "m4_other_residue": 0.0,
        "m4_ash": 0.0,
        "m4_wastewater": 0.0,
        "m4_co2": 0.0,
        "m4_additional_stream": 0.0,
        "m4_l_energy": 0,
        "m4_l_material": 0,
        "m4_l_char": 0,
        "m4_o_compost": 0,
        "m4_o_energy": 0,
        "m4_o_material": 0,
        "m4_a_reuse": 0,
        "m4_a_disposal": 0,
        "m4_water_recycle": 0,
        "m4_water_treatment": 100,
        "m4_co2_capture": 0,
        "m4_co2_use": 0,
    }
    for k, v in default_inputs.items():
        if k not in st.session_state:
            st.session_state[k] = v

    with st.expander("Stream inputs", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            lignin = st.number_input(
                f"Lignin-rich residue ({unit})",
                min_value=0.0,
                step=10.0,
                key="m4_lignin",
            )
            other_residue = st.number_input(
                f"Other solid residue / unconverted biomass ({unit})",
                min_value=0.0,
                step=10.0,
                key="m4_other_residue",
            )
        with c2:
            ash = st.number_input(
                f"Ash / inorganic solids ({unit})",
                min_value=0.0,
                step=5.0,
                key="m4_ash",
            )
            wastewater = st.number_input(
                f"Process wastewater available ({unit})",
                min_value=0.0,
                step=10.0,
                key="m4_wastewater",
            )
        with c3:
            co2 = st.number_input(
                f"Estimated CO₂ generated ({unit})",
                min_value=0.0,
                step=10.0,
                key="m4_co2",
            )
            additional_stream = st.number_input(
                f"Other discard streams ({unit})",
                min_value=0.0,
                step=5.0,
                key="m4_additional_stream",
            )

    st.header("2) Residue valorization pathways")
    st.write("Allocate each residue stream across possible routes. The allocation sliders are percentages of that stream, not conversion yields.")
    with st.expander("Lignin-rich residue allocation", expanded=True):
        l_energy = st.slider("Energy recovery / combustion (screening allocation %)", 0, 100, key="m4_l_energy")
        l_material = st.slider("Material products (e.g., binder / adsorbent research route) (%)", 0, 100, key="m4_l_material")
        l_char = st.slider("Biochar / carbonized material research route (%)", 0, 100, key="m4_l_char")
    with st.expander("Other solid residue allocation", expanded=True):
        o_compost = st.slider("Composting / soil amendment (after safety review) (%)", 0, 100, key="m4_o_compost")
        o_energy = st.slider("Energy recovery (%)", 0, 100, key="m4_o_energy")
        o_material = st.slider("Other material recovery (%)", 0, 100, key="m4_o_material")
    with st.expander("Ash allocation", expanded=False):
        a_reuse = st.slider("Potential mineral / soil use after characterization (%)", 0, 100, key="m4_a_reuse")
        a_disposal = st.slider("Managed disposal (%)", 0, 100, key="m4_a_disposal")

    l_alloc = l_energy + l_material + l_char
    o_alloc = o_compost + o_energy + o_material
    a_alloc = a_reuse + a_disposal

    alloc_errors = []
    if l_alloc > 100:
        alloc_errors.append(f"Lignin allocation ({l_alloc}%) exceeds 100%.")
    if o_alloc > 100:
        alloc_errors.append(f"Other-residue allocation ({o_alloc}%) exceeds 100%.")
    if a_alloc > 100:
        alloc_errors.append(f"Ash allocation ({a_alloc}%) exceeds 100%.")
    for e in alloc_errors:
        st.error(e)

    if l_alloc < 100:
        st.warning(f"Lignin allocation leaves {100 - l_alloc}% unassigned.")
    if o_alloc < 100:
        st.warning(f"Other-residue allocation leaves {100 - o_alloc}% unassigned.")
    if a_alloc < 100:
        st.warning(f"Ash allocation leaves {100 - a_alloc}% unassigned.")

    l_recovered = lignin * l_alloc / 100.0
    o_recovered = other_residue * o_alloc / 100.0
    a_recovered = ash * a_reuse / 100.0
    solids_recovered = l_recovered + o_recovered + a_recovered
    solids_total = lignin + other_residue + ash
    solids_unassigned = max(0.0, solids_total - solids_recovered)

    st.header("3) Water management")
    wc1, wc2 = st.columns(2)
    with wc1:
        water_recycle = st.slider("Water recycle fraction of wastewater (%)", 0, 100, key="m4_water_recycle")
    with wc2:
        water_treatment = st.slider("Fraction treated before discharge (%)", 0, 100, key="m4_water_treatment")
    water_recycled = wastewater * water_recycle / 100.0
    water_treated = max(0.0, wastewater - water_recycled) * water_treatment / 100.0
    water_discharge = max(0.0, wastewater - water_recycled - water_treated)
    st.caption("Treatment is represented as a flow fraction only. This module does not predict water quality, COD/BOD, toxicity, or compliance.")

    st.header("4) CO₂ management")
    cc1, cc2 = st.columns(2)
    with cc1:
        co2_capture = st.slider("CO₂ capture fraction (%)", 0, 100, key="m4_co2_capture")
    with cc2:
        co2_use = st.slider("Captured CO₂ utilized / stored fraction (%)", 0, 100, key="m4_co2_use")
    co2_captured = co2 * co2_capture / 100.0
    co2_utilized = co2_captured * co2_use / 100.0
    co2_released = max(0.0, co2 - co2_utilized)
    st.caption("CO₂ use/storage is an accounting pathway, not proof of permanence or net climate benefit. CO₂ generation is an estimate supplied by the upstream model or user.")

    st.header("5) Results")
    solid_recovery_pct = 100.0 * solids_recovered / solids_total if solids_total > 0 else 0.0
    water_recycle_pct = 100.0 * water_recycled / wastewater if wastewater > 0 else 0.0
    co2_util_pct = 100.0 * co2_utilized / co2 if co2 > 0 else 0.0

    # Avoid claiming a complete plant mass balance: this indicator covers only streams entered here.
    entered_streams = solids_total + wastewater + co2 + additional_stream
    tracked_recovery = solids_recovered + water_recycled + co2_utilized

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Solid recovery allocation", f"{solid_recovery_pct:.1f}%")
    c2.metric("Water recycled", f"{water_recycled:,.2f} {unit}")
    c3.metric("CO₂ utilized / stored", f"{co2_utilized:,.2f} {unit}")
    c4.metric("Unassigned solids", f"{solids_unassigned:,.2f} {unit}")

    summary = pd.DataFrame([
        ["Lignin-rich residue", lignin, l_recovered, max(0.0, lignin - l_recovered)],
        ["Other solid residue", other_residue, o_recovered, max(0.0, other_residue - o_recovered)],
        ["Ash", ash, a_recovered, max(0.0, ash - a_recovered)],
    ], columns=["Stream", f"Input ({unit})", f"Allocated to recovery ({unit})", f"Unassigned / disposal ({unit})"])
    st.subheader("Solid-stream allocation")
    st.dataframe(summary, use_container_width=True, hide_index=True)

    st.subheader("Water balance (entered wastewater stream)")
    water_tbl = pd.DataFrame([
        ["Wastewater input", wastewater],
        ["Water recycled", water_recycled],
        ["Treated after recycle", water_treated],
        ["Untreated / untreated fraction discharged", water_discharge],
    ], columns=["Item", f"Flow ({unit})"])
    st.dataframe(water_tbl, use_container_width=True, hide_index=True)

    st.subheader("CO₂ allocation")
    co2_tbl = pd.DataFrame([
        ["CO₂ generated", co2],
        ["Captured", co2_captured],
        ["Utilized / stored", co2_utilized],
        ["Not utilized (release or other)", co2_released],
    ], columns=["Item", f"Flow ({unit})"])
    st.dataframe(co2_tbl, use_container_width=True, hide_index=True)

    indicator_tbl = pd.DataFrame([
        ["Solid-residue recovery allocation", f"{solid_recovery_pct:.2f}%", "Recovered/allocated solids divided by entered solid residues"],
        ["Water recycle ratio", f"{water_recycle_pct:.2f}%", "Water recycled divided by wastewater input"],
        ["CO₂ utilization ratio", f"{co2_util_pct:.2f}%", "Utilized/stored CO₂ divided by estimated CO₂ generation"],
    ], columns=["Indicator", "Value", "Definition"])
    st.subheader("Circularity indicators")
    st.dataframe(indicator_tbl, use_container_width=True, hide_index=True)

    st.warning("These indicators are stream-specific and do not constitute a complete overall material utilization efficiency or life-cycle assessment. Unassigned streams, route suitability, contaminants, energy requirements, and permanence need further evaluation.")

    st.header("6) Export")
    export_data = {
        "basis": unit,
        "inputs": {
            "lignin_residue": lignin,
            "other_residue": other_residue,
            "ash_residue": ash,
            "wastewater": wastewater,
            "co2_generated": co2,
            "other_discard": additional_stream,
        },
        "allocations_percent": {
            "lignin_energy": l_energy,
            "lignin_material": l_material,
            "lignin_char": l_char,
            "other_compost": o_compost,
            "other_energy": o_energy,
            "other_material": o_material,
            "ash_reuse": a_reuse,
            "ash_disposal": a_disposal,
        },
        "outputs": {
            "solid_recovered": solids_recovered,
            "solid_unassigned": solids_unassigned,
            "water_recycled": water_recycled,
            "water_treated": water_treated,
            "water_discharge": water_discharge,
            "co2_captured": co2_captured,
            "co2_utilized": co2_utilized,
            "co2_released_or_not_utilized": co2_released,
        },
        "indicators": {
            "solid_residue_recovery_percent": solid_recovery_pct,
            "water_recycle_percent": water_recycle_pct,
            "co2_utilization_percent": co2_util_pct,
        },
        "limitations": "Screening calculations only; not a full process mass balance, water quality model, LCA, or commercial design.",
    }
    st.download_button(
        "Download Module 04 results (JSON)",
        data=json.dumps(export_data, indent=2),
        file_name="hyacinth_x_module_04_results.json",
        mime="application/json",
    )
    st.download_button(
        "Download solid-stream table (CSV)",
        data=summary.to_csv(index=False).encode("utf-8-sig"),
        file_name="hyacinth_x_module_04_solids.csv",
        mime="text/csv",
    )

    # Comprehensive CSV of all balances
    all_streams_df = pd.concat([
        summary.assign(Category="Solids").rename(columns={f"Input ({unit})": "Input", f"Allocated to recovery ({unit})": "Recovered/Utilized", f"Unassigned / disposal ({unit})": "Unassigned/Discharge"}),
        water_tbl.assign(Category="Water").rename(columns={f"Flow ({unit})": "Flow"}),
        co2_tbl.assign(Category="CO2").rename(columns={f"Flow ({unit})": "Flow"}),
    ], ignore_index=True, sort=False)
    st.download_button(
        "Download complete streams & indicators (CSV)",
        data=all_streams_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="hyacinth_x_module_04_all_streams.csv",
        mime="text/csv",
    )

    st.success("Module 04 calculations complete for the entered assumptions.")


if __name__ == "__main__":
    main()
