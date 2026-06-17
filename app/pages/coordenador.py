"""Pagina do coordenador."""
import streamlit as st

from design_coordenador import clusters, formacao, comercio


def render(user: dict):
    st.header(f"Bem-vindo, {user['nome']}")
    st.caption("Perfil: Coordenador")

    tab1, tab2, tab3 = st.tabs([
        "📊 Projetos Clusters",
        "Projeto Formação Ação",
        "Projeto Comércio e Serviços",
    ])

    with tab1:
        clusters.render()
    with tab2:
        formacao.render()
    with tab3:
        comercio.render()
