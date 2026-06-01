# Relatorio de Modelagem e Comparacao

## Configuracao
- Dataset de modelagem: `data/processed/us-counties-model.csv`
- Features: `['month', 'day_of_week', 'new_cases', 'new_deaths', 'cfr']`
- Alvo: `risk_level`
- Amostras usadas: `450000`
- Treino: `360000` | Teste: `90000`

## Comparacao de metricas
### Bayes Manual
- Acuracia: `0.6425`
- Precisao (weighted): `0.7083`
- Recall (weighted): `0.6425`
- F1-score (weighted): `0.6328`
- Matriz de confusao (linhas=real, colunas=predito; ordem: low, medium, high):
  `[[27772, 2192, 36], [13341, 16228, 431], [6093, 10081, 13826]]`

### Regressao Logistica
- Acuracia: `0.6317`
- Precisao (weighted): `0.6605`
- Recall (weighted): `0.6317`
- F1-score (weighted): `0.6341`
- Matriz de confusao (linhas=real, colunas=predito; ordem: low, medium, high):
  `[[23005, 6963, 32], [13372, 14291, 2337], [4690, 5749, 19561]]`

### Arvore de Decisao
- Acuracia: `0.7304`
- Precisao (weighted): `0.7288`
- Recall (weighted): `0.7304`
- F1-score (weighted): `0.7278`
- Matriz de confusao (linhas=real, colunas=predito; ordem: low, medium, high):
  `[[24387, 4383, 1230], [7593, 17700, 4707], [1925, 4427, 23648]]`

## Classification reports
### Bayes Manual
```text
              precision    recall  f1-score   support

        high       0.97      0.46      0.62     30000
         low       0.59      0.93      0.72     30000
      medium       0.57      0.54      0.55     30000

    accuracy                           0.64     90000
   macro avg       0.71      0.64      0.63     90000
weighted avg       0.71      0.64      0.63     90000
```

### Regressao Logistica
```text
              precision    recall  f1-score   support

        high       0.89      0.65      0.75     30000
         low       0.56      0.77      0.65     30000
      medium       0.53      0.48      0.50     30000

    accuracy                           0.63     90000
   macro avg       0.66      0.63      0.63     90000
weighted avg       0.66      0.63      0.63     90000
```

### Arvore de Decisao
```text
              precision    recall  f1-score   support

        high       0.80      0.79      0.79     30000
         low       0.72      0.81      0.76     30000
      medium       0.67      0.59      0.63     30000

    accuracy                           0.73     90000
   macro avg       0.73      0.73      0.73     90000
weighted avg       0.73      0.73      0.73     90000
```

