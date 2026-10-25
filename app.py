"""
HYACINTH-X — Second-Generation Bioethanol Platform
Integrated Web Application for Water Hyacinth Valorization
Streamlit Community Cloud Deployment Entry Point
"""
from __future__ import annotations

import streamlit as st

import hyacinth_x_module_01 as module_01
import hyacinth_x_module_02 as module_02

# Page configuration
st.set_page_config(
    page_title="HYACINTH-X | Bioethanol Engineering Platform",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

def main():
    st.sidebar.markdown("# 🌿 HYACINTH-X")
    st.sidebar.caption("Second-Generation Bioethanol Engineering Suite")

    selected_module = st.sidebar.radio(
        "Module Navigation",
        [
            "Module 02 — Process Yield Estimator",
            "Module 01 — Feedstock Analyzer",
        ],
        index=0,
        help="Select which engineering module to run.",
    )
    st.sidebar.markdown("---")

    if selected_module == "Module 02 — Process Yield Estimator":
        module_02.main()
    else:
        module_01.main()

if __name__ == "__main__":
    main()
