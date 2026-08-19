"""Headless smoke test: render every page and fail on any exception.

    .venv/Scripts/python.exe scripts/smoke_test.py
"""

from __future__ import annotations

import sys
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_ROOT))

from streamlit.testing.v1 import AppTest  # noqa: E402

PAGES = [
    "views/home.py",
    "views/predict.py",
    "views/batch.py",
    "views/data_analysis.py",
    "views/performance.py",
    "views/explain.py",
    "views/statistics.py",
]


def run(page: str) -> list[str]:
    app = AppTest.from_file(str(APP_ROOT / page), default_timeout=180)
    app.run()
    return [f"{e.value}" for e in app.exception]


def main() -> int:
    failures = 0
    for page in PAGES:
        errors = run(page)
        status = "FAIL" if errors else "ok"
        print(f"{page:<28} {status}")
        for error in errors:
            failures += 1
            print(f"    {error}")

    # A prediction actually produces a number, in both families.
    from src import config, models  # noqa: PLC0415

    for family in config.FAMILIES:
        spec = models.available_models(family)[0]
        values = {
            column: float(models.data.feature_stats("with_temp").loc[column, "median"])
            for column in spec.columns
        }
        frame = models.to_frame(values, spec.columns)
        prediction = models.predict(spec, frame)[0]
        lower, upper = models.predict_interval(family, frame)
        assert lower[0] <= prediction <= upper[0], f"interval does not bracket {family}"
        print(f"[predict] {family:<12} {prediction:6.2f} MPa  [{lower[0]:.2f}, {upper[0]:.2f}]")

    print("\nFAILED" if failures else "\nALL PAGES OK")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
