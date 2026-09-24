"""Ambiente de grade para o mundo do aspirador de po.

Estados de celula:
    LIVRE (0)      -> celula livre e limpa
    SUJO (1)       -> celula livre com sujeira
    OBSTACULO (2)  -> celula bloqueada

Propriedades (secao 3.2 do planejamento):
    * Deterministico: mesma acao + mesmo estado -> mesmo resultado.
    * Parcialmente observavel: o ambiente nunca entrega o mapa completo.
    * Desconhecido inicialmente: geografia e sujeira nao sao informadas.
    * Dinamico: o estado muda conforme o agente age.

Regras acordadas:
    * Toda tentativa de movimento conta como movimento (inclusive batida).
    * Obstaculos nao entram na contagem de quadrados limpos.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum

LIVRE = 0
SUJO = 1
OBSTACULO = 2

_DELTAS = {
    "cima": (-1, 0),
    "baixo": (1, 0),
    "esquerda": (0, -1),
    "direita": (0, 1),
}


class Acao(Enum):
    CIMA = "cima"
    BAIXO = "baixo"
    ESQUERDA = "esquerda"
    DIREITA = "direita"
    ASPIRAR = "aspirar"
    NOOP = "noop"


MOVIMENTOS = (Acao.CIMA, Acao.BAIXO, Acao.ESQUERDA, Acao.DIREITA)

DELTA = {
    Acao.CIMA: (-1, 0),
    Acao.BAIXO: (1, 0),
    Acao.ESQUERDA: (0, -1),
    Acao.DIREITA: (0, 1),
}


@dataclass(frozen=True)
class Config:
    """Configuracao completa e reproduzivel de um cenario."""

    config_id: int
    seed: int
    largura: int
    altura: int
    densidade_sujeira: float
    densidade_obstaculo: float
    posicao_inicial: tuple[int, int] | None = None


class Ambiente:
    """Grade 2D com sujeira, obstaculos e a posicao do agente."""

    def __init__(
        self,
        largura: int = 8,
        altura: int = 8,
        densidade_sujeira: float = 0.4,
        densidade_obstaculo: float = 0.15,
        seed: int = 0,
        posicao_inicial: tuple[int, int] | None = None,
    ) -> None:
        self.largura = largura
        self.altura = altura
        self.densidade_sujeira = densidade_sujeira
        self.densidade_obstaculo = densidade_obstaculo
        self.seed = seed
        self.posicao_inicial = posicao_inicial
        self.reset(seed, posicao_inicial)

    # ------------------------------------------------------------------ setup
    def reset(
        self,
        seed: int | None = None,
        posicao_inicial: tuple[int, int] | None = None,
    ) -> None:
        if seed is not None:
            self.seed = seed
        if posicao_inicial is not None:
            self.posicao_inicial = posicao_inicial
        self.movimentos = 0
        self.limpas = 0
        self._gerar()

    def _gerar(self) -> None:
        """Sorteia um mapa cujas celulas livres sejam todas conectadas.

        Reamostra com um deslocamento de seed enquanto o flood fill a partir
        da posicao inicial nao alcancar todas as celulas livres. A posicao
        inicial, quando informada, e respeitada (a celula nunca e obstaculo).
        """
        for tentativa in range(500):
            rng = random.Random(self.seed + tentativa * 7919)
            grade = [[LIVRE] * self.altura for _ in range(self.largura)]

            for x in range(self.largura):
                for y in range(self.altura):
                    if rng.random() < self.densidade_obstaculo:
                        grade[x][y] = OBSTACULO

            livres = [
                (x, y)
                for x in range(self.largura)
                for y in range(self.altura)
                if grade[x][y] == LIVRE
            ]
            if not livres:
                continue

            if self.posicao_inicial is None:
                posicao = rng.choice(livres)
            else:
                posicao = self.posicao_inicial
                if not self._dentro(*posicao) or grade[posicao[0]][posicao[1]] != LIVRE:
                    continue

            for x, y in livres:
                if rng.random() < self.densidade_sujeira:
                    grade[x][y] = SUJO

            if len(self._alcancaveis(grade, posicao)) == len(livres):
                self.grade = grade
                self.posicao = posicao
                self.celulas_livres = len(livres)
                self.sujos_iniciais = sum(
                    1 for x, y in livres if grade[x][y] == SUJO
                )
                return

        raise RuntimeError(
            "Nao foi possivel gerar uma grade conectada com esses parametros."
        )

    def _alcancaveis(self, grade, inicio):
        """Flood fill (BFS) das celulas nao-obstaculo alcancaveis."""
        visitados = {inicio}
        fila = [inicio]
        while fila:
            x, y = fila.pop(0)
            for dx, dy in _DELTAS.values():
                nx, ny = x + dx, y + dy
                if not self._dentro(nx, ny):
                    continue
                if (nx, ny) in visitados or grade[nx][ny] == OBSTACULO:
                    continue
                visitados.add((nx, ny))
                fila.append((nx, ny))
        return visitados

    # ---------------------------------------------------------------- consultas
    def dentro(self, x: int, y: int) -> bool:
        return self._dentro(x, y)

    def _dentro(self, x: int, y: int) -> bool:
        return 0 <= x < self.largura and 0 <= y < self.altura

    def celula(self, x: int, y: int) -> int:
        return self.grade[x][y]

    def quadrados_limpos(self) -> int:
        """Celulas livres e sem sujeira no período atual (Medida A)."""
        return sum(
            1
            for x in range(self.largura)
            for y in range(self.altura)
            if self.grade[x][y] == LIVRE
        )

    def limpo(self) -> bool:
        """True quando nao ha mais sujeira em nenhuma celula livre."""
        return all(
            self.grade[x][y] != SUJO
            for x in range(self.largura)
            for y in range(self.altura)
        )

    def copia_grade(self):
        return [linha[:] for linha in self.grade]

    def mapa_inicial_str(self) -> str:
        """Representacao textual do mapa inicial para o registro dos dados."""
        simbolos = {LIVRE: ".", SUJO: "s", OBSTACULO: "#"}
        return "/".join(
            "".join(simbolos[self.grade[x][y]] for x in range(self.largura))
            for y in range(self.altura)
        )

    def __str__(self) -> str:
        simbolos = {LIVRE: ".", SUJO: "s", OBSTACULO: "#"}
        linhas = []
        for y in range(self.altura):
            linha = []
            for x in range(self.largura):
                if (x, y) == self.posicao:
                    linha.append("A")
                else:
                    linha.append(simbolos[self.grade[x][y]])
            linhas.append("".join(linha))
        return "\n".join(linhas)
