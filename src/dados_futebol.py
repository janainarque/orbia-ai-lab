"""Leitura e validação de dados históricos de futebol."""

import csv
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit


CAMPOS_OBRIGATORIOS = {
    "data",
    "selecao_casa",
    "selecao_fora",
    "gols_casa",
    "gols_fora",
    "competicao",
    "fonte_url",
}


@dataclass(frozen=True)
class RegistroPartida:
    data: date
    selecao_casa: str
    selecao_fora: str
    gols_casa: int
    gols_fora: int
    competicao: str
    fonte_url: str


def carregar_partidas(caminho: str | Path) -> list[RegistroPartida]:
    """Carrega partidas de um CSV e valida seus registros."""

    partidas = []
    identificadores = set()

    with Path(caminho).open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as arquivo:
        leitor = csv.DictReader(arquivo)

        if not leitor.fieldnames or not CAMPOS_OBRIGATORIOS.issubset(
            leitor.fieldnames
        ):
            raise ValueError(
                "CSV sem as colunas obrigatórias de partidas."
            )

        for numero_linha, linha in enumerate(leitor, start=2):
            try:
                campos = {
                    campo: (linha.get(campo) or "").strip()
                    for campo in CAMPOS_OBRIGATORIOS
                }

                data_texto = campos["data"]

                if not re.fullmatch(
                    r"[0-9]{4}-[0-9]{2}-[0-9]{2}",
                    data_texto,
                ):
                    raise ValueError("Formato de data inválido.")

                data_partida = date.fromisoformat(data_texto)

                casa = campos["selecao_casa"]
                fora = campos["selecao_fora"]
                competicao = campos["competicao"]
                fonte = campos["fonte_url"]

                if not casa or not fora or not competicao:
                    raise ValueError(
                        "Seleções e competição são obrigatórias."
                    )

                if casa.casefold() == fora.casefold():
                    raise ValueError(
                        "Uma seleção não pode enfrentar a si mesma."
                    )

                placares = []

                for campo in ("gols_casa", "gols_fora"):
                    valor = campos[campo]

                    if not re.fullmatch(r"[0-9]+", valor):
                        raise ValueError(
                            f"Placar inválido: {campo}."
                        )

                    placares.append(int(valor))

                endereco = urlsplit(fonte)

                if (
                    endereco.scheme not in ("http", "https")
                    or not endereco.netloc
                ):
                    raise ValueError(
                        "URL da fonte inválida ou ausente."
                    )

                identificador = (
                    data_partida,
                    casa.casefold(),
                    fora.casefold(),
                    competicao.casefold(),
                )

                if identificador in identificadores:
                    raise ValueError("Partida duplicada.")

                identificadores.add(identificador)

                partidas.append(
                    RegistroPartida(
                        data=data_partida,
                        selecao_casa=casa,
                        selecao_fora=fora,
                        gols_casa=placares[0],
                        gols_fora=placares[1],
                        competicao=competicao,
                        fonte_url=fonte,
                    )
                )

            except ValueError as erro:
                raise ValueError(
                    f"Linha {numero_linha}: {erro}"
                ) from erro

    if not partidas:
        raise ValueError("Arquivo sem partidas.")

    return partidas
