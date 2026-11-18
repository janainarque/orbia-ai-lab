"""Testes do modelo experimental de probabilidades da V8."""

import math
import unittest

from src.elo_futebol import probabilidade_esperada_elo
from src.probabilidades_futebol import (
    estimar_probabilidades_resultado,
)


class TestProbabilidadesFutebol(unittest.TestCase):

    def test_ratings_iguais(self):
        resultado = estimar_probabilidades_resultado(
            1500, 1500
        )

        self.assertAlmostEqual(resultado.vitoria, 0.375)
        self.assertAlmostEqual(resultado.empate, 0.25)
        self.assertAlmostEqual(resultado.derrota, 0.375)

    def test_probabilidades_somam_um(self):
        resultado = estimar_probabilidades_resultado(
            1800, 1600
        )

        soma = (
            resultado.vitoria
            + resultado.empate
            + resultado.derrota
        )

        self.assertAlmostEqual(soma, 1.0)

    def test_selecao_mais_forte_tem_maior_chance(self):
        resultado = estimar_probabilidades_resultado(
            1900, 1500
        )

        self.assertGreater(
            resultado.vitoria,
            resultado.derrota,
        )

    def test_selecao_mais_fraca_tem_menor_chance(self):
        resultado = estimar_probabilidades_resultado(
            1400, 1800
        )

        self.assertLess(
            resultado.vitoria,
            resultado.derrota,
        )

    def test_inversao_das_selecoes(self):
        original = estimar_probabilidades_resultado(
            1800, 1600
        )

        invertido = estimar_probabilidades_resultado(
            1600, 1800
        )

        self.assertAlmostEqual(
            original.vitoria,
            invertido.derrota,
        )
        self.assertAlmostEqual(
            original.derrota,
            invertido.vitoria,
        )
        self.assertAlmostEqual(
            original.empate,
            invertido.empate,
        )

    def test_empate_diminui_com_diferenca_elo(self):
        equilibrado = estimar_probabilidades_resultado(
            1500, 1500
        )

        desequilibrado = estimar_probabilidades_resultado(
            1900, 1500
        )

        self.assertGreater(
            equilibrado.empate,
            desequilibrado.empate,
        )

    def test_consistencia_com_pontuacao_esperada_elo(self):
        rating_a = 1750
        rating_b = 1600

        resultado = estimar_probabilidades_resultado(
            rating_a, rating_b
        )

        esperado = probabilidade_esperada_elo(
            rating_a, rating_b
        )

        pontuacao_calculada = (
            resultado.vitoria
            + 0.5 * resultado.empate
        )

        self.assertAlmostEqual(
            pontuacao_calculada,
            esperado,
        )

    def test_probabilidades_dentro_do_intervalo(self):
        for rating_a, rating_b in (
            (1500, 1500),
            (2000, 1000),
            (1000, 2000),
            (1800, 1700),
        ):
            with self.subTest(
                rating_a=rating_a,
                rating_b=rating_b,
            ):
                resultado = estimar_probabilidades_resultado(
                    rating_a, rating_b
                )

                for probabilidade in (
                    resultado.vitoria,
                    resultado.empate,
                    resultado.derrota,
                ):
                    self.assertGreaterEqual(
                        probabilidade, 0.0
                    )
                    self.assertLessEqual(
                        probabilidade, 1.0
                    )

    def test_taxa_empate_zero(self):
        resultado = estimar_probabilidades_resultado(
            1500, 1500,
            taxa_empate_equilibrado=0,
        )

        self.assertAlmostEqual(resultado.empate, 0.0)
        self.assertAlmostEqual(resultado.vitoria, 0.5)
        self.assertAlmostEqual(resultado.derrota, 0.5)

    def test_taxa_empate_maxima(self):
        resultado = estimar_probabilidades_resultado(
            1500, 1500,
            taxa_empate_equilibrado=0.5,
        )

        self.assertAlmostEqual(resultado.empate, 0.5)
        self.assertAlmostEqual(resultado.vitoria, 0.25)
        self.assertAlmostEqual(resultado.derrota, 0.25)

    def test_taxas_invalidas(self):
        valores_invalidos = (
            -0.1,
            0.6,
            float("nan"),
            float("inf"),
            True,
        )

        for taxa in valores_invalidos:
            with self.subTest(taxa=taxa):
                with self.assertRaises(ValueError):
                    estimar_probabilidades_resultado(
                        1500,
                        1500,
                        taxa_empate_equilibrado=taxa,
                    )


if __name__ == "__main__":
    unittest.main()
