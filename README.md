# US Counties COVID-19 - Estatística e Probabilidade

Projeto acadêmico de análise exploratória, probabilidade e classificação aplicado aos dados reais de COVID-19 por condado dos Estados Unidos.

## Integrantes

- `KAYURY CARNEIRO`
- `JOSÉ SCAF`

## Problema investigado

O projeto investiga padrões espaciais e temporais de casos e mortes e classifica cada registro em um nível de intensidade epidemiológica:

- `low`: `new_cases_ma7` até o quantil de 33% (`1.7143`);
- `medium`: entre os quantis de 33% e 66% (`10.1429`);
- `high`: acima do quantil de 66%.

O sistema classifica o risco associado aos atributos informados pelo usuário. Ele não deve ser interpretado como previsão epidemiológica futura.

## Dataset

- Fonte: [The New York Times - COVID-19 Data](https://github.com/nytimes/covid-19-data)
- Arquivo original: [us-counties.csv](https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv)
- Período: `2020-01-21` a `2022-05-13`
- Registros: `2.502.832`
- Estados e territórios: `56`
- Condados/localizações: `3.277`
- Colunas originais: `date`, `county`, `state`, `fips`, `cases`, `deaths`

Os dados de mortes por condado em Porto Rico possuem `57.605` valores ausentes. Eles permanecem ausentes no dataset tratado para não serem confundidos com zero confirmado.

## Métodos

- Bayes Gaussiano implementado manualmente;
- Regressão Logística com transformação `log1p` e padronização;
- Árvore de Decisão;
- validação temporal, treinando antes de `2021-11-26` e testando a partir dessa data.

| Método | Acurácia | Precisão | Recall | F1-score |
| --- | ---: | ---: | ---: | ---: |
| Bayes Manual | 0.5925 | 0.6897 | 0.5925 | 0.5874 |
| Regressão Logística | 0.6037 | 0.6551 | 0.6037 | 0.5963 |
| Árvore de Decisão | 0.6594 | 0.6713 | 0.6594 | 0.6586 |

## Stack

- Backend: Python, FastAPI e Pydantic;
- Dados e modelos: pandas, NumPy e scikit-learn;
- Visualizações: Matplotlib e Plotly;
- Frontend: React e Vite.

## Estrutura

```text
backend/
  app.py                 API de análises e predição
  models/                modelos e métricas versionados
  pipeline/              qualidade, limpeza, EDA e modelagem
data/
  raw/                   dataset original
  processed/             dataset tratado
frontend/                dashboard React
reports/                 relatórios e figuras
tests/                   testes automatizados
```

## Instalação

Requisitos recomendados: Python 3.9+ e Node.js 18+.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt

cd frontend
npm install
cd ..
```

## Execução

Em um terminal, na raiz do projeto:

```bash
python3 -m uvicorn backend.app:app --reload
```

Em outro terminal:

```bash
cd frontend
npm run dev
```

Dashboard: `http://127.0.0.1:5173`

Documentação da API: `http://127.0.0.1:8000/docs`

Principais endpoints:

- `GET /health`
- `GET /analytics/overview`
- `GET /model/metrics`
- `POST /predict`

## Pipeline reproduzível

Execute na seguinte ordem:

```bash
python3 backend/pipeline/preprocess.py
python3 backend/pipeline/clean.py
python3 backend/pipeline/eda.py
python3 backend/pipeline/prepare_model_data.py
python3 backend/pipeline/train_models.py
```

`data/processed/us-counties-model.csv` não é versionado porque possui aproximadamente 256 MB. Ele é regenerado por `prepare_model_data.py`.

## Verificação

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
cd frontend && npm run build
```

## Entregas acadêmicas

- [Relatório técnico](reports/technical_report.md)
- [Declaração de uso de IA generativa](reports/ai_usage_declaration.md)
- [Relatório de qualidade](reports/data_quality_report.md)
- [Relatório de limpeza](reports/data_cleaning_report.md)
- [Relatório de EDA](reports/eda_report.md)
- [Comparação dos modelos](reports/model_comparison_report.md)
- [Checklist da atividade](reports/project_coverage_checklist.md)

## Limitações

- A variável alvo é derivada dos próprios dados e representa intensidade, não prognóstico clínico.
- Registros do mesmo condado são temporalmente dependentes.
- Mortes por condado em Porto Rico não foram disponibilizadas pela fonte.
- Valores extremos podem combinar ondas reais, notificações acumuladas e revisões retroativas.
- As probabilidades dos classificadores ainda não passaram por calibração específica.

Repositório: [KayuryC/US-counties-COVID-19](https://github.com/KayuryC/US-counties-COVID-19)
