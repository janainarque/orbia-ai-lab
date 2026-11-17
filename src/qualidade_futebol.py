"""Auditoria de duplicidades na base histórica de futebol."""

import csv
from collections import Counter
from pathlib import Path


CAMPOS_CHAVE = (
    "date",
    "home_team",
    "away_team",
    "tournament",
)


def identificar_chave(registro):
    return tuple(registro[campo] for campo in CAMPOS_CHAVE)


def auditar_resultados(caminho):
    """Separa registros sem conflito dos registros ambíguos."""

    caminho = Path(caminho)

    with caminho.open(
        "r", encoding="utf-8-sig", newline=""
    ) as arquivo:
        leitor = csv.DictReader(arquivo)

        campos = leitor.fieldnames

        if not campos or not set(CAMPOS_CHAVE).issubset(campos):
            raise ValueError(
                "O CSV não possui as colunas necessárias."
            )

        registros = list(leitor)

    contagens = Counter(
        identificar_chave(registro)
        for registro in registros
    )

    registros_validos = []
    registros_conflitantes = []

    for registro in registros:
        chave = identificar_chave(registro)

        if contagens[chave] > 1:
            registros_conflitantes.append(registro)
        else:
            registros_validos.append(registro)

    grupos_conflitantes = sum(
        1 for quantidade in contagens.values()
        if quantidade > 1
    )

    return {
        "total": len(registros),
        "validos": registros_validos,
        "conflitantes": registros_conflitantes,
        "grupos_conflitantes": grupos_conflitantes,
        "colunas": campos,
    }


def exportar_csv(caminho, registros, colunas):
    """Exporta registros mantendo o formato original."""

    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)

    with caminho.open(
        "w", encoding="utf-8", newline=""
    ) as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=colunas,
        )
        escritor.writeheader()
        escritor.writerows(registros)
