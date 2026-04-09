#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

RQ3_DIR = Path(__file__).resolve().parent
ROOT_DIR = RQ3_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(RQ3_DIR) not in sys.path:
    sys.path.insert(0, str(RQ3_DIR))

import query_taxi_duckdb as q
from cashless_payment_model import (
    DEFAULT_LOOKUP_PATH,
    DEFAULT_SAMPLE_ROWS_PER_MONTH,
    build_cashless_model_outputs,
    sample_cashless_trip_modeling_data,
)

DEFAULT_OUTPUT_DIR = RQ3_DIR / "outputs"
PERIOD_ORDER = ["pre_covid", "covid", "intermediate", "post_covid"]
BOROUGH_ORDER = ["Bronx", "Brooklyn", "Manhattan", "Queens", "Staten Island"]
MAIN_OUTPUT_FILES = {
    "cashless_monthly": "cashless_monthly_summary.csv",
    "cashless_period": "cashless_period_summary.csv",
    "cashless_change": "cashless_change_summary.csv",
    "borough_period": "cashless_borough_period_summary.csv",
    "model_split_summary": "cashless_model_split_summary.csv",
    "model_metrics": "cashless_model_metrics.csv",
    "model_feature_importance": "cashless_model_feature_importance.csv",
    "model_top_features": "cashless_model_top_features.csv",
}
OPTIONAL_OUTPUT_FILES = {
    "model_predictions": "cashless_model_predictions.csv",
}


def build_cashless_monthly_summary(
    data_dir: str | Path = q.DEFAULT_DATA_DIR,
    db_path: str = q.DEFAULT_DB_PATH,
    skip_errors: bool = True,
) -> tuple[pd.DataFrame, list[str]]:
    select_sql = """
        SELECT
            COUNT(*) AS all_trip_count,
            SUM(CASE WHEN payment_type = 1 THEN 1 ELSE 0 END) AS cashless_trip_count,
            SUM(CASE WHEN payment_type = 2 THEN 1 ELSE 0 END) AS cash_trip_count,
            SUM(CASE WHEN payment_type NOT IN (1, 2) OR payment_type IS NULL THEN 1 ELSE 0 END)
                AS ambiguous_payment_trip_count,
            AVG(fare_amount) AS avg_fare,
            AVG(total_amount) AS avg_total_amount
        FROM read_parquet('__SOURCE__', union_by_name = true)
    """
    df, skipped_sources = q.run_query(
        select_sql=select_sql,
        data_dir=data_dir,
        db_path=db_path,
        skip_errors=skip_errors,
    )
    if df.empty:
        return df, skipped_sources

    df = add_share_columns(df)
    df = df.sort_values(["year", "month"]).reset_index(drop=True)
    return df, skipped_sources


def add_share_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["known_payment_trip_count"] = (
        df["cashless_trip_count"] + df["cash_trip_count"]
    )
    df["cashless_share_all_trips"] = (
        df["cashless_trip_count"] / df["all_trip_count"]
    )
    df["cashless_share_known_payments"] = df["cashless_trip_count"] / df[
        "known_payment_trip_count"
    ].where(df["known_payment_trip_count"] > 0)
    df["cash_share_known_payments"] = df["cash_trip_count"] / df[
        "known_payment_trip_count"
    ].where(df["known_payment_trip_count"] > 0)
    df["ambiguous_payment_share"] = (
        df["ambiguous_payment_trip_count"] / df["all_trip_count"]
    )
    return df


def build_cashless_period_summary(cashless_monthly: pd.DataFrame) -> pd.DataFrame:
    summary = (
        cashless_monthly.groupby("period", as_index=False)
        .agg(
            all_trip_count=("all_trip_count", "sum"),
            cashless_trip_count=("cashless_trip_count", "sum"),
            cash_trip_count=("cash_trip_count", "sum"),
            ambiguous_payment_trip_count=("ambiguous_payment_trip_count", "sum"),
        )
    )
    summary = add_share_columns(summary)
    summary["period"] = pd.Categorical(
        summary["period"], categories=PERIOD_ORDER, ordered=True
    )
    return summary.sort_values("period").reset_index(drop=True)


def build_cashless_change_summary(cashless_period: pd.DataFrame) -> pd.DataFrame:
    baseline = cashless_period[cashless_period["period"] == "pre_covid"][
        [
            "cashless_share_known_payments",
            "cashless_share_all_trips",
            "ambiguous_payment_share",
        ]
    ]
    if baseline.empty:
        return cashless_period.copy()

    baseline_row = baseline.iloc[0]
    summary = cashless_period.copy()
    summary["cashless_share_known_change_pp"] = (
        summary["cashless_share_known_payments"]
        - baseline_row["cashless_share_known_payments"]
    ) * 100
    summary["cashless_share_all_change_pp"] = (
        summary["cashless_share_all_trips"] - baseline_row["cashless_share_all_trips"]
    ) * 100
    summary["ambiguous_share_change_pp"] = (
        summary["ambiguous_payment_share"] - baseline_row["ambiguous_payment_share"]
    ) * 100
    return summary


def build_borough_monthly_summary(
    lookup_path: str | Path = DEFAULT_LOOKUP_PATH,
    data_dir: str | Path = q.DEFAULT_DATA_DIR,
    db_path: str = q.DEFAULT_DB_PATH,
    skip_errors: bool = True,
) -> tuple[pd.DataFrame, list[str]]:
    lookup_path = Path(lookup_path)
    if not lookup_path.exists():
        return pd.DataFrame(), []

    escaped_lookup = str(lookup_path).replace("'", "''")
    select_sql = f"""
        SELECT
            COALESCE(zone_lookup.Borough, 'Unknown') AS borough,
            COUNT(*) AS all_trip_count,
            SUM(CASE WHEN payment_type = 1 THEN 1 ELSE 0 END) AS cashless_trip_count,
            SUM(CASE WHEN payment_type = 2 THEN 1 ELSE 0 END) AS cash_trip_count,
            SUM(CASE WHEN payment_type NOT IN (1, 2) OR payment_type IS NULL THEN 1 ELSE 0 END)
                AS ambiguous_payment_trip_count
        FROM read_parquet('__SOURCE__', union_by_name = true) AS trips
        LEFT JOIN read_csv_auto('{escaped_lookup}') AS zone_lookup
            ON trips.PULocationID = zone_lookup.LocationID
        GROUP BY borough
    """
    df, skipped_sources = q.run_query(
        select_sql=select_sql,
        data_dir=data_dir,
        db_path=db_path,
        skip_errors=skip_errors,
    )
    if df.empty:
        return df, skipped_sources

    df = add_share_columns(df)
    df = df.sort_values(["borough", "year", "month"]).reset_index(drop=True)
    return df, skipped_sources


def build_borough_period_summary(borough_monthly: pd.DataFrame) -> pd.DataFrame:
    if borough_monthly.empty:
        return borough_monthly

    summary = (
        borough_monthly.groupby(["period", "borough"], as_index=False)
        .agg(
            all_trip_count=("all_trip_count", "sum"),
            cashless_trip_count=("cashless_trip_count", "sum"),
            cash_trip_count=("cash_trip_count", "sum"),
            ambiguous_payment_trip_count=("ambiguous_payment_trip_count", "sum"),
        )
    )
    summary = add_share_columns(summary)
    summary["period"] = pd.Categorical(
        summary["period"], categories=PERIOD_ORDER, ordered=True
    )
    summary["borough_order"] = summary["borough"].map(
        {name: idx for idx, name in enumerate(BOROUGH_ORDER)}
    ).fillna(len(BOROUGH_ORDER))
    summary = summary.sort_values(["borough_order", "period"]).drop(
        columns="borough_order"
    )
    return summary.reset_index(drop=True)


def save_named_outputs(
    output_frames: dict[str, pd.DataFrame],
    output_files: dict[str, str],
    output_dir: str | Path,
) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for key, filename in output_files.items():
        df = output_frames.get(key)
        if df is None or df.empty:
            continue
        df.to_csv(output_dir / filename, index=False)


def run_cashless_analysis(
    data_dir: str | Path = q.DEFAULT_DATA_DIR,
    db_path: str = q.DEFAULT_DB_PATH,
    lookup_path: str | Path = DEFAULT_LOOKUP_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    sample_rows_per_month: int = DEFAULT_SAMPLE_ROWS_PER_MONTH,
) -> dict[str, pd.DataFrame | list[str]]:
    cashless_monthly, cashless_skips = build_cashless_monthly_summary(
        data_dir=data_dir,
        db_path=db_path,
    )
    borough_monthly, borough_skips = build_borough_monthly_summary(
        lookup_path=lookup_path,
        data_dir=data_dir,
        db_path=db_path,
    )
    modeling_df, modeling_skips = sample_cashless_trip_modeling_data(
        lookup_path=lookup_path,
        data_dir=data_dir,
        db_path=db_path,
        sample_rows_per_month=sample_rows_per_month,
    )
    skipped_sources = sorted(set(cashless_skips + borough_skips + modeling_skips))

    if cashless_monthly.empty or modeling_df.empty:
        return {
            "cashless_monthly": cashless_monthly,
            "modeling_df": modeling_df,
            "skipped_sources": skipped_sources,
        }

    cashless_period = build_cashless_period_summary(cashless_monthly)
    cashless_change = build_cashless_change_summary(cashless_period)
    borough_period = build_borough_period_summary(borough_monthly)
    model_outputs = build_cashless_model_outputs(modeling_df)

    output_bundle: dict[str, pd.DataFrame] = {
        "cashless_monthly": cashless_monthly,
        "cashless_period": cashless_period,
        "cashless_change": cashless_change,
        "borough_period": borough_period,
        **model_outputs,
    }
    save_named_outputs(output_bundle, MAIN_OUTPUT_FILES, output_dir)
    save_named_outputs(output_bundle, OPTIONAL_OUTPUT_FILES, output_dir)

    return {
        **output_bundle,
        "modeling_df": modeling_df,
        "skipped_sources": skipped_sources,
    }


def load_saved_cashless_outputs(
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, pd.DataFrame]:
    output_dir = Path(output_dir)
    outputs: dict[str, pd.DataFrame] = {}
    for key, filename in MAIN_OUTPUT_FILES.items():
        path = output_dir / filename
        if key == "borough_period" and not path.exists():
            outputs[key] = pd.DataFrame()
            continue
        if not path.exists():
            raise FileNotFoundError(f"Missing required RQ3 output file: {path}")
        outputs[key] = pd.read_csv(path)
    for key, filename in OPTIONAL_OUTPUT_FILES.items():
        path = output_dir / filename
        if path.exists():
            outputs[key] = pd.read_csv(path)
    return outputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the RQ3 cashless payment analysis for NYC yellow taxi trips."
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
        "--lookup-path",
        default=DEFAULT_LOOKUP_PATH,
        help="path to taxi_zone_lookup.csv for borough and modeling joins",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="directory to write CSV outputs",
    )
    parser.add_argument(
        "--sample-rows-per-month",
        type=int,
        default=DEFAULT_SAMPLE_ROWS_PER_MONTH,
        help="number of known-payment trips to sample per month for the ML model",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    results = run_cashless_analysis(
        data_dir=args.data_dir,
        db_path=args.db_path,
        lookup_path=args.lookup_path,
        output_dir=args.output_dir,
        sample_rows_per_month=args.sample_rows_per_month,
    )

    cashless_monthly = results["cashless_monthly"]
    modeling_df = results["modeling_df"]
    skipped_sources = results["skipped_sources"]

    if (
        isinstance(cashless_monthly, pd.DataFrame)
        and isinstance(modeling_df, pd.DataFrame)
        and (cashless_monthly.empty or modeling_df.empty)
    ):
        print("Cashless payment analysis could not be built from the local parquet files.")
        return 1

    print("\nCashless period summary:")
    print(results["cashless_period"])

    print("\nModel train/test split summary:")
    print(results["model_split_summary"])

    print("\nModel metrics:")
    print(results["model_metrics"])

    print("\nTop model features:")
    print(results["model_top_features"].groupby("model").head(10))

    print(f"\nSaved CSV outputs to {Path(args.output_dir).resolve()}")

    if skipped_sources:
        print("\nSkipped sources:")
        for source in skipped_sources:
            print(source)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
