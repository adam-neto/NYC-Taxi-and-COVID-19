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

RQ2_DIR = Path(__file__).resolve().parent
ROOT_DIR = RQ2_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(RQ2_DIR) not in sys.path:
    sys.path.insert(0, str(RQ2_DIR))

import query_taxi_duckdb as q
from airport_trip_analysis import (
    DEFAULT_OUTPUT_DIR,
    build_airport_mix_summary,
    build_airport_monthly_summary,
    build_airport_period_summary,
    build_airport_share_summary,
    build_recovery_summary,
    save_outputs,
)

DEFAULT_FIGURE_DIR = RQ2_DIR / "figures"
PERIOD_ORDER = ["pre_covid", "covid", "intermediate", "post_covid"]
AIRPORT_ORDER = ["JFK", "LaGuardia"]
AIRPORT_COLORS = {"JFK": "#1f77b4", "LaGuardia": "#d62728"}


def add_month_start(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["month_start"] = pd.to_datetime(
        dict(year=df["year"], month=df["month"], day=1)
    )
    return df


def plot_monthly_counts(airport_monthly: pd.DataFrame, figure_dir: str | Path) -> None:
    figure_dir = Path(figure_dir)
    figure_dir.mkdir(parents=True, exist_ok=True)

    plot_df = add_month_start(airport_monthly)
    plt.figure(figsize=(12, 6))
    sns.lineplot(
        data=plot_df,
        x="month_start",
        y="airport_trip_count",
        hue="airport",
        hue_order=AIRPORT_ORDER,
        palette=AIRPORT_COLORS,
        marker="o",
    )
    plt.title("Monthly Airport-Related Yellow Taxi Trips")
    plt.xlabel("Month")
    plt.ylabel("Trip count")
    plt.tight_layout()
    plt.savefig(figure_dir / "monthly_airport_trip_counts.png", dpi=200)
    plt.close()


def plot_monthly_share(airport_share: pd.DataFrame, figure_dir: str | Path) -> None:
    figure_dir = Path(figure_dir)
    figure_dir.mkdir(parents=True, exist_ok=True)

    plot_df = add_month_start(airport_share)
    plot_df["airport_trip_share_pct"] = plot_df["airport_trip_share"] * 100

    plt.figure(figsize=(12, 6))
    sns.lineplot(
        data=plot_df,
        x="month_start",
        y="airport_trip_share_pct",
        hue="airport",
        hue_order=AIRPORT_ORDER,
        palette=AIRPORT_COLORS,
        marker="o",
    )
    plt.title("Airport Trips as a Share of All Yellow Taxi Trips")
    plt.xlabel("Month")
    plt.ylabel("Share of all yellow taxi trips (%)")
    plt.tight_layout()
    plt.savefig(figure_dir / "monthly_airport_trip_share.png", dpi=200)
    plt.close()


def plot_airport_mix(airport_mix: pd.DataFrame, figure_dir: str | Path) -> None:
    figure_dir = Path(figure_dir)
    figure_dir.mkdir(parents=True, exist_ok=True)

    plot_df = add_month_start(airport_mix)
    plot_df["airport_mix_share_pct"] = plot_df["airport_mix_share"] * 100

    plt.figure(figsize=(12, 6))
    sns.lineplot(
        data=plot_df,
        x="month_start",
        y="airport_mix_share_pct",
        hue="airport",
        hue_order=AIRPORT_ORDER,
        palette=AIRPORT_COLORS,
        marker="o",
    )
    plt.title("Share of Combined Airport Taxi Trips by Airport")
    plt.xlabel("Month")
    plt.ylabel("Share of airport-related taxi trips (%)")
    plt.tight_layout()
    plt.savefig(figure_dir / "monthly_airport_mix_share.png", dpi=200)
    plt.close()


def plot_recovery_index(
    recovery_summary: pd.DataFrame,
    figure_dir: str | Path,
) -> None:
    figure_dir = Path(figure_dir)
    figure_dir.mkdir(parents=True, exist_ok=True)

    plot_df = recovery_summary[
        recovery_summary["period"].isin(["covid", "intermediate", "post_covid"])
    ].copy()

    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=plot_df,
        x="period",
        y="trip_count_index_vs_pre_covid",
        hue="airport",
        order=["covid", "intermediate", "post_covid"],
        hue_order=AIRPORT_ORDER,
        palette=AIRPORT_COLORS,
    )
    plt.axhline(1.0, color="black", linestyle="--", linewidth=1)
    plt.title("Recovery Index Relative to Pre-COVID Airport Trip Volume")
    plt.xlabel("Period")
    plt.ylabel("Trip count relative to pre-COVID baseline")
    plt.tight_layout()
    plt.savefig(figure_dir / "airport_recovery_index.png", dpi=200)
    plt.close()


def plot_avg_total_amount(
    airport_period: pd.DataFrame,
    figure_dir: str | Path,
) -> None:
    figure_dir = Path(figure_dir)
    figure_dir.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=airport_period,
        x="period",
        y="avg_total_amount",
        hue="airport",
        order=PERIOD_ORDER,
        hue_order=AIRPORT_ORDER,
        palette=AIRPORT_COLORS,
    )
    plt.title("Average Total Fare for Airport Trips by Period")
    plt.xlabel("Period")
    plt.ylabel("Average total amount")
    plt.tight_layout()
    plt.savefig(figure_dir / "airport_average_total_amount.png", dpi=200)
    plt.close()


def create_figures(
    airport_monthly: pd.DataFrame,
    airport_share: pd.DataFrame,
    airport_period: pd.DataFrame,
    airport_mix: pd.DataFrame,
    recovery_summary: pd.DataFrame,
    figure_dir: str | Path,
) -> None:
    plot_monthly_counts(airport_monthly, figure_dir)
    plot_monthly_share(airport_share, figure_dir)
    plot_airport_mix(airport_mix, figure_dir)
    plot_recovery_index(recovery_summary, figure_dir)
    plot_avg_total_amount(airport_period, figure_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate RQ2 airport recovery figures for JFK and LaGuardia."
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
    parser.add_argument(
        "--figure-dir",
        default=DEFAULT_FIGURE_DIR,
        help="directory to write figure outputs",
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
        print("Airport figures could not be built from the local parquet files.")
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
    create_figures(
        airport_monthly=airport_monthly,
        airport_share=airport_share,
        airport_period=airport_period,
        airport_mix=airport_mix,
        recovery_summary=recovery_summary,
        figure_dir=args.figure_dir,
    )

    print(f"Saved CSV outputs to {Path(args.output_dir).resolve()}")
    print(f"Saved figures to {Path(args.figure_dir).resolve()}")

    if skipped_sources:
        print("\nSkipped sources:")
        for source in skipped_sources:
            print(source)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
