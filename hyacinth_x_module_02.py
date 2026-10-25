"""
HYACINTH-X | Module 02 — Process Yield Estimator
Standalone Streamlit application for an illustrative water-hyacinth-to-ethanol model.

Install:
    python -m pip install streamlit pandas
Run:
    python -m streamlit run hyacinth_x_module_02.py

Important:
- Educational screening model, not a validated plant design or full mass/energy balance.
- All default efficiencies and retention values are illustrative; replace with experimental data.
"""
from __future__ import annotations

import math
from itertools import product
from typing import Dict, Any, List, Tuple

import pandas as pd
import streamlit as st

APP_TITLE = "HYACINTH-X | Module 02 — Process Yield Estimator"
SUGARS = ("Glucose", "Xylose", "Mannose")
COMPONENTS = ("Cellulose", "Xylan", "Mannan", "Lignin", "Ash", "Other / extractives")
CARBOHYDRATES = ("Cellulose", "Xylan", "Mannan")

# Theoretical sugar / anhydro-polymer mass factors (hydration during hydrolysis).
SUGAR_FACTORS = {"Cellulose": 180.0 / 162.0, "Xylan": 150.0 / 132.0, "Mannan": 180.0 / 162.0}
ETHANOL_YIELD_G_PER_G = {"Glucose": 0.511, "Xylose": 0.511, "Mannose": 0.511}

MICROBES = {
    "Conventional S. cerevisiae (illustrative)": {
        "fermentable": {"Glucose": True, "Xylose": False, "Mannose": True},
        "efficiency": {"Glucose": 0.88, "Xylose": 0.00, "Mannose": 0.80},
        "note": "A conventional profile: glucose and mannose are represented as fermentable; xylose is not assumed fermentable."
    },
    "Generic xylose-fermenting yeast (illustrative)": {
        "fermentable": {"Glucose": True, "Xylose": True, "Mannose": True},
        "efficiency": {"Glucose": 0.85, "Xylose": 0.65, "Mannose": 0.75},
        "note": "A simplified engineered/xylose-fermenting profile. Actual performance depends on strain and operating conditions."
    },
    "Custom profile": {
        "fermentable": {"Glucose": True, "Xylose": True, "Mannose": True},
        "efficiency": {"Glucose": 0.80, "Xylose": 0.50, "Mannose": 0.65},
        "note": "Enter your own assumed fermentability and conversion efficiencies."
    },
}

def clamp(x: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(x)))

def validate_composition(composition: Dict[str, float]) -> Tuple[bool, float]:
    total = sum(float(composition.get(k, 0.0)) for k in COMPONENTS)
    return abs(total - 100.0) <= 0.15, total

def calculate_scenario(params: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate a transparent screening estimate from dry biomass to recovered ethanol."""
    dry_mass = max(0.0, float(params["dry_mass_kg"]))
    moisture = clamp(params["moisture_wet_basis"])
    wet_equivalent = dry_mass / max(1e-9, (1.0 - moisture))

    comp = params["composition"]
    ok, comp_total = validate_composition(comp)
    if not ok:
        raise ValueError(f"Dry-basis composition must sum to 100%; current total = {comp_total:.2f}%.")

    # Dry component masses.
    component_kg = {k: dry_mass * float(comp.get(k, 0.0)) / 100.0 for k in COMPONENTS}

    # Pretreatment: retained solids and dissolved streams are kept separate.
    retention = clamp(params["solid_retention"])
    solubilized = clamp(params["solubilized_fraction"])
    degraded = clamp(params["degraded_fraction"])
    if retention + solubilized + degraded > 1.0001:
        raise ValueError("Pretreatment solid retention + solubilized fraction + degraded fraction cannot exceed 100%.")

    retained = {k: component_kg[k] * retention for k in COMPONENTS}
    dissolved = {k: component_kg[k] * solubilized for k in COMPONENTS}
    degraded_kg = sum(component_kg[k] * degraded for k in COMPONENTS)

    # Hydrolysis of retained structural carbohydrates. Soluble carbohydrate-derived sugars
    # are optionally added as measured values by the user (not inferred from total dissolved mass).
    hydrolysis = {
        "Cellulose": clamp(params["cellulose_hydrolysis"]),
        "Xylan": clamp(params["xylan_hydrolysis"]),
        "Mannan": clamp(params["mannan_hydrolysis"]),
    }
    sugar_mass = {
        "Glucose": retained["Cellulose"] * hydrolysis["Cellulose"] * SUGAR_FACTORS["Cellulose"],
        "Xylose": retained["Xylan"] * hydrolysis["Xylan"] * SUGAR_FACTORS["Xylan"],
        "Mannose": retained["Mannan"] * hydrolysis["Mannan"] * SUGAR_FACTORS["Mannan"],
    }
    measured = params.get("measured_sugars_kg", {})
    for sugar in SUGARS:
        sugar_mass[sugar] += max(0.0, float(measured.get(sugar, 0.0)))

    # Fermentation is pathway-specific and profile-specific.
    fermentable = params["fermentable"]
    efficiency = {s: clamp(params["fermentation_efficiency"][s]) for s in SUGARS}
    fermented_sugar = {}
    theoretical_ethanol = {}
    for sugar in SUGARS:
        fermented_sugar[sugar] = sugar_mass[sugar] * (efficiency[sugar] if fermentable.get(sugar, False) else 0.0)
        theoretical_ethanol[sugar] = fermented_sugar[sugar] * ETHANOL_YIELD_G_PER_G[sugar]

    ethanol_before_recovery = sum(theoretical_ethanol.values())
    recovery = clamp(params["ethanol_recovery"])
    recovered_ethanol = ethanol_before_recovery * recovery

    # Report only meaningful screening quantities; this is not a full stream-by-stream balance.
    total_sugars = sum(sugar_mass.values())
    total_fermented = sum(fermented_sugar.values())
    return {
        "dry_mass_kg": dry_mass,
        "moisture_wet_basis": moisture,
        "wet_equivalent_kg": wet_equivalent,
        "component_kg": component_kg,
        "retained_component_kg": retained,
        "dissolved_component_kg": dissolved,
        "degraded_kg": degraded_kg,
        "sugar_mass_kg": sugar_mass,
        "fermented_sugar_kg": fermented_sugar,
        "theoretical_ethanol_by_sugar_kg": theoretical_ethanol,
        "total_sugars_kg": total_sugars,
        "total_fermented_sugar_kg": total_fermented,
        "ethanol_before_recovery_kg": ethanol_before_recovery,
        "ethanol_recovery": recovery,
        "recovered_ethanol_kg": recovered_ethanol,
        "composition_total_pct": comp_total,
        "warnings": [
            "Default parameters are illustrative and must be validated against laboratory data.",
            "Dissolved pretreatment material is reported separately; it is not automatically counted as fermentable sugar.",
            "The model estimates ethanol mass only; it does not calculate complete wastewater, inhibitor, energy, or equipment balances."
        ]
    }

def default_params() -> Dict[str, Any]:
    microbe = MICROBES["Conventional S. cerevisiae (illustrative)"]
    return {
        "dry_mass_kg": 1000.0,
        "moisture_wet_basis": 0.80,
        "composition": {
            "Cellulose": 35.0, "Xylan": 18.0, "Mannan": 3.0,
            "Lignin": 20.0, "Ash": 12.0, "Other / extractives": 12.0
        },
        "solid_retention": 0.90,
        "solubilized_fraction": 0.07,
        "degraded_fraction": 0.03,
        "cellulose_hydrolysis": 0.75,
        "xylan_hydrolysis": 0.65,
        "mannan_hydrolysis": 0.60,
        "fermentable": dict(microbe["fermentable"]),
        "fermentation_efficiency": dict(microbe["efficiency"]),
        "ethanol_recovery": 0.95,
        "measured_sugars_kg": {"Glucose": 0.0, "Xylose": 0.0, "Mannose": 0.0},
    }

def pct(label: str, value: float, key: str, help_text: str = "") -> float:
    return st.number_input(label, min_value=0.0, max_value=100.0, value=float(value)*100.0,
                           step=1.0, key=key, help=help_text) / 100.0

def show_results(result: Dict[str, Any]) -> None:
    st.subheader("Estimated results")
    a, b, c = st.columns(3)
    a.metric("Recovered ethanol", f"{result['recovered_ethanol_kg']:,.2f} kg")
    b.metric("Ethanol before recovery", f"{result['ethanol_before_recovery_kg']:,.2f} kg")
    c.metric("Total modeled sugars", f"{result['total_sugars_kg']:,.2f} kg")

    summary = pd.DataFrame([
        ("Dry biomass input", f"{result['dry_mass_kg']:,.2f}", "kg"),
        ("Wet-equivalent biomass at stated moisture", f"{result['wet_equivalent_kg']:,.2f}", "kg"),
        ("Sugar mass available to fermentation model", f"{result['total_sugars_kg']:,.2f}", "kg"),
        ("Sugar mass fermented", f"{result['total_fermented_sugar_kg']:,.2f}", "kg"),
        ("Ethanol before recovery", f"{result['ethanol_before_recovery_kg']:,.2f}", "kg"),
        ("Recovered ethanol", f"{result['recovered_ethanol_kg']:,.2f}", "kg"),
    ], columns=["Metric", "Value", "Unit"])
    st.dataframe(summary, use_container_width=True, hide_index=True)

    sugar_df = pd.DataFrame([
        {"Sugar": s,
         "Sugar available (kg)": round(result["sugar_mass_kg"][s], 2),
         "Sugar fermented (kg)": round(result["fermented_sugar_kg"][s], 2),
         "Ethanol before recovery (kg)": round(result["theoretical_ethanol_by_sugar_kg"][s], 2)}
        for s in SUGARS
    ])
    st.markdown("**Sugar-by-sugar pathway results**")
    st.dataframe(sugar_df, use_container_width=True, hide_index=True)

    stream_df = pd.DataFrame([
        {"Component": k,
         "Initial dry mass (kg)": round(result["component_kg"][k], 2),
         "Retained solids (kg)": round(result["retained_component_kg"][k], 2),
         "Dissolved stream (kg)": round(result["dissolved_component_kg"][k], 2)}
        for k in COMPONENTS
    ])
    st.markdown("**Illustrative pretreatment split**")
    st.dataframe(stream_df, use_container_width=True, hide_index=True)
    st.caption(f"Estimated degraded mass across all components: {result['degraded_kg']:,.2f} kg. "
               "This simplified split is not a validated solids/liquids mass balance.")

    csv = pd.concat([
        summary.assign(Table="Summary"),
        sugar_df.rename(columns={"Sugar": "Metric"}).assign(Unit="kg", Table="Sugar pathways"),
        stream_df.rename(columns={"Component": "Metric"}).assign(Unit="kg", Table="Pretreatment split"),
    ], ignore_index=True, sort=False)
    st.download_button("Download summary CSV", csv.to_csv(index=False).encode("utf-8"),
                       file_name="hyacinth_x_module_02_results.csv", mime="text/csv")

def main() -> None:
    try:
        st.set_page_config(page_title=APP_TITLE, page_icon="🌿", layout="wide")
    except Exception:
        pass

    st.title(APP_TITLE)
    st.caption("Pretreatment → Hydrolysis → Fermentation → Ethanol Recovery")
    st.info("Screening model for learning and scenario comparison. Validate all assumptions experimentally before using results for design.")

    with st.sidebar:
        st.header("1. Feedstock")
        dry_mass = st.number_input("Dry biomass mass (kg)", min_value=0.0, value=1000.0, step=100.0)
        moisture = st.slider("Moisture content (wet basis, %)", 0, 95, 80) / 100.0
        st.caption("Wet-equivalent mass = dry mass / (1 − moisture fraction).")
        st.subheader("Dry-basis composition (%)")
        defaults = default_params()["composition"]
        composition = {}
        for component in COMPONENTS:
            composition[component] = st.number_input(
                f"{component} (%)", min_value=0.0, max_value=100.0,
                value=float(defaults[component]), step=1.0, key=f"comp_{component}"
            )
        total = sum(composition.values())
        st.write(f"**Composition total: {total:.2f}%**")
        if abs(total - 100.0) > 0.15:
            st.warning("Adjust composition values until their sum is 100%.")
            if st.button("Normalize to 100%", use_container_width=True, key="btn_normalize_composition"):
                if total > 0:
                    for comp_name in COMPONENTS:
                        st.session_state[f"comp_{comp_name}"] = round((composition[comp_name] / total) * 100.0, 2)
                    st.rerun()

    tab_manual, tab_sweep, tab_model = st.tabs(["Manual scenario", "Automatic scenario sweep", "Model & assumptions"])

    with tab_manual:
        st.header("2. Process assumptions")
        p1, p2 = st.columns(2)
        with p1:
            st.subheader("Pretreatment")
            solid_retention = st.slider("Solid retention (%)", 0, 100, 90) / 100.0
            solubilized = st.slider("Solubilized fraction (%)", 0, 100, 7) / 100.0
            degraded = st.slider("Degraded fraction (%)", 0, 100, 3) / 100.0
            if solid_retention + solubilized + degraded > 1.0001:
                st.error("Solid retention + solubilized + degraded must not exceed 100%.")
        with p2:
            st.subheader("Hydrolysis efficiency")
            cellulose_h = st.slider("Cellulose → glucose (%)", 0, 100, 75) / 100.0
            xylan_h = st.slider("Xylan → xylose (%)", 0, 100, 65) / 100.0
            mannan_h = st.slider("Mannan → mannose (%)", 0, 100, 60) / 100.0

        st.header("3. Fermentation")
        microbe_name = st.selectbox("Microorganism profile", list(MICROBES.keys()), key="microbe_select")
        microbe = MICROBES[microbe_name]
        st.caption(microbe["note"])
        st.write("Set whether each sugar is fermentable and the assumed conversion efficiency.")

        # Synchronize default checkboxes and sliders when a profile is changed
        if st.session_state.get("_active_microbe") != microbe_name:
            st.session_state["_active_microbe"] = microbe_name
            for s in SUGARS:
                st.session_state[f"fermentable_{s}"] = bool(microbe["fermentable"][s])
                st.session_state[f"eff_{s}"] = int(microbe["efficiency"][s] * 100)

        fcols = st.columns(3)
        fermentable, efficiency = {}, {}
        for i, sugar in enumerate(SUGARS):
            with fcols[i]:
                fermentable[sugar] = st.checkbox(
                    f"{sugar} fermentable",
                    value=st.session_state.get(f"fermentable_{sugar}", bool(microbe["fermentable"][sugar])),
                    key=f"fermentable_{sugar}"
                )
                efficiency[sugar] = st.slider(
                    f"{sugar} fermentation efficiency (%)", 0, 100,
                    value=st.session_state.get(f"eff_{sugar}", int(microbe["efficiency"][sugar] * 100)),
                    key=f"eff_{sugar}"
                ) / 100.0
                if not fermentable[sugar]:
                    st.caption("Efficiency is ignored while this pathway is disabled.")

        st.header("4. Ethanol recovery")
        recovery = st.slider("Ethanol recovery (%)", 0, 100, 95) / 100.0
        with st.expander("Optional measured soluble sugars"):
            st.caption("Enter measured monosaccharides in kg if you have lab data. Do not enter total dissolved biomass here.")
            measured = {}
            mcols = st.columns(3)
            for i, sugar in enumerate(SUGARS):
                with mcols[i]:
                    measured[sugar] = st.number_input(f"Measured {sugar} (kg)", min_value=0.0,
                                                      value=0.0, step=1.0, key=f"measured_{sugar}")

        run = st.button("Calculate scenario", type="primary", use_container_width=True)
        if run:
            params = {
                "dry_mass_kg": dry_mass, "moisture_wet_basis": moisture, "composition": composition,
                "solid_retention": solid_retention, "solubilized_fraction": solubilized,
                "degraded_fraction": degraded, "cellulose_hydrolysis": cellulose_h,
                "xylan_hydrolysis": xylan_h, "mannan_hydrolysis": mannan_h,
                "fermentable": fermentable, "fermentation_efficiency": efficiency,
                "ethanol_recovery": recovery, "measured_sugars_kg": measured,
            }
            try:
                result = calculate_scenario(params)
                st.session_state["last_result"] = result
                show_results(result)
            except ValueError as exc:
                st.error(str(exc))
        elif "last_result" in st.session_state:
            st.caption("Showing the last successfully calculated result. Press Calculate scenario to update it.")
            show_results(st.session_state["last_result"])

    with tab_sweep:
        st.header("Automatic scenario sweep")
        st.write("Compare combinations of hydrolysis and fermentation efficiencies while holding other inputs fixed.")
        st.caption("This is a structured grid sweep, not an optimizer and not a probability model.")
        s1, s2, s3 = st.columns(3)
        with s1:
            cell_values = st.multiselect("Cellulose hydrolysis (%)", [40, 50, 60, 70, 80, 90, 100], default=[60, 80, 100])
            xylan_values = st.multiselect("Xylan hydrolysis (%)", [30, 40, 50, 60, 70, 80, 90, 100], default=[50, 70, 90])
        with s2:
            glucose_values = st.multiselect("Glucose fermentation efficiency (%)", [40, 50, 60, 70, 80, 90, 100], default=[70, 90])
            xylose_values = st.multiselect("Xylose fermentation efficiency (%)", [0, 25, 50, 75, 100], default=[0, 50, 75])
        with s3:
            max_scenarios = st.number_input("Maximum scenarios", min_value=1, max_value=500, value=100, step=10)
            objective = st.selectbox("Rank by", ["Recovered ethanol (kg)", "Ethanol before recovery (kg)"])
        sweep_go = st.button("Run scenario sweep", type="primary")
        if sweep_go:
            if not all([cell_values, xylan_values, glucose_values, xylose_values]):
                st.error("Choose at least one value in each sweep parameter.")
            else:
                combos = list(product(cell_values, xylan_values, glucose_values, xylose_values))
                if len(combos) > int(max_scenarios):
                    st.warning(f"{len(combos)} combinations requested; evaluating the first {int(max_scenarios)}.")
                    combos = combos[:int(max_scenarios)]
                base_comp = composition
                base_ok, base_total = validate_composition(base_comp)
                if not base_ok:
                    st.error(f"Composition must sum to 100% before the sweep (currently {base_total:.2f}%).")
                else:
                    rows = []
                    # Sweep uses the same feedstock inputs and fixed, clearly stated process assumptions.
                    base = default_params()
                    base["dry_mass_kg"] = dry_mass
                    base["moisture_wet_basis"] = moisture
                    base["composition"] = composition
                    base["solid_retention"] = 0.90
                    base["solubilized_fraction"] = 0.07
                    base["degraded_fraction"] = 0.03
                    base["mannan_hydrolysis"] = 0.60
                    base["ethanol_recovery"] = 0.95
                    base["fermentable"] = dict(microbe["fermentable"])
                    base["fermentation_efficiency"] = dict(microbe["efficiency"])
                    for ch, xh, ge, xe in combos:
                        p = dict(base)
                        p["cellulose_hydrolysis"] = ch / 100.0
                        p["xylan_hydrolysis"] = xh / 100.0
                        p["fermentable"] = dict(base["fermentable"])
                        p["fermentation_efficiency"] = dict(base["fermentation_efficiency"])
                        p["fermentation_efficiency"]["Glucose"] = ge / 100.0
                        p["fermentation_efficiency"]["Xylose"] = xe / 100.0
                        # Ensure non-zero swept efficiency pathways are active in scenario
                        if xe > 0:
                            p["fermentable"]["Xylose"] = True
                        if ge > 0:
                            p["fermentable"]["Glucose"] = True
                        r = calculate_scenario(p)
                        rows.append({
                            "Cellulose hydrolysis (%)": ch, "Xylan hydrolysis (%)": xh,
                            "Glucose fermentation (%)": ge, "Xylose fermentation (%)": xe,
                            "Recovered ethanol (kg)": round(r["recovered_ethanol_kg"], 2),
                            "Ethanol before recovery (kg)": round(r["ethanol_before_recovery_kg"], 2),
                            "Sugar available (kg)": round(r["total_sugars_kg"], 2),
                        })
                    result_df = pd.DataFrame(rows)
                    result_df = result_df.sort_values(objective, ascending=False).reset_index(drop=True)
                    st.session_state["sweep_result"] = result_df
        if "sweep_result" in st.session_state:
            sweep_df = st.session_state["sweep_result"]
            st.dataframe(sweep_df, use_container_width=True, hide_index=True)
            st.download_button("Download sweep CSV", sweep_df.to_csv(index=False).encode("utf-8"),
                               file_name="hyacinth_x_module_02_sweep.csv", mime="text/csv")

    with tab_model:
        st.header("Model logic")
        st.markdown("""
**Process sequence**

1. **Feedstock:** dry biomass and moisture are entered separately. Dry-basis composition must total 100%.
2. **Pretreatment:** each dry component is split into retained solids, a dissolved stream, and a degraded fraction. These fractions must not sum above 100%.
3. **Hydrolysis:** retained cellulose, xylan, and mannan are converted to modeled glucose, xylose, and mannose using user-entered efficiencies.
4. **Fermentation:** each sugar has its own fermentability switch and conversion efficiency, affected by the selected microorganism profile.
5. **Recovery:** the estimated ethanol mass is multiplied by the ethanol-recovery fraction.

**Equations**

- Wet-equivalent feedstock = dry biomass / (1 − wet-basis moisture fraction)
- Component mass = dry biomass × dry-basis composition fraction
- Modeled sugar mass = retained polymer mass × hydrolysis efficiency × hydration factor
- Fermented sugar = modeled sugar × fermentation efficiency, if the sugar pathway is enabled
- Ethanol before recovery = sum of fermented sugar × theoretical ethanol yield (0.511 kg/kg)
- Recovered ethanol = ethanol before recovery × recovery fraction

**Key limitations**

- This is a simplified screening calculator, not a rigorous plant-wide mass balance or equipment simulator.
- The 0.511 kg ethanol/kg sugar value is a theoretical stoichiometric yield; actual yields are lower and depend on strain and conditions.
- Dissolved pretreatment components are not automatically converted into sugars. Add measured soluble monosaccharides only when lab data are available.
- Inhibitors, detoxification, nutrients, cell growth, sugar degradation, water consumption, energy demand, wastewater, lignin valorization, and economics are not calculated.
- All starter profile values are illustrative and should be replaced by literature-backed or experimental data.
""")
        st.subheader("Microorganism profile notes")
        for name, profile in MICROBES.items():
            with st.expander(name):
                st.write(profile["note"])
                st.write("Fermentable pathways:", ", ".join(s for s in SUGARS if profile["fermentable"][s]) or "None")
                st.write("Starter efficiencies:", ", ".join(f"{s}: {profile['efficiency'][s]*100:.0f}%" for s in SUGARS))
        st.warning("Do not use these outputs as guaranteed production rates, design specifications, or commercial forecasts.")

if __name__ == "__main__":
    main()
