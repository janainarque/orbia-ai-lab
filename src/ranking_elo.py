"""Ranking histórico de seleções baseado no motor Elo do Orbia."""

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date

from src.dados_futebol import RegistroPartida
from src.elo_futebol import calcular_ratings_elo


@dataclass(frozen=True)
class PosicaoRankingElo:
    """Representa uma seleção no ranking Elo."""

    selecao: str
    rating: float
    jogos: int


def gerar_ranking_elo(
    partidas: Iterable[RegistroPartida],
    data_fim: date | None = None,
    minimo_jogos: int = 20,
    janela_atividade_dias: int | None = None,
) -> list[PosicaoRankingElo]:
    """Gera ranking Elo com corte temporal e atividade opcional."""

    if (
        isinstance(minimo_jogos, bool)
        or not isinstance(minimo_jogos, int)
        or minimo_jogos < 1
    ):
        raise ValueError("O mínimo de jogos deve ser positivo.")

    if data_fim is not None and not isinstance(data_fim, date):
        raise ValueError("Data final inválida.")

    if janela_atividade_dias is not None:
        if (
            isinstance(janela_atividade_dias, bool)
            or not isinstance(janela_atividade_dias, int)
            or janela_atividade_dias < 1
        ):
            raise ValueError("Janela de atividade inválida.")

    # Materializa o histórico e respeita o corte temporal.
    partidas_validas = [
        partida
        for partida in partidas
        if data_fim is None or partida.data <= data_fim
    ]

    if not partidas_validas:
        return []

    # Na ausência de corte explícito, usa a última data da base.
    data_referencia = data_fim or max(
        partida.data for partida in partidas_validas
    )

    ratings = calcular_ratings_elo(partidas_validas)

    jogos = Counter()
    ultimos_jogos: dict[str, date] = {}

    for partida in partidas_validas:
        for selecao in (
            partida.selecao_casa,
            partida.selecao_fora,
        ):
            jogos[selecao] += 1

            ultima_data = ultimos_jogos.get(selecao)

            if ultima_data is None or partida.data > ultima_data:
                ultimos_jogos[selecao] = partida.data

    ranking = []

    for selecao, rating in ratings.items():
        if jogos[selecao] < minimo_jogos:
            continue

        if janela_atividade_dias is not None:
            dias_sem_jogar = (
                data_referencia - ultimos_jogos[selecao]
            ).days

            if dias_sem_jogar > janela_atividade_dias:
                continue

        ranking.append(
            PosicaoRankingElo(
                selecao=selecao,
                rating=rating,
                jogos=jogos[selecao],
            )
        )

    ranking.sort(
        key=lambda item: (
            -item.rating,
            -item.jogos,
            item.selecao,
        )
    )

    return ranking
