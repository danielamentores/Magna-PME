"""Pagina do coordenador."""
import streamlit as st

# Dados de exemplo (so para a fase visual — trocar pela BD depois)
PROJETOS = ["Projeto A", "Projeto B", "Projeto C"]
ACOES_EXEMPLO = [
    {"Acao": "Acao 1", "Estado": "Fechada",  "Execucao (%)": 100},
    {"Acao": "Acao 2", "Estado": "Em curso", "Execucao (%)": 65},
    {"Acao": "Acao 3", "Estado": "Em curso", "Execucao (%)": 30},
    {"Acao": "Acao 4", "Estado": "Fechada",  "Execucao (%)": 100},
]


def render(user: dict):
    st.header(f"Bem-vindo, {user['nome']}")
    st.caption("Perfil: Coordenador")

    tab1, tab2, tab3 = st.tabs([
        "📊 Projetos Clusters",
        "Projeto Formação Ação",
        "Projeto Comércio e Serviços",
    ])

    with tab1:
        _render_execucao(key="clusters")
        st.info("Formadores")
        st.info("Empresas")
        st.info("Faturação")

    with tab2:
        _render_execucao(key="formacao")
        st.info("Formadores")
        st.info("Empresas")
        st.info("Faturação")

    with tab3:
        _render_execucao(key="comercio")
        st.info("Formadores")
        st.info("Empresas")
        st.info("Faturação")


def _render_execucao(key: str):
    """Bloco de Execucao: escolher projeto e ver acoes fechadas / em curso."""
    with st.expander("Execução", expanded=True):
        projeto = st.selectbox(
            "Seleciona o projeto",
            PROJETOS,
            key=f"exec_projeto_{key}",
        )
        st.markdown(f"**Execução — {projeto}**")

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
