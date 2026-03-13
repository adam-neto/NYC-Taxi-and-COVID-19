#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

import duckdb
import pandas as pd

DEFAULT_DB_PATH = ":memory:"
DEFAULT_DATA_DIR = "taxi_data"
PIPELINE_YEARS = [2019, 2020, 2021, 2022, 2023]


def build_local_sources(data_dir: str | Path = DEFAULT_DATA_DIR) -> list[str]:
    data_dir = Path(data_dir)
    sources: list[Path] = []

    for year in PIPELINE_YEARS:
        sources.extend(data_dir.glob(f"yellow_tripdata_{year}-*.parquet"))

    return [str(path) for path in sorted(sources, key=lambda p: extract_year_month(str(p)))]


def resolve_sources(data_dir: str | Path = DEFAULT_DATA_DIR) -> list[str]:
    sources = build_local_sources(data_dir)
    missing_sources = [source for source in sources if not Path(source).exists()]
    if missing_sources:
        raise FileNotFoundError(
            "Missing local parquet files. First missing file: "
            f"{missing_sources[0]}"
        )
    return sources


def get_connection(db_path: str = DEFAULT_DB_PATH) -> duckdb.DuckDBPyConnection:
    return duckdb.connect(db_path)


def infer_period_from_source(source: str) -> str:
    if "yellow_tripdata_2019-" in source:
        return "pre_covid"
    if "yellow_tripdata_2020-" in source:
        return "covid"
    if "yellow_tripdata_2021-" in source or "yellow_tripdata_2022-" in source:
        return "intermediate"
    if "yellow_tripdata_2023-" in source:
        return "post_covid"
    return "other"


def extract_year_month(source: str) -> tuple[int, int]:
    stem = Path(source).stem
    year_month = stem.split("_")[2]
    year_str, month_str = year_month.split("-")
    return int(year_str), int(month_str)


def run_query(
    select_sql: str,
    data_dir: str | Path = DEFAULT_DATA_DIR,
    db_path: str = DEFAULT_DB_PATH,
    skip_errors: bool = True,
) -> tuple[pd.DataFrame, list[str]]:
    con = get_connection(db_path)
    results: list[pd.DataFrame] = []
    skipped_sources: list[str] = []

    for source in resolve_sources(data_dir):
        print(f"Querying: {source}")
        query = f"""
            SELECT
                base.*,
                '{infer_period_from_source(source)}' AS period,
                {extract_year_month(source)[0]} AS year,
                {extract_year_month(source)[1]} AS month,
                '{source.replace("'", "''")}' AS source
            FROM (
                {select_sql.strip().rstrip(';')}
            ) AS base
        """
        query = query.replace("read_parquet('__SOURCE__'", f"read_parquet('{source}'")

        try:
            results.append(con.execute(query).fetchdf())
        except Exception as exc:
            if not skip_errors:
                con.close()
                raise
            print(f"Skipping unreadable source: {source}")
            print(f"Reason: {exc}")
            skipped_sources.append(source)

    if not results:
        con.close()
        return pd.DataFrame(), skipped_sources

    df = pd.concat(results, ignore_index=True, sort=False)
    con.close()
    return df, skipped_sources


def build_monthly_summary(
    data_dir: str | Path = DEFAULT_DATA_DIR,
    db_path: str = DEFAULT_DB_PATH,
    skip_errors: bool = True,
) -> tuple[pd.DataFrame, list[str]]:
    select_sql = """
        SELECT
            COUNT(*) AS trip_count,
            AVG(fare_amount) AS avg_fare,
            AVG(tip_amount) AS avg_tip
        FROM read_parquet('__SOURCE__', union_by_name = true)
    """
    df, skipped_sources = run_query(
        select_sql=select_sql,
        data_dir=data_dir,
        db_path=db_path,
        skip_errors=skip_errors,
    )
    if df.empty:
        return df, skipped_sources

    df = df.sort_values(["year", "month"]).reset_index(drop=True)
    return df, skipped_sources


def build_period_summary(
    data_dir: str | Path = DEFAULT_DATA_DIR,
    db_path: str = DEFAULT_DB_PATH,
    skip_errors: bool = True,
    monthly_summary: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, list[str]]:
    skipped_sources: list[str] = []
    if monthly_summary is None:
        monthly_summary, skipped_sources = build_monthly_summary(
            data_dir=data_dir,
            db_path=db_path,
            skip_errors=skip_errors,
        )
    if monthly_summary.empty:
        return monthly_summary, skipped_sources

    period_summary = (
        monthly_summary.groupby("period", as_index=False)
        .agg(
            trip_count=("trip_count", "sum"),
            avg_fare=("avg_fare", "mean"),
            avg_tip=("avg_tip", "mean"),
        )
        .sort_values("period")
        .reset_index(drop=True)
    )
    return period_summary, skipped_sources


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Query local NYC taxi parquet files with DuckDB."
    )
    parser.add_argument(
        "--data-dir",
        default=DEFAULT_DATA_DIR,
        help="directory containing local parquet files",
    )
    parser.add_argument(
        "--db-path",
        default=DEFAULT_DB_PATH,
        help="path to the DuckDB database file, defaults to in-memory",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    monthly_summary, skipped_sources = build_monthly_summary(
        data_dir=args.data_dir,
        db_path=args.db_path,
    )
    period_summary, period_skips = build_period_summary(
        data_dir=args.data_dir,
        db_path=args.db_path,
        monthly_summary=monthly_summary,
    )
    skipped_sources = sorted(set(skipped_sources + period_skips))

    if period_summary.empty or monthly_summary.empty:
        print("No parquet sources were summarized successfully.")
        return 1

    print("\nPeriod summary:")
    print(period_summary)

    print("\nMonthly summary:")
    print(
        monthly_summary[
            ["period", "year", "month", "trip_count", "avg_fare", "avg_tip", "source"]
        ]
    )

    if skipped_sources:
        print("\nSkipped sources:")
        for source in skipped_sources:
            print(source)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
