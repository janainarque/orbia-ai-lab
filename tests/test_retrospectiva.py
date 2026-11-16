import tempfile
import unittest
from pathlib import Path

from src.retrospectiva import Previsao, carregar_ranking, resumo


class TestRetrospectiva(unittest.TestCase):
    def setUp(self):
        self.ranking = [Previsao("Espanha", 16.9), Previsao("Argentina", 16.4), Previsao("França", 8), Previsao("Brasil", 6.4)]

    def csv(self, conteudo):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        path = Path(temp.name) / "ranking.csv"
        path.write_text(conteudo, encoding="utf-8")
        return path

    def test_lider_e_margem(self):
        dados = resumo(self.ranking, "Espanha")
        self.assertEqual(dados["favorito"], "Espanha")
        self.assertEqual(dados["margem_primeiro_segundo_pp"], 0.5)
        self.assertTrue(dados["favorito_corresponde_ao_campeao"])

    def test_parcial_nao_e_distribuicao_completa(self):
        self.assertAlmostEqual(resumo(self.ranking, "Espanha")["probabilidade_restante_nao_exibida"], 52.3)

    def test_campeao_diferente(self):
        self.assertFalse(resumo(self.ranking, "Brasil")["favorito_corresponde_ao_campeao"])

    def test_leitura_ordenada(self):
        p = self.csv("selecao,probabilidade_percentual\nBrasil,6.4\nEspanha,16.9\n")
        self.assertEqual(carregar_ranking(p)[0].selecao, "Espanha")

    def test_duplicado(self):
        p = self.csv("selecao,probabilidade_percentual\nEspanha,16.9\nespanha,16.4\n")
        with self.assertRaises(ValueError): carregar_ranking(p)

    def test_percentual_invalido(self):
        p = self.csv("selecao,probabilidade_percentual\nEspanha,nan\n")
        with self.assertRaises(ValueError): carregar_ranking(p)

    def test_soma_acima_de_cem(self):
        p = self.csv("selecao,probabilidade_percentual\nA,80\nB,30\n")
        with self.assertRaises(ValueError): carregar_ranking(p)

    def test_cabecalho_invalido(self):
        p = self.csv("pais,valor\nEspanha,16.9\n")
        with self.assertRaises(ValueError): carregar_ranking(p)

    def test_campeao_vazio(self):
        with self.assertRaises(ValueError): resumo(self.ranking, "  ")

    def test_ranking_vazio(self):
        with self.assertRaises(ValueError): resumo([], "Espanha")


if __name__ == "__main__": unittest.main()
