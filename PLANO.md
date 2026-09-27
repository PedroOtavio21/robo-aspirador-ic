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
| Medida 1: +1 por quadrado limpo **pelo robô** por período | `aspirador/simulador.py` (`MedidaA`) |
| Medida 2: +1 limpo **pelo robô** e −1 por movimento | `aspirador/simulador.py` (`MedidaB`) |
| Fixar tamanho do ambiente | `aspirador/experimentos.py` (`TAMANHO_FIXO = 8`) |
| Múltiplas configurações (sujeira/obstáculos/posição) | `aspirador/experimentos.py` |
| Pontuação por configuração | `resultados/tables/por_config.csv` |
| Pontuação média global | `resultados/tables/medias_globais.csv` |
| Apresentação (mecanismos, comportamento, tabelas, racionalidade) | `docs/apresentacao.md` |

## 3. Extras (não exigidos pelo guia)

- **Interface gráfica Tkinter** (`aspirador/gui/`) para configurar a simulação
  manualmente (agente, seed, tamanho, densidades, posição, T) e acompanhar
  passo a passo, incluindo a opção **"Parar quando limpo"**. Entradas:
  `python -m aspirador.gui` e `python main.py`. O núcleo permanece independente
  da GUI.
- **Métricas auxiliares** de eficiência (passos até limpar, movimentos até
  limpo e percentual de sujeira removida), sem alterar as Medidas A/B.

## 4. Decisões de corte

- **Núcleo em 3 módulos** (`ambiente.py`, `agentes.py`, `simulador.py`) e
  experimentos em um único módulo.
- **Documentação final enxuta** — `README.md` + `docs/apresentacao.md`; os
  documentos antigos são substituídos.
- **Tamanho fixo 8 × 8** e **T = 500** períodos na bateria principal (a GUI
  permite outros valores manualmente).
- **Critério de parada:** T fixo nos experimentos (comparabilidade da Medida A);
  "parar quando limpo" apenas como opção da GUI, com T como teto.
- **Interpretação de "quadrado limpo":** célula cuja sujeira foi removida pelo
  agente; células que já iniciam limpas não pontuam (leitura mais estrita do que
  o texto literal do `GUIA.md`, registrada em `README.md`).
- **GUI opcional** — só a interface importa Tkinter; o restante roda sem ela.

Fora de escopo: empacotamento publicável, execução paralela.

## 5. Fases

1. `GUIA.md` imutável + `AGENTS.md`.
2. `PLANO.md` e `ARQUITETURA.md`.
3. Código em `aspirador/`.
4. Testes essenciais em `tests/test_core.py`.
5. Bateria experimental e regeneração de `resultados/`.
6. `docs/apresentacao.md` e `README.md`.
7. Interface gráfica em `aspirador/gui/` + `main.py`.
8. Validação (pytest + CLI + GUI).

## 6. Critérios de aceite

- `pytest -q` passa.
- `python -m aspirador` gera tabelas e gráficos de forma reprodutível.
- `python main.py` abre a GUI e permite configurar e executar a simulação.
- Todos os requisitos da Seção 3 do `GUIA.md` têm artefato correspondente.
