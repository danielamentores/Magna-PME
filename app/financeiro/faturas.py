"""Tab Faturas — página do financeiro."""
from __future__ import annotations
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from app.financeiro.helpers import (
    eur, ptag, bdg, CORES, ordenar, fil_proj, fil_datas,
    excel_bytes, extrair_pdf, guardar_comprovativo,
    notificar_rejeicao, reg_hist,
    _formador, _projeto, _email, ORDEM, PLOTLY_CFG,
)

try:
    from app.db_financeiro import get_supabase; get_supabase()
    SUPABASE_OK = True
except Exception:
    SUPABASE_OK = False

try:
    from app.db_financeiro import (
        get_faturas_pre_aprovacao, get_faturas_vencidas, get_faturas_a_vencer,
        get_top_formadores_pendentes, get_pendente_por_projeto,
        get_cashflow_previsto, get_projetos, get_historico_financeiro,
        aprovar_fatura, rejeitar_fatura, marcar_paga,
    )
except Exception:
    pass

def _e(v):
    try: return f"{float(v):,.2f} €".replace(",","X").replace(".",",").replace("X",".")
    except: return "— €"

def _sec(title, sub=""):
    s = f'<p style="font-size:12px;color:#8B94A3;margin:0 0 12px">{sub}</p>' if sub else ""
    return f'<p style="font-size:13px;font-weight:700;color:#4B5263;text-transform:uppercase;letter-spacing:.06em;margin:0 0 3px">{title}</p>{s}'

def _div():
    return '<div style="height:1px;background:#E4E7EF;margin:20px 0 18px"></div>'

def _kpi(icon, label, value, sub, cor):
    cores = {"g":"#16A34A","r":"#DC2626","a":"#D97706","b":"#2563EB","p":"#7C3AED"}
    c = cores.get(cor, "#6B7280")
    return (
        f'<div style="background:#fff;border:1px solid #E4E7EF;border-radius:12px;'
        f'padding:16px 18px;flex:1;min-width:130px;border-top:3px solid {c}">'
        f'<div style="font-size:11px;font-weight:600;color:#8B94A3;text-transform:uppercase;'
        f'letter-spacing:.07em;margin-bottom:5px">{icon} {label}</div>'
        f'<div style="font-size:22px;font-weight:700;color:#1A1F2E;line-height:1">{value}</div>'
        f'<div style="font-size:12px;color:#8B94A3;margin-top:4px">{sub}</div>'
        f'</div>'
    )

def _empty(msg="Sem resultados para este filtro."):
    return f'<div style="background:#F7F8FC;border:1px dashed #E4E7EF;border-radius:10px;padding:20px;text-align:center;color:#8B94A3;font-size:13px">{msg}</div>'

# ── Mock data ────────────────────────────────────────────────────────────────
_MOCK_PROJETOS = [
    {"id":"p1","nome":"MENTORES"},{"id":"p2","nome":"ANIET"},
    {"id":"p3","nome":"APCMC"},   {"id":"p4","nome":"APIMA"},
    {"id":"p5","nome":"PRODUTECH"},{"id":"p6","nome":"CALÇADO"},
]
_MOCK_PRE = [
    {"id":"f1","numero_fatura":"FT2026/0155","valor":2400,"estado":"leitura_falhada","erro_leitura":"Código interno não encontrado","created_at":"2026-06-15","ficheiro_url":None,"profiles":{"nome":"Formador 1","email":"f1@demo.pt"},"acoes":{"nome":"MENTORES"}},
    {"id":"f2","numero_fatura":"FT2026/0153","valor":1950,"estado":"acao_nao_fechada","erro_leitura":"Nome do formador não corresponde","created_at":"2026-06-14","ficheiro_url":None,"profiles":{"nome":"Formador 2","email":"f2@demo.pt"},"acoes":{"nome":"ANIET"}},
    {"id":"f3","numero_fatura":"FT2026/0150","valor":1800,"estado":"submetida","erro_leitura":"Valor diverge do contrato","created_at":"2026-06-13","ficheiro_url":None,"profiles":{"nome":"Formador 3","email":"f3@demo.pt"},"acoes":{"nome":"PRODUTECH"}},
]
_MOCK_VENC = [
    {"id":"v1","numero_fatura":"FT40","valor":3321.34,"prazo_pagamento":"2026-06-08","data_fatura":"2026-05-08","atraso":8,"profiles":{"nome":"Consultor 2","email":"c2@demo.pt"},"acoes":{"nome":"PRODUTECH"}},
]
_MOCK_AV = [
    {"id":"a1","numero_fatura":"FT2026/0142","valor":3200,"prazo_pagamento":"2026-06-21","data_fatura":"2026-06-01","dias":5, "profiles":{"nome":"Formador 1","email":"f1@demo.pt"},"acoes":{"nome":"MENTORES"}},
    {"id":"a2","numero_fatura":"FT2026/0138","valor":2800,"prazo_pagamento":"2026-06-27","data_fatura":"2026-06-03","dias":11,"profiles":{"nome":"Formador 4","email":"f4@demo.pt"},"acoes":{"nome":"ANIET"}},
    {"id":"a3","numero_fatura":"FT2026/0136","valor":1900,"prazo_pagamento":"2026-07-04","data_fatura":"2026-06-05","dias":18,"profiles":{"nome":"Formador 5","email":"f5@demo.pt"},"acoes":{"nome":"CALÇADO"}},
    {"id":"a4","numero_fatura":"FT2026/0129","valor":2100,"prazo_pagamento":"2026-07-10","data_fatura":"2026-06-06","dias":24,"profiles":{"nome":"Formador 2","email":"f2@demo.pt"},"acoes":{"nome":"APCMC"}},
    {"id":"a5","numero_fatura":"FT2026/0127","valor":2300,"prazo_pagamento":"2026-07-16","data_fatura":"2026-06-08","dias":30,"profiles":{"nome":"Consultor 1","email":"c1@demo.pt"},"acoes":{"nome":"APIMA"}},
]
_MOCK_CF_L = ["S1 Jun","S2 Jun","S3 Jun","S4 Jun","S1 Jul","S2 Jul","S3 Jul","S4 Jul","S1 Ago","S2 Ago","S3 Ago","S4 Ago","S1 Set"]
_MOCK_CF_S = [3200,2100,4100,2800,2600,3800,1900,3200,2400,2800,1800,2100,2300]

# ── Card de fatura (vencida / a vencer) ──────────────────────────────────────
def _card(row, tipo, idx, user_nome):
    fid = row.get("id") or str(idx)
    n   = row.get("numero_fatura") or "—"
    f   = _formador(row); p = _projeto(row); v = row.get("valor") or 0
    df  = row.get("data_fatura") or "—"; dp = row.get("prazo_pagamento") or "—"

    if tipo == "vencida":
        dias_txt = f'+{row.get("atraso") or 0} dias em atraso'
        borda = "#DC2626"; bg_extra = "background:#FEF2F2;"
        dias_cor = "#DC2626"
    else:
        dias_txt = f'vence em {row.get("dias") or 0} dias'
        borda = "#D97706"; bg_extra = ""
        dias_cor = "#D97706"

    col_c, col_b = st.columns([6, 2])
    with col_c:
        st.html(
            f'<div style="background:#fff;border:1px solid #E4E7EF;border-left:4px solid {borda};'
            f'border-radius:10px;padding:16px 20px;{bg_extra}display:flex;align-items:center;gap:12px">'
            f'<div style="flex:1">'
            f'<div style="font-weight:700;font-size:16px;color:#1A1F2E;margin-bottom:4px">{n}'
            f'&nbsp;&nbsp;<span style="font-size:13px;font-weight:400;color:#6B7280">{f}</span></div>'
            f'<div style="margin-bottom:4px">{ptag(p)}</div>'
            f'<div style="font-size:13px;color:#8B94A3">Emissão: {df} &nbsp;·&nbsp; Prazo: <strong style="color:#4B5263">{dp}</strong></div>'
            f'</div>'
            f'<div style="text-align:right;flex-shrink:0;padding-left:12px">'
            f'<div style="font-weight:700;font-size:18px;color:#1A1F2E">{_e(v)}</div>'
            f'<div style="font-size:13px;color:{dias_cor};margin-top:4px;font-weight:500">{dias_txt}</div>'
            f'</div>'
            f'</div>'
        )
    with col_b:
        show_key = f"show_comp_{tipo}_{idx}_{fid}"
        if not st.session_state.get(show_key):
            if st.button("✓ Marcar pago", key=f"pg_{tipo}_{idx}_{fid}",
                         use_container_width=True, type="primary"):
                st.session_state[show_key] = True; st.rerun()
        else:
            comp = st.file_uploader("📎 Comprovativo (PDF)", type=["pdf"],
                                    key=f"comp_{tipo}_{idx}_{fid}")
            col_ok, col_x = st.columns([3, 1])
            with col_ok:
                if st.button("✅ Confirmar", key=f"conf_{tipo}_{idx}_{fid}",
                             use_container_width=True, type="primary", disabled=comp is None):
                    guardar_comprovativo(fid, comp.getvalue(), comp.name, user_nome)
                    if SUPABASE_OK:
                        if marcar_paga(fid, user_nome):
                            reg_hist("Marcado pago", n, f, p, v)
                            st.session_state.pop(show_key, None)
                            st.toast(f"{n} paga. Comprovativo guardado."); st.rerun()
                    else:
                        lst_key = "mock_venc" if tipo == "vencida" else "mock_av"
                        st.session_state[lst_key] = [x for x in st.session_state[lst_key] if x.get("id") != fid]
                        reg_hist("Marcado pago", n, f, p, v)
                        st.session_state.pop(show_key, None)
                        st.toast(f"{n} paga."); st.rerun()
            with col_x:
                if st.button("✖", key=f"canc_{tipo}_{idx}_{fid}", use_container_width=True):
                    st.session_state.pop(show_key, None); st.rerun()

# ── Render principal ─────────────────────────────────────────────────────────
def render_alertas(user):
    user_nome = user.get("nome") or "Financeiro"

    # Filtros
    col_f, col_c, col_o, col_d1, col_d2 = st.columns([2,2,2,1,1])
    with col_f:
        pjs = get_projetos() if SUPABASE_OK else _MOCK_PROJETOS
        filtro = st.selectbox("Projeto", ["Todos"]+[p["nome"] for p in pjs], key="fil_p")
    with col_c:
        try:
            from app.financeiro.consultores import _get_cons
            cons_lista = _get_cons()
        except: cons_lista = []
        filtro_cons = st.selectbox("Consultor/Formador", ["Todos"]+[c["nome"] for c in cons_lista], key="fil_cons_al")
    with col_o:
        ordem = st.selectbox("Ordenar", ORDEM, key="ord_f")
    with col_d1:
        d_ini = st.date_input("De", value=None, key="d_i", format="DD/MM/YYYY")
    with col_d2:
        d_fim = st.date_input("Até", value=None, key="d_f", format="DD/MM/YYYY")

    def fil_cons_fn(dados):
        if filtro_cons == "Todos": return dados
        return [d for d in dados if filtro_cons in (_formador(d) or "")]

    if SUPABASE_OK:
        pre  = get_faturas_pre_aprovacao(filtro if filtro != "Todos" else None)
        venc = fil_datas(fil_cons_fn(fil_proj(get_faturas_vencidas(), filtro)), d_ini, d_fim)
        av   = fil_datas(fil_cons_fn(fil_proj(get_faturas_a_vencer(), filtro)), d_ini, d_fim)
        top5 = get_top_formadores_pendentes()
        pp   = get_pendente_por_projeto()
        cfl, cfs = get_cashflow_previsto()
        hist_bd  = get_historico_financeiro()
    else:
        pre  = fil_proj(st.session_state.mock_pre, filtro)
        venc = fil_datas(fil_cons_fn(fil_proj(st.session_state.mock_venc, filtro)), d_ini, d_fim)
        av   = fil_datas(fil_cons_fn(fil_proj(st.session_state.mock_av, filtro)), d_ini, d_fim)
        top5 = [{"formador":"Formador 1","valor":5000},{"formador":"Consultor 1","valor":4900},
                {"formador":"Formador 3","valor":3300},{"formador":"Formador 4","valor":2800},
                {"formador":"Formador 5","valor":2100}]
        pp   = [{"projeto":"MENTORES","valor":5000},{"projeto":"PRODUTECH","valor":4400},
                {"projeto":"CALÇADO","valor":3300},{"projeto":"ANIET","valor":2800},
                {"projeto":"APIMA","valor":2300},{"projeto":"APCMC","valor":2100}]
        cfl, cfs = _MOCK_CF_L, _MOCK_CF_S
        hist_bd  = []

    venc = ordenar(venc, ordem); av = ordenar(av, ordem)
    tv   = sum(f.get("valor") or 0 for f in venc)
    ta   = sum(f.get("valor") or 0 for f in av)

    # KPIs
    st.html(
        '<div style="display:flex;gap:12px;flex-wrap:wrap;margin:16px 0 20px">'
        + _kpi("🚨","Vencido",        _e(tv),    f"{len(venc)} fatura(s)", "r")
        + _kpi("⏳","A vencer 30 dias",_e(ta),   f"{len(av)} fatura(s)",   "a")
        + _kpi("💳","Pago este mês",   _e(23150), "23 faturas",             "b")
        + _kpi("💰","Total pendente",  _e(tv+ta), f"{len(venc)+len(av)} fatura(s)", "p")
        + '</div>'
    )

    st.html(_div())

    # ── Aprovação manual ──
    st.html(_sec(f"🔍 Aprovação Manual — {len(pre)} pendente(s)", "Faturas cuja validação automática falhou. Analisa e aprova ou rejeita."))
    if not pre:
        st.html(_empty("✅ Nenhuma fatura pendente de aprovação manual."))
    else:
        for i, row in enumerate(pre):
            fid = row.get("id") or str(i)
            n   = row.get("numero_fatura") or "—"
            f   = _formador(row); em = _email(row); p = _projeto(row)
            v   = row.get("valor") or 0
            erro = row.get("erro_leitura") or row.get("notas") or "—"
            ds   = str(row.get("created_at") or "—")[:10]
            fich = row.get("ficheiro_url")

            col_i, col_a = st.columns([5, 3])
            with col_i:
                pdf_link = f'&nbsp;<a href="{fich}" target="_blank" style="font-size:12px;color:#2A7A8C;font-weight:500">📄 Ver PDF</a>' if fich else ""
                st.html(
                    f'<div style="background:#fff;border:1px solid #E4E7EF;border-radius:10px;padding:14px 16px;margin-bottom:4px">'
                    f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">'
                    f'<span style="font-weight:700;font-size:14px;color:#1A1F2E">{n}</span>{ptag(p)}{pdf_link}'
                    f'</div>'
                    f'<div style="font-size:13px;color:#4B5263"><b>Formador:</b> {f} &nbsp;·&nbsp; <b>Valor:</b> {_e(v)}</div>'
                    f'<div style="font-size:12px;color:#DC2626;margin-top:4px;padding:5px 8px;background:#FEF2F2;border-radius:5px">⚠️ {erro}</div>'
                    f'<div style="font-size:11px;color:#8B94A3;margin-top:4px">Submetida: {ds}</div>'
                    f'</div>'
                )
            with col_a:
                st.markdown("<div style='margin-top:4px'>", unsafe_allow_html=True)
                if st.button("✅ Aprovar", key=f"ap_{i}_{fid}", use_container_width=True, type="primary"):
                    if SUPABASE_OK:
                        if aprovar_fatura(fid, user_nome):
                            reg_hist("Aprovado",n,f,p,v); st.toast(f"{n} aprovada."); st.rerun()
                    else:
                        st.session_state.mock_pre = [x for x in st.session_state.mock_pre if x.get("id")!=fid]
                        reg_hist("Aprovado",n,f,p,v); st.toast(f"{n} aprovada."); st.rerun()
                mot = st.text_input("", key=f"mt_{i}_{fid}", placeholder="Motivo de rejeição…", label_visibility="collapsed")
                if st.button("❌ Rejeitar", key=f"rj_{i}_{fid}", use_container_width=True):
                    if mot:
                        if SUPABASE_OK:
                            if rejeitar_fatura(fid, mot, user_nome):
                                reg_hist("Rejeitado",n,f,p,v,mot); notificar_rejeicao(em,n,mot); st.toast(f"{n} rejeitada."); st.rerun()
                        else:
                            st.session_state.mock_pre = [x for x in st.session_state.mock_pre if x.get("id")!=fid]
                            reg_hist("Rejeitado",n,f,p,v,mot); notificar_rejeicao(em,n,mot); st.toast(f"{n} rejeitada."); st.rerun()
                    else:
                        st.warning("Escreve um motivo de rejeição.")
                st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("🔎 Leitura Manual de Fatura PDF", expanded=False):
        st.html('<div style="font-size:13px;color:#6B7280;margin-bottom:12px">Carrega um PDF para extrair automaticamente os dados da fatura.</div>')
        up = st.file_uploader("Seleciona o PDF", type=["pdf"], key="pdf_up", label_visibility="collapsed")
        if up:
            with st.spinner("A ler o PDF..."):
                d = extrair_pdf(up.read())
            if d.get("erro"):
                st.error(f"Erro na leitura: {d['erro']}")
            else:
                st.html('<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:8px">' +
                    f'<div style="background:#F7F8FC;border-radius:8px;padding:12px 14px"><div style="font-size:11px;color:#8B94A3;font-weight:600;text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px">Nº Fatura</div><div style="font-size:15px;font-weight:700;color:#1A1F2E">{d.get("numero_fatura") or "—"}</div></div>' +
                    f'<div style="background:#F7F8FC;border-radius:8px;padding:12px 14px"><div style="font-size:11px;color:#8B94A3;font-weight:600;text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px">NIF Emitente</div><div style="font-size:15px;font-weight:700;color:#1A1F2E">{d.get("nif_emitente") or "—"}</div></div>' +
                    f'<div style="background:#F7F8FC;border-radius:8px;padding:12px 14px"><div style="font-size:11px;color:#8B94A3;font-weight:600;text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px">Valor</div><div style="font-size:15px;font-weight:700;color:#1A1F2E">{_e(d.get("valor") or 0)}</div></div>' +
                    f'<div style="background:#F7F8FC;border-radius:8px;padding:12px 14px"><div style="font-size:11px;color:#8B94A3;font-weight:600;text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px">Data</div><div style="font-size:15px;font-weight:700;color:#1A1F2E">{d.get("data_fatura") or "—"}</div></div>' +
                    '</div>')

    st.html(_div())

    # ── Faturas vencidas ──
    st.html(_sec("🔴 Faturas vencidas", f"{len(venc)} Fatura(s) com prazo ultrapassado"))
    PAGE = 10; pv = st.session_state.get("pag_v", 0)
    pagv = venc[pv*PAGE:(pv+1)*PAGE]
    if not venc:
        st.html(_empty("Nenhuma fatura vencida para este filtro."))
    else:
        for i, row in enumerate(pagv): _card(row, "vencida", pv*PAGE+i, user_nome)
        st.html(f'<div style="font-size:13px;font-weight:600;color:#DC2626;margin:8px 0">Total vencido: {_e(tv)}</div>')
        tp_ = max(1, (len(venc)+PAGE-1)//PAGE)
        if tp_ > 1:
            c1,c2,c3 = st.columns([1,2,1])
            if c1.button("← Anterior", key="pv_p", disabled=pv==0): st.session_state.pag_v=pv-1; st.rerun()
            c2.markdown(f"<div style='text-align:center;padding-top:8px;font-size:13px'>Página {pv+1} de {tp_}</div>", unsafe_allow_html=True)
            if c3.button("Próxima →", key="pv_n", disabled=pv>=tp_-1): st.session_state.pag_v=pv+1; st.rerun()
        st.download_button("⬇️ Exportar Excel", excel_bytes(venc), f"vencidas_{filtro}.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_v")

    st.html(_div())

    # ── A vencer ──
    st.html(_sec("🟡 A vencer — próximos 30 dias", f"{len(av)} Fatura(s) a vencer em breve"))
    pa = st.session_state.get("pag_a", 0)
    paga = av[pa*PAGE:(pa+1)*PAGE]
    if not av:
        st.html(_empty("Nenhuma fatura a vencer para este filtro."))
    else:
        for i, row in enumerate(paga): _card(row, "avencer", pa*PAGE+i, user_nome)
        st.html(f'<div style="font-size:13px;font-weight:600;color:#D97706;margin:8px 0">Total a vencer: {_e(ta)}</div>')
        tp_ = max(1, (len(av)+PAGE-1)//PAGE)
        if tp_ > 1:
            c1,c2,c3 = st.columns([1,2,1])
            if c1.button("← Anterior", key="pa_p", disabled=pa==0): st.session_state.pag_a=pa-1; st.rerun()
            c2.markdown(f"<div style='text-align:center;padding-top:8px;font-size:13px'>Página {pa+1} de {tp_}</div>", unsafe_allow_html=True)
            if c3.button("Próxima →", key="pa_n", disabled=pa>=tp_-1): st.session_state.pag_a=pa+1; st.rerun()
        st.download_button("⬇️ Exportar Excel", excel_bytes(av), f"avencer_{filtro}.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_a")

    st.html(_div())

    # ── Top 5 + Por projeto ──
    cl, cr = st.columns(2)
    with cl:
        st.html(_sec("🏆 Top 5 — Pendente por formador"))
        for i, row in enumerate(top5):
            st.html(
                f'<div style="background:#fff;border:1px solid #E4E7EF;border-radius:9px;'
                f'padding:10px 14px;margin-bottom:6px;display:flex;align-items:center;gap:10px">'
                f'<span style="font-size:12px;font-weight:700;color:#8B94A3;min-width:22px">#{i+1}</span>'
                f'<span style="flex:1;font-size:13px;color:#1A1F2E">{row["formador"]}</span>'
                f'<span style="font-weight:700;font-size:14px;color:#1A1F2E">{_e(row["valor"])}</span>'
                f'</div>'
            )
    with cr:
        st.html(_sec("📊 Pendente por projeto"))
        for row in pp:
            c = CORES.get(row["projeto"], "#888")
            st.html(
                f'<div style="background:#fff;border:1px solid #E4E7EF;border-radius:9px;'
                f'padding:10px 14px;margin-bottom:6px;display:flex;align-items:center;gap:10px">'
                f'<span style="width:8px;height:8px;border-radius:50%;background:{c};flex-shrink:0"></span>'
                f'<span style="flex:1;font-size:13px;color:#1A1F2E">{row["projeto"]}</span>'
                f'<span style="font-weight:700;font-size:14px;color:#1A1F2E">{_e(row["valor"])}</span>'
                f'</div>'
            )

    st.html(_div())

    # ── Cashflow ──
    st.html(_sec("📈 Cashflow previsto — próximos 90 dias", "Saídas semanais estimadas e acumulado"))
    if cfs:
        acum, tot = [], 0
        for v in cfs: tot += v; acum.append(tot)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=cfl, y=cfs, name="Saída semanal", marker_color="#FBBF24", yaxis="y1"))
        fig.add_trace(go.Scatter(x=cfl, y=acum, name="Acumulado", line=dict(color="#2563EB",width=2),
                                 mode="lines+markers", yaxis="y2"))
        fig.update_layout(
            height=300, margin=dict(t=20,b=60,l=50,r=60),
            legend=dict(orientation="h",yanchor="bottom",y=1.02,font=dict(size=11)),
            yaxis=dict(title="Saída (€)",showgrid=False,tickfont=dict(size=11)),
            yaxis2=dict(title="Acumulado (€)",overlaying="y",side="right",showgrid=False,tickfont=dict(size=11)),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickangle=45,automargin=True,tickfont=dict(size=11)),
        )
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CFG)

    st.html(_div())

    # ── Comprovativos ──
    comps = st.session_state.get("comprovativos", {})
    if comps:
        st.html(_sec(f"📎 Comprovativos guardados ({len(comps)})"))
        for fid, comp in comps.items():
            url    = comp.get("url")
            nome   = comp.get("nome", "—")
            quando = comp.get("guardado_em", "—")
            por    = comp.get("guardado_por", "—")
            link   = f'<a href="{url}" target="_blank" style="color:#2A7A8C;font-size:12px;font-weight:500">📄 Abrir PDF</a>' if url else '<span style="font-size:12px;color:#8B94A3">Guardado localmente</span>'
            st.html(
                f'<div style="background:#fff;border:1px solid #E4E7EF;border-radius:9px;'
                f'padding:11px 14px;margin-bottom:6px;display:flex;align-items:center;gap:10px">'
                f'<div style="flex:1">'
                f'<div style="font-weight:600;font-size:13px;color:#1A1F2E">{nome}</div>'
                f'<div style="font-size:12px;color:#8B94A3;margin-top:2px">Fatura: {fid} · {quando} · por {por}</div>'
                f'</div>{link}</div>'
            )
        st.html(_div())

    # ── Histórico ──
    st.html(_sec("📋 Histórico de ações"))
    hist = st.session_state.historico[::-1]
    if hist:
        df = pd.DataFrame(hist)
        df.columns = ["Data/Hora","Ação","Nº Fatura","Formador","Projeto","Valor","Motivo"]
        df["Valor"] = df["Valor"].apply(_e)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("⬇️ Exportar CSV", df.to_csv(index=False).encode(), "historico.csv", "text/csv")
    elif hist_bd:
        df = pd.DataFrame([{"Data/Hora":str(h.get("criado_em",""))[:16],"Ação":h.get("tipo",""),"Detalhe":h.get("descricao","")} for h in hist_bd])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.html(_empty("Nenhuma ação registada nesta sessão."))
