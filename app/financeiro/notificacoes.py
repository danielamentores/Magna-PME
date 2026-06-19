"""Tab Notificações — página do financeiro."""
from __future__ import annotations
import streamlit as st
from app.financeiro.helpers import (
    eur, ptag, bdg, kpi_h, sec, div, CORES, BGS,
    ordenar, fil_proj, fil_datas, excel_bytes, extrair_pdf,
    guardar_comprovativo, notificar_rejeicao,
    _formador, _projeto, _email, ORDEM, PLOTLY_CFG,
)

try:
    from app.db_financeiro import get_supabase
    get_supabase()
    SUPABASE_OK = True
except Exception:
    SUPABASE_OK = False

_MOCK_NOTIFS = [
    {"id":"n1","tipo":"fatura_formador","titulo":"Nova fatura submetida","texto":"Miguel Santos submeteu FT2026/0155 (€ 2.400) — MENTORES","timestamp":"2026-06-15 14:32","lida":False},
    {"id":"n2","tipo":"fatura_formador","titulo":"Nova fatura submetida","texto":"Sofia Rodrigues submeteu FT2026/0153 (€ 1.950) — ANIET","timestamp":"2026-06-14 11:20","lida":False},
    {"id":"n3","tipo":"fatura_consultor","titulo":"Fatura de consultor recebida","texto":"Etapas Pioneiras submeteu FT-EC-2026/001 (€ 2.902) com NH associada","timestamp":"2026-06-13 09:45","lida":False},
    {"id":"n4","tipo":"fatura_formador","titulo":"Nova fatura submetida","texto":"Luís Cardoso submeteu FT2026/0150 (€ 1.800) — PRODUTECH","timestamp":"2026-06-13 08:10","lida":True},
    {"id":"n5","tipo":"fatura_consultor","titulo":"Fatura de consultor recebida","texto":"Winet Consulting submeteu fatura NH-2026/003 (€ 1.646) com NH associada","timestamp":"2026-06-10 16:55","lida":True},
]

# ---------------------------------------------------------------------------
# PAINEL DE NOTIFICAÇÕES
# ---------------------------------------------------------------------------
def _render_notificacoes():
    notifs = st.session_state.get("notificacoes", [])
    n_novas = len([n for n in notifs if not n.get("lida")])

    col_t, col_btn = st.columns([5,2])
    with col_t:
        st.html(
            f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">'
            f'<span style="font-size:16px;font-weight:700;color:#1A1F2E">🔔 Notificações</span>'
            f'{"<span class=\\'notif-badge\\'>" + str(n_novas) + " novas</span>" if n_novas > 0 else "<span style=\\'font-size:12px;color:#8B94A3\\'>Tudo lido</span>"}'
            f'</div>'
        )
    with col_btn:
        if n_novas > 0:
            if st.button("✓ Marcar todas como lidas", key="notif_lidas", use_container_width=True):
                _marcar_todas_lidas()
                st.rerun()

    if not notifs:
        st.html('<div class="fin-empty">Sem notificações.</div>')
        return

    # Separar novas e lidas
    novas = [n for n in notifs if not n.get("lida")]
    lidas = [n for n in notifs if n.get("lida")]

    items_html = ""
    for n in novas + lidas:
        lida = n.get("lida", False)
        tipo_ico = "📄" if n.get("tipo")=="fatura_formador" else "🤝"
        dot_cls = "notif-dot lida" if lida else "notif-dot"
        item_cls = "notif-item lida" if lida else "notif-item nova"
        items_html += (
            f'<div class="{item_cls}">'
            f'<div class="{dot_cls}" style="margin-top:5px"></div>'
            f'<div style="flex:1">'
            f'<div style="font-size:13px;font-weight:{"400" if lida else "600"};color:#1A1F2E">'
            f'{tipo_ico} {n["titulo"]}</div>'
            f'<div style="font-size:12px;color:#4B5263;margin-top:2px">{n["texto"]}</div>'
            f'<div style="font-size:11px;color:#8B94A3;margin-top:2px">{n["timestamp"]}</div>'
            f'</div>'
            f'</div>'
        )

    st.html(f'<div class="notif-panel">{items_html}</div>')

    # Marcar individualmente
    with st.expander("Ver e gerir notificações individuais", expanded=False):
        for i, n in enumerate(novas):
            col_txt, col_btn2 = st.columns([5,1])
            with col_txt:
                st.markdown(f"**{n['titulo']}** — {n['texto']} _{n['timestamp']}_")
            with col_btn2:
                if st.button("✓", key=f"notif_lr_{i}", help="Marcar como lida"):
                    n["lida"] = True
                    st.rerun()
