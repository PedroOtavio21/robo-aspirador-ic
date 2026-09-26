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
| Medida 1: +1 por quadrado limpo por período | `aspirador/simulador.py` (`MedidaA`) |
| Medida 2: +1 limpo e −1 por movimento | `aspirador/simulador.py` (`MedidaB`) |
| Fixar tamanho do ambiente | `aspirador/experimentos.py` (`TAMANHO_FIXO = 8`) |
| Múltiplas configurações (sujeira/obstáculos/posição) | `aspirador/experimentos.py` |
| Pontuação por configuração | `resultados/tables/por_config.csv` |
| Pontuação média global | `resultados/tables/medias_globais.csv` |
| Apresentação (mecanismos, comportamento, tabelas, racionalidade) | `docs/apresentacao.md` |

## 3. Decisões de corte

- **Sem interface gráfica** — não é exigida pelo guia. A demo é a CLI + gráficos.
- **Núcleo em 3 módulos** (`ambiente.py`, `agentes.py`, `simulador.py`) e
  experimentos em um único módulo.
- **Documentação final enxuta** — `README.md` + `docs/apresentacao.md`; os
  documentos antigos são substituídos.
- **Tamanho fixo 8 × 8** e **T = 500** períodos por execução.

Fora de escopo: GUI, empacotamento publicável, execução paralela.

## 4. Fases

1. `GUIA.md` imutável + `AGENTS.md`.
2. `PLANO.md` e `ARQUITETURA.md`.
3. Código em `aspirador/`.
4. Testes essenciais em `tests/test_core.py`.
5. Bateria experimental e regeneração de `resultados/`.
6. `docs/apresentacao.md` e `README.md`.
7. Validação (pytest + CLI + checklist do guia).

## 5. Critérios de aceite

- `pytest -q` passa.
- `python -m aspirador` gera tabelas e gráficos de forma reprodutível.
- Todos os requisitos da Seção 3 do `GUIA.md` têm artefato correspondente.
