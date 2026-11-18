"""Comparação histórica entre Elo e baseline na validação."""

from collections.abc import Iterable
from dataclasses import dataclass, replace

from src.baseline_futebol import (
    BaselineFrequencias,
    ajustar_baseline_frequencias,
)
from src.metricas_preditivas import (
    MetricasPreditivas,
    avaliar_previsoes,
)
from src.previsao_pre_jogo import RegistroPreJogo
from src.validacao_temporal import dividir_registros_temporais


@dataclass(frozen=True)
class ResultadoAvaliacaoHistorica:
    """Resumo da comparação no período de validação."""

    quantidade_treinamento: int
    quantidade_validacao: int
    quantidade_teste: int
    baseline: BaselineFrequencias
    metricas_elo: MetricasPreditivas
    metricas_baseline: MetricasPreditivas
    diferenca_log_loss: float
    diferenca_brier_score: float


def avaliar_historico_validacao(
    registros: Iterable[RegistroPreJogo],
) -> ResultadoAvaliacaoHistorica:
    """Compara Elo e baseline sem avaliar o conjunto de teste.

    O baseline é ajustado exclusivamente no treinamento.

    As probabilidades Elo já devem ter sido geradas
    cronologicamente, antes dos resultados de cada dia.

    Diferenças negativas indicam vantagem do Elo.
    """

    divisao = dividir_registros_temporais(registros)

    treinamento = divisao.treinamento
    validacao = divisao.validacao
    teste = divisao.teste

    if not treinamento:
        raise ValueError(
            "Não existem partidas no período de treinamento."
        )

    if not validacao:
        raise ValueError(
            "Não existem partidas no período de validação."
        )

    baseline = ajustar_baseline_frequencias(
        treinamento,
        suavizacao=1.0,
    )

    metricas_elo = avaliar_previsoes(validacao)

    registros_baseline = [
        replace(
            registro,
            prob_vitoria=baseline.prob_vitoria,
            prob_empate=baseline.prob_empate,
            prob_derrota=baseline.prob_derrota,
        )
        for registro in validacao
    ]

    metricas_baseline = avaliar_previsoes(
        registros_baseline
    )

    return ResultadoAvaliacaoHistorica(
        quantidade_treinamento=len(treinamento),
        quantidade_validacao=len(validacao),
        quantidade_teste=len(teste),
        baseline=baseline,
        metricas_elo=metricas_elo,
        metricas_baseline=metricas_baseline,
        diferenca_log_loss=(
            metricas_elo.log_loss
            - metricas_baseline.log_loss
        ),
        diferenca_brier_score=(
            metricas_elo.brier_score
            - metricas_baseline.brier_score
        ),
    )
