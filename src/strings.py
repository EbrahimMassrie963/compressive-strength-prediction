"""User-facing strings.

Every label, caption and message in the application is defined here rather
than inline in the views, so the wording can be reviewed and changed in one
place.
"""

from __future__ import annotations

STRINGS: dict[str, str] = {
    "app_title": "Concrete Strength Predictor",
    "app_subtitle": (
        "Machine-learning prediction of concrete compressive strength from "
        "mix design"
    ),
    "nav_predict": "Prediction",
    "nav_batch": "Batch Prediction",
    "nav_data": "Data Analysis",
    "nav_performance": "Model Performance",
    "nav_explain": "Explainability",
    "nav_stats": "Usage Statistics",
    "nav_home": "Home",
    "section_main": "Predict",
    "section_insight": "Insight",
    "mpa": "MPa",
    "loading": "Working…",
    "sidebar_footer": "UCI Concrete Compressive Strength · 1,030 samples",
    "home_hero": (
        "Predict the 28-day compressive strength of a concrete mix before "
        "you cast it."
    ),
    "home_intro": (
        "This application serves the models produced by a five-notebook "
        "research pipeline on the UCI Concrete Compressive Strength "
        "dataset. Enter a mix design and receive a predicted strength, a "
        "calibrated 90% prediction interval, the corresponding EN 206 "
        "strength class, and a breakdown of which ingredients drove the "
        "number."
    ),
    "home_kpi_r2": "Best test R²",
    "home_kpi_rmse": "Best test RMSE",
    "home_kpi_models": "Models available",
    "home_kpi_samples": "Training samples",
    "home_start": "Start predicting",
    "home_families_title": "Two model families",
    "home_pages_title": "What is inside",
    "home_page_predict": (
        "Single-mix prediction with a calibrated uncertainty interval and "
        "per-ingredient sensitivity."
    ),
    "home_page_batch": "Upload a CSV of many mixes and download the predictions in one pass.",
    "home_page_data": "Interactive exploration of the 1,030-sample dataset behind the models.",
    "home_page_performance": (
        "Leaderboards, held-out evaluation, residual diagnostics and "
        "stability analysis."
    ),
    "home_page_explain": (
        "SHAP, permutation importance and ablation — three independent "
        "views of what matters."
    ),
    "home_page_stats": (
        "How this deployment is being used, and how accurate it proved on "
        "your own measurements."
    ),
    "home_caveat_title": "One caveat, stated up front",
    "home_caveat": (
        "**Curing temperature is a synthetic variable.** It was generated "
        "in Notebook 1 by sampling uniformly in 20–45 °C and applying a "
        "band-wise strength penalty that reflects established curing "
        "theory. It is a realistic illustration of a curing effect for "
        "pipeline purposes — not a measured quantity. Any conclusion "
        "involving temperature should be read as methodological, not "
        "physical. The 8-input model family exists precisely so you can "
        "work without it."
    ),
    "predict_title": "Predict compressive strength",
    "predict_intro": "Choose a model family, describe the mix, and run the prediction.",
    "family_label": "Model family",
    "model_label": "Algorithm",
    "model_origin": "About this model",
    "inputs_title": "Mix design",
    "binder_group": "Binders",
    "water_group": "Water & admixtures",
    "aggregate_group": "Aggregates",
    "curing_group": "Curing",
    "preset_label": "Load a preset",
    "preset_custom": "Custom",
    "preset_median": "Dataset median mix",
    "preset_high": "High-strength mix",
    "preset_standard": "Standard structural mix",
    "preset_eco": "Eco mix (slag + fly ash)",
    "predict_button": "Predict strength",
    "result_title": "Predicted compressive strength",
    "result_class": "Strength class",
    "result_interval": "90% prediction interval",
    "result_interval_help": (
        "Conformalized quantile regression. On held-out data these "
        "intervals contained the true strength about 90% of the time."
    ),
    "result_model_used": "Model used",
    "derived_title": "Derived mix indicators",
    "wc_ratio": "Water / Cement",
    "wb_ratio": "Water / Binder",
    "total_binder": "Total binder",
    "total_mass": "Total mass",
    "agg_ratio": "Coarse / Fine aggregate",
    "sensitivity_title": "What is driving this prediction",
    "sensitivity_intro": (
        "Each bar is the change in predicted strength when that single "
        "input is raised or lowered by 10%, everything else held fixed — a "
        "local sensitivity analysis of your specific mix."
    ),
    "sensitivity_up": "+10% input",
    "sensitivity_down": "−10% input",
    "sensitivity_delta": "Change in predicted strength (MPa)",
    "compare_title": "How the other models see this mix",
    "compare_intro": (
        "The same mix scored by every model in the selected family. Wide "
        "disagreement is itself a warning sign."
    ),
    "position_title": "Where this mix sits in the training data",
    "position_intro": (
        "Your value against the distribution the model learned from. Values "
        "far outside are extrapolation."
    ),
    "range_warning_title": "Outside the training range",
    "range_warning_body": (
        "These inputs fall outside the range the models were trained on. "
        "The prediction is an extrapolation and should not be trusted "
        "without laboratory confirmation:"
    ),
    "wc_warning": (
        "A water/cement ratio above 0.9 is unusual in this dataset and "
        "typically indicates a very weak mix."
    ),
    "mass_warning": (
        "Total mass per m³ is far from the 2,200–2,600 kg/m³ typical of "
        "normal-weight concrete. Check your quantities."
    ),
    "feedback_title": "Did you measure the real strength?",
    "feedback_intro": (
        "Record the laboratory result for this mix. Logged measurements "
        "feed the accuracy tracking on the Usage Statistics page."
    ),
    "feedback_input": "Measured strength (MPa)",
    "feedback_save": "Save measurement",
    "feedback_saved": "Measurement recorded.",
    "feedback_error": "Absolute error of the prediction",
    "result_stale": (
        "The inputs changed after this prediction was made. Run it again to "
        "refresh."
    ),
    "compare_spread": "Spread between models",
    "percentile_axis": "Percentile within training data",
    "samples_axis": "Samples",
    "count_axis": "Count",
    "no_models": "No models are available for this family.",
    "batch_title": "Batch prediction",
    "batch_intro": "Score an entire CSV of mix designs at once and download the results.",
    "batch_step_template": "1 · Get the template",
    "batch_template_intro": (
        "Download a template with the exact columns expected, pre-filled "
        "with a few example mixes. Column matching is case-insensitive and "
        "tolerates common aliases such as `cement` or `water`."
    ),
    "batch_download_template": "Download template CSV",
    "batch_step_upload": "2 · Upload your file",
    "batch_uploader": "CSV or Excel file",
    "batch_step_results": "3 · Results",
    "batch_rows": "Rows scored",
    "batch_mean": "Mean predicted strength",
    "batch_min": "Weakest mix",
    "batch_max": "Strongest mix",
    "batch_outside": "Rows outside training range",
    "batch_missing_cols": "The file is missing required columns:",
    "batch_mapped": "Column mapping applied",
    "batch_empty": "The uploaded file has no rows.",
    "batch_bad_values": "Rows containing non-numeric or missing values were dropped:",
    "batch_download_results": "Download results CSV",
    "batch_dist_title": "Distribution of predicted strengths",
    "batch_class_title": "Strength classes in this batch",
    "batch_log_note": (
        "Batch runs are recorded in the usage statistics as a single "
        "aggregated entry."
    ),
    "data_title": "Data analysis",
    "data_intro": (
        "The dataset behind every model on this platform: 1,030 concrete "
        "specimens from I-Cheng Yeh's UCI study, extended with the "
        "synthetic curing-temperature variable."
    ),
    "data_tab_overview": "Overview",
    "data_tab_dist": "Distributions",
    "data_tab_rel": "Relationships",
    "data_tab_corr": "Correlation",
    "data_tab_figures": "Research figures",
    "data_rows": "Samples",
    "data_cols": "Variables",
    "data_missing": "Missing values",
    "data_duplicates": "Duplicate rows",
    "data_target_mean": "Mean strength",
    "data_target_range": "Strength range",
    "data_summary_title": "Summary statistics",
    "data_preview_title": "Sample of the raw data",
    "data_select_var": "Variable",
    "data_hist_title": "Distribution",
    "data_box_title": "Spread and outliers",
    "data_scatter_title": "Against compressive strength",
    "data_trendline": "Show trend line",
    "data_colour_by": "Colour by",
    "data_corr_title": "Correlation matrix",
    "data_corr_target": "Correlation with compressive strength",
    "data_corr_note": (
        "Pearson correlation captures linear association only. Age has a "
        "weak linear correlation yet is the single most important predictor "
        "— its relationship with strength is logarithmic, not linear."
    ),
    "data_temp_band_title": "Strength by curing-temperature band",
    "data_figure_group": "Figure group",
    "data_figures_intro": "Publication figures generated by the research notebooks.",
    "perf_title": "Model performance",
    "perf_intro": (
        "Every model on this platform, evaluated on the same held-out "
        "206-sample test split it never saw during training."
    ),
    "perf_tab_live": "Live evaluation",
    "perf_tab_leaderboard": "Research leaderboards",
    "perf_tab_diag": "Error diagnostics",
    "perf_tab_stability": "Stability & significance",
    "perf_live_intro": (
        "Computed in this session by re-running the exact train/test split "
        "(seed 42) used throughout the research — not read from a saved "
        "file."
    ),
    "perf_metric_r2": "R²",
    "perf_metric_rmse": "RMSE (MPa)",
    "perf_metric_mae": "MAE (MPa)",
    "perf_metric_mape": "MAPE (%)",
    "perf_within5": "Within ±5 MPa (%)",
    "perf_select_model": "Inspect a model",
    "perf_pred_vs_actual": "Predicted vs actual",
    "perf_residuals": "Residual distribution",
    "perf_residual_vs_pred": "Residuals vs predicted",
    "perf_cv_leaderboard": "Cross-validated comparison of 12 algorithms",
    "perf_tuned_leaderboard": "Tuned finalists on the test set",
    "perf_full_comparison": "All experimental conditions",
    "perf_learning_curve": "Learning curve",
    "perf_learning_note": (
        "Validation score was still rising when the data ran out: the model "
        "is data-limited, and more samples would likely help."
    ),
    "perf_error_by_range": "Error by strength range",
    "perf_error_range_note": (
        "The model under-predicts high-strength mixes and slightly "
        "over-predicts mid-range ones — a direct consequence of having few "
        "samples above 60 MPa."
    ),
    "perf_worst": "Hardest samples to predict",
    "perf_robustness": "Repeated cross-validation stability",
    "perf_robust_mean": "Mean R² over 50 folds",
    "perf_robust_cv": "Coefficient of variation",
    "perf_robust_range": "R² range across folds",
    "perf_significance": "Statistical significance vs competitors",
    "perf_significance_note": (
        "Paired tests over 50 matched folds. A non-significant result means "
        "the two architectures are statistically indistinguishable on this "
        "dataset — an honest finding, not a failure."
    ),
    "perf_interval_title": "Prediction-interval calibration",
    "perf_interval_target": "Target coverage",
    "perf_interval_actual": "Empirical coverage",
    "perf_interval_width": "Mean interval width",
    "explain_title": "Explainability",
    "explain_intro": (
        "Three independent attribution methods were run against the "
        "champion model. They agree on the answer, which is the point: a "
        "single importance ranking is easy to fool, three agreeing ones are "
        "not."
    ),
    "explain_tab_importance": "Feature importance",
    "explain_tab_shap": "SHAP analysis",
    "explain_tab_agreement": "Method agreement",
    "explain_tab_effects": "Effect explorer",
    "explain_builtin_title": "Built-in importance of the live models",
    "explain_builtin_note": (
        "Read straight from the loaded model objects, so it reflects "
        "exactly what this app serves."
    ),
    "explain_ablation_title": "Feature ablation",
    "explain_ablation_note": (
        "How much test R² collapses when each feature is removed and the "
        "model retrained."
    ),
    "explain_shap_note": (
        "SHAP values decompose each individual prediction into per-feature "
        "contributions, then average their magnitude across the test set."
    ),
    "explain_agreement_note": (
        "Spearman rank correlation between the three importance rankings. "
        "Values above 0.6 indicate the methods tell the same story."
    ),
    "explain_effects_intro": (
        "Sweep one ingredient across its full range while holding the rest "
        "of the mix fixed, and watch the model's response — a "
        "partial-dependence view you control."
    ),
    "explain_sweep_feature": "Ingredient to sweep",
    "explain_baseline": "Baseline mix",
    "explain_baseline_median": "Dataset median",
    "explain_baseline_last": "My last prediction",
    "explain_sweep_title": "Model response",
    "explain_2d_title": "Two-ingredient interaction surface",
    "explain_2d_intro": (
        "Predicted strength across a grid of two ingredients, with the rest "
        "of the mix fixed."
    ),
    "explain_x_axis": "X axis",
    "explain_y_axis": "Y axis",
    "stats_title": "Usage statistics",
    "stats_intro": (
        "Everything predicted through this deployment, and how those "
        "predictions held up against the measurements users reported back."
    ),
    "stats_scope": "Scope",
    "stats_scope_all": "All recorded activity",
    "stats_scope_session": "My session only",
    "stats_empty": (
        "No predictions have been recorded yet. Run one on the Prediction "
        "page and this page fills up."
    ),
    "stats_kpi_total": "Predictions made",
    "stats_kpi_sessions": "Distinct sessions",
    "stats_kpi_batch": "Batch rows",
    "stats_kpi_mean": "Mean prediction",
    "stats_kpi_extrap": "Extrapolated inputs",
    "stats_kpi_feedback": "Measurements",
    "stats_tab_activity": "Activity",
    "stats_tab_predictions": "Prediction profile",
    "stats_tab_accuracy": "Real-world accuracy",
    "stats_tab_log": "Raw log",
    "stats_over_time": "Predictions over time",
    "stats_by_model": "Model usage",
    "stats_by_family": "Family usage",
    "stats_by_source": "Single vs batch",
    "stats_hourly": "Activity by hour of day",
    "stats_pred_dist": "Predicted strength distribution",
    "stats_pred_dist_note": "User predictions overlaid on the training-data distribution.",
    "stats_class_dist": "Strength classes predicted",
    "stats_input_profile": "Average input vs dataset average",
    "stats_input_note": (
        "How the mixes people test here compare with the mixes the models "
        "learned from."
    ),
    "stats_accuracy_empty": (
        "No measured strengths have been reported yet. After casting and "
        "testing a mix, return to the Prediction page and record the "
        "laboratory value — real-world accuracy will be tracked here."
    ),
    "stats_tolerance": "Count a prediction as correct within ±",
    "stats_correct": "Correct predictions",
    "stats_incorrect": "Missed predictions",
    "stats_hit_rate": "Hit rate",
    "stats_live_mae": "MAE on reported measurements",
    "stats_live_rmse": "RMSE on reported measurements",
    "stats_live_bias": "Mean bias",
    "stats_bias_note_over": "On the measurements reported so far the model tends to over-predict.",
    "stats_bias_note_under": "On the measurements reported so far the model tends to under-predict.",
    "stats_bias_note_none": "On the measurements reported so far the model shows no systematic bias.",
    "stats_interval_hit": "Inside the 90% interval",
    "stats_actual_vs_pred": "Reported vs predicted",
    "stats_error_hist": "Error distribution",
    "stats_log_note": (
        "Stored server-side in `data/usage_log.csv`. On a free hosting tier "
        "this file is reset whenever the container restarts, so treat it as "
        "a rolling window rather than a permanent database."
    ),
    "stats_clear": "Clear all recorded activity",
    "stats_clear_confirm": "Yes, delete the log",
    "stats_cleared": "Usage log cleared.",
    "stats_download_log": "Download the log",
}


def t(key: str) -> str:
    """Return the text registered under `key`.

    An unknown key returns the key itself, which makes a missing string
    obvious in the interface instead of raising at render time.
    """
    return STRINGS.get(key, key)
