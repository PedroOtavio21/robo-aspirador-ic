# Regras do projeto

## Fonte de verdade

- `GUIA.md` é **imutável**. Nunca edite, renomeie, mova ou reformate esse arquivo.
- `PLANO.md`, `ARQUITETURA.md`, o código (`aspirador/`), os testes e a documentação
  final devem **derivar e obedecer** ao `GUIA.md`.
- Se houver conflito entre qualquer artefato e o `GUIA.md`, o `GUIA.md` prevalece.
- `project-document.md` é o enunciado original da disciplina e também não deve ser alterado.

## Convenções

- Python 3.11+.
- Núcleo em `aspirador/`: `ambiente.py`, `agentes.py`, `simulador.py`.
- Experimentos em `aspirador/experimentos.py`; CLI em `python -m aspirador`.
- Interface gráfica opcional em `aspirador/gui/` (Tkinter; requer `python3-tk`).
  O núcleo não importa a GUI, então o pacote continua utilizável sem Tkinter.
- Sem comentários no código, salvo quando solicitado.
- Toda saída experimental é reproduzível por seed.
- Critério de parada: **T fixo** nos experimentos (para comparar a Medida A);
  "parar quando limpo" é apenas uma opção da GUI, com T como teto.
- "Quadrado limpo" nas medidas = célula cuja sujeira foi **removida pelo
  agente**; células que já iniciam limpas não pontuam.

## Comandos

```bash
pip install -r requirements.txt
pytest -q
python -m aspirador --configs 40 --repeticoes 10 --T 500 --seed 2024
sudo apt install python3-tk   # pré-requisito da interface
python main.py                # interface gráfica
```
