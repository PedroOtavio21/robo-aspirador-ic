from pathlib import Path

import pandas as pd
import pytest

from aspirador import experimentos
from aspirador.simulador import Resultado


def _resultado() -> Resultado:
    return Resultado(
        score_a=12.5,
        score_b=10.0,
        movimentos=7,
        passos=9,
        celulas_limpas=5,
        total_sujos=6,
        limpo=False,
        passos_ate_limpo=9,
        movimentos_ate_limpo=7,
        percentual_limpo=83.33,
        historico_a=[1.0, 2.0, 3.0],
        historico_b=[0.5, 1.5, 2.5],
    )


def _redirecionar_saida(monkeypatch, tmp_path) -> tuple[Path, Path]:
    dir_gui = tmp_path / "gui"
    dir_charts = dir_gui / "charts"
    arq = dir_gui / "execucoes.csv"
    monkeypatch.setattr(experimentos, "DIR_GUI", str(dir_gui))
    monkeypatch.setattr(experimentos, "DIR_GUI_CHARTS", str(dir_charts))
    monkeypatch.setattr(experimentos, "ARQ_GUI_EXECUCOES", str(arq))
    return dir_charts, arq


def test_salvar_execucao_gui_grava_csv_e_grafico(monkeypatch, tmp_path):
    dir_charts, arq = _redirecionar_saida(monkeypatch, tmp_path)

    caminho = experimentos.salvar_execucao_gui(
        _resultado(),
        agente="Baseado em modelo",
        memoria="mapa",
        seed=42,
        largura=8,
        altura=8,
        densidade_sujeira=0.3,
        densidade_obstaculo=0.1,
        posicao_inicial=(0, 0),
        T=500,
        parar_quando_limpo=False,
    )

    assert arq.exists()
    assert Path(caminho).exists()
    assert Path(caminho).parent == dir_charts

    df = pd.read_csv(arq)
    assert len(df) == 1
    linha = df.iloc[0]
    assert linha["origem"] == "gui"
    assert linha["agente"] == "Baseado em modelo"
    assert linha["memoria"] == "mapa"
    assert linha["seed"] == 42
    assert linha["largura"] == 8
    assert linha["altura"] == 8
    assert linha["posicao_inicial"] == "0,0"
    assert linha["T"] == 500
    assert bool(linha["parar_quando_limpo"]) is False
    assert linha["score_a"] == pytest.approx(12.5)
    assert linha["score_b"] == pytest.approx(10.0)
    assert linha["movimentos"] == 7
    assert linha["passos"] == 9
    assert linha["celulas_limpas"] == 5
    assert linha["total_sujos"] == 6
    assert linha["grafico"] == caminho


def test_salvar_execucao_gui_acrescenta_linhas_com_header_unico(monkeypatch, tmp_path):
    _, arq = _redirecionar_saida(monkeypatch, tmp_path)

    for _ in range(2):
        experimentos.salvar_execucao_gui(
            _resultado(),
            agente="Reativo simples",
            memoria=None,
            seed=1,
            largura=4,
            altura=4,
            densidade_sujeira=0.2,
            densidade_obstaculo=0.0,
            posicao_inicial=(1, 2),
            T=10,
            parar_quando_limpo=True,
        )

    linhas = arq.read_text().splitlines()
    assert linhas[0].startswith("timestamp,")
    assert sum(1 for linha in linhas if linha.startswith("timestamp,")) == 1

    df = pd.read_csv(arq)
    assert len(df) == 2
    assert (df["origem"] == "gui").all()
    assert df["memoria"].fillna("").eq("").all()
    assert (df["posicao_inicial"] == "1,2").all()
    assert df["parar_quando_limpo"].astype(bool).all()
