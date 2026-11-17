"""Orbia AI Lab — MVP independente de retrospectiva (sem LLM nem pipeline original)."""
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from src.retrospectiva import carregar_ranking, resumo
from components.header import render_header
from components.metrics import render_metrics
from components.charts import render_probability_chart
from components.statistics import render_statistical_summary
from components.simulator import render_simulator

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

aba1, aba2, aba3, aba4 = st.tabs(
    [
        "Visão geral",
        "Metodologia",
        "Origem e créditos",
        "Simulador Monte Carlo",
    ]
)

with aba1:
    render_metrics(ranking_filtrado, len(RANKING))
    render_probability_chart(ranking_filtrado)
    render_statistical_summary(RANKING)

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
    st.write(
        "O Orbia Intelligence analisa um ranking parcial "
        "observado em uma demonstração. Valida os dados, "
        "identifica a seleção líder e apresenta comparações "
        "e estatísticas descritivas."
    )

    st.subheader("Como os indicadores são calculados")

    st.markdown(
        """
        - **Percentual observado:** soma dos percentuais
          das seleções disponíveis (47,7%).
        - **Complemento até 100%:** diferença entre 100%
          e a soma observada (52,3%). Não identifica
          individualmente os resultados ausentes.
        - **Soma das duas líderes:** soma dos dois maiores
          percentuais observados (33,3%).
        - **Diferença entre líderes:** subtração entre
          os dois maiores percentuais (0,5 p.p.).
        - **Amplitude:** diferença entre o maior e o menor
          percentual observado (10,5 p.p.).
        """
    )

    st.subheader("Validação dos dados")
    st.write(
        "O motor estatístico rejeita rankings vazios, "
        "seleções duplicadas, percentuais inválidos, "
        "valores negativos, valores acima de 100% e "
        "somas superiores a 100%."
    )

    st.subheader("O que esta versão não faz")
    st.write(
        "Não executa simulações Monte Carlo, não treina "
        "modelos preditivos, não calcula novas probabilidades "
        "e não utiliza agentes ou LLMs."
    )

    st.info(
        "Para avaliar calibração ou métricas como o Brier "
        "multiclasse, precisamos de um conjunto completo, "
        "datado e verificável de probabilidades anteriores "
        "aos resultados avaliados."
    )
with aba3:
    st.subheader("Transparência de autoria")
    st.write("Este MVP é uma implementação independente de retrospectiva, criada como evolução de estudo de caso. O IAPredict original foi desenvolvido por Marcos Vinicius da Silva e utilizado como referência em um bootcamp.")
    st.markdown("[Repositório original](https://github.com/marcovsilva/iapredict-copa2026)")
    st.write("Nenhum código do pipeline original foi incluído neste MVP. A reutilização do projeto-base depende da verificação de permissões.")
with aba4:
    render_simulator()