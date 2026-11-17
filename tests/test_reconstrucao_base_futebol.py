"""Testes da recuperação independente da base histórica."""

import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from scripts import reconstruir_base_futebol as modulo


class TestReconstrucaoBaseFutebol(unittest.TestCase):

    def setUp(self):
        self.diretorio_temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self.diretorio_temporario.cleanup)

        self.dados = Path(self.diretorio_temporario.name) / "data"

        self.snapshot = (
            self.dados
            / "snapshots"
            / "international_results_b0948cb.zip"
        )

        self.snapshot.parent.mkdir(parents=True)

    def test_recupera_snapshot_sem_internet(self):
        snapshot_original = (
            modulo.RAIZ
            / "data"
            / "snapshots"
            / "international_results_b0948cb.zip"
        )

        shutil.copy2(snapshot_original, self.snapshot)

        with (
            patch.object(modulo, "DADOS", self.dados),
            patch.object(
                modulo,
                "urlopen",
                side_effect=AssertionError(
                    "O teste não pode acessar a internet."
                ),
            ),
        ):
            destino = modulo.obter_base_original()

        self.assertTrue(destino.exists())

        self.assertEqual(
            modulo.calcular_sha256(destino),
            modulo.SHA256_ESPERADO,
        )

    def test_rejeita_snapshot_com_dados_alterados(self):
        with zipfile.ZipFile(self.snapshot, "w") as pacote:
            pacote.writestr(
                "international_results.csv",
                b"Dados incorretos",
            )

        with (
            patch.object(modulo, "DADOS", self.dados),
            patch.object(
                modulo,
                "urlopen",
                side_effect=AssertionError(
                    "O teste não pode acessar a internet."
                ),
            ),
        ):
            with self.assertRaisesRegex(
                ValueError,
                "SHA-256",
            ):
                modulo.obter_base_original()

        self.assertFalse(
            (
                self.dados
                / "raw"
                / "international_results.csv"
            ).exists()
        )


if __name__ == "__main__":
    unittest.main()
