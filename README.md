# Concrete Compressive Strength Predictor — Web Application

A Streamlit application that serves the models produced by the five-notebook
research pipeline on the UCI Concrete Compressive Strength dataset
(I-Cheng Yeh, 1998; n = 1,030).

This folder is **self-contained**: it carries its own models, scalers, data,
figures and result tables. It is the only folder that needs to be pushed to
GitHub in order to deploy.

---

## Pages

| Page | What it does |
|---|---|
| **Home** | Headline metrics, the two model families, and the curing-temperature caveat |
| **Prediction** | Single-mix prediction: 8 or 9 inputs, calibrated 90% interval, EN 206 strength class, per-ingredient sensitivity, cross-model comparison, position within the training data, and optional logging of the real measured strength |
| **Batch Prediction** | CSV/Excel upload with fuzzy column matching, whole-file scoring, and result download |
| **Data Analysis** | Interactive EDA — distributions, relationships, correlation, plus the notebooks' publication figures |
| **Model Performance** | Live held-out evaluation of every served model, the research leaderboards, error diagnostics, stability and significance testing |
| **Explainability** | Built-in importance, SHAP, permutation importance, feature ablation, method agreement, and a 1-D / 2-D effect explorer |
| **Usage Statistics** | Activity, prediction profile, and real-world accuracy against user-reported laboratory measurements |

Every chart carries a two-line reading guide: **what this shows**, and an
**insight** recomputed from the numbers currently on screen — so it changes with
the user's inputs rather than repeating a fixed sentence.

## Interface

Dark theme throughout. Inputs are typed numbers with stepper buttons, each
annotated with the training range it came from and flagged in amber when the
value leaves it.

The chart palette is not decorative. It was checked with the data-viz palette
validator against the dark chart surface (`#18222e`) and passes the lightness
band, chroma floor, adjacent-pair colour-blind separation, normal-vision floor
and contrast gates:

```
#00AD83  #3987E5  #C98500  #9085E9  #E66767  #008300
```

The first three additionally clear the stricter all-pairs gate, which is why no
chart plots more than three series at once. Magnitude uses a single-hue teal
ramp, never a rainbow; anything signed uses one fixed pair — blue for positive,
red for negative — on every chart in the application, and reserved status
colours are never reused as a series.

## Model families

Users pick a family based on whether they have a curing-temperature value.

### With curing temperature — 9 inputs

Served straight from the research pipeline.

| Model | File | Test R² | Test RMSE |
|---|---|---|---|
| Gradient Boosting (champion) | `models/final_deployed_model.joblib` | 0.916 | 4.41 MPa |
| LightGBM | `models/lightgbm.joblib` | 0.913 | 4.49 MPa |
| XGBoost | `models/xgboost.joblib` | 0.911 | 4.55 MPa |

Scaler: `scalers/standard_scaler.joblib`.

### Without curing temperature — 8 inputs

Trained by `scripts/train_no_temperature_models.py` on the original UCI
dataset, replicating the notebook methodology exactly: same split
(`test_size=0.2`, `random_state=42`), `StandardScaler` fitted on the training
split only, consensus outlier removal (IsolationForest 0.05 ∩ LOF
`n_neighbors=20`, 0.05) applied to the training split only, and the tuned
hyperparameters recorded in `artifacts/model_metadata.json`.

| Model | File | Test R² | Test RMSE |
|---|---|---|---|
| XGBoost (best overall) | `models/xgboost_no_temp.joblib` | 0.941 | 3.89 MPa |
| LightGBM | `models/lightgbm_no_temp.joblib` | 0.934 | 4.14 MPa |
| Gradient Boosting | `models/gradient_boosting_no_temp.joblib` | 0.933 | 4.17 MPa |

Scaler: `scalers/standard_scaler_no_temp.joblib`.

The 8-input family scores *higher* than the 9-input family. That is expected:
the curing-temperature variable is synthetic, and the strength penalty applied
when it was generated adds variance the mix-design features cannot explain.

### Prediction intervals

Both families get a 90% interval from **conformalized quantile regression**:
Gradient Boosting quantile regressors (α = 0.05 / 0.95) fitted on 75% of the
clean training split, then calibrated by split conformal prediction on the
remaining 25%.

| Family | Target coverage | Empirical coverage | Mean width |
|---|---|---|---|
| With temperature | 90% | 90.3% | 21.2 MPa |
| Without temperature | 90% | 93.7% | 21.4 MPa |

Uncalibrated quantile regressors reached only ~77% coverage, which is why the
conformal step exists. This replaces Notebook 4's 37 MB Random Forest interval
model (88.8% coverage) with two ~700 KB models, keeping the deployment light.

---

## Running locally

### Windows — one click

Double-click **`run.bat`**. It creates the virtual environment if it is
missing, installs `requirements.txt` if anything is absent, starts the server,
and opens the browser at <http://localhost:8501>. Closing the console window
stops the app.

### Any platform — manually

```bash
cd app
py -3.13 -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe -m streamlit run streamlit_app.py
```

On macOS/Linux use `.venv/bin/python` instead.

### Tests

```bash
.venv/Scripts/python.exe scripts/smoke_test.py        # every page renders
.venv/Scripts/python.exe scripts/interaction_test.py  # widgets drive a real prediction
```

### Retraining the 8-input family

```bash
.venv/Scripts/python.exe scripts/train_no_temperature_models.py
```

Rewrites the `*_no_temp` models, the interval models for both families, and
`artifacts/app_training_manifest.json`.

---

## Deploying to Streamlit Community Cloud

1. Push this folder to a public GitHub repository.
2. Go to <https://share.streamlit.io>, sign in with GitHub, and select
   **Create app → Deploy a public app from GitHub**.
3. Set:
   - **Repository**: your repository
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py` (or `app/streamlit_app.py` if the
     folder is nested inside the repository)
   - **Python version**: 3.13
4. Deploy. The first build installs `requirements.txt`, which takes a few
   minutes.

`scikit-learn` is pinned to **1.6.1** because the `.joblib` files were pickled
with it. Do not relax that pin — a different minor version can fail to
unpickle or silently change estimator behaviour.

---

## Important caveat

**Curing temperature is a synthetic variable.** It was generated in Notebook 1
by sampling uniformly in 20–45 °C and applying a band-wise strength penalty
that reflects established curing theory. It is a realistic illustration of a
curing effect for pipeline purposes — not a measured quantity. Any conclusion
involving temperature is methodological, not physical. The 8-input family
exists precisely so the application can be used without it.

---

## Layout

```
app/
├── run.bat                       one-click launcher (Windows)
├── streamlit_app.py              entry point and navigation
├── requirements.txt              pinned dependencies
├── .streamlit/config.toml        theme and server settings
├── assets/                       logo
├── views/                        one file per page
├── src/
│   ├── config.py                 paths, feature definitions, model registry
│   ├── strings.py                every user-facing string and insight template
│   ├── data.py                   dataset and artifact access (cached)
│   ├── models.py                 loading, prediction, intervals, evaluation
│   ├── usage.py                  usage log
│   └── ui.py                     theme, Plotly template, shared components
├── scripts/                      training and test scripts
├── models/  scalers/             served artefacts
├── data/                         datasets (+ runtime usage log, git-ignored)
├── artifacts/  reports/          research metadata and result tables
└── figures/                      publication figures from the notebooks
```

Usage statistics are written to `data/usage_log.csv`. On a free hosting tier
the container filesystem is ephemeral, so that file is a rolling window of
recent activity rather than a permanent database.
