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
from airport_trip_analysis import (
    DEFAULT_OUTPUT_DIR,
    load_saved_airport_outputs,
    run_airport_analysis,
)

DEFAULT_FIGURE_DIR = RQ2_DIR / "figures"
PERIOD_ORDER = ["pre_covid", "covid", "intermediate", "post_covid"]
AIRPORT_ORDER = ["JFK", "LaGuardia"]
AIRPORT_COLORS = {"JFK": "#1f77b4", "LaGuardia": "#d62728"}
INTERACTION_TERMS = [
    "jfk_x_covid",
    "jfk_x_intermediate",
    "jfk_x_post_covid",
]
TERM_LABELS = {
    "jfk_x_covid": "JFK x COVID",
    "jfk_x_intermediate": "JFK x Intermediate",
    "jfk_x_post_covid": "JFK x Post-COVID",
}
MODEL_LABELS = {
    "airport_trip_share_panel": "Main share model",
    "log_airport_trip_count_panel": "Count robustness model",
}
SPECIFICATION_LABELS = {
    "main": "Pickup or dropoff definition",
    "pickup_only": "Pickup-only definition",
}
SPECIFICATION_COLORS = {
    "main": "#1f77b4",
    "pickup_only": "#d62728",
}


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


def plot_regression_interactions(
    regression_coefficients: pd.DataFrame,
    pickup_only_regression_coefficients: pd.DataFrame,
    figure_dir: str | Path,
) -> None:
    figure_dir = Path(figure_dir)
    figure_dir.mkdir(parents=True, exist_ok=True)

    main_df = regression_coefficients.copy()
    main_df["specification"] = "main"

    pickup_only_df = pickup_only_regression_coefficients.copy()
    pickup_only_df["specification"] = "pickup_only"

    coefficients = pd.concat([main_df, pickup_only_df], ignore_index=True, sort=False)
    coefficients = coefficients[
        coefficients["term"].isin(INTERACTION_TERMS)
        & coefficients["model"].isin(MODEL_LABELS)
    ].copy()
    coefficients["ci_lower"] = coefficients["ci_lower_95"]
    coefficients["ci_upper"] = coefficients["ci_upper_95"]

    model_order = ["airport_trip_share_panel", "log_airport_trip_count_panel"]
    term_positions = {term: index for index, term in enumerate(INTERACTION_TERMS)}
    specification_offsets = {"main": -0.08, "pickup_only": 0.08}

    fig, axes = plt.subplots(1, 2, figsize=(13, 6), sharey=False)

    for axis, model_name in zip(axes, model_order):
        plot_df = coefficients[coefficients["model"] == model_name].copy()

        for specification in ["main", "pickup_only"]:
            spec_df = plot_df[plot_df["specification"] == specification].copy()
            spec_df["x"] = spec_df["term"].map(term_positions) + specification_offsets[
                specification
            ]
            error_low = spec_df["coefficient"] - spec_df["ci_lower"]
            error_high = spec_df["ci_upper"] - spec_df["coefficient"]
            axis.errorbar(
                spec_df["x"],
                spec_df["coefficient"],
                yerr=[error_low, error_high],
                fmt="o",
                capsize=4,
                color=SPECIFICATION_COLORS[specification],
                label=SPECIFICATION_LABELS[specification],
            )

        axis.axhline(0.0, color="black", linestyle="--", linewidth=1)
        axis.set_xticks(range(len(INTERACTION_TERMS)))
        axis.set_xticklabels(
            [TERM_LABELS[term] for term in INTERACTION_TERMS],
            rotation=15,
        )
        axis.set_title(MODEL_LABELS[model_name], pad=10)
        axis.set_xlabel("Interaction term")

    axes[0].set_ylabel("Coefficient estimate with 95% CI")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.93),
        ncol=2,
        frameon=False,
    )
    fig.suptitle(
        "RQ2 JFK Interaction Coefficients\nMain and Robustness Specifications",
        y=0.995,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.80))
    fig.savefig(figure_dir / "airport_regression_interactions.png", dpi=200)
    plt.close(fig)


def create_figures(
    airport_monthly: pd.DataFrame,
    airport_share: pd.DataFrame,
    airport_period: pd.DataFrame,
    airport_mix: pd.DataFrame,
    recovery_summary: pd.DataFrame,
    regression_coefficients: pd.DataFrame,
    pickup_only_regression_coefficients: pd.DataFrame,
    figure_dir: str | Path,
) -> None:
    plot_monthly_counts(airport_monthly, figure_dir)
    plot_monthly_share(airport_share, figure_dir)
    plot_airport_mix(airport_mix, figure_dir)
    plot_recovery_index(recovery_summary, figure_dir)
    plot_avg_total_amount(airport_period, figure_dir)
    plot_regression_interactions(
        regression_coefficients,
        pickup_only_regression_coefficients,
        figure_dir,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate RQ2 airport recovery figures for JFK and LaGuardia."
    )
    parser.add_argument(
        "--data-dir",
        default="taxi_data",
        help="directory containing local parquet files",
    )
    parser.add_argument(
        "--db-path",
        default=":memory:",
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
    reused_saved_outputs = False

    try:
        outputs = load_saved_airport_outputs(args.output_dir)
        skipped_sources: list[str] = []
        reused_saved_outputs = True
    except FileNotFoundError:
        print("RQ2 analysis outputs not found. Running airport_trip_analysis first...")
        results = run_airport_analysis(
            data_dir=args.data_dir,
            db_path=args.db_path,
            output_dir=args.output_dir,
        )
        if (
            results["overall_monthly"].empty
            or results["airport_monthly"].empty
        ):
            print("Airport figures could not be built from the local parquet files.")
            return 1
        outputs = load_saved_airport_outputs(args.output_dir)
        skipped_sources = results["skipped_sources"]

    create_figures(
        airport_monthly=outputs["airport_monthly"],
        airport_share=outputs["airport_share"],
        airport_period=outputs["airport_period"],
        airport_mix=outputs["airport_mix"],
        recovery_summary=outputs["recovery_summary"],
        regression_coefficients=outputs["regression_coefficients"],
        pickup_only_regression_coefficients=outputs[
            "pickup_only_regression_coefficients"
        ],
        figure_dir=args.figure_dir,
    )

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
