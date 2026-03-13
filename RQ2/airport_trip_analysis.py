#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import query_taxi_duckdb as q

JFK_LOCATION_ID = 132
LGA_LOCATION_ID = 138
RQ2_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = RQ2_DIR / "outputs"
PERIOD_ORDER = ["pre_covid", "covid", "intermediate", "post_covid"]


def build_airport_monthly_summary(
    data_dir: str | Path = q.DEFAULT_DATA_DIR,
    db_path: str = q.DEFAULT_DB_PATH,
    skip_errors: bool = True,
) -> tuple[pd.DataFrame, list[str]]:
    select_sql = f"""
        SELECT
            CASE
                WHEN PULocationID = {JFK_LOCATION_ID} OR DOLocationID = {JFK_LOCATION_ID}
                    THEN 'JFK'
                WHEN PULocationID = {LGA_LOCATION_ID} OR DOLocationID = {LGA_LOCATION_ID}
                    THEN 'LaGuardia'
            END AS airport,
            COUNT(*) AS airport_trip_count,
            SUM(fare_amount) AS fare_amount_sum,
            SUM(tip_amount) AS tip_amount_sum,
            SUM(total_amount) AS total_amount_sum,
            SUM(trip_distance) AS trip_distance_sum,
            AVG(fare_amount) AS avg_fare,
            AVG(tip_amount) AS avg_tip,
            AVG(total_amount) AS avg_total_amount,
            AVG(trip_distance) AS avg_trip_distance
        FROM read_parquet('__SOURCE__', union_by_name = true)
        WHERE
            PULocationID IN ({JFK_LOCATION_ID}, {LGA_LOCATION_ID})
            OR DOLocationID IN ({JFK_LOCATION_ID}, {LGA_LOCATION_ID})
        GROUP BY airport
    """
    df, skipped_sources = q.run_query(
        select_sql=select_sql,
        data_dir=data_dir,
        db_path=db_path,
        skip_errors=skip_errors,
    )
    if df.empty:
        return df, skipped_sources

    df = df.sort_values(["airport", "year", "month"]).reset_index(drop=True)
    return df, skipped_sources


def build_airport_share_summary(
    airport_monthly: pd.DataFrame,
    overall_monthly: pd.DataFrame,
) -> pd.DataFrame:
    merged = airport_monthly.merge(
        overall_monthly[["year", "month", "period", "trip_count"]],
        on=["year", "month", "period"],
        how="left",
    )
    merged = merged.rename(columns={"trip_count": "all_trip_count"})
    merged["airport_trip_share"] = (
        merged["airport_trip_count"] / merged["all_trip_count"]
    )
    return merged.sort_values(["airport", "year", "month"]).reset_index(drop=True)


def build_airport_period_summary(airport_monthly: pd.DataFrame) -> pd.DataFrame:
    summary = (
        airport_monthly.groupby(["period", "airport"], as_index=False)
        .agg(
            airport_trip_count=("airport_trip_count", "sum"),
            fare_amount_sum=("fare_amount_sum", "sum"),
            tip_amount_sum=("tip_amount_sum", "sum"),
            total_amount_sum=("total_amount_sum", "sum"),
            trip_distance_sum=("trip_distance_sum", "sum"),
        )
    )
    summary["avg_fare"] = summary["fare_amount_sum"] / summary["airport_trip_count"]
    summary["avg_tip"] = summary["tip_amount_sum"] / summary["airport_trip_count"]
    summary["avg_total_amount"] = (
        summary["total_amount_sum"] / summary["airport_trip_count"]
    )
    summary["avg_trip_distance"] = (
        summary["trip_distance_sum"] / summary["airport_trip_count"]
    )
    summary = summary[
        [
            "period",
            "airport",
            "airport_trip_count",
            "avg_fare",
            "avg_tip",
            "avg_total_amount",
            "avg_trip_distance",
        ]
    ]
    summary["period"] = pd.Categorical(
        summary["period"], categories=PERIOD_ORDER, ordered=True
    )
    summary = summary.sort_values(["airport", "period"]).reset_index(drop=True)
    return summary


def build_airport_mix_summary(airport_monthly: pd.DataFrame) -> pd.DataFrame:
    mix = airport_monthly.copy()
    total_by_month = mix.groupby(["year", "month"], as_index=False).agg(
        total_airport_trip_count=("airport_trip_count", "sum")
    )
    mix = mix.merge(total_by_month, on=["year", "month"], how="left")
    mix["airport_mix_share"] = (
        mix["airport_trip_count"] / mix["total_airport_trip_count"]
    )
    return mix.sort_values(["year", "month", "airport"]).reset_index(drop=True)


def build_recovery_summary(airport_period: pd.DataFrame) -> pd.DataFrame:
    baseline = (
        airport_period[airport_period["period"] == "pre_covid"][
            ["airport", "airport_trip_count"]
        ]
        .rename(columns={"airport_trip_count": "pre_covid_trip_count"})
    )
    recovery = airport_period.merge(baseline, on="airport", how="left")
    recovery["trip_count_index_vs_pre_covid"] = (
        recovery["airport_trip_count"] / recovery["pre_covid_trip_count"]
    )
    recovery["period"] = pd.Categorical(
        recovery["period"], categories=PERIOD_ORDER, ordered=True
    )
    return recovery.sort_values(["airport", "period"]).reset_index(drop=True)


def save_outputs(
    airport_monthly: pd.DataFrame,
    airport_share: pd.DataFrame,
    airport_period: pd.DataFrame,
    airport_mix: pd.DataFrame,
    recovery_summary: pd.DataFrame,
    output_dir: str | Path,
) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    airport_monthly.to_csv(output_dir / "airport_monthly_summary.csv", index=False)
    airport_share.to_csv(output_dir / "airport_monthly_share.csv", index=False)
    airport_period.to_csv(output_dir / "airport_period_summary.csv", index=False)
    airport_mix.to_csv(output_dir / "airport_monthly_mix.csv", index=False)
    recovery_summary.to_csv(output_dir / "airport_recovery_summary.csv", index=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the RQ2 airport recovery analysis for JFK and LaGuardia."
    )
    parser.add_argument(
        "--data-dir",
        default=q.DEFAULT_DATA_DIR,
        help="directory containing local parquet files",
    )
    parser.add_argument(
        "--db-path",
        default=q.DEFAULT_DB_PATH,
        help="path to the DuckDB database file, defaults to in-memory",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="directory to write CSV outputs",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    overall_monthly, overall_skips = q.build_monthly_summary(
        data_dir=args.data_dir,
        db_path=args.db_path,
    )
    airport_monthly, airport_skips = build_airport_monthly_summary(
        data_dir=args.data_dir,
        db_path=args.db_path,
    )

    skipped_sources = sorted(set(overall_skips + airport_skips))

    if overall_monthly.empty or airport_monthly.empty:
        print("Airport analysis could not be built from the local parquet files.")
        return 1

    airport_share = build_airport_share_summary(airport_monthly, overall_monthly)
    airport_period = build_airport_period_summary(airport_monthly)
    airport_mix = build_airport_mix_summary(airport_monthly)
    recovery_summary = build_recovery_summary(airport_period)

    save_outputs(
        airport_monthly=airport_monthly,
        airport_share=airport_share,
        airport_period=airport_period,
        airport_mix=airport_mix,
        recovery_summary=recovery_summary,
        output_dir=args.output_dir,
    )
    print("\nAirport period summary:")
    print(airport_period)

    print("\nAirport monthly share sample:")
    print(
        airport_share[
            [
                "airport",
                "period",
                "year",
                "month",
                "airport_trip_count",
                "all_trip_count",
                "airport_trip_share",
            ]
        ].head(12)
    )

    print(f"\nSaved CSV outputs to {Path(args.output_dir).resolve()}")

    if skipped_sources:
        print("\nSkipped sources:")
        for source in skipped_sources:
            print(source)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
