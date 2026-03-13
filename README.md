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
- RQ2 analysis code for airport-related yellow taxi recovery at JFK and LaGuardia
- a midterm report workspace, including a nested Overleaf Git repository

The current RQ2 implementation compares JFK and LaGuardia across the four project periods using:

- monthly airport-related trip counts
- airport trips as a share of all yellow taxi trips
- the internal mix between JFK and LaGuardia
- period-level fare and trip distance summaries

## Repository Contents

- `query_taxi_duckdb.py`: reusable DuckDB query helper for local TLC parquet files
- `RQ2/`
  - `airport_trip_analysis.py`: builds RQ2 airport recovery summaries
  - `airport_trip_figures.py`: generates RQ2 figures from the airport summaries
- `proposal/`: project proposal PDF, requirements PDF, and TA feedback
- `midterm_report/`: midterm report materials and report repository

## Query Workflow

The project uses DuckDB queries against local TLC parquet files instead of building one large local pandas DataFrame.

The main entry point is [`query_taxi_duckdb.py`](query_taxi_duckdb.py), which:

- queries the selected local TLC parquet files with DuckDB
- returns monthly and period-level summaries
- can be imported from other Python files for analysis code

## Setup

Install `duckdb` and `pandas` for Python:

```bash
pip install duckdb pandas
```

This workflow expects the required parquet files to be present in `taxi_data/`.

Required files:

- `yellow_tripdata_2019-01.parquet` through `yellow_tripdata_2019-12.parquet`
- `yellow_tripdata_2020-03.parquet` through `yellow_tripdata_2020-12.parquet`
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

The shared pipeline labels `2021` and `2022` as `intermediate`. RQ2 is expected to use that intermediate period for recovery analysis; RQ1 and RQ3 can still subset the data if those years are not needed.

## RQ2 Workflow

Run the RQ2 airport analysis from the repository root:

```bash
python3 RQ2/airport_trip_analysis.py
```

This writes CSV outputs to `RQ2/outputs/`.

To generate the figures used in the report:

```bash
python3 RQ2/airport_trip_figures.py
```

This writes PNG figures to `RQ2/figures/`.

## Project Goal

The proposal framing for this project is a comparative analysis of taxi activity before, during, and after the COVID-era disruption. A typical analysis workflow would focus on questions such as:

- how trip volume changed across the selected periods
- which pickup and dropoff zones changed the most
- whether travel patterns recovered evenly across the city

## Midterm Report and Overleaf Repo

The midterm report lives under `midterm_report/`. The LaTeX report project is stored in:

- `midterm_report/report_repo/`

Important: `midterm_report/report_repo/` is its own nested Git repository used for the Overleaf project. That means:

- changes inside `midterm_report/report_repo/` have their own Git status and history
- running `git status` at the top level will not necessarily show file-level changes inside the nested report repo
- if you want to inspect or commit report changes, run Git commands from inside `midterm_report/report_repo/`

This split is intentional: the top-level repository tracks the analysis workspace, while the nested repo tracks the report source shared through Overleaf.
