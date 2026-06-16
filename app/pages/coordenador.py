"""Pagina do coordenador."""
import streamlit as st


def render(user: dict):
    st.header(f"Bem-vindo, {user['nome']}")
    st.caption("Perfil: Coordenador")
    tab1, tab2, tab3 = st.tabs(["📊 Projetos Clusters", "Projeto Formação Ação", "Projeto Comércio e Serviços"])
    with tab1:
        st.info("Execução")
        st.info("Formadores")
        st.info("Empresas")
        st.info("Faturação")
    with tab2:
        st.info("Execução")
        st.info("Formadores")
        st.info("Empresas")
        st.info("Faturação")
    with tab3:
        st.info("Execução")
        st.info("Formadores")
        st.info("Empresas")
        st.info("Faturação")
