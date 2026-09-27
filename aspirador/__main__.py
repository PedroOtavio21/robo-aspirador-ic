from __future__ import annotations

import argparse

from .experimentos import (
    MEMORIA_PADRAO,
    REPETICOES_REATIVO_PADRAO,
    T_PADRAO,
    TAMANHO_FIXO,
    executar_bateria,
    gerar_configuracoes,
    salvar_graficos,
    salvar_saidas,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Bateria de experimentos.")
    parser.add_argument("--configs", type=int, default=40)
    parser.add_argument("--repeticoes", type=int, default=REPETICOES_REATIVO_PADRAO)
    parser.add_argument("--T", type=int, default=T_PADRAO)
    parser.add_argument("--seed", type=int, default=2024)
    parser.add_argument("--tamanho", type=int, default=TAMANHO_FIXO)
    parser.add_argument(
        "--memoria", choices=("mapa", "posicao", "hibrida"), default=MEMORIA_PADRAO
    )
    args = parser.parse_args()

    configs = gerar_configuracoes(args.configs, args.seed, args.tamanho)
    print(
        f"Rodando {len(configs)} configuracoes "
        f"(tamanho {args.tamanho}x{args.tamanho}, T={args.T}, memoria={args.memoria})..."
    )
    df_resultados, df_historico = executar_bateria(
        configs, args.repeticoes, args.T, args.memoria
    )

    salvar_saidas(configs, df_resultados, df_historico)
    salvar_graficos(df_resultados, df_historico)

    print("Saidas em resultados/ (raw, tables e charts).")
    print(df_resultados.groupby("agente")[["score_a", "score_b"]].mean().round(2))


if __name__ == "__main__":
    main()
