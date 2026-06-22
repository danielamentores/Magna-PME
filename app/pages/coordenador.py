"""Pagina do coordenador."""
import streamlit as st

_CSS = """
<style>
.c-kpi-row{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0 20px}
.c-kpi{background:#fff;border:1px solid #E4E7EF;border-radius:12px;padding:16px 18px;flex:1;min-width:120px}
.c-kpi.a{border-top:3px solid #D97706}.c-kpi.b{border-top:3px solid #2563EB}
.c-kpi.g{border-top:3px solid #16A34A}.c-kpi.r{border-top:3px solid #DC2626}
.c-kpi.p{border-top:3px solid #7C3AED}
.c-kpi .lbl{font-size:11px;font-weight:600;color:#8B94A3;text-transform:uppercase;letter-spacing:.06em;margin:0 0 5px}
.c-kpi .val{font-size:22px;font-weight:700;color:#1A1F2E;margin:0;line-height:1.1}
.c-kpi .sub{font-size:12px;color:#8B94A3;margin:3px 0 0}
.c-card{background:#fff;border:1px solid #E4E7EF;border-radius:10px;padding:14px 16px;margin-bottom:8px}
.c-badge{display:inline-block;font-size:11px;font-weight:600;padding:2px 8px;border-radius:20px;white-space:nowrap}
.c-ptag{display:inline-block;font-size:11px;font-weight:700;padding:2px 8px;border-radius:4px}
.c-sec{font-size:13px;font-weight:700;color:#4B5263;text-transform:uppercase;letter-spacing:.06em;margin:0 0 3px}
.c-secs{font-size:12px;color:#8B94A3;margin:0 0 14px}
.c-div{height:1px;background:#E4E7EF;margin:20px 0 18px}
.c-empty{background:#F7F8FC;border:1px dashed #E4E7EF;border-radius:10px;padding:20px;text-align:center;color:#8B94A3;font-size:13px}
</style>
"""

def render(user: dict):
    st.html(_CSS)
    st.header(f"Bem-vindo, {user['nome']}")
    st.caption("Perfil: Coordenador")

    tab1, tab2, tab3 = st.tabs([
        "📊 Projetos Clusters",
        "📋 Projeto Formação Ação",
        "🏪 Projeto Comércio e Serviços",
    ])
    with tab1:
        from app.pages.clusters import render as r; r()
    with tab2:
        from app.pages.formacao import render as r; r()
    with tab3:
        from app.pages.comercio import render as r; r()
# --- Reembolsos (estado partilhado gestora ↔ coordenadora) ---
_CHAVE_RC = "reembolso_candidatos"
_CHAVE_RP = "reembolso_problemas"


def reembolso_candidatos() -> dict:
    return st.session_state.setdefault(_CHAVE_RC, {})


def reembolso_problemas() -> dict:
    return st.session_state.setdefault(_CHAVE_RP, {})


def marcar_problema_reembolso(key: str, motivo: str):
    reembolso_problemas()[key] = motivo
