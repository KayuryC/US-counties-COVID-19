from __future__ import annotations

from pathlib import Path

import pandas as pd


def build_data_quality_report(input_csv: Path, output_report: Path) -> None:
    df = pd.read_csv(input_csv)

    expected_cols = ["date", "county", "state", "fips", "cases", "deaths"]
    found_cols = list(df.columns)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["cases"] = pd.to_numeric(df["cases"], errors="coerce")
    df["deaths"] = pd.to_numeric(df["deaths"], errors="coerce")
    df["fips"] = df["fips"].astype("string")
    df["county"] = df["county"].astype("string")
    df["state"] = df["state"].astype("string")

    total_rows = len(df)
    null_counts = df.isna().sum()
    null_pct = (null_counts / total_rows * 100).round(2)

    exact_duplicates = int(df.duplicated().sum())
    key_duplicates = int(df.duplicated(subset=["date", "county", "state"]).sum())

    invalid_negative_cases = int((df["cases"] < 0).sum())
    invalid_negative_deaths = int((df["deaths"] < 0).sum())
    invalid_cases_lt_deaths = int((df["cases"] < df["deaths"]).sum())
    invalid_dates = int(df["date"].isna().sum())

    min_date = df["date"].min()
    max_date = df["date"].max()

    output_report.parent.mkdir(parents=True, exist_ok=True)
    with output_report.open("w", encoding="utf-8") as f:
        f.write("# Relatório de Qualidade de Dados\n\n")
        f.write("## 1) Validação de Schema\n")
        f.write(f"- Colunas esperadas: `{expected_cols}`\n")
        f.write(f"- Colunas encontradas: `{found_cols}`\n")
        f.write(f"- Total de linhas: `{total_rows}`\n\n")

        f.write("## 2) Tipos após conversão\n")
        for col, dtype in df.dtypes.items():
            f.write(f"- `{col}`: `{dtype}`\n")
        f.write("\n")

        f.write("## 3) Valores ausentes\n")
        for col in df.columns:
            f.write(f"- `{col}`: {int(null_counts[col])} ({null_pct[col]}%)\n")
        f.write("\n")

        f.write("## 4) Duplicatas\n")
        f.write(f"- Duplicatas exatas: `{exact_duplicates}`\n")
        f.write(f"- Duplicatas por chave (`date+county+state`): `{key_duplicates}`\n\n")

        f.write("## 5) Regras de consistência\n")
        f.write(f"- `cases < 0`: `{invalid_negative_cases}`\n")
        f.write(f"- `deaths < 0`: `{invalid_negative_deaths}`\n")
        f.write(f"- `cases < deaths`: `{invalid_cases_lt_deaths}`\n")
        f.write(f"- Datas inválidas (parse falhou): `{invalid_dates}`\n\n")

        f.write("## 6) Cobertura temporal\n")
        f.write(f"- Data mínima: `{min_date.date() if pd.notna(min_date) else 'N/A'}`\n")
        f.write(f"- Data máxima: `{max_date.date() if pd.notna(max_date) else 'N/A'}`\n\n")

        f.write("## 7) Próximas ações sugeridas\n")
        f.write("- Definir estratégia para `fips` ausente (manter, imputar ou remover por contexto).\n")
        f.write("- Validar se existem saltos temporais por condado após ordenar por data.\n")
        f.write("- Confirmar se `cases` e `deaths` são cumulativos e tratar anomalias de monotonicidade.\n")


if __name__ == "__main__":
    input_csv = Path("data/raw/us-counties.csv")
    output_report = Path("reports/data_quality_report.md")
    build_data_quality_report(input_csv=input_csv, output_report=output_report)
    print(f"Relatório gerado em: {output_report}")
