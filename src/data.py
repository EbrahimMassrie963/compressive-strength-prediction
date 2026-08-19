"""Dataset and research-artifact access, all cached for the app lifetime."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import pandas as pd
import streamlit as st

from src import config


@st.cache_data(show_spinner=False)
def load_dataset(family: str = "with_temp") -> pd.DataFrame:
    """Load the training dataset for a model family."""
    path = config.FAMILIES[family]["dataset"]
    df = pd.read_excel(path)
    return df


@st.cache_data(show_spinner=False)
def feature_stats(family: str = "with_temp") -> pd.DataFrame:
    """Per-feature min / max / median / mean over the training data."""
    df = load_dataset(family)
    cols = [c for c in df.columns if c != config.TARGET_COL]
    stats = df[cols].agg(["min", "max", "median", "mean", "std"]).T
    return stats


@st.cache_data(show_spinner=False)
def training_ranges(family: str = "with_temp") -> dict[str, tuple[float, float]]:
    stats = feature_stats(family)
    return {col: (float(row["min"]), float(row["max"])) for col, row in stats.iterrows()}


@st.cache_data(show_spinner=False)
def target_series(family: str = "with_temp") -> pd.Series:
    return load_dataset(family)[config.TARGET_COL]


@st.cache_data(show_spinner=False)
def load_artifact(name: str) -> dict:
    """Load a JSON artifact produced by the notebooks or the training script."""
    path = config.ARTIFACTS_DIR / name
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def load_report_csv(name: str) -> pd.DataFrame:
    """Load one of the CSV result tables exported by the notebooks."""
    path = config.REPORTS_DIR / name
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


@lru_cache(maxsize=1)
def figure_groups() -> dict[str, list[Path]]:
    """Research figures, grouped by the notebook stage that produced them."""
    groups: dict[str, list[Path]] = {}
    for sub in sorted(config.FIGURES_DIR.iterdir()):
        if sub.is_dir():
            images = sorted(sub.glob("*.png"))
            if images:
                groups[sub.name] = images
    return groups


def prettify_figure_name(path: Path) -> str:
    """`03_correlation_heatmap.png` -> `Correlation heatmap`."""
    stem = path.stem
    if "_" in stem and stem.split("_", 1)[0].isdigit():
        stem = stem.split("_", 1)[1]
    return stem.replace("_", " ").capitalize()


def short_label(column: str) -> str:
    """Short display label for a dataset column."""
    feature = config.FEATURES_BY_COLUMN.get(column)
    if feature is not None:
        return feature.label
    if column == config.TARGET_COL:
        return "Compressive strength"
    return column

