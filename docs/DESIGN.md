# Projeto — Design

Documento consolidado. Deriva de `GUIA.md` (fonte de verdade imutável) e
substitui os antigos `PLANO.md` e `ARQUITETURA.md`, reunindo escopo, requisitos,
decisões de corte, fases, critérios de aceite, estrutura, responsabilidades,
contratos, fluxo e modelo de informação.

## 1. Escopo

Implementar, simular e avaliar experimentalmente dois programas de agente para o
mundo do aspirador de pó:

1. **Agente reativo simples** — decide apenas com a percepção atual, por regras
   condição-ação, sem memória.
2. **Agente reativo baseado em modelos** — mantém estado interno que representa
   o que já foi observado, combinado com regras condição-ação.

O ambiente é determinístico e parcialmente observável; os agentes desconhecem o
padrão inicial de sujeira e a geografia (extensão, limites, obstáculos). Os
sensores operam estritamente de forma local.

## 2. Requisitos → artefato

| Requisito (GUIA.md) | Onde é atendido |
|---|---|
| Agente reativo simples | `aspirador/agentes.py` |
| Agente baseado em modelos | `aspirador/agentes.py` |
| Estado interno + regras condição-ação | `aspirador/agentes.py` |
| Ambiente determinístico e parcialmente observável | `aspirador/ambiente.py` |
| Sensores estritamente locais | `aspirador/ambiente.py` (`Sensor`) |
| Medida 1: +1 por célula limpa **pelo robô** (uma vez) | `aspirador/simulador.py` (`MedidaA`) |
| Medida 2: +1 por célula limpa **pelo robô** (uma vez) e −1 por movimento | `aspirador/simulador.py` (`MedidaB`) |
| Fixar tamanho do ambiente | `aspirador/experimentos.py` (`TAMANHO_FIXO = 8`) |
| Múltiplas configurações (sujeira/obstáculos/posição) | `aspirador/experimentos.py` |
| Pontuação por configuração | `resultados/tables/por_config.csv` |
| Pontuação média global | `resultados/tables/medias_globais.csv` |
| Discussão crítica e racionalidade | seção no `README.md` |
| Apresentação (mecanismos, comportamento, tabelas, racionalidade) | roteiro no `README.md` (oral) |

## 3. Extras (não exigidos pelo guia)

- **Interface gráfica Tkinter** (`aspirador/gui/`) para configurar a simulação
  manualmente (agente, seed, tamanho, densidades, posição, T) e acompanhar
  passo a passo, incluindo a opção **"Parar quando limpo"**. Entradas:
  `uv run python -m aspirador.gui` e `uv run python main.py`. O núcleo permanece
  independente da GUI.
- **Métricas auxiliares** de eficiência (passos até limpar, movimentos até
  limpo e percentual de sujeira removida), sem alterar as Medidas A/B.
- **Memória configurável** no agente baseado em modelos: `mapa` (padrão),
  `posicao` (só a posição atual/anterior, anti-retrocesso) ou `hibrida`
  (trajetória acumulada com 1 célula por passo); exposta na GUI e na CLI via
  `--memoria`.
- **Dados extras / aba Extra** (`--extra`): A/B com "parar quando limpo",
  comparação dos modos de memória e eficiência. Evidência secundária — a
  principal continua sendo A/B com T fixo.
- **Salvar execução na GUI** — grava parâmetros e A/B da simulação atual em
  `resultados/gui/execucoes.csv` e um PNG da evolução em
  `resultados/gui/charts/`, fora da bateria reprodutível da CLI.

## 4. Decisões de corte

- **Núcleo em 3 módulos** (`ambiente.py`, `agentes.py`, `simulador.py`) e
  experimentos em um único módulo.
- **Documentação final enxuta** — `README.md` na raiz e `docs/` (`GUIA.md`,
  `DESIGN.md`).
- **Tamanho fixo 8 × 8** e **T = 500** períodos na bateria principal (a GUI
  permite outros valores manualmente).
- **Critério de parada:** T fixo nos experimentos (igualdade do orçamento de
  movimentos e de oportunidades, para comparar as Medidas A e B em condições
  justas); "parar quando limpo" apenas como opção da GUI, com T como teto.
- **Interpretação de "quadrado limpo":** célula cuja sujeira foi removida pelo
  agente; células que já iniciam limpas não pontuam (leitura mais estrita do que
  o texto literal do `GUIA.md`, registrada em `README.md`).
- **GUI opcional** — só a interface importa Tkinter; o restante roda sem ela.

Fora de escopo: empacotamento publicável, execução paralela.

## 5. Fases

1. `docs/GUIA.md` imutável + `AGENTS.md`.
2. `docs/DESIGN.md` (consolidação do plano e da arquitetura).
3. Código em `aspirador/`.
4. Testes essenciais em `tests/`.
5. Bateria experimental e regeneração de `resultados/`.
6. `README.md`.
7. Interface gráfica em `aspirador/gui/` + `main.py`.
8. Validação (pytest + CLI + GUI).

## 6. Critérios de aceite

- `uv run pytest -q` passa.
- `uv run python -m aspirador` gera tabelas e gráficos de forma reprodutível.
- `uv run python main.py` abre a GUI e permite configurar e executar a simulação.
- Todos os requisitos da Seção 3 do `GUIA.md` têm artefato correspondente.

## 7. Estrutura

```
README.md            # execução, estrutura, resultados e discussão
AGENTS.md            # regras do projeto
main.py              # atalho da GUI: uv run python main.py
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
    widget_resultados.py # aba com gráficos da bateria (A/B)
    widget_extra.py      # aba com métricas complementares
    __main__.py          # uv run python -m aspirador.gui
tests/
  test_core.py
  test_experimentos.py
resultados/
  raw/               # resultados.csv, historico.csv (brutos)
  tables/            # por_config.csv, medias_globais.csv, eficiencia.csv
  charts/            # graficos.png + metrica_a/b, comparativo_metricas/modelos,
                     # curva_limpas, boxplot
  extra/             # parar_limpo, memorias, eficiencia, graficos_extra,
                     # comparativo_memorias, normal_vs_break, eficiencia (--extra)
  gui/               # execucoes.csv + charts/ (salvar execução da GUI)
  configuracoes.json
docs/
  GUIA.md            # fonte de verdade imutável
  DESIGN.md          # este documento
```

## 8. Responsabilidades

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
  percentual de sujeira removida). A **Medida A** soma +1 por célula limpa pelo
  robô (**uma única vez**); a **Medida B** conta o mesmo +1 por célula limpa e
  subtrai −1 por movimento (eficiência de deslocamento).
- **`experimentos.py`** — geração de configurações, execução da bateria
  principal (A/B) e da bateria extra (`--extra`: parar quando limpo, modos de
  memória, eficiência), tabelas agregadas, gráficos e a persistência da execução
  salva pela GUI.
- **`gui/`** — interface Tkinter opcional que consome o núcleo; permite
  configurar a simulação (agente, seed, tamanho, densidades, posição, T) e
  acompanhá-la. Não é importada por `aspirador/__init__.py`, então o núcleo e a
  CLI continuam funcionando sem Tkinter.

## 9. Contratos

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

## 10. Fluxo

```text
Config -> Ambiente(seed) -> Simulador(ambiente, agente, T)
       -> [ percepcao -> agente.agir -> aplicar -> sensor.perceber -> medidas ] x T
       -> Resultado -> CSV -> tabelas -> graficos
```

## 11. Modelo de informação

O agente nunca recebe a grade completa. A percepção contém apenas sujeira da
célula atual, flag de colisão, posição relativa ao ponto de partida e vizinhança
local. O estado interno é uma matriz 0–4 com origem no ponto de partida:
`0 nada`, `1 passado`, `2 sujo conhecido`, `3 passado/limpo`, `4 barreira`.
