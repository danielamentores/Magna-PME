"""Tab Faturas — página do financeiro."""
from __future__ import annotations
import streamlit as st
from app.financeiro.helpers import (
    eur, ptag, bdg, kpi_h, sec, div, CORES, BGS,
    ordenar, fil_proj, fil_datas, excel_bytes, extrair_pdf,
    guardar_comprovativo, notificar_rejeicao, reg_hist,
    _formador, _projeto, _email, ORDEM, PLOTLY_CFG,
)

try:
    from app.db_financeiro import get_supabase
    get_supabase()
    SUPABASE_OK = True
except Exception:
    SUPABASE_OK = False

import pandas as pd
from datetime import date

try:
    from app.db_financeiro import (
        get_faturas_pre_aprovacao, get_faturas_vencidas, get_faturas_a_vencer,
        get_top_formadores_pendentes, get_pendente_por_projeto,
        get_cashflow_previsto, get_projetos, get_historico_financeiro,
        aprovar_fatura, rejeitar_fatura, marcar_paga,
    )
except Exception:
    pass

import plotly.graph_objects as go

_MOCK_PROJETOS = [
    {"id":"p1","nome":"MENTORES"},{"id":"p2","nome":"ANIET"},
    {"id":"p3","nome":"APCMC"},   {"id":"p4","nome":"APIMA"},
    {"id":"p5","nome":"PRODUTECH"},{"id":"p6","nome":"CALÇADO"},
]
_MOCK_PRE = [
    {"id":"f1","numero_fatura":"FT2026/0155","valor":2400,"estado":"leitura_falhada","erro_leitura":"Código interno não encontrado","created_at":"2026-06-15","ficheiro_url":None,"profiles":{"nome":"Miguel Santos","email":"miguel@demo.pt"},"acoes":{"nome":"MENTORES"}},
    {"id":"f2","numero_fatura":"FT2026/0153","valor":1950,"estado":"acao_nao_fechada","erro_leitura":"Nome do formador não corresponde","created_at":"2026-06-14","ficheiro_url":None,"profiles":{"nome":"Sofia Rodrigues","email":"sofia@demo.pt"},"acoes":{"nome":"ANIET"}},
    {"id":"f3","numero_fatura":"FT2026/0150","valor":1800,"estado":"submetida","erro_leitura":"Valor diverge do contrato","created_at":"2026-06-13","ficheiro_url":None,"profiles":{"nome":"Luís Cardoso","email":"luis@demo.pt"},"acoes":{"nome":"PRODUTECH"}},
]
_MOCK_VENC = [
    {"id":"v1","numero_fatura":"FT2026/0110","valor":1800,"prazo_pagamento":"2026-06-02","data_fatura":"2026-05-02","atraso":14,"profiles":{"nome":"João Silva","email":"joao@demo.pt"},"acoes":{"nome":"MENTORES"}},
    {"id":"v2","numero_fatura":"FT2026/0108","valor":2600,"prazo_pagamento":"2026-06-08","data_fatura":"2026-05-08","atraso":8,"profiles":{"nome":"Rui Mendes","email":"rui@demo.pt"},"acoes":{"nome":"PRODUTECH"}},
    {"id":"v3","numero_fatura":"FT2026/0105","valor":1400,"prazo_pagamento":"2026-06-12","data_fatura":"2026-05-12","atraso":4,"profiles":{"nome":"Pedro Costa","email":"pedro@demo.pt"},"acoes":{"nome":"CALÇADO"}},
]
_MOCK_AV = [
    {"id":"a1","numero_fatura":"FT2026/0142","valor":3200,"prazo_pagamento":"2026-06-21","data_fatura":"2026-06-01","dias":5,"profiles":{"nome":"João Silva","email":"joao@demo.pt"},"acoes":{"nome":"MENTORES"}},
    {"id":"a2","numero_fatura":"FT2026/0138","valor":2800,"prazo_pagamento":"2026-06-27","data_fatura":"2026-06-03","dias":11,"profiles":{"nome":"Ana Ferreira","email":"ana@demo.pt"},"acoes":{"nome":"ANIET"}},
    {"id":"a3","numero_fatura":"FT2026/0136","valor":1900,"prazo_pagamento":"2026-07-04","data_fatura":"2026-06-05","dias":18,"profiles":{"nome":"Pedro Costa","email":"pedro@demo.pt"},"acoes":{"nome":"CALÇADO"}},
    {"id":"a4","numero_fatura":"FT2026/0129","valor":2100,"prazo_pagamento":"2026-07-10","data_fatura":"2026-06-06","dias":24,"profiles":{"nome":"Carla Neves","email":"carla@demo.pt"},"acoes":{"nome":"APCMC"}},
    {"id":"a5","numero_fatura":"FT2026/0127","valor":2300,"prazo_pagamento":"2026-07-16","data_fatura":"2026-06-08","dias":30,"profiles":{"nome":"Rui Mendes","email":"rui@demo.pt"},"acoes":{"nome":"APIMA"}},
]
_MOCK_CF_L = ["S1 Jun","S2 Jun","S3 Jun","S4 Jun","S1 Jul","S2 Jul","S3 Jul","S4 Jul","S1 Ago","S2 Ago","S3 Ago","S4 Ago","S1 Set"]
_MOCK_CF_S = [3200,2100,4100,2800,2600,3800,1900,3200,2400,2800,1800,2100,2300]

# Notificações mock

# ---------------------------------------------------------------------------
# CARD FATURA
# ---------------------------------------------------------------------------
def _card(row,tipo,idx,user_nome):
    fid=row.get("id") or str(idx)
    n=row.get("numero_fatura") or "—"; f=_formador(row); p=_projeto(row); v=row.get("valor") or 0
    df=row.get("data_fatura") or "—"; dp=row.get("prazo_pagamento") or "—"
    if tipo=="vencida":
        atraso=row.get("atraso") or 0; cls="fin-card vc"
        dias_h=f'<div class="dr">+{atraso} dias em atraso</div>'
    else:
        dias=row.get("dias") or 0; cls="fin-card av"
        dias_h=f'<div class="da">vence em {dias} dias</div>'
    # Card + acções na mesma linha
    col_c, col_b = st.columns([5, 2])
    with col_c:
        st.markdown(
            f'<div class="{cls}">'
            f'<div style="flex:1">'
            f'<div class="ct">{n} <span style="font-size:12px;font-weight:400;color:#8B94A3">{f}</span></div>'
            f'<div class="cm">{ptag(p)}</div>'
            f'<div class="cd">Emissão {df} · Prazo {dp}</div>'
            f'</div>'
            f'<div style="text-align:right;min-width:85px">'
            f'<div class="cv">{eur(v)}</div>{dias_h}'
            f'</div></div>', unsafe_allow_html=True)
    with col_b:
        show_key = f"show_comp_{tipo}_{idx}_{fid}"
        if not st.session_state.get(show_key):
            if st.button("✓ Marcar pago", key=f"pg_{tipo}_{idx}_{fid}",
                         use_container_width=True, type="primary"):
                st.session_state[show_key] = True
                st.rerun()
        else:
            comp = st.file_uploader(
                "📎 Comprovativo (PDF)",
                type=["pdf"],
                key=f"comp_{tipo}_{idx}_{fid}",
            )
            col_ok, col_x = st.columns([3, 1])
            with col_ok:
                if st.button("✅ Confirmar", key=f"conf_{tipo}_{idx}_{fid}",
                             use_container_width=True, type="primary",
                             disabled=comp is None):
                    guardar_comprovativo(fid, comp.getvalue(), comp.name, user_nome)
                    if SUPABASE_OK:
                        if marcar_paga(fid, user_nome):
                            reg_hist("Marcado pago", n, f, p, v)
                            st.session_state.pop(show_key, None)
                            st.toast(f"{n} paga. Comprovativo guardado.")
                            st.rerun()
                    else:
                        lst_key = "mock_venc" if tipo == "vencida" else "mock_av"
                        st.session_state[lst_key] = [
                            x for x in st.session_state[lst_key] if x.get("id") != fid]
                        reg_hist("Marcado pago", n, f, p, v)
                        st.session_state.pop(show_key, None)
                        st.toast(f"{n} paga.")
                        st.rerun()
            with col_x:
                if st.button("✖", key=f"canc_{tipo}_{idx}_{fid}",
                             use_container_width=True):
                    st.session_state.pop(show_key, None)
                    st.rerun()

# ---------------------------------------------------------------------------
# TAB 2 — ALERTAS
# ---------------------------------------------------------------------------
def render_alertas(user):
    user_nome=user.get("nome") or "Financeiro"
    col_f,col_c,col_o,col_d1,col_d2=st.columns([2,2,2,1,1])
    with col_f:
        pjs=get_projetos() if SUPABASE_OK else _MOCK_PROJETOS
        filtro=st.selectbox("Projeto",["Todos"]+[p["nome"] for p in pjs],key="fil_p")
    with col_c:
        try:
            from app.financeiro_consultores import _get_cons
            cons_lista=_get_cons()
        except: cons_lista=[]
        filtro_cons=st.selectbox("Consultor",["Todos"]+[c["nome"] for c in cons_lista],key="fil_cons_al")
    with col_o:
        ordem=st.selectbox("Ordenar",ORDEM,key="ord_f")
    with col_d1:
        d_ini=st.date_input("De",value=None,key="d_i",format="DD/MM/YYYY")
    with col_d2:
        d_fim=st.date_input("Até",value=None,key="d_f",format="DD/MM/YYYY")

    def fil_cons_fn(dados):
        if filtro_cons=="Todos": return dados
        return [d for d in dados if filtro_cons in (_formador(d) or "")]

    if SUPABASE_OK:
        pre=get_faturas_pre_aprovacao(filtro if filtro!="Todos" else None)
        venc=fil_datas(fil_cons_fn(fil_proj(get_faturas_vencidas(),filtro)),d_ini,d_fim)
        av=fil_datas(fil_cons_fn(fil_proj(get_faturas_a_vencer(),filtro)),d_ini,d_fim)
        top5=get_top_formadores_pendentes()
        pp=get_pendente_por_projeto()
        cfl,cfs=get_cashflow_previsto()
        hist_bd=get_historico_financeiro()
    else:
        pre=fil_proj(st.session_state.mock_pre,filtro)
        venc=fil_datas(fil_cons_fn(fil_proj(st.session_state.mock_venc,filtro)),d_ini,d_fim)
        av=fil_datas(fil_cons_fn(fil_proj(st.session_state.mock_av,filtro)),d_ini,d_fim)
        top5=[{"formador":"João Silva","valor":5000},{"formador":"Rui Mendes","valor":4900},{"formador":"Pedro Costa","valor":3300},{"formador":"Ana Ferreira","valor":2800},{"formador":"Carla Neves","valor":2100}]
        pp=[{"projeto":"MENTORES","valor":5000},{"projeto":"PRODUTECH","valor":4400},{"projeto":"CALÇADO","valor":3300},{"projeto":"ANIET","valor":2800},{"projeto":"APIMA","valor":2300},{"projeto":"APCMC","valor":2100}]
        cfl,cfs=_MOCK_CF_L,_MOCK_CF_S; hist_bd=[]

    venc=ordenar(venc,ordem); av=ordenar(av,ordem)
    tv=sum(f.get("valor") or 0 for f in venc); ta=sum(f.get("valor") or 0 for f in av)

    st.html('<div class="fin-kpi-row">'+kpi_h("🚨 Vencido",eur(tv),f"{len(venc)} faturas","r")+kpi_h("⏳ A vencer 30d",eur(ta),f"{len(av)} faturas","a")+kpi_h("💳 Pago este mês",eur(121400),"23 faturas","b")+kpi_h("💰 Total pendente",eur(tv+ta),f"{len(venc)+len(av)} faturas","p")+'</div>')
    st.html(div())

    # Pré-aprovação
    st.markdown(sec(f"🔍 Aprovação manual ({len(pre)} pendentes)","Faturas cuja validação automática falhou."),unsafe_allow_html=True)
    if not pre:
        st.html('<div class="fin-empty">✅ Nenhuma fatura pendente de aprovação manual.</div>')
    else:
        for i,row in enumerate(pre):
            fid=row.get("id") or str(i); n=row.get("numero_fatura") or "—"
            f=_formador(row); em=_email(row); p=_projeto(row); v=row.get("valor") or 0
            erro=row.get("erro_leitura") or row.get("notas") or "—"
            ds=str(row.get("created_at") or "—")[:10]; fich=row.get("ficheiro_url")
            col_i, col_a = st.columns([5, 3])
            with col_i:
                pdf_link = f'&nbsp;<a href="{fich}" target="_blank" style="font-size:12px;color:#2A7A8C">📄 Ver PDF</a>' if fich else ""
                st.markdown(
                    f'<div class="fin-aprov">'
                    f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">'
                    f'<span style="font-weight:700;font-size:14px">{n}</span>{ptag(p)}{pdf_link}'
                    f'</div>'
                    f'<div style="font-size:13px;color:#4B5263"><b>Formador:</b> {f} &nbsp;·&nbsp; <b>Valor:</b> {eur(v)}</div>'
                    f'<div class="err">⚠️ {erro}</div>'
                    f'<div class="ds">Submetida: {ds}</div>'
                    f'</div>', unsafe_allow_html=True)
            with col_a:
                if st.button("✅ Aprovar", key=f"ap_{i}_{fid}", use_container_width=True, type="primary"):
                    if SUPABASE_OK:
                        if aprovar_fatura(fid, user_nome):
                            reg_hist("Aprovado", n, f, p, v); st.toast(f"{n} aprovada."); st.rerun()
                    else:
                        st.session_state.mock_pre = [x for x in st.session_state.mock_pre if x.get("id") != fid]
                        reg_hist("Aprovado", n, f, p, v); st.toast(f"{n} aprovada."); st.rerun()
                mot = st.text_input("", key=f"mt_{i}_{fid}", placeholder="Motivo de rejeição…",
                                    label_visibility="collapsed")
                if st.button("❌ Rejeitar", key=f"rj_{i}_{fid}", use_container_width=True):
                    if mot:
                        if SUPABASE_OK:
                            if rejeitar_fatura(fid, mot, user_nome):
                                reg_hist("Rejeitado", n, f, p, v, mot)
                                notificar_rejeicao(em, n, mot)
                                st.toast(f"{n} rejeitada."); st.rerun()
                        else:
                            st.session_state.mock_pre = [x for x in st.session_state.mock_pre if x.get("id") != fid]
                            reg_hist("Rejeitado", n, f, p, v, mot)
                            notificar_rejeicao(em, n, mot)
                            st.toast(f"{n} rejeitada."); st.rerun()
                    else:
                        st.warning("Escreve um motivo.")

    with st.expander("📤 Ler fatura PDF manualmente"):
        up=st.file_uploader("PDF",type=["pdf"],key="pdf_up")
        if up:
            d=extrair_pdf(up.read())
            if d.get("erro"): st.error(f"Erro: {d['erro']}")
            else:
                c1,c2,c3,c4=st.columns(4)
                c1.metric("Nº Fatura",d.get("numero_fatura") or "—"); c2.metric("NIF",d.get("nif_emitente") or "—")
                c3.metric("Valor",eur(d.get("valor") or 0)); c4.metric("Data",d.get("data_fatura") or "—")

    st.html(div())

    # Vencidas
    st.markdown(sec("🔴 Faturas vencidas"),unsafe_allow_html=True)
    PAGE=10; pv=st.session_state.get("pag_v",0); pagv=venc[pv*PAGE:(pv+1)*PAGE]
    if not venc:
        st.html('<div class="fin-empty">Nenhuma fatura vencida para este filtro.</div>')
    else:
        for i,row in enumerate(pagv): _card(row,"vencida",pv*PAGE+i,user_nome)
        st.markdown(f"**Total vencido: {eur(tv)}**")
        tp_=max(1,(len(venc)+PAGE-1)//PAGE)
        if tp_>1:
            c1,c2,c3=st.columns([1,2,1])
            if c1.button("← Anterior",key="pv_p",disabled=pv==0): st.session_state.pag_v=pv-1; st.rerun()
            c2.markdown(f"<div style='text-align:center;padding-top:8px'>Página {pv+1}/{tp_}</div>",unsafe_allow_html=True)
            if c3.button("Próxima →",key="pv_n",disabled=pv>=tp_-1): st.session_state.pag_v=pv+1; st.rerun()
        st.download_button("⬇️ Excel vencidas",excel_bytes(venc),f"vencidas_{filtro}.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",key="dl_v")

    st.html(div())

    # A vencer
    st.markdown(sec("🟡 A vencer — próximos 30 dias"),unsafe_allow_html=True)
    pa=st.session_state.get("pag_a",0); paga=av[pa*PAGE:(pa+1)*PAGE]
    if not av:
        st.html('<div class="fin-empty">Nenhuma fatura a vencer para este filtro.</div>')
    else:
        for i,row in enumerate(paga): _card(row,"avencer",pa*PAGE+i,user_nome)
        st.markdown(f"**Total a vencer: {eur(ta)}**")
        tp_=max(1,(len(av)+PAGE-1)//PAGE)
        if tp_>1:
            c1,c2,c3=st.columns([1,2,1])
            if c1.button("← Anterior",key="pa_p",disabled=pa==0): st.session_state.pag_a=pa-1; st.rerun()
            c2.markdown(f"<div style='text-align:center;padding-top:8px'>Página {pa+1}/{tp_}</div>",unsafe_allow_html=True)
            if c3.button("Próxima →",key="pa_n",disabled=pa>=tp_-1): st.session_state.pag_a=pa+1; st.rerun()
        st.download_button("⬇️ Excel a vencer",excel_bytes(av),f"avencer_{filtro}.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",key="dl_a")

    st.html(div())

    cl,cr=st.columns(2)
    with cl:
        st.markdown(sec("Top 5 formadores pendentes"),unsafe_allow_html=True)
        h=""
        for i,row in enumerate(top5):
            h+=f'<div class="fin-card" style="padding:10px 14px"><span style="font-size:12px;font-weight:700;color:#8B94A3;min-width:22px">#{i+1}</span><span style="flex:1;font-size:13px">{row["formador"]}</span><span style="font-weight:700;font-size:14px">{eur(row["valor"])}</span></div>'
        st.markdown(h,unsafe_allow_html=True)
    with cr:
        st.markdown(sec("Pendente por projeto"),unsafe_allow_html=True)
        h=""
        for row in pp:
            c=CORES.get(row["projeto"],"#888")
            h+=f'<div class="fin-card" style="padding:10px 14px"><span style="width:8px;height:8px;border-radius:50%;background:{c};display:inline-block;margin-right:8px;flex-shrink:0"></span><span style="flex:1;font-size:13px">{row["projeto"]}</span><span style="font-weight:700;font-size:14px">{eur(row["valor"])}</span></div>'
        st.markdown(h,unsafe_allow_html=True)

    st.html(div())

    # Cashflow
    st.markdown(sec("Cashflow previsto — próximos 90 dias"),unsafe_allow_html=True)
    if cfs:
        acum,tot=[],0
        for v in cfs: tot+=v; acum.append(tot)
        fig=go.Figure()
        fig.add_trace(go.Bar(x=cfl,y=cfs,name="Saída semanal",marker_color="#FBBF24",yaxis="y1"))
        fig.add_trace(go.Scatter(x=cfl,y=acum,name="Acumulado",line=dict(color="#2563EB",width=2),mode="lines+markers",yaxis="y2"))
        fig.update_layout(height=310,margin=dict(t=20,b=60,l=50,r=60),
            legend=dict(orientation="h",yanchor="bottom",y=1.02,font=dict(size=11)),
            yaxis=dict(title="Saída (€)",showgrid=False,tickfont=dict(size=11)),
            yaxis2=dict(title="Acumulado (€)",overlaying="y",side="right",showgrid=False,tickfont=dict(size=11)),
            paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickangle=45,automargin=True,tickfont=dict(size=11)))
        st.plotly_chart(fig,use_container_width=True,config=PLOTLY_CFG)

    st.html(div())

    # Histórico
    # Comprovativos
    comps = st.session_state.get("comprovativos", {})
    if comps:
        st.html(div())
        st.markdown(sec(f"📎 Comprovativos guardados ({len(comps)})"), unsafe_allow_html=True)
        for fid, comp in comps.items():
            url  = comp.get("url")
            nome = comp.get("nome", "—")
            quando = comp.get("guardado_em", "—")
            por    = comp.get("guardado_por", "—")
            link = f'<a href="{url}" target="_blank" style="color:#2A7A8C;font-size:12px">📄 Abrir PDF</a>' if url else '<span style="font-size:12px;color:#8B94A3">Guardado localmente</span>'
            st.html(
                f'<div class="fin-card">'
                f'<div style="flex:1">'
                f'<div style="font-weight:600;font-size:13px">{nome}</div>'
                f'<div style="font-size:12px;color:#8B94A3">Fatura: {fid} · {quando} · por {por}</div>'
                f'</div>{link}</div>'
            )

    st.html(div())
    st.markdown(sec("📋 Histórico de ações"), unsafe_allow_html=True)
    hist=st.session_state.historico[::-1]
    if hist:
        df=pd.DataFrame(hist)
        df.columns=["Data/Hora","Ação","Nº Fatura","Formador","Projeto","Valor","Motivo"]
        df["Valor"]=df["Valor"].apply(eur)
        st.dataframe(df,use_container_width=True,hide_index=True)
        st.download_button("⬇️ Exportar CSV",df.to_csv(index=False).encode(),"historico.csv","text/csv")
    elif hist_bd:
        df=pd.DataFrame([{"Data/Hora":str(h.get("criado_em",""))[:16],"Ação":h.get("tipo",""),"Detalhe":h.get("descricao","")} for h in hist_bd])
        st.dataframe(df,use_container_width=True,hide_index=True)
    else:
        st.html('<div class="fin-empty">Nenhuma ação registada nesta sessão.</div>')
