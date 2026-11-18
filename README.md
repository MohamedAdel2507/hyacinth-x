# 🌿 HYACINTH-X — Second-Generation Bioethanol Platform

A suite of preliminary engineering calculators and process screening tools for water-hyacinth (*Eichhornia crassipes*) valorization and second-generation bioethanol production.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://hyacinth-x.streamlit.app)

🌐 **Public Web App URL:** [https://hyacinth-x.streamlit.app](https://hyacinth-x.streamlit.app)

---

## 🚀 Modules Overview

### ⚡ Module 03: PFD-Based Energy & Utilities Calculator *(New)*
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
   *Or run Module 03 independently:*
   ```bash
   streamlit run hyacinth_x_module_03.py
   ```

---

## ☁️ Deployment on Streamlit Community Cloud

The repository is linked directly to Streamlit Community Cloud:
- **Repository:** `MohamedAdel2507/hyacinth-x`
- **Branch:** `main`
- **Main file path:** `app.py`
- **Public URL:** [https://hyacinth-x.streamlit.app](https://hyacinth-x.streamlit.app)

Any commit pushed to `main` triggers an automatic live deployment rebuild on Streamlit Community Cloud.
