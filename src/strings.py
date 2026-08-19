"""User-facing strings.

Every label, caption and message in the application is defined here rather
than inline in the views, so the wording can be reviewed and changed in one
place.
"""

from __future__ import annotations

STRINGS: dict[str, str] = {
    # --- dynamic insight templates -----------------------------------------
    "training_range": "Training range",
    "outside_range_short": "outside",
    "none_word": "none",
    "higher_than": "higher than",
    "lower_than": "lower than",
    "evidence_thin": (
        "the model has thin evidence here, so treat the prediction with care"
    ),
    "evidence_solid": "the model has solid evidence in this region",
    "wc_verdict_excellent": "excellent — high-strength territory",
    "wc_verdict_good": "good — normal structural concrete",
    "wc_verdict_moderate": "moderate — expect ordinary strength",
    "wc_verdict_weak": "high — this alone will cap the strength",
    "compare_verdict_tight": (
        "Agreement this tight means the mix sits in well-covered training "
        "territory"
    ),
    "compare_verdict_normal": (
        "That spread is normal and roughly matches the models' own error bars"
    ),
    "compare_verdict_wide": (
        "A spread this wide means the models are extrapolating differently \u2014 "
        "treat any single number as provisional"
    ),
    "what_derived": (
        "Ratios engineers read before they read any prediction. They are "
        "computed from your inputs, not by the model, and they are the "
        "quickest sanity check on a mix design."
    ),
    "insight_derived": (
        "Your water/cement ratio is <strong>{wc}</strong> \u2014 {verdict}. "
        "Total binder is <strong>{binder} kg/m\u00b3</strong>, and the mix "
        "weighs <strong>{mass} kg/m\u00b3</strong> in total; normal-weight "
        "concrete lands between 2,200 and 2,600."
    ),
    "insight_gauge": (
        "At <strong>{value} MPa</strong> this mix reaches class "
        "<strong>{cls}</strong> \u2014 {note}. The 90% interval runs {low} to "
        "{high} MPa, a span of <strong>{width} MPa</strong>: that is the "
        "honest precision of the prediction, and the number to quote when "
        "someone asks how sure you are."
    ),
    "insight_gauge_extrapolated": (
        "One or more inputs sit outside the training range, so the true "
        "uncertainty is wider than the interval shown."
    ),
    "insight_sensitivity": (
        "<strong>{top}</strong> moves this prediction most \u2014 a 10% change "
        "shifts it by {delta} MPa. Increasing these raises predicted strength: "
        "<strong>{helpers}</strong>. Increasing these lowers it: "
        "<strong>{hurters}</strong>. Use it to decide which lever to pull "
        "before you mix anything."
    ),
    "insight_sensitivity_inert": (
        "<strong>{inert}</strong> does not move this prediction at all at "
        "these values — a tree ensemble only responds where it placed a "
        "split, so nudging them here changes nothing."
    ),
    "insight_compare": (
        "The {n} models return {low} to {high} MPa, a spread of "
        "<strong>{spread} MPa</strong>. {verdict}."
    ),
    "insight_percentile": (
        "Your most unusual input is <strong>{feature}</strong>, at the "
        "<strong>{percentile}th percentile</strong> \u2014 {comparison} {other}% "
        "of the training mixes. {edges} of your inputs sit in the outer 5% of "
        "their range, where the model is least tested."
    ),
    "insight_position_hist": (
        "<strong>{nearby}</strong> of the {total} training specimens have a "
        "{feature} within 10% of your {value} \u2014 {verdict}."
    ),

    # --- shared insight fragments -------------------------------------------
    "direction_up": "rises with",
    "direction_down": "falls as you add",
    "direction_higher": "higher",
    "direction_lower": "lower",
    "bias_under": "reads low (under-predicts)",
    "bias_over": "reads high (over-predicts)",
    "bias_none": "shows no systematic bias",
    "corr_strength_strong": "a strong linear link",
    "corr_strength_moderate": "a moderate linear link",
    "corr_strength_weak": "almost no linear link \u2014 which does not mean no link at all, only that a straight line cannot capture it",
    "stability_high": "that is a very stable model",
    "stability_low": "that is more variance than you want to see",
    "learning_more_helps": "the curve was still climbing, so more data would still buy accuracy",
    "learning_plateau": "the curve has flattened, so more of the same data would add little",
    "sweep_monotone": "the response keeps climbing to the end of the range",
    "sweep_peak": "the response peaks mid-range rather than climbing forever",
    "agreement_yes": "All three methods put <strong>{feature}</strong> first",
    "agreement_no": "The three methods disagree on the single top feature",
    "stats_dist_note_shifted": (
        "Users are exploring mixes stronger or weaker than the training "
        "population, which is where predictions get less certain"
    ),
    "stats_dist_note_aligned": (
        "Users are testing mixes much like the training population, which is "
        "where the model is most reliable"
    ),

    # --- per-chart insights --------------------------------------------------
    "insight_batch_dist": (
        "The {span} MPa spread across this batch centres on <strong>{mean} "
        "MPa</strong> (\u00b1{std} standard deviation), running from {low} to "
        "{high} MPa."
    ),
    "insight_batch_class": (
        "Most of the batch \u2014 <strong>{n} of {total}</strong> mixes \u2014 lands "
        "in class <strong>{cls}</strong>, spread over {classes} classes in "
        "total. {outside} rows used inputs outside the training range."
    ),
    "insight_target_hist": (
        "Strength averages <strong>{mean} MPa</strong> (median {median}) and "
        "runs from {low} to {high}. Only <strong>{share}%</strong> of "
        "specimens exceed 60 MPa, which is exactly why the models are least "
        "accurate at the high end."
    ),
    "insight_var_hist": (
        "{name} has a median of <strong>{median}</strong> and spans {low} to "
        "{high}. <strong>{zeros}%</strong> of mixes leave it out entirely "
        "\u2014 {note}."
    ),
    "insight_var_zeros": (
        "it is an optional ingredient, so the model has to learn both its "
        "presence and its absence"
    ),
    "insight_var_nozeros": "it is present in nearly every mix",
    "insight_scatter": (
        "{name} shows {strength} with strength (r = <strong>{r}</strong>): "
        "strength {direction} it. The curve is the fitted trend \u2014 the "
        "vertical scatter around it is everything the other ingredients are "
        "doing."
    ),
    "insight_temp_bands": (
        "Mean strength falls from <strong>{coolest} MPa</strong> in the "
        "coolest band to <strong>{hottest} MPa</strong> in the hottest, a "
        "{drop} MPa ({pct}%) drop. The monotone decline confirms the "
        "synthetic penalty was injected as specified."
    ),
    "insight_corr_matrix": (
        "The strongest relationship in the whole matrix is <strong>{a}</strong> "
        "against <strong>{b}</strong> at r = <strong>{r}</strong>. Strong "
        "pairs among the inputs mean the ingredients are not independent "
        "\u2014 changing one in practice usually changes another."
    ),
    "insight_corr_target": (
        "<strong>{top}</strong> has the strongest linear tie to strength "
        "(r = {r}). Positive drivers: {positive}. Negative drivers: {negative}."
    ),
    "insight_live_r2": (
        "<strong>{best}</strong> leads with R\u00b2 = <strong>{r2}</strong> and "
        "an RMSE of {rmse} MPa, and lands within \u00b15 MPa of the truth on "
        "{within}% of held-out specimens. The whole field spans only {spread} "
        "R\u00b2, so model choice matters far less here than data quality."
    ),
    "insight_residuals": (
        "<strong>{model}</strong> is off by <strong>{mae} MPa</strong> on "
        "average and lands within \u00b15 MPa on {within}% of specimens. Mean "
        "residual is {bias} MPa, so the model {direction}. Its worst single "
        "miss on this split is {worst} MPa."
    ),
    "insight_cv_board": (
        "Tree ensembles dominate: <strong>{best}</strong> tops the {n} "
        "algorithms at R\u00b2 = {r2}, against {linear} for linear regression. "
        "The gap is the whole argument for a non-linear model on this problem."
    ),
    "insight_learning": (
        "At full data the train\u2013validation gap is <strong>{gap}</strong> "
        "R\u00b2, and the last increment of data added {gain} R\u00b2 \u2014 "
        "{verdict}."
    ),
    "insight_error_range": (
        "The model is weakest on <strong>{worst}</strong> mixes (RMSE {worst_rmse} "
        "MPa) and strongest on <strong>{best}</strong> (RMSE {best_rmse}). In "
        "the weak band the mean error is {bias} MPa, so it {direction} there "
        "\u2014 useful to know before trusting a high-strength quote."
    ),
    "insight_robustness": (
        "Mean R\u00b2 of <strong>{mean}</strong> with a coefficient of "
        "variation of {cv}%, and no fold worse than {low} or better than "
        "{high} \u2014 {verdict}."
    ),
    "insight_significance": (
        "The champion significantly beats <strong>{beaten} of {total}</strong> "
        "competitors at p &lt; 0.05. Statistically tied with: {tied}. A tie is "
        "an honest result \u2014 it means the architectures are "
        "indistinguishable on this dataset, not that the test failed."
    ),
    "insight_builtin": (
        "<strong>{model}</strong> puts {share} of its total importance on "
        "<strong>{top}</strong> alone. The top three ({top3}) account for "
        "{top3share}, while <strong>{least}</strong> contributes least."
    ),
    "insight_ablation": (
        "Deleting <strong>{top}</strong> costs <strong>{drop}</strong> R\u00b2 "
        "\u2014 the model falls to {remaining} without it. Deleting "
        "<strong>{least}</strong> costs only {least_drop}, so it is nearly "
        "redundant given the others."
    ),
    "insight_shap": (
        "<strong>{top}</strong> moves an individual prediction by "
        "<strong>{mpa} MPa</strong> on average, ahead of {second} at "
        "{second_mpa} MPa. Unlike a correlation, this is measured on the "
        "model's actual behaviour, one specimen at a time."
    ),
    "insight_agreement": (
        "{verdict}. Per method \u2014 {detail}. Three independent methods "
        "agreeing is much harder to fool than any single importance ranking."
    ),
    "insight_sweep": (
        "Sweeping <strong>{feature}</strong> alone moves the prediction by "
        "<strong>{swing} MPa</strong> (from {low} to {high}), peaking around "
        "<strong>{best}</strong> \u2014 {shape}."
    ),
    "insight_surface": (
        "Across this grid the prediction ranges from {low} to <strong>{high} "
        "MPa</strong>, with the strongest corner at {x} \u2248 {best_x} and "
        "{y} \u2248 {best_y}. The shape of the gradient shows whether the two "
        "ingredients reinforce each other or work independently."
    ),
    "insight_stats_time": (
        "<strong>{total}</strong> predictions over {days} days, peaking at "
        "{peak} in a single interval around {when}."
    ),
    "insight_stats_usage": (
        "<strong>{model}</strong> is the most used model at {share}% of runs, "
        "the {family} family is preferred, and activity peaks around "
        "<strong>{hour}:00 UTC</strong>."
    ),
    "insight_stats_dist": (
        "Predictions here average <strong>{user_mean} MPa</strong> against "
        "{data_mean} MPa in the training data \u2014 {direction}. {note}."
    ),
    "insight_stats_class": (
        "<strong>{cls}</strong> is the most requested class, {n} times "
        "({share}% of all predictions), across {distinct} distinct classes."
    ),
    "insight_stats_input": (
        "Users push <strong>{high}</strong> hardest, at {high_ratio}\u00d7 the "
        "dataset average, and use the least <strong>{low}</strong> at "
        "{low_ratio}\u00d7. Ratios far from 1.0 mark where real usage drifts "
        "away from the training data."
    ),
    "insight_stats_accuracy": (
        "On <strong>{n}</strong> reported measurements the model lands within "
        "\u00b1{tolerance} MPa <strong>{hit}%</strong> of the time, with a mean "
        "absolute error of {mae} MPa. Average signed error is {bias} MPa, so "
        "in the field it {direction}."
    ),

    # --- chart explanations -------------------------------------------------
    "explain_what": "What this shows",
    "explain_insight": "Insight",
    "what_gauge": (
        "The predicted strength on a dial of EN 206 strength classes. The "
        "bands run dark to bright as the class rises, the violet needle is "
        "this mix, and the figure below it is the range the model is 90% "
        "confident the real cylinder test would land in."
    ),
    "what_sensitivity": (
        "Each ingredient raised and lowered by 10% on its own, with the rest "
        "of the mix frozen, and the resulting change in predicted strength. "
        "It is a what-if run on your exact mix, not a global average."
    ),
    "what_compare": (
        "Your mix scored by every algorithm in the selected family. They were "
        "trained on the same data but disagree in different regions of it."
    ),
    "what_percentile": (
        "Where each of your inputs sits inside the 1,030 training mixes. 50% "
        "is the median mix; 0% or 100% means you are at the edge of what the "
        "model has ever seen."
    ),
    "what_position_hist": (
        "The full training distribution of one ingredient, with your value "
        "marked. Dense regions are where the model has the most evidence."
    ),
    "what_batch_dist": (
        "How the predicted strengths in your uploaded file are spread out."
    ),
    "what_batch_class": (
        "Your batch sorted into EN 206 strength classes \u2014 the "
        "specification each mix would satisfy."
    ),
    "what_target_hist": (
        "The distribution of measured compressive strength across all 1,030 "
        "laboratory specimens. This is the quantity every model predicts."
    ),
    "what_var_hist": (
        "How often each value of the selected variable occurs in the dataset."
    ),
    "what_var_box": (
        "The same variable as a box plot: the box holds the middle half of "
        "the data, the line is the median, and the dots beyond the whiskers "
        "are statistical outliers."
    ),
    "what_scatter": (
        "Every specimen plotted as the selected ingredient against its "
        "measured strength, with a fitted quadratic trend."
    ),
    "what_temp_bands": (
        "Mean measured strength in each curing-temperature band \u2014 the "
        "check that the synthetic temperature variable behaves as designed."
    ),
    "what_corr_matrix": (
        "Pearson correlation between every pair of variables. Blue is a "
        "positive association, red a negative one, and the neutral grey "
        "midpoint means no linear relationship. The same two colours mean the "
        "same two things on every signed chart in this application."
    ),
    "what_corr_target": (
        "Each ingredient's linear correlation with compressive strength, "
        "ranked."
    ),
    "what_live_r2": (
        "R\u00b2 of every served model on the same held-out test split, "
        "computed in this session rather than read from a file. The "
        "highlighted bars are the champion of each family."
    ),
    "what_pred_actual": (
        "Each held-out specimen plotted as its measured strength against the "
        "model's prediction. The diagonal is a perfect prediction; distance "
        "from it is the error."
    ),
    "what_resid_hist": (
        "The distribution of residuals (measured minus predicted). A "
        "well-behaved model gives a narrow bell centred on zero."
    ),
    "what_resid_vs_pred": (
        "Residuals against the predicted value. A flat, shapeless band means "
        "the error does not depend on the size of the prediction; any tilt "
        "or fan is systematic bias."
    ),
    "what_cv_board": (
        "Twelve algorithms compared under identical 5-fold cross-validation "
        "during the research phase. The bars show mean R\u00b2, the whiskers "
        "its spread across folds."
    ),
    "what_learning": (
        "Training and validation R\u00b2 as the training set grows. The gap "
        "between the curves is overfitting; the slope of the validation curve "
        "at the right edge says whether more data would still help."
    ),
    "what_error_range": (
        "Prediction error split by how strong the specimen actually was. It "
        "answers where the model is reliable and where it is not."
    ),
    "what_bias_range": (
        "The average signed error per strength range. Positive means the "
        "model reads low (under-predicts), negative means it reads high."
    ),
    "what_robustness": (
        "The champion's R\u00b2 across 50 cross-validation folds: the full "
        "range, the 95% confidence interval, and the mean. A tight interval "
        "means the score is not an accident of one lucky split."
    ),
    "what_significance": (
        "The champion's mean R\u00b2 minus each competitor's, over 50 matched "
        "folds, with the paired t-test p-value. Highlighted bars are "
        "statistically significant differences."
    ),
    "what_builtin": (
        "How much each input the selected model actually uses, read straight "
        "from the fitted model object."
    ),
    "what_ablation": (
        "How much test R\u00b2 collapses when a feature is deleted and the "
        "model retrained from scratch. The bluntest possible importance test."
    ),
    "what_shap": (
        "Mean absolute SHAP value: the average number of MPa each feature "
        "moves an individual prediction, in either direction."
    ),
    "what_agreement": (
        "The three importance methods side by side, each rescaled to its own "
        "maximum so the rankings can be compared rather than the units."
    ),
    "what_sweep": (
        "One ingredient swept across its full training range while the rest "
        "of the mix stays fixed, tracing the model's response curve."
    ),
    "what_surface": (
        "Predicted strength over a grid of two ingredients, everything else "
        "held constant. Bright regions are strong mixes."
    ),
    "what_stats_time": "Prediction volume through this deployment over time.",
    "what_stats_model": "Which algorithms people actually run.",
    "what_stats_family": (
        "Whether users have a curing-temperature value to work with, or not."
    ),
    "what_stats_source": "Single-mix predictions against uploaded batches.",
    "what_stats_hourly": "When the system is used, by hour of day in UTC.",
    "what_stats_dist": (
        "Predictions made here, overlaid on the distribution of the training "
        "data. Both are drawn as densities so they compare on one scale."
    ),
    "what_stats_class": "Which EN 206 strength classes users are designing for.",
    "what_stats_input": (
        "Average value of each input across all predictions, divided by the "
        "dataset average. 1.0 means users test mixes just like the training "
        "data."
    ),
    "what_stats_accuracy": (
        "Every laboratory measurement users reported back, plotted against "
        "what the model had predicted. The diagonal is a perfect call."
    ),
    "what_stats_error": (
        "The distribution of prediction error on those reported measurements."
    ),

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
