"""Testes do motor de simulação Monte Carlo."""

import unittest

from src.simulacao import (
    Participante,
    probabilidade_vitoria,
    simular_torneios,
)


class TestSimulacao(unittest.TestCase):

    def setUp(self):
        """Configura seleções com ratings experimentais."""
        self.participantes = [
            Participante("Brasil", 1800),
            Participante("Argentina", 1750),
            Participante("França", 1650),
            Participante("Espanha", 1600),
        ]

    def test_probabilidade_ratings_iguais(self):
        chance = probabilidade_vitoria(1800, 1800)
        self.assertAlmostEqual(chance, 0.5)

    def test_rating_maior_tem_mais_chance(self):
        chance = probabilidade_vitoria(1800, 1600)
        self.assertGreater(chance, 0.5)

    def test_total_de_titulos(self):
        resultado = simular_torneios(
            self.participantes,
            quantidade=1000,
        )
        self.assertEqual(
            sum(resultado.titulos.values()),
            1000,
        )

    def test_probabilidades_somam_cem(self):
        resultado = simular_torneios(
            self.participantes,
            quantidade=1000,
        )
        self.assertAlmostEqual(
            sum(resultado.probabilidades.values()),
            100.0,
        )

    def test_semente_reproduz_resultados(self):
        primeiro = simular_torneios(
            self.participantes, 1000, 42
        )
        segundo = simular_torneios(
            self.participantes, 1000, 42
        )
        self.assertEqual(
            primeiro.titulos,
            segundo.titulos,
        )

    def test_quantidade_invalida(self):
        with self.assertRaises(ValueError):
            simular_torneios(self.participantes, 0)

    def test_participantes_insuficientes(self):
        with self.assertRaises(ValueError):
            simular_torneios(self.participantes[:2])

    def test_rating_invalido(self):
        with self.assertRaises(ValueError):
            probabilidade_vitoria(
                float("nan"),
                1600,
            )

    def test_todas_selecoes_presentes_no_resultado(self):
        resultado = simular_torneios(
            self.participantes,
            quantidade=1000,
            semente=42,
        )

        nomes_esperados = {
            "Brasil",
            "Argentina",
            "França",
            "Espanha",
        }

        self.assertEqual(
            set(resultado.titulos.keys()),
            nomes_esperados,
        )

        self.assertEqual(
            set(resultado.probabilidades.keys()),
            nomes_esperados,
        )

    def test_participantes_duplicados(self):
        participantes = [
            Participante("Brasil", 1800),
            Participante(" brasil ", 1750),
            Participante("França", 1650),
            Participante("Espanha", 1600),
        ]

        with self.assertRaises(ValueError):
            simular_torneios(participantes)

    def test_rating_negativo(self):
        with self.assertRaises(ValueError):
            probabilidade_vitoria(-100, 1800)

    def test_semente_invalida(self):
        with self.assertRaises(ValueError):
            simular_torneios(
                self.participantes,
                quantidade=1000,
                semente=3.5,
            )

    def test_quantidade_booleana_invalida(self):
        with self.assertRaises(ValueError):
            simular_torneios(
                self.participantes,
                quantidade=True,
            )


if __name__ == "__main__":
    unittest.main()
