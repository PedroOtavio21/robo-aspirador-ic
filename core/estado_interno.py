"""Estado interno do agente baseado em modelos: uma MATRIZ com a mesma
cobertura do mapa.

O agente nao conhece a extensao real do ambiente, portanto a matriz e
alocada com uma CAPACIDADE MAXIMA fixa, com a origem (0, 0) no centro. A
posicao (0, 0) corresponde ao ponto de partida do agente.

Valores possiveis de cada posicao (secao 7.1 do planejamento):
    0 -> NADA            (desconhecido)
    1 -> PASSADO         (visitado, ja estava limpo)
    2 -> SUJO            (conhecido sujo, ainda nao limpo)
    3 -> PASSADO_LIMPO   (visitado e a sujeira foi removida)
    4 -> BARREIRA        (obstaculo ou limite do ambiente)
"""

from __future__ import annotations

from core.ambiente import MOVIMENTOS, Acao, DELTA
from core.sensores import Percepcao

NADA = 0
PASSADO = 1
SUJO = 2
PASSADO_LIMPO = 3
BARREIRA = 4

CAPACIDADE_PADRAO = 41


class EstadoInterno:
    """Matriz 0-4 e logica de atualizacao/consulta do agente."""

    def __init__(self, capacidade: int = CAPACIDADE_PADRAO) -> None:
        self.capacidade = capacidade
        self.offset = capacidade // 2
        self.reset()

    def reset(self) -> None:
        self.matriz = [
            [NADA] * self.capacidade for _ in range(self.capacidade)
        ]
        self.posicao = (0, 0)
        self._ultima = None

    # ------------------------------------------------------------- indice/valor
    def _indice(self, pos: tuple[int, int]) -> tuple[int, int] | None:
        i = pos[0] + self.offset
        j = pos[1] + self.offset
        if 0 <= i < self.capacidade and 0 <= j < self.capacidade:
            return i, j
        return None

    def valor(self, pos: tuple[int, int]) -> int:
        idx = self._indice(pos)
        if idx is None:
            return BARREIRA
        return self.matriz[idx[0]][idx[1]]

    def marcar(self, pos: tuple[int, int], valor: int) -> None:
        idx = self._indice(pos)
        if idx is None:
            return
        self.matriz[idx[0]][idx[1]] = valor

    # ------------------------------------------------------------- atualizacao
    def atualizar(self, percepcao: Percepcao, acao_anterior: Acao | None) -> None:
        """Incorpora a percepcao (resultado da acao anterior) a matriz."""
        pos_anterior = self.posicao
        self.posicao = percepcao.posicao

        if acao_anterior in MOVIMENTOS and percepcao.bateu:
            dx, dy = DELTA[acao_anterior]
            self.marcar((pos_anterior[0] + dx, pos_anterior[1] + dy), BARREIRA)

        if percepcao.sujo:
            self.marcar(self.posicao, SUJO)
        elif acao_anterior is Acao.ASPIRAR:
            self.marcar(self.posicao, PASSADO_LIMPO)
        elif self.valor(self.posicao) == NADA:
            self.marcar(self.posicao, PASSADO)

        for dx, dy, sujo, obstaculo in percepcao.vizinhanca:
            alvo = (self.posicao[0] + dx, self.posicao[1] + dy)
            if obstaculo:
                self.marcar(alvo, BARREIRA)
            elif sujo and self.valor(alvo) not in (PASSADO, PASSADO_LIMPO):
                self.marcar(alvo, SUJO)

    # --------------------------------------------------------------- consultas
    def vizinhos(self, pos: tuple[int, int]):
        for dx, dy in DELTA.values():
            vizinho = (pos[0] + dx, pos[1] + dy)
            if self._indice(vizinho) is not None:
                yield vizinho

    def passavel(self, pos: tuple[int, int]) -> bool:
        return self.valor(pos) in (PASSADO, SUJO, PASSADO_LIMPO)

    def visitadas(self) -> set:
        celulas = set()
        for i in range(self.capacidade):
            for j in range(self.capacidade):
                if self.matriz[i][j] in (PASSADO, SUJO, PASSADO_LIMPO):
                    celulas.add((i - self.offset, j - self.offset))
        return celulas

    def sujos_conhecidos(self) -> set:
        celulas = set()
        for i in range(self.capacidade):
            for j in range(self.capacidade):
                if self.matriz[i][j] == SUJO:
                    celulas.add((i - self.offset, j - self.offset))
        return celulas

    def fronteira(self) -> set:
        """Celulas desconhecidas adjacentes a alguma celula conhecida."""
        fronteira = set()
        for x, y in self.visitadas():
            for dx, dy in DELTA.values():
                vizinho = (x + dx, y + dy)
                if self._indice(vizinho) is None:
                    continue
                if self.valor(vizinho) == NADA:
                    fronteira.add(vizinho)
        return fronteira

    def limites(self) -> tuple[int, int, int, int]:
        """Caixa (minx, miny, maxx, maxy) das celulas conhecidas."""
        celulas = set(self.visitadas()) | self.sujos_conhecidos()
        celulas.add(self.posicao)
        for i in range(self.capacidade):
            for j in range(self.capacidade):
                if self.matriz[i][j] == BARREIRA:
                    celulas.add((i - self.offset, j - self.offset))
        xs = [c[0] for c in celulas]
        ys = [c[1] for c in celulas]
        return min(xs), min(ys), max(xs), max(ys)
