"""Agentes para o mundo do aspirador de po.

Contrato:
    Agente.agir(percepcao) -> Acao
    Agente.reset()         -> reinicia o estado interno
    Agente.mapa_interno()  -> EstadoInterno (baseado em modelos) ou None

O agente reativo simples decide apenas com a percepcao atual e nao mantem
historico. O agente baseado em modelos mantem uma matriz de estado interno
(0-4) atualizada a cada percepcao.
"""

from __future__ import annotations

import random
from collections import deque

from core.ambiente import MOVIMENTOS, Acao, DELTA
from core.estado_interno import CAPACIDADE_PADRAO, EstadoInterno
from core.sensores import Percepcao

_DELTA_POR_PASSO = {v: k for k, v in DELTA.items()}


class Agente:
    """Interface base dos agentes."""

    nome = "agente"

    def agir(self, percepcao: Percepcao) -> Acao:  # pragma: no cover - interface
        raise NotImplementedError

    def reset(self, seed: int | None = None) -> None:
        pass

    def mapa_interno(self):
        return None


class AgenteReativoSimples(Agente):
    """Aspira se houver sujeira; caso contrario, anda aleatoriamente.

    Nao possui memoria: decide somente com a percepcao atual. A escolha
    aleatoria usa uma semente propria para permitir reproducao.
    """

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
    """Mantem um estado interno (matriz 0-4) e explora com BFS.

    Decisao:
        1. se a celula atual esta suja -> ASPIRAR;
        2. senao, vai ate o sujo conhecido mais proximo (valor 2);
        3. senao, vai ate a fronteira desconhecida mais proxima (valor 0);
        4. sem sujos conhecidos e sem fronteira -> NOOP (encerra).
    """

    nome = "Baseado em modelo"

    def __init__(self, seed: int = 0, capacidade: int = CAPACIDADE_PADRAO) -> None:
        self.seed = seed
        self.estado = EstadoInterno(capacidade)
        self.reset(seed)

    def reset(self, seed: int | None = None) -> None:
        if seed is not None:
            self.seed = seed
        self.estado.reset()
        self._acao_anterior: Acao | None = None

    # ------------------------------------------------------------------ acoes
    def agir(self, percepcao: Percepcao) -> Acao:
        self.estado.atualizar(percepcao, self._acao_anterior)
        acao = self._decidir(percepcao)
        self._acao_anterior = acao
        return acao

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
        """Primeiro passo do caminho mais curto ate uma celula de 'alvos'.

        So caminha por celulas conhecidas e passaveis. Devolve a celula
        vizinha que da o primeiro passo, ou None.
        """
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

    def mapa_interno(self) -> EstadoInterno:
        return self.estado


AGENTES = {
    AgenteReativoSimples.nome: AgenteReativoSimples,
    AgenteBaseadoEmModelo.nome: AgenteBaseadoEmModelo,
}
