"""Testes da evolução histórica Elo do Orbia."""

import unittest
from datetime import date

from src.dados_futebol import RegistroPartida
from src.elo_futebol import calcular_ratings_elo
from src.evolucao_elo import calcular_evolucao_elo


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


class TestEvolucaoElo(unittest.TestCase):

    def setUp(self):
        self.partidas = [
            criar_partida(
                date(2020, 1, 10),
                "Brasil", "Argentina", 2, 0,
            ),
            criar_partida(
                date(2021, 4, 10),
                "Argentina", "Franca", 1, 0,
            ),
            criar_partida(
                date(2021, 12, 10),
                "Franca", "Brasil", 0, 0,
            ),
            criar_partida(
                date(2022, 3, 10),
                "Brasil", "Argentina", 1, 2,
            ),
        ]

    def test_retorna_pontos_historicos(self):
        pontos = calcular_evolucao_elo(
            self.partidas,
            ["Brasil", "Argentina"],
        )

        self.assertEqual(len(pontos), 6)

    def test_primeira_vitoria_atualiza_rating(self):
        pontos = calcular_evolucao_elo(
            self.partidas,
            ["Brasil"],
        )

        primeiro = pontos[0]

        self.assertEqual(primeiro.ano, 2020)
        self.assertAlmostEqual(primeiro.rating, 1510.0)
        self.assertEqual(primeiro.jogos_acumulados, 1)

    def test_rating_final_igual_ao_motor_elo(self):
        pontos = calcular_evolucao_elo(
            self.partidas,
            ["Brasil", "Argentina", "Franca"],
        )

        ratings = calcular_ratings_elo(self.partidas)

        for selecao in ratings:
            pontos_selecao = [
                ponto for ponto in pontos
                if ponto.selecao == selecao
            ]

            ultimo = pontos_selecao[-1]

            self.assertAlmostEqual(
                ultimo.rating,
                ratings[selecao],
            )

    def test_data_inicio_nao_reinicia_rating(self):
        historico_completo = calcular_evolucao_elo(
            self.partidas,
            ["Brasil"],
        )

        historico_recortado = calcular_evolucao_elo(
            self.partidas,
            ["Brasil"],
            data_inicio=date(2022, 1, 1),
        )

        self.assertEqual(len(historico_recortado), 1)

        self.assertAlmostEqual(
            historico_recortado[0].rating,
            historico_completo[-1].rating,
        )

    def test_data_final_exclui_partidas_futuras(self):
        limite = date(2021, 6, 1)

        pontos = calcular_evolucao_elo(
            self.partidas,
            ["Brasil", "Argentina"],
            data_fim=limite,
        )

        self.assertTrue(
            all(
                ponto.data_ultima_partida <= limite
                for ponto in pontos
            )
        )

        ratings_ate_limite = calcular_ratings_elo(
            self.partidas,
            data_fim=limite,
        )

        ultimo_argentina = [
            ponto for ponto in pontos
            if ponto.selecao == "Argentina"
        ][-1]

        self.assertAlmostEqual(
            ultimo_argentina.rating,
            ratings_ate_limite["Argentina"],
        )

    def test_guarda_ultimo_rating_do_ano(self):
        pontos = calcular_evolucao_elo(
            self.partidas,
            ["Brasil"],
        )

        ponto_2021 = next(
            ponto for ponto in pontos
            if ponto.ano == 2021
        )

        self.assertEqual(
            ponto_2021.data_ultima_partida,
            date(2021, 12, 10),
        )

        self.assertEqual(
            ponto_2021.jogos_acumulados,
            2,
        )

    def test_aceita_gerador(self):
        partidas = (
            partida for partida in self.partidas
        )

        pontos = calcular_evolucao_elo(
            partidas,
            ["Brasil"],
        )

        self.assertEqual(len(pontos), 3)

    def test_selecao_sem_partidas(self):
        pontos = calcular_evolucao_elo(
            self.partidas,
            ["Espanha"],
        )

        self.assertEqual(pontos, [])

    def test_rejeita_intervalo_invalido(self):
        with self.assertRaises(ValueError):
            calcular_evolucao_elo(
                self.partidas,
                ["Brasil"],
                data_inicio=date(2023, 1, 1),
                data_fim=date(2022, 1, 1),
            )

    def test_rejeita_parametros_elo_invalidos(self):
        with self.assertRaises(ValueError):
            calcular_evolucao_elo(
                self.partidas,
                ["Brasil"],
                fator_k=0,
            )


if __name__ == "__main__":
    unittest.main()
