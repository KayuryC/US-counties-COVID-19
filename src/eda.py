from __future__ import annotations

from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def run_eda(input_csv: Path, report_path: Path, figures_dir: Path) -> None:
    df = pd.read_csv(input_csv, parse_dates=["date"])

    figures_dir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    n_rows = len(df)
    n_states = df["state"].nunique()
    n_counties = df[["state", "county"]].drop_duplicates().shape[0]
    min_date = df["date"].min()
    max_date = df["date"].max()

    final_date = max_date
    final_snapshot = df[df["date"] == final_date].copy()
    state_totals = (
        final_snapshot.groupby("state", as_index=False)[["cases", "deaths"]].sum()
        .sort_values("cases", ascending=False)
        .reset_index(drop=True)
    )
    top10_states = state_totals.head(10)

    daily_us = (
        df.groupby("date", as_index=False)[["cases", "deaths"]].sum().sort_values("date")
    )
    daily_us["new_cases"] = daily_us["cases"].diff().fillna(0)
    daily_us["new_deaths"] = daily_us["deaths"].diff().fillna(0)
    daily_us["new_cases_ma7"] = daily_us["new_cases"].rolling(7, min_periods=1).mean()
    daily_us["new_deaths_ma7"] = daily_us["new_deaths"].rolling(7, min_periods=1).mean()

    corr = df[["cases", "deaths"]].corr().iloc[0, 1]

    # Figura 1: Top 10 estados por casos acumulados na data final
    plt.figure(figsize=(11, 6))
    plt.bar(top10_states["state"], top10_states["cases"])
    plt.xticks(rotation=45, ha="right")
    plt.title(f"Top 10 estados por casos acumulados ({final_date.date()})")
    plt.ylabel("Casos acumulados")
    plt.tight_layout()
    fig1 = figures_dir / "top10_states_cases.png"
    plt.savefig(fig1, dpi=150)
    plt.close()

    # Figura 2: Evolução de novos casos (MA7) nos EUA
    plt.figure(figsize=(11, 6))
    plt.plot(daily_us["date"], daily_us["new_cases_ma7"])
    plt.title("Evolucao de novos casos nos EUA (media movel 7 dias)")
    plt.ylabel("Novos casos (MA7)")
    plt.xlabel("Data")
    plt.tight_layout()
    fig2 = figures_dir / "us_new_cases_ma7.png"
    plt.savefig(fig2, dpi=150)
    plt.close()

    # Figura 3: Evolução de novas mortes (MA7) nos EUA
    plt.figure(figsize=(11, 6))
    plt.plot(daily_us["date"], daily_us["new_deaths_ma7"], color="darkred")
    plt.title("Evolucao de novas mortes nos EUA (media movel 7 dias)")
    plt.ylabel("Novas mortes (MA7)")
    plt.xlabel("Data")
    plt.tight_layout()
    fig3 = figures_dir / "us_new_deaths_ma7.png"
    plt.savefig(fig3, dpi=150)
    plt.close()

    with report_path.open("w", encoding="utf-8") as f:
        f.write("# Relatorio de EDA Inicial\n\n")
        f.write("## 1) Visao geral\n")
        f.write(f"- Linhas: `{n_rows}`\n")
        f.write(f"- Estados/territorios: `{n_states}`\n")
        f.write(f"- Pares unicos (state, county): `{n_counties}`\n")
        f.write(f"- Periodo: `{min_date.date()}` a `{max_date.date()}`\n\n")

        f.write("## 2) Top estados por casos acumulados na data final\n")
        for _, row in top10_states.iterrows():
            f.write(
                f"- {row['state']}: casos `{int(row['cases'])}`, mortes `{int(row['deaths'])}`\n"
            )
        f.write("\n")

        f.write("## 3) Relacao entre variaveis\n")
        f.write(f"- Correlacao de Pearson entre `cases` e `deaths`: `{corr:.4f}`\n\n")

        f.write("## 4) Tendencias temporais\n")
        peak_cases = daily_us.loc[daily_us["new_cases_ma7"].idxmax()]
        peak_deaths = daily_us.loc[daily_us["new_deaths_ma7"].idxmax()]
        f.write(
            f"- Pico de novos casos (MA7): `{int(peak_cases['new_cases_ma7'])}` em `{peak_cases['date'].date()}`\n"
        )
        f.write(
            f"- Pico de novas mortes (MA7): `{int(peak_deaths['new_deaths_ma7'])}` em `{peak_deaths['date'].date()}`\n\n"
        )

        f.write("## 5) Graficos gerados\n")
        f.write(f"- `{fig1}`\n")
        f.write(f"- `{fig2}`\n")
        f.write(f"- `{fig3}`\n")


if __name__ == "__main__":
    run_eda(
        input_csv=Path("data/processed/us-counties-clean.csv"),
        report_path=Path("reports/eda_report.md"),
        figures_dir=Path("reports/figures"),
    )
    print("EDA concluida.")
