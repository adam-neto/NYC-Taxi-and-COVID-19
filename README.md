# Taxi Project

This repository contains the data workspace for a CISC 351 project based on a proposal to study NYC yellow taxi trip patterns across multiple phases:

- `2019`: pre-pandemic baseline
- `2020-03` through `2020-12`: pandemic disruption period
- `2021` and `2022`: intermediate recovery period
- `2023`: post-pandemic recovery period

The project is built around New York City Taxi and Limousine Commission yellow taxi trip records and the taxi zone lookup table. Original data table can be found here: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

## Repository Contents

- `query_taxi_duckdb.py`: reusable DuckDB query helper for local TLC parquet files
- `taxi_data/`: local parquet files and lookup tables used by the DuckDB workflow

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

## Project Goal

The proposal framing for this project is a comparative analysis of taxi activity before, during, and after the COVID-era disruption. A typical analysis workflow would focus on questions such as:

- how trip volume changed across the selected periods
- which pickup and dropoff zones changed the most
- whether travel patterns recovered evenly across the city
