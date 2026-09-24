"""CLI da bateria de experimentos.

Uso:
    python -m experimentos [--configs 40] [--repeticoes 10] [--T 500] [--seed 2024]
"""

from __future__ import annotations

import argparse

from experimentos.executor import (
    REPETICOES_REATIVO_PADRAO,
    T_PADRAO,
    executar_bateria,
    salvar_saidas,
)
from experimentos.gerador_config import TAMANHO_FIXO, gerar_configuracoes
from experimentos.graficos import salvar_graficos


def main() -> None:
    parser = argparse.ArgumentParser(description="Bateria de experimentos.")
    parser.add_argument("--configs", type=int, default=40)
    parser.add_argument("--repeticoes", type=int, default=REPETICOES_REATIVO_PADRAO)
    parser.add_argument("--T", type=int, default=T_PADRAO)
    parser.add_argument("--seed", type=int, default=2024)
    parser.add_argument("--tamanho", type=int, default=TAMANHO_FIXO)
    args = parser.parse_args()

    configs = gerar_configuracoes(args.configs, args.seed, args.tamanho)
    print(
        f"Rodando {len(configs)} configuracoes "
        f"(tamanho {args.tamanho}x{args.tamanho}, T={args.T})..."
    )
    df_resultados, df_historico = executar_bateria(configs, args.repeticoes, args.T)

    salvar_saidas(configs, df_resultados, df_historico)
    salvar_graficos(df_resultados, df_historico)

    print("Saidas em experimentos/ (configs e raw) e resultados/ (tabelas e charts).")
    print(df_resultados.groupby("agente")[["score_a", "score_b"]].mean().round(2))


if __name__ == "__main__":
    main()
