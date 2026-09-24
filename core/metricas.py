"""Medidas de desempenho (secao 10 do planejamento).

Medida A - recompensa por limpeza:
    +1 ponto para cada quadrado limpo em cada período.
    score_A = soma, ao longo dos períodos, da quantidade de quadrados limpos.

Medida B - limpeza com penalizacao por movimento:
    +1 ponto por quadrado limpo e -1 ponto por cada movimento.
    score_B = score_A - total de movimentos.

As duas medidas sao calculadas na MESMA execucao, pois a trajetoria do
agente nao depende da medida usada (os agentes nao aprendem com recompensa).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Medida:
    nome: str
    total: float = 0.0
    historico: list = field(default_factory=list)

    def passo(self, quadrados_limpos: int, movimentos: int) -> None:  # pragma: no cover
        raise NotImplementedError

    def media(self, n: int) -> float:
        return self.total / n if n else 0.0


class MedidaA(Medida):
    def __init__(self) -> None:
        super().__init__(nome="Medida A")

    def passo(self, quadrados_limpos: int, movimentos: int) -> None:
        self.total += quadrados_limpos
        self.historico.append(self.total)


class MedidaB(Medida):
    def __init__(self) -> None:
        super().__init__(nome="Medida B")
        self.movimentos = 0

    def passo(self, quadrados_limpos: int, movimentos: int) -> None:
        self.movimentos += movimentos
        self.total += quadrados_limpos - movimentos
        self.historico.append(self.total)
