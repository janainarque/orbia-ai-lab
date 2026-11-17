"""Dashboard de estatísticas históricas do Orbia Intelligence."""

from datetime import date
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from src.dados_futebol import carregar_partidas
from src.estatisticas_futebol import calcular_estatisticas_selecao
from src.ranking_futebol import gerar_ranking_selecoes


BASE = Path(__file__).resolve().parents[1]
ARQUIVO_PARTIDAS = BASE / "data" / "processed" / "partidas_orbia.csv"


@st.cache_data(show_spinner=False)
def obter_partidas(caminho: str):
    """Carrega e mantém em cache a base histórica validada."""
    return carregar_partidas(caminho)


def formatar_percentual(valor: float) -> str:
    return f"{valor:.2f}%".replace(".", ",")


def render_historical_dashboard() -> None:
    """Renderiza o painel histórico de seleções."""

    st.subheader("Análise histórica de seleções")

    st.caption(
        "Resultados internacionais registrados na base histórica "
        "do Orbia. Indicadores descritivos, não previsões."
    )

    if not ARQUIVO_PARTIDAS.is_file():
        st.warning(
            "A base histórica ainda não foi reconstruída "
            "neste ambiente."
        )
        st.code(
            "python -m scripts.reconstruir_base_futebol",
            language="powershell",
        )
        return

    try:
        partidas = obter_partidas(str(ARQUIVO_PARTIDAS))
    except (OSError, ValueError) as erro:
        st.error(f"Não foi possível carregar a base: {erro}")
        return

    if not partidas:
        st.info("A base histórica não contém partidas.")
        return

    menor_ano = min(partida.data.year for partida in partidas)
    maior_ano = max(partida.data.year for partida in partidas)

    competicoes = sorted({
        partida.competicao
        for partida in partidas
    })

    st.markdown("#### Filtros da análise")

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        periodo = st.slider(
            "Período",
            min_value=menor_ano,
            max_value=maior_ano,
            value=(max(2020, menor_ano), maior_ano),
            key="historico_periodo",
        )

    with col2:
        competicao_selecionada = st.selectbox(
            "Competição",
            options=["Todas as competições", *competicoes],
            key="historico_competicao",
        )

    with col3:
        minimo_jogos = st.number_input(
            "Mínimo de jogos",
            min_value=1,
            max_value=1000,
            value=20,
            step=1,
            key="historico_minimo_jogos",
        )

    data_inicio = date(periodo[0], 1, 1)
    data_fim = date(periodo[1], 12, 31)

    competicao = (
        None
        if competicao_selecionada == "Todas as competições"
        else competicao_selecionada
    )

    ranking = gerar_ranking_selecoes(
        partidas,
        data_inicio=data_inicio,
        data_fim=data_fim,
        competicao=competicao,
        minimo_jogos=int(minimo_jogos),
    )

    if not ranking:
        st.info(
            "Nenhuma seleção atende aos filtros. "
            "Experimente reduzir o mínimo de jogos "
            "ou ampliar o período."
        )
        return

    st.markdown("#### Visão geral")

    total_partidas = sum(
        1
        for partida in partidas
        if data_inicio <= partida.data <= data_fim
        and (
            competicao is None
            or partida.competicao.casefold()
            == competicao.casefold()
        )
    )

    metrica1, metrica2, metrica3 = st.columns(3)

    metrica1.metric(
        "Partidas no período",
        f"{total_partidas:,}".replace(",", "."),
    )
    metrica2.metric("Seleções elegíveis", len(ranking))
    metrica3.metric(
        "Maior aproveitamento",
        formatar_percentual(ranking[0].aproveitamento),
    )

    registros = []

    for posicao, item in enumerate(ranking, start=1):
        registros.append({
            "Posição": posicao,
            "Seleção": item.selecao,
            "Jogos": item.jogos,
            "Vitórias": item.vitorias,
            "Empates": item.empates,
            "Derrotas": item.derrotas,
            "Gols pró": item.gols_marcados,
            "Gols contra": item.gols_sofridos,
            "Saldo": item.saldo_gols,
            "Aproveitamento (%)": round(
                item.aproveitamento, 2
            ),
        })

    tabela = pd.DataFrame(registros)

    st.markdown("#### Ranking por aproveitamento")

    st.dataframe(
        tabela,
        hide_index=True,
        use_container_width=True,
    )

    st.caption(
        "Ordenação por aproveitamento, jogos, saldo de gols "
        "e gols marcados. O mínimo de jogos reduz distorções "
        "por amostras pequenas, mas não elimina diferenças "
        "na força dos adversários."
    )

    st.markdown("#### As 15 primeiras seleções")

    grafico = (
        alt.Chart(tabela.head(15))
        .mark_bar(cornerRadiusEnd=4)
        .encode(
            x=alt.X(
                "Aproveitamento (%):Q",
                title="Aproveitamento (%)",
                scale=alt.Scale(domain=[0, 100]),
            ),
            y=alt.Y(
                "Seleção:N",
                sort="-x",
                title=None,
            ),
            tooltip=[
                "Seleção:N",
                "Jogos:Q",
                alt.Tooltip(
                    "Aproveitamento (%):Q",
                    format=".2f",
                ),
            ],
        )
        .properties(height=450)
    )

    st.altair_chart(
        grafico,
        use_container_width=True,
    )

    st.markdown("#### Análise individual")

    selecao = st.selectbox(
        "Escolha uma seleção",
        options=[item.selecao for item in ranking],
        key="historico_selecao",
    )

    dados = calcular_estatisticas_selecao(
        partidas,
        selecao,
        data_inicio=data_inicio,
        data_fim=data_fim,
        competicao=competicao,
    )

    col_a, col_b, col_c, col_d = st.columns(4)

    col_a.metric("Jogos", dados.jogos)
    col_b.metric("Vitórias", dados.vitorias)
    col_c.metric("Empates", dados.empates)
    col_d.metric("Derrotas", dados.derrotas)

    col_e, col_f, col_g, col_h = st.columns(4)

    col_e.metric("Gols marcados", dados.gols_marcados)
    col_f.metric("Gols sofridos", dados.gols_sofridos)
    col_g.metric("Saldo de gols", f"{dados.saldo_gols:+d}")
    col_h.metric(
        "Aproveitamento",
        formatar_percentual(dados.aproveitamento),
    )

    st.divider()

    st.caption(
        "Fonte: martj42/international_results (CC0 1.0), "
        "snapshot versionado e auditado pelo Orbia. "
        "Os resultados podem incluir prorrogação, "
        "mas não disputas por pênaltis. "
        "Este ranking não é o ranking oficial da FIFA "
        "nem mede diretamente a força das seleções."
    )

    st.markdown(
        "[Consultar documentação e proveniência dos dados]"
        "(https://github.com/martj42/international_results)"
    )
