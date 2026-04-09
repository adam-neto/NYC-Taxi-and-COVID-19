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

- Introduction: Slides 1 and 2
- Motivation: Slide 2
- Dataset statistics: Slide 4
- Methodology: Slides 5, 6, 7, 8, 9, and 10
- Experiment results for three research questions: Slides 6 through 10
- Discussion, including things tried that did not work well: Slide 11
- Conclusion: Slide 12
- Less than 15 minutes: timed plan below totals about 14 minutes 5 seconds
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

This version is balanced so everyone speaks for almost exactly the same amount of time.

- Adam: about 4 minutes 42 seconds
- Harsh: about 4 minutes 42 seconds
- Chris: about 4 minutes 41 seconds

Recommended split:

- Adam
  - Slide 1
  - Slide 2
  - Slide 7
  - first part of Slide 8
  - Adam section of Slide 11
- Harsh
  - Slide 4
  - Slide 5
  - Slide 6
  - first part of Slide 10
  - Harsh section of Slide 11
- Chris
  - Slide 3
  - second part of Slide 8
  - Slide 9
  - second part of Slide 10
  - Slide 12
  - Chris section of Slide 11

Because Slides 8, 10, and 11 are split, the team should rehearse the handoffs so they feel intentional rather than abrupt.

## Timing Summary

- Slide 1: 0:40
- Slide 2: 1:05
- Slide 3: 1:10
- Slide 4: 1:10
- Slide 5: 1:10
- Slide 6: 1:20
- Slide 7: 1:30
- Slide 8: 1:20
- Slide 9: 1:20
- Slide 10: 1:25
- Slide 11: 1:15
- Slide 12: 0:40

Total planned time: about 14:05

## Per-Speaker Timing Plan

- Adam
  - Slide 1: 0:40
  - Slide 2: 1:05
  - Slide 7: 1:30
  - Slide 8, setup and model explanation: 0:35
  - Slide 11, Adam section: 0:52
  - Total: about 4:42
- Harsh
  - Slide 4: 1:10
  - Slide 5: 1:10
  - Slide 6: 1:20
  - Slide 10, setup and evaluation logic: 0:35
  - Slide 11, Harsh section: 0:27
  - Total: about 4:42
- Chris
  - Slide 3: 1:10
  - Slide 8, results interpretation: 0:45
  - Slide 9: 1:20
  - Slide 10, results takeaway: 0:50
  - Slide 11, Chris section: 0:16
  - Slide 12: 0:40
  - Total: about 4:41

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

“We are Group 10, and our final project studies how COVID-19 changed New York City yellow taxi behavior before, during, and after the main disruption period. Instead of looking only at whether taxi activity fell, we ask a broader question: which behaviors bounced back, and which ones stayed changed. We answer that through three research questions on tipping, airport recovery, and the shift from cash to cashless payments.”

## Slide 2 - Why This Problem Matters
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
- Emphasize that the project is not just about trip volume collapsing.

C) Draft spoken version

“This problem matters because COVID did not only reduce mobility, it also changed how people traveled, how they paid, and how different types of trips recovered. Yellow taxi data is useful because it gives trip-level information on time, fare, tips, payment type, and pickup and dropoff locations. That means we can study not just whether demand fell, but whether rider behavior inside trips changed in ways that persisted after the initial shock.”

## Slide 3 - Research Questions and Contributions
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

“Our first research question asks how recorded tipping behavior changed over time. Our second asks whether airport-related yellow taxi recovery differed between JFK and LaGuardia, which makes the airport story more specific and less trivial. Our third asks whether COVID accelerated the shift from cash to cashless payments and whether that change persisted. Across all three questions, the main contribution is a common recovery framework built on the same data source, the same period definitions, and a reproducible analysis pipeline.”

## Slide 4 - Dataset Statistics and Period Design
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
- Make clear why 2021-2022 had to be included.

C) Draft spoken version

“Our dataset is the New York City TLC yellow taxi trip record data from January 2019 through December 2023, plus the taxi zone lookup table. In total, our study window contains 60 monthly files and about 218.1 million yellow taxi trips. The key inputs are trip time, fare, tip, payment type, distance, passenger count, and pickup and dropoff locations. We organize the analysis into four periods: pre-COVID in 2019, the disruption year in 2020, an intermediate recovery period in 2021 and 2022, and a post-COVID period in 2023. That intermediate period is important because otherwise the story would jump too abruptly from the shock to the recovery.”

## Slide 5 - Shared Workflow and Methodology
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

“All three research questions are built on the same DuckDB-based query workflow rather than one giant in-memory dataframe. The shared script reads the local parquet files, assigns each month to one of the four project periods, and produces a consistent base for the downstream analyses. From there, each research question applies its own filters and methodology: RQ1 focuses on valid credit-card trips, RQ2 identifies airport-related trips and estimates a panel regression, and RQ3 groups payment types and then adds a held-out machine learning evaluation.”

## Slide 6 - RQ1: Tipping Behavior
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

“For RQ1, we measure tipping using credit-card trips only, because cash tips are not reliably captured in the TLC records. The baseline average tip percentage in 2019 is 22.57 percent. That rises to 23.34 percent in 2020 and stays at about 23.35 percent in the intermediate recovery period, before dropping to 22.19 percent in 2023. So the main pattern is that tipping appears to rise during and shortly after the disruption, but by the post-COVID period it is slightly below the 2019 baseline. Our interpretation is that the shift in tipping behavior looks more temporary than permanent, but the result only speaks to recorded card tips, not all tipping behavior.”

## Slide 7 - RQ2: Airport Recovery Descriptively
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

- Explain why RQ2 is not a trivial airport-demand question.
- Walk through the descriptive result.
- Make the comparison fair and precise.

C) Draft spoken version

“We sharpened RQ2 so that it is not just the obvious statement that airport trips fell during COVID. Instead, we ask whether JFK and LaGuardia recovered differently. Descriptively, both airports collapse in 2020, but JFK recovers more strongly afterward, both in absolute monthly volume and as a share of the yellow taxi system. By 2023, JFK is back to about 70.4 percent of its 2019 airport-trip volume, while LaGuardia is at about 57.7 percent. Because the intermediate period covers two years, we focus on average monthly comparisons rather than raw period totals so the comparison stays fair.”

## Slide 8 - RQ2: Regression Evidence
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

“To move beyond the descriptive plots, we estimate a monthly airport panel regression where LaGuardia and the 2019 baseline are the reference categories, and the key evidence comes from the JFK-by-period interaction terms. The COVID interaction is not meaningfully different from zero, but the later interactions are both positive and statistically significant. The intermediate interaction is about positive 0.0108 with a p-value of about 0.003, and the post-COVID interaction is about positive 0.0125 with a p-value below one times ten to the negative ninth. In plain terms, the difference between the airports becomes clearest during the recovery rather than during the initial collapse, and that result also survives the pickup-only robustness check.”

D) Handoff suggestion

- Adam covers the regression structure and what the interaction terms mean.
- Chris covers the significance and the plain-English takeaway.

## Slide 9 - RQ3: Cashless Shift Descriptively
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

“For RQ3, the key point is not that cashless payment suddenly appeared during COVID, because it was already common before the pandemic. The real question is whether the pandemic accelerated the shift and whether that shift persisted. Using cashless share among known payment trips, the baseline is 72.59 percent in 2019, which rises to 73.96 percent in 2020, 78.46 percent in the intermediate period, and 82.34 percent in 2023. That is a gain of about 9.75 percentage points relative to the baseline by the end of the study window. We treat known-payment share as the primary measure because ambiguous payment codes vary over time, so the all-trip version is less clean for interpretation.”

## Slide 10 - RQ3: Model-Based Evaluation
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

- Explain why this slide matters for the course requirement.
- Describe the train/test setup.
- Explain why ROC-AUC matters more than raw accuracy here.
- Summarize the modeling takeaway.

C) Draft spoken version

“RQ3 is also the section that directly satisfies the final modeling requirement. We train on known-payment trips before July 2023 and test on 56,105 held-out trips from July 2023 onward, with 513,206 training rows. Accuracy alone is not very helpful because the test set is heavily tilted toward cashless trips, so even the dummy baseline that always predicts the majority class reaches high accuracy. The more meaningful comparison is ROC-AUC, where logistic regression improves from 0.500 to 0.581, which is a 16.25 percent improvement over the dummy baseline, and XGBoost improves further to 0.638, which is a 27.54 percent improvement. That tells us the trip features contain real predictive signal, and the importance plot also shows that period indicators remain among the strongest features even after controlling for trip context.”

D) Handoff suggestion

- Harsh covers the train/test split, baseline choice, and why accuracy is not enough.
- Chris covers the model comparison, improvement percentages, and feature-importance takeaway.

## Slide 11 - Discussion, What Did Not Work, and Limitations
Time: 1:15
Suggested lead: shared round-robin

A) Slideshow visuals

- Use a 3-column “lessons learned” slide.
- Column 1, RQ1:
  - all-trip tipping was not interpretable because cash tips are not fully observed
  - final choice: credit-card trips only
- Column 2, RQ2:
  - raw airport counts alone were not enough because the whole yellow taxi system collapsed
  - final choice: share-based comparison plus robustness checks
- Column 3, RQ3:
  - raw accuracy did not separate models well because of class imbalance
  - final choice: emphasize ROC-AUC and average precision
- Add a footer limitations bar:
  - yellow taxis only
  - not causal
  - administrative data constraints

B) Script targets

- Satisfy the PDF’s discussion requirement.
- Explain what did not work well or what had to be revised.
- Close with the main validity limits.

C) Draft spoken version

“One thing the requirements explicitly ask for is a discussion of what did not work or what had to be revised, so we want to be clear about that. In RQ1, using all trips for tipping was not reliable because cash tips are not fully recorded, so we restricted the analysis to credit-card trips. In RQ2, raw airport counts alone were not enough because overall yellow taxi demand also changed dramatically, so the share-based outcome became the more informative primary comparison. In RQ3, plain accuracy looked strong for every model because the test set is imbalanced, so we shifted the comparison toward ROC-AUC and average precision. More broadly, all of our conclusions should be interpreted as evidence about yellow taxi behavior, not all mobility in New York City, and they are comparative rather than causal claims.”

D) Balanced round-robin version

- Adam: “For RQ2, one thing we learned is that raw airport counts by themselves were not enough, because the entire yellow taxi system also changed so much. That is why the share-based comparison became our main descriptive and inferential outcome.”
- Harsh: “For RQ1, we could not treat all tipping data the same way because cash tips are not fully observed in the TLC records. That is why the final analysis focuses on credit-card trips only.”
- Chris: “For RQ3, raw accuracy did not separate the models very well because the held-out test set is imbalanced toward cashless trips. That is why we rely more on ROC-AUC and average precision when comparing the models.”
- Adam close: “Across all three questions, the broader limitation is that this is evidence about yellow taxi behavior, not a causal statement about all travel in New York City.”

## Slide 12 - Conclusion
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

“Our overall conclusion is that COVID changed multiple dimensions of yellow taxi behavior, but those dimensions did not recover in the same way. Tipping rose during the disruption and intermediate period but moved back close to baseline by 2023. Airport recovery remained incomplete and uneven, with JFK recovering more strongly than LaGuardia. And payment behavior shows the most persistent shift, with cashless usage continuing to grow well after the initial shock. Those differences are the main message we want the audience to remember.”

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
