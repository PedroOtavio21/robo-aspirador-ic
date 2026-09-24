"""Testes do ambiente."""

from core import atuadores
from core.ambiente import LIVRE, OBSTACULO, SUJO, Acao, Ambiente


def _ambiente_vazio(largura=3, altura=3):
    amb = Ambiente(largura, altura, densidade_sujeira=0.0, densidade_obstaculo=0.0, seed=0)
    amb.grade = [[LIVRE] * altura for _ in range(largura)]
    amb.posicao = (0, 0)
    amb.movimentos = 0
    amb.limpas = 0
    return amb


def test_batida_nao_move_e_conta_movimento():
    amb = _ambiente_vazio()
    bateu = atuadores.aplicar(amb, Acao.CIMA)

    assert bateu is True
    assert amb.posicao == (0, 0)
    assert amb.movimentos == 1


def test_batida_em_obstaculo():
    amb = _ambiente_vazio()
    amb.grade[1][0] = OBSTACULO
    bateu = atuadores.aplicar(amb, Acao.BAIXO)

    assert bateu is True
    assert amb.posicao == (0, 0)
    assert amb.movimentos == 1


def test_movimento_valido():
    amb = _ambiente_vazio()
    bateu = atuadores.aplicar(amb, Acao.BAIXO)

    assert bateu is False
    assert amb.posicao == (1, 0)
    assert amb.movimentos == 1


def test_aspirar_limpa_a_celula():
    amb = _ambiente_vazio()
    amb.grade[0][0] = SUJO
    atuadores.aplicar(amb, Acao.ASPIRAR)

    assert amb.grade[0][0] == LIVRE
    assert amb.limpas == 1
    assert amb.movimentos == 0


def test_sujeira_nao_reaparece():
    amb = _ambiente_vazio()
    amb.grade[0][0] = SUJO
    atuadores.aplicar(amb, Acao.ASPIRAR)
    atuadores.aplicar(amb, Acao.NOOP)

    assert amb.grade[0][0] == LIVRE
    assert amb.limpas == 1


def test_grade_gerada_e_conectada():
    for seed in range(25):
        amb = Ambiente(8, 8, 0.4, 0.2, seed=seed)
        alcancaveis = amb._alcancaveis(amb.grade, amb.posicao)
        livres = {
            (x, y)
            for x in range(amb.largura)
            for y in range(amb.altura)
            if amb.grade[x][y] != OBSTACULO
        }
        assert alcancaveis == livres


def test_geracao_reprodutivel_por_seed():
    a = Ambiente(8, 8, 0.4, 0.15, seed=7)
    b = Ambiente(8, 8, 0.4, 0.15, seed=7)

    assert a.grade == b.grade
    assert a.posicao == b.posicao
    assert a.sujos_iniciais == b.sujos_iniciais


def test_posicao_inicial_configuravel():
    for _ in range(10):
        amb = Ambiente(8, 8, 0.4, 0.15, seed=1, posicao_inicial=(3, 3))
        assert amb.posicao == (3, 3)


def test_limpo():
    amb = _ambiente_vazio()
    assert amb.limpo() is True
    amb.grade[2][2] = SUJO
    assert amb.limpo() is False
