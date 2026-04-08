from __future__ import annotations

import math

import numpy as np
import pandas as pd

PERIOD_ORDER = ["pre_covid", "covid", "intermediate", "post_covid"]


def normal_survival_function(z_value: float) -> float:
    return 0.5 * math.erfc(z_value / math.sqrt(2.0))


def build_month_dummy_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for month_value in range(2, 13):
        column_name = f"month_{month_value:02d}"
        df[column_name] = (df["month"] == month_value).astype(float)
    return df


def build_airport_panel_summary(airport_share: pd.DataFrame) -> pd.DataFrame:
    panel = airport_share.copy()
    total_airport_by_month = panel.groupby(["year", "month"], as_index=False).agg(
        total_airport_trip_count=("airport_trip_count", "sum")
    )
    panel = panel.merge(total_airport_by_month, on=["year", "month"], how="left")
    panel["airport_mix_share"] = (
        panel["airport_trip_count"] / panel["total_airport_trip_count"]
    )
    panel["is_jfk"] = (panel["airport"] == "JFK").astype(float)
    panel["is_covid"] = (panel["period"] == "covid").astype(float)
    panel["is_intermediate"] = (panel["period"] == "intermediate").astype(float)
    panel["is_post_covid"] = (panel["period"] == "post_covid").astype(float)
    panel["jfk_x_covid"] = panel["is_jfk"] * panel["is_covid"]
    panel["jfk_x_intermediate"] = panel["is_jfk"] * panel["is_intermediate"]
    panel["jfk_x_post_covid"] = panel["is_jfk"] * panel["is_post_covid"]
    panel["log_airport_trip_count"] = np.log1p(panel["airport_trip_count"])
    panel["log_all_trip_count"] = np.log1p(panel["all_trip_count"])
    panel = build_month_dummy_columns(panel)
    panel["period"] = pd.Categorical(
        panel["period"], categories=PERIOD_ORDER, ordered=True
    )
    return panel.sort_values(["year", "month", "airport"]).reset_index(drop=True)


def fit_ols_regression(
    df: pd.DataFrame,
    outcome_column: str,
    feature_columns: list[str],
    model_name: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    regression_df = df[[outcome_column, *feature_columns]].dropna().copy()
    x_matrix = regression_df[feature_columns].to_numpy(dtype=float)
    y_vector = regression_df[outcome_column].to_numpy(dtype=float)

    xtx = x_matrix.T @ x_matrix
    xtx_inv = np.linalg.pinv(xtx)
    beta = xtx_inv @ (x_matrix.T @ y_vector)
    fitted = x_matrix @ beta
    residuals = y_vector - fitted

    n_obs = x_matrix.shape[0]
    n_params = x_matrix.shape[1]
    leverage_scale = n_obs / max(n_obs - n_params, 1)
    meat = (x_matrix * residuals[:, None]).T @ (x_matrix * residuals[:, None])
    robust_cov = leverage_scale * (xtx_inv @ meat @ xtx_inv)
    standard_errors = np.sqrt(np.clip(np.diag(robust_cov), a_min=0.0, a_max=None))
    z_scores = np.divide(
        beta,
        standard_errors,
        out=np.full_like(beta, np.nan, dtype=float),
        where=standard_errors > 0,
    )
    p_values = np.array(
        [
            2 * normal_survival_function(abs(z_value))
            if np.isfinite(z_value)
            else np.nan
            for z_value in z_scores
        ]
    )
    confidence_delta = 1.96 * standard_errors

    results_df = pd.DataFrame(
        {
            "model": model_name,
            "outcome": outcome_column,
            "term": feature_columns,
            "coefficient": beta,
            "robust_se": standard_errors,
            "z_score": z_scores,
            "p_value_normal_approx": p_values,
            "ci_lower_95": beta - confidence_delta,
            "ci_upper_95": beta + confidence_delta,
            "n_obs": n_obs,
            "r_squared": (
                np.nan
                if np.allclose(np.var(y_vector), 0.0)
                else 1 - np.sum(residuals**2) / np.sum((y_vector - y_vector.mean()) ** 2)
            ),
        }
    )

    diagnostics_df = pd.DataFrame(
        [
            {
                "model": model_name,
                "outcome": outcome_column,
                "n_obs": n_obs,
                "n_params": n_params,
                "rmse": float(np.sqrt(np.mean(residuals**2))),
                "mean_outcome": float(np.mean(y_vector)),
                "r_squared": results_df["r_squared"].iloc[0],
            }
        ]
    )
    return results_df, diagnostics_df


def build_airport_regression_outputs(
    airport_panel: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    base_columns = [
        "intercept",
        "is_jfk",
        "is_covid",
        "is_intermediate",
        "is_post_covid",
        "jfk_x_covid",
        "jfk_x_intermediate",
        "jfk_x_post_covid",
    ]
    month_columns = [f"month_{month_value:02d}" for month_value in range(2, 13)]

    panel = airport_panel.copy()
    panel["intercept"] = 1.0

    share_features = [*base_columns, *month_columns]
    count_features = [
        *share_features,
        "log_all_trip_count",
        "avg_total_amount",
        "avg_trip_distance",
    ]

    share_results, share_diagnostics = fit_ols_regression(
        panel,
        outcome_column="airport_trip_share",
        feature_columns=share_features,
        model_name="airport_trip_share_panel",
    )
    count_results, count_diagnostics = fit_ols_regression(
        panel,
        outcome_column="log_airport_trip_count",
        feature_columns=count_features,
        model_name="log_airport_trip_count_panel",
    )

    coefficient_table = pd.concat(
        [share_results, count_results], ignore_index=True, sort=False
    )
    diagnostics_table = pd.concat(
        [share_diagnostics, count_diagnostics], ignore_index=True, sort=False
    )
    return coefficient_table, diagnostics_table
