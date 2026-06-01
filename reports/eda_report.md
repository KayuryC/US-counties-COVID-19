# Relatorio de EDA Inicial

## 1) Visao geral
- Linhas: `2502832`
- Estados/territorios: `56`
- Pares unicos (state, county): `3277`
- Periodo: `2020-01-21` a `2022-05-13`

## 2) Top estados por casos acumulados na data final
- California: casos `9351630`, mortes `90959`
- Texas: casos `6792002`, mortes `88439`
- Florida: casos `5997998`, mortes `74178`
- New York: casos `5267378`, mortes `67938`
- Illinois: casos `3215032`, mortes `35734`
- Pennsylvania: casos `2850343`, mortes `44814`
- Ohio: casos `2724041`, mortes `38545`
- North Carolina: casos `2693618`, mortes `24598`
- Michigan: casos `2472596`, mortes `36140`
- Georgia: casos `2460845`, mortes `36605`

## 3) Relacao entre variaveis
- Correlacao de Pearson entre `cases` e `deaths`: `0.8930`

## 4) Tendencias temporais
- Pico de novos casos (MA7): `806927` em `2022-01-14`
- Pico de novas mortes (MA7): `3344` em `2021-01-26`

## 5) Graficos gerados
- `reports/figures/top10_states_cases.png`
- `reports/figures/us_new_cases_ma7.png`
- `reports/figures/us_new_deaths_ma7.png`
