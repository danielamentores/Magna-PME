"""Magna PME - entrypoint da app Streamlit."""
from __future__ import annotations
import streamlit as st
from core.config import get_settings

st.set_page_config(
    page_title="Magna PME",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# CSS GLOBAL — aplica-se a TODAS as páginas
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* ── Importar fonte profissional ────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Variáveis de cor Mentores & Tutores ────────────────── */
:root {
  --mt-dark:    #1B3A4B;
  --mt-teal:    #2A7A8C;
  --mt-teal-l:  #3A9AAC;
  --mt-teal-bg: #EBF5F7;
  --mt-bg:      #F4F7F9;
  --mt-white:   #FFFFFF;
  --mt-border:  #DDE4EA;
  --mt-text:    #1B3A4B;
  --mt-muted:   #6B8090;
  --mt-success: #16A34A;
  --mt-warn:    #D97706;
  --mt-error:   #DC2626;
}

/* ── Fonte base ──────────────────────────────────────────── */
html, body, [class*="css"], .stApp {
  font-family: 'Inter', sans-serif !important;
  color: var(--mt-text) !important;
}

/* ── Fundo geral ─────────────────────────────────────────── */
.stApp { background-color: var(--mt-bg) !important; }
.stApp > header { background-color: var(--mt-white) !important; border-bottom: 1px solid var(--mt-border); }

/* ── Sidebar ─────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background-color: var(--mt-dark) !important;
  border-right: none !important;
}
[data-testid="stSidebar"] * { color: #FFFFFF !important; }
[data-testid="stSidebar"] .stButton button {
  background: rgba(255,255,255,0.1) !important;
  color: #fff !important;
  border: 1px solid rgba(255,255,255,0.2) !important;
  border-radius: 8px !important;
  font-weight: 500 !important;
}
[data-testid="stSidebar"] .stButton button:hover {
  background: rgba(255,255,255,0.2) !important;
}
[data-testid="stSidebar"] .stSuccess {
  background: rgba(42,122,140,0.3) !important;
  color: #fff !important;
  border: 1px solid rgba(42,122,140,0.5) !important;
  border-radius: 8px !important;
}

/* ── Área principal ──────────────────────────────────────── */
.main .block-container {
  padding: 2rem 2.5rem 2rem 2.5rem !important;
  max-width: 100% !important;
}

/* ── Títulos ─────────────────────────────────────────────── */
h1 { font-size: 1.75rem !important; font-weight: 700 !important; color: var(--mt-dark) !important; margin-bottom: 0.25rem !important; }
h2 { font-size: 1.35rem !important; font-weight: 600 !important; color: var(--mt-dark) !important; }
h3 { font-size: 1.1rem  !important; font-weight: 600 !important; color: var(--mt-dark) !important; }

/* ── Tabs ────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
  gap: 0 !important;
  background: var(--mt-white) !important;
  border-radius: 10px 10px 0 0 !important;
  border: 1px solid var(--mt-border) !important;
  border-bottom: none !important;
  padding: 4px 8px 0 8px !important;
}
.stTabs [data-baseweb="tab"] {
  font-family: 'Inter', sans-serif !important;
  font-weight: 500 !important;
  font-size: 13px !important;
  color: var(--mt-muted) !important;
  padding: 10px 18px !important;
  border-radius: 8px 8px 0 0 !important;
  border: none !important;
  background: transparent !important;
}
.stTabs [aria-selected="true"] {
  color: var(--mt-teal) !important;
  font-weight: 600 !important;
  border-bottom: 2px solid var(--mt-teal) !important;
}
.stTabs [data-baseweb="tab-panel"] {
  background: var(--mt-white) !important;
  border: 1px solid var(--mt-border) !important;
  border-top: none !important;
  border-radius: 0 0 10px 10px !important;
  padding: 1.5rem !important;
}

/* ── Botões ──────────────────────────────────────────────── */
.stButton button {
  font-family: 'Inter', sans-serif !important;
  font-weight: 500 !important;
  font-size: 13px !important;
  border-radius: 8px !important;
  padding: 6px 16px !important;
  transition: all 0.15s ease !important;
}
.stButton button[kind="primary"] {
  background: var(--mt-teal) !important;
  color: #fff !important;
  border: none !important;
}
.stButton button[kind="primary"]:hover {
  background: var(--mt-dark) !important;
}
.stButton button[kind="secondary"] {
  background: var(--mt-white) !important;
  color: var(--mt-teal) !important;
  border: 1px solid var(--mt-teal) !important;
}

/* ── Inputs ──────────────────────────────────────────────── */
.stTextInput input, .stNumberInput input, .stDateInput input,
.stSelectbox select, .stTextArea textarea {
  font-family: 'Inter', sans-serif !important;
  font-size: 13px !important;
  border-radius: 8px !important;
  border: 1px solid var(--mt-border) !important;
  background: var(--mt-white) !important;
  color: var(--mt-text) !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
  border-color: var(--mt-teal) !important;
  box-shadow: 0 0 0 2px rgba(42,122,140,0.15) !important;
}

/* ── Selectbox ───────────────────────────────────────────── */
[data-baseweb="select"] > div {
  border-radius: 8px !important;
  border-color: var(--mt-border) !important;
  font-size: 13px !important;
}

/* ── Métricas nativas ────────────────────────────────────── */
[data-testid="metric-container"] {
  background: var(--mt-white) !important;
  border: 1px solid var(--mt-border) !important;
  border-radius: 10px !important;
  padding: 14px 18px !important;
}
[data-testid="metric-container"] label {
  font-size: 11px !important;
  font-weight: 600 !important;
  color: var(--mt-muted) !important;
  text-transform: uppercase !important;
  letter-spacing: .05em !important;
}
[data-testid="stMetricValue"] {
  font-size: 22px !important;
  font-weight: 700 !important;
  color: var(--mt-dark) !important;
}
[data-testid="stMetricDelta"] { display: none !important; }

/* ── Containers / expanders ──────────────────────────────── */
[data-testid="stExpander"] {
  border: 1px solid var(--mt-border) !important;
  border-radius: 10px !important;
  background: var(--mt-white) !important;
  margin-bottom: 8px !important;
}
[data-testid="stExpander"] summary {
  font-weight: 600 !important;
  font-size: 14px !important;
  color: var(--mt-dark) !important;
}

/* ── Dataframes ──────────────────────────────────────────── */
[data-testid="stDataFrame"] {
  border: 1px solid var(--mt-border) !important;
  border-radius: 10px !important;
  overflow: hidden !important;
}

/* ── Alerts / info / warning / success ───────────────────── */
.stAlert {
  border-radius: 8px !important;
  border-left-width: 3px !important;
  font-size: 13px !important;
}

/* ── File uploader ───────────────────────────────────────── */
[data-testid="stFileUploader"] {
  border: 2px dashed var(--mt-border) !important;
  border-radius: 10px !important;
  background: var(--mt-bg) !important;
}

/* ── Caption / pequeno texto ─────────────────────────────── */
.stCaption, [data-testid="stCaptionContainer"] {
  font-size: 12px !important;
  color: var(--mt-muted) !important;
}

/* ── Scrollbar ───────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--mt-bg); }
::-webkit-scrollbar-thumb { background: var(--mt-border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--mt-muted); }

/* ── Modo escuro ─────────────────────────────────────────── */
@media (prefers-color-scheme: dark) {
  :root {
    --mt-bg:     #0F1E28;
    --mt-white:  #162636;
    --mt-border: #243647;
    --mt-text:   #E8EFF3;
    --mt-muted:  #7A9AAD;
    --mt-dark:   #E8EFF3;
  }
  .stApp { background-color: var(--mt-bg) !important; }
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# SIDEBAR — logo e navegação
# ---------------------------------------------------------------------------
def _render_sidebar(user: dict):
    with st.sidebar:
        st.markdown("""
        <div style="padding:20px 16px 16px;border-bottom:1px solid rgba(255,255,255,0.1);margin-bottom:16px">
          <div style="font-size:20px;font-weight:700;color:#fff;letter-spacing:-.3px">Magna PME</div>
          <div style="font-size:11px;color:rgba(255,255,255,0.5);margin-top:2px">Gestão de Formação</div>
        </div>
        """, unsafe_allow_html=True)

        perfil_icons = {
            "formador":       "👤",
            "coordenador":    "📋",
            "gestor_projeto": "📊",
            "financeiro":     "💶",
            "admin":          "⚙️",
        }
        perfil_labels = {
            "formador":       "Formador",
            "coordenador":    "Coordenador",
            "gestor_projeto": "Gestor de Projeto",
            "financeiro":     "Financeiro",
            "admin":          "Administrador",
        }
        icon  = perfil_icons.get(user["role"], "👤")
        label = perfil_labels.get(user["role"], user["role"])

        st.markdown(f"""
        <div style="background:rgba(42,122,140,0.25);border:1px solid rgba(42,122,140,0.4);
                    border-radius:10px;padding:12px 14px;margin-bottom:20px">
          <div style="font-size:13px;font-weight:600;color:#fff">{icon} {user['nome']}</div>
          <div style="font-size:11px;color:rgba(255,255,255,0.6);margin-top:2px">{label}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("⎋  Sair", use_container_width=True, key="btn_sair"):
            st.session_state.user = None
            st.rerun()

        st.markdown("""
        <div style="position:absolute;bottom:20px;left:0;right:0;text-align:center;
                    font-size:10px;color:rgba(255,255,255,0.25)">
          Mentores & Tutores © 2026
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# LOGIN
# ---------------------------------------------------------------------------
def _login_simulado():
    # Cabeçalho centrado
    col_l, col_c, col_r = st.columns([1,2,1])
    with col_c:
        st.markdown("""
        <div style="text-align:center;padding:48px 0 32px">
          <div style="font-size:36px;font-weight:800;color:#1B3A4B;letter-spacing:-.5px">Magna PME</div>
          <div style="font-size:14px;color:#6B8090;margin-top:6px">Gestão administrativa e financeira de formação</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:#fff;border:1px solid #DDE4EA;border-radius:14px;
                    padding:32px;margin-bottom:24px">
          <div style="font-size:15px;font-weight:600;color:#1B3A4B;margin-bottom:20px;text-align:center">
            Escolhe um perfil de acesso
          </div>
        """, unsafe_allow_html=True)

        perfis = {
            "👤  Formadora":        {"nome": "Formadora",   "email": "formadora@demo.pt",   "role": "formador"},
            "📋  Coordenador":      {"nome": "Coordenador", "email": "coordenador@demo.pt", "role": "coordenador"},
            "📊  Gestora":          {"nome": "Gestora",     "email": "gestora@demo.pt",     "role": "gestor_projeto"},
            "💶  Financeiro":       {"nome": "Financeiro",  "email": "financeiro@demo.pt",  "role": "financeiro"},
        }
        for label, dados in perfis.items():
            if st.button(label, use_container_width=True, key=f"login_{label}"):
                st.session_state.user = dados
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div style="text-align:center;font-size:12px;color:#6B8090">
          🔒 Login OAuth Google em implementação
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    get_settings()

    if "user" not in st.session_state:
        st.session_state.user = None

    if st.session_state.user is None:
        _login_simulado()
        return

    user = st.session_state.user
    _render_sidebar(user)

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

if __name__ == "__main__":
    main()
