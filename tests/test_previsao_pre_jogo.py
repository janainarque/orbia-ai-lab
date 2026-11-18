"""Testes da geração de registros pré-jogo da V8."""

import unittest
from datetime import date

from src.dados_futebol import RegistroPartida
from src.previsao_pre_jogo import gerar_registros_pre_jogo


def criar_partida(data, casa, fora, gols_casa, gols_fora):
    return RegistroPartida(
        data=data,
        selecao_casa=casa,
        selecao_fora=fora,
        gols_casa=gols_casa,
        gols_fora=gols_fora,
        competicao="Amistoso de teste",
        fonte_url="https://example.com/teste",
    )


class TestPrevisaoPreJogo(unittest.TestCase):

    def test_historico_vazio(self):
        registros = gerar_registros_pre_jogo([])
        self.assertEqual(registros, [])

    def test_ratings_iniciais(self):
        partidas = [
            criar_partida(
                date(2024, 1, 10),
                "Brasil",
                "Argentina",
                2,
                1,
            )
        ]

        registros = gerar_registros_pre_jogo(partidas)

        self.assertEqual(len(registros), 1)
        self.assertEqual(registros[0].rating_casa, 1500)
        self.assertEqual(registros[0].rating_fora, 1500)
        self.assertAlmostEqual(
            registros[0].pontuacao_esperada_casa,
            0.5,
        )
        self.assertEqual(registros[0].resultado, "V")

    def test_partida_seguinte_utiliza_rating_atualizado(self):
        partidas = [
            criar_partida(
                date(2024, 1, 10),
                "Brasil",
                "Argentina",
                2,
                1,
            ),
            criar_partida(
                date(2024, 1, 11),
                "Brasil",
                "Argentina",
                1,
                1,
            ),
        ]

        registros = gerar_registros_pre_jogo(partidas)

        self.assertAlmostEqual(registros[1].rating_casa, 1510)
        self.assertAlmostEqual(registros[1].rating_fora, 1490)
        self.assertGreater(
            registros[1].pontuacao_esperada_casa,
            0.5,
        )

    def test_partidas_mesmo_dia_nao_compartilham_resultados(self):
        partidas = [
            criar_partida(
                date(2024, 1, 10),
                "Brasil",
                "Argentina",
                2,
                0,
            ),
            criar_partida(
                date(2024, 1, 10),
                "Brasil",
                "Franca",
                3,
                0,
            ),
        ]

        registros = gerar_registros_pre_jogo(partidas)

        self.assertEqual(len(registros), 2)

        for registro in registros:
            self.assertAlmostEqual(registro.rating_casa, 1500)
            self.assertAlmostEqual(registro.rating_fora, 1500)

    def test_atualizacao_simultanea_apos_o_dia(self):
        partidas = [
            criar_partida(
                date(2024, 1, 10),
                "Brasil",
                "Argentina",
                2,
                0,
            ),
            criar_partida(
                date(2024, 1, 10),
                "Brasil",
                "Franca",
                3,
                0,
            ),
            criar_partida(
                date(2024, 1, 11),
                "Brasil",
                "Espanha",
                1,
                1,
            ),
        ]

        registros = gerar_registros_pre_jogo(partidas)

        self.assertAlmostEqual(registros[2].rating_casa, 1520)
        self.assertAlmostEqual(registros[2].rating_fora, 1500)

    def test_independencia_da_ordem_de_entrada(self):
        partidas = [
            criar_partida(
                date(2024, 2, 10),
                "Argentina",
                "Franca",
                1,
                0,
            ),
            criar_partida(
                date(2024, 1, 10),
                "Brasil",
                "Argentina",
                2,
                1,
            ),
        ]

        original = gerar_registros_pre_jogo(partidas)
        invertido = gerar_registros_pre_jogo(
            list(reversed(partidas))
        )

        self.assertEqual(original, invertido)

    def test_resultados_vitoria_empate_derrota(self):
        partidas = [
            criar_partida(
                date(2024, 1, 10),
                "Brasil",
                "Argentina",
                2,
                0,
            ),
            criar_partida(
                date(2024, 1, 11),
                "Brasil",
                "Argentina",
                1,
                1,
            ),
            criar_partida(
                date(2024, 1, 12),
                "Brasil",
                "Argentina",
                0,
                2,
            ),
        ]

        registros = gerar_registros_pre_jogo(partidas)

        self.assertEqual(
            [registro.resultado for registro in registros],
            ["V", "E", "D"],
        )

    def test_fator_k_invalido(self):
        with self.assertRaises(ValueError):
            gerar_registros_pre_jogo([], fator_k=0)
    
    def test_probabilidades_integradas_ao_pre_jogo(self):
        partidas = [
            criar_partida(
                date(2024, 1, 10),
                "Brasil",
                "Argentina",
                2,
                1,
            ),
        ]

        registros = gerar_registros_pre_jogo(partidas)
        registro = registros[0]

        self.assertAlmostEqual(registro.prob_vitoria, 0.375)
        self.assertAlmostEqual(registro.prob_empate, 0.25)
        self.assertAlmostEqual(registro.prob_derrota, 0.375)

        self.assertAlmostEqual(
            registro.prob_vitoria
            + registro.prob_empate
            + registro.prob_derrota,
            1.0,
        )


if __name__ == "__main__":
    unittest.main()
