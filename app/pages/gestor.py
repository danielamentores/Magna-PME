"""Pagina do gestor de projeto."""
import streamlit as st
from app import db_coordenador as db


def render(user: dict):
    st.header(f"Bem-vinda, {user['nome']}")
    st.caption("Perfil: Gestor de Projeto")
    tab1, tab2, tab3 = st.tabs(["📊 Controlo de Execução", "✅ Confirmar faturacao", "💼 Reembolsos"])
    with tab1:
        st.info("🚧 Em construcao — dashboard com todas as acoes.")
    with tab2:
        _render_confirmacao_faturacao()
    with tab3:
        st.info("🚧 Em construcao — selecionar acoes para reembolso.")


def _render_confirmacao_faturacao():
    st.subheader("Faturação — confirmar ações da coordenadora")
    pendentes = db.acoes_em("Em confirmação")
    if not pendentes:
        st.info("Sem ações a aguardar confirmação.")
        return
    st.caption("Confirma ou devolve cada ação (prazo: 15 dias).")
    for a in pendentes:
        with st.container(border=True):
            st.write(f"**{a['acao']}** — {a['empresa']} — {db.eur(a['valor'])}")
            c1, c2 = st.columns(2)
            if c1.button("✅ Confirmar", key=f"gest_ok_{a['id']}"):
                db.definir_estado(a["id"], "Aceite")
                st.rerun()
            if c2.button("↩️ Devolver", key=f"gest_dev_{a['id']}"):
                db.definir_estado(a["id"], "Devolvida")
                st.rerun()
