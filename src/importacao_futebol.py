"""Importação segura de resultados internacionais para o Orbia."""

import csv
import os
import tempfile
from pathlib import Path

from src.dados_futebol import carregar_partidas


FONTE_DADOS = (
    "https://github.com/martj42/international_results"
)

COLUNAS_ORIGINAIS = {
    "date",
    "home_team",
    "away_team",
    "home_score",
    "away_score",
    "tournament",
}

COLUNAS_ORBIA = [
    "data",
    "selecao_casa",
    "selecao_fora",
    "gols_casa",
    "gols_fora",
    "competicao",
    "fonte_url",
]


def importar_resultados(origem, destino):
    """Importa dados com validação e substituição atômica."""

    origem = Path(origem)
    destino = Path(destino)

    if origem.resolve() == destino.resolve():
        raise ValueError(
            "Origem e destino devem ser arquivos diferentes."
        )

    destino.parent.mkdir(parents=True, exist_ok=True)

    temporario = None

    try:
        with origem.open(
            "r", encoding="utf-8-sig", newline=""
        ) as arquivo_origem:

            leitor = csv.DictReader(arquivo_origem)

            if not leitor.fieldnames or not (
                COLUNAS_ORIGINAIS.issubset(leitor.fieldnames)
            ):
                raise ValueError(
                    "O arquivo original não possui "
                    "as colunas esperadas."
                )

            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="",
                dir=destino.parent,
                prefix=f".{destino.name}.",
                suffix=".tmp",
                delete=False,
            ) as arquivo_temporario:

                temporario = Path(arquivo_temporario.name)

                escritor = csv.DictWriter(
                    arquivo_temporario,
                    fieldnames=COLUNAS_ORBIA,
                )

                escritor.writeheader()

                for linha in leitor:
                    escritor.writerow({
                        "data": linha["date"],
                        "selecao_casa": linha["home_team"],
                        "selecao_fora": linha["away_team"],
                        "gols_casa": linha["home_score"],
                        "gols_fora": linha["away_score"],
                        "competicao": linha["tournament"],
                        "fonte_url": FONTE_DADOS,
                    })

        # Valida todo o conteúdo antes de publicar.
        partidas = carregar_partidas(temporario)

        # Substitui o destino somente após validação.
        os.replace(temporario, destino)

        return len(partidas)

    finally:
        # Remove o temporário em caso de erro.
        if temporario is not None:
            temporario.unlink(missing_ok=True)
