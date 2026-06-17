"""Pagina do financeiro."""
from __future__ import annotations
import io
from datetime import date, datetime
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

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
# CSS GLOBAL — injectado uma vez no topo do render
# ---------------------------------------------------------------------------
_CSS = """
<style>
.fin-kpi-row{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0 24px}
.fin-kpi{background:#fff;border:1px solid #E4E7EF;border-radius:12px;
         padding:16px 18px;flex:1;min-width:130px}
.fin-kpi.r{border-top:3px solid #DC2626}
.fin-kpi.a{border-top:3px solid #D97706}
.fin-kpi.b{border-top:3px solid #2563EB}
.fin-kpi.g{border-top:3px solid #16A34A}
.fin-kpi.p{border-top:3px solid #7C3AED}
.fin-kpi .lbl{font-size:11px;font-weight:600;color:#8B94A3;
              text-transform:uppercase;letter-spacing:.06em;margin:0 0 5px}
.fin-kpi .val{font-size:23px;font-weight:700;color:#1A1F2E;margin:0;line-height:1.1}
.fin-kpi .sub{font-size:12px;color:#8B94A3;margin:3px 0 0}

.fin-card{background:#fff;border:1px solid #E4E7EF;border-radius:10px;
          padding:12px 14px;margin-bottom:8px;display:flex;
          align-items:center;gap:10px}
.fin-card.vc{border-left:3px solid #DC2626;background:#FEF2F2}
.fin-card.av{border-left:3px solid #D97706}
.fin-card .ct{font-weight:600;font-size:14px;color:#1A1F2E}
.fin-card .cm{font-size:12px;color:#8B94A3;margin-top:2px}
.fin-card .cd{font-size:11px;color:#8B94A3;margin-top:2px}
.fin-card .cv{font-weight:700;font-size:15px;color:#1A1F2E;white-space:nowrap}
.fin-card .dr{font-size:12px;color:#DC2626;margin-top:1px}
.fin-card .da{font-size:12px;color:#D97706;margin-top:1px}

.fin-badge{display:inline-block;font-size:11px;font-weight:600;
           padding:2px 8px;border-radius:20px;white-space:nowrap}
.fin-ptag{display:inline-block;font-size:11px;font-weight:700;
          padding:1px 7px;border-radius:4px}

.fin-sec{font-size:13px;font-weight:700;color:#4B5263;
         text-transform:uppercase;letter-spacing:.06em;margin:0 0 3px}
.fin-secs{font-size:12px;color:#8B94A3;margin:0 0 12px}
.fin-div{height:1px;background:#E4E7EF;margin:24px 0 20px}

.fin-warn{background:#FFFBEB;border:1px solid #FCD34D;
          border-left:3px solid #D97706;border-radius:8px;
          padding:9px 14px;font-size:13px;color:#92400E;margin-bottom:16px}
.fin-empty{background:#F7F8FC;border:1px dashed #E4E7EF;border-radius:10px;
           padding:20px;text-align:center;color:#8B94A3;font-size:13px;margin-bottom:8px}
.fin-aprov{background:#fff;border:1px solid #E4E7EF;border-radius:10px;
           padding:14px;margin-bottom:10px}
.fin-aprov .err{font-size:12px;color:#DC2626;margin-top:3px}
.fin-aprov .ds{font-size:11px;color:#8B94A3;margin-top:2px}
</style>
"""

# ---------------------------------------------------------------------------
# MOCK DATA
# ---------------------------------------------------------------------------
_MOCK_PROJETOS = [
    {"id":"p1","nome":"MENTORES"}, {"id":"p2","nome":"ANIET"},
    {"id":"p3","nome":"APCMC"},    {"id":"p4","nome":"APIMA"},
    {"id":"p5","nome":"PRODUTECH"},{"id":"p6","nome":"CALÇADO"},
]
_MOCK_PRE = [
    {"id":"f1","numero_fatura":"FT2026/0155","valor":2400,"estado":"leitura_falhada",  "erro_leitura":"Código interno não encontrado","created_at":"2026-06-15","ficheiro_url":None,"profiles":{"nome":"Miguel Santos",  "email":"miguel@demo.pt"},"acoes":{"nome":"MENTORES"}},
    {"id":"f2","numero_fatura":"FT2026/0153","valor":1950,"estado":"acao_nao_fechada", "erro_leitura":"Nome do formador não corresponde","created_at":"2026-06-14","ficheiro_url":None,"profiles":{"nome":"Sofia Rodrigues","email":"sofia@demo.pt"}, "acoes":{"nome":"ANIET"}},
    {"id":"f3","numero_fatura":"FT2026/0150","valor":1800,"estado":"submetida",        "erro_leitura":"Valor diverge do contrato","created_at":"2026-06-13","ficheiro_url":None,"profiles":{"nome":"Luís Cardoso",   "email":"luis@demo.pt"},  "acoes":{"nome":"PRODUTECH"}},
]
_MOCK_VENC = [
    {"id":"v1","numero_fatura":"FT2026/0110","valor":1800,"prazo_pagamento":"2026-06-02","data_fatura":"2026-05-02","atraso":14,"profiles":{"nome":"João Silva", "email":"joao@demo.pt"},"acoes":{"nome":"MENTORES"}},
    {"id":"v2","numero_fatura":"FT2026/0108","valor":2600,"prazo_pagamento":"2026-06-08","data_fatura":"2026-05-08","atraso":8, "profiles":{"nome":"Rui Mendes", "email":"rui@demo.pt"}, "acoes":{"nome":"PRODUTECH"}},
    {"id":"v3","numero_fatura":"FT2026/0105","valor":1400,"prazo_pagamento":"2026-06-12","data_fatura":"2026-05-12","atraso":4, "profiles":{"nome":"Pedro Costa","email":"pedro@demo.pt"},"acoes":{"nome":"CALÇADO"}},
]
_MOCK_AV = [
    {"id":"a1","numero_fatura":"FT2026/0142","valor":3200,"prazo_pagamento":"2026-06-21","data_fatura":"2026-06-01","dias":5, "profiles":{"nome":"João Silva",  "email":"joao@demo.pt"}, "acoes":{"nome":"MENTORES"}},
    {"id":"a2","numero_fatura":"FT2026/0138","valor":2800,"prazo_pagamento":"2026-06-27","data_fatura":"2026-06-03","dias":11,"profiles":{"nome":"Ana Ferreira","email":"ana@demo.pt"},  "acoes":{"nome":"ANIET"}},
    {"id":"a3","numero_fatura":"FT2026/0136","valor":1900,"prazo_pagamento":"2026-07-04","data_fatura":"2026-06-05","dias":18,"profiles":{"nome":"Pedro Costa", "email":"pedro@demo.pt"},"acoes":{"nome":"CALÇADO"}},
    {"id":"a4","numero_fatura":"FT2026/0129","valor":2100,"prazo_pagamento":"2026-07-10","data_fatura":"2026-06-06","dias":24,"profiles":{"nome":"Carla Neves", "email":"carla@demo.pt"},"acoes":{"nome":"APCMC"}},
    {"id":"a5","numero_fatura":"FT2026/0127","valor":2300,"prazo_pagamento":"2026-07-16","data_fatura":"2026-06-08","dias":30,"profiles":{"nome":"Rui Mendes",  "email":"rui@demo.pt"},  "acoes":{"nome":"APIMA"}},
]
_MOCK_CF_L = ["S1 Jun","S2 Jun","S3 Jun","S4 Jun","S1 Jul","S2 Jul","S3 Jul","S4 Jul","S1 Ago","S2 Ago","S3 Ago","S4 Ago","S1 Set"]
_MOCK_CF_S = [3200,2100,4100,2800,2600,3800,1900,3200,2400,2800,1800,2100,2300]

PLOTLY_CFG = {"displayModeBar": False}
ORDEM = ["Data de vencimento","Valor (maior primeiro)","Valor (menor primeiro)","Projeto"]

CORES = {"MENTORES":"#2563EB","ANIET":"#16A34A","APCMC":"#D97706",
         "APIMA":"#9D174D","PRODUTECH":"#7C3AED","CALÇADO":"#0F766E"}
BGS   = {"MENTORES":"#EEF3FD","ANIET":"#F0FDF4","APCMC":"#FFFBEB",
         "APIMA":"#FDF2F8","PRODUTECH":"#F5F3FF","CALÇADO":"#F0FDFA"}

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def _formador(r): return (r.get("profiles") or {}).get("nome") or "—"
def _projeto(r):  return (r.get("acoes")    or {}).get("nome") or "—"
def _email(r):    return (r.get("profiles") or {}).get("email") or ""

def eur(v):
    try: return f"€\u202f{float(v):,.0f}".replace(",",".")
    except: return "€ —"

def ptag(p):
    c=CORES.get(p,"#6B7280"); b=BGS.get(p,"#F3F4F6")
    return f'<span class="fin-ptag" style="background:{b};color:{c}">{p}</span>'

def bdg(estado):
    M={"submetida":("#FFFBEB","#D97706","Submetida"),
       "leitura_falhada":("#FEF2F2","#DC2626","Leitura falhada"),
       "acao_nao_fechada":("#FEF2F2","#DC2626","Ação não fechada"),
       "aprovada":("#F0FDF4","#16A34A","Aprovada"),
       "paga":("#EEF3FD","#2563EB","Paga"),
       "rejeitada":("#F3F4F6","#6B7280","Rejeitada"),
       "Pendente":("#FFFBEB","#D97706","Pendente"),
       "Aprovado":("#F0FDF4","#16A34A","Aprovado"),
       "Pago":("#EEF3FD","#2563EB","Pago"),}
    bg,c,l=M.get(estado,("#F3F4F6","#6B7280",estado))
    return f'<span class="fin-badge" style="background:{bg};color:{c}">{l}</span>'

def kpi_h(lbl,val,sub,v=""):
    cls=f"fin-kpi {v}" if v else "fin-kpi"
    return f'<div class="{cls}"><p class="lbl">{lbl}</p><p class="val">{val}</p><p class="sub">{sub}</p></div>'

def sec(titulo,sub=""):
    s=f'<p class="fin-secs">{sub}</p>' if sub else ""
    return f'<p class="fin-sec">{titulo}</p>{s}'

def div():
    return '<div class="fin-div"></div>'

def ordenar(d,c):
    if c=="Valor (maior primeiro)": return sorted(d,key=lambda x:x.get("valor") or 0,reverse=True)
    if c=="Valor (menor primeiro)": return sorted(d,key=lambda x:x.get("valor") or 0)
    if c=="Projeto": return sorted(d,key=lambda x:_projeto(x))
    col="atraso" if d and "atraso" in d[0] else "dias"
    return sorted(d,key=lambda x:x.get(col) or 0,reverse=True)

def fil_proj(d,p):
    if not p or p=="Todos": return d
    return [x for x in d if _projeto(x)==p]

def fil_datas(d,ini,fim):
    if not ini and not fim: return d
    out=[]
    for x in d:
        ps=x.get("prazo_pagamento")
        if not ps: out.append(x); continue
        try:
            p=date.fromisoformat(ps)
            if ini and p<ini: continue
            if fim and p>fim: continue
        except: pass
        out.append(x)
    return out

def excel_bytes(proj,faturas):
    rows=[{"Nº Fatura":f.get("numero_fatura") or "—","Formador":_formador(f),
           "Projeto":_projeto(f),"Valor (€)":f.get("valor") or 0,
           "Prazo":f.get("prazo_pagamento") or "—","Estado":f.get("estado") or "—"} for f in faturas]
    buf=io.BytesIO()
    pd.DataFrame(rows).to_excel(buf,index=False,engine="openpyxl")
    return buf.getvalue()

def extrair_pdf(b):
    import re,io as _io
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
# SESSION STATE
# ---------------------------------------------------------------------------
def init_state():
    if "historico" not in st.session_state: st.session_state.historico=[]
    if not SUPABASE_OK:
        if "mock_pre"  not in st.session_state: st.session_state.mock_pre=list(_MOCK_PRE)
        if "mock_venc" not in st.session_state: st.session_state.mock_venc=list(_MOCK_VENC)
        if "mock_av"   not in st.session_state: st.session_state.mock_av=list(_MOCK_AV)

def reg_hist(acao,n,form,proj,val,mot=""):
    st.session_state.historico.append({"timestamp":datetime.now().strftime("%d/%m/%Y %H:%M"),
        "acao":acao,"n_fatura":n,"formador":form,"projeto":proj,"valor":val,"motivo":mot})

# ---------------------------------------------------------------------------
# TAB 1 — DASHBOARD
# ---------------------------------------------------------------------------
def render_dashboard(user):
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

    if n_pre>0:
        st.markdown(f'<div class="fin-warn">⚠️ <strong>{n_pre} fatura(s) aguardam aprovação manual</strong> — ver em <strong>Alertas/A Pagar</strong>.</div>',unsafe_allow_html=True)

    st.markdown(
        '<div class="fin-kpi-row">'
        +kpi_h("🔍 Pré-aprovação",   eur(tp),    f"{n_pre} faturas","a")
        +kpi_h("✅ Aprovado a pagar",eur(ta),    f"{n_apr} faturas","g")
        +kpi_h("💳 Pago este mês",   eur(tpago), f"{n_pago} faturas","b")
        +kpi_h("🚨 Vencido",         eur(tv),    f"{n_venc} faturas","r")
        +'</div>',unsafe_allow_html=True
    )

    st.markdown(div(),unsafe_allow_html=True)

    col_l,col_r=st.columns([3,2])

    with col_l:
        st.markdown(sec("Faturas recentes"),unsafe_allow_html=True)
        cards_html=""
        for row in recentes:
            f=_formador(row); p=_projeto(row)
            e=row.get("estado") or "submetida"
            n=row.get("numero_fatura") or "—"; v=row.get("valor") or 0
            cards_html+=(
                f'<div class="fin-card">'
                f'<div style="flex:1">'
                f'<div class="ct">{n}</div>'
                f'<div class="cm">{ptag(p)}&nbsp;·&nbsp;{f}</div>'
                f'</div>'
                f'<div style="text-align:right;margin-right:10px">'
                f'<div class="cv">{eur(v)}</div>'
                f'</div>'
                f'{bdg(e)}'
                f'</div>'
            )
        st.markdown(cards_html,unsafe_allow_html=True)

    with col_r:
        st.markdown(sec("Por estado"),unsafe_allow_html=True)
        fig=go.Figure(go.Pie(
            labels=["Pré-aprovação","Aprovado","Pago","Vencido"],
            values=[n_pre or 1,n_apr or 1,n_pago or 1,n_venc or 1],
            hole=0.65,
            marker_colors=["#D97706","#16A34A","#2563EB","#DC2626"],
            textinfo="percent", textfont=dict(size=11),
            showlegend=True,
        ))
        fig.update_layout(
            margin=dict(t=10,b=10,l=0,r=10),height=270,
            legend=dict(orientation="v",x=1.0,y=0.5,font=dict(size=11),
                       xanchor="left",yanchor="middle"),
            paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig,use_container_width=True,config=PLOTLY_CFG)

    st.markdown(div(),unsafe_allow_html=True)
    st.markdown(sec("Despesa por projeto"),unsafe_allow_html=True)

    ds=sorted(despesa,key=lambda x:x["valor"])
    mx=max((d["valor"] for d in ds),default=1)
    fig2=go.Figure(go.Bar(
        x=[d["valor"] for d in ds],y=[d["projeto"] for d in ds],
        orientation="h",
        marker_color=[CORES.get(d["projeto"],"#888") for d in ds],
        text=[eur(d["valor"]) for d in ds],textposition="outside",
        textfont=dict(size=12),
    ))
    fig2.update_layout(
        margin=dict(t=4,b=4,l=4,r=110),height=270,
        xaxis=dict(showticklabels=False,showgrid=False,range=[0,mx*1.3]),
        yaxis=dict(showgrid=False,tickfont=dict(size=13)),
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig2,use_container_width=True,config=PLOTLY_CFG)

# ---------------------------------------------------------------------------
# CARD FATURA — componente reutilizado
# ---------------------------------------------------------------------------
def _card(row,tipo,idx,user_nome):
    fid=row.get("id") or str(idx)
    n=row.get("numero_fatura") or "—"
    f=_formador(row); p=_projeto(row); v=row.get("valor") or 0
    df=row.get("data_fatura") or "—"; dp=row.get("prazo_pagamento") or "—"

    if tipo=="vencida":
        atraso=row.get("atraso") or 0
        cls="fin-card vc"
        dias_h=f'<div class="dr">+{atraso} dias em atraso</div>'
    else:
        dias=row.get("dias") or 0
        cls="fin-card av"
        dias_h=f'<div class="da">vence em {dias} dias</div>'

    col_c,col_b=st.columns([5,2])
    with col_c:
        st.markdown(
            f'<div class="{cls}">'
            f'<div style="flex:1">'
            f'<div class="ct">{n} <span style="font-size:12px;font-weight:400;color:#8B94A3">{f}</span></div>'
            f'<div class="cm">{ptag(p)}</div>'
            f'<div class="cd">Emissão {df} · Prazo {dp}</div>'
            f'</div>'
            f'<div style="text-align:right;min-width:85px">'
            f'<div class="cv">{eur(v)}</div>'
            f'{dias_h}'
            f'</div>'
            f'</div>',unsafe_allow_html=True
        )
    with col_b:
        if st.button("✓ Marcar pago",key=f"pg_{tipo}_{idx}_{fid}",use_container_width=True):
            if SUPABASE_OK:
                if marcar_paga(fid,user_nome):
                    reg_hist("Marcado pago",n,f,p,v); st.toast(f"{n} marcada como paga."); st.rerun()
            else:
                key="mock_venc" if tipo=="vencida" else "mock_av"
                st.session_state[key]=[x for x in st.session_state[key] if x.get("id")!=fid]
                reg_hist("Marcado pago",n,f,p,v); st.toast(f"{n} marcada como paga."); st.rerun()

# ---------------------------------------------------------------------------
# TAB 2 — ALERTAS
# ---------------------------------------------------------------------------
def render_alertas(user):
    user_nome=user.get("nome") or "Financeiro"

    col_f,col_o,col_d1,col_d2=st.columns([2,2,1,1])
    with col_f:
        pjs=get_projetos() if SUPABASE_OK else _MOCK_PROJETOS
        filtro=st.selectbox("Projeto",["Todos"]+[p["nome"] for p in pjs],key="fil_p")
    with col_o:
        ordem=st.selectbox("Ordenar",ORDEM,key="ord_f")
    with col_d1:
        d_ini=st.date_input("De",value=None,key="d_i",format="DD/MM/YYYY")
    with col_d2:
        d_fim=st.date_input("Até",value=None,key="d_f",format="DD/MM/YYYY")

    if SUPABASE_OK:
        pre=get_faturas_pre_aprovacao(filtro if filtro!="Todos" else None)
        venc=fil_datas(fil_proj(get_faturas_vencidas(),filtro),d_ini,d_fim)
        av=fil_datas(fil_proj(get_faturas_a_vencer(),filtro),d_ini,d_fim)
        top5=get_top_formadores_pendentes()
        pp=get_pendente_por_projeto()
        cfl,cfs=get_cashflow_previsto()
        hist_bd=get_historico_financeiro()
    else:
        pre=fil_proj(st.session_state.mock_pre,filtro)
        venc=fil_datas(fil_proj(st.session_state.mock_venc,filtro),d_ini,d_fim)
        av=fil_datas(fil_proj(st.session_state.mock_av,filtro),d_ini,d_fim)
        top5=[{"formador":"João Silva","valor":5000},{"formador":"Rui Mendes","valor":4900},{"formador":"Pedro Costa","valor":3300},{"formador":"Ana Ferreira","valor":2800},{"formador":"Carla Neves","valor":2100}]
        pp=[{"projeto":"MENTORES","valor":5000},{"projeto":"PRODUTECH","valor":4400},{"projeto":"CALÇADO","valor":3300},{"projeto":"ANIET","valor":2800},{"projeto":"APIMA","valor":2300},{"projeto":"APCMC","valor":2100}]
        cfl,cfs=_MOCK_CF_L,_MOCK_CF_S
        hist_bd=[]

    venc=ordenar(venc,ordem); av=ordenar(av,ordem)
    tv=sum(f.get("valor") or 0 for f in venc)
    ta=sum(f.get("valor") or 0 for f in av)

    st.markdown(
        '<div class="fin-kpi-row">'
        +kpi_h("🚨 Vencido",       eur(tv),      f"{len(venc)} faturas","r")
        +kpi_h("⏳ A vencer 30d",  eur(ta),      f"{len(av)} faturas","a")
        +kpi_h("💳 Pago este mês", eur(121400),  "23 faturas","b")
        +kpi_h("💰 Total pendente",eur(tv+ta),   f"{len(venc)+len(av)} faturas","p")
        +'</div>',unsafe_allow_html=True
    )

    st.markdown(div(),unsafe_allow_html=True)

    # ---- PRÉ-APROVAÇÃO ----
    st.markdown(sec(f"🔍 Aprovação manual ({len(pre)} pendentes)","Faturas cuja validação automática falhou."),unsafe_allow_html=True)

    if not pre:
        st.markdown('<div class="fin-empty">✅ Nenhuma fatura pendente de aprovação manual.</div>',unsafe_allow_html=True)
    else:
        for i,row in enumerate(pre):
            fid=row.get("id") or str(i)
            n=row.get("numero_fatura") or "—"; f=_formador(row); em=_email(row)
            p=_projeto(row); v=row.get("valor") or 0
            erro=row.get("erro_leitura") or row.get("notas") or "—"
            ds=str(row.get("created_at") or "—")[:10]; fich=row.get("ficheiro_url")

            col_i,col_pdf,col_a=st.columns([5,1,3])
            with col_i:
                st.markdown(
                    f'<div class="fin-aprov">'
                    f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">'
                    f'<span style="font-weight:700;font-size:14px">{n}</span>{ptag(p)}'
                    f'</div>'
                    f'<div style="font-size:13px;color:#4B5263"><b>Formador:</b> {f} &nbsp;·&nbsp; <b>Valor:</b> {eur(v)}</div>'
                    f'<div class="err">⚠️ {erro}</div>'
                    f'<div class="ds">Submetida: {ds}</div>'
                    f'</div>',unsafe_allow_html=True
                )
            with col_pdf:
                st.markdown("<div style='margin-top:10px'>",unsafe_allow_html=True)
                if fich: st.link_button("📄",fich)
                else: st.caption("—")
                st.markdown("</div>",unsafe_allow_html=True)
            with col_a:
                st.markdown("<div style='margin-top:10px'>",unsafe_allow_html=True)
                if st.button("✅ Aprovar",key=f"ap_{i}_{fid}",use_container_width=True):
                    if SUPABASE_OK:
                        if aprovar_fatura(fid,user_nome):
                            reg_hist("Aprovado",n,f,p,v); st.toast(f"{n} aprovada."); st.rerun()
                    else:
                        st.session_state.mock_pre=[x for x in st.session_state.mock_pre if x.get("id")!=fid]
                        reg_hist("Aprovado",n,f,p,v); st.toast(f"{n} aprovada."); st.rerun()
                mot=st.text_input("",key=f"mt_{i}_{fid}",placeholder="Motivo de rejeição…",label_visibility="collapsed")
                if st.button("❌ Rejeitar",key=f"rj_{i}_{fid}",use_container_width=True):
                    if mot:
                        if SUPABASE_OK:
                            if rejeitar_fatura(fid,mot,user_nome):
                                reg_hist("Rejeitado",n,f,p,v,mot); st.toast(f"{n} rejeitada."); st.rerun()
                        else:
                            st.session_state.mock_pre=[x for x in st.session_state.mock_pre if x.get("id")!=fid]
                            reg_hist("Rejeitado",n,f,p,v,mot); st.toast(f"{n} rejeitada."); st.rerun()
                    else: st.warning("Escreve um motivo.")
                st.markdown("</div>",unsafe_allow_html=True)

    with st.expander("📤 Ler fatura PDF manualmente"):
        up=st.file_uploader("PDF",type=["pdf"],key="pdf_up")
        if up:
            d=extrair_pdf(up.read())
            if d.get("erro"): st.error(f"Erro: {d['erro']}")
            else:
                c1,c2,c3,c4=st.columns(4)
                c1.metric("Nº Fatura",d.get("numero_fatura") or "—")
                c2.metric("NIF",d.get("nif_emitente") or "—")
                c3.metric("Valor",eur(d.get("valor") or 0))
                c4.metric("Data",d.get("data_fatura") or "—")

    st.markdown(div(),unsafe_allow_html=True)

    # ---- VENCIDAS ----
    st.markdown(sec("🔴 Faturas vencidas"),unsafe_allow_html=True)
    PAGE=10; pv=st.session_state.get("pag_v",0)
    pagv=venc[pv*PAGE:(pv+1)*PAGE]
    if not venc:
        st.markdown('<div class="fin-empty">Nenhuma fatura vencida para este filtro.</div>',unsafe_allow_html=True)
    else:
        for i,row in enumerate(pagv): _card(row,"vencida",pv*PAGE+i,user_nome)
        st.markdown(f"**Total vencido: {eur(tv)}**")
        tp_=max(1,(len(venc)+PAGE-1)//PAGE)
        if tp_>1:
            c1,c2,c3=st.columns([1,2,1])
            if c1.button("← Anterior",key="pv_p",disabled=pv==0): st.session_state.pag_v=pv-1; st.rerun()
            c2.markdown(f"<div style='text-align:center;padding-top:8px'>Página {pv+1}/{tp_}</div>",unsafe_allow_html=True)
            if c3.button("Próxima →",key="pv_n",disabled=pv>=tp_-1): st.session_state.pag_v=pv+1; st.rerun()
        st.download_button("⬇️ Excel vencidas",excel_bytes(filtro,venc),f"vencidas_{filtro}.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",key="dl_v")

    st.markdown(div(),unsafe_allow_html=True)

    # ---- A VENCER ----
    st.markdown(sec("🟡 A vencer — próximos 30 dias"),unsafe_allow_html=True)
    pa=st.session_state.get("pag_a",0)
    paga=av[pa*PAGE:(pa+1)*PAGE]
    if not av:
        st.markdown('<div class="fin-empty">Nenhuma fatura a vencer para este filtro.</div>',unsafe_allow_html=True)
    else:
        for i,row in enumerate(paga): _card(row,"avencer",pa*PAGE+i,user_nome)
        st.markdown(f"**Total a vencer: {eur(ta)}**")
        tp_=max(1,(len(av)+PAGE-1)//PAGE)
        if tp_>1:
            c1,c2,c3=st.columns([1,2,1])
            if c1.button("← Anterior",key="pa_p",disabled=pa==0): st.session_state.pag_a=pa-1; st.rerun()
            c2.markdown(f"<div style='text-align:center;padding-top:8px'>Página {pa+1}/{tp_}</div>",unsafe_allow_html=True)
            if c3.button("Próxima →",key="pa_n",disabled=pa>=tp_-1): st.session_state.pag_a=pa+1; st.rerun()
        st.download_button("⬇️ Excel a vencer",excel_bytes(filtro,av),f"avencer_{filtro}.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",key="dl_a")

    st.markdown(div(),unsafe_allow_html=True)

    # ---- TOP 5 + POR PROJETO ----
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

    st.markdown(div(),unsafe_allow_html=True)

    # ---- CASHFLOW ----
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
            xaxis=dict(tickangle=45,automargin=True,tickfont=dict(size=11)),)
        st.plotly_chart(fig,use_container_width=True,config=PLOTLY_CFG)

    st.markdown(div(),unsafe_allow_html=True)

    # ---- HISTÓRICO ----
    st.markdown(sec("📋 Histórico de ações"),unsafe_allow_html=True)
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
        st.markdown('<div class="fin-empty">Nenhuma ação registada nesta sessão.</div>',unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# RENDER PRINCIPAL
# ---------------------------------------------------------------------------
def render(user: dict):
    init_state()
    # Injeta CSS globalmente usando st.html que é mais robusto que st.markdown para CSS
    st.html(_CSS)

    st.header(f"Bem-vindo, {user['nome']}")
    st.caption("Perfil: Financeiro")

    if SUPABASE_OK:
        try: n_pre=len(get_faturas_pre_aprovacao())
        except: n_pre=0
    else:
        n_pre=len(st.session_state.mock_pre)

    label_al=f"⚠️ Alertas/A Pagar ({n_pre})" if n_pre>0 else "⚠️ Alertas/A Pagar"

    try:
        from app.financeiro_consultores import _get_faturas_consultores_pendentes
        n_fc=len(_get_faturas_consultores_pendentes())
    except: n_fc=0
    label_cons=f"🤝 Consultores ({n_fc})" if n_fc>0 else "🤝 Consultores"

    tab1,tab2,tab3,tab4=st.tabs(["💶 Dashboard Financeiro",label_al,label_cons,"💳 Faturação Empresas"])

    with tab1: render_dashboard(user)
    with tab2: render_alertas(user)
    with tab3:
        try:
            from app.financeiro_consultores import render_consultores
            render_consultores(user)
        except Exception as e: st.error(f"Erro: {e}")
    with tab4:
        st.markdown('<div class="fin-empty" style="margin-top:40px">🚧 Em construção — histórico de pagamentos por empresa.</div>',unsafe_allow_html=True)
