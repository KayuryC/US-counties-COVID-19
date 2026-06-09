# Declaração de Uso de IA Generativa

## Identificação

**Projeto:** US Counties COVID-19 - Estatística e Probabilidade

**Integrantes:** `[PREENCHER COM OS NOMES COMPLETOS]`

## Ferramenta utilizada

- OpenAI Codex/ChatGPT;
- `[ACRESCENTAR OUTRAS FERRAMENTAS, CASO TENHAM SIDO UTILIZADAS]`.

## O que foi feito com apoio de IA

A IA generativa foi utilizada como ferramenta de apoio nas seguintes atividades:

- organização inicial da estrutura de pastas;
- sugestões de implementação para o pipeline de dados;
- revisão e depuração de código Python, FastAPI e React;
- construção e refinamento do dashboard;
- criação de testes automatizados;
- revisão da aplicação manual do Teorema de Bayes;
- identificação de inconsistências entre código, relatórios e interface;
- apoio na estruturação do README e do relatório técnico.

O código, os resultados e os textos foram revisados pela equipe. Métricas e conclusões foram obtidas pela execução do pipeline sobre o dataset, e não inventadas pela ferramenta.

## Objetivo de aprendizado

O objetivo do uso de IA foi acelerar a prototipação e apoiar a compreensão de:

- tratamento de valores ausentes e revisões em séries cumulativas;
- cálculo de probabilidades a priori, verossimilhanças e posteriori;
- comparação entre Bayes, Regressão Logística e Árvore de Decisão;
- integração entre backend, modelos e dashboard;
- construção de validação temporal e testes reproduzíveis.

A ferramenta foi usada para explicar alternativas e apontar riscos, enquanto as decisões finais permaneceram sob responsabilidade da equipe.

## Dificuldades que motivaram o uso

As principais dificuldades foram:

- processar mais de 2,5 milhões de registros com custo local controlado;
- interpretar valores ausentes de mortes sem convertê-los incorretamente em zero;
- diferenciar valores extremos reais de erros ou revisões da fonte;
- implementar Bayes manualmente com estabilidade numérica;
- evitar prioris artificiais após subamostragem;
- integrar probabilidades e métricas reais no frontend;
- organizar as entregas de acordo com todos os itens da rubrica.

## Limites e verificação

A IA não substituiu a análise dos dados nem a execução dos modelos. As sugestões foram verificadas por:

- relatórios gerados diretamente pelo pipeline;
- inspeção dos artefatos treinados;
- testes automatizados;
- build de produção do frontend;
- chamadas reais ao endpoint de predição;
- comparação entre código, resultados e requisitos da atividade.

Esta declaração deve ser atualizada pelos integrantes caso outras ferramentas ou formas de uso tenham ocorrido.
