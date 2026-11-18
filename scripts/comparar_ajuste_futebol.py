"""Compara Elo original e Elo ajustado na validação temporal."""

from dataclasses import replace
from pathlib import Path

from src.ajuste_probabilidades_futebol import (
    ajustar_probabilidades_treinamento,
    prever_probabilidades_ajustadas,
)
from src.calibracao_futebol import calcular_calibracao_validacao
from src.dados_futebol import carregar_partidas
from src.metricas_preditivas import avaliar_previsoes
from src.previsao_pre_jogo import gerar_registros_pre_jogo
from src.validacao_temporal import dividir_registros_temporais


ARQUIVO_PARTIDAS = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "processed"
    / "partidas_orbia.csv"
)

CLASSES = (
    ("Vitória", "V", "prob_vitoria"),
    ("Empate", "E", "prob_empate"),
    ("Derrota", "D", "prob_derrota"),
)


def mostrar_vies(registros):
    """Mostra probabilidades médias e frequências observadas."""

    total = len(registros)

    print(
        f"{'Resultado':<12}"
        f"{'Previsto':>12}"
        f"{'Observado':>13}"
        f"{'Diferença':>13}"
    )

    for nome, codigo, atributo in CLASSES:
        previsto = sum(
            getattr(registro, atributo)
            for registro in registros
        ) / total

        observado = sum(
            registro.resultado == codigo
            for registro in registros
        ) / total

        diferenca = (previsto - observado) * 100

        print(
            f"{nome:<12}"
            f"{previsto:>11.2%}"
            f"{observado:>13.2%}"
            f"{diferenca:>+12.2f} pp"
        )


def main():
    print("=" * 68)
    print("ORBIA INTELLIGENCE — V8")
    print("Comparação preditiva: Elo original vs. Elo ajustado")
    print("=" * 68)

    partidas = carregar_partidas(ARQUIVO_PARTIDAS)
    registros = gerar_registros_pre_jogo(partidas)

    divisao = dividir_registros_temporais(registros)

    print("\nDIVISÃO TEMPORAL")
    print(f"Treinamento: {len(divisao.treinamento):,}")
    print(f"Validação:   {len(divisao.validacao):,}")
    print(f"Teste:       {len(divisao.teste):,} (reservado)")

    print("\nSelecionando parâmetros no treinamento...")

    parametros = ajustar_probabilidades_treinamento(
        registros
    )

    print("\nPARÂMETROS SELECIONADOS")
    print(
        "Ajuste Elo mandante: "
        f"{parametros.ajuste_elo_mandante:.0f} pontos"
    )
    print(
        "Taxa empate equilibrado: "
        f"{parametros.taxa_empate_equilibrado:.2%}"
    )
    print(
        "Log Loss treinamento ajustado: "
        f"{parametros.log_loss_treinamento:.6f}"
    )

    original = divisao.validacao

    ajustado = []

    for registro in original:
        probabilidades = prever_probabilidades_ajustadas(
            registro,
            ajuste_elo_mandante=(
                parametros.ajuste_elo_mandante
            ),
            taxa_empate_equilibrado=(
                parametros.taxa_empate_equilibrado
            ),
        )

        ajustado.append(
            replace(
                registro,
                prob_vitoria=probabilidades.vitoria,
                prob_empate=probabilidades.empate,
                prob_derrota=probabilidades.derrota,
            )
        )

    ajustado = tuple(ajustado)

    metricas_original = avaliar_previsoes(original)
    metricas_ajustado = avaliar_previsoes(ajustado)

    print("\n" + "=" * 68)
    print("MÉTRICAS — VALIDAÇÃO (2018–2021)")
    print("=" * 68)

    print(
        f"{'Métrica':<22}"
        f"{'Original':>14}"
        f"{'Ajustado':>14}"
        f"{'Diferença':>14}"
    )

    metricas = (
        (
            "Log Loss",
            metricas_original.log_loss,
            metricas_ajustado.log_loss,
        ),
        (
            "Brier Score",
            metricas_original.brier_score,
            metricas_ajustado.brier_score,
        ),
    )

    for nome, antes, depois in metricas:
        print(
            f"{nome:<22}"
            f"{antes:>14.6f}"
            f"{depois:>14.6f}"
            f"{depois - antes:>+14.6f}"
        )

    print("\n" + "=" * 68)
    print("CALIBRAÇÃO — EXPECTED CALIBRATION ERROR")
    print("=" * 68)

    calibracao_original = calcular_calibracao_validacao(
        original
    )
    calibracao_ajustado = calcular_calibracao_validacao(
        ajustado
    )

    print(
        f"{'Resultado':<14}"
        f"{'Original':>14}"
        f"{'Ajustado':>14}"
        f"{'Diferença':>14}"
    )

    for antes, depois in zip(
        calibracao_original,
        calibracao_ajustado,
    ):
        print(
            f"{antes.nome:<14}"
            f"{antes.erro_calibracao_esperado:>14.6f}"
            f"{depois.erro_calibracao_esperado:>14.6f}"
            f"{depois.erro_calibracao_esperado - antes.erro_calibracao_esperado:>+14.6f}"
        )

    print("\n" + "=" * 68)
    print("VIÉS GLOBAL — MODELO ORIGINAL")
    print("=" * 68)
    mostrar_vies(original)

    print("\n" + "=" * 68)
    print("VIÉS GLOBAL — MODELO AJUSTADO")
    print("=" * 68)
    mostrar_vies(ajustado)

    print("\n" + "=" * 68)
    print("INTERPRETAÇÃO")
    print("=" * 68)
    print(
        "Diferenças negativas em Log Loss, Brier e ECE "
        "indicam menor erro do modelo ajustado."
    )
    print(
        "O ECE é sensível às faixas de probabilidade."
    )
    print(
        "A seleção de parâmetros utilizou somente o treinamento."
    )
    print(
        "O conjunto de teste (2022+) não foi avaliado."
    )


if __name__ == "__main__":
    main()
