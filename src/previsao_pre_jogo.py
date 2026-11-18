"""Geração de registros pré-jogo para validação temporal do Elo."""

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from itertools import groupby

from src.dados_futebol import RegistroPartida
from src.elo_futebol import (
    FATOR_K,
    RATING_INICIAL,
    atualizar_ratings_elo,
    probabilidade_esperada_elo,
    validar_parametros_elo,
)

from src.probabilidades_futebol import (
    estimar_probabilidades_resultado,
)

@dataclass(frozen=True)
class RegistroPreJogo:
    data: date
    selecao_casa: str
    selecao_fora: str
    competicao: str
    rating_casa: float
    rating_fora: float
    pontuacao_esperada_casa: float
    prob_vitoria: float
    prob_empate: float
    prob_derrota: float
    resultado: str


def gerar_registros_pre_jogo(
    partidas: Iterable[RegistroPartida],
    rating_inicial: float = RATING_INICIAL,
    fator_k: float = FATOR_K,
) -> list[RegistroPreJogo]:
    """Gera observações usando apenas ratings de dias anteriores.

    Partidas da mesma data compartilham o estado Elo do
    início do dia, pois seus horários reais são desconhecidos.

    Esta função ainda não estima probabilidades de
    vitória, empate e derrota.
    """

    validar_parametros_elo(rating_inicial, fator_k)

    partidas_ordenadas = sorted(
        partidas,
        key=lambda partida: (
            partida.data,
            partida.selecao_casa,
            partida.selecao_fora,
            partida.competicao,
        ),
    )

    ratings: dict[str, float] = {}
    registros: list[RegistroPreJogo] = []

    for _, grupo in groupby(
        partidas_ordenadas,
        key=lambda partida: partida.data,
    ):
        partidas_do_dia = list(grupo)

        # Congela o estado antes de qualquer jogo do dia.
        ratings_inicio_dia = ratings.copy()
        variacoes: dict[str, float] = defaultdict(float)

        for partida in partidas_do_dia:
            casa = partida.selecao_casa
            fora = partida.selecao_fora

            rating_casa = ratings_inicio_dia.get(
                casa, rating_inicial
            )
            rating_fora = ratings_inicio_dia.get(
                fora, rating_inicial
            )

            esperado = probabilidade_esperada_elo(
                rating_casa, rating_fora
            )
            
            probabilidades = estimar_probabilidades_resultado(
                rating_casa,
                rating_fora,
            )

            if partida.gols_casa > partida.gols_fora:
                resultado = "V"
            elif partida.gols_casa < partida.gols_fora:
                resultado = "D"
            else:
                resultado = "E"

            registros.append(
                RegistroPreJogo(
                    data=partida.data,
                    selecao_casa=casa,
                    selecao_fora=fora,
                    competicao=partida.competicao,
                    rating_casa=rating_casa,
                    rating_fora=rating_fora,
                    pontuacao_esperada_casa=esperado,
                    prob_vitoria=probabilidades.vitoria,
                    prob_empate=probabilidades.empate,
                    prob_derrota=probabilidades.derrota,
                    resultado=resultado,
                )
            )
            
            novo_casa, novo_fora = atualizar_ratings_elo(
                rating_casa,
                rating_fora,
                partida.gols_casa,
                partida.gols_fora,
                fator_k=fator_k,
            )

            variacoes[casa] += novo_casa - rating_casa
            variacoes[fora] += novo_fora - rating_fora

        # Atualiza somente depois de calcular todos os
        # registros pré-jogo da mesma data.
        for selecao, variacao in variacoes.items():
            rating_anterior = ratings_inicio_dia.get(
                selecao, rating_inicial
            )
            ratings[selecao] = rating_anterior + variacao

    return registros
