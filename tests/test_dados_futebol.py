"""Testes da fundação de dados de futebol."""

import tempfile
import unittest
from pathlib import Path

from src.dados_futebol import carregar_partidas


CABECALHO = (
    "data,selecao_casa,selecao_fora,gols_casa,"
    "gols_fora,competicao,fonte_url\n"
)

# Registro sintético utilizado exclusivamente nos testes.
REGISTRO = (
    "2024-01-15,Brasil,Argentina,2,1,"
    "Amistoso,https://example.org/partida\n"
)


class TestDadosFutebol(unittest.TestCase):

    def setUp(self):
        self.diretorio = tempfile.TemporaryDirectory()
        self.addCleanup(self.diretorio.cleanup)

        self.arquivo = (
            Path(self.diretorio.name) / "partidas.csv"
        )

    def carregar_csv(self, conteudo):
        self.arquivo.write_text(
            conteudo,
            encoding="utf-8",
        )
        return carregar_partidas(self.arquivo)

    def test_carregar_partida_valida(self):
        partidas = self.carregar_csv(
            CABECALHO + REGISTRO
        )

        self.assertEqual(len(partidas), 1)
        self.assertEqual(
            partidas[0].selecao_casa,
            "Brasil",
        )
        self.assertEqual(partidas[0].gols_casa, 2)

    def test_rejeitar_placar_negativo(self):
        registro = REGISTRO.replace(
            ",2,1,",
            ",-1,1,",
        )

        with self.assertRaises(ValueError):
            self.carregar_csv(
                CABECALHO + registro
            )

    def test_rejeitar_data_invalida(self):
        registro = REGISTRO.replace(
            "2024-01-15",
            "2024-13-45",
        )

        with self.assertRaises(ValueError):
            self.carregar_csv(
                CABECALHO + registro
            )

    def test_rejeitar_partida_duplicada(self):
        with self.assertRaises(ValueError):
            self.carregar_csv(
                CABECALHO + REGISTRO + REGISTRO
            )

    def test_rejeitar_fonte_ausente(self):
        registro = REGISTRO.replace(
            "https://example.org/partida",
            "",
        )

        with self.assertRaises(ValueError):
            self.carregar_csv(
                CABECALHO + registro
            )

    def test_rejeitar_colunas_ausentes(self):
        with self.assertRaises(ValueError):
            self.carregar_csv(
                "data,selecao_casa\n"
                "2024-01-15,Brasil\n"
            )


if __name__ == "__main__":
    unittest.main()
