from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier


FEATURES = [
    "month",
    "day_of_week",
    "new_cases",
    "new_deaths",
    "cfr",
]
TARGET = "risk_level"


def _gaussian_logpdf(x: np.ndarray, mean: np.ndarray, var: np.ndarray) -> np.ndarray:
    eps = 1e-9
    var = np.maximum(var, eps)
    return -0.5 * (np.log(2 * np.pi * var) + ((x - mean) ** 2) / var)


def fit_predict_manual_bayes(
    x_train: np.ndarray, y_train: np.ndarray, x_test: np.ndarray
) -> np.ndarray:
    artifact = fit_manual_bayes(x_train, y_train)
    classes = artifact["classes"]

    predictions: list[str] = []
    for row in x_test:
        posteriors = manual_bayes_log_posteriors(row, artifact)
        predictions.append(classes[int(np.argmax(posteriors))])
    return np.array(predictions)


def fit_manual_bayes(x_train: np.ndarray, y_train: np.ndarray) -> dict[str, object]:
    classes = np.array(["low", "medium", "high"])
    class_priors: list[float] = []
    class_means: list[np.ndarray] = []
    class_vars: list[np.ndarray] = []

    n = len(y_train)
    for c in classes:
        x_c = x_train[y_train == c]
        class_priors.append(len(x_c) / n)
        class_means.append(x_c.mean(axis=0))
        class_vars.append(x_c.var(axis=0))

    return {
        "classes": classes,
        "priors": np.array(class_priors),
        "means": np.vstack(class_means),
        "vars": np.vstack(class_vars),
        "features": FEATURES,
    }


def manual_bayes_log_posteriors(row: np.ndarray, artifact: dict[str, object]) -> np.ndarray:
    priors = artifact["priors"]
    means = artifact["means"]
    variances = artifact["vars"]

    return np.log(priors) + _gaussian_logpdf(row, means, variances).sum(axis=1)


def summarize_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, object]:
    acc = accuracy_score(y_true, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="weighted", zero_division=0
    )
    cm = confusion_matrix(y_true, y_pred, labels=["low", "medium", "high"])
    report = classification_report(y_true, y_pred, zero_division=0)
    return {
        "accuracy": acc,
        "precision_weighted": precision,
        "recall_weighted": recall,
        "f1_weighted": f1,
        "confusion_matrix": cm,
        "classification_report": report,
    }


def train_and_evaluate(input_csv: Path, output_report: Path, model_dir: Path) -> None:
    df = pd.read_csv(input_csv)
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=FEATURES + [TARGET])

    # Subamostragem para manter tempo de treino estável em máquina local.
    if len(df) > 450_000:
        samples: list[pd.DataFrame] = []
        for _, g in df.groupby(TARGET):
            samples.append(g.sample(n=min(len(g), 150_000), random_state=42, replace=False))
        df = pd.concat(samples, ignore_index=True)

    x = df[FEATURES].astype(float).values
    y = df[TARGET].astype(str).values

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42, stratify=y
    )

    # 1) Bayes manual (modelo gaussiano por classe)
    bayes_artifact = fit_manual_bayes(x_train, y_train)
    bayes_pred = fit_predict_manual_bayes(x_train, y_train, x_test)
    bayes_metrics = summarize_metrics(y_test, bayes_pred)

    # 2) Regressao Logistica
    lr_model = Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "model",
                LogisticRegression(max_iter=1200, solver="saga", random_state=42),
            ),
        ]
    )
    lr_model.fit(x_train, y_train)
    lr_pred = lr_model.predict(x_test)
    lr_metrics = summarize_metrics(y_test, lr_pred)

    # 3) Arvore de Decisao
    dt_model = DecisionTreeClassifier(
        max_depth=12, min_samples_leaf=20, random_state=42
    )
    dt_model.fit(x_train, y_train)
    dt_pred = dt_model.predict(x_test)
    dt_metrics = summarize_metrics(y_test, dt_pred)

    model_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(bayes_artifact, model_dir / "manual_bayes.joblib")
    joblib.dump(lr_model, model_dir / "logistic_regression.joblib")
    joblib.dump(dt_model, model_dir / "decision_tree.joblib")

    output_report.parent.mkdir(parents=True, exist_ok=True)
    with output_report.open("w", encoding="utf-8") as f:
        f.write("# Relatorio de Modelagem e Comparacao\n\n")
        f.write("## Configuracao\n")
        f.write(f"- Dataset de modelagem: `{input_csv}`\n")
        f.write(f"- Artefatos salvos em: `{model_dir}`\n")
        f.write(f"- Features: `{FEATURES}`\n")
        f.write(f"- Alvo: `{TARGET}`\n")
        f.write(f"- Amostras usadas: `{len(df)}`\n")
        f.write(f"- Treino: `{len(x_train)}` | Teste: `{len(x_test)}`\n\n")

        models = [
            ("Bayes Manual", bayes_metrics),
            ("Regressao Logistica", lr_metrics),
            ("Arvore de Decisao", dt_metrics),
        ]

        f.write("## Comparacao de metricas\n")
        for name, m in models:
            f.write(f"### {name}\n")
            f.write(f"- Acuracia: `{m['accuracy']:.4f}`\n")
            f.write(f"- Precisao (weighted): `{m['precision_weighted']:.4f}`\n")
            f.write(f"- Recall (weighted): `{m['recall_weighted']:.4f}`\n")
            f.write(f"- F1-score (weighted): `{m['f1_weighted']:.4f}`\n")
            f.write("- Matriz de confusao (linhas=real, colunas=predito; ordem: low, medium, high):\n")
            f.write(f"  `{m['confusion_matrix'].tolist()}`\n\n")

        f.write("## Classification reports\n")
        for name, m in models:
            f.write(f"### {name}\n")
            f.write("```text\n")
            f.write(m["classification_report"])
            f.write("```\n\n")


if __name__ == "__main__":
    train_and_evaluate(
        input_csv=Path("data/processed/us-counties-model.csv"),
        output_report=Path("reports/model_comparison_report.md"),
        model_dir=Path("backend/models"),
    )
    print("Treinamento e avaliacao concluidos.")
