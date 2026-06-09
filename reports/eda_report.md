# Relatorio de Analise Exploratoria de Dados

## 1) Visao geral
- Linhas: `2502832`
- Estados/territorios: `56`
- Pares unicos (state, county): `3277`
- Periodo: `2020-01-21` a `2022-05-13`

- Registros sem mortes reportadas: `57605`; usados como zero apenas nos calculos operacionais desta EDA e interpretados como cobertura incompleta.

## 2) Top estados por casos acumulados na data final
- California: casos `9351630`, mortes `90959`
- Texas: casos `6792002`, mortes `88439`
- Florida: casos `5997998`, mortes `74178`
- New York: casos `5267378`, mortes `67938`
- Illinois: casos `3217303`, mortes `38005`
- Pennsylvania: casos `2850343`, mortes `44814`
- Ohio: casos `2724046`, mortes `38550`
- North Carolina: casos `2693618`, mortes `24598`
- Michigan: casos `2472596`, mortes `36140`
- Georgia: casos `2460845`, mortes `36605`

## 3) Distribuicoes e valores extremos
- As distribuicoes diarias possuem forte assimetria a direita: a maioria dos registros tem poucos eventos e uma pequena parcela concentra valores muito altos.
- Quantis de `new_cases` (50%, 90%, 99%, 99,9%): `[2.0, 52.0, 492.0, 2914.17]`.
- Quantis de `new_deaths` (50%, 90%, 99%, 99,9%): `[0.0, 1.0, 7.0, 33.0]`.
- Registros acima do limite IQR: casos `358274`; mortes `343653`.
- Esses valores nao foram excluidos automaticamente porque podem representar ondas epidemicas, notificacoes acumuladas ou revisoes. Escala `log1p` foi usada para visualizacao e na Regressao Logistica.

## 4) Relacoes entre variaveis
- Correlacao de Pearson entre casos e mortes acumulados por estado na data final: `0.9770`.
- A associacao positiva indica que estados com maior carga acumulada de casos tendem a registrar mais mortes, sem implicar causalidade ou letalidade equivalente.
- Correlacao entre novos casos e novas mortes no nivel condado-dia: `0.2490`.

## 5) Tendencias temporais
- Pico de novos casos (MA7): `806969` em `2022-01-14`
- Pico de novas mortes (MA7): `3351` em `2021-01-12`

- O pico de mortes ocorre antes do maior pico de casos desta serie agregada; isso reflete ondas distintas, mudancas de cobertura e revisoes de notificacao, portanto nao deve ser interpretado como relacao temporal direta entre os dois maximos.

## 6) Principais insights
- A carga epidemiologica e espacialmente concentrada, com California, Texas, Florida e New York entre os maiores totais acumulados.
- As variaveis de contagem apresentam cauda longa, justificando visualizacoes logaritmicas e transformacao antes de modelos lineares.
- A mudanca na distribuicao das classes ao longo do tempo reforca a necessidade de avaliacao temporal dos classificadores.

## 7) Graficos gerados
- `reports/figures/top10_states_cases.png`
- `reports/figures/us_new_cases_ma7.png`
- `reports/figures/us_new_deaths_ma7.png`
- `reports/figures/daily_distributions_log.png`
- `reports/figures/correlation_matrix.png`
- `reports/figures/daily_outliers_boxplot_log.png`
