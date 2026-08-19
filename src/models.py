"""Model loading, prediction, uncertainty and held-out evaluation."""

from __future__ import annotations

import importlib.util
import warnings
from functools import lru_cache

import joblib
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.metrics import (
    mean_absolute_error,
    mean_absolute_percentage_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import train_test_split

from src import config, data

warnings.filterwarnings("ignore", category=UserWarning)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------
@lru_cache(maxsize=None)
def _package_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def available_models(family: str) -> list[config.ModelSpec]:
    """Registered models whose file and optional dependency are both present."""
    usable = []
    for spec in config.models_for_family(family):
        if spec.requires_package and not _package_available(spec.requires_package):
            continue
        if not (config.APP_ROOT / spec.model_path).exists():
            continue
        usable.append(spec)
    return usable


@st.cache_resource(show_spinner=False)
def load_estimator(model_path: str):
    return joblib.load(config.APP_ROOT / model_path)


@st.cache_resource(show_spinner=False)
def load_scaler(scaler_path: str):
    return joblib.load(config.APP_ROOT / scaler_path)


# ---------------------------------------------------------------------------
# Prediction
# ---------------------------------------------------------------------------
def to_frame(values: dict[str, float], columns: list[str]) -> pd.DataFrame:
    """Build a one-row frame with the exact column names the scaler expects."""
    return pd.DataFrame([[values[c] for c in columns]], columns=columns)


def scale(frame: pd.DataFrame, scaler_path: str, columns: list[str]) -> pd.DataFrame:
    scaler = load_scaler(scaler_path)
    scaled = scaler.transform(frame[columns])
    return pd.DataFrame(scaled, columns=columns, index=frame.index)


def predict(spec: config.ModelSpec, frame: pd.DataFrame) -> np.ndarray:
    """Predict compressive strength (MPa) for raw, unscaled mix rows."""
    model = load_estimator(spec.model_path)
    scaled = scale(frame, spec.scaler_path, spec.columns)
    return np.asarray(model.predict(scaled), dtype=float)


@st.cache_data(show_spinner=False)
def interval_settings(family: str) -> dict:
    """Conformal interval configuration produced by the training script."""
    manifest = data.load_artifact("app_training_manifest.json")
    return manifest.get("families", {}).get(family, {}).get("interval_model", {})


def predict_interval(family: str, frame: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Conformalized 90% prediction interval for raw, unscaled mix rows."""
    settings = interval_settings(family)
    family_cfg = config.FAMILIES[family]
    columns = (
        config.WITH_TEMP_COLUMNS if family == "with_temp" else config.NO_TEMP_COLUMNS
    )

    lower_model = load_estimator(family_cfg["interval_lower"])
    upper_model = load_estimator(family_cfg["interval_upper"])
    scaled = scale(frame, family_cfg["scaler"], columns)

    lower = np.asarray(lower_model.predict(scaled), dtype=float)
    upper = np.asarray(upper_model.predict(scaled), dtype=float)
    lower, upper = np.minimum(lower, upper), np.maximum(lower, upper)

    correction = float(settings.get("conformal_correction_mpa", 0.0))
    return lower - correction, upper + correction


def predict_with_interval(
    spec: config.ModelSpec, frame: pd.DataFrame
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Point prediction plus an interval guaranteed to contain it.

    The quantile regressors are fitted independently of the point predictor, so
    on roughly 3% of rows the point estimate lands just outside the raw band.
    Widening the band to include it keeps the displayed result coherent and can
    only raise coverage, never lower it.
    """
    prediction = predict(spec, frame)
    lower, upper = predict_interval(spec.family, frame)
    return prediction, np.minimum(lower, prediction), np.maximum(upper, prediction)


def local_sensitivity(
    spec: config.ModelSpec, values: dict[str, float], pct: float = 0.10
) -> pd.DataFrame:
    """Change in prediction when each input is moved ±pct, others held fixed.

    A model-agnostic local explanation: it needs no extra dependency and
    answers the question users actually ask — "what if I add more cement?"
    """
    columns = spec.columns
    base_frame = to_frame(values, columns)
    base_pred = float(predict(spec, base_frame)[0])

    rows = []
    perturbed = []
    for column in columns:
        for direction in (1, -1):
            variant = dict(values)
            step = abs(values[column]) * pct
            if step == 0:
                # A zero-valued ingredient has no proportional step; use a small
                # absolute one derived from the training spread instead.
                spread = data.feature_stats(spec.family).loc[column, "std"]
                step = float(spread) * pct
            variant[column] = max(0.0, values[column] + direction * step)
            perturbed.append(variant)
            rows.append((column, direction, variant[column]))

    frame = pd.DataFrame([[v[c] for c in columns] for v in perturbed], columns=columns)
    preds = predict(spec, frame)

    records = []
    for (column, direction, new_value), pred in zip(rows, preds):
        records.append(
            {
                "column": column,
                "direction": "up" if direction > 0 else "down",
                "input_value": new_value,
                "prediction": float(pred),
                "delta": float(pred) - base_pred,
            }
        )
    return pd.DataFrame(records)


def sweep(
    spec: config.ModelSpec,
    values: dict[str, float],
    column: str,
    grid: np.ndarray,
) -> np.ndarray:
    """Predictions along a one-dimensional sweep of a single ingredient."""
    columns = spec.columns
    frame = pd.DataFrame(
        [[grid[i] if c == column else values[c] for c in columns] for i in range(len(grid))],
        columns=columns,
    )
    return predict(spec, frame)


def sweep_2d(
    spec: config.ModelSpec,
    values: dict[str, float],
    x_column: str,
    x_grid: np.ndarray,
    y_column: str,
    y_grid: np.ndarray,
) -> np.ndarray:
    """Predicted strength over a 2-D grid of two ingredients."""
    columns = spec.columns
    rows = []
    for y_value in y_grid:
        for x_value in x_grid:
            row = []
            for c in columns:
                if c == x_column:
                    row.append(x_value)
                elif c == y_column:
                    row.append(y_value)
                else:
                    row.append(values[c])
            rows.append(row)
    frame = pd.DataFrame(rows, columns=columns)
    preds = predict(spec, frame)
    return preds.reshape(len(y_grid), len(x_grid))


# ---------------------------------------------------------------------------
# Held-out evaluation
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def get_split(family: str) -> dict:
    """Reproduce the exact train/test split used throughout the research."""
    df = data.load_dataset(family)
    X = df.drop(columns=config.TARGET_COL)
    y = df[config.TARGET_COL]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=config.TEST_SIZE, random_state=config.RANDOM_SEED
    )
    return {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
    }


@st.cache_data(show_spinner=False)
def test_predictions(model_key: str) -> pd.DataFrame:
    """Held-out predictions for one model, with residuals."""
    spec = config.MODELS_BY_KEY[model_key]
    split = get_split(spec.family)
    X_test, y_test = split["X_test"], split["y_test"]

    y_pred = predict(spec, X_test)
    return pd.DataFrame(
        {
            "actual": y_test.to_numpy(dtype=float),
            "predicted": y_pred,
            "residual": y_test.to_numpy(dtype=float) - y_pred,
            "abs_error": np.abs(y_test.to_numpy(dtype=float) - y_pred),
        },
        index=y_test.index,
    )


def _metrics(actual: np.ndarray, predicted: np.ndarray) -> dict:
    return {
        "r2": float(r2_score(actual, predicted)),
        "rmse": float(np.sqrt(mean_squared_error(actual, predicted))),
        "mae": float(mean_absolute_error(actual, predicted)),
        "mape": float(mean_absolute_percentage_error(actual, predicted) * 100),
        "within_5": float(np.mean(np.abs(actual - predicted) <= 5.0) * 100),
    }


@st.cache_data(show_spinner=False)
def published_metrics() -> pd.DataFrame:
    """Test metrics as recorded by the notebooks and the training script.

    Reading three small JSON files is instant, where `evaluate_all` has to load
    every model and re-score the test split. Pages that only need headline
    numbers use this; pages that plot residuals use the live evaluation.
    """
    manifest = data.load_artifact("deployment_manifest.json")
    metadata = data.load_artifact("model_metadata.json")
    training = data.load_artifact("app_training_manifest.json")

    tuned = {
        entry["model"]: entry
        for entry in metadata.get("tuned_test_leaderboard", [])
    }
    no_temp_models = (
        training.get("families", {}).get("no_temp", {}).get("models", {})
    )
    lookup = {
        "gb_with_temp": {
            "r2": manifest.get("test_metrics", {}).get("r2"),
            "rmse": manifest.get("test_metrics", {}).get("rmse"),
        },
        "lgbm_with_temp": {
            "r2": tuned.get("LightGBM", {}).get("test_r2"),
            "rmse": tuned.get("LightGBM", {}).get("test_rmse"),
        },
        "xgb_with_temp": {
            "r2": tuned.get("XGBoost", {}).get("test_r2"),
            "rmse": tuned.get("XGBoost", {}).get("test_rmse"),
        },
        "gb_no_temp": no_temp_models.get("gradient_boosting", {}),
        "lgbm_no_temp": no_temp_models.get("lightgbm", {}),
        "xgb_no_temp": no_temp_models.get("xgboost", {}),
    }

    records = []
    for family in config.FAMILIES:
        for spec in available_models(family):
            entry = lookup.get(spec.key, {})
            records.append(
                {
                    "key": spec.key,
                    "family": family,
                    "is_champion": spec.is_champion,
                    "r2": entry.get("r2", entry.get("test_r2")),
                    "rmse": entry.get("rmse", entry.get("test_rmse")),
                }
            )
    frame = pd.DataFrame(records).dropna(subset=["r2"])
    return frame.sort_values("r2", ascending=False).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def evaluate_all() -> pd.DataFrame:
    """Evaluate every available model on its family's held-out test split."""
    records = []
    for family in config.FAMILIES:
        for spec in available_models(family):
            frame = test_predictions(spec.key)
            record = {
                "key": spec.key,
                "family": family,
                "n_features": len(spec.columns),
                "is_champion": spec.is_champion,
                **_metrics(frame["actual"].to_numpy(), frame["predicted"].to_numpy()),
            }
            records.append(record)
    return pd.DataFrame(records).sort_values("r2", ascending=False).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def interval_evaluation(family: str) -> pd.DataFrame:
    """Held-out interval bounds, for calibration plots."""
    split = get_split(family)
    X_test, y_test = split["X_test"], split["y_test"]
    lower, upper = predict_interval(family, X_test)
    actual = y_test.to_numpy(dtype=float)
    return pd.DataFrame(
        {
            "actual": actual,
            "lower": lower,
            "upper": upper,
            "width": upper - lower,
            "covered": (actual >= lower) & (actual <= upper),
        },
        index=y_test.index,
    )


@st.cache_data(show_spinner=False)
def builtin_importance(model_key: str) -> pd.DataFrame:
    """The model's own feature importances, normalised to sum to 1."""
    spec = config.MODELS_BY_KEY[model_key]
    model = load_estimator(spec.model_path)
    if not hasattr(model, "feature_importances_"):
        return pd.DataFrame()

    importances = np.asarray(model.feature_importances_, dtype=float)
    total = importances.sum()
    if total > 0:
        importances = importances / total
    return (
        pd.DataFrame({"column": spec.columns, "importance": importances})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )


def out_of_range(values: dict[str, float], family: str) -> list[tuple[str, float, float, float]]:
    """Inputs outside the training range: (column, value, train_min, train_max)."""
    ranges = data.training_ranges(family)
    flagged = []
    for column, value in values.items():
        if column not in ranges:
            continue
        low, high = ranges[column]
        if value < low or value > high:
            flagged.append((column, float(value), low, high))
    return flagged


def derived_indicators(values: dict[str, float]) -> dict[str, float]:
    """Mix-design ratios civil engineers read before they read a prediction."""
    cement = values.get(config.CEMENT, 0.0)
    slag = values.get(config.SLAG, 0.0)
    fly_ash = values.get(config.FLY_ASH, 0.0)
    water = values.get(config.WATER, 0.0)
    coarse = values.get(config.COARSE_AGG, 0.0)
    fine = values.get(config.FINE_AGG, 0.0)

    binder = cement + slag + fly_ash
    return {
        "wc_ratio": water / cement if cement > 0 else float("nan"),
        "wb_ratio": water / binder if binder > 0 else float("nan"),
        "total_binder": binder,
        "agg_ratio": coarse / fine if fine > 0 else float("nan"),
        "total_mass": binder + water + coarse + fine + values.get(config.SUPERPLASTICIZER, 0.0),
    }
