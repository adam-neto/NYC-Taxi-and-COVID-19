# Taxi Project

This repository contains the analysis workspace for a CISC 351 project on COVID-era behavioral shifts in NYC yellow taxi travel. The project uses New York City Taxi and Limousine Commission yellow taxi trip records to study changes in travel behavior across multiple phases:

- `2019`: pre-pandemic baseline
- `2020`: pandemic disruption period
- `2021` and `2022`: intermediate recovery period
- `2023`: post-pandemic recovery period

The project is built around TLC trip parquet files and the taxi zone lookup table. Original trip data is available here:
https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

## Current State

The repository currently contains:

- a shared DuckDB-based query pipeline for summarizing TLC parquet files
- RQ1 analysis code for changes in tipping behavior
- RQ2 analysis code for airport-related yellow taxi recovery at JFK and LaGuardia
- RQ3 analysis and modeling code for changes in cash versus cashless payment behavior over time

The current RQ2 implementation compares JFK and LaGuardia across the four project periods using:

- monthly airport-related trip counts
- airport trips as a share of all yellow taxi trips
- the internal mix between JFK and LaGuardia
- period-level fare and trip distance summaries
- a monthly airport-panel regression comparing JFK and LaGuardia recovery paths

The current RQ3 implementation analyzes payment behavior across the four project periods using:

- monthly cashless payment share
- period-level payment mix summaries
- percentage-point changes relative to the pre-COVID baseline
- optional borough-level exploratory summaries using pickup borough
- a held-out machine learning evaluation for trip-level cashless-versus-cash prediction

## Repository Contents

- `query_taxi_duckdb.py`: reusable DuckDB query helper for local TLC parquet files
- `RQ1/`
  - `tipping_analysis.py`: builds RQ1 tipping summaries
  - `tipping_figures.py`: generates RQ1 figures from the tipping summaries
- `RQ2/`
  - `airport_trip_analysis.py`: builds RQ2 airport recovery summaries
  - `airport_recovery_regression.py`: builds the RQ2 regression-ready airport panel and panel-regression outputs
  - `airport_trip_figures.py`: generates RQ2 descriptive figures and the regression comparison plot from the saved airport outputs
- `RQ3/`
  - `cashless_payment_analysis.py`: builds RQ3 payment-behavior summaries and modeling outputs
  - `cashless_payment_model.py`: trains and evaluates the held-out RQ3 classification models
  - `cashless_payment_figures.py`: generates RQ3 figures from the payment summaries and saved model outputs

## Query Workflow

The project uses DuckDB queries against local TLC parquet files instead of building one large local pandas DataFrame.

The main entry point is [`query_taxi_duckdb.py`](query_taxi_duckdb.py), which:

- queries the selected local TLC parquet files with DuckDB
- returns monthly and period-level summaries
- can be imported from other Python files for analysis code

## Setup

Install the required Python packages:

```bash
pip install duckdb pandas numpy matplotlib seaborn scikit-learn xgboost
```

This workflow expects the required parquet files to be present in `taxi_data/`.

Required files:

- `yellow_tripdata_2019-01.parquet` through `yellow_tripdata_2019-12.parquet`
- `yellow_tripdata_2020-01.parquet` through `yellow_tripdata_2020-12.parquet`
- `yellow_tripdata_2021-*.parquet`
- `yellow_tripdata_2022-*.parquet`
- `yellow_tripdata_2023-01.parquet` through `yellow_tripdata_2023-12.parquet`
- `taxi_zone_lookup.csv`

```bash
# Create data directory
mkdir -p taxi_data
cd taxi_data

# Download 2019 data (Pre-COVID baseline)
for m in {01..12}; do
  curl -f -O https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2019-$m.parquet
done

# Download 2020 data (COVID disruption period)
for m in {01..12}; do
  curl -f -O https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2020-$m.parquet
done

# Download 2021 and 2022 data (Intermediate recovery period)
for m in {01..12}; do
  curl -f -O https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-$m.parquet
done
for m in {01..12}; do
  curl -f -O https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2022-$m.parquet
done

# Download 2023 data (Post-COVID recovery)
for m in {01..12}; do
  curl -f -O https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-$m.parquet
done

# Download taxi zone lookup table
curl -f -O https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv
```

Run the summary script from the repository root:

```bash
python3 query_taxi_duckdb.py
```

In Python analysis files, import it directly:

```python
import query_taxi_duckdb as q

monthly_df, skipped = q.build_monthly_summary(data_dir="taxi_data")
period_df, skipped = q.build_period_summary(data_dir="taxi_data")
```

The shared pipeline labels `2021` and `2022` as `intermediate`. RQ1, RQ2, and RQ3 use that intermediate period for recovery analysis, while any analysis can still subset the data further if needed.

## RQ1 Workflow

Run the RQ1 tipping analysis from the repository root:

```bash
python3 RQ1/tipping_analysis.py
```

This writes CSV outputs to `RQ1/outputs/`.

To generate the figures used in the report:

```bash
python3 RQ1/tipping_figures.py
```

After this workflow is run, the generated PNG figures are written to `RQ1/figures/`.

## RQ2 Workflow

RQ2 studies whether airport-related yellow taxi recovery differed between JFK and LaGuardia across the four project periods.

Run the following commands from the repository root.

### 1. Build the RQ2 analysis outputs

```bash
python3 RQ2/airport_trip_analysis.py
```

This writes CSV outputs to `RQ2/outputs/`, including:

- descriptive monthly and period summaries:
  - `airport_monthly_summary.csv`
  - `airport_monthly_share.csv`
  - `airport_period_share_summary.csv`
  - `airport_monthly_mix.csv`
  - `airport_period_summary.csv`
  - `airport_recovery_summary.csv`
- regression-ready and model output files for the main airport definition:
  - `airport_monthly_panel.csv`
  - `airport_regression_coefficients.csv`
  - `airport_regression_diagnostics.csv`
- robustness outputs for the pickup-only airport definition:
  - `airport_pickup_only_monthly_summary.csv`
  - `airport_pickup_only_monthly_share.csv`
  - `airport_pickup_only_monthly_panel.csv`
  - `airport_pickup_only_regression_coefficients.csv`
  - `airport_pickup_only_regression_diagnostics.csv`

The RQ2 regression module compares JFK and LaGuardia recovery paths using:

- `airport_trip_share` as the main airport-panel outcome
- a robustness model on `log(airport_trip_count + 1)`
- JFK-by-period interaction terms
- month-of-year fixed effects
- a pickup-only airport-definition robustness check in addition to the pickup-or-dropoff definition

For descriptive reporting, the repository saves both monthly-share and period-share summaries. The report currently uses average monthly shares for the main descriptive comparisons because the intermediate period spans two years, while `airport_period_share_summary.csv` provides a period-total aggregation that can be used as a robustness check on that descriptive choice.

### 2. Generate the RQ2 figures from the saved analysis outputs

```bash
python3 RQ2/airport_trip_figures.py
```

After this workflow is run, the generated standard RQ2 figures are written to `RQ2/figures/`, including:

- `monthly_airport_trip_counts.png`
- `monthly_airport_trip_share.png`
- `monthly_airport_mix_share.png`
- `airport_recovery_index.png`
- `airport_average_total_amount.png`
- `airport_regression_interactions.png`

By default, this script reads the CSV outputs written by `airport_trip_analysis.py` instead of rebuilding the airport summaries from the raw parquet files. It uses the saved main and pickup-only regression coefficient files to generate the regression interaction plot alongside the descriptive figures. If the saved outputs are missing, it will run the analysis step first and then generate the figure files.

The regression interaction plot compares the key JFK interaction coefficients across:

- the main pickup-or-dropoff specification
- the pickup-only robustness specification

### Recommended run order

If you want the full RQ2 workflow, run the scripts in this order:

```bash
python3 RQ2/airport_trip_analysis.py
python3 RQ2/airport_trip_figures.py
```

## RQ3 Workflow

RQ3 studies whether COVID accelerated the shift from cash to cashless payments and whether that shift persisted through the recovery period. The RQ3 workflow includes both descriptive summaries and a held-out machine learning evaluation for trip-level cashless-versus-cash prediction.

Run the main RQ3 analysis from the repository root:

```bash
python3 RQ3/cashless_payment_analysis.py
```

This writes CSV outputs to `RQ3/outputs/`, including:

- descriptive monthly and period summaries:
  - `cashless_monthly_summary.csv`
  - `cashless_period_summary.csv`
  - `cashless_change_summary.csv`
  - `cashless_borough_period_summary.csv`
- modeling outputs:
  - `cashless_model_split_summary.csv`
  - `cashless_model_metrics.csv`
  - `cashless_model_top_features.csv`

The RQ3 analysis groups payment behavior into:

- `cashless` for credit card trips
- `cash` for cash trips
- `ambiguous/other` for all remaining payment codes

The descriptive summaries report both:

- cashless share among all trips
- cashless share among known payment trips only

The modeling component uses known-payment trips only and compares:

- a dummy most-frequent baseline
- logistic regression
- XGBoost

The default model workflow uses a time-based split, training on trips before July 2023 and testing on trips from July 2023 onward. The script also samples a fixed number of known-payment trips per month so that the full workflow remains practical to rerun locally.

To generate the RQ3 figures used in the report:

```bash
python3 RQ3/cashless_payment_figures.py
```

After this workflow is run, the generated PNG figures are written to `RQ3/figures/`, including:

- `monthly_cashless_share.png`
- `period_payment_mix.png`
- `cashless_share_change_vs_pre_covid.png`
- `borough_cashless_share.png`
- `cashless_model_metric_comparison.png`
- `cashless_xgboost_feature_importance.png`

### Recommended run order

If you want the full RQ3 workflow, run the scripts in this order:

```bash
python3 RQ3/cashless_payment_analysis.py
python3 RQ3/cashless_payment_figures.py
```

## Project Goal

The project is a comparative analysis of NYC yellow taxi behavior before, during, and after the COVID-era disruption. The three research questions focus on:

- changes in tipping behavior
- airport-related trip recovery
- changes in cash versus cashless payment behavior
