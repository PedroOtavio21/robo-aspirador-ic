"""Testes das medidas de desempenho."""

from core.metricas import MedidaA, MedidaB


def test_medida_a_soma_quadrados_limpos_por_periodo():
    medida = MedidaA()
    medida.passo(quadrados_limpos=5, movimentos=1)
    medida.passo(quadrados_limpos=6, movimentos=1)
    medida.passo(quadrados_limpos=6, movimentos=0)

    assert medida.total == 17
    assert medida.historico == [5, 11, 17]


def test_medida_b_penaliza_movimentos():
    medida = MedidaB()
    medida.passo(quadrados_limpos=5, movimentos=2)
    medida.passo(quadrados_limpos=5, movimentos=1)

    assert medida.total == 7
    assert medida.movimentos == 3


def test_medida_b_igual_a_menos_movimentos():
    a = MedidaA()
    b = MedidaB()
    for limpos, movimentos in [(5, 1), (6, 0), (6, 2)]:
        a.passo(limpos, movimentos)
        b.passo(limpos, movimentos)

    assert b.total == a.total - b.movimentos


def test_media_global():
    medida = MedidaA()
    medida.passo(10, 0)
    medida.passo(20, 0)

    assert medida.media(2) == 15.0
    assert medida.media(0) == 0.0
