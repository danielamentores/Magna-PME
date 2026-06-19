"""Helpers e design partilhado — módulo financeiro."""
from __future__ import annotations
import io
import re
from datetime import date, datetime
import pandas as pd
import streamlit as st

CORES = {"MENTORES":"#2563EB","ANIET":"#16A34A","APCMC":"#D97706",
         "APIMA":"#9D174D","PRODUTECH":"#7C3AED","CALÇADO":"#0F766E"}
BGS   = {"MENTORES":"#EEF3FD","ANIET":"#F0FDF4","APCMC":"#FFFBEB",
         "APIMA":"#FDF2F8","PRODUTECH":"#F5F3FF","CALÇADO":"#F0FDFA"}

ORDEM = ["Data de vencimento","Valor (maior primeiro)","Valor (menor primeiro)","Projeto"]
PLOTLY_CFG = {"displayModeBar": False}

def eur(v):
    try: return f"€\u202f{float(v):,.0f}".replace(",",".")
    except: return "€ —"

def eur2(v):
    """Com dois decimais."""
    try: return f"€\u202f{float(v):,.2f}".replace(",","X").replace(".",",").replace("X",".")
    except: return "€ —"

def ptag(p):
    c=CORES.get(p,"#6B7280"); b=BGS.get(p,"#F3F4F6")
    return f'<span class="fin-ptag" style="background:{b};color:{c}">{p}</span>'

def bdg(estado):
    M={
        "submetida":           ("#FFFBEB","#D97706","Submetida"),
        "leitura_falhada":     ("#FEF2F2","#DC2626","Leitura falhada"),
        "acao_nao_fechada":    ("#FEF2F2","#DC2626","Ação não fechada"),
        "aprovada":            ("#F0FDF4","#16A34A","Aprovada"),
        "paga":                ("#F0FDF4","#16A34A","Paga"),
        "rejeitada":           ("#F3F4F6","#6B7280","Rejeitada"),
        "Pendente":            ("#FFFBEB","#D97706","Pendente"),
        "Aprovado":            ("#F0FDF4","#16A34A","Aprovado"),
        "Pago":                ("#EEF3FD","#2563EB","Pago"),
        "aguarda_fatura":      ("#FFFBEB","#D97706","Aguarda fatura"),
        "fatura_emitida":      ("#EEF3FD","#2563EB","Fatura emitida"),
        "confirmada":          ("#F0FDF4","#16A34A","Confirmada"),
        "nh_paga":             ("#F0FDF4","#16A34A","NH Paga"),
        "nh_pendente":         ("#FFFBEB","#D97706","NH Pendente"),
        "sem_fatura":          ("#F3F4F6","#6B7280","Sem fatura"),
        "por_faturar":         ("#F3F4F6","#6B7280","Por faturar"),
        "fechada":             ("#F0FDF4","#16A34A","✅ Fechada"),
        "a_decorrer":          ("#EEF3FD","#2563EB","🔵 A decorrer"),
        "planeada":            ("#F5F3FF","#7C3AED","📋 Planeada"),
        "terminada_sem_fecho": ("#FFFBEB","#D97706","⚠️ Por fechar"),
    }
    bg,c,l = M.get(estado, ("#F3F4F6","#6B7280", estado))
    return f'<span class="fin-badge" style="background:{bg};color:{c}">{l}</span>'

def kpi_h(lbl, val, sub, v=""):
    cor = {"r":"#DC2626","a":"#D97706","b":"#2563EB","g":"#16A34A","p":"#7C3AED"}.get(v,"")
    bord = f"border-top:3px solid {cor}" if cor else ""
    return (f'<div class="fin-kpi" style="{bord}">'
            f'<p class="lbl">{lbl}</p><p class="val">{val}</p><p class="sub">{sub}</p></div>')

def sec(titulo, sub=""):
    s = f'<p class="fin-secs">{sub}</p>' if sub else ""
    return f'<p class="fin-sec">{titulo}</p>{s}'

def div():
    return '<div class="fin-div"></div>'

def ordenar(d, c):
    if c=="Valor (maior primeiro)": return sorted(d, key=lambda x: x.get("valor") or 0, reverse=True)
    if c=="Valor (menor primeiro)": return sorted(d, key=lambda x: x.get("valor") or 0)
    if c=="Projeto": return sorted(d, key=lambda x: _projeto(x))
    col = "atraso" if d and "atraso" in d[0] else "dias"
    return sorted(d, key=lambda x: x.get(col) or 0, reverse=True)

def fil_proj(d, p):
    if not p or p=="Todos": return d
    return [x for x in d if _projeto(x)==p]

def fil_datas(d, ini, fim):
    if not ini and not fim: return d
    out = []
    for x in d:
        ps = x.get("prazo_pagamento")
        if not ps: out.append(x); continue
        try:
            p = date.fromisoformat(ps)
            if ini and p < ini: continue
            if fim and p > fim: continue
        except: pass
        out.append(x)
    return out

def _formador(r): return (r.get("profiles") or {}).get("nome") or "—"
def _projeto(r):  return (r.get("acoes")    or {}).get("nome") or "—"
def _email(r):    return (r.get("profiles") or {}).get("email") or ""

def excel_bytes(faturas):
    rows = [{"Nº Fatura": f.get("numero_fatura") or "—", "Formador": _formador(f),
             "Projeto": _projeto(f), "Valor (€)": f.get("valor") or 0,
             "Prazo": f.get("prazo_pagamento") or "—", "Estado": f.get("estado") or "—"}
            for f in faturas]
    buf = io.BytesIO()
    pd.DataFrame(rows).to_excel(buf, index=False, engine="openpyxl")
    return buf.getvalue()

def extrair_pdf(b):
    try: import pdfplumber, io as _io
    except: return {"erro": "pdfplumber não instalado"}
    r = {"numero_fatura":None,"nif_emitente":None,"valor":None,"data_fatura":None,"erro":None}
    try:
        with pdfplumber.open(io.BytesIO(b)) as pdf:
            txt = "\n".join(p.extract_text() or "" for p in pdf.pages)
        m = re.search(r"(?:fatura|recibo|ft|fr)[^\d]*(\d{4}[/\-]\d+)", txt, re.I)
        if m: r["numero_fatura"] = m.group(1)
        nifs = re.findall(r"\b\d{9}\b", txt)
        if nifs: r["nif_emitente"] = nifs[0]
        m = re.search(r"(?:total|valor|montante)[^\d€]*[€]?\s*([\d\s.,]+)\s*(?:€|eur)?", txt, re.I)
        if m:
            try: r["valor"] = float(m.group(1).replace(" ","").replace(".","").replace(",","."))
            except: pass
        m = re.search(r"\b(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})\b", txt)
        if m: r["data_fatura"] = f"{m.group(3)}-{m.group(2).zfill(2)}-{m.group(1).zfill(2)}"
    except Exception as e: r["erro"] = str(e)
    return r

def guardar_comprovativo(fatura_id: str, ficheiro_bytes: bytes, nome_fich: str, user_nome: str) -> str | None:
    if "comprovativos" not in st.session_state:
        st.session_state.comprovativos = {}
    try:
        from app.db_financeiro import get_supabase
        sb = get_supabase()
        path = f"comprovativos/{fatura_id}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{nome_fich}"
        sb.storage.from_("faturas").upload(path, ficheiro_bytes,
            file_options={"content-type": "application/pdf"})
        url = sb.storage.from_("faturas").get_public_url(path)
        sb.table("faturas").update({"comprovativo_url": url}).eq("id", fatura_id).execute()
        st.session_state.comprovativos[fatura_id] = {"nome": nome_fich, "url": url,
            "guardado_em": datetime.now().strftime("%d/%m/%Y %H:%M"), "guardado_por": user_nome}
        return url
    except Exception:
        st.session_state.comprovativos[fatura_id] = {"nome": nome_fich, "url": None,
            "guardado_em": datetime.now().strftime("%d/%m/%Y %H:%M"), "guardado_por": user_nome}
        return None

def notificar_rejeicao(email: str, n_fatura: str, motivo: str):
    if not email: return
    try:
        from integrations.gmail import send_email
        send_email(to=email, subject=f"Fatura {n_fatura} — rejeitada",
                   body=f"A sua fatura {n_fatura} foi rejeitada.\n\nMotivo: {motivo}\n\nCorrija e resubmeta.")
    except: pass

CSS = """
<style>
.stTabs [data-baseweb="tab-list"]{gap:2px !important;background:#F4F7F9 !important;border-radius:10px 10px 0 0 !important;padding:5px 6px 0 !important;border:1px solid #DDE4EA !important;border-bottom:none !important;}
.stTabs [data-baseweb="tab"]{border-radius:7px 7px 0 0 !important;padding:9px 18px !important;font-size:13px !important;font-weight:500 !important;color:#6B8090 !important;background:transparent !important;border:none !important;}
.stTabs [aria-selected="true"]{background:#FFFFFF !important;color:#1B3A4B !important;font-weight:700 !important;border-bottom:2px solid #2A7A8C !important;}
.stTabs [data-baseweb="tab-panel"]{background:#FFFFFF !important;border:1px solid #DDE4EA !important;border-top:none !important;border-radius:0 0 10px 10px !important;padding:1.5rem 1.75rem !important;}
.fin-kpi-row{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0 20px}
.fin-kpi{background:#fff;border:1px solid #E4E7EF;border-radius:12px;padding:16px 18px;flex:1;min-width:130px}
.fin-kpi.r{border-top:3px solid #DC2626}.fin-kpi.a{border-top:3px solid #D97706}.fin-kpi.b{border-top:3px solid #2563EB}.fin-kpi.g{border-top:3px solid #16A34A}.fin-kpi.p{border-top:3px solid #7C3AED}
.fin-kpi .lbl{font-size:11px;font-weight:600;color:#8B94A3;text-transform:uppercase;letter-spacing:.06em;margin:0 0 5px}
.fin-kpi .val{font-size:23px;font-weight:700;color:#1A1F2E;margin:0;line-height:1.1}
.fin-kpi .sub{font-size:12px;color:#8B94A3;margin:3px 0 0}
.fin-card{background:#fff;border:1px solid #E4E7EF;border-radius:10px;padding:12px 14px;margin-bottom:8px;display:flex;align-items:center;gap:10px}
.fin-card.vc{border-left:3px solid #DC2626;background:#FEF2F2}.fin-card.av{border-left:3px solid #D97706}
.fin-card .ct{font-weight:600;font-size:14px;color:#1A1F2E}.fin-card .cm{font-size:12px;color:#8B94A3;margin-top:2px}
.fin-card .cd{font-size:11px;color:#8B94A3;margin-top:2px}.fin-card .cv{font-weight:700;font-size:15px;color:#1A1F2E;white-space:nowrap}
.fin-card .dr{font-size:12px;color:#DC2626;margin-top:1px}.fin-card .da{font-size:12px;color:#D97706;margin-top:1px}
.fin-badge{display:inline-block;font-size:11px;font-weight:600;padding:2px 8px;border-radius:20px;white-space:nowrap}
.fin-ptag{display:inline-block;font-size:11px;font-weight:700;padding:1px 7px;border-radius:4px}
.fin-sec{font-size:13px;font-weight:700;color:#4B5263;text-transform:uppercase;letter-spacing:.06em;margin:0 0 3px}
.fin-secs{font-size:12px;color:#8B94A3;margin:0 0 12px}
.fin-div{height:1px;background:#E4E7EF;margin:24px 0 20px}
.fin-warn{background:#FFFBEB;border:1px solid #FCD34D;border-left:3px solid #D97706;border-radius:8px;padding:9px 14px;font-size:13px;color:#92400E;margin-bottom:16px}
.fin-empty{background:#F7F8FC;border:1px dashed #E4E7EF;border-radius:10px;padding:20px;text-align:center;color:#8B94A3;font-size:13px;margin-bottom:8px}
.fin-aprov{background:#fff;border:1px solid #E4E7EF;border-radius:10px;padding:14px;margin-bottom:10px}
.fin-aprov .err{font-size:12px;color:#DC2626;margin-top:3px}.fin-aprov .ds{font-size:11px;color:#8B94A3;margin-top:2px}
.notif-panel{background:#fff;border:1px solid #E4E7EF;border-radius:12px;margin-bottom:20px;overflow:hidden}
.notif-item{padding:10px 16px;border-bottom:1px solid #F0F2F5;display:flex;align-items:flex-start;gap:10px}
.notif-item:last-child{border-bottom:none}.notif-item.nova{background:#FFFBEB}
.notif-dot{width:8px;height:8px;border-radius:50%;background:#D97706;flex-shrink:0;margin-top:5px}
.notif-dot.lida{background:#E4E7EF}
.notif-badge{display:inline-flex;align-items:center;justify-content:center;background:#DC2626;color:#fff;font-size:10px;font-weight:700;border-radius:10px;padding:1px 6px;min-width:18px}
</style>
"""

def n_notifs_nao_lidas() -> int:
    return len([n for n in st.session_state.get("notificacoes", []) if not n.get("lida")])

def reg_hist(acao, n, form, proj, val, mot=""):
    from datetime import datetime
    entrada = {"timestamp": datetime.now().strftime("%d/%m/%Y %H:%M"),
               "acao": acao, "n_fatura": n, "formador": form,
               "projeto": proj, "valor": val, "motivo": mot}
    st.session_state.setdefault("historico", []).append(entrada)
    try:
        from app.db_financeiro import _log_evento
        _log_evento(tipo=f"financeiro_{acao.lower().replace(' ','_')}",
                    descricao=f"{acao} — {n} | {form} | {proj} | {eur(val)}" + (f" | {mot}" if mot else ""),
                    dados=entrada)
    except Exception:
        pass


def marcar_todas_lidas():
    for n in st.session_state.get("notificacoes", []):
        n["lida"] = True
