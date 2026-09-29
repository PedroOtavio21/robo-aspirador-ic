from __future__ import annotations

import os
from tkinter import ttk

import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from ..experimentos import montar_figura


class WidgetResultados(ttk.Frame):
    def __init__(self, master, diretorio: str = "resultados/raw", **kw) -> None:
        super().__init__(master, **kw)
        self.diretorio = diretorio
        self.figura = Figure(figsize=(10, 7), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figura, master=self)
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()

        ttk.Button(self, text="Atualizar gráficos", command=self.atualizar).pack(
            side="bottom", pady=4
        )
        self.atualizar()

    def atualizar(self) -> None:
        arq_res = os.path.join(self.diretorio, "resultados.csv")
        arq_hist = os.path.join(self.diretorio, "historico.csv")

        if not os.path.exists(arq_res):
            self.figura.clear()
            ax = self.figura.add_subplot(111)
            ax.axis("off")
            ax.text(
                0.5,
                0.5,
                "Nenhum resultado encontrado.\n\n"
                "Rode:  uv run python -m aspirador",
                ha="center",
                va="center",
                fontsize=12,
            )
            self.canvas.draw()
            return

        df_resultados = pd.read_csv(arq_res)
        df_historico = pd.read_csv(arq_hist) if os.path.exists(arq_hist) else None
        montar_figura(df_resultados, df_historico, self.figura)
        self.canvas.draw()
