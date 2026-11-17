"""Dashboard de ranking Elo do Orbia Intelligence."""

from datetime import date

import altair as alt
import pandas as pd
import streamlit as st

from components.historical import (
    ARQUIVO_PARTIDAS,
    obter_partidas,
)
from src.ranking_elo import gerar_ranking_elo

from src.evolucao_elo import calcular_evolucao_elo

def render_elo_dashboard() -> None:
    """Renderiza o ranking Elo histórico e seus filtros."""

    st.subheader("Ranking Elo de seleções")

    st.caption(
        "Avaliação experimental de força relativa baseada "
        "em resultados históricos de partidas internacionais."
    )

    if not ARQUIVO_PARTIDAS.is_file():
        st.warning(
            "A base histórica não foi encontrada. "
            "Reconstrua os dados antes de utilizar o ranking."
        )
        st.code(
            "python -m scripts.reconstruir_base_futebol",
            language="powershell",
        )
        return

    try:
        partidas = obter_partidas(str(ARQUIVO_PARTIDAS))
    except (OSError, ValueError) as erro:
        st.error(f"Erro ao carregar os dados: {erro}")
        return

    if not partidas:
        st.info("Nenhuma partida disponível.")
        return

    primeira_data = min(partida.data for partida in partidas)
    ultima_data = max(partida.data for partida in partidas)

    st.markdown("#### Configuração do ranking")

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        data_referencia = st.date_input(
            "Data de referência",
            value=ultima_data,
            min_value=primeira_data,
            max_value=ultima_data,
            key="elo_data_referencia",
        )

    with col2:
        minimo_jogos = st.number_input(
            "Mínimo de jogos",
            min_value=1,
            max_value=2000,
            value=20,
            step=1,
            key="elo_minimo_jogos",
        )

    with col3:
        somente_ativas = st.toggle(
            "Somente seleções ativas",
            value=True,
            key="elo_somente_ativas",
        )

    janela_atividade = None

    if somente_ativas:
        janela_atividade = st.selectbox(
            "Atividade registrada nos últimos",
            options=[365, 730, 1095],
            index=1,
            format_func=lambda dias: f"{dias} dias",
            key="elo_janela_atividade",
        )

    with st.spinner("Calculando ranking Elo..."):
        ranking = gerar_ranking_elo(
            partidas,
            data_fim=data_referencia,
            minimo_jogos=int(minimo_jogos),
            janela_atividade_dias=janela_atividade,
        )

    if not ranking:
        st.info(
            "Nenhuma seleção atende aos critérios. "
            "Experimente reduzir o mínimo de jogos "
            "ou ampliar a janela de atividade."
        )
        return

    partidas_consideradas = sum(
        partida.data <= data_referencia
        for partida in partidas
    )

    st.markdown("#### Visão geral")

    metrica1, metrica2, metrica3 = st.columns(3)

    metrica1.metric(
        "Partidas consideradas",
        f"{partidas_consideradas:,}".replace(",", "."),
    )

    metrica2.metric(
        "Seleções elegíveis",
        len(ranking),
    )

    metrica3.metric(
        "Maior rating Elo",
        f"{ranking[0].rating:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", "."),
    )

    registros = [
        {
            "Posição": posicao,
            "Seleção": item.selecao,
            "Rating Elo": round(item.rating, 2),
            "Jogos históricos": item.jogos,
        }
        for posicao, item in enumerate(ranking, start=1)
    ]

    tabela = pd.DataFrame(registros)

    st.markdown("#### Classificação Elo")

    st.dataframe(
        tabela,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Rating Elo": st.column_config.NumberColumn(
                "Rating Elo",
                format="%.2f",
            ),
        },
    )

    st.markdown("#### Top 15 seleções")

    top_15 = tabela.head(15)

    grafico = (
        alt.Chart(top_15)
        .mark_bar(
            cornerRadiusEnd=5,
            color="#66E3C9",
        )
        .encode(
            x=alt.X(
                "Rating Elo:Q",
                title="Rating Elo",
                scale=alt.Scale(zero=False),
            ),
            y=alt.Y(
                "Seleção:N",
                sort=top_15["Seleção"].tolist(),
                title=None,
            ),
            tooltip=[
                "Seleção:N",
                alt.Tooltip(
                    "Rating Elo:Q",
                    format=".2f",
                ),
                "Jogos históricos:Q",
            ],
        )
        .properties(height=480)
    )

    st.altair_chart(
        grafico,
        use_container_width=True,
    )


    st.markdown("#### Comparar seleções")

    if len(ranking) >= 2:
        nomes = [item.selecao for item in ranking]

        indice_a = (
            nomes.index("Brazil")
            if "Brazil" in nomes else 0
        )

        indice_b = (
            nomes.index("Argentina")
            if "Argentina" in nomes
            else (1 if indice_a == 0 else 0)
        )

        coluna_a, coluna_b = st.columns(2)

        with coluna_a:
            selecao_a = st.selectbox(
                "Primeira seleção",
                options=nomes,
                index=indice_a,
                key="elo_comparacao_a",
            )

        with coluna_b:
            selecao_b = st.selectbox(
                "Segunda seleção",
                options=nomes,
                index=indice_b,
                key="elo_comparacao_b",
            )

        if selecao_a == selecao_b:
            st.warning(
                "Selecione duas equipes diferentes "
                "para realizar a comparação."
            )
        else:
            posicoes = {
                item.selecao: posicao
                for posicao, item in enumerate(ranking, 1)
            }

            por_selecao = {
                item.selecao: item
                for item in ranking
            }

            dados_a = por_selecao[selecao_a]
            dados_b = por_selecao[selecao_b]

            col1, col2, col3 = st.columns(3)

            col1.metric(
                selecao_a,
                f"{dados_a.rating:.2f}",
                f"{posicoes[selecao_a]}ª posição",
                delta_color="off",
            )

            col2.metric(
                selecao_b,
                f"{dados_b.rating:.2f}",
                f"{posicoes[selecao_b]}ª posição",
                delta_color="off",
            )

            diferenca = abs(
                dados_a.rating - dados_b.rating
            )

            col3.metric(
                "Diferença Elo",
                f"{diferenca:.2f} pontos",
            )

            lider = (
                selecao_a
                if dados_a.rating > dados_b.rating
                else selecao_b
            )

            if diferenca < 0.005:
                st.info(
                    "As duas seleções apresentam "
                    "ratings praticamente iguais."
                )
            else:
                st.info(
                    f"{lider} possui o maior rating "
                    f"na data de referência selecionada."
                )

            st.caption(
                "Comparação de ratings experimentais. "
                "A diferença Elo não representa, "
                "isoladamente, uma probabilidade "
                "calibrada de vitória."
            )
    else:
        st.info(
            "São necessárias pelo menos duas seleções "
            "elegíveis para realizar uma comparação."
        )

    # EVOLUÇÃO HISTÓRICA DO RATING ELO
    st.markdown("#### Evolução histórica Elo")

    st.caption(
        "Acompanhe a evolução dos ratings das seleções "
        "ao longo dos anos. Cada ponto representa o último "
        "rating registrado em partidas daquele ano."
    )

    selecoes_disponiveis = [
        item.selecao for item in ranking
    ]

    selecoes_padrao = [
        nome for nome in ("Brazil", "Argentina")
        if nome in selecoes_disponiveis
    ]

    if not selecoes_padrao:
        selecoes_padrao = selecoes_disponiveis[:2]

    selecoes_evolucao = st.multiselect(
        "Seleções para acompanhar",
        options=selecoes_disponiveis,
        default=selecoes_padrao,
        max_selections=4,
        placeholder="Selecione as seleções",
        key="elo_evolucao_selecoes",
    )

    primeiro_ano = min(
        partida.data.year for partida in partidas
    )
    ultimo_ano = data_referencia.year


    inicio_padrao = min(
        max(2000, primeiro_ano),
        ultimo_ano,
    )

    if primeiro_ano == ultimo_ano:
        periodo_evolucao = (
            primeiro_ano,
            ultimo_ano,
        )

        st.caption(
            f"Período disponível: {primeiro_ano}"
        )
    else:
        periodo_evolucao = st.slider(
            "Período de análise",
            min_value=primeiro_ano,
            max_value=ultimo_ano,
            value=(
                inicio_padrao,
                ultimo_ano,
            ),
            key="elo_evolucao_periodo",
        )


    if not selecoes_evolucao:
        st.info(
            "Selecione pelo menos uma equipe "
            "para visualizar a evolução Elo."
        )
    else:
        data_inicio_evolucao = date(
            periodo_evolucao[0], 1, 1
        )

        data_fim_evolucao = min(
            date(periodo_evolucao[1], 12, 31),
            data_referencia,
        )

        with st.spinner(
            "Calculando evolução histórica Elo..."
        ):
            pontos = calcular_evolucao_elo(
                partidas,
                selecoes=selecoes_evolucao,
                data_inicio=data_inicio_evolucao,
                data_fim=data_fim_evolucao,
            )

        if not pontos:
            st.info(
                "Nenhuma partida das seleções escolhidas "
                "foi encontrada no período."
            )
        else:
            registros_evolucao = [
                {
                    "Ano": ponto.ano,
                    "Seleção": ponto.selecao,
                    "Rating Elo": round(
                        ponto.rating, 2
                    ),
                    "Jogos acumulados": (
                        ponto.jogos_acumulados
                    ),
                    "Última partida": (
                        ponto.data_ultima_partida.isoformat()
                    ),
                }
                for ponto in pontos
            ]

            dados_evolucao = pd.DataFrame(
                registros_evolucao
            )

            grafico_evolucao = (
                alt.Chart(dados_evolucao)
                .mark_line(
                    point=True,
                    strokeWidth=3,
                )
                .encode(
                    x=alt.X(
                        "Ano:Q",
                        title="Ano",
                        axis=alt.Axis(
                            format="d",
                            tickMinStep=1,
                        ),
                        scale=alt.Scale(
                            domain=list(periodo_evolucao)
                        ),
                    ),
                    y=alt.Y(
                        "Rating Elo:Q",
                        title="Rating Elo",
                        scale=alt.Scale(zero=False),
                    ),
                    color=alt.Color(
                        "Seleção:N",
                        title="Seleção",
                        scale=alt.Scale(
                            scheme="tableau10"
                        ),
                    ),
                    tooltip=[
                        "Seleção:N",
                        alt.Tooltip(
                            "Ano:Q",
                            format="d",
                        ),
                        alt.Tooltip(
                            "Rating Elo:Q",
                            format=".2f",
                        ),
                        "Jogos acumulados:Q",
                        "Última partida:N",
                    ],
                )
                .properties(height=430)
                .interactive()
            )

            st.altair_chart(
                grafico_evolucao,
                use_container_width=True,
            )

            st.caption(
                "O histórico anterior ao período escolhido "
                "continua sendo considerado no cálculo. "
                "Anos sem partidas não geram novos pontos; "
                "as linhas conectam as observações existentes. "
                "A escala vertical é ajustada para facilitar "
                "a comparação das variações."
            )


            with st.expander(
                "Consultar os dados da evolução"
            ):
                st.dataframe(
                    dados_evolucao,
                    hide_index=True,
                    use_container_width=True,
                )

    st.divider()

    st.caption(
        f"Data de referência: {data_referencia:%d/%m/%Y}. "
        "Rating inicial: 1500. Fator K: 20. "
        "Sem vantagem de mando ou ponderação por competição. "
        "O Elo utiliza resultados anteriores ou iguais "
        "à data selecionada."
    )

    st.info(
        "Este ranking é experimental e não corresponde "
        "ao ranking oficial da FIFA. A base inclui equipes "
        "históricas, territoriais e regionais. "
        "O filtro de atividade identifica partidas recentes "
        "registradas na base, não reconhecimento oficial. "
        "A precisão preditiva ainda não foi validada."
    )
