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

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background-color: var(--mt-dark) !important;
  border-right: none !important;
}
[data-testid="stSidebar"] * { color: #FFFFFF !important; }
[data-testid="stSidebar"] .stButton button {
  background: rgba(255,255,255,0.08) !important;
  color: #fff !important;
  border: 1px solid rgba(255,255,255,0.15) !important;
  border-radius: 8px !important;
  font-weight: 500 !important;
  font-size: 13px !important;
}
[data-testid="stSidebar"] .stButton button:hover {
  background: rgba(255,255,255,0.15) !important;
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


def _render_sidebar(user: dict):
    perfil_icons  = {"formador": "👤", "coordenador": "📋", "gestor_projeto": "📊", "financeiro": "💶", "admin": "⚙️"}
    perfil_labels = {"formador": "Formador", "coordenador": "Coordenador",
                     "gestor_projeto": "Gestor de Projeto", "financeiro": "Financeiro", "admin": "Administrador"}
    icon  = perfil_icons.get(user["role"], "👤")
    label = perfil_labels.get(user["role"], user["role"])

    with st.sidebar:
        # Marca
        st.markdown("### Magna PME")
        st.caption("Gestão de Formação")
        st.divider()

        # Utilizador
        st.markdown(f"**{icon}  {user['nome']}**")
        st.caption(label)
        st.divider()

        # Data / hora
        agora = datetime.now()
        st.caption(f"📅 {agora.strftime('%d %b %Y')}  ·  ⏰ {agora.strftime('%H:%M')}")

        # Estado da BD
        sb_ok, sb_label = _supabase_status()
        st.caption(f"{'🟢' if sb_ok else '🟠'} BD {sb_label}")

        # Sair
        if st.button("⎋  Sair da sessão", use_container_width=True, key="btn_sair"):
            st.session_state.user = None
            st.rerun()

        st.divider()
        st.caption("🚧 Ambiente de Teste · v0.1-beta")
        st.caption("Mentores & Tutores © 2026")

# ---------------------------------------------------------------------------
# BANNER TESTE
# ---------------------------------------------------------------------------
def _banner_teste():
    st.warning(
        "🚧 **Ambiente de teste** — os dados apresentados são fictícios. "
        "Não realizar operações reais nesta versão."
    )

# ---------------------------------------------------------------------------
# CABEÇALHO DE PÁGINA
# ---------------------------------------------------------------------------
def _page_header(user: dict, titulo: str, subtitulo: str = ""):
    agora = datetime.now()
    saudacao = "Bom dia" if agora.hour < 12 else ("Boa tarde" if agora.hour < 18 else "Boa noite")
    sub = subtitulo or f"{saudacao}, {user['nome']}"
    st.header(titulo)
    st.caption(sub)
    st.divider()

def _login_simulado():
    from pathlib import Path

    perfis = {
        "formador":       {"icon": "👤", "label": "Formador",          "desc": "Submissão de Faturas e Gestão de Ações",                 "nome": "Formadora",   "email": "formadora@demo.pt"},
        "coordenador":    {"icon": "📋", "label": "Coordenador",       "desc": "Gestão de Formandos, Formadores e Execução de Projetos", "nome": "Coordenador", "email": "coordenador@demo.pt"},
        "gestor_projeto": {"icon": "📊", "label": "Gestor de Projeto", "desc": "Visão Geral e Indicadores de Projetos",                  "nome": "Gestora",     "email": "gestora@demo.pt"},
        "financeiro":     {"icon": "💶", "label": "Financeiro",        "desc": "Gestão Financeira e Faturação",                          "nome": "Financeiro",  "email": "financeiro@demo.pt"},
    }

    # Única CSS do login: esconder a sidebar (é estrutural, não é "estilo")
    st.markdown('<style>[data-testid="stSidebar"]{display:none !important;}</style>', unsafe_allow_html=True)

    # Centrar numa coluna estreita usando layout nativo (sem CSS de tamanhos)
    _, centro, _ = st.columns([1, 2, 1])
    with centro:
        # Logo
        logo = next((p for p in ["docs/logo_magna_pme.png", "app/assets/logo.png",
                                  "app/logo.png", "logo.png"] if Path(p).exists()), None)
        if logo:
            st.image(logo, width=140)

        st.title("Magna PME")
        st.caption("Mentores & Tutores · Gestão de Formação")
        st.divider()
        st.caption("ACEDER COMO")

        for role, info in perfis.items():
            if st.button(f"{info['icon']}   {info['label']}", key=f"login_{role}", use_container_width=True):
                st.session_state.user = {"nome": info["nome"], "email": info["email"], "role": role}
                st.rerun()
            st.caption(info["desc"])

        st.divider()
        st.warning("🚧 Ambiente de Teste · v0.1-beta")
        st.caption("🔒 Login OAuth Google em implementação")

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

    st.markdown("""
    <div style="padding:1.5rem 2rem 0">
    """, unsafe_allow_html=True)

    _banner_teste()

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

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
