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

    
    st.info("Empresas")
    # --- Empresas (exemplo) ---
EMPRESAS = [
    {"nome": "Empresa Alfa, Lda", "nif": "501234567", "estado": "Validada"},
    {"nome": "Beta Serviços, SA", "nif": "502345678", "estado": "Validada"},
    {"nome": "Gama Comércio, Lda", "nif": "503456789", "estado": "Execução pendente"},
]

ACOES_EMPRESA = {
    "Empresa Alfa, Lda": [
        {"acao": "Ação 1 - Excel Avançado",    "formandos": 12, "certificados": 11, "volume_horas": 30, "valor_compete": 4500.0},
        {"acao": "Ação 2 - Gestão de Equipas", "formandos": 8,  "certificados": 8,  "volume_horas": 25, "valor_compete": 3200.0},
    ],
    "Beta Serviços, SA": [
        {"acao": "Ação 1 - Marketing Digital", "formandos": 10, "certificados": 9, "volume_horas": 40, "valor_compete": 6000.0},
    ],
}


def _eur(v: float) -> str:
    """Formata em euros no estilo PT: 4 500,00 €"""
    s = f"{v:,.2f}".replace(",", " ").replace(".", ",")
    return f"{s} €"


def render():
    _render_execucao()
    _render_formadores()
    _render_empresas()
    st.info("Faturação")


def _render_execucao():
    with st.expander("Execução", expanded=True):
        projeto = st.selectbox("Seleciona o projeto", PROJETOS, key="exec_projeto_clusters")
        st.markdown(f"**Execução — {projeto}**")

        if projeto in VOLUMES:
            vol = VOLUMES[projeto]
            atribuido, realizado = vol["atribuido"], vol["realizado"]
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
        for i, a in enumerate(ACOES_FORMADOR.get(nome_sel, [])):
            with st.container(border=True):
                st.markdown(f"**{a['acao']}**")
                c1, c2, c3 = st.columns(3)
                c1.write("Fechada na Magna: " + ("✅ Sim" if a["fechada_magna"] else "⏳ Não"))
                c2.write("Faturou: " + ("✅ Sim" if a["faturou"] else "❌ Não"))
                c3.write("Paga: " + ("✅ Sim" if a["paga"] else "❌ Não"))
                if a["faturou"] and a["fatura"]:
                    st.download_button("📄 Cópia da fatura", data=b"Fatura de exemplo.",
                                       file_name=a["fatura"], key=f"fatura_clusters_{nome_sel}_{i}")
                else:
                    st.caption("Sem fatura submetida.")


def _empresas_todas():
    """Empresas base + as adicionadas nesta sessão (apenas visual)."""
    return EMPRESAS + st.session_state.get("empresas_extra_clusters", [])


def _render_empresas():
    with st.expander("Empresas", expanded=False):
        vista = st.radio(
            "Vista",
            ["Validadas", "Execução pendente", "Adicionar empresa"],
            horizontal=True,
            label_visibility="collapsed",
            key="emp_vista_clusters",
        )

        if vista == "Adicionar empresa":
            _form_adicionar_empresa()
            return

        estado = "Validada" if vista == "Validadas" else "Execução pendente"
        empresas = [e for e in _empresas_todas() if e["estado"] == estado]

        termo = st.text_input("Pesquisar empresa", key="emp_pesquisa_clusters")
        if termo:
            empresas = [e for e in empresas if termo.lower() in e["nome"].lower()]

        if not empresas:
            st.caption("Sem empresas para mostrar.")
            return

        nome_sel = st.selectbox("Seleciona a empresa", [e["nome"] for e in empresas],
                                key="emp_sel_clusters")

        st.markdown("##### Ações de formação")
        acoes = ACOES_EMPRESA.get(nome_sel, [])
        if not acoes:
            st.info("Sem ações de formação registadas para esta empresa.")
            return

        total = 0.0
        for a in acoes:
            with st.container(border=True):
                st.markdown(f"**{a['acao']}**")
                c1, c2, c3 = st.columns(3)
                c1.metric("Formandos certificados", f"{a['certificados']}/{a['formandos']}")
                c2.metric("Volume de formação", f"{a['volume_horas']} h")
                c3.metric("Valor COMPETE", _eur(a["valor_compete"]))
            total += a["valor_compete"]

        st.divider()
        st.metric("Total a receber do COMPETE", _eur(total))


def _form_adicionar_empresa():
    st.markdown("##### Adicionar empresa ao projeto")
    with st.form("form_emp_clusters", clear_on_submit=True):
        nome = st.text_input("Nome da empresa")
        nif = st.text_input("NIF")
        estado = st.selectbox("Estado", ["Validada", "Execução pendente"])
        if st.form_submit_button("Adicionar"):
            if nome and nif:
                st.session_state.setdefault("empresas_extra_clusters", []).append(
                    {"nome": nome, "nif": nif, "estado": estado}
                )
                st.success(f"Empresa «{nome}» adicionada.")
            else:
                st.warning("Preenche pelo menos o nome e o NIF.")
    st.info("Faturação")
