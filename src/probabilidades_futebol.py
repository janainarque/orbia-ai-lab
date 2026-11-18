"""Modelo experimental de probabilidades de resultados de futebol."""

import math
from dataclasses import dataclass

from src.elo_futebol import probabilidade_esperada_elo


TAXA_EMPATE_EQUILIBRADO = 0.25


@dataclass(frozen=True)
class ProbabilidadesResultado:
    """Probabilidades de vitória, empate e derrota da equipe A."""

    vitoria: float
    empate: float
    derrota: float


def estimar_probabilidades_resultado(
    rating_a: float,
    rating_b: float,
    taxa_empate_equilibrado: float = TAXA_EMPATE_EQUILIBRADO,
) -> ProbabilidadesResultado:
    """Estima probabilidades V/E/D a partir dos ratings Elo.

    A probabilidade de empate é máxima quando os ratings
    são iguais e diminui conforme a diferença aumenta.

    O parâmetro de empate ainda não foi calibrado.
    """

    taxa = taxa_empate_equilibrado

    if (
        isinstance(taxa, bool)
        or not isinstance(taxa, (int, float))
        or not math.isfinite(taxa)
        or not 0 <= taxa <= 0.5
    ):
        raise ValueError(
            "A taxa de empate deve estar entre 0 e 0.5."
        )

    esperado = probabilidade_esperada_elo(
        rating_a,
        rating_b,
    )

    prob_empate = (
        4.0
        * taxa
        * esperado
        * (1.0 - esperado)
    )

    prob_vitoria = esperado - (prob_empate / 2.0)
    prob_derrota = 1.0 - esperado - (prob_empate / 2.0)

    return ProbabilidadesResultado(
        vitoria=prob_vitoria,
        empate=prob_empate,
        derrota=prob_derrota,
    )
