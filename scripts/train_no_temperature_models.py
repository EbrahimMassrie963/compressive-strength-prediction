"""
Train the "without curing temperature" model family + prediction-interval models.

Why this script exists
----------------------
The five research notebooks produced models that all consume the 9-feature
vector (8 mix/age variables + the synthetic curing temperature). The web app
must also serve users who do not have a curing-temperature value, so this
script trains a parallel 8-feature family on the *original* UCI dataset.

It deliberately replicates the notebook methodology step for step so the two
families are comparable:

  * identical split          : train_test_split(test_size=0.2, random_state=42)
  * identical preprocessing  : StandardScaler fitted on the training split only
  * identical outlier policy : consensus of IsolationForest(0.05) and
                               LocalOutlierFactor(n_neighbors=20, 0.05),
                               removed from the training split only
  * identical hyperparameters: the tuned parameters recorded in
                               artifacts/model_metadata.json ("tuning_summary")

It additionally fits *conformalized* quantile Gradient Boosting models
(alpha = 0.05 / 0.95) for BOTH families, which give the app a calibrated 90%
prediction interval that is two orders of magnitude lighter than the 37 MB
Random Forest interval model from Notebook 4. Raw quantile regressors trained
on this dataset under-cover badly (~77%), so the quantiles are calibrated on a
held-out split using split-conformal prediction (Romano et al., 2019), which
restores nominal coverage.

Run from the app/ directory:
    .venv/Scripts/python.exe scripts/train_no_temperature_models.py
"""

from __future__ import annotations

import json
import os
import sys
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from lightgbm import LGBMRegressor
from sklearn.ensemble import (
    GradientBoostingRegressor,
    IsolationForest,
)
from sklearn.metrics import (
    mean_absolute_error,
    mean_absolute_percentage_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import KFold, cross_val_score, train_test_split
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

warnings.filterwarnings("ignore")

RANDOM_SEED = 42
TEST_SIZE = 0.2
TARGET_COL = "Concrete compressive strength(MPa, megapascals) "

APP_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = APP_ROOT / "data"
MODELS_DIR = APP_ROOT / "models"
SCALERS_DIR = APP_ROOT / "scalers"
ARTIFACTS_DIR = APP_ROOT / "artifacts"

for d in (MODELS_DIR, SCALERS_DIR, ARTIFACTS_DIR):
    d.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------------------------------
# Shared helpers
# --------------------------------------------------------------------------
def tuned_params(model_name: str) -> dict:
    """Return the tuned hyperparameters recorded by Notebook 3."""
    with open(ARTIFACTS_DIR / "model_metadata.json", encoding="utf-8") as f:
        meta = json.load(f)
    for entry in meta.get("tuning_summary", []):
        if entry["model"] == model_name:
            return dict(entry.get("best_params", {}) or {})
    raise KeyError(f"No tuned parameters recorded for {model_name}")


def consensus_outlier_index(X_train_scaled: pd.DataFrame) -> pd.Index:
    """Rows flagged as outliers by BOTH IsolationForest and LOF (Notebook 4)."""
    iso = IsolationForest(contamination=0.05, random_state=RANDOM_SEED, n_jobs=-1)
    iso_labels = iso.fit_predict(X_train_scaled)

    lof = LocalOutlierFactor(n_neighbors=20, contamination=0.05)
    lof_labels = lof.fit_predict(X_train_scaled)

    iso_out = set(X_train_scaled.index[iso_labels == -1])
    lof_out = set(X_train_scaled.index[lof_labels == -1])
    return pd.Index(sorted(iso_out & lof_out))


def evaluate(model, X_test_scaled, y_test) -> dict:
    y_pred = model.predict(X_test_scaled)
    return {
        "test_r2": float(r2_score(y_test, y_pred)),
        "test_rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
        "test_mae": float(mean_absolute_error(y_test, y_pred)),
        "test_mape": float(mean_absolute_percentage_error(y_test, y_pred)),
    }


def build_estimators() -> dict:
    """The same three tuned architectures the notebooks kept as finalists."""
    gb_params = tuned_params("Gradient Boosting")
    lgbm_params = tuned_params("LightGBM")
    xgb_params = tuned_params("XGBoost")

    return {
        "gradient_boosting": GradientBoostingRegressor(
            random_state=RANDOM_SEED, **gb_params
        ),
        "lightgbm": LGBMRegressor(random_state=RANDOM_SEED, verbose=-1, **lgbm_params),
        "xgboost": XGBRegressor(random_state=RANDOM_SEED, **xgb_params),
    }


def build_quantile_models() -> tuple[GradientBoostingRegressor, GradientBoostingRegressor]:
    """Lower/upper quantile regressors for a 90% prediction interval.

    Deliberately shallower and more regularized than the point predictor: a
    quantile loss fitted as hard as the squared loss memorizes the training
    residual spread and produces intervals far too narrow to generalize.
    """
    common = dict(
        loss="quantile",
        random_state=RANDOM_SEED,
        n_estimators=300,
        max_depth=3,
        learning_rate=0.05,
        subsample=0.85,
        min_samples_leaf=10,
    )
    return (
        GradientBoostingRegressor(alpha=0.05, **common),
        GradientBoostingRegressor(alpha=0.95, **common),
    )


def conformal_correction(
    lower_cal: np.ndarray, upper_cal: np.ndarray, y_cal: np.ndarray, alpha: float = 0.10
) -> float:
    """Split-conformal correction for quantile regression (CQR).

    Returns the additive width `q` such that widening every predicted interval
    to [lower - q, upper + q] achieves >= 1 - alpha coverage on exchangeable
    future data. `q` can be negative when the raw quantiles over-cover.
    """
    scores = np.maximum(lower_cal - y_cal, y_cal - upper_cal)
    n = len(scores)
    # Finite-sample corrected quantile level; clipped for very small n.
    level = min(1.0, np.ceil((n + 1) * (1 - alpha)) / n)
    return float(np.quantile(scores, level, method="higher"))


# --------------------------------------------------------------------------
# Family training
# --------------------------------------------------------------------------
def train_family(df: pd.DataFrame, suffix: str, reuse_scaler: Path | None = None) -> dict:
    """Train one model family (with or without curing temperature)."""
    X = df.drop(columns=TARGET_COL)
    y = df[TARGET_COL]
    feature_names = X.columns.tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_SEED
    )

    if reuse_scaler is not None:
        # The with-temperature family must reuse the exact scaler the deployed
        # champion was fitted with, otherwise the interval models would live in
        # a different feature space than the point predictor.
        scaler = joblib.load(reuse_scaler)
        scaler_path = reuse_scaler
    else:
        scaler = StandardScaler().fit(X_train)
        scaler_path = SCALERS_DIR / f"standard_scaler_{suffix}.joblib"
        joblib.dump(scaler, scaler_path)

    X_train_scaled = pd.DataFrame(
        scaler.transform(X_train), columns=feature_names, index=X_train.index
    )
    X_test_scaled = pd.DataFrame(
        scaler.transform(X_test), columns=feature_names, index=X_test.index
    )

    outliers = consensus_outlier_index(X_train_scaled)
    clean_idx = X_train_scaled.index.difference(outliers)
    X_clean = X_train_scaled.loc[clean_idx]
    y_clean = y_train.loc[clean_idx]

    print(f"\n=== family: {suffix} ===")
    print(f"features : {len(feature_names)}")
    print(f"train    : {len(X_train)}  (consensus outliers removed: {len(outliers)})")
    print(f"test     : {len(X_test)}")

    results = {}
    cv = KFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)

    if reuse_scaler is None:
        # Point predictors are only trained for the new (no-temperature) family;
        # the with-temperature family already has its models from the notebooks.
        for key, estimator in build_estimators().items():
            estimator.fit(X_clean, y_clean)
            metrics = evaluate(estimator, X_test_scaled, y_test)

            cv_scores = cross_val_score(
                estimator.__class__(**estimator.get_params()),
                pd.DataFrame(scaler.transform(X), columns=feature_names),
                y,
                cv=cv,
                scoring="r2",
            )
            metrics["cv_r2_mean"] = float(cv_scores.mean())
            metrics["cv_r2_std"] = float(cv_scores.std())

            path = MODELS_DIR / f"{key}_{suffix}.joblib"
            joblib.dump(estimator, path)
            results[key] = {
                "path": f"models/{path.name}",
                "params": {
                    k: v
                    for k, v in estimator.get_params().items()
                    if k in tuned_params(
                        {
                            "gradient_boosting": "Gradient Boosting",
                            "lightgbm": "LightGBM",
                            "xgboost": "XGBoost",
                        }[key]
                    )
                },
                **metrics,
            }
            print(
                f"  {key:<18} R2={metrics['test_r2']:.4f}  "
                f"RMSE={metrics['test_rmse']:.3f}  MAE={metrics['test_mae']:.3f}"
            )

    # --- 90% prediction interval (conformalized quantile regression) --------
    # The clean training split is divided once more: the quantile regressors
    # never see the calibration rows, which is what makes the conformal
    # coverage guarantee valid.
    X_fit, X_cal, y_fit, y_cal = train_test_split(
        X_clean, y_clean, test_size=0.25, random_state=RANDOM_SEED
    )

    q_lo, q_hi = build_quantile_models()
    q_lo.fit(X_fit, y_fit)
    q_hi.fit(X_fit, y_fit)

    cal_lo = q_lo.predict(X_cal)
    cal_hi = q_hi.predict(X_cal)
    cal_lo, cal_hi = np.minimum(cal_lo, cal_hi), np.maximum(cal_lo, cal_hi)
    correction = conformal_correction(cal_lo, cal_hi, y_cal.values, alpha=0.10)

    lower = q_lo.predict(X_test_scaled)
    upper = q_hi.predict(X_test_scaled)
    # Quantile regressors are fitted independently and can cross on rare rows.
    lower, upper = np.minimum(lower, upper), np.maximum(lower, upper)
    lower, upper = lower - correction, upper + correction

    coverage = float(np.mean((y_test.values >= lower) & (y_test.values <= upper)))
    width = float(np.mean(upper - lower))

    lo_path = MODELS_DIR / f"interval_q05_{suffix}.joblib"
    hi_path = MODELS_DIR / f"interval_q95_{suffix}.joblib"
    joblib.dump(q_lo, lo_path)
    joblib.dump(q_hi, hi_path)

    print(
        f"  interval (90%)     coverage={coverage * 100:.1f}%  "
        f"mean width={width:.2f} MPa  (conformal correction {correction:+.2f} MPa)"
    )

    return {
        "suffix": suffix,
        "feature_names": feature_names,
        "target_column": TARGET_COL,
        "scaler_path": f"scalers/{Path(scaler_path).name}",
        "n_train": int(len(X_train)),
        "n_train_after_outlier_removal": int(len(X_clean)),
        "n_test": int(len(X_test)),
        "n_consensus_outliers_removed": int(len(outliers)),
        "models": results,
        "interval_model": {
            "lower_path": f"models/{lo_path.name}",
            "upper_path": f"models/{hi_path.name}",
            "method": (
                "Conformalized Quantile Regression — Gradient Boosting quantile "
                "regressors (alpha = 0.05 / 0.95) calibrated by split conformal "
                "prediction on a held-out 25% of the training split"
            ),
            "conformal_correction_mpa": correction,
            "n_calibration": int(len(X_cal)),
            "target_coverage": 0.90,
            "empirical_coverage": coverage,
            "mean_interval_width_mpa": width,
        },
    }


def main() -> int:
    no_temp_df = pd.read_excel(DATA_DIR / "Concrete_Data.xls")
    with_temp_df = pd.read_excel(DATA_DIR / "Concrete_Data_with_Temperature.xlsx")

    no_temp = train_family(no_temp_df, "no_temp")
    with_temp = train_family(
        with_temp_df,
        "with_temp",
        reuse_scaler=SCALERS_DIR / "standard_scaler.joblib",
    )

    manifest = {
        "generated_by": "app/scripts/train_no_temperature_models.py",
        "random_seed": RANDOM_SEED,
        "test_size": TEST_SIZE,
        "methodology": (
            "Replicates the notebook pipeline: identical split and seed, "
            "StandardScaler fitted on the training split, consensus outlier "
            "removal (IsolationForest 0.05 + LOF n_neighbors=20, 0.05) applied "
            "to the training split only, and the tuned hyperparameters recorded "
            "in artifacts/model_metadata.json."
        ),
        "families": {"no_temp": no_temp, "with_temp": with_temp},
    }

    out = ARTIFACTS_DIR / "app_training_manifest.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nManifest written to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
