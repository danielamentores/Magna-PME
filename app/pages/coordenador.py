"""Pagina do coordenador."""
import streamlit as st


def render(user: dict):
    st.header(f"Bem-vindo, {user['nome']}")
    st.caption("Perfil: Coordenador")
    tab1, tab2 = st.tabs(["📊 As minhas acoes", "📋 Por fechar"])
    with tab1:
        st.info("🚧 Em construcao — vai mostrar todas as acoes em que es coordenador.")
    with tab2:
        st.info("🚧 Em construcao — acoes que terminaram mas ainda nao foram fechadas.")
