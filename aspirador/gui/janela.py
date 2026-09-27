from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from ..agentes import AGENTES, AgenteBaseadoEmModelo
from ..ambiente import Ambiente
from ..simulador import Simulador
from .widget_grade import GradeCanvas
from .widget_resultados import WidgetResultados

LARGURA_PADRAO, ALTURA_PADRAO = 8, 8
DENSIDADE_SUJEIRA_PADRAO, DENSIDADE_OBSTACULO_PADRAO = 0.4, 0.15
T_PADRAO = 500
INTERVALO_PADRAO = 200
MEMORIAS = {
    "Mapa (matriz)": "mapa",
    "Apenas 1 posição": "posicao",
    "Híbrida (mapa de 1 célula)": "hibrida",
}


class JanelaPrincipal(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Aspirador de pó — Inteligência Computacional")
        self.minsize(840, 640)

        self.simulador: Simulador | None = None
        self._tocando = False
        self._after_id: str | None = None
        self._intervalo = INTERVALO_PADRAO

        self._montar()
        self.protocol("WM_DELETE_WINDOW", self._fechar)
        self.novo()

    def _montar(self) -> None:
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        self.aba_simulacao = ttk.Frame(notebook)
        self.aba_resultados = WidgetResultados(notebook)
        notebook.add(self.aba_simulacao, text="Simulação")
        notebook.add(self.aba_resultados, text="Resultados")

        self._montar_parametros()
        self._montar_controles()
        self._montar_grades()

    def _par(self, caixa, linha, coluna, rotulo, valor, largura=8):
        ttk.Label(caixa, text=rotulo).grid(
            row=linha, column=coluna, sticky="e", padx=(6, 2), pady=3
        )
        entrada = ttk.Entry(caixa, width=largura)
        entrada.insert(0, str(valor))
        entrada.grid(row=linha, column=coluna + 1, sticky="w", padx=(0, 12), pady=3)
        return entrada

    def _montar_parametros(self) -> None:
        caixa = ttk.LabelFrame(self.aba_simulacao, text="Parâmetros", padding=8)
        caixa.pack(fill="x", padx=8, pady=(8, 4))

        ttk.Label(caixa, text="Agente:").grid(
            row=0, column=0, sticky="e", padx=(6, 2), pady=3
        )
        self.combo_agente = ttk.Combobox(
            caixa, values=list(AGENTES), state="readonly", width=18
        )
        self.combo_agente.current(0)
        self.combo_agente.grid(row=0, column=1, sticky="w", padx=(0, 12), pady=3)
        self.combo_agente.bind("<<ComboboxSelected>>", self._atualizar_memoria)

        ttk.Label(caixa, text="Memória:").grid(
            row=0, column=4, sticky="e", padx=(6, 2), pady=3
        )
        self.combo_memoria = ttk.Combobox(
            caixa, values=list(MEMORIAS), state="disabled", width=26
        )
        self.combo_memoria.current(0)
        self.combo_memoria.grid(row=0, column=5, sticky="w", padx=(0, 12), pady=3)

        self.entrada_seed = self._par(caixa, 0, 2, "Seed:", 0)
        self.entrada_largura = self._par(caixa, 1, 0, "Largura:", LARGURA_PADRAO)
        self.entrada_altura = self._par(caixa, 1, 2, "Altura:", ALTURA_PADRAO)
        self.entrada_T = self._par(caixa, 1, 4, "T:", T_PADRAO)
        self.entrada_dens_sujeira = self._par(
            caixa, 2, 0, "Dens. sujeira:", DENSIDADE_SUJEIRA_PADRAO
        )
        self.entrada_dens_obstaculo = self._par(
            caixa, 2, 2, "Dens. obstáculos:", DENSIDADE_OBSTACULO_PADRAO
        )
        self.entrada_pos_x = self._par(caixa, 3, 0, "Posição x:", "")
        self.entrada_pos_y = self._par(caixa, 3, 2, "Posição y:", "")
        ttk.Label(caixa, text="(posição vazia = aleatória)").grid(
            row=3, column=4, columnspan=2, sticky="w", padx=(0, 12)
        )

    def _montar_controles(self) -> None:
        barra = ttk.Frame(self.aba_simulacao, padding=(8, 0))
        barra.pack(fill="x")

        ttk.Button(barra, text="Novo", command=self.novo).pack(side="left", padx=2)
        ttk.Button(barra, text="Passo", command=self.passo).pack(side="left", padx=2)
        self.botao_play = ttk.Button(barra, text="Play", command=self.alternar_play)
        self.botao_play.pack(side="left", padx=2)

        self.var_parar_limpo = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            barra, text="Parar quando limpo", variable=self.var_parar_limpo
        ).pack(side="left", padx=(16, 2))

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

    def _atualizar_memoria(self, _evento=None) -> None:
        if self.combo_agente.get() == AgenteBaseadoEmModelo.nome:
            self.combo_memoria.config(state="readonly")
        else:
            self.combo_memoria.config(state="disabled")

    def _inteiro(self, entrada, padrao: int) -> int:
        try:
            return int(entrada.get().strip())
        except (ValueError, AttributeError):
            return padrao

    def _real(self, entrada, padrao: float) -> float:
        try:
            return float(entrada.get().strip().replace(",", "."))
        except (ValueError, AttributeError):
            return padrao

    def _posicao(self, largura: int, altura: int):
        texto_x = self.entrada_pos_x.get().strip()
        texto_y = self.entrada_pos_y.get().strip()
        if not texto_x and not texto_y:
            return None
        x = self._inteiro(self.entrada_pos_x, -1)
        y = self._inteiro(self.entrada_pos_y, -1)
        if 0 <= x < largura and 0 <= y < altura:
            return (x, y)
        messagebox.showwarning(
            "Posição inicial",
            "Posição fora dos limites; será usada uma posição aleatória.",
        )
        return None

    def novo(self) -> None:
        self.parar_play()
        largura = max(2, self._inteiro(self.entrada_largura, LARGURA_PADRAO))
        altura = max(2, self._inteiro(self.entrada_altura, ALTURA_PADRAO))
        T = max(1, self._inteiro(self.entrada_T, T_PADRAO))
        seed = self._inteiro(self.entrada_seed, 0)
        dens_sujeira = min(
            1.0, max(0.0, self._real(self.entrada_dens_sujeira, DENSIDADE_SUJEIRA_PADRAO))
        )
        dens_obstaculo = min(
            1.0,
            max(0.0, self._real(self.entrada_dens_obstaculo, DENSIDADE_OBSTACULO_PADRAO)),
        )
        posicao = self._posicao(largura, altura)

        try:
            ambiente = Ambiente(
                largura,
                altura,
                dens_sujeira,
                dens_obstaculo,
                seed=seed,
                posicao_inicial=posicao,
            )
        except RuntimeError:
            messagebox.showerror(
                "Geração",
                "Não foi possível gerar um mapa conectado com esses parâmetros.",
            )
            return

        classe = AGENTES[self.combo_agente.get()]
        if classe is AgenteBaseadoEmModelo:
            agente = classe(seed=seed, memoria=MEMORIAS[self.combo_memoria.get()])
        else:
            agente = classe(seed=seed)
        self.simulador = Simulador(
            ambiente,
            agente,
            T=T,
            parar_quando_limpo=self.var_parar_limpo.get(),
        )
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
        estado = self.simulador.agente.mapa_interno()
        if estado is not None:
            self.canvas_mapa.mostrar_mapa(estado)
        else:
            texto = self.simulador.agente.descricao_memoria()
            self.canvas_mapa.mostrar_mensagem(
                texto or "Este agente não mantém estado interno."
            )

        resultado = self.simulador.resultado()
        if self.simulador.terminado:
            if self.simulador.parar_quando_limpo and resultado.limpo:
                status = f"fim (limpo em {resultado.passos} passos)"
            else:
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


def main() -> None:
    JanelaPrincipal().mainloop()
