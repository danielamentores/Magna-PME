"""Separador 'Controlo de Execução' do perfil do gestor.

Volume de formação = horas × formandos que terminaram.
Dados de exemplo — substituir pelos reais (db_gestor / Supabase).
"""
import streamlit as st

LIMIAR_ALERTA = 50  # % abaixo do qual se assinala "volume aquém do atribuído"

# ---------------------------------------------------------------------------
# PROJETOS (dados de exemplo)
# ---------------------------------------------------------------------------
PROJETOS_CLUSTERS = {
    "Produtech": {
        "dias_restantes": 120,
        "consultores": [
            {"nome": "Ana Martins", "volume_atribuido": 2000, "acoes": [
                {"nome": "Indústria 4.0", "horas": 20, "formandos": 10},
                {"nome": "Manutenção preditiva", "horas": 16, "formandos": 8},
            ]},
            {"nome": "Bruno Lopes", "volume_atribuido": 1500, "acoes": [
                {"nome": "Robótica colaborativa", "horas": 25, "formandos": 6},
            ]},
        ],
    },
    "APCMC": {
        "dias_restantes": 90,
        "consultores": [
            {"nome": "Carla Sousa", "volume_atribuido": 1800, "acoes": [
                {"nome": "Gestão de stocks", "horas": 30, "formandos": 12},
            ]},
        ],
    },
    "Calçado": {
        "dias_restantes": 200,
        "consultores": [
            {"nome": "Diogo Reis", "volume_atribuido": 1200, "acoes": [
                {"nome": "Design de produto", "horas": 24, "formandos": 9},
            ]},
        ],
    },
    "Mentores-Habitat": {
        "dias_restantes": 60,
        "consultores": [
            {"nome": "Eva Nunes", "volume_atribuido": 2200, "acoes": [
                {"nome": "Eficiência energética", "horas": 20, "formandos": 14},
                {"nome": "Materiais sustentáveis", "horas": 18, "formandos": 11},
            ]},
        ],
    },
    "APIMA": {
        "dias_restantes": 150,
        "consultores": [
            {"nome": "Filipe Costa", "volume_atribuido": 1600, "acoes": [
                {"nome": "Mobiliário e processos", "horas": 22, "formandos": 7},
            ]},
        ],
    },
    "ANIET": {
        "dias_restantes": 75,
        "consultores": [
            {"nome": "Gabriela Pinto", "volume_atribuido": 1900, "acoes": [
                {"nome": "Segurança em obra", "horas": 24, "formandos": 16},
            ]},
        ],
    },
}

# ---------------------------------------------------------------------------
# AÇÕES VINDAS DO FORMADOR (integradas no controlo de execução)
# ---------------------------------------------------------------------------
_ACOES_FORMADOR = [
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

# Consultor temporário onde ficam as ações ainda sem consultor atribuído
_CONSULTOR_POR_ATRIBUIR = "Ações Magna (a atribuir)"


def _integrar_acoes_formador():
    """Junta as ações do formador aos projetos, por nome de projeto.
    Como ainda não têm consultor, vão para um bloco 'a atribuir'.
    Corre uma vez (no carregamento do módulo)."""
    for ac in _ACOES_FORMADOR:
        proj_nome = (ac.get("projeto") or "—").strip()
        # encontra a chave do cluster (case-insensitive); se não existir, cria
        chave = next((k for k in PROJETOS_CLUSTERS if k.upper() == proj_nome.upper()), None)
        if chave is None:
            chave = proj_nome
            PROJETOS_CLUSTERS[chave] = {"dias_restantes": 0, "consultores": []}

        consultores = PROJETOS_CLUSTERS[chave]["consultores"]
        cons = next((c for c in consultores if c["nome"] == _CONSULTOR_POR_ATRIBUIR), None)
        if cons is None:
            cons = {"nome": _CONSULTOR_POR_ATRIBUIR, "volume_atribuido": 0, "acoes": []}
            consultores.append(cons)

        cons["acoes"].append({
            "nome": ac.get("nome", "—"),
            "horas": ac.get("volume_horas", 0),
            "formandos": ac.get("formandos_certificados", 0),
            "codigo": ac.get("codigo"),
            "empresa": ac.get("empresa_cliente"),
            "estado": ac.get("estado"),
        })


_integrar_acoes_formador()


# ---------------------------------------------------------------------------
# CÁLCULOS
# ---------------------------------------------------------------------------
def _vol_acao(a):
    return (a.get("horas") or 0) * (a.get("formandos") or 0)


def _vol_consultor(c):
    return sum(_vol_acao(a) for a in c.get("acoes", []))


def _totais_projeto(proj):
    vol_feito = sum(_vol_consultor(c) for c in proj["consultores"])
    vol_atrib = sum(c.get("volume_atribuido", 0) for c in proj["consultores"])
    pct = (vol_feito / vol_atrib * 100) if vol_atrib else 0
    return vol_feito, vol_atrib, pct


# ---------------------------------------------------------------------------
# RENDER
# ---------------------------------------------------------------------------
def render():
    st.subheader("📊 Controlo de Execução")
    area = st.radio(
        "Área",
        ["Clusters", "Formação Ação", "Comércio e Serviços"],
        horizontal=True,
        label_visibility="collapsed",
        key="ce_area",
    )
    if area == "Clusters":
        _render_clusters()
    else:
        st.info(f"«{area}» — em construção.")


def _render_clusters():
    sel = st.session_state.get("ce_proj_sel")
    if sel and sel in PROJETOS_CLUSTERS:
        _render_detalhe(sel)
        return

    st.caption("Clica num projeto para ver a execução por consultor.")
    nomes = list(PROJETOS_CLUSTERS.keys())
    cols = st.columns(3)
    for i, nome in enumerate(nomes):
        proj = PROJETOS_CLUSTERS[nome]
        vol_feito, vol_atrib, pct = _totais_projeto(proj)
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"**{nome}**")
                st.metric("Execução", f"{pct:.0f}%")
                st.progress(min(pct / 100, 1.0))
                st.caption(f"Volume: {vol_feito} / {vol_atrib}")
                st.caption(f"⏳ {proj['dias_restantes']} dias para terminar")
                if st.button("Ver detalhe", key=f"ce_ver_{nome}", use_container_width=True):
                    st.session_state["ce_proj_sel"] = nome
                    st.rerun()


def _render_detalhe(nome):
    proj = PROJETOS_CLUSTERS[nome]
    if st.button("← Voltar aos projetos", key="ce_voltar"):
        st.session_state.pop("ce_proj_sel", None)
        st.rerun()

    st.markdown(f"### {nome}")
    vol_feito, vol_atrib, pct = _totais_projeto(proj)
    c1, c2, c3 = st.columns(3)
    c1.metric("Execução", f"{pct:.0f}%")
    c2.metric("Volume feito", f"{vol_feito} / {vol_atrib}")
    c3.metric("Dias restantes", proj["dias_restantes"])

    st.divider()
    st.markdown("#### Consultores")
    for c in proj["consultores"]:
        vc = _vol_consultor(c)
        va = c.get("volume_atribuido", 0)
        with st.container(border=True):
            st.markdown(f"**{c['nome']}**")
            if va > 0:
                pc = vc / va * 100
                st.caption(f"Volume: {vc} / {va}  ·  {pc:.0f}% do atribuído")
                st.progress(min(pc / 100, 1.0))
                if pc < LIMIAR_ALERTA:
                    st.warning("⚠️ Volume bastante abaixo do atribuído — considerar redistribuir.")
            else:
                st.caption(f"Volume: {vc}  ·  sem volume atribuído definido")

            st.caption("Ações de formação:")
            for a in c.get("acoes", []):
                extra = f" [{a['codigo']}]" if a.get("codigo") else ""
                empresa = f" · {a['empresa']}" if a.get("empresa") else ""
                st.caption(
                    f"• {a['nome']}{extra}{empresa} — {a['horas']}h × {a['formandos']} formandos "
                    f"= {_vol_acao(a)} de volume"
                )
