from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum

LIVRE = 0
SUJO = 1
OBSTACULO = 2

RAIO_PADRAO = 1


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

_DELTAS = tuple(DELTA.values())


@dataclass(frozen=True)
class Config:
    config_id: int
    seed: int
    largura: int
    altura: int
    densidade_sujeira: float
    densidade_obstaculo: float
    posicao_inicial: tuple[int, int] | None = None


@dataclass(frozen=True)
class Percepcao:
    sujo: bool
    bateu: bool
    posicao: tuple[int, int]
    vizinhanca: tuple[tuple[int, int, bool, bool], ...] = ()


class Ambiente:
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
                self.sujos_iniciais = sum(1 for x, y in livres if grade[x][y] == SUJO)
                return

        raise RuntimeError("Nao foi possivel gerar uma grade conectada.")

    def _alcancaveis(self, grade, inicio):
        visitados = {inicio}
        fila = [inicio]
        while fila:
            x, y = fila.pop(0)
            for dx, dy in _DELTAS:
                nx, ny = x + dx, y + dy
                if not self._dentro(nx, ny):
                    continue
                if (nx, ny) in visitados or grade[nx][ny] == OBSTACULO:
                    continue
                visitados.add((nx, ny))
                fila.append((nx, ny))
        return visitados

    def _dentro(self, x: int, y: int) -> bool:
        return 0 <= x < self.largura and 0 <= y < self.altura

    def dentro(self, x: int, y: int) -> bool:
        return self._dentro(x, y)

    def celula(self, x: int, y: int) -> int:
        return self.grade[x][y]

    def quadrados_limpos(self) -> int:
        return sum(
            1
            for x in range(self.largura)
            for y in range(self.altura)
            if self.grade[x][y] == LIVRE
        )

    def limpo(self) -> bool:
        return all(
            self.grade[x][y] != SUJO
            for x in range(self.largura)
            for y in range(self.altura)
        )

    def copia_grade(self):
        return [linha[:] for linha in self.grade]

    def mapa_inicial_str(self) -> str:
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
                linha.append("A" if (x, y) == self.posicao else simbolos[self.grade[x][y]])
            linhas.append("".join(linha))
        return "\n".join(linhas)


class Sensor:
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


def aplicar(ambiente: Ambiente, acao: Acao) -> bool:
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
