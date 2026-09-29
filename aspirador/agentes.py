from __future__ import annotations

import random
from collections import deque

from .ambiente import DELTA, MOVIMENTOS, Acao, Percepcao

NADA = 0
PASSADO = 1
SUJO = 2
PASSADO_LIMPO = 3
BARREIRA = 4

CAPACIDADE_PADRAO = 41

_DELTA_POR_PASSO = {v: k for k, v in DELTA.items()}


class EstadoInterno:
    def __init__(self, capacidade: int = CAPACIDADE_PADRAO) -> None:
        self.capacidade = capacidade
        self.offset = capacidade // 2
        self.reset()

    def reset(self) -> None:
        self.matriz = [[NADA] * self.capacidade for _ in range(self.capacidade)]
        self.posicao = (0, 0)
        self._ultima = None

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

    def atualizar(
        self,
        percepcao: Percepcao,
        acao_anterior: Acao | None,
        vizinhanca: bool = True,
    ) -> None:
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

        if not vizinhanca:
            return

        for dx, dy, sujo, obstaculo in percepcao.vizinhanca:
            alvo = (self.posicao[0] + dx, self.posicao[1] + dy)
            if obstaculo:
                self.marcar(alvo, BARREIRA)
            elif sujo and self.valor(alvo) not in (PASSADO, PASSADO_LIMPO):
                self.marcar(alvo, SUJO)

    def vizinhos(self, pos: tuple[int, int]):
        for dx, dy in DELTA.values():
            vizinho = (pos[0] + dx, pos[1] + dy)
            if self._indice(vizinho) is not None:
                yield vizinho

    def passavel(self, pos: tuple[int, int]) -> bool:
        return self.valor(pos) in (PASSADO, SUJO, PASSADO_LIMPO)

    def visitadas(self) -> set:
        return {
            (i - self.offset, j - self.offset)
            for i in range(self.capacidade)
            for j in range(self.capacidade)
            if self.matriz[i][j] in (PASSADO, SUJO, PASSADO_LIMPO)
        }

    def sujos_conhecidos(self) -> set:
        return {
            (i - self.offset, j - self.offset)
            for i in range(self.capacidade)
            for j in range(self.capacidade)
            if self.matriz[i][j] == SUJO
        }

    def fronteira(self) -> set:
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
        celulas = set(self.visitadas()) | self.sujos_conhecidos()
        celulas.add(self.posicao)
        for i in range(self.capacidade):
            for j in range(self.capacidade):
                if self.matriz[i][j] == BARREIRA:
                    celulas.add((i - self.offset, j - self.offset))
        xs = [c[0] for c in celulas]
        ys = [c[1] for c in celulas]
        return min(xs), min(ys), max(xs), max(ys)


class Agente:
    nome = "agente"

    def agir(self, percepcao: Percepcao) -> Acao:
        raise NotImplementedError

    def reset(self, seed: int | None = None) -> None:
        pass

    def mapa_interno(self):
        return None

    def descricao_memoria(self) -> str | None:
        return None


class AgenteReativoSimples(Agente):
    nome = "Reativo simples"

    def __init__(self, seed: int = 0) -> None:
        self.seed = seed
        self._rng = random.Random(seed)

    def reset(self, seed: int | None = None) -> None:
        if seed is not None:
            self.seed = seed
        self._rng = random.Random(self.seed)

    def agir(self, percepcao: Percepcao) -> Acao:
        if percepcao.sujo:
            return Acao.ASPIRAR
        return self._rng.choice(MOVIMENTOS)


class AgenteBaseadoEmModelo(Agente):
    nome = "Baseado em modelo"

    def __init__(
        self,
        seed: int = 0,
        capacidade: int = CAPACIDADE_PADRAO,
        memoria: str = "mapa",
    ) -> None:
        if memoria not in ("mapa", "posicao", "hibrida"):
            raise ValueError(f"Memoria invalida: {memoria!r}")
        self.seed = seed
        self.memoria = memoria
        self.estado = EstadoInterno(capacidade)
        self.reset(seed)

    def reset(self, seed: int | None = None) -> None:
        if seed is not None:
            self.seed = seed
        self._rng = random.Random(self.seed)
        self.estado.reset()
        self._acao_anterior: Acao | None = None
        self._posicao = (0, 0)
        self._posicao_anterior: tuple[int, int] | None = None

    def agir(self, percepcao: Percepcao) -> Acao:
        if self.memoria == "posicao":
            acao = self._agir_posicao(percepcao)
        elif self.memoria == "hibrida":
            self.estado.atualizar(percepcao, self._acao_anterior, vizinhanca=False)
            acao = self._decidir_hibrida(percepcao)
        else:
            self.estado.atualizar(percepcao, self._acao_anterior)
            acao = self._decidir(percepcao)
        self._acao_anterior = acao
        return acao

    def _agir_posicao(self, percepcao: Percepcao) -> Acao:
        self._posicao_anterior = self._posicao
        self._posicao = percepcao.posicao
        if percepcao.sujo:
            return Acao.ASPIRAR
        return self._movimento_sem_retrocesso(percepcao)

    def _movimento_sem_retrocesso(self, percepcao: Percepcao) -> Acao:
        atual = self._posicao
        anterior = self._posicao_anterior
        volta = None
        if anterior is not None:
            volta = _DELTA_POR_PASSO.get(
                (anterior[0] - atual[0], anterior[1] - atual[1])
            )
        candidatos = [m for m in MOVIMENTOS if m is not volta]
        if not candidatos or percepcao.bateu:
            candidatos = list(MOVIMENTOS)
        return self._rng.choice(candidatos)

    def _decidir_hibrida(self, percepcao: Percepcao) -> Acao:
        if percepcao.sujo:
            return Acao.ASPIRAR

        atual = self.estado.posicao
        obstaculos = {
            (atual[0] + dx, atual[1] + dy)
            for dx, dy, _sujo, obstaculo in percepcao.vizinhanca
            if obstaculo
        }

        novos: list[Acao] = []
        revisitar: list[Acao] = []
        for movimento in MOVIMENTOS:
            dx, dy = DELTA[movimento]
            destino = (atual[0] + dx, atual[1] + dy)
            if destino in obstaculos or self.estado.valor(destino) == BARREIRA:
                continue
            if self.estado.valor(destino) == NADA:
                novos.append(movimento)
            else:
                revisitar.append(movimento)

        opcoes = novos or revisitar or list(MOVIMENTOS)
        return self._rng.choice(opcoes)

    def _decidir(self, percepcao: Percepcao) -> Acao:
        if percepcao.sujo:
            return Acao.ASPIRAR

        alvos = self.estado.sujos_conhecidos()
        alvos.discard(self.estado.posicao)
        proximo = self._bfs(alvos) if alvos else None
        if proximo is None:
            proximo = self._bfs(self.estado.fronteira())
        if proximo is None:
            return Acao.NOOP

        dx = proximo[0] - self.estado.posicao[0]
        dy = proximo[1] - self.estado.posicao[1]
        return _DELTA_POR_PASSO[(dx, dy)]

    def _bfs(self, alvos: set) -> tuple[int, int] | None:
        if not alvos:
            return None
        fila = deque([(self.estado.posicao, None)])
        vistos = {self.estado.posicao}
        while fila:
            atual, primeiro = fila.popleft()
            for vizinho in self.estado.vizinhos(atual):
                if vizinho in alvos:
                    return primeiro or vizinho
                if vizinho in vistos:
                    continue
                if self.estado.passavel(vizinho):
                    vistos.add(vizinho)
                    fila.append((vizinho, primeiro or vizinho))
        return None

    def mapa_interno(self):
        if self.memoria == "posicao":
            return None
        return self.estado

    def descricao_memoria(self) -> str | None:
        if self.memoria != "posicao":
            return None
        return (
            "Memória: apenas a posição atual\n"
            f"atual: {self._posicao}\n"
            f"anterior: {self._posicao_anterior}"
        )


AGENTES = {
    AgenteReativoSimples.nome: AgenteReativoSimples,
    AgenteBaseadoEmModelo.nome: AgenteBaseadoEmModelo,
}
