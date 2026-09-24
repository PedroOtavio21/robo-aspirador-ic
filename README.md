# Projeto 1 — Avaliação Experimental de Agentes Inteligentes

**Disciplina:** Inteligência Computacional
**Stack:** Python + Tkinter (interface) + matplotlib/pandas (experimentos)

Simulador do mundo do aspirador de pó com dois agentes — **reativo simples** e
**baseado em modelos** — comparados sob duas medidas:

- **Medida A:** +1 ponto por quadrado limpo a cada período (acumulado).
- **Medida B:** +1 ponto por quadrado limpo e −1 ponto por movimento.

Planejamento completo: [`planing_project.md`](planing_project.md).
Documentação: [`docs/`](docs/).

---

## Escolha da interface: Tkinter

**A favor**
- Biblioteca padrão: basta `python3-tk` no sistema, sem pacote pip pesado.
- `after()` resolve a animação passo a passo, sem threads.
- Grade desenhada num `tk.Canvas`; gráficos embutidos com `FigureCanvasTkAgg`.
- Fácil de rodar na demo: `python main.py`.

**Contra**
- Visual mais sóbrio que Qt; `python3-tk` é pacote de sistema.

**Mitigação:** a lógica (`core/`, `experimentos/`) é **100% independente da
interface**; os experimentos rodam sem GUI.

---

## Como executar

```bash
# 1) Dependência de sistema do Tkinter (Ubuntu/Debian)
sudo apt install python3-tk

# 2) Ambiente virtual e dependências Python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3) Testes
pytest -q

# 4) Bateria de experimentos (40 configs, 10 repetições, T=500)
python -m experimentos

# 5) Interface gráfica
python main.py
```

### Interface
- **Agente:** reativo simples / baseado em modelo.
- **Seed:** mesma seed ⇒ mesma simulação.
- **Novo / Passo / Play-Pause** e controle de **velocidade**.
- **Placar:** período, Medida A, Medida B, movimentos e status.
- Dois canvas lado a lado: **ambiente real** e **matriz interna 0–4**.

---

## Estrutura

```
core/            ambiente.py, sensores.py, atuadores.py, agentes.py,
                 estado_interno.py, metricas.py, simulador.py
experimentos/    gerador_config.py, executor.py, graficos.py, cli.py,
                 configurations/, raw/
resultados/      tables/, charts/
gui/             janela.py, widget_grade.py, widget_resultados.py
main.py          ponto de entrada da GUI
docs/            especificacao.md, metodologia.md, resultados.md, racionalidade.md
tests/           test_ambiente, test_sensores, test_estado_interno,
                 test_agentes, test_metricas, test_simulador
```

## Contrato

- `Sensor.perceber(ambiente, bateu) -> Percepcao`
- `Agente.agir(percepcao) -> Acao`
- `atuadores.aplicar(ambiente, acao) -> bool (bateu)`
- `Simulador.rodar(T) -> Resultado(score_a, score_b, movimentos, passos, acoes, ...)`

## Estado interno do agente baseado em modelos

Matriz com a mesma cobertura do mapa (capacidade máxima fixa, origem no ponto
de partida):

| valor | significado |
|---|---|
| 0 | nada / desconhecido |
| 1 | passado (já estava limpo) |
| 2 | sujo conhecido |
| 3 | passado e limpo |
| 4 | barreira / obstáculo / limite |

## Decisões registradas

- [x] Matriz interna com **capacidade máxima fixa** (não revela a extensão).
- [x] **Toda tentativa de movimento** conta como movimento (inclusive batida).
- [x] Tamanho fixo **8 × 8** no conjunto principal.
- [x] Ambas as medidas calculadas **na mesma execução**.
- [x] **T = 500 períodos fixos** para todos (mesmo nº de períodos).
- [x] Obstáculos não entram na contagem de quadrados limpos.
- [x] `ASPIRAR`/`NOOP` não contam como movimento.

---

## Resultados obtidos

Bateria: 40 configurações, T=500, reativo com 10 repetições (440 execuções).

| Agente | Medida A | Medida B | Movimentos | Limpou tudo |
|---|---:|---:|---:|---:|
| Baseado em modelo | **28.436 ± 2.199** | **28.354 ± 2.198** | 82 | 100 % |
| Reativo simples | 25.403 ± 2.938 | 24.923 ± 2.936 | 480 | 24 % |

Análise completa em [`docs/resultados.md`](docs/resultados.md) e
[`docs/racionalidade.md`](docs/racionalidade.md).

---

## Reprodutibilidade

- Versão do Python sugerida: **3.11+**.
- Dependências: `requirements.txt`.
- Sementes e configurações: `experimentos/configurations/configuracoes.json`.
- Dados brutos: `experimentos/raw/resultados.csv` e `historico.csv`.
- Tabelas e gráficos: `resultados/tables/` e `resultados/charts/`.
- **Recomendado:** versionar em git e registrar o hash do commit usado nos
  experimentos.

## Armadilhas comuns

- Rodar os agentes em configurações diferentes — invalida a comparação.
- Atualizar a posição do agente baseado em modelos mesmo quando ele bateu.
- Deixar o reativo sem seed — resultados irreprodutíveis.
- Comparar as medidas usando números diferentes de períodos.
- Misturar lógica de simulação dentro da GUI.
