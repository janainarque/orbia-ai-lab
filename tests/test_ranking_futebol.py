"""Testes do ranking histórico de seleções."""

import unittest
from datetime import date

from src.dados_futebol import RegistroPartida
from src.ranking_futebol import gerar_ranking_selecoes


def partida(data, casa, fora, gols_casa, gols_fora, competicao="Friendly"):
    return RegistroPartida(
        data=date.fromisoformat(data),
        selecao_casa=casa,
        selecao_fora=fora,
        gols_casa=gols_casa,
        gols_fora=gols_fora,
        competicao=competicao,
        fonte_url="https://example.com/dados",
    )


class TestRankingFutebol(unittest.TestCase):

    def setUp(self):
        self.partidas = [
            partida("2024-01-10", "Brazil", "Argentina", 2, 1),
            partida("2024-02-10", "France", "Brazil", 1, 1),
            partida("2024-03-10", "Argentina", "Brazil", 3, 0),
            partida("2025-01-10", "Brazil", "France", 3, 0, "World Cup"),
            partida("2025-02-10", "Spain", "France", 1, 0),
        ]

    def test_ordenacao_por_aproveitamento(self):
        ranking = gerar_ranking_selecoes(
            self.partidas, minimo_jogos=1
        )

        self.assertEqual(
            [item.selecao for item in ranking],
            ["Spain", "Brazil", "Argentina", "France"],
        )

    def test_minimo_de_jogos(self):
        ranking = gerar_ranking_selecoes(
            self.partidas, minimo_jogos=2
        )

        self.assertEqual(
            [item.selecao for item in ranking],
            ["Brazil", "Argentina", "France"],
        )

    def test_estatisticas_brasil(self):
        ranking = gerar_ranking_selecoes(
            self.partidas, minimo_jogos=1
        )
        brasil = next(
            item for item in ranking if item.selecao == "Brazil"
        )

        self.assertEqual(brasil.jogos, 4)
        self.assertEqual(brasil.vitorias, 2)
        self.assertEqual(brasil.empates, 1)
        self.assertEqual(brasil.derrotas, 1)
        self.assertEqual(brasil.saldo_gols, 1)
        self.assertEqual(brasil.pontos, 7)

    def test_filtro_competicao(self):
        ranking = gerar_ranking_selecoes(
            self.partidas,
            competicao=" world cup ",
            minimo_jogos=1,
        )

        self.assertEqual(
            [item.selecao for item in ranking],
            ["Brazil", "France"],
        )

    def test_filtro_periodo(self):
        ranking = gerar_ranking_selecoes(
            self.partidas,
            data_inicio=date(2025, 1, 1),
            data_fim=date(2025, 1, 31),
            minimo_jogos=1,
        )

        self.assertEqual(
            [item.selecao for item in ranking],
            ["Brazil", "France"],
        )

    def test_desempate_por_quantidade_de_jogos(self):
        partidas = [
            partida("2024-01-10", "Brazil", "Argentina", 1, 0),
            partida("2024-02-10", "Brazil", "France", 1, 0),
            partida("2024-03-10", "Spain", "Argentina", 1, 0),
        ]

        ranking = gerar_ranking_selecoes(
            partidas, minimo_jogos=1
        )

        self.assertEqual(ranking[0].selecao, "Brazil")
        self.assertEqual(ranking[1].selecao, "Spain")

    def test_aceita_gerador(self):
        ranking = gerar_ranking_selecoes(
            iter(self.partidas), minimo_jogos=1
        )

        self.assertEqual(len(ranking), 4)

    def test_minimo_de_jogos_invalido(self):
        for valor in (0, -1, True, 1.5):
            with self.subTest(valor=valor):
                with self.assertRaises(ValueError):
                    gerar_ranking_selecoes(
                        self.partidas, minimo_jogos=valor
                    )

    def test_periodo_invalido(self):
        with self.assertRaises(ValueError):
            gerar_ranking_selecoes(
                self.partidas,
                data_inicio=date(2025, 1, 1),
                data_fim=date(2024, 1, 1),
            )

    def test_competicao_invalida(self):
        with self.assertRaises(ValueError):
            gerar_ranking_selecoes(
                self.partidas, competicao=" "
            )


if __name__ == "__main__":
    unittest.main()
