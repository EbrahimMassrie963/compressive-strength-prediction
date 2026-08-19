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
family_keys = list(config.FAMILIES)
family = st.radio(
    t("family_label"),
    options=family_keys,
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
        format_func=lambda s: ui.model_label(s),
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


def _preset_values(name: str) -> dict[str, float]:
    medians = {column: float(stats.loc[column, "median"]) for column in stats.index}
    presets = {
        "preset_median": medians,
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
    return presets.get(name, medians)


def _slider_bounds(feature: config.Feature) -> tuple[float, float]:
    """Training range, widened slightly so extrapolation is possible but visible."""
    low = float(stats.loc[feature.column, "min"])
    high = float(stats.loc[feature.column, "max"])
    span = high - low
    return (max(0.0, low - 0.1 * span), high + 0.1 * span)


def _apply_preset(name: str) -> None:
    for column, value in _preset_values(name).items():
        feature = config.FEATURES_BY_COLUMN[column]
        low, high = _slider_bounds(feature)
        st.session_state[f"in_{feature.key}"] = float(min(max(value, low), high))


# Seed the widgets on first visit.
if "predict_initialised" not in st.session_state:
    _apply_preset("preset_median")
    st.session_state["predict_initialised"] = True

st.subheader(t("inputs_title"))

preset_options = ["preset_custom", "preset_median", "preset_standard", "preset_high", "preset_eco"]
preset_col, spacer = st.columns([1, 2])
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
        st.markdown(f"**{t(group_key)}**")
        for feature_key in feature_keys:
            feature = config.FEATURES_BY_KEY[feature_key]
            if feature not in active_features:
                continue
            low, high = _slider_bounds(feature)
            values[feature.column] = st.slider(
                f"{feature.icon} {feature.label} ({feature.unit})",
                min_value=round(low, feature.decimals),
                max_value=round(high, feature.decimals),
                step=feature.step,
                key=f"in_{feature.key}",
                help=feature.help_text,
                format=f"%.{feature.decimals}f",
            )

# The temperature slider is hidden for the 8-feature family, but its session
# value is kept so switching families does not lose the user's setting.
full_values = dict(values)
for feature in config.FEATURES:
    full_values.setdefault(feature.column, float(st.session_state.get(f"in_{feature.key}", 0.0)))

# ---------------------------------------------------------------------------
# Derived indicators + sanity checks
# ---------------------------------------------------------------------------
st.write("")
indicators = models.derived_indicators(full_values)

st.markdown(f"**{t('derived_title')}**")
d1, d2, d3, d4, d5 = st.columns(5)
d1.metric(t("wc_ratio"), f"{indicators['wc_ratio']:.2f}")
d2.metric(t("wb_ratio"), f"{indicators['wb_ratio']:.2f}")
d3.metric(t("total_binder"), f"{indicators['total_binder']:.0f} kg/m³")
d4.metric(t("agg_ratio"), f"{indicators['agg_ratio']:.2f}")
d5.metric(t("total_mass"), f"{indicators['total_mass']:.0f} kg/m³")

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
run = st.button(f"🔮 {t('predict_button')}", type="primary", width="content")

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
        strength_class=config.strength_class(prediction)[0],
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
    }

result = st.session_state.get("last_prediction")
if result and result["model_key"] == spec.key:
    st.markdown("---")
    if result["values"] != values:
        st.caption(f"⚠️ {t('result_stale')}")

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

    st.write("")
    tab_sensitivity, tab_compare, tab_position = st.tabs(
        [t("sensitivity_title"), t("compare_title"), t("position_title")]
    )

    # --- Local sensitivity ------------------------------------------------
    with tab_sensitivity:
        st.caption(t("sensitivity_intro"))
        sensitivity = models.local_sensitivity(spec, values)
        sensitivity["label"] = sensitivity["column"].map(lambda c: ui.feature_label(c))
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
            height=max(320, 46 * len(order)),
        )
        fig.add_vline(x=0, line_width=1, line_color=ui.BORDER)
        ui.chart(fig)

    # --- Cross-model comparison ------------------------------------------
    with tab_compare:
        st.caption(t("compare_intro"))
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
                        ui.SERIES[0] if selected else "#c9c7c2"
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
        spread = comparison["prediction"].max() - comparison["prediction"].min()
        fig.update_layout(
            height=90 + 52 * len(comparison),
            xaxis_title=f"{t('result_title')} ({t('mpa')})",
            bargap=0.45,
            showlegend=False,
        )
        fig.update_xaxes(range=[0, comparison["prediction"].max() * 1.18])
        ui.chart(fig)
        st.caption(f"{t('compare_spread')}: {spread:.2f} {t('mpa')}")

    # --- Position within the training data -------------------------------
    with tab_position:
        st.caption(t("position_intro"))
        training = data.load_dataset(family)

        percentiles = []
        for feature in active_features:
            column_values = training[feature.column]
            percentile = float((column_values <= values[feature.column]).mean() * 100)
            percentiles.append(
                {"label": feature.label, "percentile": percentile}
            )
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
        fig.update_layout(
            height=90 + 46 * len(percentile_frame),
            xaxis_title=t("percentile_axis"),
            xaxis_range=[0, 112],
            bargap=0.4,
            showlegend=False,
        )
        ui.chart(fig)

        focus = st.selectbox(
            t("data_select_var"),
            options=[f.column for f in active_features],
            format_func=lambda c: ui.feature_label(c),
            key="position_focus",
        )
        hist = go.Figure(
            go.Histogram(
                x=training[focus],
                nbinsx=40,
                marker=dict(color=ui.SERIES[0], line=dict(width=0)),
                opacity=0.85,
                hovertemplate="%{x}<br>%{y} samples<extra></extra>",
            )
        )
        hist.add_vline(
            x=values[focus],
            line_width=2,
            line_color=ui.SERIES[1],
            annotation_text=f"{values[focus]:.1f}",
            annotation_position="top",
            annotation_font_color=ui.SERIES[1],
        )
        hist.update_layout(
            height=320,
            xaxis_title=ui.feature_label(focus),
            yaxis_title=t("samples_axis"),
            bargap=0.04,
        )
        ui.chart(hist)

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
