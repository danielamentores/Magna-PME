"""Tab Alertas — envio e receção de alertas entre Financeiro, Formadores, Consultores e Gestora."""
from __future__ import annotations
from datetime import datetime
import streamlit as st
from app.financeiro.helpers import ptag, bdg

try:
    from app.db_financeiro import get_supabase; get_supabase()
    SUPABASE_OK = True
except Exception:
    SUPABASE_OK = False

def _e(v):
    try: return f"{float(v):,.2f} €".replace(",","X").replace(".",",").replace("X",".")
    except: return "— €"

def _ts():
    return datetime.now().strftime("%d/%m/%Y %H:%M")

# ── Mock data ────────────────────────────────────────────────────────────────
_MOCK_ALERTAS = [
    {"id":"al1","de":"Formador 1","para":"Financeiro","tipo":"problema_fatura",
     "mensagem":"A minha fatura FT2026/0155 foi rejeitada mas o valor está correto conforme o contrato.",
     "timestamp":"2026-06-15 14:32","lido":False,"prioridade":"alta","projeto":"MENTORES"},
    {"id":"al2","de":"Gestora","para":"Financeiro","tipo":"nh_emitida",
     "mensagem":"NH emitida para Consultor 2 referente à ação FENABEL.GEPSLT_16 — valor 699,84 €.",
     "timestamp":"2026-06-14 11:20","lido":False,"prioridade":"normal","projeto":"MENTORES"},
    {"id":"al3","de":"Consultor 1","para":"Financeiro","tipo":"atraso_pagamento",
     "mensagem":"A fatura FT-EC-2026/001 já está em atraso há 15 dias. Quando é previsto o pagamento?",
     "timestamp":"2026-06-13 09:45","lido":False,"prioridade":"alta","projeto":"ANIET"},
    {"id":"al4","de":"Financeiro","para":"Formador 2","tipo":"aviso",
     "mensagem":"A sua fatura FT2026/0153 tem o nome do formador incorreto. Por favor resubmete com os dados corretos.",
     "timestamp":"2026-06-12 16:00","lido":True,"prioridade":"normal","projeto":"ANIET"},
    {"id":"al5","de":"Financeiro","para":"Consultor 2","tipo":"aviso",
     "mensagem":"Aguardamos o comprovativo de pagamento para a ação FENABEL.GEPSLT_16.",
     "timestamp":"2026-06-11 10:30","lido":True,"prioridade":"normal","projeto":"MENTORES"},
    {"id":"al6","de":"Gestora","para":"Financeiro","tipo":"info",
     "mensagem":"Ação JMS.PCE.01 fechada — pode emitir a fatura à empresa J. Moreira da Silva.",
     "timestamp":"2026-06-10 09:00","lido":True,"prioridade":"normal","projeto":"MENTORES"},
]

_TIPO_ICONS = {
    "problema_fatura": "⚠️",
    "nh_emitida":      "📋",
    "atraso_pagamento":"🔴",
    "aviso":           "📢",
    "info":            "ℹ️",
    "outro":           "💬",
}
_TIPO_LABELS = {
    "problema_fatura": "Problema na fatura",
    "nh_emitida":      "NH emitida",
    "atraso_pagamento":"Atraso de pagamento",
    "aviso":           "Aviso",
    "info":            "Informação",
    "outro":           "Outro",
}
_PRIORIDADE_COR = {"alta": "#DC2626", "normal": "#2563EB", "baixa": "#6B7280"}

def _get_alertas():
    if not SUPABASE_OK:
        return list(_MOCK_ALERTAS)
    try:
        r = get_supabase().table("alertas").select("*").order("created_at", desc=True).execute()
        return r.data if r.data else _MOCK_ALERTAS
    except:
        return list(_MOCK_ALERTAS)

def _marcar_lido(alerta_id: str):
    if not SUPABASE_OK:
        for a in st.session_state.alertas:
            if a["id"] == alerta_id: a["lido"] = True
        return
    try:
        get_supabase().table("alertas").update({"lido": True}).eq("id", alerta_id).execute()
    except: pass

def _enviar_alerta(para: str, tipo: str, mensagem: str, projeto: str, prioridade: str):
    novo = {"id": f"al_{datetime.now().strftime('%H%M%S')}",
            "de": "Financeiro", "para": para, "tipo": tipo,
            "mensagem": mensagem, "timestamp": _ts(),
            "lido": False, "prioridade": prioridade, "projeto": projeto}
    if not SUPABASE_OK:
        st.session_state.alertas.insert(0, novo)
        return True
    try:
        get_supabase().table("alertas").insert({
            "de": "Financeiro", "para": para, "tipo": tipo,
            "mensagem": mensagem, "prioridade": prioridade,
            "projeto_id": projeto,
        }).execute()
        return True
    except: return False

# ── Render ────────────────────────────────────────────────────────────────────
def render_alertas_tab():
    if "alertas" not in st.session_state:
        st.session_state.alertas = _get_alertas()

    alertas = st.session_state.alertas
    nao_lidos = [a for a in alertas if not a.get("lido")]

    # ── Header com contadores ──
    col_rec, col_env, col_todos = st.columns(3)
    vista_key = "alertas_vista"
    if vista_key not in st.session_state: st.session_state[vista_key] = "recebidos"

    with col_rec:
        badge = f" ({len(nao_lidos)})" if nao_lidos else ""
        if st.button(f"📥 Recebidos{badge}", use_container_width=True,
                     type="primary" if st.session_state[vista_key]=="recebidos" else "secondary",
                     key="vista_rec"):
            st.session_state[vista_key] = "recebidos"; st.rerun()
    with col_env:
        enviados = [a for a in alertas if a.get("de") == "Financeiro"]
        if st.button(f"📤 Enviados ({len(enviados)})", use_container_width=True,
                     type="primary" if st.session_state[vista_key]=="enviados" else "secondary",
                     key="vista_env"):
            st.session_state[vista_key] = "enviados"; st.rerun()
    with col_todos:
        if st.button("➕ Novo alerta", use_container_width=True,
                     type="primary" if st.session_state[vista_key]=="novo" else "secondary",
                     key="vista_novo"):
            st.session_state[vista_key] = "novo"; st.rerun()

    st.html('<div style="height:1px;background:#E4E7EF;margin:16px 0"></div>')

    vista = st.session_state[vista_key]

    # ── Vista: Novo alerta ──
    if vista == "novo":
        st.html('<p style="font-size:13px;font-weight:700;color:#4B5263;text-transform:uppercase;letter-spacing:.06em;margin-bottom:16px">Enviar novo alerta</p>')

        col_a, col_b = st.columns(2)
        with col_a:
            destinatario = st.selectbox("Destinatário", [
                "Formador 1","Formador 2","Formador 3","Formador 4","Formador 5",
                "Consultor 1","Consultor 2","Consultor 3","Gestora",
            ], key="alerta_para")
            tipo_alerta = st.selectbox("Tipo", list(_TIPO_LABELS.keys()),
                                       format_func=lambda x: f"{_TIPO_ICONS.get(x,'')} {_TIPO_LABELS.get(x,x)}",
                                       key="alerta_tipo")
        with col_b:
            proj_opts = ["MENTORES","ANIET","APCMC","APIMA","PRODUTECH","CALÇADO","—"]
            projeto = st.selectbox("Projeto", proj_opts, key="alerta_proj")
            prioridade = st.selectbox("Prioridade", ["normal","alta","baixa"],
                                      format_func=lambda x: {"normal":"🔵 Normal","alta":"🔴 Alta","baixa":"⚪ Baixa"}.get(x,x),
                                      key="alerta_prio")

        mensagem = st.text_area("Mensagem", key="alerta_msg", height=120,
                                 placeholder="Descreve o problema ou informação a comunicar...")

        col_btn, _ = st.columns([2, 4])
        with col_btn:
            if st.button("📤 Enviar alerta", use_container_width=True, type="primary", key="btn_send"):
                if mensagem.strip():
                    if _enviar_alerta(destinatario, tipo_alerta, mensagem.strip(), projeto, prioridade):
                        st.success(f"✅ Alerta enviado para {destinatario}.")
                        st.session_state[vista_key] = "enviados"; st.rerun()
                    else:
                        st.error("Erro ao enviar o alerta.")
                else:
                    st.warning("Escreve uma mensagem antes de enviar.")
        return

    # ── Filtros ──
    col_f1, col_f2, col_f3 = st.columns([2, 2, 2])
    with col_f1:
        filtro_tipo = st.selectbox("Tipo", ["Todos"] + list(_TIPO_LABELS.keys()),
                                   format_func=lambda x: "Todos" if x=="Todos" else f"{_TIPO_ICONS.get(x,'')} {_TIPO_LABELS.get(x,x)}",
                                   key="filt_al_tipo")
    with col_f2:
        filtro_prio = st.selectbox("Prioridade", ["Todas","alta","normal","baixa"],
                                   format_func=lambda x: {"Todas":"Todas","alta":"🔴 Alta","normal":"🔵 Normal","baixa":"⚪ Baixa"}.get(x,x),
                                   key="filt_al_prio")
    with col_f3:
        filtro_proj = st.selectbox("Projeto", ["Todos","MENTORES","ANIET","APCMC","APIMA","PRODUTECH","CALÇADO"],
                                   key="filt_al_proj")

    # ── Lista de alertas ──
    if vista == "recebidos":
        lista = [a for a in alertas if a.get("para") == "Financeiro"]
        empty_msg = "Não há alertas recebidos."
    else:
        lista = [a for a in alertas if a.get("de") == "Financeiro"]
        empty_msg = "Não há alertas enviados."

    if filtro_tipo != "Todos":
        lista = [a for a in lista if a.get("tipo") == filtro_tipo]
    if filtro_prio != "Todas":
        lista = [a for a in lista if a.get("prioridade") == filtro_prio]
    if filtro_proj != "Todos":
        lista = [a for a in lista if a.get("projeto") == filtro_proj]

    if not lista:
        st.html(f'<div style="background:#F7F8FC;border:1px dashed #E4E7EF;border-radius:10px;padding:24px;text-align:center;color:#8B94A3;font-size:13px">{empty_msg}</div>')
        return

    # Botão marcar todos como lidos (só nos recebidos)
    if vista == "recebidos" and any(not a.get("lido") for a in lista):
        if st.button("✓ Marcar todos como lidos", key="mark_all_al"):
            for a in lista:
                if not a.get("lido"): _marcar_lido(a["id"])
            st.rerun()

    for a in lista:
        lido     = a.get("lido", False)
        prio     = a.get("prioridade","normal")
        tipo     = a.get("tipo","outro")
        ico      = _TIPO_ICONS.get(tipo,"💬")
        tipo_lbl = _TIPO_LABELS.get(tipo, tipo)
        prio_cor = _PRIORIDADE_COR.get(prio,"#6B7280")
        proj     = a.get("projeto","—")
        bg_card  = "#fff" if lido else "#FAFFF5" if prio=="normal" else "#FFF8F8"
        borda    = "#E4E7EF" if lido else prio_cor
        opac     = "opacity:0.7;" if lido else ""

        col_card, col_act = st.columns([7, 1])
        with col_card:
            de_para = f'{a.get("de","—")} → {a.get("para","—")}'
            st.html(
                f'<div style="background:{bg_card};border:1px solid #E4E7EF;border-left:4px solid {borda};'
                f'border-radius:10px;padding:14px 18px;{opac}margin-bottom:4px">'
                f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">'
                f'<span style="font-size:15px">{ico}</span>'
                f'<span style="font-size:13px;font-weight:600;color:#1A1F2E">{tipo_lbl}</span>'
                f'<span style="font-size:11px;color:#8B94A3;margin-left:4px">{de_para}</span>'
                f'{"&nbsp;&nbsp;" + ptag(proj) if proj != "—" else ""}'
                f'<span style="margin-left:auto;font-size:11px;color:{prio_cor};font-weight:600">'
                f'{"🔴 Alta" if prio=="alta" else "🔵 Normal" if prio=="normal" else "⚪ Baixa"}</span>'
                f'</div>'
                f'<div style="font-size:14px;color:#2D3748;line-height:1.5">{a.get("mensagem","")}</div>'
                f'<div style="font-size:11px;color:#8B94A3;margin-top:6px">{a.get("timestamp","")}'
                f'{"&nbsp;&nbsp;·&nbsp;&nbsp;✓ lido" if lido else ""}</div>'
                f'</div>'
            )
        with col_act:
            if not lido and vista == "recebidos":
                st.markdown("<div style='margin-top:14px'>", unsafe_allow_html=True)
                if st.button("✓", key=f"lido_{a['id']}", help="Marcar como lido", use_container_width=True):
                    _marcar_lido(a["id"]); st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
