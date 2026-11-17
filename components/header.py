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
