"""Evolução histórica dos ratings Elo de seleções."""

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date

from src.dados_futebol import RegistroPartida
from src.elo_futebol import (
    FATOR_K,
    RATING_INICIAL,
    atualizar_ratings_elo,
    validar_parametros_elo,
)


@dataclass(frozen=True)
class PontoEvolucaoElo:
    """Último rating registrado para uma seleção em um ano."""

    ano: int
    selecao: str
    rating: float
    jogos_acumulados: int
    data_ultima_partida: date


def calcular_evolucao_elo(
    partidas: Iterable[RegistroPartida],
    selecoes: Iterable[str],
    data_inicio: date | None = None,
    data_fim: date | None = None,
    rating_inicial: float = RATING_INICIAL,
    fator_k: float = FATOR_K,
) -> list[PontoEvolucaoElo]:
    """Calcula a evolução anual sem descartar o histórico anterior.

    Todas as partidas anteriores à data final participam
    do cálculo Elo. A data inicial restringe apenas os
    pontos apresentados, não o histórico do rating.
    """

    validar_parametros_elo(rating_inicial, fator_k)

    if data_inicio is not None and not isinstance(
        data_inicio, date
    ):
        raise ValueError("Data inicial inválida.")

    if data_fim is not None and not isinstance(
        data_fim, date
    ):
        raise ValueError("Data final inválida.")

    if (
        data_inicio is not None
        and data_fim is not None
        and data_inicio > data_fim
    ):
        raise ValueError(
            "A data inicial não pode superar a data final."
        )

    selecoes_escolhidas = set(selecoes)

    if any(
        not isinstance(nome, str) or not nome.strip()
        for nome in selecoes_escolhidas
    ):
        raise ValueError("Seleção inválida.")

    if not selecoes_escolhidas:
        return []

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

    ratings: dict[str, float] = {}
    jogos = Counter()

    pontos_por_ano: dict[
        tuple[int, str], PontoEvolucaoElo
    ] = {}

    for partida in partidas_ordenadas:
        casa = partida.selecao_casa
        fora = partida.selecao_fora

        rating_casa = ratings.get(
            casa, rating_inicial
        )
        rating_fora = ratings.get(
            fora, rating_inicial
        )

        novo_casa, novo_fora = atualizar_ratings_elo(
            rating_casa,
            rating_fora,
            partida.gols_casa,
            partida.gols_fora,
            fator_k=fator_k,
        )

        ratings[casa] = novo_casa
        ratings[fora] = novo_fora

        jogos[casa] += 1
        jogos[fora] += 1

        # Processamos todo o histórico, mas registramos
        # apenas os anos e as seleções solicitados.
        if (
            data_inicio is not None
            and partida.data < data_inicio
        ):
            continue

        for selecao in (casa, fora):
            if selecao not in selecoes_escolhidas:
                continue

            chave = (partida.data.year, selecao)

            # Cada atualização substitui a anterior
            # dentro do mesmo ano. Assim, preservamos
            # o último rating observado naquele ano.
            pontos_por_ano[chave] = PontoEvolucaoElo(
                ano=partida.data.year,
                selecao=selecao,
                rating=ratings[selecao],
                jogos_acumulados=jogos[selecao],
                data_ultima_partida=partida.data,
            )

    return sorted(
        pontos_por_ano.values(),
        key=lambda ponto: (
            ponto.ano,
            ponto.selecao,
        ),
    )
