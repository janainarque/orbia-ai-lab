"""Dashboard de validação preditiva do Orbia Intelligence."""

from dataclasses import replace
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from src.ajuste_probabilidades_futebol import (
    ajustar_probabilidades_treinamento,
    prever_probabilidades_ajustadas,
)
from src.avaliacao_historica import avaliar_historico_validacao
from src.calibracao_futebol import calcular_calibracao_validacao
from src.dados_futebol import carregar_partidas
from src.metricas_preditivas import avaliar_previsoes
from src.previsao_pre_jogo import gerar_registros_pre_jogo
from src.validacao_temporal import dividir_registros_temporais


BASE = Path(__file__).resolve().parents[1]
ARQUIVO_PARTIDAS = BASE / "data" / "processed" / "partidas_orbia.csv"


@st.cache_data(show_spinner=False)
def obter_avaliacao_preditiva(caminho: str, versao_arquivo: int):
    """Avalia baseline, Elo original e Elo ajustado."""

    partidas = carregar_partidas(caminho)
    registros = gerar_registros_pre_jogo(partidas)

    resultado = avaliar_historico_validacao(registros)

    divisao = dividir_registros_temporais(registros)

    # Os parâmetros são selecionados somente no treinamento.
    parametros = ajustar_probabilidades_treinamento(registros)

    registros_ajustados = []

    for registro in divisao.validacao:
        probabilidades = prever_probabilidades_ajustadas(
            registro,
            ajuste_elo_mandante=parametros.ajuste_elo_mandante,
            taxa_empate_equilibrado=parametros.taxa_empate_equilibrado,
        )

        registros_ajustados.append(
            replace(
                registro,
                prob_vitoria=probabilidades.vitoria,
                prob_empate=probabilidades.empate,
                prob_derrota=probabilidades.derrota,
            )
        )

    metricas_ajustado = avaliar_previsoes(
        tuple(registros_ajustados)
    )

    # Calibração calculada somente na validação temporal.
    calibracao_original = calcular_calibracao_validacao(
        divisao.validacao
    )

    calibracao_ajustado = calcular_calibracao_validacao(
        tuple(registros_ajustados)
    )

    return (
        resultado,
        metricas_ajustado,
        parametros,
        calibracao_original,
        calibracao_ajustado,
    )

def render_predictive_dashboard() -> None:
    """Renderiza a avaliação preditiva histórica."""

    st.subheader("Validação preditiva")

    st.caption(
        "Avaliação experimental das probabilidades de resultados "
        "de partidas internacionais, utilizando validação temporal."
    )

    if not ARQUIVO_PARTIDAS.is_file():
        st.warning(
            "A base histórica não foi encontrada. "
            "Reconstrua os dados antes de utilizar este painel."
        )
        st.code(
            "python -m scripts.reconstruir_base_futebol",
            language="powershell",
        )
        return

    try:
        with st.spinner("Calculando métricas preditivas..."):
            (
                resultado,
                metricas_ajustado,
                parametros,
                calibracao_original,
                calibracao_ajustado,
            ) = obter_avaliacao_preditiva(
                str(ARQUIVO_PARTIDAS),
                ARQUIVO_PARTIDAS.stat().st_mtime_ns,
            )

    except (OSError, ValueError) as erro:
        st.error(f"Não foi possível avaliar o histórico: {erro}")
        return

    st.markdown("#### Desempenho histórico")

    baseline = resultado.metricas_baseline
    ajustado = metricas_ajustado

    reducao_log_loss = (
        (baseline.log_loss - ajustado.log_loss)
        / baseline.log_loss
        * 100
    )

    reducao_brier = (
        (baseline.brier_score - ajustado.brier_score)
        / baseline.brier_score
        * 100
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Partidas de validação",
        f"{resultado.quantidade_validacao:,}".replace(",", "."),
        help="Partidas utilizadas na validação temporal (2018–2021).",
    )

    c2.metric(
        "Log Loss — Elo ajustado",
        f"{ajustado.log_loss:.4f}",
        delta=f"{reducao_log_loss:.1f}% menor que baseline",
        delta_color="normal",
    )

    c3.metric(
        "Brier Score — Elo ajustado",
        f"{ajustado.brier_score:.4f}",
        delta=f"{reducao_brier:.1f}% menor que baseline",
        delta_color="normal",
    )

    st.markdown("#### Comparação de modelos")

    comparacao = pd.DataFrame(
        [
            {
                "Modelo": "Baseline",
                "Log Loss": resultado.metricas_baseline.log_loss,
                "Brier Score": resultado.metricas_baseline.brier_score,
            },
            {
                "Modelo": "Elo original",
                "Log Loss": resultado.metricas_elo.log_loss,
                "Brier Score": resultado.metricas_elo.brier_score,
            },
            {
                "Modelo": "Elo ajustado",
                "Log Loss": metricas_ajustado.log_loss,
                "Brier Score": metricas_ajustado.brier_score,
            },
        ]
    )

    st.dataframe(
        comparacao,
        hide_index=True,
        width="stretch",
        column_config={
            "Log Loss": st.column_config.NumberColumn(format="%.4f"),
            "Brier Score": st.column_config.NumberColumn(format="%.4f"),
        },
    )

    st.markdown("#### Log Loss por modelo")

    st.bar_chart(
        comparacao,
        x="Modelo",
        y="Log Loss",
        horizontal=True,
    )

    st.caption(
        "Valores menores de Log Loss e Brier Score "
        "indicam melhor desempenho preditivo."
    )

    st.info(
        "Treinamento: até 2017. Validação: 2018–2021. "
        "O conjunto de teste (2022 em diante) permanece reservado "
        "e não foi utilizado nesta avaliação."
    )

    st.markdown("#### Calibração das probabilidades")

    st.caption(
        "O Expected Calibration Error (ECE) mede a diferença "
        "entre as probabilidades previstas e as frequências observadas. "
        "Valores menores indicam melhor calibração."
    )

    dados_calibracao = []

    for original, ajustado in zip(
        calibracao_original,
        calibracao_ajustado,
    ):
        dados_calibracao.append(
            {
                "Resultado": original.nome,
                "ECE original (%)": (
                    original.erro_calibracao_esperado * 100
                ),
                "ECE ajustado (%)": (
                    ajustado.erro_calibracao_esperado * 100
                ),
                "Diferença (pp)": (
                    ajustado.erro_calibracao_esperado
                    - original.erro_calibracao_esperado
                ) * 100,
            }
        )

    tabela_calibracao = pd.DataFrame(dados_calibracao)

    st.dataframe(
        tabela_calibracao,
        hide_index=True,
        width="stretch",
        column_config={
            "ECE original (%)": st.column_config.NumberColumn(
                format="%.2f"
            ),
            "ECE ajustado (%)": st.column_config.NumberColumn(
                format="%.2f"
            ),
            "Diferença (pp)": st.column_config.NumberColumn(
                format="%+.2f"
            ),
        },
    )

    st.caption(
        "Diferenças negativas indicam redução do erro de calibração. "
        "O ECE é sensível à quantidade e à distribuição das faixas."
    )

    st.markdown("#### Gráfico de confiabilidade")

    classe_selecionada = st.selectbox(
        "Resultado analisado",
        options=[item.nome for item in calibracao_original],
        key="classe_calibracao",
    )

    dados_confiabilidade = []

    for modelo, calibracoes in (
        ("Elo original", calibracao_original),
        ("Elo ajustado", calibracao_ajustado),
    ):
        classe = next(
            item
            for item in calibracoes
            if item.nome == classe_selecionada
        )

        for faixa in classe.faixas:
            dados_confiabilidade.append(
                {
                    "Modelo": modelo,
                    "Probabilidade prevista": faixa.probabilidade_media,
                    "Frequência observada": faixa.frequencia_observada,
                    "Partidas": faixa.quantidade,
                }
            )

    df_confiabilidade = pd.DataFrame(dados_confiabilidade)

    linha_ideal = alt.Chart(
        pd.DataFrame(
            {
                "Probabilidade prevista": [0.0, 1.0],
                "Frequência observada": [0.0, 1.0],
            }
        )
    ).mark_line(
        color="#94A3B8",
        strokeDash=[6, 5],
    ).encode(
        x="Probabilidade prevista:Q",
        y="Frequência observada:Q",
    )

    curvas = alt.Chart(df_confiabilidade).mark_line(
        point=True,
        strokeWidth=3,
    ).encode(
        x=alt.X(
            "Probabilidade prevista:Q",
            title="Probabilidade prevista",
            axis=alt.Axis(format=".0%"),
            scale=alt.Scale(domain=[0, 1]),
        ),
        y=alt.Y(
            "Frequência observada:Q",
            title="Frequência observada",
            axis=alt.Axis(format=".0%"),
            scale=alt.Scale(domain=[0, 1]),
        ),
        color=alt.Color(
            "Modelo:N",
            title="Modelo",
        ),
        tooltip=[
            "Modelo:N",
            alt.Tooltip(
                "Probabilidade prevista:Q",
                format=".1%",
            ),
            alt.Tooltip(
                "Frequência observada:Q",
                format=".1%",
            ),
            "Partidas:Q",
        ],
    )

    grafico = alt.layer(
        linha_ideal,
        curvas,
    ).properties(
        height=380,
    )

    st.altair_chart(
        grafico,
        width="stretch",
    )

    st.caption(
        "Linha tracejada: calibração perfeita. "
        "Cada ponto representa uma faixa de probabilidade. "
        "Passe o mouse sobre os pontos para consultar "
        "a quantidade de partidas."
    )

    with st.expander("Consultar distribuição das partidas por faixa"):
        distribuicao = df_confiabilidade.copy()

        distribuicao["Probabilidade prevista"] *= 100
        distribuicao["Frequência observada"] *= 100

        st.dataframe(
            distribuicao,
            hide_index=True,
            width="stretch",
            column_config={
                "Probabilidade prevista": st.column_config.NumberColumn(
                    "Probabilidade prevista (%)",
                    format="%.1f",
                ),
                "Frequência observada": st.column_config.NumberColumn(
                    "Frequência observada (%)",
                    format="%.1f",
                ),
                "Partidas": st.column_config.NumberColumn(
                    "Partidas",
                    format="%d",
                ),
            },
        )

        st.caption(
            "Faixas com poucas partidas devem ser interpretadas "
            "com cautela, pois suas frequências observadas "
            "podem apresentar maior variabilidade."
        )