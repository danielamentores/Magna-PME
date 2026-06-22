"""Tab 'Reembolsos' do perfil do coordenador.

Mostra as ações que a gestora está a considerar para reembolso.
A coordenadora pode sinalizar que uma ação não pode avançar (com motivo),
ficando esse problema visível para a gestora.
"""
import streamlit as st
import pandas as pd

from app import db_coordenador as db


def render():
    st.subheader("💼 Ações em reembolso")

    candidatos = db.reembolso_candidatos()
    if not candidatos:
        st.info("De momento não há ações a serem consideradas para reembolso pela gestora.")
        return

    problemas = db.reembolso_problemas()
    st.caption(
        "A gestora está a considerar estas ações para reembolso. "
        "Se alguma não puder avançar, sinaliza o motivo — a gestora será notificada."
    )

    # agrupar por projeto (o projeto está no início da chave: 'PROJETO|consultor|idx')
    por_proj = {}
    for key, info in candidatos.items():
        proj = key.split("|")[0]
        por_proj.setdefault(proj, []).append((key, info))

    for proj, itens in por_proj.items():
        n_prob = sum(1 for k, _ in itens if problemas.get(k))
        titulo = f"#### {proj} — {len(itens)} ação(ões)"
        if n_prob:
            titulo += f"  ·  ⚠️ {n_prob} sinalizada(s)"
        st.markdown(titulo)

        df = pd.DataFrame([{
            "Consultor": i["Consultor"],
            "Ação": i["Ação"],
            "Empresa": i["Empresa"],
            "Volume": i["Volume"],
            "Estado": "⚠️ " + problemas[k] if problemas.get(k) else "A avançar",
        } for k, i in itens])
        st.dataframe(df, hide_index=True, use_container_width=True)

        for key, info in itens:
            tem_prob = bool(problemas.get(key))
            etiqueta = ("⚠️ " if tem_prob else "") + f"{info['Ação']} — {info['Consultor']}"
            with st.expander(etiqueta):
                motivo = st.text_input(
                    "Motivo para não ir a reembolso",
                    key=f"cprob_{key}",
                    value=problemas.get(key, ""),
                    placeholder="Ex.: faltam comprovativos de assiduidade",
                )
                c1, c2 = st.columns(2)
                if c1.button("Sinalizar à gestora", key=f"cprobset_{key}", type="primary"):
                    if motivo.strip():
                        db.marcar_problema_reembolso(key, motivo.strip())
                        st.success("Problema sinalizado à gestora.")
                        st.rerun()
                    else:
                        st.warning("Escreve o motivo antes de sinalizar.")
                if tem_prob and c2.button("Remover sinalização", key=f"cprobdel_{key}"):
                    db.reembolso_problemas().pop(key, None)
                    st.rerun()

        st.divider()
