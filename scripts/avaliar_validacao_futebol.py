"""Executa a avaliação histórica de validação da V8."""

from pathlib import Path

from src.avaliacao_historica import avaliar_historico_validacao
from src.dados_futebol import carregar_partidas
from src.previsao_pre_jogo import gerar_registros_pre_jogo


BASE = Path(__file__).resolve().parents[1]
ARQUIVO_PARTIDAS = (
    BASE / "data" / "processed" / "partidas_orbia.csv"
)


def main() -> None:
    if not ARQUIVO_PARTIDAS.is_file():
        raise FileNotFoundError(
            "Base histórica não encontrada. Execute primeiro: "
            "python -m scripts.reconstruir_base_futebol"
        )

    print("\nORBIA INTELLIGENCE — V8")
    print("Avaliação histórica de validação")
    print("=" * 48)

    partidas = carregar_partidas(ARQUIVO_PARTIDAS)

    print(f"Partidas carregadas: {len(partidas):,}")

    registros = gerar_registros_pre_jogo(partidas)

    resultado = avaliar_historico_validacao(registros)

    print("\nDIVISÃO TEMPORAL")
    print(f"Treinamento (até 2017): {resultado.quantidade_treinamento:,}")
    print(f"Validação (2018–2021): {resultado.quantidade_validacao:,}")
    print(f"Teste reservado (2022+): {resultado.quantidade_teste:,}")

    print("\nBASELINE — PROBABILIDADES")
    print(f"Vitória: {resultado.baseline.prob_vitoria:.4%}")
    print(f"Empate:  {resultado.baseline.prob_empate:.4%}")
    print(f"Derrota: {resultado.baseline.prob_derrota:.4%}")

    print("\nRESULTADOS — VALIDAÇÃO (2018–2021)")
    print(f"{'Métrica':<18} {'Elo':>12} {'Baseline':>12}")
    print("-" * 44)

    print(
        f"{'Log Loss':<18} "
        f"{resultado.metricas_elo.log_loss:>12.6f} "
        f"{resultado.metricas_baseline.log_loss:>12.6f}"
    )

    print(
        f"{'Brier Score':<18} "
        f"{resultado.metricas_elo.brier_score:>12.6f} "
        f"{resultado.metricas_baseline.brier_score:>12.6f}"
    )

    print("\nDIFERENÇAS (ELO - BASELINE)")
    print(f"Log Loss:    {resultado.diferenca_log_loss:+.6f}")
    print(f"Brier Score: {resultado.diferenca_brier_score:+.6f}")

    print("\nValores negativos indicam menor erro do Elo.")
    print("O conjunto de teste não foi avaliado.")


if __name__ == "__main__":
    main()
