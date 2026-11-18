"""Testes do baseline estatístico da V8."""

import math
import unittest

from datetime import date

from src.baseline_futebol import (
    ajustar_baseline_frequencias,
)
from src.previsao_pre_jogo import RegistroPreJogo


def criar_registro(resultado="V"):
    """Cria um registro pré-jogo para testes."""

    return RegistroPreJogo(
        data=date(2024, 1, 10),
        selecao_casa="Brasil",
        selecao_fora="Argentina",
        competicao="Amistoso",
        rating_casa=1500.0,
        rating_fora=1500.0,
        pontuacao_esperada_casa=0.5,
        prob_vitoria=0.375,
        prob_empate=0.25,
        prob_derrota=0.375,
        resultado=resultado,
    )


class TestBaselineFutebol(unittest.TestCase):

    def test_frequencias_sem_suavizacao(self):
        registros = [
            criar_registro("V"),
            criar_registro("V"),
            criar_registro("E"),
            criar_registro("D"),
        ]

        baseline = ajustar_baseline_frequencias(
            registros,
            suavizacao=0,
        )

        self.assertAlmostEqual(
            baseline.prob_vitoria, 0.5
        )
        self.assertAlmostEqual(
            baseline.prob_empate, 0.25
        )
        self.assertAlmostEqual(
            baseline.prob_derrota, 0.25
        )

    def test_suavizacao_padrao(self):
        registros = [
            criar_registro("V"),
            criar_registro("V"),
            criar_registro("E"),
            criar_registro("D"),
        ]

        baseline = ajustar_baseline_frequencias(
            registros
        )

        self.assertAlmostEqual(
            baseline.prob_vitoria, 3 / 7
        )
        self.assertAlmostEqual(
            baseline.prob_empate, 2 / 7
        )
        self.assertAlmostEqual(
            baseline.prob_derrota, 2 / 7
        )

    def test_classe_ausente_com_suavizacao(self):
        registros = [
            criar_registro("V"),
        ]

        baseline = ajustar_baseline_frequencias(
            registros
        )

        self.assertAlmostEqual(
            baseline.prob_vitoria, 0.5
        )
        self.assertAlmostEqual(
            baseline.prob_empate, 0.25
        )
        self.assertAlmostEqual(
            baseline.prob_derrota, 0.25
        )

    def test_classe_ausente_sem_suavizacao(self):
        baseline = ajustar_baseline_frequencias(
            [criar_registro("V")],
            suavizacao=0,
        )

        self.assertAlmostEqual(
            baseline.prob_vitoria, 1.0
        )
        self.assertAlmostEqual(
            baseline.prob_empate, 0.0
        )
        self.assertAlmostEqual(
            baseline.prob_derrota, 0.0
        )

    def test_probabilidades_somam_um(self):
        registros = [
            criar_registro("V"),
            criar_registro("E"),
            criar_registro("D"),
        ]

        baseline = ajustar_baseline_frequencias(
            registros
        )

        soma = (
            baseline.prob_vitoria
            + baseline.prob_empate
            + baseline.prob_derrota
        )

        self.assertAlmostEqual(soma, 1.0)

    def test_quantidade_partidas(self):
        registros = [
            criar_registro("V"),
            criar_registro("E"),
            criar_registro("D"),
        ]

        baseline = ajustar_baseline_frequencias(
            registros
        )

        self.assertEqual(
            baseline.quantidade_partidas, 3
        )

    def test_historico_vazio(self):
        with self.assertRaises(ValueError):
            ajustar_baseline_frequencias([])

    def test_resultado_invalido(self):
        registros = [
            criar_registro("V"),
            criar_registro("X"),
        ]

        with self.assertRaises(ValueError):
            ajustar_baseline_frequencias(
                registros
            )

    def test_suavizacao_invalida(self):
        valores_invalidos = (
            -1,
            float("nan"),
            float("inf"),
            True,
        )

        for valor in valores_invalidos:
            with self.subTest(valor=valor):
                with self.assertRaises(ValueError):
                    ajustar_baseline_frequencias(
                        [criar_registro("V")],
                        suavizacao=valor,
                    )

    def test_independencia_da_ordem(self):
        registros = [
            criar_registro("V"),
            criar_registro("E"),
            criar_registro("V"),
            criar_registro("D"),
        ]

        original = ajustar_baseline_frequencias(
            registros
        )

        invertido = ajustar_baseline_frequencias(
            reversed(registros)
        )

        self.assertEqual(original, invertido)

    def test_aceita_gerador(self):
        registros = (
            criar_registro(resultado)
            for resultado in ("V", "E", "D")
        )

        baseline = ajustar_baseline_frequencias(
            registros
        )

        self.assertEqual(
            baseline.quantidade_partidas, 3
        )

        self.assertAlmostEqual(
            baseline.prob_vitoria,
            1 / 3,
        )
        self.assertAlmostEqual(
            baseline.prob_empate,
            1 / 3,
        )
        self.assertAlmostEqual(
            baseline.prob_derrota,
            1 / 3,
        )

    def test_resultado_reproduzivel(self):
        registros = [
            criar_registro("V"),
            criar_registro("E"),
            criar_registro("V"),
        ]

        primeiro = ajustar_baseline_frequencias(
            registros
        )

        segundo = ajustar_baseline_frequencias(
            registros
        )

        self.assertEqual(primeiro, segundo)


if __name__ == "__main__":
    unittest.main()
