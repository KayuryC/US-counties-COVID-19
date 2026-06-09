# Relatorio de Modelagem e Comparacao

## Configuracao
- Dataset de modelagem: `data/processed/us-counties-model.csv`
- Artefatos salvos em: `backend/models`
- Features: `['month', 'day_of_week', 'new_cases', 'new_deaths', 'cfr']`
- Alvo: `risk_level`
- Regressao Logistica: transformacao `log1p`, padronizacao e solver `lbfgs`
- Validacao: divisao temporal 80/20 por datas unicas
- Corte temporal: treino antes de `2021-11-26`; teste a partir dessa data
- Populacao de treino: `1953097` | Populacao de teste: `549735`
- Amostra de treino: `360000` | Amostra de teste: `90000`

## Probabilidades a priori do Bayes
- Calculadas diretamente na populacao de treino anterior ao corte temporal, antes da subamostragem.
- P(low): `0.3531` (35.31%)
- P(medium): `0.3300` (33.00%)
- P(high): `0.3170` (31.70%)

## Distribuicao das classes nas amostras
- Treino: low=35.40%, medium=32.92%, high=31.68%
- Teste: low=30.12%, medium=28.31%, high=41.57%

## Comparacao de metricas
### Bayes Manual
- Acuracia: `0.5925`
- Precisao (weighted): `0.6897`
- Recall (weighted): `0.5925`
- F1-score (weighted): `0.5874`
- Matriz de confusao (linhas=real, colunas=predito; ordem: low, medium, high):
  `[[24889, 2144, 78], [14318, 10159, 999], [12557, 6579, 18277]]`

### Regressao Logistica
- Acuracia: `0.6037`
- Precisao (weighted): `0.6551`
- Recall (weighted): `0.6037`
- F1-score (weighted): `0.5963`
- Matriz de confusao (linhas=real, colunas=predito; ordem: low, medium, high):
  `[[23110, 3790, 211], [12585, 8306, 4585], [12505, 1988, 22920]]`

### Arvore de Decisao
- Acuracia: `0.6594`
- Precisao (weighted): `0.6713`
- Recall (weighted): `0.6594`
- F1-score (weighted): `0.6586`
- Matriz de confusao (linhas=real, colunas=predito; ordem: low, medium, high):
  `[[21018, 5310, 783], [8785, 11770, 4921], [6196, 4663, 26554]]`

## Classification reports
### Bayes Manual
```text
              precision    recall  f1-score   support

         low       0.48      0.92      0.63     27111
      medium       0.54      0.40      0.46     25476
        high       0.94      0.49      0.64     37413

    accuracy                           0.59     90000
   macro avg       0.65      0.60      0.58     90000
weighted avg       0.69      0.59      0.59     90000
```

### Regressao Logistica
```text
              precision    recall  f1-score   support

         low       0.48      0.85      0.61     27111
      medium       0.59      0.33      0.42     25476
        high       0.83      0.61      0.70     37413

    accuracy                           0.60     90000
   macro avg       0.63      0.60      0.58     90000
weighted avg       0.66      0.60      0.60     90000
```

### Arvore de Decisao
```text
              precision    recall  f1-score   support

         low       0.58      0.78      0.67     27111
      medium       0.54      0.46      0.50     25476
        high       0.82      0.71      0.76     37413

    accuracy                           0.66     90000
   macro avg       0.65      0.65      0.64     90000
weighted avg       0.67      0.66      0.66     90000
```

