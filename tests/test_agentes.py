"""Testes dos agentes."""

import pytest

from core import atuadores
from core.agentes import AgenteBaseadoEmModelo, AgenteReativoSimples
from core.ambiente import MOVIMENTOS, Acao, Ambiente
from core.estado_interno import BARREIRA, EstadoInterno
from core.sensores import Percepcao, Sensor
from core.simulador import Simulador


def test_reativo_aspira_quando_sujo():
    agente = AgenteReativoSimples(seed=0)
    percepcao = Percepcao(sujo=True, bateu=False, posicao=(0, 0), vizinhanca=())
    assert agente.agir(percepcao) is Acao.ASPIRAR


def test_reativo_so_move_quando_limpo():
    agente = AgenteReativoSimples(seed=0)
    percepcao = Percepcao(sujo=False, bateu=False, posicao=(0, 0), vizinhanca=())
    assert agente.agir(percepcao) in MOVIMENTOS


def test_reativo_nao_tem_memoria():
    agente = AgenteReativoSimples(seed=0)
    assert agente.mapa_interno() is None


def test_reativo_reprodutivel():
    percepcoes = [
        Percepcao(sujo=False, bateu=False, posicao=(0, 0), vizinhanca=())
        for _ in range(20)
    ]
    a = AgenteReativoSimples(seed=42)
    b = AgenteReativoSimples(seed=42)
    assert [a.agir(p) for p in percepcoes] == [b.agir(p) for p in percepcoes]


def test_modelo_mantem_estado_interno():
    agente = AgenteBaseadoEmModelo(seed=0)
    assert isinstance(agente.mapa_interno(), EstadoInterno)


def test_modelo_limpa_tudo_e_para():
    ambiente = Ambiente(4, 4, densidade_sujeira=0.5, densidade_obstaculo=0.0, seed=3)
    agente = AgenteBaseadoEmModelo(seed=3)
    sensor = Sensor()
    sensor.reset(ambiente.posicao)
    percepcao = sensor.perceber(ambiente)

    for _ in range(300):
        acao = agente.agir(percepcao)
        if acao is Acao.NOOP:
            break
        bateu = atuadores.aplicar(ambiente, acao)
        percepcao = sensor.perceber(ambiente, bateu)
    else:
        pytest.fail("O agente baseado em modelo não parou.")

    assert ambiente.limpo() is True
    assert ambiente.limpas == ambiente.sujos_iniciais


def test_modelo_registra_obstaculos_descobertos():
    ambiente = Ambiente(5, 5, densidade_sujeira=0.3, densidade_obstaculo=0.2, seed=1)
    agente = AgenteBaseadoEmModelo(seed=1)
    Simulador(ambiente, agente, T=300).rodar()

    estado = agente.mapa_interno()
    barreiras = [
        (x, y)
        for x in range(-10, 11)
        for y in range(-10, 11)
        if estado.valor((x, y)) == BARREIRA
    ]
    assert barreiras
