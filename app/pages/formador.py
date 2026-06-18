"""Pagina do formador."""
from __future__ import annotations
import re
from datetime import datetime
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
# MOCK DATA
# ---------------------------------------------------------------------------
_MOCK_ACOES = [
    {"id": "a1", "magna_id": "COMPETE2030-FSE+-01195000", "codigo": "LIKE GARDEN.2.PCE",
     "nome": "Escalada e desmanche de árvores com motosserra", "empresa_cliente": "Like Garden",
     "data_inicio": "2026-02-19", "data_fim": "2026-03-13", "volume_horas": 50,
     "formandos_certificados": 18, "estado": "fechada", "projeto": "MENTORES", "tem_fatura": True},
    {"id": "a2", "magna_id": "COMPETE2030-FSE+-01196000", "codigo": "CAMOESAS.03.PCE",
     "nome": "Segurança nos trabalhos de construção civil",
     "empresa_cliente": "CAMOESAS, LDA", "data_inicio": "2025-11-30", "data_fim": "2025-12-12",
     "volume_horas": 24, "formandos_certificados": 16, "estado": "fechada", "projeto": "ANIET", "tem_fatura": False},
    {"id": "a3", "magna_id": "COMPETE2030-FSE+-01195000", "codigo": "FENABEL.GEPSLT_16",
     "nome": "Gestão de emergências e primeiros socorros no local de trabalho",
     "empresa_cliente": "Fenabel, S.A", "data_inicio": "2026-05-14", "data_fim": "2026-06-04",
     "volume_horas": 16, "formandos_certificados": 0, "estado": "a_decorrer", "projeto": "MENTORES", "tem_fatura": False},
    {"id": "a4", "magna_id": "COMPETE2030-FSE+-01196000", "codigo": "FORESTCORTE.2.PCE",
     "nome": "Utilização da motosserra nas operações florestais",
     "empresa_cliente": "Forestcorte", "data_inicio": "2026-04-10", "data_fim": "2026-05-31",
     "volume_horas": 25, "formandos_certificados": 8, "estado": "terminada_sem_fecho", "projeto": "ANIET", "tem_fatura": False},
]

_MOCK_FATURAS = [
    {"id": "f1", "numero_fatura": "FT2026/0142", "valor": 3200, "estado": "aprovada",
     "created_at": "2026-06-01", "acao_codigo": "LIKE GARDEN.2.PCE",
     "acao_nome": "Escalada e desmanche de árvores com motosserra",
     "projeto": "MENTORES", "prazo_pagamento": "2026-06-21", "pago_em": None,
     "notas": "", "ficheiro_url": None},
    {"id": "f2", "numero_fatura": "FT2026/0110", "valor": 1800, "estado": "paga",
     "created_at": "2026-05-10", "acao_codigo": "CAMOESAS.03.PCE",
     "acao_nome": "Segurança nos trabalhos de construção civil",
     "projeto": "ANIET", "prazo_pagamento": "2026-05-30", "pago_em": "2026-05-28",
     "notas": "", "ficheiro_url": None},
    {"id": "f3", "numero_fatura": "FT2026/0155", "valor": 2400, "estado": "leitura_falhada",
     "created_at": "2026-06-15", "acao_codigo": "FENABEL.GEPSLT_16",
     "acao_nome": "Gestão de emergências e primeiros socorros",
     "projeto": "MENTORES", "prazo_pagamento": None, "pago_em": None,
     "notas": "Código interno não encontrado no sistema", "ficheiro_url": None},
]

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def eur(v):
    try:
        return f"€\u202f{float(v):,.0f}".replace(",", ".")
    except Exception:
        return "€ —"


def label_estado_fatura(estado):
    return {
        "submetida": "⏳ Submetida",
        "leitura_falhada": "⚠️ Verificar",
        "acao_nao_fechada": "⚠️ Ação não fechada",
        "aprovada": "✅ Aprovada",
        "paga": "💳 Paga",
        "rejeitada": "❌ Rejeitada",
    }.get(estado, estado)


def label_estado_acao(estado):
    return {
        "fechada": "✅ Fechada",
        "a_decorrer": "🔵 A decorrer",
        "planeada": "📋 Planeada",
        "terminada_sem_fecho": "⚠️ Por fechar",
    }.get(estado, estado)


# ---------------------------------------------------------------------------
# QUERIES
# ---------------------------------------------------------------------------
def _get_acoes(formador_id):
    if not SUPABASE_OK:
        return _MOCK_ACOES
    try:
        r = get_supabase().table("acoes").select(
            "id,magna_id,codigo,nome,empresa_cliente,data_inicio,data_fim,"
            "volume_horas,formandos_certificados,estado"
        ).eq("formador_id", formador_id).order("data_fim", desc=True).execute()
        if not r.data:
            return _MOCK_ACOES
        ids = [a["id"] for a in r.data]
        fat_r = get_supabase().table("faturas").select("acao_id").in_("acao_id", ids).execute()
        fat_ids = {f["acao_id"] for f in (fat_r.data or [])}
        for a in r.data:
            a["tem_fatura"] = a["id"] in fat_ids
        return r.data
    except Exception:
        return _MOCK_ACOES


def _get_faturas(formador_id):
    if not SUPABASE_OK:
        return st.session_state.get("mock_fat_form", list(_MOCK_FATURAS))
    try:
        r = get_supabase().table("faturas").select(
            "id,numero_fatura,valor,estado,created_at,prazo_pagamento,pago_em,notas,ficheiro_url,"
            "acoes(codigo,nome)"
        ).eq("formador_id", formador_id).order("created_at", desc=True).execute()
        if not r.data:
            return st.session_state.get("mock_fat_form", list(_MOCK_FATURAS))
        for d in r.data:
            a = d.get("acoes") or {}
            d["acao_codigo"] = a.get("codigo") or "—"
            d["acao_nome"] = a.get("nome") or "—"
        return r.data
    except Exception:
        return st.session_state.get("mock_fat_form", list(_MOCK_FATURAS))


def _get_acao_por_codigo(codigo):
    if not SUPABASE_OK:
        m = [a for a in _MOCK_ACOES if a["codigo"].upper() == codigo.upper()]
        return m[0] if m else None
    try:
        r = get_supabase().table("acoes").select(
            "id,codigo,nome,empresa_cliente,estado,volume_horas,formandos_certificados,data_inicio,data_fim"
        ).ilike("codigo", codigo).execute()
        return r.data[0] if r.data else None
    except Exception:
        return None


def _submeter_bd(formador_id, acao_id, dados, ficheiro_bytes, nome_fich):
    if not SUPABASE_OK:
        if "mock_fat_form" not in st.session_state:
            st.session_state.mock_fat_form = list(_MOCK_FATURAS)
        nova = {
            "id": f"f{len(st.session_state.mock_fat_form) + 1}",
            "numero_fatura": dados.get("numero_fatura") or "—",
            "valor": dados.get("valor") or 0,
            "estado": "submetida", "created_at": datetime.now().strftime("%Y-%m-%d"),
            "acao_codigo": st.session_state.get("_sub_cod", "—"),
            "acao_nome": st.session_state.get("_sub_nome", "—"),
            "projeto": st.session_state.get("_sub_proj", "—"),
            "prazo_pagamento": None, "pago_em": None, "notas": "", "ficheiro_url": None,
        }
        st.session_state.mock_fat_form.insert(0, nova)
        return True
    try:
        url = None
        try:
            sb = get_supabase()
            path = f"faturas/{formador_id}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{nome_fich}"
            sb.storage.from_("faturas").upload(path, ficheiro_bytes,
                file_options={"content-type": "application/pdf"})
            url = sb.storage.from_("faturas").get_public_url(path)
        except Exception:
            pass
        get_supabase_admin().table("faturas").insert({
            "formador_id": formador_id, "acao_id": acao_id,
            "numero_fatura": dados.get("numero_fatura"),
            "data_fatura": dados.get("data_fatura"),
            "valor": dados.get("valor"),
            "nif_emitente": dados.get("nif_emitente"),
            "estado": "submetida", "ficheiro_url": url,
            "dados_extraidos": dados,
        }).execute()
        return True
    except Exception as e:
        st.error(f"Erro: {e}")
        return False


# ---------------------------------------------------------------------------
# LEITURA PDF
# ---------------------------------------------------------------------------
def _ler_pdf(b):
    try:
        import pdfplumber
        import io as _io
    except ImportError:
        return {"erro": "pdfplumber não instalado"}
    r = {"numero_fatura": None, "nif_emitente": None, "nif_destinatario": None,
         "valor": None, "data_fatura": None, "erro": None}
    try:
        with pdfplumber.open(_io.BytesIO(b)) as pdf:
            txt = "\n".join(p.extract_text() or "" for p in pdf.pages)
        m = re.search(r"(?:fatura|recibo|ft|fr)[^\d]*(\d{4}[/\-]\d+)", txt, re.I)
        if m:
            r["numero_fatura"] = m.group(1)
        nifs = re.findall(r"\b\d{9}\b", txt)
        if len(nifs) >= 1:
            r["nif_emitente"] = nifs[0]
        if len(nifs) >= 2:
            r["nif_destinatario"] = nifs[1]
        m = re.search(r"(?:total|valor|montante)[^\d€]*[€]?\s*([\d\s.,]+)\s*(?:€|eur)?", txt, re.I)
        if m:
            try:
                r["valor"] = float(m.group(1).replace(" ", "").replace(".", "").replace(",", "."))
            except Exception:
                pass
        m = re.search(r"\b(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})\b", txt)
        if m:
            r["data_fatura"] = f"{m.group(3)}-{m.group(2).zfill(2)}-{m.group(1).zfill(2)}"
    except Exception as e:
        r["erro"] = str(e)
    return r


# ---------------------------------------------------------------------------
# TAB 1 — SUBMETER FATURA
# ---------------------------------------------------------------------------
def _submeter(user):
    formador_id = user.get("id") or "mock"

    st.subheader("📤 Submeter fatura")
    st.caption("Valida o código da ação, carrega o PDF e confirma os dados.")

    # PASSO 1
    st.markdown("**1 · Código interno da ação**")
    col_cod, col_btn = st.columns([3, 1])
    with col_cod:
        codigo = st.text_input("Código", placeholder="Ex: LIKE GARDEN.2.PCE",
                               key="sub_cod", label_visibility="collapsed")
    with col_btn:
        if st.button("🔍 Validar", key="sub_val", use_container_width=True):
            if codigo:
                with st.spinner("A verificar..."):
                    acao = _get_acao_por_codigo(codigo.strip())
                if acao:
                    st.session_state.acao_val = acao
                    st.session_state._sub_cod = acao.get("codigo", "—")
                    st.session_state._sub_nome = acao.get("nome", "—")
                    st.session_state._sub_proj = acao.get("projeto", "—")
                else:
                    st.session_state.acao_val = None
                    st.warning("⚠️ Código não encontrado. Confirma na Magna.")

    acao_val = st.session_state.get("acao_val")
    if acao_val:
        fechada = acao_val.get("estado") == "fechada"
        with st.container(border=True):
            st.markdown(f"**{acao_val.get('codigo', '—')}** — {acao_val.get('nome', '—')}")
            st.caption(f"Empresa: {acao_val.get('empresa_cliente', '—')}  ·  Projeto: {acao_val.get('projeto', '—')}")
            st.caption(f"Período: {str(acao_val.get('data_inicio', '—'))[:10]} → {str(acao_val.get('data_fim', '—'))[:10]}")
            c1, c2 = st.columns(2)
            c1.metric("Horas", f"{acao_val.get('volume_horas', '—')}h")
            c2.metric("Formandos", acao_val.get("formandos_certificados", "—"))
            if fechada:
                st.success("✅ Ação fechada — pronta a faturar.")
            else:
                st.warning("⚠️ Ação ainda não fechada — o pagamento só é processado após fecho.")

    st.divider()

    # PASSO 2
    st.markdown("**2 · Carrega o PDF da fatura**")
    ficheiro = st.file_uploader("PDF da fatura", type=["pdf"], key="sub_pdf", label_visibility="collapsed")
    dados_lidos = st.session_state.get("dados_pdf")

    if ficheiro and not dados_lidos:
        with st.spinner("A ler o PDF..."):
            d = _ler_pdf(ficheiro.getvalue())
        if d.get("erro"):
            st.error(f"Erro na leitura: {d['erro']}")
        else:
            st.session_state.dados_pdf = d
            dados_lidos = d

    if ficheiro and dados_lidos:
        st.markdown("**Confirma os dados extraídos:**")
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Nº Fatura", value=dados_lidos.get("numero_fatura") or "", key="sub_nf")
            st.text_input("Data (AAAA-MM-DD)", value=dados_lidos.get("data_fatura") or "", key="sub_dt")
        with c2:
            st.number_input("Valor (€)", min_value=0.0, step=0.01,
                            value=float(dados_lidos.get("valor") or 0), key="sub_val2", format="%.2f")
            st.text_input("NIF emitente", value=dados_lidos.get("nif_emitente") or "", key="sub_nif")

    st.divider()

    # PASSO 3
    st.markdown("**3 · Submeter**")
    pode = acao_val and dados_lidos and ficheiro
    if not pode:
        missing = []
        if not acao_val:
            missing.append("código validado")
        if not ficheiro:
            missing.append("PDF carregado")
        if missing:
            st.warning(f"Ainda falta: {', '.join(missing)}")

    if st.button("📤 Submeter fatura", type="primary", disabled=not pode, key="sub_btn"):
        df = {
            "numero_fatura": st.session_state.get("sub_nf") or dados_lidos.get("numero_fatura"),
            "data_fatura": st.session_state.get("sub_dt") or dados_lidos.get("data_fatura"),
            "valor": st.session_state.get("sub_val2") or dados_lidos.get("valor"),
            "nif_emitente": st.session_state.get("sub_nif") or dados_lidos.get("nif_emitente"),
        }
        with st.spinner("A submeter..."):
            ok = _submeter_bd(formador_id, acao_val["id"], df, ficheiro.getvalue(), ficheiro.name)
        if ok:
            st.success("✅ Fatura submetida! O financeiro irá analisar brevemente.")
            for k in ["acao_val", "dados_pdf", "sub_cod", "sub_nf", "sub_dt", "sub_val2", "sub_nif"]:
                st.session_state.pop(k, None)
            st.rerun()


# ---------------------------------------------------------------------------
# TAB 2 — FATURAS
# ---------------------------------------------------------------------------
def _faturas(user):
    formador_id = user.get("id") or "mock"
    faturas = _get_faturas(formador_id)

    n_sub = len([f for f in faturas if f["estado"] in ("submetida", "leitura_falhada", "acao_nao_fechada")])
    n_apr = len([f for f in faturas if f["estado"] == "aprovada"])
    n_pago = len([f for f in faturas if f["estado"] == "paga"])
    n_rej = len([f for f in faturas if f["estado"] == "rejeitada"])
    t_pago = sum(f.get("valor") or 0 for f in faturas if f["estado"] == "paga")

    cols = st.columns(4 if n_rej > 0 else 3)
    cols[0].metric("⏳ Em análise", n_sub, help="aguardam resposta")
    cols[1].metric("✅ Aprovadas", n_apr, help="a aguardar pagamento")
    cols[2].metric("💳 Pagas", eur(t_pago), help=f"{n_pago} faturas")
    if n_rej > 0:
        cols[3].metric("❌ Rejeitadas", n_rej, help="requerem atenção")
        st.warning(f"❌ Tens {n_rej} fatura(s) rejeitada(s). Verifica o motivo e resubmete.")

    st.divider()

    col_f, col_p = st.columns([2, 3])
    with col_f:
        filtro = st.selectbox("Estado", ["Todas", "Em análise", "Aprovada", "Paga", "Rejeitada"], key="fat_fil")
    with col_p:
        pesq = st.text_input("Pesquisar", placeholder="Pesquisar nº fatura ou ação...",
                             key="fat_pesq", label_visibility="collapsed")

    fat_fil = faturas
    mapa = {"Em análise": ["submetida", "leitura_falhada", "acao_nao_fechada"],
            "Aprovada": ["aprovada"], "Paga": ["paga"], "Rejeitada": ["rejeitada"]}
    if filtro != "Todas":
        fat_fil = [f for f in fat_fil if f["estado"] in mapa.get(filtro, [])]
    if pesq:
        p = pesq.lower()
        fat_fil = [f for f in fat_fil if p in (f.get("numero_fatura") or "").lower()
                   or p in (f.get("acao_codigo") or "").lower()
                   or p in (f.get("acao_nome") or "").lower()]

    st.subheader(f"Faturas ({len(fat_fil)})")
    if not fat_fil:
        st.info("Nenhuma fatura encontrada.")
        return

    for f in fat_fil:
        estado = f.get("estado") or "submetida"
        n_fat = f.get("numero_fatura") or "—"
        valor = f.get("valor") or 0
        cod = f.get("acao_codigo") or "—"
        nome_a = f.get("acao_nome") or "—"
        proj = f.get("projeto") or "—"
        criada = str(f.get("created_at") or "—")[:10]
        prazo = str(f.get("prazo_pagamento") or "—")[:10]
        pago_em = str(f.get("pago_em") or "—")[:10]
        notas = f.get("notas") or ""
        url = f.get("ficheiro_url")
        fid = f.get("id") or n_fat

        with st.container(border=True):
            c_info, c_val = st.columns([5, 2])
            with c_info:
                st.markdown(f"**{n_fat}**  ·  {label_estado_fatura(estado)}")
                st.caption(f"{proj} · {cod}")
                st.caption(nome_a[:60])
                st.caption(f"Submetida: {criada}")
                if estado == "paga" and pago_em != "—":
                    st.caption(f"💳 Pago em {pago_em}")
                elif estado == "aprovada" and prazo != "—":
                    st.caption(f"📅 Prazo pagamento: {prazo}")
                elif estado in ("rejeitada", "leitura_falhada", "acao_nao_fechada") and notas:
                    st.error(f"❌ {notas}")
            with c_val:
                st.metric("Valor", eur(valor))
                if url:
                    st.link_button("📄 Ver fatura", url, use_container_width=True)
                if estado in ("rejeitada", "leitura_falhada"):
                    if st.button("🔄 Re-submeter", key=f"rsub_{fid}", use_container_width=True):
                        st.session_state["sub_cod"] = cod
                        st.session_state.pop("acao_val", None)
                        st.toast("Vai à tab 'Submeter fatura' para resubmeter.")

    st.divider()
    t_pago_2026 = sum(f.get("valor") or 0 for f in faturas
                      if f["estado"] == "paga" and str(f.get("created_at", "")).startswith("2026"))
    t_ano = sum(f.get("valor") or 0 for f in faturas if str(f.get("created_at", "")).startswith("2026"))
    c1, c2 = st.columns(2)
    c1.metric("Total recebido 2026", eur(t_pago_2026))
    c2.metric("Total submetido 2026", eur(t_ano))


# ---------------------------------------------------------------------------
# TAB 3 — AÇÕES
# ---------------------------------------------------------------------------
def _acoes(user):
    formador_id = user.get("id") or "mock"
    acoes = _get_acoes(formador_id)

    n_dec = len([a for a in acoes if a["estado"] == "a_decorrer"])
    n_fec = len([a for a in acoes if a["estado"] == "fechada"])
    n_pfec = len([a for a in acoes if a["estado"] == "terminada_sem_fecho"])
    n_sfat = len([a for a in acoes if a["estado"] == "fechada" and not a.get("tem_fatura")])

    cols = st.columns(4 if n_sfat > 0 else 3)
    cols[0].metric("🔵 A decorrer", n_dec, help="ações ativas")
    cols[1].metric("✅ Fechadas", n_fec, help="prontas a faturar")
    cols[2].metric("⚠️ Por fechar", n_pfec, help="requerem fecho")
    if n_sfat > 0:
        cols[3].metric("🟣 Sem fatura", n_sfat, help="fechadas sem fatura")
        st.warning(f"🟣 Tens {n_sfat} ação(ões) fechada(s) sem fatura submetida. Podes faturar agora.")

    st.divider()

    col_f, col_p = st.columns([2, 3])
    with col_f:
        filtro = st.selectbox("Estado", ["Todas", "A decorrer", "Fechada", "Por fechar", "Planeada"], key="ac_fil")
    with col_p:
        pesq = st.text_input("Pesquisar", placeholder="Pesquisar código ou empresa...",
                             key="ac_pesq", label_visibility="collapsed")

    ac_fil = acoes
    mapa = {"A decorrer": "a_decorrer", "Fechada": "fechada",
            "Por fechar": "terminada_sem_fecho", "Planeada": "planeada"}
    if filtro != "Todas":
        ac_fil = [a for a in ac_fil if a["estado"] == mapa.get(filtro, filtro)]
    if pesq:
        p = pesq.lower()
        ac_fil = [a for a in ac_fil if p in (a.get("codigo") or "").lower()
                  or p in (a.get("empresa_cliente") or "").lower()
                  or p in (a.get("nome") or "").lower()]

    st.subheader(f"Ações ({len(ac_fil)})")
    if not ac_fil:
        st.info("Nenhuma ação encontrada.")
        return

    for a in ac_fil:
        estado = a.get("estado") or "—"
        codigo = a.get("codigo") or a.get("magna_id") or "—"
        nome = a.get("nome") or "—"
        empresa = a.get("empresa_cliente") or "—"
        d_ini = str(a.get("data_inicio") or "—")[:10]
        d_fim = str(a.get("data_fim") or "—")[:10]
        horas = a.get("volume_horas") or 0
        form = a.get("formandos_certificados") or 0
        proj = a.get("projeto") or "—"
        tem_fat = a.get("tem_fatura", False)

        with st.container(border=True):
            c_info, c_btn = st.columns([5, 2])
            with c_info:
                st.markdown(f"**{codigo}**  ·  {label_estado_acao(estado)}")
                st.caption(f"{proj} · {empresa}")
                st.caption(nome[:60])
                st.caption(f"{d_ini} → {d_fim} · {horas}h · {form} formandos")
                if estado == "terminada_sem_fecho":
                    st.warning("⚠️ Terminada mas não fechada na Magna — contacta o coordenador.")
                elif estado == "a_decorrer":
                    st.caption("🔵 Em curso — podes faturar após o fecho.")
                elif estado == "fechada" and not tem_fat:
                    st.caption("🟣 Ação fechada sem fatura — podes submeter agora.")
                elif estado == "fechada" and tem_fat:
                    st.caption("✅ Fatura já submetida.")
            with c_btn:
                if estado == "fechada" and not tem_fat:
                    if st.button("📤 Faturar", key=f"fat_ac_{a['id']}",
                                 use_container_width=True, type="primary"):
                        st.session_state["sub_cod"] = codigo
                        st.session_state.pop("acao_val", None)
                        st.toast(f"Vai à tab 'Submeter fatura' — código {codigo} já preenchido.")


# ---------------------------------------------------------------------------
# RENDER PRINCIPAL
# ---------------------------------------------------------------------------
def render(user: dict):
    st.header(f"Bem-vindo, {user['nome']}")
    st.caption("Perfil: Formador")

    faturas = _get_faturas(user.get("id") or "mock")
    n_rej = len([f for f in faturas if f["estado"] == "rejeitada"])
    n_sfat = len([a for a in _get_acoes(user.get("id") or "mock")
                  if a["estado"] == "fechada" and not a.get("tem_fatura")])

    label_1 = f"📚 Ações{' 🟣' if n_sfat > 0 else ''}"
    label_2 = f"📋 Faturas{' ❗' if n_rej > 0 else ''}"
    label_3 = "📤 Submeter fatura"

    tab1, tab2, tab3 = st.tabs([label_1, label_2, label_3])
    with tab1:
        _acoes(user)
    with tab2:
        _faturas(user)
    with tab3:
        _submeter(user)
