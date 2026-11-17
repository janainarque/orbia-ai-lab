"""Ranking histórico de seleções baseado em partidas reais."""

from collections import defaultdict
from datetime import date
from typing import Iterable

from src.dados_futebol import RegistroPartida
from src.estatisticas_futebol import EstatisticasSelecao


def gerar_ranking_selecoes(
    partidas: Iterable[RegistroPartida],
    data_inicio: date | None = None,
    data_fim: date | None = None,
    competicao: str | None = None,
    minimo_jogos: int = 10,
) -> list[EstatisticasSelecao]:
    """Gera ranking descritivo com uma passagem pelas partidas."""

    if (
        not isinstance(minimo_jogos, int)
        or isinstance(minimo_jogos, bool)
        or minimo_jogos < 1
    ):
        raise ValueError("O mínimo de jogos deve ser positivo.")

    if (
        data_inicio is not None
        and data_fim is not None
        and data_inicio > data_fim
    ):
        raise ValueError("Período inválido.")

    if competicao is not None:
        if not isinstance(competicao, str) or not competicao.strip():
            raise ValueError("Competição inválida.")
        competicao = competicao.strip().casefold()

    estatisticas = defaultdict(
        lambda: {
            "jogos": 0,
            "vitorias": 0,
            "empates": 0,
            "derrotas": 0,
            "gols_marcados": 0,
            "gols_sofridos": 0,
        }
    )

    for partida in partidas:
        if data_inicio and partida.data < data_inicio:
            continue

        if data_fim and partida.data > data_fim:
            continue

        if (
            competicao is not None
            and partida.competicao.casefold() != competicao
        ):
            continue

        confrontos = (
            (
                partida.selecao_casa,
                partida.gols_casa,
                partida.gols_fora,
            ),
            (
                partida.selecao_fora,
                partida.gols_fora,
                partida.gols_casa,
            ),
        )

        for selecao, gols_favor, gols_contra in confrontos:
            dados = estatisticas[selecao]

            dados["jogos"] += 1
            dados["gols_marcados"] += gols_favor
            dados["gols_sofridos"] += gols_contra

            if gols_favor > gols_contra:
                dados["vitorias"] += 1
            elif gols_favor < gols_contra:
                dados["derrotas"] += 1
            else:
                dados["empates"] += 1

    ranking = [
        EstatisticasSelecao(selecao=selecao, **dados)
        for selecao, dados in estatisticas.items()
        if dados["jogos"] >= minimo_jogos
    ]

    ranking.sort(
        key=lambda item: (
            -item.aproveitamento,
            -item.jogos,
            -item.saldo_gols,
            -item.gols_marcados,
            item.selecao,
        )
    )

    return ranking
