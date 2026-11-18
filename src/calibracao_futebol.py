"""Análise de calibração das probabilidades da V8."""

from dataclasses import dataclass
from collections.abc import Iterable

from src.metricas_preditivas import avaliar_previsoes
from src.previsao_pre_jogo import RegistroPreJogo
from src.validacao_temporal import dividir_registros_temporais


CLASSES = (
    ("V", "Vitória", "prob_vitoria"),
    ("E", "Empate", "prob_empate"),
    ("D", "Derrota", "prob_derrota"),
)


@dataclass(frozen=True)
class FaixaCalibracao:
    indice: int
    limite_inferior: float
    limite_superior: float
    quantidade: int
    probabilidade_media: float
    frequencia_observada: float


@dataclass(frozen=True)
class CalibracaoClasse:
    resultado: str
    nome: str
    quantidade_partidas: int
    erro_calibracao_esperado: float
    faixas: tuple[FaixaCalibracao, ...]


def calcular_calibracao_validacao(
    registros: Iterable[RegistroPreJogo],
    quantidade_faixas: int = 10,
) -> tuple[CalibracaoClasse, ...]:
    """Avalia calibração exclusivamente na validação temporal.

    O ECE é calculado por classe, no formato um-contra-resto.

    O conjunto de teste não participa dos cálculos.
    """

    if (
        isinstance(quantidade_faixas, bool)
        or not isinstance(quantidade_faixas, int)
        or not 2 <= quantidade_faixas <= 100
    ):
        raise ValueError(
            "A quantidade de faixas deve estar entre 2 e 100."
        )

    divisao = dividir_registros_temporais(registros)
    validacao = divisao.validacao

    if not validacao:
        raise ValueError(
            "Não existem partidas no período de validação."
        )

    # Reutiliza as validações de probabilidades e resultados.
    avaliar_previsoes(validacao)

    quantidade_total = len(validacao)
    resultados = []

    for codigo, nome, atributo in CLASSES:
        grupos = [
            {"quantidade": 0, "soma_prob": 0.0, "observados": 0}
            for _ in range(quantidade_faixas)
        ]

        for registro in validacao:
            probabilidade = getattr(registro, atributo)

            indice = min(
                int(probabilidade * quantidade_faixas),
                quantidade_faixas - 1,
            )

            grupo = grupos[indice]
            grupo["quantidade"] += 1
            grupo["soma_prob"] += probabilidade

            if registro.resultado == codigo:
                grupo["observados"] += 1

        faixas = []
        erro_calibracao = 0.0

        for indice, grupo in enumerate(grupos):
            quantidade = grupo["quantidade"]

            if quantidade == 0:
                continue

            probabilidade_media = (
                grupo["soma_prob"] / quantidade
            )

            frequencia_observada = (
                grupo["observados"] / quantidade
            )

            erro_calibracao += (
                quantidade / quantidade_total
            ) * abs(
                probabilidade_media - frequencia_observada
            )

            faixas.append(
                FaixaCalibracao(
                    indice=indice,
                    limite_inferior=indice / quantidade_faixas,
                    limite_superior=(
                        (indice + 1) / quantidade_faixas
                    ),
                    quantidade=quantidade,
                    probabilidade_media=probabilidade_media,
                    frequencia_observada=frequencia_observada,
                )
            )

        resultados.append(
            CalibracaoClasse(
                resultado=codigo,
                nome=nome,
                quantidade_partidas=quantidade_total,
                erro_calibracao_esperado=erro_calibracao,
                faixas=tuple(faixas),
            )
        )

    return tuple(resultados)
