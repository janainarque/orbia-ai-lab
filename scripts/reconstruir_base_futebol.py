"""Reconstrói a base histórica do Orbia Intelligence V6.1."""

import hashlib
import os
import tempfile
import zipfile
from pathlib import Path
from urllib.request import urlopen

from src.importacao_futebol import importar_resultados
from src.qualidade_futebol import (
    auditar_resultados,
    exportar_csv,
)


RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "data"

COMMIT_FONTE = (
    "b0948cb558c927c357db4067eac5b37b96d0e4bb"
)

SHA256_ESPERADO = (
    "09AAC809E317F3004C69720A38ADDB65"
    "6C49EBB19F1937DEAB96F96E3362257A"
)

URL_FONTE = (
    "https://raw.githubusercontent.com/"
    "martj42/international_results/"
    f"{COMMIT_FONTE}/results.csv"
)


def calcular_sha256(caminho):
    resumo = hashlib.sha256()

    with Path(caminho).open("rb") as arquivo:
        for bloco in iter(
            lambda: arquivo.read(1024 * 1024), b""
        ):
            resumo.update(bloco)

    return resumo.hexdigest().upper()



def obter_base_original():
    destino = DADOS / "raw" / "international_results.csv"
    snapshot = (
        DADOS / "snapshots"
        / "international_results_b0948cb.zip"
    )

    destino.parent.mkdir(parents=True, exist_ok=True)

    # 1. Utiliza a base local quando ela já existe.
    if destino.exists():
        if calcular_sha256(destino) != SHA256_ESPERADO:
            raise ValueError(
                "O CSV local não corresponde à versão esperada."
            )

        print("Base original encontrada e verificada.")
        return destino

    temporario = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=destino.parent,
            delete=False,
        ) as arquivo:
            temporario = Path(arquivo.name)

            # 2. Recupera a base do snapshot próprio.
            if snapshot.exists():
                with zipfile.ZipFile(snapshot) as pacote:
                    if pacote.namelist() != [
                        "international_results.csv"
                    ]:
                        raise ValueError(
                            "O snapshot possui conteúdo inesperado."
                        )

                    with pacote.open(
                        "international_results.csv"
                    ) as origem:
                        while bloco := origem.read(1024 * 1024):
                            arquivo.write(bloco)

                origem_dados = "snapshot local"

            # 3. Recorre à fonte externa se não houver snapshot.
            else:
                with urlopen(URL_FONTE, timeout=60) as resposta:
                    while bloco := resposta.read(1024 * 1024):
                        arquivo.write(bloco)

                origem_dados = "repositório original"

        # A integridade é obrigatória em qualquer cenário.
        if calcular_sha256(temporario) != SHA256_ESPERADO:
            raise ValueError(
                "Falha na verificação SHA-256 da base."
            )

        os.replace(temporario, destino)

        print(
            f"Base recuperada de {origem_dados} "
            "e verificada."
        )

    finally:
        if temporario is not None:
            temporario.unlink(missing_ok=True)

    return destino


def reconstruir():
    origem = obter_base_original()

    auditoria = auditar_resultados(origem)

    if (
        auditoria["total"] != 49940
        or len(auditoria["validos"]) != 49938
        or len(auditoria["conflitantes"]) != 2
        or auditoria["grupos_conflitantes"] != 1
    ):
        raise ValueError(
            "Auditoria diferente da referência da V6.1."
        )

    base_filtrada = (
        DADOS / "processed"
        / "international_results_sem_conflitos.csv"
    )

    quarentena = (
        DADOS / "quarantine"
        / "international_results_conflitos.csv"
    )

    base_orbia = (
        DADOS / "processed" / "partidas_orbia.csv"
    )

    exportar_csv(
        base_filtrada,
        auditoria["validos"],
        auditoria["colunas"],
    )

    exportar_csv(
        quarentena,
        auditoria["conflitantes"],
        auditoria["colunas"],
    )

    total_importado = importar_resultados(
        base_filtrada,
        base_orbia,
    )

    if total_importado != 49938:
        raise ValueError(
            "Quantidade importada diferente da esperada."
        )

    print("\nReconstrução concluída!")
    print("Registros originais:", auditoria["total"])
    print("Partidas validadas:", total_importado)
    print(
        "Registros em quarentena:",
        len(auditoria["conflitantes"]),
    )
    print("SHA-256 verificado:", SHA256_ESPERADO)


if __name__ == "__main__":
    reconstruir()
