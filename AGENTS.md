# Regras do projeto

## Fonte de verdade

- `GUIA.md` é **imutável**. Nunca edite, renomeie, mova ou reformate esse arquivo.
- `PLANO.md`, `ARQUITETURA.md`, o código (`aspirador/`), os testes e a documentação
  final devem **derivar e obedecer** ao `GUIA.md`.
- Se houver conflito entre qualquer artefato e o `GUIA.md`, o `GUIA.md` prevalece.
- `project-document.md` é o enunciado original da disciplina e também não deve ser alterado.

## Convenções

- Python 3.11+; sem interface gráfica (a GUI não é exigida pelo guia).
- Núcleo em `aspirador/`: `ambiente.py`, `agentes.py`, `simulador.py`.
- Experimentos em `aspirador/experimentos.py`; CLI em `python -m aspirador`.
- Sem comentários no código, salvo quando solicitado.
- Toda saída experimental é reproduzível por seed.

## Comandos

```bash
pip install -r requirements.txt
pytest -q
python -m aspirador --configs 40 --repeticoes 10 --T 500 --seed 2024
```
