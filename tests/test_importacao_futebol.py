"""Testes da importação de resultados internacionais."""

import csv
import tempfile
import unittest
from pathlib import Path

from src.dados_futebol import carregar_partidas
from src.importacao_futebol import (
    FONTE_DADOS,
    importar_resultados,
)


COLUNAS = [
    "date",
    "home_team",
    "away_team",
    "home_score",
    "away_score",
    "tournament",
    "city",
    "country",
    "neutral",
]


def criar_registro(**alteracoes):
    """Cria uma partida sintética para testes."""

    registro = {
        "date": "2024-01-15",
        "home_team": "Brasil",
        "away_team": "Argentina",
        "home_score": "2",
        "away_score": "1",
        "tournament": "Friendly",
        "city": "Brasilia",
        "country": "Brazil",
        "neutral": "FALSE",
    }

    registro.update(alteracoes)
    return registro


class TestImportacaoFutebol(unittest.TestCase):

    def setUp(self):
        temporario = tempfile.TemporaryDirectory()
        self.addCleanup(temporario.cleanup)

        pasta = Path(temporario.name)

        self.origem = pasta / "original.csv"
        self.destino = pasta / "orbia.csv"

    def escrever_origem(self, registros, colunas=None):
        colunas = colunas or COLUNAS

        with self.origem.open(
            "w", encoding="utf-8", newline=""
        ) as arquivo:
            escritor = csv.DictWriter(
                arquivo,
                fieldnames=colunas,
            )
            escritor.writeheader()
            escritor.writerows(registros)

    def test_importar_partida_valida(self):
        self.escrever_origem([criar_registro()])

        quantidade = importar_resultados(
            self.origem, self.destino
        )

        self.assertEqual(quantidade, 1)

        partidas = carregar_partidas(self.destino)

        self.assertEqual(
            partidas[0].selecao_casa, "Brasil"
        )
        self.assertEqual(
            partidas[0].selecao_fora, "Argentina"
        )
        self.assertEqual(partidas[0].gols_casa, 2)
        self.assertEqual(partidas[0].gols_fora, 1)
        self.assertEqual(
            partidas[0].competicao, "Friendly"
        )
        self.assertEqual(
            partidas[0].fonte_url, FONTE_DADOS
        )

    def test_importar_multiplas_partidas(self):
        registros = [
            criar_registro(),
            criar_registro(
                date="2024-01-16",
                home_team="Franca",
                away_team="Espanha",
                home_score="1",
                away_score="1",
            ),
        ]

        self.escrever_origem(registros)

        quantidade = importar_resultados(
            self.origem, self.destino
        )

        self.assertEqual(quantidade, 2)

    def test_rejeitar_colunas_ausentes(self):
        self.escrever_origem(
            [{"date": "2024-01-15"}],
            colunas=["date"],
        )

        with self.assertRaises(ValueError):
            importar_resultados(
                self.origem, self.destino
            )

    def test_rejeitar_placar_invalido(self):
        self.escrever_origem([
            criar_registro(home_score="-2")
        ])

        with self.assertRaises(ValueError):
            importar_resultados(
                self.origem, self.destino
            )

    def test_rejeitar_partidas_duplicadas(self):
        registro = criar_registro()

        self.escrever_origem([
            registro,
            registro.copy(),
        ])

        with self.assertRaises(ValueError):
            importar_resultados(
                self.origem, self.destino
            )

    def test_preservar_arquivo_original(self):
        self.escrever_origem([criar_registro()])

        conteudo_antes = self.origem.read_bytes()

        importar_resultados(
            self.origem, self.destino
        )

        self.assertEqual(
            self.origem.read_bytes(),
            conteudo_antes,
        )

    def test_rejeitar_origem_igual_destino(self):
        self.escrever_origem([criar_registro()])

        with self.assertRaises(ValueError):
            importar_resultados(
                self.origem, self.origem
            )
            
    
    def test_importacao_invalida_preserva_destino(self):
        self.escrever_origem([
            criar_registro(home_score="-2")
        ])

        conteudo_anterior = "arquivo anterior preservado"
        self.destino.write_text(
            conteudo_anterior,
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            importar_resultados(
                self.origem, self.destino
            )

        self.assertEqual(
            self.destino.read_text(encoding="utf-8"),
            conteudo_anterior,
        )

    def test_importacao_invalida_nao_cria_destino(self):
        self.escrever_origem([
            criar_registro(home_score="invalido")
        ])

        with self.assertRaises(ValueError):
            importar_resultados(
                self.origem, self.destino
            )

        self.assertFalse(self.destino.exists())



if __name__ == "__main__":
    unittest.main()
