"""Landing page: what this is, how good it is, and the one caveat that matters."""

from __future__ import annotations

import streamlit as st

from src import config, data, models, ui
from src.strings import t


ui.page_head(t("app_title"), t("home_hero"), t("home_intro"))

# --- Headline numbers ----------------------------------------------------
scores = models.published_metrics()
best = scores.iloc[0] if not scores.empty else None

c1, c2, c3, c4 = st.columns(4)
c1.metric(t("home_kpi_r2"), f"{best['r2']:.3f}" if best is not None else "—")
c2.metric(t("home_kpi_rmse"), f"{best['rmse']:.2f} MPa" if best is not None else "—")
c3.metric(t("home_kpi_models"), f"{len(scores)}")
c4.metric(t("home_kpi_samples"), f"{len(data.load_dataset('with_temp')):,}")

st.write("")
if st.button(f"🔮 {t('home_start')}", type="primary"):
    st.switch_page("views/predict.py")

st.markdown("---")

# --- The two model families ---------------------------------------------
st.subheader(t("home_families_title"))
left, right = st.columns(2)
for column, family in zip((left, right), ("with_temp", "no_temp")):
    meta = config.FAMILIES[family]
    available = models.available_models(family)
    family_scores = scores[scores["family"] == family] if not scores.empty else scores
    best_r2 = family_scores["r2"].max() if not family_scores.empty else float("nan")
    with column:
        ui.card(
            meta["label"],
            meta["desc"]
            + f"<br><br><strong>{', '.join(m.name for m in available)}</strong>"
            + f"<br>R² = {best_r2:.3f}",
        )

st.write("")
st.markdown("---")

# --- What is inside ------------------------------------------------------
st.subheader(t("home_pages_title"))
pages = [
    ("🔮", t("nav_predict"), t("home_page_predict")),
    ("📂", t("nav_batch"), t("home_page_batch")),
    ("📊", t("nav_data"), t("home_page_data")),
    ("🏆", t("nav_performance"), t("home_page_performance")),
    ("🧠", t("nav_explain"), t("home_page_explain")),
    ("📈", t("nav_stats"), t("home_page_stats")),
]
for row_start in (0, 3):
    columns = st.columns(3)
    for column, (icon, title, body) in zip(columns, pages[row_start:row_start + 3]):
        with column:
            ui.card(f"{icon} {title}", body)
    st.write("")

st.markdown("---")

# --- The caveat ----------------------------------------------------------
st.subheader(t("home_caveat_title"))
ui.caveat(t("home_caveat"))
