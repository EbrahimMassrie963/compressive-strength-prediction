"""Model performance: held-out evaluation, leaderboards and diagnostics."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src import config, data, models, ui
from src.strings import t


ui.page_head(t("nav_performance"), t("perf_title"), t("perf_intro"))

with st.spinner(t("loading")):
    scores = models.evaluate_all()

tab_live, tab_boards, tab_diag, tab_stability = st.tabs(
    [t("perf_tab_live"), t("perf_tab_leaderboard"), t("perf_tab_diag"), t("perf_tab_stability")]
)


def model_name(key: str) -> str:
    spec = config.MODELS_BY_KEY[key]
    family_tag = "9F" if spec.family == "with_temp" else "8F"
    return f"{spec.name} · {family_tag}"


# ---------------------------------------------------------------------------
# Live evaluation
# ---------------------------------------------------------------------------
with tab_live:
    st.caption(t("perf_live_intro"))

    table = scores.copy()
    table.insert(0, "model", table["key"].map(model_name))
    display = table[["model", "r2", "rmse", "mae", "mape", "within_5"]].rename(
        columns={
            "model": t("model_label"),
            "r2": t("perf_metric_r2"),
            "rmse": t("perf_metric_rmse"),
            "mae": t("perf_metric_mae"),
            "mape": t("perf_metric_mape"),
            "within_5": t("perf_within5"),
        }
    )
    st.dataframe(display.round(3), width="stretch", hide_index=True)

    st.write("")
    ordered = scores.sort_values("r2")
    fig = go.Figure(
        go.Bar(
            x=ordered["r2"],
            y=[model_name(key) for key in ordered["key"]],
            orientation="h",
            marker=dict(
                color=[
                    ui.SERIES[0] if champion else ui.NEUTRAL_MARK
                    for champion in ordered["is_champion"]
                ],
                line=dict(width=0),
            ),
            text=[f"{value:.3f}" for value in ordered["r2"]],
            textposition="outside",
            textfont=dict(color=ui.INK_SOFT, size=12),
            hovertemplate="%{y}<br>R² = %{x:.4f}<extra></extra>",
        )
    )
    fig.update_layout(
        title=f"{t('perf_metric_r2')} — {t('perf_tab_live')}",
        xaxis_range=[0.8, 1.0],
        bargap=0.4,
        height=110 + 48 * len(ordered),
        showlegend=False,
    )
    ui.chart(fig)

    best = scores.iloc[0]
    worst = scores.iloc[-1]
    ui.explain(
        t("what_live_r2"),
        t("insight_live_r2").format(
            best=model_name(best["key"]),
            r2=f"{best['r2']:.3f}",
            rmse=f"{best['rmse']:.2f}",
            spread=f"{best['r2'] - worst['r2']:.3f}",
            within=f"{best['within_5']:.0f}",
        ),
    )

    st.markdown("---")
    st.markdown(f"**{t('perf_select_model')}**")
    selected_key = st.selectbox(
        t("perf_select_model"),
        options=scores["key"].tolist(),
        format_func=model_name,
        label_visibility="collapsed",
        key="perf_model",
    )
    frame = models.test_predictions(selected_key)

    left, right = st.columns([3, 2])
    with left:
        limits = [
            float(min(frame["actual"].min(), frame["predicted"].min())) - 3,
            float(max(frame["actual"].max(), frame["predicted"].max())) + 3,
        ]
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=limits,
                y=limits,
                mode="lines",
                line=dict(color=ui.BORDER, width=2),
                name="perfect",
                hoverinfo="skip",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=frame["actual"],
                y=frame["predicted"],
                mode="markers",
                marker=dict(
                    color=ui.SERIES[0], size=7, opacity=0.72,
                    line=dict(width=1, color=ui.SURFACE),
                ),
                name=t("perf_pred_vs_actual"),
                hovertemplate="actual %{x:.1f}<br>predicted %{y:.1f}<extra></extra>",
            )
        )
        fig.update_layout(
            title=t("perf_pred_vs_actual"),
            xaxis_title=f"actual ({t('mpa')})",
            yaxis_title=f"predicted ({t('mpa')})",
            height=440,
            showlegend=False,
        )
        ui.chart(fig)

    with right:
        fig = go.Figure(
            go.Histogram(
                x=frame["residual"],
                nbinsx=30,
                marker=dict(color=ui.SERIES[0], line=dict(width=0)),
                hovertemplate="%{x:.1f} MPa<br>%{y}<extra></extra>",
            )
        )
        fig.add_vline(x=0, line_width=2, line_color=ui.SERIES[1])
        fig.update_layout(
            title=t("perf_residuals"),
            xaxis_title=f"actual − predicted ({t('mpa')})",
            yaxis_title=t("count_axis"),
            bargap=0.05,
            height=440,
        )
        ui.chart(fig)

    fig = go.Figure(
        go.Scatter(
            x=frame["predicted"],
            y=frame["residual"],
            mode="markers",
            marker=dict(
                color=ui.SERIES[0], size=7, opacity=0.72,
                line=dict(width=1, color=ui.SURFACE),
            ),
            hovertemplate="predicted %{x:.1f}<br>residual %{y:+.1f}<extra></extra>",
        )
    )
    fig.add_hline(y=0, line_width=2, line_color=ui.BORDER)
    fig.update_layout(
        title=t("perf_residual_vs_pred"),
        xaxis_title=f"predicted ({t('mpa')})",
        yaxis_title=f"residual ({t('mpa')})",
        height=360,
        showlegend=False,
    )
    ui.chart(fig)

    selected_row = scores[scores["key"] == selected_key].iloc[0]
    bias = float(frame["residual"].mean())
    ui.explain(
        t("what_pred_actual") + " " + t("what_resid_vs_pred"),
        t("insight_residuals").format(
            model=model_name(selected_key),
            mae=f"{selected_row['mae']:.2f}",
            within=f"{selected_row['within_5']:.0f}",
            bias=f"{bias:+.2f}",
            direction=t("bias_under") if bias > 0.2
            else t("bias_over") if bias < -0.2 else t("bias_none"),
            worst=f"{frame['abs_error'].max():.1f}",
        ),
    )

    # --- Interval calibration -------------------------------------------
    st.markdown("---")
    st.markdown(f"**{t('perf_interval_title')}**")
    interval_columns = st.columns(len(config.FAMILIES))
    for column, family in zip(interval_columns, config.FAMILIES):
        settings = models.interval_settings(family)
        if not settings:
            continue
        with column:
            st.caption(
                config.FAMILIES[family]["label"]
            )
            c1, c2, c3 = st.columns(3)
            c1.metric(t("perf_interval_target"), f"{settings['target_coverage'] * 100:.0f}%")
            c2.metric(t("perf_interval_actual"), f"{settings['empirical_coverage'] * 100:.1f}%")
            c3.metric(
                t("perf_interval_width"),
                f"{settings['mean_interval_width_mpa']:.1f} {t('mpa')}",
            )

# ---------------------------------------------------------------------------
# Research leaderboards
# ---------------------------------------------------------------------------
with tab_boards:
    metadata = data.load_artifact("model_metadata.json")

    cv_board = pd.DataFrame(metadata.get("cv_leaderboard", []))
    if not cv_board.empty:
        cv_board = cv_board.sort_values("cv_r2_mean")
        fig = go.Figure(
            go.Bar(
                x=cv_board["cv_r2_mean"],
                y=cv_board["model"],
                orientation="h",
                error_x=dict(
                    type="data", array=cv_board["cv_r2_std"],
                    color=ui.INK_MUTED, thickness=1.2, width=4,
                ),
                marker=dict(color=ui.SERIES[0], line=dict(width=0)),
                hovertemplate="%{y}<br>R² = %{x:.4f}<extra></extra>",
            )
        )
        fig.update_layout(
            title=t("perf_cv_leaderboard"),
            xaxis_title=f"{t('perf_metric_r2')} (5-fold CV ± std)",
            xaxis_range=[0, 1.0],
            bargap=0.35,
            height=520,
            showlegend=False,
        )
        ui.chart(fig)
        top_row = cv_board.iloc[-1]
        linear = cv_board[cv_board["model"].str.contains("Linear")]
        ui.explain(
            t("what_cv_board"),
            t("insight_cv_board").format(
                best=top_row["model"],
                r2=f"{top_row['cv_r2_mean']:.3f}",
                linear=f"{linear['cv_r2_mean'].iloc[0]:.3f}" if not linear.empty else "0.60",
                n=len(cv_board),
            ),
        )

    tuned = pd.DataFrame(metadata.get("tuned_test_leaderboard", []))
    if not tuned.empty:
        st.markdown(f"**{t('perf_tuned_leaderboard')}**")
        st.dataframe(tuned.round(4), width="stretch", hide_index=True)

    full = data.load_report_csv("full_model_comparison.csv")
    if not full.empty:
        st.markdown(f"**{t('perf_full_comparison')}**")
        st.dataframe(full.round(4), width="stretch", hide_index=True, height=360)

# ---------------------------------------------------------------------------
# Error diagnostics
# ---------------------------------------------------------------------------
with tab_diag:
    curve = data.load_report_csv("learning_curve.csv")
    if not curve.empty:
        fig = go.Figure()
        for name, column, colour in (
            ("training", "train_r2_mean", ui.SERIES[0]),
            ("validation", "val_r2_mean", ui.SERIES[1]),
        ):
            fig.add_trace(
                go.Scatter(
                    x=curve["train_size"],
                    y=curve[column],
                    mode="lines+markers",
                    name=name,
                    line=dict(color=colour, width=2),
                    marker=dict(size=8, line=dict(width=1, color=ui.SURFACE)),
                    hovertemplate=f"{name}<br>n = %{{x}}<br>R² = %{{y:.3f}}<extra></extra>",
                )
            )
        fig.update_layout(
            title=t("perf_learning_curve"),
            xaxis_title="training samples",
            yaxis_title=t("perf_metric_r2"),
            yaxis_range=[0, 1.05],
            height=400,
        )
        ui.chart(fig)
        final_gap = float(curve["train_r2_mean"].iloc[-1] - curve["val_r2_mean"].iloc[-1])
        last_gain = float(curve["val_r2_mean"].iloc[-1] - curve["val_r2_mean"].iloc[-2])
        ui.explain(
            t("what_learning"),
            t("insight_learning").format(
                gap=f"{final_gap:.3f}",
                gain=f"{last_gain:.4f}",
                verdict=t("learning_more_helps") if last_gain > 0.002
                else t("learning_plateau"),
            ),
        )
        st.info(t("perf_learning_note"))

    ranges = data.load_report_csv("error_by_strength_range_summary.csv")
    if not ranges.empty:
        st.markdown("---")
        fig = go.Figure()
        for name, column, colour in (
            ("MAE", "mae", ui.SERIES[0]),
            ("RMSE", "rmse", ui.SERIES[1]),
        ):
            fig.add_trace(
                go.Bar(
                    x=ranges["Strength Range"],
                    y=ranges[column],
                    name=name,
                    marker=dict(color=colour, line=dict(width=0)),
                    hovertemplate=f"%{{x}}<br>{name} = %{{y:.2f}} MPa<extra></extra>",
                )
            )
        fig.update_layout(
            title=t("perf_error_by_range"),
            yaxis_title=t("mpa"),
            barmode="group",
            bargap=0.4,
            bargroupgap=0.08,
            height=380,
        )
        ui.chart(fig)

        bias = go.Figure(
            go.Bar(
                x=ranges["Strength Range"],
                y=ranges["mean_error"],
                marker=dict(
                    color=[
                        ui.POSITIVE if value >= 0 else ui.NEGATIVE
                        for value in ranges["mean_error"]
                    ],
                    line=dict(width=0),
                ),
                text=[f"{value:+.2f}" for value in ranges["mean_error"]],
                textposition="outside",
                textfont=dict(color=ui.INK_SOFT, size=12),
                hovertemplate="%{x}<br>mean error %{y:+.2f} MPa<extra></extra>",
            )
        )
        bias.add_hline(y=0, line_width=1, line_color=ui.BORDER)
        bias.update_layout(
            title="Mean signed error (actual − predicted)",
            yaxis_title=t("mpa"),
            bargap=0.5,
            height=340,
            showlegend=False,
        )
        ui.chart(bias)
        worst_row = ranges.loc[ranges["rmse"].idxmax()]
        best_row = ranges.loc[ranges["rmse"].idxmin()]
        ui.explain(
            t("what_error_range") + " " + t("what_bias_range"),
            t("insight_error_range").format(
                worst=worst_row["Strength Range"],
                worst_rmse=f"{worst_row['rmse']:.2f}",
                best=best_row["Strength Range"],
                best_rmse=f"{best_row['rmse']:.2f}",
                bias=f"{worst_row['mean_error']:+.2f}",
                direction=t("bias_under") if worst_row["mean_error"] > 0 else t("bias_over"),
            ),
        )
        st.info(t("perf_error_range_note"))

    worst = data.load_report_csv("top_worst_predictions.csv")
    if not worst.empty:
        st.markdown("---")
        st.markdown(f"**{t('perf_worst')}**")
        columns = [c for c in worst.columns if "MPa" in c or "Error" in c]
        st.dataframe(
            worst[columns].round(2).head(10), width="stretch", hide_index=True
        )

# ---------------------------------------------------------------------------
# Stability & significance
# ---------------------------------------------------------------------------
with tab_stability:
    robustness = data.load_artifact("robustness_summary.json")
    if robustness:
        k1, k2, k3 = st.columns(3)
        k1.metric(t("perf_robust_mean"), f"{robustness['mean_r2']:.4f}")
        k2.metric(t("perf_robust_cv"), f"{robustness['coefficient_of_variation'] * 100:.2f}%")
        k3.metric(
            t("perf_robust_range"),
            f"{robustness['min_r2']:.3f} – {robustness['max_r2']:.3f}",
        )

        low, high = robustness["95_percent_ci"]
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=[robustness["min_r2"], robustness["max_r2"]],
                y=[1, 1],
                mode="lines",
                line=dict(color=ui.BORDER, width=6),
                name="fold range",
                hoverinfo="skip",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[low, high],
                y=[1, 1],
                mode="lines",
                line=dict(color=ui.SERIES[0], width=14),
                name="95% CI",
                hovertemplate="%{x:.4f}<extra></extra>",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[robustness["mean_r2"]],
                y=[1],
                mode="markers+text",
                marker=dict(color=ui.SERIES[1], size=14, line=dict(width=2, color=ui.SURFACE)),
                text=[f"{robustness['mean_r2']:.4f}"],
                textposition="top center",
                textfont=dict(color=ui.INK, size=12),
                name="mean",
                hovertemplate="mean R² %{x:.4f}<extra></extra>",
            )
        )
        fig.update_layout(
            title=f"{t('perf_robustness')} ({robustness['n_folds']} folds)",
            xaxis_title=t("perf_metric_r2"),
            height=230,
            yaxis=dict(visible=False, range=[0.85, 1.25]),
        )
        ui.chart(fig)
        ui.explain(
            t("what_robustness"),
            t("insight_robustness").format(
                mean=f"{robustness['mean_r2']:.3f}",
                cv=f"{robustness['coefficient_of_variation'] * 100:.1f}",
                low=f"{robustness['min_r2']:.3f}",
                high=f"{robustness['max_r2']:.3f}",
                verdict=t("stability_high")
                if robustness["coefficient_of_variation"] < 0.05
                else t("stability_low"),
            ),
        )

    significance = data.load_report_csv("statistical_significance_tests.csv")
    if not significance.empty:
        st.markdown("---")
        st.markdown(f"**{t('perf_significance')}**")

        fig = go.Figure(
            go.Bar(
                x=significance["mean_difference"],
                y=significance["competitor"],
                orientation="h",
                marker=dict(
                    color=[
                        ui.STATUS["good"] if flag else ui.NEUTRAL_MARK
                        for flag in significance["significant_at_0.05"]
                    ],
                    line=dict(width=0),
                ),
                text=[
                    f"{value:+.4f}  (p = {p:.3g})"
                    for value, p in zip(
                        significance["mean_difference"], significance["paired_ttest_p"]
                    )
                ],
                textposition="outside",
                textfont=dict(color=ui.INK_SOFT, size=12),
                hovertemplate="%{y}<br>ΔR² = %{x:+.4f}<extra></extra>",
            )
        )
        span = float(np.abs(significance["mean_difference"]).max()) * 2.6
        fig.add_vline(x=0, line_width=1, line_color=ui.BORDER)
        fig.update_layout(
            title="Champion mean R² − competitor mean R² (50 paired folds)",
            xaxis_title="ΔR²",
            xaxis_range=[-span, span],
            bargap=0.5,
            height=300,
            showlegend=False,
        )
        ui.chart(fig)

        ui.explain(
            t("what_significance"),
            t("insight_significance").format(
                beaten=int(significance["significant_at_0.05"].sum()),
                total=len(significance),
                tied=", ".join(
                    significance.loc[~significance["significant_at_0.05"], "competitor"]
                )
                or t("none_word"),
            ),
        )
        st.dataframe(
            significance.round(5), width="stretch", hide_index=True
        )
        st.info(t("perf_significance_note"))

    outliers = data.load_report_csv("outlier_removal_comparison.csv")
    if not outliers.empty:
        st.markdown("---")
        st.dataframe(outliers.round(4), width="stretch", hide_index=True)
