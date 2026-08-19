"""Explainability: what the models learned, and how much you can trust that."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from src import config, data, models, ui
from src.strings import t


ui.page_head(t("nav_explain"), t("explain_title"), t("explain_intro"))


def label(column: str) -> str:
    return data.short_label(column)


tab_importance, tab_shap, tab_agreement, tab_effects = st.tabs(
    [
        t("explain_tab_importance"),
        t("explain_tab_shap"),
        t("explain_tab_agreement"),
        t("explain_tab_effects"),
    ]
)

# ---------------------------------------------------------------------------
# Built-in importance + ablation
# ---------------------------------------------------------------------------
with tab_importance:
    st.markdown(f"**{t('explain_builtin_title')}**")
    st.caption(t("explain_builtin_note"))

    all_specs = [
        spec
        for family in config.FAMILIES
        for spec in models.available_models(family)
    ]
    spec = st.selectbox(
        t("perf_select_model"),
        options=all_specs,
        format_func=lambda s: f"{ui.model_label(s)} · {len(s.columns)}F",
        key="explain_model",
    )

    importance = models.builtin_importance(spec.key)
    if importance.empty:
        st.info("This model does not expose feature importances.")
    else:
        importance = importance.sort_values("importance")
        fig = go.Figure(
            go.Bar(
                x=importance["importance"],
                y=[label(column) for column in importance["column"]],
                orientation="h",
                marker=dict(color=ui.SERIES[0], line=dict(width=0)),
                text=[f"{value:.1%}" for value in importance["importance"]],
                textposition="outside",
                textfont=dict(color=ui.INK_SOFT, size=12),
                hovertemplate="%{y}<br>%{x:.2%}<extra></extra>",
            )
        )
        fig.update_layout(
            xaxis_title="share of total importance",
            xaxis_tickformat=".0%",
            xaxis_range=[0, float(importance["importance"].max()) * 1.25],
            bargap=0.35,
            height=110 + 44 * len(importance),
            showlegend=False,
        )
        ui.chart(fig)

        ranked = importance.sort_values("importance", ascending=False)
        ui.explain(
            t("what_builtin"),
            t("insight_builtin").format(
                model=spec.name,
                top=label(ranked.iloc[0]["column"]),
                share=f"{ranked.iloc[0]['importance']:.0%}",
                top3=", ".join(label(c) for c in ranked["column"].head(3)),
                top3share=f"{ranked['importance'].head(3).sum():.0%}",
                least=label(ranked.iloc[-1]["column"]),
            ),
        )

    ablation = data.load_report_csv("feature_ablation_results.csv")
    if not ablation.empty:
        st.markdown("---")
        st.markdown(f"**{t('explain_ablation_title')}**")
        st.caption(t("explain_ablation_note"))

        ablation = ablation.sort_values("r2_drop")
        fig = go.Figure(
            go.Bar(
                x=ablation["r2_drop"],
                y=[label(column) for column in ablation["feature_removed"]],
                orientation="h",
                marker=dict(color=ui.SERIES[0], line=dict(width=0)),
                text=[f"{value:.3f}" for value in ablation["r2_drop"]],
                textposition="outside",
                textfont=dict(color=ui.INK_SOFT, size=12),
                hovertemplate="%{y}<br>R² drop %{x:.4f}<extra></extra>",
            )
        )
        fig.update_layout(
            xaxis_title="R² lost when the feature is removed",
            xaxis_range=[0, float(ablation["r2_drop"].max()) * 1.25],
            bargap=0.35,
            height=110 + 44 * len(ablation),
            showlegend=False,
        )
        ui.chart(fig)

        worst = ablation.iloc[-1]
        mildest = ablation.iloc[0]
        ui.explain(
            t("what_ablation"),
            t("insight_ablation").format(
                top=label(worst["feature_removed"]),
                drop=f"{worst['r2_drop']:.3f}",
                remaining=f"{worst['r2_without_feature']:.3f}",
                least=label(mildest["feature_removed"]),
                least_drop=f"{mildest['r2_drop']:.4f}",
            ),
        )

# ---------------------------------------------------------------------------
# SHAP
# ---------------------------------------------------------------------------
with tab_shap:
    st.caption(t("explain_shap_note"))

    shap_table = data.load_report_csv("shap_vs_builtin_importance.csv")
    if not shap_table.empty:
        shap_table = shap_table.rename(columns={shap_table.columns[0]: "feature"})
        shap_table = shap_table.sort_values("shap_mean_abs")
        fig = go.Figure(
            go.Bar(
                x=shap_table["shap_mean_abs"],
                y=[label(column) for column in shap_table["feature"]],
                orientation="h",
                marker=dict(color=ui.SERIES[0], line=dict(width=0)),
                text=[f"{value:.2f}" for value in shap_table["shap_mean_abs"]],
                textposition="outside",
                textfont=dict(color=ui.INK_SOFT, size=12),
                hovertemplate="%{y}<br>mean |SHAP| = %{x:.2f} MPa<extra></extra>",
            )
        )
        fig.update_layout(
            title="Mean absolute SHAP value",
            xaxis_title=f"average impact on the prediction ({t('mpa')})",
            xaxis_range=[0, float(shap_table["shap_mean_abs"].max()) * 1.22],
            bargap=0.35,
            height=110 + 44 * len(shap_table),
            showlegend=False,
        )
        ui.chart(fig)

        ranked_shap = shap_table.sort_values("shap_mean_abs", ascending=False)
        ui.explain(
            t("what_shap"),
            t("insight_shap").format(
                top=label(ranked_shap.iloc[0]["feature"]),
                mpa=f"{ranked_shap.iloc[0]['shap_mean_abs']:.2f}",
                second=label(ranked_shap.iloc[1]["feature"]),
                second_mpa=f"{ranked_shap.iloc[1]['shap_mean_abs']:.2f}",
            ),
        )

    figures = data.figure_groups().get("advanced", [])
    shap_figures = [path for path in figures if "shap" in path.stem.lower()]
    for image in shap_figures:
        st.markdown(f"**{data.prettify_figure_name(image)}**")
        st.image(str(image), width="stretch")
        st.write("")

# ---------------------------------------------------------------------------
# Method agreement
# ---------------------------------------------------------------------------
with tab_agreement:
    st.caption(t("explain_agreement_note"))

    comparison = data.load_report_csv("importance_three_way_comparison.csv")
    if not comparison.empty:
        normalised = comparison.copy()
        method_columns = ["permutation", "shap", "ablation_r2_drop"]
        for column in method_columns:
            total = normalised[column].abs().max()
            normalised[column] = normalised[column] / total if total else 0.0
        normalised = normalised.sort_values("shap")

        names = {
            "permutation": "Permutation",
            "shap": "SHAP",
            "ablation_r2_drop": "Ablation",
        }
        fig = go.Figure()
        for index, column in enumerate(method_columns):
            fig.add_trace(
                go.Bar(
                    x=normalised[column],
                    y=[label(feature) for feature in normalised["feature"]],
                    name=names[column],
                    orientation="h",
                    marker=dict(color=ui.SERIES[index], line=dict(width=0)),
                    hovertemplate=f"%{{y}}<br>{names[column]}: %{{x:.2f}}<extra></extra>",
                )
            )
        fig.update_layout(
            title="Importance by method, each scaled to its own maximum",
            xaxis_title="relative importance",
            barmode="group",
            bargap=0.3,
            bargroupgap=0.06,
            height=140 + 62 * len(normalised),
        )
        ui.chart(fig)

        leaders = {
            name: label(comparison.loc[comparison[column].idxmax(), "feature"])
            for column, name in names.items()
        }
        agreed = len(set(leaders.values())) == 1
        ui.explain(
            t("what_agreement"),
            t("insight_agreement").format(
                verdict=t("agreement_yes").format(feature=next(iter(leaders.values())))
                if agreed
                else t("agreement_no"),
                detail=" · ".join(f"{k}: {v}" for k, v in leaders.items()),
            ),
        )

    summary = data.load_artifact("notebook5_summary.json")
    agreement = summary.get("importance_method_agreement", {})
    if agreement:
        pairs = [
            ("Permutation ↔ SHAP", agreement.get("spearman_perm_vs_shap")),
            ("Permutation ↔ Ablation", agreement.get("spearman_perm_vs_ablation")),
            ("SHAP ↔ Ablation", agreement.get("spearman_shap_vs_ablation")),
        ]
        columns = st.columns(3)
        for column, (name, value) in zip(columns, pairs):
            column.metric(name, f"ρ = {value:.2f}" if value is not None else "—")

# ---------------------------------------------------------------------------
# Effect explorer
# ---------------------------------------------------------------------------
with tab_effects:
    st.caption(t("explain_effects_intro"))

    control_1, control_2 = st.columns([1, 1])
    with control_1:
        family = st.radio(
            t("family_label"),
            options=list(config.FAMILIES),
            format_func=lambda key: config.FAMILIES[key]["label"],
            horizontal=True,
            key="effects_family",
        )
    candidates = models.available_models(family)
    with control_2:
        effect_spec = st.selectbox(
            t("model_label"),
            options=candidates,
            format_func=lambda s: ui.model_label(s),
            key=f"effects_model_{family}",
        )

    stats = data.feature_stats("with_temp")
    last = st.session_state.get("last_prediction")
    baseline_options = ["explain_baseline_median"]
    if last is not None:
        baseline_options.append("explain_baseline_last")
    baseline_choice = st.radio(
        t("explain_baseline"),
        options=baseline_options,
        format_func=t,
        horizontal=True,
        key="effects_baseline",
    )

    baseline = {column: float(stats.loc[column, "median"]) for column in stats.index}
    if baseline_choice == "explain_baseline_last" and last is not None:
        baseline.update(last["values"])

    sweep_column = st.selectbox(
        t("explain_sweep_feature"),
        options=effect_spec.columns,
        format_func=label,
        index=0,
        key="effects_sweep",
    )

    grid = np.linspace(
        float(stats.loc[sweep_column, "min"]),
        float(stats.loc[sweep_column, "max"]),
        60,
    )
    curve = models.sweep(effect_spec, baseline, sweep_column, grid)

    fig = go.Figure(
        go.Scatter(
            x=grid,
            y=curve,
            mode="lines",
            line=dict(color=ui.SERIES[0], width=2.5),
            hovertemplate=f"{label(sweep_column)}: %{{x:.1f}}<br>%{{y:.1f}} MPa<extra></extra>",
        )
    )
    fig.add_vline(
        x=baseline[sweep_column],
        line_width=2,
        line_color=ui.SERIES[1],
        annotation_text=t("explain_baseline"),
        annotation_position="top",
        annotation_font_color=ui.SERIES[1],
    )
    fig.update_layout(
        title=t("explain_sweep_title"),
        xaxis_title=f"{label(sweep_column)}",
        yaxis_title=f"{t('result_title')} ({t('mpa')})",
        height=400,
        showlegend=False,
    )
    ui.chart(fig)

    swing = float(curve.max() - curve.min())
    best_at = float(grid[int(curve.argmax())])
    ui.explain(
        t("what_sweep"),
        t("insight_sweep").format(
            feature=label(sweep_column),
            swing=f"{swing:.1f}",
            low=f"{curve.min():.1f}",
            high=f"{curve.max():.1f}",
            best=f"{best_at:,.0f}",
            shape=t("sweep_monotone")
            if abs(best_at - float(grid[-1])) < (float(grid[-1]) - float(grid[0])) * 0.05
            else t("sweep_peak"),
        ),
    )

    st.markdown("---")
    st.markdown(f"**{t('explain_2d_title')}**")
    st.caption(t("explain_2d_intro"))

    axis_1, axis_2 = st.columns(2)
    with axis_1:
        x_column = st.selectbox(
            t("explain_x_axis"),
            options=effect_spec.columns,
            index=0,
            format_func=label,
            key="effects_x",
        )
    with axis_2:
        remaining = [c for c in effect_spec.columns if c != x_column]
        default_index = remaining.index(config.AGE) if config.AGE in remaining else 0
        y_column = st.selectbox(
            t("explain_y_axis"),
            options=remaining,
            index=default_index,
            format_func=label,
            key="effects_y",
        )

    x_grid = np.linspace(
        float(stats.loc[x_column, "min"]), float(stats.loc[x_column, "max"]), 40
    )
    y_grid = np.linspace(
        float(stats.loc[y_column, "min"]), float(stats.loc[y_column, "max"]), 40
    )
    surface = models.sweep_2d(effect_spec, baseline, x_column, x_grid, y_column, y_grid)

    fig = go.Figure(
        go.Heatmap(
            z=surface,
            x=x_grid,
            y=y_grid,
            colorscale=ui.sequential_scale(),
            colorbar=dict(
                title=dict(text=t("mpa"), font=dict(size=11)),
                thickness=12, outlinewidth=0, len=0.85,
            ),
            hovertemplate=(
                f"{label(x_column)}: %{{x:.0f}}<br>"
                f"{label(y_column)}: %{{y:.0f}}<br>%{{z:.1f}} MPa<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        xaxis_title=label(x_column),
        yaxis_title=label(y_column),
        height=480,
    )
    ui.chart(fig)

    best_index = np.unravel_index(int(np.argmax(surface)), surface.shape)
    ui.explain(
        t("what_surface"),
        t("insight_surface").format(
            x=label(x_column),
            y=label(y_column),
            low=f"{surface.min():.1f}",
            high=f"{surface.max():.1f}",
            best_x=f"{x_grid[best_index[1]]:,.0f}",
            best_y=f"{y_grid[best_index[0]]:,.0f}",
        ),
    )
