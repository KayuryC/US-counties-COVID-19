# Relatório de Qualidade de Dados

## 1) Validação de Schema
- Colunas esperadas: `['date', 'county', 'state', 'fips', 'cases', 'deaths']`
- Colunas encontradas: `['date', 'county', 'state', 'fips', 'cases', 'deaths']`
- Total de linhas: `2502832`

## 2) Tipos após conversão
- `date`: `datetime64[ns]`
- `county`: `string`
- `state`: `string`
- `fips`: `string`
- `cases`: `int64`
- `deaths`: `float64`

## 3) Valores ausentes
- `date`: 0 (0.0%)
- `county`: 0 (0.0%)
- `state`: 0 (0.0%)
- `fips`: 23678 (0.95%)
- `cases`: 0 (0.0%)
- `deaths`: 57605 (2.3%)

## 4) Duplicatas
- Duplicatas exatas: `0`
- Duplicatas por chave (`date+county+state`): `0`

## 5) Regras de consistência
- `cases < 0`: `0`
- `deaths < 0`: `0`
- `cases < deaths`: `2894`
- Datas inválidas (parse falhou): `0`

## 6) Cobertura temporal
- Data mínima: `2020-01-21`
- Data máxima: `2022-05-13`

## 7) Próximas ações sugeridas
- Definir estratégia para `fips` ausente (manter, imputar ou remover por contexto).
- Validar se existem saltos temporais por condado após ordenar por data.
- Confirmar se `cases` e `deaths` são cumulativos e tratar anomalias de monotonicidade.
