"""
HYACINTH-X — Module 01: Feedstock Analyzer
A preliminary engineering calculator for water-hyacinth feedstock characterization.

Run:
    pip install streamlit pandas
    streamlit run hyacinth_x_module_01.py

Notes:
- Example composition defaults are illustrative, not validated water-hyacinth data.
- Moisture is entered on a wet basis.
- Component composition is entered on a dry basis.
- Saved profiles are stored locally in feedstock_profiles.json beside this script.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
PROFILE_FILE = APP_DIR / "feedstock_profiles.json"


# -----------------------------
# Persistence helpers
# -----------------------------
def load_profiles() -> dict[str, dict[str, Any]]:
    if not PROFILE_FILE.exists():
        return {}
    try:
        with PROFILE_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def write_profiles(profiles: dict[str, dict[str, Any]]) -> None:
    with PROFILE_FILE.open("w", encoding="utf-8") as f:
        json.dump(profiles, f, ensure_ascii=False, indent=2)


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
        return result if pd.notna(result) else default
    except (TypeError, ValueError):
        return default


def fmt(value: float, decimals: int = 2) -> str:
    return f"{value:,.{decimals}f}"


def main() -> None:
    try:
        st.set_page_config(
            page_title="HYACINTH-X | Feedstock Analyzer",
            page_icon="🌿",
            layout="wide",
        )
    except Exception:
        pass

    # -----------------------------
    # Theme / page header
    # -----------------------------
    st.title("🌿 HYACINTH-X")
    st.subheader("Module 01 — Feedstock Analyzer")
    st.caption(
        "Engineering-based feedstock characterization for second-generation bioethanol. "
        "This module calculates feedstock mass inventories; it is not a full process simulator."
    )

    with st.expander("Scope and basis of calculation", expanded=False):
        st.markdown(
            """
            - **Wet biomass feed rate:** kg/day.
            - **Moisture content:** % on a **wet basis**.
            - **Cellulose, hemicellulose, lignin, ash, and optional other components:** % on a **dry basis**.
            - Calculated outputs include dry biomass, water contained in the incoming feed, and component mass flow rates.
            - The module does **not** calculate pretreatment conversion, sugar yield, ethanol production, or detailed energy demand.
            - Composition values must come from a laboratory analysis or a documented literature source for real engineering conclusions.
            """
        )

    profiles = load_profiles()

    # -----------------------------
    # Sidebar: saved profile workflow
    # -----------------------------
    st.sidebar.header("Feedstock Profiles")
    st.sidebar.caption("Save reusable composition data. Run-specific feed rate and moisture can still change.")

    profile_names = sorted(profiles.keys())
    profile_action = st.sidebar.radio(
        "Profile action",
        ["Use current / enter manually", "Load saved profile", "Create / update profile"],
        index=0,
    )

    loaded_profile = None
    if profile_action == "Load saved profile":
        if profile_names:
            selected_profile = st.sidebar.selectbox("Select profile", profile_names)
            loaded_profile = profiles.get(selected_profile)
            if st.sidebar.button("Load selected profile", use_container_width=True):
                if loaded_profile:
                    st.session_state["profile_name"] = selected_profile
                    for key in ["cellulose", "hemicellulose", "lignin", "ash", "other"]:
                        st.session_state[key] = float(loaded_profile.get(key, 0.0))
                    st.session_state["sample_id"] = loaded_profile.get("sample_id", "")
                    st.session_state["source"] = loaded_profile.get("source", "")
                    st.session_state["basis_note"] = loaded_profile.get("basis_note", "Dry basis")
                    st.session_state["data_type"] = loaded_profile.get("data_type", "Literature-based")
                    st.session_state["profile_loaded_notice"] = selected_profile
                    st.rerun()
        else:
            st.sidebar.info("No saved profiles yet. Create a profile first.")

    if "profile_loaded_notice" in st.session_state:
        st.sidebar.success(f"Loaded: {st.session_state['profile_loaded_notice']}")

    # -----------------------------
    # Input sections
    # -----------------------------
    st.header("1. Feedstock Inputs")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Run-specific inputs")
        wet_feed = st.number_input(
            "Wet biomass feed rate (kg/day)",
            min_value=0.0,
            value=1000.0,
            step=100.0,
            help="Mass flow of freshly collected biomass entering the analysis.",
        )
        moisture = st.number_input(
            "Moisture content (% wet basis)",
            min_value=0.0,
            max_value=99.9,
            value=85.0,
            step=1.0,
            help="For example, 85% wet-basis moisture means 85 kg water per 100 kg wet feed.",
        )

    with col2:
        st.markdown("#### Composition profile")
        st.caption(
            "The initial numbers are illustrative placeholders. Replace them with a documented "
            "analysis or literature values before reporting real results."
        )
        data_type = st.selectbox(
            "Data type",
            ["Illustrative assumption", "Literature-based", "Laboratory measurement"],
            index=["Illustrative assumption", "Literature-based", "Laboratory measurement"].index(
                st.session_state.get("data_type", "Illustrative assumption")
            ) if st.session_state.get("data_type", "Illustrative assumption") in [
                "Illustrative assumption", "Literature-based", "Laboratory measurement"
            ] else 0,
            key="data_type",
        )

        c1, c2 = st.columns(2)
        with c1:
            cellulose = st.number_input(
                "Cellulose (% dry basis)", min_value=0.0, max_value=100.0,
                value=float(st.session_state.get("cellulose", 25.0)), step=1.0, key="cellulose"
            )
            lignin = st.number_input(
                "Lignin (% dry basis)", min_value=0.0, max_value=100.0,
                value=float(st.session_state.get("lignin", 10.0)), step=1.0, key="lignin"
            )
            other = st.number_input(
                "Other characterized components (% dry basis)", min_value=0.0, max_value=100.0,
                value=float(st.session_state.get("other", 30.0)), step=1.0, key="other"
            )
        with c2:
            hemicellulose = st.number_input(
                "Hemicellulose (% dry basis)", min_value=0.0, max_value=100.0,
                value=float(st.session_state.get("hemicellulose", 20.0)), step=1.0, key="hemicellulose"
            )
            ash = st.number_input(
                "Ash (% dry basis)", min_value=0.0, max_value=100.0,
                value=float(st.session_state.get("ash", 15.0)), step=1.0, key="ash"
            )

    with st.expander("Advanced data source and sample tracking", expanded=False):
        meta1, meta2 = st.columns(2)
        with meta1:
            sample_id = st.text_input(
                "Sample ID / collection source",
                value=st.session_state.get("sample_id", ""),
                placeholder="e.g., WH-Sample-01",
                key="sample_id",
            )
            source = st.text_input(
                "Data source / citation",
                value=st.session_state.get("source", ""),
                placeholder="e.g., paper DOI, URL, or lab report ID",
                key="source",
            )
        with meta2:
            basis_note = st.selectbox(
                "Composition basis",
                ["Dry basis"],
                index=0,
                key="basis_note",
                help="This version expects component fractions on a dry basis.",
            )
            st.text_input(
                "Profile name (for saving)",
                value=st.session_state.get("profile_name", "Water Hyacinth — Profile 1"),
                key="profile_name",
            )

    # -----------------------------
    # Validation
    # -----------------------------
    components = {
        "Cellulose": cellulose,
        "Hemicellulose": hemicellulose,
        "Lignin": lignin,
        "Ash": ash,
        "Other characterized components": other,
    }
    composition_total = sum(components.values())
    composition_tolerance = 0.5  # percentage points; intended for rounding tolerance only
    errors: list[str] = []
    warnings: list[str] = []

    if wet_feed <= 0:
        errors.append("Wet biomass feed rate must be greater than zero.")
    if not (0 <= moisture < 100):
        errors.append("Moisture content must be at least 0% and less than 100%.")
    if any(v < 0 or v > 100 for v in components.values()):
        errors.append("Each component percentage must be between 0% and 100%.")
    if composition_total > 100 + composition_tolerance:
        errors.append(
            f"Dry-basis composition totals {composition_total:.2f}%, exceeding 100% "
            f"by more than the {composition_tolerance:.1f}-percentage-point tolerance."
        )
    elif composition_total < 100 - composition_tolerance:
        warnings.append(
            f"Composition totals {composition_total:.2f}%. About "
            f"{100-composition_total:.2f}% of dry matter is not characterized by the listed inputs."
        )
    elif composition_total != 100:
        warnings.append(
            f"Composition totals {composition_total:.2f}%; the small difference from 100% "
            "may be due to rounding or analytical uncertainty."
        )

    if not source.strip():
        warnings.append("No data source/citation is recorded. Mark results as assumptions unless a source is added.")
    if data_type == "Illustrative assumption":
        warnings.append("Composition is marked as illustrative. Do not present these values as experimental data.")
    if not sample_id.strip():
        warnings.append("No sample ID or collection source is recorded.")

    st.header("2. Data Quality Checks")
    if errors:
        for item in errors:
            st.error(item)
    elif warnings:
        st.warning("Review the following notes before using the results:")
        for item in warnings:
            st.write(f"- {item}")
    else:
        st.success("Input checks passed.")

    # -----------------------------
    # Calculations
    # -----------------------------
    results_available = not errors
    if results_available:
        dry_feed = wet_feed * (1.0 - moisture / 100.0)
        water_in_feed = wet_feed * moisture / 100.0
        component_flows = {
            name: dry_feed * pct / 100.0 for name, pct in components.items()
        }
        uncharacterized_pct = max(0.0, 100.0 - composition_total)
        uncharacterized_flow = dry_feed * uncharacterized_pct / 100.0

        # Display only if valid; uncharacterized is separate from "Other characterized components".
        st.header("3. Calculated Results")
        k1, k2, k3 = st.columns(3)
        k1.metric("Dry biomass", f"{fmt(dry_feed)} kg/day")
        k2.metric("Water in incoming feed", f"{fmt(water_in_feed)} kg/day")
        k3.metric("Known composition total", f"{fmt(composition_total)}%")

        result_df = pd.DataFrame(
            [
                {"Output": "Wet biomass feed rate", "Symbol": "ṁ_wet", "Value": wet_feed, "Unit": "kg/day"},
                {"Output": "Dry biomass flow rate", "Symbol": "ṁ_dry", "Value": dry_feed, "Unit": "kg/day"},
                {"Output": "Water in incoming feed", "Symbol": "ṁ_water", "Value": water_in_feed, "Unit": "kg/day"},
                *[
                    {"Output": f"{name} mass flow", "Symbol": "", "Value": flow, "Unit": "kg/day"}
                    for name, flow in component_flows.items()
                ],
                {"Output": "Uncharacterized dry mass flow", "Symbol": "", "Value": uncharacterized_flow, "Unit": "kg/day"},
            ]
        )
        display_df = result_df.copy()
        display_df["Value"] = display_df["Value"].apply(lambda v: fmt(v) if isinstance(v, (int, float)) else str(v))
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # -----------------------------
        # Profile save / update
        # -----------------------------
        st.header("4. Save Profile")
        profile_name = st.session_state.get("profile_name", "Water Hyacinth — Profile 1")
        if st.button("Save current composition to local profile", use_container_width=True):
            profiles[profile_name.strip()] = {
                "cellulose": cellulose,
                "hemicellulose": hemicellulose,
                "lignin": lignin,
                "ash": ash,
                "other": other,
                "sample_id": sample_id,
                "source": source,
                "basis_note": basis_note,
                "data_type": data_type,
                "saved_at": datetime.now().isoformat(timespec="seconds"),
            }
            try:
                write_profiles(profiles)
                st.success(f"Profile '{profile_name.strip()}' saved locally.")
            except OSError as exc:
                st.error(f"Could not save profile: {exc}")

        # -----------------------------
        # Export
        # -----------------------------
        st.header("5. Export Results")
        export_df = result_df.copy()
        metadata = pd.DataFrame([
            {"Output": "Data type", "Symbol": "", "Value": data_type, "Unit": ""},
            {"Output": "Sample ID / source", "Symbol": "", "Value": sample_id, "Unit": ""},
            {"Output": "Data source / citation", "Symbol": "", "Value": source, "Unit": ""},
            {"Output": "Composition basis", "Symbol": "", "Value": basis_note, "Unit": ""},
            {"Output": "Validation", "Symbol": "", "Value": "Passed with warnings" if warnings else "Passed", "Unit": ""},
        ])
        export_df["Value"] = export_df["Value"].astype(str)
        metadata["Value"] = metadata["Value"].astype(str)
        combined = pd.concat([export_df, metadata], ignore_index=True)
        st.download_button(
            "Download results as CSV",
            data=combined.to_csv(index=False).encode("utf-8-sig"),
            file_name="hyacinth_x_feedstock_analysis.csv",
            mime="text/csv",
        )

        with st.expander("Technical notes and limitations"):
            st.markdown(
                """
                - The water value is water contained in the incoming feed, not water necessarily removed by drying.
                - To calculate water removed in a dryer, a target final moisture content is required.
                - The component categories should be mutually exclusive and reported on a consistent dry basis.
                - If literature values are from a different plant part, season, location, or preparation method, the profile may not represent the current batch.
                - Cellulose and hemicellulose inventories are not the same as fermentable sugar production. Conversion calculations belong in the Core Calculation Engine.
                - This module performs feedstock characterization and simple mass accounting only.
                """
            )
    else:
        st.info("Correct the input errors above to calculate and export results.")

    st.divider()
    st.caption("HYACINTH-X | Preliminary engineering tool • Verify reference data before using results in a report.")


if __name__ == "__main__":
    main()
