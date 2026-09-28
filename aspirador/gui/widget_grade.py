from __future__ import annotations

import tkinter as tk
from pathlib import Path

from ..agentes import BARREIRA, NADA, PASSADO, PASSADO_LIMPO
from ..agentes import SUJO as SUJO_INTERNO
from ..ambiente import LIVRE, OBSTACULO, SUJO

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
    SUJO_INTERNO: "#c98a3b",
    PASSADO_LIMPO: "#a8e6a1",
    BARREIRA: "#4a4a4a",
}
LEGENDA = {
    NADA: "0 nada",
    PASSADO: "1 passado",
    SUJO_INTERNO: "2 sujo",
    PASSADO_LIMPO: "3 passado/limpo",
    BARREIRA: "4 barreira",
}

MAX_PX = 560


class GradeCanvas(tk.Canvas):
    def __init__(self, master, tamanho_celula: int = 28, **kw) -> None:
        super().__init__(
            master,
            highlightthickness=1,
            highlightbackground="#888888",
            **kw,
        )
        self.tamanho_celula = tamanho_celula
        self._t = tamanho_celula
        self.imagem_robo = self._carregar_imagem_robo()

    def _carregar_imagem_robo(self) -> tk.PhotoImage | None:
        caminho_imagem = Path(__file__).resolve().parents[2] / "img" / "robo.png"
        try:
            imagem_original = tk.PhotoImage(file=str(caminho_imagem))
        except tk.TclError:
            return None

        fator_x = max(1, imagem_original.width() // self.tamanho_celula)
        fator_y = max(1, imagem_original.height() // self.tamanho_celula)
        fator = max(fator_x, fator_y)
        return imagem_original.subsample(fator, fator)

    def _tamanho(self, largura: int, altura: int) -> int:
        return max(4, min(self.tamanho_celula, MAX_PX // max(largura, altura, 1)))

    def mostrar_ambiente(self, ambiente) -> None:
        self.delete("all")
        self._t = self._tamanho(ambiente.largura, ambiente.altura)
        self._redimensionar(ambiente.largura, ambiente.altura)
        for x in range(ambiente.largura):
            for y in range(ambiente.altura):
                self._celula(x, y, CORES_CELULA[ambiente.grade[x][y]])
        ax, ay = ambiente.posicao
        self._agente(ax, ay)

    def mostrar_mapa(self, estado) -> None:
        self.delete("all")
        if estado is None:
            self._t = self.tamanho_celula
            self._redimensionar(6, 3)
            self.create_text(
                12,
                12,
                anchor="nw",
                text="Este agente não mantém estado interno.",
                fill="#555555",
            )
            return

        minx, miny, maxx, maxy = estado.limites()
        largura = maxx - minx + 1
        altura = maxy - miny + 1
        self._t = self._tamanho(largura, altura)
        self._redimensionar(largura, altura)

        for x in range(minx, maxx + 1):
            for y in range(miny, maxy + 1):
                cor = CORES_ESTADO.get(estado.valor((x, y)), CORES_ESTADO[NADA])
                self._celula(x - minx, y - miny, cor)

        ax, ay = estado.posicao
        self._agente(ax - minx, ay - miny)

    def mostrar_mensagem(self, texto: str) -> None:
        self.delete("all")
        self._t = self.tamanho_celula
        self._redimensionar(8, 4)
        self.create_text(12, 12, anchor="nw", text=texto, fill="#555555")

    def _redimensionar(self, largura: int, altura: int) -> None:
        self.configure(width=largura * self._t, height=altura * self._t)

    def _celula(self, x: int, y: int, cor: str) -> None:
        self._celula_px(x * self._t, y * self._t, cor)

    def _celula_px(self, x0: int, y0: int, cor: str) -> None:
        self.create_rectangle(
            x0, y0, x0 + self._t, y0 + self._t, fill=cor, outline=COR_GRADE
        )

    def _agente(self, x: int, y: int) -> None:
        t = self._t
        if self.imagem_robo is None:
            x0, y0 = x * t, y * t
            margem = t * 0.18
            self.create_oval(
                x0 + margem,
                y0 + margem,
                x0 + t - margem,
                y0 + t - margem,
                fill=COR_AGENTE,
                outline="",
            )
            return
        self.create_image(
            x * t + t / 2,
            y * t + t / 2,
            image=self.imagem_robo,
            anchor="center",
        )
