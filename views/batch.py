"""Batch prediction: score a whole CSV of mix designs in one pass."""

from __future__ import annotations


import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src import config, data, models, ui, usage
from src.strings import t


ui.page_head(t("nav_batch"), t("batch_title"), t("batch_intro"))

# ---------------------------------------------------------------------------
# Model choice
# ---------------------------------------------------------------------------
family = st.radio(
    t("family_label"),
    options=list(config.FAMILIES),
    format_func=lambda key: config.FAMILIES[key]["label"],
    horizontal=True,
    key="batch_family",
)

candidates = models.available_models(family)
if not candidates:
    st.error(t("no_models"))
    st.stop()

spec = st.selectbox(
    t("model_label"),
    options=candidates,
    format_func=lambda s: ui.model_label(s),
    key=f"batch_model_{family}",
)

required_columns = spec.columns

st.markdown("---")

# ---------------------------------------------------------------------------
# 1 — template
# ---------------------------------------------------------------------------
st.subheader(t("batch_step_template"))
st.caption(t("batch_template_intro"))

stats = data.feature_stats("with_temp")
example_rows = [
    {config.CEMENT: 300.0, config.SLAG: 0.0, config.FLY_ASH: 0.0, config.WATER: 180.0,
     config.SUPERPLASTICIZER: 5.0, config.COARSE_AGG: 1000.0, config.FINE_AGG: 780.0,
     config.AGE: 28.0, config.TEMPERATURE: 23.0},
    {config.CEMENT: 500.0, config.SLAG: 100.0, config.FLY_ASH: 0.0, config.WATER: 150.0,
     config.SUPERPLASTICIZER: 14.0, config.COARSE_AGG: 1000.0, config.FINE_AGG: 700.0,
     config.AGE: 28.0, config.TEMPERATURE: 22.0},
    {config.CEMENT: 200.0, config.SLAG: 150.0, config.FLY_ASH: 100.0, config.WATER: 175.0,
     config.SUPERPLASTICIZER: 8.0, config.COARSE_AGG: 950.0, config.FINE_AGG: 780.0,
     config.AGE: 56.0, config.TEMPERATURE: 25.0},
]
template = pd.DataFrame(example_rows)[required_columns]

st.download_button(
    f"⬇️ {t('batch_download_template')}",
    data=template.to_csv(index=False).encode("utf-8-sig"),
    file_name=f"concrete_batch_template_{family}.csv",
    mime="text/csv",
)

st.markdown("---")

# ---------------------------------------------------------------------------
# 2 — upload
# ---------------------------------------------------------------------------
st.subheader(t("batch_step_upload"))
upload = st.file_uploader(
    t("batch_uploader"), type=["csv", "xlsx", "xls"], key=f"batch_upload_{family}"
)


def _read(file) -> pd.DataFrame:
    if file.name.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(file)
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            file.seek(0)
            return pd.read_csv(file, encoding=encoding)
        except UnicodeDecodeError:
            continue
    file.seek(0)
    return pd.read_csv(file)


def _normalise(name: str) -> str:
    return "".join(ch for ch in str(name).lower() if ch.isalnum())


def _map_columns(frame: pd.DataFrame) -> tuple[dict[str, str], list[str]]:
    """Match uploaded headers to model columns by exact name, then by alias."""
    lookup = {_normalise(column): column for column in frame.columns}
    mapping: dict[str, str] = {}
    missing: list[str] = []

    for column in required_columns:
        feature = config.FEATURES_BY_COLUMN[column]
        keys = [column, feature.label, feature.key, *feature.csv_aliases]
        found = next((lookup[_normalise(k)] for k in keys if _normalise(k) in lookup), None)
        if found is None:
            # Last resort: a header that starts with the canonical short label.
            prefix = _normalise(feature.label)
            found = next(
                (original for norm, original in lookup.items() if norm.startswith(prefix)),
                None,
            )
        if found is None:
            missing.append(column)
        else:
            mapping[column] = found
    return mapping, missing


if upload is not None:
    try:
        raw = _read(upload)
    except Exception as error:  # noqa: BLE001 — surfaced to the user verbatim
        st.error(f"{type(error).__name__}: {error}")
        st.stop()

    if raw.empty:
        st.warning(t("batch_empty"))
        st.stop()

    mapping, missing = _map_columns(raw)
    if missing:
        st.error(t("batch_missing_cols"))
        st.markdown(
            "".join(f"- `{column}`\n" for column in missing)
        )
        st.stop()

    with st.expander(t("batch_mapped")):
        st.dataframe(
            pd.DataFrame(
                {
                    "model input": [ui.feature_label(c) for c in mapping],
                    "your column": list(mapping.values()),
                }
            ),
            width="stretch",
            hide_index=True,
        )

    frame = raw.rename(columns={v: k for k, v in mapping.items()})[required_columns].copy()
    for column in required_columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    dropped = int(frame.isna().any(axis=1).sum())
    clean = frame.dropna().reset_index(drop=True)
    kept_index = frame.dropna().index

    if dropped:
        st.warning(f"{t('batch_bad_values')} {dropped}")
    if clean.empty:
        st.warning(t("batch_empty"))
        st.stop()

    # -----------------------------------------------------------------------
    # 3 — results
    # -----------------------------------------------------------------------
    st.markdown("---")
    st.subheader(t("batch_step_results"))

    with st.spinner(t("loading")):
        predictions, lower, upper = models.predict_with_interval(spec, clean)

        ranges = data.training_ranges(family)
        outside = np.zeros(len(clean), dtype=bool)
        for column in required_columns:
            low, high = ranges[column]
            outside |= (clean[column] < low) | (clean[column] > high)

    results = raw.loc[kept_index].reset_index(drop=True).copy()
    results["predicted_strength_MPa"] = np.round(predictions, 2)
    results["interval_lower_MPa"] = np.round(lower, 2)
    results["interval_upper_MPa"] = np.round(upper, 2)
    results["strength_class"] = [config.strength_class(p)[0] for p in predictions]
    results["outside_training_range"] = outside
    results["model"] = spec.name("en")

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric(t("batch_rows"), f"{len(results):,}")
    k2.metric(t("batch_mean"), f"{predictions.mean():.1f} {t('mpa')}")
    k3.metric(t("batch_min"), f"{predictions.min():.1f} {t('mpa')}")
    k4.metric(t("batch_max"), f"{predictions.max():.1f} {t('mpa')}")
    k5.metric(t("batch_outside"), f"{int(outside.sum()):,}")

    st.write("")
    st.dataframe(results, width="stretch", hide_index=True, height=340)

    st.download_button(
        f"⬇️ {t('batch_download_results')}",
        data=results.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"concrete_predictions_{family}.csv",
        mime="text/csv",
        type="primary",
    )

    st.write("")
    left, right = st.columns(2)

    with left:
        fig = go.Figure(
            go.Histogram(
                x=predictions,
                nbinsx=min(40, max(8, len(predictions) // 3)),
                marker=dict(color=ui.SERIES[0], line=dict(width=0)),
                hovertemplate="%{x:.0f} MPa<br>%{y}<extra></extra>",
            )
        )
        fig.update_layout(
            title=t("batch_dist_title"),
            xaxis_title=f"{t('result_title')} ({t('mpa')})",
            yaxis_title=t("count_axis"),
            bargap=0.05,
            height=340,
        )
        ui.chart(fig)
        ui.explain(
            t("what_batch_dist"),
            t("insight_batch_dist").format(
                mean=f"{predictions.mean():.1f}",
                std=f"{predictions.std():.1f}",
                low=f"{predictions.min():.1f}",
                high=f"{predictions.max():.1f}",
                span=f"{predictions.max() - predictions.min():.1f}",
            ),
        )

    with right:
        class_order = [name for _, name, _ in config.STRENGTH_CLASSES]
        counts = (
            pd.Series(results["strength_class"])
            .value_counts()
            .reindex(class_order)
            .dropna()
        )
        fig = go.Figure(
            go.Bar(
                x=counts.index.tolist(),
                y=counts.to_numpy(),
                marker=dict(color=ui.SERIES[0], line=dict(width=0)),
                hovertemplate="%{x}<br>%{y}<extra></extra>",
            )
        )
        fig.update_layout(
            title=t("batch_class_title"),
            yaxis_title=t("count_axis"),
            bargap=0.35,
            height=340,
        )
        ui.chart(fig)
        top_class = counts.idxmax() if not counts.empty else "-"
        ui.explain(
            t("what_batch_class"),
            t("insight_batch_class").format(
                cls=top_class,
                n=int(counts.max()) if not counts.empty else 0,
                total=len(results),
                classes=int(counts.notna().sum()),
                outside=int(outside.sum()),
            ),
        )

    # Log the run once per (file, model) pair — the script re-executes on every
    # widget interaction, and a batch must not be counted twice.
    signature = f"{upload.name}:{upload.size}:{spec.key}:{len(results)}"
    if st.session_state.get("_batch_logged") != signature:
        mean_inputs = {column: float(clean[column].mean()) for column in required_columns}
        usage.record(
            source="batch",
            model_key=spec.key,
            family=family,
            prediction=float(predictions.mean()),
            lower=float(lower.mean()),
            upper=float(upper.mean()),
            strength_class=config.strength_class(float(predictions.mean()))[0],
            extrapolated=bool(outside.any()),
            values=mean_inputs,
            n_rows=len(results),
        )
        st.session_state["_batch_logged"] = signature

    st.caption(t("batch_log_note"))
