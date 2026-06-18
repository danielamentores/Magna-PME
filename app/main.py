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

/* ── Esconde toolbar do Streamlit (botões a vermelho/Deploy/menu) ── */
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


# ---------------------------------------------------------------------------
# SIDEBAR — após login
# ---------------------------------------------------------------------------
def _render_sidebar(user: dict):
    with st.sidebar:
        # Logo / nome
        st.markdown("""
        <div style="padding:24px 16px 16px;border-bottom:1px solid rgba(255,255,255,0.08);margin-bottom:16px">
          <div style="font-size:11px;font-weight:600;color:rgba(255,255,255,0.4);
                      letter-spacing:.1em;text-transform:uppercase;margin-bottom:8px">Magna PME</div>
          <div style="font-size:13px;color:rgba(255,255,255,0.5)">Gestão de Formação</div>
        </div>
        """, unsafe_allow_html=True)

        # Card utilizador
        perfil_icons  = {"formador":"👤","coordenador":"📋","gestor_projeto":"📊","financeiro":"💶","admin":"⚙️"}
        perfil_labels = {"formador":"Formador","coordenador":"Coordenador",
                         "gestor_projeto":"Gestor de Projeto","financeiro":"Financeiro","admin":"Administrador"}
        icon  = perfil_icons.get(user["role"], "👤")
        label = perfil_labels.get(user["role"], user["role"])

        st.markdown(f"""
        <div style="background:rgba(42,122,140,0.2);border:1px solid rgba(42,122,140,0.35);
                    border-radius:10px;padding:12px 14px;margin-bottom:20px">
          <div style="font-size:14px;font-weight:600;color:#fff">{icon}&nbsp;&nbsp;{user['nome']}</div>
          <div style="font-size:11px;color:rgba(255,255,255,0.55);margin-top:3px">{label}</div>
        </div>
        """, unsafe_allow_html=True)

        # Data/hora
        agora = datetime.now()
        st.markdown(f"""
        <div style="font-size:12px;color:rgba(255,255,255,0.4);margin-bottom:6px;padding:0 2px">
          📅&nbsp;{agora.strftime("%d %b %Y")}&nbsp;&nbsp;⏰&nbsp;{agora.strftime("%H:%M")}
        </div>
        """, unsafe_allow_html=True)

        # Estado Supabase
        sb_ok, sb_label = _supabase_status()
        sb_color = "#22C55E" if sb_ok else "#F59E0B"
        sb_dot   = "●" if sb_ok else "●"
        st.markdown(f"""
        <div style="font-size:12px;color:rgba(255,255,255,0.4);margin-bottom:20px;padding:0 2px">
          <span style="color:{sb_color}">{sb_dot}</span>&nbsp;BD {sb_label}
        </div>
        """, unsafe_allow_html=True)

        if st.button("⎋  Sair da sessão", use_container_width=True, key="btn_sair"):
            st.session_state.user = None
            st.rerun()

        # Versão + ambiente de teste
        st.markdown("""
        <div style="margin-top:24px;padding:10px 12px;background:rgba(245,158,11,0.15);
                    border:1px solid rgba(245,158,11,0.3);border-radius:8px">
          <div style="font-size:11px;font-weight:600;color:#FCD34D">🚧 Ambiente de Teste</div>
          <div style="font-size:11px;color:rgba(255,255,255,0.4);margin-top:2px">
            Dados fictícios · v0.1-beta
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="position:fixed;bottom:16px;font-size:10px;color:rgba(255,255,255,0.2)">
          Mentores & Tutores © 2026
        </div>
        """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# BANNER TESTE — aparece no topo de cada página
# ---------------------------------------------------------------------------
def _banner_teste():
    st.markdown("""
    <div style="background:#FFFBEB;border-bottom:1px solid #FCD34D;
                padding:8px 24px;margin:-1rem -2.5rem 1.5rem -2.5rem;
                display:flex;align-items:center;gap:10px;font-size:13px;color:#92400E">
      <span>🚧</span>
      <strong>Ambiente de teste</strong>
      <span style="color:#D97706">—</span>
      <span>Os dados apresentados são fictícios. Não realizar operações reais nesta versão.</span>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# CABEÇALHO DE PÁGINA — substitui st.header genérico
# ---------------------------------------------------------------------------
def _page_header(user: dict, titulo: str, subtitulo: str = ""):
    agora = datetime.now()
    saudacao = "Bom dia" if agora.hour < 12 else ("Boa tarde" if agora.hour < 18 else "Boa noite")
    sub = subtitulo or f"{saudacao}, {user['nome']}"
    st.markdown(f"""
    <div style="padding:1.5rem 2rem 1rem;border-bottom:1px solid #DDE4EA;
                margin:-1rem -2rem 1.5rem -2rem;background:#fff">
      <div style="font-size:22px;font-weight:700;color:#1B3A4B">{titulo}</div>
      <div style="font-size:13px;color:#6B8090;margin-top:4px">{sub}</div>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# LOGIN
# ---------------------------------------------------------------------------
def _login_simulado():
    # Esconde a sidebar no login
    st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    .main .block-container { padding: 0 !important; }
    </style>
    """, unsafe_allow_html=True)

    perfis = {
        "formador":       {"icon":"👤","label":"Formador",       "desc":"Submissão de Faturas e Gestão de Ações",      "nome":"Formadora",   "email":"formadora@demo.pt"},
        "coordenador":    {"icon":"📋","label":"Coordenador",    "desc":"Gestão de Formandos, Formadores e Execução de Projetos",  "nome":"Coordenador", "email":"coordenador@demo.pt"},
        "gestor_projeto": {"icon":"📊","label":"Gestor de Projeto","desc":"Visão Geral e Indicadores de Projetos",    "nome":"Gestora",     "email":"gestora@demo.pt"},
        "financeiro":     {"icon":"💶","label":"Financeiro",     "desc":"Gestão Financeira e Faturação",              "nome":"Financeiro",  "email":"financeiro@demo.pt"},
    }

    sel = st.session_state.get("login_sel", "formador")

    import streamlit.components.v1 as components

    p = perfis[sel]

    cards_html = ""
    for role, info in perfis.items():
        ativo  = sel == role
        bg     = "rgba(42,122,140,0.35)" if ativo else "rgba(255,255,255,0.05)"
        border = "1px solid rgba(42,122,140,0.6)" if ativo else "1px solid rgba(255,255,255,0.1)"
        dot    = '<span style="color:#2A7A8C;font-size:10px">●</span>' if ativo else ""
        onclick = f"document.getElementById('role_input').value='{role}';document.getElementById('login_form').submit();"
        cards_html += f"""
        <div onclick="{onclick}" style="background:{bg};border:{border};border-radius:10px;
             padding:14px 16px;margin-bottom:8px;cursor:pointer;
             display:flex;align-items:center;gap:12px;transition:all .15s">
          <div style="font-size:22px">{info['icon']}</div>
          <div style="flex:1">
            <div style="font-size:14px;font-weight:600;color:#fff">{info['label']}</div>
            <div style="font-size:11px;color:rgba(255,255,255,0.45);margin-top:2px">{info['desc']}</div>
          </div>
          {dot}
        </div>"""

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
      * {{ margin:0;padding:0;box-sizing:border-box;font-family:'Inter',sans-serif; }}
      body {{ background:#F4F7F9;display:flex;height:100vh;overflow:hidden; }}
      .left {{
        width:380px;min-width:380px;background:#1B3A4B;
        padding:40px 28px;display:flex;flex-direction:column;
        overflow-y:auto;
      }}
      .right {{
        flex:1;display:flex;align-items:center;justify-content:center;
        padding:40px;background:#F4F7F9;
      }}
      .right-inner {{ width:100%;max-width:400px; }}
      .badge {{
        display:inline-flex;align-items:center;gap:8px;
        background:#EBF5F7;border-radius:20px;padding:6px 14px;margin-bottom:24px;
      }}
      .badge span {{ font-size:11px;font-weight:600;color:#2A7A8C;text-transform:uppercase;letter-spacing:.08em; }}
      .title {{ font-size:32px;font-weight:800;color:#1B3A4B;margin-bottom:8px; }}
      .subtitle {{ font-size:14px;color:#6B8090;margin-bottom:32px;line-height:1.5; }}
      .card {{
        background:#fff;border:1px solid #DDE4EA;border-radius:14px;padding:28px;
      }}
      .card p {{ font-size:13px;color:#6B8090;text-align:center;margin-bottom:20px; }}
      .btn {{
        width:100%;padding:14px;background:#2A7A8C;color:#fff;border:none;
        border-radius:8px;font-size:15px;font-weight:600;cursor:pointer;
        transition:background .15s;
      }}
      .btn:hover {{ background:#1B3A4B; }}
      .oauth {{ text-align:center;font-size:12px;color:#A0B0BC;margin-top:16px; }}
      .brand {{ margin-bottom:40px; }}
      .brand h1 {{ font-size:22px;font-weight:800;color:#fff;letter-spacing:-.3px; }}
      .brand p {{ font-size:12px;color:rgba(255,255,255,0.4);margin-top:4px; }}
      .aceder {{ font-size:11px;font-weight:600;color:rgba(255,255,255,0.35);
                 letter-spacing:.1em;text-transform:uppercase;margin-bottom:14px; }}
      .test-banner {{
        margin-top:auto;padding:12px 14px;
        background:rgba(245,158,11,0.12);border:1px solid rgba(245,158,11,0.25);border-radius:8px;
      }}
      .test-banner h4 {{ font-size:11px;font-weight:600;color:#FCD34D;margin-bottom:2px; }}
      .test-banner p {{ font-size:11px;color:rgba(255,255,255,0.35); }}
      form {{ display:none; }}
    </style>
    </head>
    <body>
      <div class="left">
        <div class="brand">
          <h1>Magna PME</h1>
          <p>Mentores &amp; Tutores · Gestão de Formação</p>
        </div>
        <div class="aceder">Aceder como</div>
        {cards_html}
        <div class="test-banner" style="margin-top:28px">
          <h4>🚧 Ambiente de Teste</h4>
          <p>Dados fictícios · v0.1-beta</p>
        </div>
      </div>
      <div class="right">
        <div class="right-inner">
          <div class="badge">
            <span style="font-size:18px">{p['icon']}</span>
            <span>{p['label']}</span>
          </div>
          <div class="title">Bem-vindo</div>
          <div class="subtitle">{p['desc']}</div>
          <div class="card">
            <p>Clica em <strong>Entrar</strong> para aceder como <strong>{p['label']}</strong></p>
            <button class="btn" onclick="window.parent.postMessage({{type:'streamlit:setComponentValue',value:'{sel}'}}, '*')">
              Entrar
            </button>
          </div>
          <div class="oauth">🔒 Login OAuth Google em implementação</div>
        </div>
      </div>
    </body>
    </html>
    """

    col_left, col_right = st.columns([2, 3])
    with col_left:
        for role, info in perfis.items():
            if st.button(info['label'], key=f"sel_{role}", help=info['desc']):
                st.session_state.login_sel = role
                st.rerun()
    with col_right:
        if st.button("▶ Entrar", type="primary", use_container_width=True, key="btn_entrar"):
            st.session_state.user = {
                "nome":  p["nome"],
                "email": p["email"],
                "role":  sel,
            }
            st.session_state.pop("login_sel", None)
            st.rerun()

    components.html(html, height=700, scrolling=False)


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
