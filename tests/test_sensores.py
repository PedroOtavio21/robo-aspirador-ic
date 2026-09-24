"""Testes dos sensores (observabilidade parcial)."""

from core.ambiente import LIVRE, OBSTACULO, SUJO, Ambiente
from core.sensores import Sensor


def _ambiente(largura=4, altura=4):
    amb = Ambiente(largura, altura, 0.0, 0.0, seed=0)
    amb.grade = [[LIVRE] * altura for _ in range(largura)]
    amb.posicao = (1, 1)
    return amb


def test_percepcao_da_celula_atual():
    amb = _ambiente()
    amb.grade[1][1] = SUJO
    sensor = Sensor()
    sensor.reset(amb.posicao)

    percepcao = sensor.perceber(amb)
    assert percepcao.sujo is True
    assert percepcao.posicao == (0, 0)


def test_posicao_e_relativa_ao_inicio():
    amb = _ambiente()
    sensor = Sensor()
    sensor.reset(amb.posicao)
    amb.posicao = (2, 3)

    percepcao = sensor.perceber(amb)
    assert percepcao.posicao == (1, 2)


def test_vizinhanca_detecta_obstaculo_e_sujeira():
    amb = _ambiente()
    amb.grade[0][1] = OBSTACULO
    amb.grade[1][0] = SUJO
    sensor = Sensor(raio=1)
    sensor.reset(amb.posicao)

    vizinhanca = {(dx, dy): (sujo, obst) for dx, dy, sujo, obst in
                  sensor.perceber(amb).vizinhanca}
    assert vizinhanca[(-1, 0)] == (False, True)
    assert vizinhanca[(0, -1)] == (True, False)


def test_limite_e_tratado_como_barreira():
    amb = _ambiente()
    amb.posicao = (0, 0)
    sensor = Sensor(raio=1)
    sensor.reset(amb.posicao)

    vizinhanca = {(dx, dy): (sujo, obst) for dx, dy, sujo, obst in
                  sensor.perceber(amb).vizinhanca}
    assert vizinhanca[(-1, 0)] == (False, True)
    assert vizinhanca[(0, -1)] == (False, True)


def test_nao_expoe_mapa_completo():
    amb = _ambiente()
    sensor = Sensor(raio=1)
    sensor.reset(amb.posicao)

    percepcao = sensor.perceber(amb)
    assert not hasattr(percepcao, "grade")
    assert len(percepcao.vizinhanca) == 8
