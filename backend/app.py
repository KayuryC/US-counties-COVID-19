from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path

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
    month: int
    day_of_week: int
    new_cases: float
    new_deaths: float
    cfr: float


ROOT = Path(__file__).resolve().parents[1]
CLEAN_CSV = ROOT / "data" / "processed" / "us-counties-clean.csv"
MODEL_CSV = ROOT / "data" / "processed" / "us-counties-model.csv"


def load_overview_data() -> dict:
    clean_df = pd.read_csv(CLEAN_CSV, parse_dates=["date"])
    model_df = pd.read_csv(MODEL_CSV)

    min_date = clean_df["date"].min().date().isoformat()
    max_date = clean_df["date"].max().date().isoformat()
    n_rows = int(len(clean_df))
    n_states = int(clean_df["state"].nunique())
    n_counties = int(clean_df[["state", "county"]].drop_duplicates().shape[0])

    final_snapshot = clean_df[clean_df["date"] == clean_df["date"].max()]
    state_totals_df = final_snapshot.groupby("state", as_index=False)[["cases", "deaths"]].sum()
    state_totals_payload = [{"state": row["state"], "casos": int(row["cases"]), "mortes": int(row["deaths"])} for _, row in state_totals_df.iterrows()]

    class_balance = (
        model_df["risk_level"].value_counts(normalize=True).mul(100).round(2).to_dict()
    )
    class_balance_payload = [
        {"classe": "low", "pct": float(class_balance.get("low", 0.0))},
        {"classe": "medium", "pct": float(class_balance.get("medium", 0.0))},
        {"classe": "high", "pct": float(class_balance.get("high", 0.0))},
    ]

    daily_us = clean_df.groupby("date", as_index=False)[["cases", "deaths"]].sum()
    daily_us["new_cases"] = daily_us["cases"].diff().fillna(0).clip(lower=0)
    daily_us["new_deaths"] = daily_us["deaths"].diff().fillna(0).clip(lower=0)
    daily_us["new_cases_ma7"] = daily_us["new_cases"].rolling(7, min_periods=1).mean()
    daily_us["new_deaths_ma7"] = daily_us["new_deaths"].rolling(7, min_periods=1).mean()
    trend_dates = [d.date().isoformat() for d in daily_us["date"].tolist()]
    trend_cases = [float(x) for x in daily_us["new_cases_ma7"].round(2).tolist()]
    trend_deaths = [float(x) for x in daily_us["new_deaths_ma7"].round(2).tolist()]

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

    return {
        "kpis": {
            "period_start": min_date,
            "period_end": max_date,
            "rows": n_rows,
            "states": n_states,
            "counties": n_counties,
        },
        "state_totals": state_totals_payload,
        "window_state_totals": window_state_totals,
        "state_heatmap": heatmap_payload,
        "class_balance": class_balance_payload,
        "trend_dates": trend_dates,
        "trend_cases_ma7": trend_cases,
        "trend_deaths_ma7": trend_deaths,
    }


OVERVIEW_CACHE = load_overview_data()


@app.get('/health')
def health():
    return {"status": "ok"}


@app.get('/analytics/overview')
def analytics_overview():
    return OVERVIEW_CACHE


@app.post('/predict')
def predict(payload: PredictInput):
    # Placeholder until model artifacts are served from training pipeline.
    score = payload.new_cases + 5 * payload.new_deaths + 100 * payload.cfr
    if score < 5:
        risk = "low"
    elif score < 25:
        risk = "medium"
    else:
        risk = "high"

    return {
        "bayes": {"predicted_class": risk, "probabilities": {"low": 0.33, "medium": 0.33, "high": 0.34}},
        "logistic_regression": {"predicted_class": risk},
        "decision_tree": {"predicted_class": risk},
        "note": "Endpoint scaffold pronto; integrar modelos reais no proximo passo."
    }
