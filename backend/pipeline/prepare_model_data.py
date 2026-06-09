from __future__ import annotations

from pathlib import Path

import pandas as pd


def prepare_model_data(
    input_csv: Path,
    output_csv: Path,
    report_path: Path,
) -> None:
    df = pd.read_csv(input_csv, parse_dates=["date"])
    df["deaths_was_missing"] = df["deaths"].isna()
    df["deaths"] = df["deaths"].fillna(0)
    df = df.sort_values(["state", "county", "date"]).reset_index(drop=True)

    group_cols = ["state", "county"]

    # Derivadas temporais
    df["month"] = df["date"].dt.month
    df["day_of_week"] = df["date"].dt.dayofweek

    # Novos casos/mortes diários por condado (a partir de valores cumulativos)
    df["new_cases"] = df.groupby(group_cols)["cases"].diff().fillna(df["cases"])
    df["new_deaths"] = df.groupby(group_cols)["deaths"].diff().fillna(df["deaths"])
    df["new_cases"] = df["new_cases"].clip(lower=0)
    df["new_deaths"] = df["new_deaths"].clip(lower=0)

    # Janelas móveis de 7 dias por condado
    df["new_cases_ma7"] = (
        df.groupby(group_cols)["new_cases"]
        .rolling(7, min_periods=1)
        .mean()
        .reset_index(level=group_cols, drop=True)
    )
    df["new_deaths_ma7"] = (
        df.groupby(group_cols)["new_deaths"]
        .rolling(7, min_periods=1)
        .mean()
        .reset_index(level=group_cols, drop=True)
    )

    # Razão de letalidade acumulada aproximada
    df["cfr"] = df["deaths"] / df["cases"].where(df["cases"] > 0)
    df["cfr"] = df["cfr"].fillna(0.0)

    # Alvo categórico: nível de risco baseado em quantis de new_cases_ma7
    q1 = df["new_cases_ma7"].quantile(0.33)
    q2 = df["new_cases_ma7"].quantile(0.66)

    def _risk(x: float) -> str:
        if x <= q1:
            return "low"
        if x <= q2:
            return "medium"
        return "high"

    df["risk_level"] = df["new_cases_ma7"].apply(_risk)

    model_df = df[
        [
            "date",
            "state",
            "county",
            "deaths_was_missing",
            "month",
            "day_of_week",
            "cases",
            "deaths",
            "new_cases",
            "new_deaths",
            "new_cases_ma7",
            "new_deaths_ma7",
            "cfr",
            "risk_level",
        ]
    ].copy()

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    model_df.to_csv(output_csv, index=False)

    class_dist = model_df["risk_level"].value_counts(normalize=True).mul(100).round(2)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8") as f:
        f.write("# Relatorio de Preparacao para Modelagem\n\n")
        f.write("## Variavel alvo\n")
        f.write("- `risk_level` com classes: `low`, `medium`, `high`.\n")
        f.write("- Critério: quantis 33% e 66% de `new_cases_ma7` (novos casos media movel 7 dias por condado).\n\n")
        f.write("## Variaveis preditoras principais\n")
        f.write("- Usadas pelos modelos: `month`, `day_of_week`, `new_cases`, `new_deaths`, `cfr`\n")
        f.write("- Mantidas para analise: `cases`, `deaths`, `new_cases_ma7`, `new_deaths_ma7`\n")
        f.write("- Indicador de qualidade: `deaths_was_missing`\n")
        f.write(
            "- Para modelagem, `deaths` ausente recebe zero somente apos a criacao do indicador; "
            "a limitacao de cobertura permanece documentada.\n\n"
        )
        f.write("## Pontos de corte da variavel alvo\n")
        f.write(f"- q33 (low/medium): `{q1:.4f}`\n")
        f.write(f"- q66 (medium/high): `{q2:.4f}`\n\n")
        f.write("## Distribuicao das classes\n")
        for cls in ["low", "medium", "high"]:
            f.write(f"- {cls}: `{class_dist.get(cls, 0.0)}%`\n")
        f.write("\n")
        f.write("## Saida gerada\n")
        f.write(f"- `{output_csv}`\n")


if __name__ == "__main__":
    prepare_model_data(
        input_csv=Path("data/processed/us-counties-clean.csv"),
        output_csv=Path("data/processed/us-counties-model.csv"),
        report_path=Path("reports/model_data_report.md"),
    )
    print("Preparacao de modelagem concluida.")
