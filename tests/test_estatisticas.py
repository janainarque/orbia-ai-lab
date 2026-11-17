"""Testes do motor estatístico do Orbia."""

import unittest

from src.estatisticas import analisar_recorte
from src.retrospectiva import Previsao


class TestEstatisticas(unittest.TestCase):

    def setUp(self):
        self.ranking = [
            Previsao("Espanha", 16.9),
            Previsao("Argentina", 16.4),
            Previsao("França", 8.0),
            Previsao("Brasil", 6.4),
        ]

    def test_quantidade_selecoes(self):
        resultado = analisar_recorte(self.ranking)
        self.assertEqual(resultado.quantidade_selecoes, 4)

    def test_percentual_observado(self):
        resultado = analisar_recorte(self.ranking)
        self.assertAlmostEqual(resultado.percentual_observado, 47.7)
        self.assertAlmostEqual(resultado.percentual_nao_exibido, 52.3)

    def test_concentracao_duas_lideres(self):
        resultado = analisar_recorte(self.ranking)
        self.assertAlmostEqual(
            resultado.concentracao_duas_lideres, 33.3
        )

    def test_diferenca_e_amplitude(self):
        resultado = analisar_recorte(self.ranking)
        self.assertAlmostEqual(resultado.diferenca_lideres_pp, 0.5)
        self.assertAlmostEqual(resultado.amplitude_pp, 10.5)

    def test_ranking_vazio(self):
        with self.assertRaises(ValueError):
            analisar_recorte([])

    def test_apenas_uma_selecao(self):
        resultado = analisar_recorte([Previsao("Brasil", 6.4)])
        self.assertIsNone(resultado.diferenca_lideres_pp)
        self.assertEqual(resultado.amplitude_pp, 0)
        
    
    def test_percentual_negativo(self):
        ranking = [Previsao("Brasil", -5.0)]

        with self.assertRaises(ValueError):
            analisar_recorte(ranking)

    def test_percentual_acima_de_cem(self):
        ranking = [Previsao("Brasil", 101.0)]

        with self.assertRaises(ValueError):
            analisar_recorte(ranking)

    def test_percentual_nao_finito(self):
        for valor in [float("nan"), float("inf")]:
            with self.subTest(valor=valor):
                with self.assertRaises(ValueError):
                    analisar_recorte(
                        [Previsao("Brasil", valor)]
                    )

    def test_selecao_duplicada(self):
        ranking = [
            Previsao("Brasil", 6.4),
            Previsao(" brasil ", 5.0),
        ]

        with self.assertRaises(ValueError):
            analisar_recorte(ranking)

    def test_soma_acima_de_cem(self):
        ranking = [
            Previsao("Brasil", 60.0),
            Previsao("Argentina", 50.0),
        ]

        with self.assertRaises(ValueError):
            analisar_recorte(ranking)



if __name__ == "__main__":
    unittest.main()
