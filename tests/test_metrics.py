"""Testes dos indicadores do dashboard Orbia."""

import unittest
from unittest.mock import Mock, patch

from components.metrics import render_metrics
from src.retrospectiva import Previsao


class TestMetrics(unittest.TestCase):

    def setUp(self):
        self.ranking = [
            Previsao("Espanha", 16.9),
            Previsao("Argentina", 16.4),
            Previsao("França", 8.0),
            Previsao("Brasil", 6.4),
        ]

    def preparar_colunas(self, mock_columns):
        colunas = (Mock(), Mock(), Mock())
        mock_columns.return_value = colunas
        return colunas

    @patch("components.metrics.st.caption")
    @patch("components.metrics.st.markdown")
    @patch("components.metrics.st.columns")
    def test_ranking_completo(self, mock_columns, *_):
        c1, c2, c3 = self.preparar_colunas(mock_columns)

        render_metrics(self.ranking, 4)

        c1.metric.assert_called_once_with(
            "Maior probabilidade no filtro", "Espanha"
        )
        c2.metric.assert_called_once_with(
            "Probabilidade atribuída", "16,9%"
        )
        c3.metric.assert_called_once_with(
            "Diferença entre as líderes", "0,5 p.p."
        )

    @patch("components.metrics.st.caption")
    @patch("components.metrics.st.markdown")
    @patch("components.metrics.st.columns")
    def test_apenas_uma_selecao(self, mock_columns, *_):
        c1, c2, c3 = self.preparar_colunas(mock_columns)

        render_metrics([self.ranking[3]], 4)

        c1.metric.assert_called_once_with(
            "Maior probabilidade no filtro", "Brasil"
        )
        c2.metric.assert_called_once_with(
            "Probabilidade atribuída", "6,4%"
        )
        c3.metric.assert_called_once_with(
            "Diferença entre as líderes", "—"
        )

    @patch("components.metrics.st.caption")
    @patch("components.metrics.st.markdown")
    @patch("components.metrics.st.columns")
    def test_filtro_vazio(self, mock_columns, *_):
        c1, c2, c3 = self.preparar_colunas(mock_columns)

        render_metrics([], 4)

        c1.metric.assert_called_once_with(
            "Maior probabilidade no filtro", "—"
        )
        c2.metric.assert_called_once_with(
            "Probabilidade atribuída", "—"
        )
        c3.metric.assert_called_once_with(
            "Diferença entre as líderes", "—"
        )


if __name__ == "__main__":
    unittest.main()
