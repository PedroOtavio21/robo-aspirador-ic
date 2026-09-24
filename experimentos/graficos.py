"""Tabelas e graficos dos resultados (secao 17 do planejamento).

Cada grafico deixa explicito o agente, a medida, a unidade e o conjunto de
configuracoes utilizados.
"""

from __future__ import annotations

import os

import pandas as pd
from matplotlib.figure import Figure

from core.agentes import AGENTES

CORES = {"Reativo simples": "#d98b3a", "Baseado em modelo": "#2b6cb0"}
MEDIDAS = {"score_a": "Medida A (+1/quadrado limpo por período)",
           "score_b": "Medida B (+1 limpo, -1 movimento)"}


def _resumo_por_config(df: pd.DataFrame, metrica: str) -> pd.DataFrame:
    por_config = df.groupby(["config_id", "agente"])[metrica].mean().reset_index()
    return por_config.groupby("agente")[metrica].agg(["mean", "std"]).fillna(0.0)


def plotar_barras(df: pd.DataFrame, metrica: str, ax, titulo: str) -> None:
    resumo = _resumo_por_config(df, metrica)
    resumo = resumo.reindex(list(AGENTES)).dropna(how="all")
    cores = [CORES.get(a, "#888888") for a in resumo.index]
    ax.bar(resumo.index, resumo["mean"], yerr=resumo["std"], capsize=5, color=cores)
    ax.set_title(titulo)
    ax.set_ylabel("pontuação")
    ax.grid(axis="y", alpha=0.3)


def plotar_curva(df_historico: pd.DataFrame | None, ax) -> None:
    if df_historico is None or df_historico.empty:
        ax.set_visible(False)
        return
    df = df_historico.copy()
    df["fracao"] = df["celulas_limpas"] / df["total_sujos"].replace(0, 1)
    curva = df.groupby(["agente", "passo"])["fracao"].mean().reset_index()
    for agente, grupo in curva.groupby("agente"):
        ax.plot(grupo["passo"], grupo["fracao"], label=agente, color=CORES.get(agente))
    ax.set_title("Fração de células limpas × tempo")
    ax.set_xlabel("período")
    ax.set_ylabel("fração limpa (0-1)")
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)


def plotar_boxplot(df: pd.DataFrame, ax, metrica: str = "score_b") -> None:
    por_config = df.groupby(["config_id", "agente"])[metrica].mean().reset_index()
    ordem = list(AGENTES)
    dados = [por_config[por_config["agente"] == a][metrica].values for a in ordem]
    ax.boxplot(dados, tick_labels=ordem, showmeans=True)
    ax.set_title(f"Distribuição de {MEDIDAS.get(metrica, metrica)}")
    ax.set_ylabel("pontuação")
    ax.grid(axis="y", alpha=0.3)


def montar_figura(
    df_resultados: pd.DataFrame,
    df_historico: pd.DataFrame | None = None,
    figura: Figure | None = None,
) -> Figure:
    if figura is None:
        figura = Figure(figsize=(10, 7), dpi=100)
    figura.clear()
    plotar_barras(
        df_resultados, "score_a", figura.add_subplot(2, 2, 1),
        "Medida A — média por configuração",
    )
    plotar_barras(
        df_resultados, "score_b", figura.add_subplot(2, 2, 2),
        "Medida B — média por configuração",
    )
    plotar_curva(df_historico, figura.add_subplot(2, 2, 3))
    plotar_boxplot(df_resultados, figura.add_subplot(2, 2, 4))
    figura.tight_layout()
    return figura


def salvar_graficos(
    df_resultados: pd.DataFrame,
    df_historico: pd.DataFrame | None,
    destino: str = "resultados/charts",
) -> None:
    os.makedirs(destino, exist_ok=True)

    montar_figura(df_resultados, df_historico).savefig(
        os.path.join(destino, "graficos.png")
    )

    fig_barras = Figure(figsize=(9, 4), dpi=100)
    plotar_barras(
        df_resultados, "score_a", fig_barras.add_subplot(1, 2, 1),
        "Medida A — média por configuração",
    )
    plotar_barras(
        df_resultados, "score_b", fig_barras.add_subplot(1, 2, 2),
        "Medida B — média por configuração",
    )
    fig_barras.tight_layout()
    fig_barras.savefig(os.path.join(destino, "barras_medidas.png"))

    fig_curva = Figure(figsize=(6, 4), dpi=100)
    plotar_curva(df_historico, fig_curva.add_subplot(1, 1, 1))
    fig_curva.tight_layout()
    fig_curva.savefig(os.path.join(destino, "curva_limpas.png"))

    fig_box = Figure(figsize=(5, 4), dpi=100)
    plotar_boxplot(df_resultados, fig_box.add_subplot(1, 1, 1))
    fig_box.tight_layout()
    fig_box.savefig(os.path.join(destino, "boxplot.png"))
