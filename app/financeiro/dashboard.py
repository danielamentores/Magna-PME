"""Tab Dashboard — página do financeiro."""
from __future__ import annotations
import streamlit as st
import plotly.graph_objects as go
from app.financeiro.helpers import (
    ptag, bdg, kpi_h, sec, div, CORES, BGS,
    _formador, _projeto, PLOTLY_CFG,
    n_notifs_nao_lidas, marcar_todas_lidas,
)

try:
    from app.db_financeiro import (
        get_metricas_dashboard, get_faturas_recentes, get_despesa_por_projeto,
        get_supabase,
    )
    get_supabase()
    SUPABASE_OK = True
except Exception:
    SUPABASE_OK = False

_MOCK_AV = [
    {"id":"a1","numero_fatura":"FT2026/0142","valor":3200,"prazo_pagamento":"2026-06-21","data_fatura":"2026-06-01","dias":5,"profiles":{"nome":"João Silva","email":"joao@demo.pt"},"acoes":{"nome":"MENTORES"}},
    {"id":"a2","numero_fatura":"FT2026/0138","valor":2800,"prazo_pagamento":"2026-06-27","data_fatura":"2026-06-03","dias":11,"profiles":{"nome":"Ana Ferreira","email":"ana@demo.pt"},"acoes":{"nome":"ANIET"}},
    {"id":"a3","numero_fatura":"FT2026/0136","valor":1900,"prazo_pagamento":"2026-07-04","data_fatura":"2026-06-05","dias":18,"profiles":{"nome":"Pedro Costa","email":"pedro@demo.pt"},"acoes":{"nome":"CALÇADO"}},
    {"id":"a4","numero_fatura":"FT2026/0129","valor":2100,"prazo_pagamento":"2026-07-10","data_fatura":"2026-06-06","dias":24,"profiles":{"nome":"Carla Neves","email":"carla@demo.pt"},"acoes":{"nome":"APCMC"}},
    {"id":"a5","numero_fatura":"FT2026/0127","valor":2300,"prazo_pagamento":"2026-07-16","data_fatura":"2026-06-08","dias":30,"profiles":{"nome":"Rui Mendes","email":"rui@demo.pt"},"acoes":{"nome":"APIMA"}},
]

# Mock values por período — quando a BD ligar, estes vêm da query com filtro de datas
_MOCK_PERIODOS = {
    "Tudo":          {"n_pre":3,"tp":6150,"n_apr":5,"ta":12300,"n_pago":23,"tpago":23150,"n_venc":1,"tv":3321.34},
    "Este mês":      {"n_pre":2,"tp":4350,"n_apr":3,"ta":7200, "n_pago":8, "tpago":9200, "n_venc":1,"tv":3321.34},
    "Mês anterior":  {"n_pre":1,"tp":1800,"n_apr":2,"ta":5100, "n_pago":15,"tpago":13950,"n_venc":0,"tv":0},
    "Este ano":      {"n_pre":3,"tp":6150,"n_apr":5,"ta":12300,"n_pago":23,"tpago":23150,"n_venc":1,"tv":3321.34},
}

def _e(v) -> str:
    """Valor com € à direita."""
    try: return f"{float(v):,.2f} €".replace(",","X").replace(".",",").replace("X",".")
    except: return "— €"

def render_dashboard(user):
    # ── Filtro de período ──
    col_per, _ = st.columns([2, 4])
    with col_per:
        periodo = st.selectbox(
            "Período", list(_MOCK_PERIODOS.keys()),
            key="dash_periodo",
        )

    st.html('<div style="height:6px"></div>')

    # ── Notificações — UMA vez, no topo ──
    notifs = st.session_state.get("notificacoes", [])
    novas  = [n for n in notifs if not n.get("lida")]
    if novas:
        n_txt = "🔔 1 notificação não lida" if len(novas) == 1 \
                else f"🔔 {len(novas)} notificações não lidas"
        with st.expander(n_txt, expanded=True):
            for n in novas[:5]:
                ico = "📄" if n.get("tipo") == "fatura_formador" else "🤝"
                st.html(
                    f'<div style="display:flex;align-items:flex-start;gap:10px;'
                    f'padding:8px 0;border-bottom:1px solid #F0F2F5">'
                    f'<div style="width:8px;height:8px;border-radius:50%;background:#D97706;'
                    f'flex-shrink:0;margin-top:5px"></div>'
                    f'<div style="flex:1">'
                    f'<div style="font-size:13px;font-weight:600;color:#1A1F2E">{ico} {n["titulo"]}</div>'
                    f'<div style="font-size:12px;color:#4B5263;margin-top:2px">{n["texto"]}</div>'
                    f'<div style="font-size:11px;color:#8B94A3;margin-top:2px">{n["timestamp"]}</div>'
                    f'</div></div>'
                )
            col_btn, _ = st.columns([2, 4])
            with col_btn:
                if st.button("✓ Marcar todas como lidas", key="dash_notif_lidas"):
                    marcar_todas_lidas()
                    st.rerun()

    # ── Dados (BD ou mock filtrado por período) ──
    if SUPABASE_OK:
        m      = get_metricas_dashboard()
        recentes = get_faturas_recentes(8)
        despesa  = get_despesa_por_projeto()
        n_pre, tp    = m["pre_aprovacao_count"],  m["pre_aprovacao_total"]
        n_apr, ta    = m["aprovado_count"],        m["aprovado_total"]
        n_pago, tpago= m["pago_mes_count"],        m["pago_mes_total"]
        n_venc, tv   = m["vencido_count"],         m["vencido_total"]
    else:
        p = _MOCK_PERIODOS[periodo]
        n_pre,  tp    = p["n_pre"],  p["tp"]
        n_apr,  ta    = p["n_apr"],  p["ta"]
        n_pago, tpago = p["n_pago"], p["tpago"]
        n_venc, tv    = p["n_venc"], p["tv"]
        recentes = _MOCK_AV[:5]
        despesa  = [{"projeto":k,"valor":v} for k,v in {
            "MENTORES":52400,"ANIET":38900,"APCMC":27600,
            "APIMA":19200,"PRODUTECH":61200,"CALÇADO":14600}.items()]

    # Aviso faturas pendentes
    if n_pre > 0:
        st.html(
            f'<div class="fin-warn">⚠️ <strong>{n_pre} fatura(s) aguardam aprovação manual'
            f'</strong> — ver em <strong>🧾 Faturas</strong>.</div>'
        )

    # ── KPIs ──
    kpi_pago_label = {
        "Este mês":     "💳 Pago este mês",
        "Mês anterior": "💳 Pago no mês anterior",
        "Este ano":     "💳 Pago este ano",
        "Tudo":         "💳 Total pago",
    }.get(periodo, "💳 Pago no período")

    st.html(
        '<div class="fin-kpi-row">'
        + kpi_h("🔍 Pré-aprovação",    _e(tp),    f"{n_pre} faturas",  "a")
        + kpi_h("✅ Aprovado a pagar",  _e(ta),    f"{n_apr} faturas",  "g")
        + kpi_h(kpi_pago_label,         _e(tpago), f"{n_pago} faturas", "b")
        + kpi_h("🚨 Vencido",           _e(tv),    f"{n_venc} faturas", "r")
        + '</div>'
    )

    st.html(div())

    # ── Faturas recentes + gráfico estado ──
    col_l, col_r = st.columns([3, 2])
    with col_l:
        st.markdown(sec("Faturas recentes"), unsafe_allow_html=True)
        cards = ""
        for row in recentes:
            f = _formador(row); p = _projeto(row)
            e = row.get("estado") or "submetida"
            n = row.get("numero_fatura") or "—"
            v = row.get("valor") or 0
            cards += (
                f'<div class="fin-card">'
                f'<div style="flex:1">'
                f'<div class="ct">{n}</div>'
                f'<div class="cm">{ptag(p)}&nbsp;·&nbsp;{f}</div>'
                f'</div>'
                f'<div style="text-align:right;margin-right:10px">'
                f'<div class="cv">{_e(v)}</div>'
                f'</div>'
                f'{bdg(e)}</div>'
            )
        st.markdown(cards, unsafe_allow_html=True)

    with col_r:
        st.markdown(sec("Por estado"), unsafe_allow_html=True)
        fig = go.Figure(go.Pie(
            labels=["Pré-aprovação","Aprovado","Pago","Vencido"],
            values=[n_pre or 1, n_apr or 1, n_pago or 1, n_venc or 1],
            hole=0.65,
            marker_colors=["#D97706","#16A34A","#2563EB","#DC2626"],
            textinfo="percent", textfont=dict(size=11), showlegend=True,
        ))
        fig.update_layout(
            margin=dict(t=10,b=10,l=0,r=10), height=270,
            legend=dict(orientation="v",x=1.0,y=0.5,font=dict(size=11),
                        xanchor="left",yanchor="middle"),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CFG)

    st.html(div())

    # ── Despesa por projeto ──
    st.markdown(sec("Despesa por projeto"), unsafe_allow_html=True)
    ds = sorted(despesa, key=lambda x: x["valor"])
    mx = max((d["valor"] for d in ds), default=1)
    fig2 = go.Figure(go.Bar(
        x=[d["valor"] for d in ds],
        y=[d["projeto"] for d in ds],
        orientation="h",
        marker_color=[CORES.get(d["projeto"],"#888") for d in ds],
        text=[_e(d["valor"]) for d in ds],
        textposition="outside", textfont=dict(size=12),
    ))
    fig2.update_layout(
        margin=dict(t=4,b=4,l=4,r=130), height=270,
        xaxis=dict(showticklabels=False, showgrid=False, range=[0,mx*1.35]),
        yaxis=dict(showgrid=False, tickfont=dict(size=13)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig2, use_container_width=True, config=PLOTLY_CFG)

    st.html(div())

    # ── Exportação global ──
    st.markdown(sec("⬇️ Exportação global"), unsafe_allow_html=True)
    col_e1, col_e2, col_e3 = st.columns(3)
    with col_e1:
        if st.button("📊 Exportar todas as faturas", use_container_width=True, key="exp_fat"):
            st.toast("Disponível quando a BD estiver ligada.")
    with col_e2:
        if st.button("🤝 Exportar consultores", use_container_width=True, key="exp_cons"):
            st.toast("Disponível quando a BD estiver ligada.")
    with col_e3:
        if st.button("🏢 Exportar faturação empresas", use_container_width=True, key="exp_emp"):
            st.toast("Disponível quando a BD estiver ligada.")
