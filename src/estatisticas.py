"""Análises descritivas do ranking parcial observado.

Não gera previsões ou novas probabilidades.
"""

import math
from collections.abc import Sequence
from dataclasses import dataclass

from src.retrospectiva import Previsao


@dataclass(frozen=True)
class EstatisticasRecorte:
    quantidade_selecoes: int
    percentual_observado: float
    percentual_nao_exibido: float
    concentracao_duas_lideres: float
    diferenca_lideres_pp: float | None
    amplitude_pp: float


def validar_ranking(ranking: Sequence[Previsao]) -> None:
    """Valida as entradas antes dos cálculos estatísticos."""

    if not ranking:
        raise ValueError("O ranking não pode estar vazio.")

    selecoes = set()
    total = 0.0

    for item in ranking:
        nome = item.selecao

        if not isinstance(nome, str) or not nome.strip():
            raise ValueError("Nome da seleção inválido.")

        identificador = nome.strip().casefold()

        if identificador in selecoes:
            raise ValueError(
                f"Seleção duplicada: {nome}"
            )

        selecoes.add(identificador)

        percentual = item.percentual

        if (
            isinstance(percentual, bool)
            or not isinstance(percentual, (int, float))
            or not math.isfinite(percentual)
        ):
            raise ValueError(
                f"Percentual inválido para {nome}."
            )

        if not 0 <= percentual <= 100:
            raise ValueError(
                f"Percentual fora do intervalo para {nome}."
            )

        total += percentual

    if total > 100 + 1e-9:
        raise ValueError(
            "Soma dos percentuais acima de 100%."
        )


def analisar_recorte(
    ranking: Sequence[Previsao],
) -> EstatisticasRecorte:
    """Calcula estatísticas descritivas do recorte parcial."""

    validar_ranking(ranking)

    ordenado = sorted(
        ranking,
        key=lambda item: item.percentual,
        reverse=True,
    )

    total = sum(item.percentual for item in ordenado)

    diferenca = None

    if len(ordenado) >= 2:
        diferenca = (
            ordenado[0].percentual
            - ordenado[1].percentual
        )

    return EstatisticasRecorte(
        quantidade_selecoes=len(ordenado),
        percentual_observado=round(total, 3),
        percentual_nao_exibido=round(
            max(0.0, 100 - total), 3
        ),
        concentracao_duas_lideres=round(
            sum(item.percentual for item in ordenado[:2]),
            3,
        ),
        diferenca_lideres_pp=(
            round(diferenca, 3)
            if diferenca is not None
            else None
        ),
        amplitude_pp=round(
            ordenado[0].percentual
            - ordenado[-1].percentual,
            3,
        ),
    )
