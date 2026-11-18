"""Ajuste de probabilidades preditivas do Orbia V8.

Os parâmetros são estimados exclusivamente no treinamento
temporal, preservando validação e teste para avaliação.
"""

from dataclasses import dataclass
from collections.abc import Iterable
from math import isfinite, log

from src.previsao_pre_jogo import RegistroPreJogo
from src.probabilidades_futebol import (
    ProbabilidadesResultado,
    estimar_probabilidades_resultado,
)
from src.validacao_temporal import dividir_registros_temporais


AJUSTES_ELO_CANDIDATOS = (
    0.0,
    25.0,
    50.0,
    75.0,
    100.0,
    125.0,
    150.0,
)

TAXAS_EMPATE_CANDIDATAS = (
    0.20,
    0.225,
    0.25,
    0.275,
    0.30,
    0.325,
)


@dataclass(frozen=True)
class ParametrosProbabilidades:
    ajuste_elo_mandante: float
    taxa_empate_equilibrado: float
    log_loss_treinamento: float
    quantidade_treinamento: int


def prever_probabilidades_ajustadas(
    registro: RegistroPreJogo,
    ajuste_elo_mandante: float,
    taxa_empate_equilibrado: float,
) -> ProbabilidadesResultado:
    """Calcula probabilidades sem atualizar os ratings Elo."""

    if not isfinite(ajuste_elo_mandante):
        raise ValueError("O ajuste Elo deve ser finito.")

    if not (
        isfinite(taxa_empate_equilibrado)
        and 0.0 <= taxa_empate_equilibrado <= 0.5
    ):
        raise ValueError(
            "A taxa de empate deve estar entre 0 e 0.5."
        )

    return estimar_probabilidades_resultado(
        registro.rating_casa + ajuste_elo_mandante,
        registro.rating_fora,
        taxa_empate_equilibrado=taxa_empate_equilibrado,
    )


def ajustar_probabilidades_treinamento(
    registros: Iterable[RegistroPreJogo],
) -> ParametrosProbabilidades:
    """Seleciona parâmetros minimizando Log Loss no treinamento.

    A seleção é feita por busca em grade fixa.
    Validação e teste não participam do ajuste.
    """

    divisao = dividir_registros_temporais(registros)
    treinamento = divisao.treinamento

    if not treinamento:
        raise ValueError(
            "Não existem partidas no período de treinamento."
        )

    melhor_resultado = None
    melhor_log_loss = float("inf")

    for ajuste in AJUSTES_ELO_CANDIDATOS:
        for taxa_empate in TAXAS_EMPATE_CANDIDATAS:
            soma_log_loss = 0.0

            for registro in treinamento:
                probabilidades = (
                    prever_probabilidades_ajustadas(
                        registro,
                        ajuste_elo_mandante=ajuste,
                        taxa_empate_equilibrado=taxa_empate,
                    )
                )

                probabilidades_por_resultado = {
                    "V": probabilidades.vitoria,
                    "E": probabilidades.empate,
                    "D": probabilidades.derrota,
                }

                if registro.resultado not in (
                    probabilidades_por_resultado
                ):
                    raise ValueError(
                        "Resultado de partida inválido."
                    )

                probabilidade_real = (
                    probabilidades_por_resultado[
                        registro.resultado
                    ]
                )

                soma_log_loss -= log(
                    max(probabilidade_real, 1e-15)
                )

            log_loss_medio = (
                soma_log_loss / len(treinamento)
            )

            if log_loss_medio < melhor_log_loss:
                melhor_log_loss = log_loss_medio

                melhor_resultado = ParametrosProbabilidades(
                    ajuste_elo_mandante=ajuste,
                    taxa_empate_equilibrado=taxa_empate,
                    log_loss_treinamento=log_loss_medio,
                    quantidade_treinamento=len(treinamento),
                )

    return melhor_resultado
