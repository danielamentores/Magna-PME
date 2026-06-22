"""Separador 'Controlo de Execução' do perfil do gestor.

Fase visual: dados de exemplo. Volume de formação = horas × formandos que
terminaram (ex.: 20h × 10 formandos = 200). Mais tarde trocamos os dados
mock pelas datas de fim e volumes reais (db_gestor / Supabase).
"""
import streamlit as st

# Limiar abaixo do qual se assinala "volume aquém do atribuído"
LIMIAR_ALERTA = 50  # %

# ---------------------------------------------------------------------------
# DADOS DE EXEMPLO (substituir pelos reais)
# ---------------------------------------------------------------------------
# Cada ação: horas + formandos (que terminaram) → volume = horas * formandos
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
        pc = (vc / va * 100) if va else 0
        with st.container(border=True):
            st.markdown(f"**{c['nome']}**")
            st.caption(f"Volume: {vc} / {va}  ·  {pc:.0f}% do atribuído")
            st.progress(min(pc / 100, 1.0))
            if pc < LIMIAR_ALERTA:
                st.warning("⚠️ Volume bastante abaixo do atribuído — considerar redistribuir.")

            st.caption("Ações de formação:")
            for a in c.get("acoes", []):
                st.caption(
                    f"• {a['nome']} — {a['horas']}h × {a['formandos']} formandos "
                    f"= {_vol_acao(a)} de volume"
                )
