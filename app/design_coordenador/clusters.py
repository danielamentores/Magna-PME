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


def render():
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

    st.info("Formadores")
    st.info("Empresas")
    st.info("Faturação")
