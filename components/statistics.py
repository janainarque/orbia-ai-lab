"""Componente de estatísticas descritivas do Orbia."""

from collections.abc import Sequence

import streamlit as st

from src.estatisticas import analisar_recorte
from src.retrospectiva import Previsao


def render_statistical_summary(
    ranking: Sequence[Previsao],
) -> None:
    """Exibe os indicadores do ranking observado."""

    st.markdown("### Inteligência estatística")

    st.caption(
        "Análise descritiva das seleções observadas "
        "na gravação original, independentemente do filtro."
    )

    estatisticas = analisar_recorte(ranking)

    with st.container(border=True):
        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Percentual observado",
            f"{estatisticas.percentual_observado:.1f}%"
            .replace(".", ","),
        )

        col2.metric(
            "Complemento até 100%",
            f"{estatisticas.percentual_nao_exibido:.1f}%"
            .replace(".", ","),
        )

        col3.metric(
            "Soma das duas líderes",
            f"{estatisticas.concentracao_duas_lideres:.1f}%"
            .replace(".", ","),
        )

        col4.metric(
            "Amplitude do ranking",
            f"{estatisticas.amplitude_pp:.1f} p.p."
            .replace(".", ","),
        )

    st.caption(
        "Indicadores descritivos do ranking parcial. "
        "O complemento até 100% não identifica resultados "
        "ausentes nem representa uma nova previsão."
    )
