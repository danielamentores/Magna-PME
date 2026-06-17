"""Pagina do formador."""
from __future__ import annotations
import io
import mimetypes
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
.f-kpi-row{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0 24px}
.f-kpi{background:#fff;border:1px solid #E4E7EF;border-radius:12px;padding:16px 18px;flex:1;min-width:130px}
.f-kpi.a{border-top:3px solid #D97706}.f-kpi.b{border-top:3px solid #2563EB}
.f-kpi.g{border-top:3px solid #16A34A}.f-kpi.r{border-top:3px solid #DC2626}
.f-kpi .lbl{font-size:11px;font-weight:600;color:#8B94A3;text-transform:uppercase;letter-spacing:.06em;margin:0 0 5px}
.f-kpi .val{font-size:23px;font-weight:700;color:#1A1F2E;margin:0;line-height:1.1}
.f-kpi .sub{font-size:12px;color:#8B94A3;margin:3px 0 0}

.f-card{background:#fff;border:1px solid #E4E7EF;border-radius:10px;padding:14px 16px;margin-bottom:8px}
.f-card.paga{border-left:3px solid #16A34A;background:#F0FDF4}
.f-card.submetida{border-left:3px solid #D97706}
.f-card.aprovada{border-left:3px solid #2563EB}
.f-card.rejeitada{border-left:3px solid #DC2626;background:#FEF2F2}

.f-badge{display:inline-block;font-size:11px;font-weight:600;padding:2px 8px;border-radius:20px;white-space:nowrap}
.f-ptag{display:inline-block;font-size:11px;font-weight:700;padding:1px 7px;border-radius:4px}
.f-sec{font-size:13px;font-weight:700;color:#4B5263;text-transform:uppercase;letter-spacing:.06em;margin:0 0 3px}
.f-secs{font-size:12px;color:#8B94A3;margin:0 0 12px}
.f-div{height:1px;background:#E4E7EF;margin:24px 0 20px}
.f-empty{background:#F7F8FC;border:1px dashed #E4E7EF;border-radius:10px;padding:20px;text-align:center;color:#8B94A3;font-size:13px}
.f-warn{background:#FFFBEB;border:1px solid #FCD34D;border-left:3px solid #D97706;
        border-radius:8px;padding:9px 14px;font-size:13px;color:#92400E;margin-bottom:12px}
.f-success{background:#F0FDF4;border:1px solid #BBF7D0;border-left:3px solid #16A34A;
           border-radius:8px;padding:9px 14px;font-size:13px;color:#166534;margin-bottom:12px}
.f-acao{background:#fff;border:1px solid #E4E7EF;border-radius:10px;padding:12px 14px;margin-bottom:8px}
.f-acao .cod{font-weight:700;font-size:14px;color:#1A1F2E}
.f-acao .meta{font-size:12px;color:#8B94A3;margin-top:2px}
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
     "formandos_certificados":18,"estado":"fechada","projeto":"MENTORES"},
    {"id":"a2","magna_id":"COMPETE2030-FSE+-01196000","codigo":"CAMOESAS.03.PCE",
     "nome":"Segurança nos trabalhos de construção civil",
     "empresa_cliente":"CAMOESAS, LDA","data_inicio":"2025-11-30","data_fim":"2025-12-12",
     "volume_horas":24,"formandos_certificados":16,"estado":"fechada","projeto":"ANIET"},
    {"id":"a3","magna_id":"COMPETE2030-FSE+-01195000","codigo":"FENABEL.GEPSLT_16",
     "nome":"Gestão de emergências e primeiros socorros no local de trabalho",
     "empresa_cliente":"Fenabel, S.A","data_inicio":"2026-05-14","data_fim":"2026-06-04",
     "volume_horas":16,"formandos_certificados":0,"estado":"a_decorrer","projeto":"MENTORES"},
]

_MOCK_FATURAS = [
    {"id":"f1","numero_fatura":"FT2026/0142","valor":3200,"estado":"aprovada",
     "created_at":"2026-06-01","acao_codigo":"LIKE GARDEN.2.PCE",
     "acao_nome":"Escalada e desmanche de árvores com motosserra",
     "projeto":"MENTORES","prazo_pagamento":"2026-06-21","notas":""},
    {"id":"f2","numero_fatura":"FT2026/0138","valor":1800,"estado":"paga",
     "created_at":"2026-05-10","acao_codigo":"CAMOESAS.03.PCE",
     "acao_nome":"Segurança nos trabalhos de construção civil",
     "projeto":"ANIET","prazo_pagamento":"2026-05-30","pago_em":"2026-05-28","notas":""},
    {"id":"f3","numero_fatura":"FT2026/0155","valor":2400,"estado":"submetida",
     "created_at":"2026-06-15","acao_codigo":"FENABEL.GEPSLT_16",
     "acao_nome":"Gestão de emergências e primeiros socorros",
     "projeto":"MENTORES","prazo_pagamento":None,"notas":""},
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

def estado_acao_bdg(estado):
    M={
        "fechada":              ("#F0FDF4","#16A34A","✅ Fechada"),
        "a_decorrer":           ("#EEF3FD","#2563EB","🔵 A decorrer"),
        "planeada":             ("#F5F3FF","#7C3AED","📋 Planeada"),
        "terminada_sem_fecho":  ("#FFFBEB","#D97706","⚠️ Por fechar"),
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
# QUERIES BD
# ---------------------------------------------------------------------------
def _get_acoes(formador_id: str) -> list[dict]:
    if not SUPABASE_OK: return _MOCK_ACOES
    try:
        r = get_supabase().table("acoes").select(
            "id,magna_id,codigo,nome,empresa_cliente,data_inicio,data_fim,"
            "volume_horas,formandos_certificados,estado"
        ).eq("formador_id", formador_id).order("data_fim", desc=True).execute()
        return r.data or _MOCK_ACOES
    except: return _MOCK_ACOES

def _get_faturas(formador_id: str) -> list[dict]:
    if not SUPABASE_OK: return _MOCK_FATURAS
    try:
        r = get_supabase().table("faturas").select(
            "id,numero_fatura,valor,estado,created_at,prazo_pagamento,pago_em,notas,"
            "acoes(codigo,nome,magna_id)"
        ).eq("formador_id", formador_id).order("created_at", desc=True).execute()
        dados = r.data
        if not dados: return _MOCK_FATURAS
        # normalizar para formato consistente
        for d in dados:
            acao = d.get("acoes") or {}
            d["acao_codigo"] = acao.get("codigo") or acao.get("magna_id") or "—"
            d["acao_nome"]   = acao.get("nome") or "—"
        return dados
    except: return _MOCK_FATURAS

def _get_acao_por_codigo(codigo: str) -> Optional[dict]:
    """Valida se o código interno existe."""
    if not SUPABASE_OK:
        m = [a for a in _MOCK_ACOES if a["codigo"].upper() == codigo.upper()]
        return m[0] if m else None
    try:
        r = get_supabase().table("acoes").select(
            "id,codigo,nome,empresa_cliente,estado,formandos_certificados,volume_horas"
        ).ilike("codigo", codigo).execute()
        return r.data[0] if r.data else None
    except: return None

def _submeter_fatura(formador_id: str, acao_id: str, dados_pdf: dict,
                     ficheiro_bytes: bytes, nome_ficheiro: str) -> bool:
    """Submete a fatura para o Supabase."""
    if not SUPABASE_OK:
        # Simula submissão no mock
        nova = {
            "id": f"f{len(_MOCK_FATURAS)+1}",
            "numero_fatura": dados_pdf.get("numero_fatura") or "—",
            "valor": dados_pdf.get("valor") or 0,
            "estado": "submetida",
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "acao_codigo": st.session_state.get("_acao_submissao_codigo","—"),
            "acao_nome": st.session_state.get("_acao_submissao_nome","—"),
            "projeto": "MENTORES",
            "prazo_pagamento": None,
            "notas": "",
        }
        if "mock_faturas_formador" not in st.session_state:
            st.session_state.mock_faturas_formador = list(_MOCK_FATURAS)
        st.session_state.mock_faturas_formador.append(nova)
        return True
    try:
        # Upload do ficheiro para Supabase Storage
        ficheiro_url = None
        try:
            sb = get_supabase()
            path = f"faturas/{formador_id}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{nome_ficheiro}"
            sb.storage.from_("faturas").upload(path, ficheiro_bytes,
                file_options={"content-type": "application/pdf"})
            ficheiro_url = sb.storage.from_("faturas").get_public_url(path)
        except Exception:
            pass  # upload falhou mas continua

        get_supabase_admin().table("faturas").insert({
            "formador_id":    formador_id,
            "acao_id":        acao_id,
            "numero_fatura":  dados_pdf.get("numero_fatura"),
            "data_fatura":    dados_pdf.get("data_fatura"),
            "valor":          dados_pdf.get("valor"),
            "nif_emitente":   dados_pdf.get("nif_emitente"),
            "estado":         "submetida",
            "ficheiro_url":   ficheiro_url,
            "dados_extraidos": dados_pdf,
        }).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao submeter fatura: {e}")
        return False

# ---------------------------------------------------------------------------
# LEITURA PDF (Python puro)
# ---------------------------------------------------------------------------
def _ler_pdf(ficheiro_bytes: bytes) -> dict:
    try:
        import pdfplumber, io as _io
    except ImportError:
        return {"erro": "pdfplumber não instalado"}

    r = {"numero_fatura":None,"nif_emitente":None,"nif_destinatario":None,
         "valor":None,"data_fatura":None,"descricao":None,"texto_completo":"","erro":None}
    try:
        with pdfplumber.open(_io.BytesIO(ficheiro_bytes)) as pdf:
            txt = "\n".join(p.extract_text() or "" for p in pdf.pages)
        r["texto_completo"] = txt

        m = re.search(r"(?:fatura|recibo|ft|fr)[^\d]*(\d{4}[/\-]\d+)", txt, re.I)
        if m: r["numero_fatura"] = m.group(1)

        nifs = re.findall(r"\b\d{9}\b", txt)
        if len(nifs) >= 1: r["nif_emitente"]    = nifs[0]
        if len(nifs) >= 2: r["nif_destinatario"] = nifs[1]

        m = re.search(r"(?:total|valor|montante)[^\d€]*[€]?\s*([\d\s.,]+)\s*(?:€|eur)?", txt, re.I)
        if m:
            try: r["valor"] = float(m.group(1).replace(" ","").replace(".","").replace(",","."))
            except: pass

        m = re.search(r"\b(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})\b", txt)
        if m: r["data_fatura"] = f"{m.group(3)}-{m.group(2).zfill(2)}-{m.group(1).zfill(2)}"

        # Descrição — primeira linha com conteúdo após o cabeçalho
        linhas = [l.strip() for l in txt.split("\n") if len(l.strip()) > 20]
        if linhas: r["descricao"] = linhas[0][:100]

    except Exception as e:
        r["erro"] = str(e)
    return r

# ---------------------------------------------------------------------------
# TAB 1 — SUBMETER FATURA
# ---------------------------------------------------------------------------
def _submeter(user: dict):
    formador_id = user.get("id") or "mock_formador"

    st.markdown(sec("📤 Submeter fatura",
        "Carrega o PDF da tua fatura e associa ao código interno da ação."),
        unsafe_allow_html=True)

    # ---- PASSO 1: Código interno ----
    st.markdown("**1. Código interno da ação**")
    col_cod, col_btn = st.columns([3,1])
    with col_cod:
        codigo = st.text_input("", placeholder="Ex: LIKE GARDEN.2.PCE",
                               key="sub_codigo", label_visibility="collapsed")
    with col_btn:
        st.markdown("<div style='margin-top:4px'>", unsafe_allow_html=True)
        validar = st.button("🔍 Validar", key="sub_validar", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    acao_validada = st.session_state.get("acao_validada")

    if validar and codigo:
        with st.spinner("A verificar código..."):
            acao = _get_acao_por_codigo(codigo.strip())
        if acao:
            st.session_state.acao_validada = acao
            st.session_state._acao_submissao_codigo = acao.get("codigo","—")
            st.session_state._acao_submissao_nome   = acao.get("nome","—")
            acao_validada = acao
        else:
            st.session_state.acao_validada = None
            st.html('<div class="f-warn">⚠️ Código interno não encontrado. Confirma o código na Magna.</div>')

    if acao_validada:
        estado_acao = acao_validada.get("estado","—")
        fechada = estado_acao == "fechada"
        cls = "f-success" if fechada else "f-warn"
        icone = "✅" if fechada else "⚠️"
        aviso = "" if fechada else " — Ação ainda não fechada. O pagamento só é processado após o fecho."
        st.html(
            f'<div class="{cls}">'
            f'{icone} <strong>{acao_validada.get("codigo","—")}</strong> — {acao_validada.get("nome","—")}<br>'
            f'<span style="font-size:12px">{acao_validada.get("empresa_cliente","—")}'
            f'{aviso}</span>'
            f'</div>'
        )

    st.markdown(div(), unsafe_allow_html=True)

    # ---- PASSO 2: Upload PDF ----
    st.markdown("**2. Fatura em PDF**")
    ficheiro = st.file_uploader("", type=["pdf"], key="sub_pdf",
                                label_visibility="collapsed")

    dados_lidos = st.session_state.get("dados_pdf_lidos")

    if ficheiro and not dados_lidos:
        with st.spinner("A ler o PDF..."):
            dados = _ler_pdf(ficheiro.getvalue())
        if dados.get("erro"):
            st.error(f"Erro na leitura: {dados['erro']}")
        else:
            st.session_state.dados_pdf_lidos = dados
            dados_lidos = dados

    if dados_lidos:
        st.markdown("**Dados extraídos do PDF — confirma antes de submeter:**")
        col1, col2 = st.columns(2)
        with col1:
            n_fat = st.text_input("Nº Fatura", value=dados_lidos.get("numero_fatura") or "",
                                  key="sub_nfat")
            data  = st.text_input("Data", value=dados_lidos.get("data_fatura") or "",
                                  key="sub_data", placeholder="AAAA-MM-DD")
        with col2:
            valor = st.number_input("Valor (€)", min_value=0.0, step=0.01,
                                    value=float(dados_lidos.get("valor") or 0),
                                    key="sub_valor", format="%.2f")
            nif   = st.text_input("NIF emitente", value=dados_lidos.get("nif_emitente") or "",
                                  key="sub_nif")

    st.markdown(div(), unsafe_allow_html=True)

    # ---- PASSO 3: Submeter ----
    st.markdown("**3. Submeter**")

    pode_submeter = acao_validada and dados_lidos and ficheiro
    if not pode_submeter:
        missing = []
        if not acao_validada: missing.append("código interno validado")
        if not ficheiro:      missing.append("PDF carregado")
        if ficheiro and not dados_lidos: missing.append("PDF lido")
        if missing:
            st.html(f'<div class="f-warn">Falta: {", ".join(missing)}</div>')

    if st.button("📤 Submeter fatura", type="primary",
                 disabled=not pode_submeter, key="sub_btn"):
        dados_finais = {
            "numero_fatura": st.session_state.get("sub_nfat") or dados_lidos.get("numero_fatura"),
            "data_fatura":   st.session_state.get("sub_data") or dados_lidos.get("data_fatura"),
            "valor":         st.session_state.get("sub_valor") or dados_lidos.get("valor"),
            "nif_emitente":  st.session_state.get("sub_nif") or dados_lidos.get("nif_emitente"),
        }
        with st.spinner("A submeter..."):
            ok = _submeter_fatura(
                formador_id=formador_id,
                acao_id=acao_validada["id"],
                dados_pdf=dados_finais,
                ficheiro_bytes=ficheiro.getvalue(),
                nome_ficheiro=ficheiro.name,
            )
        if ok:
            st.success("✅ Fatura submetida com sucesso! O financeiro irá analisar brevemente.")
            # Limpar estado
            for k in ["acao_validada","dados_pdf_lidos","sub_codigo","sub_nfat",
                      "sub_data","sub_valor","sub_nif"]:
                st.session_state.pop(k, None)
            st.rerun()

# ---------------------------------------------------------------------------
# TAB 2 — AS MINHAS FATURAS
# ---------------------------------------------------------------------------
def _faturas(user: dict):
    formador_id = user.get("id") or "mock_formador"

    faturas = st.session_state.get("mock_faturas_formador") if not SUPABASE_OK \
              else _get_faturas(formador_id)
    if faturas is None:
        faturas = _get_faturas(formador_id)

    # Métricas
    n_sub  = len([f for f in faturas if f["estado"] in ("submetida","leitura_falhada","acao_nao_fechada")])
    n_apr  = len([f for f in faturas if f["estado"] == "aprovada"])
    n_pago = len([f for f in faturas if f["estado"] == "paga"])
    n_rej  = len([f for f in faturas if f["estado"] == "rejeitada"])
    t_pago = sum(f.get("valor") or 0 for f in faturas if f["estado"] == "paga")
    t_pend = sum(f.get("valor") or 0 for f in faturas if f["estado"] in ("submetida","aprovada"))

    st.html(
        '<div class="f-kpi-row">'
        + kpi_h("⏳ Submetidas",  str(n_sub),  "a aguardar análise", "a")
        + kpi_h("✅ Aprovadas",   str(n_apr),  "a aguardar pagamento","b")
        + kpi_h("💳 Pagas",       eur(t_pago), f"{n_pago} faturas",   "g")
        + kpi_h("⚠️ Pendente",    eur(t_pend), "por receber",         "r")
        + '</div>'
    )

    st.html(div())

    # Filtro
    col_f, col_p = st.columns([2,3])
    with col_f:
        filtro = st.selectbox("Estado", ["Todos","Submetida","Aprovada","Paga","Rejeitada"],
                              key="fat_fil")
    with col_p:
        pesq = st.text_input("", placeholder="Pesquisar nº fatura ou ação...",
                             key="fat_pesq", label_visibility="collapsed")

    fat_fil = faturas
    if filtro != "Todos":
        mapa = {"Submetida":"submetida","Aprovada":"aprovada","Paga":"paga","Rejeitada":"rejeitada"}
        fat_fil = [f for f in fat_fil if f["estado"] == mapa.get(filtro, filtro)]
    if pesq:
        p = pesq.lower()
        fat_fil = [f for f in fat_fil if p in (f.get("numero_fatura") or "").lower()
                   or p in (f.get("acao_codigo") or "").lower()
                   or p in (f.get("acao_nome") or "").lower()]

    st.markdown(sec(f"Faturas ({len(fat_fil)})"), unsafe_allow_html=True)

    if not fat_fil:
        st.html('<div class="f-empty">Nenhuma fatura encontrada.</div>')
        return

    for f in fat_fil:
        estado   = f.get("estado") or "submetida"
        n_fat    = f.get("numero_fatura") or "—"
        valor    = f.get("valor") or 0
        cod      = f.get("acao_codigo") or "—"
        nome_a   = f.get("acao_nome") or "—"
        proj     = f.get("projeto") or "—"
        criada   = str(f.get("created_at") or "—")[:10]
        prazo    = str(f.get("prazo_pagamento") or "—")[:10]
        pago_em  = str(f.get("pago_em") or "—")[:10]
        notas    = f.get("notas") or ""

        # Alerta de rejeição destacado
        if estado == "rejeitada":
            motivo_txt = f'<div style="font-size:12px;color:#DC2626;margin-top:4px">❌ Rejeitada{": " + notas if notas else ""}</div>'
        else:
            motivo_txt = ""

        # Info de pagamento
        if estado == "paga" and pago_em != "—":
            pag_txt = f'<div style="font-size:12px;color:#16A34A;margin-top:2px">💳 Pago em {pago_em}</div>'
        elif estado == "aprovada" and prazo != "—":
            pag_txt = f'<div style="font-size:12px;color:#2563EB;margin-top:2px">📅 Prazo pagamento: {prazo}</div>'
        else:
            pag_txt = ""

        st.html(
            f'<div class="f-card {estado}">'
            f'<div style="display:flex;align-items:flex-start;justify-content:space-between">'
            f'<div style="flex:1">'
            f'<div style="font-weight:700;font-size:14px">{n_fat}</div>'
            f'<div style="font-size:12px;color:#8B94A3;margin-top:2px">'
            f'{ptag(proj)}&nbsp;·&nbsp;{cod}&nbsp;·&nbsp;{nome_a[:50]}</div>'
            f'<div style="font-size:11px;color:#8B94A3;margin-top:2px">Submetida: {criada}</div>'
            f'{pag_txt}{motivo_txt}'
            f'</div>'
            f'<div style="text-align:right;min-width:100px">'
            f'<div style="font-weight:700;font-size:16px">{eur(valor)}</div>'
            f'{bdg(estado)}'
            f'</div>'
            f'</div>'
            f'</div>'
        )

# ---------------------------------------------------------------------------
# TAB 3 — AS MINHAS AÇÕES
# ---------------------------------------------------------------------------
def _acoes(user: dict):
    formador_id = user.get("id") or "mock_formador"
    acoes = _get_acoes(formador_id)

    # Métricas
    n_dec  = len([a for a in acoes if a["estado"]=="a_decorrer"])
    n_fec  = len([a for a in acoes if a["estado"]=="fechada"])
    n_pfec = len([a for a in acoes if a["estado"]=="terminada_sem_fecho"])
    n_pl   = len([a for a in acoes if a["estado"]=="planeada"])

    st.html(
        '<div class="f-kpi-row">'
        + kpi_h("🔵 A decorrer",  str(n_dec),  "ações ativas",   "b")
        + kpi_h("✅ Fechadas",    str(n_fec),  "prontas a faturar","g")
        + kpi_h("⚠️ Por fechar",  str(n_pfec), "requerem atenção","a")
        + kpi_h("📋 Planeadas",   str(n_pl),   "futuras",         "r")
        + '</div>'
    )

    st.html(div())

    # Filtro
    col_f, col_p = st.columns([2,3])
    with col_f:
        filtro = st.selectbox("Estado",
                              ["Todas","A decorrer","Fechada","Por fechar","Planeada"],
                              key="ac_fil")
    with col_p:
        pesq = st.text_input("", placeholder="Pesquisar código ou empresa...",
                             key="ac_pesq", label_visibility="collapsed")

    ac_fil = acoes
    if filtro != "Todas":
        mapa = {"A decorrer":"a_decorrer","Fechada":"fechada",
                "Por fechar":"terminada_sem_fecho","Planeada":"planeada"}
        ac_fil = [a for a in ac_fil if a["estado"] == mapa.get(filtro, filtro)]
    if pesq:
        p = pesq.lower()
        ac_fil = [a for a in ac_fil if p in (a.get("codigo") or "").lower()
                  or p in (a.get("empresa_cliente") or "").lower()
                  or p in (a.get("nome") or "").lower()]

    st.markdown(sec(f"Ações ({len(ac_fil)})"), unsafe_allow_html=True)

    if not ac_fil:
        st.html('<div class="f-empty">Nenhuma ação encontrada.</div>')
        return

    for a in ac_fil:
        estado  = a.get("estado") or "—"
        codigo  = a.get("codigo") or a.get("magna_id") or "—"
        nome    = a.get("nome") or "—"
        empresa = a.get("empresa_cliente") or "—"
        d_ini   = str(a.get("data_inicio") or "—")[:10]
        d_fim   = str(a.get("data_fim") or "—")[:10]
        horas   = a.get("volume_horas") or 0
        form    = a.get("formandos_certificados") or 0
        proj    = a.get("projeto") or "—"

        fechada = estado == "fechada"
        aviso = ""
        if estado == "terminada_sem_fecho":
            aviso = '<div style="font-size:12px;color:#D97706;margin-top:3px">⚠️ Ação terminada mas ainda não fechada na Magna.</div>'
        elif estado == "a_decorrer":
            aviso = '<div style="font-size:12px;color:#2563EB;margin-top:3px">🔵 Ação em curso — faturação disponível após fecho.</div>'

        st.html(
            f'<div class="f-acao">'
            f'<div style="display:flex;align-items:flex-start;justify-content:space-between">'
            f'<div style="flex:1">'
            f'<div class="cod">{codigo}&nbsp;&nbsp;{estado_acao_bdg(estado)}</div>'
            f'<div class="meta">{ptag(proj)}&nbsp;·&nbsp;{empresa}</div>'
            f'<div class="meta">{nome[:60]}</div>'
            f'<div class="meta">{d_ini} → {d_fim}&nbsp;·&nbsp;{horas}h&nbsp;·&nbsp;{form} formandos</div>'
            f'{aviso}'
            f'</div>'
            f'{"<div style=\\'margin-top:4px\\'><span style=\\'font-size:12px;color:#16A34A\\'>✅ Pode faturar</span></div>" if fechada else ""}'
            f'</div>'
            f'</div>'
        )

# ---------------------------------------------------------------------------
# RENDER PRINCIPAL
# ---------------------------------------------------------------------------
def render(user: dict):
    st.html(_CSS)
    st.header(f"Bem-vindo, {user['nome']}")
    st.caption("Perfil: Formador")

    tab1, tab2, tab3 = st.tabs(["📤 Submeter fatura", "📋 As minhas faturas", "📚 As minhas ações"])

    with tab1: _submeter(user)
    with tab2: _faturas(user)
    with tab3: _acoes(user)
