"""Tab Projetos Clusters."""
import streamlit as st
from app import db_coordenador as db

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
        {"acao": "Ação 1 - Excel Avançado",    "formandos": 12, "certificados": 11, "volume_horas": 30,
         "valor_compete": 4500.0, "valor_mentores": 3000.0, "reembolso": True,  "faturada": True,  "paga": True},
        {"acao": "Ação 2 - Gestão de Equipas", "formandos": 8,  "certificados": 8,  "volume_horas": 25,
         "valor_compete": 3200.0, "valor_mentores": 2100.0, "reembolso": True,  "faturada": True,  "paga": False},
    ],
    "Beta Serviços, SA": [
        {"acao": "Ação 1 - Marketing Digital", "formandos": 10, "certificados": 9, "volume_horas": 40,
         "valor_compete": 6000.0, "valor_mentores": 4000.0, "reembolso": False, "faturada": False, "paga": False},
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
    _render_faturacao()

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

        total_compete = 0.0
        total_mentores = 0.0
        for a in acoes:
            with st.container(border=True):
                st.markdown(f"**{a['acao']}**")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Formandos certificados", f"{a['certificados']}/{a['formandos']}")
                c2.metric("Volume de formação", f"{a['volume_horas']} h")
                c3.metric("Valor COMPETE (empresa)", _eur(a["valor_compete"]))
                c4.metric("Valor Mentores fatura", _eur(a["valor_mentores"]))

                s1, s2, s3 = st.columns(3)
                s1.write("Reembolso: " + ("✅ Sim" if a["reembolso"] else "⏳ Não"))
                s2.write("Faturada à empresa: " + ("✅ Sim" if a["faturada"] else "❌ Não"))
                s3.write("Paga à Mentores: " + ("✅ Sim" if a["paga"] else "❌ Não"))
            total_compete += a["valor_compete"]
            total_mentores += a["valor_mentores"]

        st.divider()
        t1, t2 = st.columns(2)
        t1.metric("Total COMPETE (empresa recebe)", _eur(total_compete))
        t2.metric("Total a faturar Mentores", _eur(total_mentores))

def _render_faturacao():
    with st.expander("Faturação", expanded=False):
        m1, m2 = st.columns(2)
        m1.metric("Total já faturado", _eur(sum(a["valor"] for a in db.acoes_em("Faturada", "Paga"))))
        m2.metric("Total já recebido (pago)", _eur(sum(a["valor"] for a in db.acoes_em("Paga"))))
        st.divider()

        st.markdown("##### 1. Ações fechadas — selecionar para enviar à gestora")
        estados = db.estados()
        fechadas = db.acoes_em("Fechada", "Devolvida")
        if not fechadas:
            st.caption("Sem ações por enviar.")
        else:
            selecionadas = []
            for a in fechadas:
                txt = f"{a['acao']} — {a['empresa']} — {_eur(a['valor'])}"
                if estados[a["id"]] == "Devolvida":
                    txt += "  ↩️ devolvida — reenviar"
                if st.checkbox(txt, key=f"fat_chk_{a['id']}"):
                    selecionadas.append(a)
            if st.button("📧 Enviar à gestora para confirmação", key="fat_enviar_gestora"):
                if selecionadas:
                    for a in selecionadas:
                        db.definir_estado(a["id"], "Em confirmação")
                    st.success(f"{len(selecionadas)} ação(ões) enviada(s) à gestora (15 dias para confirmar).")
                    st.rerun()
                else:
                    st.warning("Seleciona pelo menos uma ação.")

        em_conf = db.acoes_em("Em confirmação")
        if em_conf:
            st.divider()
            st.markdown("##### 2. A aguardar confirmação da gestora (prazo: 15 dias)")
            for a in em_conf:
                st.write(f"⏳ {a['acao']} — {a['empresa']} — {_eur(a['valor'])}")

        devolvidas = db.acoes_em("Devolvida")
        if devolvidas:
            st.divider()
            st.markdown("##### Ações devolvidas pela gestora")
            for a in devolvidas:
                st.write(f"↩️ {a['acao']} — {a['empresa']} — {_eur(a['valor'])}")
                com = db.comentario(a["id"])
                if com:
                    st.caption(f"💬 Motivo: {com}")
                else:
                    st.caption("Corrige e reenvia acima.")

        aceites = db.acoes_em("Aceite")
        if aceites:
            st.divider()
            st.markdown("##### 3. Aceites pela gestora — nota de honorários recebida por email")
            for a in aceites:
                st.write(f"✅ {a['acao']} — {a['empresa']} — {_eur(a['valor'])}")
            st.metric("Valor da nota a faturar ao financeiro", _eur(sum(a["valor"] for a in aceites)))
            st.caption("Carrega a fatura com este valor para o financeiro.")
            ficheiro = st.file_uploader("Fatura para o financeiro", type=["pdf"], key="fat_upload")
            if st.button("Submeter fatura ao financeiro", key="fat_submeter"):
                if ficheiro is not None:
                    for a in aceites:
                        db.definir_estado(a["id"], "Faturada")
                    st.success("Fatura submetida ao financeiro. Aguarda pagamento.")
                    st.rerun()
                else:
                    st.warning("Carrega o ficheiro da fatura primeiro.")

        st.divider()
        st.markdown("##### Ações já faturadas e pagas")
        fp = db.acoes_em("Faturada", "Paga")
        if not fp:
            st.caption("Ainda sem ações faturadas.")
        else:
            estados = db.estados()
            for a in fp:
                icone = "💶 Paga" if estados[a["id"]] == "Paga" else "🧾 Faturada (aguarda pagamento)"
                st.write(f"{a['acao']} — {a['empresa']} — {_eur(a['valor'])} — {icone}")
