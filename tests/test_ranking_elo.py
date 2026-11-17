"""Testes automatizados do ranking Elo do Orbia."""

import unittest
from datetime import date

from src.dados_futebol import RegistroPartida
from src.elo_futebol import calcular_ratings_elo
from src.ranking_elo import gerar_ranking_elo


def criar_partida(data, casa, fora, gols_casa, gols_fora):
    return RegistroPartida(
        data=data,
        selecao_casa=casa,
        selecao_fora=fora,
        gols_casa=gols_casa,
        gols_fora=gols_fora,
        competicao="Amistoso de teste",
        fonte_url="https://example.com/teste",
    )


class TestRankingElo(unittest.TestCase):

    def setUp(self):
        self.partidas = [
            criar_partida(
                date(2024, 1, 10),
                "Brasil", "Argentina", 2, 1,
            ),
            criar_partida(
                date(2024, 2, 10),
                "Argentina", "Franca", 1, 0,
            ),
            criar_partida(
                date(2024, 3, 10),
                "Franca", "Brasil", 0, 0,
            ),
        ]

    def test_ranking_retorna_tres_selecoes(self):
        ranking = gerar_ranking_elo(
            self.partidas,
            minimo_jogos=1,
        )

        self.assertEqual(len(ranking), 3)

    def test_ranking_ordenado_por_rating(self):
        ranking = gerar_ranking_elo(
            self.partidas,
            minimo_jogos=1,
        )

        ratings = [item.rating for item in ranking]

        self.assertEqual(
            ratings,
            sorted(ratings, reverse=True),
        )

    def test_brasil_primeiro_no_cenario(self):
        ranking = gerar_ranking_elo(
            self.partidas,
            minimo_jogos=1,
        )

        self.assertEqual(ranking[0].selecao, "Brasil")

    def test_quantidade_de_jogos(self):
        ranking = gerar_ranking_elo(
            self.partidas,
            minimo_jogos=1,
        )

        for item in ranking:
            self.assertEqual(item.jogos, 2)

    def test_ratings_iguais_ao_motor_elo(self):
        ranking = gerar_ranking_elo(
            self.partidas,
            minimo_jogos=1,
        )

        ratings = calcular_ratings_elo(self.partidas)

        for item in ranking:
            self.assertAlmostEqual(
                item.rating,
                ratings[item.selecao],
            )

    def test_minimo_de_jogos(self):
        ranking = gerar_ranking_elo(
            self.partidas,
            minimo_jogos=3,
        )

        self.assertEqual(ranking, [])

    def test_corte_temporal(self):
        ranking = gerar_ranking_elo(
            self.partidas,
            data_fim=date(2024, 1, 10),
            minimo_jogos=1,
        )

        self.assertEqual(len(ranking), 2)
        self.assertEqual(ranking[0].selecao, "Brasil")
        self.assertAlmostEqual(ranking[0].rating, 1510)
        self.assertEqual(ranking[0].jogos, 1)

    def test_sem_partidas_ate_data(self):
        ranking = gerar_ranking_elo(
            self.partidas,
            data_fim=date(2023, 12, 31),
            minimo_jogos=1,
        )

        self.assertEqual(ranking, [])

    def test_aceita_gerador(self):
        partidas = (partida for partida in self.partidas)

        ranking = gerar_ranking_elo(
            partidas,
            minimo_jogos=1,
        )

        self.assertEqual(len(ranking), 3)

    def test_rejeita_minimo_invalido(self):
        for minimo in (0, -1, True, 1.5):
            with self.subTest(minimo=minimo):
                with self.assertRaises(ValueError):
                    gerar_ranking_elo(
                        self.partidas,
                        minimo_jogos=minimo,
                    )

    def test_rejeita_data_invalida(self):
        with self.assertRaises(ValueError):
            gerar_ranking_elo(
                self.partidas,
                data_fim="2024-01-10",
            )

    def test_desempate_alfabetico(self):
        partidas = [
            criar_partida(
                date(2024, 1, 1),
                "Brasil", "Argentina", 1, 1,
            ),
            criar_partida(
                date(2024, 1, 2),
                "Espanha", "Franca", 1, 1,
            ),
        ]

        ranking = gerar_ranking_elo(
            partidas,
            minimo_jogos=1,
        )

        nomes = [item.selecao for item in ranking]

        self.assertEqual(
            nomes,
            ["Argentina", "Brasil", "Espanha", "Franca"],
        )


    def test_filtro_atividade_remove_selecao_inativa(self):
        partidas = [
            criar_partida(
                date(2020, 1, 1),
                "Brasil", "Argentina", 2, 0,
            ),
            criar_partida(
                date(2024, 12, 1),
                "Brasil", "Franca", 1, 0,
            ),
        ]

        ranking = gerar_ranking_elo(
            partidas,
            data_fim=date(2024, 12, 31),
            minimo_jogos=1,
            janela_atividade_dias=365,
        )

        nomes = {item.selecao for item in ranking}

        self.assertEqual(nomes, {"Brasil", "Franca"})

    def test_sem_filtro_mantem_selecao_inativa(self):
        partidas = [
            criar_partida(
                date(2020, 1, 1),
                "Brasil", "Argentina", 2, 0,
            ),
            criar_partida(
                date(2024, 12, 1),
                "Brasil", "Franca", 1, 0,
            ),
        ]

        ranking = gerar_ranking_elo(
            partidas,
            data_fim=date(2024, 12, 31),
            minimo_jogos=1,
        )

        nomes = {item.selecao for item in ranking}

        self.assertEqual(
            nomes,
            {"Brasil", "Argentina", "Franca"},
        )

    def test_filtro_atividade_nao_altera_rating(self):
        sem_filtro = gerar_ranking_elo(
            self.partidas,
            minimo_jogos=1,
        )

        com_filtro = gerar_ranking_elo(
            self.partidas,
            minimo_jogos=1,
            janela_atividade_dias=365,
        )

        ratings_originais = {
            item.selecao: item.rating
            for item in sem_filtro
        }

        for item in com_filtro:
            self.assertAlmostEqual(
                item.rating,
                ratings_originais[item.selecao],
            )

    def test_filtro_atividade_rejeita_valores_invalidos(self):
        for janela in (0, -1, True, 1.5, "365"):
            with self.subTest(janela=janela):
                with self.assertRaises(ValueError):
                    gerar_ranking_elo(
                        self.partidas,
                        minimo_jogos=1,
                        janela_atividade_dias=janela,
                    )

    def test_filtro_atividade_usa_ultima_data_da_base(self):
        partidas = [
            criar_partida(
                date(2020, 1, 1),
                "Brasil", "Argentina", 2, 0,
            ),
            criar_partida(
                date(2024, 12, 1),
                "Brasil", "Franca", 1, 0,
            ),
        ]

        ranking = gerar_ranking_elo(
            partidas,
            minimo_jogos=1,
            janela_atividade_dias=365,
        )

        nomes = {item.selecao for item in ranking}

        self.assertEqual(nomes, {"Brasil", "Franca"})


if __name__ == "__main__":
    unittest.main()
