"""Testes das estatísticas históricas de futebol."""

import unittest
from datetime import date

from src.dados_futebol import RegistroPartida
from src.estatisticas_futebol import calcular_estatisticas_selecao


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


class TestEstatisticasFutebol(unittest.TestCase):

    def setUp(self):
        self.partidas = [
            partida("2024-01-10", "Brazil", "Argentina", 2, 1),
            partida("2024-02-10", "France", "Brazil", 1, 1),
            partida("2024-03-10", "Argentina", "Brazil", 3, 0),
            partida("2025-01-10", "Brazil", "France", 3, 0, "World Cup"),
        ]

    def test_vitorias_empates_derrotas(self):
        resultado = calcular_estatisticas_selecao(
            self.partidas, "Brazil"
        )

        self.assertEqual(resultado.jogos, 4)
        self.assertEqual(resultado.vitorias, 2)
        self.assertEqual(resultado.empates, 1)
        self.assertEqual(resultado.derrotas, 1)

    def test_gols_e_saldo(self):
        resultado = calcular_estatisticas_selecao(
            self.partidas, "Brazil"
        )

        self.assertEqual(resultado.gols_marcados, 6)
        self.assertEqual(resultado.gols_sofridos, 5)
        self.assertEqual(resultado.saldo_gols, 1)

    def test_pontos_e_aproveitamento(self):
        resultado = calcular_estatisticas_selecao(
            self.partidas, "Brazil"
        )

        self.assertEqual(resultado.pontos, 7)
        self.assertAlmostEqual(
            resultado.aproveitamento,
            7 / 12 * 100,
        )

    def test_partida_como_visitante(self):
        resultado = calcular_estatisticas_selecao(
            [self.partidas[2]], "Brazil"
        )

        self.assertEqual(resultado.jogos, 1)
        self.assertEqual(resultado.derrotas, 1)
        self.assertEqual(resultado.gols_marcados, 0)
        self.assertEqual(resultado.gols_sofridos, 3)

    def test_filtro_data_inicio(self):
        resultado = calcular_estatisticas_selecao(
            self.partidas,
            "Brazil",
            data_inicio=date(2025, 1, 1),
        )

        self.assertEqual(resultado.jogos, 1)
        self.assertEqual(resultado.vitorias, 1)

    def test_filtro_data_fim(self):
        resultado = calcular_estatisticas_selecao(
            self.partidas,
            "Brazil",
            data_fim=date(2024, 2, 10),
        )

        self.assertEqual(resultado.jogos, 2)

    def test_filtro_competicao(self):
        resultado = calcular_estatisticas_selecao(
            self.partidas,
            "Brazil",
            competicao="world cup",
        )

        self.assertEqual(resultado.jogos, 1)
        self.assertEqual(resultado.gols_marcados, 3)

    def test_selecao_sem_partidas(self):
        resultado = calcular_estatisticas_selecao(
            self.partidas, "Spain"
        )

        self.assertEqual(resultado.jogos, 0)
        self.assertEqual(resultado.pontos, 0)
        self.assertEqual(resultado.aproveitamento, 0.0)

    def test_selecao_invalida(self):
        with self.assertRaises(ValueError):
            calcular_estatisticas_selecao(
                self.partidas, " "
            )

    def test_periodo_invalido(self):
        with self.assertRaises(ValueError):
            calcular_estatisticas_selecao(
                self.partidas,
                "Brazil",
                data_inicio=date(2025, 1, 1),
                data_fim=date(2024, 1, 1),
            )

    def test_aceita_gerador_de_partidas(self):
        resultado = calcular_estatisticas_selecao(
            iter(self.partidas), "Brazil"
        )

        self.assertEqual(resultado.jogos, 4)


if __name__ == "__main__":
    unittest.main()
