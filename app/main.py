"""Magna PME - entrypoint da app Streamlit."""
from __future__ import annotations
from datetime import datetime
import streamlit as st
from core.config import get_settings

st.set_page_config(
    page_title="Magna PME",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# CSS GLOBAL
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

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
}

html, body, [class*="css"], .stApp {
  font-family: 'Inter', sans-serif !important;
  color: var(--mt-text) !important;
}
.stApp { background-color: var(--mt-bg) !important; }

/* ── Esconde toolbar do Streamlit ── */
.stApp > header                    { display: none !important; }
[data-testid="stToolbar"]          { display: none !important; }
[data-testid="stDecoration"]       { display: none !important; }
[data-testid="stStatusWidget"]     { display: none !important; }
header[data-testid="stHeader"]     { display: none !important; }
#MainMenu                          { display: none !important; }
footer                             { display: none !important; }

/* ── Sidebar Redesenhada ── */
[data-testid="stSidebar"] {
  background-color: var(--mt-dark) !important;
  border-right: none !important;
}
[data-testid="stSidebar"] * { color: #FFFFFF !important; }
[data-testid="stSidebar"] .stButton button {
  background: rgba(255,255,255,0.05) !important;
  color: #fff !important;
  border: 1px solid rgba(255,255,255,0.2) !important;
  border-radius: 8px !important;
  font-weight: 500 !important;
  font-size: 13px !important;
  padding: 10px 16px !important;
  transition: all 0.2s ease !important;
}
[data-testid="stSidebar"] .stButton button:hover {
  background: rgba(255,255,255,0.12) !important;
  border-color: rgba(255,255,255,0.35) !important;
}

/* ── Layout principal ── */
.main .block-container {
  padding: 0 !important;
  max-width: 100% !important;
}

/* ── Títulos ── */
h1 { font-size: 1.7rem !important; font-weight: 700 !important; color: var(--mt-dark) !important; margin-bottom: 0.2rem !important; }
h2 { font-size: 1.3rem !important; font-weight: 600 !important; color: var(--mt-dark) !important; }
h3 { font-size: 1.05rem !important; font-weight: 600 !important; color: var(--mt-dark) !important; }

/* ── Tabs ── */
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
  padding: 1.5rem 2rem !important;
}

/* ── Botões ── */
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
.stButton button[kind="primary"]:hover { background: var(--mt-dark) !important; }
.stButton button[kind="secondary"] {
  background: var(--mt-white) !important;
  color: var(--mt-teal) !important;
  border: 1px solid var(--mt-teal) !important;
}

/* ── Inputs ── */
.stTextInput input, .stNumberInput input, .stDateInput input, .stTextArea textarea {
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
[data-baseweb="select"] > div {
  border-radius: 8px !important;
  border-color: var(--mt-border) !important;
  font-size: 13px !important;
}

/* ── Métricas ── */
[data-testid="metric-container"] {
  background: var(--mt-white) !important;
  border: 1px solid var(--mt-border) !important;
  border-radius: 10px !important;
  padding: 14px 18px !important;
}
[data-testid="metric-container"] label {
  font-size: 11px !important; font-weight: 600 !important;
  color: var(--mt-muted) !important; text-transform: uppercase !important;
  letter-spacing: .05em !important;
}
[data-testid="stMetricValue"] { font-size: 22px !important; font-weight: 700 !important; color: var(--mt-dark) !important; }
[data-testid="stMetricDelta"] { display: none !important; }

/* ── Expanders ── */
[data-testid="stExpander"] {
  border: 1px solid var(--mt-border) !important;
  border-radius: 10px !important;
  background: var(--mt-white) !important;
  margin-bottom: 8px !important;
}
[data-testid="stExpander"] summary { font-weight: 600 !important; font-size: 14px !important; color: var(--mt-dark) !important; }

/* ── Dataframes ── */
[data-testid="stDataFrame"] { border: 1px solid var(--mt-border) !important; border-radius: 10px !important; overflow: hidden !important; }

/* ── File uploader ── */
[data-testid="stFileUploader"] { border: 2px dashed var(--mt-border) !important; border-radius: 10px !important; background: var(--mt-bg) !important; }

/* ── Alerts ── */
.stAlert { border-radius: 8px !important; border-left-width: 3px !important; font-size: 13px !important; }

/* ── Caption ── */
.stCaption, [data-testid="stCaptionContainer"] { font-size: 12px !important; color: var(--mt-muted) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--mt-bg); }
::-webkit-scrollbar-thumb { background: var(--mt-border); border-radius: 3px; }

/* ── Containers com border ── */
[data-testid="stVerticalBlockBorderWrapper"] {
  border-radius: 10px !important;
  border-color: var(--mt-border) !important;
}

/* ── Modo escuro ── */
@media (prefers-color-scheme: dark) {
  :root {
    --mt-bg:    #0F1E28; --mt-white: #162636; --mt-border: #243647;
    --mt-text:  #E8EFF3; --mt-muted: #7A9AAD; --mt-dark:   #E8EFF3;
  }
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def _supabase_status() -> tuple[bool, str]:
    try:
        from app.db_financeiro import get_supabase
        get_supabase()
        return True, "Ligado"
    except Exception:
        return False, "Desligado"


# ---------------------------------------------------------------------------
# SIDEBAR — após login
# ---------------------------------------------------------------------------
def _render_sidebar(user: dict):
    with st.sidebar:
        # Logo / nome
        st.markdown("""
        <div style="padding:24px 12px 20px; border-bottom:1px solid rgba(255,255,255,0.08); margin-bottom:20px">
          <div style="font-size:20px; font-weight:800; color:#FFFFFF; letter-spacing:-0.5px; margin-bottom:4px">MAGNA PME</div>
          <div style="font-size:13px; color:rgba(255,255,255,0.6); font-weight:400">Gestão de Formação</div>
        </div>
        """, unsafe_allow_html=True)

        # Card utilizador estruturado
        perfil_icons  = {"formador":"👤","coordenador":"📋","gestor_projeto":"📊","financeiro":"💷","admin":"⚙️"}
        perfil_labels = {"formador":"Formador","coordenador":"Coordenador",
                         "gestor_projeto":"Gestor de Projeto","financeiro":"Financeiro","admin":"Administrador"}
        icon  = perfil_icons.get(user["role"], "👤")
        label = perfil_labels.get(user["role"], user["role"])

        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.1);
                    border-radius:12px; padding:16px; margin-bottom:24px">
          <div style="display:flex; align-items:center; gap:12px">
            <div style="font-size:22px; background:rgba(255,255,255,0.1); width:38px; height:38px; border-radius:8px; display:flex; align-items:center; justify-content:center">{icon}</div>
            <div>
              <div style="font-size:14px; font-weight:600; color:#
