# Arquitetura

Derivada de `PLANO.md` e de `GUIA.md`.

## 1. Estrutura

```
README.md            # execução, estrutura e resultados
AGENTS.md            # regras do projeto
main.py              # atalho da GUI: python main.py
aspirador/
  __init__.py
  ambiente.py        # Ambiente, Config, Acao, Percepcao, Sensor, aplicar()
  agentes.py         # Agente, ReativoSimples, EstadoInterno, BaseadoEmModelo
  simulador.py       # MedidaA, MedidaB, Resultado, Simulador
  experimentos.py    # configs, bateria, tabelas, graficos, salvar
  __main__.py        # CLI
  gui/
    __init__.py
    janela.py            # janela, controles e laço de simulação
    widget_grade.py      # canvas: ambiente e mapa interno 0-4
    widget_resultados.py # aba com gráficos da bateria
    __main__.py          # python -m aspirador.gui
tests/
  test_core.py
resultados/
  tables/            # por_config.csv, medias_globais.csv, eficiencia.csv
  charts/            # graficos.png, barras_medidas.png, curva_limpas.png, boxplot.png
docs/
  GUIA.md            # fonte de verdade imutável
  PLANO.md           # escopo, requisitos e fases
  ARQUITETURA.md     # este documento
```

## 2. Responsabilidades

- **`ambiente.py`** — estado real do mundo (grade `LIVRE/SUJO/OBSTACULO`),
  geração reprodutível por seed com flood fill, ações (`Acao`), aplicação das
  ações (`aplicar`), e o sensor local (`Sensor`/`Percepcao`).
- **`agentes.py`** — o agente reativo simples e o baseado em modelos; este
  último tem memória configurável: `mapa` (matriz 0–4 com célula + 8 vizinhos e
  BFS), `posicao` (só a posição atual/anterior) ou `hibrida` (trajetória com 1
  célula por passo).
- **`simulador.py`** — ciclo percepção → decisão → ação → medida, as duas
  medidas de desempenho (contando apenas células limpas **pelo agente**), o
  critério de parada (T fixo; opcionalmente encerrar quando limpo) e o resultado
  consolidado, incluindo métricas de eficiência (passos e movimentos até limpar,
  percentual de sujeira removida).
- **`experimentos.py`** — geração de configurações, execução da bateria,
  tabelas agregadas e gráficos.
- **`gui/`** — interface Tkinter opcional que consome o núcleo; permite
  configurar a simulação (agente, seed, tamanho, densidades, posição, T) e
  acompanhá-la. Não é importada por `aspirador/__init__.py`, então o núcleo e a
  CLI continuam funcionando sem Tkinter.

## 3. Contratos

```text
Sensor.perceber(ambiente, bateu) -> Percepcao
Agente.agir(percepcao)           -> Acao
Agente.reset(seed)               -> None
Agente.mapa_interno()            -> EstadoInterno | None
AgenteBaseadoEmModelo(seed, memoria="mapa"|"posicao"|"hibrida")
aplicar(ambiente, acao)          -> bool (bateu)
Simulador.rodar(T)               -> Resultado
Simulador(T, parar_quando_limpo) -> encerra ao limpar (T como teto) se True
```

## 4. Fluxo

```text
Config -> Ambiente(seed) -> Simulador(ambiente, agente, T)
       -> [ percepcao -> agente.agir -> aplicar -> sensor.perceber -> medidas ] x T
       -> Resultado -> CSV -> tabelas -> graficos
```

## 5. Modelo de informação

O agente nunca recebe a grade completa. A percepção contém apenas sujeira da
célula atual, flag de colisão, posição relativa ao ponto de partida e vizinhança
local. O estado interno é uma matriz 0–4 com origem no ponto de partida:
`0 nada`, `1 passado`, `2 sujo conhecido`, `3 passado/limpo`, `4 barreira`.
