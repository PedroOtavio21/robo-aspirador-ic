"""Sensores: transformam o estado real do ambiente em percepcao local.

O agente so recebe:
    * condicao de sujeira da celula atual;
    * se a ultima acao de movimento bateu (parede/obstaculo);
    * sua posicao RELATIVA ao ponto de partida (nao revela o tamanho real);
    * a vizinhanca dentro de um alcance (raio) definido.

Nunca e entregue ao agente o mapa completo nem a extensao do ambiente.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from core.ambiente import OBSTACULO, SUJO, Ambiente

RAIO_PADRAO = 1


@dataclass(frozen=True)
class Percepcao:
    """O que o agente sente apos executar uma acao."""

    sujo: bool
    bateu: bool
    posicao: tuple[int, int]
    vizinhanca: tuple[tuple[int, int, bool, bool], ...] = field(default_factory=tuple)
    """Vizinhanca no formato (dx, dy, sujo, obstaculo)."""


class Sensor:
    """Sensor local de sujeira, obstaculos e posicao relativa."""

    def __init__(self, raio: int = RAIO_PADRAO) -> None:
        self.raio = raio
        self.origem = (0, 0)

    def reset(self, posicao_absoluta: tuple[int, int]) -> None:
        self.origem = posicao_absoluta

    def perceber(self, ambiente: Ambiente, bateu: bool = False) -> Percepcao:
        x, y = ambiente.posicao
        posicao = (x - self.origem[0], y - self.origem[1])
        sujo = ambiente.celula(x, y) == SUJO

        vizinhanca = []
        for dx in range(-self.raio, self.raio + 1):
            for dy in range(-self.raio, self.raio + 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if not ambiente.dentro(nx, ny):
                    vizinhanca.append((dx, dy, False, True))
                    continue
                valor = ambiente.celula(nx, ny)
                vizinhanca.append((dx, dy, valor == SUJO, valor == OBSTACULO))

        return Percepcao(
            sujo=sujo,
            bateu=bateu,
            posicao=posicao,
            vizinhanca=tuple(sorted(vizinhanca)),
        )
