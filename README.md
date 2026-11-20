# 🌿 HYACINTH-X — Second-Generation Bioethanol Platform

A suite of preliminary engineering calculators and process screening tools for water-hyacinth (*Eichhornia crassipes*) valorization and second-generation bioethanol production.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://hyacinth-x.streamlit.app)

🌐 **Public Web App URL:** [https://hyacinth-x.streamlit.app](https://hyacinth-x.streamlit.app)

---

## 🚀 Modules Overview

### ♻️ Module 04: Zero-Waste Manager *(New)*
Mass-flow tracking, residue valorization, and circularity indicators for biorefinery process streams:
1. **Process Streams Basis:** Time basis selection (Daily `kg/day` or Hourly `kg/hour`), with direct manual stream input or automated JSON import from upstream modules.
2. **Residue Valorization Pathways:**
   - **Lignin-rich residue:** Allocation across combustion/energy recovery, materials (binders, adsorbents), and biochar/carbonized materials.
   - **Other solid residues:** Allocation across composting/soil amendment, energy recovery, and material pathways.
   - **Ash & inorganic solids:** Partitioning between beneficial mineral/soil reuse and managed disposal.
   - Real-time allocation error checks and unassigned stream warnings.
3. **Water Management:** Wastewater recycling ratio and post-recycle wastewater treatment fraction before environmental discharge.
4. **CO₂ Management:** Biogenic CO₂ capture percentage and captured CO₂ utilization/storage accounting.
5. **Results & Circularity Indicators:**
   - Key circularity metrics: Solid residue recovery allocation %, water recycle ratio %, and CO₂ utilization ratio %.
   - Stream allocation and mass balances for solids, water, and carbon dioxide.
6. **Data Export:** Complete results export in JSON (including basis, inputs, allocations, outputs, and indicators) and solid-stream / comprehensive balances in CSV.

### ⚡ Module 03: PFD-Based Energy & Utilities Calculator
Estimates process utility demand (thermal and electrical) across equipment stages:
1. **Production Basis:** Dry biomass feed rate (kg/day) and ethanol production target (kg/day).
2. **Washing & Drying:** Hydraulic pump energy from wash flow and pump head; dryer thermal duty accounting for sensible water heating, latent heat of evaporation, and dry solids heating with efficiency rating.
3. **Milling & Slurry:** Specific electrical intensity for mechanical comminution and daily slurry tank mixing energy.
4. **Pretreatment:** Slurry liquid sensible heating plus hold-time and heat-loss allowance.
5. **Separation & Fermentation:** Solid-liquid separation filter press energy, fermenter agitation, optional cooling duty, and broth centrifugation electricity.
6. **Product Recovery:** Distillation duty per m³ broth volume and ethanol product dehydration intensity.
7. **Heat Recovery & Utility Economics:** Recoverable fraction calculation on eligible thermal loads (pretreatment + distillation) and daily/per-liter utility cost summary.
8. **Data Export:** Complete equipment thermal and electrical duty breakdown downloadable as CSV.

### 🌿 Module 02: Process Yield Estimator
A screening model that estimates ethanol yield from dry biomass through four sequential stages:
1. **Feedstock Inventory:** Wet-equivalent mass derived from dry biomass and wet-basis moisture content, with dry-basis composition tracking.
2. **Pretreatment Solid Split:** Separates initial dry components into retained solids, dissolved streams, and degraded fractions.
3. **Carbohydrate Hydrolysis:** Conversions of retained cellulose, xylan, and mannan to glucose, xylose, and mannose accounting for hydration factors. Supports measured soluble monosaccharides from lab data.
4. **Fermentation & Pathway Modeling:** Microorganism profile selection (Conventional *S. cerevisiae*, xylose-fermenting yeast, or custom profiles) with pathway-specific fermentability switches and conversion efficiencies.
5. **Recovery & Export:** Theoretical yields calculated per sugar pathway and multiplied by ethanol recovery efficiency, with CSV data export and automatic multi-parameter scenario sweeping.

### 📋 Module 01: Feedstock Analyzer
Feedstock characterization and mass accounting:
- Wet biomass feed rates (kg/day) and wet-basis moisture content.
- Dry-basis composition tracking (Cellulose, Hemicellulose, Lignin, Ash, and Other).
- Mass inventory calculation (dry matter, water content, component flow rates).
- Local profile persistence and CSV results export.

---

## 🛠️ Local Development & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MohamedAdel2507/hyacinth-x.git
   cd hyacinth-x
   ```

2. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit application:**
   ```bash
   streamlit run app.py
   ```
   *Or run Module 04 independently:*
   ```bash
   streamlit run hyacinth_x_module_04.py
   ```

---

## ☁️ Deployment on Streamlit Community Cloud

The repository is linked directly to Streamlit Community Cloud:
- **Repository:** `MohamedAdel2507/hyacinth-x`
- **Branch:** `main`
- **Main file path:** `app.py`
- **Public URL:** [https://hyacinth-x.streamlit.app](https://hyacinth-x.streamlit.app)

Any commit pushed to `main` triggers an automatic live deployment rebuild on Streamlit Community Cloud.
