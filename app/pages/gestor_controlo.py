"""Separador 'Controlo de Execução' do perfil do gestor.

Fase de demonstração: a % de execução de cada projeto é fixada em "pct_demo".
Ao abrir um consultor vê-se a tabela das suas ações (fechadas / em execução),
com exportação para Excel. Volume = horas × formandos que terminaram.
"""
import io
import streamlit as st
import pandas as pd

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

_EMPRESAS = [
    "Madeicarpin, Lda", "Florestas do Norte, SA", "Construções Beira",
    "Mobiliário Sul", "Tecno Verde", "AgroServiços, Lda",
    "Indústrias Reunidas", "Habitat Pro", "Serralharia Central",
]


# ---------------------------------------------------------------------------
# CÁLCULOS / EXEMPLOS
# ---------------------------------------------------------------------------
def _fmt(n):
    return f"{n:.0f}" if float(n).is_integer() else f"{n:.1f}"


def _consultor_pct(proj, c):
    pct_demo = proj.get("pct_demo")
    if pct_demo is None or not c.get("volume_atribuido"):
        return None
    if len(proj["consultores"]) == 1:
        return float(pct_demo)
    base = sum(ord(ch) for ch in c["nome"])
    return float(max(4, min(96, pct_demo + ((base % 31) - 15))))


def _consultor_feito(proj, c):
    va = c.get("volume_atribuido") or 0
    pc = _consultor_pct(proj, c)
    return round(pc / 100 * va) if pc is not None else 0


def _gerar_acoes(nome, vol_feito):
    """Ações de exemplo do consultor: várias fechadas (somam ~volume feito)
    e algumas em execução. Fase visual."""
    base = sum(ord(ch) for ch in nome)
    horas_opts = [16, 20, 24, 25, 30]
    acoes = []

    if vol_feito > 0:
        n = max(3, min(15, int(vol_feito // 400)))
        restante = vol_feito
        for i in range(n):
            h = horas_opts[(base + i) % len(horas_opts)]
            vol_alvo = restante if i == n - 1 else round(vol_feito / n)
            f = max(1, round(vol_alvo / h))
            acoes.append({
                "Ação": f"{_TEMAS[(base + i) % len(_TEMAS)]} (nível {i % 3 + 1})",
                "Empresa": _EMPRESAS[(base + i) % len(_EMPRESAS)],
                "Horas": h, "Formandos": f, "Volume": h * f, "Estado": "Fechada",
            })
            restante -= h * f

    for j in range(3 + base % 3):
        h = horas_opts[(base + j + 2) % len(horas_opts)]
        f = (base + j) % 12  # formandos já terminados (parcial)
        acoes.append({
            "Ação": f"{_TEMAS[(base + j + 1) % len(_TEMAS)]} (nível {j % 3 + 1})",
            "Empresa": _EMPRESAS[(base + j + 3) % len(_EMPRESAS)],
            "Horas": h, "Formandos": f, "Volume": h * f, "Estado": "Em execução",
        })
    return acoes


def _excel_bytes(df):
    """Converte o DataFrame para bytes de Excel (.xlsx)."""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="Ações")
    return buf.getvalue()


# ---------------------------------------------------------------------------
# CÁLCULO DOS TOTAIS
# ---------------------------------------------------------------------------
def _totais_projeto(proj):
    vol_atrib = sum((c.get("volume_atribuido") or 0) for c in proj["consultores"])
    n_acoes = sum((c.get("n_acoes") or 0) for c in proj["consultores"])
    pct = float(proj.get("pct_demo") or 0)
    vol_feito = round(pct / 100 * vol_atrib)
    return vol_feito, vol_atrib, pct, n_acoes


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


def _render_detalhe(proj_nome):
    proj = PROJETOS_CLUSTERS[proj_nome]
    if st.button("← Voltar aos projetos", key="ce_voltar"):
        st.session_state.pop("ce_proj_sel", None)
        st.rerun()

    st.markdown(f"### {proj_nome}")
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
        label = (f"{c['nome']}  —  {pc:.0f}%  ({_fmt(vc)} / {_fmt(va)})"
                 if pc is not None else f"{c['nome']}  —  volume feito {_fmt(vc)}")

        with st.expander(label):
            if pc is not None:
                st.progress(min(pc / 100, 1.0))

            acoes = _gerar_acoes(c["nome"], vc)
            df = pd.DataFrame(acoes)
            chave = f"{proj_nome}_{c['nome']}"

            n_fech = int((df["Estado"] == "Fechada").sum()) if not df.empty else 0
            n_exec = int((df["Estado"] == "Em execução").sum()) if not df.empty else 0

            filtro = st.radio(
                "Estado",
                ["Todas", f"Fechadas ({n_fech})", f"Em execução ({n_exec})"],
                horizontal=True,
                label_visibility="collapsed",
                key=f"acfil_{chave}",
            )
            df_v = df
            if filtro.startswith("Fechadas"):
                df_v = df[df["Estado"] == "Fechada"]
            elif filtro.startswith("Em execução"):
                df_v = df[df["Estado"] == "Em execução"]

            if df_v.empty:
                st.caption("Sem ações para mostrar.")
            else:
                st.dataframe(df_v, hide_index=True, use_container_width=True)
                st.download_button(
                    "⬇️ Exportar para Excel",
                    data=_excel_bytes(df_v),
                    file_name=f"acoes_{c['nome'].replace(' ', '_')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"acxls_{chave}",
                )
