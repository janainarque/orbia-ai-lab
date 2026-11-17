"""Motor experimental de rating Elo baseado em partidas históricas."""

import math
from collections.abc import Iterable

from src.dados_futebol import RegistroPartida
from datetime import date


RATING_INICIAL = 1500.0
FATOR_K = 20.0


def validar_parametros_elo(
    rating_inicial: float,
    fator_k: float,
) -> None:
    """Valida os parâmetros configuráveis do motor Elo."""

    for nome, valor in (
        ("Rating inicial", rating_inicial),
        ("Fator K", fator_k),
    ):
        if (
            isinstance(valor, bool)
            or not isinstance(valor, (int, float))
            or not math.isfinite(valor)
        ):
            raise ValueError(f"{nome} inválido.")

    if rating_inicial <= 0:
        raise ValueError("O rating inicial deve ser positivo.")

    if fator_k <= 0:
        raise ValueError("O fator K deve ser positivo.")


def probabilidade_esperada_elo(
    rating_a: float,
    rating_b: float,
) -> float:
    """Calcula a pontuação esperada da seleção A."""

    for rating in (rating_a, rating_b):
        if (
            isinstance(rating, bool)
            or not isinstance(rating, (int, float))
            or not math.isfinite(rating)
        ):
            raise ValueError("Rating Elo inválido.")

    diferenca = (rating_b - rating_a) / 400.0

    # Formulação numericamente estável da função logística.
    expoente = diferenca * math.log(10)

    if expoente >= 0:
        fator = math.exp(-expoente)
        return fator / (1.0 + fator)

    return 1.0 / (1.0 + math.exp(expoente))


def atualizar_ratings_elo(
    rating_casa: float,
    rating_fora: float,
    gols_casa: int,
    gols_fora: int,
    fator_k: float = FATOR_K,
) -> tuple[float, float]:
    """Atualiza os ratings das duas seleções após uma partida."""

    validar_parametros_elo(RATING_INICIAL, fator_k)

    if any(
        isinstance(gols, bool)
        or not isinstance(gols, int)
        or gols < 0
        for gols in (gols_casa, gols_fora)
    ):
        raise ValueError("Placar inválido.")

    esperado_casa = probabilidade_esperada_elo(
        rating_casa,
        rating_fora,
    )
    esperado_fora = 1.0 - esperado_casa

    if gols_casa > gols_fora:
        resultado_casa = 1.0
    elif gols_casa < gols_fora:
        resultado_casa = 0.0
    else:
        resultado_casa = 0.5

    resultado_fora = 1.0 - resultado_casa

    novo_rating_casa = (
        rating_casa
        + fator_k * (resultado_casa - esperado_casa)
    )

    novo_rating_fora = (
        rating_fora
        + fator_k * (resultado_fora - esperado_fora)
    )

    return novo_rating_casa, novo_rating_fora



def calcular_ratings_elo(
    partidas: Iterable[RegistroPartida],
    rating_inicial: float = RATING_INICIAL,
    fator_k: float = FATOR_K,
    data_fim: date | None = None,
) -> dict[str, float]:
    """Calcula ratings Elo até uma data de referência, inclusive."""

    validar_parametros_elo(rating_inicial, fator_k)

    if data_fim is not None and not isinstance(data_fim, date):
        raise ValueError("Data final inválida.")

    ratings: dict[str, float] = {}

    # O CSV não possui horário das partidas.
    # Partidas no mesmo dia usam desempate determinístico.
    partidas_ordenadas = sorted(
        (
            partida
            for partida in partidas
            if data_fim is None or partida.data <= data_fim
        ),
        key=lambda partida: (
            partida.data,
            partida.selecao_casa,
            partida.selecao_fora,
            partida.competicao,
            partida.gols_casa,
            partida.gols_fora,
        ),
    )

    for partida in partidas_ordenadas:
        casa = partida.selecao_casa
        fora = partida.selecao_fora

        rating_casa = ratings.get(casa, rating_inicial)
        rating_fora = ratings.get(fora, rating_inicial)

        novo_casa, novo_fora = atualizar_ratings_elo(
            rating_casa=rating_casa,
            rating_fora=rating_fora,
            gols_casa=partida.gols_casa,
            gols_fora=partida.gols_fora,
            fator_k=fator_k,
        )

        ratings[casa] = novo_casa
        ratings[fora] = novo_fora

    return ratings
