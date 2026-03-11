# Taxi Project

This repository contains the data workspace for a CISC 351 project based on a proposal to study NYC yellow taxi trip patterns across three periods:

- `2019`: pre-pandemic baseline
- `2020-03` through `2020-12`: pandemic disruption period
- `2023`: post-pandemic recovery period

The project is built around New York City Taxi and Limousine Commission yellow taxi trip records and the taxi zone lookup table.

## Repository Contents (after downloaded data)

- `taxi_data/`: yellow taxi trip parquet files and `taxi_zone_lookup.csv`

The current dataset footprint is large, about `2.0G`.

## Data Files Required

This project depends on the following manually downloaded files inside `taxi_data/`:

- `taxi_zone_lookup.csv`
- `yellow_tripdata_2019-01.parquet` through `yellow_tripdata_2019-12.parquet`
- `yellow_tripdata_2020-03.parquet` through `yellow_tripdata_2020-12.parquet`
- `yellow_tripdata_2023-01.parquet` through `yellow_tripdata_2023-12.parquet`

## Important Setup Note

The `taxi_data` files must be downloaded manually. They should not be assumed to come from a fresh clone of this repository.

If you are setting this project up on another machine:

1. Create a `taxi_data/` directory at the repository root.
2. Download the required NYC yellow taxi trip parquet files for the months listed above.
3. Download `taxi_zone_lookup.csv`.
4. Place all of those files directly inside `taxi_data/`.

Because these files are large, `taxi_data/` is ignored by Git in [`.gitignore`](.gitignore).

## Download Instructions

From the repository root, run the following bash commands to download all required files into `taxi_data/`:

```bash
# Create data directory
mkdir -p taxi_data
cd taxi_data

# Download 2019 data (Pre-COVID baseline)
for m in {01..12}; do
  curl -O https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2019-$m.parquet
done

# Download 2020 data (COVID disruption period)
for m in {03..12}; do
  curl -O https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2020-$m.parquet
done

# Download 2023 data (Post-COVID recovery)
for m in {01..12}; do
  curl -O https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-$m.parquet
done

# Download taxi zone lookup table
curl -O https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv
```

## Project Goal

The proposal framing for this project is a comparative analysis of taxi activity before, during, and after the COVID-era disruption. A typical analysis workflow would focus on questions such as:

- how trip volume changed across the selected periods
- which pickup and dropoff zones changed the most
- whether travel patterns recovered evenly across the city

## Data Source

Use the official NYC TLC trip record data source for the yellow taxi parquet files and the corresponding taxi zone lookup table.
