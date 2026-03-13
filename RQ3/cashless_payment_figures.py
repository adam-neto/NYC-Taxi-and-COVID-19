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

RQ3_DIR = Path(__file__).resolve().parent
ROOT_DIR = RQ3_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(RQ3_DIR) not in sys.path:
    sys.path.insert(0, str(RQ3_DIR))

import query_taxi_duckdb as q
from cashless_payment_analysis import (
    DEFAULT_LOOKUP_PATH,
    DEFAULT_OUTPUT_DIR,
    PERIOD_ORDER,
    BOROUGH_ORDER,
    build_borough_monthly_summary,
    build_borough_period_summary,
    build_cashless_change_summary,
    build_cashless_monthly_summary,
    build_cashless_period_summary,
    save_outputs,
)

DEFAULT_FIGURE_DIR = RQ3_DIR / "figures"


def add_month_start(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["month_start"] = pd.to_datetime(
        dict(year=df["year"], month=df["month"], day=1)
    )
    return df


def plot_monthly_cashless_share(
    cashless_monthly: pd.DataFrame,
    figure_dir: str | Path,
) -> None:
    figure_dir = Path(figure_dir)
    figure_dir.mkdir(parents=True, exist_ok=True)

    plot_df = add_month_start(cashless_monthly)
    plt.figure(figsize=(12, 6))
    plt.plot(
        plot_df["month_start"],
        plot_df["cashless_share_known_payments"] * 100,
        marker="o",
        label="Cashless share among known payments",
    )
    plt.plot(
        plot_df["month_start"],
        plot_df["cashless_share_all_trips"] * 100,
        marker="o",
        label="Cashless share among all trips",
    )
    plt.axvline(pd.Timestamp("2020-03-01"), linestyle="--", linewidth=1)
    plt.title("Monthly Cashless Share for NYC Yellow Taxi Trips")
    plt.xlabel("Month")
    plt.ylabel("Cashless share (%)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figure_dir / "monthly_cashless_share.png", dpi=200)
    plt.close()



def plot_period_payment_mix(
    cashless_period: pd.DataFrame,
    figure_dir: str | Path,
) -> None:
    figure_dir = Path(figure_dir)
    figure_dir.mkdir(parents=True, exist_ok=True)

    plot_df = cashless_period.copy()
    x = range(len(plot_df))
    cashless_pct = plot_df["cashless_share_all_trips"] * 100
    cash_pct = (plot_df["cash_trip_count"] / plot_df["all_trip_count"]) * 100
    ambiguous_pct = plot_df["ambiguous_payment_share"] * 100

    plt.figure(figsize=(10, 6))
    plt.bar(x, cashless_pct, label="Cashless")
    plt.bar(x, cash_pct, bottom=cashless_pct, label="Cash")
    plt.bar(x, ambiguous_pct, bottom=cashless_pct + cash_pct, label="Ambiguous / other")
    plt.xticks(list(x), plot_df["period"])
    plt.title("Payment Mix by Project Period")
    plt.xlabel("Period")
    plt.ylabel("Share of trips (%)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figure_dir / "period_payment_mix.png", dpi=200)
    plt.close()



def plot_period_cashless_change(
    cashless_change: pd.DataFrame,
    figure_dir: str | Path,
) -> None:
    figure_dir = Path(figure_dir)
    figure_dir.mkdir(parents=True, exist_ok=True)

    plot_df = cashless_change[cashless_change["period"] != "pre_covid"].copy()
    x = range(len(plot_df))

    plt.figure(figsize=(10, 6))
    plt.bar(x, plot_df["cashless_share_known_change_pp"])
    plt.axhline(0.0, linestyle="--", linewidth=1)
    plt.xticks(list(x), plot_df["period"])
    plt.title("Change in Cashless Share vs Pre-COVID")
    plt.xlabel("Period")
    plt.ylabel("Percentage-point change\n(among known payment trips)")
    plt.tight_layout()
    plt.savefig(figure_dir / "cashless_share_change_vs_pre_covid.png", dpi=200)
    plt.close()



def plot_borough_cashless_share(
    borough_period: pd.DataFrame,
    figure_dir: str | Path,
) -> None:
    if borough_period.empty:
        return

    figure_dir = Path(figure_dir)
    figure_dir.mkdir(parents=True, exist_ok=True)

    plot_df = borough_period[
        borough_period["borough"].isin(BOROUGH_ORDER)
    ].copy()
    if plot_df.empty:
        return

    pivot = (
        plot_df.pivot(
            index="borough",
            columns="period",
            values="cashless_share_known_payments",
        )
        .reindex(BOROUGH_ORDER)
        .reindex(columns=PERIOD_ORDER)
        * 100
    )

    ax = pivot.plot(kind="bar", figsize=(12, 6))
    ax.set_title("Cashless Share by Pickup Borough and Period")
    ax.set_xlabel("Pickup borough")
    ax.set_ylabel("Cashless share among known payments (%)")
    ax.legend(title="Period")
    plt.tight_layout()
    plt.savefig(figure_dir / "borough_cashless_share.png", dpi=200)
    plt.close()



def create_figures(
    cashless_monthly: pd.DataFrame,
    cashless_period: pd.DataFrame,
    cashless_change: pd.DataFrame,
    borough_period: pd.DataFrame,
    figure_dir: str | Path,
) -> None:
    plot_monthly_cashless_share(cashless_monthly, figure_dir)
    plot_period_payment_mix(cashless_period, figure_dir)
    plot_period_cashless_change(cashless_change, figure_dir)
    plot_borough_cashless_share(borough_period, figure_dir)



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
        help="path to taxi_zone_lookup.csv for borough summaries",
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

    cashless_monthly, cashless_skips = build_cashless_monthly_summary(
        data_dir=args.data_dir,
        db_path=args.db_path,
    )
    if cashless_monthly.empty:
        print("Cashless payment figures could not be built from the local parquet files.")
        return 1

    cashless_period = build_cashless_period_summary(cashless_monthly)
    cashless_change = build_cashless_change_summary(cashless_period)

    borough_monthly, borough_skips = build_borough_monthly_summary(
        lookup_path=args.lookup_path,
        data_dir=args.data_dir,
        db_path=args.db_path,
    )
    borough_period = build_borough_period_summary(borough_monthly)

    skipped_sources = sorted(set(cashless_skips + borough_skips))

    save_outputs(
        cashless_monthly=cashless_monthly,
        cashless_period=cashless_period,
        cashless_change=cashless_change,
        borough_period=borough_period,
        output_dir=args.output_dir,
    )
    create_figures(
        cashless_monthly=cashless_monthly,
        cashless_period=cashless_period,
        cashless_change=cashless_change,
        borough_period=borough_period,
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
