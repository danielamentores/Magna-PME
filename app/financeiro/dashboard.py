"""Tab Dashboard — página do financeiro."""
from __future__ import annotations
import streamlit as st
from app.financeiro.helpers import (
    eur, ptag, bdg, kpi_h, sec, div, CORES, BGS,
    ordenar, fil_proj, fil_datas, excel_bytes, extrair_pdf,
    guardar_comprovativo, notificar_rejeicao,
    _formador, _projeto, _email, ORDEM, PLOTLY_CFG,
    n_notifs_nao_lidas,
)

try:
    from app.db_financeiro import get_supabase
    get_supabase()
    SUPABASE_OK = True
except Exception:
    SUPABASE_OK = False

import plotly.graph_objects as go

_MOCK_AV = [
    {"id":"a1","numero_fatura":"FT2026/0142","valor":3200,"prazo_pagamento":"2026-06-21","data_fatura":"2026-06-01","dias":5,"profiles":{"nome":"João Silva","email":"joao@demo.pt"},"acoes":{"nome":"MENTORES"}},
    {"id":"a2","numero_fatura":"FT2026/0138","valor":2800,"prazo_pagamento":"2026-06-27","data_fatura":"2026-06-03","dias":11,"profiles":{"nome":"Ana Ferreira","email":"ana@demo.pt"},"acoes":{"nome":"ANIET"}},
    {"id":"a3","numero_fatura":"FT2026/0136","valor":1900,"prazo_pagamento":"2026-07-04","data_fatura":"2026-06-05","dias":18,"profiles":{"nome":"Pedro Costa","email":"pedro@demo.pt"},"acoes":{"nome":"CALÇADO"}},
    {"id":"a4","numero_fatura":"FT2026/0129","valor":2100,"prazo_pagamento":"2026-07-10","data_fatura":"2026-06-06","dias":24,"profiles":{"nome":"Carla Neves","email":"carla@demo.pt"},"acoes":{"nome":"APCMC"}},
    {"id":"a5","numero_fatura":"FT2026/0127","valor":2300,"prazo_pagamento":"2026-07-16","data_fatura":"2026-06-08","dias":30,"profiles":{"nome":"Rui Mendes","email":"rui@demo.pt"},"acoes":{"nome":"APIMA"}},
]


_MOCK_PROJETOS = [
    {"id":"p1","nome":"MENTORES"},{"id":"p2","nome":"ANIET"},
    {"id":"p3","nome":"APCMC"},   {"id":"p4","nome":"APIMA"},
    {"id":"p5","nome":"PRODUTECH"},{"id":"p6","nome":"CALÇADO"},
]
_MOCK_DESPESA = {"MENTORES":52400,"ANIET":38900,"APCMC":27600,
                  "APIMA":19200,"PRODUTECH":61200,"CALÇADO":14600}

# ---------------------------------------------------------------------------
# TAB 1 — DASHBOARD
# ---------------------------------------------------------------------------
def render_dashboard(user):
    # Filtro de período
    col_per, _ = st.columns([2, 4])
    with col_per:
        periodo = st.selectbox("Período", ["Tudo", "Este mês", "Mês anterior", "Este ano"],
                               key="dash_periodo", label_visibility="visible")
    st.html('<div style="height:8px"></div>')

    # Painel de notificações no topo (se houver novas)
    notifs = st.session_state.get("notificacoes", [])
    novas = [n for n in notifs if not n.get("lida")]
    if novas:
        with st.expander(f"🔔 {len(novas)} notificação(ões) não lida(s)", expanded=True):
            for n in novas[:5]:  # máx 5 no dashboard
                tipo_ico = "📄" if n.get("tipo") == "fatura_formador" else "🤝"
                st.html(
                    f'<div style="display:flex;align-items:flex-start;gap:10px;'
                    f'padding:8px 0;border-bottom:1px solid #F0F2F5">'
                    f'<div style="width:8px;height:8px;border-radius:50%;background:#D97706;'
                    f'flex-shrink:0;margin-top:5px"></div>'
                    f'<div style="flex:1">'
                    f'<div style="font-size:13px;font-weight:600;color:#1A1F2E">'
                    f'{tipo_ico} {n["titulo"]}</div>'
                    f'<div style="font-size:12px;color:#4B5263;margin-top:2px">{n["texto"]}</div>'
                    f'<div style="font-size:11px;color:#8B94A3;margin-top:2px">{n["timestamp"]}</div>'
                    f'</div></div>'
                )
            col_btn, _ = st.columns([2, 4])
            with col_btn:
                if st.button("✓ Marcar todas como lidas", key="dash_notif_lidas"):
                    from app.financeiro.helpers import marcar_todas_lidas
                    marcar_todas_lidas()
                    st.rerun()

    if SUPABASE_OK:
        m=get_metricas_dashboard()
        recentes=get_faturas_recentes(8)
        despesa=get_despesa_por_projeto()
        n_pre,tp=m["pre_aprovacao_count"],m["pre_aprovacao_total"]
        n_apr,ta=m["aprovado_count"],m["aprovado_total"]
        n_pago,tpago=m["pago_mes_count"],m["pago_mes_total"]
        n_venc,tv=m["vencido_count"],m["vencido_total"]
    else:
        n_pre=len(st.session_state.mock_pre); tp=sum(f["valor"] for f in st.session_state.mock_pre)
        n_venc=len(st.session_state.mock_venc); tv=sum(f["valor"] for f in st.session_state.mock_venc)
        n_apr=len(st.session_state.mock_av); ta=sum(f["valor"] for f in st.session_state.mock_av)
        n_pago,tpago=23,121400
        recentes=_MOCK_AV[:5]
        despesa=[{"projeto":k,"valor":v} for k,v in {"MENTORES":52400,"ANIET":38900,"APCMC":27600,"APIMA":19200,"PRODUTECH":61200,"CALÇADO":14600}.items()]

    # Banner notificações não lidas
    n_novas = n_notifs_nao_lidas()
    if n_novas > 0:
        st.html(
            f'<div class="fin-warn" style="cursor:pointer">'
            f'🔔 <strong>{n_novas} notificação(ões) não lida(s)</strong> — '
            f'nova(s) fatura(s) submetida(s). Ver em <strong>Notificações</strong>.'
            f'</div>'
        )

    if n_pre>0:
        st.html(f'<div class="fin-warn">⚠️ <strong>{n_pre} fatura(s) aguardam aprovação manual</strong> — ver em <strong>Alertas/A Pagar</strong>.</div>')

    st.html(
        '<div class="fin-kpi-row">'
        +kpi_h("🔍 Pré-aprovação",   eur(tp),    f"{n_pre} faturas","a")
        +kpi_h("✅ Aprovado a pagar",eur(ta),    f"{n_apr} faturas","g")
        +kpi_h("💳 Pago este mês",   eur(tpago), f"{n_pago} faturas","b")
        +kpi_h("🚨 Vencido",         eur(tv),    f"{n_venc} faturas","r")
        +'</div>'
    )

    st.html(div())

    col_l,col_r=st.columns([3,2])
    with col_l:
        st.markdown(sec("Faturas recentes"),unsafe_allow_html=True)
        cards_html=""
        for row in recentes:
            f=_formador(row); p=_projeto(row); e=row.get("estado") or "submetida"
            n=row.get("numero_fatura") or "—"; v=row.get("valor") or 0
            cards_html+=(f'<div class="fin-card"><div style="flex:1"><div class="ct">{n}</div>'
                        f'<div class="cm">{ptag(p)}&nbsp;·&nbsp;{f}</div></div>'
                        f'<div style="text-align:right;margin-right:10px"><div class="cv">{eur(v)}</div></div>'
                        f'{bdg(e)}</div>')
        st.markdown(cards_html,unsafe_allow_html=True)
    with col_r:
        st.markdown(sec("Por estado"),unsafe_allow_html=True)
        fig=go.Figure(go.Pie(
            labels=["Pré-aprovação","Aprovado","Pago","Vencido"],
            values=[n_pre or 1,n_apr or 1,n_pago or 1,n_venc or 1],
            hole=0.65,marker_colors=["#D97706","#16A34A","#2563EB","#DC2626"],
            textinfo="percent",textfont=dict(size=11),showlegend=True,
        ))
        fig.update_layout(margin=dict(t=10,b=10,l=0,r=10),height=270,
            legend=dict(orientation="v",x=1.0,y=0.5,font=dict(size=11),xanchor="left",yanchor="middle"),
            paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig,use_container_width=True,config=PLOTLY_CFG)

    st.html(div())
    st.markdown(sec("Despesa por projeto"),unsafe_allow_html=True)
    ds=sorted(despesa,key=lambda x:x["valor"])
    mx=max((d["valor"] for d in ds),default=1)
    fig2=go.Figure(go.Bar(x=[d["valor"] for d in ds],y=[d["projeto"] for d in ds],orientation="h",
        marker_color=[CORES.get(d["projeto"],"#888") for d in ds],
        text=[eur(d["valor"]) for d in ds],textposition="outside",textfont=dict(size=12)))
    fig2.update_layout(margin=dict(t=4,b=4,l=4,r=110),height=270,
        xaxis=dict(showticklabels=False,showgrid=False,range=[0,mx*1.3]),
        yaxis=dict(showgrid=False,tickfont=dict(size=13)),
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig2,use_container_width=True,config=PLOTLY_CFG)

    st.html(div())
    st.markdown(sec("⬇️ Exportação global"), unsafe_allow_html=True)
    col_e1, col_e2, col_e3 = st.columns(3)
    with col_e1:
        if st.button("📊 Exportar todas as faturas", use_container_width=True, key="exp_fat"):
            st.toast("Exportação disponível quando a BD estiver ligada.")
    with col_e2:
        if st.button("🤝 Exportar consultores", use_container_width=True, key="exp_cons"):
            st.toast("Exportação disponível quando a BD estiver ligada.")
    with col_e3:
        if st.button("🏢 Exportar faturação empresas", use_container_width=True, key="exp_emp"):
            st.toast("Exportação disponível quando a BD estiver ligada.")
