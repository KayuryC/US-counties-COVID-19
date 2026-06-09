from __future__ import annotations

import json
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
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler
from sklearn.tree import DecisionTreeClassifier


FEATURES = [
    "month",
    "day_of_week",
    "new_cases",
    "new_deaths",
    "cfr",
]
TARGET = "risk_level"
CLASSES = np.array(["low", "medium", "high"])
TRAIN_SAMPLE_LIMIT = 360_000
TEST_SAMPLE_LIMIT = 90_000


def _gaussian_logpdf(x: np.ndarray, mean: np.ndarray, var: np.ndarray) -> np.ndarray:
    eps = 1e-9
    var = np.maximum(var, eps)
    return -0.5 * (np.log(2 * np.pi * var) + ((x - mean) ** 2) / var)


def fit_predict_manual_bayes(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_test: np.ndarray,
    class_priors: np.ndarray | None = None,
) -> np.ndarray:
    artifact = fit_manual_bayes(x_train, y_train, class_priors=class_priors)
    classes = artifact["classes"]

    predictions: list[str] = []
    for row in x_test:
        posteriors = manual_bayes_log_posteriors(row, artifact)
        predictions.append(classes[int(np.argmax(posteriors))])
    return np.array(predictions)


def calculate_class_priors(y: np.ndarray) -> np.ndarray:
    counts = np.array([(y == klass).sum() for klass in CLASSES], dtype=float)
    if np.any(counts == 0):
        missing = CLASSES[counts == 0].tolist()
        raise ValueError(f"Classes ausentes no calculo das prioris: {missing}")
    return counts / counts.sum()


def fit_manual_bayes(
    x_train: np.ndarray,
    y_train: np.ndarray,
    class_priors: np.ndarray | None = None,
) -> dict[str, object]:
    priors = (
        calculate_class_priors(y_train)
        if class_priors is None
        else np.asarray(class_priors, dtype=float)
    )
    if priors.shape != (len(CLASSES),):
        raise ValueError("Uma probabilidade a priori deve ser informada para cada classe.")
    if not np.isclose(priors.sum(), 1.0):
        raise ValueError("As probabilidades a priori devem somar 1.")

    class_means: list[np.ndarray] = []
    class_vars: list[np.ndarray] = []

    for c in CLASSES:
        x_c = x_train[y_train == c]
        if len(x_c) == 0:
            raise ValueError(f"A classe {c!r} nao possui exemplos de treinamento.")
        class_means.append(x_c.mean(axis=0))
        class_vars.append(x_c.var(axis=0))

    return {
        "classes": CLASSES,
        "priors": priors,
        "means": np.vstack(class_means),
        "vars": np.vstack(class_vars),
        "features": FEATURES,
    }


def manual_bayes_log_posteriors(row: np.ndarray, artifact: dict[str, object]) -> np.ndarray:
    priors = artifact["priors"]
    means = artifact["means"]
    variances = artifact["vars"]

    return np.log(priors) + _gaussian_logpdf(row, means, variances).sum(axis=1)


def temporal_train_test_split(
    df: pd.DataFrame, train_fraction: float = 0.8
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Timestamp]:
    if not 0 < train_fraction < 1:
        raise ValueError("train_fraction deve estar entre 0 e 1.")

    ordered_dates = np.sort(df["date"].dropna().unique())
    if len(ordered_dates) < 2:
        raise ValueError("Sao necessarias pelo menos duas datas para a divisao temporal.")

    split_index = min(int(len(ordered_dates) * train_fraction), len(ordered_dates) - 1)
    cutoff = pd.Timestamp(ordered_dates[split_index])
    train_df = df[df["date"] < cutoff].copy()
    test_df = df[df["date"] >= cutoff].copy()

    if train_df.empty or test_df.empty:
        raise ValueError("A divisao temporal gerou um conjunto vazio.")
    return train_df, test_df, cutoff


def sample_rows(df: pd.DataFrame, limit: int, random_state: int) -> pd.DataFrame:
    if len(df) <= limit:
        return df.copy()
    return df.sample(n=limit, random_state=random_state, replace=False)


def class_distribution(y: np.ndarray) -> dict[str, float]:
    return {
        klass: float((y == klass).mean())
        for klass in CLASSES
    }


def summarize_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, object]:
    acc = accuracy_score(y_true, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="weighted", zero_division=0
    )
    cm = confusion_matrix(y_true, y_pred, labels=CLASSES)
    report = classification_report(
        y_true,
        y_pred,
        labels=CLASSES,
        target_names=CLASSES,
        zero_division=0,
    )
    return {
        "accuracy": acc,
        "precision_weighted": precision,
        "recall_weighted": recall,
        "f1_weighted": f1,
        "confusion_matrix": cm,
        "classification_report": report,
    }


def train_and_evaluate(input_csv: Path, output_report: Path, model_dir: Path) -> None:
    df = pd.read_csv(input_csv, parse_dates=["date"])
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=["date"] + FEATURES + [TARGET])

    train_population, test_population, cutoff = temporal_train_test_split(df)
    population_priors = calculate_class_priors(
        train_population[TARGET].astype(str).values
    )

    # Mantem a proporcao natural das classes, limitando apenas o custo local.
    train_df = sample_rows(train_population, TRAIN_SAMPLE_LIMIT, random_state=42)
    test_df = sample_rows(test_population, TEST_SAMPLE_LIMIT, random_state=43)

    x_train = train_df[FEATURES].astype(float).values
    y_train = train_df[TARGET].astype(str).values
    x_test = test_df[FEATURES].astype(float).values
    y_test = test_df[TARGET].astype(str).values

    # 1) Bayes manual (modelo gaussiano por classe)
    bayes_artifact = fit_manual_bayes(
        x_train, y_train, class_priors=population_priors
    )
    bayes_artifact["prior_source"] = "full_temporal_training_population"
    bayes_artifact["training_cutoff"] = cutoff.date().isoformat()
    bayes_pred = fit_predict_manual_bayes(
        x_train,
        y_train,
        x_test,
        class_priors=population_priors,
    )
    bayes_metrics = summarize_metrics(y_test, bayes_pred)

    # 2) Regressao Logistica
    lr_model = Pipeline(
        [
            ("log1p", FunctionTransformer(np.log1p, validate=True)),
            ("scaler", StandardScaler()),
            (
                "model",
                LogisticRegression(
                    max_iter=2000,
                    solver="lbfgs",
                    random_state=42,
                ),
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

    model_results = [
        ("bayes", "Bayes Manual", bayes_metrics),
        ("logistic_regression", "Regressao Logistica", lr_metrics),
        ("decision_tree", "Arvore de Decisao", dt_metrics),
    ]
    metrics_payload = {
        "class_order": CLASSES.tolist(),
        "validation": {
            "strategy": "temporal_80_20_unique_dates",
            "cutoff": cutoff.date().isoformat(),
            "train_population": len(train_population),
            "test_population": len(test_population),
            "train_sample": len(x_train),
            "test_sample": len(x_test),
        },
        "priors": {
            klass: float(prior)
            for klass, prior in zip(CLASSES, population_priors)
        },
        "models": {
            key: {
                "label": label,
                "accuracy": float(metrics["accuracy"]),
                "precision_weighted": float(metrics["precision_weighted"]),
                "recall_weighted": float(metrics["recall_weighted"]),
                "f1_weighted": float(metrics["f1_weighted"]),
                "confusion_matrix": metrics["confusion_matrix"].tolist(),
            }
            for key, label, metrics in model_results
        },
    }
    with (model_dir / "model_metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, ensure_ascii=True, indent=2)

    output_report.parent.mkdir(parents=True, exist_ok=True)
    with output_report.open("w", encoding="utf-8") as f:
        f.write("# Relatorio de Modelagem e Comparacao\n\n")
        f.write("## Configuracao\n")
        f.write(f"- Dataset de modelagem: `{input_csv}`\n")
        f.write(f"- Artefatos salvos em: `{model_dir}`\n")
        f.write(f"- Features: `{FEATURES}`\n")
        f.write(f"- Alvo: `{TARGET}`\n")
        f.write(
            "- Regressao Logistica: transformacao `log1p`, padronizacao e solver `lbfgs`\n"
        )
        f.write("- Validacao: divisao temporal 80/20 por datas unicas\n")
        f.write(
            f"- Corte temporal: treino antes de `{cutoff.date()}`; teste a partir dessa data\n"
        )
        f.write(
            f"- Populacao de treino: `{len(train_population)}` | Populacao de teste: `{len(test_population)}`\n"
        )
        f.write(
            f"- Amostra de treino: `{len(x_train)}` | Amostra de teste: `{len(x_test)}`\n\n"
        )

        f.write("## Probabilidades a priori do Bayes\n")
        f.write(
            "- Calculadas diretamente na populacao de treino anterior ao corte temporal, antes da subamostragem.\n"
        )
        for klass, prior in zip(CLASSES, population_priors):
            f.write(f"- P({klass}): `{prior:.4f}` ({prior * 100:.2f}%)\n")
        f.write("\n")

        f.write("## Distribuicao das classes nas amostras\n")
        for label, values in [
            ("Treino", class_distribution(y_train)),
            ("Teste", class_distribution(y_test)),
        ]:
            rendered = ", ".join(
                f"{klass}={pct * 100:.2f}%" for klass, pct in values.items()
            )
            f.write(f"- {label}: {rendered}\n")
        f.write("\n")

        f.write("## Comparacao de metricas\n")
        for _, name, m in model_results:
            f.write(f"### {name}\n")
            f.write(f"- Acuracia: `{m['accuracy']:.4f}`\n")
            f.write(f"- Precisao (weighted): `{m['precision_weighted']:.4f}`\n")
            f.write(f"- Recall (weighted): `{m['recall_weighted']:.4f}`\n")
            f.write(f"- F1-score (weighted): `{m['f1_weighted']:.4f}`\n")
            f.write(
                "- Matriz de confusao (linhas=real, colunas=predito; ordem: low, medium, high):\n"
            )
            f.write(f"  `{m['confusion_matrix'].tolist()}`\n\n")

        f.write("## Classification reports\n")
        for _, name, m in model_results:
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
