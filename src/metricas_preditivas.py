"""Métricas de avaliação preditiva multiclasse da V8."""

import math
from collections.abc import Iterable
from dataclasses import dataclass

from src.previsao_pre_jogo import RegistroPreJogo


EPSILON = 1e-15

RESULTADOS = {
    "V": 0,
    "E": 1,
    "D": 2,
}


@dataclass(frozen=True)
class MetricasPreditivas:
    quantidade_partidas: int
    log_loss: float
    brier_score: float


def avaliar_previsoes(
    registros: Iterable[RegistroPreJogo],
) -> MetricasPreditivas:
    """Calcula Log Loss e Brier Score multiclasse.

    Ordem das classes: vitória, empate e derrota.

    Brier Score utiliza a soma dos erros quadráticos
    das três classes, sem divisão pelo número de classes.

    Probabilidades nulas são limitadas por EPSILON
    apenas no cálculo do logaritmo.
    """

    registros = list(registros)

    if not registros:
        raise ValueError(
            "Não existem partidas para avaliação."
        )

    soma_log_loss = 0.0
    soma_brier = 0.0

    for registro in registros:
        if registro.resultado not in RESULTADOS:
            raise ValueError(
                "Resultado de partida inválido."
            )

        probabilidades = (
            registro.prob_vitoria,
            registro.prob_empate,
            registro.prob_derrota,
        )

        for probabilidade in probabilidades:
            if (
                isinstance(probabilidade, bool)
                or not isinstance(
                    probabilidade, (int, float)
                )
                or not math.isfinite(probabilidade)
                or not 0.0 <= probabilidade <= 1.0
            ):
                raise ValueError(
                    "Probabilidade inválida."
                )

        if not math.isclose(
            sum(probabilidades),
            1.0,
            rel_tol=0.0,
            abs_tol=1e-9,
        ):
            raise ValueError(
                "As probabilidades devem somar 1."
            )

        indice_real = RESULTADOS[registro.resultado]

        probabilidade_real = probabilidades[indice_real]

        soma_log_loss -= math.log(
            max(probabilidade_real, EPSILON)
        )

        for indice, probabilidade in enumerate(
            probabilidades
        ):
            observado = (
                1.0 if indice == indice_real else 0.0
            )

            soma_brier += (
                probabilidade - observado
            ) ** 2

    quantidade = len(registros)

    return MetricasPreditivas(
        quantidade_partidas=quantidade,
        log_loss=soma_log_loss / quantidade,
        brier_score=soma_brier / quantidade,
    )
