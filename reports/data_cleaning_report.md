# Relatório de Limpeza de Dados

## 1) Decisões e justificativas técnicas
- **Tipos:** `date` foi convertido para data; `cases` e `deaths` para números; `fips` foi mantido como texto para preservar seu papel de código geográfico.
- **Datas ou casos inválidos:** linhas sem esses campos são removidas porque não é possível posicioná-las na série temporal nem calcular incidência com segurança.
- **Mortes ausentes:** permanecem como `NA` no dataset tratado para não interpretar falta de informação como ausência comprovada de óbitos. A base de modelagem cria um indicador antes de aplicar zero apenas como imputação operacional.
  - Distribuição original das ausências por estado/território: `{'Puerto Rico': 57605}`.
- **Contagens negativas:** são substituídas por zero, pois contagens acumuladas negativas não possuem significado válido.
- **Mortes maiores que casos:** `cases` é elevado até `deaths`, preservando a contagem de mortes e garantindo o limite lógico mínimo. Registros ajustados: `2894`.
- **FIPS ausente:** permanece ausente porque não há imputação segura para códigos geográficos; as análises usam o par `state+county` como chave.
- **Duplicatas:** duplicatas exatas são removidas para evitar dupla contagem.

## 2) Comparativo antes vs depois
- `cases_lt_deaths`: antes `2894` -> depois `0`
- `exact_duplicates`: antes `0` -> depois `0`
- `key_duplicates`: antes `0` -> depois `0`
- `missing_deaths`: antes `57605` -> depois `57605`
- `missing_fips`: antes `23678` -> depois `23678`
- `negative_cases`: antes `0` -> depois `0`
- `negative_deaths`: antes `0` -> depois `0`
- `rows`: antes `2502832` -> depois `2502832`

## 3) Revisões temporais e valores extremos
- Quedas em contagens cumulativas de casos: `40527` registros.
- Quedas em contagens cumulativas de mortes: `11144` registros.
- Essas quedas são tratadas como revisões retroativas da fonte. Na engenharia de atributos, diferenças negativas são limitadas a zero para não representar incidência negativa.
- Percentil 99,9% dos aumentos diários por condado: casos `2916.89`, mortes `34.00`.
- Valores altos não são removidos automaticamente: podem representar ondas reais, acúmulo de notificações ou revisões. A EDA usa escala logarítmica e a Regressão Logística aplica `log1p` para reduzir assimetria sem apagar observações.

## 4) Impacto esperado
- As séries permanecem reproduzíveis, as limitações de cobertura de mortes ficam explícitas e os modelos deixam de interpretar revisões negativas como novos eventos.
- Análises de mortes em Porto Rico devem ser interpretadas como incompletas no nível de condado por causa da ausência original da fonte.

## 5) Arquivo gerado
- Dataset tratado: `data/processed/us-counties-clean.csv`
