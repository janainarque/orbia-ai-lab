"""Orbia AI Lab — MVP independente de retrospectiva (sem LLM nem pipeline original)."""
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from src.retrospectiva import carregar_ranking, resumo

BASE = Path(__file__).resolve().parent
RANKING = carregar_ranking(BASE / "data" / "ranking_observado_video.csv")
DADOS = resumo(RANKING, "Espanha")

st.set_page_config(page_title="Orbia AI Lab · Copa 2026", page_icon="⚽", layout="wide")
st.markdown("""
<style>
.stApp {background: #0b111a; color: #e9edf5;}
.block-container {max-width: 1120px; padding-top: 2.2rem;}
.hero {border:1px solid #27364a; border-radius:22px; padding:30px 34px; background:linear-gradient(110deg,#101d2a,#17152b); margin-bottom:24px;}
.eyebrow {color:#6ee7cf;letter-spacing:.16em;font-size:.75rem;font-weight:700;}
.hero h1 {color:#f4f7fb;font-size:3rem;margin:.35rem 0;}
.hero p {color:#b6c3d5;max-width:660px;}
.tag {display:inline-block;background:#1b3441;color:#8fe5d8;padding:5px 12px;border-radius:20px;font-size:.75rem;}
.note {border-left:3px solid #7d75ee;background:#151c2a;padding:13px 17px;border-radius:5px;color:#cbd5e1;}


</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>
/* Estrutura */
[data-testid="stAppViewContainer"] {
    background: #0b111a;
}

[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
}

/* Navegação lateral */
[data-testid="stSidebar"] {
    background: #101a29;
    border-right: 1px solid #29374b;
}

[data-testid="stSidebar"] [data-baseweb="tag"] {
    background: #205348 !important;
    border-radius: 7px;
}

[data-testid="stSidebar"] [data-baseweb="tag"] span {
    color: #c2f8e9 !important;
}

/* Indicadores */
[data-testid="stMetric"] {
    background: linear-gradient(
        145deg, #172438, #111b2a
    );
    border: 1px solid #2c3b51;
    border-radius: 16px;
    padding: 22px;
    min-height: 135px;
}

[data-testid="stMetricLabel"] p {
    color: #9cacc2 !important;
    font-size: 13px;
}

[data-testid="stMetricValue"] {
    color: #f0f5ff !important;
    font-weight: 750;
    letter-spacing: -0.04em;
}

/* Abas */
[data-baseweb="tab"] {
    color: #9aacc3 !important;
    font-weight: 600;
}

[data-baseweb="tab"][aria-selected="true"] {
    color: #66e3c9 !important;
}

[data-baseweb="tab-highlight"] {
    background: #66e3c9 !important;
}

/* Gráficos e contêineres */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: #29374b;
}

h2, h3 {
    letter-spacing: -0.035em;
}


/* ORBIA V3 — Identidade visual */

.block-container {
    max-width: 1180px;
    padding-top: 1.4rem;
    padding-bottom: 3rem;
}

/* Identidade */
.orbia-topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 22px;
}

.orbia-brand {
    display: flex;
    align-items: center;
    gap: 12px;
}

.orbia-brand-icon {
    width: 42px;
    height: 42px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    background: #193a3b;
    color: #69e5d0;
    font-size: 25px;
}

.orbia-brand-name {
    color: #f5f7fc;
    font-size: 16px;
    font-weight: 800;
    letter-spacing: .12em;
}

.orbia-brand-subtitle {
    color: #8394ac;
    font-size: 10px;
    letter-spacing: .16em;
}

.orbia-status {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #a5b8c9;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: .08em;
}

.orbia-status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #69e5d0;
    box-shadow: 0 0 12px #69e5d055;
}

/* Hero */
.hero {
    background:
        radial-gradient(
            circle at 92% 10%,
            #49316c44,
            transparent 42%
        ),
        linear-gradient(120deg, #142232, #171829);
    border: 1px solid #29364a;
    border-radius: 20px;
    padding: 30px 34px;
    margin-bottom: 18px;
}

.hero h1 {
    font-size: clamp(2rem, 3.2vw, 2.9rem);
    line-height: 1.12;
    letter-spacing: -.045em;
    max-width: 750px;
    margin: 12px 0;
}

.hero h1 span {
    color: #69e5d0;
}

.hero p {
    font-size: 14px;
    line-height: 1.7;
    max-width: 630px;
    margin-bottom: 18px;
}

.hero-footer {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
}

.hero-meta {
    color: #91a2b8;
    font-size: 11px;
}

/* Cards de indicadores */
[data-testid="stMetric"] {
    position: relative;
    background: linear-gradient(145deg, #192538, #121d2c);
    border: 1px solid #2a3a50;
    border-radius: 16px;
    padding: 20px 22px;
    min-height: 124px;
    overflow: hidden;
}

[data-testid="stMetric"]::before {
    content: "";
    position: absolute;
    left: 22px;
    bottom: 0;
    width: 42px;
    height: 3px;
    border-radius: 4px;
    background: #69e5d0;
}

[data-testid="stMetricValue"] {
    color: #f2f6ff !important;
    font-size: clamp(1.55rem, 2.3vw, 2.1rem);
}

@media (max-width: 700px) {
    .hero {
        padding: 22px;
    }

    .orbia-status {
        font-size: 9px;
    }

    .hero-footer {
        gap: 10px;
    }
}

</style>
""", unsafe_allow_html=True)



st.html("""
<div class="orbia-topbar">
    <div class="orbia-brand">
        <div class="orbia-brand-icon">◈</div>
        <div>
            <div class="orbia-brand-name">ORBIA</div>
            <div class="orbia-brand-subtitle">INTELLIGENCE LAB</div>
        </div>
    </div>
    <div class="orbia-status">
        <span class="orbia-status-dot"></span>
        ESTUDO DE CASO
    </div>
</div>

<div class="hero">
    <div class="eyebrow">
        WORLD CUP 2026 / ANALYTICS
    </div>

    <h1>
        Probabilidades sob uma
        <span>nova perspectiva.</span>
    </h1>

    <p>
        Explore o ranking observado, compare seleções
        e entenda o contexto por trás das previsões
        apresentadas na demonstração.
    </p>

    <div class="hero-footer">
        <span class="tag">MVP 01</span>
        <span class="hero-meta">Dados parciais observados</span>
        <span class="hero-meta">Sem retreinamento</span>
    </div>
</div>
""")


# Filtros do Intelligence Dashboard
st.sidebar.title("⚽ Orbia Intelligence")
st.sidebar.caption("Exploração do ranking observado")

selecoes = [item.selecao for item in RANKING]

selecoes_filtradas = st.sidebar.multiselect(
    "Seleções para comparar",
    options=selecoes,
    default=selecoes,
)

ranking_filtrado = [
    item for item in RANKING
    if item.selecao in selecoes_filtradas
]

aba1, aba2, aba3 = st.tabs(["Visão geral", "Metodologia", "Origem e créditos"])

with aba1:
    st.markdown("#### Panorama do recorte")

    st.caption(
        f"{len(ranking_filtrado)} de {len(RANKING)} seleções "
        "incluídas na comparação"
    )

    c1, c2, c3 = st.columns(3)

    if ranking_filtrado:
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

    else:
        c1.metric("Maior probabilidade no filtro", "—")
        c2.metric("Probabilidade atribuída", "—")
        c3.metric("Diferença entre as líderes", "—")

    st.subheader("Probabilidades exibidas na gravação")


    if ranking_filtrado:
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

    else:
        st.info(
            "Selecione pelo menos uma seleção para visualizar o gráfico."
        )

    st.markdown(
        """
        <div class="note">
            O carrossel enviado informa a <strong>Espanha</strong>
            como campeã. Ela também era a favorita do recorte exibido
            no vídeo, com <strong>16,9%</strong> — o que não significa
            que o título fosse certo. As quatro seleções exibidas
            somam 47,7%; os outros 52,3% não aparecem neste recorte.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        "Fonte dos percentuais: observação da gravação enviada pela "
        "participante. Ainda não é um snapshot completo exportado do modelo."
    )
with aba2:
    st.subheader("O que esta versão faz")
    st.write("Lê um ranking parcial, valida percentuais, identifica a seleção líder e compara com o campeão informado no material fornecido.")
    st.subheader("O que esta versão não faz")
    st.write("Não executa simulações Monte Carlo, não treina modelos, não calcula probabilidades novas e não utiliza agentes ou LLMs.")
    st.info("Para métricas como Brier multiclasse ou calibração, precisamos de um snapshot completo, datado e verificável das probabilidades pré-torneio.")
with aba3:
    st.subheader("Transparência de autoria")
    st.write("Este MVP é uma implementação independente de retrospectiva, criada como evolução de estudo de caso. O IAPredict original foi desenvolvido por Marcos Vinicius da Silva e utilizado como referência em um bootcamp.")
    st.markdown("[Repositório original](https://github.com/marcovsilva/iapredict-copa2026)")
    st.write("Nenhum código do pipeline original foi incluído neste MVP. A reutilização do projeto-base depende da verificação de permissões.")
