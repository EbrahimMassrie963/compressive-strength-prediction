"""Exploratory data analysis of the dataset the models learned from."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src import config, data, ui
from src.strings import t


ui.page_head(t("nav_data"), t("data_title"), t("data_intro"))

df = data.load_dataset("with_temp")
feature_columns = [c for c in df.columns if c != config.TARGET_COL]
target = df[config.TARGET_COL]


def label(column: str) -> str:
    return data.short_label(column)


tab_overview, tab_dist, tab_rel, tab_corr, tab_figures = st.tabs(
    [
        t("data_tab_overview"),
        t("data_tab_dist"),
        t("data_tab_rel"),
        t("data_tab_corr"),
        t("data_tab_figures"),
    ]
)

# ---------------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------------
with tab_overview:
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric(t("data_rows"), f"{len(df):,}")
    k2.metric(t("data_cols"), f"{df.shape[1]}")
    k3.metric(t("data_missing"), f"{int(df.isna().sum().sum())}")
    k4.metric(t("data_duplicates"), f"{int(df.duplicated().sum())}")
    k5.metric(t("data_target_mean"), f"{target.mean():.1f} {t('mpa')}")
    k6.metric(t("data_target_range"), f"{target.min():.0f} – {target.max():.0f}")

    st.write("")
    fig = go.Figure(
        go.Histogram(
            x=target,
            nbinsx=45,
            marker=dict(color=ui.SERIES[0], line=dict(width=0)),
            hovertemplate="%{x:.0f} MPa<br>%{y} samples<extra></extra>",
        )
    )
    fig.add_vline(
        x=float(target.mean()),
        line_width=2,
        line_color=ui.SERIES[1],
        annotation_text=f"mean {target.mean():.1f}",
        annotation_position="top right",
        annotation_font_color=ui.SERIES[1],
    )
    fig.update_layout(
        title=f"{label(config.TARGET_COL)} ({t('mpa')})",
        yaxis_title=t("samples_axis"),
        bargap=0.04,
        height=360,
    )
    ui.chart(fig)
    high_share = float((target > 60).mean() * 100)
    ui.explain(
        t("what_target_hist"),
        t("insight_target_hist").format(
            mean=f"{target.mean():.1f}",
            median=f"{target.median():.1f}",
            low=f"{target.min():.1f}",
            high=f"{target.max():.1f}",
            share=f"{high_share:.1f}",
        ),
    )

    st.markdown(f"**{t('data_summary_title')}**")
    summary = df.describe().T[["mean", "std", "min", "25%", "50%", "75%", "max"]]
    summary.index = [label(c) for c in summary.index]
    st.dataframe(summary.round(2), width="stretch")

    st.markdown(f"**{t('data_preview_title')}**")
    preview = df.head(12).copy()
    preview.columns = [label(c) for c in preview.columns]
    st.dataframe(preview.round(2), width="stretch", hide_index=True)

# ---------------------------------------------------------------------------
# Distributions
# ---------------------------------------------------------------------------
with tab_dist:
    variable = st.selectbox(
        t("data_select_var"),
        options=feature_columns + [config.TARGET_COL],
        format_func=label,
        key="dist_variable",
    )
    series = df[variable]

    left, right = st.columns([2, 1])
    with left:
        fig = go.Figure(
            go.Histogram(
                x=series,
                nbinsx=45,
                marker=dict(color=ui.SERIES[0], line=dict(width=0)),
                hovertemplate="%{x}<br>%{y} samples<extra></extra>",
            )
        )
        fig.update_layout(
            title=t("data_hist_title"),
            xaxis_title=label(variable),
            yaxis_title=t("samples_axis"),
            bargap=0.04,
            height=380,
        )
        ui.chart(fig)

    with right:
        fig = go.Figure(
            go.Box(
                y=series,
                name=label(variable),
                marker=dict(color=ui.SERIES[0], size=4),
                line=dict(width=1.5),
                boxpoints="outliers",
                hovertemplate="%{y}<extra></extra>",
            )
        )
        fig.update_layout(
            title=t("data_box_title"),
            showlegend=False,
            height=380,
            yaxis_title=label(variable),
        )
        ui.chart(fig)

    zero_share = float((series == 0).mean() * 100)
    ui.explain(
        t("what_var_hist"),
        t("insight_var_hist").format(
            name=label(variable),
            median=f"{series.median():,.1f}",
            low=f"{series.min():,.1f}",
            high=f"{series.max():,.1f}",
            zeros=f"{zero_share:.0f}",
            note=t("insight_var_zeros") if zero_share > 20 else t("insight_var_nozeros"),
        ),
    )

    stats_row = series.describe()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("mean", f"{stats_row['mean']:.2f}")
    c2.metric("std", f"{stats_row['std']:.2f}")
    c3.metric("min", f"{stats_row['min']:.2f}")
    c4.metric("max", f"{stats_row['max']:.2f}")

# ---------------------------------------------------------------------------
# Relationships
# ---------------------------------------------------------------------------
with tab_rel:
    control_1, control_2, control_3 = st.columns([2, 2, 1])
    with control_1:
        x_column = st.selectbox(
            t("data_select_var"), options=feature_columns, format_func=label, key="rel_x"
        )
    with control_2:
        colour_column = st.selectbox(
            t("data_colour_by"),
            options=[None] + feature_columns,
            format_func=lambda c: "—" if c is None else label(c),
            key="rel_colour",
        )
    with control_3:
        st.write("")
        show_trend = st.checkbox(t("data_trendline"), value=True, key="rel_trend")

    marker = dict(size=6, line=dict(width=1, color=ui.SURFACE))
    if colour_column is None:
        marker["color"] = ui.SERIES[0]
        marker["opacity"] = 0.7
    else:
        marker.update(
            color=df[colour_column],
            colorscale=ui.sequential_scale(),
            showscale=True,
            colorbar=dict(
                title=dict(text=label(colour_column), font=dict(size=11)),
                thickness=12,
                outlinewidth=0,
                len=0.8,
            ),
        )

    fig = go.Figure(
        go.Scatter(
            x=df[x_column],
            y=target,
            mode="markers",
            marker=marker,
            name=label(config.TARGET_COL),
            hovertemplate=f"{label(x_column)}: %{{x}}<br>{t('mpa')}: %{{y:.1f}}<extra></extra>",
        )
    )

    if show_trend:
        order = np.argsort(df[x_column].to_numpy())
        x_sorted = df[x_column].to_numpy()[order]
        coefficients = np.polyfit(df[x_column], target, 2)
        fig.add_trace(
            go.Scatter(
                x=x_sorted,
                y=np.polyval(coefficients, x_sorted),
                mode="lines",
                line=dict(color=ui.SERIES[1], width=2),
                name="trend",
                hoverinfo="skip",
            )
        )

    correlation = float(df[x_column].corr(target))
    fig.update_layout(
        title=f"{t('data_scatter_title')} — r = {correlation:+.3f}",
        xaxis_title=label(x_column),
        yaxis_title=f"{label(config.TARGET_COL)} ({t('mpa')})",
        height=460,
        showlegend=show_trend,
    )
    ui.chart(fig)

    strength = (
        t("corr_strength_strong") if abs(correlation) >= 0.4
        else t("corr_strength_moderate") if abs(correlation) >= 0.2
        else t("corr_strength_weak")
    )
    ui.explain(
        t("what_scatter"),
        t("insight_scatter").format(
            name=label(x_column),
            r=f"{correlation:+.3f}",
            strength=strength,
            direction=t("direction_up") if correlation >= 0 else t("direction_down"),
        ),
    )

    # Temperature bands, the check that the synthetic feature behaves as designed
    st.markdown(f"**{t('data_temp_band_title')}**")
    bands = pd.cut(
        df[config.TEMPERATURE],
        bins=[20, 26, 31, 36, 45.01],
        labels=["20–26 °C", "26–31 °C", "31–36 °C", "36–45 °C"],
        right=False,
    )
    band_means = target.groupby(bands, observed=False).mean()
    fig = go.Figure(
        go.Bar(
            x=band_means.index.astype(str),
            y=band_means.to_numpy(),
            marker=dict(color=ui.SERIES[0], line=dict(width=0)),
            text=[f"{v:.1f}" for v in band_means],
            textposition="outside",
            textfont=dict(color=ui.INK_SOFT, size=12),
            hovertemplate="%{x}<br>%{y:.2f} MPa<extra></extra>",
        )
    )
    fig.update_layout(
        yaxis_title=f"{t('data_target_mean')} ({t('mpa')})",
        bargap=0.45,
        height=330,
        yaxis_range=[0, band_means.max() * 1.2],
    )
    ui.chart(fig)
    ui.explain(
        t("what_temp_bands"),
        t("insight_temp_bands").format(
            hottest=f"{band_means.iloc[-1]:.1f}",
            coolest=f"{band_means.iloc[0]:.1f}",
            drop=f"{band_means.iloc[0] - band_means.iloc[-1]:.1f}",
            pct=f"{(1 - band_means.iloc[-1] / band_means.iloc[0]) * 100:.0f}",
        ),
    )

# ---------------------------------------------------------------------------
# Correlation
# ---------------------------------------------------------------------------
with tab_corr:
    corr = df.corr()
    labels = [label(c) for c in corr.columns]

    fig = go.Figure(
        go.Heatmap(
            z=corr.to_numpy(),
            x=labels,
            y=labels,
            zmin=-1,
            zmax=1,
            colorscale=ui.DIVERGING,
            xgap=2,
            ygap=2,
            colorbar=dict(thickness=12, outlinewidth=0, len=0.8),
            hovertemplate="%{y} ↔ %{x}<br>r = %{z:.2f}<extra></extra>",
        )
    )
    fig.update_layout(title=t("data_corr_title"), height=560)
    fig.update_xaxes(tickangle=-35, showgrid=False)
    fig.update_yaxes(showgrid=False, autorange="reversed")
    ui.chart(fig)

    off_diagonal = corr.where(~np.eye(len(corr), dtype=bool))
    strongest_pair = off_diagonal.abs().stack().idxmax()
    strongest_value = float(corr.loc[strongest_pair[0], strongest_pair[1]])
    ui.explain(
        t("what_corr_matrix"),
        t("insight_corr_matrix").format(
            a=label(strongest_pair[0]),
            b=label(strongest_pair[1]),
            r=f"{strongest_value:+.2f}",
        ),
    )

    target_corr = (
        corr[config.TARGET_COL].drop(config.TARGET_COL).sort_values()
    )
    fig = go.Figure(
        go.Bar(
            x=target_corr.to_numpy(),
            y=[label(c) for c in target_corr.index],
            orientation="h",
            marker=dict(
                color=[ui.POSITIVE if v >= 0 else ui.NEGATIVE for v in target_corr],
                line=dict(width=0),
            ),
            text=[f"{v:+.2f}" for v in target_corr],
            textposition="outside",
            textfont=dict(color=ui.INK_SOFT, size=12),
            hovertemplate="%{y}<br>r = %{x:+.3f}<extra></extra>",
        )
    )
    fig.update_layout(
        title=t("data_corr_target"),
        xaxis_title="Pearson r",
        xaxis_range=[-0.65, 0.65],
        bargap=0.35,
        height=420,
        showlegend=False,
    )
    fig.add_vline(x=0, line_width=1, line_color=ui.BORDER)
    ui.chart(fig)

    ui.explain(
        t("what_corr_target"),
        t("insight_corr_target").format(
            top=label(target_corr.abs().idxmax()),
            r=f"{target_corr[target_corr.abs().idxmax()]:+.2f}",
            positive=", ".join(label(c) for c in target_corr[target_corr > 0].index[-2:]),
            negative=", ".join(label(c) for c in target_corr[target_corr < 0].index[:2]),
        ),
    )
    st.info(t("data_corr_note"))

# ---------------------------------------------------------------------------
# Research figures
# ---------------------------------------------------------------------------
with tab_figures:
    st.caption(t("data_figures_intro"))
    groups = data.figure_groups()
    if not groups:
        st.info("No figures were bundled with this deployment.")
    else:
        group = st.selectbox(
            t("data_figure_group"),
            options=list(groups),
            format_func=lambda name: name.upper(),
            key="figure_group",
        )
        for image in groups[group]:
            st.markdown(f"**{data.prettify_figure_name(image)}**")
            st.image(str(image), width="stretch")
            st.write("")
