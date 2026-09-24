# Racionalidade dos agentes

A racionalidade de um agente depende de quatro elementos (Russell & Norvig):

1. **informações perceptíveis** — o que o agente consegue observar;
2. **ações disponíveis** — o que ele pode fazer;
3. **objetivo** — o que se busca;
4. **medida de desempenho** — como o sucesso é aferido.

Neste projeto, o objetivo é limpar o ambiente, mas a medida de desempenho
define *como* isso é recompensado — e é isso que muda o que significa "ser
racional".

## 1. Agente reativo simples

- **Informações:** apenas a percepção atual (`sujo`, `bateu`, `posicao`,
  vizinhança imediata).
- **Ações:** aspirar e mover-se (aleatoriamente).
- **Objetivo:** limpar.
- **Racionalidade:** localmente sensata (aspira quando há sujeira), mas
  incapaz de coordenar a cobertura sem memória. Racional *dado o programa*.
  Na prática, gasta movimentos, revisita células e raramente termina.

## 2. Agente baseado em modelos

- **Informações:** percepção atual **+ estado interno** (matriz 0–4).
- **Ações:** as mesmas, porém escolhidas com base no mapa inferido.
- **Objetivo:** limpar com poucos movimentos.
- **Racionalidade:** usa informação acumulada para evitar trabalho repetido,
  priorizar sujeira conhecida e **decidir parar** quando não há mais alvos.
  É racional de forma mais robusta porque explora a memória disponível.

## 3. Por que "maior pontuação" não significa "mais inteligente"

- A **Medida A** recompensa manter o ambiente limpo por período. Um agente que
  limpa rápido e depois fica parado acumula muitos pontos — a medida premia
  eficiência e permanência, não "inteligência" universal.
- A **Medida B** premia o mesmo, mas desconta movimentos — aproxima-se de uma
  noção de eficiência.
- Sob **outra medida** (p. ex., energia, tempo ou penalização por aspiração
  desnecessária), a avaliação poderá mudar.

Assim, os resultados valem **para as medidas adotadas e para o ambiente 8 × 8
parcialmente observável**. A conclusão apropriada é: *o agente baseado em
modelos é mais racional sob estas medidas porque o estado interno reduz o custo
de exploração e evita movimentos improdutivos*, e não que o reativo seja
"burro" em termos absolutos. O reativo é limitado pelas informações que seu
programa permite usar.
