"""Concrete Compressive Strength Predictor — application entry point."""

from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="Concrete Strength Predictor",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src import ui  # noqa: E402  (must follow set_page_config)
from src.strings import t  # noqa: E402

ui.bootstrap()
ui.sidebar()

navigation = {
    t("section_main"): [
        st.Page("views/home.py", title=t("nav_home"), icon=":material/home:", default=True),
        st.Page("views/predict.py", title=t("nav_predict"), icon=":material/science:"),
        st.Page("views/batch.py", title=t("nav_batch"), icon=":material/table_rows:"),
    ],
    t("section_insight"): [
        st.Page("views/data_analysis.py", title=t("nav_data"), icon=":material/analytics:"),
        st.Page("views/performance.py", title=t("nav_performance"), icon=":material/leaderboard:"),
        st.Page("views/explain.py", title=t("nav_explain"), icon=":material/psychology:"),
        st.Page("views/statistics.py", title=t("nav_stats"), icon=":material/monitoring:"),
    ],
}

st.navigation(navigation).run()
