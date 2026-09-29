from __future__ import annotations

import json
import os
import random
from datetime import datetime

import pandas as pd
from matplotlib.figure import Figure

from .agentes import AGENTES, AgenteBaseadoEmModelo, AgenteReativoSimples
from .ambiente import Ambiente, Config
from .simulador import Resultado, Simulador

TAMANHO_FIXO = 8
T_PADRAO = 500
REPETICOES_REATIVO_PADRAO = 10
MEMORIA_PADRAO = "mapa"
MEMORIAS_COMPARADAS = ("mapa", "posicao", "hibrida")

DIR_CONFIGS = "resultados/configuracoes.json"
DIR_RAW = "resultados/raw"
DIR_TABELAS = "resultados/tables"
DIR_CHARTS = "resultados/charts"
DIR_EXTRA = "resultados/extra"
DIR_GUI = "resultados/gui"
DIR_GUI_CHARTS = os.path.join(DIR_GUI, "charts")
ARQ_GUI_EXECUCOES = os.path.join(DIR_GUI, "execucoes.csv")

CORES = {"Reativo simples": "#d98b3a", "Baseado em modelo": "#2b6cb0"}
CORES_MEMORIA = {
    "mapa": "#2b6cb0",
    "posicao": "#d98b3a",
    "hibrida": "#2f855a",
}
CORES_MODO = {"T fixo": "#2b6cb0", "Parar quando limpo": "#d98b3a"}
ROTULOS_MEMORIA = {
    "mapa": "Mapa",
    "posicao": "Último movimento",
    "hibrida": "Híbrida",
}
ROTULOS_METRICA = {"score_a": "Medida A", "score_b": "Medida B"}
MEDIDAS = {
    "score_a": "Medida A (+1 por célula limpa pelo robô)",
    "score_b": "Medida B (eficiência: +1/célula limpa, −1/movimento)",
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
    parar_quando_limpo: bool = False,
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
            simulador = Simulador(
                ambiente, agente, T=T, parar_quando_limpo=parar_quando_limpo
            )
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
                    "origem": "cli",
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
    parar_quando_limpo: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    linhas: list[dict] = []
    historico: list[dict] = []
    for config in configs:
        novas_linhas, novo_historico = rodar_configuracao(
            config, repeticoes_reativo, T, memoria, parar_quando_limpo
        )
        linhas.extend(novas_linhas)
        historico.extend(novo_historico)
    return pd.DataFrame(linhas), pd.DataFrame(historico)


def rodar_memorias(
    config: Config,
    T: int = T_PADRAO,
    memorias: tuple[str, ...] = MEMORIAS_COMPARADAS,
) -> list[dict]:
    linhas: list[dict] = []
    for memoria in memorias:
        ambiente = Ambiente(
            config.largura,
            config.altura,
            config.densidade_sujeira,
            config.densidade_obstaculo,
            seed=config.seed,
            posicao_inicial=config.posicao_inicial,
        )
        agente = AgenteBaseadoEmModelo(seed=config.seed, memoria=memoria)
        resultado = Simulador(ambiente, agente, T=T).rodar()
        linhas.append(
            {
                "config_id": config.config_id,
                "agente": AgenteBaseadoEmModelo.nome,
                "memoria": memoria,
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
            }
        )
    return linhas


def executar_extra(
    configs: list[Config],
    repeticoes_reativo: int = REPETICOES_REATIVO_PADRAO,
    T: int = T_PADRAO,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    df_stop, _ = executar_bateria(
        configs, repeticoes_reativo, T, parar_quando_limpo=True
    )
    linhas: list[dict] = []
    for config in configs:
        linhas.extend(rodar_memorias(config, T))
    return df_stop, pd.DataFrame(linhas)


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


def resumo_parar_limpo(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("agente")
        .agg(
            score_a=("score_a", "mean"),
            score_b=("score_b", "mean"),
            movimentos=("movimentos", "mean"),
            passos=("passos", "mean"),
            celulas_limpas=("celulas_limpas", "mean"),
            percentual_limpo=("percentual_limpo", "mean"),
            limpo=("limpo", "mean"),
        )
        .reset_index()
    )


def resumo_memorias(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["agente", "memoria"])
        .agg(
            score_a=("score_a", "mean"),
            score_b=("score_b", "mean"),
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


def _figura_execucao_gui(resultado: Resultado, agente: str, memoria: str | None) -> Figure:
    figura = Figure(figsize=(6, 4), dpi=100)
    ax = figura.add_subplot(111)
    passos = range(1, len(resultado.historico_a) + 1)
    ax.plot(passos, resultado.historico_a, label="Medida A")
    ax.plot(passos, resultado.historico_b, label="Medida B")
    titulo = f"Evolução da execução (GUI) — {agente}"
    if memoria:
        titulo += f" ({memoria})"
    ax.set_title(titulo)
    ax.set_xlabel("período")
    ax.set_ylabel("pontuação")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    figura.tight_layout()
    return figura


def salvar_execucao_gui(
    resultado: Resultado,
    agente: str,
    memoria: str | None,
    seed: int,
    largura: int,
    altura: int,
    densidade_sujeira: float,
    densidade_obstaculo: float,
    posicao_inicial: tuple[int, int],
    T: int,
    parar_quando_limpo: bool,
) -> str:
    os.makedirs(DIR_GUI, exist_ok=True)
    os.makedirs(DIR_GUI_CHARTS, exist_ok=True)

    identificador = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    caminho_grafico = os.path.join(DIR_GUI_CHARTS, f"{identificador}.png")
    _figura_execucao_gui(resultado, agente, memoria).savefig(caminho_grafico)

    linha = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "origem": "gui",
        "agente": agente,
        "memoria": memoria or "",
        "seed": seed,
        "largura": largura,
        "altura": altura,
        "densidade_sujeira": densidade_sujeira,
        "densidade_obstaculo": densidade_obstaculo,
        "posicao_inicial": f"{posicao_inicial[0]},{posicao_inicial[1]}",
        "T": T,
        "parar_quando_limpo": parar_quando_limpo,
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
        "grafico": caminho_grafico,
    }
    pd.DataFrame([linha]).to_csv(
        ARQ_GUI_EXECUCOES,
        mode="a",
        header=not os.path.exists(ARQ_GUI_EXECUCOES),
        index=False,
    )
    return caminho_grafico


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


def _rotular_barras(ax, fmt: str = "{:.0f}") -> None:
    for container in ax.containers:
        try:
            ax.bar_label(container, fmt=fmt, fontsize=8, padding=2)
        except (AttributeError, TypeError):
            continue


def _estilizar(ax, titulo: str, ylabel: str | None = None) -> None:
    ax.set_title(titulo, fontsize=11, fontweight="bold")
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=9)


def plotar_barras(df: pd.DataFrame, metrica: str, ax, titulo: str) -> None:
    resumo = _resumo_por_config(df, metrica)
    resumo = resumo.reindex(list(AGENTES)).dropna(how="all")
    cores = [CORES.get(a, "#888888") for a in resumo.index]
    ax.bar(resumo.index, resumo["mean"], yerr=resumo["std"], capsize=5, color=cores)
    _rotular_barras(ax, "{:,.0f}")
    _estilizar(ax, titulo, "pontuação")


def plotar_curva(df_historico: pd.DataFrame | None, ax) -> None:
    if df_historico is None or df_historico.empty:
        ax.set_visible(False)
        return
    df = df_historico.copy()
    df["fracao"] = df["celulas_limpas"] / df["total_sujos"].replace(0, 1)
    curva = df.groupby(["agente", "passo"])["fracao"].mean().reset_index()
    for agente, grupo in curva.groupby("agente"):
        ax.plot(
            grupo["passo"],
            grupo["fracao"],
            label=agente,
            color=CORES.get(agente),
            linewidth=2,
        )
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("período", fontsize=9)
    _estilizar(ax, "Fração de células limpas × tempo", "fração limpa (0-1)")
    ax.legend(fontsize=8)


def plotar_boxplot(df: pd.DataFrame, ax, metrica: str = "score_b") -> None:
    por_config = df.groupby(["config_id", "agente"])[metrica].mean().reset_index()
    ordem = list(AGENTES)
    dados = [por_config[por_config["agente"] == a][metrica].values for a in ordem]
    caixas = ax.boxplot(dados, tick_labels=ordem, showmeans=True, patch_artist=True)
    for caixa, agente in zip(caixas["boxes"], ordem):
        caixa.set_facecolor(CORES.get(agente, "#888888"))
        caixa.set_alpha(0.55)
    _estilizar(ax, f"Distribuição de {MEDIDAS.get(metrica, metrica)}", "pontuação")
    ax.tick_params(axis="x", labelsize=8)


def plotar_metricas_agrupadas(df: pd.DataFrame, ax) -> None:
    resumo = _resumo_por_config(df, "score_a")[["mean"]].rename(
        columns={"mean": "score_a"}
    )
    resumo["score_b"] = _resumo_por_config(df, "score_b")["mean"]
    resumo = resumo.reindex(list(AGENTES)).dropna(how="all")
    posicoes = list(range(len(resumo)))
    largura = 0.38
    ax.bar(
        [p - largura / 2 for p in posicoes],
        resumo["score_a"],
        width=largura,
        label="Medida A",
        color="#2b6cb0",
    )
    ax.bar(
        [p + largura / 2 for p in posicoes],
        resumo["score_b"],
        width=largura,
        label="Medida B (eficiência)",
        color="#d98b3a",
    )
    _rotular_barras(ax, "{:,.0f}")
    ax.set_xticks(posicoes)
    ax.set_xticklabels(resumo.index, fontsize=8)
    _estilizar(ax, "Comparação entre métricas — A × B", "pontuação")
    ax.legend(fontsize=8)


def plotar_comparativo_metricas(df: pd.DataFrame, figura: Figure) -> None:
    figura.clear()
    plotar_barras(
        df, "score_a", figura.add_subplot(1, 2, 1),
        "Medida A — média por configuração",
    )
    plotar_barras(
        df, "score_b", figura.add_subplot(1, 2, 2),
        "Medida B — eficiência (maior é melhor)",
    )
    figura.tight_layout()


def plotar_comparativo_modelos(df: pd.DataFrame, figura: Figure) -> None:
    figura.clear()
    agentes = list(AGENTES)
    eficiencia = resumo_eficiencia(df).set_index("agente").reindex(agentes)

    plotar_barras(
        df, "score_a", figura.add_subplot(1, 3, 1),
        "Medida A — desempenho",
    )
    plotar_barras(
        df, "score_b", figura.add_subplot(1, 3, 2),
        "Medida B — eficiência",
    )

    ax3 = figura.add_subplot(1, 3, 3)
    barras = ax3.bar(
        agentes,
        eficiencia["movimentos"],
        color=[CORES.get(a, "#888888") for a in agentes],
    )
    ax3.bar_label(barras, fmt="{:,.0f}", fontsize=8, padding=2)
    _estilizar(ax3, "Esforço e limpeza total", "movimentos")
    ax3.tick_params(axis="x", labelsize=8)
    ax3b = ax3.twinx()
    ax3b.plot(
        agentes,
        eficiencia["limpo"] * 100,
        "o--",
        color="#2f855a",
        linewidth=2,
        label="% limpou tudo",
    )
    for agente, valor in zip(agentes, eficiencia["limpo"] * 100):
        ax3b.annotate(
            f"{valor:.0f}%",
            (agente, valor),
            textcoords="offset points",
            xytext=(0, 6),
            ha="center",
            fontsize=8,
            color="#2f855a",
        )
    ax3b.set_ylabel("% limpou tudo", fontsize=9, color="#2f855a")
    ax3b.set_ylim(0, 112)
    ax3b.tick_params(labelsize=9, colors="#2f855a")
    figura.tight_layout()


def montar_figura(
    df_resultados: pd.DataFrame,
    df_historico: pd.DataFrame | None = None,
    figura: Figure | None = None,
) -> Figure:
    if figura is None:
        figura = Figure(figsize=(11, 8), dpi=100)
    figura.clear()
    plotar_barras(
        df_resultados, "score_a", figura.add_subplot(2, 2, 1),
        "Medida A — média por configuração",
    )
    plotar_barras(
        df_resultados, "score_b", figura.add_subplot(2, 2, 2),
        "Medida B — média por configuração",
    )
    plotar_metricas_agrupadas(df_resultados, figura.add_subplot(2, 2, 3))
    plotar_curva(df_historico, figura.add_subplot(2, 2, 4))
    figura.tight_layout()
    return figura


def _salvar_figura(figura: Figure, destino: str, nome: str, dpi: int = 150) -> None:
    figura.tight_layout()
    figura.savefig(os.path.join(destino, nome), dpi=dpi, bbox_inches="tight")


def salvar_graficos(
    df_resultados: pd.DataFrame,
    df_historico: pd.DataFrame | None,
    destino: str = DIR_CHARTS,
) -> None:
    os.makedirs(destino, exist_ok=True)

    _salvar_figura(
        montar_figura(df_resultados, df_historico), destino, "graficos.png", dpi=140
    )

    fig_a = Figure(figsize=(6, 4.5), dpi=100)
    plotar_barras(
        df_resultados, "score_a", fig_a.add_subplot(1, 1, 1),
        "Medida A — média por configuração",
    )
    _salvar_figura(fig_a, destino, "metrica_a.png")

    fig_b = Figure(figsize=(6, 4.5), dpi=100)
    plotar_barras(
        df_resultados, "score_b", fig_b.add_subplot(1, 1, 1),
        "Medida B — média por configuração",
    )
    _salvar_figura(fig_b, destino, "metrica_b.png")

    fig_metricas = Figure(figsize=(11, 4.5), dpi=100)
    plotar_comparativo_metricas(df_resultados, fig_metricas)
    _salvar_figura(fig_metricas, destino, "comparativo_metricas.png")

    fig_modelos = Figure(figsize=(14, 4.5), dpi=100)
    plotar_comparativo_modelos(df_resultados, fig_modelos)
    _salvar_figura(fig_modelos, destino, "comparativo_modelos.png")

    fig_curva = Figure(figsize=(6.5, 4.5), dpi=100)
    plotar_curva(df_historico, fig_curva.add_subplot(1, 1, 1))
    _salvar_figura(fig_curva, destino, "curva_limpas.png")

    fig_box = Figure(figsize=(6, 4.5), dpi=100)
    plotar_boxplot(df_resultados, fig_box.add_subplot(1, 1, 1))
    _salvar_figura(fig_box, destino, "boxplot.png")


def _resumo_metrica_por_agente(df: pd.DataFrame, metrica: str) -> pd.DataFrame:
    por_config = (
        df.groupby(["config_id", "agente"])[metrica].mean().reset_index()
    )
    return por_config.groupby("agente")[metrica].agg(["mean", "std"]).fillna(0.0)


def plotar_memorias(df_mem: pd.DataFrame, ax, metrica: str = "score_a") -> None:
    resumo = resumo_memorias(df_mem)
    ordem = [m for m in ("mapa", "posicao", "hibrida") if m in set(resumo["memoria"])]
    resumo = resumo.set_index("memoria").reindex(ordem)
    cores = [CORES_MEMORIA.get(m, "#888888") for m in resumo.index]
    barras = ax.bar(
        [ROTULOS_MEMORIA.get(m, m) for m in resumo.index],
        resumo[metrica].fillna(0.0),
        color=cores,
    )
    ax.bar_label(barras, fmt="{:,.0f}", fontsize=8, padding=2)
    sufixo = "Medida A" if metrica == "score_a" else "Medida B (eficiência)"
    _estilizar(ax, f"Tipos de memória — {sufixo}", "pontuação")
    ax.tick_params(axis="x", labelsize=8)


def plotar_comparativo_memorias(df_mem: pd.DataFrame, figura: Figure) -> None:
    figura.clear()
    plotar_memorias(df_mem, figura.add_subplot(1, 2, 1), "score_a")
    plotar_memorias(df_mem, figura.add_subplot(1, 2, 2), "score_b")
    figura.tight_layout()


def plotar_normal_vs_break(
    df_normal: pd.DataFrame,
    df_stop: pd.DataFrame,
    ax,
    metrica: str = "score_a",
) -> None:
    normal = _resumo_metrica_por_agente(df_normal, metrica).reindex(list(AGENTES))
    parado = _resumo_metrica_por_agente(df_stop, metrica).reindex(list(AGENTES))
    posicoes = list(range(len(normal)))
    largura = 0.38
    ax.bar(
        [p - largura / 2 for p in posicoes],
        normal["mean"],
        width=largura,
        yerr=normal["std"],
        capsize=4,
        label="T fixo (tempo normal)",
        color=CORES_MODO["T fixo"],
    )
    ax.bar(
        [p + largura / 2 for p in posicoes],
        parado["mean"],
        width=largura,
        yerr=parado["std"],
        capsize=4,
        label="Parar quando limpo",
        color=CORES_MODO["Parar quando limpo"],
    )
    _rotular_barras(ax, "{:,.0f}")
    ax.set_xticks(posicoes)
    ax.set_xticklabels(normal.index, fontsize=8)
    _estilizar(
        ax,
        f"Tempo normal × parar após limpar — {ROTULOS_METRICA.get(metrica, metrica)}",
        "pontuação",
    )
    ax.legend(fontsize=8)


def plotar_eficiencia_extra(df: pd.DataFrame, ax) -> None:
    resumo = resumo_eficiencia(df).set_index("agente").reindex(list(AGENTES))
    posicoes = list(range(len(resumo)))
    largura = 0.38
    ax.bar(
        [p - largura / 2 for p in posicoes],
        resumo["movimentos"],
        width=largura,
        label="movimentos",
        color="#2b6cb0",
    )
    ax.bar(
        [p + largura / 2 for p in posicoes],
        resumo["passos_ate_limpo"].fillna(0.0),
        width=largura,
        label="passos até limpar",
        color="#d98b3a",
    )
    _rotular_barras(ax, "{:,.0f}")
    ax.set_xticks(posicoes)
    ax.set_xticklabels(resumo.index, fontsize=8)
    _estilizar(ax, "Eficiência por agente", "quantidade")
    ax.legend(fontsize=8)


def montar_figura_extra(
    df_stop: pd.DataFrame,
    df_mem: pd.DataFrame,
    df_principal: pd.DataFrame,
    figura: Figure | None = None,
) -> Figure:
    if figura is None:
        figura = Figure(figsize=(11, 8), dpi=100)
    figura.clear()
    plotar_memorias(df_mem, figura.add_subplot(2, 2, 1), "score_a")
    plotar_normal_vs_break(
        df_principal, df_stop, figura.add_subplot(2, 2, 2), "score_a"
    )
    plotar_normal_vs_break(
        df_principal, df_stop, figura.add_subplot(2, 2, 3), "score_b"
    )
    plotar_eficiencia_extra(df_principal, figura.add_subplot(2, 2, 4))
    figura.tight_layout()
    return figura


def salvar_extra(
    df_stop: pd.DataFrame,
    df_mem: pd.DataFrame,
    df_principal: pd.DataFrame,
    destino: str = DIR_EXTRA,
) -> None:
    os.makedirs(destino, exist_ok=True)
    pesadas = ("acoes", "mapa_inicial")
    df_stop.drop(columns=[c for c in pesadas if c in df_stop.columns]).to_csv(
        os.path.join(destino, "stop_raw.csv"), index=False
    )
    df_mem.drop(columns=[c for c in pesadas if c in df_mem.columns]).to_csv(
        os.path.join(destino, "memorias_raw.csv"), index=False
    )
    resumo_parar_limpo(df_stop).to_csv(
        os.path.join(destino, "parar_limpo.csv"), index=False
    )
    resumo_memorias(df_mem).to_csv(
        os.path.join(destino, "memorias.csv"), index=False
    )
    resumo_eficiencia(df_principal).to_csv(
        os.path.join(destino, "eficiencia.csv"), index=False
    )

    _salvar_figura(
        montar_figura_extra(df_stop, df_mem, df_principal),
        destino,
        "graficos_extra.png",
        dpi=140,
    )

    fig_mem = Figure(figsize=(11, 4.5), dpi=100)
    plotar_comparativo_memorias(df_mem, fig_mem)
    _salvar_figura(fig_mem, destino, "comparativo_memorias.png")

    fig_break = Figure(figsize=(11, 4.5), dpi=100)
    plotar_normal_vs_break(
        df_principal, df_stop, fig_break.add_subplot(1, 2, 1), "score_a"
    )
    plotar_normal_vs_break(
        df_principal, df_stop, fig_break.add_subplot(1, 2, 2), "score_b"
    )
    _salvar_figura(fig_break, destino, "normal_vs_break.png")

    fig_ef = Figure(figsize=(7, 4.5), dpi=100)
    plotar_eficiencia_extra(df_principal, fig_ef.add_subplot(1, 1, 1))
    _salvar_figura(fig_ef, destino, "eficiencia.png")
