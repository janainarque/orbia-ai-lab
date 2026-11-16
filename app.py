"""Orbia AI Lab — MVP independente de retrospectiva (sem LLM nem pipeline original)."""
from pathlib import Path

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
<div class="hero">
  <div class="eyebrow">ORBiA AI LAB / ESTUDO DE CASO</div>
  <h1>Previsão <span style="color:#6ee7cf">vs. realidade.</span></h1>
  <p>Uma leitura retrospectiva das probabilidades mostradas em uma demonstração do IAPredict para a Copa do Mundo de 2026.</p>
  <span class="tag">MVP 01 · Ranking observado · Sem retreinamento</span>
</div>
""", unsafe_allow_html=True)

aba1, aba2, aba3 = st.tabs(["Visão geral", "Metodologia", "Origem e créditos"])
with aba1:
    c1, c2, c3 = st.columns(3)
    c1.metric("Favorita no vídeo", DADOS["favorito"])
    c2.metric("Probabilidade atribuída", f'{DADOS["probabilidade_favorito"]:.1f}%'.replace(".", ","))
    c3.metric("Margem sobre a 2ª", f'{DADOS["margem_primeiro_segundo_pp"]:.1f} p.p.'.replace(".", ","))
    st.subheader("Probabilidades exibidas na gravação")
    st.bar_chart(
        [{"Seleção": item.selecao, "Probabilidade (%)": item.percentual} for item in RANKING],
        x="Seleção",
        y="Probabilidade (%)",
        horizontal=True,
        color="#64dcc7",
    )
    st.markdown(f"""<div class="note">O carrossel enviado informa a <strong>Espanha</strong> como campeã. Ela também era a favorita do recorte exibido no vídeo, com <strong>16,9%</strong> — o que não significa que o título fosse certo. As quatro seleções exibidas somam 47,7%; os outros 52,3% não aparecem neste recorte.</div>""", unsafe_allow_html=True)
    st.caption("Fonte dos percentuais: observação da gravação enviada pela participante. Ainda não é um snapshot completo exportado do modelo.")
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
