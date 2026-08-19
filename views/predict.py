"""Single-mix prediction: the page the whole application exists for."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src import config, data, models, ui, usage
from src.strings import t

ui.page_head(t("nav_predict"), t("predict_title"), t("predict_intro"))

# ---------------------------------------------------------------------------
# Model choice
# ---------------------------------------------------------------------------
family = st.radio(
    t("family_label"),
    options=list(config.FAMILIES),
    format_func=lambda key: config.FAMILIES[key]["label"],
    horizontal=True,
    key="predict_family",
)

candidates = models.available_models(family)
if not candidates:
    st.error(t("no_models"))
    st.stop()

col_model, col_origin = st.columns([1, 2])
with col_model:
    spec = st.selectbox(
        t("model_label"),
        options=candidates,
        format_func=ui.model_label,
        key=f"predict_model_{family}",
    )
with col_origin:
    st.markdown(f"**{t('model_origin')}**")
    st.caption(spec.origin)

active_features = [f for f in config.FEATURES if f.column in spec.columns]

st.markdown("---")

# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------
stats = data.feature_stats("with_temp")


def _training_range(feature: config.Feature) -> tuple[float, float]:
    return (
        float(stats.loc[feature.column, "min"]),
        float(stats.loc[feature.column, "max"]),
    )


def _input_bounds(feature: config.Feature) -> tuple[float, float]:
    """Typing limits, deliberately wider than the training range.

    A user may legitimately want to score an unusual mix; it is the
    extrapolation warning, not the widget, that tells them it is unusual.
    """
    _, high = _training_range(feature)
    return 0.0, round(high * 2.5, feature.decimals)


PRESETS = {
    "preset_standard": {
        config.CEMENT: 300.0, config.SLAG: 0.0, config.FLY_ASH: 0.0,
        config.WATER: 180.0, config.SUPERPLASTICIZER: 5.0,
        config.COARSE_AGG: 1000.0, config.FINE_AGG: 780.0,
        config.AGE: 28.0, config.TEMPERATURE: 23.0,
    },
    "preset_high": {
        config.CEMENT: 500.0, config.SLAG: 100.0, config.FLY_ASH: 0.0,
        config.WATER: 150.0, config.SUPERPLASTICIZER: 14.0,
        config.COARSE_AGG: 1000.0, config.FINE_AGG: 700.0,
        config.AGE: 28.0, config.TEMPERATURE: 22.0,
    },
    "preset_eco": {
        config.CEMENT: 200.0, config.SLAG: 150.0, config.FLY_ASH: 100.0,
        config.WATER: 175.0, config.SUPERPLASTICIZER: 8.0,
        config.COARSE_AGG: 950.0, config.FINE_AGG: 780.0,
        config.AGE: 56.0, config.TEMPERATURE: 25.0,
    },
}


def _preset_values(name: str) -> dict[str, float]:
    if name in PRESETS:
        return PRESETS[name]
    return {column: float(stats.loc[column, "median"]) for column in stats.index}


def _apply_preset(name: str) -> None:
    for column, value in _preset_values(name).items():
        feature = config.FEATURES_BY_COLUMN[column]
        low, high = _input_bounds(feature)
        st.session_state[f"in_{feature.key}"] = float(min(max(value, low), high))


if "predict_initialised" not in st.session_state:
    _apply_preset("preset_median")
    st.session_state["predict_initialised"] = True

st.subheader(t("inputs_title"))

preset_options = [
    "preset_custom", "preset_median", "preset_standard", "preset_high", "preset_eco",
]
preset_col, _ = st.columns([1, 2])
with preset_col:
    preset = st.selectbox(
        t("preset_label"), options=preset_options, format_func=t, key="predict_preset"
    )
if preset != "preset_custom" and st.session_state.get("_applied_preset") != preset:
    _apply_preset(preset)
    st.session_state["_applied_preset"] = preset
    st.rerun()
if preset == "preset_custom":
    st.session_state["_applied_preset"] = None

GROUPS = (
    ("binder_group", ("cement", "slag", "fly_ash")),
    ("water_group", ("water", "superplasticizer")),
    ("aggregate_group", ("coarse_agg", "fine_agg")),
    ("curing_group", ("age", "temperature")),
)

values: dict[str, float] = {}
group_columns = st.columns(len(GROUPS))
for column, (group_key, feature_keys) in zip(group_columns, GROUPS):
    with column:
        ui.group_title(t(group_key))
        for feature_key in feature_keys:
            feature = config.FEATURES_BY_KEY[feature_key]
            if feature not in active_features:
                continue
            low, high = _input_bounds(feature)
            value = float(
                st.number_input(
                    f"{feature.icon}  {feature.label} ({feature.unit})",
                    min_value=low,
                    max_value=high,
                    step=feature.step,
                    format=f"%.{feature.decimals}f",
                    key=f"in_{feature.key}",
                    help=feature.help_text,
                )
            )
            values[feature.column] = value

            train_low, train_high = _training_range(feature)
            outside = value < train_low or value > train_high
            ui.range_hint(
                f"{t('training_range')} {train_low:,.0f} – {train_high:,.0f}"
                + (f" · {t('outside_range_short')}" if outside else ""),
                out_of_range=outside,
            )

# The temperature input is hidden for the 8-feature family, but its session
# value is kept so switching families does not lose the user's setting.
full_values = dict(values)
for feature in config.FEATURES:
    full_values.setdefault(feature.column, float(st.session_state.get(f"in_{feature.key}", 0.0)))

# ---------------------------------------------------------------------------
# Derived indicators + sanity checks
# ---------------------------------------------------------------------------
indicators = models.derived_indicators(full_values)

st.markdown(f"**{t('derived_title')}**")
d1, d2, d3, d4, d5 = st.columns(5)
d1.metric(t("wc_ratio"), f"{indicators['wc_ratio']:.3f}")
d2.metric(t("wb_ratio"), f"{indicators['wb_ratio']:.3f}")
d3.metric(t("total_binder"), f"{indicators['total_binder']:.0f} kg/m³")
d4.metric(t("agg_ratio"), f"{indicators['agg_ratio']:.2f}")
d5.metric(t("total_mass"), f"{indicators['total_mass']:.0f} kg/m³")

wc = indicators["wc_ratio"]
if wc < 0.40:
    wc_verdict = t("wc_verdict_excellent")
elif wc < 0.50:
    wc_verdict = t("wc_verdict_good")
elif wc < 0.60:
    wc_verdict = t("wc_verdict_moderate")
else:
    wc_verdict = t("wc_verdict_weak")

ui.explain(
    t("what_derived"),
    t("insight_derived").format(
        wc=f"{wc:.3f}",
        verdict=wc_verdict,
        binder=f"{indicators['total_binder']:.0f}",
        mass=f"{indicators['total_mass']:.0f}",
    ),
)

flagged = models.out_of_range(values, family)
if flagged:
    lines = "".join(
        f"<li>{ui.feature_label(column)}: <strong>{value:,.1f}</strong> "
        f"(training range {low:,.1f} – {high:,.1f})</li>"
        for column, value, low, high in flagged
    )
    st.warning(f"**{t('range_warning_title')}** — {t('range_warning_body')}")
    st.markdown(f"<ul>{lines}</ul>", unsafe_allow_html=True)

if indicators["wc_ratio"] > 0.9:
    st.info(t("wc_warning"))
if not 2200 <= indicators["total_mass"] <= 2600:
    st.info(t("mass_warning"))

st.write("")
run = st.button(f"⚡  {t('predict_button')}", type="primary", width="content")

# ---------------------------------------------------------------------------
# Prediction
# ---------------------------------------------------------------------------
if run:
    frame = models.to_frame(values, spec.columns)
    point, lower, upper = models.predict_with_interval(spec, frame)
    prediction = float(point[0])
    class_name, class_note = config.strength_class(prediction)

    record_id = usage.record(
        source="single",
        model_key=spec.key,
        family=family,
        prediction=prediction,
        lower=float(lower[0]),
        upper=float(upper[0]),
        strength_class=class_name,
        extrapolated=bool(flagged),
        values=values,
    )

    st.session_state["last_prediction"] = {
        "record_id": record_id,
        "model_key": spec.key,
        "family": family,
        "values": dict(values),
        "prediction": prediction,
        "lower": float(lower[0]),
        "upper": float(upper[0]),
        "class_name": class_name,
        "class_note": class_note,
        "extrapolated": bool(flagged),
    }

result = st.session_state.get("last_prediction")
if result and result["model_key"] == spec.key:
    st.markdown("---")
    if result["values"] != values:
        st.caption(f"⚠️ {t('result_stale')}")

    interval_width = result["upper"] - result["lower"]

    left, right = st.columns([1, 1])
    with left:
        ui.result_card(
            result["prediction"],
            t("mpa"),
            t("result_title"),
            f"{t('result_model_used')}: {spec.name}",
        )
        st.write("")
        m1, m2 = st.columns(2)
        m1.metric(t("result_class"), result["class_name"], help=result["class_note"])
        m2.metric(
            t("result_interval"),
            f"{result['lower']:.1f} – {result['upper']:.1f}",
            help=t("result_interval_help"),
        )
    with right:
        ui.chart(ui.gauge(result["prediction"], result["lower"], result["upper"]))

    gauge_insight = t("insight_gauge").format(
        value=f"{result['prediction']:.1f}",
        cls=result["class_name"],
        note=result["class_note"].lower(),
        width=f"{interval_width:.1f}",
        low=f"{result['lower']:.1f}",
        high=f"{result['upper']:.1f}",
    )
    if result["extrapolated"]:
        gauge_insight += " " + t("insight_gauge_extrapolated")
    ui.explain(t("what_gauge"), gauge_insight)

    tab_sensitivity, tab_compare, tab_position = st.tabs(
        [t("sensitivity_title"), t("compare_title"), t("position_title")]
    )

    # --- Local sensitivity ------------------------------------------------
    with tab_sensitivity:
        sensitivity = models.local_sensitivity(spec, values)
        sensitivity["label"] = sensitivity["column"].map(ui.feature_label)
        order = (
            sensitivity.groupby("label")["delta"]
            .apply(lambda s: s.abs().max())
            .sort_values()
            .index.tolist()
        )

        fig = go.Figure()
        for series_name, direction, colour in (
            (t("sensitivity_up"), "up", ui.SERIES[0]),
            (t("sensitivity_down"), "down", ui.SERIES[1]),
        ):
            subset = sensitivity[sensitivity["direction"] == direction].set_index("label")
            subset = subset.reindex(order)
            fig.add_trace(
                go.Bar(
                    y=subset.index,
                    x=subset["delta"],
                    name=series_name,
                    orientation="h",
                    marker=dict(color=colour, line=dict(width=0)),
                    hovertemplate="%{y}<br>%{x:+.2f} MPa<extra>" + series_name + "</extra>",
                )
            )
        fig.update_layout(
            barmode="group",
            bargap=0.35,
            bargroupgap=0.08,
            xaxis_title=t("sensitivity_delta"),
            height=max(320, 48 * len(order)),
        )
        fig.add_vline(x=0, line_width=1, line_color=ui.BORDER)
        ui.chart(fig)

        strongest = sensitivity.loc[sensitivity["delta"].abs().idxmax()]
        up_rows = sensitivity[sensitivity["direction"] == "up"]
        helpers = [ui.feature_label(r.column) for r in up_rows.itertuples() if r.delta > 0.05]
        hurters = [ui.feature_label(r.column) for r in up_rows.itertuples() if r.delta < -0.05]

        # A tree ensemble only reacts where it placed a split, so an input can
        # legitimately show no bar at all. Saying so stops that reading as a bug.
        inert = [
            ui.feature_label(column)
            for column, group in sensitivity.groupby("column")
            if group["delta"].abs().max() < 0.01
        ]
        insight = t("insight_sensitivity").format(
            top=ui.feature_label(strongest["column"]),
            delta=f"{abs(strongest['delta']):.2f}",
            helpers=", ".join(helpers[:3]) if helpers else t("none_word"),
            hurters=", ".join(hurters[:3]) if hurters else t("none_word"),
        )
        if inert:
            insight += " " + t("insight_sensitivity_inert").format(
                inert=", ".join(inert[:3])
            )
        ui.explain(t("what_sensitivity"), insight)

    # --- Cross-model comparison ------------------------------------------
    with tab_compare:
        comparison = []
        for candidate in candidates:
            candidate_pred = float(
                models.predict(candidate, models.to_frame(values, candidate.columns))[0]
            )
            comparison.append(
                {
                    "model": candidate.name,
                    "prediction": candidate_pred,
                    "selected": candidate.key == spec.key,
                }
            )
        comparison = pd.DataFrame(comparison).sort_values("prediction")

        fig = go.Figure(
            go.Bar(
                x=comparison["prediction"],
                y=comparison["model"],
                orientation="h",
                marker=dict(
                    color=[
                        ui.SERIES[0] if selected else ui.NEUTRAL_MARK
                        for selected in comparison["selected"]
                    ],
                    line=dict(width=0),
                ),
                text=[f"{value:.1f}" for value in comparison["prediction"]],
                textposition="outside",
                textfont=dict(color=ui.INK_SOFT, size=12),
                hovertemplate="%{y}<br>%{x:.2f} MPa<extra></extra>",
            )
        )
        spread = float(comparison["prediction"].max() - comparison["prediction"].min())
        fig.update_layout(
            height=100 + 54 * len(comparison),
            xaxis_title=f"{t('result_title')} ({t('mpa')})",
            xaxis_range=[0, float(comparison["prediction"].max()) * 1.18],
            bargap=0.45,
            showlegend=False,
        )
        ui.chart(fig)

        if spread <= 3:
            verdict = t("compare_verdict_tight")
        elif spread > 7:
            verdict = t("compare_verdict_wide")
        else:
            verdict = t("compare_verdict_normal")
        ui.explain(
            t("what_compare"),
            t("insight_compare").format(
                n=len(comparison),
                spread=f"{spread:.1f}",
                low=f"{comparison['prediction'].min():.1f}",
                high=f"{comparison['prediction'].max():.1f}",
                verdict=verdict,
            ),
        )

    # --- Position within the training data -------------------------------
    with tab_position:
        training = data.load_dataset(family)

        percentiles = []
        for feature in active_features:
            column_values = training[feature.column]
            percentile = float((column_values <= values[feature.column]).mean() * 100)
            percentiles.append({"label": feature.label, "percentile": percentile})
        percentile_frame = pd.DataFrame(percentiles).sort_values("percentile")

        fig = go.Figure(
            go.Bar(
                x=percentile_frame["percentile"],
                y=percentile_frame["label"],
                orientation="h",
                marker=dict(color=ui.SERIES[0], line=dict(width=0)),
                text=[f"{value:.0f}%" for value in percentile_frame["percentile"]],
                textposition="outside",
                textfont=dict(color=ui.INK_SOFT, size=12),
                hovertemplate="%{y}<br>percentile %{x:.0f}<extra></extra>",
            )
        )
        fig.add_vline(x=50, line_width=1, line_color=ui.BORDER)
        fig.update_layout(
            height=100 + 46 * len(percentile_frame),
            xaxis_title=t("percentile_axis"),
            xaxis_range=[0, 112],
            bargap=0.4,
            showlegend=False,
        )
        ui.chart(fig)

        extreme = percentile_frame.iloc[
            (percentile_frame["percentile"] - 50).abs().argmax()
        ]
        edge_count = int(
            ((percentile_frame["percentile"] <= 5) | (percentile_frame["percentile"] >= 95)).sum()
        )
        above = extreme["percentile"] >= 50
        ui.explain(
            t("what_percentile"),
            t("insight_percentile").format(
                feature=extreme["label"],
                percentile=f"{extreme['percentile']:.0f}",
                comparison=t("higher_than") if above else t("lower_than"),
                other=f"{extreme['percentile'] if above else 100 - extreme['percentile']:.0f}",
                edges=edge_count,
            ),
        )

        focus = st.selectbox(
            t("data_select_var"),
            options=[f.column for f in active_features],
            format_func=ui.feature_label,
            key="position_focus",
        )
        hist = go.Figure(
            go.Histogram(
                x=training[focus],
                nbinsx=40,
                marker=dict(color=ui.SERIES[1], line=dict(width=0)),
                hovertemplate="%{x}<br>%{y} samples<extra></extra>",
            )
        )
        hist.add_vline(
            x=values[focus],
            line_width=2,
            line_color=ui.ACCENT,
            annotation_text=f"{values[focus]:.1f}",
            annotation_position="top",
            annotation_font_color=ui.ACCENT,
        )
        hist.update_layout(
            height=330,
            xaxis_title=ui.feature_label(focus),
            yaxis_title=t("samples_axis"),
            bargap=0.04,
        )
        ui.chart(hist)

        focus_values = training[focus]
        tolerance = max(abs(values[focus]) * 0.1, float(focus_values.std()) * 0.1)
        nearby = int(((focus_values - values[focus]).abs() <= tolerance).sum())
        ui.explain(
            t("what_position_hist"),
            t("insight_position_hist").format(
                feature=ui.feature_label(focus),
                value=f"{values[focus]:,.1f}",
                nearby=nearby,
                total=len(training),
                verdict=t("evidence_thin") if nearby < 30 else t("evidence_solid"),
            ),
        )

    # --- Ground-truth feedback -------------------------------------------
    st.markdown("---")
    with st.expander(f"🧪 {t('feedback_title')}"):
        st.caption(t("feedback_intro"))
        fb_left, fb_right = st.columns([1, 1])
        with fb_left:
            measured = st.number_input(
                t("feedback_input"),
                min_value=0.0,
                max_value=150.0,
                value=float(round(result["prediction"], 1)),
                step=0.5,
                key="feedback_value",
            )
        with fb_right:
            st.write("")
            st.write("")
            if st.button(t("feedback_save"), key="feedback_save_button"):
                if usage.add_measurement(result["record_id"], measured):
                    st.success(t("feedback_saved"))
                    st.metric(
                        t("feedback_error"),
                        f"{abs(measured - result['prediction']):.2f} {t('mpa')}",
                    )
