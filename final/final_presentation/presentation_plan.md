# Final Presentation Plan

This plan has been checked against:

- `final/final_presentation/Winter 2026 Advanced Data Analytics Group Project Presentation Requirements.pdf`
- `README.md`
- `project_evaluation.txt`
- proposal and midterm feedback
- `final/final_report/*.tex`
- committed RQ2 outputs and figures
- locally rerun RQ1 outputs and figures on April 9, 2026
- locally rerun RQ3 outputs and figures on April 9, 2026

Current repo-status takeaway:

- RQ1 is presentation-ready from code, outputs, and figures.
- RQ2 is the strongest and most complete section in the repo.
- RQ3 is also presentation-ready from code, outputs, and figures.

## Requirements Coverage Check

The presentation PDF requires the following content. This plan covers each item explicitly.

- Introduction: Slides 1, 2, and 3
- Motivation: Slide 3
- Dataset statistics: Slides 2 and 5
- Methodology: Slides 6, 7, 8, 9, 10, and 11
- Experiment results for three research questions: Slides 7 through 11
- Discussion and limitations: Slide 12, including why the chosen outcome measures and evaluation metrics are the most informative
- Conclusion: Slide 13
- Less than 15 minutes: timed plan below totals about 14 minutes 55 seconds
- Each member must present: speaker allocation below assigns material to all three members
- Conclusions supported by exact numbers: exact values are included throughout the plan

## Presentation-Wide Requirements

These are non-negotiable details from the PDF and should be treated as a final checklist.

- Put `Group 10`, all member names, and the presentation title on Slide 1.
- Export the final deck as PDF for submission.
- Submit both the slide PDF and the presentation video.
- Keep the video under 15 minutes.
- Put slide numbers on every slide.
- Keep font size at least 18.
- Check all figures for readability and blurriness before exporting.
- Do not overload slides with text or too many findings at once.
- Use exact numbers whenever possible instead of saying “around” or “roughly.”
- Make each slide self-explanatory for someone who has not read the report.

## Balanced Presenter Allocation

This version is still reasonably balanced after adding a short shared overview slide near the start.

- Adam: about 4 minutes 42 seconds
- Harsh: about 5 minutes 7 seconds
- Chris: about 5 minutes 6 seconds

Recommended split:

- Adam
  - Slide 1
  - Slide 3
  - Slide 8
  - first part of Slide 9
  - Adam section of Slide 12
- Harsh
  - first half of Slide 2
  - Slide 5
  - Slide 6
  - Slide 7
  - first part of Slide 11
  - Harsh section of Slide 12
- Chris
  - second half of Slide 2
  - Slide 4
  - second part of Slide 9
  - Slide 10
  - second part of Slide 11
  - Slide 13
  - Chris section of Slide 12

Because Slides 2, 9, 11, and 12 are split, the team should rehearse the handoffs so they feel intentional rather than abrupt.

## Timing Summary

- Slide 1: 0:40
- Slide 2: 0:50
- Slide 3: 1:05
- Slide 4: 1:10
- Slide 5: 1:10
- Slide 6: 1:10
- Slide 7: 1:20
- Slide 8: 1:30
- Slide 9: 1:20
- Slide 10: 1:20
- Slide 11: 1:25
- Slide 12: 1:15
- Slide 13: 0:40

Total planned time: about 14:55

The revised script drafts below are intentionally fuller than the earlier version. At a normal presentation pace, with brief pauses for slide changes and handoffs, they should land much closer to the full 15-minute window without forcing anyone to rush.

## Per-Speaker Timing Plan

- Adam
  - Slide 1: 0:40
  - Slide 3: 1:05
  - Slide 8: 1:30
  - Slide 9, setup and model explanation: 0:35
  - Slide 12, Adam section: 0:52
  - Total: about 4:42
- Harsh
  - Slide 2, dataset overview: 0:25
  - Slide 5: 1:10
  - Slide 6: 1:10
  - Slide 7: 1:20
  - Slide 11, setup and evaluation logic: 0:35
  - Slide 12, Harsh section: 0:27
  - Total: about 5:07
- Chris
  - Slide 2, research-problem overview: 0:25
  - Slide 4: 1:10
  - Slide 9, results interpretation: 0:45
  - Slide 10: 1:20
  - Slide 11, results takeaway: 0:50
  - Slide 12, Chris section: 0:16
  - Slide 13: 0:40
  - Total: about 5:06

## Slide 1 - Title and Thesis
Time: 0:40
Suggested lead: Adam

A) Slideshow visuals

- Clean title slide with project title, `Group 10`, member names, course, and date.
- Put slide number on the bottom right.
- Background should be one strong NYC taxi visual only: skyline, yellow cab close-up, or a muted NYC map.
- Add a one-line thesis under the title:
  - COVID changed NYC yellow taxi behavior, but the recovery was uneven across tipping, airport demand, and payment choice.

B) Script targets

- Introduce the project in one sentence.
- Frame the whole presentation around one big question.
- Preview the three research questions at a high level.

C) Draft spoken version

“We are Group 10, and our project studies how COVID-19 changed New York City yellow taxi behavior before, during, and after the main disruption period. We study three dimensions of that change: tipping behavior, airport-related recovery, and the shift from cash to cashless payments. Our central question is not simply whether taxi demand fell, because that part is obvious. What matters is which behaviors returned to baseline and which remained changed after recovery. Taken together, these three questions let us compare one behavior that mostly reverted, one that recovered unevenly, and one that appears to have shifted more persistently.”

## Slide 2 - Dataset and Research Problem Overview
Time: 0:50
Suggested lead: shared, Harsh then Chris

A) Slideshow visuals

- Use a two-part overview slide.
- Left side: one compact dataset box:
  - NYC TLC yellow taxi trip records
  - January 2019 through December 2023
  - 60 monthly parquet files
  - 218,118,168 trips
- Right side: one compact research-problem box:
  - which taxi behaviors changed during COVID?
  - which returned to baseline?
  - which stayed changed through recovery?
- Add a small footer line:
  - trip-level data supports behavioral analysis, not only demand analysis

B) Script targets

- Introduce the dataset at a high level.
- Frame the research problem before the motivation slide.
- Bridge cleanly into why the problem matters.

C) Draft spoken version

“Harsh: Before getting into the motivation, here is the project at a glance. We use NYC TLC yellow taxi trip records from January 2019 through December 2023, which gives us 60 monthly parquet files and about 218.1 million trips. Chris: The research problem is to understand not just whether taxi activity changed during COVID, but which specific behaviors changed, whether they recovered, and whether some of those changes persisted. That is the question that connects the rest of the presentation.”

## Slide 3 - Why This Problem Matters
Time: 1:05
Suggested lead: Adam

A) Slideshow visuals

- Left side: 3 short motivation bullets.
- Right side: simple icon row for tipping, airports, and payment method.
- Keep text minimal and large.
- Add one small footer note:
  - yellow taxi data lets us study behavior inside trips, not just total demand

B) Script targets

- Explain why the problem matters.
- Explain why yellow taxi data is a useful lens.
- Emphasize that the project studies behavioral change, not only trip totals.

C) Draft spoken version

“This problem matters because COVID did not only reduce mobility, it also changed how people traveled, how they paid, and how different types of trips recovered. A simple citywide trip-count graph would show the shock, but it would miss the behavioral detail inside each trip. Yellow taxi data is useful because it gives trip-level information on time, fare, tips, payment type, and pickup and dropoff locations. That means we can study whether tipping changed, whether airport travel came back in the same way across airports, and whether payment habits kept shifting after the city reopened. It also lets us separate the immediate disruption in 2020 from the slower reopening years, which is important if we want to distinguish temporary shocks from more persistent behavioral change.”

## Slide 4 - Research Questions and Contributions
Time: 1:10
Suggested lead: Chris

A) Slideshow visuals

- Use a 3-column layout, one card per RQ.
- RQ1: how did tipping behavior change across the four periods?
- RQ2: did JFK and LaGuardia recover differently?
- RQ3: did COVID accelerate the move to cashless payments, and did that persist?
- Add a contribution row at the bottom:
  - common 4-period design
  - reproducible DuckDB pipeline
  - descriptive, inferential, and ML evidence

B) Script targets

- State each RQ clearly.
- Explain what ties the three questions together.
- Highlight the shared project contributions.

C) Draft spoken version

“Our first research question asks how recorded tipping behavior changed over time and whether it eventually returned to the 2019 baseline. Our second asks whether airport-related yellow taxi recovery differed between JFK and LaGuardia, rather than treating airport demand as one combined category. Our third asks whether COVID accelerated the shift from cash to cashless payments and whether that change persisted. What ties these three questions together is a common four-period design, the same TLC data source, and the same reproducible DuckDB pipeline. The questions also give us three different types of evidence: a descriptive tipping analysis, a descriptive plus inferential airport analysis, and a descriptive plus machine-learning payment analysis.”

## Slide 5 - Dataset Statistics and Period Design
Time: 1:10
Suggested lead: Harsh

A) Slideshow visuals

- Timeline graphic with four labeled periods:
  - 2019 = pre-COVID
  - 2020 = COVID disruption
  - 2021-2022 = intermediate recovery
  - 2023 = post-COVID recovery
- Add a dataset statistics box with exact values:
  - 60 monthly TLC yellow taxi parquet files
  - 2019 through 2023
  - 218,118,168 total yellow taxi trips in the study window
  - key variables: timestamps, fare, tip, payment type, passenger count, trip distance, pickup and dropoff zones
- Add one plain-language note:
  - the input is trip-level taxi behavior, not just raw files and rows

B) Script targets

- Explain the input data in plain English.
- Explain the four-period design.
- Explain what each period represents.

C) Draft spoken version

“Our dataset is the New York City TLC yellow taxi trip record data from January 2019 through December 2023, plus the taxi zone lookup table. In total, the study window contains 60 monthly parquet files and about 218.1 million yellow taxi trips. The variables we rely on most are pickup and dropoff time, pickup and dropoff zone, fare amount, tip amount, total amount, trip distance, passenger count, and payment type. We organize the analysis into four periods: pre-COVID in 2019, the disruption year in 2020, an intermediate recovery period in 2021 and 2022, and a post-COVID period in 2023. Including 2021 and 2022 is important because recovery was gradual and uneven. If we jumped directly from 2020 to 2023, we would miss the transition period where some behaviors started to rebound while others were still far from baseline.”

## Slide 6 - Shared Workflow and Methodology
Time: 1:10
Suggested lead: Harsh

A) Slideshow visuals

- Use a horizontal pipeline diagram:
  - local parquet files
  - `query_taxi_duckdb.py`
  - RQ1 / RQ2 / RQ3 analysis scripts
  - saved CSV outputs and figures
- Add one small methodology box:
  - preprocess
  - question-specific filtering
  - summaries and models
  - figure generation

B) Script targets

- Explain the shared pipeline.
- Mention data preprocessing and filtering.
- Preview how methodology changes by research question.

C) Draft spoken version

“All three research questions use the same DuckDB-based query workflow on the local parquet files instead of loading the entire dataset into one giant in-memory table. The shared script assigns each month to one of the four study periods and produces a consistent base for the downstream analyses. That consistency matters because we want all three questions to be comparable, not built on different period definitions or different preprocessing choices. From there, each research question applies its own filtering and analysis logic. RQ1 focuses on valid credit-card trips because cash tips are not reliably observed. RQ2 identifies airport-related trips using JFK and LaGuardia zone definitions and then builds both descriptive summaries and a monthly panel regression. RQ3 groups payment types into cashless, cash, and ambiguous categories and then adds a held-out machine learning evaluation.”

## Slide 7 - RQ1: Tipping Behavior
Time: 1:20
Suggested lead: Harsh

A) Slideshow visuals

- Main visual: `RQ1/figures/monthly_tipping_trend.png`
- Small side visual: `RQ1/figures/period_tipping_change.png`
- Add one takeaway box with exact period averages:
  - pre-COVID: 22.57%
  - COVID: 23.34%
  - intermediate: 23.35%
  - post-COVID: 22.19%
- Add percentage-point changes versus baseline:
  - COVID: +0.764 pp
  - intermediate: +0.775 pp
  - post-COVID: -0.388 pp

B) Script targets

- State the measurement choice.
- Explain the pattern over the four periods.
- Interpret the result carefully.
- Mention the limitation.

C) Draft spoken version

“For RQ1, we measure tipping using valid credit-card trips only, because cash tips are not reliably captured in the TLC records. Even with that restriction, the sample is still very large: about 60.6 million valid credit-card trips in 2019, 17.5 million in 2020, 52.6 million in the intermediate period, and 29.9 million in 2023. The baseline average tip percentage in 2019 is 22.57 percent. That rises to 23.34 percent in 2020 and stays at 23.35 percent in the intermediate recovery period, before dropping to 22.19 percent in 2023. Relative to the baseline, that is a positive shift of about 0.76 to 0.78 percentage points during the disruption and intermediate recovery, followed by a decline to about 0.39 percentage points below baseline in 2023. So the overall pattern is not a steady upward trend. It looks more like a temporary increase in recorded card-tip share that mostly fades out by the post-COVID period.”

## Slide 8 - RQ2: Airport Recovery Descriptively
Time: 1:30
Suggested lead: Adam

A) Slideshow visuals

- Main visual: `RQ2/figures/monthly_airport_trip_counts.png`
- Secondary visual: `RQ2/figures/monthly_airport_trip_share.png`
- Add a compact recovery box:
  - JFK 2023 recovery index: 0.704
  - LaGuardia 2023 recovery index: 0.577
- Add one small note:
  - comparisons use average monthly values where period lengths differ

B) Script targets

- Explain the airport comparison directly.
- Walk through the descriptive result.
- Make the comparison fair and precise.

C) Draft spoken version

“For RQ2, we ask a direct comparative question: did airport-related yellow taxi recovery differ between JFK and LaGuardia after the COVID shock? The descriptive evidence suggests that it did. Both airports collapse in 2020, but JFK recovers more strongly afterward, both in absolute monthly volume and as a share of the yellow taxi system. Using average monthly trip counts to keep the comparison fair across periods of different lengths, JFK falls from about 281,827 airport-related trips per month in 2019 to about 62,362 in 2020. LaGuardia falls from about 250,675 to about 46,398. During the intermediate recovery period, JFK climbs back to roughly 148,752 trips per month, while LaGuardia recovers to about 101,457. In 2023, JFK reaches about 198,405 trips per month, or 70.4 percent of its 2019 baseline, while LaGuardia reaches about 144,561 trips per month, or 57.7 percent of baseline. The share view tells the same story: JFK rises from about 4.03 percent of all yellow taxi trips before COVID to 6.23 percent in 2023, while LaGuardia rises from 3.56 percent to 4.52 percent. So recovery is not only incomplete, it is also uneven.”

## Slide 9 - RQ2: Regression Evidence
Time: 1:20
Suggested lead: Adam for setup, Chris for interpretation

A) Slideshow visuals

- Main visual: `RQ2/figures/airport_regression_interactions.png`
- Add a compact coefficient box:
  - JFK x intermediate: +0.0108, p = 0.0031
  - JFK x post-COVID: +0.0125, p < 1e-9
- Add one short interpretation line:
  - positive interaction terms mean stronger JFK recovery relative to LaGuardia

B) Script targets

- Explain the regression in plain English.
- Focus on the interaction terms.
- State the inferential conclusion.
- Mention robustness.

C) Draft spoken version

“Adam: To test whether that descriptive gap is statistically meaningful, we estimate a monthly airport panel regression. The outcome is airport trip share, LaGuardia and 2019 are the reference categories, and we include month-of-year fixed effects so that seasonal variation is not confused with recovery. The key coefficients are the JFK-by-period interaction terms, because they tell us whether JFK changes differently from LaGuardia in each later phase. Chris: The COVID interaction is essentially zero, which means the initial collapse does not look meaningfully different across the two airports once we compare them relative to baseline. The divergence appears later. The intermediate interaction is about positive 0.0108 with a p-value of 0.0031, and the post-COVID interaction is about positive 0.0125 with a p-value below one times ten to the negative ninth. In substantive terms, JFK’s airport-trip share rises by roughly 1.1 to 1.3 percentage points more than LaGuardia’s in the recovery phases. The pickup-only robustness check shows the same sign and significance pattern, which strengthens the claim that the uneven recovery is not just an artifact of one airport definition.”

D) Handoff suggestion

- Adam covers the regression structure and what the interaction terms mean.
- Chris covers the significance and the plain-English takeaway.

## Slide 10 - RQ3: Cashless Shift Descriptively
Time: 1:20
Suggested lead: Chris

A) Slideshow visuals

- Main visual: `RQ3/figures/monthly_cashless_share.png`
- Secondary visual: `RQ3/figures/period_payment_mix.png`
- Add one exact takeaway box with known-payment cashless shares:
  - pre-COVID: 72.59%
  - COVID: 73.96%
  - intermediate: 78.46%
  - post-COVID: 82.34%
- Add percentage-point changes versus baseline:
  - COVID: +1.38 pp
  - intermediate: +5.87 pp
  - post-COVID: +9.75 pp

B) Script targets

- Frame the question carefully.
- Explain the descriptive trend using exact numbers.
- Explain why known-payment share is the primary measure.

C) Draft spoken version

“For RQ3, cashless payment is already common before COVID, but it becomes even more prevalent over the study window. Using cashless share among known payment trips, the baseline is 72.59 percent in 2019. That rises to 73.96 percent in 2020, 78.46 percent in the intermediate recovery period, and 82.34 percent in 2023. Relative to the baseline, that is an increase of about 1.38 percentage points during COVID, 5.87 points in the intermediate period, and 9.75 points by the post-COVID period. So unlike the tipping result, this pattern does not move back toward baseline. It keeps strengthening. We treat known-payment share as the primary measure because ambiguous payment codes vary over time, and we do not want those administrative coding shifts to blur the cash-versus-cashless comparison. The descriptive takeaway is that the move away from cash persists well beyond the initial disruption.”

## Slide 11 - RQ3: Model-Based Evaluation
Time: 1:25
Suggested lead: Harsh for setup, Chris for results

A) Slideshow visuals

- Main visual: `RQ3/figures/cashless_model_metric_comparison.png`
- Secondary visual: `RQ3/figures/cashless_xgboost_feature_importance.png`
- Add an exact metrics box:
  - dummy ROC-AUC: 0.500
  - logistic ROC-AUC: 0.581
  - XGBoost ROC-AUC: 0.638
- Add improvement percentages versus the dummy baseline:
  - logistic ROC-AUC improvement: +16.25%
  - XGBoost ROC-AUC improvement: +27.54%
- Add one split box:
  - train rows: 513,206
  - test rows: 56,105
  - test starts: 2023-07-01

B) Script targets

- Explain the modeling setup and why the evaluation metric matters.
- Describe the train/test setup.
- Explain why ROC-AUC matters more than raw accuracy here.
- Summarize the modeling takeaway.

C) Draft spoken version

“Harsh: For RQ3, we complement the descriptive analysis with a held-out prediction task. The model predicts whether a known-payment trip is cashless or cash. We train on trips before July 2023 and test on trips from July 2023 onward, which gives us 513,206 training rows and 56,105 held-out test rows. We use a time-based split rather than a random split so the evaluation reflects a more realistic future-prediction setting and reduces temporal leakage. Because the test set is heavily tilted toward cashless trips, accuracy by itself can be misleading. Chris: That is why ROC-AUC and average precision matter more here. The dummy most-frequent baseline has ROC-AUC of 0.500. Logistic regression improves that to 0.581, and XGBoost improves further to 0.638. Those are improvements of about 16.25 percent and 27.54 percent over the dummy baseline. Average precision also rises from 0.825 for the dummy model to 0.859 for logistic regression and 0.885 for XGBoost. The feature-importance results show that period indicators, borough variables, and fare amount remain among the strongest predictors, which supports the descriptive conclusion that payment behavior changes across recovery phases rather than only across trip geography.”

D) Handoff suggestion

- Harsh covers the train/test split, baseline choice, and why accuracy is not enough.
- Chris covers the model comparison, improvement percentages, and feature-importance takeaway.

## Slide 12 - Discussion and Limitations
Time: 1:15
Suggested lead: shared round-robin

A) Slideshow visuals

- Use a 3-column discussion slide.
- Column 1, RQ1:
  - tipping is measured on credit-card trips
  - cash tips are not fully observed in TLC data
- Column 2, RQ2:
  - airport trip share is the primary outcome
  - this accounts for swings in total yellow taxi demand
- Column 3, RQ3:
  - ROC-AUC and average precision are emphasized
  - the held-out test set is imbalanced toward cashless trips
- Add a footer limitations bar:
  - yellow taxis only
  - not causal
  - administrative data constraints

B) Script targets

- Explain the main methodological choices and their implications.
- Close with the main validity limits.

C) Draft spoken version

“This slide brings together the main interpretation and the main limitations. In RQ1, tipping is measured on credit-card trips because cash tips are not fully observed in the TLC records, so the result is about recorded card-tip behavior rather than all tipping. In RQ2, airport trip share is the primary comparative outcome because total yellow taxi demand also changes sharply over time, and raw counts alone would mix airport recovery with system-wide recovery. In RQ3, ROC-AUC and average precision are more informative than raw accuracy because the held-out test set is imbalanced toward cashless trips. More broadly, these are yellow taxi data rather than all travel in New York City, and the results should be interpreted as comparative evidence about behavioral change rather than a causal estimate of what COVID alone caused.”

D) Balanced round-robin version

- Adam: “For RQ2, the main comparative outcome is airport trip share, because total yellow taxi demand also changes a lot across the study window. Looking only at counts would mix airport recovery with the broader recovery of the yellow taxi system.”
- Harsh: “For RQ1, tipping is measured on credit-card trips, because cash tips are not fully observed in the TLC records. That means the result is informative, but it should be interpreted as recorded card-tip behavior rather than all tipping.”
- Chris: “For RQ3, ROC-AUC and average precision are the most informative model metrics here, because the held-out test set is imbalanced toward cashless trips. A model can look strong on raw accuracy even if it is mostly just tracking the majority class.”
- Adam close: “Across all three questions, the broader limitation is that this is evidence about yellow taxi behavior, not a causal statement about all travel in New York City. Other factors like fare changes, trip mix, and broader market changes may also contribute to the observed patterns.”

## Slide 13 - Conclusion
Time: 0:40
Suggested lead: Chris

A) Slideshow visuals

- One closing thesis sentence:
  - COVID changed multiple parts of yellow taxi behavior, but those behaviors did not recover in the same way.
- Three short conclusion bullets:
  - tipping mostly reverted toward baseline
  - airport recovery stayed uneven, favoring JFK
  - cashless payment adoption continued to strengthen
- Add the repo link in small text at the bottom if desired.

B) Script targets

- Restate the overall takeaway.
- Summarize the three result patterns in one tight close.
- End cleanly and confidently.

C) Draft spoken version

“Our overall conclusion is that COVID changed multiple dimensions of yellow taxi behavior, but those dimensions did not recover in the same way. Tipping rose during the disruption and intermediate period but moved back close to baseline by 2023, which makes it look more temporary. Airport recovery remained incomplete and uneven, with JFK recovering more strongly than LaGuardia in both the descriptive and regression evidence. Payment behavior shows the most persistent shift, with cashless usage continuing to grow well after the initial shock. So the main message we want the audience to remember is that recovery in the taxi system was not uniform: some behaviors reverted, some diverged, and some appear to have structurally shifted.”

## Backup Slides

These are not part of the timed 15-minute core presentation, but they are useful for questions.

### Backup 1 - RQ2 coefficient table

- Show the exact JFK interaction coefficients and p-values.
- Use if someone asks about the inferential evidence behind the airport claim.

### Backup 2 - RQ3 full metrics table

- Show accuracy, precision, recall, F1, ROC-AUC, and average precision for all three models.
- Use if someone asks why ROC-AUC matters more than accuracy here.

### Backup 3 - Replication workflow

- Show the repo structure and the main commands:
  - `python3 RQ1/tipping_analysis.py`
  - `python3 RQ2/airport_trip_analysis.py`
  - `python3 RQ3/cashless_payment_analysis.py`
- Mention the local data requirement in `taxi_data/`.

## Submission Checklist

- Export the slide deck as PDF.
- Submit the slide PDF and the presentation video.
- Verify that the final video is under 15 minutes.
- Verify that each team member speaks in the final video.
- Verify that every slide has a slide number.
- Verify that all fonts are at least 18.
- Verify that all figures are readable after PDF export.
- Verify that every conclusion on the slides is supported by exact numbers.

## Design Notes

- Keep each slide focused on one main message.
- Prefer charts and short labels over dense paragraphs.
- Use exact values rather than vague wording.
- When discussing model comparisons, highlight percentage improvement over baseline.
- Make every slide self-explanatory for an audience that has not seen the report.
- Keep a consistent color mapping:
  - JFK and LaGuardia consistent across the RQ2 slides
  - cashless, cash, and ambiguous consistent across the RQ3 slides
- Avoid equations in the main deck unless the team feels strongly about them.
