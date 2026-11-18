"""Executa a análise histórica de calibração do Orbia V8."""

from pathlib import Path

from src.calibracao_futebol import calcular_calibracao_validacao
from src.dados_futebol import carregar_partidas
from src.previsao_pre_jogo import gerar_registros_pre_jogo
from src.validacao_temporal import dividir_registros_temporais

ARQUIVO_PARTIDAS = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "processed"
    / "partidas_orbia.csv"
)


def main():
    print("=" * 64)
    print("ORBIA INTELLIGENCE — V8")
    print("Análise de calibração preditiva")
    print("=" * 64)

    partidas = carregar_partidas(ARQUIVO_PARTIDAS)
    registros = gerar_registros_pre_jogo(partidas)

    resultados = calcular_calibracao_validacao(
        registros,
        quantidade_faixas=10,
    )

    print(f"\nPartidas históricas: {len(partidas):,}")
    print(
        "Período avaliado: 2018–2021 "
        "(validação temporal)"
    )
    

    # Diagnóstico global de viés por resultado.
    validacao = dividir_registros_temporais(
        registros
    ).validacao

    total = len(validacao)

    print("\n" + "=" * 64)
    print("DIAGNÓSTICO GLOBAL — PREVISTO VS. OBSERVADO")
    print("=" * 64)

    print(
        f"{'Resultado':<12}"
        f"{'Previsto':>12}"
        f"{'Observado':>13}"
        f"{'Diferença':>13}"
    )

    classes = (
        ("Vitória", "V", "prob_vitoria"),
        ("Empate", "E", "prob_empate"),
        ("Derrota", "D", "prob_derrota"),
    )

    for nome, codigo, atributo in classes:
        previsto = sum(
            getattr(registro, atributo)
            for registro in validacao
        ) / total

        observado = sum(
            registro.resultado == codigo
            for registro in validacao
        ) / total

        diferenca = previsto - observado

        print(
            f"{nome:<12}"
            f"{previsto:>11.2%}"
            f"{observado:>13.2%}"
            f"{diferenca * 100:>+12.2f} pp"
        )
        
    
    
    # Diagnóstico temporal: treinamento vs. validação.
    divisao = dividir_registros_temporais(registros)

    print("\n" + "=" * 64)
    print("COMPARAÇÃO TEMPORAL — VIÉS DO MODELO")
    print("=" * 64)

    periodos = (
        ("Treinamento (até 2017)", divisao.treinamento),
        ("Validação (2018–2021)", divisao.validacao),
    )

    for nome_periodo, amostra in periodos:
        print(f"\n{nome_periodo}")
        print(f"Partidas: {len(amostra):,}")

        print(
            f"{'Resultado':<12}"
            f"{'Previsto':>12}"
            f"{'Observado':>13}"
            f"{'Diferença':>13}"
        )

        total = len(amostra)

        if total == 0:
            print("Nenhuma partida disponível.")
            continue

        for nome, codigo, atributo in classes:
            previsto = sum(
                getattr(registro, atributo)
                for registro in amostra
            ) / total

            observado = sum(
                registro.resultado == codigo
                for registro in amostra
            ) / total

            diferenca = (previsto - observado) * 100

            print(
                f"{nome:<12}"
                f"{previsto:>11.2%}"
                f"{observado:>13.2%}"
                f"{diferenca:>+12.2f} pp"
            )


    for classe in resultados:
        print("\n" + "-" * 64)
        print(f"RESULTADO: {classe.nome.upper()}")
        print("-" * 64)

        print(
            f"Partidas na validação: "
            f"{classe.quantidade_partidas:,}"
        )
        print(
            f"ECE: "
            f"{classe.erro_calibracao_esperado:.6f}"
        )

        print(
            f"\n{'Faixa':<13}"
            f"{'Partidas':>10}"
            f"{'Previsto':>13}"
            f"{'Observado':>13}"
        )

        for faixa in classe.faixas:
            intervalo = (
                f"{faixa.limite_inferior:.0%}"
                f"–{faixa.limite_superior:.0%}"
            )

            print(
                f"{intervalo:<13}"
                f"{faixa.quantidade:>10}"
                f"{faixa.probabilidade_media:>12.2%}"
                f"{faixa.frequencia_observada:>13.2%}"
            )

    print("\n" + "=" * 64)
    print("INTERPRETAÇÃO")
    print("=" * 64)
    print(
        "ECE menor indica menor diferença entre "
        "probabilidades previstas e frequências observadas."
    )
    print(
        "A métrica depende do agrupamento em faixas "
        "e não substitui Log Loss ou Brier Score."
    )
    print(
        "O conjunto de teste (2022+) não foi avaliado."
    )


if __name__ == "__main__":
    main()
