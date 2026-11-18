"""Testes da separação temporal da V8."""

import unittest
from datetime import date

from src.dados_futebol import RegistroPartida
from src.previsao_pre_jogo import gerar_registros_pre_jogo
from src.validacao_temporal import dividir_registros_temporais


def criar_partida(data, casa="Brasil", fora="Argentina"):
    return RegistroPartida(
        data=data,
        selecao_casa=casa,
        selecao_fora=fora,
        gols_casa=1,
        gols_fora=0,
        competicao="Amistoso de teste",
        fonte_url="https://example.com/teste",
    )


class TestValidacaoTemporal(unittest.TestCase):

    def setUp(self):
        partidas = [
            criar_partida(date(2017, 12, 31)),
            criar_partida(date(2018, 1, 1)),
            criar_partida(date(2021, 12, 31)),
            criar_partida(date(2022, 1, 1)),
            criar_partida(date(2026, 10, 6)),
        ]

        self.registros = gerar_registros_pre_jogo(partidas)

    def test_divisao_dos_periodos(self):
        divisao = dividir_registros_temporais(self.registros)

        self.assertEqual(len(divisao.treinamento), 1)
        self.assertEqual(len(divisao.validacao), 2)
        self.assertEqual(len(divisao.teste), 2)

    def test_limites_temporais(self):
        divisao = dividir_registros_temporais(self.registros)

        self.assertEqual(
            divisao.treinamento[-1].data,
            date(2017, 12, 31),
        )
        self.assertEqual(
            divisao.validacao[0].data,
            date(2018, 1, 1),
        )
        self.assertEqual(
            divisao.teste[0].data,
            date(2022, 1, 1),
        )

    def test_nenhum_registro_perdido(self):
        divisao = dividir_registros_temporais(self.registros)

        total = (
            len(divisao.treinamento)
            + len(divisao.validacao)
            + len(divisao.teste)
        )

        self.assertEqual(total, len(self.registros))

    def test_ordem_de_entrada_nao_altera_divisao(self):
        original = dividir_registros_temporais(self.registros)

        invertido = dividir_registros_temporais(
            reversed(self.registros)
        )

        self.assertEqual(original, invertido)

    def test_historico_vazio(self):
        divisao = dividir_registros_temporais([])

        self.assertEqual(divisao.treinamento, ())
        self.assertEqual(divisao.validacao, ())
        self.assertEqual(divisao.teste, ())

    def test_limites_invalidos(self):
        with self.assertRaises(ValueError):
            dividir_registros_temporais(
                self.registros,
                inicio_validacao=date(2022, 1, 1),
                inicio_teste=date(2018, 1, 1),
            )

        with self.assertRaises(ValueError):
            dividir_registros_temporais(
                self.registros,
                inicio_validacao=date(2022, 1, 1),
                inicio_teste=date(2022, 1, 1),
            )

    def test_limites_personalizados(self):
        divisao = dividir_registros_temporais(
            self.registros,
            inicio_validacao=date(2020, 1, 1),
            inicio_teste=date(2025, 1, 1),
        )

        self.assertEqual(len(divisao.treinamento), 2)
        self.assertEqual(len(divisao.validacao), 2)
        self.assertEqual(len(divisao.teste), 1)


if __name__ == "__main__":
    unittest.main()
