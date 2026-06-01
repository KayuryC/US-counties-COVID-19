from __future__ import annotations

from pathlib import Path

import pandas as pd


def _metrics(df: pd.DataFrame) -> dict[str, int]:
    return {
        "rows": len(df),
        "missing_fips": int(df["fips"].isna().sum()),
        "missing_deaths": int(df["deaths"].isna().sum()),
        "cases_lt_deaths": int((df["cases"] < df["deaths"]).sum()),
        "negative_cases": int((df["cases"] < 0).sum()),
        "negative_deaths": int((df["deaths"] < 0).sum()),
        "exact_duplicates": int(df.duplicated().sum()),
        "key_duplicates": int(df.duplicated(subset=["date", "county", "state"]).sum()),
    }


def clean_dataset(input_csv: Path, output_csv: Path, output_report: Path) -> None:
    df = pd.read_csv(input_csv)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["cases"] = pd.to_numeric(df["cases"], errors="coerce")
    df["deaths"] = pd.to_numeric(df["deaths"], errors="coerce")
    # Preserva FIPS como código textual (sem sufixo ".0" vindo de float).
    df["fips"] = (
        pd.to_numeric(df["fips"], errors="coerce")
        .round()
        .astype("Int64")
        .astype("string")
    )
    df["county"] = df["county"].astype("string")
    df["state"] = df["state"].astype("string")

    before = _metrics(df)

    # 1) Remover linhas com data/cases inválidos (não há como recuperar com segurança)
    df = df.dropna(subset=["date", "cases"])

    # 2) Imputar deaths faltante com 0 (interpretação: sem registro de óbito naquele dia)
    # e garantir inteiro não-negativo.
    df["deaths"] = df["deaths"].fillna(0)
    df.loc[df["deaths"] < 0, "deaths"] = 0

    # 3) Cases negativos também são inválidos.
    df.loc[df["cases"] < 0, "cases"] = 0

    # 4) Ajuste de consistência: deaths não pode exceder cases.
    df.loc[df["deaths"] > df["cases"], "deaths"] = df["cases"]

    # 5) Remover duplicatas exatas, se existirem.
    df = df.drop_duplicates()

    # 6) Reordenar e tipar para saída final consistente.
    df = df.sort_values(["state", "county", "date"]).reset_index(drop=True)
    df["cases"] = df["cases"].round().astype("int64")
    df["deaths"] = df["deaths"].round().astype("int64")

    after = _metrics(df)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)

    output_report.parent.mkdir(parents=True, exist_ok=True)
    with output_report.open("w", encoding="utf-8") as f:
        f.write("# Relatório de Limpeza de Dados\n\n")
        f.write("## Regras aplicadas\n")
        f.write("- Remoção de linhas com `date` ou `cases` inválidos.\n")
        f.write("- Imputação de `deaths` ausente com 0.\n")
        f.write("- Correção de valores negativos (`cases`/`deaths`) para 0.\n")
        f.write("- Ajuste de inconsistência: `deaths > cases` passa a `deaths = cases`.\n")
        f.write("- Remoção de duplicatas exatas.\n\n")

        f.write("## Comparativo antes vs depois\n")
        for k in before.keys():
            f.write(f"- `{k}`: antes `{before[k]}` -> depois `{after[k]}`\n")
        f.write("\n")

        f.write("## Arquivo gerado\n")
        f.write(f"- Dataset tratado: `{output_csv}`\n")


if __name__ == "__main__":
    clean_dataset(
        input_csv=Path("data/raw/us-counties.csv"),
        output_csv=Path("data/processed/us-counties-clean.csv"),
        output_report=Path("reports/data_cleaning_report.md"),
    )
    print("Limpeza concluída.")
