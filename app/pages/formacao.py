"""Tab Projeto Formação Ação."""
import streamlit as st

PROJETOS = []  # preencher depois


def render():
    with st.expander("Execução", expanded=True):
        if PROJETOS:
            st.selectbox("Seleciona o projeto", PROJETOS, key="exec_projeto_formacao")
        else:
            st.caption("Sem projetos definidos.")

    st.info("Formadores")
    st.info("Empresas")
    st.info("Faturação")
