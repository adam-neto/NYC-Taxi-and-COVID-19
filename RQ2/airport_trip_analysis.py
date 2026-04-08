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
from airport_recovery_regression import (
    build_airport_panel_summary,
    build_airport_regression_outputs,
)

JFK_LOCATION_ID = 132
LGA_LOCATION_ID = 138
RQ2_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = RQ2_DIR / "outputs"
PERIOD_ORDER = ["pre_covid", "covid", "intermediate", "post_covid"]
MAIN_OUTPUT_FILES = {
    "airport_monthly": "airport_monthly_summary.csv",
    "airport_share": "airport_monthly_share.csv",
    "airport_period_share": "airport_period_share_summary.csv",
    "airport_period": "airport_period_summary.csv",
    "airport_mix": "airport_monthly_mix.csv",
    "recovery_summary": "airport_recovery_summary.csv",
    "airport_panel": "airport_monthly_panel.csv",
    "regression_coefficients": "airport_regression_coefficients.csv",
    "regression_diagnostics": "airport_regression_diagnostics.csv",
}
ROBUSTNESS_OUTPUT_FILES = {
    "airport_monthly": "airport_pickup_only_monthly_summary.csv",
    "airport_share": "airport_pickup_only_monthly_share.csv",
    "airport_panel": "airport_pickup_only_monthly_panel.csv",
    "regression_coefficients": "airport_pickup_only_regression_coefficients.csv",
    "regression_diagnostics": "airport_pickup_only_regression_diagnostics.csv",
}


def build_airport_monthly_summary(
    data_dir: str | Path = q.DEFAULT_DATA_DIR,
    db_path: str = q.DEFAULT_DB_PATH,
    skip_errors: bool = True,
    airport_definition: str = "pickup_or_dropoff",
) -> tuple[pd.DataFrame, list[str]]:
    if airport_definition == "pickup_or_dropoff":
        airport_case = f"""
            CASE
                WHEN PULocationID = {JFK_LOCATION_ID} OR DOLocationID = {JFK_LOCATION_ID}
                    THEN 'JFK'
                WHEN PULocationID = {LGA_LOCATION_ID} OR DOLocationID = {LGA_LOCATION_ID}
                    THEN 'LaGuardia'
            END
        """
        where_clause = f"""
            PULocationID IN ({JFK_LOCATION_ID}, {LGA_LOCATION_ID})
            OR DOLocationID IN ({JFK_LOCATION_ID}, {LGA_LOCATION_ID})
        """
    elif airport_definition == "pickup_only":
        airport_case = f"""
            CASE
                WHEN PULocationID = {JFK_LOCATION_ID} THEN 'JFK'
                WHEN PULocationID = {LGA_LOCATION_ID} THEN 'LaGuardia'
            END
        """
        where_clause = f"PULocationID IN ({JFK_LOCATION_ID}, {LGA_LOCATION_ID})"
    else:
        raise ValueError(
            "airport_definition must be 'pickup_or_dropoff' or 'pickup_only'"
        )

    select_sql = f"""
        SELECT
            {airport_case} AS airport,
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
            {where_clause}
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


def build_airport_period_share_summary(airport_share: pd.DataFrame) -> pd.DataFrame:
    summary = (
        airport_share.groupby(["period", "airport"], as_index=False)
        .agg(
            airport_trip_count=("airport_trip_count", "sum"),
            all_trip_count=("all_trip_count", "sum"),
        )
    )
    summary["airport_trip_share"] = (
        summary["airport_trip_count"] / summary["all_trip_count"]
    )
    summary["period"] = pd.Categorical(
        summary["period"], categories=PERIOD_ORDER, ordered=True
    )
    return summary.sort_values(["airport", "period"]).reset_index(drop=True)


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


def build_airport_output_bundle(
    airport_monthly: pd.DataFrame,
    overall_monthly: pd.DataFrame,
    include_extended_outputs: bool = True,
) -> dict[str, pd.DataFrame]:
    airport_share = build_airport_share_summary(airport_monthly, overall_monthly)
    airport_panel = build_airport_panel_summary(airport_share)
    regression_coefficients, regression_diagnostics = build_airport_regression_outputs(
        airport_panel
    )
    output_bundle = {
        "airport_monthly": airport_monthly,
        "airport_share": airport_share,
        "airport_panel": airport_panel,
        "regression_coefficients": regression_coefficients,
        "regression_diagnostics": regression_diagnostics,
    }
    if include_extended_outputs:
        airport_period = build_airport_period_summary(airport_monthly)
        output_bundle["airport_period_share"] = build_airport_period_share_summary(
            airport_share
        )
        output_bundle["airport_period"] = airport_period
        output_bundle["airport_mix"] = build_airport_mix_summary(airport_monthly)
        output_bundle["recovery_summary"] = build_recovery_summary(airport_period)
    return output_bundle


def save_named_outputs(
    output_frames: dict[str, pd.DataFrame],
    output_files: dict[str, str],
    output_dir: str | Path,
) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for key, filename in output_files.items():
        output_frames[key].to_csv(output_dir / filename, index=False)


def run_airport_analysis(
    data_dir: str | Path = q.DEFAULT_DATA_DIR,
    db_path: str = q.DEFAULT_DB_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, pd.DataFrame | list[str]]:
    overall_monthly, overall_skips = q.build_monthly_summary(
        data_dir=data_dir,
        db_path=db_path,
    )
    airport_monthly, airport_skips = build_airport_monthly_summary(
        data_dir=data_dir,
        db_path=db_path,
    )
    pickup_only_monthly, pickup_only_skips = build_airport_monthly_summary(
        data_dir=data_dir,
        db_path=db_path,
        airport_definition="pickup_only",
    )

    skipped_sources = sorted(set(overall_skips + airport_skips + pickup_only_skips))

    if overall_monthly.empty or airport_monthly.empty:
        return {
            "overall_monthly": overall_monthly,
            "airport_monthly": airport_monthly,
            "skipped_sources": skipped_sources,
        }

    main_outputs = build_airport_output_bundle(airport_monthly, overall_monthly)
    pickup_only_outputs = build_airport_output_bundle(
        pickup_only_monthly,
        overall_monthly,
        include_extended_outputs=False,
    )

    save_named_outputs(main_outputs, MAIN_OUTPUT_FILES, output_dir)
    save_named_outputs(pickup_only_outputs, ROBUSTNESS_OUTPUT_FILES, output_dir)

    return {
        "overall_monthly": overall_monthly,
        "skipped_sources": skipped_sources,
        **main_outputs,
        "pickup_only_monthly": pickup_only_outputs["airport_monthly"],
        "pickup_only_share": pickup_only_outputs["airport_share"],
        "pickup_only_panel": pickup_only_outputs["airport_panel"],
        "pickup_only_regression_coefficients": pickup_only_outputs[
            "regression_coefficients"
        ],
        "pickup_only_regression_diagnostics": pickup_only_outputs[
            "regression_diagnostics"
        ],
    }


def load_saved_airport_outputs(
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, pd.DataFrame]:
    output_dir = Path(output_dir)
    outputs: dict[str, pd.DataFrame] = {}
    for key, filename in MAIN_OUTPUT_FILES.items():
        path = output_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing required RQ2 output file: {path}")
        outputs[key] = pd.read_csv(path)
    for key, filename in ROBUSTNESS_OUTPUT_FILES.items():
        if key not in {"regression_coefficients", "regression_diagnostics"}:
            continue
        path = output_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing required RQ2 output file: {path}")
        outputs[f"pickup_only_{key}"] = pd.read_csv(path)
    return outputs


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

    results = run_airport_analysis(
        data_dir=args.data_dir,
        db_path=args.db_path,
        output_dir=args.output_dir,
    )
    overall_monthly = results["overall_monthly"]
    airport_monthly = results["airport_monthly"]
    skipped_sources = results["skipped_sources"]

    if (
        isinstance(overall_monthly, pd.DataFrame)
        and isinstance(airport_monthly, pd.DataFrame)
        and (overall_monthly.empty or airport_monthly.empty)
    ):
        print("Airport analysis could not be built from the local parquet files.")
        return 1

    airport_share = results["airport_share"]
    airport_period = results["airport_period"]
    regression_coefficients = results["regression_coefficients"]
    regression_diagnostics = results["regression_diagnostics"]
    pickup_only_regression_coefficients = results["pickup_only_regression_coefficients"]
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

    print("\nAirport panel regression coefficients:")
    print(
        regression_coefficients[
            regression_coefficients["term"].isin(
                [
                    "is_jfk",
                    "jfk_x_covid",
                    "jfk_x_intermediate",
                    "jfk_x_post_covid",
                ]
            )
        ][
            [
                "model",
                "term",
                "coefficient",
                "robust_se",
                "p_value_normal_approx",
            ]
        ]
    )

    print("\nAirport regression diagnostics:")
    print(regression_diagnostics)

    print("\nPickup-only robustness regression coefficients:")
    print(
        pickup_only_regression_coefficients[
            pickup_only_regression_coefficients["term"].isin(
                [
                    "is_jfk",
                    "jfk_x_covid",
                    "jfk_x_intermediate",
                    "jfk_x_post_covid",
                ]
            )
        ][
            [
                "model",
                "term",
                "coefficient",
                "robust_se",
                "p_value_normal_approx",
            ]
        ]
    )

    print(f"\nSaved CSV outputs to {Path(args.output_dir).resolve()}")

    if skipped_sources:
        print("\nSkipped sources:")
        for source in skipped_sources:
            print(source)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
