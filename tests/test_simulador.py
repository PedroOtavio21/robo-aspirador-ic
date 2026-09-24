"""Testes do simulador e das medidas."""

from core.agentes import AgenteBaseadoEmModelo, AgenteReativoSimples
from core.ambiente import Ambiente
from core.simulador import Simulador


def test_medidas_consistentes():
    ambiente = Ambiente(8, 8, 0.4, 0.15, seed=10)
    simulador = Simulador(ambiente, AgenteBaseadoEmModelo(seed=10), T=500)
    resultado = simulador.rodar()

    assert resultado.score_b == resultado.score_a - resultado.movimentos
    assert resultado.movimentos == ambiente.movimentos
    assert len(resultado.historico_limpos) == resultado.passos
    assert len(resultado.acoes) == resultado.passos


def test_historico_nao_decresce():
    ambiente = Ambiente(8, 8, 0.4, 0.15, seed=11)
    simulador = Simulador(ambiente, AgenteReativoSimples(seed=11), T=200)
    resultado = simulador.rodar()

    assert all(
        a <= b for a, b in zip(resultado.historico_limpos, resultado.historico_limpos[1:])
    )


def test_para_no_limite_de_passos():
    ambiente = Ambiente(8, 8, 0.6, 0.2, seed=5)
    simulador = Simulador(ambiente, AgenteReativoSimples(seed=5), T=5)
    resultado = simulador.rodar()

    assert resultado.passos == 5


def test_simulacao_reprodutivel():
    a = Simulador(
        Ambiente(8, 8, 0.4, 0.15, seed=99), AgenteReativoSimples(seed=99), T=300
    ).rodar()
    b = Simulador(
        Ambiente(8, 8, 0.4, 0.15, seed=99), AgenteReativoSimples(seed=99), T=300
    ).rodar()

    assert a.score_a == b.score_a
    assert a.score_b == b.score_b
    assert a.movimentos == b.movimentos
    assert a.acoes == b.acoes


def test_modelo_limpa_mais_que_reativo():
    ambiente = Ambiente(8, 8, 0.4, 0.15, seed=123)
    modelo = Simulador(ambiente, AgenteBaseadoEmModelo(seed=123), T=500).rodar()

    ambiente = Ambiente(8, 8, 0.4, 0.15, seed=123)
    reativo = Simulador(ambiente, AgenteReativoSimples(seed=123), T=500).rodar()

    assert modelo.celulas_limpas >= reativo.celulas_limpas
    assert modelo.score_a >= reativo.score_a
