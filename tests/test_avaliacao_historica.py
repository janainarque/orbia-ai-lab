"""Testes da comparação histórica entre Elo e baseline."""

import math
import unittest

from dataclasses import replace
from datetime import date

from src.avaliacao_historica import (
    avaliar_historico_validacao,
)
from src.metricas_preditivas import avaliar_previsoes
from src.previsao_pre_jogo import RegistroPreJogo


def criar_registro(data, resultado="V"):
    """Cria um registro pré-jogo sintético."""

    return RegistroPreJogo(
        data=data,
        selecao_casa="Brasil",
        selecao_fora="Argentina",
        competicao="Amistoso",
        rating_casa=1600.0,
        rating_fora=1500.0,
        pontuacao_esperada_casa=0.625,
        prob_vitoria=0.5,
        prob_empate=0.25,
        prob_derrota=0.25,
        resultado=resultado,
    )


class TestAvaliacaoHistorica(unittest.TestCase):

    def setUp(self):
        self.treinamento = [
            criar_registro(date(2015, 1, 1), "V"),
            criar_registro(date(2016, 1, 1), "V"),
            criar_registro(date(2016, 6, 1), "E"),
            criar_registro(date(2017, 1, 1), "D"),
        ]

        self.validacao = [
            criar_registro(date(2018, 1, 1), "E"),
            criar_registro(date(2020, 1, 1), "D"),
        ]

        self.teste = [
            criar_registro(date(2022, 1, 1), "V"),
            criar_registro(date(2024, 1, 1), "D"),
        ]

        self.registros = (
            self.treinamento
            + self.validacao
            + self.teste
        )

    def test_quantidade_por_periodo(self):
        resultado = avaliar_historico_validacao(
            self.registros
        )

        self.assertEqual(
            resultado.quantidade_treinamento, 4
        )
        self.assertEqual(
            resultado.quantidade_validacao, 2
        )
        self.assertEqual(
            resultado.quantidade_teste, 2
        )

    def test_baseline_usa_apenas_treinamento(self):
        resultado = avaliar_historico_validacao(
            self.registros
        )

        self.assertEqual(
            resultado.baseline.quantidade_partidas,
            4,
        )

        self.assertAlmostEqual(
            resultado.baseline.prob_vitoria,
            3 / 7,
        )
        self.assertAlmostEqual(
            resultado.baseline.prob_empate,
            2 / 7,
        )
        self.assertAlmostEqual(
            resultado.baseline.prob_derrota,
            2 / 7,
        )

    def test_metricas_elo_usam_apenas_validacao(self):
        resultado = avaliar_historico_validacao(
            self.registros
        )

        esperado = avaliar_previsoes(
            self.validacao
        )

        self.assertEqual(
            resultado.metricas_elo,
            esperado,
        )

        self.assertEqual(
            resultado.metricas_elo.quantidade_partidas,
            2,
        )

    def test_metricas_baseline(self):
        resultado = avaliar_historico_validacao(
            self.registros
        )

        baseline = resultado.baseline

        registros_baseline = [
            replace(
                registro,
                prob_vitoria=baseline.prob_vitoria,
                prob_empate=baseline.prob_empate,
                prob_derrota=baseline.prob_derrota,
            )
            for registro in self.validacao
        ]

        esperado = avaliar_previsoes(
            registros_baseline
        )

        self.assertEqual(
            resultado.metricas_baseline,
            esperado,
        )

    def test_diferenca_log_loss(self):
        resultado = avaliar_historico_validacao(
            self.registros
        )

        esperado = (
            resultado.metricas_elo.log_loss
            - resultado.metricas_baseline.log_loss
        )

        self.assertAlmostEqual(
            resultado.diferenca_log_loss,
            esperado,
        )

    def test_diferenca_brier_score(self):
        resultado = avaliar_historico_validacao(
            self.registros
        )

        esperado = (
            resultado.metricas_elo.brier_score
            - resultado.metricas_baseline.brier_score
        )

        self.assertAlmostEqual(
            resultado.diferenca_brier_score,
            esperado,
        )

    def test_resultados_do_teste_nao_afetam_avaliacao(self):
        original = avaliar_historico_validacao(
            self.registros
        )

        teste_alterado = [
            replace(registro, resultado="E")
            for registro in self.teste
        ]

        alterados = (
            self.treinamento
            + self.validacao
            + teste_alterado
        )

        novo = avaliar_historico_validacao(
            alterados
        )

        self.assertEqual(original, novo)

    def test_probabilidades_do_teste_nao_afetam_avaliacao(self):
        original = avaliar_historico_validacao(
            self.registros
        )

        teste_alterado = [
            replace(
                registro,
                prob_vitoria=0.1,
                prob_empate=0.1,
                prob_derrota=0.8,
            )
            for registro in self.teste
        ]

        novo = avaliar_historico_validacao(
            self.treinamento
            + self.validacao
            + teste_alterado
        )

        self.assertEqual(original, novo)

    def test_treinamento_vazio(self):
        with self.assertRaises(ValueError):
            avaliar_historico_validacao(
                self.validacao + self.teste
            )

    def test_validacao_vazia(self):
        with self.assertRaises(ValueError):
            avaliar_historico_validacao(
                self.treinamento + self.teste
            )

    def test_aceita_gerador(self):
        registros = (
            registro
            for registro in self.registros
        )

        resultado = avaliar_historico_validacao(
            registros
        )

        self.assertEqual(
            resultado.quantidade_validacao,
            2,
        )

    def test_independencia_da_ordem(self):
        original = avaliar_historico_validacao(
            self.registros
        )

        invertido = avaliar_historico_validacao(
            reversed(self.registros)
        )

        self.assertEqual(original, invertido)

    def test_metricas_finitas(self):
        resultado = avaliar_historico_validacao(
            self.registros
        )

        valores = (
            resultado.metricas_elo.log_loss,
            resultado.metricas_elo.brier_score,
            resultado.metricas_baseline.log_loss,
            resultado.metricas_baseline.brier_score,
            resultado.diferenca_log_loss,
            resultado.diferenca_brier_score,
        )

        for valor in valores:
            self.assertTrue(math.isfinite(valor))


if __name__ == "__main__":
    unittest.main()
