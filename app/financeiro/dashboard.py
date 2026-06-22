"""Tab Dashboard — página do financeiro."""
from __future__ import annotations
import streamlit as st
import plotly.graph_objects as go
from app.financeiro.helpers import (
    ptag, bdg, sec, div, CORES, PLOTLY_CFG,
    _formador, _projeto, n_notifs_nao_lidas, marcar_todas_lidas,
)

try:
    from app.db_financeiro import (
        get_metricas_dashboard, get_faturas_recentes,
        get_despesa_por_projeto, get_supabase,
    )
    get_supabase()
    SUPABASE_OK = True
except Exception:
    SUPABASE_OK = False

_MOCK_AV = [
    {"id":"a1","numero_fatura":"FT2026/0142","valor":3200,"profiles":{"nome":"João Silva"},"acoes":{"nome":"MENTORES"},"estado":"aprovada"},
    {"id":"a2","numero_fatura":"FT2026/0138","valor":2800,"profiles":{"nome":"Ana Ferreira"},"acoes":{"nome":"ANIET"},"estado":"submetida"},
    {"id":"a3","numero_fatura":"FT2026/0136","valor":1900,"profiles":{"nome":"Pedro Costa"},"acoes":{"nome":"CALÇADO"},"estado":"aprovada"},
    {"id":"a4","numero_fatura":"FT2026/0129","valor":2100,"profiles":{"nome":"Carla Neves"},"acoes":{"nome":"APCMC"},"estado":"submetida"},
    {"id":"a5","numero_fatura":"FT2026/0127","valor":2300,"profiles":{"nome":"Rui Mendes"},"acoes":{"nome":"APIMA"},"estado":"aprovada"},
]

_MOCK_PERIODOS = {
    "Tudo":         {"n_pre":3,"tp":6150,"n_apr":5,"ta":12300,"n_pago":23,"tpago":23150,"n_venc":1,"tv":3321.34},
    "Este mês":     {"n_pre":2,"tp":4350,"n_apr":3,"ta":7200, "n_pago":8, "tpago":9200, "n_venc":1,"tv":3321.34},
    "Mês anterior": {"n_pre":1,"tp":1800,"n_apr":2,"ta":5100, "n_pago":15,"tpago":13950,"n_venc":0,"tv":0},
    "Este ano":     {"n_pre":3,"tp":6150,"n_apr":5,"ta":12300,"n_pago":23,"tpago":23150,"n_venc":1,"tv":3321.34},
}

def _e(v):
    try: return f"{float(v):,.2f} €".replace(",","X").replace(".",",").replace("X",".")
    except: return "— €"

def _kpi(icon, label, value, sub, cor):
    cores = {"g":"#16A34A","r":"#DC2626","a":"#D97706","b":"#2563EB","p":"#7C3AED"}
    c = cores.get(cor, "#6B7280")
    return (
        f'<div style="background:#fff;border:1px solid #E4E7EF;border-radius:12px;'
        f'padding:18px 20px;flex:1;min-width:140px;border-top:3px solid {c}">'
        f'<div style="font-size:11px;font-weight:600;color:#8B94A3;text-transform:uppercase;'
        f'letter-spacing:.07em;margin-bottom:6px">{icon} {label}</div>'
        f'<div style="font-size:24px;font-weight:700;color:#1A1F2E;line-height:1">{value}</div>'
        f'<div style="font-size:12px;color:#8B94A3;margin-top:5px">{sub}</div>'
        f'</div>'
    )

def render_dashboard(user):
    # ── Filtro período ──
    col_f, col_info = st.columns([2, 4])
    with col_f:
        periodo = st.selectbox("Período", list(_MOCK_PERIODOS.keys()), key="dash_periodo")
    with col_info:
        st.html('<div style="padding-top:28px;font-size:12px;color:#8B94A3">Dados em Modo de Demonstração</div>')

    # ── Notificações ──
    notifs = st.session_state.get("notificacoes", [])
    novas  = [n for n in notifs if not n.get("lida")]
    if novas:
        n_txt = "🔔 1 Notificação Não Lida" if len(novas)==1 else f"🔔 {len(novas)} Notificações Não Lidas"
        with st.expander(n_txt, expanded=True):
            for n in novas[:5]:
                ico = "📄" if n.get("tipo")=="fatura_formador" else "🤝"
                st.html(
                    f'<div style="display:flex;gap:10px;padding:9px 0;border-bottom:1px solid #F0F2F5">'
                    f'<div style="width:7px;height:7px;border-radius:50%;background:#D97706;flex-shrink:0;margin-top:5px"></div>'
                    f'<div><div style="font-size:13px;font-weight:600;color:#1A1F2E">{ico} {n["titulo"]}</div>'
                    f'<div style="font-size:12px;color:#4B5263;margin-top:1px">{n["texto"]}</div>'
                    f'<div style="font-size:11px;color:#8B94A3;margin-top:1px">{n["timestamp"]}</div></div>'
                    f'</div>'
                )
            col_b, _ = st.columns([2,4])
            with col_b:
                if st.button("✓ Marcar todas como lidas", key="dash_notif_lidas"):
                    marcar_todas_lidas(); st.rerun()

    # ── Dados ──
    if SUPABASE_OK:
        m = get_metricas_dashboard()
        recentes = get_faturas_recentes(6)
        despesa  = get_despesa_por_projeto()
        n_pre,tp    = m["pre_aprovacao_count"], m["pre_aprovacao_total"]
        n_apr,ta    = m["aprovado_count"],       m["aprovado_total"]
        n_pago,tpago= m["pago_mes_count"],       m["pago_mes_total"]
        n_venc,tv   = m["vencido_count"],        m["vencido_total"]
    else:
        p = _MOCK_PERIODOS[periodo]
        n_pre,tp     = p["n_pre"], p["tp"]
        n_apr,ta     = p["n_apr"], p["ta"]
        n_pago,tpago = p["n_pago"],p["tpago"]
        n_venc,tv    = p["n_venc"],p["tv"]
        recentes = _MOCK_AV[:5]
        despesa  = [{"projeto":k,"valor":v} for k,v in {
            "MENTORES":52400,"ANIET":38900,"APIMA":27600,
            "PRODUTECH":9200,"APCMC":61200,"CALÇADO":4600}.items()]

    if n_pre > 0:
        st.html(f'<div style="background:#FFFBEB;border:1px solid #FCD34D;border-left:3px solid #D97706;border-radius:8px;padding:9px 14px;font-size:13px;color:#92400E;margin:8px 0 4px">⚠️ <strong>{n_pre} Fatura(s) Aguardam Aprovação Manual</strong> — Ver em <strong>🧾 Faturas</strong></div>')

    # ── KPIs ──
    kpi_pago = {"Este mês":"Pago este mês","Mês anterior":"Pago mês anterior",
                "Este ano":"Pago este ano","Tudo":"Total pago"}.get(periodo,"Pago no período")

    st.html(
        '<div style="display:flex;gap:12px;flex-wrap:wrap;margin:16px 0 20px">'
        + _kpi("🔍","Pré-aprovação", _e(tp),    f"{n_pre} faturas",  "a")
        + _kpi("✅","Aprovado a Pagar",_e(ta),   f"{n_apr} faturas",  "g")
        + _kpi("💳", kpi_pago,        _e(tpago), f"{n_pago} faturas", "b")
        + _kpi("🚨","Vencido",        _e(tv),    f"{n_venc} faturas", "r")
        + '</div>'
    )

    st.html(div())

    # ── Faturas recentes + Gráfico ──
    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.html(f'<p style="font-size:13px;font-weight:700;color:#4B5263;text-transform:uppercase;letter-spacing:.06em;margin-bottom:12px">Faturas recentes</p>')
        for row in recentes:
            f = _formador(row); p = _projeto(row)
            e = row.get("estado") or "submetida"
            n = row.get("numero_fatura") or "—"
            v = row.get("valor") or 0
            st.html(
                f'<div style="background:#fff;border:1px solid #E4E7EF;border-radius:10px;'
                f'padding:11px 14px;margin-bottom:7px;display:flex;align-items:center;gap:10px">'
                f'<div style="flex:1">'
                f'<div style="font-weight:600;font-size:13px;color:#1A1F2E">{n}</div>'
                f'<div style="font-size:12px;color:#8B94A3;margin-top:2px">{ptag(p)}&nbsp;·&nbsp;{f}</div>'
                f'</div>'
                f'<div style="text-align:right">'
                f'<div style="font-weight:700;font-size:14px;color:#1A1F2E">{_e(v)}</div>'
                f'<div style="margin-top:3px">{bdg(e)}</div>'
                f'</div>'
                f'</div>'
            )

    with col_r:
        st.html('<p style="font-size:13px;font-weight:700;color:#4B5263;text-transform:uppercase;letter-spacing:.06em;margin-bottom:12px">Distribuição por estado</p>')
        fig = go.Figure(go.Pie(
            labels=["Pré-aprovação","Aprovado","Pago","Vencido"],
            values=[n_pre or 1, n_apr or 1, n_pago or 1, n_venc or 1],
            hole=0.6,
            marker_colors=["#D97706","#16A34A","#2563EB","#DC2626"],
            textinfo="percent+label", textfont=dict(size=10),
            showlegend=False,
        ))
        fig.update_layout(
            margin=dict(t=10,b=10,l=10,r=10), height=240,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CFG)

    st.html(div())

    # ── Despesa por projeto ──
    st.html('<p style="font-size:13px;font-weight:700;color:#4B5263;text-transform:uppercase;letter-spacing:.06em;margin-bottom:12px">Despesa por projeto</p>')
    ds = sorted(despesa, key=lambda x: x["valor"])
    mx = max((d["valor"] for d in ds), default=1)
    fig2 = go.Figure(go.Bar(
        x=[d["valor"] for d in ds], y=[d["projeto"] for d in ds],
        orientation="h",
        marker_color=[CORES.get(d["projeto"],"#888") for d in ds],
        text=[_e(d["valor"]) for d in ds],
        textposition="outside", textfont=dict(size=11),
    ))
    fig2.update_layout(
        margin=dict(t=4,b=4,l=4,r=120), height=260,
        xaxis=dict(showticklabels=False, showgrid=False, range=[0,mx*1.35]),
        yaxis=dict(showgrid=False, tickfont=dict(size=12)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig2, use_container_width=True, config=PLOTLY_CFG)

    st.html(div())

    # ── Exportação ──
    st.html('<p style="font-size:13px;font-weight:700;color:#4B5263;text-transform:uppercase;letter-spacing:.06em;margin-bottom:12px">Exportação de dados</p>')
    c1,c2,c3 = st.columns(3)
    with c1:
        if st.button("📊 Exportar Faturas", use_container_width=True, key="exp_fat"):
            st.toast("Disponível quando a BD estiver ligada.")
    with c2:
        if st.button("🤝 Exportar Consultores", use_container_width=True, key="exp_cons"):
            st.toast("Disponível quando a BD estiver ligada.")
    with c3:
        if st.button("🏢 Exportar Faturação Empresas", use_container_width=True, key="exp_emp"):
            st.toast("Disponível quando a BD estiver ligada.")
