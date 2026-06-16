"""Pagina do financeiro."""
import streamlit as st


def render(user: dict):
    st.header(f"Bem-vindo, {user['nome']}")
    st.caption("Perfil: Financeiro")
    tab1, tab2, tab3 = st.tabs(["💶 Dashboard Financeiro", "⚠️ Alertas/A Pagar", "💳 Faturação Empresas"])
    with tab1:
        st.info("🚧 Em construcao — faturas aprovadas a aguardar pagamento.")
    with tab2:
        st.info("🚧 Em construcao — leituras de fatura que falharam.")
    with tab3:
        st.info("🚧 Em construcao — historico de pagamentos.")
