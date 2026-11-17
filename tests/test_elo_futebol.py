"""Testes automatizados do motor Elo do Orbia."""

import unittest
from datetime import date

from src.dados_futebol import RegistroPartida
from src.elo_futebol import (
    atualizar_ratings_elo,
    calcular_ratings_elo,
    probabilidade_esperada_elo,
    validar_parametros_elo,
)


def criar_partida(
    data: date,
    casa: str,
    fora: str,
    gols_casa: int,
    gols_fora: int,
) -> RegistroPartida:
    """Cria uma partida fictícia para os testes."""

    return RegistroPartida(
        data=data,
        selecao_casa=casa,
        selecao_fora=fora,
        gols_casa=gols_casa,
        gols_fora=gols_fora,
        competicao="Amistoso de teste",
        fonte_url="https://example.com/teste",
    )


class TestProbabilidadeEsperada(unittest.TestCase):

    def test_ratings_iguais(self):
        resultado = probabilidade_esperada_elo(1500, 1500)
        self.assertAlmostEqual(resultado, 0.5)

    def test_rating_superior(self):
        resultado = probabilidade_esperada_elo(1700, 1500)
        self.assertGreater(resultado, 0.5)

    def test_rating_inferior(self):
        resultado = probabilidade_esperada_elo(1300, 1500)
        self.assertLess(resultado, 0.5)

    def test_probabilidades_complementares(self):
        a = probabilidade_esperada_elo(1800, 1600)
        b = probabilidade_esperada_elo(1600, 1800)
        self.assertAlmostEqual(a + b, 1.0)


class TestAtualizacaoElo(unittest.TestCase):

    def test_vitoria_com_ratings_iguais(self):
        casa, fora = atualizar_ratings_elo(
            1500, 1500, 2, 1
        )

        self.assertAlmostEqual(casa, 1510)
        self.assertAlmostEqual(fora, 1490)

    def test_derrota_com_ratings_iguais(self):
        casa, fora = atualizar_ratings_elo(
            1500, 1500, 0, 2
        )

        self.assertAlmostEqual(casa, 1490)
        self.assertAlmostEqual(fora, 1510)

    def test_empate_com_ratings_iguais(self):
        casa, fora = atualizar_ratings_elo(
            1500, 1500, 1, 1
        )

        self.assertAlmostEqual(casa, 1500)
        self.assertAlmostEqual(fora, 1500)

    def test_empate_favorece_selecao_mais_fraca(self):
        forte, fraca = atualizar_ratings_elo(
            1800, 1400, 0, 0
        )

        self.assertLess(forte, 1800)
        self.assertGreater(fraca, 1400)

    def test_conservacao_dos_pontos(self):
        casa, fora = atualizar_ratings_elo(
            1750, 1600, 3, 0
        )

        self.assertAlmostEqual(
            casa + fora,
            1750 + 1600,
        )

    def test_placar_negativo_rejeitado(self):
        with self.assertRaises(ValueError):
            atualizar_ratings_elo(
                1500, 1500, -1, 0
            )


class TestParametrosElo(unittest.TestCase):

    def test_fator_k_invalido(self):
        with self.assertRaises(ValueError):
            validar_parametros_elo(1500, 0)

    def test_rating_inicial_invalido(self):
        with self.assertRaises(ValueError):
            validar_parametros_elo(-100, 20)


class TestHistoricoElo(unittest.TestCase):

    def setUp(self):
        self.partidas = [
            criar_partida(
                date(2024, 1, 10),
                "Brasil",
                "Argentina",
                2,
                1,
            ),
            criar_partida(
                date(2024, 2, 10),
                "Argentina",
                "Franca",
                1,
                0,
            ),
            criar_partida(
                date(2024, 3, 10),
                "Franca",
                "Brasil",
                0,
                0,
            ),
        ]

    def test_todas_selecoes_recebem_rating(self):
        ratings = calcular_ratings_elo(self.partidas)

        self.assertEqual(
            set(ratings),
            {"Brasil", "Argentina", "Franca"},
        )

    def test_historico_vazio(self):
        ratings = calcular_ratings_elo([])

        self.assertEqual(ratings, {})

    def test_independencia_da_ordem_de_entrada(self):
        original = calcular_ratings_elo(self.partidas)

        invertido = calcular_ratings_elo(
            list(reversed(self.partidas))
        )

        self.assertEqual(original, invertido)

    def test_resultado_reproduzivel(self):
        primeiro = calcular_ratings_elo(self.partidas)
        segundo = calcular_ratings_elo(self.partidas)

        self.assertEqual(primeiro, segundo)

    def test_sem_vazamento_de_partidas_futuras(self):
        primeira = self.partidas[0]

        rating_apos_primeira = calcular_ratings_elo(
            [primeira]
        )

        self.assertAlmostEqual(
            rating_apos_primeira["Brasil"],
            1510,
        )

        self.assertAlmostEqual(
            rating_apos_primeira["Argentina"],
            1490,
        )

    def test_partidas_mesmo_dia_ordem_deterministica(self):
        partidas = [
            criar_partida(
                date(2024, 5, 1),
                "Brasil",
                "Argentina",
                1,
                0,
            ),
            criar_partida(
                date(2024, 5, 1),
                "Argentina",
                "Franca",
                2,
                0,
            ),
        ]

        primeiro = calcular_ratings_elo(partidas)

        segundo = calcular_ratings_elo(
            list(reversed(partidas))
        )

        self.assertEqual(primeiro, segundo)


    def test_corte_temporal_exclui_partidas_futuras(self):
        resultado = calcular_ratings_elo(
            self.partidas,
            data_fim=date(2024, 1, 10),
        )

        self.assertAlmostEqual(resultado["Brasil"], 1510)
        self.assertAlmostEqual(resultado["Argentina"], 1490)
        self.assertNotIn("Franca", resultado)

    def test_corte_temporal_antes_da_primeira_partida(self):
        resultado = calcular_ratings_elo(
            self.partidas,
            data_fim=date(2023, 12, 31),
        )

        self.assertEqual(resultado, {})

    def test_corte_temporal_rejeita_data_invalida(self):
        with self.assertRaises(ValueError):
            calcular_ratings_elo(
                self.partidas,
                data_fim="2024-01-10",
            )


if __name__ == "__main__":
    unittest.main()
