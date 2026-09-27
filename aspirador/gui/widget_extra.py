from __future__ import annotations

import os
from tkinter import ttk

import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from ..experimentos import montar_figura_extra


class WidgetExtra(ttk.Frame):
    def __init__(
        self,
        master,
        diretorio: str = "resultados/extra",
        diretorio_principal: str = "resultados/raw",
        **kw,
    ) -> None:
        super().__init__(master, **kw)
        self.diretorio = diretorio
        self.diretorio_principal = diretorio_principal
        self.figura = Figure(figsize=(10, 7), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figura, master=self)
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()

        ttk.Button(self, text="Atualizar gráficos", command=self.atualizar).pack(
            side="bottom", pady=4
        )
        self.atualizar()

    def _mensagem(self, texto: str) -> None:
        self.figura.clear()
        ax = self.figura.add_subplot(111)
        ax.axis("off")
        ax.text(0.5, 0.5, texto, ha="center", va="center", fontsize=12)
        self.canvas.draw()

    def atualizar(self) -> None:
        arq_stop = os.path.join(self.diretorio, "stop_raw.csv")
        arq_mem = os.path.join(self.diretorio, "memorias_raw.csv")
        arq_principal = os.path.join(self.diretorio_principal, "resultados.csv")

        if not (
            os.path.exists(arq_stop)
            and os.path.exists(arq_mem)
            and os.path.exists(arq_principal)
        ):
            self._mensagem(
                "Nenhum dado extra encontrado.\n\n"
                "Rode:  python -m aspirador --extra"
            )
            return

        df_stop = pd.read_csv(arq_stop)
        df_mem = pd.read_csv(arq_mem)
        df_principal = pd.read_csv(arq_principal)
        montar_figura_extra(df_stop, df_mem, df_principal, self.figura)
        self.canvas.draw()
