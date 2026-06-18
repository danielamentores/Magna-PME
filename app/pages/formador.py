"""Pagina do formador."""
from __future__ import annotations
import base64
import io
import re
from datetime import datetime
from typing import Optional
import streamlit as st

# ---------------------------------------------------------------------------
# IMPORTS BD
# ---------------------------------------------------------------------------
try:
    from app.db_financeiro import get_supabase, get_supabase_admin
    get_supabase()
    SUPABASE_OK = True
except Exception:
    SUPABASE_OK = False

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
_CSS = """
<style>
.f-kpi-row{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0 20px}
.f-kpi{background:#fff;border:1px solid #E4E7EF;border-radius:12px;padding:16px 18px;flex:1;min-width:120px}
.f-kpi.a{border-top:3px solid #D97706}.f-kpi.b{border-top:3px solid #2563EB}
.f-kpi.g{border-top:3px solid #16A34A}.f-kpi.r{border-top:3px solid #DC2626}
.f-kpi .lbl{font-size:11px;font-weight:600;color:#8B94A3;text-transform:uppercase;letter-spacing:.06em;margin:0 0 5px}
.f-kpi .val{font-size:22px;font-weight:700;color:#1A1F2E;margin:0;line-height:1.1}
.f-kpi .sub{font-size:12px;color:#8B94A3;margin:3px 0 0}

.f-card{background:#fff;border:1px solid #E4E7EF;border-radius:12px;padding:16px;margin-bottom:10px}
.f-card.paga{border-left:4px solid #16A34A;background:#F0FDF4}
.f-card.aprovada{border-left:4px solid #2563EB;background:#EEF3FD}
.f-card.submetida{border-left:4px solid #D97706}
.f-card.leitura_falhada{border-left:4px solid #DC2626;background:#FEF2F2}
.f-card.acao_nao_fechada{border-left:4px solid #DC2626;background:#FEF2F2}
.f-card.rejeitada{border-left:4px solid #DC2626;background:#FEF2F2}

.f-fat-title{font-weight:700;font-size:15px;color:#1A1F2E}
.f-fat-meta{font-size:12px;color:#8B94A3;margin-top:3px}
.f-fat-val{font-weight:700;font-size:18px;color:#1A1F2E;text-align:right}
.f-fat-rej{font-size:13px;color:#DC2626;background:#FEF2F2;border-radius:6px;
           padding:6px 10px;margin-top:8px}
.f-fat-pago{font-size:12px;color:#16A34A;margin-top:4px}
.f-fat-prazo{font-size:12px;color:#2563EB;margin-top:4px}

.f-badge{display:inline-block;font-size:11px;font-weight:600;padding:2px 9px;border-radius:20px;white-space:nowrap}
.f-ptag{display:inline-block;font-size:11px;font-weight:700;padding:2px 8px;border-radius:4px}

.f-acao{background:#fff;border:1px solid #E4E7EF;border-radius:12px;padding:14px 16px;margin-bottom:8px}
.f-acao.fechada{border-left:4px solid #16A34A}
.f-acao.a_decorrer{border-left:4px solid #2563EB}
.f-acao.terminada_sem_fecho{border-left:4px solid #D97706;background:#FFFBEB}
.f-acao.sem_fatura{border-left:4px solid #7C3AED;background:#F5F3FF}

.f-sec{font-size:13px;font-weight:700;color:#4B5263;text-transform:uppercase;letter-spacing:.06em;margin:0 0 3px}
.f-secs{font-size:12px;color:#8B94A3;margin:0 0 14px}
.f-div{height:1px;background:#E4E7EF;margin:20px 0 18px}
.f-empty{background:#F7F8FC;border:1px dashed #E4E7EF;border-radius:10px;padding:24px;text-align:center;color:#8B94A3;font-size:13px}
.f-warn{background:#FFFBEB;border:1px solid #FCD34D;border-left:3px solid #D97706;
        border-radius:8px;padding:9px 14px;font-size:13px;color:#92400E;margin-bottom:10px}
.f-ok{background:#F0FDF4;border:1px solid #BBF7D0;border-left:3px solid #16A34A;
      border-radius:8px;padding:9px 14px;font-size:13px;color:#166534;margin-bottom:10px}
.f-step{display:flex;align-items:center;gap:10px;margin-bottom:16px}
.f-step-num{background:#1A1F2E;color:#fff;font-weight:700;font-size:13px;
            width:26px;height:26px;border-radius:50%;display:flex;align-items:center;
            justify-content:center;flex-shrink:0}
.f-step-lbl{font-weight:600;font-size:14px;color:#1A1F2E}
.f-resumo{background:#F7F8FC;border:1px solid #E4E7EF;border-radius:8px;
          padding:12px 14px;margin:8px 0 12px;font-size:13px}
.f-resumo .r-row{display:flex;gap:16px;flex-wrap:wrap;margin-top:4px}
.f-resumo .r-item{color:#4B5263}
.f-resumo .r-lbl{font-size:11px;color:#8B94A3;font-weight:600;text-transform:uppercase;letter-spacing:.04em}
</style>
"""

CORES = {"MENTORES":"#2563EB","ANIET":"#16A34A","APCMC":"#D97706",
         "APIMA":"#9D174D","PRODUTECH":"#7C3AED","CALÇADO":"#0F766E"}
BGS   = {"MENTORES":"#EEF3FD","ANIET":"#F0FDF4","APCMC":"#FFFBEB",
         "APIMA":"#FDF2F8","PRODUTECH":"#F5F3FF","CALÇADO":"#F0FDFA"}

# ---------------------------------------------------------------------------
# MOCK DATA
# ---------------------------------------------------------------------------
_MOCK_ACOES = [
    {"id":"a1","magna_id":"COMPETE2030-FSE+-01195000","codigo":"LIKE GARDEN.2.PCE",
     "nome":"Escalada e desmanche de árvores com motosserra","empresa_cliente":"Like Garden",
     "data_inicio":"2026-02-19","data_fim":"2026-03-13","volume_horas":50,
     "formandos_certificados":18,"estado":"fechada","projeto":"MENTORES","tem_fatura":True},
    {"id":"a2","magna_id":"COMPETE2030-FSE+-01196000","codigo":"CAMOESAS.03.PCE",
     "nome":"Segurança nos trabalhos de construção civil",
     "empresa_cliente":"CAMOESAS, LDA","data_inicio":"2025-11-30","data_fim":"2025-12-12",
     "volume_horas":24,"formandos_certificados":16,"estado":"fechada","projeto":"ANIET","tem_fatura":False},
    {"id":"a3","magna_id":"COMPETE2030-FSE+-01195000","codigo":"FENABEL.GEPSLT_16",
     "nome":"Gestão de emergências e primeiros socorros no local de trabalho",
     "empresa_cliente":"Fenabel, S.A","data_inicio":"2026-05-14","data_fim":"2026-06-04",
     "volume_horas":16,"formandos_certificados":0,"estado":"a_decorrer","projeto":"MENTORES","tem_fatura":False},
    {"id":"a4","magna_id":"COMPETE2030-FSE+-01196000","codigo":"FORESTCORTE.2.PCE",
     "nome":"Utilização da motosserra nas operações florestais",
     "empresa_cliente":"Forestcorte","data_inicio":"2026-04-10","data_fim":"2026-05-31",
     "volume_horas":25,"formandos_certificados":8,"estado":"terminada_sem_fecho","projeto":"ANIET","tem_fatura":False},
]

_MOCK_FATURAS = [
    {"id":"f1","numero_fatura":"FT2026/0142","valor":3200,"estado":"aprovada",
     "created_at":"2026-06-01","acao_codigo":"LIKE GARDEN.2.PCE",
     "acao_nome":"Escalada e desmanche de árvores com motosserra",
     "projeto":"MENTORES","prazo_pagamento":"2026-06-21","pago_em":None,
     "notas":"","ficheiro_url":None},
    {"id":"f2","numero_fatura":"FT2026/0110","valor":1800,"estado":"paga",
     "created_at":"2026-05-10","acao_codigo":"CAMOESAS.03.PCE",
     "acao_nome":"Segurança nos trabalhos de construção civil",
     "projeto":"ANIET","prazo_pagamento":"2026-05-30","pago_em":"2026-05-28",
     "notas":"","ficheiro_url":None},
    {"id":"f3","numero_fatura":"FT2026/0155","valor":2400,"estado":"leitura_falhada",
     "created_at":"2026-06-15","acao_codigo":"FENABEL.GEPSLT_16",
     "acao_nome":"Gestão de emergências e primeiros socorros",
     "projeto":"MENTORES","prazo_pagamento":None,"pago_em":None,
     "notas":"Código interno não encontrado no sistema","ficheiro_url":None},
]

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def eur(v):
    try: return f"€\u202f{float(v):,.0f}".replace(",",".")
    except: return "€ —"

def ptag(p):
    c=CORES.get(p,"#6B7280"); b=BGS.get(p,"#F3F4F6")
    return f'<span class="f-ptag" style="background:{b};color:{c}">{p}</span>'

def bdg(estado):
    M={
        "submetida":        ("#FFFBEB","#D97706","⏳ Submetida"),
        "leitura_falhada":  ("#FEF2F2","#DC2626","⚠️ Verificar"),
        "acao_nao_fechada": ("#FEF2F2","#DC2626","⚠️ Ação não fechada"),
        "aprovada":         ("#EEF3FD","#2563EB","✅ Aprovada"),
        "paga":             ("#F0FDF4","#16A34A","💳 Paga"),
        "rejeitada":        ("#FEF2F2","#DC2626","❌ Rejeitada"),
    }
    bg,c,l=M.get(estado,("#F3F4F6","#6B7280",estado))
    return f'<span class="f-badge" style="background:{bg};color:{c}">{l}</span>'

def bdg_acao(estado):
    M={
        "fechada":             ("#F0FDF4","#16A34A","✅ Fechada"),
        "a_decorrer":          ("#EEF3FD","#2563EB","🔵 A decorrer"),
        "planeada":            ("#F5F3FF","#7C3AED","📋 Planeada"),
        "terminada_sem_fecho": ("#FFFBEB","#D97706","⚠️ Por fechar"),
    }
    bg,c,l=M.get(estado,("#F3F4F6","#6B7280",estado))
    return f'<span class="f-badge" style="background:{bg};color:{c}">{l}</span>'

def kpi_h(lbl,val,sub,v=""):
    cls=f"f-kpi {v}" if v else "f-kpi"
    return f'<div class="{cls}"><p class="lbl">{lbl}</p><p class="val">{val}</p><p class="sub">{sub}</p></div>'

def sec(t,s=""):
    sub=f'<p class="f-secs">{s}</p>' if s else ""
    return f'<p class="f-sec">{t}</p>{sub}'

def div(): return '<div class="f-div"></div>'

# ---------------------------------------------------------------------------
# QUERIES
# ---------------------------------------------------------------------------
def _get_acoes(formador_id):
    if not SUPABASE_OK: return _MOCK_ACOES
    try:
        r=get_supabase().table("acoes").select(
            "id,magna_id,codigo,nome,empresa_cliente,data_inicio,data_fim,"
            "volume_horas,formandos_certificados,estado"
        ).eq("formador_id",formador_id).order("data_fim",desc=True).execute()
        if not r.data: return _MOCK_ACOES
        # Verificar quais têm fatura
        ids=[a["id"] for a in r.data]
        fat_r=get_supabase().table("faturas").select("acao_id").in_("acao_id",ids).execute()
        fat_ids={f["acao_id"] for f in (fat_r.data or [])}
        for a in r.data: a["tem_fatura"]=a["id"] in fat_ids
        return r.data
    except: return _MOCK_ACOES

def _get_faturas(formador_id):
    if not SUPABASE_OK:
        return st.session_state.get("mock_fat_form", list(_MOCK_FATURAS))
    try:
        r=get_supabase().table("faturas").select(
            "id,numero_fatura,valor,estado,created_at,prazo_pagamento,pago_em,notas,ficheiro_url,"
            "acoes(codigo,nome)"
        ).eq("formador_id",formador_id).order("created_at",desc=True).execute()
        if not r.data:
            return st.session_state.get("mock_fat_form", list(_MOCK_FATURAS))
        for d in r.data:
            a=d.get("acoes") or {}
            d["acao_codigo"]=a.get("codigo") or "—"
            d["acao_nome"]=a.get("nome") or "—"
        return r.data
    except: return st.session_state.get("mock_fat_form", list(_MOCK_FATURAS))

def _get_acao_por_codigo(codigo):
    if not SUPABASE_OK:
        m=[a for a in _MOCK_ACOES if a["codigo"].upper()==codigo.upper()]
        return m[0] if m else None
    try:
        r=get_supabase().table("acoes").select(
            "id,codigo,nome,empresa_cliente,estado,volume_horas,formandos_certificados,data_inicio,data_fim"
        ).ilike("codigo",codigo).execute()
        return r.data[0] if r.data else None
    except: return None

def _submeter_bd(formador_id,acao_id,dados,ficheiro_bytes,nome_fich):
    if not SUPABASE_OK:
        if "mock_fat_form" not in st.session_state:
            st.session_state.mock_fat_form=list(_MOCK_FATURAS)
        nova={
            "id":f"f{len(st.session_state.mock_fat_form)+1}",
            "numero_fatura":dados.get("numero_fatura") or "—",
            "valor":dados.get("valor") or 0,
            "estado":"submetida","created_at":datetime.now().strftime("%Y-%m-%d"),
            "acao_codigo":st.session_state.get("_sub_cod","—"),
            "acao_nome":st.session_state.get("_sub_nome","—"),
            "projeto":st.session_state.get("_sub_proj","—"),
            "prazo_pagamento":None,"pago_em":None,"notas":"","ficheiro_url":None,
        }
        st.session_state.mock_fat_form.insert(0,nova)
        return True
    try:
        url=None
        try:
            sb=get_supabase()
            path=f"faturas/{formador_id}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{nome_fich}"
            sb.storage.from_("faturas").upload(path,ficheiro_bytes,
                file_options={"content-type":"application/pdf"})
            url=sb.storage.from_("faturas").get_public_url(path)
        except: pass
        get_supabase_admin().table("faturas").insert({
            "formador_id":formador_id,"acao_id":acao_id,
            "numero_fatura":dados.get("numero_fatura"),
            "data_fatura":dados.get("data_fatura"),
            "valor":dados.get("valor"),
            "nif_emitente":dados.get("nif_emitente"),
            "estado":"submetida","ficheiro_url":url,
            "dados_extraidos":dados,
        }).execute()
        return True
    except Exception as e: st.error(f"Erro: {e}"); return False

# ---------------------------------------------------------------------------
# LEITURA PDF
# ---------------------------------------------------------------------------
def _ler_pdf(b):
    try:
        import pdfplumber, io as _io
    except ImportError:
        return {"erro":"pdfplumber não instalado"}
    r={"numero_fatura":None,"nif_emitente":None,"nif_destinatario":None,
       "valor":None,"data_fatura":None,"erro":None}
    try:
        with pdfplumber.open(_io.BytesIO(b)) as pdf:
            txt="\n".join(p.extract_text() or "" for p in pdf.pages)
        m=re.search(r"(?:fatura|recibo|ft|fr)[^\d]*(\d{4}[/\-]\d+)",txt,re.I)
        if m: r["numero_fatura"]=m.group(1)
        nifs=re.findall(r"\b\d{9}\b",txt)
        if len(nifs)>=1: r["nif_emitente"]=nifs[0]
        if len(nifs)>=2: r["nif_destinatario"]=nifs[1]
        m=re.search(r"(?:total|valor|montante)[^\d€]*[€]?\s*([\d\s.,]+)\s*(?:€|eur)?",txt,re.I)
        if m:
            try: r["valor"]=float(m.group(1).replace(" ","").replace(".","").replace(",","."))
            except: pass
        m=re.search(r"\b(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})\b",txt)
        if m: r["data_fatura"]=f"{m.group(3)}-{m.group(2).zfill(2)}-{m.group(1).zfill(2)}"
    except Exception as e: r["erro"]=str(e)
    return r

# ---------------------------------------------------------------------------
# TAB 1 — SUBMETER FATURA
# ---------------------------------------------------------------------------
def _submeter(user):
    formador_id=user.get("id") or "mock"

    st.markdown(sec("📤 Submeter fatura",
        "Valida o código da ação, carrega o PDF e confirma os dados."),
        unsafe_allow_html=True)

    # ---- PASSO 1 ----
    st.html('<div class="f-step"><div class="f-step-num">1</div><div class="f-step-lbl">Código interno da ação</div></div>')

    col_cod,col_btn=st.columns([3,1])
    with col_cod:
        codigo=st.text_input("",placeholder="Ex: LIKE GARDEN.2.PCE",
                             key="sub_cod",label_visibility="collapsed")
    with col_btn:
        st.markdown("<div style='margin-top:2px'>",unsafe_allow_html=True)
        if st.button("🔍 Validar",key="sub_val",use_container_width=True):
            if codigo:
                with st.spinner("A verificar..."):
                    acao=_get_acao_por_codigo(codigo.strip())
                if acao:
                    st.session_state.acao_val=acao
                    st.session_state._sub_cod=acao.get("codigo","—")
                    st.session_state._sub_nome=acao.get("nome","—")
                    st.session_state._sub_proj=acao.get("projeto","—")
                else:
                    st.session_state.acao_val=None
                    st.html('<div class="f-warn">⚠️ Código não encontrado. Confirma na Magna.</div>')
        st.markdown("</div>",unsafe_allow_html=True)

    acao_val=st.session_state.get("acao_val")

    if acao_val:
        fechada=acao_val.get("estado")=="fechada"
        aviso="" if fechada else "<br><span style='color:#D97706;font-size:12px'>⚠️ Ação ainda não fechada — o pagamento só é processado após fecho.</span>"
        cls="f-ok" if fechada else "f-warn"
        st.html(
            f'<div class="{cls}">'
            f'<strong>{acao_val.get("codigo","—")}</strong> — {acao_val.get("nome","—")}<br>'
            f'<div class="f-resumo" style="margin-top:8px">'
            f'<div class="r-row">'
            f'<div><div class="r-lbl">Empresa</div><div class="r-item">{acao_val.get("empresa_cliente","—")}</div></div>'
            f'<div><div class="r-lbl">Período</div><div class="r-item">{str(acao_val.get("data_inicio","—"))[:10]} → {str(acao_val.get("data_fim","—"))[:10]}</div></div>'
            f'<div><div class="r-lbl">Horas</div><div class="r-item">{acao_val.get("volume_horas","—")}h</div></div>'
            f'<div><div class="r-lbl">Formandos</div><div class="r-item">{acao_val.get("formandos_certificados","—")}</div></div>'
            f'</div></div>'
            f'{aviso}'
            f'</div>'
        )

    st.html(div())

    # ---- PASSO 2 ----
    st.html('<div class="f-step"><div class="f-step-num">2</div><div class="f-step-lbl">Carrega o PDF da fatura</div></div>')

    ficheiro=st.file_uploader("",type=["pdf"],key="sub_pdf",label_visibility="collapsed")
    dados_lidos=st.session_state.get("dados_pdf")

    if ficheiro and not dados_lidos:
        with st.spinner("A ler o PDF..."):
            d=_ler_pdf(ficheiro.getvalue())
        if d.get("erro"):
            st.error(f"Erro na leitura: {d['erro']}")
        else:
            st.session_state.dados_pdf=d
            dados_lidos=d

    if ficheiro and dados_lidos:
        st.markdown("**Confirma os dados extraídos:**")
        c1,c2=st.columns(2)
        with c1:
            st.text_input("Nº Fatura",value=dados_lidos.get("numero_fatura") or "",key="sub_nf")
            st.text_input("Data (AAAA-MM-DD)",value=dados_lidos.get("data_fatura") or "",key="sub_dt")
        with c2:
            st.number_input("Valor (€)",min_value=0.0,step=0.01,
                           value=float(dados_lidos.get("valor") or 0),
                           key="sub_val2",format="%.2f")
            st.text_input("NIF emitente",value=dados_lidos.get("nif_emitente") or "",key="sub_nif")

    st.html(div())

    # ---- PASSO 3 ----
    st.html('<div class="f-step"><div class="f-step-num">3</div><div class="f-step-lbl">Submeter</div></div>')

    pode=acao_val and dados_lidos and ficheiro
    if not pode:
        missing=[]
        if not acao_val: missing.append("código validado")
        if not ficheiro: missing.append("PDF carregado")
        if missing:
            st.html(f'<div class="f-warn">Ainda falta: {", ".join(missing)}</div>')

    if st.button("📤 Submeter fatura",type="primary",disabled=not pode,key="sub_btn"):
        df={
            "numero_fatura":st.session_state.get("sub_nf") or dados_lidos.get("numero_fatura"),
            "data_fatura":  st.session_state.get("sub_dt") or dados_lidos.get("data_fatura"),
            "valor":        st.session_state.get("sub_val2") or dados_lidos.get("valor"),
            "nif_emitente": st.session_state.get("sub_nif") or dados_lidos.get("nif_emitente"),
        }
        with st.spinner("A submeter..."):
            ok=_submeter_bd(formador_id,acao_val["id"],df,ficheiro.getvalue(),ficheiro.name)
        if ok:
            st.success("✅ Fatura submetida! O financeiro irá analisar brevemente.")
            for k in ["acao_val","dados_pdf","sub_cod","sub_nf","sub_dt","sub_val2","sub_nif"]:
                st.session_state.pop(k,None)
            st.rerun()

# ---------------------------------------------------------------------------
# TAB 2 — FATURAS
# ---------------------------------------------------------------------------
def _faturas(user):
    formador_id=user.get("id") or "mock"
    faturas=_get_faturas(formador_id)

    n_sub =len([f for f in faturas if f["estado"] in ("submetida","leitura_falhada","acao_nao_fechada")])
    n_apr =len([f for f in faturas if f["estado"]=="aprovada"])
    n_pago=len([f for f in faturas if f["estado"]=="paga"])
    n_rej =len([f for f in faturas if f["estado"]=="rejeitada"])
    t_pago=sum(f.get("valor") or 0 for f in faturas if f["estado"]=="paga")
    t_pend=sum(f.get("valor") or 0 for f in faturas if f["estado"] in ("submetida","aprovada"))

    st.html(
        '<div class="f-kpi-row">'
        +kpi_h("⏳ Em análise",   str(n_sub),  "aguardam resposta","a")
        +kpi_h("✅ Aprovadas",    str(n_apr),  "a aguardar pagamento","b")
        +kpi_h("💳 Pagas",        eur(t_pago), f"{n_pago} faturas","g")
        +(kpi_h("❌ Rejeitadas",  str(n_rej),  "requerem atenção","r") if n_rej>0 else "")
        +'</div>'
    )

    if n_rej>0:
        st.html(f'<div class="f-warn">❌ Tens {n_rej} fatura(s) rejeitada(s). Verifica o motivo e resubmete.</div>')

    st.html(div())

    col_f,col_p=st.columns([2,3])
    with col_f:
        filtro=st.selectbox("Estado",
            ["Todas","Em análise","Aprovada","Paga","Rejeitada"],key="fat_fil")
    with col_p:
        pesq=st.text_input("",placeholder="Pesquisar nº fatura ou ação...",
                          key="fat_pesq",label_visibility="collapsed")

    fat_fil=faturas
    mapa={"Em análise":["submetida","leitura_falhada","acao_nao_fechada"],
          "Aprovada":["aprovada"],"Paga":["paga"],"Rejeitada":["rejeitada"]}
    if filtro!="Todas":
        fat_fil=[f for f in fat_fil if f["estado"] in mapa.get(filtro,[])]
    if pesq:
        p=pesq.lower()
        fat_fil=[f for f in fat_fil if p in (f.get("numero_fatura") or "").lower()
                 or p in (f.get("acao_codigo") or "").lower()
                 or p in (f.get("acao_nome") or "").lower()]

    st.markdown(sec(f"Faturas ({len(fat_fil)})"),unsafe_allow_html=True)

    if not fat_fil:
        st.html('<div class="f-empty">Nenhuma fatura encontrada.</div>')
        return

    for f in fat_fil:
        estado =f.get("estado") or "submetida"
        n_fat  =f.get("numero_fatura") or "—"
        valor  =f.get("valor") or 0
        cod    =f.get("acao_codigo") or "—"
        nome_a =f.get("acao_nome") or "—"
        proj   =f.get("projeto") or "—"
        criada =str(f.get("created_at") or "—")[:10]
        prazo  =str(f.get("prazo_pagamento") or "—")[:10]
        pago_em=str(f.get("pago_em") or "—")[:10]
        notas  =f.get("notas") or ""
        url    =f.get("ficheiro_url")
        fid    =f.get("id") or n_fat

        # linha extra conforme estado
        if estado=="paga" and pago_em!="—":
            extra=f'<div class="f-fat-pago">💳 Pago em {pago_em}</div>'
        elif estado=="aprovada" and prazo!="—":
            extra=f'<div class="f-fat-prazo">📅 Prazo pagamento: {prazo}</div>'
        elif estado in ("rejeitada","leitura_falhada","acao_nao_fechada") and notas:
            extra=f'<div class="f-fat-rej">❌ {notas}</div>'
        else:
            extra=""

        col_card,col_btn=st.columns([5,2])
        with col_card:
            st.html(
                f'<div class="f-card {estado}">'
                f'<div style="display:flex;justify-content:space-between;align-items:flex-start">'
                f'<div style="flex:1">'
                f'<div class="f-fat-title">{n_fat}</div>'
                f'<div class="f-fat-meta">{ptag(proj)}&nbsp;·&nbsp;{cod}</div>'
                f'<div class="f-fat-meta">{nome_a[:55]}</div>'
                f'<div class="f-fat-meta">Submetida: {criada}</div>'
                f'{extra}'
                f'</div>'
                f'<div style="text-align:right;min-width:110px">'
                f'<div class="f-fat-val">{eur(valor)}</div>'
                f'<div style="margin-top:4px">{bdg(estado)}</div>'
                f'</div>'
                f'</div>'
                f'</div>'
            )
        with col_btn:
            st.markdown("<div style='margin-top:10px;display:flex;flex-direction:column;gap:6px'>",
                       unsafe_allow_html=True)

            # Botão Ver fatura (pré-visualização inline)
            if url:
                if st.button("📄 Ver fatura",key=f"ver_{fid}",use_container_width=True):
                    st.session_state[f"show_pdf_{fid}"]=not st.session_state.get(f"show_pdf_{fid}",False)
            else:
                # Mock: simula visualização com placeholder
                if st.button("📄 Ver fatura",key=f"ver_{fid}",use_container_width=True):
                    st.session_state[f"show_pdf_{fid}"]=not st.session_state.get(f"show_pdf_{fid}",False)

            # Re-submeter se rejeitada
            if estado in ("rejeitada","leitura_falhada"):
                if st.button("🔄 Re-submeter",key=f"rsub_{fid}",use_container_width=True):
                    # Pré-preenche com dados da fatura rejeitada
                    st.session_state["sub_cod"]=cod
                    st.session_state.pop("acao_val",None)
                    st.toast("Vai à tab 'Submeter fatura' para resubmeter.")

            st.markdown("</div>",unsafe_allow_html=True)

        # Pré-visualização inline do PDF
        if st.session_state.get(f"show_pdf_{fid}"):
            with st.container(border=True):
                if url:
                    # PDF real via URL
                    st.markdown(
                        f'<iframe src="{url}" width="100%" height="600px" '
                        f'style="border:none;border-radius:8px"></iframe>',
                        unsafe_allow_html=True
                    )
                else:
                    # Mock: placeholder
                    st.markdown(
                        '<div style="background:#F7F8FC;border:1px dashed #E4E7EF;'
                        'border-radius:8px;padding:40px;text-align:center;color:#8B94A3">'
                        '📄 Pré-visualização disponível quando o PDF estiver no servidor.'
                        '</div>',
                        unsafe_allow_html=True
                    )
                if st.button("✖ Fechar",key=f"close_{fid}"):
                    st.session_state[f"show_pdf_{fid}"]=False
                    st.rerun()

    # Total acumulado
    st.html(div())
    t_total=sum(f.get("valor") or 0 for f in faturas)
    t_ano  =sum(f.get("valor") or 0 for f in faturas
                if str(f.get("created_at","")).startswith("2026"))
    st.html(
        f'<div style="display:flex;gap:24px;padding:12px 0">'
        f'<div><span style="font-size:12px;color:#8B94A3;font-weight:600;text-transform:uppercase;letter-spacing:.05em">Total recebido 2026</span><br>'
        f'<span style="font-size:20px;font-weight:700;color:#1A1F2E">{eur(sum(f.get("valor") or 0 for f in faturas if f["estado"]=="paga" and str(f.get("created_at","")).startswith("2026")))}</span></div>'
        f'<div><span style="font-size:12px;color:#8B94A3;font-weight:600;text-transform:uppercase;letter-spacing:.05em">Total submetido 2026</span><br>'
        f'<span style="font-size:20px;font-weight:700;color:#4B5263">{eur(t_ano)}</span></div>'
        f'</div>'
    )

# ---------------------------------------------------------------------------
# TAB 3 — AÇÕES
# ---------------------------------------------------------------------------
def _acoes(user):
    formador_id=user.get("id") or "mock"
    acoes=_get_acoes(formador_id)

    n_dec =len([a for a in acoes if a["estado"]=="a_decorrer"])
    n_fec =len([a for a in acoes if a["estado"]=="fechada"])
    n_pfec=len([a for a in acoes if a["estado"]=="terminada_sem_fecho"])
    n_sfat=len([a for a in acoes if a["estado"]=="fechada" and not a.get("tem_fatura")])

    st.html(
        '<div class="f-kpi-row">'
        +kpi_h("🔵 A decorrer", str(n_dec),  "ações ativas",       "b")
        +kpi_h("✅ Fechadas",   str(n_fec),  "prontas a faturar",  "g")
        +kpi_h("⚠️ Por fechar", str(n_pfec), "requerem fecho",     "a")
        +(kpi_h("🟣 Sem fatura",str(n_sfat), "fechadas sem fatura","r") if n_sfat>0 else "")
        +'</div>'
    )

    if n_sfat>0:
        st.html(f'<div class="f-warn">🟣 Tens {n_sfat} ação(ões) fechada(s) sem fatura submetida. Podes faturar agora.</div>')

    st.html(div())

    col_f,col_p=st.columns([2,3])
    with col_f:
        filtro=st.selectbox("Estado",
            ["Todas","A decorrer","Fechada","Por fechar","Planeada"],key="ac_fil")
    with col_p:
        pesq=st.text_input("",placeholder="Pesquisar código ou empresa...",
                          key="ac_pesq",label_visibility="collapsed")

    ac_fil=acoes
    mapa={"A decorrer":"a_decorrer","Fechada":"fechada",
          "Por fechar":"terminada_sem_fecho","Planeada":"planeada"}
    if filtro!="Todas":
        ac_fil=[a for a in ac_fil if a["estado"]==mapa.get(filtro,filtro)]
    if pesq:
        p=pesq.lower()
        ac_fil=[a for a in ac_fil if p in (a.get("codigo") or "").lower()
                or p in (a.get("empresa_cliente") or "").lower()
                or p in (a.get("nome") or "").lower()]

    st.markdown(sec(f"Ações ({len(ac_fil)})"),unsafe_allow_html=True)

    if not ac_fil:
        st.html('<div class="f-empty">Nenhuma ação encontrada.</div>')
        return

    for a in ac_fil:
        estado =a.get("estado") or "—"
        codigo =a.get("codigo") or a.get("magna_id") or "—"
        nome   =a.get("nome") or "—"
        empresa=a.get("empresa_cliente") or "—"
        d_ini  =str(a.get("data_inicio") or "—")[:10]
        d_fim  =str(a.get("data_fim") or "—")[:10]
        horas  =a.get("volume_horas") or 0
        form   =a.get("formandos_certificados") or 0
        proj   =a.get("projeto") or "—"
        tem_fat=a.get("tem_fatura",False)

        # Classe extra para fechada sem fatura
        css_extra="sem_fatura" if estado=="fechada" and not tem_fat else estado

        if estado=="terminada_sem_fecho":
            aviso='<div style="font-size:12px;color:#D97706;margin-top:4px">⚠️ Terminada mas não fechada na Magna — contacta o coordenador.</div>'
        elif estado=="a_decorrer":
            aviso='<div style="font-size:12px;color:#2563EB;margin-top:4px">🔵 Em curso — podes faturar após o fecho.</div>'
        elif estado=="fechada" and not tem_fat:
            aviso='<div style="font-size:12px;color:#7C3AED;margin-top:4px">🟣 Ação fechada sem fatura — podes submeter agora.</div>'
        elif estado=="fechada" and tem_fat:
            aviso='<div style="font-size:12px;color:#16A34A;margin-top:4px">✅ Fatura já submetida.</div>'
        else:
            aviso=""

        col_ac,col_btn=st.columns([5,2])
        with col_ac:
            st.html(
                f'<div class="f-acao {css_extra}">'
                f'<div style="display:flex;align-items:flex-start;gap:8px;margin-bottom:4px">'
                f'<span style="font-weight:700;font-size:14px">{codigo}</span>'
                f'&nbsp;{bdg_acao(estado)}'
                f'</div>'
                f'<div style="font-size:12px;color:#8B94A3">{ptag(proj)}&nbsp;·&nbsp;{empresa}</div>'
                f'<div style="font-size:13px;color:#4B5263;margin-top:2px">{nome[:60]}</div>'
                f'<div style="font-size:12px;color:#8B94A3;margin-top:2px">'
                f'{d_ini} → {d_fim}&nbsp;·&nbsp;{horas}h&nbsp;·&nbsp;{form} formandos'
                f'</div>'
                f'{aviso}'
                f'</div>'
            )
        with col_btn:
            if estado=="fechada" and not tem_fat:
                st.markdown("<div style='margin-top:10px'>",unsafe_allow_html=True)
                if st.button("📤 Faturar",key=f"fat_ac_{a['id']}",
                            use_container_width=True,type="primary"):
                    st.session_state["sub_cod"]=codigo
                    st.session_state.pop("acao_val",None)
                    st.toast(f"Vai à tab 'Submeter fatura' — código {codigo} já preenchido.")
                st.markdown("</div>",unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# RENDER PRINCIPAL
# ---------------------------------------------------------------------------
def render(user: dict):
    st.html(_CSS)
    st.header(f"Bem-vindo, {user['nome']}")
    st.caption("Perfil: Formador")

    faturas=_get_faturas(user.get("id") or "mock")
    n_rej=len([f for f in faturas if f["estado"]=="rejeitada"])
    n_sfat=len([a for a in _get_acoes(user.get("id") or "mock")
                if a["estado"]=="fechada" and not a.get("tem_fatura")])

    label_fat=f"📋 Faturas{' ❗' if n_rej>0 else ''}"
    label_ac =f"📚 Ações{' 🟣' if n_sfat>0 else ''}"

    tab1,tab2,tab3=st.tabs(["📤 Submeter fatura",label_fat,label_ac])
    with tab1: _acoes(user)
    with tab2: _faturas(user)
    with tab3: _submeter(user)
