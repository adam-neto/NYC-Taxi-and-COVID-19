#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

RQ3_DIR = Path(__file__).resolve().parent
ROOT_DIR = RQ3_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(RQ3_DIR) not in sys.path:
    sys.path.insert(0, str(RQ3_DIR))

import query_taxi_duckdb as q
from cashless_payment_analysis import (
    DEFAULT_OUTPUT_DIR,
    PERIOD_ORDER,
    BOROUGH_ORDER,
    DEFAULT_LOOKUP_PATH,
    load_saved_cashless_outputs,
    run_cashless_analysis,
)
from cashless_payment_model import DEFAULT_SAMPLE_ROWS_PER_MONTH

DEFAULT_FIGURE_DIR = RQ3_DIR / "figures"
PERIOD_LABELS = {
    "pre_covid": "Pre-COVID",
    "covid": "COVID",
    "intermediate": "Intermediate",
    "post_covid": "Post-COVID",
}


def add_month_start(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["month_start"] = pd.to_datetime(dict(year=df["year"], month=df["month"], day=1))
    return df


def plot_monthly_cashless_share(cashless_monthly: pd.DataFrame, figure_dir: str | Path) -> None:
    figure_dir = Path(figure_dir)
    figure_dir.mkdir(parents=True, exist_ok=True)

    plot_df = add_month_start(cashless_monthly)
    plt.figure(figsize=(12, 6))
    sns.lineplot(
        data=plot_df,
        x="month_start",
        y=plot_df["cashless_share_known_payments"] * 100,
        marker="o",
        label="Cashless share among known payments",
    )
    sns.lineplot(
        data=plot_df,
        x="month_start",
        y=plot_df["cashless_share_all_trips"] * 100,
        marker="o",
        label="Cashless share among all trips",
    )
    plt.axvline(pd.Timestamp("2020-03-01"), color="black", linestyle="--", linewidth=1)
    plt.title("Monthly Cashless Share for NYC Yellow Taxi Trips")
    plt.xlabel("Month")
    plt.ylabel("Cashless share (%)")
    plt.tight_layout()
    plt.savefig(figure_dir / "monthly_cashless_share.png", dpi=200)
    plt.close()


def plot_period_payment_mix(cashless_period: pd.DataFrame, figure_dir: str | Path) -> None:
    figure_dir = Path(figure_dir)
    figure_dir.mkdir(parents=True, exist_ok=True)

    plot_df = cashless_period.copy()
    plot_df["period_label"] = plot_df["period"].map(PERIOD_LABELS)
    x = range(len(plot_df))
    cashless_pct = plot_df["cashless_share_all_trips"] * 100
    cash_pct = (plot_df["cash_trip_count"] / plot_df["all_trip_count"]) * 100
    ambiguous_pct = plot_df["ambiguous_payment_share"] * 100

    plt.figure(figsize=(10, 6))
    plt.bar(x, cashless_pct, label="Cashless")
    plt.bar(x, cash_pct, bottom=cashless_pct, label="Cash")
    plt.bar(x, ambiguous_pct, bottom=cashless_pct + cash_pct, label="Ambiguous / other")
    plt.xticks(list(x), plot_df["period_label"])
    plt.title("Payment Mix by Project Period")
    plt.xlabel("Period")
    plt.ylabel("Share of trips (%)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figure_dir / "period_payment_mix.png", dpi=200)
    plt.close()


def plot_model_metric_comparison(model_metrics: pd.DataFrame, figure_dir: str | Path) -> None:
    figure_dir = Path(figure_dir)
    figure_dir.mkdir(parents=True, exist_ok=True)
    plot_df = model_metrics.melt(
        id_vars="model",
        value_vars=["accuracy", "precision", "recall", "f1", "roc_auc"],
        var_name="metric",
        value_name="score",
    )
    plt.figure(figsize=(11, 6))
    sns.barplot(data=plot_df, x="metric", y="score", hue="model")
    plt.ylim(0, 1)
    plt.title("RQ3 Model Comparison on Held-Out 2023 Test Months")
    plt.xlabel("Metric")
    plt.ylabel("Score")
    plt.tight_layout()
    plt.savefig(figure_dir / "cashless_model_metric_comparison.png", dpi=200)
    plt.close()


def plot_xgboost_feature_importance(model_top_features: pd.DataFrame, figure_dir: str | Path) -> None:
    figure_dir = Path(figure_dir)
    figure_dir.mkdir(parents=True, exist_ok=True)
    plot_df = model_top_features[model_top_features["model"] == "xgboost"].copy()
    if plot_df.empty:
        return
    plot_df = plot_df.head(12).iloc[::-1]
    plt.figure(figsize=(10, 7))
    sns.barplot(data=plot_df, x="abs_value", y="feature")
    plt.title("Top XGBoost Features for Predicting Cashless Payments")
    plt.xlabel("Importance")
    plt.ylabel("Feature")
    plt.tight_layout()
    plt.savefig(figure_dir / "cashless_xgboost_feature_importance.png", dpi=200)
    plt.close()


def create_figures(outputs: dict[str, pd.DataFrame], figure_dir: str | Path) -> None:
    plot_monthly_cashless_share(outputs["cashless_monthly"], figure_dir)
    plot_period_payment_mix(outputs["cashless_period"], figure_dir)
    plot_model_metric_comparison(outputs["model_metrics"], figure_dir)
    plot_xgboost_feature_importance(outputs["model_top_features"], figure_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate RQ3 cashless payment figures for NYC yellow taxi trips."
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
        "--figure-dir",
        default=DEFAULT_FIGURE_DIR,
        help="directory to write figure outputs",
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
    reused_saved_outputs = False

    try:
        outputs = load_saved_cashless_outputs(args.output_dir)
        skipped_sources: list[str] = []
        reused_saved_outputs = True
    except FileNotFoundError:
        print("RQ3 analysis outputs not found. Running cashless_payment_analysis first...")
        results = run_cashless_analysis(
            data_dir=args.data_dir,
            db_path=args.db_path,
            lookup_path=args.lookup_path,
            output_dir=args.output_dir,
            sample_rows_per_month=args.sample_rows_per_month,
        )
        if results["cashless_monthly"].empty or results["model_metrics"].empty:
            print("Cashless figures could not be built from the local parquet files.")
            return 1
        outputs = load_saved_cashless_outputs(args.output_dir)
        skipped_sources = results["skipped_sources"]

    create_figures(outputs, args.figure_dir)

    if reused_saved_outputs:
        print(f"Reused saved CSV outputs from {Path(args.output_dir).resolve()}")
    else:
        print(f"Saved CSV outputs to {Path(args.output_dir).resolve()}")
    print(f"Saved figures to {Path(args.figure_dir).resolve()}")

    if skipped_sources:
        print("\nSkipped sources:")
        for source in skipped_sources:
            print(source)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
