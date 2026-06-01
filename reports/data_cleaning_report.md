# Relatório de Limpeza de Dados

## Regras aplicadas
- Remoção de linhas com `date` ou `cases` inválidos.
- Imputação de `deaths` ausente com 0.
- Correção de valores negativos (`cases`/`deaths`) para 0.
- Ajuste de inconsistência: `deaths > cases` passa a `deaths = cases`.
- Remoção de duplicatas exatas.

## Comparativo antes vs depois
- `rows`: antes `2502832` -> depois `2502832`
- `missing_fips`: antes `23678` -> depois `23678`
- `missing_deaths`: antes `57605` -> depois `0`
- `cases_lt_deaths`: antes `2894` -> depois `0`
- `negative_cases`: antes `0` -> depois `0`
- `negative_deaths`: antes `0` -> depois `0`
- `exact_duplicates`: antes `0` -> depois `0`
- `key_duplicates`: antes `0` -> depois `0`

## Arquivo gerado
- Dataset tratado: `data/processed/us-counties-clean.csv`
