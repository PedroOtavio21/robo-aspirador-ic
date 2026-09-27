# Projeto 1 — Avaliação Experimental de Agentes Inteligentes

Simulador do mundo do aspirador de pó com dois agentes — **reativo simples** e
**baseado em modelos** — comparados sob duas medidas de desempenho:

- **Medida A:** +1 ponto por quadrado **limpo pelo robô** em cada período
  (acumulado).
- **Medida B:** +1 ponto por quadrado **limpo pelo robô** e −1 ponto por
  movimento.

> **Interpretação adotada:** "quadrado limpo" = célula cuja sujeira foi removida
> pelo agente. Células que já iniciam limpas **não pontuam**. O `GUIA.md` usa a
> expressão "cada quadrado limpo" sem restringir a origem; adotamos esta leitura
> mais estrita (a alternativa contaria também as células pré-limpias, inflando a
> medida sem refletir trabalho do agente).

Stack: Python 3.11+, com execução por **CLI** e por **interface gráfica
(Tkinter)**. Dependências: `matplotlib`, `pandas`, `pytest` (+ `python3-tk`
como pacote de sistema para a interface).

## Documentos

| Arquivo | Papel |
|---|---|
| `GUIA.md` | **Fonte de verdade imutável.** Não editar. |
| `PLANO.md` | Escopo, requisitos e fases (deriva do guia). |
| `ARQUITETURA.md` | Módulos, contratos e fluxo. |
| `docs/apresentacao.md` | Roteiro da apresentação (10 min). |
| `project-document.md` | Enunciado original da disciplina. |

Integridade do guia: `sha256(GUIA.md) = 13ee570fbe224882070e9c2c59f5f0f33db327de24d1f558d4731062591b7c5e`.

## Como executar

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

pytest -q
python -m aspirador --configs 40 --repeticoes 10 --T 500 --seed 2024
```

A bateria gera:

- `resultados/raw/` — resultados brutos e histórico por período;
- `resultados/tables/` — `por_config.csv`, `medias_globais.csv` e
  `eficiencia.csv`;
- `resultados/charts/` — `graficos.png`, `barras_medidas.png`,
  `curva_limpas.png`, `boxplot.png`;
- `resultados/configuracoes.json` — configurações usadas.

## Interface gráfica

Pré-requisito de sistema (Ubuntu/Debian):

```bash
sudo apt install python3-tk
```

Abrir a GUI (qualquer uma das formas):

```bash
python main.py
# ou
python -m aspirador.gui
```

Na aba **Simulação** o usuário configura manualmente: **agente** (reativo
simples / baseado em modelos), **seed**, **largura × altura**, **densidade de
sujeira**, **densidade de obstáculos**, **posição inicial** (vazia = aleatória)
e **T** (períodos). Os botões **Novo / Passo / Play-Pause** controlam a execução
e o placar mostra passo, Medida A, Medida B, movimentos e status. Dois canvas
exibem o **ambiente real** e o **mapa interno 0–4**. A aba **Resultados** embute
os gráficos da bateria (lidos de `resultados/raw/`). Há ainda a opção **"Parar
quando limpo"**: com ela marcada, o episódio encerra assim que o ambiente fica
sem sujeira (T permanece como teto de segurança).

## Estrutura

```
GUIA.md, PLANO.md, ARQUITETURA.md, README.md
main.py             atalho da GUI (python main.py)
aspirador/
  ambiente.py       Ambiente, Config, Acao, Sensor/Percepcao, aplicar()
  agentes.py        ReativoSimples, BaseadoEmModelo, EstadoInterno (0-4)
  simulador.py      MedidaA, MedidaB, Resultado, Simulador
  experimentos.py   configs, bateria, tabelas e graficos
  __main__.py       CLI (python -m aspirador)
  gui/
    janela.py             janela, controles e laço de simulação
    widget_grade.py       canvas do ambiente e do mapa interno
    widget_resultados.py  aba com gráficos da bateria
    __main__.py           entrada da GUI
tests/test_core.py
resultados/         raw, tables, charts (gerados)
docs/apresentacao.md
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

## Critério de parada

Nos **experimentos** todos os agentes executam **exatamente T períodos** (T = 500
por padrão). Isso é necessário para comparar a **Medida A**, que é uma soma ao
longo do tempo: fixar T torna a recompensa de manutenção (permanecer limpo)
comparável entre agentes. Se o episódio terminasse ao limpar, o agente rápido
acumularia poucos pontos e o agente que nunca termina acumularia mais — o
ranking poderia se inverter.

Na **GUI** existe a opção **"Parar quando limpo"** (desligada por padrão), útil
para observar o episódio terminar naturalmente; T continua como teto de
segurança. O critério é aplicado pelo simulador, não é uma percepção do agente,
portanto não afeta a observabilidade parcial.

Métricas auxiliares (sem alterar A/B): **passos até limpar**, **movimentos até
limpo** e **percentual de sujeira removida** (`resultados/tables/eficiencia.csv`).

## Resultados obtidos

Bateria: 40 configurações, 8 × 8, T = 500, reativo com 10 repetições.

| Agente | Medida A | Medida B | Movimentos | Limpou tudo |
|---|---:|---:|---:|---:|
| Baseado em modelo | **10.161,05 ± 3.232,85** | **10.079,40 ± 3.226,68** | 81,7 | 100 % |
| Reativo simples | 7.128,04 ± 2.366,50 | 6.647,76 ± 2.372,96 | 480,3 | 24,2 % |

Eficiência (médias por execução):

| Agente | Passos até limpar | Movimentos até limpo | Sujeira removida |
|---|---:|---:|---:|
| Baseado em modelo | 84,3 | 62,3 | 100 % |
| Reativo simples | 376,1* | 357,2* | 90,0 % |

\* média apenas entre as execuções em que o reativo terminou a limpeza (24,2 %).

Análise completa em `docs/apresentacao.md`.

## Reprodutibilidade

- Sementes e configurações em `resultados/configuracoes.json`.
- Mesma `--seed` ⇒ mesma bateria; o ambiente é determinístico.
- Recomenda-se registrar o *hash* do commit usado nos experimentos.

## Regras de contagem

- Toda tentativa de movimento conta como movimento (inclusive batida).
- `ASPIRAR` e `NOOP` não contam.
- Obstáculos não entram na contagem de quadrados limpos.
