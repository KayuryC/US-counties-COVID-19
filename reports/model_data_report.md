# Relatorio de Preparacao para Modelagem

## Variavel alvo
- `risk_level` com classes: `low`, `medium`, `high`.
- Critério: quantis 33% e 66% de `new_cases_ma7` (novos casos media movel 7 dias por condado).

## Variaveis preditoras principais
- Usadas pelos modelos: `month`, `day_of_week`, `new_cases`, `new_deaths`, `cfr`
- Mantidas para analise: `cases`, `deaths`, `new_cases_ma7`, `new_deaths_ma7`
- Indicador de qualidade: `deaths_was_missing`
- Para modelagem, `deaths` ausente recebe zero somente apos a criacao do indicador; a limitacao de cobertura permanece documentada.

## Pontos de corte da variavel alvo
- q33 (low/medium): `1.7143`
- q66 (medium/high): `10.1429`

## Distribuicao das classes
- low: `34.17%`
- medium: `31.96%`
- high: `33.87%`

## Saida gerada
- `data/processed/us-counties-model.csv`
