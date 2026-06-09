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
    missing_deaths_by_state = (
        df.loc[df["deaths"].isna(), "state"].value_counts().to_dict()
    )

    # 1) Remover linhas com data/cases inválidos (não há como recuperar com segurança)
    df = df.dropna(subset=["date", "cases"])

    # 2) Manter deaths ausente. No dataset do NYT, esses valores estão
    # concentrados em Porto Rico e significam falta de detalhamento por condado,
    # não evidência de zero óbito.

    # 3) Contagens negativas não possuem interpretação epidemiológica válida.
    df.loc[df["deaths"] < 0, "deaths"] = 0
    df.loc[df["cases"] < 0, "cases"] = 0

    # 4) Uma morte confirmada implica ao menos um caso. Preservamos a contagem de
    # mortes observada e elevamos cases ao mínimo lógico, registrando o ajuste.
    inconsistent_mask = df["deaths"] > df["cases"]
    adjusted_cases_count = int(inconsistent_mask.sum())
    df.loc[inconsistent_mask, "cases"] = df.loc[inconsistent_mask, "deaths"]

    # 5) Remover duplicatas exatas, se existirem.
    df = df.drop_duplicates()

    # 6) Reordenar e tipar para saída final consistente.
    df = df.sort_values(["state", "county", "date"]).reset_index(drop=True)
    df["cases"] = df["cases"].round().astype("int64")
    df["deaths"] = df["deaths"].round().astype("Int64")

    after = _metrics(df)
    grouped = df.groupby(["state", "county"], sort=False)
    case_changes = grouped["cases"].diff()
    death_changes = grouped["deaths"].diff()
    negative_case_revisions = int((case_changes < 0).sum())
    negative_death_revisions = int((death_changes < 0).sum())
    case_p999_value = case_changes.clip(lower=0).quantile(0.999)
    death_p999_value = death_changes.clip(lower=0).quantile(0.999)
    case_p999 = float(case_p999_value) if pd.notna(case_p999_value) else 0.0
    death_p999 = float(death_p999_value) if pd.notna(death_p999_value) else 0.0

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)

    output_report.parent.mkdir(parents=True, exist_ok=True)
    with output_report.open("w", encoding="utf-8") as f:
        f.write("# Relatório de Limpeza de Dados\n\n")
        f.write("## 1) Decisões e justificativas técnicas\n")
        f.write(
            "- **Tipos:** `date` foi convertido para data; `cases` e `deaths` para números; "
            "`fips` foi mantido como texto para preservar seu papel de código geográfico.\n"
        )
        f.write(
            "- **Datas ou casos inválidos:** linhas sem esses campos são removidas porque não "
            "é possível posicioná-las na série temporal nem calcular incidência com segurança.\n"
        )
        f.write(
            "- **Mortes ausentes:** permanecem como `NA` no dataset tratado para não interpretar "
            "falta de informação como ausência comprovada de óbitos. A base de modelagem cria "
            "um indicador antes de aplicar zero apenas como imputação operacional.\n"
        )
        f.write(
            f"  - Distribuição original das ausências por estado/território: `{missing_deaths_by_state}`.\n"
        )
        f.write(
            "- **Contagens negativas:** são substituídas por zero, pois contagens acumuladas "
            "negativas não possuem significado válido.\n"
        )
        f.write(
            "- **Mortes maiores que casos:** `cases` é elevado até `deaths`, preservando a "
            "contagem de mortes e garantindo o limite lógico mínimo. "
            f"Registros ajustados: `{adjusted_cases_count}`.\n"
        )
        f.write(
            "- **FIPS ausente:** permanece ausente porque não há imputação segura para códigos "
            "geográficos; as análises usam o par `state+county` como chave.\n"
        )
        f.write(
            "- **Duplicatas:** duplicatas exatas são removidas para evitar dupla contagem.\n\n"
        )

        f.write("## 2) Comparativo antes vs depois\n")
        for k in sorted(set(before) | set(after)):
            f.write(
                f"- `{k}`: antes `{before.get(k, 0)}` -> depois `{after.get(k, 0)}`\n"
            )
        f.write("\n")

        f.write("## 3) Revisões temporais e valores extremos\n")
        f.write(
            f"- Quedas em contagens cumulativas de casos: `{negative_case_revisions}` registros.\n"
        )
        f.write(
            f"- Quedas em contagens cumulativas de mortes: `{negative_death_revisions}` registros.\n"
        )
        f.write(
            "- Essas quedas são tratadas como revisões retroativas da fonte. Na engenharia de "
            "atributos, diferenças negativas são limitadas a zero para não representar incidência negativa.\n"
        )
        f.write(
            f"- Percentil 99,9% dos aumentos diários por condado: casos `{case_p999:.2f}`, "
            f"mortes `{death_p999:.2f}`.\n"
        )
        f.write(
            "- Valores altos não são removidos automaticamente: podem representar ondas reais, "
            "acúmulo de notificações ou revisões. A EDA usa escala logarítmica e a Regressão "
            "Logística aplica `log1p` para reduzir assimetria sem apagar observações.\n\n"
        )

        f.write("## 4) Impacto esperado\n")
        f.write(
            "- As séries permanecem reproduzíveis, as limitações de cobertura de mortes ficam "
            "explícitas e os modelos deixam de interpretar revisões negativas como novos eventos.\n"
        )
        f.write(
            "- Análises de mortes em Porto Rico devem ser interpretadas como incompletas no nível "
            "de condado por causa da ausência original da fonte.\n\n"
        )

        f.write("## 5) Arquivo gerado\n")
        f.write(f"- Dataset tratado: `{output_csv}`\n")


if __name__ == "__main__":
    clean_dataset(
        input_csv=Path("data/raw/us-counties.csv"),
        output_csv=Path("data/processed/us-counties-clean.csv"),
        output_report=Path("reports/data_cleaning_report.md"),
    )
    print("Limpeza concluída.")
