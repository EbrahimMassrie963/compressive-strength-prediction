"""Usage statistics: how the deployment is used and how well it holds up."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src import config, data, ui, usage
from src.strings import t


ui.page_head(t("nav_stats"), t("stats_title"), t("stats_intro"))

scope = st.radio(
    t("stats_scope"),
    options=["all", "session"],
    format_func=lambda key: t("stats_scope_all") if key == "all" else t("stats_scope_session"),
    horizontal=True,
    key="stats_scope",
)

log = usage.load(scope)
totals = usage.summary(log)

if log.empty:
    st.info(t("stats_empty"))
    st.stop()


def model_name(key: str) -> str:
    spec = config.MODELS_BY_KEY.get(key)
    if spec is None:
        return key
    tag = "9F" if spec.family == "with_temp" else "8F"
    return f"{spec.name} · {tag}"


k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric(t("stats_kpi_total"), f"{totals['total_events']:,}")
k2.metric(t("stats_kpi_sessions"), f"{totals['sessions']:,}")
k3.metric(t("stats_kpi_batch"), f"{totals['batch_rows']:,}")
k4.metric(t("stats_kpi_mean"), f"{totals['mean_prediction']:.1f} {t('mpa')}")
k5.metric(t("stats_kpi_extrap"), f"{totals['extrapolated']:,}")
k6.metric(t("stats_kpi_feedback"), f"{totals['measurements']:,}")

st.write("")
tab_activity, tab_profile, tab_accuracy, tab_log = st.tabs(
    [
        t("stats_tab_activity"),
        t("stats_tab_predictions"),
        t("stats_tab_accuracy"),
        t("stats_tab_log"),
    ]
)

# ---------------------------------------------------------------------------
# Activity
# ---------------------------------------------------------------------------
with tab_activity:
    timeline = log.set_index("timestamp").sort_index()
    span_days = (timeline.index.max() - timeline.index.min()).total_seconds() / 86400
    rule = "h" if span_days <= 2 else "D"
    counts = timeline["prediction"].resample(rule).count()

    fig = go.Figure(
        go.Scatter(
            x=counts.index,
            y=counts.to_numpy(),
            mode="lines+markers",
            line=dict(color=ui.SERIES[0], width=2),
            marker=dict(size=8, line=dict(width=1, color=ui.SURFACE)),
            fill="tozeroy",
            fillcolor="rgba(42,120,214,0.10)",
            hovertemplate="%{x}<br>%{y}<extra></extra>",
        )
    )
    fig.update_layout(
        title=t("stats_over_time"),
        yaxis_title=t("count_axis"),
        height=340,
        showlegend=False,
    )
    ui.chart(fig)

    left, right = st.columns(2)

    with left:
        by_model = log["model_key"].value_counts()
        fig = go.Figure(
            go.Bar(
                x=by_model.to_numpy(),
                y=[model_name(key) for key in by_model.index],
                orientation="h",
                marker=dict(color=ui.SERIES[0], line=dict(width=0)),
                text=by_model.to_numpy(),
                textposition="outside",
                textfont=dict(color=ui.INK_SOFT, size=12),
                hovertemplate="%{y}<br>%{x}<extra></extra>",
            )
        )
        fig.update_layout(
            title=t("stats_by_model"),
            xaxis_title=t("count_axis"),
            xaxis_range=[0, float(by_model.max()) * 1.25],
            bargap=0.4,
            height=100 + 46 * len(by_model),
            showlegend=False,
        )
        ui.chart(fig)

    with right:
        by_family = log["family"].value_counts()
        family_labels = [
            config.FAMILIES.get(key, {}).get("label", key)
            for key in by_family.index
        ]
        fig = go.Figure(
            go.Bar(
                x=by_family.to_numpy(),
                y=family_labels,
                orientation="h",
                marker=dict(color=ui.SERIES[0], line=dict(width=0)),
                text=by_family.to_numpy(),
                textposition="outside",
                textfont=dict(color=ui.INK_SOFT, size=12),
                hovertemplate="%{y}<br>%{x}<extra></extra>",
            )
        )
        fig.update_layout(
            title=t("stats_by_family"),
            xaxis_title=t("count_axis"),
            xaxis_range=[0, float(by_family.max()) * 1.3],
            bargap=0.45,
            height=100 + 46 * len(by_family),
            showlegend=False,
        )
        ui.chart(fig)

        by_source = log["source"].value_counts()
        fig = go.Figure(
            go.Bar(
                x=by_source.index.tolist(),
                y=by_source.to_numpy(),
                marker=dict(color=ui.SERIES[0], line=dict(width=0)),
                text=by_source.to_numpy(),
                textposition="outside",
                textfont=dict(color=ui.INK_SOFT, size=12),
                hovertemplate="%{x}<br>%{y}<extra></extra>",
            )
        )
        fig.update_layout(
            title=t("stats_by_source"),
            yaxis_title=t("count_axis"),
            yaxis_range=[0, float(by_source.max()) * 1.25],
            bargap=0.55,
            height=300,
            showlegend=False,
        )
        ui.chart(fig)

    hours = log["timestamp"].dt.hour.value_counts().reindex(range(24), fill_value=0)
    fig = go.Figure(
        go.Bar(
            x=hours.index.tolist(),
            y=hours.to_numpy(),
            marker=dict(color=ui.SERIES[0], line=dict(width=0)),
            hovertemplate="%{x}:00 UTC<br>%{y}<extra></extra>",
        )
    )
    fig.update_layout(
        title=t("stats_hourly"),
        xaxis_title="hour (UTC)",
        yaxis_title=t("count_axis"),
        bargap=0.2,
        height=300,
        showlegend=False,
    )
    ui.chart(fig)

# ---------------------------------------------------------------------------
# Prediction profile
# ---------------------------------------------------------------------------
with tab_profile:
    training_target = data.target_series("with_temp")

    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=training_target,
            name="training data",
            histnorm="probability density",
            nbinsx=40,
            marker=dict(color="#c9c7c2", line=dict(width=0)),
            opacity=0.85,
            hovertemplate="%{x:.0f} MPa<extra>training data</extra>",
        )
    )
    fig.add_trace(
        go.Histogram(
            x=log["prediction"],
            name="user predictions",
            histnorm="probability density",
            nbinsx=40,
            marker=dict(color=ui.SERIES[0], line=dict(width=0)),
            opacity=0.75,
            hovertemplate="%{x:.0f} MPa<extra>user predictions</extra>",
        )
    )
    fig.update_layout(
        title=t("stats_pred_dist"),
        barmode="overlay",
        xaxis_title=f"{t('result_title')} ({t('mpa')})",
        yaxis_title="density",
        height=380,
        bargap=0.04,
    )
    ui.chart(fig)
    st.caption(t("stats_pred_dist_note"))

    classes = log["strength_class"].dropna().astype(str)
    if not classes.empty:
        order = [name for _, name, _ in config.STRENGTH_CLASSES]
        counts = classes.value_counts().reindex(order).dropna()
        fig = go.Figure(
            go.Bar(
                x=counts.index.tolist(),
                y=counts.to_numpy(),
                marker=dict(color=ui.SERIES[0], line=dict(width=0)),
                text=counts.to_numpy(),
                textposition="outside",
                textfont=dict(color=ui.INK_SOFT, size=12),
                hovertemplate="%{x}<br>%{y}<extra></extra>",
            )
        )
        fig.update_layout(
            title=t("stats_class_dist"),
            yaxis_title=t("count_axis"),
            yaxis_range=[0, float(counts.max()) * 1.25],
            bargap=0.35,
            height=330,
            showlegend=False,
        )
        ui.chart(fig)

    # How the mixes people test compare with the training population
    dataset = data.load_dataset("with_temp")
    ratios = []
    for feature in config.FEATURES:
        used = pd.to_numeric(log[feature.column], errors="coerce").dropna()
        if used.empty:
            continue
        reference = float(dataset[feature.column].mean())
        if reference == 0:
            continue
        ratios.append(
            {
                "label": feature.label,
                "ratio": float(used.mean()) / reference,
                "user_mean": float(used.mean()),
                "dataset_mean": reference,
            }
        )

    if ratios:
        ratio_frame = pd.DataFrame(ratios).sort_values("ratio")
        fig = go.Figure(
            go.Bar(
                x=ratio_frame["ratio"] - 1,
                y=ratio_frame["label"],
                orientation="h",
                base=1,
                marker=dict(
                    color=[
                        ui.SERIES[0] if value >= 1 else ui.SERIES[7]
                        for value in ratio_frame["ratio"]
                    ],
                    line=dict(width=0),
                ),
                customdata=np.stack(
                    [ratio_frame["user_mean"], ratio_frame["dataset_mean"]], axis=-1
                ),
                hovertemplate=(
                    "%{y}<br>users: %{customdata[0]:.1f}"
                    "<br>dataset: %{customdata[1]:.1f}<extra></extra>"
                ),
            )
        )
        fig.add_vline(x=1, line_width=1.5, line_color=ui.BORDER)
        fig.update_layout(
            title=t("stats_input_profile"),
            xaxis_title="user mean ÷ dataset mean",
            bargap=0.35,
            height=110 + 44 * len(ratio_frame),
            showlegend=False,
        )
        ui.chart(fig)
        st.caption(t("stats_input_note"))

# ---------------------------------------------------------------------------
# Real-world accuracy
# ---------------------------------------------------------------------------
with tab_accuracy:
    measured = usage.measured(log)
    if measured.empty:
        st.info(t("stats_accuracy_empty"))
    else:
        tolerance = st.slider(
            f"{t('stats_tolerance')} ({t('mpa')})",
            min_value=1.0,
            max_value=15.0,
            value=5.0,
            step=0.5,
            key="stats_tolerance_value",
        )
        correct = int((measured["abs_error"] <= tolerance).sum())
        incorrect = int(len(measured) - correct)
        bias = float(measured["error"].mean())

        k1, k2, k3, k4 = st.columns(4)
        k1.metric(t("stats_correct"), f"{correct:,}")
        k2.metric(t("stats_incorrect"), f"{incorrect:,}")
        k3.metric(t("stats_hit_rate"), f"{correct / len(measured) * 100:.0f}%")
        interval_rows = measured["in_interval"].dropna()
        k4.metric(
            t("stats_interval_hit"),
            f"{interval_rows.mean() * 100:.0f}%" if not interval_rows.empty else "—",
        )

        m1, m2, m3 = st.columns(3)
        m1.metric(t("stats_live_mae"), f"{measured['abs_error'].mean():.2f} {t('mpa')}")
        m2.metric(
            t("stats_live_rmse"),
            f"{np.sqrt((measured['error'] ** 2).mean()):.2f} {t('mpa')}",
        )
        m3.metric(t("stats_live_bias"), f"{bias:+.2f} {t('mpa')}")

        if abs(bias) < 1.0:
            st.info(t("stats_bias_note_none"))
        elif bias > 0:
            st.info(t("stats_bias_note_over"))
        else:
            st.info(t("stats_bias_note_under"))

        left, right = st.columns([3, 2])
        with left:
            low = float(min(measured["actual"].min(), measured["prediction"].min())) - 3
            high = float(max(measured["actual"].max(), measured["prediction"].max())) + 3
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=[low, high],
                    y=[low, high],
                    mode="lines",
                    line=dict(color=ui.BORDER, width=2),
                    hoverinfo="skip",
                    showlegend=False,
                )
            )
            within = measured["abs_error"] <= tolerance
            for name, mask, colour in (
                (t("stats_correct"), within, ui.STATUS["good"]),
                (t("stats_incorrect"), ~within, ui.STATUS["critical"]),
            ):
                subset = measured[mask]
                if subset.empty:
                    continue
                fig.add_trace(
                    go.Scatter(
                        x=subset["actual"],
                        y=subset["prediction"],
                        mode="markers",
                        name=name,
                        marker=dict(
                            color=colour, size=10,
                            line=dict(width=2, color=ui.SURFACE),
                        ),
                        hovertemplate="measured %{x:.1f}<br>predicted %{y:.1f}<extra></extra>",
                    )
                )
            fig.update_layout(
                title=t("stats_actual_vs_pred"),
                xaxis_title=f"measured ({t('mpa')})",
                yaxis_title=f"predicted ({t('mpa')})",
                height=420,
            )
            ui.chart(fig)

        with right:
            fig = go.Figure(
                go.Histogram(
                    x=measured["error"],
                    nbinsx=min(24, max(6, len(measured))),
                    marker=dict(color=ui.SERIES[0], line=dict(width=0)),
                    hovertemplate="%{x:.1f} MPa<br>%{y}<extra></extra>",
                )
            )
            fig.add_vline(x=0, line_width=2, line_color=ui.SERIES[1])
            fig.update_layout(
                title=t("stats_error_hist"),
                xaxis_title=f"predicted − measured ({t('mpa')})",
                yaxis_title=t("count_axis"),
                bargap=0.05,
                height=420,
            )
            ui.chart(fig)

# ---------------------------------------------------------------------------
# Raw log
# ---------------------------------------------------------------------------
with tab_log:
    st.caption(t("stats_log_note"))

    display = log.sort_values("timestamp", ascending=False).copy()
    display["timestamp"] = display["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
    display["model"] = display["model_key"].map(model_name)
    columns = [
        "timestamp", "model", "source", "prediction", "lower", "upper",
        "strength_class", "extrapolated", "actual", "n_rows",
    ]
    st.dataframe(
        display[columns].round(2), width="stretch", hide_index=True, height=420
    )

    left, right = st.columns([1, 1])
    with left:
        st.download_button(
            f"⬇️ {t('stats_download_log')}",
            data=log.to_csv(index=False).encode("utf-8-sig"),
            file_name="usage_log.csv",
            mime="text/csv",
        )
    with right:
        with st.popover(f"🗑️ {t('stats_clear')}"):
            if st.button(t("stats_clear_confirm"), type="primary", key="confirm_clear"):
                usage.clear()
                st.success(t("stats_cleared"))
                st.rerun()
