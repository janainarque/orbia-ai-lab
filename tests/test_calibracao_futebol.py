"""Testes do motor de calibração preditiva da V8."""

import math
import unittest

from dataclasses import replace
from datetime import date

from src.calibracao_futebol import (
    calcular_calibracao_validacao,
)
from src.previsao_pre_jogo import RegistroPreJogo


def criar_registro(
    resultado="V",
    prob_vitoria=0.6,
    prob_empate=0.2,
    prob_derrota=0.2,
    data=date(2019, 1, 10),
):
    """Cria uma previsão sintética para testes."""

    return RegistroPreJogo(
        data=data,
        selecao_casa="Brasil",
        selecao_fora="Argentina",
        competicao="Amistoso",
        rating_casa=1500.0,
        rating_fora=1500.0,
        pontuacao_esperada_casa=0.5,
        prob_vitoria=prob_vitoria,
        prob_empate=prob_empate,
        prob_derrota=prob_derrota,
        resultado=resultado,
    )


class TestCalibracaoFutebol(unittest.TestCase):

    def test_retorna_tres_classes(self):
        resultado = calcular_calibracao_validacao(
            [criar_registro()]
        )

        self.assertEqual(len(resultado), 3)
        self.assertEqual(
            [item.resultado for item in resultado],
            ["V", "E", "D"],
        )
        self.assertEqual(
            [item.nome for item in resultado],
            ["Vitória", "Empate", "Derrota"],
        )

    def test_calibracao_perfeita(self):
        registros = [
            criar_registro("V", 1.0, 0.0, 0.0),
            criar_registro("E", 0.0, 1.0, 0.0),
            criar_registro("D", 0.0, 0.0, 1.0),
        ]

        resultado = calcular_calibracao_validacao(
            registros
        )

        for classe in resultado:
            self.assertAlmostEqual(
                classe.erro_calibracao_esperado,
                0.0,
            )

            for faixa in classe.faixas:
                self.assertAlmostEqual(
                    faixa.probabilidade_media,
                    faixa.frequencia_observada,
                )

    def test_erro_calibracao_uma_partida(self):
        resultado = calcular_calibracao_validacao(
            [criar_registro()]
        )

        esperado = {
            "V": 0.4,
            "E": 0.2,
            "D": 0.2,
        }

        for classe in resultado:
            self.assertAlmostEqual(
                classe.erro_calibracao_esperado,
                esperado[classe.resultado],
            )

    def test_faixas_vazias_sao_omitidas(self):
        resultado = calcular_calibracao_validacao(
            [criar_registro()],
            quantidade_faixas=10,
        )

        for classe in resultado:
            self.assertEqual(len(classe.faixas), 1)
            self.assertEqual(
                classe.faixas[0].quantidade,
                1,
            )

    def test_probabilidade_um_na_ultima_faixa(self):
        registro = criar_registro(
            "V", 1.0, 0.0, 0.0
        )

        resultado = calcular_calibracao_validacao(
            [registro],
            quantidade_faixas=10,
        )

        vitoria = resultado[0]

        self.assertEqual(
            vitoria.faixas[0].indice,
            9,
        )
        self.assertAlmostEqual(
            vitoria.faixas[0].limite_superior,
            1.0,
        )

    def test_fronteira_de_faixa(self):
        registro = criar_registro(
            "V", 0.5, 0.25, 0.25
        )

        resultado = calcular_calibracao_validacao(
            [registro],
            quantidade_faixas=2,
        )

        vitoria = resultado[0]

        self.assertEqual(
            vitoria.faixas[0].indice,
            1,
        )
        self.assertAlmostEqual(
            vitoria.faixas[0].limite_inferior,
            0.5,
        )

    def test_erro_ponderado_por_faixa(self):
        registros = [
            criar_registro(
                "V", 0.2, 0.3, 0.5
            ),
            criar_registro(
                "D", 0.8, 0.1, 0.1
            ),
        ]

        resultado = calcular_calibracao_validacao(
            registros,
            quantidade_faixas=2,
        )

        vitoria = resultado[0]

        # Faixa 1: prevista 0.2, observada 1.0
        # Faixa 2: prevista 0.8, observada 0.0
        esperado = (
            0.5 * abs(0.2 - 1.0)
            + 0.5 * abs(0.8 - 0.0)
        )

        self.assertAlmostEqual(
            vitoria.erro_calibracao_esperado,
            esperado,
        )
        self.assertAlmostEqual(
            esperado,
            0.8,
        )

    def test_usa_somente_validacao(self):
        treinamento = criar_registro(
            "D",
            0.1, 0.1, 0.8,
            date(2016, 1, 10),
        )

        validacao = criar_registro(
            "V",
            0.6, 0.2, 0.2,
            date(2019, 1, 10),
        )

        teste = criar_registro(
            "E",
            0.1, 0.8, 0.1,
            date(2024, 1, 10),
        )

        resultado = calcular_calibracao_validacao(
            [treinamento, validacao, teste]
        )

        esperado = calcular_calibracao_validacao(
            [validacao]
        )

        self.assertEqual(resultado, esperado)

        for classe in resultado:
            self.assertEqual(
                classe.quantidade_partidas,
                1,
            )

    def test_alterar_teste_nao_afeta_resultado(self):
        validacao = criar_registro(
            data=date(2020, 1, 10)
        )

        teste = criar_registro(
            data=date(2024, 1, 10)
        )

        original = calcular_calibracao_validacao(
            [validacao, teste]
        )

        teste_alterado = replace(
            teste,
            resultado="D",
            prob_vitoria=0.1,
            prob_empate=0.1,
            prob_derrota=0.8,
        )

        novo = calcular_calibracao_validacao(
            [validacao, teste_alterado]
        )

        self.assertEqual(original, novo)

    def test_validacao_vazia(self):
        registros = [
            criar_registro(
                data=date(2016, 1, 10)
            ),
            criar_registro(
                data=date(2024, 1, 10)
            ),
        ]

        with self.assertRaises(ValueError):
            calcular_calibracao_validacao(
                registros
            )

    def test_quantidade_faixas_invalida(self):
        valores_invalidos = (
            0,
            1,
            101,
            -1,
            2.5,
            True,
            "10",
        )

        for valor in valores_invalidos:
            with self.subTest(valor=valor):
                with self.assertRaises(ValueError):
                    calcular_calibracao_validacao(
                        [criar_registro()],
                        quantidade_faixas=valor,
                    )

    def test_probabilidades_invalidas(self):
        registros_invalidos = [
            criar_registro(
                prob_vitoria=float("nan")
            ),
            criar_registro(
                prob_vitoria=1.2
            ),
            criar_registro(
                prob_vitoria=0.7
            ),
        ]

        for registro in registros_invalidos:
            with self.subTest(
                probabilidade=registro.prob_vitoria
            ):
                with self.assertRaises(ValueError):
                    calcular_calibracao_validacao(
                        [registro]
                    )

    def test_aceita_gerador(self):
        registros = (
            criar_registro(resultado)
            for resultado in ("V", "E", "D")
        )

        resultado = calcular_calibracao_validacao(
            registros
        )

        self.assertEqual(len(resultado), 3)

        for classe in resultado:
            self.assertEqual(
                classe.quantidade_partidas,
                3,
            )
            self.assertTrue(
                math.isfinite(
                    classe.erro_calibracao_esperado
                )
            )


if __name__ == "__main__":
    unittest.main()
