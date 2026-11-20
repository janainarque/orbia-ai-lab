"""Testes da integração preditiva do Orbia V9."""

import unittest

from dataclasses import replace
from datetime import date
from unittest.mock import patch

from components.predictive_dashboard import obter_avaliacao_preditiva
from src.previsao_pre_jogo import RegistroPreJogo


def criar_registro(data, resultado):
    """Cria uma previsão sintética sem depender do CSV."""

    return RegistroPreJogo(
        data=data,
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


def criar_historico():
    """Monta registros de treinamento, validação e teste."""

    return [
        criar_registro(date(2016, 1, 10), "V"),
        criar_registro(date(2017, 1, 10), "E"),
        criar_registro(date(2019, 1, 10), "V"),
        criar_registro(date(2020, 1, 10), "D"),
        criar_registro(date(2024, 1, 10), "E"),
    ]


def executar_integracao(registros):
    """Executa a integração real sem cache nem arquivos externos."""

    with (
        patch(
            "components.predictive_dashboard.carregar_partidas",
            return_value=[],
        ),
        patch(
            "components.predictive_dashboard.gerar_registros_pre_jogo",
            return_value=registros,
        ),
        patch(
            "components.predictive_dashboard.avaliar_historico_validacao",
            return_value="avaliacao_sintetica",
        ),
    ):
        # Executa a função original, ignorando o cache do Streamlit.
        return obter_avaliacao_preditiva.__wrapped__(
            "historico_sintetico.csv",
            1,
        )


class TestPredictiveDashboard(unittest.TestCase):

    def test_integra_elo_ajustado_e_calibracao(self):
        resultado = executar_integracao(criar_historico())

        (
            avaliacao,
            metricas,
            parametros,
            calibracao_original,
            calibracao_ajustado,
        ) = resultado

        self.assertEqual(avaliacao, "avaliacao_sintetica")

        self.assertTrue(0.0 <= parametros.taxa_empate_equilibrado <= 0.5)

        self.assertGreaterEqual(metricas.log_loss, 0.0)
        self.assertGreaterEqual(metricas.brier_score, 0.0)

        self.assertEqual(
            [classe.nome for classe in calibracao_original],
            ["Vitória", "Empate", "Derrota"],
        )

        self.assertEqual(len(calibracao_ajustado), 3)

        for classe in calibracao_original + calibracao_ajustado:
            self.assertEqual(classe.quantidade_partidas, 2)

    def test_alterar_conjunto_teste_nao_afeta_dashboard(self):
        registros = criar_historico()

        original = executar_integracao(registros)

        teste_alterado = replace(
            registros[-1],
            resultado="D",
            rating_casa=1000.0,
            rating_fora=2000.0,
            prob_vitoria=0.1,
            prob_empate=0.1,
            prob_derrota=0.8,
        )

        modificados = registros[:-1] + [teste_alterado]

        novo = executar_integracao(modificados)

        self.assertEqual(original, novo)

    def test_indicadores_fora_do_tratamento_de_erro(self):
        """Garante que os três cards estejam no fluxo principal."""

        import ast
        from pathlib import Path

        arquivo = (
            Path(__file__).resolve().parents[1]
            / "components"
            / "predictive_dashboard.py"
        )

        arvore = ast.parse(arquivo.read_text(encoding="utf-8"))

        funcao = next(
            node
            for node in arvore.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "render_predictive_dashboard"
        )

        chamadas = [
            node.value
            for node in funcao.body
            if isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
        ]

        indicadores = [
            chamada.func.value.id
            for chamada in chamadas
            if chamada.func.attr == "metric"
            and isinstance(chamada.func.value, ast.Name)
        ]

        self.assertEqual(indicadores, ["c1", "c2", "c3"])


if __name__ == "__main__":
    unittest.main()
