from __future__ import annotations
import argparse
from pathlib import Path
import sys
import pandas as pd

RQ1_DIR = Path(__file__).resolve().parent
ROOT_DIR = RQ1_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import query_taxi_duckdb as q

DEFAULT_OUTPUT_DIR = RQ1_DIR / "outputs"
PERIOD_ORDER = ["pre_covid", "covid", "intermediate", "post_covid"]

def build_tipping_monthly_summary(
    data_dir: str | Path = q.DEFAULT_DATA_DIR,
    db_path: str = q.DEFAULT_DB_PATH,
    skip_errors: bool = True,
) -> tuple[pd.DataFrame, list[str]]:
    #credit card trips: payment_type = 1
    select_sql = """
        SELECT
            COUNT(*) AS valid_cc_trip_count,
            SUM(fare_amount) AS fare_amount_sum,
            SUM(tip_amount) AS tip_amount_sum,
            AVG(tip_amount) AS avg_tip,
            AVG(fare_amount) AS avg_fare,
            AVG(tip_amount / fare_amount) * 100 AS avg_tip_percent
        FROM read_parquet('__SOURCE__', union_by_name = true)
        WHERE payment_type = 1 AND fare_amount > 0
    """
    df, skipped_sources = q.run_query(
        select_sql=select_sql,
        data_dir=data_dir,
        db_path=db_path,
        skip_errors=skip_errors,
    )
    if df.empty:
        return df, skipped_sources

    df = df.sort_values(["year", "month"]).reset_index(drop=True)
    return df, skipped_sources

def build_tipping_period_summary(tipping_monthly: pd.DataFrame) -> pd.DataFrame:
    summary = (
        tipping_monthly.groupby("period", as_index=False)
        .agg(
            valid_cc_trip_count=("valid_cc_trip_count", "sum"),
            fare_amount_sum=("fare_amount_sum", "sum"),
            tip_amount_sum=("tip_amount_sum", "sum"),
        )
    )
    summary["period_avg_tip_percent"] = (summary["tip_amount_sum"] / summary["fare_amount_sum"]) * 100
    summary["period"] = pd.Categorical(
        summary["period"], categories=PERIOD_ORDER, ordered=True
    )
    return summary.sort_values("period").reset_index(drop=True)

def build_tipping_change_summary(tipping_period: pd.DataFrame) -> pd.DataFrame:
    baseline = tipping_period[tipping_period["period"] == "pre_covid"][["period_avg_tip_percent"]]
    
    if baseline.empty:
        return tipping_period.copy()

    baseline_val = baseline.iloc[0]["period_avg_tip_percent"]
    summary = tipping_period.copy()
    summary["tip_percent_change_pp"] = summary["period_avg_tip_percent"] - baseline_val
    return summary

def save_outputs(
    tipping_monthly: pd.DataFrame,
    tipping_period: pd.DataFrame,
    tipping_change: pd.DataFrame,
    output_dir: str | Path,
) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    tipping_monthly.to_csv(output_dir / "tipping_monthly_summary.csv", index=False)
    tipping_period.to_csv(output_dir / "tipping_period_summary.csv", index=False)
    tipping_change.to_csv(output_dir / "tipping_change_summary.csv", index=False)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run RQ1 tipping behavior analysis.")
    parser.add_argument("--data-dir", default=q.DEFAULT_DATA_DIR)
    parser.add_argument("--db-path", default=q.DEFAULT_DB_PATH)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()

def main() -> int:
    args = parse_args()

    tipping_monthly, skipped = build_tipping_monthly_summary(
        data_dir=args.data_dir,
        db_path=args.db_path,
    )
    if tipping_monthly.empty:
        print("Tipping analysis could not be built from the local parquet files.")
        return 1

    tipping_period = build_tipping_period_summary(tipping_monthly)
    tipping_change = build_tipping_change_summary(tipping_period)

    save_outputs(tipping_monthly, tipping_period, tipping_change, args.output_dir)

    print("\nTipping period summary:")
    print(tipping_change[["period", "valid_cc_trip_count", "period_avg_tip_percent", "tip_percent_change_pp"]])
    print(f"\nSaved outputs to {Path(args.output_dir).resolve()}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())