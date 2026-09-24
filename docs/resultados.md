# Resultados e análise

Bateria principal: **40 configurações**, ambiente **8 × 8**, **T = 500
períodos**, reativo simples com **10 repetições** por configuração (440
execuções). Sementes e configurações em `experimentos/configurations/`; dados
brutos em `experimentos/raw/`.

## 1. Pontuações médias globais

| Agente | Medida A (média ± desvio) | Medida B (média ± desvio) |
|---|---:|---:|
| Baseado em modelo | **28.436 ± 2.199** | **28.354 ± 2.198** |
| Reativo simples | 25.403 ± 2.938 | 24.923 ± 2.936 |

Tabela completa: `resultados/tables/medias_globais.csv`.
Resultados por configuração: `resultados/tables/por_config.csv`.

## 2. Métricas auxiliares (médias por execução)

| Agente | Movimentos | Células limpas | Total de sujeira | Terminou limpo |
|---|---:|---:|---:|---:|
| Baseado em modelo | 81,7 | 21,9 | 21,9 | **100 %** |
| Reativo simples | 480,3 | 19,7 | 21,9 | 24,2 % |

## 3. Amostra por configuração

| Config | Agente | Medida A | Medida B | Movimentos | Células limpas |
|---:|---|---:|---:|---:|---:|
| 0 | Baseado em modelo | 30.896 | 30.809 | 87 | 19 |
| 0 | Reativo simples | 28.526 | 28.044 | 482 | 18 |
| 2 | Baseado em modelo | 27.511 | 27.426 | 85 | 17 |
| 2 | Reativo simples | 24.871 | 24.385 | 486 | 14,5 |
| 3 | Baseado em modelo | 29.215 | 29.127 | 88 | 31 |
| 3 | Reativo simples | 25.252 | 24.781 | 471 | 29 |

(Valores do reativo são médias de 10 repetições.)

## 4. Comportamento dos agentes

- **Reativo simples:** aspira a célula atual e depois se move ao acaso. Sem
  memória, revisita células, bate muito em obstáculos/paredes e raramente
  termina a limpeza dentro de T (24,2 % das configurações). Consome ~480
  movimentos por execução.
- **Baseado em modelos:** mantém a matriz 0–4, direciona-se a sujeira conhecida
  e a fronteiras, e para (`NOOP`) quando não há mais alvos. Limpa tudo em
  **100 %** das configurações com apenas ~82 movimentos.

## 5. Interpretação das medidas

- **Medida A** recompensa *ter o ambiente limpo ao longo do tempo*. Quem limpa
  mais rápido acumula mais períodos com muitos quadrados limpos; logo, o
  agente baseado em modelos tem vantagem estrutural.
- **Medida B** subtrai os movimentos. Como o reativo se move ~6× mais, sua
  pontuação cai mais do que a do modelo, ampliando a diferença.

## 6. Impacto dos fatores

- **Sujeira inicial:** mais sujeira aumenta o teto da Medida A e alonga o tempo
  de limpeza; o modelo degrada pouco, o reativo muito.
- **Obstáculos:** reduzem a conectividade e provocam batidas; o reativo sofre
  porque não os memoriza, o modelo os registra como valor 4.
- **Posição inicial:** afeta o tempo até a primeira limpeza e o esforço de
  exploração; o impacto é maior no agente sem memória.
- **Observabilidade parcial:** exige exploração. Sem estado interno, o reativo
  não consegue coordenar a cobertura e repete caminhos.
- **Memória/estado interno:** é o fator decisivo — a matriz 0–4 permite evitar
  reinspeção e decidir quando parar.

## 7. Gráficos

- `resultados/charts/graficos.png` — painel geral (médias A/B, curva e
  distribuição);
- `resultados/charts/barras_medidas.png` — comparação das médias A e B;
- `resultados/charts/curva_limpas.png` — fração de células limpas × período;
- `resultados/charts/boxplot.png` — distribuição de desempenho.

## 8. Limitações

- Os resultados referem-se a 40 configurações com uma semente do gerador
  (`--seed 2024`); outras sementes podem deslocar levemente as médias.
- O reativo é comparado pela média de 10 repetições; a variabilidade entre
  configurações é reportada pelo desvio.
