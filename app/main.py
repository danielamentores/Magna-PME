"""Gestform - entrypoint da app Streamlit."""
from __future__ import annotations

import streamlit as st

from core.config import get_settings

st.set_page_config(
    page_title="Gestform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    settings = get_settings()

    st.title("🎓 Gestform")
    st.caption("Agente de IA para gestao administrativa e financeira de formacao")

    if "user" not in st.session_state:
        st.session_state.user = None

    if st.session_state.user is None:
        _login_simulado()
        return

    user = st.session_state.user
    st.sidebar.success(f"Sessao: {user['nome']}")
    st.sidebar.caption(f"Perfil: {user['role']}")

    if st.sidebar.button("Sair"):
        st.session_state.user = None
        st.rerun()

    role = user["role"]
    if role == "formador":
        from app.pages.formador import render
        render(user)
    elif role == "coordenador":
        from app.pages.coordenador import render
        render(user)
    elif role == "gestor_projeto":
        from app.pages.gestor import render
        render(user)
    elif role in ("financeiro", "admin"):
        from app.pages.financeiro import render
        render(user)
    else:
        st.error(f"Perfil desconhecido: {role}")


def _login_simulado():
    st.info("🚧 Login simulado para desenvolvimento. OAuth Google sera adicionado a seguir.")

    perfis_demo = {
        "Maria Formadora": {"nome": "Maria Formadora", "email": "maria@demo.pt", "role": "formador"},
        "Joao Coordenador": {"nome": "Joao Coordenador", "email": "joao@demo.pt", "role": "coordenador"},
        "Ana Gestora": {"nome": "Ana Gestora", "email": "ana@demo.pt", "role": "gestor_projeto"},
        "Carlos Financeiro": {"nome": "Carlos Financeiro", "email": "carlos@demo.pt", "role": "financeiro"},
    }

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("### Escolhe um perfil de teste")
        for nome, dados in perfis_demo.items():
            if st.button(nome, use_container_width=True):
                st.session_state.user = dados
                st.rerun()

    with col2:
        st.markdown("### Sobre")
        st.markdown(
            """
            **Gestform** — versao inicial.

            **Funcionalidades nesta etapa:**
            - Estrutura de paginas por perfil
            - Leitura de faturas com Gemini
            - Adaptador Magna (modo Excel)

            **A seguir:**
            - Integracao Supabase
            - Login OAuth Google
            - Envio de emails via Gmail API
            - Sincronizacao automatica com a Magna
            """
        )


if __name__ == "__main__":
    main()
