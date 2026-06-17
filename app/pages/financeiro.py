"""Pagina do financeiro."""
from __future__ import annotations
import io
from datetime import date, datetime
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# IMPORTS BD
# ---------------------------------------------------------------------------
try:
    from app.db_financeiro import (
        get_metricas_dashboard, get_faturas_recentes, get_despesa_por_projeto,
        get_faturas_pre_aprovacao, get_faturas_vencidas, get_faturas_a_vencer,
        get_top_formadores_pendentes, get_pendente_por_projeto,
        get_cashflow_previsto, get_projetos, get_historico_financeiro,
        aprovar_fatura, rejeitar_fatura, marcar_paga, get_supabase,
    )
    get_supabase()
    SUPABASE_OK = True
except Exception:
    SUPABASE_OK = False

# ---------------------------------------------------------------------------
# DESIGN
# ---------------------------------------------------------------------------
try:
    from app.design_financeiro import (
        DESIGN_CSS, proj_tag, badge, fmt_eur, kpi, sec_header,
        CORES_PROJETO, BG_PROJETO,
    )
except Exception:
    DESIGN_CSS = ""
    CORES_PROJETO = {}
    BG_PROJETO = {}
    def proj_tag(p): return f"`{p}`"
    def badge(e): return e
    def fmt_eur(v):
        try: return f"€ {float(v):,.0f}".replace(",",".")
        except: return "€ —"
    def kpi(l,v,s,var=""): return f"**{l}**: {v}"
    def sec_header(t,s=""): return t

# ---------------------------------------------------------------------------
# MOCK DATA
# ---------------------------------------------------------------------------
_MOCK_PROJETOS = [
    {"id":"p1","nome":"MENTORES", "magna_id":"COMPETE2030-FSE+-01195000"},
    {"id":"p2","nome":"ANIET",    "magna_id":"COMPETE2030-FSE+-01196000"},
    {"id":"p3","nome":"APCMC",    "magna_id":"COMPETE2030-FSE+-01195400"},
    {"id":"p4","nome":"APIMA",    "magna_id":"COMPETE2030-FSE+-01194800"},
    {"id":"p5","nome":"PRODUTECH","magna_id":"COMPETE2030-FSE+-02982000"},
    {"id":"p6","nome":"CALÇADO",  "magna_id":"COMPETE2030-FSE+-02981900"},
]
_MOCK_PRE_APROVACAO = [
    {"id":"f1","numero_fatura":"FT2026/0155","valor":2400,"estado":"leitura_falhada",  "erro_leitura":"Código interno não encontrado no sistema",    "created_at":"2026-06-15","ficheiro_url":None,"profiles":{"nome":"Miguel Santos",  "email":"miguel@demo.pt"},"acoes":{"nome":"MENTORES", "magna_id":"01195000"}},
    {"id":"f2","numero_fatura":"FT2026/0153","valor":1950,"estado":"acao_nao_fechada", "erro_leitura":"Nome do formador não corresponde ao projeto", "created_at":"2026-06-14","ficheiro_url":None,"profiles":{"nome":"Sofia Rodrigues","email":"sofia@demo.pt"}, "acoes":{"nome":"ANIET",    "magna_id":"01196000"}},
    {"id":"f3","numero_fatura":"FT2026/0150","valor":1800,"estado":"submetida",        "erro_leitura":"Valor diverge do contrato registado",         "created_at":"2026-06-13","ficheiro_url":None,"profiles":{"nome":"Luís Cardoso",   "email":"luis@demo.pt"},  "acoes":{"nome":"PRODUTECH","magna_id":"02982000"}},
]
_MOCK_VENCIDAS = [
    {"id":"v1","numero_fatura":"FT2026/0110","valor":1800,"prazo_pagamento":"2026-06-02","data_fatura":"2026-05-02","atraso":14,"profiles":{"nome":"João Silva", "email":"joao@demo.pt"},"acoes":{"nome":"MENTORES", "magna_id":"01195000"}},
    {"id":"v2","numero_fatura":"FT2026/0108","valor":2600,"prazo_pagamento":"2026-06-08","data_fatura":"2026-05-08","atraso":8, "profiles":{"nome":"Rui Mendes", "email":"rui@demo.pt"}, "acoes":{"nome":"PRODUTECH","magna_id":"02982000"}},
    {"id":"v3","numero_fatura":"FT2026/0105","valor":1400,"prazo_pagamento":"2026-06-12","data_fatura":"2026-05-12","atraso":4, "profiles":{"nome":"Pedro Costa","email":"pedro@demo.pt"},"acoes":{"nome":"CALÇADO",  "magna_id":"02981900"}},
]
_MOCK_A_VENCER = [
    {"id":"a1","numero_fatura":"FT2026/0142","valor":3200,"prazo_pagamento":"2026-06-21","data_fatura":"2026-06-01","dias":5, "profiles":{"nome":"João Silva",  "email":"joao@demo.pt"}, "acoes":{"nome":"MENTORES","magna_id":"01195000"}},
    {"id":"a2","numero_fatura":"FT2026/0138","valor":2800,"prazo_pagamento":"2026-06-27","data_fatura":"2026-06-03","dias":11,"profiles":{"nome":"Ana Ferreira","email":"ana@demo.pt"},  "acoes":{"nome":"ANIET",   "magna_id":"01196000"}},
    {"id":"a3","numero_fatura":"FT2026/0136","valor":1900,"prazo_pagamento":"2026-07-04","data_fatura":"2026-06-05","dias":18,"profiles":{"nome":"Pedro Costa", "email":"pedro@demo.pt"},"acoes":{"nome":"CALÇADO", "magna_id":"02981900"}},
    {"id":"a4","numero_fatura":"FT2026/0129","valor":2100,"prazo_pagamento":"2026-07-10","data_fatura":"2026-06-06","dias":24,"profiles":{"nome":"Carla Neves", "email":"carla@demo.pt"},"acoes":{"nome":"APCMC",   "magna_id":"01195400"}},
    {"id":"a5","numero_fatura":"FT2026/0127","valor":2300,"prazo_pagamento":"2026-07-16","data_fatura":"2026-06-08","dias":30,"profiles":{"nome":"Rui Mendes",  "email":"rui@demo.pt"},  "acoes":{"nome":"APIMA",   "magna_id":"01194800"}},
]
_MOCK_CF_LABELS = ["S1 Jun","S2 Jun","S3 Jun","S4 Jun","S1 Jul","S2 Jul","S3 Jul","S4 Jul","S1 Ago","S2 Ago","S3 Ago","S4 Ago","S1 Set"]
_MOCK_CF_SAIDAS = [3200,2100,4100,2800,2600,3800,1900,3200,2400,2800,1800,2100,2300]
PLOTLY_CFG = {"displayModeBar":False}
ORDEM_OPCOES = ["Data de vencimento","Valor (maior primeiro)","Valor (menor primeiro)","Projeto"]

# ---------------------------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------------------------
def init_state():
    if "historico" not in st.session_state:
        st.session_state.historico = []
    if not SUPABASE_OK:
        if "mock_pre"      not in st.session_state: st.session_state.mock_pre      = list(_MOCK_PRE_APROVACAO)
        if "mock_vencidas" not in st.session_state: st.session_state.mock_vencidas = list(_MOCK_VENCIDAS)
        if "mock_a_vencer" not in st.session_state: st.session_state.mock_a_vencer = list(_MOCK_A_VENCER)

def reg_historico(acao,n_fatura,formador,projeto,valor,motivo=""):
    st.session_state.historico.append({
        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "acao":acao,"n_fatura":n_fatura,"formador":formador,
        "projeto":projeto,"valor":valor,"motivo":motivo,
    })

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def _row_formador(r): return (r.get("profiles") or {}).get("nome") or "—"
def _row_projeto(r):  return (r.get("acoes")    or {}).get("nome") or "—"
def _row_email(r):    return (r.get("profiles") or {}).get("email") or ""

def ordenar(dados,criterio):
    if criterio=="Valor (maior primeiro)": return sorted(dados,key=lambda x:x.get("valor") or 0,reverse=True)
    if criterio=="Valor (menor primeiro)": return sorted(dados,key=lambda x:x.get("valor") or 0)
    if criterio=="Projeto": return sorted(dados,key=lambda x:_row_projeto(x))
    col="atraso" if dados and "atraso" in dados[0] else "dias"
    return sorted(dados,key=lambda x:x.get(col) or 0,reverse=True)

def filtrar_proj(dados,proj):
    if not proj or proj=="Todos": return dados
    return [d for d in dados if _row_projeto(d)==proj]

def filtrar_datas(dados,d_ini,d_fim):
    if not d_ini and not d_fim: return dados
    out=[]
    for d in dados:
        ps=d.get("prazo_pagamento")
        if not ps: out.append(d); continue
        try:
            p=date.fromisoformat(ps)
            if d_ini and p<d_ini: continue
            if d_fim and p>d_fim: continue
        except: pass
        out.append(d)
    return out

def gerar_excel(projeto,faturas):
    rows=[{"Nº Fatura":f.get("numero_fatura") or "—","Formador":_row_formador(f),
           "Projeto":_row_projeto(f),"Valor (€)":f.get("valor") or 0,
           "Data Fatura":f.get("data_fatura") or "—",
           "Prazo Pagamento":f.get("prazo_pagamento") or "—",
           "Estado":f.get("estado") or "—"} for f in faturas]
    buf=io.BytesIO()
    pd.DataFrame(rows).to_excel(buf,index=False,engine="openpyxl")
    return buf.getvalue()

def extrair_pdf(b):
    import re, io as _io
    try: import pdfplumber
    except: return {"erro":"pdfplumber não instalado"}
    r={"numero_fatura":None,"nif_emitente":None,"valor":None,"data_fatura":None,"texto_completo":"","erro":None}
    try:
        with pdfplumber.open(_io.BytesIO(b)) as pdf:
            txt="\n".join(p.extract_text() or "" for p in pdf.pages)
        r["texto_completo"]=txt
        m=re.search(r"(?:fatura|recibo|ft|fr)[^\d]*(\d{4}[/\-]\d+)",txt,re.I)
        if m: r["numero_fatura"]=m.group(1)
        nifs=re.findall(r"\b\d{9}\b",txt)
        if nifs: r["nif_emitente"]=nifs[0]
        m=re.search(r"(?:total|valor|montante)[^\d€]*[€]?\s*([\d\s.,]+)\s*(?:€|eur)?",txt,re.I)
        if m:
            try: r["valor"]=float(m.group(1).replace(" ","").replace(".","").replace(",","."))
            except: pass
        m=re.search(r"\b(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})\b",txt)
        if m: r["data_fatura"]=f"{m.group(3)}-{m.group(2).zfill(2)}-{m.group(1).zfill(2)}"
    except Exception as e: r["erro"]=str(e)
    return r

# ---------------------------------------------------------------------------
# TAB 1 — DASHBOARD
# ---------------------------------------------------------------------------
def render_dashboard(user):
    if SUPABASE_OK:
        m=get_metricas_dashboard()
        recentes=get_faturas_recentes(10)
        despesa=get_despesa_por_projeto()
        n_pre=m["pre_aprovacao_count"]; total_pre=m["pre_aprovacao_total"]
        n_apr=m["aprovado_count"];      total_apr=m["aprovado_total"]
        n_pago=m["pago_mes_count"];     total_pago=m["pago_mes_total"]
        n_venc=m["vencido_count"];      total_venc=m["vencido_total"]
    else:
        n_pre=len(st.session_state.mock_pre); total_pre=sum(f["valor"] for f in st.session_state.mock_pre)
        total_apr=sum(f["valor"] for f in st.session_state.mock_a_vencer); n_apr=len(st.session_state.mock_a_vencer)
        total_pago=121400; n_pago=23
        total_venc=sum(f["valor"] for f in st.session_state.mock_vencidas); n_venc=len(st.session_state.mock_vencidas)
        recentes=_MOCK_A_VENCER[:5]
        despesa=[{"projeto":k,"valor":v} for k,v in {"MENTORES":52400,"ANIET":38900,"APCMC":27600,"APIMA":19200,"PRODUTECH":61200,"CALÇADO":14600}.items()]

    if n_pre>0:
        st.markdown(f'<div class="alert-warn">⚠️ <strong>{n_pre} fatura(s) aguardam aprovação manual</strong> — ver em <strong>Alertas/A Pagar</strong>.</div>',unsafe_allow_html=True)

    # KPIs
    st.markdown(
        '<div class="kpi-row">'
        + kpi("🔍 Pré-aprovação",    fmt_eur(total_pre),  f"{n_pre} faturas",  "amber")
        + kpi("✅ Aprovado a pagar", fmt_eur(total_apr),  f"{n_apr} faturas",  "green")
        + kpi("💳 Pago este mês",    fmt_eur(total_pago), f"{n_pago} faturas", "blue")
        + kpi("🚨 Vencido",          fmt_eur(total_venc), f"{n_venc} faturas", "red")
        + '</div>', unsafe_allow_html=True
    )

    st.markdown('<div class="sec-divider"></div>', unsafe_allow_html=True)

    col_l, col_r = st.columns([3,2])

    with col_l:
        st.markdown(sec_header("Faturas recentes"), unsafe_allow_html=True)
        for row in recentes:
            formador=_row_formador(row); projeto=_row_projeto(row)
            estado=row.get("estado") or "submetida"
            n_fat=row.get("numero_fatura") or "—"; valor=row.get("valor") or 0
            st.markdown(
                f'<div class="fatura-card">'
                f'<div style="flex:1">'
                f'<div class="fatura-title">{n_fat}</div>'
                f'<div class="fatura-meta">{proj_tag(projeto)}&nbsp;·&nbsp;{formador}</div>'
                f'</div>'
                f'<div style="text-align:right;margin-right:12px">'
                f'<div class="fatura-valor">{fmt_eur(valor)}</div>'
                f'</div>'
                f'{badge(estado)}'
                f'</div>', unsafe_allow_html=True
            )

    with col_r:
        st.markdown(sec_header("Por estado"), unsafe_allow_html=True)
        fig=go.Figure(go.Pie(
            labels=["Pré-aprovação","Aprovado","Pago","Vencido"],
            values=[n_pre or 1, n_apr or 1, n_pago or 1, n_venc or 1],
            hole=0.68,
            marker_colors=["#D97706","#16A34A","#2563EB","#DC2626"],
            textinfo="percent",
            textfont=dict(size=12),
            showlegend=True,
        ))
        fig.update_layout(
            margin=dict(t=10,b=10,l=0,r=0), height=280,
            legend=dict(orientation="v",x=1,y=0.5,font=dict(size=11)),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig,use_container_width=True,config=PLOTLY_CFG)

    st.markdown('<div class="sec-divider"></div>', unsafe_allow_html=True)
    st.markdown(sec_header("Despesa por projeto"), unsafe_allow_html=True)

    ds=sorted(despesa,key=lambda x:x["valor"])
    max_v=max((d["valor"] for d in ds),default=1)
    fig2=go.Figure(go.Bar(
        x=[d["valor"] for d in ds], y=[d["projeto"] for d in ds],
        orientation="h",
        marker_color=[CORES_PROJETO.get(d["projeto"],"#888") for d in ds],
        text=[fmt_eur(d["valor"]) for d in ds], textposition="outside",
        textfont=dict(size=12),
    ))
    fig2.update_layout(
        margin=dict(t=4,b=4,l=4,r=120), height=280,
        xaxis=dict(showticklabels=False,showgrid=False,range=[0,max_v*1.28]),
        yaxis=dict(showgrid=False,tickfont=dict(size=13)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig2,use_container_width=True,config=PLOTLY_CFG)

# ---------------------------------------------------------------------------
# CARD FATURA — reutilizado em alertas
# ---------------------------------------------------------------------------
def _card_fatura(row, tipo, idx, user_nome):
    fatura_id=row.get("id") or str(idx)
    n_fatura=row.get("numero_fatura") or "—"
    formador=_row_formador(row); projeto=_row_projeto(row)
    valor=row.get("valor") or 0
    data_fat=row.get("data_fatura") or "—"
    prazo=row.get("prazo_pagamento") or "—"

    if tipo=="vencida":
        atraso=row.get("atraso") or 0
        card_cls="fatura-card vencida"
        dias_html=f'<div class="fatura-dias-r">+{atraso} dias em atraso</div>'
    else:
        dias=row.get("dias") or 0
        card_cls="fatura-card a-vencer"
        dias_html=f'<div class="fatura-dias-a">vence em {dias} dias</div>'

    col_card, col_btn = st.columns([5,2])
    with col_card:
        st.markdown(
            f'<div class="{card_cls}">'
            f'<div style="flex:1">'
            f'<div class="fatura-title">{n_fatura} &nbsp;<span style="font-size:12px;font-weight:400;color:#8B94A3">{formador}</span></div>'
            f'<div class="fatura-meta">{proj_tag(projeto)}</div>'
            f'<div class="fatura-datas">Emissão {data_fat} · Prazo {prazo}</div>'
            f'</div>'
            f'<div style="text-align:right;min-width:90px">'
            f'<div class="fatura-valor">{fmt_eur(valor)}</div>'
            f'{dias_html}'
            f'</div>'
            f'</div>', unsafe_allow_html=True
        )
    with col_btn:
        st.markdown("<div style='margin-top:6px'>",unsafe_allow_html=True)
        if st.button("✓ Marcar pago", key=f"pago_{tipo}_{idx}_{fatura_id}", use_container_width=True):
            if SUPABASE_OK:
                if marcar_paga(fatura_id, user_nome):
                    reg_historico("Marcado pago",n_fatura,formador,projeto,valor)
                    st.toast(f"Fatura {n_fatura} marcada como paga.")
                    st.rerun()
            else:
                key="mock_vencidas" if tipo=="vencida" else "mock_a_vencer"
                st.session_state[key]=[f for f in st.session_state[key] if f.get("id")!=fatura_id]
                reg_historico("Marcado pago",n_fatura,formador,projeto,valor)
                st.toast(f"Fatura {n_fatura} marcada como paga.")
                st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TAB 2 — ALERTAS / A PAGAR
# ---------------------------------------------------------------------------
def render_alertas(user):
    user_nome=user.get("nome") or "Financeiro"

    # Filtros
    col_f,col_o,col_d1,col_d2=st.columns([2,2,1,1])
    with col_f:
        proj_bd=get_projetos() if SUPABASE_OK else _MOCK_PROJETOS
        filtro=st.selectbox("Projeto",[" Todos"]+[p["nome"] for p in proj_bd],key="fil_proj",label_visibility="visible")
        filtro=filtro.strip()
    with col_o:
        ordem=st.selectbox("Ordenar por",ORDEM_OPCOES,key="ord_fat")
    with col_d1:
        d_ini=st.date_input("De",value=None,key="d_ini",format="DD/MM/YYYY")
    with col_d2:
        d_fim=st.date_input("Até",value=None,key="d_fim",format="DD/MM/YYYY")

    if SUPABASE_OK:
        pre_dados=get_faturas_pre_aprovacao(filtro if filtro!="Todos" else None)
        venc_dados=filtrar_datas(filtrar_proj(get_faturas_vencidas(),filtro),d_ini,d_fim)
        aven_dados=filtrar_datas(filtrar_proj(get_faturas_a_vencer(),filtro),d_ini,d_fim)
        top5=get_top_formadores_pendentes()
        pend_proj=get_pendente_por_projeto()
        cf_l,cf_s=get_cashflow_previsto()
        hist_bd=get_historico_financeiro()
    else:
        pre_dados=filtrar_proj(st.session_state.mock_pre,filtro)
        venc_dados=filtrar_datas(filtrar_proj(st.session_state.mock_vencidas,filtro),d_ini,d_fim)
        aven_dados=filtrar_datas(filtrar_proj(st.session_state.mock_a_vencer,filtro),d_ini,d_fim)
        top5=[{"formador":"João Silva","valor":5000},{"formador":"Rui Mendes","valor":4900},{"formador":"Pedro Costa","valor":3300},{"formador":"Ana Ferreira","valor":2800},{"formador":"Carla Neves","valor":2100}]
        pend_proj=[{"projeto":"MENTORES","valor":5000},{"projeto":"PRODUTECH","valor":4400},{"projeto":"CALÇADO","valor":3300},{"projeto":"ANIET","valor":2800},{"projeto":"APIMA","valor":2300},{"projeto":"APCMC","valor":2100}]
        cf_l,cf_s=_MOCK_CF_LABELS,_MOCK_CF_SAIDAS
        hist_bd=[]

    venc_dados=ordenar(venc_dados,ordem)
    aven_dados=ordenar(aven_dados,ordem)
    tv=sum(f.get("valor") or 0 for f in venc_dados)
    ta=sum(f.get("valor") or 0 for f in aven_dados)

    # KPIs
    st.markdown(
        '<div class="kpi-row">'
        + kpi("🚨 Vencido",        fmt_eur(tv),         f"{len(venc_dados)} faturas","red")
        + kpi("⏳ A vencer 30d",   fmt_eur(ta),         f"{len(aven_dados)} faturas","amber")
        + kpi("💳 Pago este mês",  fmt_eur(121400),      "23 faturas",               "blue")
        + kpi("💰 Total pendente", fmt_eur(tv+ta),       f"{len(venc_dados)+len(aven_dados)} faturas","purple")
        + '</div>', unsafe_allow_html=True
    )

    st.markdown('<div class="sec-divider"></div>',unsafe_allow_html=True)

    # ---- PRÉ-APROVAÇÃO ----
    st.markdown(sec_header(f"🔍 Aprovação manual ({len(pre_dados)} pendentes)","Faturas cuja validação automática falhou."),unsafe_allow_html=True)

    if not pre_dados:
        st.markdown('<div class="empty-state">✅ Nenhuma fatura pendente de aprovação manual.</div>',unsafe_allow_html=True)
    else:
        for i,row in enumerate(pre_dados):
            fid=row.get("id") or str(i)
            n_fat=row.get("numero_fatura") or "—"
            formador=_row_formador(row); email_fm=_row_email(row)
            projeto=_row_projeto(row); valor=row.get("valor") or 0
            erro=row.get("erro_leitura") or row.get("notas") or "—"
            data_sub=str(row.get("created_at") or "—")[:10]
            ficheiro=row.get("ficheiro_url")

            col_info,col_pdf,col_acao=st.columns([5,1,3])
            with col_info:
                st.markdown(
                    f'<div class="aprov-card">'
                    f'<div style="display:flex;gap:8px;align-items:center;margin-bottom:4px">'
                    f'<span style="font-weight:700;font-size:14px">{n_fat}</span>'
                    f'&nbsp;{proj_tag(projeto)}'
                    f'</div>'
                    f'<div style="font-size:13px;color:#4B5263"><strong>Formador:</strong> {formador} &nbsp;·&nbsp; <strong>Valor:</strong> {fmt_eur(valor)}</div>'
                    f'<div class="erro">⚠️ {erro}</div>'
                    f'<div class="data-sub">Submetida: {data_sub}</div>'
                    f'</div>', unsafe_allow_html=True
                )
            with col_pdf:
                st.markdown("<div style='margin-top:12px'>",unsafe_allow_html=True)
                if ficheiro: st.link_button("📄 PDF",ficheiro)
                else: st.caption("—")
                st.markdown("</div>",unsafe_allow_html=True)
            with col_acao:
                st.markdown("<div style='margin-top:12px'>",unsafe_allow_html=True)
                if st.button("✅ Aprovar",key=f"apr_{i}_{fid}",use_container_width=True):
                    if SUPABASE_OK:
                        if aprovar_fatura(fid,user_nome):
                            reg_historico("Aprovado",n_fat,formador,projeto,valor)
                            st.toast(f"{n_fat} aprovada."); st.rerun()
                    else:
                        st.session_state.mock_pre=[f for f in st.session_state.mock_pre if f.get("id")!=fid]
                        reg_historico("Aprovado",n_fat,formador,projeto,valor)
                        st.toast(f"{n_fat} aprovada."); st.rerun()
                motivo=st.text_input("",key=f"mot_{i}_{fid}",placeholder="Motivo de rejeição…",label_visibility="collapsed")
                if st.button("❌ Rejeitar",key=f"rej_{i}_{fid}",use_container_width=True):
                    if motivo:
                        if SUPABASE_OK:
                            if rejeitar_fatura(fid,motivo,user_nome):
                                reg_historico("Rejeitado",n_fat,formador,projeto,valor,motivo)
                                st.toast(f"{n_fat} rejeitada."); st.rerun()
                        else:
                            st.session_state.mock_pre=[f for f in st.session_state.mock_pre if f.get("id")!=fid]
                            reg_historico("Rejeitado",n_fat,formador,projeto,valor,motivo)
                            st.toast(f"{n_fat} rejeitada."); st.rerun()
                    else: st.warning("Escreve um motivo antes de rejeitar.")
                st.markdown("</div>",unsafe_allow_html=True)

    # Upload PDF
    with st.expander("📤 Ler fatura PDF manualmente"):
        up=st.file_uploader("PDF",type=["pdf"],key="pdf_up")
        if up:
            d=extrair_pdf(up.read())
            if d.get("erro"): st.error(f"Erro: {d['erro']}")
            else:
                c1,c2,c3,c4=st.columns(4)
                c1.metric("Nº Fatura",d.get("numero_fatura") or "—")
                c2.metric("NIF",d.get("nif_emitente") or "—")
                c3.metric("Valor",fmt_eur(d.get("valor") or 0))
                c4.metric("Data",d.get("data_fatura") or "—")

    st.markdown('<div class="sec-divider"></div>',unsafe_allow_html=True)

    # ---- VENCIDAS ----
    st.markdown(sec_header("🔴 Faturas vencidas"),unsafe_allow_html=True)
    PAGE=10
    pv=st.session_state.get("pag_v",0)
    pag_v=venc_dados[pv*PAGE:(pv+1)*PAGE]
    if not venc_dados:
        st.markdown('<div class="empty-state">Nenhuma fatura vencida para este filtro.</div>',unsafe_allow_html=True)
    else:
        for i,row in enumerate(pag_v): _card_fatura(row,"vencida",pv*PAGE+i,user_nome)
        st.markdown(f"**Total vencido: {fmt_eur(tv)}**")
        tp=max(1,(len(venc_dados)+PAGE-1)//PAGE)
        if tp>1:
            c1,c2,c3=st.columns([1,2,1])
            if c1.button("← Anterior",key="prev_v",disabled=pv==0): st.session_state.pag_v=pv-1; st.rerun()
            c2.markdown(f"<div style='text-align:center;padding-top:8px'>Página {pv+1}/{tp}</div>",unsafe_allow_html=True)
            if c3.button("Próxima →",key="next_v",disabled=pv>=tp-1): st.session_state.pag_v=pv+1; st.rerun()
        st.download_button("⬇️ Exportar Excel",gerar_excel(filtro,venc_dados),f"vencidas_{filtro}.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.markdown('<div class="sec-divider"></div>',unsafe_allow_html=True)

    # ---- A VENCER ----
    st.markdown(sec_header("🟡 A vencer — próximos 30 dias"),unsafe_allow_html=True)
    pa=st.session_state.get("pag_a",0)
    pag_a=aven_dados[pa*PAGE:(pa+1)*PAGE]
    if not aven_dados:
        st.markdown('<div class="empty-state">Nenhuma fatura a vencer para este filtro.</div>',unsafe_allow_html=True)
    else:
        for i,row in enumerate(pag_a): _card_fatura(row,"avencer",pa*PAGE+i,user_nome)
        st.markdown(f"**Total a vencer: {fmt_eur(ta)}**")
        tp=max(1,(len(aven_dados)+PAGE-1)//PAGE)
        if tp>1:
            c1,c2,c3=st.columns([1,2,1])
            if c1.button("← Anterior",key="prev_a",disabled=pa==0): st.session_state.pag_a=pa-1; st.rerun()
            c2.markdown(f"<div style='text-align:center;padding-top:8px'>Página {pa+1}/{tp}</div>",unsafe_allow_html=True)
            if c3.button("Próxima →",key="next_a",disabled=pa>=tp-1): st.session_state.pag_a=pa+1; st.rerun()
        st.download_button("⬇️ Exportar Excel",gerar_excel(filtro,aven_dados),f"avencer_{filtro}.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.markdown('<div class="sec-divider"></div>',unsafe_allow_html=True)

    # ---- TOP 5 + POR PROJETO ----
    c_l,c_r=st.columns(2)
    with c_l:
        st.markdown(sec_header("Top 5 formadores pendentes"),unsafe_allow_html=True)
        for i,row in enumerate(top5):
            st.markdown(
                f'<div class="fatura-card" style="padding:10px 14px">'
                f'<span style="font-size:12px;font-weight:700;color:#8B94A3;min-width:24px">#{i+1}</span>'
                f'<span style="flex:1;font-size:13px">{row["formador"]}</span>'
                f'<span style="font-weight:700;font-size:14px">{fmt_eur(row["valor"])}</span>'
                f'</div>', unsafe_allow_html=True
            )
    with c_r:
        st.markdown(sec_header("Pendente por projeto"),unsafe_allow_html=True)
        for row in pend_proj:
            cor=CORES_PROJETO.get(row["projeto"],"#888")
            st.markdown(
                f'<div class="fatura-card" style="padding:10px 14px">'
                f'<span style="width:8px;height:8px;border-radius:50%;background:{cor};display:inline-block;margin-right:8px;flex-shrink:0"></span>'
                f'<span style="flex:1;font-size:13px">{row["projeto"]}</span>'
                f'<span style="font-weight:700;font-size:14px">{fmt_eur(row["valor"])}</span>'
                f'</div>', unsafe_allow_html=True
            )

    st.markdown('<div class="sec-divider"></div>',unsafe_allow_html=True)

    # ---- CASHFLOW ----
    st.markdown(sec_header("Cashflow previsto — próximos 90 dias"),unsafe_allow_html=True)
    if cf_s:
        acum,tot=[],0
        for v in cf_s: tot+=v; acum.append(tot)
        fig=go.Figure()
        fig.add_trace(go.Bar(x=cf_l,y=cf_s,name="Saída semanal",marker_color="#FBBF24",yaxis="y1"))
        fig.add_trace(go.Scatter(x=cf_l,y=acum,name="Acumulado",line=dict(color="#2563EB",width=2),mode="lines+markers",yaxis="y2"))
        fig.update_layout(
            height=320, margin=dict(t=20,b=60,l=50,r=60),
            legend=dict(orientation="h",yanchor="bottom",y=1.02,font=dict(size=11)),
            yaxis=dict(title="Saída semanal (€)",showgrid=False,tickfont=dict(size=11)),
            yaxis2=dict(title="Acumulado (€)",overlaying="y",side="right",showgrid=False,tickfont=dict(size=11)),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickangle=45,automargin=True,tickfont=dict(size=11)),
        )
        st.plotly_chart(fig,use_container_width=True,config=PLOTLY_CFG)

    st.markdown('<div class="sec-divider"></div>',unsafe_allow_html=True)

    # ---- HISTÓRICO ----
    st.markdown(sec_header("📋 Histórico de ações"),unsafe_allow_html=True)
    hist=st.session_state.historico[::-1]
    if hist:
        df=pd.DataFrame(hist)
        df.columns=["Data/Hora","Ação","Nº Fatura","Formador","Projeto","Valor","Motivo"]
        df["Valor"]=df["Valor"].apply(fmt_eur)
        st.dataframe(df,use_container_width=True,hide_index=True)
        st.download_button("⬇️ Exportar CSV",df.to_csv(index=False).encode(),"historico.csv","text/csv")
    elif hist_bd:
        df=pd.DataFrame([{"Data/Hora":str(h.get("criado_em",""))[:16],"Ação":h.get("tipo",""),"Detalhe":h.get("descricao","")} for h in hist_bd])
        st.dataframe(df,use_container_width=True,hide_index=True)
    else:
        st.markdown('<div class="empty-state">Nenhuma ação registada nesta sessão.</div>',unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# RENDER PRINCIPAL
# ---------------------------------------------------------------------------
def render(user: dict):
    init_state()
    st.markdown(DESIGN_CSS, unsafe_allow_html=True)

    st.header(f"Bem-vindo, {user['nome']}")
    st.caption("Perfil: Financeiro")

    if SUPABASE_OK:
        try: n_pre=len(get_faturas_pre_aprovacao())
        except: n_pre=0
    else:
        n_pre=len(st.session_state.mock_pre)

    label_alertas=f"⚠️ Alertas/A Pagar ({n_pre})" if n_pre>0 else "⚠️ Alertas/A Pagar"

    try:
        from app.financeiro_consultores import _get_faturas_consultores_pendentes
        n_fc=len(_get_faturas_consultores_pendentes())
    except: n_fc=0
    label_cons=f"🤝 Consultores ({n_fc})" if n_fc>0 else "🤝 Consultores"

    tab1,tab2,tab3,tab4=st.tabs(["💶 Dashboard Financeiro",label_alertas,label_cons,"💳 Faturação Empresas"])

    with tab1: render_dashboard(user)
    with tab2: render_alertas(user)
    with tab3:
        try:
            from app.financeiro_consultores import render_consultores
            render_consultores(user)
        except Exception as e:
            st.error(f"Erro na tab consultores: {e}")
    with tab4:
        st.markdown('<div class="empty-state" style="margin-top:40px">🚧 Em construção — histórico de pagamentos por empresa.</div>',unsafe_allow_html=True)
