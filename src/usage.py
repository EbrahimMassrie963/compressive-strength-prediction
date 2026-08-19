"""Usage logging: what was predicted, by whom, and how accurate it turned out.

Records land in `data/usage_log.csv`. On a free hosting tier the container
filesystem is ephemeral, so this is a rolling window of recent activity rather
than a permanent database — the Statistics page says so explicitly.
"""

from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone

import pandas as pd
import streamlit as st

from src import config

_LOCK = threading.Lock()

COLUMNS = [
    "record_id",
    "timestamp",
    "session_id",
    "source",
    "model_key",
    "family",
    "n_rows",
    "prediction",
    "lower",
    "upper",
    "strength_class",
    "extrapolated",
    "actual",
] + [f.column for f in config.FEATURES]


def session_id() -> str:
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = uuid.uuid4().hex[:12]
    return st.session_state["session_id"]


def _empty_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=COLUMNS)


def load(scope: str = "all") -> pd.DataFrame:
    """Read the usage log. `scope` is "all" or "session"."""
    path = config.USAGE_LOG
    if not path.exists():
        frame = _empty_frame()
    else:
        try:
            frame = pd.read_csv(path)
        except (pd.errors.EmptyDataError, pd.errors.ParserError):
            frame = _empty_frame()

    for column in COLUMNS:
        if column not in frame.columns:
            frame[column] = pd.NA
    frame = frame[COLUMNS]

    if not frame.empty:
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="coerce", utc=True)
        for column in ("prediction", "lower", "upper", "actual", "n_rows"):
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
        frame = frame.dropna(subset=["timestamp", "prediction"])

    if scope == "session" and not frame.empty:
        frame = frame[frame["session_id"] == session_id()]

    return frame.reset_index(drop=True)


def record(
    *,
    source: str,
    model_key: str,
    family: str,
    prediction: float,
    lower: float | None = None,
    upper: float | None = None,
    strength_class: str = "",
    extrapolated: bool = False,
    values: dict[str, float] | None = None,
    n_rows: int = 1,
) -> str:
    """Append one prediction event and return its record id."""
    values = values or {}
    record_id = uuid.uuid4().hex[:16]

    row = {
        "record_id": record_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id(),
        "source": source,
        "model_key": model_key,
        "family": family,
        "n_rows": n_rows,
        "prediction": round(float(prediction), 4),
        "lower": None if lower is None else round(float(lower), 4),
        "upper": None if upper is None else round(float(upper), 4),
        "strength_class": strength_class,
        "extrapolated": bool(extrapolated),
        "actual": None,
    }
    for feature in config.FEATURES:
        value = values.get(feature.column)
        row[feature.column] = None if value is None else round(float(value), 4)

    frame = pd.DataFrame([row], columns=COLUMNS)
    with _LOCK:
        config.USAGE_LOG.parent.mkdir(parents=True, exist_ok=True)
        header = not config.USAGE_LOG.exists()
        frame.to_csv(config.USAGE_LOG, mode="a", header=header, index=False)

    return record_id


def add_measurement(record_id: str, actual: float) -> bool:
    """Attach a laboratory-measured strength to an existing record."""
    path = config.USAGE_LOG
    if not path.exists():
        return False

    with _LOCK:
        frame = pd.read_csv(path)
        if "record_id" not in frame.columns:
            return False
        mask = frame["record_id"] == record_id
        if not mask.any():
            return False
        frame.loc[mask, "actual"] = float(actual)
        frame.to_csv(path, index=False)
    return True


def clear() -> None:
    with _LOCK:
        if config.USAGE_LOG.exists():
            config.USAGE_LOG.unlink()


def summary(frame: pd.DataFrame) -> dict:
    """Headline numbers for the statistics page."""
    if frame.empty:
        return {
            "total_events": 0,
            "total_rows": 0,
            "sessions": 0,
            "batch_rows": 0,
            "mean_prediction": float("nan"),
            "extrapolated": 0,
            "measurements": 0,
        }

    n_rows = pd.to_numeric(frame["n_rows"], errors="coerce").fillna(1)
    batch_mask = frame["source"] == "batch"
    extrapolated = frame["extrapolated"].astype(str).str.lower().isin(["true", "1"])

    return {
        "total_events": int(len(frame)),
        "total_rows": int(n_rows.sum()),
        "sessions": int(frame["session_id"].nunique()),
        "batch_rows": int(n_rows[batch_mask].sum()),
        "mean_prediction": float(frame["prediction"].mean()),
        "extrapolated": int(extrapolated.sum()),
        "measurements": int(frame["actual"].notna().sum()),
    }


def measured(frame: pd.DataFrame) -> pd.DataFrame:
    """Rows where the user reported a laboratory-measured strength."""
    if frame.empty:
        return frame
    result = frame[frame["actual"].notna()].copy()
    if result.empty:
        return result
    result["error"] = result["prediction"] - result["actual"]
    result["abs_error"] = result["error"].abs()
    covered = (result["actual"] >= result["lower"]) & (result["actual"] <= result["upper"])
    result["in_interval"] = covered.where(result["lower"].notna() & result["upper"].notna())
    return result
