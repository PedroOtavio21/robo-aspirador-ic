"""Janela principal (Tkinter) do simulador do aspirador de po."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from core.agentes import AGENTES
from core.ambiente import Ambiente
from core.simulador import Simulador
from gui.widget_grade import GradeCanvas
from gui.widget_resultados import WidgetResultados

LARGURA, ALTURA = 8, 8
DENSIDADE_SUJEIRA, DENSIDADE_OBSTACULO = 0.4, 0.15
T_PADRAO = 500
INTERVALO_PADRAO = 200


class JanelaPrincipal(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Aspirador de pó — Inteligência Computacional")
        self.minsize(760, 560)

        self.simulador: Simulador | None = None
        self._tocando = False
        self._after_id: str | None = None
        self._intervalo = INTERVALO_PADRAO

        self._montar()
        self.protocol("WM_DELETE_WINDOW", self._fechar)
        self.novo()

    # ------------------------------------------------------------------ layout
    def _montar(self) -> None:
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        self.aba_simulacao = ttk.Frame(notebook)
        self.aba_resultados = WidgetResultados(notebook)
        notebook.add(self.aba_simulacao, text="Simulação")
        notebook.add(self.aba_resultados, text="Resultados")

        self._montar_controles()
        self._montar_grades()

    def _montar_controles(self) -> None:
        barra = ttk.Frame(self.aba_simulacao, padding=8)
        barra.pack(fill="x")

        ttk.Label(barra, text="Agente:").pack(side="left")
        self.combo_agente = ttk.Combobox(
            barra, values=list(AGENTES), state="readonly", width=18
        )
        self.combo_agente.current(0)
        self.combo_agente.pack(side="left", padx=(4, 12))

        ttk.Label(barra, text="Seed:").pack(side="left")
        self.entrada_seed = ttk.Entry(barra, width=8)
        self.entrada_seed.insert(0, "0")
        self.entrada_seed.pack(side="left", padx=(4, 12))

        ttk.Button(barra, text="Novo", command=self.novo).pack(side="left", padx=2)
        ttk.Button(barra, text="Passo", command=self.passo).pack(side="left", padx=2)
        self.botao_play = ttk.Button(barra, text="Play", command=self.alternar_play)
        self.botao_play.pack(side="left", padx=2)

        ttk.Label(barra, text="Velocidade:").pack(side="left", padx=(16, 4))
        self.escala = ttk.Scale(
            barra,
            from_=10,
            to=1000,
            orient="horizontal",
            length=160,
            command=self._mudar_velocidade,
        )
        self.escala.set(INTERVALO_PADRAO)
        self.escala.pack(side="left")

        self.placar = tk.StringVar()
        ttk.Label(
            self.aba_simulacao,
            textvariable=self.placar,
            padding=(8, 4),
            font=("TkDefaultFont", 10, "bold"),
        ).pack(fill="x")

    def _montar_grades(self) -> None:
        area = ttk.Frame(self.aba_simulacao, padding=8)
        area.pack(fill="both", expand=True)

        moldura_esq = ttk.LabelFrame(area, text="Ambiente", padding=6)
        moldura_esq.pack(side="left", fill="both", expand=True, padx=(0, 6))
        self.canvas_ambiente = GradeCanvas(moldura_esq)
        self.canvas_ambiente.pack()

        moldura_dir = ttk.LabelFrame(area, text="Mapa interno do agente", padding=6)
        moldura_dir.pack(side="left", fill="both", expand=True)
        self.canvas_mapa = GradeCanvas(moldura_dir)
        self.canvas_mapa.pack()

    # ------------------------------------------------------------------ acoes
    def _seed(self) -> int:
        try:
            return int(self.entrada_seed.get())
        except ValueError:
            self.entrada_seed.delete(0, "end")
            self.entrada_seed.insert(0, "0")
            return 0

    def novo(self) -> None:
        self.parar_play()
        seed = self._seed()
        ambiente = Ambiente(
            LARGURA, ALTURA, DENSIDADE_SUJEIRA, DENSIDADE_OBSTACULO, seed=seed
        )
        classe = AGENTES[self.combo_agente.get()]
        agente = classe(seed=seed)
        self.simulador = Simulador(ambiente, agente, T=T_PADRAO)
        self._atualizar()

    def passo(self) -> None:
        if self.simulador is None or self.simulador.terminado:
            return
        self.simulador.passo()
        self._atualizar()
        if self.simulador.terminado:
            self.parar_play()

    def alternar_play(self) -> None:
        if self._tocando:
            self.parar_play()
        elif self.simulador is not None and not self.simulador.terminado:
            self._tocando = True
            self.botao_play.config(text="Pause")
            self._tick()

    def parar_play(self) -> None:
        self._tocando = False
        if self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None
        self.botao_play.config(text="Play")

    def _tick(self) -> None:
        self._after_id = None
        if not self._tocando:
            return
        self.passo()
        if self._tocando and self.simulador is not None and not self.simulador.terminado:
            self._after_id = self.after(self._intervalo, self._tick)
        else:
            self.parar_play()

    def _mudar_velocidade(self, valor: str) -> None:
        self._intervalo = max(1, int(float(valor)))

    def _atualizar(self) -> None:
        if self.simulador is None:
            return
        ambiente = self.simulador.ambiente
        self.canvas_ambiente.mostrar_ambiente(ambiente)
        self.canvas_mapa.mostrar_mapa(self.simulador.agente.mapa_interno())

        resultado = self.simulador.resultado()
        if self.simulador.terminado:
            status = f"fim ({self.simulador.T} períodos)"
        elif resultado.limpo:
            status = "ambiente limpo"
        else:
            status = "em execução"
        self.placar.set(
            f"Passo: {self.simulador.passos}/{self.simulador.T}    "
            f"Medida A: {resultado.score_a:.0f}    "
            f"Medida B: {resultado.score_b:.0f}    "
            f"Movimentos: {resultado.movimentos}    [{status}]"
        )

    def _fechar(self) -> None:
        self.parar_play()
        self.destroy()
