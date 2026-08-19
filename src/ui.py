"""Shared presentation layer: dark theme, Plotly defaults and reusable blocks."""

from __future__ import annotations

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

from src import config
from src.strings import t

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
# Chart series. Assigned in this fixed order and never cycled. Validated for
# the dark chart surface (#18222e) with the data-viz palette validator:
# lightness band, chroma floor, adjacent-pair CVD separation, normal-vision
# floor and contrast all pass. The first three additionally pass the stricter
# all-pairs gate, which is why no chart in this app plots more than three
# series at once.
SERIES = (
    "#00AD83",  # 1 teal — the brand hue
    "#3987E5",  # 2 blue
    "#C98500",  # 3 amber
    "#9085E9",  # 4 violet
    "#E66767",  # 5 red
    "#008300",  # 6 green
)

# Single-hue ramp for magnitude (heatmaps, ordered bands), dark -> bright.
SEQUENTIAL_TEAL = [
    "#12352f", "#17594a", "#1a6b58", "#1a8872",
    "#00AD83", "#35c39c", "#6ed7bb", "#a9e9d7",
]

# The ordinal subset, validated separately: monotone lightness, visible step
# gaps, and a dark end that still reads against the surface.
ORDINAL_TEAL = ["#1a6b58", "#1a8872", "#00AD83", "#35c39c", "#6ed7bb", "#a9e9d7"]

# Polarity, used wherever a value is signed: red for negative, blue for
# positive, and a neutral (uncoloured) midpoint that reads as "nothing". Warm
# against cool, so the poles read as opposites and stay distinguishable under
# red-green colour blindness — which a teal/red pair would not.
DIVERGING = [
    [0.0, "#a32f2f"], [0.25, "#E66767"], [0.5, "#2a3644"],
    [0.75, "#3987E5"], [1.0, "#1b4f8f"],
]
POSITIVE = "#3987E5"
NEGATIVE = "#E66767"

# Reserved for state, never reused as a series colour.
STATUS = {
    "good": "#0ca30c",
    "warning": "#fab219",
    "serious": "#ec835a",
    "critical": "#d03b3b",
}

# Interface chrome. Brighter than the series steps because it carries text and
# controls rather than adjacent data marks.
ACCENT = "#00d9a3"
ACCENT_BLUE = "#3b9ef5"
ACCENT_VIOLET = "#b06bf5"
ACCENT_AMBER = "#f5a623"

BG = "#0f1720"
SURFACE = "#18222e"
SURFACE_2 = "#1f2b39"
BORDER = "#2a3949"
INK = "#e8eef5"
INK_SOFT = "#a7b6c6"
INK_MUTED = "#74869a"
GRID = "#243140"

NEUTRAL_MARK = "#4c5f73"  # de-emphasised bars in an emphasis chart


# ---------------------------------------------------------------------------
# Plotly
# ---------------------------------------------------------------------------
def register_plotly_theme() -> None:
    """A recessive, hairline chart template used by every figure in the app."""
    axis = dict(
        gridcolor=GRID, gridwidth=1, griddash="solid", zeroline=False,
        linecolor=BORDER, linewidth=1, ticks="outside", ticklen=4,
        tickcolor=BORDER, tickfont=dict(size=12, color=INK_MUTED),
        title=dict(font=dict(size=12, color=INK_MUTED)),
        automargin=True,
    )

    template = go.layout.Template()
    template.layout = go.Layout(
        colorway=list(SERIES),
        font=dict(
            family="Inter, 'Segoe UI', system-ui, sans-serif",
            size=13,
            color=INK_SOFT,
        ),
        title=dict(
            font=dict(size=15, color=INK),
            x=0, xanchor="left", y=1, yanchor="top", pad=dict(b=10),
        ),
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        margin=dict(l=8, r=8, t=48, b=8),
        xaxis=axis,
        yaxis=axis,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0,
            font=dict(size=12, color=INK_SOFT), bgcolor="rgba(0,0,0,0)",
            title=dict(text=""),
        ),
        hoverlabel=dict(
            bgcolor=SURFACE_2, bordercolor=BORDER,
            font=dict(size=12, color=INK, family="Inter, 'Segoe UI', sans-serif"),
        ),
        colorscale=dict(
            sequential=[[i / (len(SEQUENTIAL_TEAL) - 1), c]
                        for i, c in enumerate(SEQUENTIAL_TEAL)],
            diverging=DIVERGING,
        ),
        separators=".,",
    )
    pio.templates["concrete_dark"] = template
    pio.templates.default = "concrete_dark"


def sequential_scale() -> list[list]:
    """The single-hue magnitude ramp in Plotly's colorscale form."""
    return [
        [i / (len(SEQUENTIAL_TEAL) - 1), colour]
        for i, colour in enumerate(SEQUENTIAL_TEAL)
    ]


def _has_colour_scale(fig: go.Figure) -> bool:
    """True when the figure draws a colour bar outside the plotting area."""
    for trace in fig.data:
        if trace.type in ("heatmap", "contour", "surface"):
            if getattr(trace, "showscale", None) is not False:
                return True
        marker = getattr(trace, "marker", None)
        if marker is not None and getattr(marker, "showscale", False):
            return True
    return False


def chart(fig: go.Figure, height: int | None = None, key: str | None = None) -> None:
    """Render a Plotly figure, reserving room for whatever chrome it carries.

    Plotly anchors the title and a top legend to the same edge, so a figure
    that has both will overlap unless the top margin grows to hold them. That
    is computed here rather than hand-tuned per chart.
    """
    if height is not None:
        fig.update_layout(height=height)

    has_title = bool(fig.layout.title.text)
    named_traces = sum(
        1 for trace in fig.data
        if getattr(trace, "name", None) and getattr(trace, "showlegend", None) is not False
    )
    shows_legend = fig.layout.showlegend is not False and named_traces >= 2

    top = 16
    if has_title:
        top += 34
    if shows_legend:
        top += 32

    # A colour bar lives outside the plotting area and is clipped to nothing
    # unless the right margin makes room for it.
    right = 84 if _has_colour_scale(fig) else 8

    fig.update_layout(
        margin=dict(l=8, r=right, t=top, b=8),
        showlegend=shows_legend,
    )
    if shows_legend and has_title:
        # Title on the first line, legend tucked directly beneath it.
        fig.update_layout(legend=dict(y=1.0, yanchor="bottom"))
        fig.update_layout(title=dict(y=1, yanchor="top", pad=dict(b=34)))

    st.plotly_chart(
        fig,
        width="stretch",
        key=key,
        config={"displayModeBar": False, "scrollZoom": False},
    )


# ---------------------------------------------------------------------------
# Page chrome
# ---------------------------------------------------------------------------
CSS = f"""
<style>
:root {{
    --bg: {BG};
    --surface: {SURFACE};
    --surface-2: {SURFACE_2};
    --border: {BORDER};
    --ink: {INK};
    --ink-soft: {INK_SOFT};
    --ink-muted: {INK_MUTED};
    --accent: {ACCENT};
    --accent-blue: {ACCENT_BLUE};
    --accent-violet: {ACCENT_VIOLET};
    --accent-amber: {ACCENT_AMBER};
}}

.stApp {{ background: var(--bg); }}
.block-container {{ padding-top: 3.4rem; padding-bottom: 4rem; max-width: 1240px; }}

h1, h2, h3, h4 {{ color: var(--ink); letter-spacing: -0.015em; }}
h1 {{ font-size: 1.95rem; font-weight: 700; line-height: 1.2; }}
h2 {{ font-size: 1.3rem; font-weight: 650; margin-top: 0.4rem; }}
h3 {{ font-size: 1.02rem; font-weight: 600; }}
p, li, label, .stMarkdown {{ color: var(--ink-soft); }}
a {{ color: var(--accent); }}
hr {{ border-color: var(--border); }}

/* --- page header ------------------------------------------------------- */
.page-head {{ margin-bottom: 1.5rem; }}
.page-head .eyebrow {{
    text-transform: uppercase; letter-spacing: 0.14em; font-size: 0.68rem;
    font-weight: 700; color: var(--accent); margin-bottom: 0.4rem;
}}
.page-head p {{
    color: var(--ink-soft); font-size: 0.96rem; max-width: 74ch; margin: 0.45rem 0 0;
    line-height: 1.6;
}}

/* --- cards ------------------------------------------------------------- */
.card {{
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 1.05rem 1.2rem; height: 100%;
}}
.card h4 {{ margin: 0 0 0.4rem; font-size: 0.94rem; font-weight: 650; color: var(--ink); }}
.card p {{ margin: 0; font-size: 0.86rem; color: var(--ink-soft); line-height: 1.55; }}

/* --- headline result --------------------------------------------------- */
.result-card {{
    background: linear-gradient(140deg, #16202c 0%, #1d2c3d 100%);
    border: 1px solid var(--border); border-radius: 16px; padding: 1.5rem 1.7rem;
}}
.result-card .label {{
    text-transform: uppercase; letter-spacing: 0.14em; font-size: 0.68rem;
    font-weight: 700; color: var(--ink-muted);
}}
.result-card .value {{
    font-size: 3.5rem; font-weight: 700; line-height: 1.05; margin: 0.25rem 0;
    color: var(--accent-violet);
}}
.result-card .value span {{
    font-size: 1.25rem; font-weight: 500; color: var(--ink-soft); margin-left: 0.45rem;
}}
.result-card .meta {{ font-size: 0.86rem; color: var(--ink-muted); }}

/* --- explanation block under every chart -------------------------------- */
.explain {{
    background: var(--surface); border: 1px solid var(--border);
    border-left: 3px solid var(--accent); border-radius: 0 10px 10px 0;
    padding: 0.85rem 1.05rem; margin: 0.15rem 0 1.9rem;
}}
.explain .row {{ display: flex; gap: 0.7rem; align-items: baseline; }}
.explain .row + .row {{ margin-top: 0.55rem; padding-top: 0.55rem; border-top: 1px solid var(--border); }}
.explain .tag {{
    flex: 0 0 auto; min-width: 96px; text-transform: uppercase;
    letter-spacing: 0.1em; font-size: 0.63rem; font-weight: 700;
    color: var(--ink-muted); padding-top: 0.12rem;
}}
.explain .tag.is-insight {{ color: var(--accent); }}
.explain p {{ margin: 0; font-size: 0.855rem; line-height: 1.6; color: var(--ink-soft); }}
.explain p strong {{ color: var(--ink); font-weight: 600; }}

/* --- caveat ------------------------------------------------------------- */
.caveat {{
    border-left: 3px solid var(--accent-amber); background: #241f14;
    border-radius: 0 10px 10px 0; padding: 0.95rem 1.15rem;
}}
.caveat p {{ margin: 0; font-size: 0.89rem; color: #e6d7b4; line-height: 1.65; }}

/* --- metrics ------------------------------------------------------------ */
div[data-testid="stMetric"] {{
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 10px; padding: 0.8rem 0.95rem;
}}
div[data-testid="stMetricLabel"] p {{
    font-size: 0.75rem !important; color: var(--ink-muted); font-weight: 500;
}}
div[data-testid="stMetricValue"] {{ font-size: 1.45rem; color: var(--ink); font-weight: 650; }}
div[data-testid="stMetricDelta"] {{ font-size: 0.78rem; }}

/* --- inputs -------------------------------------------------------------- */
div[data-testid="stNumberInput"] label p {{
    font-size: 0.84rem !important; color: var(--ink-soft); font-weight: 550;
}}
div[data-testid="stNumberInput"] input {{
    background: var(--surface-2); color: var(--ink); border-radius: 8px;
    font-variant-numeric: tabular-nums; font-size: 0.95rem; font-weight: 600;
}}
div[data-testid="stNumberInput"] button {{
    background: var(--surface-2); color: var(--ink-soft);
}}
div[data-testid="stNumberInput"] button:hover {{ color: var(--accent); }}
.range-hint {{
    font-size: 0.7rem; color: var(--ink-muted); margin: -0.55rem 0 0.85rem 0.1rem;
    font-variant-numeric: tabular-nums;
}}
.range-hint.is-out {{ color: var(--accent-amber); font-weight: 600; }}
.group-title {{
    font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.12em;
    font-weight: 700; color: var(--accent); margin: 0 0 0.7rem;
    padding-bottom: 0.45rem; border-bottom: 1px solid var(--border);
}}

div[data-baseweb="select"] > div, div[data-testid="stSelectbox"] > div > div {{
    background: var(--surface-2); border-color: var(--border);
}}

/* --- tabs, buttons ------------------------------------------------------ */
.stTabs [data-baseweb="tab-list"] {{ gap: 0.3rem; border-bottom: 1px solid var(--border); }}
.stTabs [data-baseweb="tab"] {{ font-size: 0.88rem; font-weight: 550; color: var(--ink-muted); }}
.stTabs [aria-selected="true"] {{ color: var(--accent) !important; }}

.stButton > button {{ border-radius: 8px; font-weight: 650; letter-spacing: 0.01em; }}
.stButton > button[kind="primary"] {{
    background: var(--accent); color: #052018; border: none; font-weight: 700;
}}
/* Streamlit wraps the label in its own <p>, which carries its own colour. */
.stButton > button[kind="primary"] p,
.stButton > button[kind="primary"] div {{ color: #052018 !important; font-weight: 700; }}
.stButton > button[kind="primary"]:hover {{ background: #19edb9; color: #052018; }}
.stDownloadButton > button {{ border-radius: 8px; font-weight: 600; }}

/* --- sidebar ------------------------------------------------------------ */
section[data-testid="stSidebar"] {{
    background: #131b25; border-right: 1px solid var(--border);
}}
section[data-testid="stSidebar"] .sidebar-brand {{ padding: 0.2rem 0 0.4rem; }}
section[data-testid="stSidebar"] .sidebar-brand .tag {{
    font-size: 0.75rem; color: var(--ink-muted); line-height: 1.5;
}}
section[data-testid="stSidebar"] .sidebar-foot {{
    font-size: 0.71rem; color: var(--ink-muted); line-height: 1.5;
}}

/* --- dataframes --------------------------------------------------------- */
div[data-testid="stDataFrame"] {{ border: 1px solid var(--border); border-radius: 10px; }}
</style>
"""

LOGO = config.APP_ROOT / "assets" / "logo.svg"
LOGO_ICON = config.APP_ROOT / "assets" / "icon.svg"


def bootstrap(page_title: str | None = None) -> None:
    """Apply the shared theme. Call once at the top of every page."""
    register_plotly_theme()
    if LOGO.exists():
        st.logo(str(LOGO), icon_image=str(LOGO_ICON), size="large")
    st.markdown(CSS, unsafe_allow_html=True)
    if page_title:
        st.session_state["_current_page"] = page_title


def sidebar() -> None:
    """Tagline and dataset footnote, below the navigation block."""
    with st.sidebar:
        st.markdown(
            f'<div class="sidebar-brand"><div class="tag">{t("app_subtitle")}</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.markdown(
            f'<div class="sidebar-foot">{t("sidebar_footer")}</div>',
            unsafe_allow_html=True,
        )


def page_head(eyebrow: str, title: str, description: str = "") -> None:
    body = f"<p>{description}</p>" if description else ""
    st.markdown(
        f"""
        <div class="page-head">
            <div class="eyebrow">{eyebrow}</div>
            <h1>{title}</h1>
            {body}
        </div>
        """,
        unsafe_allow_html=True,
    )


def card(title: str, body: str) -> None:
    st.markdown(
        f'<div class="card"><h4>{title}</h4><p>{body}</p></div>',
        unsafe_allow_html=True,
    )


def caveat(body: str) -> None:
    st.markdown(f'<div class="caveat"><p>{body}</p></div>', unsafe_allow_html=True)


def explain(what: str, insight: str | None = None) -> None:
    """The reading guide printed under a chart.

    `what` says what is plotted; `insight` states what the numbers currently on
    screen actually mean, and is recomputed from live values so it changes with
    the user's inputs rather than repeating a fixed sentence.
    """
    rows = f'<div class="row"><span class="tag">{t("explain_what")}</span><p>{what}</p></div>'
    if insight:
        rows += (
            f'<div class="row"><span class="tag is-insight">{t("explain_insight")}</span>'
            f"<p>{insight}</p></div>"
        )
    st.markdown(f'<div class="explain">{rows}</div>', unsafe_allow_html=True)


def result_card(value: float, unit: str, label: str, meta: str) -> None:
    st.markdown(
        f"""
        <div class="result-card">
            <div class="label">{label}</div>
            <div class="value">{value:.1f}<span>{unit}</span></div>
            <div class="meta">{meta}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def range_hint(text: str, out_of_range: bool = False) -> None:
    css_class = "range-hint is-out" if out_of_range else "range-hint"
    st.markdown(f'<div class="{css_class}">{text}</div>', unsafe_allow_html=True)


def group_title(text: str) -> None:
    st.markdown(f'<div class="group-title">{text}</div>', unsafe_allow_html=True)


def model_label(spec: config.ModelSpec) -> str:
    star = " ★" if spec.is_champion else ""
    return f"{spec.name}{star}"


def feature_label(column: str) -> str:
    feature = config.FEATURES_BY_COLUMN.get(column)
    return column if feature is None else feature.label


def gauge(value: float, lower: float | None, upper: float | None, vmax: float = 90.0) -> go.Figure:
    """Prediction dial: ordered strength bands and the predicted value.

    The bands are the EN 206 strength classes, which are *ordered*, so they
    carry the single-hue ordinal ramp rather than a rainbow — darker means
    weaker, brighter means stronger, and the reading survives greyscale. The
    interval is deliberately not drawn here: it is already stated as a metric
    beside the dial, and a second overlay on a 90-degree arc only muddles it.
    """
    bands = [0, 20, 30, 40, 50, 60, vmax]
    steps = [
        dict(range=[bands[i], bands[i + 1]], color=ORDINAL_TEAL[i])
        for i in range(len(bands) - 1)
    ]

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            domain=dict(x=[0, 1], y=[0.22, 1]),
            number=dict(
                suffix=" MPa",
                font=dict(size=26, color=INK, family="Inter, 'Segoe UI', sans-serif"),
            ),
            gauge=dict(
                axis=dict(
                    range=[0, vmax], tickwidth=1, tickcolor=BORDER,
                    tickfont=dict(size=11, color=INK_MUTED),
                ),
                bar=dict(color="rgba(0,0,0,0)", thickness=0),
                bgcolor=SURFACE,
                bordercolor=BORDER,
                borderwidth=1,
                steps=steps,
                threshold=dict(
                    line=dict(color=ACCENT_VIOLET, width=5),
                    thickness=0.9,
                    value=value,
                ),
            ),
        )
    )
    fig.update_layout(height=260, margin=dict(l=30, r=30, t=18, b=10))
    return fig
