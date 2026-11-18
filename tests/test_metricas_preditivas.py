"""Testes das métricas preditivas multiclasse da V8."""

import math
import unittest

from dataclasses import replace
from datetime import date

from src.metricas_preditivas import (
    EPSILON,
    avaliar_previsoes,
)
from src.previsao_pre_jogo import RegistroPreJogo


def criar_registro(
    resultado="V",
    prob_vitoria=0.6,
    prob_empate=0.25,
    prob_derrota=0.15,
):
    """Cria um registro pré-jogo para os testes."""

    return RegistroPreJogo(
        data=date(2024, 1, 10),
        selecao_casa="Brasil",
        selecao_fora="Argentina",
        competicao="Amistoso",
        rating_casa=1600.0,
        rating_fora=1500.0,
        pontuacao_esperada_casa=0.64,
        prob_vitoria=prob_vitoria,
        prob_empate=prob_empate,
        prob_derrota=prob_derrota,
        resultado=resultado,
    )


class TestMetricasPreditivas(unittest.TestCase):

    def test_log_loss_vitoria(self):
        registro = criar_registro()

        metricas = avaliar_previsoes([registro])

        self.assertAlmostEqual(
            metricas.log_loss,
            -math.log(0.6),
        )

    def test_brier_score_vitoria(self):
        registro = criar_registro()

        metricas = avaliar_previsoes([registro])

        esperado = (
            (0.6 - 1.0) ** 2
            + 0.25 ** 2
            + 0.15 ** 2
        )

        self.assertAlmostEqual(
            metricas.brier_score,
            esperado,
        )

    def test_previsao_perfeita(self):
        registro = criar_registro(
            resultado="V",
            prob_vitoria=1.0,
            prob_empate=0.0,
            prob_derrota=0.0,
        )

        metricas = avaliar_previsoes([registro])

        self.assertAlmostEqual(metricas.log_loss, 0.0)
        self.assertAlmostEqual(metricas.brier_score, 0.0)

    def test_previsao_uniforme(self):
        registro = criar_registro(
            resultado="E",
            prob_vitoria=1 / 3,
            prob_empate=1 / 3,
            prob_derrota=1 / 3,
        )

        metricas = avaliar_previsoes([registro])

        self.assertAlmostEqual(
            metricas.log_loss,
            math.log(3),
        )

        self.assertAlmostEqual(
            metricas.brier_score,
            2 / 3,
        )

    def test_empate_e_derrota(self):
        empate = criar_registro(
            resultado="E",
            prob_vitoria=0.2,
            prob_empate=0.6,
            prob_derrota=0.2,
        )

        derrota = criar_registro(
            resultado="D",
            prob_vitoria=0.1,
            prob_empate=0.2,
            prob_derrota=0.7,
        )

        metricas = avaliar_previsoes(
            [empate, derrota]
        )

        log_loss_esperado = (
            -math.log(0.6) - math.log(0.7)
        ) / 2

        brier_esperado = (
            (0.2**2 + 0.4**2 + 0.2**2)
            + (0.1**2 + 0.2**2 + 0.3**2)
        ) / 2

        self.assertEqual(metricas.quantidade_partidas, 2)

        self.assertAlmostEqual(
            metricas.log_loss,
            log_loss_esperado,
        )

        self.assertAlmostEqual(
            metricas.brier_score,
            brier_esperado,
        )

    def test_probabilidade_real_zero(self):
        registro = criar_registro(
            resultado="V",
            prob_vitoria=0.0,
            prob_empate=0.5,
            prob_derrota=0.5,
        )

        metricas = avaliar_previsoes([registro])

        self.assertAlmostEqual(
            metricas.log_loss,
            -math.log(EPSILON),
        )

    def test_historico_vazio(self):
        with self.assertRaises(ValueError):
            avaliar_previsoes([])

    def test_resultado_invalido(self):
        registro = criar_registro(resultado="X")

        with self.assertRaises(ValueError):
            avaliar_previsoes([registro])

    def test_probabilidades_nao_somam_um(self):
        registro = criar_registro(
            prob_vitoria=0.5,
            prob_empate=0.3,
            prob_derrota=0.3,
        )

        with self.assertRaises(ValueError):
            avaliar_previsoes([registro])

    def test_probabilidades_invalidas(self):
        valores_invalidos = (
            -0.1,
            1.1,
            float("nan"),
            float("inf"),
            True,
        )

        for valor in valores_invalidos:
            with self.subTest(valor=valor):
                registro = replace(
                    criar_registro(),
                    prob_vitoria=valor,
                )

                with self.assertRaises(ValueError):
                    avaliar_previsoes([registro])

    def test_aceita_gerador(self):
        registros = (
            criar_registro(resultado=resultado)
            for resultado in ("V", "E", "D")
        )

        metricas = avaliar_previsoes(registros)

        self.assertEqual(
            metricas.quantidade_partidas,
            3,
        )

        self.assertTrue(math.isfinite(metricas.log_loss))
        self.assertTrue(math.isfinite(metricas.brier_score))


if __name__ == "__main__":
    unittest.main()
