"""Testes da auditoria de qualidade dos dados."""

import csv
import tempfile
import unittest
from pathlib import Path

from src.qualidade_futebol import (
    auditar_resultados,
    exportar_csv,
)


COLUNAS = [
    "date",
    "home_team",
    "away_team",
    "home_score",
    "away_score",
    "tournament",
]


def partida(data, casa, fora, gols_casa, gols_fora):
    return {
        "date": data,
        "home_team": casa,
        "away_team": fora,
        "home_score": str(gols_casa),
        "away_score": str(gols_fora),
        "tournament": "Friendly",
    }


class TestQualidadeFutebol(unittest.TestCase):

    def setUp(self):
        temporario = tempfile.TemporaryDirectory()
        self.addCleanup(temporario.cleanup)

        self.pasta = Path(temporario.name)
        self.origem = self.pasta / "partidas.csv"

    def escrever(self, registros):
        exportar_csv(
            self.origem,
            registros,
            COLUNAS,
        )

    def test_base_sem_conflitos(self):
        self.escrever([
            partida("2024-01-01", "Brasil", "Argentina", 2, 1),
            partida("2024-01-02", "Franca", "Espanha", 1, 1),
        ])

        resultado = auditar_resultados(self.origem)

        self.assertEqual(resultado["total"], 2)
        self.assertEqual(len(resultado["validos"]), 2)
        self.assertEqual(len(resultado["conflitantes"]), 0)
        self.assertEqual(resultado["grupos_conflitantes"], 0)

    def test_placares_conflitantes(self):
        self.escrever([
            partida("1974-02-17", "Tahiti", "New Caledonia", 2, 1),
            partida("1974-02-17", "Tahiti", "New Caledonia", 1, 2),
        ])

        resultado = auditar_resultados(self.origem)

        self.assertEqual(len(resultado["validos"]), 0)
        self.assertEqual(len(resultado["conflitantes"]), 2)
        self.assertEqual(resultado["grupos_conflitantes"], 1)

    def test_duplicacao_identica(self):
        registro = partida(
            "2024-01-01", "Brasil", "Argentina", 2, 1
        )

        self.escrever([registro, registro.copy()])

        resultado = auditar_resultados(self.origem)

        self.assertEqual(len(resultado["conflitantes"]), 2)
        self.assertEqual(resultado["grupos_conflitantes"], 1)

    def test_exportacao_preserva_registros(self):
        registros = [
            partida("2024-01-01", "Brasil", "Argentina", 2, 1),
        ]

        self.escrever(registros)

        with self.origem.open(
            "r", encoding="utf-8", newline=""
        ) as arquivo:
            recuperados = list(csv.DictReader(arquivo))

        self.assertEqual(recuperados, registros)


if __name__ == "__main__":
    unittest.main()
