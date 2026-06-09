# Checklist de Cobertura da Lauda

## Status geral

O núcleo técnico e os documentos obrigatórios estão implementados. Restam apenas ações manuais de identificação e preparação da entrega.

## Requisitos

| Requisito | Status | Evidência |
| --- | --- | --- |
| Dataset real e confiável | Concluído | `data/raw/us-counties.csv` e link do NYT no README |
| Tratamento e limpeza obrigatórios | Concluído | `backend/pipeline/clean.py` e `reports/data_cleaning_report.md` |
| Justificativa e impacto dos tratamentos | Concluído | Seção 4 do relatório técnico |
| Distribuições quantitativas e qualitativas | Concluído | EDA, figuras e dashboard |
| Correlações, padrões, tendências e insights | Concluído | `reports/eda_report.md` e Seção 1 do dashboard |
| Variável alvo categórica | Concluído | `risk_level` em `prepare_model_data.py` |
| Prioris diretamente dos dados | Concluído | Distribuição temporal de treino em `model_metrics.json` |
| Verossimilhança e posteriori de Bayes | Concluído | Bayes manual e probabilidades exibidas no dashboard |
| Dois classificadores adicionais | Concluído | Regressão Logística e Árvore de Decisão |
| Métricas e matrizes de confusão | Concluído | Dashboard e relatório de comparação |
| Entrada de novos dados pelo usuário | Concluído | Formulário da Seção 2 e endpoint `/predict` |
| Comparação visual dos três métodos | Concluído | Predições e probabilidades na Seção 2 |
| Relatório técnico estruturado | Concluído | `reports/technical_report.md` |
| Declaração de IA generativa | Concluído | `reports/ai_usage_declaration.md` |
| GitHub organizado e README explicativo | Concluído | Estrutura, instruções, testes e histórico de commits |

## Pendências manuais antes da entrega

- Preencher os nomes completos dos integrantes no README e nos documentos.
- Acrescentar outras ferramentas de IA utilizadas pela equipe, caso existam.
- Exportar o relatório técnico e a declaração de IA para PDF, se o professor exigir esse formato.
- Conferir os links enviados no formulário ou ambiente de entrega.
- Ensaiar a arguição individual sobre limpeza, Bayes, modelos e limitações.

## Verificações técnicas

- Testes automatizados: `python3 -m unittest discover -s tests -v`
- Build do frontend: `npm run build`
- Saúde da API: `GET /health`
- Artefatos reais: `backend/models/*.joblib`
- Métricas estruturadas: `backend/models/model_metrics.json`
