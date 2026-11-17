"""Orbia AI Lab — MVP independente de retrospectiva (sem LLM nem pipeline original)."""
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from src.retrospectiva import carregar_ranking, resumo
from components.header import render_header
from components.metrics import render_metrics
from components.charts import render_probability_chart

BASE = Path(__file__).resolve().parent
RANKING = carregar_ranking(BASE / "data" / "ranking_observado_video.csv")
DADOS = resumo(RANKING, "Espanha")

st.set_page_config(page_title="Orbia AI Lab · Copa 2026", page_icon="⚽", layout="wide")
st.html(
    "<style>"
    + (BASE / "assets" / "styles.css").read_text(encoding="utf-8")
    + "</style>"
)



render_header()


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
    render_metrics(ranking_filtrado, len(RANKING))

    render_probability_chart(ranking_filtrado)

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
