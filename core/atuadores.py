"""Atuadores: aplicam a acao escolhida pelo agente ao ambiente real.

Regra de movimento (secao 5 e 10.3 do planejamento):
    * Toda tentativa de movimento conta como movimento, inclusive quando
      bate em parede/obstaculo.
    * ASPIRAR e NOOP nao contam como movimento.
A regra e identica para os dois agentes.
"""

from __future__ import annotations

from core.ambiente import LIVRE, MOVIMENTOS, OBSTACULO, SUJO, Acao, Ambiente, DELTA


def aplicar(ambiente: Ambiente, acao: Acao) -> bool:
    """Aplica a acao e devolve True se houve batida (movimento invalido)."""
    if acao in MOVIMENTOS:
        dx, dy = DELTA[acao]
        nx, ny = ambiente.posicao[0] + dx, ambiente.posicao[1] + dy
        ambiente.movimentos += 1
        if ambiente.dentro(nx, ny) and ambiente.celula(nx, ny) != OBSTACULO:
            ambiente.posicao = (nx, ny)
            return False
        return True

    if acao is Acao.ASPIRAR:
        x, y = ambiente.posicao
        if ambiente.celula(x, y) == SUJO:
            ambiente.grade[x][y] = LIVRE
            ambiente.limpas += 1
        return False

    if acao is Acao.NOOP:
        return False

    raise ValueError(f"Acao invalida: {acao!r}")
