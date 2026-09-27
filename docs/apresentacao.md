# Apresentação (até 10 minutos)

Roteiro alinhado à Seção 4 do `GUIA.md`.

## 1. Mecanismos internos

### Agente reativo simples (`aspirador/agentes.py`)

- Decide **apenas** com a percepção atual, por regra condição-ação:
  `SE sujo ENTÃO aspirar; SENÃO mover aleatoriamente`.
- Não possui memória; `mapa_interno()` retorna `None`.
- A escolha aleatória usa uma semente própria, garantindo reprodutibilidade.

### Agente reativo baseado em modelos (`aspirador/agentes.py`)

- Mantém um **estado interno** (`EstadoInterno`): matriz com origem no ponto de
  partida, valores `0 nada`, `1 passado`, `2 sujo conhecido`, `3 passado/limpo`,
  `4 barreira`.
- Atualização a cada ciclo: reconcilia a posição (se bateu, a célula tentada
  vira `4`), marca a célula atual (`1`/`2`/`3`) e a vizinhança percebida.
- Decisão por prioridade, usando BFS sobre o que conhece:
  1. célula atual suja → `ASPIRAR`;
  2. sujo conhecido (valor `2`) mais próximo;
  3. fronteira desconhecida (valor `0`) mais próxima;
  4. sem alvos → `NOOP`.

A memória é configurável: **Mapa** (acima) ou **1 posição** — neste, o agente
guarda só a posição atual e a anterior, aspira se sujo e evita refazer o último
passo, sem construir mapa. O modo "1 posição" é mais fraco e evidencia o papel
da memória; é selecionável na GUI e por `--memoria`.

Em ambos os casos, as ações são aplicadas por `aspirador/ambiente.py`
(`aplicar`), que registra batidas e movimentos.

## 2. Análise comportamental

- **Baseado em modelos:** explora de forma dirigida, evita reinspeção e **para**
  quando não há mais alvos. Limpou tudo em **100 %** das configurações, com
  ~**82 movimentos** por execução.
- **Reativo simples:** aspira o que encontra, mas sem memória revisita células e
  colide repetidamente. Consome ~**480 movimentos** e ficou limpo em **24,2 %**
  das configurações dentro de T = 500.

### Critério de parada

Nos experimentos, todos executam **exatamente T = 500 períodos**, o que torna a
Medida A (soma, por período, das células limpas **pelo robô**) comparável — a
medida premia limpar cedo e manter limpo o que foi limpo. Terminar ao limpar
mudaria a escala do ranking. Na GUI há a opção **"Parar quando limpo"**
(desligada por padrão), com T como teto.

## 3. Resultados empíricos

Bateria: 40 configurações, 8 × 8, T = 500, reativo com 10 repetições.

| Agente | Medida A (média ± desvio) | Medida B (média ± desvio) |
|---|---:|---:|
| Baseado em modelo | 10.161,05 ± 3.232,85 | 10.079,40 ± 3.226,68 |
| Reativo simples | 7.128,04 ± 2.366,50 | 6.647,76 ± 2.372,96 |

| Agente | Movimentos | Células limpas | Terminou limpo |
|---|---:|---:|---:|
| Baseado em modelo | 81,7 | 21,9 | 100 % |
| Reativo simples | 480,3 | 19,7 | 24,2 % |

Eficiência (T fixo; médias por execução):

| Agente | Passos até limpar | Movimentos até limpo | Sujeira removida |
|---|---:|---:|---:|
| Baseado em modelo | 84,3 | 62,3 | 100 % |
| Reativo simples | 376,1* | 357,2* | 90,0 % |

\* média apenas entre as execuções em que o reativo terminou a limpeza.

Tabelas: `resultados/tables/medias_globais.csv`, `por_config.csv` e
`eficiencia.csv`.
Gráficos: `resultados/charts/` (`graficos.png`, `barras_medidas.png`,
`curva_limpas.png`, `boxplot.png`).

## 4. Discussão crítica (racionalidade)

A racionalidade depende de: **informações perceptíveis**, **ações
disponíveis**, **objetivo** e **medida de desempenho**.

- Sob **ambas as medidas**, o agente baseado em modelos é mais racional porque o
  estado interno reduz o custo de exploração e evita movimentos improdutivos.
- O reativo é *localmente* sensato (aspira quando há sujeira) e racional **dado
  o seu programa**, mas não consegue coordenar a cobertura sem memória.
- A Medida A soma as células **limpas pelo robô** a cada período (células que já
  iniciam limpas não contam); a Medida B acrescenta a **eficiência** de
  deslocamento. Sob outra medida (energia, tempo, aspiração desnecessária), a
  avaliação poderia mudar.
- Conclusão adequada: o resultado vale **para estas medidas e para este
  ambiente**; não se deve concluir que o reativo seja "burro", mas sim limitado
  pelas informações que seu programa permite usar.
