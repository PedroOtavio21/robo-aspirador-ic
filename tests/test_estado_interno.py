"""Testes do estado interno (matriz 0-4)."""

from core.estado_interno import (
    BARREIRA,
    NADA,
    PASSADO,
    PASSADO_LIMPO,
    SUJO,
    EstadoInterno,
)
from core.ambiente import Acao
from core.sensores import Percepcao


def test_matriz_inicia_toda_zero():
    estado = EstadoInterno(capacidade=11)
    assert all(valor == NADA for linha in estado.matriz for valor in linha)
    assert estado.valor((0, 0)) == NADA


def test_percepcao_limpa_marca_passado():
    estado = EstadoInterno(capacidade=11)
    percepcao = Percepcao(sujo=False, bateu=False, posicao=(0, 0), vizinhanca=())
    estado.atualizar(percepcao, acao_anterior=None)

    assert estado.posicao == (0, 0)
    assert estado.valor((0, 0)) == PASSADO


def test_percepcao_suja_marca_sujo():
    estado = EstadoInterno(capacidade=11)
    percepcao = Percepcao(sujo=True, bateu=False, posicao=(1, 0), vizinhanca=())
    estado.atualizar(percepcao, acao_anterior=Acao.DIREITA)

    assert estado.valor((1, 0)) == SUJO


def test_aspirar_marca_passado_limpo():
    estado = EstadoInterno(capacidade=11)
    estado.atualizar(
        Percepcao(sujo=True, bateu=False, posicao=(0, 0), vizinhanca=()),
        acao_anterior=None,
    )
    estado.atualizar(
        Percepcao(sujo=False, bateu=False, posicao=(0, 0), vizinhanca=()),
        acao_anterior=Acao.ASPIRAR,
    )
    assert estado.valor((0, 0)) == PASSADO_LIMPO


def test_batida_marca_barreira():
    estado = EstadoInterno(capacidade=11)
    estado.atualizar(
        Percepcao(sujo=False, bateu=True, posicao=(0, 0), vizinhanca=()),
        acao_anterior=Acao.CIMA,
    )
    assert estado.posicao == (0, 0)
    assert estado.valor((-1, 0)) == BARREIRA


def test_obstaculo_da_vizinhanca_vira_barreira():
    estado = EstadoInterno(capacidade=11)
    percepcao = Percepcao(
        sujo=False,
        bateu=False,
        posicao=(0, 0),
        vizinhanca=(( -1, 0, False, True),),
    )
    estado.atualizar(percepcao, acao_anterior=None)
    assert estado.valor((-1, 0)) == BARREIRA


def test_informacao_nao_observada_permanece_desconhecida():
    estado = EstadoInterno(capacidade=11)
    estado.atualizar(
        Percepcao(sujo=False, bateu=False, posicao=(0, 0), vizinhanca=()),
        acao_anterior=None,
    )
    assert estado.valor((3, 3)) == NADA
    assert estado.valor((0, 1)) == NADA


def test_fronteira_e_sujos_conhecidos():
    estado = EstadoInterno(capacidade=11)
    estado.atualizar(
        Percepcao(sujo=False, bateu=False, posicao=(0, 0), vizinhanca=()),
        acao_anterior=None,
    )
    assert (0, 1) in estado.fronteira()
    assert estado.sujos_conhecidos() == set()
