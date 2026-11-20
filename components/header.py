"""Cabeçalho visual do Orbia Intelligence."""

import streamlit as st


def render_header() -> None:
    """Renderiza a identidade e a apresentação do dashboard."""

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
            PROJETO EXPERIMENTAL
        </div>
    </div>

    <div class="hero">
        <div class="eyebrow">
            FOOTBALL DATA / ANALYTICS LAB
        </div>

        <h1>
            Do histórico à
            <span>inteligência de jogo.</span>
        </h1>

        <p>
            Explore dados históricos de seleções,
            analise rankings Elo e compare modelos
            preditivos com validação temporal,
            métricas de desempenho e calibração.
        </p>


        <div class="hero-footer">
            <span class="tag">V9</span>
            <span class="hero-meta">
                49.938 partidas auditadas
            </span>
            <span class="hero-meta">
                Elo Rating Engine
            </span>
            <span class="hero-meta">
                Validação preditiva
            </span>
        </div>

    </div>
    """)
