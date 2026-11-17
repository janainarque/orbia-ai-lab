
"""Interface do laboratório Monte Carlo do Orbia Intelligence."""

import math

import altair as alt
import pandas as pd
import streamlit as st

from src.simulacao import Participante, simular_torneios


def render_simulator() -> None:
    """Renderiza controles e resultados do simulador."""

    st.subheader("Laboratório Monte Carlo")

    st.caption(
        "Experimente cenários, ajuste ratings e execute "
        "torneios eliminatórios simulados."
    )

    st.info(
        "Este laboratório utiliza seleções reais com ratings "
        "experimentais e ilustrativos. Os resultados não "
        "representam previsões oficiais da Copa de 2026."
    )

    nomes = ["Brasil", "Argentina", "França", "Espanha"]
    ratings_iniciais = [1800, 1750, 1650, 1600]

    with st.form("formulario_monte_carlo"):
        st.markdown("#### Configuração dos participantes")

        colunas = st.columns(4)
        participantes = []

        for coluna, nome, rating in zip(
            colunas,
            nomes,
            ratings_iniciais,
        ):
            with coluna:
                valor = st.number_input(
                    f"Rating · {nome}",
                    min_value=0,
                    max_value=3000,
                    value=rating,
                    step=25,
                )

                participantes.append(
                    Participante(nome, valor)
                )

        col1, col2 = st.columns(2)

        with col1:
            quantidade = st.number_input(
                "Quantidade de torneios",
                min_value=1000,
                max_value=100000,
                value=10000,
                step=1000,
            )

        with col2:
            semente = st.number_input(
                "Semente aleatória",
                value=42,
                step=1,
            )

        executar = st.form_submit_button(
            "Executar simulação",
            type="primary",
            use_container_width=True,
        )

    if executar:
        resultado = simular_torneios(
            participantes,
            quantidade=int(quantidade),
            semente=int(semente),
        )

        # Guarda o resultado junto com os parâmetros
        # efetivamente utilizados na execução.
        st.session_state["orbia_ultima_simulacao"] = {
            "resultado": resultado,
            "participantes": tuple(participantes),
        }

    execucao = st.session_state.get(
        "orbia_ultima_simulacao"
    )

    if execucao is None:
        st.info(
            "Configure os parâmetros e clique em "
            "'Executar simulação' para começar."
        )
        return

    resultado = execucao["resultado"]
    participantes_executados = execucao["participantes"]

    dados = pd.DataFrame(
        [
            {
                "Participante": nome,
                "Frequencia": probabilidade,
                "Titulos": resultado.titulos[nome],
                "Rotulo": f"{probabilidade:.2f}%".replace(
                    ".", ","
                ),
            }
            for nome, probabilidade
            in resultado.probabilidades.items()
        ]
    ).sort_values(
        "Frequencia",
        ascending=False,
    )

    lider = dados.iloc[0]

    st.markdown("### Resultados da simulação")

    st.caption(
        "Os resultados abaixo pertencem à última "
        "execução concluída. Alterações no formulário "
        "só entram em vigor ao executar novamente."
    )

    with st.container(border=True):
        st.markdown("**Cenário analisado**")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Torneios simulados",
            f"{resultado.simulacoes:,}".replace(",", "."),
        )

        col2.metric(
            "Participante mais frequente",
            str(lider["Participante"]),
        )

        col3.metric(
            "Frequência de títulos",
            f"{lider['Frequencia']:.2f}%".replace(".", ","),
        )

        st.caption(
            f"Semente: {resultado.semente} · "
            "Torneio eliminatório com duas semifinais "
            "e uma final."
        )

    st.markdown("#### Distribuição de títulos")

    ordem = dados["Participante"].tolist()

    maior_frequencia = float(dados["Frequencia"].max())

    # Reserva espaço à direita das barras
    # para exibir os rótulos percentuais.
    limite_eixo = min(
        110,
        max(
            50,
            math.ceil(maior_frequencia / 10) * 10 + 10,
        ),
    )

    eixo_y = alt.Y(
        "Participante:N",
        sort=ordem,
        title=None,
        axis=alt.Axis(
            labelColor="#D9E4F2",
            labelFontSize=13,
            ticks=False,
            domain=False,
        ),
    )

    eixo_x = alt.X(
        "Frequencia:Q",
        title="Frequência de títulos (%)",
        scale=alt.Scale(domain=[0, limite_eixo]),
        axis=alt.Axis(
            labelColor="#91A4BB",
            titleColor="#91A4BB",
            gridColor="#29384C",
            tickCount=6,
            domain=False,
        ),
    )

    barras = alt.Chart(dados).mark_bar(
        cornerRadiusEnd=6,
        size=28,
    ).encode(
        x=eixo_x,
        y=eixo_y,
        color=alt.condition(
            alt.datum.Participante == lider["Participante"],
            alt.value("#66E3C9"),
            alt.value("#8975ED"),
        ),
        tooltip=[
            alt.Tooltip(
                "Participante:N",
                title="Participante",
            ),
            alt.Tooltip(
                "Frequencia:Q",
                title="Frequência (%)",
                format=".2f",
            ),
            alt.Tooltip(
                "Titulos:Q",
                title="Títulos",
                format=",d",
            ),
        ],
    )

    rotulos = alt.Chart(dados).mark_text(
        align="left",
        baseline="middle",
        dx=10,
        fontSize=13,
        fontWeight="bold",
        color="#E9F0FA",
    ).encode(
        x="Frequencia:Q",
        y=eixo_y,
        text="Rotulo:N",
    )

    grafico = (
        alt.layer(barras, rotulos)
        .properties(
            height=260,
            background="#121D2B",
        )
        .configure_view(stroke=None)
    )

    with st.container(border=True):
        st.altair_chart(
            grafico,
            use_container_width=True,
            theme=None,
        )

    st.markdown("#### Parâmetros da última execução")

    parametros = pd.DataFrame(
        [
            {
                "Participante": item.nome,
                "Rating utilizado": item.rating,
                "Títulos": resultado.titulos[item.nome],
                "Frequência (%)": resultado.probabilidades[
                    item.nome
                ],
            }
            for item in participantes_executados
        ]
    ).sort_values(
        "Frequência (%)",
        ascending=False,
    )

    st.dataframe(
        parametros,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Frequência (%)": st.column_config.NumberColumn(
                "Frequência (%)",
                format="%.2f",
            ),
        },
    )

    with st.expander("Como funciona esta simulação?"):
        st.markdown(
            r"""
            **Modelo experimental**

            Cada participante recebe um rating que
            representa sua força relativa no cenário.

            A probabilidade de vitória é calculada
            por uma fórmula inspirada no sistema Elo:

            \[
            P(A) = \\frac{1}{1 + 10^{(R_B-R_A)/400}}
            \]

            **Formato do torneio**

            - Brasil enfrenta Argentina na primeira semifinal.
            - França enfrenta Espanha na segunda semifinal.
            - Os vencedores disputam a final.
            - O processo é repetido pela quantidade de torneios configurada.

            **Interpretação**

            A frequência de títulos corresponde à
            proporção de simulações vencidas por cada
            participante.

            O modelo não considera empates, mando
            de campo, lesões ou outras variáveis reais.
            Não representa uma previsão oficial.
            """
        )
