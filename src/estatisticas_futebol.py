"""Estatísticas históricas de seleções nacionais."""

from dataclasses import dataclass
from datetime import date
from typing import Iterable

from src.dados_futebol import RegistroPartida


@dataclass(frozen=True)
class EstatisticasSelecao:
    selecao: str
    jogos: int
    vitorias: int
    empates: int
    derrotas: int
    gols_marcados: int
    gols_sofridos: int

    @property
    def saldo_gols(self) -> int:
        return self.gols_marcados - self.gols_sofridos

    @property
    def pontos(self) -> int:
        return self.vitorias * 3 + self.empates

    @property
    def aproveitamento(self) -> float:
        if self.jogos == 0:
            return 0.0

        return self.pontos / (self.jogos * 3) * 100


def calcular_estatisticas_selecao(
    partidas: Iterable[RegistroPartida],
    selecao: str,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    competicao: str | None = None,
) -> EstatisticasSelecao:
    """Calcula estatísticas a partir de partidas registradas."""

    if not isinstance(selecao, str) or not selecao.strip():
        raise ValueError("Informe uma seleção válida.")

    selecao = selecao.strip()

    if (
        data_inicio is not None
        and data_fim is not None
        and data_inicio > data_fim
    ):
        raise ValueError(
            "A data inicial não pode ser posterior à final."
        )

    jogos = 0
    vitorias = 0
    empates = 0
    derrotas = 0
    gols_marcados = 0
    gols_sofridos = 0

    for partida in partidas:
        if data_inicio and partida.data < data_inicio:
            continue

        if data_fim and partida.data > data_fim:
            continue

        if (
            competicao is not None
            and partida.competicao.casefold()
            != competicao.strip().casefold()
        ):
            continue

        if partida.selecao_casa == selecao:
            gols_favor = partida.gols_casa
            gols_contra = partida.gols_fora

        elif partida.selecao_fora == selecao:
            gols_favor = partida.gols_fora
            gols_contra = partida.gols_casa

        else:
            continue

        jogos += 1
        gols_marcados += gols_favor
        gols_sofridos += gols_contra

        if gols_favor > gols_contra:
            vitorias += 1
        elif gols_favor < gols_contra:
            derrotas += 1
        else:
            empates += 1

    return EstatisticasSelecao(
        selecao=selecao,
        jogos=jogos,
        vitorias=vitorias,
        empates=empates,
        derrotas=derrotas,
        gols_marcados=gols_marcados,
        gols_sofridos=gols_sofridos,
    )
