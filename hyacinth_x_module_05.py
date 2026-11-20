# HYACINTH-X | Module 05: Techno-Economic Analysis
# Run standalone: python -m streamlit run hyacinth_x_module_05.py
from __future__ import annotations

import json
import math
from typing import Any

import pandas as pd
import streamlit as st


def num(v: Any, default: float | None = 0.0) -> float | None:
    """Safely convert value to finite float or return default."""
    try:
        if v is None:
            return default
        x = float(v)
        return x if math.isfinite(x) else default
    except (ValueError, TypeError):
        return default


def find_nested_val(obj: Any, aliases: set[str] | list[str]) -> float | None:
    """Recursively search for alias match returning first valid numeric float."""
    alias_set = {str(a).lower().replace(" ", "_") for a in aliases}
    if isinstance(obj, dict):
        for k, v in obj.items():
            if str(k).lower().replace(" ", "_") in alias_set and not isinstance(v, (dict, list)):
                val = num(v, None)
                if val is not None:
                    return val
        for v in obj.values():
            x = find_nested_val(v, alias_set)
            if x is not None:
                return x
    elif isinstance(obj, list):
        for item in obj:
            x = find_nested_val(item, alias_set)
            if x is not None:
                return x
    return None


def imported_val(data: dict, aliases: list[str]) -> float:
    v = find_nested_val(data, aliases)
    return float(v) if v is not None else 0.0


def main() -> None:
    try:
        st.set_page_config(page_title="HYACINTH-X | Module 05", page_icon="💰", layout="wide")
    except Exception:
        pass

    st.title("💰 HYACINTH-X | Module 05")
    st.header("Techno-Economic Analysis (TEA)")
    st.caption("Screening-level economic assessment of the water-hyacinth bioethanol process.")
    st.info("This is a screening model, not a validated plant design or investment forecast. Check imported values and units.")

    st.subheader("1 | Import process data")
    upload = st.file_uploader("Import JSON from Modules 02–04 (optional)", type=["json"])
    data: dict[str, Any] = {}
    if upload:
        try:
            data = json.load(upload)
            st.success("JSON loaded. Please verify the mapped quantities and units below.")
        except Exception as e:
            st.error(f"JSON read error: {e}")

    aliases = {
        "annual": [
            "annual_ethanol_production", "ethanol_annual_l", "annual_production_l",
            "ethanol_production_l_year", "annual_ethanol_l", "ethanol_produced_annual"
        ],
        "daily": [
            "ethanol_production", "ethanol_l_day", "daily_ethanol_production",
            "ethanol_produced_l_day", "daily_production_l", "recovered_ethanol_kg",
            "ethanol_kg_day"
        ],
        "feed": [
            "feedstock_kg", "biomass_kg", "water_hyacinth_kg", "feedstock_mass_kg",
            "dry_mass_kg", "dry_biomass_kg_day", "wet_equivalent_kg"
        ],
        "enzymes": [
            "enzyme_consumption", "enzymes_kg", "enzyme_kg", "enzyme_requirement_kg",
            "enzyme_consumption_kg_day"
        ],
        "chem": [
            "chemical_consumption_kg", "chemicals_kg", "chemical_requirement_kg",
            "chemicals_consumption"
        ],
        "yeast": [
            "yeast_kg", "microorganism_kg", "microbial_consumption_kg", "yeast_consumption"
        ],
        "elec": [
            "electricity_kwh", "electricity_consumption_kwh", "power_consumption_kwh_day",
            "total_electricity_kwh_day", "total_electric_kwh"
        ],
        "heat": [
            "thermal_energy_kwh", "steam_energy_kwh", "heat_consumption_kwh",
            "thermal_consumption_kwh", "total_thermal_kwh", "thermal_kwh_day"
        ],
        "water": [
            "freshwater_m3", "water_consumption_m3", "process_water_m3",
            "water_requirement_m3", "water_discharge", "water_treated", "wastewater_raw"
        ],
        "waste": [
            "waste_treatment_kg", "waste_kg", "discard_kg", "waste_mass_kg",
            "solid_unassigned", "ash_disposal"
        ],
        "co2": [
            "co2_kg", "co2_produced", "co2_generation_kg", "biogenic_co2",
            "co2_captured", "co2_utilized"
        ],
        "biochar": [
            "biochar_kg", "biochar_produced_kg", "biochar_yield", "lignin_char",
            "solid_recovered"
        ]
    }
    vals = {k: imported_val(data, a) for k, a in aliases.items()}

    st.subheader("2 | Production & consumption data")
    st.caption("Imported values are suggested starting values; edit them as needed. Quantities below are annual unless noted.")
    c1, c2, c3 = st.columns(3)
    with c1:
        days = st.number_input("Operating days/year", min_value=1, max_value=365, value=300)
        daily = st.number_input("Ethanol production (L/day)", min_value=0.0, value=float(max(0.0, vals["daily"])), step=10.0)
    with c2:
        annual_import = max(0.0, vals["annual"])
        default_annual = float(annual_import if annual_import > 0 else (daily * days))
        annual = st.number_input("Annual ethanol production (L/year)", min_value=0.0, value=default_annual, step=100.0)
        capacity = st.number_input("Nameplate capacity (L/year, optional)", min_value=0.0, value=0.0, step=1000.0)
    with c3:
        feedstock = st.number_input("Feedstock consumption (kg/year)", min_value=0.0, value=float(max(0.0, vals["feed"])), step=100.0)

    c1, c2, c3 = st.columns(3)
    with c1:
        enzyme_qty = st.number_input("Enzymes (kg/year)", min_value=0.0, value=float(max(0.0, vals["enzymes"])), step=10.0)
    with c2:
        chemical_qty = st.number_input("Other chemicals (kg/year)", min_value=0.0, value=float(max(0.0, vals["chem"])), step=10.0)
    with c3:
        yeast_qty = st.number_input("Yeast / microorganisms (kg/year)", min_value=0.0, value=float(max(0.0, vals["yeast"])), step=10.0)

    c1, c2, c3 = st.columns(3)
    with c1:
        electricity = st.number_input("Electricity (kWh/year)", min_value=0.0, value=float(max(0.0, vals["elec"])), step=100.0)
    with c2:
        thermal = st.number_input("Thermal energy / steam (kWh/year)", min_value=0.0, value=float(max(0.0, vals["heat"])), step=100.0)
    with c3:
        water = st.number_input("Freshwater (m³/year)", min_value=0.0, value=float(max(0.0, vals["water"])), step=10.0)

    c1, c2, c3 = st.columns(3)
    with c1:
        waste_qty = st.number_input("Waste for treatment (kg/year)", min_value=0.0, value=float(max(0.0, vals["waste"])), step=100.0)
    with c2:
        co2_qty = st.number_input("CO₂ generated (kg/year, optional)", min_value=0.0, value=float(max(0.0, vals["co2"])), step=100.0)
    with c3:
        biochar_qty = st.number_input("Biochar / saleable by-product (kg/year)", min_value=0.0, value=float(max(0.0, vals["biochar"])), step=100.0)

    st.subheader("3 | Market prices")
    st.caption("Enter prices in EGP; use the same currency consistently.")
    st.markdown("**Raw materials**")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        feed_price = st.number_input("Feedstock (EGP/kg)", min_value=0.0, value=0.0, step=0.1)
    with c2:
        enzyme_price = st.number_input("Enzymes (EGP/kg)", min_value=0.0, value=0.0, step=1.0)
    with c3:
        chem_price = st.number_input("Chemicals average (EGP/kg)", min_value=0.0, value=0.0, step=1.0)
    with c4:
        yeast_price = st.number_input("Yeast (EGP/kg)", min_value=0.0, value=0.0, step=1.0)

    st.markdown("**Utilities**")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        elec_price = st.number_input("Electricity (EGP/kWh)", min_value=0.0, value=0.0, step=0.1)
    with c2:
        heat_price = st.number_input("Thermal energy (EGP/kWh)", min_value=0.0, value=0.0, step=0.1)
    with c3:
        water_price = st.number_input("Water (EGP/m³)", min_value=0.0, value=0.0, step=0.1)
    with c4:
        fuel_cost = st.number_input("Other fuel (EGP/year)", min_value=0.0, value=0.0, step=100.0)

    st.markdown("**Product & by-products**")
    c1, c2, c3 = st.columns(3)
    with c1:
        ethanol_price = st.number_input("Bioethanol selling price (EGP/L)", min_value=0.0, value=0.0, step=1.0)
    with c2:
        biochar_price = st.number_input("Biochar selling price (EGP/kg)", min_value=0.0, value=0.0, step=0.1)
    with c3:
        other_revenue = st.number_input("Other by-product revenue (EGP/year)", min_value=0.0, value=0.0, step=100.0)

    st.subheader("4 | Annual operating costs")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        labor = st.number_input("Labor (EGP/year)", min_value=0.0, value=0.0, step=1000.0)
    with c2:
        maintenance = st.number_input("Maintenance (EGP/year)", min_value=0.0, value=0.0, step=1000.0)
    with c3:
        transport = st.number_input("Transportation (EGP/year)", min_value=0.0, value=0.0, step=1000.0)
    with c4:
        waste_cost = st.number_input("Waste treatment (EGP/year)", min_value=0.0, value=0.0, step=1000.0)

    c1, c2 = st.columns(2)
    with c1:
        other_opex = st.number_input("Other OPEX (EGP/year)", min_value=0.0, value=0.0, step=1000.0)
    with c2:
        energy_credit = st.number_input("Energy recovery savings / credit (EGP/year)", min_value=0.0, value=0.0, step=1000.0)

    st.subheader("5 | Optional financial assumptions")
    c1, c2, c3 = st.columns(3)
    with c1:
        capex = st.number_input("CAPEX (EGP)", min_value=0.0, value=0.0, step=100000.0)
    with c2:
        lifetime = st.number_input("Plant lifetime (years)", min_value=1, max_value=50, value=10)
    with c3:
        discount_pct = st.number_input("Discount rate (%)", min_value=0.0, max_value=100.0, value=10.0, step=1.0)

    c1, c2 = st.columns(2)
    with c1:
        tax_pct = st.number_input("Tax rate (%) (optional)", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
    with c2:
        capital_in_break_even = st.checkbox("Include annualized CAPEX in break-even", value=True)

    # Calculation engine
    costs = {
        "Feedstock": feedstock * feed_price,
        "Enzymes": enzyme_qty * enzyme_price,
        "Chemicals": chemical_qty * chem_price,
        "Yeast / microorganisms": yeast_qty * yeast_price,
        "Electricity": electricity * elec_price,
        "Thermal energy": thermal * heat_price,
        "Freshwater": water * water_price,
        "Fuel": fuel_cost,
        "Labor": labor,
        "Maintenance": maintenance,
        "Transportation": transport,
        "Waste treatment": waste_cost,
        "Other OPEX": other_opex
    }
    gross_opex = sum(costs.values())
    net_opex = max(0.0, gross_opex - energy_credit)

    r = discount_pct / 100.0
    if capex == 0:
        capital_charge = 0.0
    elif r == 0:
        capital_charge = capex / lifetime
    else:
        capital_charge = capex * (r * (1 + r) ** lifetime) / (((1 + r) ** lifetime) - 1)

    biochar_revenue = biochar_qty * biochar_price
    byproduct_revenue = biochar_revenue + other_revenue
    revenue = annual * ethanol_price + byproduct_revenue
    operating_profit = revenue - net_opex
    profit_after_capital_before_tax = operating_profit - capital_charge
    tax_estimate = max(0.0, profit_after_capital_before_tax) * (tax_pct / 100.0)
    indicative_net_profit = profit_after_capital_before_tax - tax_estimate

    cost_per_l = (net_opex / annual) if annual > 0 else None
    be_operating = (max(0.0, (net_opex - byproduct_revenue) / annual)) if annual > 0 else None
    be_capital = (max(0.0, (net_opex + capital_charge - byproduct_revenue) / annual)) if annual > 0 else None
    margin = (operating_profit / revenue * 100.0) if revenue > 0 else None
    payback = (capex / operating_profit) if (capex > 0 and operating_profit > 0) else None

    st.subheader("6 | Economic results")
    if annual <= 0:
        st.warning("Annual ethanol production must be above zero for per-liter metrics.")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Annual OPEX", f"{net_opex:,.2f} EGP")
    k2.metric("Operating cost / L", f"{cost_per_l:,.2f} EGP/L" if cost_per_l is not None else "—")
    k3.metric("Annual revenue", f"{revenue:,.2f} EGP")
    k4.metric("Operating profit", f"{operating_profit:,.2f} EGP")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Operating break-even", f"{be_operating:,.2f} EGP/L" if be_operating is not None else "—")
    k2.metric("Break-even incl. capital", f"{be_capital:,.2f} EGP/L" if be_capital is not None else "—")
    k3.metric("Operating margin", f"{margin:,.2f}%" if margin is not None else "—")
    k4.metric("Simple payback", f"{payback:,.2f} years" if payback is not None else "—")

    st.markdown("**Cost breakdown**")
    cost_rows = [{"Cost category": k, "Annual cost (EGP)": v} for k, v in costs.items() if v > 0]
    if energy_credit > 0:
        cost_rows.append({"Cost category": "Energy recovery credit", "Annual cost (EGP)": -energy_credit})

    if cost_rows:
        cost_df = pd.DataFrame(cost_rows)
        st.bar_chart(cost_df.set_index("Cost category")["Annual cost (EGP)"])
        st.dataframe(cost_df, width="stretch", hide_index=True)
    else:
        st.caption("Enter costs to display the breakdown.")

    comparison = pd.DataFrame({
        "Metric": ["Annual revenue", "Annual OPEX", "OPEX + annualized CAPEX"],
        "EGP/year": [revenue, net_opex, net_opex + capital_charge]
    })
    st.markdown("**Revenue vs. cost**")
    st.bar_chart(comparison.set_index("Metric"))
    st.dataframe(comparison, width="stretch", hide_index=True)

    if annual > 0:
        if operating_profit >= 0:
            st.success("Operating scenario is above operating break-even under the entered assumptions.")
        else:
            st.warning("Operating scenario is below operating break-even under the entered assumptions.")

    st.subheader("7 | Sensitivity analysis")
    change = st.slider("One-at-a-time change in selected input prices (%)", 5, 100, 20, 5)
    sens_rows = []
    for label, cost in [
        ("Feedstock price", costs["Feedstock"]),
        ("Enzyme price", costs["Enzymes"]),
        ("Chemical prices", costs["Chemicals"]),
        ("Electricity price", costs["Electricity"]),
        ("Thermal energy price", costs["Thermal energy"]),
    ]:
        delta = cost * (change / 100.0)
        sens_rows.append({
            "Variable": label,
            f"+{change}% price (profit EGP/year)": f"{(operating_profit - delta):,.2f}",
            f"-{change}% price (profit EGP/year)": f"{(operating_profit + delta):,.2f}",
        })
    sensitivity_df = pd.DataFrame(sens_rows)
    st.dataframe(sensitivity_df, width="stretch", hide_index=True)
    st.caption("One factor changes at a time; all other inputs remain constant. This is not probabilistic risk analysis.")

    st.subheader("8 | Export")
    inputs = {
        "ethanol_L_year": annual,
        "operating_days_year": days,
        "feedstock_kg_year": feedstock,
        "enzymes_kg_year": enzyme_qty,
        "chemicals_kg_year": chemical_qty,
        "yeast_kg_year": yeast_qty,
        "electricity_kWh_year": electricity,
        "thermal_kWh_year": thermal,
        "freshwater_m3_year": water,
        "waste_kg_year": waste_qty,
        "co2_kg_year": co2_qty,
        "biochar_kg_year": biochar_qty,
        "nameplate_capacity_L_year": capacity,
    }
    prices = {
        "feedstock_EGP_kg": feed_price,
        "enzyme_EGP_kg": enzyme_price,
        "chemical_EGP_kg": chem_price,
        "yeast_EGP_kg": yeast_price,
        "electricity_EGP_kWh": elec_price,
        "thermal_EGP_kWh": heat_price,
        "water_EGP_m3": water_price,
        "ethanol_EGP_L": ethanol_price,
        "biochar_EGP_kg": biochar_price,
    }
    results = {
        "annual_OPEX_EGP": net_opex,
        "gross_annual_cost_EGP": gross_opex,
        "energy_recovery_credit_EGP": energy_credit,
        "annualized_CAPEX_EGP": capital_charge,
        "annual_revenue_EGP": revenue,
        "byproduct_revenue_EGP": byproduct_revenue,
        "operating_profit_EGP": operating_profit,
        "estimated_net_profit_after_capital_and_tax_EGP": indicative_net_profit,
        "production_cost_EGP_L": cost_per_l,
        "operating_break_even_EGP_L": be_operating,
        "break_even_including_capital_EGP_L": be_capital,
        "operating_margin_percent": margin,
        "simple_payback_years": payback,
    }

    summary_rows = (
        [{"Type": "Input", "Item": k, "Value": v} for k, v in inputs.items()]
        + [{"Type": "Price", "Item": k, "Value": v} for k, v in prices.items()]
        + [{"Type": "Cost", "Item": k, "Value": v} for k, v in costs.items()]
        + [{"Type": "Result", "Item": k, "Value": (f"{v:,.4f}" if isinstance(v, (int, float)) else (v if v is not None else ""))} for k, v in results.items()]
    )
    summary_df = pd.DataFrame(summary_rows)
    st.download_button(
        label="⬇️ Download economic summary CSV",
        data=summary_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="HYACINTH_X_Module_05_Economic_Summary.csv",
        mime="text/csv",
    )

    json_data = {
        "module": "HYACINTH-X Module 05 TEA",
        "scope": "screening estimate",
        "inputs": inputs,
        "prices": prices,
        "annual_cost_breakdown_EGP": costs,
        "results": results,
        "financial_assumptions": {
            "CAPEX_EGP": capex,
            "lifetime_years": lifetime,
            "discount_rate_percent": discount_pct,
            "tax_rate_percent": tax_pct,
            "capital_in_break_even": capital_in_break_even,
        },
        "note": "Check units and assumptions. Alias-based JSON import is a convenience and may require manual verification.",
    }
    st.download_button(
        label="⬇️ Download inputs & results JSON",
        data=json.dumps(json_data, indent=2, ensure_ascii=False),
        file_name="HYACINTH_X_Module_05_Economic_Summary.json",
        mime="application/json",
    )

    with st.expander("Model assumptions and limitations"):
        st.markdown("""
- Preliminary screening model, not a validated plant financial model.
- Alias-based JSON matching is a convenience, not a guaranteed integration/API; verify imported data and annualization.
- All quantities and price units must be consistent and annualized.
- Water cost uses entered freshwater demand; ensure recycled water is already reflected in net freshwater quantity to avoid double counting.
- Waste-treatment cost is an annual cost entry; do not double count it with separate quantity-based pricing.
- Energy-recovery credit reduces OPEX; avoid also reducing energy consumption unless consistent with the accounting basis.
- By-product revenue assumes the entered quantity is saleable at the entered price.
- Capital charge uses a capital recovery factor (or straight-line allocation when discount rate is zero) and is separate from OPEX.
- Operating margin is calculated before annualized CAPEX and tax. The net-profit estimate subtracts annualized CAPEX and estimated tax.
- Simple payback ignores time value of money and taxes.
- Sensitivity changes one input at a time, not a Monte Carlo analysis.
""")
    st.caption("HYACINTH-X | Module 05 | Techno-Economic Analysis")


if __name__ == "__main__":
    main()
