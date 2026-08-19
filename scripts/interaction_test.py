"""Interaction test: drive the real widgets the way a user would.

Complements smoke_test.py, which only checks that pages render.

    .venv/Scripts/python.exe scripts/interaction_test.py
"""

from __future__ import annotations

import sys
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_ROOT))

import pandas as pd  # noqa: E402
from streamlit.testing.v1 import AppTest  # noqa: E402

from src import config, models, usage  # noqa: E402

failures: list[str] = []


def check(condition: bool, message: str) -> None:
    print(("  ok   " if condition else "  FAIL ") + message)
    if not condition:
        failures.append(message)


def run_prediction_flow(family: str) -> None:
    print(f"\n[predict page · {family}]")
    app = AppTest.from_file(str(APP_ROOT / "views/predict.py"), default_timeout=180)
    app.session_state["predict_family"] = family
    app.run()
    check(not app.exception, "page renders")

    # Type a value into the cement box, then predict.
    cement = next(w for w in app.number_input if "Cement" in w.label)
    cement.set_value(450.0).run()
    check(not app.exception, "number input accepted")

    button = next(b for b in app.button if "Predict" in b.label)
    button.click().run()
    check(not app.exception, "predict button")

    has_result = "last_prediction" in app.session_state
    check(has_result, "result stored in session state")
    result = app.session_state["last_prediction"] if has_result else None
    if result:
        check(0 < result["prediction"] < 150, f"plausible value ({result['prediction']:.1f} MPa)")
        check(
            result["lower"] <= result["prediction"] <= result["upper"],
            f"interval brackets prediction [{result['lower']:.1f}, {result['upper']:.1f}]",
        )
        check(
            len(result["values"]) == (9 if family == "with_temp" else 8),
            f"{len(result['values'])} inputs used",
        )
        check(
            result["values"][config.CEMENT] == 450.0,
            "slider value reached the model",
        )

    # The prediction must have been written to the usage log.
    log = usage.load("all")
    check(not log.empty, "usage log written")


def run_extrapolation_warning() -> None:
    print("\n[extrapolation warning]")
    app = AppTest.from_file(str(APP_ROOT / "views/predict.py"), default_timeout=180)
    app.run()
    cement = next(w for w in app.number_input if "Cement" in w.label)
    cement.set_value(1200.0).run()
    check(not app.exception, "extreme input renders")
    check(len(app.warning) > 0, "out-of-range warning shown")
    check(
        any("outside" in str(m.value).lower() for m in app.markdown),
        "per-input range hint flags the outlier",
    )


def run_batch_pipeline() -> None:
    print("\n[batch pipeline]")
    # The upload widget cannot be driven by AppTest, so the scoring path that
    # sits behind it is exercised directly.
    for family in config.FAMILIES:
        spec = models.available_models(family)[0]
        frame = pd.DataFrame(
            [
                {column: 300.0 if "Cement" in column else 180.0 for column in spec.columns},
                {column: 250.0 if "Cement" in column else 200.0 for column in spec.columns},
            ]
        )
        frame[config.AGE] = [28.0, 90.0]
        predictions, lower, upper = models.predict_with_interval(spec, frame)
        check(len(predictions) == 2, f"{family}: two rows scored")
        check(
            bool((lower <= predictions).all() and (predictions <= upper).all()),
            f"{family}: intervals bracket every row",
        )


def run_statistics_page() -> None:
    print("\n[statistics page]")
    app = AppTest.from_file(str(APP_ROOT / "views/statistics.py"), default_timeout=180)
    app.run()
    check(not app.exception, "renders with logged activity")
    check(len(app.metric) >= 6, f"{len(app.metric)} KPI tiles rendered")


def run_measurement_feedback() -> None:
    print("\n[measurement feedback]")
    log = usage.load("all")
    if log.empty:
        check(False, "no records to attach a measurement to")
        return
    record_id = log.iloc[-1]["record_id"]
    check(usage.add_measurement(record_id, 42.5), "measurement stored")
    measured = usage.measured(usage.load("all"))
    check(not measured.empty, "measurement visible in accuracy view")
    check("abs_error" in measured.columns, "error computed")


def main() -> int:
    # Start from a clean log so the assertions are about this run.
    usage.clear()

    for family in config.FAMILIES:
        run_prediction_flow(family)
    run_extrapolation_warning()
    run_batch_pipeline()
    run_statistics_page()
    run_measurement_feedback()

    usage.clear()

    print("\n" + ("FAILED: " + "; ".join(failures) if failures else "ALL INTERACTIONS OK"))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
