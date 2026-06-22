"""Separador 'Controlo de Execução' do perfil do gestor.

Fase de demonstração: a % de execução de cada projeto é fixada em "pct_demo".
Cada consultor mostra uma % à volta desse valor (variação realista) e as suas
ações de formação ao expandir. Volume = horas × formandos que terminaram.
"""
import streamlit as st

# ---------------------------------------------------------------------------
# PROJETOS (volume atribuído real; % de execução ajustada para a demo)
# ---------------------------------------------------------------------------
PROJETOS_CLUSTERS = {
    "Produtech": {
        "dias_restantes": None,
        "pct_demo": 9,
        "consultores": [
            {"nome": "Semet", "volume_atribuido": 66667, "n_acoes": 7},
        ],
    },
    "APCMC": {
        "dias_restantes": 122,
        "pct_demo": 71,
        "consultores": [
            {"nome": "RPA", "volume_atribuido": 30360},
            {"nome": "Euroceg", "volume_atribuido": 86680},
            {"nome": "Mais Advantage", "volume_atribuido": 28400},
            {"nome": "Nortefor", "volume_atribuido": 5680},
            {"nome": "Winet", "volume_atribuido": 168},
            {"nome": "Talento Planetário", "volume_atribuido": 4772},
            {"nome": "Semet", "volume_atribuido": 6000},
            {"nome": "Lenhotec", "volume_atribuido": 3760},
            {"nome": "Etapas", "volume_atribuido": 14600},
            {"nome": "Mentores & Tutores", "volume_atribuido": 4000},
        ],
    },
    "Calçado": {
        "dias_restantes": None,
        "pct_demo": 5,
        "consultores": [
            {"nome": "Etapas", "volume_atribuido": 46000, "n_acoes": 7},
        ],
    },
    "Mentores": {
        "dias_restantes": 253,
        "pct_demo": 34,
        "consultores": [
            {"nome": "RPA", "volume_atribuido": 16538},
            {"nome": "Euroceg", "volume_atribuido": 9000},
            {"nome": "Cristina Ferreira", "volume_atribuido": 7510},
            {"nome": "Mais Advantage", "volume_atribuido": 45125},
            {"nome": "Nortefor", "volume_atribuido": 28375},
            {"nome": "Winet", "volume_atribuido": 30125},
            {"nome": "Talento Planetário", "volume_atribuido": 15750},
            {"nome": "Semet", "volume_atribuido": 15000},
            {"nome": "Multiformativa", "volume_atribuido": 16538},
            {"nome": "Etapas", "volume_atribuido": 36238},
            {"nome": "Mentores & Tutores", "volume_atribuido": 13538},
            {"nome": "AEBA", "volume_atribuido": 20000},
        ],
    },
    "APIMA": {
        "dias_restantes": 253,
        "pct_demo": 15,
        "consultores": [
            {"nome": "Consultora Joana Peixoto", "volume_atribuido": 23000},
            {"nome": "Semet", "volume_atribuido": 5000},
            {"nome": "Lenhotec", "volume_atribuido": 58000},
            {"nome": "Psolutions", "volume_atribuido": 12000},
            {"nome": "Mentores & Tutores", "volume_atribuido": 2000},
        ],
    },
    "ANIET": {
        "dias_restantes": 192,
        "pct_demo": 66,
        "consultores": [
            {"nome": "Mais Advantage", "volume_atribuido": 9760},
            {"nome": "Omega", "volume_atribuido": 11760},
            {"nome": "Winet", "volume_atribuido": 25080},
            {"nome": "Semet", "volume_atribuido": 12000},
            {"nome": "Consultora Joana Peixoto", "volume_atribuido": 9800},
            {"nome": "Multiformativa", "volume_atribuido": 2840},
            {"nome": "Psolutions", "volume_atribuido": 29000},
            {"nome": "Lenhotec", "volume_atribuido": 1200},
        ],
    },
}

_TEMAS = [
    "Higiene e Segurança no Trabalho",
    "Excel Aplicado à Gestão",
    "Liderança e Gestão de Equipas",
    "Marketing Digital",
    "Sustentabilidade e Economia Circular",
    "Atendimento e Vendas",
]


# ---------------------------------------------------------------------------
# CÁLCULOS / EXEMPLOS
# ---------------------------------------------------------------------------
def _fmt(n):
    return f"{n:.0f}" if float(n).is_integer() else f"{n:.1f}"


def _consultor_pct(proj, c):
    """% de execução do consultor: à volta da % do projeto, com variação."""
    pct_demo = proj.get("pct_demo")
    if pct_demo is None or not c.get("volume_atribuido"):
        return None
    if len(proj["consultores"]) == 1:
        return float(pct_demo)
    base = sum(ord(ch) for ch in c["nome"])
    pc = pct_demo + ((base % 31) - 15)  # ±15
    return float(max(4, min(96, pc)))


def _consultor_feito(proj, c):
    va = c.get("volume_atribuido") or 0
    pc = _consultor_pct(proj, c)
    if pc is None:
        return 0
    return round(pc / 100 * va)


def _totais_projeto(proj):
    vol_atrib = sum((c.get("volume_atribuido") or 0) for c in proj["consultores"])
    n_acoes = sum((c.get("n_acoes") or 0) for c in proj["consultores"])
    pct = float(proj.get("pct_demo") or 0)
    vol_feito = round(pct / 100 * vol_atrib)
    return vol_feito, vol_atrib, pct, n_acoes


def _acoes_exemplo(nome, V):
    """Duas ações de exemplo que repartem o volume feito do consultor."""
    if V <= 0:
        return []
    base = sum(ord(ch) for ch in nome)
    i1 = base % len(_TEMAS)
    i2 = (base // 5 + 2) % len(_TEMAS)
    if i2 == i1:
        i2 = (i1 + 1) % len(_TEMAS)
    v1 = round(V * 0.6)
    v2 = V - v1
    return [
        {"nome": _TEMAS[i1], "horas": 25, "formandos": max(1, round(v1 / 25))},
        {"nome": _TEMAS[i2], "horas": 20, "formandos": max(1, round(v2 / 20))},
    ]


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
        vol_feito, vol_atrib, pct, n_acoes = _totais_projeto(proj)
        dias = proj.get("dias_restantes")
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"**{nome}**")
                st.metric("Execução", f"{pct:.0f}%")
                st.progress(min(pct / 100, 1.0))
                st.caption(f"Volume: {_fmt(vol_feito)} / {_fmt(vol_atrib)}")
                st.caption(f"⏳ {dias} dias para terminar" if dias is not None else "⏳ data de fim por definir")
                if st.button("Ver detalhe", key=f"ce_ver_{nome}", use_container_width=True):
                    st.session_state["ce_proj_sel"] = nome
                    st.rerun()


def _render_detalhe(nome):
    proj = PROJETOS_CLUSTERS[nome]
    if st.button("← Voltar aos projetos", key="ce_voltar"):
        st.session_state.pop("ce_proj_sel", None)
        st.rerun()

    st.markdown(f"### {nome}")
    vol_feito, vol_atrib, pct, n_acoes = _totais_projeto(proj)
    dias = proj.get("dias_restantes")
    c1, c2, c3 = st.columns(3)
    c1.metric("Execução", f"{pct:.0f}%")
    c2.metric("Volume feito", f"{_fmt(vol_feito)} / {_fmt(vol_atrib)}")
    c3.metric("Dias restantes", dias if dias is not None else "—")

    st.divider()
    st.markdown("#### Consultores (clica para ver as ações)")
    consultores = sorted(proj["consultores"], key=lambda c: _consultor_pct(proj, c) or 0)
    for c in consultores:
        pc = _consultor_pct(proj, c)
        vc = _consultor_feito(proj, c)
        va = c.get("volume_atribuido")
        if pc is not None:
            label = f"{c['nome']}  —  {pc:.0f}%  ({_fmt(vc)} / {_fmt(va)})"
        else:
            label = f"{c['nome']}  —  volume feito {_fmt(vc)}"

        with st.expander(label):
            if pc is not None:
                st.progress(min(pc / 100, 1.0))
                st.caption(f"{_fmt(vc)} de {_fmt(va)} do volume atribuído")
            st.markdown("**Ações de formação**")
            acoes = _acoes_exemplo(c["nome"], vc)
            if not acoes:
                st.caption("Sem ações terminadas ainda.")
            else:
                for a in acoes:
                    vol = a["horas"] * a["formandos"]
                    st.caption(
                        f"• {a['nome']} — {a['horas']}h × {a['formandos']} formandos = {vol} de volume"
                    )
