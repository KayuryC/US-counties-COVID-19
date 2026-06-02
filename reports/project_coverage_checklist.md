# Checklist de Cobertura da Lauda

## Status geral

O projeto cobre a maior parte dos requisitos principais: dataset real, limpeza, EDA, Bayes, dois classificadores, dashboard e GitHub organizado.

Ainda faltam dois pontos para considerar a entrega 100% fechada:
- Integrar o endpoint `/predict` aos modelos reais, pois hoje ele ainda usa uma regra provisoria.
- Escrever o relatorio tecnico final e a declaracao formal de uso de IA generativa.

## Requisitos da lauda

| Requisito | Status | Evidencia no projeto |
| --- | --- | --- |
| Dataset real e confiavel | OK | `data/raw/us-counties.csv` |
| Tratamento e limpeza obrigatorios | OK | `backend/pipeline/preprocess.py`, `backend/pipeline/clean.py`, `reports/data_cleaning_report.md` |
| EDA com distribuicoes, relacoes, padroes e insights | Em expansao forte | Dashboard, `backend/app.py`, `reports/eda_report.md` |
| Variavel alvo categorica | OK | `risk_level` em `backend/pipeline/prepare_model_data.py` |
| Teorema de Bayes com priori, verossimilhanca e posterior | Parcialmente OK | `backend/pipeline/train_models.py`, falta expor modelo real no `/predict` |
| Dois classificadores | OK | Regressao Logistica e Arvore de Decisao em `backend/pipeline/train_models.py` |
| Metricas e comparacao | OK | `reports/model_comparison_report.md`, Secao 3 do dashboard |
| Dashboard interativo | OK, em evolucao | `frontend/src/App.jsx`, filtros globais, graficos Plotly |
| Declaracao de IA generativa | Estrutura criada | Secao 6 do dashboard, falta texto final no relatorio |
| Relatorio tecnico final | Pendente | Deve consolidar decisoes, codigos, graficos, resultados e conclusoes |

## Analises exploratorias adicionadas ao dashboard

- KPIs gerais do dataset.
- Ranking de estados por casos/mortes, com filtro por periodo e Top N.
- Distribuicao da variavel alvo `risk_level`.
- Serie temporal com media movel de casos e mortes.
- Mapa de calor dos EUA por estado.
- Resumo de picos temporais.
- Dispersao casos x mortes por estado.
- Ranking de letalidade acumulada (CFR).
- Evolucao mensal de casos/mortes.
- Top condados por casos/mortes.
- Perfil medio por dia da semana.
