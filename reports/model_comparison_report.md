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
- P(low): `0.3534` (35.34%)
- P(medium): `0.3297` (32.97%)
- P(high): `0.3169` (31.69%)

## Distribuicao das classes nas amostras
- Treino: low=35.44%, medium=32.89%, high=31.67%
- Teste: low=30.15%, medium=28.29%, high=41.56%

## Comparacao de metricas
### Bayes Manual
- Acuracia: `0.5934`
- Precisao (weighted): `0.6910`
- Recall (weighted): `0.5934`
- F1-score (weighted): `0.5897`
- Matriz de confusao (linhas=real, colunas=predito; ordem: low, medium, high):
  `[[24528, 2526, 78], [13604, 10931, 927], [12463, 6993, 17950]]`

### Regressao Logistica
- Acuracia: `0.6039`
- Precisao (weighted): `0.6551`
- Recall (weighted): `0.6039`
- F1-score (weighted): `0.5964`
- Matriz de confusao (linhas=real, colunas=predito; ordem: low, medium, high):
  `[[23130, 3789, 213], [12570, 8292, 4600], [12502, 1974, 22930]]`

### Arvore de Decisao
- Acuracia: `0.6596`
- Precisao (weighted): `0.6715`
- Recall (weighted): `0.6596`
- F1-score (weighted): `0.6588`
- Matriz de confusao (linhas=real, colunas=predito; ordem: low, medium, high):
  `[[21052, 5304, 776], [8780, 11760, 4922], [6200, 4656, 26550]]`

## Classification reports
### Bayes Manual
```text
              precision    recall  f1-score   support

         low       0.48      0.90      0.63     27132
      medium       0.53      0.43      0.48     25462
        high       0.95      0.48      0.64     37406

    accuracy                           0.59     90000
   macro avg       0.66      0.60      0.58     90000
weighted avg       0.69      0.59      0.59     90000
```

### Regressao Logistica
```text
              precision    recall  f1-score   support

         low       0.48      0.85      0.61     27132
      medium       0.59      0.33      0.42     25462
        high       0.83      0.61      0.70     37406

    accuracy                           0.60     90000
   macro avg       0.63      0.60      0.58     90000
weighted avg       0.66      0.60      0.60     90000
```

### Arvore de Decisao
```text
              precision    recall  f1-score   support

         low       0.58      0.78      0.67     27132
      medium       0.54      0.46      0.50     25462
        high       0.82      0.71      0.76     37406

    accuracy                           0.66     90000
   macro avg       0.65      0.65      0.64     90000
weighted avg       0.67      0.66      0.66     90000
```

