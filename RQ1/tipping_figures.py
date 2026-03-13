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

RQ1_DIR = Path(__file__).resolve().parent
ROOT_DIR = RQ1_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import query_taxi_duckdb as q
from tipping_analysis import (
    DEFAULT_OUTPUT_DIR,
    build_tipping_change_summary,
    build_tipping_monthly_summary,
    build_tipping_period_summary,
    save_outputs,
)

DEFAULT_FIGURE_DIR = RQ1_DIR / "figures"
PERIOD_ORDER = ["pre_covid", "covid", "intermediate", "post_covid"]

def add_month_start(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["month_start"] = pd.to_datetime(dict(year=df["year"], month=df["month"], day=1))
    return df

def plot_monthly_tipping(tipping_monthly: pd.DataFrame, figure_dir: Path) -> None:
    plot_df = add_month_start(tipping_monthly)
    plt.figure(figsize=(12, 6))
    plt.plot(
        plot_df["month_start"],
        plot_df["avg_tip_percent"],
        marker="o",
        color="#2ca02c"
    )
    plt.axvline(pd.Timestamp("2020-03-01"), color="black", linestyle="--", linewidth=1)
    plt.title("Monthly Average Tip Percentage (Credit Card Trips)")
    plt.xlabel("Month")
    plt.ylabel("Average Tip (%)")
    plt.tight_layout()
    plt.savefig(figure_dir / "monthly_tipping_trend.png", dpi=200)
    plt.close()

def plot_period_tipping_change(tipping_change: pd.DataFrame, figure_dir: Path) -> None:
    plot_df = tipping_change[tipping_change["period"] != "pre_covid"].copy()
    x = range(len(plot_df))

    plt.figure(figsize=(10, 6))
    plt.bar(x, plot_df["tip_percent_change_pp"], color="#ff7f0e")
    plt.axhline(0.0, color="black", linestyle="--", linewidth=1)
    plt.xticks(list(x), plot_df["period"])
    plt.title("Change in Tip Percentage vs Pre-COVID Baseline")
    plt.xlabel("Period")
    plt.ylabel("Percentage-point change")
    plt.tight_layout()
    plt.savefig(figure_dir / "period_tipping_change.png", dpi=200)
    plt.close()

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default=q.DEFAULT_DATA_DIR)
    parser.add_argument("--db-path", default=q.DEFAULT_DB_PATH)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--figure-dir", default=DEFAULT_FIGURE_DIR)
    args = parser.parse_args()

    tipping_monthly, _ = build_tipping_monthly_summary(args.data_dir, args.db_path)
    if tipping_monthly.empty:
        return 1

    tipping_period = build_tipping_period_summary(tipping_monthly)
    tipping_change = build_tipping_change_summary(tipping_period)

    Path(args.figure_dir).mkdir(parents=True, exist_ok=True)
    plot_monthly_tipping(tipping_monthly, Path(args.figure_dir))
    plot_period_tipping_change(tipping_change, Path(args.figure_dir))
    
    print(f"Saved figures to {Path(args.figure_dir).resolve()}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())