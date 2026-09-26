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

Em ambos os casos, as ações são aplicadas por `aspirador/ambiente.py`
(`aplicar`), que registra batidas e movimentos.

## 2. Análise comportamental

- **Baseado em modelos:** explora de forma dirigida, evita reinspeção e **para**
  quando não há mais alvos. Limpou tudo em **100 %** das configurações, com
  ~**82 movimentos** por execução.
- **Reativo simples:** aspira o que encontra, mas sem memória revisita células e
  colide repetidamente. Consome ~**480 movimentos** e ficou limpo em **24,2 %**
  das configurações dentro de T = 500.

## 3. Resultados empíricos

Bateria: 40 configurações, 8 × 8, T = 500, reativo com 10 repetições.

| Agente | Medida A (média ± desvio) | Medida B (média ± desvio) |
|---|---:|---:|
| Baseado em modelo | 28.436,05 ± 2.198,63 | 28.354,40 ± 2.198,06 |
| Reativo simples | 25.403,03 ± 2.938,47 | 24.922,76 ± 2.935,98 |

| Agente | Movimentos | Células limpas | Terminou limpo |
|---|---:|---:|---:|
| Baseado em modelo | 81,7 | 21,9 | 100 % |
| Reativo simples | 480,3 | 19,7 | 24,2 % |

Tabelas: `resultados/tables/medias_globais.csv` e `por_config.csv`.
Gráficos: `resultados/charts/` (`graficos.png`, `barras_medidas.png`,
`curva_limpas.png`, `boxplot.png`).

## 4. Discussão crítica (racionalidade)

A racionalidade depende de: **informações perceptíveis**, **ações
disponíveis**, **objetivo** e **medida de desempenho**.

- Sob **ambas as medidas**, o agente baseado em modelos é mais racional porque o
  estado interno reduz o custo de exploração e evita movimentos improdutivos.
- O reativo é *localmente* sensato (aspira quando há sujeira) e racional **dado
  o seu programa**, mas não consegue coordenar a cobertura sem memória.
- A Medida A premia **manter** o ambiente limpo ao longo do tempo; a Medida B
  acrescenta a **eficiência** de deslocamento. Sob outra medida (energia, tempo,
  aspiração desnecessária), a avaliação poderia mudar.
- Conclusão adequada: o resultado vale **para estas medidas e para este
  ambiente**; não se deve concluir que o reativo seja "burro", mas sim limitado
  pelas informações que seu programa permite usar.
