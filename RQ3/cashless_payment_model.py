#!/usr/bin/env python3

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

try:
    from xgboost import XGBClassifier
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "xgboost is required for the RQ3 modeling workflow. Install it first."
    ) from exc

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import query_taxi_duckdb as q

JFK_LOCATION_ID = 132
LGA_LOCATION_ID = 138
PERIOD_ORDER = ["pre_covid", "covid", "intermediate", "post_covid"]
DEFAULT_LOOKUP_PATH = q.DEFAULT_DATA_DIR + "/taxi_zone_lookup.csv"
DEFAULT_SAMPLE_ROWS_PER_MONTH = 10000
DEFAULT_TEST_START = pd.Timestamp("2023-07-01")
RANDOM_STATE = 42

NUMERIC_FEATURES = [
    "passenger_count",
    "trip_distance",
    "fare_amount",
    "trip_duration_minutes",
    "pickup_hour",
    "pickup_day_of_week",
]
CATEGORICAL_FEATURES = [
    "pickup_borough",
    "dropoff_borough",
    "VendorID",
    "RatecodeID",
    "store_and_fwd_flag",
    "period",
    "month",
    "airport_related",
]
MODEL_FEATURES = [*NUMERIC_FEATURES, *CATEGORICAL_FEATURES]


@dataclass(frozen=True)
class SplitSummary:
    train_rows: int
    test_rows: int
    train_positive_rate: float
    test_positive_rate: float
    test_start: str


def sample_cashless_trip_modeling_data(
    lookup_path: str | Path = DEFAULT_LOOKUP_PATH,
    data_dir: str | Path = q.DEFAULT_DATA_DIR,
    db_path: str = q.DEFAULT_DB_PATH,
    skip_errors: bool = True,
    sample_rows_per_month: int = DEFAULT_SAMPLE_ROWS_PER_MONTH,
) -> tuple[pd.DataFrame, list[str]]:
    lookup_path = Path(lookup_path)
    if not lookup_path.exists():
        raise FileNotFoundError(f"Missing taxi zone lookup file: {lookup_path}")

    sample_clause = ""
    if sample_rows_per_month > 0:
        sample_clause = f"USING SAMPLE reservoir({int(sample_rows_per_month)} ROWS)"

    escaped_lookup = str(lookup_path).replace("'", "''")
    select_sql = f"""
        SELECT
            CASE WHEN payment_type = 1 THEN 1 ELSE 0 END AS is_cashless,
            COALESCE(pu_lookup.Borough, 'Unknown') AS pickup_borough,
            COALESCE(do_lookup.Borough, 'Unknown') AS dropoff_borough,
            CAST(EXTRACT(hour FROM tpep_pickup_datetime) AS INTEGER) AS pickup_hour,
            CAST(EXTRACT(dow FROM tpep_pickup_datetime) AS INTEGER) AS pickup_day_of_week,
            CASE
                WHEN PULocationID IN ({JFK_LOCATION_ID}, {LGA_LOCATION_ID})
                    OR DOLocationID IN ({JFK_LOCATION_ID}, {LGA_LOCATION_ID})
                THEN 'airport_related'
                ELSE 'non_airport'
            END AS airport_related,
            CAST(passenger_count AS DOUBLE) AS passenger_count,
            CAST(trip_distance AS DOUBLE) AS trip_distance,
            CAST(fare_amount AS DOUBLE) AS fare_amount,
            CAST(
                EXTRACT(epoch FROM (tpep_dropoff_datetime - tpep_pickup_datetime)) / 60.0
                AS DOUBLE
            ) AS trip_duration_minutes,
            CAST(VendorID AS VARCHAR) AS VendorID,
            CAST(RatecodeID AS VARCHAR) AS RatecodeID,
            CAST(store_and_fwd_flag AS VARCHAR) AS store_and_fwd_flag
        FROM read_parquet('__SOURCE__', union_by_name = true) AS trips
        LEFT JOIN read_csv_auto('{escaped_lookup}') AS pu_lookup
            ON trips.PULocationID = pu_lookup.LocationID
        LEFT JOIN read_csv_auto('{escaped_lookup}') AS do_lookup
            ON trips.DOLocationID = do_lookup.LocationID
        WHERE
            payment_type IN (1, 2)
            AND fare_amount > 0
            AND trip_distance >= 0
            AND tpep_pickup_datetime IS NOT NULL
            AND tpep_dropoff_datetime IS NOT NULL
            AND tpep_dropoff_datetime >= tpep_pickup_datetime
            AND passenger_count IS NOT NULL
        {sample_clause}
    """
    df, skipped_sources = q.run_query(
        select_sql=select_sql,
        data_dir=data_dir,
        db_path=db_path,
        skip_errors=skip_errors,
    )
    if df.empty:
        return df, skipped_sources

    df = df.copy()
    df["month_start"] = pd.to_datetime(dict(year=df["year"], month=df["month"], day=1))
    df["trip_duration_minutes"] = df["trip_duration_minutes"].clip(lower=0, upper=240)
    df["trip_distance"] = df["trip_distance"].clip(lower=0, upper=100)
    df["fare_amount"] = df["fare_amount"].clip(lower=0, upper=500)
    df["passenger_count"] = df["passenger_count"].clip(lower=0, upper=8)
    df["month"] = df["month"].astype(str).str.zfill(2)
    df["period"] = pd.Categorical(df["period"], categories=PERIOD_ORDER, ordered=True)
    df = df.sort_values(["year", "month_start"]).reset_index(drop=True)
    return df, skipped_sources


def build_preprocessor() -> ColumnTransformer:
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "onehot",
                OneHotEncoder(handle_unknown="ignore", sparse_output=True),
            ),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERIC_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
        ]
    )


def split_train_test(
    df: pd.DataFrame,
    test_start: pd.Timestamp = DEFAULT_TEST_START,
) -> tuple[pd.DataFrame, pd.DataFrame, SplitSummary]:
    train_df = df[df["month_start"] < test_start].copy()
    test_df = df[df["month_start"] >= test_start].copy()
    if train_df.empty or test_df.empty:
        raise ValueError(
            "Train/test split produced an empty partition. Adjust the test_start date."
        )

    summary = SplitSummary(
        train_rows=int(len(train_df)),
        test_rows=int(len(test_df)),
        train_positive_rate=float(train_df["is_cashless"].mean()),
        test_positive_rate=float(test_df["is_cashless"].mean()),
        test_start=str(test_start.date()),
    )
    return train_df, test_df, summary


def build_model_pipelines() -> dict[str, Pipeline]:
    return {
        "dummy_most_frequent": Pipeline(
            steps=[("preprocessor", build_preprocessor()), ("model", DummyClassifier(strategy="most_frequent"))]
        ),
        "logistic_regression": Pipeline(
            steps=[
                ("preprocessor", build_preprocessor()),
                (
                    "model",
                    LogisticRegression(
                        max_iter=1000,
                        solver="lbfgs",
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
        "xgboost": Pipeline(
            steps=[
                ("preprocessor", build_preprocessor()),
                (
                    "model",
                    XGBClassifier(
                        n_estimators=350,
                        max_depth=6,
                        learning_rate=0.05,
                        subsample=0.8,
                        colsample_bytree=0.8,
                        objective="binary:logistic",
                        eval_metric="logloss",
                        random_state=RANDOM_STATE,
                        tree_method="hist",
                        n_jobs=4,
                    ),
                ),
            ]
        ),
    }


def evaluate_classifier(
    model_name: str,
    pipeline: Pipeline,
    x_train: pd.DataFrame,
    y_train: pd.Series,
    x_test: pd.DataFrame,
    y_test: pd.Series,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    pipeline.fit(x_train, y_train)
    y_pred = pipeline.predict(x_test)

    if hasattr(pipeline.named_steps["model"], "predict_proba"):
        y_score = pipeline.predict_proba(x_test)[:, 1]
    elif hasattr(pipeline.named_steps["model"], "decision_function"):
        y_score = pipeline.decision_function(x_test)
    else:
        y_score = y_pred.astype(float)

    metrics = pd.DataFrame(
        [
            {
                "model": model_name,
                "accuracy": accuracy_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred, zero_division=0),
                "recall": recall_score(y_test, y_pred, zero_division=0),
                "f1": f1_score(y_test, y_pred, zero_division=0),
                "roc_auc": roc_auc_score(y_test, y_score),
                "average_precision": average_precision_score(y_test, y_score),
                "test_rows": int(len(y_test)),
                "test_positive_rate": float(y_test.mean()),
                "predicted_positive_rate": float(np.mean(y_pred)),
            }
        ]
    )

    prediction_frame = pd.DataFrame(
        {
            "model": model_name,
            "actual_is_cashless": y_test.to_numpy(),
            "predicted_is_cashless": y_pred,
            "predicted_probability_cashless": y_score,
        }
    )
    return metrics, prediction_frame


def build_feature_importance_tables(
    fitted_pipeline: Pipeline,
    model_name: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    preprocessor = fitted_pipeline.named_steps["preprocessor"]
    feature_names = preprocessor.get_feature_names_out()
    model = fitted_pipeline.named_steps["model"]

    if model_name == "logistic_regression":
        coefficients = model.coef_[0]
        full_table = pd.DataFrame(
            {
                "model": model_name,
                "feature": feature_names,
                "value": coefficients,
                "abs_value": np.abs(coefficients),
                "importance_type": "coefficient",
            }
        ).sort_values("abs_value", ascending=False)
        top_table = full_table.head(20).reset_index(drop=True)
        return full_table.reset_index(drop=True), top_table

    if model_name == "xgboost":
        importances = model.feature_importances_
        full_table = pd.DataFrame(
            {
                "model": model_name,
                "feature": feature_names,
                "value": importances,
                "abs_value": np.abs(importances),
                "importance_type": "gain_proxy",
            }
        ).sort_values("abs_value", ascending=False)
        top_table = full_table.head(20).reset_index(drop=True)
        return full_table.reset_index(drop=True), top_table

    empty = pd.DataFrame(columns=["model", "feature", "value", "abs_value", "importance_type"])
    return empty, empty


def build_cashless_model_outputs(
    modeling_df: pd.DataFrame,
    test_start: pd.Timestamp = DEFAULT_TEST_START,
) -> dict[str, pd.DataFrame]:
    train_df, test_df, split_summary = split_train_test(modeling_df, test_start=test_start)

    x_train = train_df[MODEL_FEATURES].copy()
    y_train = train_df["is_cashless"].astype(int)
    x_test = test_df[MODEL_FEATURES].copy()
    y_test = test_df["is_cashless"].astype(int)

    pipelines = build_model_pipelines()

    metrics_frames: list[pd.DataFrame] = []
    prediction_frames: list[pd.DataFrame] = []
    full_importance_frames: list[pd.DataFrame] = []
    top_importance_frames: list[pd.DataFrame] = []

    for model_name, pipeline in pipelines.items():
        metrics_df, prediction_df = evaluate_classifier(
            model_name=model_name,
            pipeline=pipeline,
            x_train=x_train,
            y_train=y_train,
            x_test=x_test,
            y_test=y_test,
        )
        metrics_frames.append(metrics_df)
        prediction_frames.append(prediction_df)

        full_importance_df, top_importance_df = build_feature_importance_tables(
            fitted_pipeline=pipeline,
            model_name=model_name,
        )
        if not full_importance_df.empty:
            full_importance_frames.append(full_importance_df)
        if not top_importance_df.empty:
            top_importance_frames.append(top_importance_df)

    split_summary_df = pd.DataFrame([split_summary.__dict__])
    metrics_table = pd.concat(metrics_frames, ignore_index=True)
    predictions_table = pd.concat(prediction_frames, ignore_index=True)
    feature_importance_table = (
        pd.concat(full_importance_frames, ignore_index=True)
        if full_importance_frames
        else pd.DataFrame()
    )
    top_feature_table = (
        pd.concat(top_importance_frames, ignore_index=True)
        if top_importance_frames
        else pd.DataFrame()
    )

    return {
        "model_split_summary": split_summary_df,
        "model_metrics": metrics_table,
        "model_predictions": predictions_table,
        "model_feature_importance": feature_importance_table,
        "model_top_features": top_feature_table,
    }
