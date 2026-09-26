from aspirador.agentes import (
    BARREIRA,
    NADA,
    PASSADO,
    PASSADO_LIMPO,
    AgenteBaseadoEmModelo,
    AgenteReativoSimples,
    EstadoInterno,
)
from aspirador.agentes import SUJO as SUJO_INTERNO
from aspirador.ambiente import (
    LIVRE,
    OBSTACULO,
    SUJO,
    Acao,
    Ambiente,
    Percepcao,
    Sensor,
    aplicar,
)
from aspirador.simulador import MedidaA, MedidaB, Simulador


def _ambiente_vazio(largura=3, altura=3):
    amb = Ambiente(largura, altura, densidade_sujeira=0.0, densidade_obstaculo=0.0, seed=0)
    amb.grade = [[LIVRE] * altura for _ in range(largura)]
    amb.posicao = (0, 0)
    amb.movimentos = 0
    amb.limpas = 0
    return amb


def test_batida_nao_move_e_conta_movimento():
    amb = _ambiente_vazio()
    assert aplicar(amb, Acao.CIMA) is True
    assert amb.posicao == (0, 0)
    assert amb.movimentos == 1


def test_movimento_valido():
    amb = _ambiente_vazio()
    assert aplicar(amb, Acao.BAIXO) is False
    assert amb.posicao == (1, 0)
    assert amb.movimentos == 1


def test_aspirar_limpa_a_celula():
    amb = _ambiente_vazio()
    amb.grade[0][0] = SUJO
    aplicar(amb, Acao.ASPIRAR)
    assert amb.grade[0][0] == LIVRE
    assert amb.limpas == 1
    assert amb.movimentos == 0


def test_geracao_conectada_e_reprodutivel():
    for seed in range(10):
        amb = Ambiente(8, 8, 0.4, 0.2, seed=seed)
        alcancaveis = amb._alcancaveis(amb.grade, amb.posicao)
        livres = {
            (x, y)
            for x in range(amb.largura)
            for y in range(amb.altura)
            if amb.grade[x][y] != OBSTACULO
        }
        assert alcancaveis == livres

    a = Ambiente(8, 8, 0.4, 0.15, seed=7)
    b = Ambiente(8, 8, 0.4, 0.15, seed=7)
    assert a.grade == b.grade
    assert a.posicao == b.posicao


def test_posicao_inicial_configuravel():
    amb = Ambiente(8, 8, 0.4, 0.15, seed=1, posicao_inicial=(3, 3))
    assert amb.posicao == (3, 3)


def test_sensor_local_e_posicao_relativa():
    amb = _ambiente_vazio(4, 4)
    amb.grade[1][1] = SUJO
    amb.grade[0][1] = OBSTACULO
    amb.posicao = (1, 1)

    sensor = Sensor(raio=1)
    sensor.reset(amb.posicao)
    amb.posicao = (2, 3)
    percepcao = sensor.perceber(amb)

    assert percepcao.posicao == (1, 2)
    assert not hasattr(percepcao, "grade")
    assert len(percepcao.vizinhanca) == 8


def test_reativo_aspira_e_muda():
    agente = AgenteReativoSimples(seed=0)
    assert agente.agir(Percepcao(True, False, (0, 0))) is Acao.ASPIRAR
    assert agente.mapa_interno() is None


def test_reativo_reprodutivel():
    percepcoes = [Percepcao(False, False, (0, 0)) for _ in range(20)]
    a = AgenteReativoSimples(seed=42)
    b = AgenteReativoSimples(seed=42)
    assert [a.agir(p) for p in percepcoes] == [b.agir(p) for p in percepcoes]


def test_estado_interno_atualizacao():
    estado = EstadoInterno(capacidade=11)
    estado.atualizar(Percepcao(False, False, (0, 0)), None)
    assert estado.valor((0, 0)) == PASSADO
    assert estado.valor((3, 3)) == NADA

    estado.atualizar(Percepcao(True, False, (1, 0)), Acao.DIREITA)
    assert estado.valor((1, 0)) == SUJO_INTERNO

    estado.atualizar(Percepcao(False, False, (1, 0)), Acao.ASPIRAR)
    assert estado.valor((1, 0)) == PASSADO_LIMPO

    estado.atualizar(Percepcao(False, True, (1, 0)), Acao.CIMA)
    assert estado.valor((0, 0)) == BARREIRA


def test_modelo_limpa_tudo_e_para():
    amb = Ambiente(4, 4, densidade_sujeira=0.5, densidade_obstaculo=0.0, seed=3)
    agente = AgenteBaseadoEmModelo(seed=3)
    simulador = Simulador(amb, agente, T=300)
    resultado = simulador.rodar()

    assert resultado.limpo is True
    assert resultado.celulas_limpas == resultado.total_sujos


def test_medida_a_soma_limpos():
    medida = MedidaA()
    medida.passo(5, 1)
    medida.passo(6, 0)
    assert medida.total == 11


def test_medida_b_penaliza_movimentos():
    medida = MedidaB()
    medida.passo(5, 2)
    medida.passo(5, 1)
    assert medida.total == 7
    assert medida.movimentos == 3


def test_simulador_consistente_e_reprodutivel():
    a = Simulador(
        Ambiente(8, 8, 0.4, 0.15, seed=99), AgenteReativoSimples(seed=99), T=200
    ).rodar()
    b = Simulador(
        Ambiente(8, 8, 0.4, 0.15, seed=99), AgenteReativoSimples(seed=99), T=200
    ).rodar()

    assert a.score_b == a.score_a - a.movimentos
    assert a.passos == 200
    assert a.acoes == b.acoes
    assert a.score_a == b.score_a


def test_modelo_nao_pior_que_reativo():
    m = Simulador(
        Ambiente(8, 8, 0.4, 0.15, seed=123), AgenteBaseadoEmModelo(seed=123), T=500
    ).rodar()
    r = Simulador(
        Ambiente(8, 8, 0.4, 0.15, seed=123), AgenteReativoSimples(seed=123), T=500
    ).rodar()
    assert m.score_a >= r.score_a


def test_t_fixo_mantem_passos_mesmo_limpo():
    resultado = Simulador(
        Ambiente(4, 4, 0.5, 0.0, seed=3),
        AgenteBaseadoEmModelo(seed=3),
        T=300,
    ).rodar()
    assert resultado.limpo is True
    assert resultado.passos == 300
    assert resultado.passos_ate_limpo is not None
    assert resultado.passos_ate_limpo < 300
    assert resultado.percentual_limpo == 100.0


def test_parar_quando_limpo_encerra_antes_de_t():
    resultado = Simulador(
        Ambiente(4, 4, 0.5, 0.0, seed=3),
        AgenteBaseadoEmModelo(seed=3),
        T=300,
        parar_quando_limpo=True,
    ).rodar()
    assert resultado.limpo is True
    assert resultado.passos < 300
    assert resultado.passos == resultado.passos_ate_limpo
    assert resultado.movimentos_ate_limpo == resultado.movimentos


def test_ambiente_sem_sujeira():
    resultado = Simulador(
        Ambiente(3, 3, 0.0, 0.0, seed=0),
        AgenteBaseadoEmModelo(seed=0),
        T=50,
        parar_quando_limpo=True,
    ).rodar()
    assert resultado.passos == 0
    assert resultado.passos_ate_limpo == 0
    assert resultado.movimentos_ate_limpo == 0
    assert resultado.percentual_limpo == 100.0
