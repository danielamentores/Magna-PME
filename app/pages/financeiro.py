"""Pagina do financeiro."""
from __future__ import annotations

import io
from datetime import date, datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# IMPORTS DA BD — com fallback para mock data se Supabase não estiver ligado
# ---------------------------------------------------------------------------

try:
    from app.db_financeiro import (
        get_metricas_dashboard,
        get_faturas_recentes,
        get_despesa_por_projeto,
        get_faturas_pre_aprovacao,
        get_faturas_vencidas,
        get_faturas_a_vencer,
        get_top_formadores_pendentes,
        get_pendente_por_projeto,
        get_cashflow_previsto,
        get_projetos,
        get_historico_financeiro,
        aprovar_fatura,
        rejeitar_fatura,
        marcar_paga,
        get_supabase,
    )
    # Testa ligação real — se as variáveis de ambiente estiverem em falta, falha aqui
    get_supabase()
    SUPABASE_OK = True
except Exception:
    SUPABASE_OK = False

# ---------------------------------------------------------------------------
# MOCK DATA — usado quando Supabase não está disponível
# ---------------------------------------------------------------------------

_MOCK_PROJETOS = [
    {"id": "p1", "nome": "MENTORES",  "magna_id": "COMPETE2030-FSE+-01195000"},
    {"id": "p2", "nome": "ANIET",     "magna_id": "COMPETE2030-FSE+-01196000"},
    {"id": "p3", "nome": "APCMC",     "magna_id": "COMPETE2030-FSE+-01195400"},
    {"id": "p4", "nome": "APIMA",     "magna_id": "COMPETE2030-FSE+-01194800"},
    {"id": "p5", "nome": "PRODUTECH", "magna_id": "COMPETE2030-FSE+-02982000"},
    {"id": "p6", "nome": "CALÇADO",   "magna_id": "COMPETE2030-FSE+-02981900"},
]

_MOCK_PRE_APROVACAO = [
    {"id": "f1", "numero_fatura": "FT2026/0155", "valor": 2400, "estado": "leitura_falhada",   "erro_leitura": "Código interno não encontrado no sistema",    "created_at": "2026-06-15", "ficheiro_url": None, "profiles": {"nome": "Miguel Santos",   "email": "miguel@demo.pt"}, "acoes": {"nome": "MENTORES",  "magna_id": "01195000"}},
    {"id": "f2", "numero_fatura": "FT2026/0153", "valor": 1950, "estado": "acao_nao_fechada",  "erro_leitura": "Nome do formador não corresponde ao projeto", "created_at": "2026-06-14", "ficheiro_url": None, "profiles": {"nome": "Sofia Rodrigues", "email": "sofia@demo.pt"},  "acoes": {"nome": "ANIET",     "magna_id": "01196000"}},
    {"id": "f3", "numero_fatura": "FT2026/0150", "valor": 1800, "estado": "submetida",         "erro_leitura": "Valor diverge do contrato registado",         "created_at": "2026-06-13", "ficheiro_url": None, "profiles": {"nome": "Luís Cardoso",    "email": "luis@demo.pt"},   "acoes": {"nome": "PRODUTECH", "magna_id": "02982000"}},
]

_MOCK_VENCIDAS = [
    {"id": "v1", "numero_fatura": "FT2026/0110", "valor": 1800, "prazo_pagamento": "2026-06-02", "data_fatura": "2026-05-02", "atraso": 14, "profiles": {"nome": "João Silva",  "email": "joao@demo.pt"}, "acoes": {"nome": "MENTORES",  "magna_id": "01195000"}},
    {"id": "v2", "numero_fatura": "FT2026/0108", "valor": 2600, "prazo_pagamento": "2026-06-08", "data_fatura": "2026-05-08", "atraso": 8,  "profiles": {"nome": "Rui Mendes",  "email": "rui@demo.pt"},  "acoes": {"nome": "PRODUTECH", "magna_id": "02982000"}},
    {"id": "v3", "numero_fatura": "FT2026/0105", "valor": 1400, "prazo_pagamento": "2026-06-12", "data_fatura": "2026-05-12", "atraso": 4,  "profiles": {"nome": "Pedro Costa", "email": "pedro@demo.pt"},"acoes": {"nome": "CALÇADO",   "magna_id": "02981900"}},
]

_MOCK_A_VENCER = [
    {"id": "a1", "numero_fatura": "FT2026/0142", "valor": 3200, "prazo_pagamento": "2026-06-21", "data_fatura": "2026-06-01", "dias": 5,  "profiles": {"nome": "João Silva",   "email": "joao@demo.pt"},  "acoes": {"nome": "MENTORES", "magna_id": "01195000"}},
    {"id": "a2", "numero_fatura": "FT2026/0138", "valor": 2800, "prazo_pagamento": "2026-06-27", "data_fatura": "2026-06-03", "dias": 11, "profiles": {"nome": "Ana Ferreira", "email": "ana@demo.pt"},   "acoes": {"nome": "ANIET",    "magna_id": "01196000"}},
    {"id": "a3", "numero_fatura": "FT2026/0136", "valor": 1900, "prazo_pagamento": "2026-07-04", "data_fatura": "2026-06-05", "dias": 18, "profiles": {"nome": "Pedro Costa",  "email": "pedro@demo.pt"}, "acoes": {"nome": "CALÇADO",  "magna_id": "02981900"}},
    {"id": "a4", "numero_fatura": "FT2026/0129", "valor": 2100, "prazo_pagamento": "2026-07-10", "data_fatura": "2026-06-06", "dias": 24, "profiles": {"nome": "Carla Neves",  "email": "carla@demo.pt"}, "acoes": {"nome": "APCMC",    "magna_id": "01195400"}},
    {"id": "a5", "numero_fatura": "FT2026/0127", "valor": 2300, "prazo_pagamento": "2026-07-16", "data_fatura": "2026-06-08", "dias": 30, "profiles": {"nome": "Rui Mendes",   "email": "rui@demo.pt"},   "acoes": {"nome": "APIMA",    "magna_id": "01194800"}},
]

_MOCK_CASHFLOW_LABELS = ["S1 Jun","S2 Jun","S3 Jun","S4 Jun","S1 Jul","S2 Jul","S3 Jul","S4 Jul","S1 Ago","S2 Ago","S3 Ago","S4 Ago","S1 Set"]
_MOCK_CASHFLOW_SAIDAS = [3200, 2100, 4100, 2800, 2600, 3800, 1900, 3200, 2400, 2800, 1800, 2100, 2300]

CORES_PROJETO = {
    "MENTORES":  "#378ADD",
    "ANIET":     "#97C459",
    "APCMC":     "#EF9F27",
    "APIMA":     "#D4537E",
    "PRODUTECH": "#534AB7",
    "CALÇADO":   "#1D9E75",
}

PLOTLY_CONFIG  = {"displayModeBar": False}
ORDEM_OPCOES   = ["Data de vencimento", "Valor (maior primeiro)", "Valor (menor primeiro)", "Projeto"]
ESTADO_BADGE   = {
    "submetida":        ("#FEF3C7", "#92400E", "Submetida"),
    "leitura_falhada":  ("#FEE2E2", "#991B1B", "Leitura falhada"),
    "acao_nao_fechada": ("#FEE2E2", "#991B1B", "Ação não fechada"),
    "aprovada":         ("#D1FAE5", "#065F46", "Aprovada"),
    "paga":             ("#DBEAFE", "#1E40AF", "Paga"),
    "rejeitada":        ("#F3F4F6", "#374151", "Rejeitada"),
}


# ---------------------------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------------------------

def init_state():
    if "historico" not in st.session_state:
        st.session_state.historico = []
    # mock state (só usado quando Supabase não está disponível)
    if not SUPABASE_OK:
        if "mock_pre" not in st.session_state:
            st.session_state.mock_pre = list(_MOCK_PRE_APROVACAO)
        if "mock_vencidas" not in st.session_state:
            st.session_state.mock_vencidas = list(_MOCK_VENCIDAS)
        if "mock_a_vencer" not in st.session_state:
            st.session_state.mock_a_vencer = list(_MOCK_A_VENCER)


def registar_historico(acao: str, n_fatura: str, formador: str, projeto: str, valor: float, motivo: str = ""):
    st.session_state.historico.append({
        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "acao": acao,
        "n_fatura": n_fatura,
        "formador": formador,
        "projeto": projeto,
        "valor": valor,
        "motivo": motivo,
    })


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def fmt_eur(valor) -> str:
    try:
        return f"€ {float(valor):,.0f}".replace(",", ".")
    except Exception:
        return "€ —"


def badge_html(estado: str) -> str:
    bg, color, label = ESTADO_BADGE.get(estado, ("#F3F4F6", "#374151", estado))
    return (
        f"<span style='background:{bg};color:{color};padding:2px 10px;"
        f"border-radius:12px;font-size:12px;font-weight:500'>{label}</span>"
    )


def secao_header(titulo: str, subtitulo: str = ""):
    st.markdown(f"### {titulo}")
    if subtitulo:
        st.caption(subtitulo)
    st.markdown(
        "<div style='height:3px;background:linear-gradient(90deg,#E5E7EB,transparent);"
        "border-radius:2px;margin-bottom:16px'></div>",
        unsafe_allow_html=True,
    )


def ordenar_lista(dados: list[dict], criterio: str) -> list[dict]:
    if criterio == "Valor (maior primeiro)":
        return sorted(dados, key=lambda x: x.get("valor") or 0, reverse=True)
    elif criterio == "Valor (menor primeiro)":
        return sorted(dados, key=lambda x: x.get("valor") or 0)
    elif criterio == "Projeto":
        return sorted(dados, key=lambda x: (x.get("acoes") or {}).get("nome") or "")
    else:
        col = "atraso" if dados and "atraso" in dados[0] else "dias"
        return sorted(dados, key=lambda x: x.get(col) or 0, reverse=True)


def filtrar_por_projeto(dados: list[dict], projeto: str) -> list[dict]:
    if not projeto or projeto == "Todos":
        return dados
    return [d for d in dados if (d.get("acoes") or {}).get("nome") == projeto]


def _row_formador(row: dict) -> str:
    return (row.get("profiles") or {}).get("nome") or "—"


def _row_projeto(row: dict) -> str:
    return (row.get("acoes") or {}).get("nome") or "—"


def _row_email(row: dict) -> str:
    return (row.get("profiles") or {}).get("email") or ""


# ---------------------------------------------------------------------------
# LEITURA PDF (Python puro — sem Gemini)
# ---------------------------------------------------------------------------

def extrair_dados_pdf(ficheiro_bytes: bytes) -> dict:
    """
    Extrai campos da fatura a partir do PDF usando pdfplumber.
    Devolve dict com: numero_fatura, formador, nif, valor, data_fatura.
    """
    import re
    try:
        import pdfplumber
    except ImportError:
        return {"erro": "pdfplumber não instalado. Corre: pip install pdfplumber"}

    resultado = {
        "numero_fatura": None,
        "nif_emitente": None,
        "valor": None,
        "data_fatura": None,
        "texto_completo": "",
        "erro": None,
    }

    try:
        with pdfplumber.open(io.BytesIO(ficheiro_bytes)) as pdf:
            texto = "\n".join(p.extract_text() or "" for p in pdf.pages)
        resultado["texto_completo"] = texto

        # Número de fatura — padrões comuns: FT 2026/123, Fatura n.º 2026/123
        m = re.search(r"(?:fatura|recibo|ft|fr)[^\d]*(\d{4}[/\-]\d+)", texto, re.IGNORECASE)
        if m:
            resultado["numero_fatura"] = m.group(1)

        # NIF — 9 dígitos
        nifs = re.findall(r"\b\d{9}\b", texto)
        if nifs:
            resultado["nif_emitente"] = nifs[0]

        # Valor — procura padrão €, EUR ou "total"
        m = re.search(r"(?:total|valor|montante)[^\d€]*[€]?\s*([\d\s.,]+)\s*(?:€|eur)?", texto, re.IGNORECASE)
        if m:
            val_str = m.group(1).replace(" ", "").replace(".", "").replace(",", ".")
            try:
                resultado["valor"] = float(val_str)
            except ValueError:
                pass

        # Data — DD/MM/AAAA ou DD-MM-AAAA
        m = re.search(r"\b(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})\b", texto)
        if m:
            resultado["data_fatura"] = f"{m.group(3)}-{m.group(2).zfill(2)}-{m.group(1).zfill(2)}"

    except Exception as e:
        resultado["erro"] = str(e)

    return resultado


# ---------------------------------------------------------------------------
# NOTIFICAÇÃO AO FORMADOR (Gmail API — placeholder)
# ---------------------------------------------------------------------------

def notificar_rejeicao(email: str, n_fatura: str, motivo: str) -> bool:
    """
    Envia email de rejeição ao formador via Gmail API.
    TODO: ligar ao gmail_service quando disponível.
    """
    # from integrations.gmail import send_email
    # send_email(to=email, subject=f"Fatura {n_fatura} rejeitada", body=motivo)
    st.toast(f"📧 Notificação enviada para {email} (A ligar ao Gmail API)")
    return True


# ---------------------------------------------------------------------------
# EXPORT EXCEL
# ---------------------------------------------------------------------------

def gerar_excel_projeto(projeto: str, faturas: list[dict]) -> bytes:
    """Gera ficheiro Excel de controlo para um projeto."""
    rows = []
    for f in faturas:
        rows.append({
            "Nº Fatura":        f.get("numero_fatura") or "—",
            "Formador":         _row_formador(f),
            "Projeto":          _row_projeto(f),
            "Valor (€)":        f.get("valor") or 0,
            "Data Fatura":      f.get("data_fatura") or "—",
            "Prazo Pagamento":  f.get("prazo_pagamento") or "—",
            "Estado":           f.get("estado") or "—",
        })
    df = pd.DataFrame(rows)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=projeto[:31])
    return buf.getvalue()


# ---------------------------------------------------------------------------
# COMPONENTE — card fatura vencida
# ---------------------------------------------------------------------------

def card_vencida(row: dict, idx: int, user_nome: str):
    fatura_id  = row.get("id") or str(idx)
    n_fatura   = row.get("numero_fatura") or "—"
    formador   = _row_formador(row)
    projeto    = _row_projeto(row)
    valor      = row.get("valor") or 0
    atraso     = row.get("atraso") or 0
    data_fat   = row.get("data_fatura") or "—"
    prazo      = row.get("prazo_pagamento") or "—"

    st.markdown(
        f"<div style='background:#FEF2F2;border:1px solid #FECACA;border-left:4px solid #DC2626;"
        f"border-radius:8px;padding:14px 16px;margin-bottom:10px'>",
        unsafe_allow_html=True,
    )
    col_info, col_valor, col_acao = st.columns([5, 2, 2])
    with col_info:
        st.markdown(
            f"**{n_fatura}** &nbsp;<span style='font-size:12px;color:#6B7280'>{formador}</span><br>"
            f"<span style='font-size:13px'>`{projeto}`</span><br>"
            f"<span style='font-size:12px;color:#9CA3AF'>Fatura {data_fat}&nbsp;·&nbsp;Prazo {prazo}</span>",
            unsafe_allow_html=True,
        )
    with col_valor:
        st.markdown(
            f"<div style='margin-top:8px'><strong>{fmt_eur(valor)}</strong><br>"
            f"<span style='color:#DC2626;font-size:13px'>+{atraso} dias em atraso</span></div>",
            unsafe_allow_html=True,
        )
    with col_acao:
        if st.button("✓ Marcar pago", key=f"pago_v_{idx}_{fatura_id}", use_container_width=True):
            if SUPABASE_OK:
                if marcar_paga(fatura_id, user_nome):
                    registar_historico("Marcado pago", n_fatura, formador, projeto, valor)
                    st.toast(f"Fatura {n_fatura} marcada como paga.")
                    st.rerun()
            else:
                st.session_state.mock_vencidas = [
                    f for f in st.session_state.mock_vencidas if f.get("id") != fatura_id
                ]
                registar_historico("Marcado pago", n_fatura, formador, projeto, valor)
                st.toast(f"Fatura {n_fatura} marcada como paga.")
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# COMPONENTE — card fatura a vencer
# ---------------------------------------------------------------------------

def card_a_vencer(row: dict, idx: int, user_nome: str):
    fatura_id = row.get("id") or str(idx)
    n_fatura  = row.get("numero_fatura") or "—"
    formador  = _row_formador(row)
    projeto   = _row_projeto(row)
    valor     = row.get("valor") or 0
    dias      = row.get("dias") or 0
    data_fat  = row.get("data_fatura") or "—"
    prazo     = row.get("prazo_pagamento") or "—"

    with st.container(border=True):
        col_info, col_valor, col_acao = st.columns([5, 2, 2])
        with col_info:
            st.markdown(
                f"**{n_fatura}** &nbsp;<span style='font-size:12px;color:#6B7280'>{formador}</span><br>"
                f"<span style='font-size:13px'>`{projeto}`</span><br>"
                f"<span style='font-size:12px;color:#9CA3AF'>Fatura {data_fat}&nbsp;·&nbsp;Prazo {prazo}</span>",
                unsafe_allow_html=True,
            )
        with col_valor:
            st.markdown(
                f"<div style='margin-top:8px'><strong>{fmt_eur(valor)}</strong><br>"
                f"<span style='color:#D97706;font-size:13px'>vence em {dias} dias</span></div>",
                unsafe_allow_html=True,
            )
        with col_acao:
            if st.button("✓ Marcar pago", key=f"pago_a_{idx}_{fatura_id}", use_container_width=True):
                if SUPABASE_OK:
                    if marcar_paga(fatura_id, user_nome):
                        registar_historico("Marcado pago", n_fatura, formador, projeto, valor)
                        st.toast(f"Fatura {n_fatura} marcada como paga.")
                        st.rerun()
                else:
                    st.session_state.mock_a_vencer = [
                        f for f in st.session_state.mock_a_vencer if f.get("id") != fatura_id
                    ]
                    registar_historico("Marcado pago", n_fatura, formador, projeto, valor)
                    st.toast(f"Fatura {n_fatura} marcada como paga.")
                    st.rerun()


# ---------------------------------------------------------------------------
# TAB 1 — DASHBOARD FINANCEIRO
# ---------------------------------------------------------------------------

def render_dashboard(user: dict):
    if SUPABASE_OK:
        metricas   = get_metricas_dashboard()
        recentes   = get_faturas_recentes(10)
        despesa    = get_despesa_por_projeto()
        n_pre      = metricas["pre_aprovacao_count"]
        total_pre  = metricas["pre_aprovacao_total"]
        total_apr  = metricas["aprovado_total"]
        total_pago = metricas["pago_mes_total"]
        total_venc = metricas["vencido_total"]
        n_apr      = metricas["aprovado_count"]
        n_pago     = metricas["pago_mes_count"]
        n_venc     = metricas["vencido_count"]
    else:
        n_pre      = len(st.session_state.mock_pre)
        total_pre  = sum(f["valor"] for f in st.session_state.mock_pre)
        total_apr  = sum(f["valor"] for f in st.session_state.mock_a_vencer)
        total_pago = 121400
        total_venc = sum(f["valor"] for f in st.session_state.mock_vencidas)
        n_apr      = len(st.session_state.mock_a_vencer)
        n_pago     = 23
        n_venc     = len(st.session_state.mock_vencidas)
        recentes   = _MOCK_A_VENCER[:5]
        despesa    = [{"projeto": k, "valor": v} for k, v in {
            "MENTORES": 52400, "ANIET": 38900, "APCMC": 27600,
            "APIMA": 19200, "PRODUTECH": 61200, "CALÇADO": 14600,
        }.items()]

    if n_pre > 0:
        st.warning(f"⚠️ **{n_pre} fatura(s) aguardam aprovação manual.** Ver em **Alertas/A Pagar**.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🔍 Pré-aprovação",    fmt_eur(total_pre),  f"{n_pre} faturas")
    c2.metric("✅ Aprovado a pagar", fmt_eur(total_apr),  f"{n_apr} faturas")
    c3.metric("💳 Pago este mês",    fmt_eur(total_pago), f"{n_pago} faturas")
    c4.metric("🚨 Vencido",          fmt_eur(total_venc), f"{n_venc} faturas")

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 2])

    with col_left:
        secao_header("Faturas recentes")
        for row in recentes:
            formador = _row_formador(row)
            projeto  = _row_projeto(row)
            estado   = row.get("estado") or "submetida"
            n_fat    = row.get("numero_fatura") or "—"
            valor    = row.get("valor") or 0
            with st.container(border=True):
                cc1, cc2, cc3 = st.columns([4, 2, 2])
                cc1.markdown(
                    f"**{n_fat}**<br>"
                    f"<span style='font-size:12px;color:#6B7280'>`{projeto}`&nbsp;·&nbsp;{formador}</span>",
                    unsafe_allow_html=True,
                )
                cc2.markdown(f"<div style='margin-top:4px'><strong>{fmt_eur(valor)}</strong></div>", unsafe_allow_html=True)
                cc3.markdown(f"<div style='margin-top:4px'>{badge_html(estado)}</div>", unsafe_allow_html=True)

    with col_right:
        secao_header("Distribuição por estado")
        fig_donut = go.Figure(go.Pie(
            labels=["Pré-aprovação", "Aprovado", "Pago", "Vencido"],
            values=[n_pre or 1, n_apr or 1, n_pago or 1, n_venc or 1],
            hole=0.65,
            marker_colors=["#EF9F27", "#97C459", "#378ADD", "#E24B4A"],
            textinfo="label+percent",
            showlegend=False,
        ))
        fig_donut.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
        st.plotly_chart(fig_donut, use_container_width=True, config=PLOTLY_CONFIG)

    st.markdown("<br>", unsafe_allow_html=True)
    secao_header("Despesa por projeto")

    despesa_sorted = sorted(despesa, key=lambda x: x["valor"])
    max_val = max((d["valor"] for d in despesa_sorted), default=1)
    fig_bar = go.Figure(go.Bar(
        x=[d["valor"] for d in despesa_sorted],
        y=[d["projeto"] for d in despesa_sorted],
        orientation="h",
        marker_color=[CORES_PROJETO.get(d["projeto"], "#888") for d in despesa_sorted],
        text=[fmt_eur(d["valor"]) for d in despesa_sorted],
        textposition="outside",
    ))
    fig_bar.update_layout(
        margin=dict(t=10, b=10, l=10, r=120),
        height=300,
        xaxis=dict(showticklabels=False, showgrid=False, range=[0, max_val * 1.3]),
        yaxis=dict(showgrid=False),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_bar, use_container_width=True, config=PLOTLY_CONFIG)


# ---------------------------------------------------------------------------
# TAB 2 — ALERTAS / A PAGAR
# ---------------------------------------------------------------------------

def render_alertas(user: dict):
    user_nome = user.get("nome") or "Financeiro"

    # Filtros no topo
    col_f, col_o, col_d1, col_d2 = st.columns([2, 2, 1, 1])
    with col_f:
        projetos_bd = get_projetos() if SUPABASE_OK else _MOCK_PROJETOS
        nomes = ["Todos"] + [p["nome"] for p in projetos_bd]
        filtro = st.selectbox("Projeto", nomes, key="filtro_proj")
    with col_o:
        ordem = st.selectbox("Ordenar por", ORDEM_OPCOES, key="ordem_fat")
    with col_d1:
        data_ini = st.date_input("De", value=None, key="data_ini")
    with col_d2:
        data_fim_f = st.date_input("Até", value=None, key="data_fim")

    def filtrar_datas(dados: list[dict]) -> list[dict]:
        if not data_ini and not data_fim_f:
            return dados
        resultado = []
        for d in dados:
            prazo_str = d.get("prazo_pagamento")
            if not prazo_str:
                resultado.append(d)
                continue
            try:
                prazo = date.fromisoformat(prazo_str)
                if data_ini and prazo < data_ini:
                    continue
                if data_fim_f and prazo > data_fim_f:
                    continue
            except Exception:
                pass
            resultado.append(d)
        return resultado

    # Carregar dados
    if SUPABASE_OK:
        pre_dados = get_faturas_pre_aprovacao(filtro)
        venc_dados = filtrar_datas(filtrar_por_projeto(get_faturas_vencidas(), filtro))
        aven_dados = filtrar_datas(filtrar_por_projeto(get_faturas_a_vencer(), filtro))
        top5       = get_top_formadores_pendentes()
        pendente_proj = get_pendente_por_projeto()
        cf_labels, cf_saidas = get_cashflow_previsto()
        historico_bd = get_historico_financeiro()
    else:
        pre_dados    = filtrar_por_projeto(st.session_state.mock_pre, filtro)
        venc_dados   = filtrar_datas(filtrar_por_projeto(st.session_state.mock_vencidas, filtro))
        aven_dados   = filtrar_datas(filtrar_por_projeto(st.session_state.mock_a_vencer, filtro))
        top5         = [{"formador": "João Silva", "valor": 5000}, {"formador": "Rui Mendes", "valor": 4900}, {"formador": "Pedro Costa", "valor": 3300}, {"formador": "Ana Ferreira", "valor": 2800}, {"formador": "Carla Neves", "valor": 2100}]
        pendente_proj = [{"projeto": "MENTORES", "valor": 5000}, {"projeto": "PRODUTECH", "valor": 4400}, {"projeto": "CALÇADO", "valor": 3300}, {"projeto": "ANIET", "valor": 2800}, {"projeto": "APIMA", "valor": 2300}, {"projeto": "APCMC", "valor": 2100}]
        cf_labels, cf_saidas = _MOCK_CASHFLOW_LABELS, _MOCK_CASHFLOW_SAIDAS
        historico_bd = []

    venc_dados = ordenar_lista(venc_dados, ordem)
    aven_dados = ordenar_lista(aven_dados, ordem)

    total_vencido  = sum(f.get("valor") or 0 for f in venc_dados)
    total_a_vencer = sum(f.get("valor") or 0 for f in aven_dados)

    # Métricas
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🚨 Vencido",        fmt_eur(total_vencido),          f"{len(venc_dados)} faturas")
    c2.metric("⏳ A vencer 30d",   fmt_eur(total_a_vencer),         f"{len(aven_dados)} faturas")
    c3.metric("💳 Pago este mês",  fmt_eur(121400),                 "23 faturas")
    c4.metric("💰 Total pendente", fmt_eur(total_vencido + total_a_vencer), f"= {fmt_eur(total_vencido)} + {fmt_eur(total_a_vencer)}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ---- PRÉ-APROVAÇÃO ----
    secao_header(f"🔍 Aprovação manual ({len(pre_dados)} pendentes)", "Faturas submetidas por formadores cuja validação automática falhou.")

    if not pre_dados:
        st.success("Nenhuma fatura pendente de aprovação manual.")
    else:
        for i, row in enumerate(pre_dados):
            fatura_id = row.get("id") or str(i)
            n_fatura  = row.get("numero_fatura") or "—"
            formador  = _row_formador(row)
            email_fm  = _row_email(row)
            projeto   = _row_projeto(row)
            valor     = row.get("valor") or 0
            erro      = row.get("erro_leitura") or row.get("notas") or "—"
            data_sub  = row.get("created_at") or "—"
            ficheiro  = row.get("ficheiro_url")

            with st.container(border=True):
                col_info, col_pdf, col_acao = st.columns([4, 1, 3])
                with col_info:
                    st.markdown(
                        f"**Nº Fatura:** {n_fatura}&nbsp;&nbsp;**Formador:** {formador}<br>"
                        f"**Projeto:** `{projeto}`&nbsp;&nbsp;**Valor:** {fmt_eur(valor)}<br>"
                        f"<span style='color:#DC2626;font-size:12px'>⚠️ {erro}</span>&nbsp;&nbsp;"
                        f"<span style='color:#9CA3AF;font-size:12px'>Submetida: {str(data_sub)[:10]}</span>",
                        unsafe_allow_html=True,
                    )
                with col_pdf:
                    if ficheiro:
                        st.link_button("📄 Ver PDF", ficheiro)
                    else:
                        st.caption("Sem PDF")
                with col_acao:
                    if st.button("✅ Aprovar", key=f"apr_{i}_{fatura_id}", use_container_width=True):
                        if SUPABASE_OK:
                            if aprovar_fatura(fatura_id, user_nome):
                                registar_historico("Aprovado", n_fatura, formador, projeto, valor)
                                st.toast(f"Fatura {n_fatura} aprovada.")
                                st.rerun()
                        else:
                            st.session_state.mock_pre = [f for f in st.session_state.mock_pre if f.get("id") != fatura_id]
                            registar_historico("Aprovado", n_fatura, formador, projeto, valor)
                            st.toast(f"Fatura {n_fatura} aprovada.")
                            st.rerun()

                    motivo = st.text_input("Motivo", key=f"motivo_{i}_{fatura_id}", placeholder="Motivo de rejeição...", label_visibility="collapsed")
                    if st.button("❌ Rejeitar", key=f"rej_{i}_{fatura_id}", use_container_width=True):
                        if motivo:
                            if SUPABASE_OK:
                                if rejeitar_fatura(fatura_id, motivo, user_nome):
                                    registar_historico("Rejeitado", n_fatura, formador, projeto, valor, motivo)
                                    notificar_rejeicao(email_fm, n_fatura, motivo)
                                    st.toast(f"Fatura {n_fatura} rejeitada.")
                                    st.rerun()
                            else:
                                st.session_state.mock_pre = [f for f in st.session_state.mock_pre if f.get("id") != fatura_id]
                                registar_historico("Rejeitado", n_fatura, formador, projeto, valor, motivo)
                                notificar_rejeicao(email_fm, n_fatura, motivo)
                                st.rerun()
                        else:
                            st.warning("Escreve um motivo antes de rejeitar.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ---- UPLOAD PDF (leitura manual) ----
    with st.expander("📤 Ler fatura PDF manualmente"):
        uploaded = st.file_uploader("Carrega o PDF da fatura", type=["pdf"], key="pdf_upload")
        if uploaded:
            dados = extrair_dados_pdf(uploaded.read())
            if dados.get("erro"):
                st.error(f"Erro na leitura: {dados['erro']}")
            else:
                st.success("Campos extraídos do PDF:")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Nº Fatura", dados.get("numero_fatura") or "—")
                c2.metric("NIF Emitente", dados.get("nif_emitente") or "—")
                c3.metric("Valor", fmt_eur(dados.get("valor") or 0))
                c4.metric("Data", dados.get("data_fatura") or "—")
                with st.expander("Texto completo extraído"):
                    st.text(dados.get("texto_completo", ""))

    st.markdown("<br>", unsafe_allow_html=True)

    # ---- VENCIDAS ----
    secao_header("🔴 Faturas vencidas")

    # Paginação
    pag_v = st.session_state.get("pag_vencidas", 0)
    PAGE_SIZE = 10
    total_pag_v = max(1, (len(venc_dados) + PAGE_SIZE - 1) // PAGE_SIZE)
    pagina_v = venc_dados[pag_v * PAGE_SIZE:(pag_v + 1) * PAGE_SIZE]

    if not venc_dados:
        st.info("Nenhuma fatura vencida para este filtro.")
    else:
        for i, row in enumerate(pagina_v):
            card_vencida(row, pag_v * PAGE_SIZE + i, user_nome)
        st.markdown(f"**Total vencido: {fmt_eur(total_vencido)}**")
        if total_pag_v > 1:
            col_prev, col_info_p, col_next = st.columns([1, 2, 1])
            if col_prev.button("← Anterior", key="prev_v", disabled=pag_v == 0):
                st.session_state.pag_vencidas = pag_v - 1
                st.rerun()
            col_info_p.markdown(f"<div style='text-align:center;padding-top:8px'>Página {pag_v+1} / {total_pag_v}</div>", unsafe_allow_html=True)
            if col_next.button("Próxima →", key="next_v", disabled=pag_v >= total_pag_v - 1):
                st.session_state.pag_vencidas = pag_v + 1
                st.rerun()

        # Export Excel vencidas
        excel_bytes = gerar_excel_projeto(filtro or "Vencidas", venc_dados)
        st.download_button("⬇️ Exportar vencidas Excel", excel_bytes, f"vencidas_{filtro or 'todas'}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.markdown("<br>", unsafe_allow_html=True)

    # ---- A VENCER ----
    secao_header("🟡 A vencer — próximos 30 dias")

    pag_a = st.session_state.get("pag_avencer", 0)
    total_pag_a = max(1, (len(aven_dados) + PAGE_SIZE - 1) // PAGE_SIZE)
    pagina_a = aven_dados[pag_a * PAGE_SIZE:(pag_a + 1) * PAGE_SIZE]

    if not aven_dados:
        st.info("Nenhuma fatura a vencer para este filtro.")
    else:
        for i, row in enumerate(pagina_a):
            card_a_vencer(row, pag_a * PAGE_SIZE + i, user_nome)
        st.markdown(f"**Total a vencer: {fmt_eur(total_a_vencer)}**")
        if total_pag_a > 1:
            col_prev, col_info_p, col_next = st.columns([1, 2, 1])
            if col_prev.button("← Anterior", key="prev_a", disabled=pag_a == 0):
                st.session_state.pag_avencer = pag_a - 1
                st.rerun()
            col_info_p.markdown(f"<div style='text-align:center;padding-top:8px'>Página {pag_a+1} / {total_pag_a}</div>", unsafe_allow_html=True)
            if col_next.button("Próxima →", key="next_a", disabled=pag_a >= total_pag_a - 1):
                st.session_state.pag_avencer = pag_a + 1
                st.rerun()

        excel_bytes = gerar_excel_projeto(filtro or "A_vencer", aven_dados)
        st.download_button("⬇️ Exportar a vencer Excel", excel_bytes, f"a_vencer_{filtro or 'todas'}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.markdown("<br>", unsafe_allow_html=True)

    # ---- TOP 5 + POR PROJETO ----
    col_l, col_r = st.columns(2)
    with col_l:
        secao_header("Top 5 formadores pendentes")
        for i, row in enumerate(top5):
            with st.container(border=True):
                cc1, cc2 = st.columns([3, 1])
                cc1.markdown(f"**#{i+1}** {row['formador']}")
                cc2.markdown(f"**{fmt_eur(row['valor'])}**")

    with col_r:
        secao_header("Pendente por projeto")
        for row in pendente_proj:
            cor = CORES_PROJETO.get(row["projeto"], "#888")
            with st.container(border=True):
                cc1, cc2 = st.columns([3, 1])
                cc1.markdown(f"<span style='color:{cor};font-size:16px'>●</span> {row['projeto']}", unsafe_allow_html=True)
                cc2.markdown(f"**{fmt_eur(row['valor'])}**")

    st.markdown("<br>", unsafe_allow_html=True)

    # ---- CASHFLOW ----
    secao_header("Cashflow previsto — próximos 90 dias")
    if cf_saidas:
        acumulado, total = [], 0
        for v in cf_saidas:
            total += v
            acumulado.append(total)

        fig_cf = go.Figure()
        fig_cf.add_trace(go.Bar(x=cf_labels, y=cf_saidas, name="Saída semanal", marker_color="#F09595", yaxis="y1"))
        fig_cf.add_trace(go.Scatter(x=cf_labels, y=acumulado, name="Acumulado", line=dict(color="#378ADD", width=2), mode="lines+markers", yaxis="y2"))
        fig_cf.update_layout(
            height=350,
            margin=dict(t=30, b=80, l=60, r=60),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            yaxis=dict(title="Saída semanal (€)", showgrid=False),
            yaxis2=dict(title="Acumulado (€)", overlaying="y", side="right", showgrid=False),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickangle=45, automargin=True),
        )
        st.plotly_chart(fig_cf, use_container_width=True, config=PLOTLY_CONFIG)

    st.markdown("<br>", unsafe_allow_html=True)

    # ---- HISTÓRICO ----
    secao_header("📋 Histórico de ações")

    # Combina histórico da sessão + BD
    hist_sessao = st.session_state.historico[::-1]
    if hist_sessao:
        df_hist = pd.DataFrame(hist_sessao)
        df_hist.columns = ["Data/Hora", "Ação", "Nº Fatura", "Formador", "Projeto", "Valor", "Motivo"]
        df_hist["Valor"] = df_hist["Valor"].apply(fmt_eur)
        st.dataframe(df_hist, use_container_width=True, hide_index=True)
        csv = df_hist.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Exportar histórico CSV", csv, "historico_financeiro.csv", "text/csv")
    elif historico_bd:
        df_bd = pd.DataFrame([{
            "Data/Hora": str(h.get("criado_em", ""))[:16],
            "Ação":      h.get("tipo", ""),
            "Detalhe":   h.get("descricao", ""),
        } for h in historico_bd])
        st.dataframe(df_bd, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma ação registada nesta sessão.")


# ---------------------------------------------------------------------------
# RENDER PRINCIPAL
# ---------------------------------------------------------------------------

def render(user: dict):
    init_state()

    if not SUPABASE_OK:
        st.info("🔌 Supabase não ligado — a usar dados de demonstração.", icon="ℹ️")

    st.header(f"Bem-vindo, {user['nome']}")
    st.caption("Perfil: Financeiro")

    if SUPABASE_OK:
        try:
            n_pre = len(get_faturas_pre_aprovacao())
        except Exception:
            n_pre = 0
    else:
        n_pre = len(st.session_state.mock_pre)
    label_alertas = f"⚠️ Alertas/A Pagar ({n_pre})" if n_pre > 0 else "⚠️ Alertas/A Pagar"

    tab1, tab2, tab3 = st.tabs(["💶 Dashboard Financeiro", label_alertas, "💳 Faturação Empresas"])

    with tab1:
        render_dashboard(user)

    with tab2:
        render_alertas(user)

    with tab3:
        st.info("🚧 Em construção — histórico de pagamentos.")
