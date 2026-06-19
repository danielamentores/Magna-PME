"""Página do financeiro — entrypoint."""
from __future__ import annotations
import streamlit as st
from app.financeiro.helpers import CSS

try:
    from app.db_financeiro import get_faturas_pre_aprovacao, get_supabase
    get_supabase()
    SUPABASE_OK = True
except Exception:
    SUPABASE_OK = False

def _init_state():
    if "historico"       not in st.session_state: st.session_state.historico = []
    if "notificacoes"    not in st.session_state:
        from app.financeiro.notificacoes import _MOCK_NOTIFS
        st.session_state.notificacoes = list(_MOCK_NOTIFS)
    if "comprovativos"   not in st.session_state: st.session_state.comprovativos = {}
    if not SUPABASE_OK:
        from app.financeiro.faturas import _MOCK_PRE, _MOCK_VENC, _MOCK_AV
        if "mock_pre"  not in st.session_state: st.session_state.mock_pre  = list(_MOCK_PRE)
        if "mock_venc" not in st.session_state: st.session_state.mock_venc = list(_MOCK_VENC)
        if "mock_av"   not in st.session_state: st.session_state.mock_av   = list(_MOCK_AV)

def render(user: dict):
    _init_state()
    st.html(CSS)

    # Contadores para labels das tabs
    n_pre = len(st.session_state.mock_pre) if not SUPABASE_OK else (
        len(get_faturas_pre_aprovacao()) if SUPABASE_OK else 0)
    n_novas = len([n for n in st.session_state.notificacoes if not n.get("lida")])

    try:
        from app.financeiro.consultores import _get_faturas_consultores_pendentes
        n_fc = len(_get_faturas_consultores_pendentes())
    except: n_fc = 0

    # Badge de notificações no título
    badge = (f' <span style="display:inline-flex;align-items:center;justify-content:center;'
             f'background:#DC2626;color:#fff;font-size:11px;font-weight:700;border-radius:10px;'
             f'padding:2px 7px;vertical-align:middle">{n_novas}</span>') if n_novas > 0 else ""
    st.markdown(f"# Bem-vindo, {user['nome']}{badge}", unsafe_allow_html=True)
    st.caption("Perfil: Financeiro")

    label_fat   = f"🧾 Faturas ({n_pre})"       if n_pre   > 0 else "🧾 Faturas"
    label_cons  = f"🤝 Consultores ({n_fc})"     if n_fc    > 0 else "🤝 Consultores"
    label_notif = f"🔔 Notificações ({n_novas})" if n_novas > 0 else "🔔 Notificações"

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard",
        label_fat,
        label_cons,
        "🏢 Faturação Empresas",
        label_notif,
    ])

    with tab1:
        from app.financeiro.dashboard import render_dashboard
        render_dashboard(user)

    with tab2:
        from app.financeiro.faturas import render_alertas
        render_alertas(user)

    with tab3:
        from app.financeiro.consultores import render_consultores_financeiro
        render_consultores_financeiro(user)

    with tab4:
        from app.financeiro.faturacao_empresas import render_faturacao_empresas
        render_faturacao_empresas(user)

    with tab5:
        from app.financeiro.notificacoes import render_notificacoes
        render_notificacoes()
