# Projeto 1 — Avaliação Experimental de Agentes Inteligentes

Simulador do mundo do aspirador de pó com dois agentes — **reativo simples** e
**baseado em modelos** — comparados sob duas medidas de desempenho:

- **Medida A:** +1 ponto por quadrado **limpo pelo robô** (cada célula conta
  **uma única vez**) — recompensa pela limpeza realizada.
- **Medida B:** +1 ponto por quadrado **limpo pelo robô** (cada célula conta
  **uma única vez**) e −1 ponto por movimento — medida de **eficiência de
  deslocamento**, tipicamente negativa.

> **Interpretação adotada:** "quadrado limpo" = célula cuja sujeira foi removida
> pelo agente. Células que já iniciam limpas **não pontuam**. O `docs/GUIA.md` usa
> a expressão "cada quadrado limpo" sem restringir a origem; adotamos esta
> leitura mais estrita (a alternativa contaria também as células pré-limpias,
> inflando a medida sem refletir trabalho do agente). Em **ambas** as medidas o
> bônus é contado **uma única vez por célula**; interpretamos a expressão "em
> cada período" do Critério 1 como a **avaliação feita a cada período sobre as
> células limpas naquele passo** (evento de limpeza), e não como o estado "está
> limpo" somado repetidamente. Assim A e B medem a mesma limpeza e diferem apenas
> pela penalidade de movimento.

Stack: Python 3.11+, com execução por **CLI** e por **interface gráfica
(Tkinter)**. Dependências: `matplotlib`, `pandas`, `pytest` (+ `python3-tk`
como pacote de sistema para a interface).

## Documentos

| Arquivo | Papel |
|---|---|
| `docs/GUIA.md` | **Fonte de verdade imutável.** Não editar. |
| `docs/PLANO.md` | Escopo, requisitos e fases (deriva do guia). |
| `docs/ARQUITETURA.md` | Módulos, contratos e fluxo. |
| `project-document.md` | Enunciado original da disciplina. |

Integridade do guia: `sha256(docs/GUIA.md) = 13ee570fbe224882070e9c2c59f5f0f33db327de24d1f558d4731062591b7c5e`.

## Instalar o uv

O projeto usa [uv](https://docs.astral.sh/uv/) para gerenciar o ambiente virtual
e as dependências (`pyproject.toml` + `uv.lock`).

```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```bash
# Linux / macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Como executar

`uv sync` cria o `.venv` automaticamente (a partir do `uv.lock`) e instala as
dependências — não é preciso criar o venv nem rodar `pip install` manualmente.

```bash
uv sync

uv run pytest -q
uv run python -m aspirador --configs 40 --repeticoes 10 --T 500 --seed 2024
uv run python -m aspirador --memoria posicao   # opcional; padrão da bateria: mapa
uv run python -m aspirador --extra             # gera também resultados/extra/
```

A bateria gera:

- `resultados/raw/` — resultados brutos e histórico por período;
- `resultados/tables/` — `por_config.csv`, `medias_globais.csv` e
  `eficiencia.csv`;
- `resultados/charts/` — visão consolidada `graficos.png` e gráficos
  individuais em alta resolução: `metrica_a.png`, `metrica_b.png`,
  `comparativo_metricas.png`, `comparativo_modelos.png`, `curva_limpas.png`,
  `boxplot.png`;
- `resultados/configuracoes.json` — configurações usadas;
- `resultados/extra/` (com `--extra`) — métricas complementares: consolidado
  `graficos_extra.png` e individuais `comparativo_memorias.png`
  (mapa × último movimento × híbrida), `normal_vs_break.png`
  (T fixo × parar após limpar) e `eficiencia.png`.

## Interface gráfica

Pré-requisito de sistema (Ubuntu/Debian):

```bash
sudo apt install python3-tk
```

Abrir a GUI (qualquer uma das formas):

```bash
uv run python main.py
# ou
uv run python -m aspirador.gui
```

Na aba **Simulação** o usuário configura manualmente: **agente** (reativo
simples / baseado em modelos), **seed**, **largura × altura**, **densidade de
sujeira**, **densidade de obstáculos**, **posição inicial** (vazia = aleatória)
e **T** (períodos). Para o agente baseado em modelos há ainda o seletor
**Memória** (`Mapa (matriz)`, `Apenas 1 posição` ou
`Híbrida (mapa de 1 célula)`). Os botões
**Novo / Passo / Play-Pause** controlam a execução
e o placar mostra passo, Medida A, Medida B, movimentos e status. Dois canvas
exibem o **ambiente real** e o **mapa interno 0–4**. A aba **Resultados** embute
os gráficos da bateria (lidos de `resultados/raw/`). A aba **Extra** mostra as
métricas complementares de `resultados/extra/` (parar quando limpo, modos de
memória e eficiência); se faltarem, rode `uv run python -m aspirador --extra`. Há ainda
a opção **"Parar quando limpo"**: com ela marcada, o episódio encerra assim que o
ambiente fica sem sujeira (T permanece como teto de segurança).

O botão **"Salvar execução"** grava o resultado da simulação atual (parâmetros,
Medida A/B, movimentos, etc.) em `resultados/gui/execucoes.csv`, adicionando uma
linha por clique, e também gera uma imagem PNG com a evolução de Medida A/B ao
longo dos períodos em `resultados/gui/charts/` (nome com timestamp; o caminho
fica registrado na coluna `grafico` do CSV). Esses arquivos ficam separados da
bateria de experimentos da CLI (`resultados/raw/`, `resultados/tables/`,
`resultados/charts/`, `resultados/extra/`) para não misturar execuções
manuais/exploratórias com a bateria reprodutível por seed; ambos os CSVs também
têm a coluna `origem` (`gui` ou `cli`) para diferenciar a fonte caso sejam
analisados em conjunto.

## Estrutura

```
README.md           documentação principal
AGENTS.md           regras do projeto
main.py             atalho da GUI (uv run python main.py)
aspirador/
  ambiente.py       Ambiente, Config, Acao, Sensor/Percepcao, aplicar()
  agentes.py        ReativoSimples, BaseadoEmModelo, EstadoInterno (0-4)
  simulador.py      MedidaA, MedidaB, Resultado, Simulador
  experimentos.py   configs, bateria, tabelas e graficos
  __main__.py       CLI (uv run python -m aspirador)
  gui/
    janela.py             janela, controles e laço de simulação
    widget_grade.py       canvas do ambiente e do mapa interno
    widget_resultados.py  aba com gráficos da bateria (A/B)
    widget_extra.py       aba com métricas complementares
    __main__.py           entrada da GUI
tests/test_core.py
resultados/         raw, tables, charts, extra, gui (gerados)
docs/               GUIA.md, PLANO.md, ARQUITETURA.md
```

## Contrato

```text
Sensor.perceber(ambiente, bateu) -> Percepcao
Agente.agir(percepcao)           -> Acao
Agente.mapa_interno()            -> EstadoInterno | None
aplicar(ambiente, acao)          -> bool (bateu)
Simulador.rodar(T)               -> Resultado
```

## Estado interno do agente baseado em modelos

Matriz com origem no ponto de partida (capacidade máxima fixa):

| valor | significado |
|---|---|
| 0 | nada / desconhecido |
| 1 | passado (já estava limpo) |
| 2 | sujo conhecido |
| 3 | passado e limpo |
| 4 | barreira / obstáculo / limite |

## Memória do agente baseado em modelos

A memória é configurável:

- **Mapa (padrão):** acumula a matriz 0–4 a partir das percepções e decide por
  BFS (sujo conhecido → fronteira → `NOOP`).
- **1 posição:** guarda apenas a posição atual e a anterior (sem mapa). Aspira se
  a célula está suja; caso contrário, move-se evitando refazer o último passo
  (e libera a volta ao bater, para não travar em becos).
- **Híbrida:** acumula a **trajetória** gravando **1 célula por passo** (sem os 8
  vizinhos); decide evitando todo o caminho já memorizado e as barreiras,
  preferindo células novas, com aleatoriedade (seed) para escapar de becos.

Os modos "1 posição" e "híbrida" são mais fracos por construção e servem para
evidenciar o papel da memória. Selecionáveis na GUI (**Memória**) e por
`--memoria {mapa,posicao,hibrida}` (padrão `mapa`; a coluna `memoria` é
registrada em `resultados/raw/`). Rodar com outro valor sobrescreve as saídas da
bateria principal — use deliberadamente.

## Critério de parada

Nos **experimentos** todos os agentes executam **exatamente T períodos** (T = 500
por padrão). Isso garante igualdade de **orçamento de movimentos** e de
oportunidades de limpeza, condição necessária para comparar a **Medida B**
(eficiência): se o episódio terminasse ao limpar, o agente que termina cedo
faria menos movimentos e teria uma B artificialmente melhor. Fixar T mantém a
comparação justa entre agentes. (A **Medida A**, contada uma vez por célula, não
cresce com T, mas a igualdade de condições continua valendo para B.)

Na **GUI** existe a opção **"Parar quando limpo"** (desligada por padrão), útil
para observar o episódio terminar naturalmente; T continua como teto de
segurança. O critério é aplicado pelo simulador, não é uma percepção do agente,
portanto não afeta a observabilidade parcial.

Métricas auxiliares (sem alterar A/B): **passos até limpar**, **movimentos até
limpo** e **percentual de sujeira removida** (`resultados/tables/eficiencia.csv`).

## Resultados obtidos

Bateria: 40 configurações, 8 × 8, T = 500, reativo com 10 repetições.

| Agente | Medida A | Medida B (eficiência) | Movimentos | Limpou tudo |
|---|---:|---:|---:|---:|
| Baseado em modelo | **21,92 ± 7,19** | **−59,72 ± 5,71** | 81,7 | 100 % |
| Reativo simples | 19,73 ± 6,51 | −460,55 ± 13,02 | 480,3 | 24,2 % |

Eficiência (médias por execução):

| Agente | Passos até limpar | Movimentos até limpo | Sujeira removida |
|---|---:|---:|---:|
| Baseado em modelo | 84,3 | 62,3 | 100 % |
| Reativo simples | 376,1* | 357,2* | 90,0 % |

\* média apenas entre as execuções em que o reativo terminou a limpeza (24,2 %).

## Reprodutibilidade

- Sementes e configurações em `resultados/configuracoes.json`.
- Mesma `--seed` ⇒ mesma bateria; o ambiente é determinístico.
- Recomenda-se registrar o *hash* do commit usado nos experimentos.

## Regras de contagem

- Toda tentativa de movimento conta como movimento (inclusive batida).
- `ASPIRAR` e `NOOP` não contam.
- Obstáculos não entram na contagem de quadrados limpos.
