"""Central configuration: paths, feature definitions and the model registry."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = APP_ROOT / "data"
MODELS_DIR = APP_ROOT / "models"
SCALERS_DIR = APP_ROOT / "scalers"
ARTIFACTS_DIR = APP_ROOT / "artifacts"
REPORTS_DIR = APP_ROOT / "reports"
FIGURES_DIR = APP_ROOT / "figures"

DATASET_WITH_TEMP = DATA_DIR / "Concrete_Data_with_Temperature.xlsx"
DATASET_NO_TEMP = DATA_DIR / "Concrete_Data.xls"

USAGE_LOG = DATA_DIR / "usage_log.csv"

TARGET_COL = "Concrete compressive strength(MPa, megapascals) "

RANDOM_SEED = 42
TEST_SIZE = 0.2


# ---------------------------------------------------------------------------
# Features
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Feature:
    """One model input, with everything the UI needs to render it."""

    key: str
    column: str          # exact column name expected by the fitted scalers
    label: str
    unit: str
    icon: str
    step: float
    decimals: int
    help_text: str
    csv_aliases: tuple[str, ...] = field(default_factory=tuple)


CEMENT = "Cement (component 1)(kg in a m^3 mixture)"
SLAG = "Blast Furnace Slag (component 2)(kg in a m^3 mixture)"
FLY_ASH = "Fly Ash (component 3)(kg in a m^3 mixture)"
WATER = "Water  (component 4)(kg in a m^3 mixture)"
SUPERPLASTICIZER = "Superplasticizer (component 5)(kg in a m^3 mixture)"
COARSE_AGG = "Coarse Aggregate  (component 6)(kg in a m^3 mixture)"
FINE_AGG = "Fine Aggregate (component 7)(kg in a m^3 mixture)"
AGE = "Age (day)"
TEMPERATURE = "Curing Temperature (Celsius)"


FEATURES: tuple[Feature, ...] = (
    Feature(
        key="cement",
        column=CEMENT,
        label="Cement",
        unit="kg/m³",
        icon="🏗️",
        step=5.0,
        decimals=1,
        help_text=(
            "Portland cement content — the primary binder and the strongest "
            "positive driver of strength."
        ),
        csv_aliases=("cement", "cement (component 1)"),
    ),
    Feature(
        key="slag",
        column=SLAG,
        label="Blast Furnace Slag",
        unit="kg/m³",
        icon="⚙️",
        step=5.0,
        decimals=1,
        help_text=(
            "Ground granulated blast-furnace slag: a supplementary binder that "
            "builds late strength."
        ),
        csv_aliases=("slag", "blast furnace slag", "bfs"),
    ),
    Feature(
        key="fly_ash",
        column=FLY_ASH,
        label="Fly Ash",
        unit="kg/m³",
        icon="💨",
        step=5.0,
        decimals=1,
        help_text=(
            "Pozzolanic by-product of coal combustion; improves workability, "
            "slows early strength gain."
        ),
        csv_aliases=("fly ash", "flyash", "ash"),
    ),
    Feature(
        key="water",
        column=WATER,
        label="Water",
        unit="kg/m³",
        icon="💧",
        step=2.0,
        decimals=1,
        help_text=(
            "Mixing water. More water means easier placement but markedly "
            "lower strength."
        ),
        csv_aliases=("water",),
    ),
    Feature(
        key="superplasticizer",
        column=SUPERPLASTICIZER,
        label="Superplasticizer",
        unit="kg/m³",
        icon="🧪",
        step=0.5,
        decimals=2,
        help_text=(
            "Chemical admixture that keeps the mix workable at a low water "
            "content."
        ),
        csv_aliases=("superplasticizer", "plasticizer", "sp"),
    ),
    Feature(
        key="coarse_agg",
        column=COARSE_AGG,
        label="Coarse Aggregate",
        unit="kg/m³",
        icon="🧱",
        step=10.0,
        decimals=1,
        help_text="Gravel or crushed stone — the load-bearing skeleton of the mix.",
        csv_aliases=("coarse aggregate", "coarse agg", "gravel"),
    ),
    Feature(
        key="fine_agg",
        column=FINE_AGG,
        label="Fine Aggregate",
        unit="kg/m³",
        icon="⏳",
        step=10.0,
        decimals=1,
        help_text="Sand, which fills the voids between coarse particles.",
        csv_aliases=("fine aggregate", "fine agg", "sand"),
    ),
    Feature(
        key="age",
        column=AGE,
        label="Age",
        unit="days",
        icon="📅",
        step=1.0,
        decimals=0,
        help_text=(
            "Curing age at testing. Strength grows steeply up to ~28 days, "
            "then slowly."
        ),
        csv_aliases=("age", "age (day)", "age_days"),
    ),
    Feature(
        key="temperature",
        column=TEMPERATURE,
        label="Curing Temperature",
        unit="°C",
        icon="🌡️",
        step=0.5,
        decimals=1,
        help_text=(
            "Ambient curing temperature. NOTE: synthetic feature — see the "
            "caveat on the home page."
        ),
        csv_aliases=("curing temperature", "temperature", "temp"),
    ),
)

FEATURES_BY_KEY = {f.key: f for f in FEATURES}
FEATURES_BY_COLUMN = {f.column: f for f in FEATURES}

NO_TEMP_COLUMNS = [f.column for f in FEATURES if f.key != "temperature"]
WITH_TEMP_COLUMNS = [f.column for f in FEATURES]


# ---------------------------------------------------------------------------
# Model registry
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ModelSpec:
    key: str
    name: str
    family: str                    # "with_temp" | "no_temp"
    model_path: str
    scaler_path: str
    origin: str
    is_champion: bool = False
    requires_package: str | None = None

    @property
    def columns(self) -> list[str]:
        return WITH_TEMP_COLUMNS if self.family == "with_temp" else NO_TEMP_COLUMNS


FAMILIES = {
    "with_temp": {
        "label": "With curing temperature — 9 inputs",
        "desc": (
            "The full research pipeline. Models trained on the extended dataset "
            "that adds a curing-temperature variable to the 8 UCI mix variables."
        ),
        "interval_lower": "models/interval_q05_with_temp.joblib",
        "interval_upper": "models/interval_q95_with_temp.joblib",
        "scaler": "scalers/standard_scaler.joblib",
        "dataset": DATASET_WITH_TEMP,
    },
    "no_temp": {
        "label": "Without curing temperature — 8 inputs",
        "desc": (
            "Trained on the original UCI dataset only. Use this when no curing "
            "temperature was recorded — it avoids inventing a value the model "
            "would act on."
        ),
        "interval_lower": "models/interval_q05_no_temp.joblib",
        "interval_upper": "models/interval_q95_no_temp.joblib",
        "scaler": "scalers/standard_scaler_no_temp.joblib",
        "dataset": DATASET_NO_TEMP,
    },
}


MODEL_REGISTRY: tuple[ModelSpec, ...] = (
    ModelSpec(
        key="gb_with_temp",
        name="Gradient Boosting — Champion",
        family="with_temp",
        model_path="models/final_deployed_model.joblib",
        scaler_path="scalers/standard_scaler.joblib",
        origin="Notebook 4 champion: tuned Gradient Boosting, consensus outliers removed.",
        is_champion=True,
    ),
    ModelSpec(
        key="lgbm_with_temp",
        name="LightGBM",
        family="with_temp",
        model_path="models/lightgbm.joblib",
        scaler_path="scalers/standard_scaler.joblib",
        origin="Notebook 3 tuned LightGBM — the strongest model in cross-validation.",
        requires_package="lightgbm",
    ),
    ModelSpec(
        key="xgb_with_temp",
        name="XGBoost",
        family="with_temp",
        model_path="models/xgboost.joblib",
        scaler_path="scalers/standard_scaler.joblib",
        origin="Notebook 3 tuned XGBoost — best tuning-stage cross-validated score.",
        requires_package="xgboost",
    ),
    ModelSpec(
        key="gb_no_temp",
        name="Gradient Boosting",
        family="no_temp",
        model_path="models/gradient_boosting_no_temp.joblib",
        scaler_path="scalers/standard_scaler_no_temp.joblib",
        origin=(
            "Same tuned architecture and outlier policy, retrained on the 8 "
            "original variables."
        ),
    ),
    ModelSpec(
        key="lgbm_no_temp",
        name="LightGBM",
        family="no_temp",
        model_path="models/lightgbm_no_temp.joblib",
        scaler_path="scalers/standard_scaler_no_temp.joblib",
        origin="Tuned LightGBM retrained on the 8 original variables.",
        requires_package="lightgbm",
    ),
    ModelSpec(
        key="xgb_no_temp",
        name="XGBoost — Best without temperature",
        family="no_temp",
        model_path="models/xgboost_no_temp.joblib",
        scaler_path="scalers/standard_scaler_no_temp.joblib",
        origin=(
            "Tuned XGBoost retrained on the 8 original variables — highest test "
            "R² of any model here."
        ),
        is_champion=True,
        requires_package="xgboost",
    ),
)

MODELS_BY_KEY = {m.key: m for m in MODEL_REGISTRY}


def models_for_family(family: str) -> list[ModelSpec]:
    return [m for m in MODEL_REGISTRY if m.family == family]


# ---------------------------------------------------------------------------
# Concrete strength classes (EN 206 / Eurocode 2, cylinder characteristic strength)
# ---------------------------------------------------------------------------
STRENGTH_CLASSES: tuple[tuple[float, str, str], ...] = (
    (0, "Below C12/15", "Not structural — very low strength"),
    (12, "C12/15", "Blinding, non-structural fill"),
    (16, "C16/20", "Light structural, foundations in dry conditions"),
    (20, "C20/25", "General reinforced concrete"),
    (25, "C25/30", "Standard structural — slabs, beams, columns"),
    (30, "C30/37", "Exposed structural elements, bridge decks"),
    (35, "C35/45", "High-durability structural work"),
    (40, "C40/50", "Heavily loaded columns, precast elements"),
    (45, "C45/55", "High-performance concrete"),
    (50, "C50/60", "High-strength concrete"),
    (60, "C55/67 +", "Very high-strength / special applications"),
)


def strength_class(mpa: float) -> tuple[str, str]:
    """Map a predicted MPa value to an EN 206 strength class and a usage note."""
    chosen = STRENGTH_CLASSES[0]
    for entry in STRENGTH_CLASSES:
        if mpa >= entry[0]:
            chosen = entry
    return chosen[1], chosen[2]
