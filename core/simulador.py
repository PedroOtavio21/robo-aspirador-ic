"""Simulador: liga Ambiente + Sensor + Agente + Atuadores e calcula as medidas.

Ciclo de cada período (secao 9 do planejamento):
    percepcao -> decisao do agente -> acao -> atualizacao do ambiente ->
    calculo das medidas -> registro dos dados.

Todos os agentes e experimentos executam exatamente T períodos (mesmo numero
de periodos), condicao necessaria para comparar a Medida A com justiça.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from core import atuadores
from core.agentes import Agente
from core.ambiente import Ambiente
from core.metricas import MedidaA, MedidaB
from core.sensores import RAIO_PADRAO, Sensor


@dataclass
class Resultado:
    score_a: float
    score_b: float
    movimentos: int
    passos: int
    celulas_limpas: int
    total_sujos: int
    limpo: bool
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
    ) -> None:
        self.ambiente = ambiente
        self.agente = agente
        self.T = T
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

    def passo(self) -> None:
        if self.terminado:
            return

        acao = self.agente.agir(self.percepcao)
        movimentos_antes = self.ambiente.movimentos
        bateu = atuadores.aplicar(self.ambiente, acao)
        movimentos_delta = self.ambiente.movimentos - movimentos_antes
        self.percepcao = self.sensor.perceber(self.ambiente, bateu=bateu)

        self.passos += 1
        self.acoes.append(acao.value)
        limpos = self.ambiente.quadrados_limpos()
        self.medida_a.passo(limpos, movimentos_delta)
        self.medida_b.passo(limpos, movimentos_delta)
        self.historico_limpos.append(self.ambiente.limpas)

        if self.passos >= self.T:
            self.terminado = True

    def resultado(self) -> Resultado:
        return Resultado(
            score_a=self.medida_a.total,
            score_b=self.medida_b.total,
            movimentos=self.ambiente.movimentos,
            passos=self.passos,
            celulas_limpas=self.ambiente.limpas,
            total_sujos=self.ambiente.sujos_iniciais,
            limpo=self.ambiente.limpo(),
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
