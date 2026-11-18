"""
HYACINTH-X — Module 03: PFD-Based Energy & Utilities Calculator
Standalone Streamlit screening model for the water-hyacinth bioethanol process.
Run:
    pip install streamlit pandas
    streamlit run hyacinth_x_module_03.py

All default values are illustrative. Replace with measured/vendor/literature data.
This is a preliminary energy screening tool, not a validated plant design.
"""
from __future__ import annotations
import math
import pandas as pd
import streamlit as st

APP_TITLE = "HYACINTH-X | Module 03 — Energy & Utilities Calculator"
CP_WATER = 0.004186              # MJ/(kg.K)
CP_BIOMASS = 0.0015              # MJ/(kg.K), approximate dry biomass
LATENT_WATER = 2.257             # MJ/kg at ~100 C
RHO_WATER = 1000.0               # kg/m3
G = 9.81
ETHANOL_DENSITY = 0.789          # kg/L
MJ_PER_KWH = 3.6

def _nonnegative(x, name):
    x = float(x)
    if x < 0:
        raise ValueError(f"{name} cannot be negative.")
    return x

def calculate_energy(p: dict) -> dict:
    """Return per-equipment energy on a daily basis. Inputs use kg/day, m3/day, kWh/day."""
    dry = _nonnegative(p["dry_biomass_kg_day"], "Dry biomass")
    ethanol = _nonnegative(p["ethanol_kg_day"], "Ethanol production")
    m0 = float(p["initial_moisture_pct"]) / 100
    mt = float(p["target_moisture_pct"]) / 100
    if not (0 <= m0 < 1 and 0 <= mt < 1):
        raise ValueError("Moisture values must be from 0% to less than 100%.")
    if mt > m0:
        raise ValueError("Target moisture must not exceed initial moisture for a drying calculation.")

    # 1) Washing: pump hydraulic energy from flow and head.
    wash_water = _nonnegative(p["washing_water_m3_day"], "Washing water")
    head = _nonnegative(p["washing_pump_head_m"], "Pump head")
    pump_eff = float(p["washing_pump_eff_pct"]) / 100
    if not 0 < pump_eff <= 1: raise ValueError("Pump efficiency must be >0 and <=100%.")
    wash_kwh = (RHO_WATER * G * head * wash_water / pump_eff) / 3.6e6

    # 2) Drying: water removed from wet biomass, plus heating of solids and evaporated water.
    water_initial = dry * m0 / (1-m0) if m0 else 0.0
    water_target = dry * mt / (1-mt) if mt else 0.0
    water_removed = max(0.0, water_initial-water_target)
    t_in = float(p["dryer_inlet_temp_c"])
    t_evap = 100.0
    dryer_eff = float(p["dryer_eff_pct"])/100
    if not 0 < dryer_eff <= 1: raise ValueError("Dryer efficiency must be >0 and <=100%.")
    water_heat = water_removed * CP_WATER * max(0, t_evap-t_in)
    evaporation = water_removed * LATENT_WATER
    solids_heat = dry * CP_BIOMASS * max(0, t_evap-t_in)
    dryer_mj = (water_heat + evaporation + solids_heat) / dryer_eff

    # 3) Milling: specific electrical consumption per tonne dry feed.
    milling_kwh = dry/1000 * _nonnegative(p["milling_kwh_per_t"], "Milling intensity")

    # 4) Slurry tank: user-entered mixer electricity.
    slurry_kwh = _nonnegative(p["slurry_mixing_kwh_day"], "Slurry mixing energy")

    # 5) Pretreatment: sensible heating of biomass + process liquid from inlet to setpoint.
    lsr = _nonnegative(p["pretreatment_liquid_solid_ratio"], "Liquid-to-solid ratio")
    slurry_liquid = dry * lsr
    t_pre_in = float(p["pretreatment_inlet_temp_c"])
    t_pre = float(p["pretreatment_temp_c"])
    if t_pre < t_pre_in: raise ValueError("Pretreatment temperature must be >= inlet temperature.")
    pre_eff = float(p["pretreatment_heater_eff_pct"])/100
    if not 0 < pre_eff <= 1: raise ValueError("Pretreatment heater efficiency must be >0 and <=100%.")
    pre_sensible = (slurry_liquid*CP_WATER + dry*CP_BIOMASS) * (t_pre-t_pre_in)
    pre_allowance = _nonnegative(p["pretreatment_hold_loss_mj_day"], "Pretreatment hold/loss allowance")
    pretreatment_mj = (pre_sensible + pre_allowance)/pre_eff

    # 6) Filter press: specific electrical energy per tonne of incoming slurry.
    slurry_mass = dry + slurry_liquid
    filter_kwh = slurry_mass/1000 * _nonnegative(p["filter_press_kwh_per_t"], "Filter press intensity")

    # 7) Fermenter: agitation plus optional cooling duty.
    broth_volume = 0.0
    ethanol_l = ethanol / ETHANOL_DENSITY
    broth_pct = float(p["broth_ethanol_vol_pct"])
    if not 0 < broth_pct <= 100:
        raise ValueError("Broth ethanol concentration must be >0 and <=100 vol%.")
    broth_ethanol_fraction = broth_pct / 100.0
    if ethanol_l > 0:
        # Convert broth volume from Liters to m3 (1 m3 = 1000 L)
        broth_volume = (ethanol_l / broth_ethanol_fraction) / 1000.0
    fermenter_mix = broth_volume * _nonnegative(p["fermenter_mixing_kwh_m3"], "Fermenter mixing intensity")
    fermenter_cooling = _nonnegative(p["fermenter_cooling_mj_day"], "Fermenter cooling duty")

    # 8) Centrifuge: specific electrical energy per m3 broth.
    centrifuge_kwh = broth_volume * _nonnegative(p["centrifuge_kwh_per_m3"], "Centrifuge intensity")

    # 9) Distillation and 10) dehydration. Distillation basis is broth volume.
    dist_eff = float(p["distillation_heater_eff_pct"])/100
    if not 0 < dist_eff <= 1: raise ValueError("Distillation heater efficiency must be >0 and <=100%.")
    dist_mj = broth_volume * _nonnegative(p["distillation_mj_per_m3_broth"], "Distillation intensity") / dist_eff
    dehydration_mj = ethanol_l * _nonnegative(p["dehydration_mj_per_l_ethanol"], "Dehydration intensity")

    # Optional heat recovery applied only to the stated eligible thermal loads.
    recovery_pct = float(p["heat_recovery_pct"])/100
    if not 0 <= recovery_pct <= 1: raise ValueError("Heat recovery must be between 0% and 100%.")
    eligible = pretreatment_mj + dist_mj
    recovered = eligible * recovery_pct

    thermal_rows = [
        ("Dryer (D-101)", dryer_mj, "Evaporation + sensible heating"),
        ("Pretreatment reactor (R-101)", pretreatment_mj, "Slurry sensible heating + hold/loss allowance"),
        ("Fermenter cooling (F-101)", fermenter_cooling, "User-entered cooling duty; reported separately"),
        ("Distillation column (C-101)", dist_mj, "Specific energy × broth volume / heater efficiency"),
        ("Dehydration", dehydration_mj, "Specific energy × ethanol product volume"),
    ]
    gross_thermal = sum(x[1] for x in thermal_rows)
    net_thermal = gross_thermal - recovered
    electric_rows = [
        ("Washing pump (T-101 service)", wash_kwh, "Hydraulic pump estimate"),
        ("Mill (M-101)", milling_kwh, "Specific electricity × dry biomass"),
        ("Slurry tank mixer (T-102)", slurry_kwh, "User-entered daily mixer electricity"),
        ("Filter press", filter_kwh, "Specific electricity × slurry mass"),
        ("Fermenter agitation (F-101)", fermenter_mix, "Specific electricity × broth volume"),
        ("Centrifuge (S-101)", centrifuge_kwh, "Specific electricity × broth volume"),
        ("Other auxiliaries", _nonnegative(p["auxiliary_kwh_day"], "Auxiliary electricity"), "User-entered daily electricity"),
    ]
    total_electric = sum(x[1] for x in electric_rows)
    thermal_cost = net_thermal/MJ_PER_KWH * _nonnegative(p["thermal_price_per_kwh"], "Thermal price")
    electric_cost = total_electric * _nonnegative(p["electricity_price_per_kwh"], "Electricity price")
    total_cost = thermal_cost + electric_cost
    energy_kwh_equiv = net_thermal/MJ_PER_KWH + total_electric
    return {
        "ethanol_l_day": ethanol_l, "broth_volume_m3_day": broth_volume,
        "water_removed_kg_day": water_removed, "slurry_liquid_kg_day": slurry_liquid,
        "thermal_rows": thermal_rows, "electric_rows": electric_rows,
        "gross_thermal_mj_day": gross_thermal, "recovered_heat_mj_day": recovered,
        "net_thermal_mj_day": net_thermal, "net_thermal_kwh_day": net_thermal/MJ_PER_KWH,
        "electric_kwh_day": total_electric, "energy_kwh_equiv_day": energy_kwh_equiv,
        "energy_kwh_per_l": energy_kwh_equiv/ethanol_l if ethanol_l else None,
        "utility_cost_day": total_cost, "utility_cost_per_l": total_cost/ethanol_l if ethanol_l else None,
        "thermal_cost_day": thermal_cost, "electric_cost_day": electric_cost,
        "eligible_heat_mj_day": eligible
    }

def main():
    try:
        st.set_page_config(page_title=APP_TITLE, page_icon="🌿", layout="wide")
    except Exception:
        pass

    st.title(APP_TITLE)
    st.caption("PFD-based preliminary energy screening for bioethanol production from water hyacinth")
    st.info("This module estimates utility demand by process equipment. Default values are illustrative, not validated design data.")
    with st.sidebar:
        st.header("1. Production basis")
        dry = st.number_input("Dry biomass feed (kg/day)", min_value=0.0, value=1000.0, step=50.0)
        ethanol = st.number_input("Ethanol production (kg/day)", min_value=0.0, value=120.0, step=10.0)
        st.caption("Enter the Module 01 dry biomass output and Module 02 ethanol output.")
        st.header("2. Washing & drying")
        wash_water = st.number_input("Washing water (m³/day)", min_value=0.0, value=3.0, step=0.5)
        head = st.number_input("Washing pump head (m)", min_value=0.0, value=15.0)
        pump_eff = st.slider("Pump efficiency (%)", 10, 95, 65)
        m0 = st.slider("Feed moisture before drying (wet basis, %)", 0, 95, 80)
        mt = st.slider("Target moisture after drying (wet basis, %)", 0, 95, 10)
        dryer_in = st.number_input("Dryer inlet temperature (°C)", value=25.0)
        dryer_eff = st.slider("Dryer thermal efficiency (%)", 10, 95, 55)
        st.header("3. Milling & slurry preparation")
        mill_int = st.number_input("Milling electricity (kWh/tonne dry biomass)", min_value=0.0, value=25.0)
        slurry_mix = st.number_input("Slurry tank mixing (kWh/day)", min_value=0.0, value=8.0)
        lsr = st.number_input("Pretreatment liquid-to-solid ratio (kg liquid/kg dry biomass)", min_value=0.0, value=8.0, step=0.5)
        st.header("4. Pretreatment")
        pre_in = st.number_input("Pretreatment inlet temperature (°C)", value=25.0)
        pre_temp = st.number_input("Pretreatment temperature (°C)", min_value=25.0, value=120.0)
        pre_eff = st.slider("Pretreatment heater efficiency (%)", 10, 99, 80)
        pre_loss = st.number_input("Hold time & heat-loss allowance (MJ/day)", min_value=0.0, value=500.0, step=50.0)
        st.header("5. Separation & fermentation")
        filter_int = st.number_input("Filter press electricity (kWh/tonne slurry)", min_value=0.0, value=5.0)
        broth_pct = st.number_input("Ethanol in fermentation broth (vol%)", min_value=0.1, max_value=20.0, value=5.0, step=0.5)
        ferment_mix = st.number_input("Fermenter mixing (kWh/m³ broth)", min_value=0.0, value=3.0)
        ferment_cool = st.number_input("Fermenter cooling duty (MJ/day)", min_value=0.0, value=0.0)
        centrifuge_int = st.number_input("Centrifuge electricity (kWh/m³ broth)", min_value=0.0, value=1.5)
        st.header("6. Product recovery")
        dist_int = st.number_input("Distillation duty (MJ/m³ broth)", min_value=0.0, value=1800.0, step=100.0)
        dist_eff = st.slider("Distillation heater efficiency (%)", 10, 99, 85)
        dehyd_int = st.number_input("Dehydration duty (MJ/L ethanol)", min_value=0.0, value=1.5, step=0.1)
        st.header("7. Heat recovery & utility prices")
        recovery = st.slider("Recoverable fraction of pretreatment + distillation heat (%)", 0, 60, 10)
        aux = st.number_input("Other auxiliary electricity (kWh/day)", min_value=0.0, value=10.0)
        thermal_price = st.number_input("Thermal utility price (currency/kWh)", min_value=0.0, value=1.5, step=0.1)
        electric_price = st.number_input("Electricity price (currency/kWh)", min_value=0.0, value=2.0, step=0.1)

    p = {
        "dry_biomass_kg_day": dry, "ethanol_kg_day": ethanol,
        "washing_water_m3_day": wash_water, "washing_pump_head_m": head, "washing_pump_eff_pct": pump_eff,
        "initial_moisture_pct": m0, "target_moisture_pct": mt, "dryer_inlet_temp_c": dryer_in,
        "dryer_eff_pct": dryer_eff, "milling_kwh_per_t": mill_int, "slurry_mixing_kwh_day": slurry_mix,
        "pretreatment_liquid_solid_ratio": lsr, "pretreatment_inlet_temp_c": pre_in,
        "pretreatment_temp_c": pre_temp, "pretreatment_heater_eff_pct": pre_eff,
        "pretreatment_hold_loss_mj_day": pre_loss, "filter_press_kwh_per_t": filter_int,
        "broth_ethanol_vol_pct": broth_pct, "fermenter_mixing_kwh_m3": ferment_mix,
        "fermenter_cooling_mj_day": ferment_cool, "centrifuge_kwh_per_m3": centrifuge_int,
        "distillation_mj_per_m3_broth": dist_int, "distillation_heater_eff_pct": dist_eff,
        "dehydration_mj_per_l_ethanol": dehyd_int, "heat_recovery_pct": recovery,
        "auxiliary_kwh_day": aux, "thermal_price_per_kwh": thermal_price,
        "electricity_price_per_kwh": electric_price
    }
    try:
        r = calculate_energy(p)
    except ValueError as e:
        st.error(str(e))
        st.stop()

    st.subheader("Key performance indicators")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Net thermal demand", f'{r["net_thermal_mj_day"]:,.0f} MJ/day')
    c2.metric("Electrical demand", f'{r["electric_kwh_day"]:,.1f} kWh/day')
    c3.metric("Energy intensity", f'{r["energy_kwh_per_l"]:,.2f} kWh/L' if r["energy_kwh_per_l"] is not None else "N/A")
    c4.metric("Utility cost", f'{r["utility_cost_day"]:,.2f} /day')
    c5,c6,c7,c8 = st.columns(4)
    c5.metric("Ethanol product", f'{r["ethanol_l_day"]:,.1f} L/day')
    c6.metric("Fermentation broth", f'{r["broth_volume_m3_day"]:,.2f} m³/day')
    c7.metric("Water evaporated in dryer", f'{r["water_removed_kg_day"]:,.0f} kg/day')
    c8.metric("Utility cost intensity", f'{r["utility_cost_per_l"]:,.2f} /L' if r["utility_cost_per_l"] is not None else "N/A")

    st.subheader("Energy demand by equipment")
    thermal_df = pd.DataFrame(r["thermal_rows"], columns=["Equipment / stage","Thermal duty (MJ/day)","Calculation meaning"])
    electric_df = pd.DataFrame(r["electric_rows"], columns=["Equipment / stage","Electricity (kWh/day)","Calculation meaning"])
    tab1,tab2,tab3 = st.tabs(["Thermal utilities","Electrical utilities","Cost breakdown"])
    with tab1:
        st.dataframe(thermal_df, use_container_width=True, hide_index=True)
        st.write(f'Gross thermal demand: **{r["gross_thermal_mj_day"]:,.1f} MJ/day**')
        st.write(f'Estimated heat recovery: **{r["recovered_heat_mj_day"]:,.1f} MJ/day**')
        st.write(f'Net thermal demand: **{r["net_thermal_mj_day"]:,.1f} MJ/day**')
    with tab2:
        st.dataframe(electric_df, use_container_width=True, hide_index=True)
    with tab3:
        cost_df = pd.DataFrame([
            ["Thermal utility",r["thermal_cost_day"]],
            ["Electricity",r["electric_cost_day"]],
            ["Total utilities",r["utility_cost_day"]]
        ],columns=["Cost item","Daily cost"])
        st.dataframe(cost_df,use_container_width=True,hide_index=True)

    st.subheader("Process basis and calculated intermediate values")
    basis = pd.DataFrame([
        ["Dry biomass feed",dry,"kg/day"],
        ["Ethanol product",ethanol,"kg/day"],
        ["Ethanol product volume",r["ethanol_l_day"],"L/day"],
        ["Water removed in drying",r["water_removed_kg_day"],"kg/day"],
        ["Pretreatment liquid estimate",r["slurry_liquid_kg_day"],"kg/day"],
        ["Fermentation broth estimate",r["broth_volume_m3_day"],"m³/day"],
        ["Eligible heat-recovery load",r["eligible_heat_mj_day"],"MJ/day"]
    ],columns=["Variable","Value","Unit"])
    st.dataframe(basis,use_container_width=True,hide_index=True)

    st.subheader("Engineering assumptions & limitations")
    st.markdown("""
    - Drying uses a simplified water-heating + evaporation + dry-solids sensible-heat model.
    - Pretreatment heating assumes the liquid-to-solid ratio represents water-like process liquid.
    - Distillation uses a user-editable specific duty per m³ of fermentation broth; it is not a rigorous VLE/column model.
    - Dehydration is an additional user-entered duty to reach the selected high-purity ethanol target.
    - Heat recovery is a screening credit applied to pretreatment and distillation loads only; temperature compatibility and exchanger design are not solved.
    - Washing, milling, mixing, filtration and centrifugation use hydraulic or specific-energy estimates.
    - Condenser cooling-water flow, steam pressure, equipment sizing, transient operation and detailed heat integration are outside this module.
    """)
    out = pd.concat([
        thermal_df.assign(Utility="Thermal"),
        electric_df.rename(columns={"Electricity (kWh/day)":"Thermal duty (MJ/day)"}).assign(Utility="Electrical")
    ],ignore_index=True,sort=False)
    st.download_button("Download equipment energy results (CSV)",out.to_csv(index=False).encode("utf-8-sig"),
                       file_name="hyacinth_x_module_03_energy_results.csv",mime="text/csv")
    st.caption("HYACINTH-X | Module 03 | Preliminary engineering estimate — validate all inputs before design decisions.")

if __name__ == "__main__":
    main()
