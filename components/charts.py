"""Gráficos do Orbia Intelligence."""

from collections.abc import Sequence

import altair as alt
import pandas as pd
import streamlit as st

from src.retrospectiva import Previsao


def render_probability_chart(
    ranking_filtrado: Sequence[Previsao],
) -> None:
    """Exibe o comparativo de probabilidades do ranking."""

    st.subheader("Probabilidades exibidas na gravação")

    if not ranking_filtrado:
        st.info(
            "Selecione pelo menos uma seleção para visualizar o gráfico."
        )
        return

    dados_grafico = [
        {
            "selecao": item.selecao,
            "percentual": item.percentual,
            "rotulo": f"{item.percentual:.1f}".replace(".", ",") + "%",
        }
        for item in ranking_filtrado
    ]

    df_grafico = pd.DataFrame(dados_grafico)
    ordem = [item.selecao for item in ranking_filtrado]

    eixo_y = alt.Y(
        "selecao:N",
        sort=ordem,
        title=None,
        axis=alt.Axis(
            labelColor="#D9E4F2",
            labelFontSize=13,
            labelPadding=12,
            ticks=False,
            domain=False,
        ),
    )

    barras = alt.Chart(df_grafico).mark_bar(
        size=26,
        cornerRadiusEnd=6,
    ).encode(
        x=alt.X(
            "percentual:Q",
            title="Probabilidade (%)",
            scale=alt.Scale(domain=[0, 20]),
            axis=alt.Axis(
                labelColor="#91A4BB",
                titleColor="#91A4BB",
                gridColor="#29384C",
                domain=False,
            ),
        ),
        y=eixo_y,
        color=alt.condition(
            alt.datum.selecao == ranking_filtrado[0].selecao,
            alt.value("#66E3C9"),
            alt.value("#8975ED"),
        ),
        tooltip=[
            alt.Tooltip("selecao:N", title="Seleção"),
            alt.Tooltip(
                "percentual:Q",
                title="Probabilidade (%)",
                format=".1f",
            ),
        ],
    )

    rotulos = alt.Chart(df_grafico).mark_text(
        align="left",
        baseline="middle",
        dx=10,
        fontSize=13,
        fontWeight="bold",
        color="#E9F0FA",
    ).encode(
        x="percentual:Q",
        y=eixo_y,
        text="rotulo:N",
    )

    grafico = (
        alt.layer(barras, rotulos)
        .properties(
            height=max(220, len(ranking_filtrado) * 58),
            background="#121D2B",
        )
        .configure_view(stroke=None)
    )

    with st.container(border=True):
        st.markdown("**Comparativo de probabilidades**")
        st.caption("Ranking parcial observado na demonstração")
        st.altair_chart(
            grafico,
            use_container_width=True,
            theme=None,
        )
