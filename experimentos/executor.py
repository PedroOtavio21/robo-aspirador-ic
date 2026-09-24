"""Execucao dos experimentos: os dois agentes nas MESMAS configuracoes.

Para cada configuracao e medida, executamos:
    * Agente reativo simples (com repeticao, pois e aleatorio);
    * Agente baseado em modelos (deterministico).

As duas medidas (A e B) sao calculadas na mesma execucao.
"""

from __future__ import annotations

import json
import os

import pandas as pd

from core.agentes import AGENTES, AgenteReativoSimples
from core.ambiente import Ambiente, Config
from core.simulador import Simulador

T_PADRAO = 500
REPETICOES_REATIVO_PADRAO = 10


def rodar_configuracao(
    config: Config,
    repeticoes_reativo: int = REPETICOES_REATIVO_PADRAO,
    T: int = T_PADRAO,
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
                    "repeticao": repeticao,
                    "score_a": resultado.score_a,
                    "score_b": resultado.score_b,
                    "movimentos": resultado.movimentos,
                    "passos": resultado.passos,
                    "celulas_limpas": resultado.celulas_limpas,
                    "total_sujos": resultado.total_sujos,
                    "limpo": resultado.limpo,
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
) -> tuple[pd.DataFrame, pd.DataFrame]:
    linhas: list[dict] = []
    historico: list[dict] = []
    for config in configs:
        novas_linhas, novo_historico = rodar_configuracao(
            config, repeticoes_reativo, T
        )
        linhas.extend(novas_linhas)
        historico.extend(novo_historico)
    return pd.DataFrame(linhas), pd.DataFrame(historico)


# ------------------------------------------------------------------- tabelas
def medias_globais(df: pd.DataFrame) -> pd.DataFrame:
    """Media por (config, agente) e depois estatisticas por agente+medida."""
    por_config = (
        df.groupby(["config_id", "agente"])[["score_a", "score_b"]]
        .mean()
        .reset_index()
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
            ["score_a", "score_b", "movimentos", "celulas_limpas", "passos"]
        ]
        .mean()
        .reset_index()
    )


def salvar_saidas(
    configs: list[Config],
    df_resultados: pd.DataFrame,
    df_historico: pd.DataFrame,
    dir_configs: str = "experimentos/configurations",
    dir_raw: str = "experimentos/raw",
    dir_tabelas: str = "resultados/tables",
) -> None:
    for diretorio in (dir_configs, dir_raw, dir_tabelas):
        os.makedirs(diretorio, exist_ok=True)

    with open(os.path.join(dir_configs, "configuracoes.json"), "w", encoding="utf-8") as fh:
        json.dump([c.__dict__ for c in configs], fh, indent=2, default=list)

    df_resultados.to_csv(os.path.join(dir_raw, "resultados.csv"), index=False)
    df_historico.to_csv(os.path.join(dir_raw, "historico.csv"), index=False)
    medias_globais(df_resultados).to_csv(
        os.path.join(dir_tabelas, "medias_globais.csv"), index=False
    )
    por_configuracao(df_resultados).to_csv(
        os.path.join(dir_tabelas, "por_config.csv"), index=False
    )
