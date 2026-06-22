"""Separador 'Reembolsos' do perfil do gestor.

Reaproveita os projetos/consultores/ações do gestor_controlo.
Aqui só aparecem as ações FECHADAS. A gestora pode pô-las em reembolso
(a coordenadora vê o alerta no perfil dela) e exportar para Excel.
"""
import streamlit as st
import pandas as pd

from app import db_coordenador as db
from app.pages import gestor_controlo as ge

# ---------------------------------------------------------------------------
# REEMBOLSOS POR PROJETO (acumulam-se; por agora um por projeto)
# ---------------------------------------------------------------------------
REEMBOLSOS = {
    "APCMC": [{"valor": 200000, "pct": 10}],
    "ANIET": [{"valor": 78000, "pct": 4}],
    "Mentores": [{"valor": 230000, "pct": 5}],
}


def _reembolso_totais(proj_nome):
    rs = REEMBOLSOS.get(proj_nome, [])
    return len(rs), sum(r["valor"] for r in rs), sum(r["pct"] for r in rs)


def _fechadas_projeto(proj_nome):
    """Devolve {key: info} de todas as ações fechadas do projeto."""
    proj = ge.PROJETOS_CLUSTERS[proj_nome]
    out = {}
    for c in proj["consultores"]:
        vc = ge._consultor_feito(proj, c)
        fechadas = [a for a in ge._gerar_acoes(c["nome"], vc) if a["Estado"] == "Fechada"]
        for idx, a in enumerate(fechadas):
            key = f"{proj_nome}|{c['nome']}|{idx}"
            out[key] = {
                "Consultor": c["nome"], "Ação": a["Ação"], "Empresa": a["Empresa"],
                "Horas": a["Horas"], "Formandos": a["Formandos"], "Volume": a["Volume"],
                "Estado": a["Estado"],
            }
    return out


# ---------------------------------------------------------------------------
# RENDER
# ---------------------------------------------------------------------------
def render():
    st.subheader("💼 Reembolsos")
    area = st.radio(
        "Área",
        ["Clusters", "Formação Ação", "Comércio e Serviços"],
        horizontal=True,
        label_visibility="collapsed",
        key="re_area",
    )
    if area == "Clusters":
        _render_clusters()
    else:
        st.info(f"«{area}» — em construção.")


def _render_clusters():
    sel = st.session_state.get("re_proj_sel")
    if sel and sel in ge.PROJETOS_CLUSTERS:
        _render_detalhe(sel)
        return

    st.caption("Estado de reembolso por projeto. Clica para ver as ações fechadas.")
    nomes = list(ge.PROJETOS_CLUSTERS.keys())
    cols = st.columns(3)
    for i, nome in enumerate(nomes):
        n, valor, pct = _reembolso_totais(nome)
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"**{nome}**")
                if n > 0:
                    st.metric("Reembolso (acumulado)", db.eur(valor))
                    st.caption(f"✅ {pct}% · {n} reembolso(s)")
                else:
                    st.metric("Reembolso", "—")
                    st.caption("Sem reembolso ainda")
                if st.button("Ver ações fechadas", key=f"re_ver_{nome}", use_container_width=True):
                    st.session_state["re_proj_sel"] = nome
                    st.rerun()


def _render_detalhe(proj_nome):
    if st.button("← Voltar aos projetos", key="re_voltar"):
        st.session_state.pop("re_proj_sel", None)
        st.rerun()

    st.markdown(f"### {proj_nome} — Reembolsos")
    n, valor, pct = _reembolso_totais(proj_nome)
    c1, c2, c3 = st.columns(3)
    c1.metric("Nº reembolsos", n)
    c2.metric("Valor acumulado", db.eur(valor))
    c3.metric("% acumulada", f"{pct}%")
    if n == 0:
        st.info("Ainda sem reembolso submetido neste projeto.")

    st.divider()

    fechadas = _fechadas_projeto(proj_nome)
    if not fechadas:
        st.caption("Sem ações fechadas neste projeto.")
        return

    # Exportar todas as ações fechadas
    df_todas = pd.DataFrame(list(fechadas.values()))
    st.download_button(
        "⬇️ Exportar todas as ações fechadas (Excel)",
        data=ge._excel_bytes(df_todas),
        file_name=f"reembolso_{proj_nome}_fechadas.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"re_xls_todas_{proj_nome}",
    )

    st.markdown("#### Ações fechadas por consultor")
    st.caption("Seleciona as ações e coloca-as em reembolso (a coordenadora será notificada).")

    candidatos = db.reembolso_candidatos()
    problemas = db.reembolso_problemas()

    # agrupar por consultor
    por_consultor = {}
    for key, info in fechadas.items():
        por_consultor.setdefault(info["Consultor"], []).append((key, info))

    for consultor, itens in por_consultor.items():
        with st.expander(f"{consultor} — {len(itens)} ações fechadas"):
            for key, info in itens:
                ja = key in candidatos
                problema = problemas.get(key)
                st.checkbox(
                    f"{info['Ação']} · {info['Empresa']} · {info['Volume']} de volume",
                    key=f"resel_{key}",
                    value=ja,
                )
                if ja and problema:
                    st.caption(f"📌 Em reembolso · ⚠️ Coordenadora: {problema}")
                elif ja:
                    st.caption("📌 Em reembolso")

    # ações selecionadas (lidas do session_state)
    selecionadas = {k: v for k, v in fechadas.items() if st.session_state.get(f"resel_{k}")}

    st.divider()
    b1, b2 = st.columns(2)
    if b1.button(f"📌 Colocar selecionadas em reembolso ({len(selecionadas)})",
                 key=f"re_pôr_{proj_nome}", disabled=not selecionadas, type="primary"):
        for key, info in selecionadas.items():
            candidatos[key] = info
        st.success(f"{len(selecionadas)} ação(ões) colocadas em reembolso. A coordenadora foi notificada.")
        st.rerun()

    if selecionadas:
        df_sel = pd.DataFrame(list(selecionadas.values()))
        b2.download_button(
            "⬇️ Exportar selecionadas (Excel)",
            data=ge._excel_bytes(df_sel),
            file_name=f"reembolso_{proj_nome}_selecionadas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"re_xls_sel_{proj_nome}",
        )
