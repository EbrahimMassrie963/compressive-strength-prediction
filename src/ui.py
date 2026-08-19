"""Shared presentation layer: theme, Plotly defaults and reusable blocks."""

from __future__ import annotations

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

from src import config
from src.strings import t

# --- Palette -------------------------------------------------------------
# Categorical slots are assigned in this fixed order and never cycled.
SERIES = (
    "#2a78d6",  # 1 blue
    "#eb6834",  # 2 orange
    "#1baf7a",  # 3 aqua
    "#eda100",  # 4 yellow
    "#e87ba4",  # 5 magenta
    "#008300",  # 6 green
    "#4a3aa7",  # 7 violet
    "#e34948",  # 8 red
)

SEQUENTIAL_BLUE = [
    "#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec",
    "#5598e7", "#3987e5", "#2a78d6", "#256abf", "#1c5cab",
    "#184f95", "#104281", "#0d366b",
]

DIVERGING = [
    [0.0, "#0d366b"], [0.25, "#3987e5"], [0.5, "#f0efec"],
    [0.75, "#e34948"], [1.0, "#8f1f1f"],
]

STATUS = {
    "good": "#0ca30c",
    "warning": "#fab219",
    "serious": "#ec835a",
    "critical": "#d03b3b",
}

SURFACE = "#ffffff"
SURFACE_ALT = "#f6f6f4"
INK = "#0b0b0b"
INK_SOFT = "#52514e"
INK_MUTED = "#7c7a75"
GRID = "#e8e7e4"
BORDER = "#dedcd7"


def register_plotly_theme() -> None:
    """A recessive, hairline chart template used by every figure in the app."""
    template = go.layout.Template()
    template.layout = go.Layout(
        colorway=list(SERIES),
        font=dict(
            family="Inter, 'Segoe UI', system-ui, sans-serif",
            size=13,
            color=INK_SOFT,
        ),
        title=dict(font=dict(size=15, color=INK), x=0, xanchor="left", pad=dict(b=12)),
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        margin=dict(l=8, r=8, t=48, b=8),
        xaxis=dict(
            gridcolor=GRID, gridwidth=1, griddash="solid", zeroline=False,
            linecolor=BORDER, linewidth=1, ticks="outside", ticklen=4,
            tickcolor=BORDER, tickfont=dict(size=12, color=INK_MUTED),
            title=dict(font=dict(size=12, color=INK_MUTED)),
            automargin=True,
        ),
        yaxis=dict(
            gridcolor=GRID, gridwidth=1, griddash="solid", zeroline=False,
            linecolor=BORDER, linewidth=1, ticks="outside", ticklen=4,
            tickcolor=BORDER, tickfont=dict(size=12, color=INK_MUTED),
            title=dict(font=dict(size=12, color=INK_MUTED)),
            automargin=True,
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            font=dict(size=12, color=INK_SOFT), bgcolor="rgba(0,0,0,0)",
            title=dict(text=""),
        ),
        hoverlabel=dict(
            bgcolor=SURFACE, bordercolor=BORDER,
            font=dict(size=12, color=INK, family="Inter, 'Segoe UI', sans-serif"),
        ),
        colorscale=dict(sequential=[[i / 12, c] for i, c in enumerate(SEQUENTIAL_BLUE)]),
        separators=".,",
    )
    pio.templates["concrete"] = template
    pio.templates.default = "concrete"


def chart(fig: go.Figure, height: int | None = None, key: str | None = None) -> None:
    """Render a Plotly figure with the app's fixed display options."""
    if height is not None:
        fig.update_layout(height=height)
    st.plotly_chart(
        fig,
        width="stretch",
        key=key,
        config={"displayModeBar": False, "scrollZoom": False},
    )


# --- Page chrome ---------------------------------------------------------
CSS = """
<style>
:root {
    --surface: #ffffff;
    --surface-alt: #f6f6f4;
    --ink: #0b0b0b;
    --ink-soft: #52514e;
    --ink-muted: #7c7a75;
    --border: #dedcd7;
    --accent: #2a78d6;
}
.block-container { padding-top: 3.6rem; padding-bottom: 4rem; max-width: 1180px; }
h1, h2, h3 { color: var(--ink); letter-spacing: -0.015em; }
h1 { font-size: 1.9rem; font-weight: 700; line-height: 1.2; }
h2 { font-size: 1.35rem; font-weight: 650; margin-top: 0.4rem; }
h3 { font-size: 1.05rem; font-weight: 600; }

.page-head { margin-bottom: 1.6rem; }
.page-head .eyebrow {
    text-transform: uppercase; letter-spacing: 0.12em; font-size: 0.7rem;
    font-weight: 600; color: var(--accent); margin-bottom: 0.35rem;
}
.page-head p { color: var(--ink-soft); font-size: 0.98rem; max-width: 68ch; margin: 0.4rem 0 0; }

.card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 1.1rem 1.25rem; height: 100%;
}
.card h4 { margin: 0 0 0.35rem; font-size: 0.95rem; font-weight: 650; color: var(--ink); }
.card p { margin: 0; font-size: 0.87rem; color: var(--ink-soft); line-height: 1.5; }

.result-card {
    background: linear-gradient(135deg, #12243b 0%, #1d3a5c 100%);
    border-radius: 16px; padding: 1.6rem 1.8rem; color: #ffffff;
}
.result-card .label {
    text-transform: uppercase; letter-spacing: 0.12em; font-size: 0.7rem;
    font-weight: 600; opacity: 0.75;
}
.result-card .value { font-size: 3.4rem; font-weight: 700; line-height: 1.05; margin: 0.2rem 0; }
.result-card .value span { font-size: 1.3rem; font-weight: 500; opacity: 0.8; margin-inline-start: 0.4rem; }
.result-card .meta { font-size: 0.88rem; opacity: 0.85; }

.pill {
    display: inline-block; padding: 0.18rem 0.6rem; border-radius: 999px;
    font-size: 0.74rem; font-weight: 600; letter-spacing: 0.02em;
}
.pill-champion { background: rgba(12,163,12,0.12); color: #0a7a0a; }
.pill-neutral { background: var(--surface-alt); color: var(--ink-soft); }

.caveat {
    border-inline-start: 3px solid #fab219; background: #fffaf0;
    border-radius: 8px; padding: 0.9rem 1.1rem;
}
.caveat p { margin: 0; font-size: 0.9rem; color: #6b4d0c; line-height: 1.6; }

div[data-testid="stMetric"] {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 10px; padding: 0.75rem 0.9rem;
}
div[data-testid="stMetricLabel"] p { font-size: 0.78rem !important; color: var(--ink-muted); }
div[data-testid="stMetricValue"] { font-size: 1.5rem; color: var(--ink); }

section[data-testid="stSidebar"] { background: var(--surface-alt); border-inline-end: 1px solid var(--border); }
section[data-testid="stSidebar"] .sidebar-brand { padding: 0.2rem 0 1rem; }
section[data-testid="stSidebar"] .sidebar-brand .name { font-weight: 700; font-size: 1rem; color: var(--ink); }
section[data-testid="stSidebar"] .sidebar-brand .tag { font-size: 0.76rem; color: var(--ink-muted); line-height: 1.4; }
section[data-testid="stSidebar"] .sidebar-foot { font-size: 0.72rem; color: var(--ink-muted); line-height: 1.5; }

.stTabs [data-baseweb="tab-list"] { gap: 0.25rem; border-bottom: 1px solid var(--border); }
.stTabs [data-baseweb="tab"] { font-size: 0.9rem; font-weight: 550; }

.stButton > button { border-radius: 8px; font-weight: 600; }
hr { border-color: var(--border); }
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
    body = f'<p>{description}</p>' if description else ""
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


def model_label(spec: config.ModelSpec) -> str:
    star = " ★" if spec.is_champion else ""
    return f"{spec.name}{star}"


def feature_label(column: str) -> str:
    feature = config.FEATURES_BY_COLUMN.get(column)
    return column if feature is None else feature.label


def gauge(value: float, lower: float | None, upper: float | None, vmax: float = 90.0) -> go.Figure:
    """A single-number gauge with the prediction interval drawn as a band."""
    steps = []
    if lower is not None and upper is not None:
        steps.append(
            dict(range=[max(0, lower), min(vmax, upper)], color="rgba(42,120,214,0.16)")
        )

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number=dict(suffix=" MPa", font=dict(size=30, color=INK)),
            gauge=dict(
                axis=dict(
                    range=[0, vmax], tickwidth=1, tickcolor=BORDER,
                    tickfont=dict(size=11, color=INK_MUTED),
                ),
                bar=dict(color=SERIES[0], thickness=0.28),
                bgcolor=SURFACE_ALT,
                borderwidth=0,
                steps=steps,
            ),
        )
    )
    fig.update_layout(height=210, margin=dict(l=24, r=24, t=16, b=8))
    return fig
