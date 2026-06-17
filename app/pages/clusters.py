"""Tab Projetos Clusters."""
import streamlit as st

PROJETOS = ["APCMC", "ANIET", "Mentores"]

VOLUMES = {
    "APCMC": {"atribuido": 1200, "realizado": 780},
}

ACOES_EXEMPLO = [
    {"Acao": "Acao 1", "Estado": "Fechada",  "Execucao (%)": 100},
    {"Acao": "Acao 2", "Estado": "Em curso", "Execucao (%)": 65},
    {"Acao": "Acao 3", "Estado": "Em curso", "Execucao (%)": 30},
    {"Acao": "Acao 4", "Estado": "Fechada",  "Execucao (%)": 100},
]

# --- Dados de exemplo dos formadores (trocar pela BD depois) ---
FORMADORES = [
    {"nome": "Ana Silva",   "consultor": "Consultor 1"},
    {"nome": "Bruno Costa", "consultor": "Consultor 1"},
    {"nome": "Carla Dias",  "consultor": "Consultor 2"},
]

ACOES_FORMADOR = {
    "Ana Silva": [
        {"acao": "Ação 1 - Cibersegurança", "fechada_magna": True,  "faturou": True,  "fatura": "fatura_ana_001.pdf", "paga": True},
        {"acao": "Ação 2 - Cloud",          "fechada_magna": True,  "faturou": True,  "fatura": "fatura_ana_002.pdf", "paga": False},
        {"acao": "Ação 3 - IA aplicada",    "fechada_magna": False, "faturou": False, "fatura": None,                 "paga": False},
    ],
    "Bruno Costa": [
        {"acao": "Ação 1 - Dados", "fechada_magna": True, "faturou": False, "fatura": None, "paga": False},
    ],
}


def render():
    _render_execucao()
    _render_formadores()
    st.info("Empresas")
    st.info("Faturação")


def _render_execucao():
    with st.expander("Execução", expanded=True):
        projeto = st.selectbox(
            "Seleciona o projeto",
            PROJETOS,
            key="exec_projeto_clusters",
        )
        st.markdown(f"**Execução — {projeto}**")

        if projeto in VOLUMES:
            vol = VOLUMES[projeto]
            atribuido = vol["atribuido"]
            realizado = vol["realizado"]
            pct = (realizado / atribuido * 100) if atribuido else 0

            v1, v2, v3 = st.columns(3)
            v1.metric("Volume atribuído", f"{atribuido}")
            v2.metric("Volume realizado", f"{realizado}")
            v3.metric("Execução", f"{pct:.0f}%")
            st.progress(min(pct / 100, 1.0))
            st.divider()

        fechadas = [a for a in ACOES_EXEMPLO if a["Estado"] == "Fechada"]
        em_curso = [a for a in ACOES_EXEMPLO if a["Estado"] == "Em curso"]
        media = sum(a["Execucao (%)"] for a in ACOES_EXEMPLO) / len(ACOES_EXEMPLO)

        c1, c2, c3 = st.columns(3)
        c1.metric("Ações fechadas", len(fechadas))
        c2.metric("Ações em curso", len(em_curso))
        c3.metric("Execução média", f"{media:.0f}%")

        st.markdown("##### ✅ Ações fechadas")
        if fechadas:
            st.dataframe(fechadas, hide_index=True, use_container_width=True)
        else:
            st.caption("Sem ações fechadas.")

        st.markdown("##### 🔄 Ações em curso")
        if em_curso:
            for a in em_curso:
                st.write(f"**{a['Acao']}** — {a['Execucao (%)']}%")
                st.progress(a["Execucao (%)"] / 100)
        else:
            st.caption("Sem ações em curso.")


def _render_formadores():
    with st.expander("Formadores", expanded=False):
        termo = st.text_input("Pesquisar formador", key="form_pesquisa_clusters")
        if st.button("🔍 Pesquisar", key="form_btn_clusters"):
            st.session_state["form_pesquisou_clusters"] = True

        if not st.session_state.get("form_pesquisou_clusters"):
            st.caption("Escreve o nome do formador e carrega em Pesquisar.")
            return

        encontrados = [f for f in FORMADORES if termo.lower() in f["nome"].lower()]
        if not encontrados:
            st.warning("Nenhum formador encontrado para essa pesquisa.")
            return

        nomes = [f["nome"] for f in encontrados]
        nome_sel = st.selectbox("Seleciona o formador", nomes, key="form_sel_clusters")
        formador = next(f for f in encontrados if f["nome"] == nome_sel)
        st.caption(f"Consultor associado: **{formador['consultor']}**")

        st.markdown("##### Ações da Magna")
        acoes = ACOES_FORMADOR.get(nome_sel, [])
        if not acoes:
            st.info("Este formador não tem ações registadas.")
            return

        for i, a in enumerate(acoes):
            with st.container(border=True):
                st.markdown(f"**{a['acao']}**")
                c1, c2, c3 = st.columns(3)
                c1.write("Fechada na Magna: " + ("✅ Sim" if a["fechada_magna"] else "⏳ Não"))
                c2.write("Faturou: " + ("✅ Sim" if a["faturou"] else "❌ Não"))
                c3.write("Paga pelo financeiro: " + ("✅ Sim" if a["paga"] else "❌ Não"))

                if a["faturou"] and a["fatura"]:
                    st.download_button(
                        "📄 Cópia da fatura",
                        data=b"Fatura de exemplo (placeholder visual).",
                        file_name=a["fatura"],
                        key=f"fatura_clusters_{nome_sel}_{i}",
                    )
                else:
                    st.caption("Sem fatura submetida pelo formador.")

    st.info("Formadores")
    st.info("Empresas")
    st.info("Faturação")
