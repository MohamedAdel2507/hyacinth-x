# 🌿 HYACINTH-X — Module 01: Feedstock Analyzer

A preliminary engineering calculator for water-hyacinth feedstock characterization for second-generation bioethanol production.

## 🚀 Overview

HYACINTH-X Module 01 calculates feedstock mass inventories from wet biomass feed rates and dry-basis composition parameters:
- **Run-specific inputs:** Wet biomass feed rate (kg/day) and moisture content (% wet basis).
- **Composition tracking:** Cellulose, Hemicellulose, Lignin, Ash, and other characterized components (% dry basis).
- **Mass accounting:** Computes dry biomass flow rate, water content, and component mass flows with automated validation and consistency checks.
- **Profiles:** Save and load custom feedstock composition profiles locally.
- **Export:** Export comprehensive analysis results to CSV.

## 🛠️ Local Setup

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

## ☁️ Deployment on Streamlit Community Cloud

1. Push this repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io).
3. Connect your GitHub account (`MohamedAdel2507`).
4. Click **New app** and select:
   - **Repository:** `MohamedAdel2507/<repo-name>`
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. Click **Deploy!**
