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
    {"descricao": "Formação Excel Avançado", "projeto": "MENTORES",  "fornecedor": "TechTrain Lda", "valor": 3200,  "estado": "Pendente"},
    {"descricao": "Consultoria RH",          "projeto": "ANIET",     "fornecedor": "HRConsult",     "valor": 8500,  "estado": "Aprovado"},
    {"descricao": "Formação Liderança",      "projeto": "PRODUTECH", "fornecedor": "LeadAcademy",   "valor": 12000, "estado": "Pago"},
    {"descricao": "Material Didático",       "projeto": "APCMC",     "fornecedor": "EduSupply",     "valor": 2100,  "estado": "Aprovado"},
    {"descricao": "Formação Compliance",     "projeto": "CALÇADO",   "fornecedor": "LexForm",       "valor": 5800,  "estado": "Pendente"},
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
    {"descricao": "Formação Segurança",    "projeto": "MENTORES",  "fornecedor": "TechTrain Lda", "valor": 4800, "emissao": date(2026, 5, 2),  "vencimento": date(2026, 6, 2),  "atraso": 14},
    {"descricao": "Consultoria Processos", "projeto": "PRODUTECH", "fornecedor": "Optimia SA",    "valor": 6200, "emissao": date(2026, 5, 8),  "vencimento": date(2026, 6, 8),  "atraso": 8},
    {"descricao": "Material Formativo",    "projeto": "CALÇADO",   "fornecedor": "EduSupply",     "valor": 3600, "emissao": date(2026, 5, 12), "vencimento": date(2026, 6, 12), "atraso": 4},
])

FATURAS_A_VENCER = pd.DataFrame([
    {"descricao": "Formação Excel Avançado", "projeto": "MENTORES", "fornecedor": "TechTrain Lda", "valor": 3200, "emissao": date(2026, 6, 1),  "vencimento": date(2026, 6, 21), "dias": 5},
    {"descricao": "Consultoria RH",          "projeto": "ANIET",    "fornecedor": "HRConsult",     "valor": 8500, "emissao": date(2026, 6, 3),  "vencimento": date(2026, 6, 27), "dias": 11},
    {"descricao": "Formação Compliance",     "projeto": "CALÇADO",  "fornecedor": "LexForm",       "valor": 5800, "emissao": date(2026, 6, 5),  "vencimento": date(2026, 7, 4),  "dias": 18},
    {"descricao": "Material Didático",       "projeto": "APCMC",    "fornecedor": "EduSupply",     "valor": 2100, "emissao": date(2026, 6, 6),  "vencimento": date(2026, 7, 10), "dias": 24},
    {"descricao": "Formação Liderança",      "projeto": "APIMA",    "fornecedor": "LeadAcademy",   "valor": 4900, "emissao": date(2026, 6, 8),  "vencimento": date(2026, 7, 16), "dias": 30},
])

TOP5_FORNECEDORES = pd.DataFrame([
    {"fornecedor": "HRConsult",     "valor": 8500},
    {"fornecedor": "TechTrain Lda", "valor": 8000},
    {"fornecedor": "LexForm",       "valor": 5800},
    {"fornecedor": "EduSupply",     "valor": 5700},
    {"fornecedor": "Optimia SA",    "valor": 6200},
]).sort_values("valor", ascending=False).reset_index(drop=True)

PENDENTE_PROJETO = pd.DataFrame([
    {"projeto": "MENTORES",  "valor": 8000},
    {"projeto": "PRODUTECH", "valor": 6200},
    {"projeto": "ANIET",     "valor": 8500},
    {"projeto": "CALÇADO",   "valor": 9400},
    {"projeto": "APCMC",     "valor": 2100},
    {"projeto": "APIMA",     "valor": 4900},
])

CASHFLOW_SEMANAS = [
    "S1 Jun", "S2 Jun", "S3 Jun", "S4 Jun",
    "S1 Jul", "S2 Jul", "S3 Jul", "S4 Jul",
    "S1 Ago", "S2 Ago", "S3 Ago", "S4 Ago", "S1 Set",
]
CASHFLOW_SAIDAS = [8200, 5400, 9800, 7800, 6200, 8400, 5800, 8000, 4200, 7600, 3800, 4000, 5200]


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

ESTADO_COR = {
    "Pendente": "🟡",
    "Aprovado": "🟢",
    "Pago":     "🔵",
    "Vencido":  "🔴",
}

def fmt_eur(valor: float) -> str:
    return f"€ {valor:,.0f}".replace(",", ".")


# ---------------------------------------------------------------------------
# TAB 1 — DASHBOARD FINANCEIRO
# ---------------------------------------------------------------------------

def render_dashboard():
    # Métricas de topo
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("⏳ Pendente aprovação", fmt_eur(47320), "12 faturas")
    c2.metric("✅ Aprovado a pagar",   fmt_eur(83150), "8 faturas")
    c3.metric("💳 Pago este mês",      fmt_eur(121400), "23 faturas")
    c4.metric("🚨 Vencido",            fmt_eur(14600),  "3 faturas")

    st.divider()

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("Faturas recentes")
        for _, row in FATURAS_RECENTES.iterrows():
            icon = ESTADO_COR.get(row["estado"], "⚪")
            with st.container(border=True):
                cc1, cc2, cc3 = st.columns([4, 2, 1])
                cc1.markdown(f"**{row['descricao']}**  \n`{row['projeto']}`")
                cc2.markdown(f"**{fmt_eur(row['valor'])}**")
                cc3.markdown(f"{icon} {row['estado']}")

    with col_right:
        st.subheader("Distribuição por estado")
        fig_donut = go.Figure(go.Pie(
            labels=["Pendente", "Aprovado", "Pago", "Vencido"],
            values=[35, 31, 24, 10],
            hole=0.65,
            marker_colors=["#EF9F27", "#97C459", "#378ADD", "#E24B4A"],
            textinfo="label+percent",
            showlegend=False,
        ))
        fig_donut.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=260)
        st.plotly_chart(fig_donut, use_container_width=True)

    st.divider()

    st.subheader("Despesa por projeto")
    df_sorted = DESPESA_PROJETO.sort_values("valor", ascending=True)
    fig_bar = go.Figure(go.Bar(
        x=df_sorted["valor"],
        y=df_sorted["projeto"],
        orientation="h",
        marker_color=[CORES_PROJETO.get(p, "#888") for p in df_sorted["projeto"]],
        text=[fmt_eur(v) for v in df_sorted["valor"]],
        textposition="outside",
    ))
    fig_bar.update_layout(
        margin=dict(t=0, b=0, l=0, r=80),
        height=280,
        xaxis=dict(showticklabels=False, showgrid=False),
        yaxis=dict(showgrid=False),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_bar, use_container_width=True)


# ---------------------------------------------------------------------------
# TAB 2 — ALERTAS / A PAGAR
# ---------------------------------------------------------------------------

def render_alertas():
    # Métricas de topo
    total_vencido  = int(FATURAS_VENCIDAS["valor"].sum())
    total_a_vencer = int(FATURAS_A_VENCER["valor"].sum())
    total_pendente = total_vencido + total_a_vencer

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🚨 Vencido",         fmt_eur(total_vencido),  f"{len(FATURAS_VENCIDAS)} faturas")
    c2.metric("⏳ A vencer 30d",    fmt_eur(total_a_vencer), f"{len(FATURAS_A_VENCER)} faturas")
    c3.metric("💳 Pago",            fmt_eur(121400),         "23 faturas")
    c4.metric("💰 Total pendente",  fmt_eur(total_pendente), f"= {fmt_eur(total_vencido)} + {fmt_eur(total_a_vencer)}")

    st.divider()

    # Filtro por projeto
    nomes_projeto = ["Todos"] + [p["nome"] for p in PROJETOS]
    filtro = st.selectbox("Filtrar por projeto", nomes_projeto, index=0)

    def aplicar_filtro(df):
        if filtro == "Todos":
            return df
        return df[df["projeto"] == filtro].reset_index(drop=True)

    fv = aplicar_filtro(FATURAS_VENCIDAS)
    fa = aplicar_filtro(FATURAS_A_VENCER)

    # Faturas vencidas
    st.subheader("🔴 Faturas vencidas")
    if fv.empty:
        st.info("Nenhuma fatura vencida para este projeto.")
    else:
        for _, row in fv.iterrows():
            with st.container(border=True):
                c1, c2, c3 = st.columns([4, 2, 2])
                c1.markdown(
                    f"**{row['descricao']}**  \n"
                    f"`{row['projeto']}` · {row['fornecedor']}  \n"
                    f"<span style='font-size:12px;color:gray'>Emissão {row['emissao'].strftime('%d/%m/%Y')} · Vencimento {row['vencimento'].strftime('%d/%m/%Y')}</span>",
                    unsafe_allow_html=True,
                )
                c2.markdown(f"**{fmt_eur(row['valor'])}**  \n🔴 +{row['atraso']} dias")
                if c3.button("✓ Marcar pago", key=f"pago_v_{row['descricao']}"):
                    st.toast(f"'{row['descricao']}' marcada como paga. (A ligar à BD)")

        st.markdown(f"**Total vencido: {fmt_eur(int(fv['valor'].sum()))}**")

    st.divider()

    # Faturas a vencer
    st.subheader("🟡 A vencer — próximos 30 dias")
    if fa.empty:
        st.info("Nenhuma fatura a vencer para este projeto.")
    else:
        for _, row in fa.iterrows():
            with st.container(border=True):
                c1, c2, c3 = st.columns([4, 2, 2])
                c1.markdown(
                    f"**{row['descricao']}**  \n"
                    f"`{row['projeto']}` · {row['fornecedor']}  \n"
                    f"<span style='font-size:12px;color:gray'>Emissão {row['emissao'].strftime('%d/%m/%Y')} · Vencimento {row['vencimento'].strftime('%d/%m/%Y')}</span>",
                    unsafe_allow_html=True,
                )
                c2.markdown(f"**{fmt_eur(row['valor'])}**  \n🟡 {row['dias']} dias")
                if c3.button("✓ Marcar pago", key=f"pago_a_{row['descricao']}"):
                    st.toast(f"'{row['descricao']}' marcada como paga. (A ligar à BD)")

        st.markdown(f"**Total a vencer: {fmt_eur(int(fa['valor'].sum()))}**")

    st.divider()

    col_l, col_r = st.columns(2)

    with col_l:
        st.subheader("Top 5 fornecedores pendentes")
        for i, row in TOP5_FORNECEDORES.iterrows():
            st.markdown(f"**#{i+1}** {row['fornecedor']} — {fmt_eur(row['valor'])}")

    with col_r:
        st.subheader("Pendente por projeto")
        for _, row in PENDENTE_PROJETO.iterrows():
            st.markdown(f"● {row['projeto']} — {fmt_eur(row['valor'])}")

    st.divider()

    # Cashflow 90 dias
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
        height=300,
        margin=dict(t=10, b=0, l=0, r=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        yaxis=dict(title="Saída semanal (€)", showgrid=False),
        yaxis2=dict(title="Acumulado (€)", overlaying="y", side="right", showgrid=False),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickangle=45),
    )
    st.plotly_chart(fig_cf, use_container_width=True)


# ---------------------------------------------------------------------------
# RENDER PRINCIPAL
# ---------------------------------------------------------------------------

def render(user: dict):
    st.header(f"Bem-vindo, {user['nome']}")
    st.caption("Perfil: Financeiro")

    tab1, tab2, tab3 = st.tabs(["💶 Dashboard Financeiro", "⚠️ Alertas/A Pagar", "💳 Faturação Empresas"])

    with tab1:
        render_dashboard()

    with tab2:
        render_alertas()

    with tab3:
        st.info("🚧 Em construção — histórico de pagamentos.")
