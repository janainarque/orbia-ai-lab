"""Baseline estatístico para avaliação preditiva da V8."""

import math

from collections.abc import Iterable
from dataclasses import dataclass

from src.previsao_pre_jogo import RegistroPreJogo


RESULTADOS_VALIDOS = ("V", "E", "D")


@dataclass(frozen=True)
class BaselineFrequencias:
    """Probabilidades estimadas pelo histórico de treinamento."""

    prob_vitoria: float
    prob_empate: float
    prob_derrota: float
    quantidade_partidas: int


def ajustar_baseline_frequencias(
    registros_treinamento: Iterable[RegistroPreJogo],
    suavizacao: float = 1.0,
) -> BaselineFrequencias:
    """Estima frequências V/E/D apenas com dados de treinamento.

    Aplica suavização aditiva para evitar probabilidades
    nulas quando uma classe não aparece no treinamento.

    O baseline não utiliza ratings Elo nem dados dos
    períodos de validação ou teste.
    """

    if (
        isinstance(suavizacao, bool)
        or not isinstance(suavizacao, (int, float))
        or not math.isfinite(suavizacao)
        or suavizacao < 0
    ):
        raise ValueError(
            "A suavização deve ser um número finito "
            "maior ou igual a zero."
        )

    contagens = {
        "V": 0,
        "E": 0,
        "D": 0,
    }

    quantidade = 0

    for registro in registros_treinamento:
        if registro.resultado not in RESULTADOS_VALIDOS:
            raise ValueError(
                "Resultado inválido no treinamento."
            )

        contagens[registro.resultado] += 1
        quantidade += 1

    if quantidade == 0:
        raise ValueError(
            "O treinamento não pode estar vazio."
        )

    denominador = quantidade + (
        suavizacao * len(RESULTADOS_VALIDOS)
    )

    return BaselineFrequencias(
        prob_vitoria=(
            contagens["V"] + suavizacao
        ) / denominador,
        prob_empate=(
            contagens["E"] + suavizacao
        ) / denominador,
        prob_derrota=(
            contagens["D"] + suavizacao
        ) / denominador,
        quantidade_partidas=quantidade,
    )
