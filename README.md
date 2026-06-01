# Projeto Estatística e Probabilidade - US Counties COVID-19

Neste projeto, selecionamos um dataset real e adequado para limpeza, análise exploratória e classificação probabilística.

## Stack
- Backend: Python + FastAPI
- Ciência de dados: pandas, numpy, scikit-learn
- Frontend: React + Vite

## Estrutura
- `data/raw`: dados brutos
- `data/processed`: dados tratados
- `src`: scripts de preprocessamento, treino e avaliação
- `backend`: API para predição
- `frontend`: dashboard React
- `reports`: relatório técnico e artefatos

## Rodando o projeto
### 1) Backend
```bash
python3 -m uvicorn backend.app:app --reload
```

### 2) Frontend
```bash
cd frontend
npm install
npm run dev
```

## Pipeline de dados
1. `python3 src/preprocess.py`
2. `python3 src/clean.py`
3. `python3 src/eda.py`
4. `python3 src/prepare_model_data.py`
5. `python3 src/train_models.py`
