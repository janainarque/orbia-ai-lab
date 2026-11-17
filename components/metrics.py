"""Indicadores do Orbia Intelligence."""

from collections.abc import Sequence

import streamlit as st

from src.retrospectiva import Previsao


def render_metrics(
    ranking_filtrado: Sequence[Previsao],
    total_selecoes: int,
) -> None:
    """Exibe os indicadores do recorte selecionado."""

    st.markdown("#### Panorama do recorte")

    st.caption(
        f"{len(ranking_filtrado)} de {total_selecoes} seleções "
        "incluídas na comparação"
    )

    c1, c2, c3 = st.columns(3)

    if not ranking_filtrado:
        c1.metric("Maior probabilidade no filtro", "—")
        c2.metric("Probabilidade atribuída", "—")
        c3.metric("Diferença entre as líderes", "—")
        return

    # O ranking original já vem ordenado por probabilidade.
    lider = ranking_filtrado[0]

    c1.metric(
        "Maior probabilidade no filtro",
        lider.selecao,
    )

    c2.metric(
        "Probabilidade atribuída",
        f"{lider.percentual:.1f}".replace(".", ",") + "%",
    )

    if len(ranking_filtrado) >= 2:
        margem = (
            ranking_filtrado[0].percentual
            - ranking_filtrado[1].percentual
        )

        c3.metric(
            "Diferença entre as líderes",
            f"{margem:.1f}".replace(".", ",") + " p.p.",
        )
    else:
        c3.metric("Diferença entre as líderes", "—")
