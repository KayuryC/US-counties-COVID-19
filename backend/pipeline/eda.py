from __future__ import annotations

from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def run_eda(input_csv: Path, report_path: Path, figures_dir: Path) -> None:
    df = pd.read_csv(input_csv, parse_dates=["date"])
    missing_deaths = int(df["deaths"].isna().sum())
    df["deaths"] = df["deaths"].fillna(0)
    df = df.sort_values(["state", "county", "date"]).reset_index(drop=True)

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

    grouped = df.groupby(["state", "county"], sort=False)
    df["new_cases"] = grouped["cases"].diff().fillna(df["cases"]).clip(lower=0)
    df["new_deaths"] = grouped["deaths"].diff().fillna(df["deaths"]).clip(lower=0)
    df["cfr"] = (df["deaths"] / df["cases"].where(df["cases"] > 0)).fillna(0)

    state_corr = state_totals[["cases", "deaths"]].corr().iloc[0, 1]
    correlation_columns = ["cases", "deaths", "new_cases", "new_deaths", "cfr"]
    corr_matrix = df[correlation_columns].corr()
    case_q = df["new_cases"].quantile([0.5, 0.9, 0.99, 0.999])
    death_q = df["new_deaths"].quantile([0.5, 0.9, 0.99, 0.999])
    case_iqr_limit = (
        df["new_cases"].quantile(0.75)
        + 1.5 * (df["new_cases"].quantile(0.75) - df["new_cases"].quantile(0.25))
    )
    death_iqr_limit = (
        df["new_deaths"].quantile(0.75)
        + 1.5 * (df["new_deaths"].quantile(0.75) - df["new_deaths"].quantile(0.25))
    )
    case_outliers = int((df["new_cases"] > case_iqr_limit).sum())
    death_outliers = int((df["new_deaths"] > death_iqr_limit).sum())

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

    # Figura 4: distribuições em escala logarítmica para lidar com a cauda longa
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].hist(np.log1p(df["new_cases"]), bins=60, color="#0f766e")
    axes[0].set_title("Distribuicao de novos casos por condado")
    axes[0].set_xlabel("log(1 + novos casos)")
    axes[0].set_ylabel("Frequencia")
    axes[1].hist(np.log1p(df["new_deaths"]), bins=60, color="#0b4f6c")
    axes[1].set_title("Distribuicao de novas mortes por condado")
    axes[1].set_xlabel("log(1 + novas mortes)")
    axes[1].set_ylabel("Frequencia")
    fig.tight_layout()
    fig4 = figures_dir / "daily_distributions_log.png"
    fig.savefig(fig4, dpi=150)
    plt.close(fig)

    # Figura 5: matriz de correlação entre variáveis quantitativas
    fig, ax = plt.subplots(figsize=(8, 6))
    image = ax.imshow(corr_matrix, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(correlation_columns)), correlation_columns, rotation=35, ha="right")
    ax.set_yticks(range(len(correlation_columns)), correlation_columns)
    for i in range(len(correlation_columns)):
        for j in range(len(correlation_columns)):
            ax.text(j, i, f"{corr_matrix.iloc[i, j]:.2f}", ha="center", va="center")
    ax.set_title("Matriz de correlacao das variaveis quantitativas")
    fig.colorbar(image, ax=ax, label="Correlacao de Pearson")
    fig.tight_layout()
    fig5 = figures_dir / "correlation_matrix.png"
    fig.savefig(fig5, dpi=150)
    plt.close(fig)

    # Figura 6: boxplots logarítmicos para evidenciar valores extremos
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.boxplot(
        [np.log1p(df["new_cases"]), np.log1p(df["new_deaths"])],
        tick_labels=["Novos casos", "Novas mortes"],
        showfliers=False,
    )
    ax.set_ylabel("log(1 + valor)")
    ax.set_title("Dispersao robusta das variacoes diarias por condado")
    fig.tight_layout()
    fig6 = figures_dir / "daily_outliers_boxplot_log.png"
    fig.savefig(fig6, dpi=150)
    plt.close(fig)

    with report_path.open("w", encoding="utf-8") as f:
        f.write("# Relatorio de Analise Exploratoria de Dados\n\n")
        f.write("## 1) Visao geral\n")
        f.write(f"- Linhas: `{n_rows}`\n")
        f.write(f"- Estados/territorios: `{n_states}`\n")
        f.write(f"- Pares unicos (state, county): `{n_counties}`\n")
        f.write(f"- Periodo: `{min_date.date()}` a `{max_date.date()}`\n\n")
        f.write(
            f"- Registros sem mortes reportadas: `{missing_deaths}`; usados como zero apenas "
            "nos calculos operacionais desta EDA e interpretados como cobertura incompleta.\n\n"
        )

        f.write("## 2) Top estados por casos acumulados na data final\n")
        for _, row in top10_states.iterrows():
            f.write(
                f"- {row['state']}: casos `{int(row['cases'])}`, mortes `{int(row['deaths'])}`\n"
            )
        f.write("\n")

        f.write("## 3) Distribuicoes e valores extremos\n")
        f.write(
            "- As distribuicoes diarias possuem forte assimetria a direita: a maioria dos "
            "registros tem poucos eventos e uma pequena parcela concentra valores muito altos.\n"
        )
        f.write(
            f"- Quantis de `new_cases` (50%, 90%, 99%, 99,9%): "
            f"`{[round(float(value), 2) for value in case_q.tolist()]}`.\n"
        )
        f.write(
            f"- Quantis de `new_deaths` (50%, 90%, 99%, 99,9%): "
            f"`{[round(float(value), 2) for value in death_q.tolist()]}`.\n"
        )
        f.write(
            f"- Registros acima do limite IQR: casos `{case_outliers}`; mortes `{death_outliers}`.\n"
        )
        f.write(
            "- Esses valores nao foram excluidos automaticamente porque podem representar ondas "
            "epidemicas, notificacoes acumuladas ou revisoes. Escala `log1p` foi usada para "
            "visualizacao e na Regressao Logistica.\n\n"
        )

        f.write("## 4) Relacoes entre variaveis\n")
        f.write(
            f"- Correlacao de Pearson entre casos e mortes acumulados por estado na data final: "
            f"`{state_corr:.4f}`.\n"
        )
        f.write(
            "- A associacao positiva indica que estados com maior carga acumulada de casos "
            "tendem a registrar mais mortes, sem implicar causalidade ou letalidade equivalente.\n"
        )
        f.write(
            f"- Correlacao entre novos casos e novas mortes no nivel condado-dia: "
            f"`{corr_matrix.loc['new_cases', 'new_deaths']:.4f}`.\n\n"
        )

        f.write("## 5) Tendencias temporais\n")
        peak_cases = daily_us.loc[daily_us["new_cases_ma7"].idxmax()]
        peak_deaths = daily_us.loc[daily_us["new_deaths_ma7"].idxmax()]
        f.write(
            f"- Pico de novos casos (MA7): `{int(peak_cases['new_cases_ma7'])}` em `{peak_cases['date'].date()}`\n"
        )
        f.write(
            f"- Pico de novas mortes (MA7): `{int(peak_deaths['new_deaths_ma7'])}` em `{peak_deaths['date'].date()}`\n\n"
        )
        f.write(
            "- O pico de mortes ocorre antes do maior pico de casos desta serie agregada; isso "
            "reflete ondas distintas, mudancas de cobertura e revisoes de notificacao, portanto "
            "nao deve ser interpretado como relacao temporal direta entre os dois maximos.\n\n"
        )

        f.write("## 6) Principais insights\n")
        f.write(
            "- A carga epidemiologica e espacialmente concentrada, com California, Texas, "
            "Florida e New York entre os maiores totais acumulados.\n"
        )
        f.write(
            "- As variaveis de contagem apresentam cauda longa, justificando visualizacoes "
            "logaritmicas e transformacao antes de modelos lineares.\n"
        )
        f.write(
            "- A mudanca na distribuicao das classes ao longo do tempo reforca a necessidade "
            "de avaliacao temporal dos classificadores.\n\n"
        )

        f.write("## 7) Graficos gerados\n")
        f.write(f"- `{fig1}`\n")
        f.write(f"- `{fig2}`\n")
        f.write(f"- `{fig3}`\n")
        f.write(f"- `{fig4}`\n")
        f.write(f"- `{fig5}`\n")
        f.write(f"- `{fig6}`\n")


if __name__ == "__main__":
    run_eda(
        input_csv=Path("data/processed/us-counties-clean.csv"),
        report_path=Path("reports/eda_report.md"),
        figures_dir=Path("reports/figures"),
    )
    print("EDA concluida.")
