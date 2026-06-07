"""Pagina do gestor de projeto."""
import streamlit as st


def render(user: dict):
    st.header(f"Bem-vinda, {user['nome']}")
    st.caption("Perfil: Gestor de Projeto")
    tab1, tab2, tab3 = st.tabs(["📊 Visao geral", "✅ Confirmar faturacao", "💼 Reembolsos"])
    with tab1:
        st.info("🚧 Em construcao — dashboard com todas as acoes.")
    with tab2:
        st.info("🚧 Em construcao — confirmar acoes para faturar.")
    with tab3:
        st.info("🚧 Em construcao — selecionar acoes para reembolso.")
