"""Pagina do financeiro."""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date

# ---------------------------------------------------------------------------
# MOCK DATA — substituir por queries à BD quando disponível
# ---------------------------------------------------------------------------

PROJETOS = [
    {"code": "01195000", "nome": "MENTORES"},
    {"code": "01196000", "nome": "ANIET"},
    {"code": "01195400", "nome": "APCMC"},
    {"code": "01194800", "nome": "APIMA"},
    {"code": "02982000", "nome": "PRODUTECH"},
    {"code": "02981900", "nome": "CALÇADO"},
]

CORES_PROJETO = {
    "MENTORES":  "#378ADD",
    "ANIET":     "#97C459",
    "APCMC":     "#EF9F27",
    "APIMA":     "#D4537E",
    "PRODUTECH": "#534AB7",
    "CALÇADO":   "#1D9E75",
}

FATURAS_RECENTES = pd.DataFrame([
    {"descricao": "Formação Excel Avançado",       "projeto": "MENTORES",  "formador": "João Silva",      "n_fatura": "FT2026/0142", "valor": 3200,  "estado": "Pendente"},
    {"descricao": "Formação Gestão de Equipas",    "projeto": "ANIET",     "formador": "Ana Ferreira",    "n_fatura": "FT2026/0138", "valor": 2800,  "estado": "Aprovado"},
    {"descricao": "Formação Liderança",             "projeto": "PRODUTECH", "formador": "Rui Mendes",      "n_fatura": "FT2026/0131", "valor": 4100,  "estado": "Pago"},
    {"descricao": "Formação Comunicação",           "projeto": "APCMC",     "formador": "Carla Neves",     "n_fatura": "FT2026/0129", "valor": 2100,  "estado": "Aprovado"},
    {"descricao": "Formação Segurança no Trabalho", "projeto": "CALÇADO",   "formador": "Pedro Costa",     "n_fatura": "FT2026/0125", "valor": 1900,  "estado": "Pendente"},
])

FATURAS_PRE_APROVACAO = pd.DataFrame([
    {
        "n_fatura": "FT2026/0155",
        "formador": "Miguel Santos",
        "cod_interno": "FM-2026-0042",
        "projeto": "MENTORES",
        "valor": 2400,
        "motivo_falha": "Código interno não encontrado no sistema",
        "data_submissao": date(2026, 6, 15),
    },
    {
        "n_fatura": "FT2026/0153",
        "formador": "Sofia Rodrigues",
        "cod_interno": "FM-2026-0038",
        "projeto": "ANIET",
        "valor": 1950,
        "motivo_falha": "Nome do formador não corresponde ao projeto",
        "data_submissao": date(2026, 6, 14),
    },
    {
        "n_fatura": "FT2026/0150",
        "formador": "Luís Cardoso",
        "cod_interno": "FM-2026-0035",
        "projeto": "PRODUTECH",
        "valor": 1800,
        "motivo_falha": "Valor diverge do contrato registado",
        "data_submissao": date(2026, 6, 13),
    },
])

DESPESA_PROJETO = pd.DataFrame([
    {"projeto": "MENTORES",  "valor": 52400},
    {"projeto": "ANIET",     "valor": 38900},
    {"projeto": "APCMC",     "valor": 27600},
    {"projeto": "APIMA",     "valor": 19200},
    {"projeto": "PRODUTECH", "valor": 61200},
    {"projeto": "CALÇADO",   "valor": 14600},
])

FATURAS_VENCIDAS = pd.DataFrame([
    {"n_fatura": "FT2026/0110", "descricao": "Formação Segurança",          "projeto": "MENTORES",  "formador": "João Silva",   "valor": 1800, "emissao": date(2026, 5, 2),  "vencimento": date(2026, 6, 2),  "atraso": 14},
    {"n_fatura": "FT2026/0108", "descricao": "Formação Lean Manufacturing", "projeto": "PRODUTECH", "formador": "Rui Mendes",   "valor": 2600, "emissao": date(2026, 5, 8),  "vencimento": date(2026, 6, 8),  "atraso": 8},
    {"n_fatura": "FT2026/0105", "descricao": "Formação Qualidade",          "projeto": "CALÇADO",   "formador": "Pedro Costa",  "valor": 1400, "emissao": date(2026, 5, 12), "vencimento": date(2026, 6, 12), "atraso": 4},
])

FATURAS_A_VENCER = pd.DataFrame([
    {"n_fatura": "FT2026/0142", "descricao": "Formação Excel Avançado",       "projeto": "MENTORES", "formador": "João Silva",   "valor": 3200, "emissao": date(2026, 6, 1),  "vencimento": date(2026, 6, 21), "dias": 5},
    {"n_fatura": "FT2026/0138", "descricao": "Formação Gestão de Equipas",    "projeto": "ANIET",    "formador": "Ana Ferreira", "valor": 2800, "emissao": date(2026, 6, 3),  "vencimento": date(2026, 6, 27), "dias": 11},
    {"n_fatura": "FT2026/0136", "descricao": "Formação Segurança no Trabalho","projeto": "CALÇADO",  "formador": "Pedro Costa",  "valor": 1900, "emissao": date(2026, 6, 5),  "vencimento": date(2026, 7, 4),  "dias": 18},
    {"n_fatura": "FT2026/0129", "descricao": "Formação Comunicação",          "projeto": "APCMC",    "formador": "Carla Neves",  "valor": 2100, "emissao": date(2026, 6, 6),  "vencimento": date(2026, 7, 10), "dias": 24},
    {"n_fatura": "FT2026/0127", "descricao": "Formação Liderança",            "projeto": "APIMA",    "formador": "Rui Mendes",   "valor": 2300, "emissao": date(2026, 6, 8),  "vencimento": date(2026, 7, 16), "dias": 30},
])

TOP5_FORMADORES = pd.DataFrame([
    {"formador": "João Silva",   "valor": 5000},
    {"formador": "Ana Ferreira", "valor": 2800},
    {"formador": "Rui Mendes",   "valor": 4900},
    {"formador": "Carla Neves",  "valor": 2100},
    {"formador": "Pedro Costa",  "valor": 3300},
]).sort_values("valor", ascending=False).reset_index(drop=True)

PENDENTE_PROJETO = pd.DataFrame([
    {"projeto": "MENTORES",  "valor": 5000},
    {"projeto": "PRODUTECH", "valor": 4400},
    {"projeto": "ANIET",     "valor": 2800},
    {"projeto": "CALÇADO",   "valor": 3300},
    {"projeto": "APCMC",     "valor": 2100},
    {"projeto": "APIMA",     "valor": 2300},
])

CASHFLOW_SEMANAS = [
    "S1 Jun", "S2 Jun", "S3 Jun", "S4 Jun",
    "S1 Jul", "S2 Jul", "S3 Jul", "S4 Jul",
    "S1 Ago", "S2 Ago", "S3 Ago", "S4 Ago", "S1 Set",
]
CASHFLOW_SAIDAS = [3200, 2100, 4100, 2800, 2600, 3800, 1900, 3200, 2400, 2800, 1800, 2100, 2300]

PLOTLY_CONFIG = {"displayModeBar": False}


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

ESTADO_BADGE = {
    "Pendente": ("#FEF3C7", "#92400E"),
    "Aprovado": ("#D1FAE5", "#065F46"),
    "Pago":     ("#DBEAFE", "#1E40AF"),
    "Vencido":  ("#FEE2E2", "#991B1B"),
}

def fmt_eur(valor: float) -> str:
    return f"€ {valor:,.0f}".replace(",", ".")

def badge_html(estado: str) -> str:
    bg, color = ESTADO_BADGE.get(estado, ("#F3F4F6", "#374151"))
    return (
        f"<span style='background:{bg};color:{color};padding:2px 10px;"
        f"border-radius:12px;font-size:12px;font-weight:500'>{estado}</span>"
    )

def card_fatura(row, tipo: str, idx: int):
    with st.container(border=True):
        col_info, col_valor, col_acao = st.columns([5, 2, 2])

        with col_info:
            st.markdown(
                f"**{row['descricao']}**&nbsp;&nbsp;"
                f"<span style='font-size:12px;color:#6B7280'>{row['n_fatura']}</span><br>"
                f"<span style='font-size:13px'>`{row['projeto']}`&nbsp;·&nbsp;{row['formador']}</span><br>"
                f"<span style='font-size:12px;color:#9CA3AF'>"
                f"Emissão {row['emissao'].strftime('%d/%m/%Y')}&nbsp;·&nbsp;"
                f"Vencimento {row['vencimento'].strftime('%d/%m/%Y')}</span>",
                unsafe_allow_html=True,
            )
        with col_valor:
            if tipo == "vencida":
                st.markdown(
                    f"<div style='margin-top:8px'><strong>{fmt_eur(row['valor'])}</strong><br>"
                    f"<span style='color:#DC2626;font-size:13px'>+{row['atraso']} dias em atraso</span></div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<div style='margin-top:8px'><strong>{fmt_eur(row['valor'])}</strong><br>"
                    f"<span style='color:#D97706;font-size:13px'>vence em {row['dias']} dias</span></div>",
                    unsafe_allow_html=True,
                )
        with col_acao:
            if st.button("✓ Marcar pago", key=f"pago_{tipo}_{idx}", use_container_width=True):
                st.toast(f"Fatura {row['n_fatura']} marcada como paga. (A ligar à BD)")


# ---------------------------------------------------------------------------
# TAB 1 — DASHBOARD FINANCEIRO
# ---------------------------------------------------------------------------

def render_dashboard():
    n_pre = len(FATURAS_PRE_APROVACAO)

    if n_pre > 0:
        st.warning(f"⚠️ **{n_pre} fatura(s) aguardam aprovação manual** — validação automática falhou. Ver em **Alertas/A Pagar**.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🔍 Pré-aprovação",    fmt_eur(int(FATURAS_PRE_APROVACAO["valor"].sum())), f"{n_pre} faturas")
    c2.metric("✅ Aprovado a pagar", fmt_eur(83150), "8 faturas")
    c3.metric("💳 Pago este mês",    fmt_eur(121400), "23 faturas")
    c4.metric("🚨 Vencido",          fmt_eur(int(FATURAS_VENCIDAS["valor"].sum())), f"{len(FATURAS_VENCIDAS)} faturas")

    st.markdown("---")

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("Faturas recentes")
        for _, row in FATURAS_RECENTES.iterrows():
            with st.container(border=True):
                cc1, cc2, cc3 = st.columns([4, 2, 2])
                cc1.markdown(
                    f"**{row['descricao']}**<br>"
                    f"<span style='font-size:12px;color:#6B7280'>`{row['projeto']}`&nbsp;·&nbsp;{row['formador']}&nbsp;·&nbsp;{row['n_fatura']}</span>",
                    unsafe_allow_html=True,
                )
                cc2.markdown(f"<div style='margin-top:4px'><strong>{fmt_eur(row['valor'])}</strong></div>", unsafe_allow_html=True)
                cc3.markdown(f"<div style='margin-top:4px'>{badge_html(row['estado'])}</div>", unsafe_allow_html=True)

    with col_right:
        st.subheader("Distribuição por estado")
        fig_donut = go.Figure(go.Pie(
            labels=["Pré-aprovação", "Aprovado", "Pago", "Vencido"],
            values=[35, 31, 24, 10],
            hole=0.65,
            marker_colors=["#EF9F27", "#97C459", "#378ADD", "#E24B4A"],
            textinfo="label+percent",
            showlegend=False,
        ))
        fig_donut.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
        st.plotly_chart(fig_donut, use_container_width=True, config=PLOTLY_CONFIG)

    st.markdown("---")

    st.subheader("Despesa por projeto")
    df_sorted = DESPESA_PROJETO.sort_values("valor", ascending=True)
    max_val = df_sorted["valor"].max()

    fig_bar = go.Figure(go.Bar(
        x=df_sorted["valor"],
        y=df_sorted["projeto"],
        orientation="h",
        marker_color=[CORES_PROJETO.get(p, "#888") for p in df_sorted["projeto"]],
        text=[fmt_eur(v) for v in df_sorted["valor"]],
        textposition="outside",
    ))
    fig_bar.update_layout(
        margin=dict(t=10, b=10, l=10, r=120),
        height=300,
        xaxis=dict(showticklabels=False, showgrid=False, range=[0, max_val * 1.25]),
        yaxis=dict(showgrid=False),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_bar, use_container_width=True, config=PLOTLY_CONFIG)


# ---------------------------------------------------------------------------
# TAB 2 — ALERTAS / A PAGAR
# ---------------------------------------------------------------------------

def render_alertas():
    total_vencido  = int(FATURAS_VENCIDAS["valor"].sum())
    total_a_vencer = int(FATURAS_A_VENCER["valor"].sum())
    total_pendente = total_vencido + total_a_vencer
    n_pre          = len(FATURAS_PRE_APROVACAO)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🚨 Vencido",        fmt_eur(total_vencido),  f"{len(FATURAS_VENCIDAS)} faturas")
    c2.metric("⏳ A vencer 30d",   fmt_eur(total_a_vencer), f"{len(FATURAS_A_VENCER)} faturas")
    c3.metric("💳 Pago",           fmt_eur(121400),         "23 faturas")
    c4.metric("💰 Total pendente", fmt_eur(total_pendente), f"= {fmt_eur(total_vencido)} + {fmt_eur(total_a_vencer)}")

    st.markdown("---")

    # Aprovação manual
    st.subheader(f"🔍 Aprovação manual ({n_pre} pendentes)")
    st.caption("Faturas submetidas por formadores cuja validação automática falhou.")

    if FATURAS_PRE_APROVACAO.empty:
        st.success("Nenhuma fatura pendente de aprovação manual.")
    else:
        for i, row in FATURAS_PRE_APROVACAO.iterrows():
            with st.container(border=True):
                col_info, col_acao = st.columns([5, 3])
                with col_info:
                    st.markdown(
                        f"**Nº Fatura:** {row['n_fatura']}&nbsp;&nbsp;"
                        f"**Formador:** {row['formador']}<br>"
                        f"**Cód. Interno:** `{row['cod_interno']}`&nbsp;&nbsp;"
                        f"**Projeto:** `{row['projeto']}`&nbsp;&nbsp;"
                        f"**Valor:** {fmt_eur(row['valor'])}<br>"
                        f"<span style='color:#DC2626;font-size:12px'>⚠️ {row['motivo_falha']}</span>&nbsp;&nbsp;"
                        f"<span style='color:#9CA3AF;font-size:12px'>Submetida a {row['data_submissao'].strftime('%d/%m/%Y')}</span>",
                        unsafe_allow_html=True,
                    )
                with col_acao:
                    if st.button("✅ Aprovar", key=f"apr_{i}", use_container_width=True):
                        st.toast(f"Fatura {row['n_fatura']} aprovada. (A ligar à BD)")
                    motivo = st.text_input(
                        "Motivo",
                        key=f"motivo_{i}",
                        placeholder="Motivo de rejeição...",
                        label_visibility="collapsed",
                    )
                    if st.button("❌ Rejeitar", key=f"rej_{i}", use_container_width=True):
                        if motivo:
                            st.toast(f"Fatura {row['n_fatura']} rejeitada. Notificação enviada ao formador. (A ligar à BD)")
                        else:
                            st.warning("Escreve um motivo antes de rejeitar.")

    st.markdown("---")

    nomes_projeto = ["Todos"] + [p["nome"] for p in PROJETOS]
    filtro = st.selectbox("Filtrar por projeto", nomes_projeto, index=0)

    def aplicar_filtro(df):
        if filtro == "Todos":
            return df
        return df[df["projeto"] == filtro].reset_index(drop=True)

    fv = aplicar_filtro(FATURAS_VENCIDAS)
    fa = aplicar_filtro(FATURAS_A_VENCER)

    st.subheader("🔴 Faturas vencidas")
    if fv.empty:
        st.info("Nenhuma fatura vencida para este projeto.")
    else:
        for i, row in fv.iterrows():
            card_fatura(row, "vencida", i)
        st.markdown(f"**Total vencido: {fmt_eur(int(fv['valor'].sum()))}**")

    st.markdown("---")

    st.subheader("🟡 A vencer — próximos 30 dias")
    if fa.empty:
        st.info("Nenhuma fatura a vencer para este projeto.")
    else:
        for i, row in fa.iterrows():
            card_fatura(row, "avencer", i)
        st.markdown(f"**Total a vencer: {fmt_eur(int(fa['valor'].sum()))}**")

    st.markdown("---")

    col_l, col_r = st.columns(2)

    with col_l:
        st.subheader("Top 5 formadores pendentes")
        for i, row in TOP5_FORMADORES.iterrows():
            with st.container(border=True):
                cc1, cc2 = st.columns([3, 1])
                cc1.markdown(f"**#{i+1}** {row['formador']}")
                cc2.markdown(f"**{fmt_eur(row['valor'])}**")

    with col_r:
        st.subheader("Pendente por projeto")
        for _, row in PENDENTE_PROJETO.iterrows():
            cor = CORES_PROJETO.get(row["projeto"], "#888")
            with st.container(border=True):
                cc1, cc2 = st.columns([3, 1])
                cc1.markdown(
                    f"<span style='color:{cor};font-size:16px'>●</span> {row['projeto']}",
                    unsafe_allow_html=True,
                )
                cc2.markdown(f"**{fmt_eur(row['valor'])}**")

    st.markdown("---")

    st.subheader("Cashflow previsto — próximos 90 dias")
    acumulado = []
    total = 0
    for v in CASHFLOW_SAIDAS:
        total += v
        acumulado.append(total)

    fig_cf = go.Figure()
    fig_cf.add_trace(go.Bar(
        x=CASHFLOW_SEMANAS,
        y=CASHFLOW_SAIDAS,
        name="Saída semanal",
        marker_color="#F09595",
        yaxis="y1",
    ))
    fig_cf.add_trace(go.Scatter(
        x=CASHFLOW_SEMANAS,
        y=acumulado,
        name="Acumulado",
        line=dict(color="#378ADD", width=2),
        mode="lines+markers",
        yaxis="y2",
    ))
    fig_cf.update_layout(
        height=350,
        margin=dict(t=30, b=60, l=60, r=60),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        yaxis=dict(title="Saída semanal (€)", showgrid=False),
        yaxis2=dict(title="Acumulado (€)", overlaying="y", side="right", showgrid=False),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickangle=45, automargin=True),
    )
    st.plotly_chart(fig_cf, use_container_width=True, config=PLOTLY_CONFIG)


# ---------------------------------------------------------------------------
# RENDER PRINCIPAL
# ---------------------------------------------------------------------------

def render(user: dict):
    st.header(f"Bem-vindo, {user['nome']}")
    st.caption("Perfil: Financeiro")

    n_pre = len(FATURAS_PRE_APROVACAO)
    label_alertas = f"⚠️ Alertas/A Pagar ({n_pre})" if n_pre > 0 else "⚠️ Alertas/A Pagar"

    tab1, tab2, tab3 = st.tabs(["💶 Dashboard Financeiro", label_alertas, "💳 Faturação Empresas"])

    with tab1:
        render_dashboard()

    with tab2:
        render_alertas()

    with tab3:
        st.info("🚧 Em construção — histórico de pagamentos.")
