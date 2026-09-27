from __future__ import annotations

import json
import os
import random

import pandas as pd
from matplotlib.figure import Figure

from .agentes import AGENTES, AgenteBaseadoEmModelo, AgenteReativoSimples
from .ambiente import Ambiente, Config
from .simulador import Simulador

TAMANHO_FIXO = 8
T_PADRAO = 500
REPETICOES_REATIVO_PADRAO = 10
MEMORIA_PADRAO = "mapa"

DIR_CONFIGS = "resultados/configuracoes.json"
DIR_RAW = "resultados/raw"
DIR_TABELAS = "resultados/tables"
DIR_CHARTS = "resultados/charts"

CORES = {"Reativo simples": "#d98b3a", "Baseado em modelo": "#2b6cb0"}
MEDIDAS = {
    "score_a": "Medida A (+1/quadrado limpo por período)",
    "score_b": "Medida B (+1 limpo, -1 movimento)",
}


def gerar_configuracoes(
    n: int = 40,
    seed: int = 2024,
    tamanho: int = TAMANHO_FIXO,
) -> list[Config]:
    rng = random.Random(seed)
    configs: list[Config] = []
    for i in range(n):
        posicao = (rng.randrange(tamanho), rng.randrange(tamanho))
        configs.append(
            Config(
                config_id=i,
                seed=rng.randrange(1, 1_000_000),
                largura=tamanho,
                altura=tamanho,
                densidade_sujeira=round(rng.uniform(0.2, 0.6), 2),
                densidade_obstaculo=round(rng.uniform(0.0, 0.25), 2),
                posicao_inicial=posicao,
            )
        )
    return configs


def rodar_configuracao(
    config: Config,
    repeticoes_reativo: int = REPETICOES_REATIVO_PADRAO,
    T: int = T_PADRAO,
    memoria: str = MEMORIA_PADRAO,
) -> tuple[list[dict], list[dict]]:
    linhas: list[dict] = []
    historico: list[dict] = []

    for nome, classe in AGENTES.items():
        repeticoes = repeticoes_reativo if classe is AgenteReativoSimples else 1
        for repeticao in range(repeticoes):
            ambiente = Ambiente(
                config.largura,
                config.altura,
                config.densidade_sujeira,
                config.densidade_obstaculo,
                seed=config.seed,
                posicao_inicial=config.posicao_inicial,
            )
            mapa_inicial = ambiente.mapa_inicial_str()
            if classe is AgenteBaseadoEmModelo:
                agente = classe(seed=config.seed + repeticao, memoria=memoria)
            else:
                agente = classe(seed=config.seed + repeticao)
            simulador = Simulador(ambiente, agente, T=T)
            resultado = simulador.rodar()

            linhas.append(
                {
                    "config_id": config.config_id,
                    "seed": config.seed,
                    "largura": config.largura,
                    "altura": config.altura,
                    "densidade_sujeira": config.densidade_sujeira,
                    "densidade_obstaculo": config.densidade_obstaculo,
                    "posicao_inicial": f"{config.posicao_inicial[0]},"
                    f"{config.posicao_inicial[1]}",
                    "mapa_inicial": mapa_inicial,
                    "agente": nome,
                    "memoria": memoria,
                    "repeticao": repeticao,
                    "score_a": resultado.score_a,
                    "score_b": resultado.score_b,
                    "movimentos": resultado.movimentos,
                    "passos": resultado.passos,
                    "celulas_limpas": resultado.celulas_limpas,
                    "total_sujos": resultado.total_sujos,
                    "limpo": resultado.limpo,
                    "passos_ate_limpo": resultado.passos_ate_limpo,
                    "movimentos_ate_limpo": resultado.movimentos_ate_limpo,
                    "percentual_limpo": resultado.percentual_limpo,
                    "acoes": " ".join(resultado.acoes),
                }
            )
            for passo, limpas in enumerate(resultado.historico_limpos, start=1):
                historico.append(
                    {
                        "config_id": config.config_id,
                        "agente": nome,
                        "repeticao": repeticao,
                        "passo": passo,
                        "celulas_limpas": limpas,
                        "total_sujos": resultado.total_sujos,
                    }
                )
    return linhas, historico


def executar_bateria(
    configs: list[Config],
    repeticoes_reativo: int = REPETICOES_REATIVO_PADRAO,
    T: int = T_PADRAO,
    memoria: str = MEMORIA_PADRAO,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    linhas: list[dict] = []
    historico: list[dict] = []
    for config in configs:
        novas_linhas, novo_historico = rodar_configuracao(
            config, repeticoes_reativo, T, memoria
        )
        linhas.extend(novas_linhas)
        historico.extend(novo_historico)
    return pd.DataFrame(linhas), pd.DataFrame(historico)


def medias_globais(df: pd.DataFrame) -> pd.DataFrame:
    por_config = (
        df.groupby(["config_id", "agente"])[["score_a", "score_b"]].mean().reset_index()
    )
    registros = []
    for agente, grupo in por_config.groupby("agente"):
        for medida, coluna in (("Medida A", "score_a"), ("Medida B", "score_b")):
            registros.append(
                {
                    "agente": agente,
                    "medida": medida,
                    "media": grupo[coluna].mean(),
                    "desvio": grupo[coluna].std(ddof=0),
                }
            )
    return pd.DataFrame(registros)


def por_configuracao(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["config_id", "agente"])[
            [
                "score_a",
                "score_b",
                "movimentos",
                "celulas_limpas",
                "passos",
                "passos_ate_limpo",
                "movimentos_ate_limpo",
                "percentual_limpo",
            ]
        ]
        .mean()
        .reset_index()
    )


def resumo_eficiencia(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("agente")
        .agg(
            movimentos=("movimentos", "mean"),
            passos=("passos", "mean"),
            celulas_limpas=("celulas_limpas", "mean"),
            percentual_limpo=("percentual_limpo", "mean"),
            limpo=("limpo", "mean"),
            passos_ate_limpo=("passos_ate_limpo", "mean"),
            movimentos_ate_limpo=("movimentos_ate_limpo", "mean"),
        )
        .reset_index()
    )


def salvar_saidas(
    configs: list[Config],
    df_resultados: pd.DataFrame,
    df_historico: pd.DataFrame,
) -> None:
    for diretorio in (DIR_RAW, DIR_TABELAS):
        os.makedirs(diretorio, exist_ok=True)

    with open(DIR_CONFIGS, "w", encoding="utf-8") as fh:
        json.dump([c.__dict__ for c in configs], fh, indent=2, default=list)

    df_resultados.to_csv(os.path.join(DIR_RAW, "resultados.csv"), index=False)
    df_historico.to_csv(os.path.join(DIR_RAW, "historico.csv"), index=False)
    medias_globais(df_resultados).to_csv(
        os.path.join(DIR_TABELAS, "medias_globais.csv"), index=False
    )
    por_configuracao(df_resultados).to_csv(
        os.path.join(DIR_TABELAS, "por_config.csv"), index=False
    )
    resumo_eficiencia(df_resultados).to_csv(
        os.path.join(DIR_TABELAS, "eficiencia.csv"), index=False
    )


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
    destino: str = DIR_CHARTS,
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
