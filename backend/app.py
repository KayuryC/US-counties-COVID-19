import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import joblib
import numpy as np
import pandas as pd

app = FastAPI(title="US Counties COVID-19 API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictInput(BaseModel):
    month: int = Field(ge=1, le=12)
    day_of_week: int = Field(ge=0, le=6)
    new_cases: float = Field(ge=0)
    new_deaths: float = Field(ge=0)
    cfr: float = Field(ge=0, le=1)


ROOT = Path(__file__).resolve().parents[1]
CLEAN_CSV = ROOT / "data" / "processed" / "us-counties-clean.csv"
MODEL_CSV = ROOT / "data" / "processed" / "us-counties-model.csv"
MODELS_DIR = ROOT / "backend" / "models"
MODEL_METRICS_JSON = MODELS_DIR / "model_metrics.json"
FEATURES = ["month", "day_of_week", "new_cases", "new_deaths", "cfr"]
RISK_CLASSES = ["low", "medium", "high"]


def load_prediction_artifacts() -> Optional[dict[str, object]]:
    paths = {
        "bayes": MODELS_DIR / "manual_bayes.joblib",
        "logistic_regression": MODELS_DIR / "logistic_regression.joblib",
        "decision_tree": MODELS_DIR / "decision_tree.joblib",
    }
    if not all(path.exists() for path in paths.values()):
        return None
    return {name: joblib.load(path) for name, path in paths.items()}


def load_model_metrics() -> Optional[dict]:
    if not MODEL_METRICS_JSON.exists():
        return None
    with MODEL_METRICS_JSON.open(encoding="utf-8") as f:
        return json.load(f)


def gaussian_logpdf(x: np.ndarray, mean: np.ndarray, var: np.ndarray) -> np.ndarray:
    var = np.maximum(var, 1e-9)
    return -0.5 * (np.log(2 * np.pi * var) + ((x - mean) ** 2) / var)


def predict_bayes(row: np.ndarray, artifact: dict[str, object]) -> dict:
    classes = list(artifact["classes"])
    log_posteriors = (
        np.log(artifact["priors"])
        + gaussian_logpdf(row, artifact["means"], artifact["vars"]).sum(axis=1)
    )
    shifted = log_posteriors - np.max(log_posteriors)
    probabilities = np.exp(shifted) / np.exp(shifted).sum()
    probability_payload = {
        klass: float(probabilities[classes.index(klass)]) if klass in classes else 0.0
        for klass in RISK_CLASSES
    }
    return {
        "predicted_class": str(classes[int(np.argmax(probabilities))]),
        "probabilities": probability_payload,
    }


def predict_sklearn(row: np.ndarray, model: object) -> dict:
    prediction = str(model.predict([row])[0])
    payload = {"predicted_class": prediction}
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba([row])[0]
        classes = list(model.classes_)
        payload["probabilities"] = {
            klass: float(probabilities[classes.index(klass)]) if klass in classes else 0.0
            for klass in RISK_CLASSES
        }
    return payload


def _histogram_payload(values: pd.Series, bins: int = 32) -> dict:
    transformed = np.log1p(values.astype(float).clip(lower=0))
    counts, edges = np.histogram(transformed, bins=bins)
    centers = (edges[:-1] + edges[1:]) / 2
    return {
        "x": [round(float(value), 4) for value in centers],
        "counts": [int(value) for value in counts],
    }


def build_model_analytics(clean_df: pd.DataFrame) -> tuple[list[dict], dict, dict]:
    if MODEL_CSV.exists():
        model_df = pd.read_csv(
            MODEL_CSV,
            usecols=["risk_level", "new_cases", "new_deaths"],
        )
    else:
        model_df = clean_df.sort_values(["state", "county", "date"]).copy()
        model_df["new_cases"] = (
            model_df.groupby(["state", "county"])["cases"].diff().fillna(model_df["cases"])
        )
        model_df["new_cases"] = model_df["new_cases"].clip(lower=0)
        model_df["new_deaths"] = (
            model_df.groupby(["state", "county"])["deaths"]
            .diff()
            .fillna(model_df["deaths"])
            .clip(lower=0)
        )
        model_df["new_cases_ma7"] = (
            model_df.groupby(["state", "county"])["new_cases"]
            .rolling(7, min_periods=1)
            .mean()
            .reset_index(level=["state", "county"], drop=True)
        )
        q1 = model_df["new_cases_ma7"].quantile(0.33)
        q2 = model_df["new_cases_ma7"].quantile(0.66)
        model_df["risk_level"] = pd.cut(
            model_df["new_cases_ma7"],
            bins=[-float("inf"), q1, q2, float("inf")],
            labels=["low", "medium", "high"],
            include_lowest=True,
        )

    class_balance = (
        model_df["risk_level"].value_counts(normalize=True).mul(100).round(2).to_dict()
    )
    class_balance_payload = [
        {"classe": "low", "pct": float(class_balance.get("low", 0.0))},
        {"classe": "medium", "pct": float(class_balance.get("medium", 0.0))},
        {"classe": "high", "pct": float(class_balance.get("high", 0.0))},
    ]
    distributions = {
        "new_cases": _histogram_payload(model_df["new_cases"]),
        "new_deaths": _histogram_payload(model_df["new_deaths"]),
    }
    quantiles = [0.5, 0.9, 0.99, 0.999]
    distribution_summary = {
        column: {
            str(quantile): round(float(value), 2)
            for quantile, value in model_df[column].quantile(quantiles).items()
        }
        for column in ["new_cases", "new_deaths"]
    }
    return class_balance_payload, distributions, distribution_summary


def load_overview_data() -> dict:
    clean_df = pd.read_csv(CLEAN_CSV, parse_dates=["date"])
    missing_deaths_count = int(clean_df["deaths"].isna().sum())
    missing_deaths_locations = sorted(
        clean_df.loc[clean_df["deaths"].isna(), "state"].dropna().unique().tolist()
    )
    clean_df["deaths"] = clean_df["deaths"].fillna(0)

    min_date = clean_df["date"].min().date().isoformat()
    max_date = clean_df["date"].max().date().isoformat()
    n_rows = int(len(clean_df))
    n_states = int(clean_df["state"].nunique())
    n_counties = int(clean_df[["state", "county"]].drop_duplicates().shape[0])

    final_snapshot = clean_df[clean_df["date"] == clean_df["date"].max()]
    state_totals_df = final_snapshot.groupby("state", as_index=False)[["cases", "deaths"]].sum()
    state_totals_payload = [{"state": row["state"], "casos": int(row["cases"]), "mortes": int(row["deaths"])} for _, row in state_totals_df.iterrows()]
    state_rates_df = state_totals_df.copy()
    state_rates_df["cfr"] = (state_rates_df["deaths"] / state_rates_df["cases"].where(state_rates_df["cases"] > 0) * 100).fillna(0)
    state_rates_payload = [
        {
            "state": row["state"],
            "casos": int(row["cases"]),
            "mortes": int(row["deaths"]),
            "cfr": round(float(row["cfr"]), 3),
        }
        for _, row in state_rates_df.iterrows()
    ]

    (
        class_balance_payload,
        daily_distributions,
        distribution_summary,
    ) = build_model_analytics(clean_df)

    daily_us = clean_df.groupby("date", as_index=False)[["cases", "deaths"]].sum()
    daily_us["new_cases"] = daily_us["cases"].diff().fillna(0).clip(lower=0)
    daily_us["new_deaths"] = daily_us["deaths"].diff().fillna(0).clip(lower=0)
    daily_us["new_cases_ma7"] = daily_us["new_cases"].rolling(7, min_periods=1).mean()
    daily_us["new_deaths_ma7"] = daily_us["new_deaths"].rolling(7, min_periods=1).mean()
    trend_dates = [d.date().isoformat() for d in daily_us["date"].tolist()]
    trend_cases = [float(x) for x in daily_us["new_cases_ma7"].round(2).tolist()]
    trend_deaths = [float(x) for x in daily_us["new_deaths_ma7"].round(2).tolist()]

    monthly = daily_us.copy()
    monthly["month"] = monthly["date"].dt.to_period("M").astype(str)
    monthly_trend = monthly.groupby("month", as_index=False)[["new_cases", "new_deaths"]].sum()
    monthly_payload = [
        {"month": row["month"], "casos": int(row["new_cases"]), "mortes": int(row["new_deaths"])}
        for _, row in monthly_trend.iterrows()
    ]

    weekday = daily_us.copy()
    weekday["weekday"] = weekday["date"].dt.dayofweek
    weekday_profile = weekday.groupby("weekday", as_index=False)[["new_cases", "new_deaths"]].mean()
    weekday_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    weekday_payload = [
        {
            "weekday": weekday_labels[int(row["weekday"])],
            "casos": round(float(row["new_cases"]), 2),
            "mortes": round(float(row["new_deaths"]), 2),
        }
        for _, row in weekday_profile.iterrows()
    ]

    peak_cases = daily_us.loc[daily_us["new_cases_ma7"].idxmax()]
    peak_deaths = daily_us.loc[daily_us["new_deaths_ma7"].idxmax()]
    state_corr = state_totals_df[["cases", "deaths"]].corr().iloc[0, 1]
    peak_summary = {
        "peak_cases_date": peak_cases["date"].date().isoformat(),
        "peak_cases_ma7": round(float(peak_cases["new_cases_ma7"]), 2),
        "peak_deaths_date": peak_deaths["date"].date().isoformat(),
        "peak_deaths_ma7": round(float(peak_deaths["new_deaths_ma7"]), 2),
        "state_cases_deaths_corr": round(float(state_corr), 4),
    }

    # Agregacoes por janela temporal para filtros globais no frontend.
    state_daily = clean_df.groupby(["state", "date"], as_index=False)[["cases", "deaths"]].sum().sort_values(["state", "date"])
    state_daily["new_cases"] = state_daily.groupby("state")["cases"].diff().fillna(state_daily["cases"]).clip(lower=0)
    state_daily["new_deaths"] = state_daily.groupby("state")["deaths"].diff().fillna(state_daily["deaths"]).clip(lower=0)

    max_dt = state_daily["date"].max()
    windows = {"30": 30, "90": 90, "180": 180, "365": 365, "total": None}
    window_state_totals: dict[str, list[dict]] = {}
    for key, days in windows.items():
        if days is None:
            subset = state_daily
        else:
            start_dt = max_dt - pd.Timedelta(days=days - 1)
            subset = state_daily[state_daily["date"] >= start_dt]
        agg = subset.groupby("state", as_index=False)[["new_cases", "new_deaths"]].sum()
        window_state_totals[key] = [
            {"state": r["state"], "casos": int(r["new_cases"]), "mortes": int(r["new_deaths"])}
            for _, r in agg.iterrows()
        ]

    state_to_abbr = {
        "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
        "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
        "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
        "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
        "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
        "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
        "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
        "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
        "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
        "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
        "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
        "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
        "Wisconsin": "WI", "Wyoming": "WY", "District of Columbia": "DC",
    }
    heatmap_payload = []
    for _, row in state_totals_df.iterrows():
        state_name = row["state"]
        abbr = state_to_abbr.get(state_name)
        if abbr:
            heatmap_payload.append(
                {
                    "state": state_name,
                    "code": abbr,
                    "casos": int(row["cases"]),
                    "mortes": int(row["deaths"]),
                }
            )

    top_counties_df = (
        final_snapshot[~final_snapshot["county"].str.contains("Unknown", case=False, na=False)]
        .sort_values("cases", ascending=False)
        .head(15)
    )
    top_counties_payload = [
        {
            "county": row["county"],
            "state": row["state"],
            "casos": int(row["cases"]),
            "mortes": int(row["deaths"]),
        }
        for _, row in top_counties_df.iterrows()
    ]

    return {
        "kpis": {
            "period_start": min_date,
            "period_end": max_date,
            "rows": n_rows,
            "states": n_states,
            "counties": n_counties,
            "missing_deaths": missing_deaths_count,
            "missing_deaths_locations": missing_deaths_locations,
        },
        "state_totals": state_totals_payload,
        "state_rates": state_rates_payload,
        "window_state_totals": window_state_totals,
        "state_heatmap": heatmap_payload,
        "top_counties": top_counties_payload,
        "class_balance": class_balance_payload,
        "daily_distributions": daily_distributions,
        "distribution_summary": distribution_summary,
        "monthly_trend": monthly_payload,
        "weekday_profile": weekday_payload,
        "peak_summary": peak_summary,
        "trend_dates": trend_dates,
        "trend_cases_ma7": trend_cases,
        "trend_deaths_ma7": trend_deaths,
    }


OVERVIEW_CACHE = load_overview_data()
PREDICTION_ARTIFACTS = load_prediction_artifacts()
MODEL_METRICS_CACHE = load_model_metrics()


@app.get('/health')
def health():
    return {"status": "ok"}


@app.get('/analytics/overview')
def analytics_overview():
    return OVERVIEW_CACHE


@app.get('/model/metrics')
def model_metrics():
    if MODEL_METRICS_CACHE is None:
        return {"status": "unavailable"}
    return MODEL_METRICS_CACHE


@app.post('/predict')
def predict(payload: PredictInput):
    row = np.array(
        [
            payload.month,
            payload.day_of_week,
            payload.new_cases,
            payload.new_deaths,
            payload.cfr,
        ],
        dtype=float,
    )

    if PREDICTION_ARTIFACTS:
        return {
            "bayes": predict_bayes(row, PREDICTION_ARTIFACTS["bayes"]),
            "logistic_regression": predict_sklearn(
                row, PREDICTION_ARTIFACTS["logistic_regression"]
            ),
            "decision_tree": predict_sklearn(row, PREDICTION_ARTIFACTS["decision_tree"]),
            "model_status": "real_artifacts_loaded",
        }

    return {
        "bayes": {
            "predicted_class": "unavailable",
            "probabilities": {"low": 0.0, "medium": 0.0, "high": 0.0},
        },
        "logistic_regression": {"predicted_class": "unavailable"},
        "decision_tree": {"predicted_class": "unavailable"},
        "model_status": "missing_artifacts_run_python3_backend_pipeline_train_models",
    }
