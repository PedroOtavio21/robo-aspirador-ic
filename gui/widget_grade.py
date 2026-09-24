"""Canvas Tkinter que desenha uma grade (ambiente real ou mapa interno 0-4)."""

from __future__ import annotations

import tkinter as tk

from core.ambiente import LIVRE, OBSTACULO, SUJO
from core.estado_interno import (
    BARREIRA,
    NADA,
    PASSADO,
    PASSADO_LIMPO,
    SUJO as INTERNO_SUJO,
)

CORES_CELULA = {
    LIVRE: "#ffffff",
    SUJO: "#c98a3b",
    OBSTACULO: "#4a4a4a",
}
COR_GRADE = "#c8c8c8"
COR_AGENTE = "#2b6cb0"

CORES_ESTADO = {
    NADA: "#e6e6e6",
    PASSADO: "#cfe8ff",
    INTERNO_SUJO: "#c98a3b",
    PASSADO_LIMPO: "#a8e6a1",
    BARREIRA: "#4a4a4a",
}
LEGENDA = {
    NADA: "0 nada",
    PASSADO: "1 passado",
    INTERNO_SUJO: "2 sujo",
    PASSADO_LIMPO: "3 passado/limpo",
    BARREIRA: "4 barreira",
}


class GradeCanvas(tk.Canvas):
    def __init__(self, master, tamanho_celula: int = 28, **kw) -> None:
        super().__init__(
            master,
            highlightthickness=1,
            highlightbackground="#888888",
            **kw,
        )
        self.tamanho_celula = tamanho_celula

    # --------------------------------------------------------------- ambiente
    def mostrar_ambiente(self, ambiente) -> None:
        self.delete("all")
        t = self.tamanho_celula
        self._redimensionar(ambiente.largura, ambiente.altura)
        for x in range(ambiente.largura):
            for y in range(ambiente.altura):
                self._celula(x, y, CORES_CELULA[ambiente.grade[x][y]])
        ax, ay = ambiente.posicao
        self._agente(ax * t, ay * t)

    # ------------------------------------------------------------ mapa interno
    def mostrar_mapa(self, estado) -> None:
        self.delete("all")
        if estado is None:
            self._redimensionar(6, 3)
            self.create_text(
                12,
                12,
                anchor="nw",
                text="Este agente não mantém estado interno.",
                fill="#555555",
            )
            return

        t = self.tamanho_celula
        minx, miny, maxx, maxy = estado.limites()
        largura = maxx - minx + 1
        altura = maxy - miny + 1
        self._redimensionar(largura, altura)

        for x in range(minx, maxx + 1):
            for y in range(miny, maxy + 1):
                cor = CORES_ESTADO.get(estado.valor((x, y)), CORES_ESTADO[NADA])
                self._celula(x - minx, y - miny, cor)

        ax, ay = estado.posicao
        self._agente((ax - minx) * t, (ay - miny) * t)

    # ------------------------------------------------------------------ helpers
    def _redimensionar(self, largura: int, altura: int) -> None:
        t = self.tamanho_celula
        self.configure(width=largura * t, height=altura * t)

    def _celula(self, x: int, y: int, cor: str) -> None:
        t = self.tamanho_celula
        self._celula_px(x * t, y * t, cor)

    def _celula_px(self, x0: int, y0: int, cor: str) -> None:
        t = self.tamanho_celula
        self.create_rectangle(x0, y0, x0 + t, y0 + t, fill=cor, outline=COR_GRADE)

    def _agente(self, x0: int, y0: int) -> None:
        t = self.tamanho_celula
        margem = t * 0.18
        self.create_oval(
            x0 + margem,
            y0 + margem,
            x0 + t - margem,
            y0 + t - margem,
            fill=COR_AGENTE,
            outline="",
        )
