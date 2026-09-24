"""Gerador de configuracoes experimentais (secao 11 do planejamento).

O tamanho do ambiente e FIXO no conjunto principal. As configuracoes variam:
    * padrao inicial de sujeira (densidade_sujeira);
    * posicao/quantidade de obstaculos (densidade_obstaculo);
    * posicao inicial do agente (posicao_inicial).

Cada configuracao tem uma semente propria, garantindo reprodutibilidade.
"""

from __future__ import annotations

import random

from core.ambiente import Config

TAMANHO_FIXO = 8


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
