from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="US Counties COVID-19 API")


class PredictInput(BaseModel):
    month: int
    day_of_week: int
    new_cases: float
    new_deaths: float
    cfr: float


@app.get('/health')
def health():
    return {"status": "ok"}


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
