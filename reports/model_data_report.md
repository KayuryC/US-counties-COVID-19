# Relatorio de Preparacao para Modelagem

## Variavel alvo
- `risk_level` com classes: `low`, `medium`, `high`.
- Critério: quantis 33% e 66% de `new_cases_ma7` (novos casos media movel 7 dias por condado).

## Variaveis preditoras principais
- Temporais: `month`, `day_of_week`
- Epidemiologicas: `cases`, `deaths`, `new_cases`, `new_deaths`, `new_cases_ma7`, `new_deaths_ma7`, `cfr`

## Pontos de corte da variavel alvo
- q33 (low/medium): `1.7143`
- q66 (medium/high): `10.1429`

## Distribuicao das classes
- low: `34.21%`
- medium: `31.93%`
- high: `33.86%`

## Saida gerada
- `data/processed/us-counties-model.csv`
