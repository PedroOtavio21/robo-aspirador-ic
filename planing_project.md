# Planejamento — Projeto 1: Avaliação Experimental de Agentes Inteligentes

**Tema:** mundo do aspirador de pó (AIMA, cap. 2 de Russell & Norvig)
**Stack:** Python 3 + Tkinter (interface) + matplotlib/pandas (experimentos)
**Tamanho fixo dos experimentos:** 8 × 8
**Períodos por execução:** T = 500 (mesmo para todos os agentes)

---

## 1. Visão geral

### Objetivo

Implementar, simular e avaliar experimentalmente dois agentes para o mundo do
aspirador de pó:

1. **Agente reativo simples** — decide exclusivamente com a **percepção atual**
   e regras condição-ação; não possui memória.
2. **Agente reativo baseado em modelos** — mantém um **estado interno** (uma
   matriz de mesmo porte do mapa) e o atualiza a cada percepção.

O ambiente é **determinístico**, **parcialmente observável**, **desconhecido
inicialmente** e **dinâmico**. A avaliação compara os agentes sob as mesmas
configurações e sob **duas medidas de desempenho**.

### Conceitos exigidos

Agente, sensores, percepções, atuadores, ações, estados do ambiente,
racionalidade, medida de desempenho, observabilidade parcial e tipos de
programa de agente (reativo simples × baseado em modelos).

---

## 2. Stack e dependências

- **Python 3.11+**
- **Tkinter** (biblioteca padrão; no Ubuntu: `sudo apt install python3-tk`)
- **matplotlib** e **pandas** (experimentos e gráficos)
- **pytest** (testes)

Arquivos: `requirements.txt` e registro da versão do Python no README.

A lógica (`core/`, `experimentos/`) é **independente da interface**: a GUI
apenas consome o simulador.

---

## 3. Arquitetura e separação de responsabilidades

```
projeto-ic/
├── README.md
├── requirements.txt
├── planing_project.md
├── docs/
│   ├── especificacao.md
│   ├── metodologia.md
│   ├── resultados.md
│   └── racionalidade.md
├── core/
│   ├── ambiente.py          # estado real do mundo + geração
│   ├── sensores.py          # estado real -> Percepcao (local)
│   ├── atuadores.py         # aplica Acao (regra de movimento inválido)
│   ├── agentes.py           # reativo simples + baseado em modelos
│   ├── estado_interno.py    # matriz 0–4 do agente baseado em modelos
│   ├── metricas.py          # Medida A e Medida B
│   └── simulador.py         # ciclo da simulação + Resultado
├── experimentos/
│   ├── gerador_config.py    # configurações (tamanho fixo)
│   ├── executor.py          # roda os dois agentes nas mesmas configs
│   ├── graficos.py          # tabelas/figuras
│   ├── cli.py               # python -m experimentos
│   ├── configurations/      # JSON das configs
│   └── raw/                 # resultados brutos + histórico
├── resultados/
│   ├── tables/              # tabelas processadas
│   └── charts/              # gráficos
├── gui/                     # janela.py, widget_grade.py, widget_resultados.py
├── main.py                  # entrada da GUI
└── tests/                   # testes do ambiente, sensores, agentes, métricas
```

Responsabilidades: `Environment` (estado real), `Sensors` (estado →
percepção), `Actuators` (aplica ação), `Agent` (decisão), `Simulator`
(ciclo), `PerformanceMeasure` (métricas), `ExperimentGenerator` e
`ExperimentRunner` (configs/execução), `Results` (armazenamento).

---

## 4. Ambiente de tarefas

### 4.1 Representação

Grade 2D de células. Cada célula possui:

- posição `(x, y)`;
- estado: `LIVRE`, `SUJO` ou `OBSTACULO`;
- possibilidade de movimentação (livre/sujo andável; obstáculo bloqueado).

O ambiente possui **tamanho configurável**, **limites definidos**,
**obstáculos configuráveis**, **sujeira inicial configurável** e **posição
inicial do agente configurável** (`posicao_inicial`).

### 4.2 Propriedades

- **Determinístico:** mesma ação + mesmo estado ⇒ mesmo resultado.
- **Parcialmente observável:** nunca entrega o mapa completo.
- **Desconhecido inicialmente:** geografia, extensão e sujeira não informadas.
- **Dinâmico:** o estado muda conforme o agente age.

### 4.3 Geração

Por `seed` + flood fill, garantindo que todas as células livres sejam
conectadas e que a posição inicial informada seja respeitada e nunca um
obstáculo. Configuração **reprodutível**.

---

## 5. Sensores e percepção

`Percepcao` contém apenas:

- `sujo` — condição de sujeira da célula atual;
- `bateu` — se a última tentativa de movimento colidiu;
- `posicao` — posição **relativa** ao ponto de partida (não revela a extensão);
- `vizinhanca` — células no **alcance** do sensor (`raio`, padrão 1), com
  indicação de sujeira e obstáculo; o limite do ambiente é tratado como
  barreira.

**Garantias:** o agente não recebe a matriz completa nem o layout de sujeira;
toma decisões apenas com as percepções permitidas.

---

## 6. Atuadores e ações

Ações: `CIMA`, `BAIXO`, `ESQUERDA`, `DIREITA`, `ASPIRAR`, `NOOP`.

- Tentar atravessar obstáculo ou sair dos limites **não move** o agente e
  retorna `bateu = True` (determinístico).
- **Regra de movimento:** toda tentativa de movimento conta como movimento,
  inclusive a batida; `ASPIRAR` e `NOOP` não contam. Regra igual para os dois
  agentes.

---

## 7. Agente reativo simples

Estrutura condição-ação:

```text
SE a posição atual está suja
    ENTÃO aspirar
SENÃO
    escolher uma ação de movimentação (aleatória, com seed própria)
```

Restrições: sem mapa interno, sem histórico, sem acesso ao estado completo do
simulador. A aleatoriedade é reprodutível por `seed`.

---

## 8. Agente reativo baseado em modelos

### 8.1 Estado interno — matriz

Também chamada de "histórico". É uma **matriz com a mesma cobertura do mapa**,
com a origem `(0, 0)` no ponto de partida. Como o agente não conhece a
extensão real, a matriz é alocada com **capacidade máxima fixa** (padrão 41×41,
origem no centro).

| valor | significado | quando é gravado |
|---|---|---|
| `0` | nada / desconhecido | estado inicial |
| `1` | passado (visitado, já estava limpo) | entra em célula limpa desconhecida |
| `2` | sujo (conhecido, ainda não limpo) | percepção detecta sujeira |
| `3` | passado e limpo (sujeira removida) | após `ASPIRAR` confirmado |
| `4` | barreira / obstáculo / limite | colisão, vizinhança ou limite |

### 8.2 Atualização (a cada ciclo)

```text
1. Receber percepção.
2. Reconciliar posição: se bateu, a célula tentada vira 4; senão move.
3. Marcar célula atual: sujo -> 2; limpo -> 1; recém-aspirado -> 3.
4. Vizinhança: obstáculo/limite -> 4; sujeira -> 2.
5. Avaliar regras condição-ação.
6. Escolher ação.
7. Repetir.
```

### 8.3 Decisão

1. Célula atual suja → `ASPIRAR`.
2. Senão, BFS até o **sujo conhecido** (valor 2) mais próximo.
3. Senão, BFS até a **fronteira** desconhecida (valor 0) mais próxima.
4. Sem sujos conhecidos e sem fronteira → `NOOP`.

O agente **nunca** recebe informações do estado completo do ambiente; todo
conhecimento vem das percepções.

---

## 9. Simulador e períodos

Ciclo de cada período:

```text
Percepção -> Decisão -> Ação -> Atualização do ambiente ->
Cálculo das medidas -> Registro dos dados
```

A ordem é idêntica para todos os agentes e experimentos. Todos executam
**exatamente T = 500 períodos** (mesmo número de períodos), condição necessária
para comparar a Medida A de forma justa.

---

## 10. Medidas de desempenho

### 10.1 Medida A — recompensa por limpeza

> **+1 ponto para cada quadrado limpo em cada período.**

```text
score_A = Σ_t (quantidade de quadrados limpos no período t)
```

Recompensa manter o ambiente limpo; quem limpa mais rápido acumula mais
períodos "limpos".

### 10.2 Medida B — limpeza com penalização por movimento

> **+1 ponto por quadrado limpo e −1 ponto por movimento.**

```text
score_B = score_A − total de movimentos
```

### 10.3 Regras de contagem

- Movimento válido conta como movimento.
- Batida em obstáculo/parede também conta como movimento.
- `ASPIRAR` e `NOOP` não contam como movimento.
- As duas medidas são calculadas **na mesma execução** (a trajetória do agente
  não depende da medida).

---

## 11. Geração das configurações experimentais

- **Tamanho fixo:** 8 × 8 no conjunto principal.
- Variação: **padrão de sujeira**, **posição/quantidade de obstáculos** e
  **posição inicial do agente**.
- Geração pseudoaleatória controlada por `seed`; as configurações são salvas em
  JSON e os dois agentes enfrentam as mesmas configurações.

---

## 12. Execução experimental e controle

Para cada configuração: executa **reativo simples** e **baseado em modelos**
(mesmo ambiente, mesmos obstáculos, mesma sujeira, mesma posição inicial, mesmo
T, mesma pontuação e mesma condição de parada) e registra os resultados.

O reativo é repetido `N` vezes (aleatório) e comparado pela média; o baseado em
modelos é determinístico. CLI:

```bash
python -m experimentos --configs 40 --repeticoes 10 --T 500 --seed 2024
```

---

## 13. Dados registrados

`config_id`, `agente`, `seed`, `largura`, `altura`, `densidade_sujeira`,
`densidade_obstaculo`, `posicao_inicial`, `mapa_inicial`, `repeticao`,
`score_a`, `score_b`, `movimentos`, `passos`, `celulas_limpas`, `total_sujos`,
`limpo`, `acoes` (sequência completa) e observações. O histórico por período
fica em `experimentos/raw/historico.csv`.

---

## 14. Pontuação média global

Para cada combinação agente × medida: média das pontuações por configuração.
Obtém-se as quatro médias exigidas (reativo/modelo × Medida A/B), salvas em
`resultados/tables/medias_globais.csv`.

---

## 15. Análise experimental e racionalidade

Analisa-se: comportamento de cada agente; impacto da sujeira, dos obstáculos,
da posição inicial e da observabilidade parcial; impacto da memória/estado
interno; número de movimentos; eficiência de limpeza; dificuldades; diferenças
entre as medidas. A racionalidade é contextualizada (informação perceptível,
ações disponíveis, objetivo, medida e limitações) — evita-se "maior pontuação =
mais inteligente".

---

## 16. Visualização

- **Tabelas:** `resultados/tables/medias_globais.csv` e `por_config.csv`.
- **Gráficos:** `resultados/charts/graficos.png`, `barras_medidas.png`,
  `curva_limpas.png`, `boxplot.png`.
- Cada gráfico deixa claro agente, medida, unidade e conjunto de configurações.

---

## 17. Interface (Tkinter)

- Grade do **ambiente real** e **matriz interna 0–4** colorida lado a lado.
- Controles: agente, seed, Novo/Passo/Play, velocidade.
- Placar: período, Medida A, Medida B, movimentos e status.

A interface é recurso de apoio; os dados experimentais vêm do núcleo.

---

## 18. Testes

Cobrem: criação/limites/movimentação/aspiração/posição inicial do ambiente;
observabilidade dos sensores; matriz 0–4 (inicialização, atualização, obstáculo
→ 4, aspirar → 3, sem "mágica"); reativo (aspira/move/sem memória/
reprodutível); modelo (limpa tudo, registra obstáculos); métricas A e B e média
global; simulador (consistência, reprodutibilidade, número de períodos).

---

## 19. Reprodutibilidade

Registrar: versão do código (git), versão do Python, dependências, tamanho fixo,
número de configs, `T`, sementes, configurações em JSON, resultados brutos e
instruções de execução (README).

---

## 20. Entregáveis

- **Código:** ambiente, sensores, atuadores, agentes, estado interno,
  simulador, métricas, gerador/executor de experimentos, GUI e testes.
- **Dados:** configurações, resultados brutos, processados, pontuações por
  configuração e médias globais.
- **Documentação:** `docs/` (especificação, metodologia, resultados,
  racionalidade) e README.
- **Apresentação:** até 10 minutos, com mecanismos, tabelas, gráficos e
  discussão de racionalidade.

---

## 21. Ordem de desenvolvimento

```text
ambiente -> sensores/atuadores -> ciclo+medidas -> reativo ->
estado interno (matriz) -> modelo -> gerador -> experimentos ->
tabelas/gráficos -> análise -> GUI -> apresentação
```

---

## 22. Decisões registradas

- [x] Matriz interna com **capacidade máxima fixa** (não revela a extensão).
- [x] **Toda tentativa de movimento** conta como movimento (inclusive batida).
- [x] Tamanho fixo **8 × 8** no conjunto principal.
- [x] Ambas as medidas calculadas **na mesma execução**.
- [x] Execução com **T = 500 períodos fixos** para todos (mesmo nº de períodos).
- [x] Obstáculos não entram na contagem de quadrados limpos.
- [x] `ASPIRAR`/`NOOP` não contam como movimento.

> Referência conceitual: Capítulo 2 de Russell e Norvig (agentes e ambientes,
> percepções e ações, racionalidade, medidas de desempenho, propriedades dos
> ambientes de tarefa, programas de agentes, mundo do aspirador de pó).
