"""Separador 'Controlo de Execução' do perfil do gestor.

Dados dos consultores por projeto, vindos do mapa de execução (Excel).
Volume = volume de formação (horas × formandos que terminaram), já totalizado
por consultor na coluna "Volume Terminado". "volume_atribuido" é o volume
que foi atribuído a cada consultor.
"""
import streamlit as st

LIMIAR_ALERTA = 50  # % do atribuído abaixo do qual se assinala "aquém"

# ---------------------------------------------------------------------------
# PROJETOS (dados reais do mapa de execução)
# Produtech e Calçado começaram este ano — ainda sem execução.
# ---------------------------------------------------------------------------
PROJETOS_CLUSTERS = {
    "Produtech": {
        "dias_restantes": None,
        "consultores": [],
    },
    "APCMC": {
        "dias_restantes": 122,
        "consultores": [
            {"nome": "RPA", "volume_atribuido": 30360, "volume_feito": 1903},
            {"nome": "Euroceg", "volume_atribuido": 86680, "volume_feito": 36990},
            {"nome": "Mais Advantage", "volume_atribuido": 28400, "volume_feito": 176},
            {"nome": "Nortefor", "volume_atribuido": 5680, "volume_feito": 1073},
            {"nome": "Winet", "volume_atribuido": 168, "volume_feito": 56},
            {"nome": "Talento Planetário", "volume_atribuido": 4772, "volume_feito": 1616},
            {"nome": "Semet", "volume_atribuido": 6000, "volume_feito": 480},
            {"nome": "Lenhotec", "volume_atribuido": 3760, "volume_feito": 695},
            {"nome": "Etapas", "volume_atribuido": 14600, "volume_feito": 3000},
            {"nome": "Mentores & Tutores", "volume_atribuido": 4000, "volume_feito": 597},
        ],
    },
    "Calçado": {
        "dias_restantes": None,
        "consultores": [],
    },
    "Mentores": {
        "dias_restantes": 253,
        "consultores": [
            {"nome": "RPA", "volume_atribuido": 16538, "volume_feito": 0},
            {"nome": "Euroceg", "volume_atribuido": 9000, "volume_feito": 0},
            {"nome": "Cristina Ferreira", "volume_atribuido": 7510, "volume_feito": 0},
            {"nome": "Mais Advantage", "volume_atribuido": 45125, "volume_feito": 1352},
            {"nome": "Nortefor", "volume_atribuido": 28375, "volume_feito": 482},
            {"nome": "Winet", "volume_atribuido": 30125, "volume_feito": 2974},
            {"nome": "Talento Planetário", "volume_atribuido": 15750, "volume_feito": 2439},
            {"nome": "Semet", "volume_atribuido": 15000, "volume_feito": 7104},
            {"nome": "Multiformativa", "volume_atribuido": 16538, "volume_feito": 328},
            {"nome": "Etapas", "volume_atribuido": 36238, "volume_feito": 9147},
            {"nome": "Mentores & Tutores", "volume_atribuido": 13538, "volume_feito": 2066},
            {"nome": "AEBA", "volume_atribuido": 20000, "volume_feito": 0},
        ],
    },
    "APIMA": {
        "dias_restantes": 253,
        "consultores": [
            {"nome": "Consultora Joana Peixoto", "volume_atribuido": 23000, "volume_feito": 400},
            {"nome": "Semet", "volume_atribuido": 5000, "volume_feito": 240},
            {"nome": "Lenhotec", "volume_atribuido": 58000, "volume_feito": 3083.5},
            {"nome": "Psolutions", "volume_atribuido": 12000, "volume_feito": 0},
            {"nome": "Mentores & Tutores", "volume_atribuido": 2000, "volume_feito": 0},
        ],
    },
    "ANIET": {
        "dias_restantes": 192,
        "consultores": [
            {"nome": "Mais Advantage", "volume_atribuido": 9760, "volume_feito": 2906},
            {"nome": "Omega", "volume_atribuido": 11760, "volume_feito": 4864},
            {"nome": "Winet", "volume_atribuido": 25080, "volume_feito": 5706},
            {"nome": "Semet", "volume_atribuido": 12000, "volume_feito": 8327},
            {"nome": "Consultora Joana Peixoto", "volume_atribuido": 9800, "volume_feito": 550},
            {"nome": "Multiformativa", "volume_atribuido": 2840, "volume_feito": 448},
            {"nome": "Psolutions", "volume_atribuido": 29000, "volume_feito": 1200},
            {"nome": "Lenhotec", "volume_atribuido": 1200, "volume_feito": 1200},
        ],
    },
}


# ---------------------------------------------------------------------------
# CÁLCULOS
# ---------------------------------------------------------------------------
def _vol_consultor(c):
    return c.get("volume_feito", 0)


def _totais_projeto(proj):
    vol_feito = sum(_vol_consultor(c) for c in proj["consultores"])
    vol_atrib = sum(c.get("volume_atribuido", 0) for c in proj["consultores"])
    pct = (vol_feito / vol_atrib * 100) if vol_atrib else 0
    return vol_feito, vol_atrib, pct


def _fmt(n):
    """Mostra inteiros sem decimais e o resto com 1 casa."""
    return f"{n:.0f}" if float(n).is_integer() else f"{n:.1f}"


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
        dias = proj.get("dias_restantes")
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"**{nome}**")
                if not proj["consultores"]:
                    st.caption("A iniciar este ano — sem execução ainda.")
                    st.button("Ver detalhe", key=f"ce_ver_{nome}",
                              use_container_width=True, disabled=True)
                    continue
                st.metric("Execução", f"{pct:.0f}%")
                st.progress(min(pct / 100, 1.0))
                st.caption(f"Volume: {_fmt(vol_feito)} / {_fmt(vol_atrib)}")
                st.caption(f"⏳ {dias} dias para terminar" if dias is not None else "⏳ —")
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
    dias = proj.get("dias_restantes")
    c1, c2, c3 = st.columns(3)
    c1.metric("Execução", f"{pct:.0f}%")
    c2.metric("Volume feito", f"{_fmt(vol_feito)} / {_fmt(vol_atrib)}")
    c3.metric("Dias restantes", dias if dias is not None else "—")

    if not proj["consultores"]:
        st.info("Projeto a iniciar este ano — ainda sem consultores/execução.")
        return

    st.divider()
    st.markdown("#### Consultores")
    # ordenar do mais aquém para o mais avançado
    consultores = sorted(
        proj["consultores"],
        key=lambda c: (c["volume_feito"] / c["volume_atribuido"]) if c.get("volume_atribuido") else 0,
    )
    for c in consultores:
        vc = _vol_consultor(c)
        va = c.get("volume_atribuido", 0)
        with st.container(border=True):
            st.markdown(f"**{c['nome']}**")
            if va > 0:
                pc = vc / va * 100
                st.caption(f"Volume: {_fmt(vc)} / {_fmt(va)}  ·  {pc:.0f}% do atribuído")
                st.progress(min(pc / 100, 1.0))
                if pc < LIMIAR_ALERTA:
                    st.warning("⚠️ Abaixo do volume atribuído — considerar redistribuir.")
            else:
                st.caption(f"Volume feito: {_fmt(vc)}  ·  sem volume atribuído")
