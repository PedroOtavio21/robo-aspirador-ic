# Plano do Projeto

Derivado de `GUIA.md` (imutável). Define escopo, requisitos e fases.

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
| Apresentação (mecanismos, comportamento, tabelas, racionalidade) | apresentação oral (fora do repositório) |

## 3. Extras (não exigidos pelo guia)

- **Interface gráfica Tkinter** (`aspirador/gui/`) para configurar a simulação
  manualmente (agente, seed, tamanho, densidades, posição, T) e acompanhar
  passo a passo, incluindo a opção **"Parar quando limpo"**. Entradas:
  `python -m aspirador.gui` e `python main.py`. O núcleo permanece independente
  da GUI.
- **Métricas auxiliares** de eficiência (passos até limpar, movimentos até
  limpo e percentual de sujeira removida), sem alterar as Medidas A/B.
- **Memória configurável** no agente baseado em modelos: `mapa` (padrão),
  `posicao` (só a posição atual/anterior, anti-retrocesso) ou `hibrida`
  (trajetória acumulada com 1 célula por passo); exposta na GUI e na CLI via
  `--memoria`.
- **Dados extras / aba Extra** (`--extra`): A/B com "parar quando limpo",
  comparação dos modos de memória e eficiência. Evidência secundária — a
  principal continua sendo A/B com T fixo.

## 4. Decisões de corte

- **Núcleo em 3 módulos** (`ambiente.py`, `agentes.py`, `simulador.py`) e
  experimentos em um único módulo.
- **Documentação final enxuta** — `README.md` na raiz e `docs/` (`GUIA.md`,
  `PLANO.md`, `ARQUITETURA.md`).
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
2. `docs/PLANO.md` e `docs/ARQUITETURA.md`.
3. Código em `aspirador/`.
4. Testes essenciais em `tests/test_core.py`.
5. Bateria experimental e regeneração de `resultados/`.
6. `README.md`.
7. Interface gráfica em `aspirador/gui/` + `main.py`.
8. Validação (pytest + CLI + GUI).

## 6. Critérios de aceite

- `pytest -q` passa.
- `python -m aspirador` gera tabelas e gráficos de forma reprodutível.
- `python main.py` abre a GUI e permite configurar e executar a simulação.
- Todos os requisitos da Seção 3 do `GUIA.md` têm artefato correspondente.
