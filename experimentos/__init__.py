"""Pacote de experimentos do Projeto 1 (agentes inteligentes)."""

from experimentos.executor import (
    executar_bateria,
    medias_globais,
    por_configuracao,
    rodar_configuracao,
    salvar_saidas,
)
from experimentos.gerador_config import TAMANHO_FIXO, gerar_configuracoes
from experimentos.graficos import montar_figura, salvar_graficos

__all__ = [
    "executar_bateria",
    "gerar_configuracoes",
    "medias_globais",
    "montar_figura",
    "por_configuracao",
    "rodar_configuracao",
    "salvar_graficos",
    "salvar_saidas",
    "TAMANHO_FIXO",
]
