"""Testes do ajuste de probabilidades do Orbia V8."""

import math
import unittest

from dataclasses import replace
from datetime import date

from src.ajuste_probabilidades_futebol import (
    AJUSTES_ELO_CANDIDATOS,
    TAXAS_EMPATE_CANDIDATAS,
    ajustar_probabilidades_treinamento,
    prever_probabilidades_ajustadas,
)
from src.previsao_pre_jogo import RegistroPreJogo
from src.probabilidades_futebol import (
    estimar_probabilidades_resultado,
)


def criar_registro(
    resultado="V",
    data=date(2015, 6, 10),
    rating_casa=1500.0,
    rating_fora=1500.0,
):
    """Cria registro sintético de previsão pré-jogo."""

    return RegistroPreJogo(
        data=data,
        selecao_casa="Brasil",
        selecao_fora="Argentina",
        competicao="Amistoso",
        rating_casa=rating_casa,
        rating_fora=rating_fora,
        pontuacao_esperada_casa=0.5,
        prob_vitoria=0.375,
        prob_empate=0.25,
        prob_derrota=0.375,
        resultado=resultado,
    )


class TestAjusteProbabilidadesFutebol(unittest.TestCase):

    def test_ajuste_zero_reproduz_modelo_original(self):
        registro = criar_registro()

        ajustado = prever_probabilidades_ajustadas(
            registro, 0.0, 0.25
        )

        original = estimar_probabilidades_resultado(
            1500.0, 1500.0, 0.25
        )

        self.assertEqual(ajustado, original)

    def test_ajuste_positivo_aumenta_vitoria(self):
        registro = criar_registro()

        original = prever_probabilidades_ajustadas(
            registro, 0.0, 0.25
        )

        ajustado = prever_probabilidades_ajustadas(
            registro, 100.0, 0.25
        )

        self.assertGreater(
            ajustado.vitoria, original.vitoria
        )
        self.assertLess(
            ajustado.derrota, original.derrota
        )

    def test_taxa_empate_maior_aumenta_empate(self):
        registro = criar_registro()

        menor = prever_probabilidades_ajustadas(
            registro, 0.0, 0.20
        )

        maior = prever_probabilidades_ajustadas(
            registro, 0.0, 0.30
        )

        self.assertGreater(
            maior.empate, menor.empate
        )

    def test_probabilidades_somam_um(self):
        registro = criar_registro(
            rating_casa=1650.0,
            rating_fora=1400.0,
        )

        for ajuste in AJUSTES_ELO_CANDIDATOS:
            for taxa in TAXAS_EMPATE_CANDIDATAS:
                with self.subTest(
                    ajuste=ajuste, taxa=taxa
                ):
                    previsao = (
                        prever_probabilidades_ajustadas(
                            registro, ajuste, taxa
                        )
                    )

                    valores = (
                        previsao.vitoria,
                        previsao.empate,
                        previsao.derrota,
                    )

                    self.assertAlmostEqual(
                        sum(valores), 1.0
                    )

                    for valor in valores:
                        self.assertTrue(
                            0.0 <= valor <= 1.0
                        )

    def test_rejeita_ajuste_nao_finito(self):
        registro = criar_registro()

        for ajuste in (
            float("nan"),
            float("inf"),
            float("-inf"),
        ):
            with self.subTest(ajuste=ajuste):
                with self.assertRaises(ValueError):
                    prever_probabilidades_ajustadas(
                        registro, ajuste, 0.25
                    )

    def test_rejeita_taxa_empate_invalida(self):
        registro = criar_registro()

        for taxa in (
            -0.01,
            0.51,
            float("nan"),
            float("inf"),
        ):
            with self.subTest(taxa=taxa):
                with self.assertRaises(ValueError):
                    prever_probabilidades_ajustadas(
                        registro, 0.0, taxa
                    )

    def test_aceita_limites_taxa_empate(self):
        registro = criar_registro()

        for taxa in (0.0, 0.5):
            with self.subTest(taxa=taxa):
                previsao = prever_probabilidades_ajustadas(
                    registro, 0.0, taxa
                )

                self.assertAlmostEqual(
                    sum((
                        previsao.vitoria,
                        previsao.empate,
                        previsao.derrota,
                    )),
                    1.0,
                )

    def test_grade_possui_42_combinacoes(self):
        combinacoes = [
            (ajuste, taxa)
            for ajuste in AJUSTES_ELO_CANDIDATOS
            for taxa in TAXAS_EMPATE_CANDIDATAS
        ]

        self.assertEqual(len(combinacoes), 42)
        self.assertEqual(
            len(set(combinacoes)), 42
        )

    def test_seleciona_ajuste_para_vitorias(self):
        registros = [
            criar_registro("V"),
            criar_registro(
                "V", date(2016, 1, 10)
            ),
            criar_registro(
                "V", date(2017, 1, 10)
            ),
        ]

        parametros = ajustar_probabilidades_treinamento(
            registros
        )

        self.assertEqual(
            parametros.ajuste_elo_mandante,
            max(AJUSTES_ELO_CANDIDATOS),
        )
        self.assertEqual(
            parametros.taxa_empate_equilibrado,
            min(TAXAS_EMPATE_CANDIDATAS),
        )

    def test_seleciona_taxa_para_empates(self):
        registros = [
            criar_registro("E"),
            criar_registro(
                "E", date(2016, 1, 10)
            ),
        ]

        parametros = ajustar_probabilidades_treinamento(
            registros
        )

        self.assertEqual(
            parametros.ajuste_elo_mandante,
            0.0,
        )
        self.assertEqual(
            parametros.taxa_empate_equilibrado,
            max(TAXAS_EMPATE_CANDIDATAS),
        )

    def test_nao_utiliza_validacao_nem_teste(self):
        treinamento = [
            criar_registro("V"),
            criar_registro(
                "V", date(2016, 1, 10)
            ),
        ]

        validacao = criar_registro(
            "D", date(2019, 1, 10)
        )

        teste = criar_registro(
            "E", date(2024, 1, 10)
        )

        somente_treinamento = (
            ajustar_probabilidades_treinamento(
                treinamento
            )
        )

        todos_periodos = (
            ajustar_probabilidades_treinamento(
                treinamento + [validacao, teste]
            )
        )

        self.assertEqual(
            somente_treinamento,
            todos_periodos,
        )

    def test_alterar_teste_nao_afeta_ajuste(self):
        treinamento = criar_registro("V")

        teste = criar_registro(
            "E", date(2024, 1, 10)
        )

        original = ajustar_probabilidades_treinamento(
            [treinamento, teste]
        )

        teste_alterado = replace(
            teste,
            resultado="D",
            rating_casa=1000.0,
            rating_fora=2000.0,
        )

        novo = ajustar_probabilidades_treinamento(
            [treinamento, teste_alterado]
        )

        self.assertEqual(original, novo)

    def test_treinamento_vazio(self):
        registros = [
            criar_registro(
                "V", date(2019, 1, 10)
            ),
            criar_registro(
                "D", date(2024, 1, 10)
            ),
        ]

        with self.assertRaises(ValueError):
            ajustar_probabilidades_treinamento(
                registros
            )

    def test_resultado_invalido_no_treinamento(self):
        registro = criar_registro(
            resultado="INVALIDO"
        )

        with self.assertRaises(ValueError):
            ajustar_probabilidades_treinamento(
                [registro]
            )

    def test_log_loss_corresponde_previsao(self):
        registro = criar_registro("V")

        parametros = ajustar_probabilidades_treinamento(
            [registro]
        )

        previsao = prever_probabilidades_ajustadas(
            registro,
            parametros.ajuste_elo_mandante,
            parametros.taxa_empate_equilibrado,
        )

        esperado = -math.log(
            max(previsao.vitoria, 1e-15)
        )

        self.assertAlmostEqual(
            parametros.log_loss_treinamento,
            esperado,
        )
        self.assertEqual(
            parametros.quantidade_treinamento,
            1,
        )

    def test_aceita_gerador(self):
        registros = (
            criar_registro(resultado)
            for resultado in ("V", "E", "D")
        )

        parametros = ajustar_probabilidades_treinamento(
            registros
        )

        self.assertEqual(
            parametros.quantidade_treinamento,
            3,
        )
        self.assertTrue(
            math.isfinite(
                parametros.log_loss_treinamento
            )
        )

    def test_resultado_deterministico(self):
        registros = [
            criar_registro("V"),
            criar_registro(
                "E", date(2016, 1, 10)
            ),
            criar_registro(
                "D", date(2017, 1, 10)
            ),
        ]

        primeiro = ajustar_probabilidades_treinamento(
            registros
        )

        segundo = ajustar_probabilidades_treinamento(
            list(reversed(registros))
        )

        self.assertEqual(primeiro, segundo)


if __name__ == "__main__":
    unittest.main()
