from __future__ import annotations

from dataclasses import dataclass, field

from .agentes import Agente
from .ambiente import RAIO_PADRAO, Ambiente, Sensor, aplicar


@dataclass
class Medida:
    nome: str
    total: float = 0.0
    historico: list = field(default_factory=list)

    def passo(self, quadrados_limpos: int, movimentos: int) -> None:
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


@dataclass
class Resultado:
    score_a: float
    score_b: float
    movimentos: int
    passos: int
    celulas_limpas: int
    total_sujos: int
    limpo: bool
    passos_ate_limpo: int | None = None
    movimentos_ate_limpo: int | None = None
    percentual_limpo: float = 0.0
    acoes: list = field(default_factory=list)
    historico_limpos: list = field(default_factory=list)
    historico_a: list = field(default_factory=list)
    historico_b: list = field(default_factory=list)

    def linha(self) -> str:
        return (
            f"Passos: {self.passos} | A: {self.score_a:.1f} | "
            f"B: {self.score_b:.1f} | Movimentos: {self.movimentos}"
        )


class Simulador:
    def __init__(
        self,
        ambiente: Ambiente,
        agente: Agente,
        T: int = 500,
        raio_sensor: int = RAIO_PADRAO,
        parar_quando_limpo: bool = False,
    ) -> None:
        self.ambiente = ambiente
        self.agente = agente
        self.T = T
        self.parar_quando_limpo = parar_quando_limpo
        self.sensor = Sensor(raio_sensor)
        self.reset()

    def reset(self) -> None:
        self.ambiente.reset()
        self.agente.reset()
        self.sensor.reset(self.ambiente.posicao)
        self.percepcao = self.sensor.perceber(self.ambiente, bateu=False)
        self.medida_a = MedidaA()
        self.medida_b = MedidaB()
        self.passos = 0
        self.acoes: list[str] = []
        self.historico_limpos: list[int] = []
        self.terminado = False
        self.passos_ate_limpo: int | None = None
        self.movimentos_ate_limpo: int | None = None
        if self.ambiente.limpo():
            self.passos_ate_limpo = 0
            self.movimentos_ate_limpo = 0
            if self.parar_quando_limpo:
                self.terminado = True

    def passo(self) -> None:
        if self.terminado:
            return

        acao = self.agente.agir(self.percepcao)
        movimentos_antes = self.ambiente.movimentos
        bateu = aplicar(self.ambiente, acao)
        movimentos_delta = self.ambiente.movimentos - movimentos_antes
        self.percepcao = self.sensor.perceber(self.ambiente, bateu=bateu)

        self.passos += 1
        self.acoes.append(acao.value)
        limpos = self.ambiente.quadrados_limpos()
        self.medida_a.passo(limpos, movimentos_delta)
        self.medida_b.passo(limpos, movimentos_delta)
        self.historico_limpos.append(self.ambiente.limpas)

        if self.passos_ate_limpo is None and self.ambiente.limpo():
            self.passos_ate_limpo = self.passos
            self.movimentos_ate_limpo = self.ambiente.movimentos

        if self.passos >= self.T or (
            self.parar_quando_limpo and self.ambiente.limpo()
        ):
            self.terminado = True

    def resultado(self) -> Resultado:
        if self.ambiente.sujos_iniciais:
            percentual = 100.0 * self.ambiente.limpas / self.ambiente.sujos_iniciais
        else:
            percentual = 100.0
        return Resultado(
            score_a=self.medida_a.total,
            score_b=self.medida_b.total,
            movimentos=self.ambiente.movimentos,
            passos=self.passos,
            celulas_limpas=self.ambiente.limpas,
            total_sujos=self.ambiente.sujos_iniciais,
            limpo=self.ambiente.limpo(),
            passos_ate_limpo=self.passos_ate_limpo,
            movimentos_ate_limpo=self.movimentos_ate_limpo,
            percentual_limpo=percentual,
            acoes=list(self.acoes),
            historico_limpos=list(self.historico_limpos),
            historico_a=list(self.medida_a.historico),
            historico_b=list(self.medida_b.historico),
        )

    def rodar(self, T: int | None = None) -> Resultado:
        if T is not None:
            self.T = T
        while not self.terminado:
            self.passo()
        return self.resultado()
