# Projeto Estatística e Probabilidade - US Counties COVID-19

Neste projeto, selecionamos um dataset real e adequado para limpeza, análise exploratória e classificação probabilística.

## Stack
- Backend: Python + FastAPI
- Ciência de dados: pandas, numpy, scikit-learn
- Frontend: React + Vite

## Estrutura
- `data/raw`: dados brutos
- `data/processed`: dados tratados
- `backend`: API para predição
- `backend/pipeline`: scripts de preprocessamento, treino e avaliação
- `frontend`: dashboard React
- `reports`: relatório técnico e artefatos

## Rodando o projeto
### 1) Backend
Na raiz do projeto:
```bash
python3 -m uvicorn backend.app:app --reload
```

Se o terminal estiver dentro de `backend/`:
```bash
python3 -m uvicorn app:app --reload
```

### 2) Frontend
```bash
cd frontend
npm install
npm run dev
```

## Pipeline de dados
1. `python3 backend/pipeline/preprocess.py`
2. `python3 backend/pipeline/clean.py`
3. `python3 backend/pipeline/eda.py`
4. `python3 backend/pipeline/prepare_model_data.py`
5. `python3 backend/pipeline/train_models.py`

Observacao: `data/processed/us-counties-model.csv` nao fica versionado no GitHub por exceder o limite de tamanho. Ele pode ser regenerado com `python3 backend/pipeline/prepare_model_data.py`.
